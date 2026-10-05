"""Formal error analysis of the 48-term E5 ablation (results/retrieval_e5_48_ablation.json).

Descriptive only: reads the stored per-query results and the terminology pilot, runs no retrieval model
and computes no embeddings (the E5 tokenizer is used only to count example tokens). All metrics here are
derived from the stored ranks and are reconciled against the stored metrics before anything is written.

Manual, exploratory inputs are kept in clearly labelled dictionaries below (ERROR_CATEGORIES,
SPECIFICITY, ATTRACTOR_NOTES); they annotate the data and never change it.

Writes results/error_analysis_e5_48.json and results/error_analysis_e5_48.md.
"""
import json
import statistics
import sys
from collections import Counter
from pathlib import Path

from transformers import AutoTokenizer

from pilot_sources import norm, term_regex

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ABLATION = PROJECT_ROOT / "results/retrieval_e5_48_ablation.json"
PILOT = PROJECT_ROOT / "data/processed/data_ai/terminology_pilot_50.json"
OUT_JSON = PROJECT_ROOT / "results/error_analysis_e5_48.json"
OUT_MD = PROJECT_ROOT / "results/error_analysis_e5_48.md"

A, B, C = "A_term_only", "B_term_definition", "C_term_definition_example"
TOP_KS = (1, 3, 5)

CATEGORY_NAMES = {
    1: "general_example_language",
    2: "competing_terminology",
    3: "semantically_broad_target_term",
    4: "example_definition_mismatch",
    5: "lexical_mismatch_or_synonym",
    6: "query_ambiguity",
    7: "neighbor_attraction",
    8: "source_domain_style_effect",
    9: "no_clear_cause",
}

# Manual categorisation of the 13 queries whose rank worsened from B to C (inspection of query, definition,
# first example and the B/C top-5). Categories are evidence-based labels, not established causes.
ERROR_CATEGORIES = {
    "GOLD_022": ([2, 4, 8], "The example is mainly about deepfakes (another pilot term, تزييف عميق) and its social/media "
                            "spread; التعلم العميق is mentioned once as a contributing factor, not described."),
    "GOLD_024": ([6], "Query (finding patterns/groupings in unlabelled data) also fits تنقيب في البيانات; drop is 1->2 "
                      "with a small score margin (0.795 vs 0.791)."),
    "GOLD_025": ([5, 7], "The example uses the translator's term «فرط الاستعداد», not فرط التخصيص; مُولِّد (whose "
                         "example discusses training instability and output quality) moves to Top-1."),
    "GOLD_028": ([4, 8, 7], "The example discusses generative AI's implications for open science and plagiarism, not "
                            "content generation; اسم (example: «إنشاء ... نموذج») and مُولِّد rise above the target."),
    "GOLD_032": ([1], "Long example listing statistical and neural approaches and 'deep neural networks'; the broader "
                      "neighbour معالجة اللغات الطبيعية overtakes the target by a small margin."),
    "GOLD_033": ([2, 4, 8], "The example is a banking-sector finding that pairs decision trees with logistic regression; "
                            "it does not describe branching on features, which is what the query describes."),
    "GOLD_037": ([3, 4, 8], "Broad target term; the example is about machine learning in cybersecurity threat detection, "
                            "while the query describes generic learn-from-examples-then-predict."),
    "GOLD_040": ([3, 9], "Already a failure under B (rank 34) and C (35); a one-place change on a broad term is not "
                         "attributable to the example."),
    "GOLD_041": ([5], "The example uses «الشبكة العصبية الالتفافية» rather than the Siwar term «ترشيحية»; small change "
                      "(9->11) on an already-missed mixed-language query."),
    "GOLD_042": ([6, 7], "The query (sequential processing with a carried state) also fits مُحوِّل and LSTM; مُحوِّل, "
                         "whose example mentions «تسلسل محدد», moves to Top-1."),
    "GOLD_044": ([8], "Long example about forecasting gold prices with SVM model comparison; it does not mention "
                      "margins or support vectors' role, which the query describes."),
    "GOLD_049": ([1, 2, 4, 5], "Multi-topic example (sports media, big-data analysis, prediction systems) that mentions "
                               "«رؤية الحاسوب» only as one tool; it also names بيانات ضخمة (as «البيانات الكبيرة»)."),
    "GOLD_050": ([6], "The query (a number measuring distance from the correct value, used to adjust the model) also "
                      "fits متوسط الخطأ التربيعي, which rises to rank 2; مُولِّد is Top-1 under both B and C."),
}

