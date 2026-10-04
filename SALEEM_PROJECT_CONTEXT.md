# Saleem Specialization Layer — Project Context

## Project Goal
Build a lightweight specialization layer for the Arabic writing system **Saleem**.

The layer does not replace Saleem and does not train a new writing model from scratch.

Its job is to provide Saleem with:
1. the most relevant specialized terminology and lexical knowledge for the input text;
2. later, examples of domain-specific writing style;
3. enough context to help Saleem rewrite the text in a specialized way while preserving meaning.

Keep the design simple. Do not add architectural complexity unless there is a clear, measurable research benefit.

## Main Research Question
Does adding retrieved domain-specific lexical knowledge improve Saleem's specialized Arabic writing compared with using Saleem alone?

## Part A — Terminology Retrieval
Input text → embedding/retrieval model → relevant terminology from the domain lexicon.

Models planned for comparison:
- `intfloat/multilingual-e5-large`
- `BAAI/bge-m3`
- `Qwen/Qwen3-Embedding-0.6B`

E5 is treated as the previous-work baseline because prior Arabic lexical-retrieval work on Riyadh Dictionary data reported strong E5 performance. The other two models are modern comparison baselines.

## Part B — Specialized Writing
Original text + retrieved terminology/definitions/context → Saleem → specialized rewritten text.

Saleem remains the writing model unless experiments show a clear need for something else.

## First Domain and Source
First domain: **Data & Artificial Intelligence**

Primary source:
**Siwar — Data and Artificial Intelligence Dictionary**

Original file:
`data/raw/data_ai/siwar_data_ai_dictionary.json`

The raw source must never be edited.

## Repository Structure
```text
saleem-specialization-layer/
│
├── data/
│   ├── raw/
│   │   └── data_ai/
│   │       └── siwar_data_ai_dictionary.json
│   ├── processed/
│   │   └── data_ai/
│   │       ├── terminology_base.json
│   │       └── terminology_enriched.json
│   └── gold_test/
├── scripts/
│   ├── prepare_terminology.py
│   └── enrich_terminology.py
├── results/
└── README.md
```

## Current Base Terminology Schema
```json
{
  "id": "",
  "source": "siwar",
  "source_dictionary": "data_ai",
  "domain": "data_ai",
  "term": "",
  "lemma_type": "",
  "pos": null,
  "definition": "",
  "english_term": "",
  "abbreviations": [],
  "aliases": [],
  "canonical_term": null,
  "canonical_term_id": null,
  "variants": [],
  "positive_examples": [],
  "negative_examples": []
}
```

The preprocessing:
- keeps the original Siwar ID;
- keeps the official Arabic term and definition;
- extracts the English equivalent when available;
- extracts abbreviations written in the English equivalent;
- extracts aliases explicitly stated in the source definition;
- detects entries that say `انظر "..."` and stores the referenced canonical term;
- does not generate new lexical content.

## Pilot Strategy
Do not enrich all 1,443 Arabic entries initially.

Start with a **50-term pilot** only.

The 50 terms should intentionally include:
- ambiguous Arabic words that may have a general-language meaning and a technical AI/data meaning;
- clear technical multi-word terms;
- terms with abbreviations or aliases.

The pilot is a feasibility sample, not claimed to be statistically representative of the full dictionary.

## Enrichment Rules
Priority: minimize synthetic data.

For each selected term, add only useful evidence-backed information.

### Positive usage examples
Prefer real Arabic sentences from:
- official reports;
- standards;
- authoritative technical publications;
- peer-reviewed papers.

Store:
- text
- source_title
- source_type
- year
- page_or_section
- url_or_doi

### Negative/context-disambiguation examples
Only for ambiguous terms where there is a realistic competing sense.

A negative example means the same surface word appears, but with another meaning, so the technical lexicon entry should not be selected.

Prefer real examples from reliable sources.

### Variants
Use only attested or source-supported variants:
- official abbreviation;
- explicit alias;
- documented transliteration;
- documented spelling variant.

Do not invent variants only to populate the field.

## Specialized Writing Dataset — Separate Dataset
Do not mix terminology entries with writing-style examples.

A second dataset will later contain authentic Arabic domain-writing examples such as:
- technical report paragraph;
- model explanation;
- algorithm comparison;
- concept definition;
- methodology paragraph;
- research-results paragraph;
- analytical discussion paragraph.

Purpose:
- terminology dataset answers: **what terminology should be used?**
- writing-style dataset helps Saleem with: **how specialists write in the domain**

## Gold Test Set
The Gold Test Set must be independent from the enrichment examples.

Do not reuse positive examples from the terminology dataset as test queries.

Use the same Gold Test Set to compare:
- E5
- BGE-M3
- Qwen3-Embedding-0.6B

Possible retrieval metrics:
- Hit/Recall@1
- Hit/Recall@3
- Hit/Recall@5
- MRR

Final writing experiment:
1. Saleem alone
2. Saleem + retrieved specialized knowledge

Evaluation dimensions:
- terminology accuracy
- contextual appropriateness
- meaning preservation
- quality of specialized style

## Research Discipline
Every methodological choice that appears in the paper must be:
1. supported by a scientific reference; or
2. explicitly described as an engineering choice; or
3. explicitly described as an experiment/hypothesis.

For every research recommendation, provide:
- rationale;
- supporting academic source;
- exactly what the source supports;
- what remains a project-specific decision.

Prefer peer-reviewed papers, official benchmark/model documentation, and authoritative Arabic-language sources.

## Simplicity Rule
Do not propose:
- extra models;
- rerankers;
- fine-tuning;
- vector databases;
- complex morphological pipelines;
- knowledge graphs;
- extra infrastructure

unless there is a clear experimental failure showing they are needed and the expected benefit justifies the added complexity.

Default architecture:

**Input text → terminology retriever → retrieved lexical knowledge → Saleem → specialized output**

Future domains should be added mainly by adding new lexicon/style data using the same schema, not by redesigning the system.
