# Error analysis — E5 48-term ablation

Source: `results/retrieval_e5_48_ablation.json` (intfloat/multilingual-e5-large, 48 queries). Descriptive analysis of stored results; no model was re-run. Manual categorisations are exploratory and marked as such.

Excluded entries (no valid independent usage example): حُزمة (terminological_mismatch); بث (source_scarcity).

## 1. Overall results

| Metric | Term only | Term + definition | Term + definition + example |
|---|---:|---:|---:|
| top1_accuracy | 0.250 | 0.500 | 0.458 |
| top3_accuracy | 0.438 | 0.750 | 0.688 |
| top5_accuracy | 0.583 | 0.833 | 0.792 |
| mrr | 0.394 | 0.637 | 0.614 |

## 2. Outcome groups (definition → definition + example)

| Group | n | % |
|---|---:|---:|
| improved_with_example | 11 | 22.9 |
| unchanged_with_example | 24 | 50.0 |
| worsened_with_example | 13 | 27.1 |

| Top-1 status | n | % |
|---|---:|---:|
| dropped_from_top1 | 4 | 8.3 |
| newly_reached_top1 | 2 | 4.2 |
| remained_correct_top1 | 20 | 41.7 |
| remained_incorrect | 22 | 45.8 |

## 3. Worsened queries and error categories (manual, exploratory)

| Query | Term | Style | Rank B → C | Top-1 under C | Categories |
|---|---|---|---|---|---|
| GOLD_022 | تعلُّم عميق | msa | 1 → 4 | شبكة عصبية تكرارية | competing_terminology, example_definition_mismatch, source_domain_style_effect |
| GOLD_024 | تعلُّم غير موجَّه | msa | 1 → 2 | تنقيب في البيانات | query_ambiguity |
| GOLD_025 | فرط التخصيص | saudi_colloquial | 3 → 6 | مُولِّد | lexical_mismatch_or_synonym, neighbor_attraction |
| GOLD_028 | ذكاء اصطناعي توليدي | msa | 1 → 3 | اسم | example_definition_mismatch, source_domain_style_effect, neighbor_attraction |
| GOLD_032 | ترجمة الآلة | msa | 1 → 2 | معالجة اللغات الطبيعية | general_example_language |
| GOLD_033 | شجرة القرار | msa | 5 → 8 | اسم | competing_terminology, example_definition_mismatch, source_domain_style_effect |
| GOLD_037 | تعلُّم الآلة | saudi_colloquial | 15 → 28 | تعلُّم موجَّه | semantically_broad_target_term, example_definition_mismatch, source_domain_style_effect |
| GOLD_040 | شبكة عصبية اصطناعية | msa | 34 → 35 | سياسة | semantically_broad_target_term, no_clear_cause |
| GOLD_041 | شبكة عصبية ترشيحية | arabic_english_mixed | 9 → 11 | اسم | lexical_mismatch_or_synonym |
| GOLD_042 | شبكة عصبية تكرارية | msa | 2 → 4 | مُحوِّل | query_ambiguity, neighbor_attraction |
| GOLD_044 | آلة المُتَّجهات الداعمة | msa | 3 → 4 | مُولِّد | source_domain_style_effect |
| GOLD_049 | رؤية الحاسب | saudi_colloquial | 3 → 6 | تعرُّف على الكيانات المُسمّاة | general_example_language, competing_terminology, example_definition_mismatch, lexical_mismatch_or_synonym |
| GOLD_050 | دالة الخسارة | saudi_colloquial | 2 → 7 | مُولِّد | query_ambiguity |

Category counts (a query can have several): general_example_language 2, competing_terminology 3, semantically_broad_target_term 2, example_definition_mismatch 5, lexical_mismatch_or_synonym 3, query_ambiguity 3, neighbor_attraction 3, source_domain_style_effect 5, no_clear_cause 1.

