"""Protected text-centered decision (S4) for development experiments.

S4 is intentionally asymmetric:
- the existing baseline decision is protected;
- a challenger may replace it only with explicit semantic evidence from the input text;
- otherwise the system keeps the baseline or abstains.

This module does not modify the frozen E8/E9 selectors.
"""

from __future__ import annotations

import json
import re

from .decision import render_candidate
from .schema import RetrievalUnit

RELATIONS = {"EXACT", "BROADER", "NARROWER", "RELATED", "CONTRADICTED", "NONE"}

SYSTEM = (
    "أمامك نص، وقرار حالي من النظام (BASELINE)، ومجموعة مفاهيم مرشحة من المعجم. "
    "مهمتك ليست البحث عن مصطلح قريب فقط، بل التحقق هل يجب الاحتفاظ بقرار BASELINE أو تغييره أو الامتناع.\n\n"
    "صنّف علاقة كل مفهوم مهم بالنص بهذه المعاني:\n"
    "- EXACT: النص يثبت المفهوم نفسه بخصائصه المميزة.\n"
    "- BROADER: المفهوم أعم من المقصود.\n"
    "- NARROWER: المفهوم أخص ويتطلب تفصيلًا غير موجود في النص.\n"
    "- RELATED: مرتبط بالموضوع لكنه ليس المفهوم الموصوف.\n"
    "- CONTRADICTED: لا يناسب معنى النص.\n\n"
    "قاعدة الحماية الأساسية:\n"
    "لا تغيّر BASELINE لمجرد أن هناك مرشحًا يبدو أكثر تخصصًا أو أشهر أو أقرب موضوعيًا. "
    "التغيير مسموح فقط إذا كان BASELINE ليس EXACT، ويوجد مرشح آخر EXACT بوضوح، "
    "ويمكن الاستشهاد بعبارة قصيرة موجودة فعلًا في النص تبيّن سبب التمييز.\n\n"
    "قواعد مهمة:\n"
    "1. لا تستنتج تفاصيل غير مكتوبة: إذا احتاج المرشح إلى تدرجات، إعادة تدريب، بنية محددة، "
    "نوع خوارزمية، آلية تحديث، أو شرط إضافي غير مذكور فهو NARROWER وليس EXACT.\n"
    "2. إذا كان BASELINE نفسه EXACT فاحتفظ به حتى لو وُجد مرشح قريب آخر.\n"
    "3. إذا كان الفرق بين المرشحين غير محسوم من النص، اختر NONE بدل التغيير.\n"
    "4. evidence_span يجب أن يكون اقتباسًا قصيرًا من النص نفسه (2 إلى 12 كلمة) "
    "يثبت الخاصية التي تجعل البديل أدق من BASELINE. لا تكتب تعريفًا من عندك.\n"
    "5. ترتيب المرشحين لا يدل على الأفضلية.\n\n"
    "أعد JSON فقط بأحد الأشكال التالية:\n"
    '{"action":"KEEP","choice":"C3","baseline_relation":"EXACT","choice_relation":"EXACT",'
    '"ambiguous":false,"evidence_span":"","reason":"سبب مختصر"}\n'
    '{"action":"CHANGE","choice":"C7","baseline_relation":"BROADER","choice_relation":"EXACT",'
    '"ambiguous":false,"evidence_span":"عبارة من النص","reason":"سبب مختصر"}\n'
    '{"action":"NONE","choice":"NONE","baseline_relation":"RELATED","choice_relation":"NONE",'
    '"ambiguous":true,"evidence_span":"","reason":"سبب مختصر"}'
)

_DIAC = re.compile(r"[\u0610-\u061A\u064B-\u065F\u0670\u06D6-\u06EDـ]")
_WORD = re.compile(r"[ء-يA-Za-z0-9]+")


def _norm_words(text: str) -> list[str]:
    text = _DIAC.sub("", text)
    text = re.sub("[إأآٱ]", "ا", text)
    text = text.replace("ى", "ي").replace("ة", "ه").replace("ؤ", "و").replace("ئ", "ي")
    return [x.lower() for x in _WORD.findall(text)]


