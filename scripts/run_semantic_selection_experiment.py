#!/usr/bin/env python3
"""Top-3 retrieval -> semantic selection -> controlled rewrite experiment."""

from __future__ import annotations

import argparse
import json
import os
import re
import time
from datetime import datetime, timezone
from pathlib import Path

from run_final_layer_experiment import (
    ROOT, TERMS, DOMAIN, INPUTS, RETRIEVAL_MODEL,
    retrieve, retrieval_summary, score_use,
)
from run_qwen_domain_ablation import (
    DEFAULT_BASE_URL, DEFAULT_MODEL, call_with_retry, extract_output,
    load_dotenv, load_json, save_json,
)

TOP_K = 3
CONDITIONS = ["S0_qwen_only", "S1_selected_term", "S2_selected_term_domain"]
OUTDIR = ROOT / "results" / "semantic_selection_experiment"
CHECKPOINT = OUTDIR / "semantic_selection_in_progress.json"

SELECTOR_SYSTEM = (
    "تحقق دلاليًا من المصطلحات المرشحة. اختر مصطلحًا واحدًا فقط إذا كان تعريفه يطابق المفهوم الموجود فعلًا في النص. "
    "لا تعتمد على تشابه لفظي أو كلمة مشتركة فقط. إذا لم يطابق أي مرشح معنى النص فاختر NONE. "
    "أعد JSON فقط: {\"choice\":\"C1\"} أو C2 أو C3 أو NONE ضمن الحقل نفسه."
)

REWRITE_SYSTEM = (
    "أعد صياغة النص العربي ليصبح واضحًا وفصيحًا وتخصصيًا مع الحفاظ الكامل على جميع معانيه ومعلوماته. "
    "لا تضف حقائق أو علاقات أو قدرات أو درجة يقين غير موجودة في النص. أعد النص النهائي فقط دون شرح."
)


def selector_messages(text, candidates):
    blocks = ["النص:\n" + text, "المصطلحات المرشحة:"]
    for i, c in enumerate(candidates, 1):
        blocks.append(f"C{i}\nالمصطلح: {c['term']}\nالتعريف: {c['definition']}")
    return [
        {"role": "system", "content": SELECTOR_SYSTEM},
        {"role": "user", "content": "\n\n".join(blocks)},
    ]


def parse_choice(raw):
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\\s*", "", cleaned)
        cleaned = re.sub(r"\\s*```$", "", cleaned)
    try:
        choice = str(json.loads(cleaned).get("choice", "")).upper()
    except Exception:
        m = re.search(r"\\b(C1|C2|C3|NONE)\\b", cleaned.upper())
        if not m:
            raise ValueError(f"Cannot parse selector output: {raw}")
        choice = m.group(1)
    if choice not in {"C1", "C2", "C3", "NONE"}:
        raise ValueError(f"Invalid selector choice: {choice}")
    return choice


def selected_candidate(choice, candidates):
    if choice == "NONE":
        return None
    return candidates[int(choice[1:]) - 1]


def domain_context(domain):
    guidelines = "\n".join(f"- {g['instruction_ar']}" for g in domain['writing_guidelines'])
    return (
        f"المجال الذي اختاره المستخدم: {domain['names']['ar']}\n"
        f"تعريف المجال: {domain['definition']['text_ar']}\n"
        f"إرشادات الكتابة في المجال:\n{guidelines}"
    )


def term_context(selected):
    if selected is None:
        return (
            "لم تجد مرحلة التحقق الدلالي مصطلحًا مناسبًا. لا تفرض مصطلحًا معجميًا، وحسّن الصياغة فقط."
        )
    return (
        "تم التحقق دلاليًا من المصطلح التالي، وهو المصطلح المعتمد لهذا النص:\n"
        f"المصطلح: {selected['term']}\n"
        f"التعريف: {selected['definition']}\n"
        "استخدم المصطلح العربي المعتمد في النص النهائي استخدامًا طبيعيًا وصحيحًا، ولا تستبدله بوصف عام. "
        "لا تضف من التعريف أي معلومة غير موجودة في النص الأصلي."
    )


