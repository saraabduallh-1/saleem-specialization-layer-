#!/usr/bin/env python3
"""Guarded manual Qwen rewrite tester. It does not change frozen E8-E10 evaluations.

Enter multiple lines and finish with ':end' on a separate line.
--required-term must be verified against Siwar by the caller beforehand.
"""
from __future__ import annotations
import argparse
import os
import sys
from output_guards import check_rewrite
from run_qwen_domain_ablation import (
    DEFAULT_BASE_URL, DEFAULT_MODEL, DOMAIN_PATH, ROOT, load_dotenv,
    load_json, call_with_retry, extract_output, make_messages, build_context,
)

STYLE_RULES = {
    "saudi_colloquial": "حافظ على اللهجة السعودية الأصلية. لا تستخدم لهجة مصرية، ولا تحول النص إلى الفصحى إلا إذا طلب المستخدم ذلك.",
    "formal": "حافظ على الأسلوب العربي الفصيح الرسمي دون تغيير معنى النص أو درجة اليقين فيه.",
}

def read_multiline() -> str:
    print("أدخل النص، ثم اكتب :end في سطر منفصل. يمكن إدخال أسطر فارغة:")
    lines = []
    while True:
        try:
            line = input()
        except EOFError:
            break
        if line == ":end":
            break
        lines.append(line)
    return "\n".join(lines).strip()

def guarded_messages(text: str, domain: dict, style: str | None, terms: list[str]):
    msgs = make_messages(text, build_context(domain, "D3_domain_guidance"))
    extra = [STYLE_RULES[style]] if style else []
    if terms:
        extra.append("مصطلحات معتمدة بعد التحقق الخارجي من معجم سوار: " + "، ".join(terms))
        extra.append("استخدم المصطلحات المعتمدة دون تغييرها إذا كانت دقيقة للسياق؛ لا تخترع بدائل.")
    extra.append("حافظ على ترتيب الفقرات والأسطر، وعلى المعنى ودرجة اليقين، ولا تضف تشخيصات أو معلومات جديدة.")
    msgs[0] = dict(msgs[0], content=msgs[0]["content"] + "\n" + "\n".join(extra))
    return msgs

def main():
    p = argparse.ArgumentParser(description="Manual safeguarded rewrite, NOT held-out evaluation")
    p.add_argument("--text", help="Text; if omitted, interactive multiline input ends at :end")
    p.add_argument("--style", choices=sorted(STYLE_RULES))
    p.add_argument("--required-term", action="append", default=[], help="Only already-approved Siwar term; repeatable")
    p.add_argument("--retry-on-guard", action="store_true", help="One extra model call if a guard fails")
    p.add_argument("--timeout", type=int, default=180)
    args = p.parse_args()
    text = args.text if args.text is not None else read_multiline()
    if not text.strip():
        p.error("empty text")
    load_dotenv(ROOT / ".env")
    key = os.getenv("SALEEM_API_KEY", "").strip()
    if not key:
        p.error("SALEEM_API_KEY missing from local .env")
    base = os.getenv("SALEEM_BASE_URL", DEFAULT_BASE_URL).strip()
    model = os.getenv("SALEEM_MODEL", DEFAULT_MODEL).strip()
    domain = next(d for d in load_json(DOMAIN_PATH)["domains"] if d["domain_id"] == "artificial_intelligence")
    msgs = guarded_messages(text, domain, args.style, args.required_term)
    for attempt in range(2 if args.retry_on_guard else 1):
        resp = call_with_retry(base_url=base, api_key=key, model=model,
            messages=msgs, temperature=0.0, max_tokens=512, timeout=args.timeout,
            retries=1, retry_wait=5)
        if (resp.get("choices") or [{}])[0].get("finish_reason") == "length":
            print("REJECTED: truncated model output", file=sys.stderr)
            return 2
        output = extract_output(resp).strip()
        check = check_rewrite(text, output, style=args.style,
            terms=args.required_term, preserve_newlines=True)
        if check.passed:
            print(output)
            print("GUARDS PASS (semantic correctness not established)", file=sys.stderr)
            return 0
        print("GUARDS FAILED: " + "; ".join(check.warnings), file=sys.stderr)
        if attempt == 0 and args.retry_on_guard:
            msgs += [{"role": "assistant", "content": output},
                {"role": "user", "content": "صحح هذه المخالفات فقط: " + "; ".join(check.warnings) +
                 ". حافظ على المعنى الأصلي ولا تضف معلومات. أعد النص وحده."}]
        else:
            print("REJECTED OUTPUT, FOR INSPECTION ONLY:\n" + output, file=sys.stderr)
            return 2
    return 2

if __name__ == "__main__":
    raise SystemExit(main())
