"""Multi-concept understanding for interactive/product use.

This is not part of the frozen research experiments. It extracts every
independent technical concept actually described in the text so the runtime can
specialize more than one concept in a single passage.
"""

from __future__ import annotations

import json
import re

SYSTEM_TEMPLATE = (
    "أنت تحلل نصًا في مجال: {domain}. استخرج كل مفهوم تقني مستقل يصفه النص فعلًا ويمكن أن يكون له مصطلح تخصصي، "
    "ولا تكتفِ بالمفهوم الأبرز فقط. لا تستخرج كلمات عامة أو أسماء أدوات لمجرد ورودها. "
    "إذا احتوى النص على عدة مفاهيم، أعدها كلها، كل مفهوم مرة واحدة فقط.\n"
    "لكل مفهوم أعد:\n"
    "- concept_ar: وصف عربي فصيح وموجز للمعنى المقصود، لا اسم مصطلح محفوظ بالضرورة.\n"
    "- concept_en: من صفر إلى ثلاثة أسماء إنجليزية محتملة للمفهوم.\n"
    "- keywords: حتى خمس كلمات/عبارات عربية تساعد على الاسترجاع.\n"
    "- evidence_span: أقصر عبارة من النص الأصلي تثبت هذا المفهوم، من دون إعادة صياغة.\n"
    "إذا لم يوجد أي مفهوم تقني تخصصي فأعد concepts كقائمة فارغة.\n"
    "أعد JSON فقط بمفتاح technical وقائمة concepts، وكل عنصر فيها يحتوي concept_ar وconcept_en وkeywords وevidence_span."
)


def messages(text: str, domain: str) -> list[dict]:
    return [
        {"role": "system", "content": SYSTEM_TEMPLATE.format(domain=domain)},
        {"role": "user", "content": "النص:\n" + text},
    ]


def _clean_list(v, n):
    if isinstance(v, str):
        v = [v]
    return [str(x).strip() for x in (v or []) if str(x).strip()][:n]


def parse(raw: str, max_concepts: int = 8) -> dict:
    s = raw.strip().replace("~~~json", "").replace("~~~", "").strip()
    try:
        obj = json.loads(s)
    except Exception:
        m = re.search(r"\\{.*\\}", s, flags=re.S)
        obj = json.loads(m.group(0)) if m else {}

    out = []
    seen = set()
    for c in obj.get("concepts") or []:
        if not isinstance(c, dict):
            continue
        ar = str(c.get("concept_ar") or "").strip()
        span = str(c.get("evidence_span") or "").strip()
        if not ar:
            continue
        key = (ar, span)
        if key in seen:
            continue
        seen.add(key)
        out.append({
            "concept_ar": ar,
            "concept_en": _clean_list(c.get("concept_en"), 3),
            "keywords": _clean_list(c.get("keywords"), 5),
            "evidence_span": span,
        })
        if len(out) >= max_concepts:
            break

    tech_flag = obj.get("technical")
    technical = bool(out) and (
        tech_flag is True or str(tech_flag).lower() == "true"
    )
    return {"technical": technical, "concepts": out}
