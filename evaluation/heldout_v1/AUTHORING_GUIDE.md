# Authoring guide — held-out evaluation set `heldout_v1`

**Who this is for:** Arabic-speaking domain experts in AI/data who will write the evaluation texts.
You do not need to know anything about the system being evaluated — and you must not look at any
of its outputs or experiment results.

## 1. What you are building and why

We are testing a component that reads a short Arabic text, decides whether it describes a specific
concept from the Siwar AI dictionary, and either names that concept's official Arabic term or
answers "none". Your texts are the **test**. They must look like what real users write — and they
must not give the answer away.

Each item is one short text (1–3 sentences, **8–45 words**) plus a label.

## 1A. Authoring method (Amendment A3)

Items are **source-grounded, LLM-drafted, human-validated**:

1. The target comes from `sampled_terms.json`.
2. The meaning of each item is grounded, where reasonably possible, in an **independent
   authoritative technical or scientific source** (official documentation, standards, textbooks,
   peer-reviewed papers). Record it in the item (`semantic_source`: organisation, title, URL).
3. The Arabic text may be **drafted or paraphrased with an LLM**. Record this in the item
   (`authoring_method`). It must be a new paraphrase: never copy the source.
4. Vary the writing context deliberately: formal technical/report writing; developer questions and
   issues; social / Saudi conversational technical writing; product, support and workplace writing.
   Record it in `style_profile`.
5. Public human writing (Reddit, GitHub Issues, Stack Overflow, forums, …) may be used **only as a
   style reference** (`style_reference`), never as the semantic source.
6. Every item, and its label, must be validated by humans (ANNOTATION_GUIDE.md) before the set can be
   frozen. LLM drafting must never be hidden.

## 2. Ground rules (apply to every item)

1. **Never look at system outputs**, experiment results, or anything in the `results/` folder.
   Use only: this guide, `sampled_terms.json` (your assignments), `dictionary_reference.csv`
   (the dictionary, for checking), independent authoritative sources for meaning, and public human
   writing for style only (§1A).
2. **Write naturally.** Imagine a student, engineer, analyst, or journalist writing or speaking
   about their work. Do not imitate dictionary definitions. If an LLM drafts the text, the human
   writer is responsible for every rule in this guide.
3. **For positive items, never write the term itself**, its aliases, its abbreviation, or its
   English equivalent — not even in English inside an Arabic sentence. Describe the concept; do not
   name it. (The validation script rejects items that contain them.)
4. **Do not copy the definition.** Paraphrase in your own words; at most 3 consecutive words may
   match the definition.
5. **One concept per positive item.** The text should be about that concept, not mention it in passing.
6. **No invented facts about the concept.** Ordinary context (a team, a project, a product) is fine.
7. **Register quota** (per writer, roughly): 50 % Modern Standard Arabic (`msa`), 30 % light Saudi
   colloquial (`saudi`), 20 % mixed Arabic with some English technical words (`mixed`) — but in
   `mixed` items never use the English name of the target concept.
8. Write each item in a fresh state of mind: do not reuse sentence templates across items.

## 3. Using the sampled lists (no cherry-picking)

`sampled_terms.json` contains pools of dictionary entries drawn at random (fixed seed). Use them
**in the listed order**. You may skip an entry **only** for one of these reasons, and you must
record it in `skip_log.csv` (`pool, unit_id, reason_code, comment`):

| Code | Allowed reason |
|---|---|
| S1 | Product / library / proper name (e.g. a software framework) — cannot be described without naming it |
| S2 | Definition is unclear, circular, or wrong, so the concept cannot be described reliably |
| S3 | (pairs only) The two entries are not genuinely related concepts |
| S4 | (everyday pool only) The headword has no natural general-language meaning |
| S5 | Concept is essentially identical to another entry already used |

When you skip, take the next entry from that pool's `reserve` list, again in order.

## 4. Item types

The examples below use terms that are **not** in the held-out pools, only to illustrate style.

