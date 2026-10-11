"""Generic retrieval engine: activates the signals a dictionary supports and fuses them.

Signal specs are (signal_name, query_part). Query parts:
  text        the user's input text
  concept_ar  Arabic concept description from query understanding (optional)
  keywords    list of key terms (optional)
  concept_en  list of foreign-language concept names (optional)

Fusion = reciprocal rank fusion. Missing-field policy:
  "zero"    a unit without the signal's role simply gets no contribution
  "neutral" a unit without the role receives the mean of its contributions from
            the signals that do apply to it (missing evidence is neither good nor bad)
A unit that HAS the role but receives no evidence (e.g. no lexical overlap) is a
genuine zero in both policies.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from ..schema import RetrievalUnit, profile_of
from .signals import REGISTRY


@dataclass
class Query:
    text: str
    concept_ar: str | None = None
    keywords: list[str] | None = None
    concept_en: list[str] | None = None

    def part(self, name):
        return getattr(self, name)


class Engine:
    def __init__(self, units: list[RetrievalUnit], specs: list[tuple[str, str]],
                 fusion: str = "neutral", rrf_k: int = 60):
        self.units = units
        self.profile = profile_of(units[0].source if units else "", units)
        self.fusion, self.rrf_k = fusion, rrf_k
        built = {}
        self.signals = []
        for name, part in specs:
            if name not in built:
                built[name] = REGISTRY[name](units)
            sig = built[name]
            if sig.active():
                self.signals.append((sig, part))
        self.inactive = [f"{n}[{p}]" for n, p in specs if not built[n].active()]

    def active_signals(self, q: Query) -> list[tuple]:
        out = []
        for sig, part in self.signals:
            v = q.part(part)
            if v and (not isinstance(v, list) or any(str(x).strip() for x in v)):
                out.append((sig, part))
        return out

    def rank(self, q: Query):
        """Full ranking. Returns (order, fused_scores, evidence_ranks)."""
        n = len(self.units)
        sigs = self.active_signals(q)
        contrib = np.zeros((len(sigs), n))
        appl = np.zeros((len(sigs), n), dtype=bool)
        evidence = {}
        for j, (sig, part) in enumerate(sigs):
            sc = sig.score(q.part(part))
            appl[j] = sig.applicable
            if sc:
                idx = np.fromiter(sc.keys(), dtype=int)
                val = np.fromiter(sc.values(), dtype=float)
                order = idx[np.argsort(-val, kind="stable")]
                ranks = np.empty(len(order), dtype=int)
                ranks[:] = np.arange(1, len(order) + 1)
                contrib[j, order] = 1.0 / (self.rrf_k + ranks)
                evidence[f"{sig.name}[{part}]"] = dict(zip(order[:50].tolist(), ranks[:50].tolist()))
        if self.fusion == "neutral" and len(sigs) > 1:
            n_app = appl.sum(axis=0)
            mean_app = np.where(n_app > 0, (contrib * appl).sum(axis=0) / np.maximum(n_app, 1), 0.0)
            fused = np.where(appl, contrib, mean_app[None, :]).sum(axis=0)
        else:
            fused = contrib.sum(axis=0)
        # deterministic tie-break by unit position
        order = np.lexsort((np.arange(n), -fused))
        return order, fused, evidence

    def search(self, q: Query, k: int = 10) -> list[dict]:
        order, fused, evidence = self.rank(q)
        out = []
        for pos, i in enumerate(order[:k]):
            u = self.units[i]
            out.append({"unit_id": u.unit_id, "headword": u.headword, "rank": pos + 1,
                        "score": round(float(fused[i]), 6),
                        "evidence": {s: r[i] for s, r in evidence.items() if i in r}})
        return out

    def rank_of(self, q: Query, unit_id: str) -> int:
        order, _, _ = self.rank(q)
        pos = {self.units[i].unit_id: p for p, i in enumerate(order)}
        return pos[unit_id] + 1
