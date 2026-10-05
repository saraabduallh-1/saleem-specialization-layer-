"""Pure E5 retrieval baseline on the 50-term pilot.

Each terminology entry is embedded from its Arabic `term` field only (no
definitions, aliases, variants or examples). Each Gold query is embedded and
the pilot terms are ranked by cosine similarity. Reports Top-1/3/5 accuracy
and MRR, and writes per-query results to results/.

Datasets are read only; nothing under data/ is modified.
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
OUT_PATH = PROJECT_ROOT / "results/retrieval_baseline_e5_large.json"

MODEL_NAME = "intfloat/multilingual-e5-large"
# Prefixes recommended on the E5 model card for asymmetric retrieval.
QUERY_PREFIX = "query: "
PASSAGE_PREFIX = "passage: "
TOP_KS = (1, 3, 5)
BATCH_SIZE = 32


def fail(message):
    print(f"FAIL: {message}", file=sys.stderr)
    sys.exit(1)


def load_data():
    terms = json.loads(TERMS_PATH.read_text(encoding="utf-8"))
    gold = json.loads(GOLD_PATH.read_text(encoding="utf-8"))
    queries = gold["queries"]

    term_ids = [t["id"] for t in terms]
    if len(set(term_ids)) != len(term_ids):
        fail("Duplicate ids in terminology pilot.")
    missing = [q["query_id"] for q in queries if q["expected_id"] not in set(term_ids)]
    if missing:
        fail(f"Gold queries whose expected_id is not in the pilot: {missing}")
    return terms, gold, queries


def main():
    if not torch.cuda.is_available():
        fail("CUDA is not available to PyTorch.")

    terms, gold, queries = load_data()
    print(f"{len(terms)} terms | {len(queries)} gold queries | GPU: {torch.cuda.get_device_name(0)}")

    t0 = time.perf_counter()
    model = SentenceTransformer(MODEL_NAME, device="cuda")
    model.eval()
    load_seconds = time.perf_counter() - t0
    if next(model.parameters()).device.type != "cuda":
        fail("Model is not on CUDA.")

    term_texts = [PASSAGE_PREFIX + t["term"] for t in terms]
    query_texts = [QUERY_PREFIX + q["query"] for q in queries]

    torch.cuda.synchronize()
    t0 = time.perf_counter()
    term_emb = model.encode(term_texts, batch_size=BATCH_SIZE, convert_to_tensor=True, normalize_embeddings=True)
    torch.cuda.synchronize()
    term_seconds = time.perf_counter() - t0

    t0 = time.perf_counter()
    query_emb = model.encode(query_texts, batch_size=BATCH_SIZE, convert_to_tensor=True, normalize_embeddings=True)
    torch.cuda.synchronize()
    query_seconds = time.perf_counter() - t0

    if term_emb.device.type != "cuda" or query_emb.device.type != "cuda":
        fail("Embeddings were not computed on CUDA.")

    t0 = time.perf_counter()
    scores = query_emb @ term_emb.T  # cosine similarity (embeddings are normalized)
    ranking = torch.argsort(scores, dim=1, descending=True).cpu().tolist()
    scores = scores.cpu().tolist()
    search_seconds = time.perf_counter() - t0

    per_query = []
    hits = {k: 0 for k in TOP_KS}
    reciprocal_ranks = []
    for q, order, row in zip(queries, ranking, scores):
        ranked_ids = [terms[i]["id"] for i in order]
        rank = ranked_ids.index(q["expected_id"]) + 1
        for k in TOP_KS:
            hits[k] += rank <= k
        reciprocal_ranks.append(1.0 / rank)
        per_query.append({
            "query_id": q["query_id"],
            "query": q["query"],
            "language_style": q.get("language_style"),
            "expected_id": q["expected_id"],
            "expected_term": q["expected_term"],
            "expected_rank": rank,
            "expected_score": round(row[order[rank - 1]], 6),
            **{f"hit@{k}": rank <= k for k in TOP_KS},
            "top5": [
                {"rank": r + 1, "id": terms[i]["id"], "term": terms[i]["term"], "score": round(row[i], 6)}
                for r, i in enumerate(order[:5])
            ],
        })

    n = len(queries)
    metrics = {f"top{k}_accuracy": hits[k] / n for k in TOP_KS}
    metrics["mrr"] = sum(reciprocal_ranks) / n

    output = {
        "run": {
            "baseline": "pure_e5_term_only",
            "model_name": MODEL_NAME,
            "timestamp_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "term_text": "passage: + term (Arabic term field only)",
            "query_text": "query: + query",
            "similarity": "cosine (L2-normalized dot product)",
            "terms_file": TERMS_PATH.relative_to(PROJECT_ROOT).as_posix(),
            "gold_file": GOLD_PATH.relative_to(PROJECT_ROOT).as_posix(),
            "gold_version": gold.get("metadata", {}).get("version"),
            "n_terms": len(terms),
            "n_queries": n,
            "batch_size": BATCH_SIZE,
        },
        "environment": {
            "python": platform.python_version(),
            "torch": torch.__version__,
            "cuda": torch.version.cuda,
            "gpu": torch.cuda.get_device_name(0),
            "transformers": transformers.__version__,
            "sentence_transformers": sentence_transformers.__version__,
        },
        "timing_seconds": {
            "model_load": round(load_seconds, 3),
            "encode_terms": round(term_seconds, 3),
            "encode_queries": round(query_seconds, 3),
            "search": round(search_seconds, 3),
        },
        "metrics": metrics,
        "per_query": per_query,
    }

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Model: {MODEL_NAME}")
    for k in TOP_KS:
        print(f"Top-{k} accuracy: {metrics[f'top{k}_accuracy']:.3f} ({hits[k]}/{n})")
    print(f"MRR:            {metrics['mrr']:.3f}")
    print(f"Timing (s):     {output['timing_seconds']}")
    print(f"Saved: {OUT_PATH.relative_to(PROJECT_ROOT).as_posix()}")


if __name__ == "__main__":
    main()
