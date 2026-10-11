# Deviations from PREREGISTRATION.md

## D1 — 2026-10-11 — Amendment A1: add S2 contrastive decision

- **When:** before any held-out item existed (`items.json` absent; nothing written, labelled,
  frozen or split). No system has been run on held-out data.
- **What changed:** added §4A (S2 contrastive decision) and updated §5 (comparisons), §7 (success
  criteria now evaluated for S1 and S2 separately; tie-break between them) and §8 (run protocol).
- **What did not change:** the S1 rule, its `k` grid and selection procedure, data, sampling, split,
  metrics, success thresholds, and the frozen pipeline in §3.
- **Why:** development diagnostic E6 (`v3-retrieval-study`, commit 8f0e6f3,
  `results/v3_retrieval_study/e6_corroboration_dev.json`) showed that S1 eliminates false
  specialization on development negatives but barely raises precision (P-full 0.61 → 0.69–0.71,
  P-def 0.65 → 0.67–0.73), because the dominant remaining error is near-neighbour confusion that both
  retrieval views share. S1 cannot address this by construction, so a second mechanism aimed at it
  is registered.
- **Safeguards (D1):** S2 has no tunable parameter; its prompt and rules are fixed verbatim in §4A; it
  will be implemented exactly as written, its commit recorded in `RUN_LOG.md`, and run once on
  development data as a sanity check with no changes allowed afterwards.

## D2 — 2026-10-11 — Amendment A2: registered P-def decision pipeline

- **When:** before any held-out item existed (`items.json` absent). Based only on development evidence.
- **What changed:** §3 now registers a different decision pipeline per profile:
  - **P-def**: first-stage retrieval → Qwen listwise reranker (top-50) → selector over the reranked top-10.
  - **P-full**: unchanged — first-stage retrieval → one-call decision over the top-30.
  Consequential wording fix in §6: candidate availability refers to the candidates shown to the
  final decision call (30 in P-full, 10 in P-def) instead of "the 30 candidates".
- **What did not change:** S1 (rule, `k` grid, selection procedure), S2 (§4A, verbatim), data,
  sampling, split, metrics, success criteria, and every other part of §3.
- **Why:** development evidence from E5 (`results/v3_retrieval_study/e5_decision_*.json`) and E6
  (`e6_corroboration_dev.json`) showed that for Arabic-only / P-def retrieval the reranker + selector
  pipeline materially outperformed the one-call design (pooled 51 correct / 28 wrong vs 44 / 35;
  correct entry available to the decision in 69 vs 68 of 80 positives), whereas for P-full the extra
  reranker call was not justified (49 / 30 vs 48 / 31 for the one-call design, at about one third of
  the decision latency).

## D3 — 2026-10-11 — Amendment A3: source-grounded, LLM-drafted, human-validated authoring; interim pilot E8

- **When:** before the formal held-out set is frozen (`items.json` absent; no labels frozen; no split).
- **Approved by:** the project owner.
- **What changed:**
  - Authoring method (§2, AUTHORING_GUIDE / ANNOTATION_GUIDE in English and Arabic): no longer
    "human-authored from scratch" but **source-grounded, LLM-drafted, human-validated**. Targets still
    come from `sampled_terms.json`; meaning is grounded in an independent authoritative source where
    reasonably possible; the Arabic text may be LLM-drafted/paraphrased, must not copy the source and
    must not leak the headword/alias/abbreviation/English equivalent; writing contexts vary (formal
    technical/report, developer questions/issues, social/Saudi, product/support); public human writing
    is a style reference only; LLM drafting and provenance are recorded per item; gold labels still
    need human validation before freezing.
  - §8: a 100-item source-grounded positive draft (`source_grounded_draft/`) is run once as an
    **interim pilot (E8)** before freezing. These items are thereafter **excluded from the formal
    frozen test** unless a further amendment decides otherwise, because §8 forbids running the system
    on formal held-out items before freezing.
- **What did not change:** S1, S2 (§4A), the registered P-full and P-def pipelines (§3, D2), metrics,
  success criteria (§7), split procedure, sampled pools, and E1–E7.
- **Observations about the draft recorded here for transparency:**
  - All 100 targets come from the `plain_positive` primary pool (none from the excluded development
    terms; independently re-checked: valid ids, no duplicates, no headword/alias/abbreviation/English
    leakage, all with a source URL).
  - The 100 were **selected from the 120 primary entries** "avoiding niche/unclear entries", not taken
    in listed order with logged skip reasons (AUTHORING_GUIDE §3). The 20 unused entries include some
    niche ones but also ordinary concepts (e.g. تعرُّف على الأنماط, نموذج فضاء الحالة, واحد مقابل الكل),
    so the pilot may over-represent well-known concepts and give optimistic results.
  - The draft contains positive items only; no new negatives, near-neighbour or ambiguous items, and no
    independent blind gold annotation yet. E8 therefore cannot report a false-specialization rate and
    cannot assess §7.
- **Consequence for the formal set:** the formal plain-positive items must come from the remaining
  `plain_positive` entries (20 primary + 60 reserve) in listed order with logged skips, or from a new
  documented sample if more are needed.
