"""Two-view corroboration: accept a decided unit only if independent retrieval views agree.

Views are defined by the QUERY PART a signal consumes, never by dictionary fields:
  text view            signals over the user's original text (no LLM involved)
  interpretation view  signals over LLM-derived query parts (concept_ar, keywords, concept_en)
A view's rank for a unit is the best rank among that view's active signals. Fields a
dictionary lacks simply deactivate signals; they never change the rule.
"""

from __future__ import annotations

TEXT_PARTS = {"text"}
INTERP_PARTS = {"concept_ar", "keywords", "concept_en"}
INF = 10 ** 9


def view_ranks(evidence: dict[str, dict[int, int]], unit_index: int) -> dict[str, int]:
    """evidence: {"signal[part]": {unit_index: rank}} as returned by Engine.rank."""
    best = {"text": INF, "interp": INF}
    active = {"text": False, "interp": False}
    for key, ranks in evidence.items():
        part = key[key.index("[") + 1:-1]
        view = "text" if part in TEXT_PARTS else ("interp" if part in INTERP_PARTS else None)
        if view is None:
            continue
        active[view] = True
        best[view] = min(best[view], ranks.get(unit_index, INF))
    return {"text": best["text"], "interp": best["interp"],
            "text_active": active["text"], "interp_active": active["interp"]}


def corroborated(evidence: dict[str, dict[int, int]], unit_index: int, k: int) -> tuple[bool, dict]:
    v = view_ranks(evidence, unit_index)
    ok = v["text_active"] and v["interp_active"] and v["text"] <= k and v["interp"] <= k
    return ok, v
