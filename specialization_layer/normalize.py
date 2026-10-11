"""Language-level text normalization (no dictionary-specific logic)."""

from __future__ import annotations

import re

_DIAC = re.compile(r"[ؐ-ًؚ-ٰٟۖ-ۭـ]")
_TOKEN = re.compile(r"[ء-يa-zA-Z0-9]+")
_AR_PREFIXES = ("وبال", "وكال", "فبال", "وال", "فال", "بال", "كال", "لل", "ال")
# Short Arabic function words; removing them only affects the lexical signal.
_AR_STOP = set("""
في من على الى عن مع هذا هذه ذلك تلك التي الذي الذين او ثم قد لا ما لم لن ان كان كانت
هو هي هم نحن انا انت كل بعض اي حتى عند بين بعد قبل اذا لكن بل غير مثل عبر حول ضمن
و ف ب ل ك يتم تم يكون تكون اللي عشان بس شي وش
""".split())
_EN_STOP = {"the", "a", "an", "of", "for", "and", "or", "in", "on", "to", "with", "by"}


def norm_ar(text: str) -> str:
    text = _DIAC.sub("", text)
    text = re.sub("[إأآٱ]", "ا", text)
    return text.replace("ى", "ي").replace("ة", "ه").replace("ؤ", "و").replace("ئ", "ي").lower()


def tokens(text: str) -> list[str]:
    return _TOKEN.findall(norm_ar(text))


def ar_stem(tok: str) -> str:
    """Light stemming: strip one article/clitic prefix and the accusative alif."""
    for p in _AR_PREFIXES:
        if tok.startswith(p) and len(tok) - len(p) >= 2:
            tok = tok[len(p):]
            break
    if len(tok) > 3 and tok.endswith("ا"):
        tok = tok[:-1]
    return tok


def lexical_terms(text: str) -> list[str]:
    out = []
    for t in tokens(text):
        if t in _AR_STOP or t in _EN_STOP or len(t) < 2:
            continue
        out.append(ar_stem(t) if re.match(r"[ء-ي]", t) else en_stem(t))
    return out


def en_stem(w: str) -> str:
    w = w.lower()
    return w[:-1] if len(w) > 4 and w.endswith("s") and not w.endswith("ss") else w


_EN_EXPAND = {"ai": "artificial intelligence"}


def norm_en_phrase(text: str) -> list[str]:
    """Lower-case English tokens with plural stripping and common abbreviation expansion."""
    text = re.sub(r"\(.*?\)", " ", text or "").lower()
    words = []
    for w in re.findall(r"[a-z0-9]+", text):
        words.extend(_EN_EXPAND.get(w, w).split())
    return [en_stem(w) for w in words if w not in _EN_STOP]
