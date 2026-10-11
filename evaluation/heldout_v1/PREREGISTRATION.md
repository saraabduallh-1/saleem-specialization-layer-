# Pre-registration — abstention rule evaluation on `heldout_v1`

Registered on branch `heldout-eval-framework` (created from `v3-retrieval-study`) before any
held-out item exists. This document, `sampled_terms.json`, and the scripts
`heldout_sample_terms.py`, `heldout_freeze_split.py` and `heldout_score.py` are frozen from the
commit that adds them. Any change after that commit must be logged in `DEVIATIONS.md` with a reason
and date, and reported.

## 1. Question
Does a deterministic, dictionary-agnostic corroboration rule (S1) raise the precision of accepted
terminology and keep false specialization low, on texts never used in development, at an acceptable
loss of coverage?

## 2. Data
- **Authoring method (amended, A3 / D3):** items are **source-grounded, LLM-drafted,
  human-validated**. Targets come from `sampled_terms.json`; each item's meaning is grounded in an
  independent authoritative technical/scientific source where reasonably possible (provenance kept
  in the item); the Arabic text may be drafted/paraphrased by an LLM, must not copy the source and
  must not leak the target headword, alias, abbreviation or English equivalent; writing contexts vary
  (formal technical/report, developer questions/issues, social/Saudi conversational technical,
  product/support/workplace). Public human writing (Reddit, GitHub Issues, Stack Overflow, forums)
  may serve only as a style reference, not as the semantic source. LLM drafting is disclosed per item.
  Gold labels still require the human validation in ANNOTATION_GUIDE.md before the set is frozen.
- `heldout_v1`: about 290 items drafted as above (see AUTHORING_GUIDE.md),
  second-annotated and adjudicated (see ANNOTATION_GUIDE.md):
  120 plain positives, 40 near-neighbour positives (20 pairs), 30 ambiguous positives
  (two acceptable entries), 50 everyday-sense negatives, 50 vague technical negatives.
  Final counts may be lower after drops; drops are logged.
- Terms sampled with seed 20261011 from the full Siwar AI dictionary
  (`terminology_base.json`, SHA-256 recorded in `sampled_terms.json`), excluding the 50 pilot terms,
  every expected/selected/rejected/forced term in any stored v1–v3 result, and the three writer
  demonstration terms (199 entries excluded; 1,117 eligible).
- Split: stratified by `item_type`, 30 % calibration / 70 % test, seed 20261012
  (`heldout_freeze_split.py split`), created once, only after `freeze`.

## 3. Frozen system (no architecture or prompt changes after items are visible)
- Model Qwen/Qwen3.5-4B, temperature 0, thinking disabled; retriever intfloat/multilingual-e5-large.
- Query understanding: `specialization_layer/engine/query_understanding.py` (one call; gate:
  `technical == false` → NONE).
- First stage: `Engine` with signals dense_unit, dense_def, lexical on the text; dense_unit,
  dense_def on `concept_ar`; lexical on `keywords`; plus translation_lex and translation_dense on
  `concept_en` **only in P-full**. Fusion: RRF, neutral missing-field policy.
- Decision (amended, D2), per profile:
  - **P-full**: one call over the first-stage top-30 (`decision.JOINT_SYSTEM`).
  - **P-def**: Qwen listwise reranker over the first-stage top-50
    (`engine.rerank.LLMListwiseReranker`) → selector over the reranked top-10
    (`decision.SELECTOR_SYSTEM`).
  Candidate availability (§6) refers to the candidates shown to the final decision call
  (30 in P-full, 10 in P-def).
- Profiles: **P-def** (headword + definition; Arabic-only) and **P-full** (all Siwar roles),
  simulated by role masking (`schema.restrict_roles`).

## 4. The abstention rule S1 (two-view corroboration)
For the unit `u` chosen by the decision call:

- **Text view** = the signals whose query part is the original text.
- **Interpretation view** = the signals whose query part comes from query understanding
  (`concept_ar`, `keywords`, and `concept_en` when the profile has translations).
