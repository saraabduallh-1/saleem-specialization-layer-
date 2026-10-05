"""E5 48-term ablation: term-only vs term + definition vs term + definition + usage example.

Fair comparison on the 48 pilot entries that have at least one verified positive usage example.
The two entries without one are excluded by ID (حُزمة: terminological_mismatch, بث: source_scarcity),
together with their Gold queries; the subset is built in memory and no dataset file is modified.

All three conditions share the model, the 48 terms, the 48 Gold queries (encoded once with the same
"query: " prefix), cosine similarity on L2-normalized embeddings and batch size. Only the text embedded
per terminology entry changes:
  A  passage: {term}
  B  passage: المصطلح: {term}. التعريف: {definition}
  C  passage: المصطلح: {term}. التعريف: {definition}. مثال الاستخدام: {first positive example}
Condition C uses exactly the first stored positive example; no negative, generated or extra examples,
aliases, variants, abbreviations or English terms are used. Results go to a new file; the 50-term
results are not touched.
"""
import json
import platform
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import sentence_transformers
import torch
import transformers
from sentence_transformers import SentenceTransformer

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TERMS_PATH = PROJECT_ROOT / "data/processed/data_ai/terminology_pilot_50.json"
GOLD_PATH = PROJECT_ROOT / "data/gold_test/data_ai_retrieval_gold_50.json"
OUT_PATH = PROJECT_ROOT / "results/retrieval_e5_48_ablation.json"

MODEL_NAME = "intfloat/multilingual-e5-large"
QUERY_PREFIX = "query: "
PASSAGE_PREFIX = "passage: "
TOP_KS = (1, 3, 5)
BATCH_SIZE = 32

# Entries without a verified positive usage example (see pilot.positive_example_unresolved).
EXCLUDED = {
    "28c82b94-8d47-4728-b819-1544d54b9103": ("حُزمة", "terminological_mismatch"),
    "45590793-f757-41fc-8325-5ed6303f02a8": ("بث", "source_scarcity"),
}

CONDITIONS = {
    "A_term_only": PASSAGE_PREFIX + "{term}",
    "B_term_definition": PASSAGE_PREFIX + "المصطلح: {term}. التعريف: {definition}",
    "C_term_definition_example": PASSAGE_PREFIX + "المصطلح: {term}. التعريف: {definition}. مثال الاستخدام: {example}",
}


def fail(message):
    print(f"FAIL: {message}", file=sys.stderr)
    sys.exit(1)


def load_subset():
    terms = json.loads(TERMS_PATH.read_text(encoding="utf-8"))
    gold = json.loads(GOLD_PATH.read_text(encoding="utf-8"))
    queries = gold["queries"]
    by_id = {t["id"]: t for t in terms}

    for eid, (term, reason) in EXCLUDED.items():
        t = by_id.get(eid)
        if t is None or t["term"] != term:
            fail(f"Excluded id {eid} does not match term {term}.")
        if t["positive_examples"] or t["pilot"].get("positive_example_unresolved", {}).get("reason") != reason:
            fail(f"Excluded entry {term} is not recorded as unresolved ({reason}).")

    terms48 = [t for t in terms if t["id"] not in EXCLUDED]
    queries48 = [q for q in queries if q["expected_id"] not in EXCLUDED]
    if len(terms48) != 48 or len(queries48) != 48:
        fail(f"Expected 48 terms and 48 queries, got {len(terms48)} and {len(queries48)}.")
    if any(not t["positive_examples"] for t in terms48):
        fail("A retained entry has no positive example.")
    if {q["expected_id"] for q in queries48} != {t["id"] for t in terms48}:
        fail("Gold queries and retained terms do not correspond one-to-one.")
    gold_texts = {q["query"].strip() for q in queries}
    if any(t["positive_examples"][0]["text"].strip() in gold_texts for t in terms48):
        fail("A Gold query is used as a usage example.")
    return terms48, queries48, gold


def term_text(condition, t):
    return CONDITIONS[condition].format(term=t["term"], definition=t["definition"],
                                        example=t["positive_examples"][0]["text"])


def evaluate(terms, queries, query_emb, term_emb):
    scores = query_emb @ term_emb.T  # cosine similarity (embeddings are normalized)
    ranking = torch.argsort(scores, dim=1, descending=True).cpu().tolist()
    scores = scores.cpu().tolist()
    per_query, hits, rr = [], {k: 0 for k in TOP_KS}, []
    for q, order, row in zip(queries, ranking, scores):
        ranked_ids = [terms[i]["id"] for i in order]
        rank = ranked_ids.index(q["expected_id"]) + 1
        for k in TOP_KS:
            hits[k] += rank <= k
        rr.append(1.0 / rank)
        per_query.append({
            "query_id": q["query_id"],
            "query": q["query"],
            "language_style": q.get("language_style"),
            "expected_id": q["expected_id"],
            "expected_term": q["expected_term"],
            "expected_rank": rank,
            "expected_score": round(row[order[rank - 1]], 6),
            **{f"hit@{k}": rank <= k for k in TOP_KS},
            "top5": [{"rank": r + 1, "id": terms[i]["id"], "term": terms[i]["term"], "score": round(row[i], 6)}
                     for r, i in enumerate(order[:5])],
        })
    n = len(queries)
    metrics = {f"top{k}_accuracy": hits[k] / n for k in TOP_KS}
    metrics["mrr"] = sum(rr) / n
    return metrics, per_query


