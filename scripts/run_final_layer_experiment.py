#!/usr/bin/env python3
"""Final experiment for the Saleem specialization layer.

T0 = Qwen only
T1 = Qwen + top-k Siwar terms (term + definition)
T2 = T1 + selected-domain definition + D3 writing guidelines

Evaluation labels in the dataset are never sent to Qwen.
"""

from __future__ import annotations

import argparse, json, os, re, time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import torch
from sentence_transformers import SentenceTransformer

from run_qwen_domain_ablation import (
    DEFAULT_BASE_URL, DEFAULT_MODEL, call_with_retry, extract_output,
    load_dotenv, load_json, save_json,
)

ROOT = Path(__file__).resolve().parents[1]
TERMS = ROOT / "data/processed/data_ai/terminology_pilot_50.json"
DOMAIN = ROOT / "data/domain/saleem_domain_knowledge_v1.json"
INPUTS = ROOT / "data/evaluation/ai_final_layer_eval_v1.json"
OUTDIR = ROOT / "results/final_layer_experiment"
CHECKPOINT = OUTDIR / "final_layer_in_progress.json"
RETRIEVAL_MODEL = "intfloat/multilingual-e5-large"
CONDITIONS = ["T0_qwen_only", "T1_terminology", "T2_terminology_domain"]

SYSTEM = (
    "أعد صياغة النص العربي ليصبح واضحًا وفصيحًا وتخصصيًا مع الحفاظ الكامل على معناه. "
    "إذا كان النص يصف مفهومًا تخصصيًا معروفًا فاستخدم المصطلح العربي التخصصي الأدق بدل التعبير العام. "
    "لا تستبدل عبارة بمصطلح إلا إذا كان المعنى متطابقًا. "
    "لا تضف حقائق أو علاقات أو قدرات أو درجة يقين غير موجودة في النص. "
    "إذا عُرضت عليك مصطلحات مرشحة فلا تستخدمها لمجرد التشابه اللفظي، "
    "واستخدم الاسم العربي كما ورد في القائمة عند اختيار المصطلح. "
    "أعد النص النهائي فقط دون شرح."
)

DIAC = re.compile(r"[\u0610-\u061A\u064B-\u065F\u0670\u06D6-\u06ED]")


def norm(s):
    s = DIAC.sub("", s).replace("ـ", "")
    s = re.sub("[إأآٱ]", "ا", s).replace("ى", "ي")
    return " ".join(s.lower().split())


def has(text, form):
    return bool(form) and norm(form) in norm(text)


def forms(term):
    return [term["term"], *(term.get("aliases") or [])]


def validate(dataset, terms):
    by_id = {t["id"]: t for t in terms}
    ids = [x["id"] for x in dataset["items"]]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate evaluation IDs.")
    for item in dataset["items"]:
        if item["kind"] != "positive":
            continue
        term = by_id.get(item["expected_term_id"])
        if not term or item["expected_term"] != term["term"]:
            raise ValueError(f"{item['id']}: invalid expected term label.")
        forbidden = forms(term) + (term.get("abbreviations") or [])
        if term.get("english_term"):
            forbidden.append(term["english_term"])
        leaks = [x for x in forbidden if has(item["text"], x)]
        if leaks:
            raise ValueError(f"{item['id']}: target leaks into input: {leaks}")


def retrieve(terms, items, top_k):
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Retrieval model: {RETRIEVAL_MODEL} on {device}")
    model = SentenceTransformer(RETRIEVAL_MODEL, device=device)
    passages = [f"passage: المصطلح: {t['term']}\nالتعريف: {t['definition']}" for t in terms]
    queries = ["query: " + x["text"] for x in items]
    p = model.encode(passages, batch_size=32, convert_to_numpy=True,
                     normalize_embeddings=True, show_progress_bar=True)
    q = model.encode(queries, batch_size=32, convert_to_numpy=True,
                     normalize_embeddings=True, show_progress_bar=True)
    term_pos = {t["id"]: i for i, t in enumerate(terms)}
    out = {}
    for i, item in enumerate(items):
        scores = q[i] @ p.T
        order = np.argsort(-scores)
        top = []
        for idx in order[:top_k]:
            t = terms[int(idx)]
            top.append({"id": t["id"], "term": t["term"],
                        "definition": t["definition"],
                        "score": round(float(scores[int(idx)]), 6)})
        rank = None
        if item.get("expected_term_id"):
            rank = int(np.where(order == term_pos[item["expected_term_id"]])[0][0]) + 1
        out[item["id"]] = {"top_k": top, "expected_rank": rank}
    return out, device


