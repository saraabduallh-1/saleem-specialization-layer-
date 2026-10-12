# E10 — Protected contrastive decision (S4)

> **Development only.** S4 was designed after inspecting E8 and E9.
> These numbers are not held-out evidence and must not be used for final success criteria.

## Mechanism

S4 protects the E8 baseline. A challenger may replace it only when the model says the baseline is not EXACT, the challenger is EXACT, the case is unambiguous, and a short evidence span is verified against the input text.
The candidate pool is widened to first-stage Top-30 plus the baseline, with retrieval rank hidden.

## Results

| Profile | Setting | Correct | Wrong | NONE | Precision | Coverage |
|---|---|---:|---:|---:|---:|---:|
| P-full | baseline_E8 | 67 | 33 | 0 | 0.67 | 0.67 |
| P-full | S4 | 68 | 32 | 0 | 0.68 | 0.68 |
| P-full | S3_E9_reference | 70 | 27 | 3 | 0.722 | 0.7 |
| P-full | S4+S1@k=1 | 30 | 3 | 67 | 0.909 | 0.3 |
| P-full | S4+S1@k=3 | 52 | 5 | 43 | 0.912 | 0.52 |
| P-full | S4+S1@k=5 | 57 | 10 | 33 | 0.851 | 0.57 |
| P-full | S4+S1@k=10 | 61 | 15 | 24 | 0.803 | 0.61 |
| P-def | baseline_E8 | 67 | 33 | 0 | 0.67 | 0.67 |
| P-def | S4 | 67 | 33 | 0 | 0.67 | 0.67 |
| P-def | S3_E9_reference | 68 | 26 | 6 | 0.723 | 0.68 |
| P-def | S4+S1@k=1 | 28 | 1 | 71 | 0.966 | 0.28 |
| P-def | S4+S1@k=3 | 49 | 7 | 44 | 0.875 | 0.49 |
| P-def | S4+S1@k=5 | 51 | 10 | 39 | 0.836 | 0.51 |
| P-def | S4+S1@k=10 | 55 | 17 | 28 | 0.764 | 0.55 |

## Protection summary

- **P-full:** corrected wrong=2, correct→wrong=1, correct→NONE=0, wrong→NONE=0; gold present in S4 pool=93/100; resolutions={'keep_baseline': 96, 'validated_change': 4}.
- **P-def:** corrected wrong=0, correct→wrong=0, correct→NONE=0, wrong→NONE=0; gold present in S4 pool=95/100; resolutions={'keep_baseline': 99, 'blocked_change_keep_baseline': 1}.

## Interpretation guardrail

Even if S4 improves on E8/E9, treat it only as a development signal because the mechanism was created from those observed errors. Freeze the architecture before evaluating on a fresh untouched held-out set.
