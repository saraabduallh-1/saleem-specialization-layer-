"""Optional retrieval signals.

Each signal declares the unit roles it needs (`needs_role`) and the query part it
consumes (`query_part`). The engine activates a signal only if the dictionary has
that role for at least one unit AND the query provides that part.

`applicable[i]` is True for units that have the needed role. A signal ranks only
applicable units; whether a non-applicable unit is treated as "missing" (neutral)
or "zero" is decided by the fusion policy, not by the signal.

Every signal returns {unit_index: score} for the units it gives positive evidence
to (dense signals score all applicable units).
"""

from __future__ import annotations

import math
from collections import Counter

import numpy as np

from ..normalize import ar_stem, lexical_terms, norm_en_phrase, tokens
from ..schema import RetrievalUnit
from .embed import encode


class Signal:
    name = "signal"
    needs_role: str | None = None   # None -> every unit (headword) is applicable
    query_part = "text"

    def __init__(self, units: list[RetrievalUnit]):
        self.units = units
        self.applicable = np.array([self.needs_role is None or u.has(self.needs_role) for u in units])
        self.build()

    def build(self):
        pass

    def active(self) -> bool:
        return bool(self.applicable.any())

    def score(self, q) -> dict[int, float]:
        raise NotImplementedError

    def label(self):
        return f"{self.name}[{self.query_part}]"


def _as_list(q):
    if q is None:
        return []
    return [q] if isinstance(q, str) else [x for x in q if x and str(x).strip()]


# ---------------------------------------------------------------- dense

class DenseUnit(Signal):
    """Headword plus definition when the unit has one (headword alone otherwise)."""
    name = "dense_unit"

    def build(self):
        def render(u):
            d = u.get("definition")
            return f"passage: المصطلح: {u.headword}\nالتعريف: {d[0]}" if d else f"passage: المصطلح: {u.headword}"
        self.P = encode([render(u) for u in self.units])

    def score(self, q):
        qs = _as_list(q)
        if not qs:
            return {}
        s = (encode(["query: " + x for x in qs]) @ self.P.T).max(axis=0)
        return {i: float(s[i]) for i in range(len(self.units))}


class DenseDefinition(Signal):
    name = "dense_def"
    needs_role = "definition"

    def build(self):
        self.idx = [i for i, a in enumerate(self.applicable) if a]
        self.P = encode(["passage: " + self.units[i].get("definition")[0] for i in self.idx])

    def score(self, q):
        qs = _as_list(q)
        if not qs or not self.idx:
            return {}
        s = (encode(["query: " + x for x in qs]) @ self.P.T).max(axis=0)
        return {i: float(v) for i, v in zip(self.idx, s)}


class DenseExample(DenseDefinition):
    name = "dense_example"
    needs_role = "example"

    def build(self):
        self.idx, texts = [], []
        for i, u in enumerate(self.units):
            for ex in u.get("example"):
                self.idx.append(i)
                texts.append("passage: " + ex)
        self.P = encode(texts)

    def score(self, q):
        qs = _as_list(q)
        if not qs or not self.idx:
            return {}
        s = (encode(["query: " + x for x in qs]) @ self.P.T).max(axis=0)
        out = {}
        for i, v in zip(self.idx, s):
            out[i] = max(out.get(i, -1.0), float(v))
        return out


class TranslationDense(Signal):
    """Foreign-language concept names vs the unit's translations (any language E5 covers)."""
    name = "translation_dense"
    needs_role = "translation"
    query_part = "concept_en"

    def build(self):
        self.idx, texts = [], []
        for i, u in enumerate(self.units):
            for vs in u.translation.values():
                for v in vs:
                    if v.strip():
                        self.idx.append(i)
                        texts.append("passage: " + v.strip())
        self.P = encode(texts)

    def score(self, q):
        qs = _as_list(q)
        if not qs or not self.idx:
            return {}
        s = (encode(["query: " + x for x in qs]) @ self.P.T).max(axis=0)
        out = {}
        for i, v in zip(self.idx, s):
            out[i] = max(out.get(i, -1.0), float(v))
        return out


# ---------------------------------------------------------------- lexical

class Lexical(Signal):
    """Okapi BM25 over the normalized text of whatever textual roles the unit has."""
    name = "lexical"
    roles = ("definition", "alias", "abbreviation", "example")
    k1, b = 1.2, 0.75

    def build(self):
        self.docs = []
        for u in self.units:
            text = " ".join([u.headword] + [v for r in self.roles for v in u.get(r)])
            self.docs.append(Counter(lexical_terms(text)))
        n = len(self.docs)
        df = Counter(t for d in self.docs for t in d)
        self.idf = {t: math.log(1 + (n - c + 0.5) / (c + 0.5)) for t, c in df.items()}
        self.len = np.array([sum(d.values()) for d in self.docs], dtype=float)
        self.avg = float(self.len.mean())
        self.post = {}
        for i, d in enumerate(self.docs):
            for t in d:
                self.post.setdefault(t, []).append(i)

    def score(self, q):
        terms = [t for x in _as_list(q) for t in lexical_terms(x)]
        out: dict[int, float] = {}
        for t in set(terms):
            for i in self.post.get(t, []):
                tf = self.docs[i][t]
                s = self.idf[t] * tf * (self.k1 + 1) / (tf + self.k1 * (1 - self.b + self.b * self.len[i] / self.avg))
                out[i] = out.get(i, 0.0) + s
        return out


class Surface(Signal):
    """A headword / alias / abbreviation literally present in the query (clitic-tolerant)."""
    name = "surface"

    def build(self):
        self.forms = []
        for i, u in enumerate(self.units):
            for f in [u.headword, *u.get("alias"), *u.get("abbreviation")]:
                toks = [ar_stem(t) for t in tokens(f)]
                if toks:
                    self.forms.append((i, tuple(toks)))

    def score(self, q):
        out: dict[int, float] = {}
        for x in _as_list(q):
            qt = [ar_stem(t) for t in tokens(x)]
            grams = {tuple(qt[j:j + n]) for n in range(1, 8) for j in range(len(qt) - n + 1)}
            for i, f in self.forms:
                if f in grams:
                    out[i] = max(out.get(i, 0.0), float(len(f)))
        return out


class TranslationLexical(Signal):
    """Token-level match of foreign concept names to translations:
    exact = 3, head match (one is the final token sequence of the other) = 2,
    otherwise token Jaccard if >= 0.5."""
    name = "translation_lex"
    needs_role = "translation"
    query_part = "concept_en"

    def build(self):
        self.tr = [(i, norm_en_phrase(v)) for i, u in enumerate(self.units)
                   for vs in u.translation.values() for v in vs if v.strip()]

    def score(self, q):
        out: dict[int, float] = {}
        for c in _as_list(q):
            ct = norm_en_phrase(c)
            if not ct:
                continue
            for i, tt in self.tr:
                if not tt:
                    continue
                if tt == ct:
                    s = 3.0
                elif ct[-len(tt):] == tt or tt[-len(ct):] == ct:
                    s = 2.0
                else:
                    j = len(set(tt) & set(ct)) / len(set(tt) | set(ct))
                    s = j if j >= 0.5 else 0.0
                if s > out.get(i, 0.0):
                    out[i] = s
        return out


REGISTRY = {cls.name: cls for cls in
            (DenseUnit, DenseDefinition, DenseExample, Lexical, Surface, TranslationDense, TranslationLexical)}
