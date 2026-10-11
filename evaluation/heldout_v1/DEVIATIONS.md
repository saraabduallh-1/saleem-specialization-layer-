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
- **Safeguards:** S2 has no tunable parameter; its prompt and rules are fixed verbatim in §4A; it
  will be implemented exactly as written, its commit recorded in `RUN_LOG.md`, and run once on
  development data as a sanity check with no changes allowed afterwards.
