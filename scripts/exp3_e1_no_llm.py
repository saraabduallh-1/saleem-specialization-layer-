#!/usr/bin/env python3
"""E1: generic engine with schema-generic, LLM-free signals under simulated profiles.

Signals: dense_unit[text] (baseline = v2 E5 term+definition), dense_def[text],
lexical[text] (BM25), surface[text] (headword/alias/abbreviation literally in input).
Profiles: P-min (headword only), P-def (+definition), P-full (all Siwar roles).
No translation signal here (it needs an LLM-produced concept_en; tested in E2).
"""

from __future__ import annotations

import json

from exp3_common import (OUTDIR, Engine, Query, evaluate, eval_items, fmt, load_units, save_json)

CONFIGS = {
    "dense_unit": [("dense_unit", "text")],
    "+dense_def": [("dense_unit", "text"), ("dense_def", "text")],
    "+lexical": [("dense_unit", "text"), ("lexical", "text")],
    "+surface": [("dense_unit", "text"), ("surface", "text")],
    "all4": [("dense_unit", "text"), ("dense_def", "text"), ("lexical", "text"), ("surface", "text")],
    "dense3": [("dense_unit", "text"), ("dense_def", "text"), ("lexical", "text")],
    "lexical_only": [("lexical", "text")],
}


def main():
    items = eval_items()
    report = {"note": "Development evidence; full Siwar AI dictionary (1,316 units); fusion=RRF neutral.",
              "results": {}}
    for prof in ("P-min", "P-def", "P-full"):
        units, e2u = load_units(prof)
        for name, specs in CONFIGS.items():
            eng = Engine(units, specs, fusion="neutral")
            r = evaluate(eng, items, e2u, lambda x: Query(text=x["text"]))
            r["active_signals"] = [f"{s.name}[{p}]" for s, p in eng.signals]
            r["inactive_signals"] = eng.inactive
            report["results"][f"{prof}|{name}"] = r
            print(f"{prof:6} {name:12} dev36 {fmt(r['metrics']['dev36'])}")
            print(f"{'':6} {'':12} gold50 {fmt(r['metrics']['gold50'])}  inactive={eng.inactive}", flush=True)
    save_json(report, OUTDIR / "e1_no_llm.json")


if __name__ == "__main__":
    main()