def by_style(per_query):
    out = {}
    for p in per_query:
        s = out.setdefault(p["language_style"], {"n": 0, "top1_hits": 0})
        s["n"] += 1
        s["top1_hits"] += p["hit@1"]
    for s in out.values():
        s["top1_accuracy"] = s["top1_hits"] / s["n"]
    return out


def compare(before, after):
    """Per-query rank changes from condition `before` to condition `after`."""
    rows = []
    for b, a in zip(before, after):
        rows.append({"query_id": b["query_id"], "expected_term": b["expected_term"],
                     "language_style": b["language_style"], "rank_before": b["expected_rank"],
                     "rank_after": a["expected_rank"], "rank_change": b["expected_rank"] - a["expected_rank"]})
    return {
        "improved": sum(r["rank_change"] > 0 for r in rows),
        "worsened": sum(r["rank_change"] < 0 for r in rows),
        "unchanged": sum(r["rank_change"] == 0 for r in rows),
        "newly_top1": [r["query_id"] for r in rows if r["rank_before"] > 1 and r["rank_after"] == 1],
        "dropped_from_top1": [r["query_id"] for r in rows if r["rank_before"] == 1 and r["rank_after"] > 1],
        "per_query": rows,
    }


def main():
    if not torch.cuda.is_available():
        fail("CUDA is not available to PyTorch.")

    terms, queries, gold = load_subset()
    print(f"{len(terms)} terms | {len(queries)} gold queries | GPU: {torch.cuda.get_device_name(0)}")

    t0 = time.perf_counter()
    model = SentenceTransformer(MODEL_NAME, device="cuda")
    model.eval()
    load_seconds = time.perf_counter() - t0
    if next(model.parameters()).device.type != "cuda":
        fail("Model is not on CUDA.")

    def encode(texts):
        torch.cuda.synchronize()
        start = time.perf_counter()
        emb = model.encode(texts, batch_size=BATCH_SIZE, convert_to_tensor=True, normalize_embeddings=True)
        torch.cuda.synchronize()
        if emb.device.type != "cuda":
            fail("Embeddings were not computed on CUDA.")
        return emb, time.perf_counter() - start

    query_emb, query_seconds = encode([QUERY_PREFIX + q["query"] for q in queries])

    results, timing = {}, {"model_load": round(load_seconds, 3), "encode_queries": round(query_seconds, 3)}
    for cond in CONDITIONS:
        term_emb, secs = encode([term_text(cond, t) for t in terms])
        timing[f"encode_terms_{cond}"] = round(secs, 3)
        metrics, per_query = evaluate(terms, queries, query_emb, term_emb)
        results[cond] = {"term_text": CONDITIONS[cond], "metrics": metrics,
                         "top1_by_language_style": by_style(per_query), "per_query": per_query}

    names = list(CONDITIONS)
    deltas = {f"{a}->{b}": {m: results[b]["metrics"][m] - results[a]["metrics"][m] for m in results[a]["metrics"]}
              for a, b in [(names[0], names[1]), (names[1], names[2]), (names[0], names[2])]}

    output = {
        "run": {
            "experiment": "e5_48_term_ablation",
            "model_name": MODEL_NAME,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "query_text": QUERY_PREFIX + "query",
            "similarity": "cosine (L2-normalized dot product)",
            "example_selection": "first stored positive_examples entry; exactly one per term",
            "terms_file": TERMS_PATH.relative_to(PROJECT_ROOT).as_posix(),
            "gold_file": GOLD_PATH.relative_to(PROJECT_ROOT).as_posix(),
            "gold_version": gold.get("metadata", {}).get("version"),
            "n_terms": len(terms),
            "n_queries": len(queries),
            "excluded_entries": [{"id": i, "term": t, "reason": r} for i, (t, r) in EXCLUDED.items()],
            "batch_size": BATCH_SIZE,
            "not_used": ["aliases", "abbreviations", "variants", "english_term", "negative_examples",
                         "generated_examples", "reranking", "bm25", "hybrid_search", "query_expansion"],
            "note": "48-term pilot ablation; metrics are not comparable with the 50-term runs.",
        },
        "environment": {
            "python": platform.python_version(),
            "torch": torch.__version__,
            "cuda": torch.version.cuda,
            "gpu": torch.cuda.get_device_name(0),
            "transformers": transformers.__version__,
            "sentence_transformers": sentence_transformers.__version__,
        },
        "timing_seconds": timing,
        "conditions": results,
        "metric_deltas": deltas,
        "comparison_B_to_C": compare(results[names[1]]["per_query"], results[names[2]]["per_query"]),
    }

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Model: {MODEL_NAME}")
    print(f"{'metric':<14}" + "".join(f"{c:>28}" for c in names))
    for m in results[names[0]]["metrics"]:
        print(f"{m:<14}" + "".join(f"{results[c]['metrics'][m]:>28.4f}" for c in names))
    print(f"Timing (s): {timing}")
    print(f"Saved: {OUT_PATH.relative_to(PROJECT_ROOT).as_posix()}")


if __name__ == "__main__":
    main()
