#!/usr/bin/env python3
"""Exp Q: LLM concept naming as query expansion for retrieval.

Qwen reads ONLY the user text (no dictionary, no labels) and names the
technical concept(s) it describes, in English plus a short MSA technical
paraphrase. These are matched against the dictionary:
  - E5 over the Arabic paraphrase (same passages: term + Siwar definition)
  - normalized exact match of the English names against Siwar english_term
and fused with the original-query E5 ranking by reciprocal rank fusion.

Outputs are cached per text so later experiments reuse identical expansions.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import numpy as np

from spec_layer_v2 import (ROOT, Qwen, Retriever, hit_summary, load_eval_items, load_json,
                           load_pool, parse_json_obj, save_json)

OUT = ROOT / "results/v2_architecture_study/exp_q_query_expansion.json"
CACHE = ROOT / "results/v2_architecture_study/concept_naming_cache.json"

NAMING_SYSTEM = (
    "أنت خبير في الذكاء الاصطناعي وعلم البيانات. اقرأ النص وحدد المفهوم التقني الذي يصفه النص فعلًا، إن وُجد. "
    "لا تعتمد على كلمة مفردة لها معنى عام، بل على المعنى الكامل للنص. "
    "أعد JSON فقط بالشكل: "
    "{\"concepts_en\": [\"...\"], \"description_ar\": \"...\"} "
    "حيث concepts_en قائمة من مصطلح إلى ثلاثة مصطلحات إنجليزية تقنية مرتبة من الأدق إلى الأعم، "
    "وdescription_ar وصف تقني موجز بالعربية الفصحى للمفهوم كما ورد في النص. "
    "إذا كان النص لا يصف مفهومًا تقنيًا في الذكاء الاصطناعي أو البيانات فأعد قائمة فارغة ووصفًا فارغًا."
)


def naming_messages(text):
    return [{"role": "system", "content": NAMING_SYSTEM}, {"role": "user", "content": "النص:\n" + text}]


def en_norm(s):
    s = re.sub(r"\(.*?\)", " ", s or "").lower()
    s = re.sub(r"[^a-z0-9 ]+", " ", s)
    s = re.sub(r"\b(the|a|an)\b", " ", s)
    words = [w[:-1] if len(w) > 4 and w.endswith("s") else w for w in s.split()]
    return " ".join(words)


def get_namings(items, qwen):
    cache = load_json(CACHE) if CACHE.exists() else {"prompt": NAMING_SYSTEM, "items": {}}
    if cache["prompt"] != NAMING_SYSTEM:
        raise SystemExit("Concept-naming prompt changed; use a new cache file.")
    for x in items:
        if x["text"] in cache["items"]:
            continue
        raw, meta = qwen(naming_messages(x["text"]))
        try:
            obj = parse_json_obj(raw)
            obj = {"concepts_en": [str(c) for c in (obj.get("concepts_en") or [])][:3],
                   "description_ar": str(obj.get("description_ar") or "")}
        except Exception:
            obj = {"concepts_en": [], "description_ar": "", "parse_error": True}
        obj["raw"] = raw
        cache["items"][x["text"]] = obj
        save_json(cache, CACHE)
        print(x["id"], obj["concepts_en"])
    return cache["items"]


class ExpandedRetriever:
    """Fusion of original-query E5, paraphrase E5 and English-name match."""

    def __init__(self, pool, namings, rrf_k=60):
        self.pool, self.namings, self.rrf_k = pool, namings, rrf_k
        self.base = Retriever(pool, "term_def")
        self.en_index = {}
        for i, e in enumerate(pool.candidates):
            k = en_norm(e.get("english_term"))
            if k:
                self.en_index.setdefault(k, []).append(i)
        # redirect entries' English names point to their canonical entry
        pos = {e["id"]: i for i, e in enumerate(pool.candidates)}
        for e in pool.entries:
            c = pool.canonical_of[e["id"]]
            k = en_norm(e.get("english_term"))
            if c != e["id"] and k and c in pos:
                self.en_index.setdefault(k, []).append(pos[c])

    def _rankings(self, text, mode):
        n = self.namings.get(text, {})
        q = self.base
        rankings = []
        s0 = (q.p @ _enc(["query: " + text])[0])
        if mode in ("orig", "orig+desc", "orig+en", "all"):
            rankings.append(np.argsort(-s0))
        if mode in ("desc", "orig+desc", "all") and n.get("description_ar"):
            s1 = q.p @ _enc(["query: " + n["description_ar"]])[0]
            rankings.append(np.argsort(-s1))
        en_hits = []
        if mode in ("orig+en", "all"):
            for c in n.get("concepts_en") or []:
                en_hits.extend(self.en_index.get(en_norm(c), []))
        return rankings, en_hits, s0

    def search_ids(self, text, mode, k):
        rankings, en_hits, s0 = self._rankings(text, mode)
        score = np.zeros(len(self.pool.candidates))
        for r in rankings:
            score[r] += 1.0 / (self.rrf_k + np.arange(1, len(r) + 1))
        for j, idx in enumerate(dict.fromkeys(en_hits)):
            score[idx] += 1.0 / (self.rrf_k + 1 + j)
        if not rankings:
            score += 1e-9 * s0
        order = np.argsort(-score)
        return [int(i) for i in order[:k]], order

    def search(self, text, mode, k):
        idxs, _ = self.search_ids(text, mode, k)
        return [{"id": self.pool.candidates[i]["id"], "term": self.pool.candidates[i]["term"],
                 "definition": self.pool.candidates[i]["definition"]} for i in idxs]

    def rank(self, text, mode, expected_id):
        _, order = self.search_ids(text, mode, 1)
        pos = {e["id"]: i for i, e in enumerate(self.pool.candidates)}
        target = pos[self.pool.resolve(expected_id)]
        return int(np.where(order == target)[0][0]) + 1


def _enc(texts):
    from spec_layer_v2 import encode
    return encode(texts)


MODES = ["orig", "desc", "orig+desc", "orig+en", "all"]


def main():
    sets = {s: load_eval_items(s) for s in ("dev36", "gold50", "probes")}
    allx = [x for s in sets.values() for x in s]
    qwen = Qwen(max_tokens=200)
    namings = get_namings(allx, qwen)
    report = {"note": "Development evidence only.", "naming_prompt": NAMING_SYSTEM,
              "qwen": qwen.meta(), "results": {}, "abstention_signal": {}}
    for pool_name in ("pilot50", "full"):
        r = ExpandedRetriever(load_pool(pool_name), namings)
        for mode in MODES:
            res = {}
            for s in ("dev36", "gold50"):
                pos = [x for x in sets[s] if x["kind"] == "positive"]
                res[s] = hit_summary([r.rank(x["text"], mode, x["expected_term_id"]) for x in pos])
            report["results"][f"{pool_name}|{mode}"] = res
    # Does an empty concept list work as an abstention signal?
    for s in ("dev36", "gold50", "probes"):
        xs = sets[s]
        report["abstention_signal"][s] = {
            "positives_named_empty": sum(not namings[x["text"]]["concepts_en"] for x in xs if x["kind"] == "positive"),
            "n_positive": sum(x["kind"] == "positive" for x in xs),
            "negatives_named_empty": sum(not namings[x["text"]]["concepts_en"] for x in xs if x["kind"] != "positive"),
            "n_negative": sum(x["kind"] != "positive" for x in xs),
        }
    save_json(report, OUT)
    print(json.dumps({k: report[k] for k in ("results", "abstention_signal")}, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
