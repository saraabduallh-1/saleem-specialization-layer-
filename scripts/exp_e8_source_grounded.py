#!/usr/bin/env python3
"""E8: interim pilot on the 100 source-grounded positive drafts (heldout_v1 D3).

Not the formal held-out evaluation: positives only, no independent gold annotation, no negatives.
Runs the frozen registered pipelines unchanged:
  P-full : query understanding -> first stage -> one-call decision over top-30
  P-def  : query understanding -> first stage -> Qwen listwise rerank (top-50) -> selector (top-10)
  gate   : technical == false -> NONE
Then S1 (k in 1,3,5,10), S2 (frozen, §4A) and S1+S2 (exploratory).
Strict scoring against the item's unit_id. Resumable: every LLM call is cached.
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
from specialization_layer import contrastive, decision  # noqa: E402
from specialization_layer.abstention import view_ranks  # noqa: E402
from specialization_layer.engine import query_understanding as qu_mod  # noqa: E402
from specialization_layer.engine.rerank import LISTWISE_SYSTEM, LLMListwiseReranker  # noqa: E402
from specialization_layer.engine.signals import DenseUnit  # noqa: E402
from spec_layer_v2 import Qwen, load_json, save_json  # noqa: E402

DATA = ROOT / "evaluation/heldout_v1/source_grounded_draft/heldout_source_grounded_balanced_100_v1.json"
OUT = ROOT / "results/e8_source_grounded_positive_100"
CACHE = OUT / "llm_calls_cache.json"
DOMAIN = "الذكاء الاصطناعي"
KS = (1, 3, 5, 10)
STYLE_GROUP = {"formal_technical": "reports_formal", "report_technical": "reports_formal",
               "developer_question": "developer", "developer_issue": "developer",
               "social_tech": "social", "social_saudi": "social", "product_support": "product_support"}
PROFILES = {"P-full": (TEXT3 + AR + EN, True), "P-def": (TEXT3 + AR, False)}
MAXTOK = {"qu": 300, "decision": 60, "rerank": 200, "s2": contrastive.MAX_TOKENS}


class LLM:
    def __init__(self):
        self.cache = load_json(CACHE) if CACHE.exists() else {}
        self.clients = {k: Qwen(max_tokens=v) for k, v in MAXTOK.items()}
        self.new_calls = 0

    def stage(self, name):
        q = self.clients[name]

        def call(msgs):
            k = hashlib.sha256(json.dumps([name, q.max_tokens, msgs], ensure_ascii=False).encode()).hexdigest()[:24]
            if k not in self.cache:
                out, meta = q(msgs)
                self.cache[k] = {"stage": name, "output": out, "meta": meta}
                save_json(self.cache, CACHE)
                self.new_calls += 1
            call.last = self.cache[k]["meta"]
            return self.cache[k]["output"]
        return call


def sha(s):
    return hashlib.sha256(s.encode()).hexdigest()[:16]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    data = load_json(DATA)
    items = data["items"]
    llm = LLM()
    qu_call, dec_call, rr_call, s2_call = (llm.stage(s) for s in ("qu", "decision", "rerank", "s2"))

    qu = {}
    for n, it in enumerate(items, 1):
        qu[it["item_id"]] = qu_mod.parse(qu_call(qu_mod.messages(it["draft_text_ar"], DOMAIN)))
        if n % 25 == 0:
            print(f"  query understanding {n}/100", flush=True)

    per_item = {it["item_id"]: {"item_id": it["item_id"], "text": it["draft_text_ar"],
                                "gold_unit_id": it["unit_id"], "gold_headword": it["gold_headword"],
                                "style_profile": it["style_profile"], "style_group": STYLE_GROUP[it["style_profile"]],
                                "technical": qu[it["item_id"]]["technical"], "query_understanding": qu[it["item_id"]],
                                "profiles": {}} for it in items}

    for prof, (specs, use_en) in PROFILES.items():
        units, _ = load_units(prof)
        eng = Engine(units, specs, fusion="neutral")
        uv = next(s for s, _ in eng.signals if isinstance(s, DenseUnit)).P
        uidx = {u.unit_id: i for i, u in enumerate(units)}
        reranker = LLMListwiseReranker(rr_call)
        for n, it in enumerate(items, 1):
            iid, text = it["item_id"], it["draft_text_ar"]
            gi = uidx[it["unit_id"]]
            order, _, ev = eng.rank(qu_mod.to_query(text, qu[iid], use_en=use_en))
            order = [int(i) for i in order]
            fs_rank = order.index(gi) + 1
            rec = {"first_stage_rank": fs_rank, "first_stage_top5": [units[i].headword for i in order[:5]],
                   "rerank_rank": None, "decision_candidates_n": None, "available_to_decision": None,
                   "c_star": None, "c_star_headword": None, "s2": None, "s2_headword": None, "s2_reason": None,
                   "views_c_star": None, "views_s2": None, "potential_alt_c_star": None, "potential_alt_s2": None}
            if prof == "P-full":
                cands = order[:30]
            else:
                top50 = order[:50]
                new, _ = reranker.rerank(text, [units[i] for i in top50])
                reranked = [top50[i] for i in new]
                rec["rerank_rank"] = reranked.index(gi) + 1 if gi in reranked else None
                cands = reranked[:10]
            rec["decision_candidates_n"] = len(cands)
            rec["available_to_decision"] = gi in cands
            if qu[iid]["technical"]:
                system = decision.JOINT_SYSTEM if prof == "P-full" else decision.SELECTOR_SYSTEM
                pick, raw = decision.decide(dec_call, system, text, [units[i] for i in cands])
                rec["decision_raw"] = raw
                if pick is not None:
                    ci = cands[pick]
                    rec["c_star"], rec["c_star_headword"] = units[ci].unit_id, units[ci].headword
                    rec["views_c_star"] = view_ranks(ev, ci)
                    s2_pick, reason, idxs, s2_raw = contrastive.decide(s2_call, text, units, uv, ci)
                    rec.update({"s2_reason": reason, "s2_raw": raw if False else s2_raw,
                                "s2_contrast_set": [units[i].headword for i in idxs],
                                "gold_in_contrast_set": gi in idxs,
                                "s2_latency": s2_call.last["elapsed_seconds"],
                                "s2_prompt_tokens": (s2_call.last.get("usage") or {}).get("prompt_tokens")})
                    if s2_pick is not None:
                        rec["s2"], rec["s2_headword"] = units[s2_pick].unit_id, units[s2_pick].headword
                        rec["views_s2"] = view_ranks(ev, s2_pick)
                    # potential acceptable alternative (heuristic flag only, not counted as correct):
                    # a wrong pick among the gold entry's 10 nearest units by dense_unit cosine
                    nn = set(np.argsort(-(uv @ uv[gi]))[1:11].tolist())
                    rec["potential_alt_c_star"] = ci != gi and ci in nn
                    rec["potential_alt_s2"] = s2_pick is not None and s2_pick != gi and s2_pick in nn
            per_item[iid]["profiles"][prof] = rec
            if n % 20 == 0:
                print(f"  {prof} {n}/100 (new calls so far {llm.new_calls})", flush=True)

    # ------------------------------------------------------------- scoring
    def passes(v, k):
        return bool(v) and v["text_active"] and v["interp_active"] and v["text"] <= k and v["interp"] <= k

    def outcome(sel, gold):
        return "none" if not sel else ("correct" if sel == gold else "wrong")

    summary, style = {}, {}
    for prof in PROFILES:
        recs = [(p, p["profiles"][prof]) for p in per_item.values()]
        settings = {"baseline": {p["item_id"]: r["c_star"] for p, r in recs},
                    "S2": {p["item_id"]: r["s2"] for p, r in recs}}
        for k in KS:
            settings[f"S1@k={k}"] = {p["item_id"]: r["c_star"] if passes(r["views_c_star"], k) else None for p, r in recs}
            settings[f"S1+S2@k={k} (exploratory)"] = {p["item_id"]: r["s2"] if passes(r["views_s2"], k) else None
                                                     for p, r in recs}
        ranks = np.array([r["first_stage_rank"] for _, r in recs])
        res = {"first_stage": {**{f"hit@{k}": round(float((ranks <= k).mean()), 3) for k in (1, 3, 5, 10, 30, 50)},
                               "mrr": round(float((1 / ranks).mean()), 4),
                               "never_top50": int((ranks > 50).sum())},
               "available_to_decision": sum(r["available_to_decision"] for _, r in recs),
               "decision_candidates_n": recs[0][1]["decision_candidates_n"],
               "gate_rejected": sum(not p["technical"] for p, _ in recs), "settings": {}}
        if prof == "P-def":
            rr = [r["rerank_rank"] for _, r in recs]
            res["after_rerank"] = {f"hit@{k}": round(sum(x is not None and x <= k for x in rr) / 100, 3) for k in (1, 3, 5, 10)}
        base = settings["baseline"]
        for name, sel in settings.items():
            oc = Counter(outcome(sel[p["item_id"]], p["gold_unit_id"]) for p, _ in recs)
            c, w = oc["correct"], oc["wrong"]
            s = {"correct": c, "wrong": w, "none": oc["none"],
                 "precision": round(c / (c + w), 3) if c + w else None, "coverage": round(c / 100, 3),
                 "potential_alternatives_among_wrong": sum(
                     outcome(sel[p["item_id"]], p["gold_unit_id"]) == "wrong" and
                     (r["potential_alt_s2"] if sel[p["item_id"]] == r["s2"] and sel[p["item_id"]] != r["c_star"]
                      else r["potential_alt_c_star"]) for p, r in recs)}
            if name != "baseline":
                bo = {p["item_id"]: outcome(base[p["item_id"]], p["gold_unit_id"]) for p, _ in recs}
                so = {p["item_id"]: outcome(sel[p["item_id"]], p["gold_unit_id"]) for p, _ in recs}
                s.update({"rejected_correct": sum(bo[i] == "correct" and so[i] == "none" for i in bo),
                          "rejected_wrong": sum(bo[i] == "wrong" and so[i] == "none" for i in bo),
                          "corrected_wrong": sum(bo[i] == "wrong" and so[i] == "correct" for i in bo),
                          "changed_correct_to_wrong": sum(bo[i] == "correct" and so[i] == "wrong" for i in bo),
                          "changed_wrong_to_other_wrong": sum(bo[i] == "wrong" and so[i] == "wrong"
                                                              and sel[i] != base[i] for i in bo)})
            res["settings"][name] = s
            for g in ("reports_formal", "developer", "social", "product_support"):
                sub = [(p, r) for p, r in recs if p["style_group"] == g]
                oc2 = Counter(outcome(sel[p["item_id"]], p["gold_unit_id"]) for p, _ in sub)
                rk = np.array([r["first_stage_rank"] for _, r in sub])
                st = style.setdefault(prof, {}).setdefault(g, {"n": len(sub),
                                                               "first_stage_hit@10": round(float((rk <= 10).mean()), 3),
                                                               "first_stage_hit@30": round(float((rk <= 30).mean()), 3),
                                                               "available_to_decision": sum(r["available_to_decision"] for _, r in sub),
                                                               "gate_rejected": sum(not p["technical"] for p, _ in sub)})
                st[name] = {"correct": oc2["correct"], "wrong": oc2["wrong"], "none": oc2["none"],
                            "precision": round(oc2["correct"] / (oc2["correct"] + oc2["wrong"]), 3)
                            if oc2["correct"] + oc2["wrong"] else None}
        summary[prof] = res

    # ------------------------------------------------------------- failure stages
    errors = []
    for p in per_item.values():
        for prof in PROFILES:
            r = p["profiles"][prof]
            gold = p["gold_unit_id"]
            stage_base = None
            if r["c_star"] != gold:
                if not p["technical"]:
                    stage_base = "technical_gate_failure"
                elif prof == "P-def" and (r["first_stage_rank"] <= 50) and not r["available_to_decision"]:
                    stage_base = "reranker_failure"
                elif not r["available_to_decision"]:
                    stage_base = "retrieval_failure"
                else:
                    stage_base = "decision_failure"
            s2_stage = None
            if r["c_star"] == gold and r["s2"] is None:
                s2_stage = "s2_false_rejection"
            elif r["c_star"] == gold and r["s2"] not in (None, gold):
                s2_stage = "s2_wrong_correction_drift"
            s1_false_rej = [k for k in KS if r["c_star"] == gold and not passes(r["views_c_star"], k)]
            if stage_base or s2_stage or s1_false_rej:
                errors.append({"item_id": p["item_id"], "profile": prof, "style_group": p["style_group"],
                               "text": p["text"], "expected": p["gold_headword"],
                               "selected_baseline": r["c_star_headword"] or "NONE",
                               "selected_s2": r["s2_headword"] or "NONE",
                               "expected_first_stage_rank": r["first_stage_rank"],
                               "expected_rerank_rank": r["rerank_rank"],
                               "baseline_failure_stage": stage_base,
                               "potential_acceptable_alternative": bool(r["potential_alt_c_star"]),
                               "s2_failure": s2_stage, "s1_false_rejection_at_k": s1_false_rej})
    for prof in PROFILES:
        summary[prof]["baseline_failure_stages"] = dict(Counter(
            e["baseline_failure_stage"] for e in errors if e["profile"] == prof and e["baseline_failure_stage"]))
        summary[prof]["s2_failures"] = dict(Counter(
            e["s2_failure"] for e in errors if e["profile"] == prof and e["s2_failure"]))
        lat = [r["profiles"][prof].get("s2_latency") for r in per_item.values() if r["profiles"][prof].get("s2_latency")]
        summary[prof]["s2_cost"] = {"calls": len(lat), "latency_median_s": round(float(np.median(lat)), 3) if lat else None,
                                    "prompt_tokens_mean": int(np.mean([r["profiles"][prof].get("s2_prompt_tokens") or 0
                                                                        for r in per_item.values()
                                                                        if r["profiles"][prof].get("s2_latency")])) if lat else None}

    cfg = {"experiment": "E8 source-grounded positive pilot (interim; not the formal held-out test)",
           "code_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
           "dataset": str(DATA.relative_to(ROOT)), "dataset_sha256": hashlib.sha256(DATA.read_bytes()).hexdigest(),
           "model": llm.clients["qu"].model, "temperature": 0.0, "enable_thinking": False, "max_tokens": MAXTOK,
           "retriever": "intfloat/multilingual-e5-large",
           "prompt_sha256_16": {"query_understanding": sha(qu_mod.SYSTEM_TEMPLATE.format(domain=DOMAIN)),
                                "joint_decision": sha(decision.JOINT_SYSTEM), "selector": sha(decision.SELECTOR_SYSTEM),
                                "listwise_rerank": sha(LISTWISE_SYSTEM), "s2_contrastive": sha(contrastive.SYSTEM)},
           "s1_s2_implementation_commit": "3490f269ac954eef2daed2990ecf2b9fcc1559f5",
           "scoring": "strict against unit_id; potential_acceptable_alternative = wrong pick among gold's 10 nearest "
                      "units by dense_unit cosine (heuristic flag, never counted as correct)",
           "false_specialization": "NOT reported: the pilot contains positives only"}
    save_json(cfg, OUT / "run_config.json")
    save_json(summary, OUT / "summary.json")
    save_json(list(per_item.values()), OUT / "per_item_results.json")
    save_json(errors, OUT / "errors.json")
    save_json(style, OUT / "style_breakdown.json")
    print(json.dumps({p: {k: v for k, v in s.items() if k != "settings"} for p, s in summary.items()}, ensure_ascii=False, indent=1))
    for p, s in summary.items():
        for name, v in s["settings"].items():
            print(p, name, v)


if __name__ == "__main__":
    main()