- **GOLD_022 تعلُّم عميق**: The example is mainly about deepfakes (another pilot term, تزييف عميق) and its social/media spread; التعلم العميق is mentioned once as a contributing factor, not described.
- **GOLD_024 تعلُّم غير موجَّه**: Query (finding patterns/groupings in unlabelled data) also fits تنقيب في البيانات; drop is 1->2 with a small score margin (0.795 vs 0.791).
- **GOLD_025 فرط التخصيص**: The example uses the translator's term «فرط الاستعداد», not فرط التخصيص; مُولِّد (whose example discusses training instability and output quality) moves to Top-1.
- **GOLD_028 ذكاء اصطناعي توليدي**: The example discusses generative AI's implications for open science and plagiarism, not content generation; اسم (example: «إنشاء ... نموذج») and مُولِّد rise above the target.
- **GOLD_032 ترجمة الآلة**: Long example listing statistical and neural approaches and 'deep neural networks'; the broader neighbour معالجة اللغات الطبيعية overtakes the target by a small margin.
- **GOLD_033 شجرة القرار**: The example is a banking-sector finding that pairs decision trees with logistic regression; it does not describe branching on features, which is what the query describes.
- **GOLD_037 تعلُّم الآلة**: Broad target term; the example is about machine learning in cybersecurity threat detection, while the query describes generic learn-from-examples-then-predict.
- **GOLD_040 شبكة عصبية اصطناعية**: Already a failure under B (rank 34) and C (35); a one-place change on a broad term is not attributable to the example.
- **GOLD_041 شبكة عصبية ترشيحية**: The example uses «الشبكة العصبية الالتفافية» rather than the Siwar term «ترشيحية»; small change (9->11) on an already-missed mixed-language query.
- **GOLD_042 شبكة عصبية تكرارية**: The query (sequential processing with a carried state) also fits مُحوِّل and LSTM; مُحوِّل, whose example mentions «تسلسل محدد», moves to Top-1.
- **GOLD_044 آلة المُتَّجهات الداعمة**: Long example about forecasting gold prices with SVM model comparison; it does not mention margins or support vectors' role, which the query describes.
- **GOLD_049 رؤية الحاسب**: Multi-topic example (sports media, big-data analysis, prediction systems) that mentions «رؤية الحاسوب» only as one tool; it also names بيانات ضخمة (as «البيانات الكبيرة»).
- **GOLD_050 دالة الخسارة**: The query (a number measuring distance from the correct value, used to adjust the model) also fits متوسط الخطأ التربيعي, which rises to rank 2; مُولِّد is Top-1 under both B and C.

## 4. Attraction analysis

Incorrect Top-1 occurrences per term (terms with any change between conditions):

| Term | Incorrect Top-1 (definition) | Incorrect Top-1 (definition + example) | Change |
|---|---:|---:|---:|
| اسم | 2 | 5 | +3 |
| مُحوِّل | 0 | 3 | +3 |
| مُولِّد | 1 | 4 | +3 |
| تعلُّم موجَّه | 0 | 2 | +2 |
| سياسة | 0 | 2 | +2 |
| آلة المُتَّجهات الداعمة | 0 | 1 | +1 |
| انتشار عكسي | 0 | 1 | +1 |
| تنقيب في البيانات | 0 | 1 | +1 |
| معالجة اللغات الطبيعية | 0 | 1 | +1 |
| تحليل المشاعر | 1 | 0 | -1 |
| تحيُّز | 2 | 1 | -1 |
| تعرُّف على الكيانات المُسمّاة | 3 | 2 | -1 |
| تعلُّم غير موجَّه | 1 | 0 | -1 |
| دالة الخسارة | 1 | 0 | -1 |
| دالة تنشيط | 1 | 0 | -1 |
| وكيل | 1 | 0 | -1 |
| دورة | 2 | 0 | -2 |
| أمر | 3 | 0 | -3 |
| شجرة القرار | 3 | 0 | -3 |

Major attractors (incorrect Top-1 increase ≥ 2):

