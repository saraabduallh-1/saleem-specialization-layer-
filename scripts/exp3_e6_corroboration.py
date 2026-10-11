#!/usr/bin/env python3
"""E6 (development only): two-view corroboration rule on stored E5 decisions.

No new LLM calls: decisions are read from E5 result files.
  P-full : system C  (first stage -> one-call decision over top-30)
  P-def  : system B  (first stage -> Qwen listwise rerank -> selector over top-10)
For each k in {1,3,5,10}: accept the decided unit only if it ranks <= k in both the
text view and the interpretation view of the first-stage signals (see
specialization_layer/abstention.py). The technical gate stays in front.
Diagnostic evidence on repeatedly examined data; NOT used to set the held-out k.
"""

from __future__ import annotations

from collections import Counter

from exp3_common import OUTDIR, Engine, eval_items, load_json, load_units, save_json
from exp3_e2_query_understanding import AR, CACHE as QU_CACHE, EN, TEXT3
from specialization_layer.abstention import corroborated
from specialization_layer.engine import query_understanding as qu_mod

KS = (1, 3, 5, 10)
RUNS = {"P-full": ("C", TEXT3 + AR + EN, True), "P-def": ("B", TEXT3 + AR, False)}


def classify(r, accepted):
    """Error/outcome category for one item under one setting."""
    if r["kind"] == "positive":
        if not r["technical"]:
            return "gate_false_reject"
        if accepted and r["correct"]:
            return "correct"
        if accepted:
            return "retrieval_failure_wrong" if not r["available"] else "decision_failure_wrong"
        # abstained
        if r["selected_id"] and r["correct"]:
            return "corroboration_false_reject"
        if r["selected_id"]:
            return "corroboration_true_reject"      # a wrong pick was blocked
        return "decision_none"
    if not r["technical"]:
        return "gate_true_reject"
    if accepted:
        return "false_specialization"
    return "corroboration_true_reject" if r["selected_id"] else "decision_none"


def summarize(rows, acc):
    out = {}
    for s in ("dev36", "gold50"):
        P = [r for r in rows if r["set"] == s and r["kind"] == "positive"]
        c = sum(acc[r["id"]] and r["correct"] for r in P)
        w = sum(acc[r["id"]] and not r["correct"] for r in P)
        out[s] = {"n": len(P), "available": sum(r["available"] for r in P), "correct": c, "wrong": w,
                  "none": len(P) - c - w}
    P = [r for r in rows if r["kind"] == "positive"]
    N = [r for r in rows if r["kind"] != "positive"]
    c = sum(acc[r["id"]] and r["correct"] for r in P)
    w = sum(acc[r["id"]] and not r["correct"] for r in P)
    fs = sum(acc[r["id"]] for r in N)
    out["pooled"] = {"n_pos": len(P), "correct": c, "wrong": w, "none": len(P) - c - w,
                     "accepted_precision_pos": round(c / (c + w), 3) if c + w else None,
                     "accepted_precision_incl_neg": round(c / (c + w + fs), 3) if c + w + fs else None,
                     "coverage": round(c / len(P), 3),
                     "available": sum(r["available"] for r in P),
                     "false_specialization": fs, "n_neg": len(N), "fs_rate": round(fs / len(N), 3),
                     "gate_failures_pos": sum(not r["technical"] for r in P),
                     "gate_failures_neg": sum(r["technical"] for r in N)}
    out["categories"] = dict(Counter(classify(r, acc[r["id"]]) for r in rows))
    return out


def main():
    items = eval_items()
    qu = load_json(QU_CACHE)["items"]
    allx = {x["id"]: x for s in items.values() for x in s}
    report = {"note": "Development diagnostic on dev36/gold50/probes; decisions reused from E5; "
                      "not used to choose the held-out k.", "profiles": {}}
    for prof, (system, specs, use_en) in RUNS.items():
        units, _ = load_units(prof)
        eng = Engine(units, specs, fusion="neutral")
        uidx = {u.unit_id: i for i, u in enumerate(units)}
        rows = load_json(OUTDIR / f"e5_decision_{prof}_{system}.json")["rows"]
        views = {}
        for r in rows:
            if r["selected_id"] and r["technical"]:
                x = allx[r["id"]]
                _, _, ev = eng.rank(qu_mod.to_query(x["text"], qu[x["text"]], use_en=use_en))
                _, v = corroborated(ev, uidx[r["selected_id"]], 10)
                views[r["id"]] = v
        settings = {"no_rule": {r["id"]: bool(r["selected_id"]) and r["technical"] for r in rows}}
        for k in KS:
            settings[f"k={k}"] = {r["id"]: bool(r["selected_id"]) and r["technical"]
                                  and r["id"] in views and views[r["id"]]["text"] <= k
                                  and views[r["id"]]["interp"] <= k
                                  and views[r["id"]]["text_active"] and views[r["id"]]["interp_active"]
                                  for r in rows}
        res = {name: summarize(rows, acc) for name, acc in settings.items()}
        per_item = {r["id"]: {"set": r["set"], "kind": r["kind"], "expected": r["expected"],
                              "selected": r["selected"], "correct": r["correct"], "available": r["available"],
                              "technical": r["technical"], "view_ranks": views.get(r["id"])} for r in rows}
        report["profiles"][prof] = {"system": system, "results": res, "per_item": per_item}
        print(f"\n== {prof} (system {system})")
        for name, s in res.items():
            p = s["pooled"]
            print(f"{name:8} correct {p['correct']:2} wrong {p['wrong']:2} none {p['none']:2} | "
                  f"prec(pos) {p['accepted_precision_pos']} prec(incl neg) {p['accepted_precision_incl_neg']} "
                  f"cov {p['coverage']} | FS {p['false_specialization']}/{p['n_neg']} ({p['fs_rate']}) | "
                  f"dev36 {s['dev36']['correct']}/{s['dev36']['wrong']} gold50 {s['gold50']['correct']}/{s['gold50']['wrong']}")
            print(f"{'':8} {s['categories']}")
    save_json(report, OUTDIR / "e6_corroboration_dev.json")


if __name__ == "__main__":
    main()
