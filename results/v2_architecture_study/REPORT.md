# v2 architecture study — Saleem AI specialization layer

**Status:** development / ablation evidence only. `dev36` (ai_final_layer_eval_v1) has been examined
repeatedly; `gold50` (data_ai_retrieval_gold_50) is the earlier retrieval set (some items paraphrase dev36);
`probes` (ai_abstention_probes_v1, 16 NONE items) were written by the assistant and committed before any
v2 run. None of these is an independent test. No Gold label was changed; no expected term reaches any prompt.

Fixed controls: Qwen/Qwen3.5-4B, temperature 0, thinking disabled; Siwar terminology only;
E5-large over `term + original Siwar definition`. Historical results were not modified.

## 1. Methodology problems found in the earlier experiments

| Problem | Evidence | Fix in v2 |
|---|---|---|
| All retrieval numbers used a **50-term candidate pool**, not the 1,443-entry dictionary | dev36 Hit@3 0.83 (pilot-50) → **0.33** (full); gold50 0.72 → 0.30 (`exp_r_retrieval.json`) | All final runs search the full dictionary (1,316 canonical entries; Siwar "انظر" redirects resolved to their target) |
| Substring term metric | fails on ال/inflection (البيانات الضخمة, نموذجًا لغويًا كبيرًا), false-positive on أمر⊂أمريكا; undercounted term use by ~30 % | Token-level clitic/inflection-tolerant matcher (`spec_layer_v2.term_present`) |
| Post-generation LLM validator | dropped the term in 16/29 items, **10 of which were correct**; judged "term unfit" when the writer had merely omitted it (9 cases) | Validator removed; deterministic presence check + one retry that keeps the term |
| Writer prompt leaked pipeline language | S1 outputs contained "تم التحقق دلاليًا… المصطلح المعتمد" in 9/36 | Writer never sees verification wording; leak detector added |
| No underspecified-AI negatives | dev36 controls are only everyday-sense words | Added 16 frozen probes (everyday sense, human activity, vague AI text) |
| Strict gold-id scoring is invalid on the full dictionary | legitimate neighbours exist (e.g. تقليص الأبعاد vs PCA) | Report strict id accuracy **and** blinded semantic judgement |

Re-scoring of old outputs: `reanalysis_previous_runs.json`.

## 2. What the experiments show

### Retrieval (no LLM; `exp_r_retrieval.json`, `exp_q_query_expansion.json`)
Full dictionary, Hit@5 / Hit@10:

| Query | dev36 | gold50 |
|---|---|---|
| E5 original text | 0.50 / 0.63 | 0.38 / 0.50 |
| + English term in passage | 0.50 / 0.60 | 0.38 / 0.46 |
| + CSLS hubness correction | 0.47 / 0.50 | 0.40 / 0.46 |
| **+ Qwen concept naming → match Siwar `english_term`** | **0.80 / 0.87** | **0.70 / 0.78** |

Concept naming (Qwen names the concept in English from the text only, no dictionary) is the only change
that helps on both sets. It also returned an empty list for 16/22 negatives and 0/80 positives → a free
abstention gate.

### Decision stage (`exp_s_*`, tables in `*_table.json`)
Full dictionary, strict gold-id: correct / wrong / NONE, negatives falsely specialized.

| Decision | dev36 | gold50 | neg FP |
|---|---|---|---|
| Selector v2, K=3 | 21/9/0 | 24/25/1 | 8/22 |
| Selector v2, K=10 | 24/6/0 | 27/23/0 | 10/22 |
| Selector v2, K=10 + naming gate | 24/6/0 | 27/23/0 | 3/22 |
| Selector v3 (stricter wording), K=10 + gate | 22/8/0 | 21/28/1 | 6/22 |
| + LLM binary verify of chosen term | 13/3/14 | 11/3/36 | 0/22 |
| English-name lookup only (no selector) | 21/6/3 | 21/26/3 | 2/22 |
| **K=10 + gate + relaxed agreement** | **22/1/7** | **23/9/18** | **1/22** |

- Top-3 is **not** the best depth once the pool is realistic: K=10 gives more correct picks and no more confusion.
- Prompt wording cannot make the 4B selector abstain (v3 is worse); a pre-generation LLM verifier is
  as over-strict as the old validator (rejects ~half of correct terms).
- The deterministic **agreement rule** (accept the selected entry only if its Siwar English name matches,
  or is the head of, a concept named independently by the naming call; "AI" expanded) gives high precision
  with no extra call. The relaxed head-match was introduced after dev error analysis and adds 3+2 correct,
  0 wrong — treat as dev-tuned.

### Writer (`exp_w_writer.json`, same selections for all variants)
Correct-term use given a correct selection (automatic), plus blinded quality on positives:

