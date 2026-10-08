#!/usr/bin/env python3
"""Run D0-D4 domain-context ablation against the company Qwen endpoint.

The same model, prompts, inputs, and generation settings are reused across all
conditions; only injected domain context changes.

This runner is resilient to slow API responses:
- long per-request timeout by default,
- automatic retries for timeouts/transient server errors,
- checkpoint saved after every successful condition,
- automatic resume from the checkpoint on rerun.

Expected local secret:
    SALEEM_API_KEY

Optional overrides:
    SALEEM_BASE_URL (default: http://136.119.196.95:8000/v1)
    SALEEM_MODEL    (default: Qwen/Qwen3.5-4B)
"""

from __future__ import annotations

import argparse
import json
import os
import socket
import subprocess
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
CHECKPOINT_PATH = RESULTS_DIR / "qwen_domain_ablation_in_progress.json"

DEFAULT_BASE_URL = "http://136.119.196.95:8000/v1"
DEFAULT_MODEL = "Qwen/Qwen3.5-4B"
ENABLE_THINKING = False

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


def save_json(data: Any, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


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


def call_once(
    *,
    base_url: str,
    api_key: str,
    model: str,
    messages: list[dict[str, str]],
    temperature: float,
    max_tokens: int,
    timeout: int,
) -> dict[str, Any]:
    url = base_url.rstrip("/") + "/chat/completions"
    payload = {
        "model": model,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "chat_template_kwargs": {"enable_thinking": ENABLE_THINKING},
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
    open_kwargs = {}
    if timeout and timeout > 0:
        open_kwargs["timeout"] = timeout
    with urllib.request.urlopen(request, **open_kwargs) as response:
        return json.loads(response.read().decode("utf-8"))


def call_with_retry(
    *,
    base_url: str,
    api_key: str,
    model: str,
    messages: list[dict[str, str]],
    temperature: float,
    max_tokens: int,
    timeout: int,
    retries: int,
    retry_wait: int,
) -> dict[str, Any]:
    """Retry transient failures. retries=-1 means retry forever."""
    attempt = 0

    while True:
        attempt += 1
        try:
            return call_once(
                base_url=base_url,
                api_key=api_key,
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                timeout=timeout,
            )
        except urllib.error.HTTPError as exc:
            # Authentication/permission errors will not improve by retrying.
            if exc.code in {400, 401, 403, 404}:
                raise
            retryable = exc.code == 429 or 500 <= exc.code <= 599
            if not retryable:
                raise
            if retries >= 0 and attempt > retries:
                raise
            label = "forever" if retries < 0 else str(retries)
            print(
                f"  transient HTTP {exc.code}; retry attempt {attempt} "
                f"(limit: {label}) after {retry_wait}s"
            )
        except (TimeoutError, socket.timeout, ConnectionResetError, urllib.error.URLError) as exc:
            if retries >= 0 and attempt > retries:
                raise
            label = "forever" if retries < 0 else str(retries)
            print(
                f"  temporary connection/timeout error: {exc}; retry attempt {attempt} "
                f"(limit: {label}) after {retry_wait}s"
            )

        time.sleep(retry_wait)

def extract_output(response: dict[str, Any]) -> str:
    choices = response.get("choices") or []
    if not choices:
        raise ValueError(f"API response contains no choices: {response}")
    message = choices[0].get("message") or {}
    content = message.get("content")
    if isinstance(content, str) and content.strip():
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
        f"- Max tokens: {result['metadata']['max_tokens']}",
        f"- Thinking enabled: {result['metadata']['enable_thinking']}",
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
            run = item["conditions"].get(condition)
            if not run:
                continue
            lines += [
                f"### {condition}",
                "",
                run["output"],
                "",
            ]

    path.write_text("\n".join(lines), encoding="utf-8")


def new_result(
    *,
    model: str,
    base_url: str,
    temperature: float,
    max_tokens: int,
    inputs: list[dict[str, Any]],
) -> dict[str, Any]:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return {
        "metadata": {
            "experiment": "qwen_domain_ablation_pilot",
            "timestamp_utc": timestamp,
            "model": model,
            "base_url": base_url,
            "domain_dataset": str(DOMAIN_PATH.relative_to(ROOT)),
            "input_dataset": str(INPUTS_PATH.relative_to(ROOT)),
            "input_count": len(inputs),
            "conditions": CONDITIONS,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "enable_thinking": ENABLE_THINKING,
            "base_instruction": BASE_INSTRUCTION,
            "notes": [
                "Pilot only; not the final Gold evaluation.",
                "Same model, inputs and generation settings across D0-D4.",
                "Only injected domain context changes between conditions.",
                "No terminology retrieval is injected in this experiment.",
                "Checkpoint is saved after every successful condition.",
                "Default runner uses no client-side timeout and retries transient failures indefinitely.",
                "Generation is capped at 256 output tokens by default, and per-request latency is recorded.",
                "Thinking mode is disabled so the saved output is the final rewritten text rather than internal reasoning.",
                "Checkpoint is automatically committed and pushed to GitHub every five successful conditions by default.",
            ],
        },
        "items": [
            {
                "id": item["id"],
                "input": item["text"],
                "conditions": {},
            }
            for item in inputs
        ],
    }


def compatible_checkpoint(
    checkpoint: dict[str, Any],
    *,
    model: str,
    base_url: str,
    temperature: float,
    max_tokens: int,
    inputs: list[dict[str, Any]],
) -> bool:
    md = checkpoint.get("metadata", {})
    expected_ids = [item["id"] for item in inputs]
    actual_ids = [item.get("id") for item in checkpoint.get("items", [])]
    return (
        md.get("model") == model
        and md.get("base_url") == base_url
        and md.get("temperature") == temperature
        and md.get("max_tokens") == max_tokens
        and md.get("enable_thinking") == ENABLE_THINKING
        and md.get("conditions") == CONDITIONS
        and expected_ids == actual_ids
    )



def push_checkpoint(done: int, total: int) -> None:
    """Commit and push only the experiment checkpoint. Failure does not stop the run."""
    rel = CHECKPOINT_PATH.relative_to(ROOT)
    try:
        subprocess.run(
            ["git", "add", str(rel)],
            cwd=ROOT,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        diff = subprocess.run(
            ["git", "diff", "--cached", "--quiet"],
            cwd=ROOT,
        )
        if diff.returncode == 0:
            return
        subprocess.run(
            ["git", "commit", "-m", f"Checkpoint Qwen domain ablation {done}/{total}"],
            cwd=ROOT,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        subprocess.run(
            ["git", "push", "origin", "main"],
            cwd=ROOT,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        print(f"  pushed checkpoint to GitHub ({done}/{total})")
    except Exception as exc:
        print(f"  WARNING: checkpoint saved locally but GitHub push failed: {exc}")



def push_final_results(json_path: Path, md_path: Path) -> None:
    """Commit final result files and remove the tracked in-progress checkpoint."""
    try:
        subprocess.run(
            ["git", "add", "-A", str(RESULTS_DIR.relative_to(ROOT))],
            cwd=ROOT,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        diff = subprocess.run(
            ["git", "diff", "--cached", "--quiet"],
            cwd=ROOT,
        )
        if diff.returncode == 0:
            return
        subprocess.run(
            ["git", "commit", "-m", "Add completed Qwen domain ablation results"],
            cwd=ROOT,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        subprocess.run(
            ["git", "push", "origin", "main"],
            cwd=ROOT,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        print("  pushed final Qwen domain ablation results to GitHub")
    except Exception as exc:
        print(f"  WARNING: final results saved locally but GitHub push failed: {exc}")
        print(f"  Final files remain at: {json_path} and {md_path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--max-tokens", type=int, default=256)
    parser.add_argument("--timeout", type=int, default=0, help="0 = no client-side timeout")
    parser.add_argument("--retries", type=int, default=-1, help="-1 = retry forever on transient errors")
    parser.add_argument("--retry-wait", type=int, default=20)
    parser.add_argument("--sleep", type=float, default=2.0)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--push-every", type=int, default=5, help="Push checkpoint every N successful conditions; 0 disables.")
    parser.add_argument(
        "--restart",
        action="store_true",
        help="Ignore and overwrite any existing in-progress checkpoint.",
    )
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

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    if CHECKPOINT_PATH.exists() and not args.restart:
        checkpoint = load_json(CHECKPOINT_PATH)
        if compatible_checkpoint(
            checkpoint,
            model=model,
            base_url=base_url,
            temperature=args.temperature,
            max_tokens=args.max_tokens,
            inputs=inputs,
        ):
            result = checkpoint
            print(f"Resuming checkpoint: {CHECKPOINT_PATH}")
        else:
            raise SystemExit(
                "An incompatible checkpoint exists. "
                "Use --restart to begin a fresh run."
            )
    else:
        result = new_result(
            model=model,
            base_url=base_url,
            temperature=args.temperature,
            max_tokens=args.max_tokens,
            inputs=inputs,
        )
        save_json(result, CHECKPOINT_PATH)

    item_rows = {item["id"]: item for item in result["items"]}
    total = len(inputs) * len(CONDITIONS)
    done = sum(
        1
        for row in result["items"]
        for condition in CONDITIONS
        if condition in row.get("conditions", {})
    )

    for item in inputs:
        row = item_rows[item["id"]]

        for condition in CONDITIONS:
            if condition in row["conditions"]:
                continue

            context = build_context(domain, condition)
            messages = make_messages(item["text"], context)

            print(f"[{done + 1}/{total}] {item['id']} {condition}")

            if args.dry_run:
                output = "[DRY RUN]"
                raw = None
            else:
                started_at = time.perf_counter()
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
                elapsed_seconds = round(time.perf_counter() - started_at, 3)
                output = extract_output(response)
                finish_reason = (response.get("choices") or [{}])[0].get("finish_reason")
                if finish_reason == "length":
                    raise RuntimeError(
                        "Generation hit max_tokens before completing. "
                        "Result was not saved; increase --max-tokens only before restarting the full experiment."
                    )
                normalized_output = output.lstrip().lower()
                if normalized_output.startswith("thinking process:") or "<think>" in normalized_output:
                    raise RuntimeError(
                        "Thinking content leaked into the response. Result was not saved. "
                        "Verify the server honors chat_template_kwargs.enable_thinking=false."
                    )
                raw = {
                    "id": response.get("id"),
                    "usage": response.get("usage"),
                    "finish_reason": finish_reason,
                    "elapsed_seconds": elapsed_seconds,
                    "max_tokens": args.max_tokens,
                }
                print(f"  API completed in {elapsed_seconds:.3f}s")

            row["conditions"][condition] = {
                "context": context,
                "output": output,
                "api_metadata": raw,
            }
            done += 1

            # Save immediately so a later failure never loses completed work.
            save_json(result, CHECKPOINT_PATH)
            print(f"  saved checkpoint ({done}/{total})")

            if args.push_every > 0 and (done % args.push_every == 0 or done == total):
                push_checkpoint(done, total)

            if args.sleep:
                time.sleep(args.sleep)

    timestamp = result["metadata"]["timestamp_utc"]
    json_path = RESULTS_DIR / f"qwen_domain_ablation_{timestamp}.json"
    md_path = RESULTS_DIR / f"qwen_domain_ablation_{timestamp}.md"

    save_json(result, json_path)
    write_markdown(result, md_path)

    if CHECKPOINT_PATH.exists():
        CHECKPOINT_PATH.unlink()

    push_final_results(json_path, md_path)

    print(f"\nCompleted all {total} runs.")
    print(f"Saved:\n- {json_path}\n- {md_path}")


if __name__ == "__main__":
    main()
