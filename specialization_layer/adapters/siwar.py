"""Adapter: Siwar processed terminology (terminology_base.json) -> RetrievalUnits.

All Siwar-specific knowledge lives here:
- entries whose definition is a cross-reference ("انظر X") become variants of X,
  not separate retrievable units;
- `english_term` -> translation["en"]; `aliases` -> alias; `abbreviations` -> abbreviation.
"""

from __future__ import annotations

import json
from pathlib import Path

from ..normalize import tokens
from ..schema import RetrievalUnit

SOURCE = "siwar_data_ai"


def _key(term: str) -> str:
    return " ".join(tokens(term))


def load(path: str | Path) -> tuple[list[RetrievalUnit], dict[str, str]]:
    """Return (units, entry_to_unit) where entry_to_unit maps every source entry id
    (including redirect entries) to the unit that represents it."""
    entries = json.loads(Path(path).read_text(encoding="utf-8"))
    by_key = {_key(e["term"]): e for e in entries}
    target = {}
    for e in entries:
        ref = e.get("canonical_term")
        target[e["id"]] = by_key[_key(ref)]["id"] if ref and _key(ref) in by_key else e["id"]

    units: dict[str, RetrievalUnit] = {}
    for e in entries:
        if target[e["id"]] != e["id"]:
            continue
        roles = {}
        if (e.get("definition") or "").strip():
            roles["definition"] = [e["definition"].strip()]
        if e.get("aliases"):
            roles["alias"] = list(e["aliases"])
        if e.get("abbreviations"):
            roles["abbreviation"] = list(e["abbreviations"])
        tr = {"en": [e["english_term"].strip()]} if (e.get("english_term") or "").strip() else {}
        units[e["id"]] = RetrievalUnit(e["id"], e["id"], SOURCE, e["term"], None, roles, tr)

    for e in entries:  # fold redirect entries into their target
        t = target[e["id"]]
        if t == e["id"]:
            continue
        u = units[t]
        u.roles.setdefault("alias", []).append(e["term"])
        if (e.get("english_term") or "").strip():
            u.translation.setdefault("en", []).append(e["english_term"].strip())
        u.roles.setdefault("abbreviation", []).extend(e.get("abbreviations") or [])
        if not u.roles["abbreviation"]:
            del u.roles["abbreviation"]
    return list(units.values()), target
