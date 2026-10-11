"""Dictionary-agnostic query understanding.

One LLM call turns the user text into a structured concept representation. The
engine uses only the parts the current dictionary can consume (e.g. concept_en is
ignored for a dictionary without translations). The LLM is injected by the caller
(`llm(messages) -> str`), so the engine has no dependency on a specific provider.
"""

from __future__ import annotations

import json
import re

from .retriever import Query

SYSTEM_TEMPLATE = (
    "أنت مساعد لفهم النصوص في مجال: {domain}. اقرأ النص وحدد المفهوم المتخصص الذي يصفه فعلًا، إن وُجد، "
    "معتمدًا على المعنى الكامل للنص لا على كلمة مفردة لها معنى عام.\n"
    "أعد JSON فقط بالشكل:\n"
    "{{\"technical\": true, \"concept_ar\": \"...\", \"concept_en\": [\"...\"], \"keywords\": [\"...\"]}}\n"
    "- technical: هل يصف النص مفهومًا متخصصًا في هذا المجال؟\n"
    "- concept_ar: وصف موجز للمفهوم بالعربية الفصحى بأسلوب تعريف معجمي متخصص.\n"
    "- concept_en: من اسم إلى ثلاثة أسماء إنجليزية للمفهوم، من الأدق إلى الأعم.\n"
    "- keywords: حتى خمس كلمات أو عبارات عربية تخصصية تدل على المفهوم.\n"
    "إذا لم يصف النص مفهومًا متخصصًا في المجال فاجعل technical=false واترك الحقول الأخرى فارغة."
)


def messages(text: str, domain: str) -> list[dict]:
    return [{"role": "system", "content": SYSTEM_TEMPLATE.format(domain=domain)},
            {"role": "user", "content": "النص:\n" + text}]


def parse(raw: str) -> dict:
    s = raw.strip().replace("```json", "").replace("```", "").strip()
    try:
        obj = json.loads(s)
    except Exception:
        m = re.search(r"\{.*\}", s, flags=re.S)
        obj = json.loads(m.group(0)) if m else {}

    def lst(v, n):
        if isinstance(v, str):
            v = [v]
        return [str(x).strip() for x in (v or []) if str(x).strip()][:n]
    tech = obj.get("technical")
    return {"technical": tech is True or str(tech).lower() == "true",
            "concept_ar": str(obj.get("concept_ar") or "").strip(),
            "concept_en": lst(obj.get("concept_en"), 3),
            "keywords": lst(obj.get("keywords"), 5)}


def to_query(text: str, qu: dict, use_ar=True, use_en=True, use_kw=True) -> Query:
    return Query(text=text,
                 concept_ar=qu.get("concept_ar") if use_ar else None,
                 keywords=qu.get("keywords") if use_kw else None,
                 concept_en=qu.get("concept_en") if use_en else None)
