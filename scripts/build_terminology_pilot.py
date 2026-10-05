"""Build data/processed/data_ai/terminology_pilot_50.json.

Inputs : terminology_base.json (official Siwar fields, copied unchanged),
         the raw Siwar file (consistency check), scripts/pilot_curation.py (selection + evidence).
Process: every source-derived example is cut out of the fetched source by its start/end
         snippets (never retyped); PDF quotes transcribed from page images are fuzzily
         matched against the PDF text layer. Synthetic examples go ONLY to
         `generated_examples`.
Run    : python scripts/build_terminology_pilot.py && python scripts/validate_terminology_pilot.py
"""
import copy
import json
import re

from pilot_curation import CURATION, EGYPT, EXTRA_VARIANTS, LAW
from pilot_sources import (PROJECT_ROOT, asjp_abstract, asjp_article_url, asjp_bibtex, fuzzy, get, norm,
                           pdf_page_text, snippet_regex)

BASE = PROJECT_ROOT / "data/processed/data_ai/terminology_base.json"
RAW = PROJECT_ROOT / "data/raw/data_ai/siwar_data_ai_dictionary.json"
OUT = PROJECT_ROOT / "data/processed/data_ai/terminology_pilot_50.json"
RETRIEVED = "2026-10-04"  # date the cited sources were retrieved and checked
# Verification mode for quotes whose PDF text layer is too corrupted to match in full (kept separate from
# exact_substring_of_source and from the fuzzy text-layer match).
IMAGE_TRANSCRIBED = "image_transcribed_manual_visual_verification"

problems = []


def span(text, start, end):
    """Exact source substring from `start` snippet to `end` snippet (or to the sentence end)."""
    m = snippet_regex(start).search(text)
    if not m:
        return None
    if end:
        e = snippet_regex(end).search(text, m.end() - 1)
        return text[m.start():e.end()].strip() if e else None
    m2 = re.search(r"[.؟!](?=\s|$)", text[m.end():])
    return text[m.start():m.end() + (m2.end() if m2 else len(text) - m.end())].strip()


_bib = {}


def asjp_meta(aid):
    if aid not in _bib:
        f = asjp_bibtex(aid)
        if f.get("url") != asjp_article_url(aid):
            problems.append(f"bibtex url mismatch for {aid}: {f.get('url')}")
        _bib[aid] = {
            "source_title": re.sub(r"\s+", " ", f.get("title", "")).strip(),
            "source_type": "peer_reviewed_journal_article",
            "authors_or_org": [a.strip() for a in f.get("author", "").split(" and ") if a.strip()],
            "year": int(f["year"]) if f.get("year", "").isdigit() else None,
            "venue": {"journal": f.get("journal"), "volume": f.get("volume"), "issue": f.get("number"),
                      "article_pages": f.get("pages"), "platform": "ASJP — Algerian Scientific Journal Platform (CERIST)"},
            "url_or_doi": asjp_article_url(aid),
        }
    return copy.deepcopy(_bib[aid])


def law_meta(key, flat):
    name, hijri, greg = re.search(r"الاسم (.{3,60}?) تاريخ الإصدار (\S+) هـ الموافق ?: ?(\S+)", flat).groups()
    return {
        "source_title": name,
        "source_type": "official_legislation",
        "authors_or_org": ["المملكة العربية السعودية — هيئة الخبراء بمجلس الوزراء (منصة الأنظمة السعودية)"],
        "year": int(greg.split("/")[-1]),
        "issue_date": {"hijri": hijri, "gregorian": greg},
        "url_or_doi": LAW[key],
        "text_version_note": "نص النظام كما يظهر في منصة الأنظمة السعودية بتاريخ الاسترجاع (قد يتضمن تعديلات لاحقة على تاريخ الإصدار).",
    }


