#!/usr/bin/env python3
"""E2: structured query understanding + optional translation signals + fairness test.

One Qwen call per input (cached) -> {technical, concept_ar, concept_en, keywords}.
Profiles:
  P-def   Arabic-only path (no translation role, concept_en unused)
  P-full  all Siwar roles, concept_en used for translation signals
  P-gloss headword + translation + abbreviation, no definitions
Fairness: under P-full, translations removed from 50% of units (seeds 1..3);
compare items whose expected unit kept vs lost its translation, for fusion
"neutral" vs "zero".
"""

from __future__ import annotations

import random
from concurrent.futures import ThreadPoolExecutor

import numpy as np

from exp3_common import (OUTDIR, PROFILES, SIWAR, Engine, eval_items, evaluate, fmt, load_json,
                         load_units, metrics, save_json)
from specialization_layer.adapters import siwar
from specialization_layer.engine import query_understanding as qu_mod
from specialization_layer.schema import RetrievalUnit, restrict_roles
from spec_layer_v2 import Qwen

DOMAIN = "الذكاء الاصطناعي"
CACHE = OUTDIR / "query_understanding_cache.json"

TEXT3 = [("dense_unit", "text"), ("dense_def", "text"), ("lexical", "text")]
AR = [("dense_unit", "concept_ar"), ("dense_def", "concept_ar"), ("lexical", "keywords")]
EN = [("translation_lex", "concept_en"), ("translation_dense", "concept_en")]

CONFIGS = [  # (name, profile, specs, use_en)
    ("E1-best text only", "P-def", TEXT3, False),
    ("+concept_ar", "P-def", TEXT3 + AR[:2], False),
    ("+concept_ar+keywords", "P-def", TEXT3 + AR, False),
    ("P-full no concept_en", "P-full", TEXT3 + AR, False),
    ("P-full +concept_en", "P-full", TEXT3 + AR + EN, True),
    ("P-full text+EN only", "P-full", [("dense_unit", "text")] + EN, True),
    ("P-gloss all", "P-gloss", [("dense_unit", "text"), ("dense_unit", "concept_ar"), ("lexical", "text"),
                                ("lexical", "keywords")] + EN, True),
]


def understand(items):
    cache = load_json(CACHE) if CACHE.exists() else {"system": qu_mod.SYSTEM_TEMPLATE, "domain": DOMAIN, "items": {}}
    assert cache["system"] == qu_mod.SYSTEM_TEMPLATE, "prompt changed: use a new cache file"
    todo = [x for x in items if x["text"] not in cache["items"]]
    if todo:
        import threading
        qwen = Qwen(max_tokens=300)
        cache["qwen"] = qwen.meta()
        lock = threading.Lock()

        def one(x):
            raw, meta = qwen(qu_mod.messages(x["text"], DOMAIN))
            with lock:  # save incrementally so an interrupted run resumes
                cache["items"][x["text"]] = {**qu_mod.parse(raw), "raw": raw}
                save_json(cache, CACHE)
                print(f"  understood {len(cache['items'])}/{len(items)}", flush=True)
        with ThreadPoolExecutor(1) as ex:
            list(ex.map(one, todo))
    return cache["items"]


def mask_translations(units, seed):
    rng = random.Random(seed)
    ids = sorted(u.unit_id for u in units if u.has("translation"))
    drop = set(rng.sample(ids, len(ids) // 2))
    out = []
    for u in units:
        tr = {} if u.unit_id in drop else {l: list(v) for l, v in u.translation.items()}
        out.append(RetrievalUnit(u.unit_id, u.entry_id, u.source, u.headword, u.sense_no,
                                 {r: list(v) for r, v in u.roles.items()}, tr))
    return out, drop


def main():
    items = eval_items()
    qu = understand([x for s in items.values() for x in s])
    report = {"note": "Development evidence; full dictionary.", "prompt": qu_mod.SYSTEM_TEMPLATE,
              "results": {}, "fairness": {}, "technical_flag": {}}

    # technical flag as an abstention signal
    for s, xs in items.items():
        report["technical_flag"][s] = {
            "positives_flagged_nontechnical": sum(not qu[x["text"]]["technical"] for x in xs if x["kind"] == "positive"),
            "n_positive": sum(x["kind"] == "positive" for x in xs),
            "negatives_flagged_technical": sum(qu[x["text"]]["technical"] for x in xs if x["kind"] != "positive"),
            "n_negative": sum(x["kind"] != "positive" for x in xs)}

    for name, prof, specs, use_en in CONFIGS:
        units, e2u = load_units(prof)
        eng = Engine(units, specs, fusion="neutral")
        r = evaluate(eng, items, e2u, lambda x: qu_mod.to_query(x["text"], qu[x["text"]], use_en=use_en))
        r["active_signals"] = [f"{s.name}[{p}]" for s, p in eng.signals]
        report["results"][f"{prof}|{name}"] = r
        print(f"{prof:7} {name:24} dev36  {fmt(r['metrics']['dev36'])}")
        print(f"{'':7} {'':24} gold50 {fmt(r['metrics']['gold50'])}", flush=True)

    # fairness: partial translation coverage
    full_units, e2u = siwar.load(SIWAR)
    full_units = restrict_roles(full_units, PROFILES["P-full"])
    specs = TEXT3 + AR + EN
    pos = [x for s in ("dev36", "gold50") for x in items[s] if x["kind"] == "positive"]
    ref = {}
    for ref_name, ref_specs, use_en, ref_units in (("no_english_anywhere", TEXT3 + AR, False,
                                                     restrict_roles(full_units, PROFILES["P-def"])),
                                                    ("english_everywhere", specs, True, full_units)):
        eng = Engine(ref_units, ref_specs, fusion="neutral")
        ref[ref_name] = {x["id"]: rank(eng, x, e2u, qu, use_en) for x in pos}
    for fusion in ("neutral", "zero"):
        for seed in (1, 2, 3):
            units, dropped = mask_translations(full_units, seed)
            eng = Engine(units, specs, fusion=fusion)
            kept, lost = [], []
            for x in pos:
                rk = rank(eng, x, e2u, qu, True)
                (lost if e2u[x["expected_term_id"]] in dropped else kept).append((x["id"], rk))
            key = f"{fusion}|seed{seed}"
            report["fairness"][key] = {
                "kept_translation": {"partial": metrics([r for _, r in kept]),
                                     "english_everywhere": metrics([ref["english_everywhere"][i] for i, _ in kept])},
                "lost_translation": {"partial": metrics([r for _, r in lost]),
                                     "no_english_anywhere": metrics([ref["no_english_anywhere"][i] for i, _ in lost])},
            }
            f = report["fairness"][key]
            print(f"fairness {key}: lost n={len(lost)} hit@10 partial={f['lost_translation']['partial']['hit@10']} "
                  f"vs no-English-anywhere={f['lost_translation']['no_english_anywhere']['hit@10']} | "
                  f"kept n={len(kept)} hit@10 partial={f['kept_translation']['partial']['hit@10']} "
                  f"vs English-everywhere={f['kept_translation']['english_everywhere']['hit@10']}", flush=True)
    print("technical flag:", report["technical_flag"])
    save_json(report, OUTDIR / "e2_query_understanding.json")


def rank(eng, x, e2u, qu, use_en):
    order, _, _ = eng.rank(qu_mod.to_query(x["text"], qu[x["text"]], use_en=use_en))
    target = e2u[x["expected_term_id"]]
    idx = next(i for i, u in enumerate(eng.units) if u.unit_id == target)
    return int(np.where(order == idx)[0][0]) + 1


if __name__ == "__main__":
    main()
