#!/usr/bin/env python3
"""E5: retrieval + decision. Can reranking and selection be one Qwen call?

Systems (all share the query-understanding call from E2 and its `technical` gate):
  A  first stage top-10 -> selector                         (QU + 1 call)
  B  first stage top-50 -> Qwen listwise rerank -> top-10 -> selector   (QU + 2 calls)
  C  first stage top-30 -> one joint rerank+select call     (QU + 1 call)
Profiles: P-def (Arabic-only), P-full. Negatives (22) are E4.
Strict correctness = expected Siwar entry (redirects resolved). Gate on by default;
"ungated" numbers are also stored to show what the decision call alone does.
"""

from __future__ import annotations

import argparse
import hashlib
import time

import numpy as np

from exp3_common import OUTDIR, Engine, eval_items, load_json, load_units, save_json
from exp3_e2_query_understanding import AR, CACHE as QU_CACHE, EN, TEXT3
from exp3_e3_rerank import LLM_CACHE as RERANK_CACHE
from specialization_layer import decision
from specialization_layer.engine import query_understanding as qu_mod
from specialization_layer.engine.rerank import LLMListwiseReranker
from spec_layer_v2 import Qwen

PROFILES = {"P-def": (TEXT3 + AR, False), "P-full": (TEXT3 + AR + EN, True)}
CALL_CACHE = OUTDIR / "e5_decision_calls.json"
SYSTEMS = {"A": "top10 -> selector", "B": "top50 -> rerank -> top10 -> selector", "C": "top30 -> joint rerank+select"}


class CachedLLM:
    def __init__(self, path, max_tokens):
        self.path, self.cache = path, (load_json(path) if path.exists() else {})
        self.qwen = Qwen(max_tokens=max_tokens)
        self.log = []

    def __call__(self, msgs):
        k = hashlib.sha256(repr(msgs).encode()).hexdigest()[:24]
        if k not in self.cache:
            out, meta = self.qwen(msgs)
            self.cache[k] = {"output": out, "meta": meta}
            save_json(self.cache, self.path)
        m = self.cache[k]["meta"]
        self.log.append({"latency": m["elapsed_seconds"],
                         "prompt_tokens": (m.get("usage") or {}).get("prompt_tokens", 0),
                         "completion_tokens": (m.get("usage") or {}).get("completion_tokens", 0)})
        return self.cache[k]["output"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--profile", choices=list(PROFILES), required=True)
    ap.add_argument("--system", choices=list(SYSTEMS), required=True)
    a = ap.parse_args()
    specs, use_en = PROFILES[a.profile]
    items = eval_items()
    qu = load_json(QU_CACHE)
    qu_items = qu["items"]
    units, e2u = load_units(a.profile)
    eng = Engine(units, specs, fusion="neutral")
    sel_llm = CachedLLM(CALL_CACHE, 60)
    rr_llm = CachedLLM(RERANK_CACHE, 200)   # reuses E3 rerank calls (identical prompts)
    reranker = LLMListwiseReranker(rr_llm)

    rows = []
    allx = [x for s in ("dev36", "gold50", "probes") for x in items[s]]
    for n, x in enumerate(allx, 1):
        q = qu_items[x["text"]]
        order, _, _ = eng.rank(qu_mod.to_query(x["text"], q, use_en=use_en))
        calls = [{"stage": "query_understanding", "latency": None, "prompt_tokens": None}]
        sel_llm.log.clear(); rr_llm.log.clear()
        if a.system == "A":
            cands = list(order[:10])
            pick, raw = decision.decide(sel_llm, decision.SELECTOR_SYSTEM, x["text"], [units[i] for i in cands])
        elif a.system == "B":
            top50 = list(order[:50])
            new, _ = reranker.rerank(x["text"], [units[i] for i in top50])
            cands = [top50[i] for i in new[:10]]
            pick, raw = decision.decide(sel_llm, decision.SELECTOR_SYSTEM, x["text"], [units[i] for i in cands])
        else:
            cands = list(order[:30])
            pick, raw = decision.decide(sel_llm, decision.JOINT_SYSTEM, x["text"], [units[i] for i in cands])
        sel_id = units[cands[pick]].unit_id if pick is not None else None
        exp = e2u[x["expected_term_id"]] if x.get("expected_term_id") else None
        rows.append({
            "id": x["id"], "set": x["set"], "kind": x["kind"], "technical": q["technical"],
            "available": (exp in [units[i].unit_id for i in cands]) if exp else None,
            "selected": units[cands[pick]].headword if pick is not None else None,
            "selected_id": sel_id, "expected": x.get("expected_term"),
            "correct": sel_id == exp if exp else None, "raw": raw,
            "decision_calls": [*rr_llm.log, *sel_llm.log],
        })
        if n % 20 == 0:
            print(f"  {n}/{len(allx)}", flush=True)

    def summarize(gated):
        out = {}
        for s in ("dev36", "gold50"):
            P = [r for r in rows if r["set"] == s and r["kind"] == "positive"]
            sel = [r for r in P if r["selected_id"] and (r["technical"] or not gated)]
            c = sum(r["correct"] for r in sel)
            out[s] = {"n": len(P), "available": sum(r["available"] for r in P), "correct": c,
                      "wrong": len(sel) - c, "none": len(P) - len(sel),
                      "coverage": round(len(sel) / len(P), 3), "precision": round(c / len(sel), 3) if sel else None}
        N = [r for r in rows if r["kind"] != "positive"]
        fs = [r for r in N if r["selected_id"] and (r["technical"] or not gated)]
        out["negatives"] = {"n": len(N), "false_specialization": len(fs),
                            "items": {r["id"]: r["selected"] for r in fs}}
        return out

    # cost: QU call (from E2 cache) + decision-stage calls; gated items skip decision calls
    qu_meta = []
    for r in rows:
        d = r["decision_calls"]
        r["skipped_by_gate"] = not r["technical"]
    dec = [r for r in rows if r["technical"]]
    lat = [sum(c["latency"] for c in r["decision_calls"]) for r in dec]
    ptok = [sum(c["prompt_tokens"] for c in r["decision_calls"]) for r in dec]
    cost = {"api_calls_per_query": {"query_understanding": 1, "decision_stage": len(dec[0]["decision_calls"]) if dec else 0},
            "decision_latency_s_mean": round(float(np.mean(lat)), 3),
            "decision_latency_s_p90": round(float(np.percentile(lat, 90)), 3),
            "decision_prompt_tokens_mean": int(np.mean(ptok)),
            "queries_skipped_by_gate": sum(r["skipped_by_gate"] for r in rows), "n_queries": len(rows)}
    res = {"profile": a.profile, "system": a.system, "description": SYSTEMS[a.system],
           "gated": summarize(True), "ungated": summarize(False), "cost": cost, "rows": rows,
           "prompts": {"selector": decision.SELECTOR_SYSTEM, "joint": decision.JOINT_SYSTEM}}
    save_json(res, OUTDIR / f"e5_decision_{a.profile}_{a.system}.json")
    print(a.profile, a.system, "gated", {k: v for k, v in res["gated"].items()})
    print("ungated negatives FS:", res["ungated"]["negatives"]["false_specialization"], "| cost", cost)


if __name__ == "__main__":
    main()
