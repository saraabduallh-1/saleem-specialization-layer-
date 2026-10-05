"""Validate data/processed/data_ai/terminology_pilot_50.json.

Checks:
  1. 50 unique entries; every official Siwar field equals terminology_base.json, and term/definition
     equal the raw Siwar file.
  2. Real vs synthetic separation: positive/negative examples are all source_derived; synthetic text
     appears only in generated_examples and never duplicates a real example.
  3. Every negative example has a valid contrast_type, intended_sense and why_not_this_term.
  4. Every source-derived quote is re-found in its (cached) source. Quotes marked
     image_transcribed_manual_visual_verification (corrupted PDF text layer) are a separate mode: only their
     recorded anchor is machine-checked; the full text was compared by eye with the rendered page.
  5. With --check-urls: every cited URL answers HTTP 200.

usage: python scripts/validate_terminology_pilot.py [--check-urls]
"""
import json
import re
import sys

from build_terminology_pilot import IMAGE_TRANSCRIBED
from pilot_curation import EGYPT
from pilot_sources import (PROJECT_ROOT, asjp_abstract, asjp_article_url, fuzzy, get, pdf_page_text,
                           url_status)

PILOT = PROJECT_ROOT / "data/processed/data_ai/terminology_pilot_50.json"
BASE = PROJECT_ROOT / "data/processed/data_ai/terminology_base.json"
RAW = PROJECT_ROOT / "data/raw/data_ai/siwar_data_ai_dictionary.json"

OFFICIAL = ["id", "source", "source_dictionary", "domain", "term", "lemma_type", "pos", "definition",
            "english_term", "abbreviations", "aliases", "canonical_term", "canonical_term_id"]
CONTRAST_TYPES = {"different_sense", "different_domain", "abbreviation_collision"}
REQUIRED = ["text", "source_title", "source_type", "authors_or_org", "year", "page_or_section", "url_or_doi"]


def quote_found(e):
    url = e["url_or_doi"]
    if e["verification"] == "exact_substring_of_source":
        if url.startswith("https://asjp.cerist.dz/en/article/"):
            return e["text"] in (asjp_abstract(get(url)) or "")
        # Saudi laws and other web pages (e.g. Hindawi books, journal pages): whitespace-collapsed page text
        return e["text"] in re.sub(r"\s+", " ", get(url))
    if e["verification"] == IMAGE_TRANSCRIBED:
        # Separate mode (text layer too corrupted for a full match): the quote was checked by eye against the
        # rendered page; here only the recorded anchor is checked against the text layer and the quote.
        anchor = e.get("text_layer_anchor") or ""
        return bool(anchor and e.get("manual_verification") and e.get("pdf_page")) \
            and fuzzy(anchor) in fuzzy(e["text"]) and fuzzy(anchor) in fuzzy(pdf_page_text(url, e["pdf_page"]))
    if e.get("pdf_page"):  # PDF quote whose record stores its PDF page (e.g. HIAST theses)
        return fuzzy(e["text"]) in fuzzy(pdf_page_text(url, e["pdf_page"]))
    pdf_url = e.get("full_text_url") or EGYPT
    page = int(re.search(r"PDF رقم (\d+)", e["page_or_section"]).group(1)) if url == EGYPT \
        else _asjp_pdf_page(e)
    return fuzzy(e["text"]) in fuzzy(pdf_page_text(pdf_url, page))


def _asjp_pdf_page(e):
    # the record stores the printed page only; locate the PDF page holding the quote
    pages = re.split(r"\[\[PAGE (\d+)\]\]", get(e["full_text_url"]))
    for n, body in zip(pages[1::2], pages[2::2]):
        if fuzzy(e["text"]) in fuzzy(body):
            return int(n)
    return 1


def main():
    errors = []
    pilot = json.load(open(PILOT, encoding="utf-8"))
    base = {x["id"]: x for x in json.load(open(BASE, encoding="utf-8"))}
    raw = {e["id"]: e for e in json.load(open(RAW, encoding="utf-8"))["entries"]}

    if len(pilot) != 50 or len({x["id"] for x in pilot}) != 50:
        errors.append(f"expected 50 unique entries, got {len(pilot)}")

    urls = set()
    for x in pilot:
        t = x["term"]
        b = base.get(x["id"])
        if not b:
            errors.append(f"[{t}] id not in terminology_base.json")
            continue
        for k in OFFICIAL:
            if x[k] != b[k]:
                errors.append(f"[{t}] official field '{k}' differs from terminology_base.json")
        if x["term"] != raw[x["id"]]["lemma"].strip() or x["definition"] != raw[x["id"]].get("definition", "").strip():
            errors.append(f"[{t}] term/definition differs from raw Siwar")

        real = x["positive_examples"] + x["negative_examples"]
        for e in real:
            if e.get("data_origin") != "source_derived" or e.get("source_type") == "synthetic":
                errors.append(f"[{t}] non-source-derived example inside positive/negative_examples")
            missing = [k for k in REQUIRED if e.get(k) in (None, "", [])]
            if missing:
                errors.append(f"[{t}] example missing {missing}")
            if not quote_found(e):
                errors.append(f"[{t}] quote not re-found in source: {e['text'][:50]}")
            urls.add(e["url_or_doi"])
            if e.get("full_text_url"):
                urls.add(e["full_text_url"])
        for e in x["negative_examples"]:
            if e.get("contrast_type") not in CONTRAST_TYPES:
                errors.append(f"[{t}] invalid contrast_type: {e.get('contrast_type')}")
            if not e.get("intended_sense") or not e.get("why_not_this_term"):
                errors.append(f"[{t}] negative example missing intended_sense/why_not_this_term")
        real_texts = {e["text"] for e in real}
        for g in x["generated_examples"]:
            if g.get("source_type") != "synthetic" or g.get("data_origin") != "generated":
                errors.append(f"[{t}] generated example not marked synthetic/generated")
            if g["text"] in real_texts:
                errors.append(f"[{t}] synthetic text duplicates a real example")
        official = {a for a in x["abbreviations"] + x["aliases"]}
        for v in x["variants"]:
            if v["value"] in official:
                errors.append(f"[{t}] variant duplicates official abbreviation/alias: {v['value']}")
            urls.update(v.get("evidence", []))

    if "--check-urls" in sys.argv:
        for u in sorted(urls):
            if url_status(u) != "200":
                errors.append(f"URL not 200: {u}")

    n_pos = sum(len(x["positive_examples"]) for x in pilot)
    n_neg = sum(len(x["negative_examples"]) for x in pilot)
    n_syn = sum(len(x["generated_examples"]) for x in pilot)
    print(f"entries={len(pilot)} real_positive={n_pos} real_negative={n_neg} synthetic={n_syn} cited_urls={len(urls)}")
    if errors:
        print("FAILED:", *errors, sep="\n  ")
        raise SystemExit(1)
    print("OK")


if __name__ == "__main__":
    main()
