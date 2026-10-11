#!/usr/bin/env python3
"""Aggregate blinded quality labels per configuration and evaluation set.

Success definition for a positive item ("specialized successfully"):
  concept_correct == yes AND term_in_output == yes AND term_natural == yes
  AND meaning_preserved == 2 AND unsupported_addition != major.
"Safe" for a negative item: no false specialization and no term introduced.
"""

from __future__ import annotations

import json
from statistics import mean

from spec_layer_v2 import ROOT, load_json, save_json

D = ROOT / "results/v2_architecture_study"


def main():
    merged = load_json(D / "annotation/merged_labels.json")["labels_by_config"]
    files = {"exp_final_end_to_end.json": load_json(D / "exp_final_end_to_end.json"),
             "exp_w_writer.json": load_json(D / "exp_w_writer.json")}
    rows_by_cfg = {}
    for f in files.values():
        for name, c in f["configs"].items():
            rows_by_cfg[name] = {r["id"]: r for r in c["rows"]}
    report = {}
    for cfg, labels in merged.items():
        rows = rows_by_cfg[cfg]
        out = {}
        for st in ("dev36", "gold50", "probes"):
            ids = [i for i, r in rows.items() if r["set"] == st]
            L = [(rows[i], labels[i]) for i in ids if labels.get(i)]
            pos = [(r, l) for r, l in L if r["kind"] == "positive"]
            neg = [(r, l) for r, l in L if r["kind"] != "positive"]
            s = {"n": len(L),
                 "meaning_2_rate": round(mean(l["meaning_preserved"] == 2 for _, l in L), 3),
                 "meaning_0": sum(l["meaning_preserved"] == 0 for _, l in L),
                 "unsupported_major": sum(l["unsupported_addition"] == "major" for _, l in L),
                 "unsupported_minor": sum(l["unsupported_addition"] == "minor" for _, l in L),
                 "fluency_mean": round(mean(l["fluency"] for _, l in L), 2),
                 "dictionary_style": sum(l["dictionary_style"] == "yes" for _, l in L),
                 "instruction_leak": sum(l["instruction_leak"] == "yes" for _, l in L),
                 "false_specialization": sum(l["false_specialization"] == "yes" for _, l in L)}
            if pos:
                termed = [(r, l) for r, l in pos if r["score"]["selected_term"]]
                s.update({
                    "n_pos": len(pos), "n_term_selected": len(termed),
                    "concept_yes": sum(l["concept_correct"] == "yes" for _, l in termed),
                    "concept_partial": sum(l["concept_correct"] == "partial" for _, l in termed),
                    "concept_no": sum(l["concept_correct"] == "no" for _, l in termed),
                    "specialized_successfully": sum(
                        l["concept_correct"] == "yes" and l["term_in_output"] == "yes" and l["term_natural"] == "yes"
                        and l["meaning_preserved"] == 2 and l["unsupported_addition"] != "major" for _, l in pos),
                    "wrong_concept_in_output": sum(l["concept_correct"] == "no" and l["term_in_output"] == "yes"
                                                   for _, l in pos),
                })
                s["specialized_successfully_rate"] = round(s["specialized_successfully"] / len(pos), 3)
            if neg:
                s.update({"n_neg": len(neg),
                          "neg_safe": sum(l["false_specialization"] != "yes" and not r["score"]["selected_term_used"]
                                          for r, l in neg)})
            out[st] = s
        report[cfg] = out
    save_json(report, D / "quality_report.json")
    keys = ["n_pos", "concept_yes", "concept_partial", "concept_no", "specialized_successfully",
            "wrong_concept_in_output", "meaning_2_rate", "meaning_0", "unsupported_major", "unsupported_minor",
            "fluency_mean", "dictionary_style", "instruction_leak", "false_specialization", "n_neg", "neg_safe"]
    for cfg, out in report.items():
        print(cfg)
        for st, s in out.items():
            print("   ", st, " ".join(f"{k}={s[k]}" for k in keys if k in s))


if __name__ == "__main__":
    main()