def retrieval_summary(items, ret):
    ranks = [ret[x["id"]]["expected_rank"] for x in items if x["kind"] == "positive"]
    n = len(ranks)
    return {
        "n_positive": n,
        "hit_at_1": round(sum(r <= 1 for r in ranks) / n, 4),
        "hit_at_3": round(sum(r <= 3 for r in ranks) / n, 4),
        "hit_at_5": round(sum(r <= 5 for r in ranks) / n, 4),
        "mrr": round(sum(1 / r for r in ranks) / n, 4),
    }


def term_context(cands):
    lines = ["مصطلحات مرشحة مسترجعة من معجم سوار. ليست كلها مناسبة بالضرورة؛ استخدم فقط ما يطابق معنى النص:"]
    for i, c in enumerate(cands, 1):
        lines.append(f"{i}. {c['term']}: {c['definition']}")
    return "\n".join(lines)


def domain_context(domain):
    guide = "\n".join(f"- {g['instruction_ar']}" for g in domain["writing_guidelines"])
    return (
        f"المجال الذي اختاره المستخدم: {domain['names']['ar']}\n"
        f"تعريف المجال: {domain['definition']['text_ar']}\n"
        f"إرشادات الكتابة:\n{guide}"
    )


def context(condition, cands, domain):
    if condition == "T0_qwen_only":
        return ""
    t = term_context(cands)
    if condition == "T1_terminology":
        return t
    return domain_context(domain) + "\n\n" + t


def messages(text, ctx):
    user = (ctx + "\n\n" if ctx else "") + "النص المطلوب تحسينه:\n" + text
    return [{"role": "system", "content": SYSTEM}, {"role": "user", "content": user}]


def score_use(output, item, by_id):
    if item["kind"] != "positive":
        return None
    term = by_id[item["expected_term_id"]]
    return {
        "canonical_term_used": has(output, term["term"]),
        "accepted_lexicon_form_used": any(has(output, f) for f in forms(term)),
    }


