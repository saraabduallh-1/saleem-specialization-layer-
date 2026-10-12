#!/usr/bin/env python3
"""E10: protected contrastive decision (S4), development-only.

Designed after inspecting E8 and E9, so this is NOT independent evidence.

S4 keeps the E8 baseline as a protected anchor. It sees a broader first-stage
top-30 candidate pool (plus the baseline if needed), with rank hidden. A
challenger can replace the baseline only when Qwen marks:
- baseline != EXACT,
- challenger == EXACT,
- ambiguous == false,
- and supplies a short evidence span that is verified against the input text.

Otherwise S4 keeps the baseline. S1 is then evaluated unchanged.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from exp3_common import Engine, load_units  # noqa: E402
from exp3_e2_query_understanding import AR, EN, TEXT3  # noqa: E402
from specialization_layer import protected_decision  # noqa: E402
from specialization_layer.abstention import view_ranks  # noqa: E402
from specialization_layer.engine import query_understanding as qu_mod  # noqa: E402
from spec_layer_v2 import Qwen, load_json, save_json  # noqa: E402

DATA = ROOT / "evaluation/heldout_v1/source_grounded_draft/heldout_source_grounded_balanced_100_v1.json"
E8 = ROOT / "results/e8_source_grounded_positive_100/per_item_results.json"
E9 = ROOT / "results/e9_text_centered_decision/per_item_results.json"
OUT = ROOT / "results/e10_protected_decision"
CACHE = OUT / "llm_calls_cache.json"
KS = (1, 3, 5, 10)
PROFILES = {"P-full": (TEXT3 + AR + EN, True), "P-def": (TEXT3 + AR, False)}
STYLE_GROUP = {"formal_technical": "reports_formal", "report_technical": "reports_formal",
               "developer_question": "developer", "developer_issue": "developer",
               "social_tech": "social", "social_saudi": "social", "product_support": "product_support"}


class S4LLM:
    def __init__(self):
        self.cache = load_json(CACHE) if CACHE.exists() else {}
        self.client = Qwen(max_tokens=240)
        self.new_calls = 0
        self.last = {}

    def __call__(self, msgs):
        key = hashlib.sha256(
            json.dumps(["s4", self.client.max_tokens, msgs], ensure_ascii=False).encode()
        ).hexdigest()[:24]
        if key not in self.cache:
            out, meta = self.client(msgs)
            self.cache[key] = {"stage": "s4", "output": out, "meta": meta}
            save_json(self.cache, CACHE)
            self.new_calls += 1
        self.last = self.cache[key]["meta"]
        return self.cache[key]["output"]


def sha(s: str) -> str:
    return hashlib.sha256(s.encode()).hexdigest()[:16]


def passes(v, k: int) -> bool:
    return bool(v) and v["text_active"] and v["interp_active"] and v["text"] <= k and v["interp"] <= k


def outcome(sel, gold):
    return "none" if not sel else ("correct" if sel == gold else "wrong")


def safe_div(a, b):
    return round(a / b, 3) if b else None


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    data = load_json(DATA)
    e8_rows = {x["item_id"]: x for x in load_json(E8)}
    e9_rows = {(x["item_id"], x["profile"]): x for x in load_json(E9)} if E9.exists() else {}
    items = data["items"]
    llm = S4LLM()

    per_item = []
    for prof, (specs, use_en) in PROFILES.items():
        units, _ = load_units(prof)
        eng = Engine(units, specs, fusion="neutral")
        uidx = {u.unit_id: i for i, u in enumerate(units)}

        for n, it in enumerate(items, 1):
            iid, text = it["item_id"], it["draft_text_ar"]
            prev = e8_rows[iid]
            qu = prev["query_understanding"]
            e8rec = prev["profiles"][prof]
            gold_i = uidx[it["unit_id"]]

            order, _, ev = eng.rank(qu_mod.to_query(text, qu, use_en=use_en))
            order = [int(i) for i in order]
            gold_rank = order.index(gold_i) + 1

            baseline_id = e8rec["c_star"]
            baseline_i = uidx[baseline_id] if baseline_id in uidx else None

            # Broader than E9: first-stage top 30. Always retain the baseline
            # candidate as the protected anchor even if it lies outside top 30.
            pool = list(order[:30])
            if baseline_i is not None and baseline_i not in pool:
                pool.append(baseline_i)

            # Hide first-stage rank. The model only knows which candidate is the
            # current baseline; it does not know retrieval positions.
            pool = sorted(set(pool), key=lambda i: units[i].unit_id)
            baseline_pool_i = pool.index(baseline_i) if baseline_i is not None else None

            s4_id = s4_head = None
            meta = {
                "resolution": "technical_gate_false",
                "action": "NONE",
                "evidence_valid": False,
            }
            raw = None
            views = None
            if prev["technical"]:
                pick, meta, raw = protected_decision.decide(
                    llm, text, [units[i] for i in pool], baseline_pool_i
                )
                if pick is not None:
                    chosen_i = pool[pick]
                    s4_id, s4_head = units[chosen_i].unit_id, units[chosen_i].headword
                    views = view_ranks(ev, chosen_i)

            e9rec = e9_rows.get((iid, prof), {})
            per_item.append({
                "item_id": iid,
                "profile": prof,
                "style_group": STYLE_GROUP[it["style_profile"]],
                "text": text,
                "gold_unit_id": it["unit_id"],
                "gold_headword": it["gold_headword"],
                "first_stage_rank": gold_rank,
                "gold_in_s4_pool": gold_i in pool,
                "s4_pool_n": len(pool),
                "baseline": baseline_id,
                "baseline_headword": e8rec["c_star_headword"],
                "s3_e9": e9rec.get("s3"),
                "s3_e9_headword": e9rec.get("s3_headword"),
                "s4": s4_id,
                "s4_headword": s4_head,
                "s4_meta": meta,
                "s4_raw": raw,
                "views_s4": views,
                "latency_s": (llm.last or {}).get("elapsed_seconds") if raw is not None else None,
                "prompt_tokens": ((llm.last or {}).get("usage") or {}).get("prompt_tokens") if raw is not None else None,
            })
            if n % 20 == 0:
                print(f"  {prof} {n}/100; new S4 calls={llm.new_calls}", flush=True)

    summary, style = {}, {}
    for prof in PROFILES:
        recs = [r for r in per_item if r["profile"] == prof]
        selections = {
            "baseline_E8": {r["item_id"]: r["baseline"] for r in recs},
            "S4": {r["item_id"]: r["s4"] for r in recs},
        }
        if any(r["s3_e9"] is not None for r in recs):
            selections["S3_E9_reference"] = {r["item_id"]: r["s3_e9"] for r in recs}
        for k in KS:
            selections[f"S4+S1@k={k}"] = {
                r["item_id"]: r["s4"] if passes(r["views_s4"], k) else None for r in recs
            }

        prof_sum = {
            "n": len(recs),
            "first_stage": {
                "hit@1": safe_div(sum(r["first_stage_rank"] <= 1 for r in recs), len(recs)),
                "hit@3": safe_div(sum(r["first_stage_rank"] <= 3 for r in recs), len(recs)),
                "hit@5": safe_div(sum(r["first_stage_rank"] <= 5 for r in recs), len(recs)),
                "hit@10": safe_div(sum(r["first_stage_rank"] <= 10 for r in recs), len(recs)),
                "hit@30": safe_div(sum(r["first_stage_rank"] <= 30 for r in recs), len(recs)),
                "mrr": round(float(np.mean([1 / r["first_stage_rank"] for r in recs])), 4),
            },
            "gold_in_s4_pool": sum(r["gold_in_s4_pool"] for r in recs),
            "s4_resolutions": dict(Counter(r["s4_meta"].get("resolution") for r in recs)),
            "s4_evidence_valid": sum(bool(r["s4_meta"].get("evidence_valid")) for r in recs),
            "settings": {},
        }

        base = selections["baseline_E8"]
        for name, sel in selections.items():
            oc = Counter(outcome(sel[r["item_id"]], r["gold_unit_id"]) for r in recs)
            c, w, ne = oc["correct"], oc["wrong"], oc["none"]
            out = {
                "correct": c,
                "wrong": w,
                "none": ne,
                "precision": safe_div(c, c + w),
                "coverage": safe_div(c, len(recs)),
            }
            if name not in {"baseline_E8", "S3_E9_reference"}:
                bo = {r["item_id"]: outcome(base[r["item_id"]], r["gold_unit_id"]) for r in recs}
                so = {r["item_id"]: outcome(sel[r["item_id"]], r["gold_unit_id"]) for r in recs}
                out.update({
                    "corrected_wrong": sum(bo[i] == "wrong" and so[i] == "correct" for i in bo),
                    "correct_to_wrong": sum(bo[i] == "correct" and so[i] == "wrong" for i in bo),
                    "correct_to_none": sum(bo[i] == "correct" and so[i] == "none" for i in bo),
                    "wrong_to_none": sum(bo[i] == "wrong" and so[i] == "none" for i in bo),
                })
            prof_sum["settings"][name] = out

        for group in ("reports_formal", "developer", "social", "product_support"):
            sub = [r for r in recs if r["style_group"] == group]
            g = style.setdefault(prof, {}).setdefault(group, {"n": len(sub)})
            for name, sel in selections.items():
                oc = Counter(outcome(sel[r["item_id"]], r["gold_unit_id"]) for r in sub)
                g[name] = {
                    "correct": oc["correct"],
                    "wrong": oc["wrong"],
                    "none": oc["none"],
                    "precision": safe_div(oc["correct"], oc["correct"] + oc["wrong"]),
                    "coverage": safe_div(oc["correct"], len(sub)),
                }
        summary[prof] = prof_sum

    transitions = []
    for r in per_item:
        b = outcome(r["baseline"], r["gold_unit_id"])
        s = outcome(r["s4"], r["gold_unit_id"])
        if b != s or r["baseline"] != r["s4"]:
            transitions.append({
                "item_id": r["item_id"],
                "profile": r["profile"],
                "style_group": r["style_group"],
                "text": r["text"],
                "expected": r["gold_headword"],
                "baseline": r["baseline_headword"] or "NONE",
                "baseline_outcome": b,
                "s4": r["s4_headword"] or "NONE",
                "s4_outcome": s,
                "first_stage_rank": r["first_stage_rank"],
                "gold_in_s4_pool": r["gold_in_s4_pool"],
                "action": r["s4_meta"].get("action"),
                "resolution": r["s4_meta"].get("resolution"),
                "baseline_relation": r["s4_meta"].get("baseline_relation"),
                "choice_relation": r["s4_meta"].get("choice_relation"),
                "evidence_span": r["s4_meta"].get("evidence_span"),
                "evidence_valid": r["s4_meta"].get("evidence_valid"),
                "reason": r["s4_meta"].get("reason"),
            })

    cfg = {
        "experiment": "E10 protected contrastive decision (S4)",
        "status": "DEVELOPMENT ONLY: designed after inspecting E8 and E9; not independent evaluation",
        "code_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "dataset": str(DATA.relative_to(ROOT)),
        "dataset_sha256": hashlib.sha256(DATA.read_bytes()).hexdigest(),
        "e8_results": str(E8.relative_to(ROOT)),
        "e9_results": str(E9.relative_to(ROOT)),
        "model": llm.client.model,
        "temperature": 0.0,
        "enable_thinking": False,
        "max_tokens": {"s4": llm.client.max_tokens},
        "retriever": "intfloat/multilingual-e5-large",
        "s4_candidate_pool": "first-stage top30 UNION E8 baseline; deduplicated; sorted by unit_id to hide retrieval rank",
        "s4_change_guard": "baseline!=EXACT AND challenger==EXACT AND ambiguous=false AND verified 2-12-word evidence span",
        "s4_prompt_sha256_16": sha(protected_decision.SYSTEM),
        "s1": "unchanged; applied after S4 at k=1,3,5,10",
        "methodological_warning": "E10 is tuning/development on exposed pilot items. A fresh untouched held-out set is required after architecture freeze.",
    }

    save_json(cfg, OUT / "run_config.json")
    save_json(summary, OUT / "summary.json")
    save_json(per_item, OUT / "per_item_results.json")
    save_json(transitions, OUT / "transitions.json")
    save_json(style, OUT / "style_breakdown.json")

    lines = [
        "# E10 — Protected contrastive decision (S4)",
        "",
        "> **Development only.** S4 was designed after inspecting E8 and E9.",
        "> These numbers are not held-out evidence and must not be used for final success criteria.",
        "",
        "## Mechanism",
        "",
        "S4 protects the E8 baseline. A challenger may replace it only when the model says the baseline is not EXACT, "
        "the challenger is EXACT, the case is unambiguous, and a short evidence span is verified against the input text.",
        "The candidate pool is widened to first-stage Top-30 plus the baseline, with retrieval rank hidden.",
        "",
        "## Results",
        "",
        "| Profile | Setting | Correct | Wrong | NONE | Precision | Coverage |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for prof in PROFILES:
        for name, v in summary[prof]["settings"].items():
            lines.append(
                f"| {prof} | {name} | {v['correct']} | {v['wrong']} | {v['none']} | "
                f"{v['precision']} | {v['coverage']} |"
            )
    lines += ["", "## Protection summary", ""]
    for prof in PROFILES:
        s = summary[prof]["settings"]["S4"]
        lines.append(
            f"- **{prof}:** corrected wrong={s['corrected_wrong']}, correct→wrong={s['correct_to_wrong']}, "
            f"correct→NONE={s['correct_to_none']}, wrong→NONE={s['wrong_to_none']}; "
            f"gold present in S4 pool={summary[prof]['gold_in_s4_pool']}/100; "
            f"resolutions={summary[prof]['s4_resolutions']}."
        )
    lines += [
        "",
        "## Interpretation guardrail",
        "",
        "Even if S4 improves on E8/E9, treat it only as a development signal because the mechanism was created from those observed errors. "
        "Freeze the architecture before evaluating on a fresh untouched held-out set.",
    ]
    (OUT / "REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"\nNew S4 API calls: {llm.new_calls}")
    print(f"Results written to {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
