"""Runtime wrapper for trying the current specialization layer on real text.

This is product/testing glue, not a new research experiment. Keep the active
pipeline here so both the web UI and future hosts consume one implementation.

Current active test pipeline:
  P-full query understanding -> hybrid retrieval -> semantic decision over
  top-30 -> S1 corroboration at k=3 -> structured term or NONE.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from exp3_common import Engine, load_units  # noqa: E402
from exp3_e2_query_understanding import AR, EN, TEXT3  # noqa: E402
from specialization_layer import decision  # noqa: E402
from specialization_layer.abstention import view_ranks  # noqa: E402
from specialization_layer.engine import query_understanding as qu_mod  # noqa: E402
from spec_layer_v2 import Qwen  # noqa: E402

DOMAIN = "الذكاء الاصطناعي"
ACTIVE_PROFILE = "P-full"
ACTIVE_S1_K = 3
DECISION_TOP_N = 30


def _s1_pass(v: dict, k: int) -> bool:
    return bool(
        v
        and v["text_active"]
        and v["interp_active"]
        and v["text"] <= k
        and v["interp"] <= k
    )


class SpecializationRuntime:
    """Long-lived runtime so E5 is loaded once and reused between web requests."""

    def __init__(self, s1_k: int = ACTIVE_S1_K):
        self.s1_k = s1_k
        self.units, _ = load_units(ACTIVE_PROFILE)
        self.engine = Engine(self.units, TEXT3 + AR + EN, fusion="neutral")
        self.qu_llm = Qwen(max_tokens=300)
        self.decision_llm = Qwen(max_tokens=80)

    def analyze(self, text: str) -> dict:
        text = (text or "").strip()
        if not text:
            return {"status": "NONE", "term": None, "reason": "empty_input"}

        qu_raw, _ = self.qu_llm(qu_mod.messages(text, DOMAIN))
        qu = qu_mod.parse(qu_raw)

        base = {
            "status": "NONE",
            "term": None,
            "unit_id": None,
            "source": None,
            "technical": qu["technical"],
            "concept_ar": qu["concept_ar"],
            "reason": None,
        }

        if not qu["technical"]:
            base["reason"] = "nontechnical"
            return base

        query = qu_mod.to_query(text, qu, use_en=True)
        order, _, evidence = self.engine.rank(query)
        order = [int(i) for i in order]
        candidates = order[:DECISION_TOP_N]

        def llm(messages):
            raw, _ = self.decision_llm(messages)
            return raw

        pick, _ = decision.decide(
            llm,
            decision.JOINT_SYSTEM,
            text,
            [self.units[i] for i in candidates],
        )
        if pick is None:
            base["reason"] = "decision_none"
            return base

        chosen_i = candidates[pick]
        chosen = self.units[chosen_i]
        views = view_ranks(evidence, chosen_i)

        if not _s1_pass(views, self.s1_k):
            base["reason"] = "s1_rejected"
            return base

        base.update({
            "status": "SPECIALIZED",
            "term": chosen.headword,
            "unit_id": chosen.unit_id,
            "source": chosen.source,
            "reason": "accepted",
        })
        return base