# Manual specificity classification of the 48 target terms from their Siwar definitions (conceptual scope),
# made without reference to retrieval performance. Exploratory.
SPECIFICITY = {
    "broad": ["نموذج", "ذكاء اصطناعي", "تعلُّم الآلة", "تعلُّم عميق", "شبكة عصبية اصطناعية", "تدريب",
              "بيانات ضخمة", "معالجة اللغات الطبيعية", "ذكاء اصطناعي توليدي", "تنقيب في البيانات"],
    "moderately_general": ["وكيل", "هلوسة", "بيئة", "طبقة", "أمر", "تأسيس", "مواءمة", "تعلُّم موجَّه",
                           "تعلُّم غير موجَّه", "فرط التخصيص", "رؤية الحاسب", "تحليل المشاعر", "ترجمة الآلة",
                           "نموذج لغوي كبير", "شبكة عصبية ترشيحية", "شبكة عصبية تكرارية",
                           "توليد مُعَزَّز بالاسترجاع", "مكافأة", "سياسة", "دالة الخسارة", "تزييف عميق"],
    "specific": ["وزن", "تحيُّز", "دورة", "مُحوِّل", "مُولِّد", "عائد", "اسم", "تجذيع", "دالة تنشيط", "انتشار عكسي",
                 "تقسيم النصوص", "شجرة القرار", "ذاكرة قصيرة المدى مُطَوَّلة", "آلة المُتَّجهات الداعمة",
                 "تعرُّف على الكيانات المُسمّاة", "تحليل المُكوِّن الرئيس", "متوسط الخطأ التربيعي"],
}

# Manual inspection notes for the terms whose incorrect Top-1 count rises most from B to C.
ATTRACTOR_NOTES = {
    "اسم": "Example describes building a classification model from a labelled dataset with a machine-learning "
           "algorithm («مجموعة بيانات»، «نموذج التصنيف»، «خوارزمية تعلُّم آلة»، «إنشاء النموذج»): generic "
           "model-building vocabulary; it literally contains other pilot terms (نموذج، تعلُّم الآلة).",
    "مُولِّد": "Example describes GAN training difficulty («تدريب»، «التدريب»، «عدم الاستقرار»، «إنتاج صور ذات جودة "
              "منخفضة»): training and output-quality vocabulary shared with many queries; it contains the pilot "
              "term تدريب. مُولِّد was already an incorrect Top-1 once under B (GOLD_050).",
    "مُحوِّل": "Example (Egypt GenAI guidelines) mentions computer vision, generative modelling, diffusion models and "
              "«تسلسل محدد»: several concepts in one sentence, including sequence vocabulary relevant to RNN/LSTM "
              "queries.",
    "سياسة": "Example is a long technical Q-learning/MDP sentence (states, actions, Q-table, Bellman update); it "
             "attracts the other RL query (بيئة) and شبكة عصبية اصطناعية (already a deep failure).",
    "تعلُّم موجَّه": "Example describes a random-forest model presented as supervised machine learning in finance; it "
                    "contains broad terms (تعلم آلي، الذكاء الاصطناعي) and attracts the label (اسم) and machine "
                    "learning (تعلُّم الآلة) queries.",
}

GENERAL_ML_VOCAB = ["الذكاء الاصطناعي", "تعلم الآلة", "التعلم الآلي", "تعلم آلي", "خوارزمية", "خوارزميات", "نموذج",
                    "نماذج", "بيانات", "البيانات", "تدريب", "التدريب", "الشبكات العصبية", "الشبكة العصبية", "التنبؤ",
                    "تصنيف", "التصنيف"]


def fail(msg):
    print(f"FAIL: {msg}", file=sys.stderr)
    sys.exit(1)


def metrics_from_ranks(ranks):
    n = len(ranks)
    m = {f"top{k}_accuracy": sum(r <= k for r in ranks) / n for k in TOP_KS}
    m["mrr"] = sum(1 / r for r in ranks) / n
    return m


def group(values):
    values = list(values)
    return {"n": len(values), "mean": round(statistics.mean(values), 2) if values else None,
            "median": statistics.median(values) if values else None}