### 4.1 `plain_positive` — 120 items (pool `plain_positive`)
Describe the concept's **essential features** (what makes it this concept and not a neighbour)
in natural language.

- Good (target فرط التخصيص): «المودل ممتاز على البيانات اللي تدرب عليها، لكن أول ما نجربه على
  بيانات جديدة يطيح أداؤه.»
- Too vague (reject): «المودل ما يتعلم زين.» — does not state the defining features.
- Gives it away (reject): «عندنا مشكلة فرط تخصيص في المودل.» — names the term.

Label: `TERM`, `acceptable_unit_ids` = the sampled entry (plus any other entry the annotator also
accepts — see the annotation guide), `preferred_unit_id` = the sampled entry.

### 4.2 `near_neighbour` — 40 items (pool `near_neighbour_pairs`, 20 pairs)
Each pair (`a`, `b`) contains two **related but distinct** concepts. Write **two texts**, one for
`a` and one for `b`. Each text must include the feature that **distinguishes** its concept from the
other one, so that an expert would pick exactly one of them.

- Illustration (pair: متوسط الخطأ التربيعي / متوسط الخطأ المطلق): text for the first should mention
  squaring the differences; text for the second should mention absolute differences.

Label: `TERM`, `acceptable_unit_ids` = only the intended entry.

### 4.3 `ambiguous` — 30 items (pool `ambiguous_pairs`, one item per pair)
Write **one text** that genuinely fits **both** entries of the pair — describe what they share
without the feature that would separate them. If you cannot write such a text honestly, skip with
reason S3.

Label: `TERM`, `acceptable_unit_ids` = both entries, `preferred_unit_id` = the one you consider more natural.

### 4.4 `everyday_negative` — 50 items (pool `everyday_candidates`)
Use the headword (or a natural inflection of it, e.g. with ال) in its **general, non-AI meaning**,
in an ordinary sentence. Skip with S4 if the word has no natural general meaning.

- Illustration (headword دورة): «حضرت دورة تدريبية لمدة يومين عن إدارة المشاريع.»
- Illustration (headword سياسة): «سياسة الشركة تمنع مشاركة ملفات العملاء خارج الفريق.»
- Not acceptable: a sentence where the AI meaning is plausible.

Label: `NONE`; `source_unit_ids` = the headword's entry.

### 4.5 `vague_negative` — 50 items (no pool)
Texts in an AI/data context that **do not identify any specific concept**. Aim for 10 of each:

1. Vague complaints («النتائج اليوم مو مثل أمس.»)
2. Vague goals or plans («نبي نطور النظام قبل الإطلاق.»)
3. Process / project talk («اجتمعنا مع الفريق التقني وناقشنا الخطوات الجاية.»)
4. Opinions or evaluations («أشوف إن أداة الذكاء الاصطناعي هذي مفيدة بشكل عام.»)
5. Logistics / deployment / cost («نحتاج ميزانية إضافية للخوادم هذا الربع.»)

If, after writing, you realise the text actually describes a dictionary concept, discard it and
write another. Label: `NONE`; `source_unit_ids` = `[]`.

## 5. Self-check before handing in an item
- [ ] 8–45 words, natural, register tag correct.
- [ ] Positive: no term / alias / abbreviation / English name; not a definition paraphrase.
- [ ] Positive: an expert could identify the concept from the text alone.
- [ ] Near-neighbour: the distinguishing feature is present.
- [ ] Ambiguous: both concepts genuinely fit.
- [ ] Everyday: the general meaning is the only reasonable reading.
- [ ] Vague: no specific concept is identifiable.

## 6. Hand-in
Fill `items.json` following `items_template.json` (item ids: `PP-`, `NN-`, `AM-`, `EN-`, `VN-`
+ three digits). Leave `annotator_*` fields for the annotator. Hand in `skip_log.csv` too.
Also include, per item, the provenance fields of §1A: `semantic_source`, `style_profile`,
`style_reference` (if any) and `authoring_method`.
