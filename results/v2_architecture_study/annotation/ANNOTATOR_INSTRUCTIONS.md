# Annotation instructions (blinded)

You are annotating Arabic rewrites produced by different (hidden) system variants.
Each item has: `original` (user text), `rewrite` (system output), and optionally
`term` + `term_definition` (a Siwar AI-dictionary term the system tried to introduce).
You do not know which system produced an item. Judge each item on its own.

For every item return one JSON object with these fields:

- `blind_id`: copy from the item.
- `concept_correct`: only if `term` is not null. Does the term (per its Siwar definition)
  accurately name the concept the ORIGINAL text expresses?
  `yes` | `partial` (related but broader/narrower/imprecise, or a near-synonym entry) | `no`.
  Use `null` when `term` is null.
- `term_in_output`: only if `term` is not null: does the rewrite use the term (allow ال / inflection)? `yes` | `no` | `null`.
- `term_natural`: only if term_in_output = yes: integrated as natural specialist prose? `yes` | `no` | `null`.
- `meaning_preserved`: 2 = all information kept; 1 = minor loss/shift; 0 = meaning changed or important info lost.
- `unsupported_addition`: `none` | `minor` (small embellishment) | `major` (new fact, capability,
  cause, certainty, or definition content not in the original).
- `fluency`: integer 1-5 (natural, correct MSA a specialist would write).
- `dictionary_style`: `yes` if the rewrite gratuitously defines/explains the term
  (e.g. "يُعرّف بأنه", "وهو ما يُعرف بـ") instead of just using it.
- `instruction_leak`: `yes` if it mentions the pipeline (approved term, verification, "النص الأصلي", etc.).
- `false_specialization`: `yes` if the rewrite turns an everyday/general meaning into an AI-technical
  meaning, or adds AI technicality the original does not support; else `no`.
- `note`: optional, at most 15 words, only for `no`/`major`/0 judgements.

Be strict and consistent. A rewrite that is simply a faithful, fluent paraphrase with no term is fine
(meaning 2, none, fluency per quality). Do not reward terminology for its own sake: a wrong or forced
term is worse than no term.