def main():
    abl = json.loads(ABLATION.read_text(encoding="utf-8"))
    pilot = {x["id"]: x for x in json.loads(PILOT.read_text(encoding="utf-8"))}
    conds = abl["conditions"]
    pq = {c: {p["query_id"]: p for p in conds[c]["per_query"]} for c in (A, B, C)}
    qids = [p["query_id"] for p in conds[A]["per_query"]]

    # ---- validation of inputs --------------------------------------------------------------------------
    if len(qids) != 48 or len(set(qids)) != 48:
        fail("Expected 48 unique queries.")
    for c in (A, B, C):
        if [p["query_id"] for p in conds[c]["per_query"]] != qids:
            fail(f"Query order/set differs in {c}.")
        recomputed = metrics_from_ranks([pq[c][q]["expected_rank"] for q in qids])
        for k, v in conds[c]["metrics"].items():
            if abs(recomputed[k] - v) > 1e-12:
                fail(f"Metric {k} of {c} does not reconcile with stored ranks.")
    if {pq[A][q]["expected_id"] for q in qids} & {e["id"] for e in abl["run"]["excluded_entries"]}:
        fail("An excluded entry appears among the evaluated queries.")

    tok = AutoTokenizer.from_pretrained(abl["run"]["model_name"])
    all_terms = list(pilot.values())
    term_rx = {t["term"]: term_regex(t["term"]) for t in all_terms}
    # manual dictionaries are matched on diacritic-stripped keys (typed and stored diacritics may differ in order)
    spec_norm = {norm(t): cls for cls, ts in SPECIFICITY.items() for t in ts}
    eval_terms = {pq[A][q]["expected_term"] for q in qids}
    spec_of = {t: spec_norm.get(norm(t)) for t in eval_terms}
    notes_norm = {norm(k): v for k, v in ATTRACTOR_NOTES.items()}
    if None in spec_of.values() or len(spec_norm) != 48 or sum(len(v) for v in SPECIFICITY.values()) != 48:
        fail("SPECIFICITY must classify exactly the 48 evaluated terms.")

    # ---- A. analysis dataset ------------------------------------------------------------------------------
    rows = []
    for q in qids:
        a, b, c = pq[A][q], pq[B][q], pq[C][q]
        t = pilot[a["expected_id"]]
        ex = t["positive_examples"][0]
        ex_norm = norm(ex["text"])
        others = sorted(n for n, rx in term_rx.items() if n != t["term"] and rx.search(ex_norm))
        exact = bool(term_rx[t["term"]].search(ex_norm))
        general = sorted({w for w in GENERAL_ML_VOCAB if norm(w) in ex_norm})
        d_ex = b["expected_rank"] - c["expected_rank"]
        rows.append({
            "query_id": q, "query": a["query"], "language_style": a["language_style"],
            "expected_term": a["expected_term"], "expected_id": a["expected_id"],
            "selection_category": t["pilot"]["selection_category"], "specificity": spec_of[a["expected_term"]],
            "rank_term_only": a["expected_rank"], "rank_definition": b["expected_rank"],
            "rank_example": c["expected_rank"],
            "rank_change_term_to_definition": a["expected_rank"] - b["expected_rank"],
            "rank_change_definition_to_example": d_ex,
            **{f"{lab}_hit@{k}": p[f"hit@{k}"] for lab, p in (("term_only", a), ("definition", b), ("example", c))
               for k in TOP_KS},
            "example_text": ex["text"], "example_source_title": ex["source_title"],
            "example_source_type": ex["source_type"], "example_url": ex["url_or_doi"],
            "example_verification": ex["verification"],
            "example_chars": len(ex["text"]), "example_tokens": len(tok(ex["text"])["input_ids"]),
            "example_exact_siwar_term": exact,
            "example_lexical_form_used": (ex.get("audit") or {}).get("lexical_form_used"),
            "example_other_pilot_terms": others,
            "example_multiple_technical_concepts": len(others) + int(exact) >= 2,
            "example_general_ml_vocabulary": general,
            "top1_definition": b["top5"][0]["term"], "top1_example": c["top5"][0]["term"],
            "top1_changed_with_example": b["top5"][0]["id"] != c["top5"][0]["id"],
            "outcome_definition_to_example": ("improved_with_example" if d_ex > 0 else
                                              "worsened_with_example" if d_ex < 0 else "unchanged_with_example"),
            "top1_status": ("newly_reached_top1" if b["expected_rank"] > 1 and c["expected_rank"] == 1 else
                            "dropped_from_top1" if b["expected_rank"] == 1 and c["expected_rank"] > 1 else
                            "remained_correct_top1" if b["expected_rank"] == 1 else "remained_incorrect"),
        })
        if q in ERROR_CATEGORIES:
            cats, why = ERROR_CATEGORIES[q]
            rows[-1]["error_categories"] = [CATEGORY_NAMES[k] for k in cats]
            rows[-1]["error_rationale"] = why

    worsened = {r["query_id"] for r in rows if r["outcome_definition_to_example"] == "worsened_with_example"}
    if worsened != set(ERROR_CATEGORIES):
        fail(f"ERROR_CATEGORIES must cover exactly the worsened queries: {sorted(worsened)}")

    # ---- B. outcome groups ----------------------------------------------------------------------------------
    def counts(key):
        c = Counter(r[key] for r in rows)
        return {k: {"n": v, "pct": round(100 * v / 48, 1)} for k, v in sorted(c.items())}
    outcomes = {"outcome": counts("outcome_definition_to_example"), "top1_status": counts("top1_status")}

    # ---- C. error categories --------------------------------------------------------------------------------
    cat_counts = Counter(c for r in rows for c in r.get("error_categories", []))

    # ---- D. attraction ----------------------------------------------------------------------------------------
    attraction = {}
    for lab, c in (("term_only", A), ("definition", B), ("example", C)):
        per = {}
        for p in conds[c]["per_query"]:
            top = p["top5"][0]["term"]
            d = per.setdefault(top, {"correct_top1": 0, "incorrect_top1": 0, "incorrect_queries": []})
            if p["hit@1"]:
                d["correct_top1"] += 1
            else:
                d["incorrect_top1"] += 1
                d["incorrect_queries"].append(p["query_id"])
        attraction[lab] = dict(sorted(per.items(), key=lambda kv: -(kv[1]["correct_top1"] + kv[1]["incorrect_top1"])))
    names = set(attraction["definition"]) | set(attraction["example"])
    inc = lambda lab, n: attraction[lab].get(n, {}).get("incorrect_top1", 0)  # noqa: E731
    shifts = sorted(({"term": n, "incorrect_top1_definition": inc("definition", n),
                      "incorrect_top1_example": inc("example", n),
                      "change": inc("example", n) - inc("definition", n)} for n in names),
                    key=lambda d: (-d["change"], d["term"]))
    by_term = {t["term"]: t for t in all_terms}
    attractors = []
    for s in shifts:
        if s["change"] < 2:
            continue
        t = by_term[s["term"]]
        ex = t["positive_examples"][0]["text"]
        attractors.append({**s, "incorrect_queries_example": attraction["example"][s["term"]]["incorrect_queries"],
                           "definition": t["definition"], "example": ex,
                           "example_other_pilot_terms": sorted(n for n, rx in term_rx.items()
                                                               if n != t["term"] and rx.search(norm(ex))),
                           "example_general_ml_vocabulary": sorted({w for w in GENERAL_ML_VOCAB if norm(w) in norm(ex)}),
                           "example_chars": len(ex), "inspection_note": notes_norm.get(norm(s["term"]))})
    if any(a["inspection_note"] is None for a in attractors):
        fail("Every major attractor needs a manual inspection note.")

    # ---- E. example properties by outcome ----------------------------------------------------------------------
    props = {}
    for o in ("improved_with_example", "worsened_with_example", "unchanged_with_example"):
        g = [r for r in rows if r["outcome_definition_to_example"] == o]
        props[o] = {
            "n": len(g),
            "example_chars": group(r["example_chars"] for r in g),
            "example_tokens": group(r["example_tokens"] for r in g),
            "exact_siwar_term_present": sum(r["example_exact_siwar_term"] for r in g),
            "other_pilot_term_present": sum(bool(r["example_other_pilot_terms"]) for r in g),
            "multiple_technical_concepts": sum(r["example_multiple_technical_concepts"] for r in g),
            "general_ml_vocabulary_items": group(len(r["example_general_ml_vocabulary"]) for r in g),
            "source_types": dict(Counter(r["example_source_type"] for r in g)),
        }

    # ---- F. specificity -----------------------------------------------------------------------------------------
    spec = {}
    for cls in SPECIFICITY:
        g = [r for r in rows if r["specificity"] == cls]
        spec[cls] = {"n": len(g), **{lab: metrics_from_ranks([r[f"rank_{lab}"] for r in g])
                                     for lab in ("term_only", "definition", "example")},
                     "definition_to_example": dict(Counter(r["outcome_definition_to_example"] for r in g))}

    # ---- G. language style ----------------------------------------------------------------------------------------
    styles = {}
    for s in sorted({r["language_style"] for r in rows}):
        g = [r for r in rows if r["language_style"] == s]
        styles[s] = {"n": len(g), **{lab: metrics_from_ranks([r[f"rank_{lab}"] for r in g])
                                     for lab in ("term_only", "definition", "example")},
                     "definition_to_example": dict(Counter(r["outcome_definition_to_example"] for r in g))}
    for s, v in styles.items():  # reconcile Top-1 hit counts with the stored per-style counts
        for lab, c in (("term_only", A), ("definition", B), ("example", C)):
            stored = conds[c]["top1_by_language_style"][s]
            if round(v[lab]["top1_accuracy"] * v["n"]) != stored["top1_hits"] or v["n"] != stored["n"]:
                fail(f"Style {s} does not reconcile for {c}.")

    # ---- H. definition contribution -------------------------------------------------------------------------------
    d_rows = sorted(rows, key=lambda r: -r["rank_change_term_to_definition"])
    definition = {
        "improved": sum(r["rank_change_term_to_definition"] > 0 for r in rows),
        "worsened": sum(r["rank_change_term_to_definition"] < 0 for r in rows),
        "unchanged": sum(r["rank_change_term_to_definition"] == 0 for r in rows),
        "largest_gains": [{k: r[k] for k in ("query_id", "expected_term", "selection_category", "rank_term_only",
                                             "rank_definition")} for r in d_rows[:10]],
        "largest_losses": [{k: r[k] for k in ("query_id", "expected_term", "selection_category", "rank_term_only",
                                              "rank_definition")} for r in d_rows[::-1][:5]
                           if r["rank_change_term_to_definition"] < 0],
        "by_pilot_selection_category": {
            cat: {"n": len(g), "median_rank_gain": statistics.median(r["rank_change_term_to_definition"] for r in g),
                  "top1_term_only": sum(r["term_only_hit@1"] for r in g),
                  "top1_definition": sum(r["definition_hit@1"] for r in g)}
            for cat in ("ambiguous", "technical", "abbreviation_alias")
            for g in [[r for r in rows if r["selection_category"] == cat]]},
        "previously_noted_terms": [{k: r[k] for k in ("expected_term", "rank_term_only", "rank_definition")}
                                   for r in rows if norm(r["expected_term"]) in {norm(w) for w in ("هلوسة", "وكيل", "تحيُّز", "بيئة")}],
    }

    out = {
        "analysis": "error_analysis_e5_48",
        "source_results": ABLATION.relative_to(PROJECT_ROOT).as_posix(),
        "source_timestamp_utc": abl["run"]["timestamp_utc"],
        "model_name": abl["run"]["model_name"],
        "n_queries": 48,
        "excluded_entries": abl["run"]["excluded_entries"],
        "method_notes": [
            "Descriptive analysis of stored results; no retrieval model was run and no embeddings were computed.",
            "Metrics per subgroup are recomputed from stored ranks; overall metrics reconcile exactly with the source file.",
            "error_categories, specificity and attractor inspection notes are manual, exploratory annotations.",
            "Literal pilot-term matches use the pilot's clitic-tolerant regex on diacritic-stripped text; a literal "
            "match does not imply the same sense.",
            "example_multiple_technical_concepts = the example literally matches two or more pilot terms (target included).",
        ],
        "category_definitions": CATEGORY_NAMES,
        "overall_metrics": {lab: conds[c]["metrics"] for lab, c in (("term_only", A), ("definition", B), ("example", C))},
        "outcome_groups": outcomes,
        "error_category_counts": {k: cat_counts.get(k, 0) for k in CATEGORY_NAMES.values()},
        "attraction": {"top1_by_term": attraction, "incorrect_top1_shift_definition_to_example": shifts,
                       "major_attractors": attractors},
        "example_properties_by_outcome": props,
        "specificity": {"classification": SPECIFICITY, "by_class": spec},
        "language_style": styles,
        "definition_contribution": definition,
        "per_query": rows,
    }
    OUT_JSON.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    OUT_MD.write_text(render_md(out), encoding="utf-8")
    print(f"Saved: {OUT_JSON.relative_to(PROJECT_ROOT).as_posix()}, {OUT_MD.relative_to(PROJECT_ROOT).as_posix()}")