def evidence_valid(span: str, text: str) -> bool:
    """Accept a short copied span only when it is genuinely present in the input."""
    sw = _norm_words(span)
    tw = _norm_words(text)
    if not (2 <= len(sw) <= 12) or not tw or len(sw) >= len(tw):
        return False
    n = len(sw)
    return any(tw[i:i + n] == sw for i in range(len(tw) - n + 1))


def messages(text: str, units: list[RetrievalUnit], baseline_index: int | None) -> list[dict]:
    baseline_label = f"C{baseline_index + 1}" if baseline_index is not None else "NONE"
    blocks = [
        "النص:\n" + text,
        "قرار BASELINE الحالي: " + baseline_label,
        "المرشحون (الترتيب محايد ولا يدل على الأفضلية):",
    ]
    blocks.extend(render_candidate(i, u, max_words=24) for i, u in enumerate(units, 1))
    return [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": "\n\n".join(blocks)},
    ]


def _json_obj(raw: str) -> dict:
    s = raw.strip().replace("\`\`\`json", "").replace("\`\`\`", "")
    try:
        m = re.search(r"\{.*\}", s, flags=re.S)
        return json.loads(m.group(0)) if m else {}
    except Exception:
        return {}


def _idx(value: str, k: int) -> int | None:
    m = re.fullmatch(r"C(\d+)", value.strip().upper())
    if m and 1 <= int(m.group(1)) <= k:
        return int(m.group(1)) - 1
    return None


def parse(
    raw: str,
    text: str,
    k: int,
    baseline_index: int | None,
) -> tuple[int | None, dict]:
    """Apply the protected decision deterministically.

    If a proposed change does not satisfy every guardrail, fall back to the
    baseline. A model-proposed NONE cannot erase an EXACT baseline.
    """
    obj = _json_obj(raw)
    action = str(obj.get("action", "KEEP")).strip().upper()
    choice_s = str(obj.get("choice", "NONE")).strip().upper()
    baseline_relation = str(obj.get("baseline_relation", "NONE")).strip().upper()
    choice_relation = str(obj.get("choice_relation", "NONE")).strip().upper()
    ambiguous = obj.get("ambiguous", True)
    if isinstance(ambiguous, str):
        ambiguous = ambiguous.strip().lower() not in {"false", "0", "no"}
    else:
        ambiguous = bool(ambiguous)
    span = str(obj.get("evidence_span", "")).strip()
    reason = str(obj.get("reason", "")).strip()
    choice_i = _idx(choice_s, k)
    ev_ok = evidence_valid(span, text) if span else False

    valid_relation = baseline_relation in RELATIONS and choice_relation in RELATIONS
    result = baseline_index
    resolution = "fallback_keep_baseline" if baseline_index is not None else "fallback_none"

    if valid_relation:
        if action == "KEEP":
            result = baseline_index
            resolution = "keep_baseline"
        elif action == "NONE":
            if baseline_index is not None and baseline_relation == "EXACT":
                result = baseline_index
                resolution = "protect_exact_baseline"
            else:
                result = None
                resolution = "abstain"
        elif action == "CHANGE":
            change_ok = (
                choice_i is not None
                and choice_i != baseline_index
                and choice_relation == "EXACT"
                and baseline_relation != "EXACT"
                and not ambiguous
                and ev_ok
            )
            if change_ok:
                result = choice_i
                resolution = "validated_change"
            else:
                result = baseline_index
                resolution = "blocked_change_keep_baseline" if baseline_index is not None else "blocked_change_none"

    meta = {
        "action": action,
        "choice": choice_s,
        "baseline_relation": baseline_relation,
        "choice_relation": choice_relation,
        "ambiguous": ambiguous,
        "evidence_span": span,
        "evidence_valid": ev_ok,
        "reason": reason,
        "resolution": resolution,
        "parse_valid": bool(valid_relation and action in {"KEEP", "CHANGE", "NONE"}),
    }
    return result, meta


def decide(
    llm,
    text: str,
    units: list[RetrievalUnit],
    baseline_index: int | None,
) -> tuple[int | None, dict, str]:
    raw = llm(messages(text, units, baseline_index))
    idx, meta = parse(raw, text, len(units), baseline_index)
    return idx, meta, raw
