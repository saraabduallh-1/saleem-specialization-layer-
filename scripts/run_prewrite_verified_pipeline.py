#!/usr/bin/env python3
"""Pre-write semantic verification -> forced rewrite -> simple post-validator.

This follow-up reuses the exact Top-3 semantic-selector decisions from the
completed semantic-selection experiment. Gold/expected labels are evaluation
only and are never sent to Qwen.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import time
from datetime import datetime, timezone
from pathlib import Path

from run_final_layer_experiment import ROOT, TERMS, DOMAIN, norm
from run_qwen_domain_ablation import (
    DEFAULT_BASE_URL,
    DEFAULT_MODEL,
    call_with_retry,
    extract_output,
    load_dotenv,
    load_json,
    save_json,
)

DEFAULT_SELECTION = (
    ROOT
    / "results"
    / "semantic_selection_experiment"
    / "semantic_selection_experiment_20261008T102751Z.json"
)
OUTDIR = ROOT / "results" / "prewrite_verified_pipeline_experiment"
CHECKPOINT = OUTDIR / "prewrite_verified_pipeline_in_progress.json"

PREVERIFY_SYSTEM = (
    "تحقق من أن المصطلح التخصصي المرشح هو المفهوم التقني المحدد الذي يصف المعنى الرئيس في النص الأصلي. "
    "لا يكفي أن يكون المصطلح مرتبطًا بالموضوع أو أن تظهر كلمة مشابهة في النص. "
    "ارفض المصطلح إذا كان أوسع أو أضيق من المقصود، أو مجرد جزء من الظاهرة، أو يحمل معنى تقنيًا مختلفًا عن الاستعمال في النص. "
    "لا تشترط أن يكون المصطلح مكتوبًا حرفيًا في النص الأصلي؛ المطلوب مطابقة المفهوم مع التعريف. "
    "أعد JSON فقط بهذه الصيغة: "
    '{"match":true,"reason":"..."} أو {"match":false,"reason":"..."}.'
)

WRITER_SYSTEM = (
    "أعد صياغة النص العربي ليصبح واضحًا وفصيحًا وتخصصيًا مع الحفاظ الكامل على جميع معلوماته ومعناه. "
    "لا تضف حقائق أو أمثلة أو علاقات أو قدرات أو درجة يقين غير موجودة في النص الأصلي. "
    "لا تشرح التعليمات ولا تعريف المصطلح، ولا تقل: المصطلح المعتمد، تم التحقق، يُعرّف بأنه، أو النص المحسن. "
    "أعد النص النهائي فقط دون أي شرح إضافي."
)

POSTVALIDATOR_SYSTEM = (
    "قارن الصياغة الجديدة بالنص الأصلي فقط. لا تقرر هل المصطلح التخصصي مناسب؛ هذا القرار تم قبل الكتابة. "
    "تحقق فقط من أن المعنى والمعلومات الأصلية محفوظة، وأن الصياغة لا تضيف حقائق أو علاقات أو قدرات أو درجة يقين جديدة، "
    "وأنها لا تتضمن شرحًا للتعليمات أو حديثًا عن عملية التحقق. "
    "أعد JSON فقط بهذه الصيغة: "
    '{"meaning_preserved":true,"unsupported_addition":false,"instruction_leak":false,"reason":"..."}.'
)

FORBIDDEN_META = [
    "المصطلح المعتمد",
    "تم التحقق",
    "التحقق الدلالي",
    "النص المحسن",
    "ملاحظات التصحيح",
    "التعليمات",
]


def selection_path(explicit: str | None) -> Path:
    if not explicit:
        path = DEFAULT_SELECTION
    else:
        path = Path(explicit)
        if not path.is_absolute():
            path = ROOT / path
    if not path.exists():
        raise FileNotFoundError(path)
    return path


def selected_from_row(row: dict) -> dict | None:
    sel = row.get("selection") or {}
    if not sel.get("selected_term_id"):
        return None
    return {
        "id": sel["selected_term_id"],
        "term": sel["selected_term"],
        "definition": sel["selected_definition"],
    }


def preverify_messages(text: str, selected: dict):
    return [
        {"role": "system", "content": PREVERIFY_SYSTEM},
        {
            "role": "user",
            "content": (
                "النص الأصلي:\n"
                + text
                + "\n\nالمصطلح المرشح:\n"
                + selected["term"]
                + "\n\nتعريف المصطلح:\n"
                + selected["definition"]
            ),
        },
    ]


def writer_messages(
    text: str,
    verified_term: dict | None,
    domain_name: str,
    correction: str | None = None,
):
    parts = [f"المجال الذي اختاره المستخدم: {domain_name}"]
    if verified_term:
        parts.extend(
            [
                f"المصطلح التخصصي المطلوب استخدامه: {verified_term['term']}",
                (
                    f"استخدم المصطلح «{verified_term['term']}» مرة واحدة على الأقل داخل الصياغة النهائية استخدامًا طبيعيًا. "
                    "يجوز إضافة أل التعريف عند الحاجة النحوية، لكن لا تستبدل كلمات المصطلح بمرادفات. "
                    "لا تشرح تعريف المصطلح ولا تضف منه معلومات ليست موجودة في النص الأصلي."
                ),
            ]
        )
    else:
        parts.append(
            "لم يجتز أي مصطلح التحقق الدلالي. لا تفرض مصطلحًا تخصصيًا من المعجم، وحسّن النص فقط."
        )
    if correction:
        parts.append("تصحيح مطلوب للمحاولة الجديدة:\n" + correction)
    parts.append("النص الأصلي:\n" + text)
    return [
        {"role": "system", "content": WRITER_SYSTEM},
        {"role": "user", "content": "\n\n".join(parts)},
    ]


def postvalidator_messages(source: str, output: str):
    return [
        {"role": "system", "content": POSTVALIDATOR_SYSTEM},
        {
            "role": "user",
            "content": "النص الأصلي:\n" + source + "\n\nالصياغة الجديدة:\n" + output,
        },
    ]


def call_qwen(base_url, api_key, model, messages, args):
    started = time.perf_counter()
    response = call_with_retry(
        base_url=base_url,
        api_key=api_key,
        model=model,
        messages=messages,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
        timeout=args.timeout,
        retries=args.retries,
        retry_wait=args.retry_wait,
    )
    output = extract_output(response)
    finish = (response.get("choices") or [{}])[0].get("finish_reason")
    if finish == "length":
        raise RuntimeError("Output hit max_tokens; result not saved.")
    low = output.lstrip().lower()
    if low.startswith("thinking process:") or "<think>" in low:
        raise RuntimeError("Thinking content leaked into output.")
    return output, {
        "finish_reason": finish,
        "elapsed_seconds": round(time.perf_counter() - started, 3),
        "usage": response.get("usage"),
    }


def parse_json_object(raw: str) -> dict:
    fence = chr(96) * 3
    cleaned = raw.strip().replace(fence + "json", "").replace(fence, "").strip()
    try:
        return json.loads(cleaned)
    except Exception:
        match = re.search(r"\{.*\}", cleaned, flags=re.S)
        if not match:
            raise ValueError(f"Could not parse JSON output: {raw}")
        return json.loads(match.group(0))


def token_norm(text: str) -> list[str]:
    cleaned = norm(text)
    cleaned = re.sub(r"[^\u0621-\u063A\u0641-\u064A0-9A-Za-z]+", " ", cleaned)
    return [x for x in cleaned.split() if x]


def strip_definite_article(token: str) -> str:
    if token.startswith("ال") and len(token) > 3:
        return token[2:]
    return token


def tolerant_term_present(output: str, term: str | None) -> bool | None:
    if not term:
        return None
    out_tokens = [strip_definite_article(x) for x in token_norm(output)]
    term_tokens = [strip_definite_article(x) for x in token_norm(term)]
    if not term_tokens:
        return False
    width = len(term_tokens)
    return any(
        out_tokens[i : i + width] == term_tokens
        for i in range(len(out_tokens) - width + 1)
    )


def instruction_leak(output: str) -> bool:
    text = norm(output)
    return any(norm(x) in text for x in FORBIDDEN_META)


def normalize_postvalidation(raw: dict, output: str, verified_term: dict | None) -> dict:
    meaning = bool(raw.get("meaning_preserved"))
    unsupported = bool(raw.get("unsupported_addition"))
    leak_model = bool(raw.get("instruction_leak"))
    leak_hard = instruction_leak(output)
    term_present = tolerant_term_present(
        output, verified_term["term"] if verified_term else None
    )
    passed = meaning and not unsupported and not leak_model and not leak_hard
    if verified_term:
        passed = passed and bool(term_present)
    return {
        "term_present": term_present,
        "meaning_preserved": meaning,
        "unsupported_addition": unsupported,
        "instruction_leak_model": leak_model,
        "instruction_leak_hard": leak_hard,
        "pass": passed,
        "reason": str(raw.get("reason", "")),
    }


def retry_correction(v: dict, verified_term: dict | None) -> str:
    issues = []
    if verified_term and not v["term_present"]:
        issues.append(
            f"استخدم المصطلح «{verified_term['term']}» صراحة وبصورة طبيعية في النص النهائي."
        )
    if not v["meaning_preserved"]:
        issues.append("حافظ على جميع معلومات ومعنى النص الأصلي دون حذف أو تغيير.")
    if v["unsupported_addition"]:
        issues.append("احذف أي معلومة أو علاقة أو تفصيل غير موجود في النص الأصلي.")
    if v["instruction_leak_model"] or v["instruction_leak_hard"]:
        issues.append("احذف أي حديث عن التعليمات أو التحقق أو المصطلح المطلوب.")
    return "\n".join(f"- {x}" for x in issues) or "- أعد الصياغة بدقة أكبر."


def expected_term_present(output: str, row: dict) -> bool | None:
    if row["kind"] != "positive":
        return None
    return tolerant_term_present(output, row.get("expected_term"))


def summarize(result: dict) -> dict:
    items = result["items"]
    positives = [x for x in items if x["kind"] == "positive"]
    controls = [x for x in items if x["kind"] != "positive"]
    selected = [x for x in items if x.get("selected_term")]
    verified = [
        x for x in selected if (x.get("preverification") or {}).get("match") is True
    ]
    selector_correct = [
        x
        for x in positives
        if (x.get("selection") or {}).get("evaluation", {}).get("correct")
    ]
    selector_wrong = [
        x
        for x in positives
        if not (x.get("selection") or {}).get("evaluation", {}).get("correct")
    ]
    selector_correct_selected = [x for x in selector_correct if x.get("selected_term")]
    selector_wrong_selected = [x for x in selector_wrong if x.get("selected_term")]
    final = [x for x in items if x.get("final_validation")]

    correct_accept = sum(
        (x.get("preverification") or {}).get("match") is True
        for x in selector_correct_selected
    )
    wrong_reject = sum(
        (x.get("preverification") or {}).get("match") is False
        for x in selector_wrong_selected
    )
    expected_used = sum(bool(x.get("expected_term_present")) for x in positives)
    correct_verified = [
        x
        for x in selector_correct_selected
        if (x.get("preverification") or {}).get("match") is True
    ]
    expected_used_correct_verified = sum(
        bool(x.get("expected_term_present")) for x in correct_verified
    )
    final_pass = sum(bool(x["final_validation"]["pass"]) for x in final)
    control_safe = sum(
        (x.get("verified_term") is None)
        and bool((x.get("final_validation") or {}).get("pass"))
        for x in controls
    )

    return {
        "n_items": len(items),
        "selected_for_preverification": len(selected),
        "preverification_accept": len(verified),
        "selector_correct_selected_n": len(selector_correct_selected),
        "preverification_accept_on_selector_correct": correct_accept,
        "preverification_accept_rate_on_selector_correct": (
            round(correct_accept / len(selector_correct_selected), 4)
            if selector_correct_selected
            else None
        ),
        "selector_wrong_selected_n": len(selector_wrong_selected),
        "preverification_reject_on_selector_wrong": wrong_reject,
        "preverification_reject_rate_on_selector_wrong": (
            round(wrong_reject / len(selector_wrong_selected), 4)
            if selector_wrong_selected
            else None
        ),
        "final_validation_pass": final_pass,
        "final_validation_pass_rate": (
            round(final_pass / len(final), 4) if final else None
        ),
        "retry_count": sum(
            max(0, len(x.get("attempts", [])) - 1) for x in items
        ),
        "positive_expected_term_used": expected_used,
        "positive_expected_term_use_rate": (
            round(expected_used / len(positives), 4) if positives else None
        ),
        "correct_selector_and_verified_n": len(correct_verified),
        "expected_term_used_when_selector_correct_and_verified": expected_used_correct_verified,
        "expected_term_use_rate_when_selector_correct_and_verified": (
            round(expected_used_correct_verified / len(correct_verified), 4)
            if correct_verified
            else None
        ),
        "control_safe_final": control_safe,
        "control_n": len(controls),
        "control_safe_rate": (
            round(control_safe / len(controls), 4) if controls else None
        ),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--selection-file", default=None)
    ap.add_argument("--temperature", type=float, default=0.0)
    ap.add_argument("--max-tokens", type=int, default=256)
    ap.add_argument("--timeout", type=int, default=0)
    ap.add_argument("--retries", type=int, default=-1)
    ap.add_argument("--retry-wait", type=int, default=20)
    ap.add_argument("--sleep", type=float, default=1.0)
    ap.add_argument("--max-rewrite-attempts", type=int, default=2)
    ap.add_argument("--restart", action="store_true")
    args = ap.parse_args()

    if args.max_rewrite_attempts < 1:
        raise SystemExit("--max-rewrite-attempts must be >= 1")

    load_dotenv(ROOT / ".env")
    api_key = os.getenv("SALEEM_API_KEY", "").strip()
    if not api_key:
        raise SystemExit("Missing SALEEM_API_KEY in local .env")
    base_url = os.getenv("SALEEM_BASE_URL", DEFAULT_BASE_URL).strip()
    model = os.getenv("SALEEM_MODEL", DEFAULT_MODEL).strip()

    source_path = selection_path(args.selection_file)
    source = load_json(source_path)
    domain_store = load_json(DOMAIN)
    domain_id = "artificial_intelligence"
    domain = next(d for d in domain_store["domains"] if d["domain_id"] == domain_id)
    domain_name = domain["names"]["ar"]

    OUTDIR.mkdir(parents=True, exist_ok=True)

    if CHECKPOINT.exists() and not args.restart:
        result = load_json(CHECKPOINT)
        print(f"Resuming checkpoint: {CHECKPOINT}")
    else:
        result = {
            "metadata": {
                "experiment": "prewrite_verified_pipeline_v1",
                "timestamp_utc": datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"),
                "model": model,
                "temperature": args.temperature,
                "max_tokens": args.max_tokens,
                "max_rewrite_attempts": args.max_rewrite_attempts,
                "selection_source": str(source_path.relative_to(ROOT)),
                "selection_experiment": source["metadata"].get("experiment"),
                "notes": [
                    "Reuses fixed Top-3 selector decisions from the prior experiment.",
                    "Pre-write verifier decides semantic fit before generation and never sees Gold labels.",
                    "Post-validator does not reconsider term fit; it checks preservation, unsupported additions, instruction leakage, and deterministic term presence.",
                    "Term presence accepts normal Arabic definite-article variation token by token.",
                    "This is a follow-up ablation on the same 36 inputs, not a new held-out Gold test.",
                ],
            },
            "summary": {},
            "items": [
                {
                    "id": x["id"],
                    "kind": x["kind"],
                    "input": x["input"],
                    "expected_term_id": x.get("expected_term_id"),
                    "expected_term": x.get("expected_term"),
                    "selection": x.get("selection"),
                    "selected_term": selected_from_row(x),
                    "preverification": None,
                    "verified_term": None,
                    "attempts": [],
                    "final_output": None,
                    "final_validation": None,
                    "expected_term_present": None,
                }
                for x in source["items"]
            ],
        }
        save_json(result, CHECKPOINT)

    rows = {x["id"]: x for x in result["items"]}

    for src in source["items"]:
        row = rows[src["id"]]
        if row.get("preverification") is not None:
            continue
        selected = row.get("selected_term")
        if not selected:
            row["preverification"] = {
                "match": None,
                "reason": "Selector returned NONE; no term to verify.",
                "raw_output": None,
                "api_metadata": None,
            }
            row["verified_term"] = None
        else:
            print(f"[VERIFY] {row['id']} term={selected['term']}")
            raw, meta = call_qwen(
                base_url,
                api_key,
                model,
                preverify_messages(row["input"], selected),
                args,
            )
            parsed = parse_json_object(raw)
            match = bool(parsed.get("match"))
            row["preverification"] = {
                "match": match,
                "reason": str(parsed.get("reason", "")),
                "raw_output": raw,
                "api_metadata": meta,
            }
            row["verified_term"] = selected if match else None
            print(f"  match={match}")
            if args.sleep:
                time.sleep(args.sleep)
        result["summary"] = summarize(result)
        save_json(result, CHECKPOINT)

    for row in result["items"]:
        if row.get("final_validation") is not None:
            continue
        verified_term = row.get("verified_term")
        correction = None
        start_attempt = len(row.get("attempts", [])) + 1
        if row.get("attempts"):
            correction = retry_correction(
                row["attempts"][-1]["validation"], verified_term
            )

        for attempt_no in range(start_attempt, args.max_rewrite_attempts + 1):
            print(
                f"[{row['id']}] rewrite attempt {attempt_no}/{args.max_rewrite_attempts} "
                f"term={verified_term['term'] if verified_term else 'NONE'}"
            )
            output, writer_meta = call_qwen(
                base_url,
                api_key,
                model,
                writer_messages(
                    row["input"], verified_term, domain_name, correction
                ),
                args,
            )
            raw_val, val_meta = call_qwen(
                base_url,
                api_key,
                model,
                postvalidator_messages(row["input"], output),
                args,
            )
            parsed_val = parse_json_object(raw_val)
            validation = normalize_postvalidation(
                parsed_val, output, verified_term
            )
            row["attempts"].append(
                {
                    "attempt": attempt_no,
                    "forced_term_id": verified_term["id"] if verified_term else None,
                    "forced_term": verified_term["term"] if verified_term else None,
                    "output": output,
                    "writer_api_metadata": writer_meta,
                    "validator_raw_output": raw_val,
                    "validator_api_metadata": val_meta,
                    "validation": validation,
                }
            )
            result["summary"] = summarize(result)
            save_json(result, CHECKPOINT)
            print(
                f"  pass={validation['pass']} present={validation['term_present']} "
                f"meaning={validation['meaning_preserved']} "
                f"unsupported={validation['unsupported_addition']} "
                f"leak={validation['instruction_leak_hard']}"
            )
            if validation["pass"]:
                break
            correction = retry_correction(validation, verified_term)
            if args.sleep:
                time.sleep(args.sleep)

        last = row["attempts"][-1]
        row["final_output"] = last["output"]
        row["final_validation"] = last["validation"]
        row["expected_term_present"] = expected_term_present(
            row["final_output"], row
        )
        result["summary"] = summarize(result)
        save_json(result, CHECKPOINT)

    stamp = result["metadata"]["timestamp_utc"]
    final_path = OUTDIR / f"prewrite_verified_pipeline_{stamp}.json"
    result["summary"] = summarize(result)
    save_json(result, final_path)
    if CHECKPOINT.exists():
        CHECKPOINT.unlink()

    print("\nFINAL SUMMARY")
    print(json.dumps(result["summary"], ensure_ascii=False, indent=2))
    print(f"Saved: {final_path}")


if __name__ == "__main__":
    main()
