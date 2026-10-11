#!/usr/bin/env python3
"""Frozen metrics for heldout_v1 (pre-registered; do not edit after the labels are frozen).

Input predictions file (one per system x profile x split):
  {"system": "...", "profile": "P-def|P-full", "split": "calibration|test",
   "predictions": {item_id: {"selected_unit_id": str|null, "candidate_unit_ids": [...]}}}

Definitions (item level)
  positive types : plain_positive, near_neighbour, ambiguous (label TERM, acceptable set)
  negative types : everyday_negative, vague_negative (label NONE)
  correct  = positive item, selected in acceptable set
  wrong    = positive item, selected not in acceptable set
  none     = no selection
  false_specialization (FS) = negative item with any selection
  accepted_precision = correct / (correct + wrong + FS)          [primary]
  accepted_accuracy  = correct / (correct + wrong)               [positives only]
  coverage           = correct / n_positive
  fs_rate            = FS / n_negative
  abstention_rate    = none / n_items
  availability       = positives with an acceptable unit among candidates / n_positive
95 % percentile bootstrap CIs: 10,000 item-level resamples, seed 20261013.
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path

POS = {"plain_positive", "near_neighbour", "ambiguous"}
NEG = {"everyday_negative", "vague_negative"}
BOOT_N, BOOT_SEED = 10_000, 20261013
# Pre-registered success criteria (test split, each profile separately)
SC_PRECISION_POINT, SC_PRECISION_CI_LOW, SC_FS_RATE_MAX = 0.85, 0.75, 0.05


def outcomes(items, preds):
    rows = []
    for it in items:
        p = preds.get(it["item_id"], {})
        sel = p.get("selected_unit_id")
        cands = set(p.get("candidate_unit_ids") or [])
        acc = set(it["acceptable_unit_ids"])
        if it["item_type"] in POS:
            o = "none" if not sel else ("correct" if sel in acc else "wrong")
            avail = bool(acc & cands)
        else:
            o = "fs" if sel else "none"
            avail = None
        rows.append({"item_id": it["item_id"], "type": it["item_type"], "outcome": o, "available": avail})
    return rows


def metrics(rows):
    c = sum(r["outcome"] == "correct" for r in rows)
    w = sum(r["outcome"] == "wrong" for r in rows)
    fs = sum(r["outcome"] == "fs" for r in rows)
    none = sum(r["outcome"] == "none" for r in rows)
    npos = sum(r["type"] in POS for r in rows)
    nneg = sum(r["type"] in NEG for r in rows)
    acc_n = c + w + fs
    return {"n_items": len(rows), "n_positive": npos, "n_negative": nneg,
            "correct": c, "wrong": w, "none": none, "false_specialization": fs,
            "accepted_precision": c / acc_n if acc_n else None,
            "accepted_accuracy": c / (c + w) if c + w else None,
            "coverage": c / npos if npos else None,
            "fs_rate": fs / nneg if nneg else None,
            "abstention_rate": none / len(rows) if rows else None,
            "availability": (sum(bool(r["available"]) for r in rows if r["type"] in POS) / npos) if npos else None}


def bootstrap(rows, keys=("accepted_precision", "coverage", "fs_rate", "accepted_accuracy")):
    rng = random.Random(BOOT_SEED)
    vals = {k: [] for k in keys}
    for _ in range(BOOT_N):
        m = metrics([rows[rng.randrange(len(rows))] for _ in rows])
        for k in keys:
            if m[k] is not None:
                vals[k].append(m[k])
    ci = {}
    for k, v in vals.items():
        v.sort()
        ci[k] = [v[int(0.025 * len(v))], v[int(0.975 * len(v)) - 1]] if v else None
    return ci


def score(items, preds):
    rows = outcomes(items, preds)
    out = {"overall": metrics(rows), "ci95": bootstrap(rows), "by_type": {}}
    for t in sorted({r["type"] for r in rows}):
        out["by_type"][t] = metrics([r for r in rows if r["type"] == t])
    o = out["overall"]
    out["success"] = {
        "precision_point_ok": o["accepted_precision"] is not None and o["accepted_precision"] >= SC_PRECISION_POINT,
        "precision_ci_low_ok": bool(out["ci95"]["accepted_precision"]) and out["ci95"]["accepted_precision"][0] >= SC_PRECISION_CI_LOW,
        "fs_rate_ok": o["fs_rate"] is not None and o["fs_rate"] <= SC_FS_RATE_MAX,
    }
    out["success"]["all"] = all(out["success"].values())
    return out


def selftest():
    """Synthetic sanity check of the metric definitions (no real items)."""
    items = [{"item_id": "p1", "item_type": "plain_positive", "acceptable_unit_ids": ["a"]},
             {"item_id": "p2", "item_type": "ambiguous", "acceptable_unit_ids": ["b", "c"]},
             {"item_id": "p3", "item_type": "near_neighbour", "acceptable_unit_ids": ["d"]},
             {"item_id": "n1", "item_type": "everyday_negative", "acceptable_unit_ids": []},
             {"item_id": "n2", "item_type": "vague_negative", "acceptable_unit_ids": []}]
    preds = {"p1": {"selected_unit_id": "a", "candidate_unit_ids": ["a"]},
             "p2": {"selected_unit_id": "c", "candidate_unit_ids": ["c"]},
             "p3": {"selected_unit_id": "e", "candidate_unit_ids": ["e"]},
             "n1": {"selected_unit_id": "x", "candidate_unit_ids": ["x"]},
             "n2": {"selected_unit_id": None, "candidate_unit_ids": []}}
    m = metrics(outcomes(items, preds))
    assert (m["correct"], m["wrong"], m["false_specialization"], m["none"]) == (2, 1, 1, 1)
    assert abs(m["accepted_precision"] - 0.5) < 1e-9 and abs(m["coverage"] - 2 / 3) < 1e-9
    assert m["fs_rate"] == 0.5 and m["availability"] == 2 / 3
    print("selftest OK")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--items")
    ap.add_argument("--split")
    ap.add_argument("--predictions")
    ap.add_argument("--out")
    a = ap.parse_args()
    if a.selftest:
        selftest()
        sys.exit(0)
    items_all = json.loads(Path(a.items).read_text(encoding="utf-8"))["items"]
    pred = json.loads(Path(a.predictions).read_text(encoding="utf-8"))
    assign = json.loads(Path(a.split).read_text(encoding="utf-8"))["assignment"]
    items = [it for it in items_all if assign[it["item_id"]] == pred["split"]]
    res = {"system": pred["system"], "profile": pred["profile"], "split": pred["split"], **score(items, pred["predictions"])}
    Path(a.out).write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(res["overall"], indent=1), res["success"])
