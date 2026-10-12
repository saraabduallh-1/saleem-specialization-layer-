# E9 — Text-centered contrastive decision (S3)

> **Development only.** S3 was designed after E8 error analysis and E9 reuses the E8 100 items.
> These numbers are not held-out evidence and must not be used for the final success criteria.

## Results

| Profile | Setting | Correct | Wrong | NONE | Precision | Coverage |
|---|---|---:|---:|---:|---:|---:|
| P-full | baseline_E8 | 67 | 33 | 0 | 0.67 | 0.67 |
| P-full | S3 | 70 | 27 | 3 | 0.722 | 0.7 |
| P-full | S3+S1@k=1 | 30 | 4 | 66 | 0.882 | 0.3 |
| P-full | S3+S1@k=3 | 54 | 8 | 38 | 0.871 | 0.54 |
| P-full | S3+S1@k=5 | 59 | 12 | 29 | 0.831 | 0.59 |
| P-full | S3+S1@k=10 | 62 | 15 | 23 | 0.805 | 0.62 |
| P-def | baseline_E8 | 67 | 33 | 0 | 0.67 | 0.67 |
| P-def | S3 | 68 | 26 | 6 | 0.723 | 0.68 |
| P-def | S3+S1@k=1 | 24 | 2 | 74 | 0.923 | 0.24 |
| P-def | S3+S1@k=3 | 50 | 6 | 44 | 0.893 | 0.5 |
| P-def | S3+S1@k=5 | 53 | 10 | 37 | 0.841 | 0.53 |
| P-def | S3+S1@k=10 | 55 | 16 | 29 | 0.775 | 0.55 |

## Transition summary

- **P-full:** corrected wrong=10, correct→wrong=5, correct→NONE=2, wrong→NONE=1; gold present in S3 pool=88/100.
- **P-def:** corrected wrong=11, correct→wrong=6, correct→NONE=4, wrong→NONE=2; gold present in S3 pool=89/100.

## Interpretation guardrail

If S3 looks better here, treat that as a development signal only. The mechanism was created from E8's observed errors. A new untouched held-out set is required after architecture freeze.
