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
