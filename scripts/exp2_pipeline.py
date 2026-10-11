#!/usr/bin/env python3
"""Exp S/W: decision-stage and writer-stage ablations for the specialization layer.

Stages
  retrieval  : E5 term+definition over pool {pilot50, full}; query mode
               {orig, all = orig + concept-naming expansion (exp2_query_expansion)}
  decision   : sel_v1 (previous Top-K selector prompt, generalized to K)
               sel_v2 (evidence-first selector with explicit specificity / NONE rules)
               joint  (one call that selects AND rewrites)
  writer     : W_def   term + definition
               W_term  term only
               W_fs    term only + 3 generic demonstrations (terms unrelated to all eval sets)
               W_dom   term only + domain label
               W_d3    term only + domain definition + writing guidelines
               each optionally followed by a deterministic presence check and one
               retry that KEEPS the term ("+chk"). No LLM validator.
  NONE path  : plain rewrite, identical base instruction, no terminology.

Every LLM call is cached by (stage, prompt-hash) in results/v2_architecture_study/calls/,
so writers are compared on identical selections. Expected labels are used only by
the scoring code at the end.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from spec_layer_v2 import (DOMAIN, ROOT, Qwen, definitional_framing, load_eval_items, load_json,
                           load_pool, meta_leak, parse_json_obj, save_json, term_present)
from exp2_query_expansion import CACHE as NAMING_CACHE, ExpandedRetriever, en_norm

OUTDIR = ROOT / "results/v2_architecture_study"
CALLS = OUTDIR / "calls"

# ------------------------------------------------------------------ prompts

SEL_V1_SYSTEM = (  # previous experiment's selector, unchanged except for K
    "تحقق دلاليًا من المصطلحات المرشحة. اختر مصطلحًا واحدًا فقط إذا كان تعريفه يطابق المفهوم الموجود فعلًا في النص. "
    "لا تعتمد على تشابه لفظي أو كلمة مشتركة فقط. إذا لم يطابق أي مرشح معنى النص فاختر NONE. "
    "أعد JSON فقط: {\"choice\":\"C1\"} أو رقم مرشح آخر أو NONE ضمن الحقل نفسه."
)

SEL_V2_SYSTEM = (
    "مهمتك أن تقرر هل يعبّر النص عن أحد المفاهيم المرشحة من معجم المصطلحات.\n"
    "القواعد:\n"
    "1. اختر مرشحًا فقط إذا كان النص يذكر الخصائص الجوهرية الواردة في تعريفه، ولو بألفاظ عامة أو عامية.\n"
    "2. لا يكفي اشتراك كلمة أو تقارب الموضوع. الكلمة التي تُستعمل في النص بمعناها العام أو اليومي لا تبرر المصطلح.\n"
    "3. إذا انطبق أكثر من مرشح فاختر الأدق: لا تختر مفهومًا أعمّ إذا وُجد مرشح أخصّ تنطبق خصائصه على النص، "
    "ولا تختر مفهومًا أخصّ إذا كان النص لا يذكر ما يميّزه.\n"
    "4. إذا كان النص مبهمًا أو لا يحدد المفهوم بما يكفي فاختر NONE.\n"
    "أعد JSON فقط بالشكل: {\"evidence\": \"العبارة من النص التي تعبّر عن خصائص المفهوم، أو فارغ\", \"choice\": \"C1\"} "
    "مع رقم المرشح المختار أو NONE."
)

SEL_V3_SYSTEM = (
    "مهمتك أن تقرر هل أحد المصطلحات المرشحة هو الاسم الدقيق للمفهوم الذي يصفه النص.\n"
    "القواعد:\n"
    "1. المصطلح الصحيح هو اسم الشيء نفسه الذي يصفه النص، وتنطبق خصائص تعريفه الجوهرية على ما ورد في النص، ولو بألفاظ عامة أو عامية.\n"
    "2. لا تختر مصطلحًا لمجرد أنه مرتبط بالموضوع: لا تختر اسم المجال الأعم، ولا اسم مكوّن أو أداة أو نتيجة أو مفهوم مجاور، "
    "إذا لم يكن هو نفسه ما يصفه النص.\n"
    "3. الكلمة المستعملة في النص بمعناها العام أو اليومي لا تبرر المصطلح التقني.\n"
    "4. إذا لم يكن بين المرشحين اسم دقيق لما يصفه النص، أو كان النص مبهمًا، فاختر NONE. اختيار NONE أفضل من اختيار مصطلح قريب غير دقيق.\n"
    "أعد JSON فقط بالشكل: {\"choice\": \"C1\"} مع رقم المرشح المختار أو NONE."
)

VERIFY_SYSTEM = (
    "اقرأ النص ثم المفهوم المعجمي وتعريفه. أجب: هل يصف النص هذا المفهوم بعينه، "
    "أي أن الخصائص الجوهرية في التعريف موجودة في معنى النص، ولو بألفاظ عامة أو عامية؟ "
    "أجب بـ false إذا كان النص يصف مفهومًا آخر مرتبطًا به (أعم أو أخص أو مكوّنًا أو نتيجة)، "
    "أو كانت الكلمة مستعملة بمعناها العام، أو كان النص مبهمًا. "
    "أعد JSON فقط: {\"match\": true} أو {\"match\": false}."
)

BASE_WRITER = (
    "أعد صياغة النص العربي بلغة فصيحة واضحة كما يكتبها مختص، مع الحفاظ على جميع معلوماته. "
    "لا تضف حقائق أو أمثلة أو علاقات سببية أو قدرات أو درجة يقين غير موجودة في النص. "
    "لا تشرح المصطلحات ولا تعرّفها، ولا تتحدث عن التعليمات. أعد النص المعاد صياغته فقط."
)

TERM_RULE = (
    "استخدم في صياغتك المصطلح التخصصي «{term}» للتعبير عن المفهوم الذي يصفه النص، "
    "ودمجه في الجملة دمجًا طبيعيًا بدل الوصف العام، مع جواز إضافة «ال» أو تصريفه بحسب السياق."
)

DEMOS = [  # terms deliberately unrelated to every development item
    ("كثّرنا الصور اللي عندنا بإننا قلبناها ودوّرناها وغيرنا إضاءتها عشان يصير عندنا أمثلة أكثر للتدريب.",
     "زيادة البيانات",
     "وسّعنا مجموعة الصور بتطبيق زيادة البيانات عليها، فقلبناها وأدرناها وعدّلنا إضاءتها لنحصل على أمثلة تدريب إضافية."),
    ("درّبنا نموذج صغير يقلّد مخرجات النموذج الكبير عشان نقدر نشغله على الجوال.",
     "تقطير المعرفة",
     "استخدمنا تقطير المعرفة لتدريب نموذج صغير يحاكي مخرجات النموذج الكبير، حتى يمكن تشغيله على الهاتف المحمول."),
    ("بعد كم شهر صارت البيانات اللي توصل للنظام مختلفة عن اللي تدرب عليها، ونزل أداؤه.",
     "انحراف البيانات",
     "بعد بضعة أشهر ظهر انحراف البيانات، إذ أصبحت المدخلات الواردة إلى النظام مختلفة عن بيانات تدريبه، فانخفض أداؤه."),
]

JOINT_SYSTEM = (
    SEL_V2_SYSTEM.split("أعد JSON")[0]
    + "بعد ذلك أعد صياغة النص بلغة فصيحة واضحة كما يكتبها مختص مع الحفاظ على جميع معلوماته، "
    "ودون إضافة حقائق أو أمثلة أو علاقات أو درجة يقين غير موجودة. إذا اخترت مرشحًا فاستخدم مصطلحه في الصياغة "
    "استخدامًا طبيعيًا دون تعريفه. وإذا اخترت NONE فلا تستخدم أي مصطلح من القائمة.\n"
    "أعد JSON فقط بالشكل: {\"evidence\": \"...\", \"choice\": \"C1\", \"rewrite\": \"...\"}"
)

# ------------------------------------------------------------------ caching


class Caller:
    def __init__(self, qwen: Qwen):
        self.qwen = qwen
        CALLS.mkdir(parents=True, exist_ok=True)

    def __call__(self, stage: str, messages: list[dict]) -> str:
        h = hashlib.sha256(json.dumps([self.qwen.model, self.qwen.temperature, self.qwen.max_tokens,
                                       messages], ensure_ascii=False).encode()).hexdigest()[:24]
        path = CALLS / f"{stage}_{h}.json"
        if path.exists():
            return load_json(path)["output"]
        out, meta = self.qwen(messages)
        save_json({"stage": stage, "messages": messages, "output": out, "api": meta}, path)
        return out


# ------------------------------------------------------------------ stages

def cand_block(text, cands):
    blocks = ["النص:\n" + text, "المصطلحات المرشحة:"]
    for i, c in enumerate(cands, 1):
        blocks.append(f"C{i}\nالمصطلح: {c['term']}\nالتعريف: {c['definition']}")
    return "\n\n".join(blocks)


def parse_choice(raw, k):
    try:
        obj = parse_json_obj(raw)
        choice = str(obj.get("choice", "")).strip().upper()
    except Exception:
        obj, choice = {}, ""
        up = raw.upper()
        for c in [f"C{i}" for i in range(k, 0, -1)] + ["NONE"]:
            if c in up:
                choice = c
                break
    valid = {f"C{i}" for i in range(1, k + 1)} | {"NONE"}
    if choice not in valid:
        choice = "NONE"  # unparseable -> abstain (counted in report)
        obj["_parse_fallback"] = True
    return choice, obj


def decide(call, selector, text, cands):
    system = {"sel_v1": SEL_V1_SYSTEM, "sel_v2": SEL_V2_SYSTEM, "sel_v3": SEL_V3_SYSTEM}[selector]
    raw = call(selector, [{"role": "system", "content": system},
                          {"role": "user", "content": cand_block(text, cands)}])
    choice, obj = parse_choice(raw, len(cands))
    sel = None if choice == "NONE" else cands[int(choice[1:]) - 1]
    return sel, {"choice": choice, "raw": raw, "evidence": obj.get("evidence"),
                 "parse_fallback": bool(obj.get("_parse_fallback"))}


def verify(call, text, sel):
    """Pre-generation binary check of ONE selected candidate against the input only."""
    raw = call("verify", [{"role": "system", "content": VERIFY_SYSTEM},
                          {"role": "user", "content": f"النص:\n{text}\n\nالمفهوم: {sel['term']}\nالتعريف: {sel['definition']}"}])
    try:
        m = parse_json_obj(raw).get("match")
        ok = m is True or str(m).lower() == "true"
    except Exception:
        ok = "true" in raw.lower()
    return ok, raw


def domain_block(kind):
    d = next(x for x in load_json(DOMAIN)["domains"] if x["domain_id"] == "artificial_intelligence")
    if kind == "label":
        return f"المجال: {d['names']['ar']}"
    guide = "\n".join(f"- {g['instruction_ar']}" for g in d["writing_guidelines"])
    return (f"المجال: {d['names']['ar']}\nتعريف المجال: {d['definition']['text_ar']}\n"
            f"إرشادات الكتابة في المجال:\n{guide}")


def writer_messages(writer, text, sel):
    msgs = [{"role": "system", "content": BASE_WRITER}]
    if sel is None:
        msgs.append({"role": "user", "content": "النص:\n" + text})
        return msgs
    parts = []
    if writer == "W_dom":
        parts.append(domain_block("label"))
    if writer == "W_d3":
        parts.append(domain_block("full"))
    if writer == "W_def":
        parts.append(f"تعريف المصطلح «{sel['term']}» للاستئناس فقط، ولا تنقله إلى النص: {sel['definition']}")
    parts.append(TERM_RULE.format(term=sel["term"]))
    if writer == "W_fs":
        for src, term, out in DEMOS:
            msgs.append({"role": "user", "content": TERM_RULE.format(term=term) + "\n\nالنص:\n" + src})
            msgs.append({"role": "assistant", "content": out})
    parts.append("النص:\n" + text)
    msgs.append({"role": "user", "content": "\n\n".join(parts)})
    return msgs


def write(call, writer, text, sel, check):
    base = writer.replace("+chk", "")
    msgs = writer_messages(base, text, sel)
    out = call(base if sel else "W_none", msgs)
    trace = {"attempts": 1, "first_output": out}
    if check and sel and not term_present(out, sel["term"]):
        retry = msgs + [{"role": "assistant", "content": out},
                        {"role": "user", "content":
                         f"لم يظهر المصطلح «{sel['term']}» في صياغتك. أعد الصياغة نفسها مع استخدام هذا المصطلح "
                         "استخدامًا طبيعيًا، دون تعريفه ودون إضافة أي معلومة جديدة. أعد النص فقط."}]
        out = call(base + "_retry", retry)
        trace["attempts"] = 2
    return out, trace


def joint(call, text, cands):
    raw = call("joint", [{"role": "system", "content": JOINT_SYSTEM},
                         {"role": "user", "content": cand_block(text, cands)}])
    choice, obj = parse_choice(raw, len(cands))
    sel = None if choice == "NONE" else cands[int(choice[1:]) - 1]
    rewrite = str(obj.get("rewrite") or "").strip()
    return sel, rewrite, {"choice": choice, "raw": raw, "evidence": obj.get("evidence"),
                          "parse_fallback": bool(obj.get("_parse_fallback")) or not rewrite}


# ------------------------------------------------------------------ scoring

def score_item(x, pool, cands, sel, output):
    exp = pool.resolve(x["expected_term_id"]) if x["expected_term_id"] else None
    sel_id = pool.resolve(sel["id"]) if sel else None
    r = {
        "available": (exp in [pool.resolve(c["id"]) for c in cands]) if exp else None,
        "selected_id": sel_id, "selected_term": sel["term"] if sel else None,
        "selection_strict_correct": (sel_id == exp),
        "selected_term_used": term_present(output, sel["term"]) if sel else None,
        "expected_term_used": (any(term_present(output, f) for f in pool.accepted_forms(exp))
                               if exp else None),
        "meta_leak": meta_leak(output),
        "definitional_framing": definitional_framing(output),
    }
    return r


def summarize(rows):
    def agg(xs):
        pos = [r for r in xs if r["kind"] == "positive"]
        neg = [r for r in xs if r["kind"] != "positive"]
        s = {}
        if pos:
            n = len(pos)
            avail = [r for r in pos if r["score"]["available"]]
            s.update({
                "n_pos": n,
                "available": len(avail),
                "selected_correct": sum(r["score"]["selection_strict_correct"] for r in pos),
                "selected_correct_given_available": f"{sum(r['score']['selection_strict_correct'] for r in avail)}/{len(avail)}",
                "selected_wrong_term": sum(bool(r["score"]["selected_id"]) and not r["score"]["selection_strict_correct"] for r in pos),
                "abstained": sum(r["score"]["selected_id"] is None for r in pos),
                "correct_and_term_used": sum(r["score"]["selection_strict_correct"] and bool(r["score"]["selected_term_used"]) for r in pos),
                "wrong_term_used_in_output": sum(bool(r["score"]["selected_id"]) and not r["score"]["selection_strict_correct"]
                                                 and bool(r["score"]["selected_term_used"]) for r in pos),
                "expected_term_in_output": sum(bool(r["score"]["expected_term_used"]) for r in pos),
            })
            sel_ok = s["selected_correct"]
            s["term_use_rate_given_correct"] = round(s["correct_and_term_used"] / sel_ok, 3) if sel_ok else None
            s["end_to_end_rate"] = round(s["correct_and_term_used"] / n, 3)
        if neg:
            s.update({"n_neg": len(neg),
                      "false_specialization": sum(r["score"]["selected_id"] is not None for r in neg),
                      "false_term_in_output": sum(bool(r["score"]["selected_term_used"]) for r in neg)})
        s["meta_leak_outputs"] = sum(bool(r["score"]["meta_leak"]) for r in xs)
        s["definitional_framing_outputs"] = sum(bool(r["score"]["definitional_framing"]) for r in xs)
        s["retries"] = sum(r.get("writer_trace", {}).get("attempts", 1) - 1 for r in xs)
        return s
    out = {}
    for st in sorted({r["set"] for r in rows}):
        out[st] = agg([r for r in rows if r["set"] == st])
    return out


# ------------------------------------------------------------------ main

def run_config(cfg, items, retrievers, call, namings):
    pool_name, mode, k, decision, writer = cfg["pool"], cfg["mode"], cfg["k"], cfg["decision"], cfg["writer"]
    retr = retrievers[pool_name]
    pool = retr.pool
    cand_map = {x["id"]: retr.search(x["text"], mode, k) for x in items}  # sequential E5
    en_names = {}  # canonical id -> English names from Siwar (incl. redirect entries)
    for e in pool.entries:
        if en_norm(e.get("english_term")):
            en_names.setdefault(pool.resolve(e["id"]), set()).add(en_norm(e["english_term"]))

    def one(x):
        cands = cand_map[x["id"]]
        named = bool(namings.get(x["text"], {}).get("concepts_en"))
        if cfg.get("gate") and not named:
            # deterministic abstention: concept-naming call found no technical concept
            sel, dmeta = None, {"choice": "NONE", "gated": True}
            output, trace = ("", {"attempts": 1}) if writer is None and decision != "joint" else \
                (call("W_none", writer_messages("W_term", x["text"], None)), {"attempts": 1})
        elif decision == "none":  # baseline: Qwen rewrite without any terminology
            sel, dmeta = None, {"choice": "NONE", "baseline": True}
            output, trace = call("W_none", writer_messages("W_term", x["text"], None)), {"attempts": 1}
        elif decision == "joint":
            sel, output, dmeta = joint(call, x["text"], cands)
            trace = {"attempts": 1}
            if not output:
                output = ""
        else:
            sel, dmeta = decide(call, decision.replace("+ver", ""), x["text"], cands)
            if sel and cfg.get("agree"):
                # deterministic agreement: the selected entry's Siwar English name must match
                # one of the concepts named independently from the text alone
                named_en = {en_norm(c) for c in namings.get(x["text"], {}).get("concepts_en", [])}
                dmeta["agreement"] = bool(en_names.get(pool.resolve(sel["id"]), set()) & named_en)
                if not dmeta["agreement"]:
                    dmeta["rejected_term"] = sel["term"]
                    sel = None
            if sel and decision.endswith("+ver"):
                ok, vraw = verify(call, x["text"], sel)
                dmeta["verify_raw"], dmeta["verified"] = vraw, ok
                if not ok:
                    dmeta["rejected_term"] = sel["term"]
                    sel = None
            if writer is None:
                output, trace = "", {"attempts": 1}
            else:
                output, trace = write(call, writer, x["text"], sel, writer.endswith("+chk"))
        row = {"id": x["id"], "set": x["set"], "kind": x["kind"], "input": x["text"],
               "expected_term": x["expected_term"],
               "candidates": [c["term"] for c in cands], "decision": dmeta, "naming_nonempty": named,
               "output": output, "writer_trace": trace}
        row["score"] = score_item(x, pool, cands, sel, output)
        return row
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(8) as ex:
        rows = list(ex.map(one, items))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", required=True, help="JSON file with a list of configs")
    ap.add_argument("--sets", default="dev36,gold50,probes")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    plan = load_json(Path(args.plan))
    items = [x for s in args.sets.split(",") for x in load_eval_items(s)]
    namings = load_json(NAMING_CACHE)["items"]
    retrievers = {p: ExpandedRetriever(load_pool(p), namings) for p in {c["pool"] for c in plan}}
    qwen = Qwen(max_tokens=400)
    call = Caller(qwen)
    out_path = OUTDIR / args.out
    result = load_json(out_path) if out_path.exists() else {
        "metadata": {"qwen": qwen.meta(), "retrieval_model": "intfloat/multilingual-e5-large",
                     "passage": "term + original Siwar definition", "sets": args.sets,
                     "note": "Development/ablation evidence. dev36 has been examined repeatedly; "
                             "probes authored by the assistant; gold50 is the earlier retrieval set.",
                     "prompts": {"sel_v1": SEL_V1_SYSTEM, "sel_v2": SEL_V2_SYSTEM, "sel_v3": SEL_V3_SYSTEM, "verify": VERIFY_SYSTEM, "writer": BASE_WRITER,
                                 "term_rule": TERM_RULE, "joint": JOINT_SYSTEM, "demos": DEMOS}},
        "configs": {}}
    for cfg in plan:
        name = cfg["name"]
        if name in result["configs"]:
            continue
        print("=== running", name, flush=True)
        rows = run_config(cfg, items, retrievers, call, namings)
        result["configs"][name] = {"config": cfg, "summary": summarize(rows), "rows": rows}
        save_json(result, out_path)
        print(json.dumps(result["configs"][name]["summary"], ensure_ascii=False), flush=True)
    print("\nSUMMARY")
    for name, c in result["configs"].items():
        print(name, json.dumps(c["summary"], ensure_ascii=False))


if __name__ == "__main__":
    main()
