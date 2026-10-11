#!/usr/bin/env python3
"""Blinded annotation packets for the v2 writer comparison, and merge-back.

prepare: collect (input, output, selected term) from chosen configs, de-duplicate
         identical outputs, shuffle with a fixed seed, and write packets that contain
         NO condition names. A private key file maps blind ids back to configs.
merge:   read annotator JSON files and attach labels to every (config, item) pair.

The annotator sees: original text, rewritten text, and - if the system introduced a
dictionary term - that term with its Siwar definition (needed to judge correctness).
Gold labels are NOT shown, so concept correctness is judged on meaning, which also
handles legitimate near-synonyms in the full dictionary.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random

from spec_layer_v2 import ROOT, load_json, save_json, load_pool

OUTDIR = ROOT / "results/v2_architecture_study/annotation"

RUBRIC = {
    "concept_correct": "Only if a term is given: does the Siwar term (per its definition) accurately name the concept the ORIGINAL text expresses? yes | partial (related but broader/narrower/imprecise) | no",
    "term_in_output": "Only if a term is given: does the rewrite actually use that term (allowing ال/inflection)? yes | no",
    "term_natural": "Only if term_in_output=yes: is it integrated as natural specialist prose (not a dictionary insertion or bolted-on clause)? yes | no",
    "meaning_preserved": "2 = all information of the original kept; 1 = minor loss/shift; 0 = meaning changed or important information lost",
    "unsupported_addition": "none | minor (small embellishment) | major (new fact, capability, cause, certainty or definition content not in the original)",
    "fluency": "1-5: natural, correct MSA a specialist would write",
    "dictionary_style": "yes if the rewrite reads like a definition/explanation of the term (e.g. 'يُعرّف بأنه', 'وهو ما يُعرف بـ' added gratuitously)",
    "instruction_leak": "yes if it mentions the pipeline (approved term, verification, the original text, etc.)",
    "false_specialization": "yes if the rewrite turns an everyday/general meaning into an AI-technical meaning, or adds AI technicality the original does not support",
}


def prepare(args):
    pool = load_pool("full")
    defs = {e["term"]: e["definition"] for e in pool.entries}
    items, key = {}, []
    for spec in args.configs:
        file, cfg = spec.split(":")
        res = load_json(ROOT / "results/v2_architecture_study" / file)
        for row in res["configs"][cfg]["rows"]:
            term = row["score"]["selected_term"]
            sig = hashlib.sha256(json.dumps([row["input"], row["output"], term], ensure_ascii=False).encode()).hexdigest()[:12]
            if sig not in items:
                items[sig] = {"blind_id": sig, "original": row["input"], "rewrite": row["output"],
                              "term": term, "term_definition": defs.get(term) if term else None}
            key.append({"blind_id": sig, "file": file, "config": cfg, "item_id": row["id"]})
    packet = list(items.values())
    random.Random(13).shuffle(packet)
    OUTDIR.mkdir(parents=True, exist_ok=True)
    n = args.batches
    for b in range(n):
        save_json({"rubric": RUBRIC, "items": packet[b::n]}, OUTDIR / f"packet_{b + 1}.json")
    save_json(key, OUTDIR / "blind_key.json")
    print(f"{len(packet)} unique outputs from {len(key)} (config, item) pairs -> {n} packets")


def merge(args):
    labels = {}
    for b in range(1, args.batches + 1):
        for x in load_json(OUTDIR / f"labels_{b}.json")["labels"]:
            labels[x["blind_id"]] = x
    key = load_json(OUTDIR / "blind_key.json")
    merged = {}
    for k in key:
        merged.setdefault(k["config"], {})[k["item_id"]] = labels.get(k["blind_id"])
    missing = sum(v is None for c in merged.values() for v in c.values())
    save_json({"rubric": RUBRIC, "labels_by_config": merged, "missing": missing}, OUTDIR / "merged_labels.json")
    print("merged; missing labels:", missing)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("prepare")
    p.add_argument("--configs", nargs="+", required=True, help="file.json:config_name")
    p.add_argument("--batches", type=int, default=4)
    m = sub.add_parser("merge")
    m.add_argument("--batches", type=int, default=4)
    a = ap.parse_args()
    prepare(a) if a.cmd == "prepare" else merge(a)
