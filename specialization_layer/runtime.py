"""Runtime wrapper for trying the current specialization layer on real text.

This is product/testing glue, not a new research experiment.

Interactive pipeline:
  multi-concept understanding -> P-full hybrid retrieval/decision per concept
  -> S1 corroboration per selected term -> whole-text specialization rewrite.

The research experiments E8-E10 remain unchanged.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from exp3_common import Engine, load_units
from exp3_e2_query_understanding import AR, EN, TEXT3
from specialization_layer import decision, multi_query_understanding
from specialization_layer.abstention import view_ranks
from specialization_layer.engine import query_understanding as qu_mod
from spec_layer_v2 import Qwen, term_present

DOMAIN = "الذكاء الاصطناعي"
ACTIVE_PROFILE = "P-full"
ACTIVE_S1_K = 3
DECISION_TOP_N = 30
MAX_CONCEPTS = 8

WRITER_SYSTEM = (
    "أنت طبقة كتابة عربية تخصصية. أعد صياغة النص كاملًا ليصبح أوضح وأدق تخصصيًا مع الحفاظ الكامل على معناه ونبرته ونوع الكتابة.\n"
    "ستصلك هوية الكتابة المستخرجة من النص، وتخصيصات دلالية معتمدة من المعجم.\n"
    "القواعد:\n"
    "1. حافظ على نوع النص: التقرير يبقى تقريرًا، السؤال يبقى سؤالًا، والمنشور الاجتماعي يبقى طبيعيًا وغير أكاديمي.\n"
    "2. حافظ على السجل اللغوي والغرض ما لم تكن هناك ضرورة لغوية بسيطة.\n"
    "3. استخدم كل مصطلح معتمد في الموضع الذي يعبّر عن معناه، ولا تستبدله بمصطلح آخر.\n"
    "4. لا تضف حقائق أو أسبابًا أو علاقات أو درجة يقين غير موجودة في النص.\n"
    "5. لا تضف تعريفات معجمية ولا تشرح المصطلح إلا إذا كان الشرح موجودًا أصلًا في النص.\n"
    "6. حسّن بقية الصياغة بقدر الحاجة فقط لتكون عربية طبيعية وتخصصية.\n"
    "7. لا تذكر المعجم أو الطبقة أو المرشحين أو عملية الاختيار.\n"
    "8. أعد النص النهائي فقط، بلا مقدمة أو شرح."
)


def _s1_pass(v: dict, k: int) -> bool:
    return bool(
        v
        and v["text_active"]
        and v["interp_active"]
        and v["text"] <= k
        and v["interp"] <= k
    )


def _usable_span(span: str, full_text: str) -> str:
    span = (span or "").strip()
    if len(span.split()) >= 3 and span in full_text:
        return span
    return full_text


def _writer_messages(
    text: str,
    accepted: list[dict],
    writing_profile: dict,
    retry: bool = False,
) -> list[dict]:
    if accepted:
        mappings = "\n".join(
            f"- العبارة: {x['evidence_span'] or x['concept_ar']}\n  المصطلح المعتمد: {x['term']}"
            for x in accepted
        )
    else:
        mappings = "- لا توجد مصطلحات معتمدة؛ حسّن الصياغة فقط من غير اختراع مصطلحات تخصصية."

    style_context = (
        "نوع الكتابة: " + writing_profile.get("writing_type", "أخرى")
        + "\nالسجل اللغوي: " + writing_profile.get("register", "محايد")
        + "\nالغرض: " + writing_profile.get("purpose", "أخرى")
    )
    if writing_profile.get("style_note"):
        style_context += "\nملاحظة الأسلوب: " + writing_profile["style_note"]

    extra = (
        "\nتنبيه: المحاولة السابقة لم تستخدم كل المصطلحات المعتمدة. "
        "يجب أن تظهر المصطلحات المعتمدة نفسها في النص النهائي ما دام معناها موجودًا."
        if retry else ""
    )

    user = (
        "النص الأصلي:\n" + text
        + "\n\nهوية الكتابة التي يجب الحفاظ عليها:\n" + style_context
        + "\n\nالتخصيصات المعتمدة:\n" + mappings
        + extra
    )
    return [
        {"role": "system", "content": WRITER_SYSTEM},
        {"role": "user", "content": user},
    ]


class SpecializationRuntime:
    """Long-lived runtime so E5 is loaded once and reused between web requests."""

    def __init__(self, s1_k: int = ACTIVE_S1_K):
        self.s1_k = s1_k
        self.units, _ = load_units(ACTIVE_PROFILE)
        self.engine = Engine(self.units, TEXT3 + AR + EN, fusion="neutral")
        self.qu_llm = Qwen(max_tokens=500)
        self.decision_llm = Qwen(max_tokens=80)
        self.writer_llm = Qwen(max_tokens=700)

    def _specialize_concept(self, full_text: str, concept: dict) -> dict:
        local_text = _usable_span(concept.get("evidence_span", ""), full_text)
        qu = {
            "concept_ar": concept.get("concept_ar", ""),
            "concept_en": concept.get("concept_en", []),
            "keywords": concept.get("keywords", []),
        }
        query = qu_mod.to_query(local_text, qu, use_en=True)
        order, _, evidence = self.engine.rank(query)
        order = [int(i) for i in order]
        candidates = order[:DECISION_TOP_N]

        def llm(messages):
            raw, _ = self.decision_llm(messages)
            return raw

        pick, _ = decision.decide(
            llm,
            decision.JOINT_SYSTEM,
            local_text,
            [self.units[i] for i in candidates],
        )
        if pick is None:
            return {
                **concept,
                "status": "NONE",
                "term": None,
                "unit_id": None,
                "reason": "decision_none",
            }

        chosen_i = candidates[pick]
        chosen = self.units[chosen_i]
        views = view_ranks(evidence, chosen_i)
        if not _s1_pass(views, self.s1_k):
            return {
                **concept,
                "status": "NONE",
                "term": None,
                "unit_id": None,
                "reason": "s1_rejected",
            }

        return {
            **concept,
            "status": "SPECIALIZED",
            "term": chosen.headword,
            "unit_id": chosen.unit_id,
            "source": chosen.source,
            "reason": "accepted",
        }

    def _rewrite(self, text: str, accepted: list[dict], writing_profile: dict) -> str:
        raw, _ = self.writer_llm(
            _writer_messages(text, accepted, writing_profile, retry=False)
        )
        output = raw.strip()

        missing = [
            x["term"] for x in accepted
            if x.get("term") and not term_present(output, x["term"])
        ]
        if missing:
            raw, _ = self.writer_llm(
                _writer_messages(text, accepted, writing_profile, retry=True)
            )
            output = raw.strip()
        return output or text

    def analyze(self, text: str) -> dict:
        text = (text or "").strip()
        if not text:
            return {
                "status": "NONE",
                "input": "",
                "output": "",
                "domain": DOMAIN,
                "writing_profile": {
                    "writing_type": "أخرى",
                    "register": "محايد",
                    "purpose": "أخرى",
                    "style_note": "",
                },
                "terms": [],
                "concepts": [],
                "reason": "empty_input",
            }

        qu_raw, _ = self.qu_llm(
            multi_query_understanding.messages(text, DOMAIN)
        )
        qu = multi_query_understanding.parse(qu_raw, max_concepts=MAX_CONCEPTS)

        writing_profile = {
            "writing_type": qu.get("writing_type", "أخرى"),
            "register": qu.get("register", "محايد"),
            "purpose": qu.get("purpose", "أخرى"),
            "style_note": qu.get("style_note", ""),
        }

        concept_results = []
        if qu["technical"]:
            for concept in qu["concepts"]:
                concept_results.append(self._specialize_concept(text, concept))

        accepted = []
        seen_units = set()
        for x in concept_results:
            if x.get("status") != "SPECIALIZED" or not x.get("unit_id"):
                continue
            if x["unit_id"] in seen_units:
                continue
            seen_units.add(x["unit_id"])
            accepted.append(x)

        output = self._rewrite(text, accepted, writing_profile)

        return {
            "status": "SPECIALIZED" if accepted else "REWRITTEN",
            "input": text,
            "output": output,
            "domain": DOMAIN,
            "writing_profile": writing_profile,
            "terms": [
                {
                    "term": x["term"],
                    "unit_id": x["unit_id"],
                    "source": x.get("source"),
                    "evidence_span": x.get("evidence_span", ""),
                }
                for x in accepted
            ],
            "concepts": concept_results,
            "reason": "accepted_terms_and_rewritten" if accepted else "rewritten_without_accepted_term",
        }
