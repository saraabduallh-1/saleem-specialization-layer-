"""S2 — contrastive decision (heldout_v1 PREREGISTRATION §4A, amendment A1). FROZEN.

Implements §4A exactly; do not edit (any change is a new mechanism version):
- competitors: the 3 units most similar to c* by cosine of the engine's dense_unit
  embeddings, over the whole dictionary, excluding c*; ties by unit_id
- contrast set {c*} + competitors, shown sorted by unit_id as C1..C4
- rendering: المصطلح / أسماء أخرى (<=3 aliases) / المقابل (first translation) /
  التعريف (first 40 words) / مثال (first example, first 25 words); missing roles omitted
- verbatim system prompt below; user message "النص:\n<text>\n\nالمفاهيم:\n\n" + blocks
- max_tokens 150 (set by the caller's LLM), temperature 0, thinking disabled
- output: chosen unit, or NONE if choice invalid/NONE, evidence empty, evidence not a
  substring of the text after normalization, or evidence equal to the whole text
"""

from __future__ import annotations

import json
import re

import numpy as np

from .schema import RetrievalUnit

N_COMPETITORS = 3
MAX_TOKENS = 150

SYSTEM = (
    "أمامك نص ومجموعة صغيرة من المفاهيم المتقاربة من معجم مصطلحات. هذه المفاهيم متشابهة عمدًا، والمطلوب التمييز بينها.\n"
    "لكل مفهوم، حدّد ما يميّزه عن بقية المفاهيم في المجموعة، ثم ابحث في النص عن دليل على هذه الخاصية المميّزة تحديدًا.\n"
    "اختر مفهومًا فقط إذا كان النص يحتوي على دليل يدعمه هو دون المفاهيم الأخرى في المجموعة.\n"
    "إذا كان النص ينطبق على أكثر من مفهوم بالقدر نفسه، أو لا يذكر ما يميّز أيًّا منها، أو لا يعبّر عن أيٍّ منها، فاختر NONE.\n"
    "أعد JSON فقط بالشكل: {\"choice\": \"C2\", \"evidence\": \"عبارة منقولة حرفيًا من النص تدل على الخاصية المميّزة\"} "
    "أو {\"choice\": \"NONE\", \"evidence\": \"\"}."
)

_DIAC = re.compile(r"[ؐ-ًؚ-ٰٟ]")


def normalize(s: str) -> str:
    """§4A normalization: diacritics removed, alef/ya/ta-marbuta unified, whitespace collapsed."""
    s = _DIAC.sub("", s)
    s = re.sub("[إأآٱ]", "ا", s).replace("ى", "ي").replace("ة", "ه")
    return " ".join(s.split())


def competitors(unit_vectors: np.ndarray, units: list[RetrievalUnit], c_index: int) -> list[int]:
    sims = unit_vectors @ unit_vectors[c_index]
    order = sorted((i for i in range(len(units)) if i != c_index),
                   key=lambda i: (-float(sims[i]), units[i].unit_id))
    return order[:N_COMPETITORS]


def render(i: int, u: RetrievalUnit) -> str:
    lines = [f"C{i}", f"المصطلح: {u.headword}"]
    aliases = u.get("alias")[:3]
    if aliases:
        lines.append("أسماء أخرى: " + "، ".join(aliases))
    tr = [v for vs in u.translation.values() for v in vs if v.strip()]
    if tr:
        lines.append(f"المقابل: {tr[0]}")
    d = u.get("definition")
    if d:
        lines.append("التعريف: " + " ".join(d[0].split()[:40]))
    ex = u.get("example")
    if ex:
        lines.append("مثال: " + " ".join(ex[0].split()[:25]))
    return "\n".join(lines)


def contrast_set(unit_vectors, units, c_index) -> list[int]:
    return sorted([c_index] + competitors(unit_vectors, units, c_index), key=lambda i: units[i].unit_id)


def messages(text: str, units: list[RetrievalUnit], idxs: list[int]) -> list[dict]:
    blocks = "\n\n".join(render(n, units[i]) for n, i in enumerate(idxs, 1))
    return [{"role": "system", "content": SYSTEM},
            {"role": "user", "content": "النص:\n" + text + "\n\nالمفاهيم:\n\n" + blocks}]


def apply_rules(raw: str, text: str, idxs: list[int]) -> tuple[int | None, str]:
    """Return (unit index or None, reason)."""
    s = raw.strip().replace("```json", "").replace("```", "")
    try:
        obj = json.loads(re.search(r"\{.*\}", s, flags=re.S).group(0))
    except Exception:
        return None, "unparseable"
    choice = str(obj.get("choice", "")).strip().upper()
    m = re.fullmatch(r"C([1-9])", choice)
    if not m or not 1 <= int(m.group(1)) <= len(idxs):
        return None, "choice_none_or_invalid"
    ev = normalize(str(obj.get("evidence") or ""))
    if not ev:
        return None, "evidence_empty"
    t = normalize(text)
    if ev not in t:
        return None, "evidence_not_in_text"
    if ev == t:
        return None, "evidence_is_whole_text"
    return idxs[int(m.group(1)) - 1], "accepted"


def decide(llm, text: str, units: list[RetrievalUnit], unit_vectors: np.ndarray, c_index: int):
    """llm(messages) -> str. Returns (unit index or None, reason, contrast idxs, raw)."""
    idxs = contrast_set(unit_vectors, units, c_index)
    raw = llm(messages(text, units, idxs))
    pick, reason = apply_rules(raw, text, idxs)
    return pick, reason, idxs, raw
