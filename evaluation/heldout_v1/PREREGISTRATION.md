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
- `heldout_v1`: about 290 items written by human domain experts (see AUTHORING_GUIDE.md),
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
- Decision: one call over the first-stage top-30 (`decision.JOINT_SYSTEM`).
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

## 5. Comparisons (all on the same test split, same calls)
- **S1** (frozen rule, chosen `k`) — primary.
- **Baseline** — identical pipeline without S1 (gate only).

## 6. Metrics (implemented in `scripts/heldout_score.py`)
Per profile and split; overall and per item type:
correct, wrong, NONE, false specialization (FS), accepted precision = correct / (correct + wrong + FS),
accepted accuracy = correct / (correct + wrong), coverage = correct / positives,
FS rate = FS / negatives (also per negative type), abstention rate, and candidate availability
(an acceptable entry among the 30 candidates shown to the decision call).
95 % percentile bootstrap CIs, 10,000 item-level resamples, seed 20261013.
Annotator agreement (κ, preferred-in-set rate, Jaccard) reported with the results.

## 7. Success criteria (test split, S1, each profile separately)
- **SC1** accepted precision ≥ 0.85 **and** its 95 % CI lower bound ≥ 0.75.
- **SC2** FS rate on all negatives ≤ 0.05.
- Coverage has no threshold; it is reported with the baseline's coverage and precision.

Interpretation fixed in advance:
- SC1 and SC2 pass in both profiles → adopt S1 as the default abstention rule.
- Pass in P-full only → adopt S1 for dictionaries with translations; flag the Arabic-only path.
- Fail → report as a negative result. **No re-tuning on the test split.** Any new rule requires a
  new held-out set.

## 8. Run protocol
1. Writers and annotators complete `items.json`; `validate` passes; `freeze`; `split`.
2. Implement S1; commit; record hash in `RUN_LOG.md`.
3. Run calibration once per profile; select `k` automatically; write `K_SELECTION.json`; commit.
4. Run test once per profile (S1 and baseline from the same calls); score; commit predictions and scores.
5. Report everything, including failures, drops, skips and deviations.

The specialization system must not be run on any held-out item before step 1 is complete.
