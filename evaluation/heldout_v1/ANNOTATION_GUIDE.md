# Annotation guide — held-out evaluation set `heldout_v1`

**Who this is for:** a second domain expert who did **not** write the item. Like the writers, you
must not look at any system outputs or the `results/` folder.

## 1. Two passes

### Pass 1 — independent labelling (author's label hidden)
You receive each item's `text` and `item_type` only (a copy of `items.json` with `label`,
`acceptable_unit_ids`, `preferred_unit_id` and `source_unit_ids` removed). For each item decide:

1. **Does the text express one specific dictionary concept?** → `TERM` or `NONE`.
2. If `TERM`: search `dictionary_reference.csv` and list **every entry an expert would accept as a
   correct technical name for what the text expresses** (`acceptable_unit_ids`), and choose the most
   natural one (`preferred_unit_id`).

Rules for the acceptable set:
- Include an entry if its definition covers what the text describes **without adding features the
  text does not support**.
- Do **not** include a broader field or umbrella term when a more specific entry fits
  (e.g. not «تعلُّم الآلة» when the text clearly describes «تعلُّم موجَّه»).
- Do **not** include an entry whose distinguishing feature contradicts or is absent from the text.
- An entry may come from anywhere in the dictionary, not only the sampled lists.

### Pass 2 — reconciliation
Compare your pass-1 label with the author's. Set:
- `annotator_agreed = true` if both say `NONE`, or both say `TERM` and the **acceptable sets
  overlap in the author's preferred entry**.
- Otherwise discuss with the author; record the final label, set `adjudicated = true`, and write the
  reason in `notes`. If no agreement is reached, a third expert decides; if the item is still
  disputed, **drop it** and log it in `dropped_items.csv` (`item_id, reason`).

## 2. Quality checks (reject and return to the author if any fails)
- Positive item contains the term, an alias, the abbreviation, or the English name.
- Positive item is too vague to identify the concept, or copies the definition.
- Near-neighbour item lacks its distinguishing feature, or fits both entries.
- Ambiguous item does not genuinely fit both entries.
- Everyday negative admits an AI reading; vague negative identifies a specific concept.
- Register tag or word count (8–45) wrong; unnatural Arabic.

## 3. Agreement to report (computed after pass 1, before reconciliation)
- Cohen's κ on TERM vs NONE.
- For items both labelled TERM: share where the author's preferred entry is in the annotator's
  acceptable set, and mean Jaccard overlap of acceptable sets.

These are reported alongside the results; low agreement on a type is itself a finding.

## 4. Freezing
After reconciliation, run:

```
python3 scripts/heldout_freeze_split.py validate
python3 scripts/heldout_freeze_split.py freeze --by "<name>"
python3 scripts/heldout_freeze_split.py split
```

After `freeze`, `items.json` must never change. Any later correction requires a new dataset
version (`heldout_v2`).
