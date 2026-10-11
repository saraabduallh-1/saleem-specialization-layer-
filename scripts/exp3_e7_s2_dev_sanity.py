#!/usr/bin/env python3
"""E7: the single pre-registered development sanity check of S2 (PREREGISTRATION §4A).

Development data only (dev36, gold50, probes). Registered pipelines (§3, D2):
  P-full : first stage -> one-call decision over top-30   (decisions reused from E5 system C)
  P-def  : first stage -> reranker -> selector             (decisions reused from E5 system B)
Settings reported: baseline (gate only), S1 (k in {1,3,5,10}), S2, S1+S2 (k in {1,3,5,10}).
Run once: refuses to start if the result file exists. An interrupted run resumes from the
call cache (no call is repeated). No change to S2 is allowed after this run.
"""

from __future__ import annotations

import hashlib
import statistics
import subprocess
import sys
from collections import Counter

from exp3_common import OUTDIR, Engine, eval_items, load_json, load_units, save_json
from exp3_e2_query_understanding import AR, CACHE as QU_CACHE, EN, TEXT3
from specialization_layer import contrastive
from specialization_layer.abstention import view_ranks
from specialization_layer.engine import query_understanding as qu_mod
from specialization_layer.engine.signals import DenseUnit
from spec_layer_v2 import Qwen

OUT = OUTDIR / "e7_s2_dev_sanity.json"
CALLS = OUTDIR / "e7_s2_calls.json"
KS = (1, 3, 5, 10)
PROFILES = {"P-full": ("C", TEXT3 + AR + EN, True), "P-def": ("B", TEXT3 + AR, False)}


