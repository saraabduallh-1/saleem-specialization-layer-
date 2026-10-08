#!/usr/bin/env python3
"""Interactively try Saleem/Qwen domain-context variants on any Arabic text.

This is a manual exploration utility, not part of the controlled pilot.
It sends one user-provided text through D0-D4 using the same model,
generation settings, domain data, and non-thinking mode as the ablation runner.

The real API key is read only from the local .env file:
    SALEEM_API_KEY
"""

from __future__ import annotations

import argparse
import os
import time

from run_qwen_domain_ablation import (
    CONDITIONS,
    DEFAULT_BASE_URL,
    DEFAULT_MODEL,
    DOMAIN_PATH,
    ROOT,
    build_context,
    call_with_retry,
    extract_output,
    load_dotenv,
    load_json,
    make_messages,
)

LABELS = {
    "D0_saleem_only": "D0 - Qwen فقط",
    "D1_domain_name": "D1 - + اسم المجال",
    "D2_domain_name_definition": "D2 - + تعريف المجال",
    "D3_domain_guidance": "D3 - + إرشادات المجال",
    "D4_domain_guidance_examples": "D4 - + أمثلة المجال",
}


def get_text(cli_text: str | None) -> str:
    if cli_text and cli_text.strip():
        return cli_text.strip()

    print("اكتب النص العربي الذي تريد تجربته، ثم اضغط Enter:")
    text = input("> ").strip()
    if not text:
        raise SystemExit("لم يتم إدخال نص.")
    return text


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Try one Arabic text through Qwen D0-D4 domain conditions."
    )
    parser.add_argument(
        "--text",
        default=None,
        help="Optional text. If omitted, the script asks interactively.",
    )
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--max-tokens", type=int, default=256)
    parser.add_argument("--timeout", type=int, default=1800)
    parser.add_argument("--retries", type=int, default=-1)
    parser.add_argument("--retry-wait", type=int, default=20)
    parser.add_argument("--sleep", type=float, default=0.5)
    args = parser.parse_args()

    load_dotenv(ROOT / ".env")

    api_key = os.getenv("SALEEM_API_KEY", "").strip()
    base_url = os.getenv("SALEEM_BASE_URL", DEFAULT_BASE_URL).strip()
    model = os.getenv("SALEEM_MODEL", DEFAULT_MODEL).strip()

    if not api_key:
        raise SystemExit(
            "Missing SALEEM_API_KEY. Put the real key only in your local .env file."
        )

    text = get_text(args.text)

    domain_store = load_json(DOMAIN_PATH)
    domain = next(
        d for d in domain_store["domains"]
        if d["domain_id"] == "artificial_intelligence"
    )

    print("\n" + "=" * 72)
    print("النص الأصلي:")
    print(text)
    print("=" * 72)

    for condition in CONDITIONS:
        context = build_context(domain, condition)
        messages = make_messages(text, context)

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
        elapsed = time.perf_counter() - started_at

        output = extract_output(response)
        finish_reason = (response.get("choices") or [{}])[0].get("finish_reason")

        if finish_reason == "length":
            raise RuntimeError(
                f"{condition} hit max_tokens before completing. "
                "No partial output is accepted."
            )

        normalized = output.lstrip().lower()
        if normalized.startswith("thinking process:") or "<think>" in normalized:
            raise RuntimeError(
                f"{condition} returned thinking content instead of the final rewrite."
            )

        print(f"\n{LABELS[condition]}")
        print("-" * 72)
        print(output)
        print(f"\nالزمن: {elapsed:.2f} ثانية")

        if args.sleep:
            time.sleep(args.sleep)

    print("\n" + "=" * 72)
    print("انتهت التجربة اليدوية. هذه النتائج للاستكشاف وليست جزءًا من Gold Test.")
    print("=" * 72)


if __name__ == "__main__":
    main()