- `rank_view(u)` = the best (smallest) rank of `u` among the view's active signals, where a signal's
  rank is the position of `u` in that signal's own ranking (units the signal gives no evidence to
  are unranked = ∞). Inactive signals (missing field or missing query part) are ignored.
- **Accept `u` iff `rank_text(u) ≤ k` and `rank_interp(u) ≤ k`; otherwise output NONE.**
  If the interpretation view has no active signal, output NONE.

`k` is selected from the grid **{1, 3, 5, 10}**, separately for each profile, on the calibration
split only:
1. For each `k`, compute accepted precision (definition below) on calibration.
2. Choose the `k` with the **highest coverage among those with accepted precision ≥ 0.85**; ties →
   smaller `k`.
3. If no `k` reaches 0.85, choose the `k` with the highest accepted precision; ties → smaller `k`.

The chosen `k` per profile is recorded in `K_SELECTION.json` before
the test split is run. The rule implementation will be committed and its commit hash recorded in
`RUN_LOG.md` **before** the calibration run.

## 4A. Amendment A1 (2026-10-11) — S2 contrastive decision

Added before any held-out item existed; see `DEVIATIONS.md` (D1). S1 above is unchanged and remains
the baseline mechanism. S2 targets near-neighbour confusion and is reported separately.

**Position.** S2 *augments* the registered decision call; it does not replace it. It runs after the
technical gate and the existing decision call, only when that call selected a unit `c*`.

**Competitor set (deterministic, schema-independent).**
- Similarity = cosine between the units' `dense_unit` E5 embeddings (the engine's unit
  representation: headword plus definition when the unit has one, headword alone otherwise).
- Competitors = the **3** units of the whole dictionary most similar to `c*`, excluding `c*`;
  ties broken by `unit_id`. Redirect handling is already done by the adapter.
- The contrast set `{c*} ∪ competitors` (4 units) is shown **sorted by `unit_id`**, so the position of
  `c*` carries no information.

**Candidate rendering.** Only roles the unit has, in this order; missing roles are omitted:
`المصطلح` (headword) · `أسماء أخرى` (up to 3 aliases) · `المقابل` (first translation) ·
`التعريف` (definition, first 40 words) · `مثال` (first example, first 25 words).

**Prompt (verbatim; system message).**

```
أمامك نص ومجموعة صغيرة من المفاهيم المتقاربة من معجم مصطلحات. هذه المفاهيم متشابهة عمدًا، والمطلوب التمييز بينها.
لكل مفهوم، حدّد ما يميّزه عن بقية المفاهيم في المجموعة، ثم ابحث في النص عن دليل على هذه الخاصية المميّزة تحديدًا.
اختر مفهومًا فقط إذا كان النص يحتوي على دليل يدعمه هو دون المفاهيم الأخرى في المجموعة.
إذا كان النص ينطبق على أكثر من مفهوم بالقدر نفسه، أو لا يذكر ما يميّز أيًّا منها، أو لا يعبّر عن أيٍّ منها، فاختر NONE.
أعد JSON فقط بالشكل: {"choice": "C2", "evidence": "عبارة منقولة حرفيًا من النص تدل على الخاصية المميّزة"} أو {"choice": "NONE", "evidence": ""}.
```

User message: `النص:\n<text>\n\nالمفاهيم:\n\n` followed by the rendered units `C1` … `C4`
separated by blank lines. Same model and settings as the rest of the pipeline (temperature 0,
thinking disabled), `max_tokens` = 150.

**Output rule (deterministic).** The S2 result is the chosen unit, or NONE if **any** of:
1. `choice` is `NONE`, missing, unparseable, or not one of `C1`–`C4`;
2. `evidence` is empty;
3. after normalization (diacritics removed, alef/ya/ta-marbuta unified, whitespace collapsed),
   `evidence` is **not** a substring of the user text;
4. normalized `evidence` is the entire normalized user text (it must be a proper part of it).

