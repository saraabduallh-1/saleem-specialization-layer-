#!/usr/bin/env python3
"""Run D0-D4 domain-context ablation against the company Qwen endpoint.

No training or model changes are performed. The same model, prompts, inputs,
and generation settings are reused across all conditions; only injected
domain context changes.

Expected local secrets:
    SALEEM_API_KEY
Optional overrides:
    SALEEM_BASE_URL (default: http://136.119.196.95:8000/v1)
    SALEEM_MODEL    (default: Qwen/Qwen3.5-4B)
"""

from __future__ import annotations

import argparse
import json
import os
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DOMAIN_PATH = ROOT / "data" / "domain" / "saleem_domain_knowledge_v1.json"
INPUTS_PATH = ROOT / "data" / "evaluation" / "domain_ai_pilot_inputs.json"
RESULTS_DIR = ROOT / "results" / "domain_ablation_qwen"

DEFAULT_BASE_URL = "http://136.119.196.95:8000/v1"
DEFAULT_MODEL = "Qwen/Qwen3.5-4B"

CONDITIONS = [
    "D0_saleem_only",
    "D1_domain_name",
    "D2_domain_name_definition",
    "D3_domain_guidance",
    "D4_domain_guidance_examples",
]

BASE_INSTRUCTION = (
    "أعد صياغة النص العربي ليكون أوضح وأدق مع الحفاظ على معناه. "
    "لا تضف حقائق أو معلومات غير موجودة في النص. أعد النص المصاغ فقط دون شرح."
)


def load_dotenv(path: Path) -> None:
    if not path.exists():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key, value = key.strip(), value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def build_context(domain: dict[str, Any], condition: str) -> str:
    if condition == "D0_saleem_only":
        return ""
    parts: list[str] = []

    if condition in {
        "D1_domain_name",
        "D2_domain_name_definition",
        "D3_domain_guidance",
        "D4_domain_guidance_examples",
    }:
        parts.append(f"المجال: {domain['names']['ar']}")

    if condition in {
        "D2_domain_name_definition",
        "D3_domain_guidance",
        "D4_domain_guidance_examples",
    }:
        parts.append(f"تعريف المجال: {domain['definition']['text_ar']}")

    if condition in {"D3_domain_guidance", "D4_domain_guidance_examples"}:
        guidelines = "\n".join(
            f"- {g['instruction_ar']}" for g in domain["writing_guidelines"]
        )
        parts.append("إرشادات الكتابة في المجال:\n" + guidelines)

    if condition == "D4_domain_guidance_examples":
        examples = "\n".join(
            f"- {e['text_ar']}" for e in domain["examples"]["items"]
        )
        parts.append("أمثلة حقيقية على الكتابة في المجال:\n" + examples)

    return "\n\n".join(parts)


def make_messages(text: str, context: str) -> list[dict[str, str]]:
    user_parts = []
    if context:
        user_parts.append(context)
    user_parts.append("النص المطلوب تحسينه:\n" + text)
    return [
        {"role": "system", "content": BASE_INSTRUCTION},
        {"role": "user", "content": "\n\n".join(user_parts)},
    ]


def call_chat_completions(
    *,
    base_url: str,
    api_key: str,
    model: str,
    messages: list[dict[str, str]],
    temperature: float,
    timeout: int,
) -> dict[str, Any]:
    url = base_url.rstrip("/") + "/chat/completions"
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
    }
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def extract_output(response: dict[str, Any]) -> str:
    choices = response.get("choices") or []
    if not choices:
        raise ValueError(f"API response contains no choices: {response}")
    message = choices[0].get("message") or {}
    content = message.get("content")
    if isinstance(content, str):
        return content.strip()
    raise ValueError(f"API response contains no text content: {response}")


def write_markdown(result: dict[str, Any], path: Path) -> None:
    lines = [
        "# Qwen Domain Ablation Pilot",
        "",
        f"- Model: \`{result['metadata']['model']}\`",
        f"- Inputs: {result['metadata']['input_count']}",
        f"- Conditions: {', '.join(result['metadata']['conditions'])}",
        f"- Temperature: {result['metadata']['temperature']}",
        "",
    ]
    for item in result["items"]:
        lines += [
            f"## {item['id']}",
            "",
            f"**Input:** {item['input']}",
            "",
        ]
        for condition in result["metadata"]["conditions"]:
            run = item["conditions"][condition]
            lines += [
                f"### {condition}",
                "",
                run["output"],
                "",
            ]
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--timeout", type=int, default=120)
    parser.add_argument("--sleep", type=float, default=0.0)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    load_dotenv(ROOT / ".env")

    api_key = os.getenv("SALEEM_API_KEY", "").strip()
    base_url = os.getenv("SALEEM_BASE_URL", DEFAULT_BASE_URL).strip()
    model = os.getenv("SALEEM_MODEL", DEFAULT_MODEL).strip()

    if not args.dry_run and not api_key:
        raise SystemExit(
            "Missing SALEEM_API_KEY. Copy .env.example to .env and put the real key there."
        )

    domain_store = load_json(DOMAIN_PATH)
    domain = next(
        d for d in domain_store["domains"] if d["domain_id"] == "artificial_intelligence"
    )
    input_store = load_json(INPUTS_PATH)
    inputs = input_store["items"][: args.limit] if args.limit else input_store["items"]

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    result: dict[str, Any] = {
        "metadata": {
            "experiment": "qwen_domain_ablation_pilot",
            "timestamp_utc": timestamp,
            "model": model,
            "base_url": base_url,
            "domain_dataset": str(DOMAIN_PATH.relative_to(ROOT)),
            "input_dataset": str(INPUTS_PATH.relative_to(ROOT)),
            "input_count": len(inputs),
            "conditions": CONDITIONS,
            "temperature": args.temperature,
            "base_instruction": BASE_INSTRUCTION,
            "notes": [
                "Pilot only; not the final Gold evaluation.",
                "Same model, inputs and generation settings across D0-D4.",
                "Only injected domain context changes between conditions.",
                "No terminology retrieval is injected in this experiment.",
            ],
        },
        "items": [],
    }

    total = len(inputs) * len(CONDITIONS)
    done = 0

    for item in inputs:
        row = {
            "id": item["id"],
            "input": item["text"],
            "conditions": {},
        }
        for condition in CONDITIONS:
            context = build_context(domain, condition)
            messages = make_messages(item["text"], context)

            if args.dry_run:
                output = "[DRY RUN]"
                raw = None
            else:
                response = call_chat_completions(
                    base_url=base_url,
                    api_key=api_key,
                    model=model,
                    messages=messages,
                    temperature=args.temperature,
                    timeout=args.timeout,
                )
                output = extract_output(response)
                raw = {
                    "id": response.get("id"),
                    "usage": response.get("usage"),
                    "finish_reason": (response.get("choices") or [{}])[0].get("finish_reason"),
                }

            row["conditions"][condition] = {
                "context": context,
                "output": output,
                "api_metadata": raw,
            }
            done += 1
            print(f"[{done}/{total}] {item['id']} {condition}")
            if args.sleep:
                time.sleep(args.sleep)

        result["items"].append(row)

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    json_path = RESULTS_DIR / f"qwen_domain_ablation_{timestamp}.json"
    md_path = RESULTS_DIR / f"qwen_domain_ablation_{timestamp}.md"

    json_path.write_text(
        json.dumps(result, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    write_markdown(result, md_path)

    print(f"\nSaved:\n- {json_path}\n- {md_path}")


if __name__ == "__main__":
    main()