def resolve(ex, term):
    src, out = ex["src"], {}
    if src == "asjp":
        ab = asjp_abstract(get(asjp_article_url(ex["id"]))) or ""
        text = span(ab, ex["start"], ex.get("end"))
        if text:
            out.update(asjp_meta(ex["id"]))
            out["page_or_section"] = "الملخص العربي (Abstract) في صفحة المقال"
        verification = "exact_substring_of_source"
    elif src == "boe":
        flat = re.sub(r"\s+", " ", get(LAW[ex["law"]]))
        text = span(flat, ex["start"], ex.get("end"))
        if text:
            out.update(law_meta(ex["law"], flat))
            out["page_or_section"] = ex["section"]
        verification = "exact_substring_of_source"
    elif src == "egypt":
        text = ex["manual_text"] if fuzzy(ex["manual_text"]) in fuzzy(pdf_page_text(EGYPT, ex["pdf_page"])) else None
        out.update({
            "source_title": "المبادئ التوجيهية الوطنية للذكاء الاصطناعي التوليدي (الإصدار 1.0)",
            "source_type": "official_government_guideline",
            "authors_or_org": ["جمهورية مصر العربية — المجلس الوطني للذكاء الاصطناعي والحوسبة الكمية والتكنولوجيات البازغة",
                               "المركز المصري للذكاء الاصطناعي المسؤول"],
            "year": 2026,
            "page_or_section": f"ص {ex['printed_page']} (صفحة PDF رقم {ex['pdf_page']}) — {ex['section']}",
            "url_or_doi": EGYPT,
            "transcription_note": "طبقة النص في ملف PDF تُفسد ترميز (لا) في وسط الكلمات؛ نُقل النص من صورة الصفحة المعروضة وطوبق آليًا مع طبقة النص بعد تطبيع الألف واللام.",
        })
        verification = "page_image_transcription+fuzzy_text_layer_match"
    elif src == "asjp_pdf":
        text = ex["manual_text"] if fuzzy(ex["manual_text"]) in fuzzy(pdf_page_text(ex["pdf_url"], ex["pdf_page"])) else None
        if text:
            out.update(asjp_meta(ex["id"]))
            out["page_or_section"] = f"ص {ex['printed_page']} من النص الكامل (PDF)"
            out["full_text_url"] = ex["pdf_url"]
            out["transcription_note"] = "طبقة النص في ملف PDF تُفسد ترميز (لا)؛ نُقل النص من صورة الصفحة المعروضة وطوبق آليًا مع طبقة النص بعد تطبيع الألف واللام. الإملاء كما في الأصل."
        verification = "page_image_transcription+fuzzy_text_layer_match"
    elif src == "web":
        flat = re.sub(r"\s+", " ", get(ex["url"]))
        text = span(flat, ex["start"], ex.get("end"))
        if text:
            out.update(copy.deepcopy(ex["meta"]))
            out["page_or_section"] = ex["section"]
            out["url_or_doi"] = ex["url"]
        verification = "exact_substring_of_source"
    elif src in ("pdf", "image"):
        layer = fuzzy(pdf_page_text(ex["url"], ex["pdf_page"]))
        if src == "pdf":
            ok = fuzzy(ex["manual_text"]) in layer
            verification = "page_image_transcription+fuzzy_text_layer_match"
        else:
            # corrupted text layer: only the recorded anchor (also part of the quote) is machine-checked
            ok = fuzzy(ex["anchor"]) in layer and fuzzy(ex["anchor"]) in fuzzy(ex["manual_text"])
            verification = IMAGE_TRANSCRIBED
        text = ex["manual_text"] if ok else None
        if text:
            out.update(copy.deepcopy(ex["meta"]))
            out["page_or_section"] = f"ص {ex['printed_page']} (صفحة PDF رقم {ex['pdf_page']}) — {ex['section']}"
            out["url_or_doi"] = ex["url"]
            out["pdf_page"] = ex["pdf_page"]
            if src == "image":
                out["text_layer_anchor"] = ex["anchor"]
                out["manual_verification"] = ex["manual_verification"]
    else:
        raise ValueError(src)
    if not text:
        problems.append(f"[{term}] quote not found/verified in {src}: {(ex.get('start') or ex.get('manual_text'))[:50]}")
        return None
    out.update({"text": text, "data_origin": "source_derived", "retrieved_at": ex.get("retrieved", RETRIEVED),
                "verification": verification})
    for k in ("intended_sense", "why_not_this_term", "contrast_type", "terminology_note", "audit"):
        if k in ex:
            out[k] = ex[k]
    order = ["text", "contrast_type", "intended_sense", "why_not_this_term", "source_title", "source_type",
             "authors_or_org", "year", "page_or_section", "url_or_doi"]
    return {**{k: out[k] for k in order if k in out}, **{k: v for k, v in out.items() if k not in order}}


def main():
    base = json.load(open(BASE, encoding="utf-8"))
    raw = {e["id"]: e for e in json.load(open(RAW, encoding="utf-8"))["entries"]}
    by_norm = {}
    for x in base:
        by_norm.setdefault(norm(x["term"]), []).append(x)

    out = []
    for key, cur in CURATION.items():
        cands = by_norm.get(key, [])
        assert len(cands) == 1, (key, len(cands))
        rec = copy.deepcopy(cands[0])
        r = raw[rec["id"]]
        if r["lemma"].strip() != rec["term"] or r.get("definition", "").strip() != rec["definition"]:
            problems.append(f"[{key}] term/definition differs from raw Siwar")

        official = {norm(a) for a in rec["abbreviations"] + rec["aliases"]}
        variants = list(rec["variants"])
        for v in cur.get("variants", []) + EXTRA_VARIANTS.get(key, []):
            if norm(v["value"]) in official:
                problems.append(f"[{key}] variant duplicates an official abbreviation/alias: {v['value']}")
                continue
            variants.append({**v, "data_origin": "source_derived"})

        rec["variants"] = variants
        rec["positive_examples"] = [e for e in (resolve(x, key) for x in cur.get("pos", [])) if e]
        rec["negative_examples"] = [e for e in (resolve(x, key) for x in cur.get("neg", [])) if e]
        rec["generated_examples"] = [{
            "text": t, "example_type": "positive", "source_type": "synthetic", "data_origin": "generated",
            "generated_by": "Claude (claude-opus-5-5)", "generated_at": RETRIEVED,
            "reason": "لم يُعثر على مثال عربي حقيقي موثّق وقابل للتحقق لهذا المعنى ضمن المصادر المتاحة في هذه الجولة.",
            "do_not_use_as": ["gold_test_query", "source_derived_evidence", "main_retrieval_experiment"],
        } for t in cur.get("synthetic", [])]
        rec["pilot"] = {
            "selection_category": cur["category"],
            "has_documented_competing_sense": bool(rec["negative_examples"]),
            "has_abbreviation_or_alias": bool(rec["abbreviations"] or rec["aliases"] or
                                              any(v["type"] in ("abbreviation", "explicit_alias") for v in variants)),
            "n_real_positive": len(rec["positive_examples"]),
            "n_real_negative": len(rec["negative_examples"]),
            "n_synthetic": len(rec["generated_examples"]),
            "usage_restriction": "Pilot enrichment data only — must not be reused as Gold Test queries. "
                                 "generated_examples are synthetic and must be excluded from the main retrieval experiment.",
        }
        if "unresolved" in cur:
            if rec["positive_examples"]:
                problems.append(f"[{key}] marked unresolved but has positive examples")
            rec["pilot"]["positive_example_unresolved"] = copy.deepcopy(cur["unresolved"])
        out.append(rec)

    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(out)} entries -> {OUT}")
    if problems:
        print("PROBLEMS:", *problems, sep="\n  ")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
