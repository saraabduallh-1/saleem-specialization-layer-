#!/usr/bin/env python3
"""Compact comparison tables for v2 result files (decision and writer stages).

Gated variants are computed offline: a row is turned into NONE when the
concept-naming call (run once per text, label-free) returned no concept.
"""

from __future__ import annotations

import argparse
import json

from spec_layer_v2 import ROOT, load_json, save_json

DIR = ROOT / "results/v2_architecture_study"


def decision_row(rows, gate):
    def sel(r):
        return None if (gate and not r["naming_nonempty"]) else r["score"]["selected_id"]

    def ok(r):
        return sel(r) is not None and r["score"]["selection_strict_correct"]
    out = {}
    for st in ("dev36", "gold50"):
        pos = [r for r in rows if r["set"] == st and r["kind"] == "positive"]
        out[st] = {"avail": sum(bool(r["score"]["available"]) for r in pos),
                   "correct": sum(ok(r) for r in pos),
                   "wrong": sum(sel(r) is not None and not ok(r) for r in pos),
                   "none": sum(sel(r) is None for r in pos), "n": len(pos)}
    neg = [r for r in rows if r["kind"] != "positive"]
    out["neg_false_spec"] = f"{sum(sel(r) is not None for r in neg)}/{len(neg)}"
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("file")
    a = ap.parse_args()
    d = load_json(DIR / a.file)
    table = {}
    for name, c in d["configs"].items():
        for gate in (False, True):
            table[name + ("+gate" if gate else "")] = decision_row(c["rows"], gate)
    hdr = f"{'config':28} | {'dev36 avail/corr/wrong/none':28} | {'gold50 avail/corr/wrong/none':29} | neg FP"
    print(hdr)
    print("-" * len(hdr))
    for k, v in table.items():
        f = lambda s: f"{v[s]['avail']:>2}/{v[s]['correct']:>2}/{v[s]['wrong']:>2}/{v[s]['none']:>2}  (n={v[s]['n']})"
        print(f"{k:28} | {f('dev36'):28} | {f('gold50'):29} | {v['neg_false_spec']}")
    save_json(table, DIR / a.file.replace(".json", "_table.json"))


if __name__ == "__main__":
    main()
