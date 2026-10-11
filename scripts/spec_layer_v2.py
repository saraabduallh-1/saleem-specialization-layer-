#!/usr/bin/env python3
"""Shared utilities for the v2 specialization-layer experiments.

Contents
- dictionary loading with Siwar redirect ("انظر") resolution
- cached E5 retrieval over a chosen candidate pool (pilot-50 or full dictionary)
- morphology-tolerant canonical-term matcher (evaluation and deterministic checks)
- instruction-leak / definitional-framing detectors
- a thin Qwen call wrapper (temperature, thinking flag and token limit fixed by caller)

Expected/Gold labels are never used by anything that builds a prompt.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import time
from pathlib import Path

import numpy as np

from run_qwen_domain_ablation import (
    DEFAULT_BASE_URL, DEFAULT_MODEL, call_with_retry, extract_output,
    load_dotenv, load_json, save_json,
)

ROOT = Path(__file__).resolve().parents[1]
BASE_TERMS = ROOT / "data/processed/data_ai/terminology_base.json"
PILOT_TERMS = ROOT / "data/processed/data_ai/terminology_pilot_50.json"
DOMAIN = ROOT / "data/domain/saleem_domain_knowledge_v1.json"
EVAL_36 = ROOT / "data/evaluation/ai_final_layer_eval_v1.json"
GOLD_50 = ROOT / "data/gold_test/data_ai_retrieval_gold_50.json"
PROBES = ROOT / "data/evaluation/ai_abstention_probes_v1.json"
EMB_CACHE = ROOT / ".cache/embeddings"
RETRIEVAL_MODEL = "intfloat/multilingual-e5-large"

# --------------------------------------------------------------------------
# Arabic normalization and morphology-tolerant term matching
# --------------------------------------------------------------------------

DIAC = re.compile(r"[ؐ-ًؚ-ٰٟۖ-ۭـ]")
TOKEN = re.compile(r"[ء-يa-zA-Z0-9]+")

# Proclitics: conjunction (و/ف) + preposition (ب/ك/ل) + article (ال), and the
# contracted لل (ل + ال). Order matters only for efficiency.
PREFIXES = sorted({
    a + b + c
    for a in ("", "و", "ف")
    for b in ("", "ب", "ك", "ل")
    for c in ("", "ال")
} | {"لل", "ولل", "فلل"}, key=len, reverse=True)
# Inflectional endings handled: accusative tanween alif (after diacritic
# removal), sound feminine plural, dual/sound masculine plural, nisba-ya
# spelling variant, and attached pronouns on the final token.
SUFFIXES = ("", "ا", "ات", "ان", "ين", "ون", "ي", "ه", "ها", "هم", "هما")


def norm(text: str) -> str:
    text = DIAC.sub("", text)
    text = re.sub("[إأآٱ]", "ا", text)
    text = text.replace("ى", "ي").replace("ة", "ه").replace("ؤ", "و").replace("ئ", "ي")
    return text.lower()


def tokens(text: str) -> list[str]:
    return TOKEN.findall(norm(text))


def _bases(token: str) -> set[str]:
    out = set()
    for p in PREFIXES:
        if p and not token.startswith(p):
            continue
        stem = token[len(p):]
        if len(stem) < 2:
            continue
        for s in SUFFIXES:
            if s and not stem.endswith(s):
                continue
            core = stem[: len(stem) - len(s)] if s else stem
            if len(core) >= 2:
                out.add(core)
                if s == "ات":          # شبكات -> شبكه
                    out.add(core + "ه")
    return out


def _term_tokens(term: str) -> list[str]:
    toks = tokens(term)
    out = []
    for t in toks:
        out.append(t[2:] if t.startswith("ال") and len(t) > 3 else t)
    return out


def term_spans(text: str, term: str) -> list[tuple[int, int]]:
    """Token spans in text matching the term up to clitics/inflection."""
    tt = _term_tokens(term)
    if not tt:
        return []
    xs = tokens(text)
    bases = [_bases(x) | {x} for x in xs]
    spans = []
    for i in range(len(xs) - len(tt) + 1):
        if all(tt[j] in bases[i + j] for j in range(len(tt))):
            spans.append((i, i + len(tt)))
    return spans


def term_present(text: str, term: str) -> bool:
    return bool(term_spans(text, term))


def naive_present(text: str, term: str) -> bool:
    """The previous experiments' substring metric, kept for comparison."""
    def n(s):
        s = DIAC.sub("", s).replace("ـ", "")
        s = re.sub("[إأآٱ]", "ا", s).replace("ى", "ي")
        return " ".join(s.lower().split())
    return bool(term) and n(term) in n(text)


