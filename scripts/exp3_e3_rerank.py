#!/usr/bin/env python3
"""E3: second-stage reranking of the top-50 from the E2 first stage.

First stage (unchanged from E2):
  P-def  : Arabic-only path  (text + concept_ar + keywords), no translation role
  P-full : + translation signals with concept_en
Rerankers (both see units rendered from whatever roles exist):
  CE     : local cross-encoder (query = user text)
  CE+ar  : local cross-encoder (query = user text + Arabic concept description)
  LLM    : one Qwen listwise call (query = user text)
Reports accuracy, latency, memory, model size, API calls; negatives: how often the
top-1 is an everyday-sense lexical trap (its headword literally occurs in the input).
"""

from __future__ import annotations

import argparse
import hashlib
import os
import time
from pathlib import Path

import numpy as np
import psutil

from exp3_common import (OUTDIR, Engine, eval_items, load_json, load_units, save_json)
from exp3_e2_query_understanding import AR, CACHE as QU_CACHE, EN, TEXT3
from specialization_layer.engine import query_understanding as qu_mod
from specialization_layer.engine.rerank import CrossEncoderReranker, LLMListwiseReranker, render_unit
from specialization_layer.normalize import ar_stem, tokens
from spec_layer_v2 import Qwen

CE_MODEL = "cross-encoder/mmarco-mMiniLMv2-L12-H384-v1"
TOP_N = 50
LLM_CACHE = OUTDIR / "e3_listwise_cache.json"
PROFILES = {"P-def": (TEXT3 + AR, False), "P-full": (TEXT3 + AR + EN, True)}


def literal_in_input(headword: str, text: str) -> bool:
    h = [ar_stem(t) for t in tokens(headword)]
    q = [ar_stem(t) for t in tokens(text)]
    return bool(h) and any(q[i:i + len(h)] == h for i in range(len(q) - len(h) + 1))


def hits(ranks):
    r = np.array(ranks)
    return {**{f"hit@{k}": round(float((r <= k).mean()), 4) for k in (1, 3, 5, 10)},
            "mrr": round(float((1 / r).mean()), 4), "never_top10": int((r > 10).sum()), "n": len(r)}


def auc(pos, neg):
    p, n = np.array(pos)[:, None], np.array(neg)[None, :]
    return round(float((p > n).mean() + 0.5 * (p == n).mean()), 3)