def generation_summary(result):
    out = {}
    positives = [x for x in result["items"] if x["kind"] == "positive"]
    for cond in CONDITIONS:
        vals = []
        for x in positives:
            run = x["conditions"].get(cond)
            if run:
                vals.append(bool(run["term_usage"]["canonical_term_used"]))
        out[cond] = {
            "n_scored": len(vals),
            "canonical_term_used": sum(vals),
            "canonical_term_use_rate": round(sum(vals) / len(vals), 4) if vals else None,
        }
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--top-k", type=int, default=5)
    ap.add_argument("--temperature", type=float, default=0.0)
    ap.add_argument("--max-tokens", type=int, default=256)
    ap.add_argument("--timeout", type=int, default=0)
    ap.add_argument("--retries", type=int, default=-1)
    ap.add_argument("--retry-wait", type=int, default=20)
    ap.add_argument("--sleep", type=float, default=1.0)
    ap.add_argument("--retrieval-only", action="store_true")
    ap.add_argument("--restart", action="store_true")
    args = ap.parse_args()

    load_dotenv(ROOT / ".env")
    dataset, terms, domain_store = load_json(INPUTS), load_json(TERMS), load_json(DOMAIN)
    items = dataset["items"]
    validate(dataset, terms)
    domain = next(d for d in domain_store["domains"] if d["domain_id"] == dataset["domain_id"])
    ret, device = retrieve(terms, items, args.top_k)
    rsum = retrieval_summary(items, ret)
    print(json.dumps(rsum, ensure_ascii=False, indent=2))
    for item in items:
        if item["kind"] == "positive":
            print(f"{item['id']} expected={item['expected_term']} rank={ret[item['id']]['expected_rank']}")

    OUTDIR.mkdir(parents=True, exist_ok=True)
    if args.retrieval_only:
        save_json({"summary": rsum, "items": ret}, OUTDIR / "retrieval_preview.json")
        print("Saved retrieval_preview.json")
        return

    api_key = os.getenv("SALEEM_API_KEY", "").strip()
    if not api_key:
        raise SystemExit("Missing SALEEM_API_KEY in local .env")
    base_url = os.getenv("SALEEM_BASE_URL", DEFAULT_BASE_URL).strip()
    model = os.getenv("SALEEM_MODEL", DEFAULT_MODEL).strip()
    by_id = {t["id"]: t for t in terms}

    if CHECKPOINT.exists() and not args.restart:
        result = load_json(CHECKPOINT)
        print("Resuming existing checkpoint.")
    else:
        result = {
            "metadata": {
                "experiment": "final_saleem_specialization_layer_v1",
                "timestamp_utc": datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"),
                "model": model, "retrieval_model": RETRIEVAL_MODEL,
                "retrieval_device": device, "top_k": args.top_k,
                "temperature": args.temperature, "max_tokens": args.max_tokens,
                "conditions": CONDITIONS, "enable_thinking": False,
                "input_dataset": str(INPUTS.relative_to(ROOT)),
                "terminology_dataset": str(TERMS.relative_to(ROOT)),
                "domain_dataset": str(DOMAIN.relative_to(ROOT)),
            },
            "summary": {"retrieval": rsum, "generation": {}},
            "items": [{
                "id": x["id"], "kind": x["kind"], "input": x["text"],
                "expected_term_id": x.get("expected_term_id"),
                "expected_term": x.get("expected_term"),
                "retrieval": ret[x["id"]], "conditions": {}
            } for x in items]
        }
        save_json(result, CHECKPOINT)

    rows = {x["id"]: x for x in result["items"]}
    total = len(items) * len(CONDITIONS)
    done = sum(len(x["conditions"]) for x in result["items"])

    for item in items:
        row = rows[item["id"]]
        cands = ret[item["id"]]["top_k"]
        for cond in CONDITIONS:
            if cond in row["conditions"]:
                continue
            ctx = context(cond, cands, domain)
            print(f"[{done+1}/{total}] {item['id']} {cond}")
            started = time.perf_counter()
            response = call_with_retry(
                base_url=base_url, api_key=api_key, model=model,
                messages=messages(item["text"], ctx),
                temperature=args.temperature, max_tokens=args.max_tokens,
                timeout=args.timeout, retries=args.retries,
                retry_wait=args.retry_wait,
            )
            elapsed = round(time.perf_counter() - started, 3)
            output = extract_output(response)
            finish = (response.get("choices") or [{}])[0].get("finish_reason")
            if finish == "length":
                raise RuntimeError("Output hit max_tokens; restart with a larger fixed limit.")
            low = output.lstrip().lower()
            if low.startswith("thinking process:") or "<think>" in low:
                raise RuntimeError("Thinking content leaked into output.")

            row["conditions"][cond] = {
                "output": output,
                "term_usage": score_use(output, item, by_id),
                "api_metadata": {
                    "finish_reason": finish, "elapsed_seconds": elapsed,
                    "usage": response.get("usage"),
                },
            }
            done += 1
            result["summary"]["generation"] = generation_summary(result)
            save_json(result, CHECKPOINT)
            print(f"  {elapsed:.3f}s | saved {done}/{total}")
            if args.sleep:
                time.sleep(args.sleep)

    result["summary"]["generation"] = generation_summary(result)
    stamp = result["metadata"]["timestamp_utc"]
    final_path = OUTDIR / f"final_layer_experiment_{stamp}.json"
    save_json(result, final_path)
    if CHECKPOINT.exists():
        CHECKPOINT.unlink()
    print("\nFINAL SUMMARY")
    print(json.dumps(result["summary"], ensure_ascii=False, indent=2))
    print(f"Saved: {final_path}")


if __name__ == "__main__":
    main()
