#!/usr/bin/env python3
"""Exp R: retrieval over the pilot-50 pool vs the full Siwar AI dictionary.

No LLM calls. Compares candidate representations / hubness correction on two
development sets (dev36 positives and gold50). A change is only adopted if it
helps on BOTH sets, to limit overfitting to either.

Also reports whether E5 scores alone could make the specialize/abstain decision
(score / margin separability of positives vs controls and probes).
"""

from __future__ import annotations

import json

import numpy as np

from spec_layer_v2 import (ROOT, Retriever, hit_summary, load_eval_items, load_pool, save_json)

OUT = ROOT / "results/v2_architecture_study/exp_r_retrieval.json"
CONFIGS = [("term_def", False), ("term_en_def", False), ("term_def", True), ("term_en_def", True)]


def auc(pos, neg):
    pos, neg = np.array(pos), np.array(neg)
    return float(((pos[:, None] > neg[None, :]).mean() + 0.5 * (pos[:, None] == neg[None, :]).mean()))


def main():
    sets = {s: load_eval_items(s) for s in ("dev36", "gold50", "probes")}
    report = {"note": "Development evidence only (dev36 repeatedly examined; gold50 earlier retrieval set).",
              "results": {}, "decision_separability": {}, "per_item": {}}
    for pool_name in ("pilot50", "full"):
        pool = load_pool(pool_name)
        for rep, hub in CONFIGS:
            key = f"{pool_name}|{rep}|hub={hub}"
            r = Retriever(pool, rep, hub)
            report["results"][key] = {"n_candidates": len(pool.candidates)}
            for s in ("dev36", "gold50"):
                pos = [x for x in sets[s] if x["kind"] == "positive"]
                ranks = r.rank_of([x["text"] for x in pos], [x["expected_term_id"] for x in pos])
                report["results"][key][s] = hit_summary(ranks)
                if rep == "term_def" and not hub:
                    report["per_item"][f"{pool_name}|{s}"] = {x["id"]: rk for x, rk in zip(pos, ranks)}
            if rep == "term_def" and not hub:
                # Could E5 scores alone decide specialize vs abstain?
                allx = sets["dev36"] + sets["gold50"] + sets["probes"]
                top = r.search([x["text"] for x in allx], 2)
                s1 = {x["id"]: t[0]["score"] for x, t in zip(allx, top)}
                mg = {x["id"]: t[0]["score"] - t[1]["score"] for x, t in zip(allx, top)}
                posids = [x["id"] for x in allx if x["kind"] == "positive"]
                negids = [x["id"] for x in allx if x["kind"] != "positive"]
                report["decision_separability"][pool_name] = {
                    "n_pos": len(posids), "n_neg": len(negids),
                    "auc_top1_score": round(auc([s1[i] for i in posids], [s1[i] for i in negids]), 3),
                    "auc_top1_margin": round(auc([mg[i] for i in posids], [mg[i] for i in negids]), 3),
                    "pos_top1_score_range": [round(min(s1[i] for i in posids), 3), round(max(s1[i] for i in posids), 3)],
                    "neg_top1_score_range": [round(min(s1[i] for i in negids), 3), round(max(s1[i] for i in negids), 3)],
                }
    save_json(report, OUT)
    print(json.dumps({k: v for k, v in report.items() if k != "per_item"}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
