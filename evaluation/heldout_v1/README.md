# heldout_v1 — held-out evaluation framework

Status: **framework only — no evaluation texts exist yet.** Texts and labels are written and reviewed
by human domain experts. The specialization system must not be run on any item before the labels
are frozen.

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
