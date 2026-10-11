#!/usr/bin/env python3
"""Seeded, reproducible sampling of dictionary entries for the held-out set (heldout_v1).

Eligible = canonical Siwar entries (redirects folded by the adapter) that were NEVER
used in development:
  - the 50 pilot terms,
  - every expected term in dev36 / gold50,
  - every term selected, rejected, forced or expected in any stored v1/v2/v3 result,
  - the three writer-demonstration terms embedded in v2 writer prompts.

Output pools (disjoint; each entry appears in at most one pool):
  plain_positive        120 primary + 60 reserve
  near_neighbour_pairs  20 primary + 15 reserve   (pairs of eligible entries)
  ambiguous_pairs       30 primary + 15 reserve   (pairs of eligible entries)
  everyday_candidates   50 primary + 50 reserve   (short headwords, may have a general sense)

Pairs are proposed automatically as mutual nearest neighbours of definition embeddings
(E5, definitions only — no evaluation data involved); human experts accept or skip them
following the authoring guide. Nothing here uses system outputs on new items.
"""

from __future__ import annotations

import glob
import hashlib
import json
import random
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from specialization_layer.adapters import siwar  # noqa: E402
from specialization_layer.engine.embed import encode  # noqa: E402
from specialization_layer.normalize import tokens  # noqa: E402

SEED = 20261011
DICT = ROOT / "data/processed/data_ai/terminology_base.json"
PILOT = ROOT / "data/processed/data_ai/terminology_pilot_50.json"
OUT = ROOT / "evaluation/heldout_v1/sampled_terms.json"
WRITER_DEMO_TERMS = ["زيادة البيانات", "تقطير المعرفة", "انحراف البيانات"]
SIZES = {"plain_positive": (120, 60), "near_neighbour_pairs": (20, 15),
         "ambiguous_pairs": (30, 15), "everyday_candidates": (50, 50)}
UUID = __import__("re").compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")


def key(t):
    return " ".join(tokens(t))


def used_in_development(units, entry_to_unit):
    by_name = {key(u.headword): u.unit_id for u in units}
    for u in units:
        for a in u.get("alias"):
            by_name.setdefault(key(a), u.unit_id)
    ids, names = set(), set()

    def walk(o):
        if isinstance(o, dict):
            for k, v in o.items():
                if k in ("selected_id", "selected_term_id", "expected_term_id", "expected_id",
                         "forced_term_id") and isinstance(v, str):
                    ids.add(v)
                elif k in ("selected_term", "rejected_term", "forced_term", "expected_term",
                           "selected") and isinstance(v, str):
                    names.add(v)
                else:
                    walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    for f in sorted(glob.glob(str(ROOT / "results/**/*.json"), recursive=True)):
        walk(json.loads(Path(f).read_text(encoding="utf-8")))
    for f in ("data/evaluation/ai_final_layer_eval_v1.json", "data/gold_test/data_ai_retrieval_gold_50.json"):
        walk(json.loads((ROOT / f).read_text(encoding="utf-8")))
    for e in json.loads(PILOT.read_text(encoding="utf-8")):
        ids.add(e["id"])
    names.update(WRITER_DEMO_TERMS)
    excluded = {entry_to_unit.get(i, i) for i in ids}
    unresolved = []
    for n in names:
        if UUID.match(n):          # some result files store ids in name-like fields
            excluded.add(entry_to_unit.get(n, n))
            continue
        u = by_name.get(key(n))
        if u:
            excluded.add(u)
        else:
            unresolved.append(n)
    return excluded, unresolved


def main():
    units, entry_to_unit = siwar.load(DICT)
    excluded, unresolved = used_in_development(units, entry_to_unit)
    eligible = [u for u in units if u.unit_id not in excluded and u.has("definition")]
    rng = random.Random(SEED)
    taken = set()

    def entry(u):
        return {"unit_id": u.unit_id, "headword": u.headword,
                "definition": u.get("definition")[0],
                "english": (u.translations("en") or [None])[0],
                "aliases": u.get("alias"), "abbreviations": u.get("abbreviation")}

    # --- pairs first (they need related entries), from definition similarity
    order = sorted(eligible, key=lambda u: u.unit_id)
    D = encode(["passage: " + u.get("definition")[0] for u in order])
    S = D @ D.T
    np.fill_diagonal(S, -1)
    # mutual nearest neighbours by definition (scale-free; no similarity threshold)
    nn = S.argmax(axis=1)
    cand = [(i, int(nn[i])) for i in range(len(order)) if nn[nn[i]] == i and i < nn[i]]
    rng.shuffle(cand)
    pools = {}
    for pool in ("near_neighbour_pairs", "ambiguous_pairs"):
        need = sum(SIZES[pool])
        chosen = []
        for i, j in cand:
            a, b = order[i], order[j]
            if a.unit_id in taken or b.unit_id in taken:
                continue
            chosen.append({"pair_similarity": round(float(S[i, j]), 4), "a": entry(a), "b": entry(b)})
            taken.update([a.unit_id, b.unit_id])
            if len(chosen) == need:
                break
        p, r = SIZES[pool]
        pools[pool] = {"primary": chosen[:p], "reserve": chosen[p:p + r]}

    # --- everyday candidates: single-word headwords first (most likely to have a general
    # sense), then two-word headwords; experts take them in order and skip those without one
    one = [u for u in order if u.unit_id not in taken and len(tokens(u.headword)) == 1]
    two = [u for u in order if u.unit_id not in taken and len(tokens(u.headword)) == 2]
    rng.shuffle(one)
    rng.shuffle(two)
    p, r = SIZES["everyday_candidates"]
    ev = (one + two)[:p + r]
    taken.update(u.unit_id for u in ev)
    pools["everyday_candidates"] = {"primary": [entry(u) for u in ev[:p]],
                                    "reserve": [entry(u) for u in ev[p:]]}

    # --- plain positives: stratified by headword length (1 / 2 / 3+ tokens), proportional
    rest = [u for u in order if u.unit_id not in taken]
    strata = {}
    for u in rest:
        strata.setdefault(min(len(tokens(u.headword)), 3), []).append(u)
    p, r = SIZES["plain_positive"]
    total = len(rest)
    prim, res = [], []
    for s in sorted(strata):
        group = strata[s]
        rng.shuffle(group)
        np_, nr = round(p * len(group) / total), round(r * len(group) / total)
        prim += [dict(entry(u), stratum=f"{s}{'+' if s == 3 else ''}_token") for u in group[:np_]]
        res += [dict(entry(u), stratum=f"{s}{'+' if s == 3 else ''}_token") for u in group[np_:np_ + nr]]
    pools["plain_positive"] = {"primary": prim[:p], "reserve": res[:r]}

    out = {
        "dataset": "heldout_v1", "seed": SEED, "pair_rule": "mutual nearest neighbours by E5 definition embedding",
        "dictionary_file": str(DICT.relative_to(ROOT)),
        "dictionary_sha256": hashlib.sha256(DICT.read_bytes()).hexdigest(),
        "n_canonical_units": len(units), "n_excluded_dev_terms": len(excluded),
        "n_eligible": len(eligible), "unresolved_excluded_names": sorted(unresolved),
        "excluded_unit_ids": sorted(excluded),
        "usage": "Use pools in listed order; skip an entry only for a reason allowed by the authoring "
                 "guide, record the reason, then take the next reserve entry.",
        "pools": pools,
    }
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print({k: (len(v["primary"]), len(v["reserve"])) for k, v in pools.items()},
          "eligible", len(eligible), "excluded", len(excluded), "unresolved names", len(unresolved))


if __name__ == "__main__":
    main()
