"""Find candidate example sentences for a term in ASJP Arabic abstracts (selection aid).

Searches ASJP, fetches the top article pages, and prints abstract sentences matching
any of the given term forms. Output is for human review only; chosen sentences are
then recorded as spans in pilot_curation.py.

usage:
  python scripts/pilot_harvest_candidates.py "الشبكات العصبية الاصطناعية"
  python scripts/pilot_harvest_candidates.py "آلة المتجهات الداعمة||SVM" --query SVM --raw --max 30
"""
import argparse
import re

from pilot_sources import asjp_abstract, asjp_article_url, asjp_search, get, norm, term_regex


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("forms", help="term forms to match, separated by ||")
    ap.add_argument("--query", help="search query (default: first form)")
    ap.add_argument("--raw", action="store_true", help="do not wrap the query in quotes (OR search)")
    ap.add_argument("--max", type=int, default=12, help="max articles to inspect")
    a = ap.parse_args()

    forms = a.forms.split("||")
    q = a.query or forms[0]
    if not a.raw:
        q = f'"{q}"'
    rxs = [term_regex(f) for f in forms]

    for aid, title in asjp_search(q)[:a.max]:
        page = get(asjp_article_url(aid))
        ab = asjp_abstract(page)
        if not ab:
            continue
        hits = [s for s in re.split(r"(?<=[.؟!؛])\s+", ab) if any(r.search(norm(s)) for r in rxs)]
        if hits:
            print(f"\n== {aid} | {title[:140]}")
            for s in hits[:3]:
                print("   >>", s[:400])


if __name__ == "__main__":
    main()