def f3(x):
    return f"{x:.3f}"


def render_md(o):
    m = o["overall_metrics"]
    L = ["# Error analysis — E5 48-term ablation", "",
         f"Source: `{o['source_results']}` ({o['model_name']}, 48 queries). Descriptive analysis of stored results; "
         "no model was re-run. Manual categorisations are exploratory and marked as such.", "",
         "Excluded entries (no valid independent usage example): "
         + "; ".join(f"{e['term']} ({e['reason']})" for e in o["excluded_entries"]) + ".", "",
         "## 1. Overall results", "",
         "| Metric | Term only | Term + definition | Term + definition + example |", "|---|---:|---:|---:|"]
    for k in ("top1_accuracy", "top3_accuracy", "top5_accuracy", "mrr"):
        L.append(f"| {k} | {f3(m['term_only'][k])} | {f3(m['definition'][k])} | {f3(m['example'][k])} |")
    og = o["outcome_groups"]
    L += ["", "## 2. Outcome groups (definition → definition + example)", "",
          "| Group | n | % |", "|---|---:|---:|"]
    L += [f"| {k} | {v['n']} | {v['pct']} |" for k, v in og["outcome"].items()]
    L += ["", "| Top-1 status | n | % |", "|---|---:|---:|"]
    L += [f"| {k} | {v['n']} | {v['pct']} |" for k, v in og["top1_status"].items()]

    L += ["", "## 3. Worsened queries and error categories (manual, exploratory)", "",
          "| Query | Term | Style | Rank B → C | Top-1 under C | Categories |", "|---|---|---|---|---|---|"]
    for r in o["per_query"]:
        if "error_categories" in r:
            L.append(f"| {r['query_id']} | {r['expected_term']} | {r['language_style']} | {r['rank_definition']} → "
                     f"{r['rank_example']} | {r['top1_example']} | {', '.join(r['error_categories'])} |")
    L += ["", "Category counts (a query can have several): "
          + ", ".join(f"{k} {v}" for k, v in o["error_category_counts"].items() if v) + ".", ""]
    for r in o["per_query"]:
        if "error_rationale" in r:
            L.append(f"- **{r['query_id']} {r['expected_term']}**: {r['error_rationale']}")

    a = o["attraction"]
    L += ["", "## 4. Attraction analysis", "",
          "Incorrect Top-1 occurrences per term (terms with any change between conditions):", "",
          "| Term | Incorrect Top-1 (definition) | Incorrect Top-1 (definition + example) | Change |",
          "|---|---:|---:|---:|"]
    L += [f"| {s['term']} | {s['incorrect_top1_definition']} | {s['incorrect_top1_example']} | {s['change']:+d} |"
          for s in a["incorrect_top1_shift_definition_to_example"] if s["change"] != 0]
    L += ["", "Major attractors (incorrect Top-1 increase ≥ 2):", ""]
    for x in a["major_attractors"]:
        L.append(f"- **{x['term']}** ({x['incorrect_top1_definition']} → {x['incorrect_top1_example']}; queries "
                 f"{', '.join(x['incorrect_queries_example'])}). Other pilot terms in its example: "
                 f"{', '.join(x['example_other_pilot_terms']) or 'none'}; general ML vocabulary items: "
                 f"{len(x['example_general_ml_vocabulary'])}; {x['example_chars']} chars. {x['inspection_note']}")

    L += ["", "## 5. Example properties by outcome (descriptive)", "",
          "| Outcome | n | Mean chars | Mean tokens | Exact Siwar term | Other pilot term in example | ≥2 pilot terms | Mean general-ML items |",
          "|---|---:|---:|---:|---:|---:|---:|---:|"]
    for k, p in o["example_properties_by_outcome"].items():
        L.append(f"| {k} | {p['n']} | {p['example_chars']['mean']} | {p['example_tokens']['mean']} | "
                 f"{p['exact_siwar_term_present']} | {p['other_pilot_term_present']} | {p['multiple_technical_concepts']} | "
                 f"{p['general_ml_vocabulary_items']['mean']} |")

    L += ["", "## 6. Term specificity (manual, exploratory)", "",
          "| Class | n | Top-1 term | Top-1 def | Top-1 def+ex | MRR term | MRR def | MRR def+ex | Def→ex improved/worsened/unchanged |",
          "|---|---:|---:|---:|---:|---:|---:|---:|---|"]
    for k, v in o["specificity"]["by_class"].items():
        d = v["definition_to_example"]
        L.append(f"| {k} | {v['n']} | {f3(v['term_only']['top1_accuracy'])} | {f3(v['definition']['top1_accuracy'])} | "
                 f"{f3(v['example']['top1_accuracy'])} | {f3(v['term_only']['mrr'])} | {f3(v['definition']['mrr'])} | "
                 f"{f3(v['example']['mrr'])} | {d.get('improved_with_example', 0)}/{d.get('worsened_with_example', 0)}/"
                 f"{d.get('unchanged_with_example', 0)} |")

    L += ["", "## 7. Language style", "",
          "Saudi colloquial (n=7) and Arabic–English mixed (n=4) are too small for reliable conclusions.", "",
          "| Style | n | Condition | Top-1 | Top-3 | Top-5 | MRR |", "|---|---:|---|---:|---:|---:|---:|"]
    for s, v in o["language_style"].items():
        for lab in ("term_only", "definition", "example"):
            x = v[lab]
            L.append(f"| {s} | {v['n']} | {lab} | {f3(x['top1_accuracy'])} | {f3(x['top3_accuracy'])} | "
                     f"{f3(x['top5_accuracy'])} | {f3(x['mrr'])} |")
    L += ["", "Definition → example rank changes by style: "
          + "; ".join(f"{s}: " + ", ".join(f"{k.split('_')[0]} {n}" for k, n in sorted(v["definition_to_example"].items()))
                      for s, v in o["language_style"].items()) + "."]

    d = o["definition_contribution"]
    L += ["", "## 8. Definition contribution (term only → term + definition)", "",
          f"Improved {d['improved']}, worsened {d['worsened']}, unchanged {d['unchanged']}.", "",
          "| Query | Term | Pilot category | Rank term only → definition |", "|---|---|---|---|"]
    L += [f"| {r['query_id']} | {r['expected_term']} | {r['selection_category']} | {r['rank_term_only']} → {r['rank_definition']} |"
          for r in d["largest_gains"]]
    if d["largest_losses"]:
        L += ["", "Largest losses: " + "; ".join(f"{r['query_id']} {r['expected_term']} {r['rank_term_only']} → "
                                               f"{r['rank_definition']}" for r in d["largest_losses"]) + "."]
    L += ["", "| Pilot selection category | n | Median rank gain | Top-1 term only | Top-1 definition |",
          "|---|---:|---:|---:|---:|"]
    L += [f"| {k} | {v['n']} | {v['median_rank_gain']} | {v['top1_term_only']} | {v['top1_definition']} |"
          for k, v in d["by_pilot_selection_category"].items()]
    L += ["", "Previously noted terms: " + "; ".join(f"{r['expected_term']} {r['rank_term_only']} → {r['rank_definition']}"
                                                   for r in d["previously_noted_terms"]) + "."]
    L += ["", render_conclusions(o), THREATS_AND_HYPOTHESES]
    return "\n".join(L) + "\n"