- **اسم** (2 → 5; queries GOLD_001, GOLD_028, GOLD_031, GOLD_033, GOLD_041). Other pilot terms in its example: تعلُّم الآلة, نموذج; general ML vocabulary items: 5; 132 chars. Example describes building a classification model from a labelled dataset with a machine-learning algorithm («مجموعة بيانات»، «نموذج التصنيف»، «خوارزمية تعلُّم آلة»، «إنشاء النموذج»): generic model-building vocabulary; it literally contains other pilot terms (نموذج، تعلُّم الآلة).
- **مُحوِّل** (0 → 3; queries GOLD_026, GOLD_042, GOLD_047). Other pilot terms in its example: none; general ML vocabulary items: 1; 211 chars. Example (Egypt GenAI guidelines) mentions computer vision, generative modelling, diffusion models and «تسلسل محدد»: several concepts in one sentence, including sequence vocabulary relevant to RNN/LSTM queries.
- **مُولِّد** (1 → 4; queries GOLD_003, GOLD_025, GOLD_044, GOLD_050). Other pilot terms in its example: أمر, تدريب; general ML vocabulary items: 2; 227 chars. Example describes GAN training difficulty («تدريب»، «التدريب»، «عدم الاستقرار»، «إنتاج صور ذات جودة منخفضة»): training and output-quality vocabulary shared with many queries; it contains the pilot term تدريب. مُولِّد was already an incorrect Top-1 once under B (GOLD_050).
- **تعلُّم موجَّه** (0 → 2; queries GOLD_016, GOLD_037). Other pilot terms in its example: تعلُّم الآلة, ذكاء اصطناعي, نموذج; general ML vocabulary items: 6; 207 chars. Example describes a random-forest model presented as supervised machine learning in finance; it contains broad terms (تعلم آلي، الذكاء الاصطناعي) and attracts the label (اسم) and machine learning (تعلُّم الآلة) queries.
- **سياسة** (0 → 2; queries GOLD_004, GOLD_040). Other pilot terms in its example: none; general ML vocabulary items: 1; 289 chars. Example is a long technical Q-learning/MDP sentence (states, actions, Q-table, Bellman update); it attracts the other RL query (بيئة) and شبكة عصبية اصطناعية (already a deep failure).

## 5. Example properties by outcome (descriptive)

| Outcome | n | Mean chars | Mean tokens | Exact Siwar term | Other pilot term in example | ≥2 pilot terms | Mean general-ML items |
|---|---:|---:|---:|---:|---:|---:|---:|
| improved_with_example | 11 | 189.73 | 61.73 | 9 | 6 | 6 | 1.64 |
| worsened_with_example | 13 | 262.54 | 78.46 | 4 | 7 | 4 | 2.38 |
| unchanged_with_example | 24 | 197.04 | 62.88 | 13 | 15 | 10 | 1.67 |

## 6. Term specificity (manual, exploratory)

| Class | n | Top-1 term | Top-1 def | Top-1 def+ex | MRR term | MRR def | MRR def+ex | Def→ex improved/worsened/unchanged |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| broad | 10 | 0.200 | 0.500 | 0.300 | 0.381 | 0.538 | 0.411 | 3/4/3 |
| moderately_general | 21 | 0.333 | 0.524 | 0.524 | 0.442 | 0.705 | 0.682 | 3/7/11 |
| specific | 17 | 0.176 | 0.471 | 0.471 | 0.342 | 0.611 | 0.650 | 5/2/10 |

## 7. Language style

Saudi colloquial (n=7) and Arabic–English mixed (n=4) are too small for reliable conclusions.

| Style | n | Condition | Top-1 | Top-3 | Top-5 | MRR |
|---|---:|---|---:|---:|---:|---:|
| arabic_english_mixed | 4 | term_only | 0.750 | 0.750 | 0.750 | 0.756 |
| arabic_english_mixed | 4 | definition | 0.750 | 0.750 | 0.750 | 0.778 |
| arabic_english_mixed | 4 | example | 0.750 | 0.750 | 0.750 | 0.773 |
| msa | 37 | term_only | 0.243 | 0.378 | 0.541 | 0.372 |
| msa | 37 | definition | 0.541 | 0.757 | 0.838 | 0.663 |
| msa | 37 | example | 0.486 | 0.730 | 0.865 | 0.645 |
| saudi_colloquial | 7 | term_only | 0.000 | 0.571 | 0.714 | 0.304 |
| saudi_colloquial | 7 | definition | 0.143 | 0.714 | 0.857 | 0.419 |
| saudi_colloquial | 7 | example | 0.143 | 0.429 | 0.429 | 0.359 |

Definition → example rank changes by style: arabic_english_mixed: unchanged 3, worsened 1; msa: improved 10, unchanged 19, worsened 8; saudi_colloquial: improved 1, unchanged 2, worsened 4.

## 8. Definition contribution (term only → term + definition)

Improved 28, worsened 8, unchanged 12.