If S2 chooses a competitor rather than `c*`, the competitor is the output (S2 may correct a
near-neighbour error as well as abstain). No other post-processing; no further LLM call.

**No tunable parameter.** Competitor count (3), rendering limits and the rules above are fixed here;
nothing in S2 is selected on calibration data.

**Cost.** +1 call per query that reaches a selection (≈ 4 short candidates, expected ≈ 600–900
prompt tokens, ≈ 1 s). Queries stopped by the gate or with no selection incur no extra call.

**Behaviour by dictionary profile.** With headword + definition, units are contrasted on their
definitions. With richer metadata, aliases / translations / examples are added to each rendering,
giving more distinguishing text; nothing else changes. With headword only, the contrast relies on the
headwords and model knowledge; the evidence rules still apply, so weak cases fall to NONE.

**Freezing.** Before any run of S2 (including the development sanity check):
implement exactly this specification, commit, and record the commit hash in `RUN_LOG.md`.
The development sanity check on the old development data (dev36 / gold50 / probes) is run **once**;
its results are reported but **no change** to S2 is permitted afterwards. Any change creates a new
mechanism version that requires a new held-out set.

## 5. Comparisons (all on the same test split, same calls)
- **S1** (frozen rule, chosen `k`) — primary (as originally registered).
- **S2** (contrastive decision, A1) — primary for near-neighbour confusion, reported separately.
- **S1 + S2** (accept only if S2 outputs a unit that also passes S1 with the same `k`) — exploratory.
- **Baseline** — identical pipeline without S1/S2 (gate only).
Results are additionally broken down for `near_neighbour` and `ambiguous` items.

## 6. Metrics (implemented in `scripts/heldout_score.py`)
Per profile and split; overall and per item type:
correct, wrong, NONE, false specialization (FS), accepted precision = correct / (correct + wrong + FS),
accepted accuracy = correct / (correct + wrong), coverage = correct / positives,
FS rate = FS / negatives (also per negative type), abstention rate, and candidate availability
(an acceptable entry among the candidates shown to the final decision call; see §3).
95 % percentile bootstrap CIs, 10,000 item-level resamples, seed 20261013.
Annotator agreement (κ, preferred-in-set rate, Jaccard) reported with the results.

## 7. Success criteria (test split; evaluated for S1 and for S2 separately, each profile separately)
- **SC1** accepted precision ≥ 0.85 **and** its 95 % CI lower bound ≥ 0.75.
- **SC2** FS rate on all negatives ≤ 0.05.
- Coverage has no threshold; it is reported with the baseline's coverage and precision.

Interpretation fixed in advance (applied to each mechanism):
- SC1 and SC2 pass in both profiles → the mechanism is adopted as a default abstention rule.
- Pass in P-full only → adopt for dictionaries with translations; flag the Arabic-only path.
- Fail → report as a negative result. **No re-tuning on the test split.** Any new rule requires a
  new held-out set.
- If both S1 and S2 pass, prefer the one with higher test coverage; if within 0.03 coverage, prefer S1
  (no extra call).

## 8. Run protocol
1. Writers and annotators complete `items.json`; `validate` passes; `freeze`; `split`.
2. Implement S1 and S2 (S2 exactly per §4A); commit; record hash in `RUN_LOG.md`.
   (S2 is implemented and its single development sanity check is run before step 1 may finish;
   see §4A Freezing.)
3. Run calibration once per profile; select `k` for S1 automatically; write `K_SELECTION.json`; commit.
4. Run test once per profile (baseline, S1, S2, S1 + S2 from the same calls); score; commit predictions and scores.
5. Report everything, including failures, drops, skips and deviations.

The specialization system must not be run on any held-out item before step 1 is complete.

**Interim pilot (A3 / D3).** The 100 source-grounded positive drafts in `source_grounded_draft/`
are run once as an interim pilot (E8) before step 1. Because the system has then been run on them,
these 100 items are **pilot items and are excluded from the formal frozen test** unless a further
recorded amendment decides otherwise. E8 is not a test of the success criteria in §7.
