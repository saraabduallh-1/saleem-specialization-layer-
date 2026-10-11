# heldout_v1 — held-out evaluation framework

Status: **framework only — no formal evaluation items exist yet.** Items are source-grounded,
LLM-drafted and human-validated (Amendment A3, `DEVIATIONS.md` D3); labels are validated by human
domain experts. The specialization system must not be run on any formal item before the labels are
frozen. `source_grounded_draft/` holds a 100-item positive draft used only as the interim pilot E8;
those items are excluded from the formal test (D3).

| File | Purpose |
|---|---|
| `PREREGISTRATION.md` | Frozen question, rule, k-selection procedure, metrics, success criteria, run protocol |
| `sampled_terms.json` | Seeded (20261011) term pools; excludes every development term |
| `AUTHORING_GUIDE.md` | Instructions for writers |
| `ANNOTATION_GUIDE.md` | Instructions for the second annotator, reconciliation, freezing |
| `items_template.json` | Item schema with placeholders (not items) |
| `dictionary_reference.csv` | Read-only dictionary view (headword, English, aliases, abbreviations, definition) |
| `skip_log.csv`, `dropped_items.csv` | Logs to be filled by writers / annotators |

Scripts:
- `scripts/heldout_sample_terms.py` — regenerates `sampled_terms.json` (byte-identical).
- `scripts/heldout_freeze_split.py` — `reference`, `validate`, `freeze`, `split`.
- `scripts/heldout_score.py` — frozen metrics and success criteria (`--selftest` for a synthetic check).

Workflow: write → annotate (pass 1 blind, pass 2 reconcile) → `validate` → `freeze` → `split` →
implement S1 and record commit → calibration run → `K_SELECTION.json` → single test run → score → report.
