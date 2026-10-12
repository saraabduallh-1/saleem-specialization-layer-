"""Multi-concept and writing-profile understanding for interactive/product use.

This is not part of the frozen research experiments. It extracts every
independent technical concept actually described in the text and also classifies
the writing form/register so the final rewrite preserves the user's intended
genre rather than forcing every input into one formal style.
"""

from __future__ import annotations

import json
import re

WRITING_TYPES = {
    "تقرير تقني",
    "سؤال مطوّر",
    "منشور اجتماعي",
    "دعم أو منتج",
    "مقال أو شرح",
    "توثيق تقني",
    "رسالة عمل",
    "أخرى",
}

REGISTERS = {
    "رسمي",
    "شبه رسمي",
    "تقني مباشر",
    "عامي سعودي",
    "مختلط عربي/إنجليزي",
    "محايد",
}

PURPOSES = {
    "خبري",
    "تحليلي",
    "استفساري",
    "إرشادي",
    "تفسيري",
    "ترويجي",
    "حل مشكلة",
    "أخرى",
}

SYSTEM_TEMPLATE = (
    "أنت تحلل نصًا في مجال: {domain}. المطلوب مهمتان في استجابة واحدة:\n"
    "أولًا: صنّف طريقة الكتابة كما هي في النص الأصلي، ولا تحولها تلقائيًا إلى كتابة أكاديمية.\n"
    "writing_type يجب أن يكون واحدًا من: تقرير تقني، سؤال مطوّر، منشور اجتماعي، دعم أو منتج، "
    "مقال أو شرح، توثيق تقني، رسالة عمل، أخرى.\n"
    "register يجب أن يكون واحدًا من: رسمي، شبه رسمي، تقني مباشر، عامي سعودي، مختلط عربي/إنجليزي، محايد.\n"
    "purpose يجب أن يكون واحدًا من: خبري، تحليلي، استفساري، إرشادي، تفسيري، ترويجي، حل مشكلة، أخرى.\n"
    "style_note: جملة عربية قصيرة تصف كيف ينبغي الحفاظ على أسلوب النص عند إعادة صياغته.\n\n"
    "ثانيًا: استخرج كل مفهوم تقني مستقل يصفه النص فعلًا ويمكن أن يكون له مصطلح تخصصي، "
    "ولا تكتفِ بالمفهوم الأبرز فقط. لا تستخرج كلمات عامة أو أسماء أدوات لمجرد ورودها. "
    "إذا احتوى النص على عدة مفاهيم، أعدها كلها، كل مفهوم مرة واحدة فقط.\n"
    "لكل مفهوم أعد:\n"
    "- concept_ar: وصف عربي فصيح وموجز للمعنى المقصود، لا اسم مصطلح محفوظ بالضرورة.\n"
    "- concept_en: من صفر إلى ثلاثة أسماء إنجليزية محتملة للمفهوم.\n"
    "- keywords: حتى خمس كلمات/عبارات عربية تساعد على الاسترجاع.\n"
    "- evidence_span: أقصر عبارة من النص الأصلي تثبت هذا المفهوم، من دون إعادة صياغة.\n"
    "إذا لم يوجد أي مفهوم تقني تخصصي فأعد concepts كقائمة فارغة.\n"
    "أعد JSON فقط بالمفاتيح: technical, writing_type, register, purpose, style_note, concepts."
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


def _choice(value, allowed, default):
    value = str(value or "").strip()
    return value if value in allowed else default


def parse(raw: str, max_concepts: int = 8) -> dict:
    s = raw.strip().replace("~~~json", "").replace("~~~", "")
    s = s.replace("```json", "").replace("```", "").strip()
    try:
        obj = json.loads(s)
    except Exception:
        m = re.search(r"\{.*\}", s, flags=re.S)
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

    return {
        "technical": technical,
        "writing_type": _choice(obj.get("writing_type"), WRITING_TYPES, "أخرى"),
        "register": _choice(obj.get("register"), REGISTERS, "محايد"),
        "purpose": _choice(obj.get("purpose"), PURPOSES, "أخرى"),
        "style_note": str(obj.get("style_note") or "").strip(),
        "concepts": out,
    }