def rewrite_messages(text, condition, selected, domain):
    parts = []
    if condition in {"S1_selected_term", "S2_selected_term_domain"}:
        parts.append(term_context(selected))
    if condition == "S2_selected_term_domain":
        parts.append(domain_context(domain))
    parts.append("النص المطلوب تحسينه:\n" + text)
    return [
        {"role": "system", "content": REWRITE_SYSTEM},
        {"role": "user", "content": "\n\n".join(parts)},
    ]


def call_qwen(base_url, api_key, model, messages, args):
    started = time.perf_counter()
    response = call_with_retry(
        base_url=base_url, api_key=api_key, model=model, messages=messages,
        temperature=args.temperature, max_tokens=args.max_tokens,
        timeout=args.timeout, retries=args.retries, retry_wait=args.retry_wait,
    )
    output = extract_output(response)
    finish = (response.get("choices") or [{}])[0].get("finish_reason")
    if finish == "length":
        raise RuntimeError("Generation hit max_tokens; result not saved.")
    low = output.lstrip().lower()
    if low.startswith("thinking process:") or "<think>" in low:
        raise RuntimeError("Thinking content leaked into output.")
    return output, {
        "finish_reason": finish,
        "elapsed_seconds": round(time.perf_counter() - started, 3),
        "usage": response.get("usage"),
    }


def selector_eval(item, selected):
    selected_id = selected['id'] if selected else None
    expected = item.get('expected_term_id') if item['kind'] == 'positive' else None
    return {"correct": selected_id == expected, "expected": expected, "selected": selected_id}


def summarize_selector(result):
    rows = [x for x in result['items'] if x.get('selection')]
    positives = [x for x in rows if x['kind'] == 'positive']
    controls = [x for x in rows if x['kind'] != 'positive']
    def rate(xs):
        return round(sum(x['selection']['evaluation']['correct'] for x in xs) / len(xs), 4) if xs else None
    return {
        "overall_accuracy": rate(rows),
        "positive_accuracy": rate(positives),
        "positive_correct": sum(x['selection']['evaluation']['correct'] for x in positives),
        "positive_n": len(positives),
        "control_abstention_accuracy": rate(controls),
        "control_correct": sum(x['selection']['evaluation']['correct'] for x in controls),
        "control_n": len(controls),
        "none_count": sum(x['selection']['choice'] == 'NONE' for x in rows),
    }


