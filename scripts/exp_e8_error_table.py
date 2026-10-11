#!/usr/bin/env python3
"""Render E8 errors.json as ERRORS.md (explanations are derived mechanically from stage data)."""

from __future__ import annotations

import json
from pathlib import Path

D = Path(__file__).resolve().parents[1] / "results/e8_source_grounded_positive_100"


def explain(e, n_cands):
    r, rr = e["expected_first_stage_rank"], e["expected_rerank_rank"]
    st = e["baseline_failure_stage"]
    if st == "retrieval_failure":
        s = f"expected not among the {n_cands} decision candidates (first-stage rank {r})"
    elif st == "reranker_failure":
        s = f"first-stage rank {r}; reranker placed it at {rr} (outside the selector's top-10)"
    elif st == "technical_gate_failure":
        s = "query understanding marked the text non-technical"
    else:
        s = f"expected available (first-stage rank {r}); decision chose «{e['selected_baseline']}»"
    if e["potential_acceptable_alternative"]:
        s += "; flagged potential acceptable alternative (unvalidated)"
    return s


def main():
    errors = json.loads((D / "errors.json").read_text(encoding="utf-8"))
    summary = json.loads((D / "summary.json").read_text(encoding="utf-8"))
    out = ["# E8 error table (baseline pipeline errors)", "",
           "Strict scoring against the item's `unit_id`. `alt` = potential acceptable alternative "
           "(heuristic flag: wrong pick among the gold entry's 10 nearest dictionary units; NOT counted as "
           "correct; needs human acceptable-entry annotation). Explanations are derived mechanically.", ""]
    for prof in ("P-full", "P-def"):
        n = summary[prof]["decision_candidates_n"]
        rows = [e for e in errors if e["profile"] == prof and e["baseline_failure_stage"]]
        out += [f"## {prof} — {len(rows)} errors", "",
                "| item_id | style | text | expected | selected | exp. rank (first stage / rerank) | stage | alt | explanation |",
                "|---|---|---|---|---|---|---|---|---|"]
        for e in rows:
            rk = f"{e['expected_first_stage_rank']}" + (f" / {e['expected_rerank_rank']}" if prof == "P-def" else "")
            out.append(f"| {e['item_id']} | {e['style_group']} | {e['text']} | {e['expected']} | "
                       f"{e['selected_baseline']} | {rk} | {e['baseline_failure_stage']} | "
                       f"{'yes' if e['potential_acceptable_alternative'] else ''} | {explain(e, n)} |")
        s1 = [e for e in errors if e["profile"] == prof and e["s1_false_rejection_at_k"]]
        s2 = [e for e in errors if e["profile"] == prof and e["s2_failure"]]
        out += ["", f"S1 false rejections of correct baseline decisions ({prof}): "
                + ", ".join(f"k={k}: {sum(k in e['s1_false_rejection_at_k'] for e in s1)}" for k in (1, 3, 5, 10)),
                "", f"S2 failures on correct baseline decisions ({prof}): "
                + ", ".join(f"{e['item_id']} ({e['s2_failure']}, → {e['selected_s2']})" for e in s2), ""]
    (D / "ERRORS.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    print("wrote", D / "ERRORS.md")


if __name__ == "__main__":
    main()
