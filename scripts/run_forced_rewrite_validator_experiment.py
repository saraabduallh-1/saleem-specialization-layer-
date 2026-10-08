#!/usr/bin/env python3
"""Forced rewrite + validator follow-up experiment.

Reuses the exact semantic-selector decisions from the latest completed
Top-3 semantic-selection experiment. No Gold/expected label is sent to
the writer or validator.

Pipeline:
semantic selection (reused) -> forced rewrite -> validation -> targeted retry.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import time
from datetime import datetime, timezone
from pathlib import Path

from run_final_layer_experiment import ROOT, TERMS, DOMAIN, norm, score_use
from run_qwen_domain_ablation import (
    DEFAULT_BASE_URL,
    DEFAULT_MODEL,
    call_with_retry,
    extract_output,
    load_dotenv,
    load_json,
    save_json,
)

SOURCE_DIR = ROOT / "results" / "semantic_selection_experiment"
OUTDIR = ROOT / "results" / "forced_rewrite_validator_experiment"
CHECKPOINT = OUTDIR / "forced_rewrite_validator_in_progress.json"

WRITER_SYSTEM = (
    "أعد صياغة النص العربي ليصبح واضحًا وفصيحًا وتخصصيًا مع الحفاظ الكامل على جميع معانيه ومعلوماته. "
    "لا تضف حقائق أو علاقات أو أمثلة أو قدرات أو درجة يقين غير موجودة في النص الأصلي. "
    "لا تشرح التعليمات ولا تذكر عبارات مثل: المصطلح المعتمد، تم التحقق، يُعرّف بأنه، أو النص المحسن. "
    "أعد النص النهائي فقط."
)

VALIDATOR_SYSTEM = (
    "قيّم الصياغة الجديدة مقارنة بالنص الأصلي فقط. لا تحسّن النص ولا تعيد كتابته. "
    "إذا زُوّدت بمصطلح وتعريفه، فتحقق أولًا هل المفهوم الذي يصفه التعريف موجود فعلًا في النص الأصلي، "
    "ثم تحقق من ظهور المصطلح في الصياغة بصورة طبيعية. "
    "تحقق أيضًا من الحفاظ على كل المعلومات وعدم إضافة حقائق أو علاقات أو قدرات جديدة وعدم تسريب تعليمات النظام. "
    "أعد JSON فقط بالمفاتيح التالية: "
    "{\"selected_term_fit\":true,\"term_present\":true,\"meaning_preserved\":true,"
    "\"unsupported_addition\":false,\"instruction_leak\":false,\"reason\":\"...\"}. "
    "إذا لم يوجد مصطلح مختار، اجعل selected_term_fit وterm_present بقيمة null."
)

FORBIDDEN_META = [
    "المصطلح المعتمد",
    "تم التحقق",
    "التحقق الدلالي",
    "النص المحسن",
    "التعليمات",
]


def latest_selection_file(explicit: str | None) -> Path:
    if explicit:
        path = Path(explicit)
        if not path.is_absolute():
            path = ROOT / path
        if not path.exists():
            raise FileNotFoundError(path)
        return path
    files = sorted(SOURCE_DIR.glob("semantic_selection_experiment_*.json"))
    if not files:
        raise FileNotFoundError(
            "No semantic selection result found. Run the Top-3 semantic-selection experiment first."
        )
    return files[-1]


def writer_messages(text: str, selected: dict | None, domain_name: str, correction: str | None = None):
    parts = [f"المجال: {domain_name}"]
    if selected:
        parts.extend([
            f"المصطلح الذي تم اختياره دلاليًا: {selected['term']}",
            f"تعريف المصطلح: {selected['definition']}",
            (
                f"يجب أن يظهر المصطلح العربي «{selected['term']}» في النص النهائي بصيغته المعجمية "
                "استخدامًا طبيعيًا. لا تستبدله بمرادف أو وصف عام. "
                "لا تنقل تعريف المصطلح إلى النص إلا بقدر ما هو موجود أصلًا في معنى النص."
            ),
        ])
    else:
        parts.append(
            "لم يتم اختيار مصطلح معجمي مناسب. لا تفرض أي مصطلح من المعجم، وحسّن النص فقط."
        )
    if correction:
        parts.append("ملاحظات التصحيح من المحاولة السابقة:
" + correction)
    parts.append("النص الأصلي:
" + text)
    return [
        {"role": "system", "content": WRITER_SYSTEM},
        {"role": "user", "content": "

".join(parts)},
    ]


def validator_messages(source: str, output: str, selected: dict | None):
    parts = [
        "النص الأصلي:
" + source,
        "الصياغة الجديدة:
" + output,
    ]
    if selected:
        parts.append(
            f"المصطلح المختار: {selected['term']}
تعريفه: {selected['definition']}"
        )
    else:
        parts.append("لا يوجد مصطلح مختار.")
    return [
        {"role": "system", "content": VALIDATOR_SYSTEM},
        {"role": "user", "content": "

".join(parts)},
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
    cleaned = raw.strip().replace("```json", "").replace("```", "").strip()
    try:
        obj = json.loads(cleaned)
    except Exception:
        match = re.search(r"\{.*\}", cleaned, flags=re.S)
        if not match:
            raise ValueError(f"Could not parse validator JSON: {raw}")
        obj = json.loads(match.group(0))
    return obj


def lexical_term_present(output: str, selected: dict | None) -> bool | None:
    if not selected:
        return None
    return norm(selected["term"]) in norm(output)


def instruction_leak(output: str) -> bool:
    text = norm(output)
    return any(norm(x) in text for x in FORBIDDEN_META)


def normalize_validation(raw_obj: dict, output: str, selected: dict | None) -> dict:
    model_fit = raw_obj.get("selected_term_fit")
    model_present = raw_obj.get("term_present")
    meaning = bool(raw_obj.get("meaning_preserved"))
    unsupported = bool(raw_obj.get("unsupported_addition"))
    leak_model = bool(raw_obj.get("instruction_leak"))
    lexical = lexical_term_present(output, selected)
    leak_hard = instruction_leak(output)

    if selected:
        fit = bool(model_fit)
        present = bool(model_present) and bool(lexical)
        passed = fit and present and meaning and not unsupported and not leak_model and not leak_hard
    else:
        fit = None
        present = None
        passed = meaning and not unsupported and not leak_model and not leak_hard

    return {
        "selected_term_fit": fit,
        "term_present_model": model_present if selected else None,
        "term_present_lexical": lexical,
        "term_present": present,
        "meaning_preserved": meaning,
        "unsupported_addition": unsupported,
        "instruction_leak_model": leak_model,
        "instruction_leak_hard": leak_hard,
        "pass": passed,
        "reason": str(raw_obj.get("reason", "")),
    }


def correction_from_validation(v: dict, selected: dict | None) -> str:
    issues = []
    if selected and v["selected_term_fit"] is False:
        issues.append(
            "المصطلح المختار لا يطابق معنى النص بحسب التحقق. في المحاولة الجديدة لا تستخدم المصطلح ولا تضف مفهومه."
        )
    elif selected and not v["term_present"]:
        issues.append(f"استخدم المصطلح «{selected['term']}» صراحة وبصورة طبيعية.")
    if not v["meaning_preserved"]:
        issues.append("حافظ على جميع معلومات ومعنى النص الأصلي دون حذف أو تغيير.")
    if v["unsupported_addition"]:
        issues.append("احذف أي معلومة أو علاقة غير موجودة في النص الأصلي.")
    if v["instruction_leak_model"] or v["instruction_leak_hard"]:
        issues.append("احذف أي شرح للتعليمات أو حديث عن المصطلح المعتمد أو عملية التحقق.")
    return "
".join(f"- {x}" for x in issues) or "- أعد الصياغة بدقة أكبر مع الالتزام بالتعليمات."


def effective_selected(selected: dict | None, validation: dict) -> dict | None:
    # If validation says the selector chose a semantically wrong term, abstain on retry.
    if selected and validation.get("selected_term_fit") is False:
        return None
    return selected


def make_selected(row: dict) -> dict | None:
    selection = row.get("selection") or {}
    if not selection.get("selected_term_id"):
        return None
    return {
        "id": selection["selected_term_id"],
        "term": selection["selected_term"],
        "definition": selection["selected_definition"],
    }


def summarize(result: dict) -> dict:
    items = result["items"]
    positives = [x for x in items if x["kind"] == "positive"]
    controls = [x for x in items if x["kind"] != "positive"]

    attempted = [x for x in items if x.get("attempts")]
    final = [x for x in items if x.get("final_validation")]

    initial_pass = sum(bool(x["attempts"][0]["validation"]["pass"]) for x in attempted)
    final_pass = sum(bool(x["final_validation"]["pass"]) for x in final)
    retries = sum(max(0, len(x.get("attempts", [])) - 1) for x in items)

    selected_correct = [
        x for x in positives
        if (x.get("selection") or {}).get("evaluation", {}).get("correct")
    ]
    final_term_correct = sum(
        bool((x.get("final_term_usage") or {}).get("canonical_term_used"))
        for x in selected_correct
    )

    control_pass = sum(bool(x.get("final_validation", {}).get("pass")) for x in controls)

    return {
        "n_items": len(items),
        "initial_validation_pass": initial_pass,
        "initial_validation_pass_rate": round(initial_pass / len(attempted), 4) if attempted else None,
        "final_validation_pass": final_pass,
        "final_validation_pass_rate": round(final_pass / len(final), 4) if final else None,
        "retry_count": retries,
        "selector_correct_positive_n": len(selected_correct),
        "canonical_term_used_after_pipeline_on_selector_correct": final_term_correct,
        "canonical_term_use_rate_on_selector_correct": (
            round(final_term_correct / len(selected_correct), 4) if selected_correct else None
        ),
        "control_final_pass": control_pass,
        "control_n": len(controls),
        "control_final_pass_rate": round(control_pass / len(controls), 4) if controls else None,
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

    source_path = latest_selection_file(args.selection_file)
    source = load_json(source_path)
    terms = load_json(TERMS)
    domain_store = load_json(DOMAIN)
    by_id = {t["id"]: t for t in terms}
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
                "experiment": "forced_rewrite_validator_v1",
                "timestamp_utc": datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"),
                "model": model,
                "temperature": args.temperature,
                "max_tokens": args.max_tokens,
                "max_rewrite_attempts": args.max_rewrite_attempts,
                "selection_source": str(source_path.relative_to(ROOT)),
                "selection_experiment": source["metadata"].get("experiment"),
                "notes": [
                    "Reuses fixed semantic-selector decisions from the previous Top-3 experiment.",
                    "Expected/Gold labels are never sent to the writer or validator.",
                    "Validator combines Qwen semantic checks with deterministic canonical-term presence and instruction-leak checks.",
                    "If the validator judges the selected term semantically wrong, retry abstains from forcing that term.",
                    "This is a follow-up ablation on the same 36 inputs, not a new held-out Gold test.",
                ],
            },
            "summary": {},
            "items": [{
                "id": x["id"],
                "kind": x["kind"],
                "input": x["input"],
                "expected_term_id": x.get("expected_term_id"),
                "expected_term": x.get("expected_term"),
                "selection": x.get("selection"),
                "attempts": [],
                "final_output": None,
                "final_validation": None,
                "final_term_usage": None,
            } for x in source["items"]],
        }
        save_json(result, CHECKPOINT)

    rows = {x["id"]: x for x in result["items"]}

    for src in source["items"]:
        row = rows[src["id"]]
        if row.get("final_validation"):
            continue

        selected_original = make_selected(src)
        selected_for_attempt = selected_original
        correction = None

        start_attempt = len(row["attempts"]) + 1
        if row["attempts"]:
            previous = row["attempts"][-1]["validation"]
            selected_for_attempt = effective_selected(selected_original, previous)
            correction = correction_from_validation(previous, selected_original)

        for attempt_no in range(start_attempt, args.max_rewrite_attempts + 1):
            print(
                f"[{src['id']}] rewrite attempt {attempt_no}/{args.max_rewrite_attempts} "
                f"term={selected_for_attempt['term'] if selected_for_attempt else 'NONE'}"
            )
            output, write_meta = call_qwen(
                base_url,
                api_key,
                model,
                writer_messages(src["input"], selected_for_attempt, domain_name, correction),
                args,
            )
            raw_validation, val_meta = call_qwen(
                base_url,
                api_key,
                model,
                validator_messages(src["input"], output, selected_for_attempt),
                args,
            )
            parsed = parse_json_object(raw_validation)
            validation = normalize_validation(parsed, output, selected_for_attempt)

            row["attempts"].append({
                "attempt": attempt_no,
                "forced_term_id": selected_for_attempt["id"] if selected_for_attempt else None,
                "forced_term": selected_for_attempt["term"] if selected_for_attempt else None,
                "output": output,
                "writer_api_metadata": write_meta,
                "validator_raw_output": raw_validation,
                "validator_api_metadata": val_meta,
                "validation": validation,
            })
            result["summary"] = summarize(result)
            save_json(result, CHECKPOINT)

            print(
                f"  pass={validation['pass']} fit={validation['selected_term_fit']} "
                f"present={validation['term_present']} meaning={validation['meaning_preserved']} "
                f"unsupported={validation['unsupported_addition']} leak={validation['instruction_leak_hard']}"
            )

            if validation["pass"]:
                break

            selected_for_attempt = effective_selected(selected_for_attempt, validation)
            correction = correction_from_validation(validation, selected_original)
            if args.sleep:
                time.sleep(args.sleep)

        last = row["attempts"][-1]
        row["final_output"] = last["output"]
        row["final_validation"] = last["validation"]
        # Evaluation only; not used in writer/validator prompts.
        item_for_score = {
            "kind": src["kind"],
            "expected_term_id": src.get("expected_term_id"),
        }
        row["final_term_usage"] = score_use(row["final_output"], item_for_score, by_id)
        result["summary"] = summarize(result)
        save_json(result, CHECKPOINT)

    stamp = result["metadata"]["timestamp_utc"]
    final_path = OUTDIR / f"forced_rewrite_validator_{stamp}.json"
    result["summary"] = summarize(result)
    save_json(result, final_path)
    if CHECKPOINT.exists():
        CHECKPOINT.unlink()

    print("\nFINAL SUMMARY")
    print(json.dumps(result["summary"], ensure_ascii=False, indent=2))
    print(f"Saved: {final_path}")


if __name__ == "__main__":
    main()