| Writer input | use dev36 / gold50 | successful specialisation* dev36 / gold50 | dictionary-style | leaks |
|---|---|---|---|---|
| term + definition | 0.93 / 0.62 | 2 / 10 | 29 | 10 |
| term only | 1.00 / 0.79 | — | — | — |
| term + domain label | 0.93 / 0.82 | — | — | — |
| term + full domain context (D3) | 0.86 / 0.56 | 7 / 9 | 11 | 0 |
| term only + check/retry | 1.00 / 0.91 | 13 / 13 | 6 | 0 |
| **term + 3 generic demos + check/retry** | **1.00 / 0.94** | **17 / 17** | **1** | 0 (1 on a false probe) |
| joint select+rewrite (one call) | 0.29 / 0.35 | — | — | — (10/16 probe FP) |

\*concept correct ∧ term present ∧ natural ∧ meaning fully preserved ∧ no major addition (blinded LLM annotation).
Definitions and full domain context **reduce** term use and cause definition-copying; demonstrations
(3 terms unrelated to every eval item) reduce bolted-on usage.

### Final end-to-end comparison (full dictionary; blinded annotation, `quality_report.json`)

| System | dev36 success | gold50 success | wrong concept in output | meaning=2 (dev/gold) | fluency | negatives safe |
|---|---|---|---|---|---|---|
| Qwen only | 0/30 | 0/50 | 0 | 0.72 / 0.70 | 4.2 | 22/22 |
| selector K10+gate, no agreement, term-only | 13/30 | 12/50 | 4 | 0.75 / 0.58 | 3.6 | 19/22 |
| **Recommended (below)** | **14/30** | **13/50** | **0** | **0.78 / 0.82** | 3.9 | 21/22† |

Judged concept correctness of the recommended system: dev36 22 yes / 1 partial / 0 no (of 23 terms
introduced); gold50 29 / 3 / 0 (of 32). †The one "unsafe" probe is P14 → تأخير (latency) for
"the model became slower to respond"; the blinded annotator did not judge it a false specialization.

## 3. Recommended architecture

```
input ─► [Qwen call 1] concept naming (English concept names, from text only)
           │  empty ─► NONE
           ▼
         retrieval: E5(term+definition) on original text  ⊕  exact/head match of named concepts
         to Siwar english_term (RRF), full dictionary, K=10
           ▼
         [Qwen call 2] selector v2 (choose C1..C10 or NONE)
           ▼
         deterministic agreement check (selected entry's Siwar English name ~ a named concept)
           │  disagree ─► NONE
           ▼
         [Qwen call 3] writer: term only + 3 generic demonstrations
           ▼
         deterministic morphology-aware presence check → at most one retry that keeps the term
NONE path: same writer instruction without terminology.
```

Removed: LLM post-validator, retry-that-drops-the-term, definitions and domain definition/guidelines in
the writer prompt, Top-3 limit, joint select+rewrite, LLM pre-verifier.

## 4. What is still broken

1. **Coverage**: only 22/30 (dev36) and 23/50 (gold50) positives receive a term; recall is limited by
   retrieval (11/50 gold50 never in top-10) and by agreement rejecting correct picks when concept naming
   disagrees (e.g. it never names "epoch" for "five passes over the data") or Siwar lacks an English name (وكيل).
2. **Naturalness**: in ~40 % of correct-term outputs the annotator judged the term bolted on
   ("…وذلك عبر X"). Fluency drops from 4.2 (Qwen alone) to ~3.9.
3. **Meaning drift exists in Qwen itself** (~30 % of baseline rewrites lose some nuance, e.g. a wish
   becoming a statement); the layer does not worsen it but does not fix it.
4. Strict-wrong selections on gold50 (9) are mostly near-neighbours (تعلُّم تعزيزي for reward,
   نموذج الانتباه for transformer); one was judged wrong in the output on gold50 under the no-agreement variant only.
5. Quality labels come from blinded LLM annotators (Claude), not human experts.

## 5. Next technically justified changes
- Add Siwar English equivalents/aliases where the **source** provides them (not invented) and use the
  naming call's Arabic description as a second agreement signal for entries without English names.
- Writer naturalness: try a "rewrite-then-substitute" variant (writer may place the term once where the
  described concept appears) and measure with the same blinded rubric.

## 6. Required held-out evaluation
New, unseen, expert-reviewed set before any claim: ≥150 positives across subdomains and registers
(MSA / Saudi / mixed), ≥60 negatives in three types (everyday sense, human activity, vague AI text),
written by people who have not seen these results, labels = acceptable term set (primary + acceptable
alternatives, decided before running), scored by two human annotators with this rubric
(report agreement), against the full dictionary, run once with frozen prompts and code.
