#!/usr/bin/env python3
"""Re-score stored outputs of the earlier experiments with the v2 matcher.

No model is called. Historical result files are only read.
Writes results/v2_architecture_study/reanalysis_previous_runs.json
"""

from __future__ import annotations

from spec_layer_v2 import (ROOT, load_json, save_json, term_present, naive_present,
                           meta_leak, definitional_framing)

OUT = ROOT / "results/v2_architecture_study/reanalysis_previous_runs.json"
RUNS = {
    "top5_writer": ("results/final_layer_experiment/final_layer_experiment_20261008T093228Z.json",
                    ["T1_terminology", "T2_terminology_domain"]),
    "top1_writer": ("results/final_layer_experiment/final_layer_experiment_20261008T100947Z.json",
                    ["T1_terminology", "T2_terminology_domain"]),
    "top3_selector_writer": ("results/semantic_selection_experiment/semantic_selection_experiment_20261008T102751Z.json",
                             ["S1_selected_term", "S2_selected_term_domain"]),
}


def score(rows, get_output, get_selected=None):
    pos = [r for r in rows if r["kind"] == "positive"]
    out = {"n_positive": len(pos), "expected_term_naive": 0, "expected_term_morph": 0,
           "meta_leak_outputs": 0, "definitional_framing_outputs": 0}
    if get_selected:
        out.update({"selected_correct": 0, "selected_correct_and_used_morph": 0,
                    "selected_wrong_and_wrong_term_used": 0})
    for r in rows:
        o = get_output(r)
        out["meta_leak_outputs"] += bool(meta_leak(o))
        out["definitional_framing_outputs"] += bool(definitional_framing(o))
    for r in pos:
        o = get_output(r)
        out["expected_term_naive"] += naive_present(o, r["expected_term"])
        out["expected_term_morph"] += term_present(o, r["expected_term"])
        if get_selected:
            sel = get_selected(r)
            if sel and sel[0] == r["expected_term_id"]:
                out["selected_correct"] += 1
                out["selected_correct_and_used_morph"] += term_present(o, sel[1])
            elif sel:
                out["selected_wrong_and_wrong_term_used"] += term_present(o, sel[1])
    return out


def main():
    report = {"note": "Re-scoring of stored outputs only; dev/ablation evidence on the 36 repeatedly examined items.",
              "runs": {}}
    for name, (path, conds) in RUNS.items():
        d = load_json(ROOT / path)
        for c in conds:
            sel = None
            if "selection" in d["items"][0]:
                sel = lambda r: ((r["selection"]["selected_term_id"], r["selection"]["selected_term"])
                                 if r["selection"]["selected_term_id"] else None)
            elif d["metadata"]["top_k"] == 1:
                sel = lambda r: (r["retrieval"]["top_k"][0]["id"], r["retrieval"]["top_k"][0]["term"])
            report["runs"][f"{name}/{c}"] = score(d["items"], lambda r, c=c: r["conditions"][c]["output"], sel)

    d = load_json(ROOT / "results/forced_rewrite_validator_experiment/forced_rewrite_validator_20261008T104627Z.json")
    rows = d["items"]
    sel = lambda r: ((r["selection"]["selected_term_id"], r["selection"]["selected_term"])
                     if r["selection"]["selected_term_id"] else None)
    report["runs"]["forced_rewrite/attempt1"] = score(rows, lambda r: r["attempts"][0]["output"], sel)
    report["runs"]["forced_rewrite/final"] = score(rows, lambda r: r["final_output"], sel)

    # Validator behaviour audit
    audit = {"items_with_forced_term": 0, "term_dropped_on_retry": 0,
             "dropped_although_selection_correct": 0,
             "attempt1_term_present_morph_but_lexical_check_false": 0,
             "validator_fit_false_when_term_absent": 0, "dropped_ids": []}
    for r in rows:
        a1 = r["attempts"][0]
        if not a1["forced_term"]:
            continue
        audit["items_with_forced_term"] += 1
        v = a1["validation"]
        if term_present(a1["output"], a1["forced_term"]) and not v["term_present_lexical"]:
            audit["attempt1_term_present_morph_but_lexical_check_false"] += 1
        if not term_present(a1["output"], a1["forced_term"]) and v["selected_term_fit"] is False:
            audit["validator_fit_false_when_term_absent"] += 1
        if len(r["attempts"]) > 1 and r["attempts"][1]["forced_term"] is None:
            audit["term_dropped_on_retry"] += 1
            ok = r["selection"]["selected_term_id"] == r["expected_term_id"]
            audit["dropped_although_selection_correct"] += ok
            audit["dropped_ids"].append((r["id"], r["forced_term"] if "forced_term" in r else a1["forced_term"], ok))
    report["forced_rewrite_validator_audit"] = audit
    save_json(report, OUT)
    import json
    print(json.dumps(report, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
