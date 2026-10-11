#!/usr/bin/env python3
"""Validate, freeze and split the human-written held-out set (heldout_v1).

Commands
  reference  export the full dictionary as a read-only CSV for writers/annotators
  validate   check items.json against the schema and authoring rules (no model involved)
  freeze     validate, then write FROZEN.json with the SHA-256 of items.json
  split      (only after freeze) stratified 30 % calibration / 70 % test, fixed seed

No command here runs the specialization system.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import random
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from specialization_layer.adapters import siwar  # noqa: E402
from specialization_layer.normalize import ar_stem, tokens  # noqa: E402

D = ROOT / "evaluation/heldout_v1"
ITEMS = D / "items.json"
FROZEN = D / "FROZEN.json"
SPLIT = D / "split.json"
DICT = ROOT / "data/processed/data_ai/terminology_base.json"
SPLIT_SEED = 20261012
CALIBRATION_FRACTION = 0.30

TYPES = {"plain_positive", "near_neighbour", "ambiguous", "everyday_negative", "vague_negative"}
POSITIVE_TYPES = {"plain_positive", "near_neighbour", "ambiguous"}
REGISTERS = {"msa", "saudi", "mixed"}
REQUIRED = ["item_id", "item_type", "register", "text", "source_unit_ids", "label",
            "acceptable_unit_ids", "preferred_unit_id", "author_id", "annotator_id",
            "annotator_agreed", "adjudicated"]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def contains(text: str, form: str) -> bool:
    f = [ar_stem(t) for t in tokens(form)]
    q = [ar_stem(t) for t in tokens(text)]
    return bool(f) and any(q[i:i + len(f)] == f for i in range(len(q) - len(f) + 1))


def cmd_reference(_):
    units, _ = siwar.load(DICT)
    out = D / "dictionary_reference.csv"
    with out.open("w", encoding="utf-8-sig", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["unit_id", "headword", "english", "aliases", "abbreviations", "definition"])
        for u in sorted(units, key=lambda u: u.headword):
            w.writerow([u.unit_id, u.headword, "; ".join(u.translations("en")), "; ".join(u.get("alias")),
                        "; ".join(u.get("abbreviation")), (u.get("definition") or [""])[0]])
    print("wrote", out)


def validate() -> list[str]:
    if not ITEMS.exists():
        return [f"{ITEMS} does not exist"]
    data = json.loads(ITEMS.read_text(encoding="utf-8"))
    units, _ = siwar.load(DICT)
    by_id = {u.unit_id: u for u in units}
    errs, seen = [], set()
    for n, it in enumerate(data.get("items", [])):
        where = it.get("item_id", f"#{n}")
        for k in REQUIRED:
            if k not in it:
                errs.append(f"{where}: missing field {k}")
        if errs and errs[-1].startswith(where):
            continue
        if it["item_id"] in seen:
            errs.append(f"{where}: duplicate item_id")
        seen.add(it["item_id"])
        if it["item_type"] not in TYPES:
            errs.append(f"{where}: bad item_type")
        if it["register"] not in REGISTERS:
            errs.append(f"{where}: bad register")
        if not it["text"].strip():
            errs.append(f"{where}: empty text")
        for uid in it["source_unit_ids"] + it["acceptable_unit_ids"] + ([it["preferred_unit_id"]] if it["preferred_unit_id"] else []):
            if uid not in by_id:
                errs.append(f"{where}: unknown unit id {uid}")
        if not it["annotator_id"] or it["annotator_id"] == it["author_id"]:
            errs.append(f"{where}: needs a second annotator different from the author")
        if not it["annotator_agreed"] and not it["adjudicated"]:
            errs.append(f"{where}: disagreement not adjudicated")
        if it["item_type"] in POSITIVE_TYPES:
            if it["label"] != "TERM" or not it["acceptable_unit_ids"]:
                errs.append(f"{where}: positive item needs label TERM and acceptable_unit_ids")
            if it["preferred_unit_id"] not in it["acceptable_unit_ids"]:
                errs.append(f"{where}: preferred_unit_id must be in acceptable_unit_ids")
            if it["item_type"] == "ambiguous" and len(it["acceptable_unit_ids"]) < 2:
                errs.append(f"{where}: ambiguous item needs >= 2 acceptable units")
            for uid in it["acceptable_unit_ids"]:
                u = by_id.get(uid)
                if not u:
                    continue
                for f in [u.headword, *u.get("alias"), *u.get("abbreviation"), *u.translations("en")]:
                    if f and contains(it["text"], f):
                        errs.append(f"{where}: text contains the term/alias/abbreviation/translation '{f}'")
        else:
            if it["label"] != "NONE" or it["acceptable_unit_ids"] or it["preferred_unit_id"]:
                errs.append(f"{where}: negative item needs label NONE and no acceptable units")
            if it["item_type"] == "everyday_negative":
                u = by_id.get((it["source_unit_ids"] or [None])[0])
                if not u or not contains(it["text"], u.headword):
                    errs.append(f"{where}: everyday negative must contain its source headword")
    return errs


def cmd_validate(_):
    errs = validate()
    print("\n".join(errs) if errs else "OK: items.json passes all checks")
    return 1 if errs else 0


def cmd_freeze(a):
    errs = validate()
    if errs:
        print("\n".join(errs))
        sys.exit("Not frozen: fix validation errors first.")
    if FROZEN.exists():
        sys.exit("Already frozen. A new freeze requires a new dataset version (heldout_v2).")
    data = json.loads(ITEMS.read_text(encoding="utf-8"))
    counts = {}
    for it in data["items"]:
        counts[it["item_type"]] = counts.get(it["item_type"], 0) + 1
    FROZEN.write_text(json.dumps({
        "items_sha256": sha256(ITEMS), "sampled_terms_sha256": sha256(D / "sampled_terms.json"),
        "frozen_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "frozen_by": a.by, "counts": counts, "n_items": len(data["items"]),
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print("frozen:", FROZEN.read_text(encoding="utf-8"))


def require_frozen():
    if not FROZEN.exists():
        sys.exit("items.json is not frozen.")
    if json.loads(FROZEN.read_text(encoding="utf-8"))["items_sha256"] != sha256(ITEMS):
        sys.exit("items.json changed after freezing — evaluation is invalid.")


def stratified_split(item_ids_by_type: dict[str, list[str]], seed: int, frac: float) -> dict[str, str]:
    rng = random.Random(seed)
    out = {}
    for t in sorted(item_ids_by_type):
        ids = sorted(item_ids_by_type[t])
        rng.shuffle(ids)
        n_cal = round(frac * len(ids))
        for i, iid in enumerate(ids):
            out[iid] = "calibration" if i < n_cal else "test"
    return out


def cmd_split(_):
    require_frozen()
    if SPLIT.exists():
        sys.exit("Split already exists; it must not be regenerated.")
    data = json.loads(ITEMS.read_text(encoding="utf-8"))
    by_type = {}
    for it in data["items"]:
        by_type.setdefault(it["item_type"], []).append(it["item_id"])
    assign = stratified_split(by_type, SPLIT_SEED, CALIBRATION_FRACTION)
    SPLIT.write_text(json.dumps({"seed": SPLIT_SEED, "calibration_fraction": CALIBRATION_FRACTION,
                                 "items_sha256": sha256(ITEMS), "assignment": assign},
                                ensure_ascii=False, indent=2), encoding="utf-8")
    print({s: sum(v == s for v in assign.values()) for s in ("calibration", "test")})


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("reference")
    sub.add_parser("validate")
    f = sub.add_parser("freeze")
    f.add_argument("--by", required=True, help="name of the person freezing the labels")
    sub.add_parser("split")
    a = ap.parse_args()
    sys.exit({"reference": cmd_reference, "validate": cmd_validate,
              "freeze": cmd_freeze, "split": cmd_split}[a.cmd](a) or 0)
