"""Text-centered contrastive decision for development experiments.

This module deliberately does not replace the frozen selector in decision.py.
It compares a text-derived candidate pool directly against the user's text and
rejects broader, narrower, merely related, or ambiguous matches.
"""

from __future__ import annotations

import json
import re

from .decision import render_candidate
from .schema import RetrievalUnit

RELATIONS = {"EXACT", "BROADER", "NARROWER", "RELATED", "CONTRADICTED"}

SYSTEM = (
    "أمامك نص ومجموعة مفاهيم مرشحة من معجم متخصص. المطلوب تحديد المفهوم الذي يعبّر عنه النص تحديدًا، "
    "لا المفهوم الأقرب موضوعيًا فقط. قارن المرشحين بالنص نفسه وبالفروق بينهم.\n\n"
    "صنّف العلاقة ذهنيًا بهذه الفئات:\n"
    "- EXACT: النص يذكر الخصائص الجوهرية التي تميز المفهوم نفسه.\n"
    "- BROADER: المفهوم أعم من المقصود في النص.\n"
    "- NARROWER: المفهوم أخص ويحتاج تفصيلًا أو شرطًا غير موجود في النص.\n"
    "- RELATED: المفهوم مرتبط بالموضوع لكنه ليس ما يصفه النص.\n"
    "- CONTRADICTED: النص لا يناسب المفهوم.\n\n"
    "قواعد القرار:\n"
    "1. لا تستنتج تفاصيل تنفيذية غير مذكورة في النص. إذا كان المرشح يحتاج خطوة مثل إعادة تدريب، تدرجات، "
    "نوع خوارزمية محدد، أو بنية محددة ولم يذكرها النص، فهو NARROWER وليس EXACT.\n"
    "2. لا تختَر مفهومًا عامًا إذا كان هناك مفهوم أدق وتدعمه تفاصيل النص كاملة.\n"
    "3. لا تختَر اسم مجموعة بيانات أو نموذج أو طريقة بعينها لمجرد أن وصفها قريب؛ يجب أن يثبت النص خصائصها المميزة.\n"
    "4. إذا كان أكثر من مرشح يمكن اعتباره EXACT بنفس الدرجة، أو كان الفرق بين أفضل مرشحين غير محسوم من النص، اختر NONE.\n"
    "5. إذا لم يوجد EXACT واضح، اختر NONE.\n"
    "6. ترتيب المرشحين لا يدل على الأفضلية.\n\n"
    "أعد JSON فقط بهذا الشكل:\n"
    '{"choice":"C4","choice_relation":"EXACT","runner_up":"C2",'
    '"runner_up_relation":"BROADER","ambiguous":false,"reason":"سبب مختصر"}\n'
    "أو إذا لا يوجد اختيار وحيد واضح:\n"
    '{"choice":"NONE","choice_relation":"NONE","runner_up":"C2",'
    '"runner_up_relation":"RELATED","ambiguous":true,"reason":"سبب مختصر"}'
)


def messages(text: str, units: list[RetrievalUnit]) -> list[dict]:
    # Candidate order is supplied by the caller and should not encode retrieval rank.
    blocks = ["النص:\n" + text, "المرشحون (الترتيب عشوائي/محايد ولا يدل على الأفضلية):"]
    blocks.extend(render_candidate(i, u, max_words=35) for i, u in enumerate(units, 1))
    return [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": "\n\n".join(blocks)},
    ]


def _json_obj(raw: str) -> dict:
    s = raw.strip().replace("```json", "").replace("```", "")
    try:
        m = re.search(r"\{.*\}", s, flags=re.S)
        return json.loads(m.group(0)) if m else {}
    except Exception:
        return {}


def parse(raw: str, k: int) -> tuple[int | None, dict]:
    """Parse a conservative S3 decision.

    A candidate is accepted only when the model explicitly marks it EXACT and
    ambiguous=false. Malformed, out-of-range, or ambiguous responses abstain.
    """
    obj = _json_obj(raw)
    choice = str(obj.get("choice", "NONE")).strip().upper()
    relation = str(obj.get("choice_relation", "NONE")).strip().upper()
    ambiguous = obj.get("ambiguous", True)
    if isinstance(ambiguous, str):
        ambiguous = ambiguous.strip().lower() not in {"false", "0", "no"}
    else:
        ambiguous = bool(ambiguous)

    idx = None
    m = re.fullmatch(r"C(\d+)", choice)
    if m and 1 <= int(m.group(1)) <= k:
        idx = int(m.group(1)) - 1

    accepted = idx is not None and relation == "EXACT" and not ambiguous
    meta = {
        "choice": choice,
        "choice_relation": relation,
        "runner_up": str(obj.get("runner_up", "NONE")).strip().upper(),
        "runner_up_relation": str(obj.get("runner_up_relation", "NONE")).strip().upper(),
        "ambiguous": ambiguous,
        "reason": str(obj.get("reason", "")).strip(),
        "parse_valid": bool(idx is not None or choice == "NONE"),
        "accepted": accepted,
    }
    return (idx if accepted else None), meta


def decide(llm, text: str, units: list[RetrievalUnit]) -> tuple[int | None, dict, str]:
    raw = llm(messages(text, units))
    idx, meta = parse(raw, len(units))
    return idx, meta, raw
