#!/usr/bin/env python3
"""Shared evaluation helpers for the v3 retrieval study (full dictionary only)."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from specialization_layer.adapters import siwar  # noqa: E402
from specialization_layer.engine.retriever import Engine, Query  # noqa: E402
from specialization_layer.schema import restrict_roles  # noqa: E402
from spec_layer_v2 import load_eval_items, load_json, save_json  # noqa: E402

OUTDIR = ROOT / "results/v3_retrieval_study"
SIWAR = ROOT / "data/processed/data_ai/terminology_base.json"

# Simulated capability profiles (roles exposed to the engine; headword always kept).
PROFILES = {
    "P-min": set(),
    "P-def": {"definition"},
    "P-gloss": {"translation", "abbreviation"},
    "P-full": {"definition", "alias", "abbreviation", "example", "translation"},
}
KS = (1, 3, 5, 10, 50)


def load_units(profile: str):
    units, entry_to_unit = siwar.load(SIWAR)
    return restrict_roles(units, PROFILES[profile]), entry_to_unit


def eval_items():
    return {s: load_eval_items(s) for s in ("dev36", "gold50", "probes")}


def metrics(ranks: list[int]) -> dict:
    r = np.array(ranks)
    out = {f"hit@{k}": round(float((r <= k).mean()), 4) for k in KS}
    out["mrr"] = round(float((1 / r).mean()), 4)
    out["never_top10"] = int((r > 10).sum())
    out["n"] = len(r)
    return out


def evaluate(engine: Engine, items: dict, entry_to_unit: dict, query_fn) -> dict:
    """query_fn(item) -> Query. Returns per-set metrics and per-item ranks."""
    res, per_item = {}, {}
    for s in ("dev36", "gold50"):
        pos = [x for x in items[s] if x["kind"] == "positive"]
        ranks = []
        for x in pos:
            order, _, _ = engine.rank(query_fn(x))
            target = entry_to_unit[x["expected_term_id"]]
            idx = next(i for i, u in enumerate(engine.units) if u.unit_id == target)
            rk = int(np.where(order == idx)[0][0]) + 1
            ranks.append(rk)
            per_item[x["id"]] = {"rank": rk, "expected": x["expected_term"],
                                 "top3": [engine.units[i].headword for i in order[:3]]}
        res[s] = metrics(ranks)
    return {"metrics": res, "per_item": per_item}


def fmt(m: dict) -> str:
    return " ".join(f"{k}={m[k]}" for k in ("hit@1", "hit@3", "hit@5", "hit@10", "hit@50", "mrr", "never_top10"))
