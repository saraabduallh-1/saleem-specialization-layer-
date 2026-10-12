# Run log — heldout_v1

| Date (UTC) | Event | Commit |
|---|---|---|
| 2026-10-11 | S2 implemented exactly per §4A (`specialization_layer/contrastive.py`); prompt verified identical to §4A; S1 implementation `specialization_layer/abstention.py` (from v3 E6) | `3490f269ac954eef2daed2990ecf2b9fcc1559f5` |
| 2026-10-11 | Single S2 development sanity check (E7) on dev36 / gold50 / probes with the registered pipelines (§3, D2); decisions reused from E5 (P-full system C, P-def system B). Result: S2 lowers precision and coverage on development data (see `results/v3_retrieval_study/e7_s2_dev_sanity.json`). Per §4A, S2 is not modified. | `3490f269ac954eef2daed2990ecf2b9fcc1559f5` (code) |
| 2026-10-12 | E9/S3 development follow-up prepared after E8 error analysis: text-centered contrastive decision over first-stage top-10 plus the E8 baseline nomination, with rank hidden. This is explicitly tuning/development on exposed E8 pilot items and is not held-out evidence. Frozen E1-E8 results remain unchanged. | `67336fd5c0389037c3b384a5b012993c765931c2` (runner) |