def dir_size_mb(model_name):
    root = Path.home() / ".cache/huggingface/hub" / ("models--" + model_name.replace("/", "--"))
    return round(sum(f.stat().st_size for f in root.rglob("*") if f.is_file() and not f.is_symlink()) / 1e6, 1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--profile", choices=list(PROFILES), required=True)
    ap.add_argument("--skip-llm", action="store_true")
    a = ap.parse_args()
    specs, use_en = PROFILES[a.profile]

    items = eval_items()
    qu = load_json(QU_CACHE)["items"]
    units, e2u = load_units(a.profile)
    eng = Engine(units, specs, fusion="neutral")
    pos_items = [x for s in ("dev36", "gold50") for x in items[s] if x["kind"] == "positive"]
    neg_items = [x for s in ("dev36", "probes") for x in items[s] if x["kind"] != "positive"]
    uidx = {u.unit_id: i for i, u in enumerate(units)}

    # ---- first stage
    first, t_first = {}, []
    for x in pos_items + neg_items:
        t0 = time.perf_counter()
        order, _, _ = eng.rank(qu_mod.to_query(x["text"], qu[x["text"]], use_en=use_en))
        t_first.append(time.perf_counter() - t0)
        first[x["id"]] = order

    def rank_after(x, new_top):
        """new_top: reordered list of the first-stage top-N unit indices."""
        full = list(new_top) + [i for i in first[x["id"]] if i not in set(new_top)]
        return full.index(uidx[e2u[x["expected_term_id"]]]) + 1

    methods = {"first_stage": {x["id"]: list(first[x["id"]][:TOP_N]) for x in pos_items + neg_items}}
    cost = {"first_stage": {"latency_s_mean": round(float(np.mean(t_first)), 4), "api_calls_per_query": 1,
                            "note": "1 call = shared query-understanding call (from E2)"}}
    ce_scores = {}

    # ---- cross-encoder
    proc = psutil.Process(os.getpid())
    rss0 = proc.memory_info().rss
    t0 = time.perf_counter()
    ce = CrossEncoderReranker(CE_MODEL)
    load_s = time.perf_counter() - t0
    n_params = sum(p.numel() for p in ce.model.model.parameters())
    for variant in ("CE", "CE+ar"):
        lat, out = [], {}
        for x in pos_items + neg_items:
            top = list(first[x["id"]][:TOP_N])
            q = x["text"] if variant == "CE" else (x["text"] + "\n" + (qu[x["text"]].get("concept_ar") or "")).strip()
            t1 = time.perf_counter()
            order, scores = ce.rerank(q, [units[i] for i in top])
            lat.append(time.perf_counter() - t1)
            out[x["id"]] = [top[i] for i in order]
            ce_scores.setdefault(variant, {})[x["id"]] = scores[0]
        methods[variant] = out
        cost[variant] = {"latency_s_mean": round(float(np.mean(lat)), 4), "latency_s_p90": round(float(np.percentile(lat, 90)), 4),
                         "api_calls_per_query": 1, "model": CE_MODEL, "params_M": round(n_params / 1e6, 1),
                         "disk_MB": dir_size_mb(CE_MODEL), "load_s": round(load_s, 2),
                         "rss_increase_MB": round((proc.memory_info().rss - rss0) / 1e6, 1),
                         "device": str(ce.model.device)}

    # ---- Qwen listwise
    if not a.skip_llm:
        qwen = Qwen(max_tokens=200)
        cache = load_json(LLM_CACHE) if LLM_CACHE.exists() else {}
        usage = {}

        def llm(msgs):
            k = hashlib.sha256(repr(msgs).encode()).hexdigest()[:24]
            if k not in cache:
                outp, meta = qwen(msgs)
                cache[k] = {"output": outp, "meta": meta}
                save_json(cache, LLM_CACHE)
            usage.setdefault("lat", []).append(cache[k]["meta"]["elapsed_seconds"])
            usage.setdefault("ptok", []).append((cache[k]["meta"].get("usage") or {}).get("prompt_tokens", 0))
            return cache[k]["output"]
        rr = LLMListwiseReranker(llm)
        out, parse_fail = {}, 0
        for n, x in enumerate(pos_items + neg_items, 1):
            top = list(first[x["id"]][:TOP_N])
            order, raw = rr.rerank(x["text"], [units[i] for i in top])
            parse_fail += not rr.parse(raw, len(top))
            out[x["id"]] = [top[i] for i in order]
            print(f"  listwise {n}/{len(pos_items) + len(neg_items)}", flush=True)
        methods["LLM"] = out
        cost["LLM"] = {"latency_s_mean": round(float(np.mean(usage["lat"])), 3),
                       "latency_s_p90": round(float(np.percentile(usage["lat"], 90)), 3),
                       "api_calls_per_query": 2, "prompt_tokens_mean": int(np.mean(usage["ptok"])),
                       "parse_failures": parse_fail, "local_memory_MB": 0, "model": qwen.model + " (remote)"}

    # ---- evaluation
    res = {}
    for m, tops in methods.items():
        r = {}
        for s in ("dev36", "gold50"):
            r[s] = hits([rank_after(x, tops[x["id"]]) for x in pos_items if x["set"] == s])
        traps = [x["id"] for x in neg_items if literal_in_input(units[tops[x["id"]][0]].headword, x["text"])]
        r["negatives"] = {"n": len(neg_items), "top1_literal_trap": len(traps), "trap_ids": traps,
                          "top1": {x["id"]: units[tops[x["id"]][0]].headword for x in neg_items}}
        if m in ce_scores:
            r["negatives"]["top1_score_auc_pos_vs_neg"] = auc([ce_scores[m][x["id"]] for x in pos_items],
                                                               [ce_scores[m][x["id"]] for x in neg_items])
        res[m] = r
        print(f"{a.profile} {m:12} dev36 {r['dev36']} | gold50 {r['gold50']} | neg traps {len(traps)}/{len(neg_items)}")
    save_json({"profile": a.profile, "top_n": TOP_N, "note": "Development evidence; full dictionary.",
               "listwise_prompt": LLMListwiseReranker.messages.__doc__ or "", "results": res, "cost": cost,
               "render_example": render_unit(units[0])},
              OUTDIR / f"e3_rerank_{a.profile}.json")
    print(cost)


if __name__ == "__main__":
    main()