def render_conclusions(o):
    """Conclusions with every number taken from the computed analysis (no hand-typed figures)."""
    m, d, og = o["overall_metrics"], o["definition_contribution"], o["outcome_groups"]
    oc, ts = og["outcome"], og["top1_status"]
    n = lambda grp, k: grp.get(k, {}).get("n", 0)  # noqa: E731
    top1_b = n(ts, "remained_correct_top1") + n(ts, "dropped_from_top1")
    spec = o["specificity"]["by_class"]
    cat = d["by_pilot_selection_category"]
    attr = ", ".join(a["term"] for a in o["attraction"]["major_attractors"])
    worse = o["example_properties_by_outcome"]
    return "\n".join([
        "## 9. Conclusions", "",
        "### Supported findings",
        f"- Adding the Siwar definition to the term substantially improved retrieval over the term-only representation "
        f"on the same 48 terms and queries (Top-1 {f3(m['term_only']['top1_accuracy'])} → {f3(m['definition']['top1_accuracy'])}, "
        f"MRR {f3(m['term_only']['mrr'])} → {f3(m['definition']['mrr'])}); {d['improved']} queries improved in rank, "
        f"{d['worsened']} worsened and {d['unchanged']} were unchanged.",
        f"- No additional benefit from a single usage example was detected beyond the definition-only representation in "
        f"this pilot (Top-1 {f3(m['definition']['top1_accuracy'])} → {f3(m['example']['top1_accuracy'])}, MRR "
        f"{f3(m['definition']['mrr'])} → {f3(m['example']['mrr'])}; {n(oc, 'improved_with_example')} queries improved, "
        f"{n(oc, 'worsened_with_example')} worsened, {n(oc, 'unchanged_with_example')} unchanged).", "",
        "### Observed patterns (descriptive)",
        f"- After adding the example, half of the queries keep the same rank and changes go in both directions; "
        f"{n(ts, 'remained_correct_top1')} of the {top1_b} Top-1 hits under the definition condition are retained, "
        f"{n(ts, 'dropped_from_top1')} drop out and {n(ts, 'newly_reached_top1')} are newly reached.",
        f"- Some terms became incorrect Top-1 answers more often with examples ({attr}). Their examples use "
        "model-building / training vocabulary, combine several technical concepts, or literally contain other pilot terms.",
        f"- Examples of worsened queries are longer on average ({worse['worsened_with_example']['example_chars']['mean']} chars vs "
        f"{worse['improved_with_example']['example_chars']['mean']} for improved and "
        f"{worse['unchanged_with_example']['example_chars']['mean']} for unchanged) and less often contain the exact Siwar "
        f"term ({worse['worsened_with_example']['exact_siwar_term_present']}/{worse['worsened_with_example']['n']} vs "
        f"{worse['improved_with_example']['exact_siwar_term_present']}/{worse['improved_with_example']['n']} improved).",
        "- Several worsened queries have examples that discuss the target term in a different context than its "
        "definition (cybersecurity, banking, open science, sports media, deepfakes) or use a different lexical form "
        "(فرط الاستعداد, الالتفافية).",
        f"- By manual specificity class, Top-1 for broad terms fell from {f3(spec['broad']['definition']['top1_accuracy'])} to "
        f"{f3(spec['broad']['example']['top1_accuracy'])} with examples (n={spec['broad']['n']}), while specific terms kept "
        f"Top-1 ({f3(spec['specific']['definition']['top1_accuracy'])}) and their MRR moved "
        f"{f3(spec['specific']['definition']['mrr'])} → {f3(spec['specific']['example']['mrr'])} (n={spec['specific']['n']}).",
        f"- In the term-only → definition transition, gains concentrate in the pilot's 'ambiguous' category (terms whose "
        f"names are general-language words): median rank gain {cat['ambiguous']['median_rank_gain']} and Top-1 "
        f"{cat['ambiguous']['top1_term_only']} → {cat['ambiguous']['top1_definition']} of {cat['ambiguous']['n']}, versus "
        f"median {cat['technical']['median_rank_gain']} (technical) and {cat['abbreviation_alias']['median_rank_gain']} "
        f"(abbreviation/alias). Definitions also worsened {d['worsened']} queries, including broad terms (e.g. "
        + "; ".join(f"{r['expected_term']} {r['rank_term_only']} → {r['rank_definition']}" for r in d["largest_losses"][:3])
        + ").",
    ])


THREATS_AND_HYPOTHESES = """
### Hypotheses for future work (not findings)
- Usage examples written in broad ML/AI language may introduce semantic competition between entries.
- More discriminative examples (describing the concept's mechanism) may work better than topical examples.
- Broad target terms may be more vulnerable to semantic competition from examples than specific terms
  (suggested only by the exploratory specificity split; small groups, single annotator).
- The example selection strategy (which example, how long, what context) may matter more than the presence
  of an example; the deterministic first-example rule was not optimised.

## 10. Threats to validity
- Small pilot: 48 evaluated terms, one Gold query per term; one query moves Top-1 by about 0.021.
- One usage example per term, chosen deterministically as the first stored example (not selected for quality).
- Examples vary in source type and writing style (journal abstracts, theses, guidelines, book translations).
- Error categories, specificity classes and attractor notes are manual and exploratory (single annotator).
- Two entries (حُزمة, بث) were excluded because no valid independent example was found.
- Saudi colloquial (n=7) and Arabic–English mixed (n=4) query groups are small.
- Some Siwar definitions contain aliases or related terminology (e.g. «ويُطلق عليه أيضًا ...»), which can affect
  both definition and example conditions.
"""


if __name__ == "__main__":
    main()
