# v3 retrieval study — E1–E3 summary (development evidence)

Full Siwar AI dictionary (1,316 units). dev36 = 30 positives, gold50 = 50 positives, negatives = 6 dev36
controls + 16 probes. Dictionary capability profiles are simulated by masking roles
(`P-def` = headword + definition, no English; `P-full` = all Siwar roles). Not an independent test.

## E1 — no LLM (`e1_no_llm.json`)
Best generic combination: dense_unit + dense_def + lexical (BM25), RRF.
P-def Hit@10 / MRR: dev36 0.63/0.31 → 0.73/0.48; gold50 0.50/0.27 → 0.54/0.29.
Surface (literal headword) signal hurts on descriptive input → excluded from fusion.

## E2 — structured query understanding (`e2_query_understanding.json`)
One Qwen call → {technical, concept_ar, concept_en, keywords}.
- Arabic-only (P-def): Hit@10 0.83 / 0.60, Hit@50 1.00 / 0.88, MRR 0.64 / 0.38.
- With English (P-full): Hit@10 0.97 / 0.78, Hit@50 1.00 / 0.96, MRR 0.88 / 0.49.
- No-definition glossary profile still works: 0.77 / 0.52.
- `technical=false` for 20/22 negatives and 1/80 positives.
- Fairness (English removed from 50 % of units, 3 seeds): with **neutral** missing-field fusion, entries
  that lost English are never worse than with no English anywhere; with **zero** fusion they lose
  2.5–3 points in every seed. Neutral is the default.

## E3 — reranking first-stage top-50 (`e3_rerank_P-def.json`, `e3_rerank_P-full.json`)

| Profile | Method | dev36 H@1/H@3/H@5/H@10/MRR | gold50 H@1/H@3/H@5/H@10/MRR | neg. literal traps |
|---|---|---|---|---|
| P-def | first stage | .53/.70/.77/.83/.64 | .28/.42/.46/.60/.38 | 2/22 |
| P-def | cross-encoder | .37/.53/.60/.70/.48 | .16/.30/.38/.52/.28 | 0/22 |
| P-def | **Qwen listwise** | **.70/.90/.93/1.00/.79** | **.48/.64/.74/.78/.58** | 3/22 |
| P-full | first stage | **.83/.90/.93/.97/.88** | .38/.54/.56/.78/.49 | 3/22 |
| P-full | cross-encoder | .40/.50/.60/.73/.50 | .16/.38/.48/.62/.32 | 0/22 |
| P-full | Qwen listwise | .60/.80/.87/.87/.71 | **.46/.76/.80/.88/.62** | 3/22 |

Cost per query (excluding the shared query-understanding call):

| Method | extra calls | latency | local memory | model size |
|---|---|---|---|---|
| first stage (E5 + BM25 + fusion) | 0 | ~0.16 s (query encoding) | E5 already loaded | — |
| cross-encoder mMiniLMv2-L12 | 0 | 0.30 s (MPS) | +340–1,190 MB RSS | 118 M params, 493 MB |
| Qwen listwise (top-50) | 1 API call | 2.7 s median-ish (p90 2.9 s) | 0 | remote 4B, ~1.8–2.0 k prompt tokens |

Cross-encoder variant with the Arabic description in the query (CE+ar) is worse still. CE top-1 score
separates positives from negatives well (AUC 0.93 for CE+ar) but it is not a good ranker here.
"Traps" = negatives whose top-1 headword literally occurs in the input (دورة/دورة تدريبية,
مُحوِّل/electrical transformer, مكافأة/bonus); rerankers do not make abstention decisions.