# Hard leaks: pipeline/meta language that never belongs in the user's text.
META_LEAK = [
    "المصطلح المعتمد", "المصطلح المختار", "تم التحقق", "التحقق الدلالي",
    "النص الاصلي", "النص النهائي", "النص المحسن", "الصياغه", "التعليمات",
    "معجم سوار", "المصطلحات المرشحه",
]
# Definitional framing: dictionary-style insertion of the term or its definition.
DEFN_FRAMING = [
    "يعرف بانه", "يعرف بانها", "تعرف بانها", "تعرف بانه", "يعرف ب", "يعرف علي انه",
    "يطلق عليه", "يطلق عليها", "وهو ما يعرف", "وهي ما يعرف", "ما يعرف ب",
    "يشير الي", "تشير الي", "مصطلح",
]


def meta_leak(text: str) -> list[str]:
    t = " ".join(tokens(text))
    return [m for m in META_LEAK if " ".join(tokens(m)) in t]


def definitional_framing(text: str) -> list[str]:
    t = " " + " ".join(tokens(text)) + " "
    return [m for m in DEFN_FRAMING if " " + " ".join(tokens(m)) in t]


# --------------------------------------------------------------------------
# Dictionary with redirect resolution
# --------------------------------------------------------------------------

def _key(term: str) -> str:
    return " ".join(tokens(term))


class Dictionary:
    """Siwar entries; redirect entries ("انظر X") resolve to their canonical entry.

    Redirect resolution is taken from the source itself (canonical_term field
    extracted by prepare_terminology.py); nothing is added by hand.
    """

    def __init__(self, entries: list[dict]):
        self.entries = entries
        self.by_id = {e["id"]: e for e in entries}
        by_key = {_key(e["term"]): e for e in entries}
        self.canonical_of = {}
        for e in entries:
            target = e.get("canonical_term")
            if target and _key(target) in by_key:
                self.canonical_of[e["id"]] = by_key[_key(target)]["id"]
            else:
                self.canonical_of[e["id"]] = e["id"]
        # Only non-redirect entries are retrieval candidates; a redirect's
        # surface form is attached to its canonical entry as a source variant.
        self.candidates = [e for e in entries if self.canonical_of[e["id"]] == e["id"]]
        self.variants = {e["id"]: [] for e in self.candidates}
        for e in entries:
            c = self.canonical_of[e["id"]]
            if c != e["id"]:
                self.variants[c].append(e["term"])

    def resolve(self, entry_id: str | None) -> str | None:
        return self.canonical_of.get(entry_id, entry_id) if entry_id else None

    def accepted_forms(self, entry_id: str) -> list[str]:
        e = self.by_id[entry_id]
        return [e["term"], *(e.get("aliases") or []), *self.variants.get(entry_id, [])]


def load_pool(name: str) -> Dictionary:
    if name == "pilot50":
        return Dictionary(load_json(PILOT_TERMS))
    if name == "full":
        return Dictionary(load_json(BASE_TERMS))
    raise ValueError(name)


# --------------------------------------------------------------------------
# Retrieval (E5-large, term + original Siwar definition)
# --------------------------------------------------------------------------

def passage_text(e: dict, rep: str = "term_def") -> str:
    if rep == "term_def":
        return f"passage: المصطلح: {e['term']}\nالتعريف: {e['definition']}"
    if rep == "term_en_def":
        en = f" ({e['english_term'].strip()})" if (e.get("english_term") or "").strip() else ""
        return f"passage: المصطلح: {e['term']}{en}\nالتعريف: {e['definition']}"
    raise ValueError(rep)


_MODEL = None


def e5():
    global _MODEL
    if _MODEL is None:
        import torch
        from sentence_transformers import SentenceTransformer
        device = "cuda" if torch.cuda.is_available() else (
            "mps" if torch.backends.mps.is_available() else "cpu")
        _MODEL = SentenceTransformer(RETRIEVAL_MODEL, device=device)
        _MODEL._spec_device = device
    return _MODEL


def encode(texts: list[str]) -> np.ndarray:
    """E5 encoding with an on-disk cache keyed by the exact input strings."""
    h = hashlib.sha256(("\x1e".join(texts) + RETRIEVAL_MODEL).encode()).hexdigest()[:20]
    path = EMB_CACHE / f"{h}.npy"
    if path.exists():
        return np.load(path)
    vecs = e5().encode(texts, batch_size=32, convert_to_numpy=True,
                       normalize_embeddings=True, show_progress_bar=len(texts) > 64)
    EMB_CACHE.mkdir(parents=True, exist_ok=True)
    np.save(path, vecs)
    return vecs