def summarize_generation(result):
    positives = [x for x in result['items'] if x['kind'] == 'positive']
    out = {}
    for cond in CONDITIONS:
        vals = []
        for x in positives:
            run = x['conditions'].get(cond)
            if run and run.get('term_usage') is not None:
                vals.append(bool(run['term_usage']['canonical_term_used']))
        out[cond] = {
            "n_scored": len(vals),
            "canonical_term_used": sum(vals),
            "canonical_term_use_rate": round(sum(vals) / len(vals), 4) if vals else None,
        }
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--temperature', type=float, default=0.0)
    ap.add_argument('--max-tokens', type=int, default=256)
    ap.add_argument('--timeout', type=int, default=0)
    ap.add_argument('--retries', type=int, default=-1)
    ap.add_argument('--retry-wait', type=int, default=20)
    ap.add_argument('--sleep', type=float, default=1.0)
    ap.add_argument('--restart', action='store_true')
    args = ap.parse_args()

    load_dotenv(ROOT / '.env')
    api_key = os.getenv('SALEEM_API_KEY', '').strip()
    if not api_key:
        raise SystemExit('Missing SALEEM_API_KEY in local .env')
    base_url = os.getenv('SALEEM_BASE_URL', DEFAULT_BASE_URL).strip()
    model = os.getenv('SALEEM_MODEL', DEFAULT_MODEL).strip()

    dataset = load_json(INPUTS)
    terms = load_json(TERMS)
    domain_store = load_json(DOMAIN)
    items = dataset['items']
    domain = next(d for d in domain_store['domains'] if d['domain_id'] == dataset['domain_id'])
    by_id = {t['id']: t for t in terms}

    retrieval, device = retrieve(terms, items, TOP_K)
    rsum = retrieval_summary(items, retrieval)
    print('Retrieval:', json.dumps(rsum, ensure_ascii=False, indent=2))

    OUTDIR.mkdir(parents=True, exist_ok=True)
    if CHECKPOINT.exists() and not args.restart:
        result = load_json(CHECKPOINT)
        print(f'Resuming checkpoint: {CHECKPOINT}')
    else:
        result = {
            'metadata': {
                'experiment': 'semantic_selection_top3_v1',
                'timestamp_utc': datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ'),
                'model': model, 'retrieval_model': RETRIEVAL_MODEL,
                'retrieval_device': device, 'top_k': TOP_K,
                'temperature': args.temperature, 'max_tokens': args.max_tokens,
                'conditions': CONDITIONS,
                'notes': [
                    'Follow-up ablation on the same 36 inputs; not a new held-out Gold test.',
                    'One semantic selector call per item; the same choice is reused in S1 and S2.',
                    'Expected labels are evaluation-only and are never sent to Qwen.',
                ],
            },
            'summary': {'retrieval': rsum, 'selector': {}, 'generation': {}},
            'items': [{
                'id': x['id'], 'kind': x['kind'], 'input': x['text'],
                'expected_term_id': x.get('expected_term_id'),
                'expected_term': x.get('expected_term'),
                'retrieval': retrieval[x['id']],
                'selection': None, 'conditions': {},
            } for x in items],
        }
        save_json(result, CHECKPOINT)

    rows = {x['id']: x for x in result['items']}

    for item in items:
        row = rows[item['id']]
        if row.get('selection'):
            continue
        candidates = retrieval[item['id']]['top_k']
        print(f"[SELECT] {item['id']}")
        raw, meta = call_qwen(base_url, api_key, model, selector_messages(item['text'], candidates), args)
        choice = parse_choice(raw)
        selected = selected_candidate(choice, candidates)
        row['selection'] = {
            'choice': choice,
            'selected_term_id': selected['id'] if selected else None,
            'selected_term': selected['term'] if selected else None,
            'selected_definition': selected['definition'] if selected else None,
            'raw_output': raw, 'api_metadata': meta,
        }
        row['selection']['evaluation'] = selector_eval(item, selected)
        result['summary']['selector'] = summarize_selector(result)
        save_json(result, CHECKPOINT)
        print(f"  choice={choice} term={row['selection']['selected_term']} correct={row['selection']['evaluation']['correct']}")
        if args.sleep:
            time.sleep(args.sleep)

    total = len(items) * len(CONDITIONS)
    done = sum(len(x['conditions']) for x in result['items'])
    for item in items:
        row = rows[item['id']]
        selected = None
        if row['selection']['selected_term_id']:
            selected = {
                'id': row['selection']['selected_term_id'],
                'term': row['selection']['selected_term'],
                'definition': row['selection']['selected_definition'],
            }
        for cond in CONDITIONS:
            if cond in row['conditions']:
                continue
            print(f"[{done + 1}/{total}] {item['id']} {cond}")
            output, meta = call_qwen(base_url, api_key, model, rewrite_messages(item['text'], cond, selected, domain), args)
            row['conditions'][cond] = {
                'output': output,
                'term_usage': score_use(output, item, by_id),
                'api_metadata': meta,
            }
            done += 1
            result['summary']['selector'] = summarize_selector(result)
            result['summary']['generation'] = summarize_generation(result)
            save_json(result, CHECKPOINT)
            print(f'  saved {done}/{total}')
            if args.sleep:
                time.sleep(args.sleep)

    result['summary']['selector'] = summarize_selector(result)
    result['summary']['generation'] = summarize_generation(result)
    stamp = result['metadata']['timestamp_utc']
    final_path = OUTDIR / f'semantic_selection_experiment_{stamp}.json'
    save_json(result, final_path)
    if CHECKPOINT.exists():
        CHECKPOINT.unlink()
    print('\nFINAL SUMMARY')
    print(json.dumps(result['summary'], ensure_ascii=False, indent=2))
    print(f'Saved: {final_path}')


if __name__ == '__main__':
    main()
