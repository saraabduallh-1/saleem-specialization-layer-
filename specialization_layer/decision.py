"""Decision layer: choose one retrieved unit or NONE. Dictionary-agnostic.

Candidates are rendered only from the roles each unit has:
  المصطلح (always) / المقابل (if a translation exists) / التعريف (if a definition exists)
  / مثال (only if no definition but an example exists).
The LLM is injected by the caller: llm(messages) -> str.
"""

from __future__ import annotations

import json
import re

from .schema import RetrievalUnit

RULES = (
    "1. اختر مرشحًا فقط إذا كان النص يذكر الخصائص الجوهرية الواردة في وصفه، ولو بألفاظ عامة أو عامية.\n"
    "2. لا يكفي اشتراك كلمة أو تقارب الموضوع. الكلمة التي تُستعمل في النص بمعناها العام أو اليومي لا تبرر المصطلح.\n"
    "3. إذا انطبق أكثر من مرشح فاختر الأدق: لا تختر مفهومًا أعمّ إذا وُجد مرشح أخصّ تنطبق خصائصه على النص، "
    "ولا تختر مفهومًا أخصّ إذا كان النص لا يذكر ما يميّزه.\n"
    "4. إذا كان النص مبهمًا أو لا يحدد المفهوم بما يكفي فاختر NONE.\n"
)

# Same rules as the v2 selector (sel_v2), with generic field wording.
SELECTOR_SYSTEM = (
    "مهمتك أن تقرر هل يعبّر النص عن أحد المفاهيم المرشحة من معجم المصطلحات.\nالقواعد:\n" + RULES +
    "أعد JSON فقط بالشكل: {\"choice\": \"C1\"} مع رقم المرشح المختار أو NONE."
)

JOINT_SYSTEM = (
    "أمامك نص وقائمة مرشحين مسترجعة آليًا من معجم مصطلحات، مرتبة ترتيبًا تقريبيًا وقد يكون المرشح الصحيح في أي موضع منها، "
    "وقد لا يكون فيها أصلًا. قيّم المرشحين كلهم مقابل معنى النص، ثم قرر.\nالقواعد:\n" + RULES +
    "أعد JSON فقط بالشكل: {\"choice\": \"C7\"} مع رقم المرشح الأنسب أو NONE."
)


def render_candidate(i: int, u: RetrievalUnit, max_words: int = 40) -> str:
    lines = [f"C{i}", f"المصطلح: {u.headword}"]
    tr = [v for vs in u.translation.values() for v in vs if v.strip()]
    if tr:
        lines.append(f"المقابل: {tr[0]}")
    d = u.get("definition")
    if d:
        lines.append("التعريف: " + " ".join(d[0].split()[:max_words]))
    elif u.get("example"):
        lines.append("مثال: " + " ".join(u.get("example")[0].split()[:max_words]))
    return "\n".join(lines)


def messages(system: str, text: str, units: list[RetrievalUnit]) -> list[dict]:
    blocks = ["النص:\n" + text, "المرشحون:"] + [render_candidate(i, u) for i, u in enumerate(units, 1)]
    return [{"role": "system", "content": system}, {"role": "user", "content": "\n\n".join(blocks)}]


def parse_choice(raw: str, k: int) -> int | None:
    """Return candidate index (0-based) or None for NONE/unparseable."""
    s = raw.strip().replace("```json", "").replace("```", "")
    try:
        choice = str(json.loads(re.search(r"\{.*\}", s, flags=re.S).group(0)).get("choice", "")).strip().upper()
    except Exception:
        m = re.search(r"\bC(\d+)\b|NONE", s.upper())
        choice = m.group(0) if m else "NONE"
    m = re.fullmatch(r"C?(\d+)", choice)
    if m and 1 <= int(m.group(1)) <= k:
        return int(m.group(1)) - 1
    return None


def decide(llm, system: str, text: str, units: list[RetrievalUnit]) -> tuple[int | None, str]:
    raw = llm(messages(system, text, units))
    return parse_choice(raw, len(units)), raw