class Retriever:
    def __init__(self, pool: Dictionary, rep: str = "term_def", hubness: bool = False):
        self.pool = pool
        self.rep = rep
        self.p = encode([passage_text(e, rep) for e in pool.candidates])
        self.penalty = np.zeros(len(pool.candidates))
        if hubness:
            # CSLS-style hubness correction (Conneau et al., 2018). Background
            # queries are the dictionary's own definitions encoded as queries:
            # independent of every evaluation set. penalty(p) = mean cosine of
            # passage p to its 10 nearest background queries.
            bg_entries = load_pool("full").candidates
            bg = encode(["query: " + e["definition"] for e in bg_entries])
            sims = self.p @ bg.T
            k = 10
            self.penalty = np.sort(sims, axis=1)[:, -k:].mean(axis=1)

    def search(self, texts: list[str], k: int) -> list[list[dict]]:
        q = encode(["query: " + t for t in texts])
        scores = q @ self.p.T - 0.5 * self.penalty[None, :]
        out = []
        for i in range(len(texts)):
            order = np.argsort(-scores[i])
            row = []
            for idx in order[:k]:
                e = self.pool.candidates[int(idx)]
                row.append({"id": e["id"], "term": e["term"], "definition": e["definition"],
                            "score": round(float(scores[i, int(idx)]), 6)})
            out.append(row)
        return out

    def rank_of(self, texts: list[str], expected_ids: list[str | None]) -> list[int | None]:
        q = encode(["query: " + t for t in texts])
        scores = q @ self.p.T - 0.5 * self.penalty[None, :]
        pos = {e["id"]: i for i, e in enumerate(self.pool.candidates)}
        ranks = []
        for i, eid in enumerate(expected_ids):
            eid = self.pool.resolve(eid)
            if eid is None or eid not in pos:
                ranks.append(None)
                continue
            s = scores[i, pos[eid]]
            ranks.append(int((scores[i] > s).sum()) + 1)
        return ranks


def hit_summary(ranks: list[int], ks=(1, 3, 5, 10, 20)) -> dict:
    n = len(ranks)
    out = {"n": n}
    for k in ks:
        out[f"hit_at_{k}"] = round(sum(r <= k for r in ranks) / n, 4)
    out["mrr"] = round(sum(1 / r for r in ranks) / n, 4)
    return out


# --------------------------------------------------------------------------
# Evaluation sets
# --------------------------------------------------------------------------

def load_eval_items(which: str) -> list[dict]:
    """Uniform item format: id, set, kind, text, expected_term_id, expected_term."""
    if which == "dev36":
        d = load_json(EVAL_36)
        return [{"id": x["id"], "set": "dev36", "kind": x["kind"], "text": x["text"],
                 "expected_term_id": x.get("expected_term_id"),
                 "expected_term": x.get("expected_term")} for x in d["items"]]
    if which == "gold50":
        d = load_json(GOLD_50)
        return [{"id": x["query_id"], "set": "gold50", "kind": "positive", "text": x["query"],
                 "expected_term_id": x["expected_id"], "expected_term": x["expected_term"]}
                for x in d["queries"]]
    if which == "probes":
        d = load_json(PROBES)
        return [{"id": x["id"], "set": "probes", "kind": x["kind"], "text": x["text"],
                 "expected_term_id": None, "expected_term": None} for x in d["items"]]
    raise ValueError(which)


# --------------------------------------------------------------------------
# Qwen wrapper
# --------------------------------------------------------------------------

class Qwen:
    def __init__(self, temperature=0.0, max_tokens=320, retries=-1, retry_wait=20):
        load_dotenv(ROOT / ".env")
        self.api_key = os.getenv("SALEEM_API_KEY", "").strip()
        if not self.api_key:
            raise SystemExit("Missing SALEEM_API_KEY in local environment")
        self.base_url = os.getenv("SALEEM_BASE_URL", DEFAULT_BASE_URL).strip()
        self.model = os.getenv("SALEEM_MODEL", DEFAULT_MODEL).strip()
        self.temperature, self.max_tokens = temperature, max_tokens
        self.retries, self.retry_wait = retries, retry_wait

    def __call__(self, messages: list[dict]) -> tuple[str, dict]:
        t0 = time.perf_counter()
        resp = call_with_retry(
            base_url=self.base_url, api_key=self.api_key, model=self.model,
            messages=messages, temperature=self.temperature,
            max_tokens=self.max_tokens, timeout=180,
            retries=self.retries, retry_wait=self.retry_wait)
        out = extract_output(resp)
        finish = (resp.get("choices") or [{}])[0].get("finish_reason")
        if finish == "length":
            raise RuntimeError("Output hit max_tokens")
        low = out.lstrip().lower()
        if low.startswith("thinking process:") or "<think>" in low:
            raise RuntimeError("Thinking content leaked into output")
        return out, {"finish_reason": finish, "usage": resp.get("usage"),
                     "elapsed_seconds": round(time.perf_counter() - t0, 3)}

    def meta(self) -> dict:
        return {"model": self.model, "temperature": self.temperature,
                "max_tokens": self.max_tokens, "enable_thinking": False}


def parse_json_obj(raw: str) -> dict:
    s = raw.strip().replace("```json", "").replace("```", "").strip()
    try:
        return json.loads(s)
    except Exception:
        m = re.search(r"\{.*\}", s, flags=re.S)
        if not m:
            raise ValueError(f"No JSON object in: {raw!r}")
        return json.loads(m.group(0))


__all__ = [n for n in dir() if not n.startswith("_")] + ["load_json", "save_json"]