| Query | Term | Pilot category | Rank term only → definition |
|---|---|---|---|
| GOLD_004 | بيئة | ambiguous | 45 → 2 |
| GOLD_003 | هلوسة | ambiguous | 46 → 5 |
| GOLD_016 | اسم | ambiguous | 40 → 5 |
| GOLD_008 | تحيُّز | ambiguous | 33 → 1 |
| GOLD_041 | شبكة عصبية ترشيحية | abbreviation_alias | 39 → 9 |
| GOLD_014 | مُولِّد | ambiguous | 30 → 1 |
| GOLD_002 | وكيل | ambiguous | 27 → 1 |
| GOLD_013 | مُحوِّل | ambiguous | 34 → 11 |
| GOLD_019 | مواءمة | ambiguous | 18 → 1 |
| GOLD_018 | تأسيس | ambiguous | 17 → 1 |

Largest losses: GOLD_001 نموذج 3 → 21; GOLD_040 شبكة عصبية اصطناعية 24 → 34; GOLD_037 تعلُّم الآلة 5 → 15; GOLD_015 عائد 4 → 11; GOLD_033 شجرة القرار 1 → 5.

| Pilot selection category | n | Median rank gain | Top-1 term only | Top-1 definition |
|---|---:|---:|---:|---:|
| ambiguous | 18 | 13.5 | 1 | 8 |
| technical | 15 | 1 | 6 | 11 |
| abbreviation_alias | 15 | 0 | 5 | 5 |

Previously noted terms: وكيل 27 → 1; هلوسة 46 → 5; بيئة 45 → 2; تحيُّز 33 → 1.

## 9. Conclusions

### Supported findings
- Adding the Siwar definition to the term substantially improved retrieval over the term-only representation on the same 48 terms and queries (Top-1 0.250 → 0.500, MRR 0.394 → 0.637); 28 queries improved in rank, 8 worsened and 12 were unchanged.
- No additional benefit from a single usage example was detected beyond the definition-only representation in this pilot (Top-1 0.500 → 0.458, MRR 0.637 → 0.614; 11 queries improved, 13 worsened, 24 unchanged).

### Observed patterns (descriptive)
- After adding the example, half of the queries keep the same rank and changes go in both directions; 20 of the 24 Top-1 hits under the definition condition are retained, 4 drop out and 2 are newly reached.
- Some terms became incorrect Top-1 answers more often with examples (اسم, مُحوِّل, مُولِّد, تعلُّم موجَّه, سياسة). Their examples use model-building / training vocabulary, combine several technical concepts, or literally contain other pilot terms.
- Examples of worsened queries are longer on average (262.54 chars vs 189.73 for improved and 197.04 for unchanged) and less often contain the exact Siwar term (4/13 vs 9/11 improved).
- Several worsened queries have examples that discuss the target term in a different context than its definition (cybersecurity, banking, open science, sports media, deepfakes) or use a different lexical form (فرط الاستعداد, الالتفافية).
- By manual specificity class, Top-1 for broad terms fell from 0.500 to 0.300 with examples (n=10), while specific terms kept Top-1 (0.471) and their MRR moved 0.611 → 0.650 (n=17).
- In the term-only → definition transition, gains concentrate in the pilot's 'ambiguous' category (terms whose names are general-language words): median rank gain 13.5 and Top-1 1 → 8 of 18, versus median 1 (technical) and 0 (abbreviation/alias). Definitions also worsened 8 queries, including broad terms (e.g. نموذج 3 → 21; شبكة عصبية اصطناعية 24 → 34; تعلُّم الآلة 5 → 15).

### Hypotheses for future work (not findings)
- Usage examples written in broad ML/AI language may introduce semantic competition between entries.
- More discriminative examples (describing the concept's mechanism) may work better than topical examples.
- Broad target terms may be more vulnerable to semantic competition from examples than specific terms
  (suggested only by the exploratory specificity split; small groups, single annotator).
- The example selection strategy (which example, how long, what context) may matter more than the presence
  of an example; the deterministic first-example rule was not optimised.

## 10. Threats to validity
- Small pilot: 48 evaluated terms, one Gold query per term; one query moves Top-1 by about 0.021.
- One usage example per term, chosen deterministically as the first stored example (not selected for quality).
- Examples vary in source type and writing style (journal abstracts, theses, guidelines, book translations).
- Error categories, specificity classes and attractor notes are manual and exploratory (single annotator).
- Two entries (حُزمة, بث) were excluded because no valid independent example was found.
- Saudi colloquial (n=7) and Arabic–English mixed (n=4) query groups are small.
- Some Siwar definitions contain aliases or related terminology (e.g. «ويُطلق عليه أيضًا ...»), which can affect
  both definition and example conditions.