def main():
    if OUT.exists():
        sys.exit("E7 has already been run; the S2 sanity check is single-run by pre-registration.")
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    items = eval_items()
    qu = load_json(QU_CACHE)["items"]
    allx = {x["id"]: x for s in items.values() for x in s}
    cache = load_json(CALLS) if CALLS.exists() else {}
    qwen = Qwen(max_tokens=contrastive.MAX_TOKENS)
    log = []

    def llm(msgs):
        k = hashlib.sha256(repr(msgs).encode()).hexdigest()[:24]
        if k not in cache:
            out, meta = qwen(msgs)
            cache[k] = {"output": out, "meta": meta}
            save_json(cache, CALLS)
        log.append(cache[k]["meta"])
        return cache[k]["output"]

    report = {"note": "Single pre-registered development sanity check of S2; development data only; "
                      "no S2 changes permitted after this run.",
              "code_commit": commit, "profiles": {}}
    for prof, (system, specs, use_en) in PROFILES.items():
        units, e2u = load_units(prof)
        eng = Engine(units, specs, fusion="neutral")
        uv = next(s for s, _ in eng.signals if isinstance(s, DenseUnit)).P
        uidx = {u.unit_id: i for i, u in enumerate(units)}
        rows = load_json(OUTDIR / f"e5_decision_{prof}_{system}.json")["rows"]
        log.clear()
        recs = []
        for n, r in enumerate(rows, 1):
            x = allx[r["id"]]
            exp = e2u[x["expected_term_id"]] if x.get("expected_term_id") else None
            rec = {"id": r["id"], "set": r["set"], "kind": r["kind"], "technical": r["technical"],
                   "expected": exp, "available": r["available"], "c_star": None, "s2": None,
                   "s2_reason": None, "views_c_star": None, "views_s2": None}
            if r["technical"] and r["selected_id"]:
                ci = uidx[r["selected_id"]]
                _, _, ev = eng.rank(qu_mod.to_query(x["text"], qu[x["text"]], use_en=use_en))
                pick, reason, idxs, raw = contrastive.decide(llm, x["text"], units, uv, ci)
                rec.update({"c_star": units[ci].unit_id, "contrast_set": [units[i].unit_id for i in idxs],
                            "contrast_headwords": [units[i].headword for i in idxs],
                            "s2": units[pick].unit_id if pick is not None else None,
                            "s2_headword": units[pick].headword if pick is not None else None,
                            "s2_reason": reason, "s2_raw": raw,
                            "views_c_star": view_ranks(ev, ci),
                            "views_s2": view_ranks(ev, pick) if pick is not None else None,
                            "s2_latency": log[-1]["elapsed_seconds"],
                            "s2_prompt_tokens": (log[-1].get("usage") or {}).get("prompt_tokens"),
                            "s2_completion_tokens": (log[-1].get("usage") or {}).get("completion_tokens")})
            recs.append(rec)
            if n % 20 == 0:
                print(f"  {prof} {n}/{len(rows)}", flush=True)

        def passes(v, k):
            return bool(v) and v["text_active"] and v["interp_active"] and v["text"] <= k and v["interp"] <= k

        settings = {"baseline": {r["id"]: r["c_star"] for r in recs}, "S2": {r["id"]: r["s2"] for r in recs}}
        for k in KS:
            settings[f"S1@k={k}"] = {r["id"]: r["c_star"] if passes(r["views_c_star"], k) else None for r in recs}
            settings[f"S1+S2@k={k}"] = {r["id"]: r["s2"] if passes(r["views_s2"], k) else None for r in recs}

        def summarize(sel):
            out = {}
            for scope, rs in (("dev36", [r for r in recs if r["set"] == "dev36"]),
                              ("gold50", [r for r in recs if r["set"] == "gold50"]), ("all", recs)):
                P = [r for r in rs if r["kind"] == "positive"]
                N = [r for r in rs if r["kind"] != "positive"]
                c = sum(sel[r["id"]] == r["expected"] for r in P if sel[r["id"]])
                w = sum(sel[r["id"]] != r["expected"] for r in P if sel[r["id"]])
                fs = sum(bool(sel[r["id"]]) for r in N)
                out[scope] = {"correct": c, "wrong": w, "none": len(P) - c - w, "n_pos": len(P),
                              "fs": fs, "n_neg": len(N),
                              "precision_incl_neg": round(c / (c + w + fs), 3) if c + w + fs else None,
                              "precision_pos": round(c / (c + w), 3) if c + w else None,
                              "coverage": round(c / len(P), 3) if P else None,
                              "fs_rate": round(fs / len(N), 3) if N else None}
            return out

        T = [r for r in recs if r["c_star"]]
        pos_ok = [r for r in T if r["kind"] == "positive" and r["c_star"] == r["expected"]]
        pos_bad = [r for r in T if r["kind"] == "positive" and r["c_star"] != r["expected"]]
        negs = [r for r in T if r["kind"] != "positive"]
        behaviour = {
            "decisions_reaching_s2": len(T),
            "c_star_correct": len(pos_ok),
            "  kept_correct": sum(r["s2"] == r["c_star"] for r in pos_ok),
            "  wrongly_changed_to_other_unit": sum(r["s2"] not in (None, r["c_star"]) for r in pos_ok),
            "  abstained_on_correct": sum(r["s2"] is None for r in pos_ok),
            "c_star_wrong": len(pos_bad),
            "  corrected_to_expected": sum(r["s2"] == r["expected"] for r in pos_bad),
            "  changed_to_another_wrong": sum(r["s2"] not in (None, r["c_star"], r["expected"]) for r in pos_bad),
            "  kept_same_wrong": sum(r["s2"] == r["c_star"] for r in pos_bad),
            "  abstained_on_wrong": sum(r["s2"] is None for r in pos_bad),
            "  expected_in_contrast_set": sum(r["expected"] in r["contrast_set"] for r in pos_bad),
            "negatives_reaching_s2": len(negs),
            "  abstained_on_negative": sum(r["s2"] is None for r in negs),
            "s2_abstentions_total": sum(r["s2"] is None for r in T),
            "abstention_reasons": dict(Counter(r["s2_reason"] for r in T)),
            "near_neighbour_correction_rate": round(sum(r["s2"] == r["expected"] for r in pos_bad) / len(pos_bad), 3)
            if pos_bad else None,
        }
        lat = [r["s2_latency"] for r in T]
        cost = {"extra_calls_per_query_reaching_s2": 1,
                "s2_latency_median_s": round(statistics.median(lat), 3),
                "s2_latency_p90_s": round(sorted(lat)[int(0.9 * len(lat)) - 1], 3),
                "s2_prompt_tokens_mean": int(statistics.mean(r["s2_prompt_tokens"] or 0 for r in T)),
                "s2_completion_tokens_mean": int(statistics.mean(r["s2_completion_tokens"] or 0 for r in T))}
        report["profiles"][prof] = {"system": system, "results": {k: summarize(v) for k, v in settings.items()},
                                    "s2_behaviour": behaviour, "cost": cost, "records": recs}
        print(f"\n== {prof}")
        for k, v in report["profiles"][prof]["results"].items():
            a = v["all"]
            print(f"{k:12} correct {a['correct']:2} wrong {a['wrong']:2} none {a['none']:2} "
                  f"prec {a['precision_incl_neg']} cov {a['coverage']} FS {a['fs']}/{a['n_neg']}")
        print(behaviour)
        print(cost)
    save_json(report, OUT)


if __name__ == "__main__":
    main()
