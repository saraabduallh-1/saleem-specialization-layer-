#!/usr/bin/env python3
"""E9: text-centered contrastive decision (S3) development follow-up.

IMPORTANT: E9 is a development/ablation experiment designed after inspecting
E8 errors. It reuses the E8 100-item positive pilot and therefore is NOT an
independent evaluation and MUST NOT be reported as held-out performance.

Frozen pieces are left untouched. S3 is added only as an experimental decision
stage:
  1) Recompute deterministic first-stage retrieval using E8's stored query
     understanding (no new QU calls).
  2) Build a text-centered candidate pool = first-stage top-10 UNION the E8
     baseline decision candidate. This also lets P-def recover candidates that
     its reranker demoted.
  3) Hide rank by sorting candidates by unit_id and make one new Qwen call that
     classifies exact/broader/narrower/related/contradicted relations.
  4) Accept only a unique explicit EXACT; otherwise NONE.
  5) Report S3 alone and S3 + the unchanged S1 corroboration at k=1/3/5/10.

The company API key remains local; the script reads the existing local env in
exactly the same way as prior experiments and never prints it.
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
from specialization_layer import text_centered  # noqa: E402
from specialization_layer.abstention import view_ranks  # noqa: E402
from specialization_layer.engine import query_understanding as qu_mod  # noqa: E402
from specialization_layer.engine.signals import DenseUnit  # noqa: E402
from spec_layer_v2 import Qwen, load_json, save_json  # noqa: E402

DATA = ROOT / "evaluation/heldout_v1/source_grounded_draft/heldout_source_grounded_balanced_100_v1.json"
E8 = ROOT / "results/e8_source_grounded_positive_100/per_item_results.json"
OUT = ROOT / "results/e9_text_centered_decision"
CACHE = OUT / "llm_calls_cache.json"
KS = (1, 3, 5, 10)
PROFILES = {"P-full": (TEXT3 + AR + EN, True), "P-def": (TEXT3 + AR, False)}
STYLE_GROUP = {"formal_technical": "reports_formal", "report_technical": "reports_formal",
               "developer_question": "developer", "developer_issue": "developer",
               "social_tech": "social", "social_saudi": "social", "product_support": "product_support"}


class S3LLM:
    def __init__(self):
        self.cache = load_json(CACHE) if CACHE.exists() else {}
        self.client = Qwen(max_tokens=220)
        self.new_calls = 0
        self.last = {}

    def __call__(self, msgs):
        key = hashlib.sha256(json.dumps(["s3", self.client.max_tokens, msgs], ensure_ascii=False).encode()).hexdigest()[:24]
        if key not in self.cache:
            out, meta = self.client(msgs)
            self.cache[key] = {"stage": "s3", "output": out, "meta": meta}
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
    items = data["items"]
    llm = S3LLM()

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

            baseline_id = e8rec["c_star"]
            baseline_i = uidx[baseline_id] if baseline_id in uidx else None

            # Text-derived pool: first-stage top 10, plus the previous baseline
            # nomination if it fell outside top 10. No semantic neighbours around
            # the selected term are injected (the failure mode of S2).
            pool = list(order[:10])
            if baseline_i is not None and baseline_i not in pool:
                pool.append(baseline_i)
            # Hide retrieval rank from the decision model.
            pool = sorted(set(pool), key=lambda i: units[i].unit_id)

            s3_id = s3_head = None
            meta, raw = {"accepted": False, "reason": "technical gate=false"}, None
            views = None
            if prev["technical"]:
                pick, meta, raw = text_centered.decide(llm, text, [units[i] for i in pool])
                if pick is not None:
                    chosen_i = pool[pick]
                    s3_id, s3_head = units[chosen_i].unit_id, units[chosen_i].headword
                    views = view_ranks(ev, chosen_i)

            gold_rank = order.index(gold_i) + 1
            rec = {
                "item_id": iid,
                "profile": prof,
                "style_group": STYLE_GROUP[it["style_profile"]],
                "text": text,
                "gold_unit_id": it["unit_id"],
                "gold_headword": it["gold_headword"],
                "first_stage_rank": gold_rank,
                "gold_in_s3_pool": gold_i in pool,
                "s3_pool_n": len(pool),
                "s3_pool": [{"unit_id": units[i].unit_id, "headword": units[i].headword} for i in pool],
                "baseline": baseline_id,
                "baseline_headword": e8rec["c_star_headword"],
                "s3": s3_id,
                "s3_headword": s3_head,
                "s3_meta": meta,
                "s3_raw": raw,
                "views_s3": views,
                "latency_s": (llm.last or {}).get("elapsed_seconds") if raw is not None else None,
                "prompt_tokens": ((llm.last or {}).get("usage") or {}).get("prompt_tokens") if raw is not None else None,
            }
            per_item.append(rec)
            if n % 20 == 0:
                print(f"  {prof} {n}/100; new S3 calls={llm.new_calls}", flush=True)

    summary, style = {}, {}
    for prof in PROFILES:
        recs = [r for r in per_item if r["profile"] == prof]
        selections = {
            "baseline_E8": {r["item_id"]: r["baseline"] for r in recs},
            "S3": {r["item_id"]: r["s3"] for r in recs},
        }
        for k in KS:
            selections[f"S3+S1@k={k}"] = {
                r["item_id"]: r["s3"] if passes(r["views_s3"], k) else None for r in recs
            }

        prof_sum = {
            "n": len(recs),
            "first_stage": {
                "hit@1": safe_div(sum(r["first_stage_rank"] <= 1 for r in recs), len(recs)),
                "hit@3": safe_div(sum(r["first_stage_rank"] <= 3 for r in recs), len(recs)),
                "hit@5": safe_div(sum(r["first_stage_rank"] <= 5 for r in recs), len(recs)),
                "hit@10": safe_div(sum(r["first_stage_rank"] <= 10 for r in recs), len(recs)),
                "mrr": round(float(np.mean([1 / r["first_stage_rank"] for r in recs])), 4),
            },
            "gold_in_s3_pool": sum(r["gold_in_s3_pool"] for r in recs),
            "settings": {},
        }
        base = selections["baseline_E8"]
        for name, sel in selections.items():
            oc = Counter(outcome(sel[r["item_id"]], r["gold_unit_id"]) for r in recs)
            c, w, ne = oc["correct"], oc["wrong"], oc["none"]
            out = {"correct": c, "wrong": w, "none": ne,
                   "precision": safe_div(c, c + w), "coverage": safe_div(c, len(recs))}
            if name != "baseline_E8":
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
                g[name] = {"correct": oc["correct"], "wrong": oc["wrong"], "none": oc["none"],
                           "precision": safe_div(oc["correct"], oc["correct"] + oc["wrong"]),
                           "coverage": safe_div(oc["correct"], len(sub))}
        summary[prof] = prof_sum

    transitions = []
    for r in per_item:
        b = outcome(r["baseline"], r["gold_unit_id"])
        s = outcome(r["s3"], r["gold_unit_id"])
        if b != s or b == "wrong":
            transitions.append({
                "item_id": r["item_id"], "profile": r["profile"], "style_group": r["style_group"],
                "text": r["text"], "expected": r["gold_headword"],
                "baseline": r["baseline_headword"] or "NONE", "baseline_outcome": b,
                "s3": r["s3_headword"] or "NONE", "s3_outcome": s,
                "first_stage_rank": r["first_stage_rank"], "gold_in_s3_pool": r["gold_in_s3_pool"],
                "s3_relation": r["s3_meta"].get("choice_relation"),
                "s3_runner_up_relation": r["s3_meta"].get("runner_up_relation"),
                "s3_reason": r["s3_meta"].get("reason"),
            })

    cfg = {
        "experiment": "E9 text-centered contrastive decision (S3) development follow-up",
        "status": "DEVELOPMENT ONLY: designed after inspecting E8; reuses E8 items; not independent evaluation",
        "code_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "dataset": str(DATA.relative_to(ROOT)),
        "dataset_sha256": hashlib.sha256(DATA.read_bytes()).hexdigest(),
        "e8_results": str(E8.relative_to(ROOT)),
        "model": llm.client.model,
        "temperature": 0.0,
        "enable_thinking": False,
        "max_tokens": {"s3": llm.client.max_tokens},
        "retriever": "intfloat/multilingual-e5-large",
        "s3_candidate_pool": "first-stage top10 UNION E8 baseline nomination; deduplicated; sorted by unit_id to hide rank",
        "s3_prompt_sha256_16": sha(text_centered.SYSTEM),
        "s1": "unchanged; applied after S3 at k=1,3,5,10",
        "methodological_warning": "Do not use E9 to claim held-out improvement. Any final evaluation must use a fresh untouched set.",
    }

    save_json(cfg, OUT / "run_config.json")
    save_json(summary, OUT / "summary.json")
    save_json(per_item, OUT / "per_item_results.json")
    save_json(transitions, OUT / "transitions.json")
    save_json(style, OUT / "style_breakdown.json")

    lines = [
        "# E9 — Text-centered contrastive decision (S3)", "",
        "> **Development only.** S3 was designed after E8 error analysis and E9 reuses the E8 100 items.",
        "> These numbers are not held-out evidence and must not be used for the final success criteria.", "",
        "## Results", "",
        "| Profile | Setting | Correct | Wrong | NONE | Precision | Coverage |", "|---|---|---:|---:|---:|---:|---:|",
    ]
    for prof in PROFILES:
        for name, v in summary[prof]["settings"].items():
            lines.append(f"| {prof} | {name} | {v['correct']} | {v['wrong']} | {v['none']} | {v['precision']} | {v['coverage']} |")
    lines += ["", "## Transition summary", ""]
    for prof in PROFILES:
        s = summary[prof]["settings"]["S3"]
        lines.append(
            f"- **{prof}:** corrected wrong={s['corrected_wrong']}, correct→wrong={s['correct_to_wrong']}, "
            f"correct→NONE={s['correct_to_none']}, wrong→NONE={s['wrong_to_none']}; "
            f"gold present in S3 pool={summary[prof]['gold_in_s3_pool']}/100."
        )
    lines += ["", "## Interpretation guardrail", "",
              "If S3 looks better here, treat that as a development signal only. The mechanism was created from E8's observed errors. "
              "A new untouched held-out set is required after architecture freeze."]
    (OUT / "REPORT.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"\nNew S3 API calls: {llm.new_calls}")
    print(f"Results written to {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
