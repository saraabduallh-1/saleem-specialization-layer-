#!/usr/bin/env python3
"""Interactive smoke test for the current specialization layer.

This is a user-facing tester, not a new experiment. It does not change E8-E10.
Pipeline:
  query understanding -> P-full hybrid retrieval -> top-30 semantic decision
  -> optional S1 corroboration -> structured output.

Use --s1-k to explicitly choose an S1 threshold for hands-on testing. If it is
omitted, the baseline decision is shown together with S1 diagnostics at k=1,3,5,10.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from exp3_common import Engine, load_units  # noqa: E402
from exp3_e2_query_understanding import AR, EN, TEXT3  # noqa: E402
from specialization_layer import decision  # noqa: E402
from specialization_layer.abstention import view_ranks  # noqa: E402
from specialization_layer.engine import query_understanding as qu_mod  # noqa: E402
from spec_layer_v2 import Qwen  # noqa: E402

DOMAIN = "الذكاء الاصطناعي"
KS = (1, 3, 5, 10)


def s1_pass(v: dict, k: int) -> bool:
    return bool(
        v
        and v["text_active"]
        and v["interp_active"]
        and v["text"] <= k
        and v["interp"] <= k
    )


class Layer:
    def __init__(self):
        self.units, _ = load_units("P-full")
        self.engine = Engine(self.units, TEXT3 + AR + EN, fusion="neutral")
        self.qu_llm = Qwen(max_tokens=300)
        self.decision_llm = Qwen(max_tokens=80)

    def run(self, text: str, s1_k: int | None = None) -> dict:
        qu_raw, qu_meta = self.qu_llm(qu_mod.messages(text, DOMAIN))
        qu = qu_mod.parse(qu_raw)

        base = {
            "status": "NONE",
            "input": text,
            "domain": DOMAIN,
            "technical": qu["technical"],
            "query_understanding": {
                "concept_ar": qu["concept_ar"],
                "concept_en": qu["concept_en"],
                "keywords": qu["keywords"],
            },
            "selected": None,
            "s1": None,
            "top_candidates": [],
            "final": None,
            "metadata": {
                "profile": "P-full",
                "retrieval_top_n_for_decision": 30,
                "s1_k_applied": s1_k,
                "query_usage": qu_meta.get("usage"),
            },
        }

        if not qu["technical"]:
            base["reason"] = "query_understanding marked the text non-technical"
            return base

        query = qu_mod.to_query(text, qu, use_en=True)
        order, fused, evidence = self.engine.rank(query)
        order = [int(i) for i in order]
        cands = order[:30]

        base["top_candidates"] = [
            {
                "rank": rank,
                "unit_id": self.units[i].unit_id,
                "term": self.units[i].headword,
                "score": round(float(fused[i]), 6),
            }
            for rank, i in enumerate(order[:5], 1)
        ]

        def call_decision(messages):
            raw, meta = self.decision_llm(messages)
            call_decision.meta = meta
            return raw

        pick, raw = decision.decide(
            call_decision,
            decision.JOINT_SYSTEM,
            text,
            [self.units[i] for i in cands],
        )
        base["metadata"]["decision_usage"] = getattr(call_decision, "meta", {}).get("usage")
        base["decision_raw"] = raw

        if pick is None:
            base["reason"] = "semantic decision returned NONE"
            return base

        chosen_i = cands[pick]
        chosen = self.units[chosen_i]
        views = view_ranks(evidence, chosen_i)
        checks = {str(k): s1_pass(views, k) for k in KS}

        base["selected"] = {
            "unit_id": chosen.unit_id,
            "term": chosen.headword,
            "source": chosen.source,
            "first_stage_rank": order.index(chosen_i) + 1,
        }
        base["s1"] = {
            "view_ranks": views,
            "passes": checks,
        }

        if s1_k is None:
            accepted = True
            reason = "baseline decision shown; S1 is diagnostic only"
        else:
            accepted = checks[str(s1_k)]
            reason = (
                f"selected term passed S1@{s1_k}"
                if accepted
                else f"selected term failed S1@{s1_k}; abstaining"
            )

        base["status"] = "SPECIALIZED" if accepted else "NONE"
        base["final"] = base["selected"] if accepted else None
        base["reason"] = reason
        return base


def print_result(result: dict) -> None:
    print("\n" + "=" * 72)
    print("النص:", result["input"])
    print("تقني؟", "نعم" if result["technical"] else "لا")
    qu = result["query_understanding"]
    if qu["concept_ar"]:
        print("فهم المفهوم:", qu["concept_ar"])
    if result["top_candidates"]:
        print("أعلى المرشحين:")
        for c in result["top_candidates"]:
            print(f"  {c['rank']}. {c['term']}")
    if result["selected"]:
        print("اختيار القرار:", result["selected"]["term"])
        v = result["s1"]["view_ranks"]
        print(f"S1 ranks: text={v['text']} | interpretation={v['interp']}")
        print("S1:", ", ".join(
            f"k={k}:{'PASS' if ok else 'FAIL'}"
            for k, ok in result["s1"]["passes"].items()
        ))
    print("النتيجة النهائية:", result["final"]["term"] if result["final"] else "NONE")
    print("السبب:", result["reason"])
    print("=" * 72)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--text", help="Run one text and exit.")
    ap.add_argument(
        "--s1-k",
        type=int,
        choices=KS,
        default=None,
        help="Apply S1 at k=1,3,5,10. Omit to show baseline + diagnostics only.",
    )
    ap.add_argument("--json", action="store_true", help="Print full structured JSON.")
    args = ap.parse_args()

    print("Loading the current P-full specialization layer...")
    layer = Layer()

    def one(text: str):
        result = layer.run(text.strip(), args.s1_k)
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print_result(result)

    if args.text:
        one(args.text)
        return

    print("جاهز. اكتب نصًا عربيًا لتجربة الطبقة. اكتب exit للخروج.")
    while True:
        try:
            text = input("\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not text:
            continue
        if text.lower() in {"exit", "quit", "q"}:
            break
        one(text)


if __name__ == "__main__":
    main()
