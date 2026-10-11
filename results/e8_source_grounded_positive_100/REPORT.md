# E8 — Source-grounded positive pilot (100 items)

**Status: INTERIM PILOT — not the formal held-out evaluation.** The 100 items are positives only, LLM-drafted from independent sources (Amendment A3/D3), and have **not** yet received independent blind human gold annotation; there are no new negatives and no validated acceptable-entry sets. No claim of held-out success or failure (PREREGISTRATION §7) is made. Per D3 these items are now pilot items, excluded from the formal frozen test unless a further amendment decides otherwise. The pilot's 100 targets were hand-selected from the 120-entry primary pool (avoiding niche entries), which may make it easier than a strictly ordered sample.

**False-specialization rate is NOT reported**: this set contains no negative items. (Old development reference only, not part of E8: on the 22 old dev negatives, baseline 2/22 and S1 0/22 at every k — E6/E7.)

Frozen system, code commit `4a1278ee834b07f9a46ce06e968bf17d7853220c`, S1/S2 implementation `3490f269ac954eef2daed2990ecf2b9fcc1559f5`; model Qwen/Qwen3.5-4B (T=0, thinking off); retriever intfloat/multilingual-e5-large; prompt hashes in `run_config.json`. Strict scoring against each item's `unit_id`. Nothing was tuned or edited after seeing results.

## 1. Summary table (all registered S1 k values shown; no threshold chosen)

| Profile | Setting | Correct | Wrong | NONE | Precision | Coverage | Wrong flagged as potential alternative |
|---|---|---|---|---|---|---|---|
| P-full | baseline | 67 | 33 | 0 | 0.67 | 0.67 | 15 |
| P-full | S1@k=1 | 30 | 3 | 67 | 0.909 | 0.3 | 2 |
| P-full | S1@k=3 | 51 | 6 | 43 | 0.895 | 0.51 | 5 |
| P-full | S1@k=5 | 56 | 11 | 33 | 0.836 | 0.56 | 7 |
| P-full | S1@k=10 | 59 | 15 | 26 | 0.797 | 0.59 | 8 |
| P-full | S2 | 48 | 30 | 22 | 0.615 | 0.48 | 17 |
| P-full | S1+S2@k=1 (exploratory) | 17 | 2 | 81 | 0.895 | 0.17 | 1 |
| P-full | S1+S2@k=3 (exploratory) | 34 | 6 | 60 | 0.85 | 0.34 | 5 |
| P-full | S1+S2@k=5 (exploratory) | 38 | 10 | 52 | 0.792 | 0.38 | 8 |
| P-full | S1+S2@k=10 (exploratory) | 41 | 15 | 44 | 0.732 | 0.41 | 9 |
| P-def | baseline | 67 | 33 | 0 | 0.67 | 0.67 | 20 |
| P-def | S1@k=1 | 28 | 1 | 71 | 0.966 | 0.28 | 1 |
| P-def | S1@k=3 | 49 | 7 | 44 | 0.875 | 0.49 | 5 |
| P-def | S1@k=5 | 51 | 10 | 39 | 0.836 | 0.51 | 8 |
| P-def | S1@k=10 | 55 | 17 | 28 | 0.764 | 0.55 | 12 |
| P-def | S2 | 57 | 26 | 17 | 0.687 | 0.57 | 16 |
| P-def | S1+S2@k=1 (exploratory) | 22 | 1 | 77 | 0.957 | 0.22 | 1 |
| P-def | S1+S2@k=3 (exploratory) | 37 | 10 | 53 | 0.787 | 0.37 | 8 |
| P-def | S1+S2@k=5 (exploratory) | 38 | 12 | 50 | 0.76 | 0.38 | 10 |
| P-def | S1+S2@k=10 (exploratory) | 42 | 15 | 43 | 0.737 | 0.42 | 12 |

Precision = correct / (correct + wrong) on positives (no negatives exist here). Coverage = correct / 100.

## 2. Retrieval and availability

| | Hit@1 | Hit@3 | Hit@5 | Hit@10 | Hit@30 | Hit@50 | MRR | Expected among decision candidates | Gate rejections |
|---|---|---|---|---|---|---|---|---|---|
| P-full first stage | 0.53 | 0.76 | 0.8 | 0.84 | 0.93 | 0.98 | 0.6504 | 93/100 (of 30) | 0 |
| P-def first stage | 0.44 | 0.68 | 0.75 | 0.83 | 0.92 | 0.97 | 0.5792 | 86/100 (of 10) | 0 |
| P-def after reranker | 0.61 | 0.77 | 0.8 | 0.86 | – | – | – | – | – |

In P-def the reranker moved the expected entry into the selector's top-10 from outside the first-stage top-10 in 11 items, but pushed it out of the top-10 from first-stage rank 1 in 6 items (SG100-015, 027, 034, 048, 060, 068).

## 3. S1 and S2 detail (relative to the baseline decision)

| Profile | Setting | Correct decisions rejected | Wrong decisions rejected | Wrong corrected | Correct → wrong | Wrong → other wrong |
|---|---|---|---|---|---|---|
| P-full | S1@k=1 | 37 | 30 | 0 | 0 | 0 |
| P-full | S1@k=3 | 16 | 27 | 0 | 0 | 0 |
| P-full | S1@k=5 | 11 | 22 | 0 | 0 | 0 |
| P-full | S1@k=10 | 8 | 18 | 0 | 0 | 0 |
| P-full | S2 | 17 | 5 | 3 | 5 | 6 |
| P-full | S1+S2@k=3 (exploratory) | 33 | 27 | 2 | 2 | 1 |
| P-full | S1+S2@k=5 (exploratory) | 28 | 24 | 2 | 3 | 1 |
| P-def | S1@k=1 | 39 | 32 | 0 | 0 | 0 |
| P-def | S1@k=3 | 18 | 26 | 0 | 0 | 0 |
| P-def | S1@k=5 | 16 | 23 | 0 | 0 | 0 |
| P-def | S1@k=10 | 12 | 16 | 0 | 0 | 0 |
| P-def | S2 | 14 | 3 | 7 | 3 | 4 |
| P-def | S1+S2@k=3 (exploratory) | 29 | 24 | 2 | 3 | 0 |
| P-def | S1+S2@k=5 (exploratory) | 28 | 22 | 2 | 3 | 1 |

S2 cost (P-full): 100 extra calls, median 1.571 s, ~458 prompt tokens each.

S2 cost (P-def): 100 extra calls, median 1.618 s, ~433 prompt tokens each.

## 4. Baseline failure stages

| Profile | Retrieval | Reranker | Decision (expected available) | Technical gate | Wrong picks flagged as potential alternatives |
|---|---|---|---|---|---|
| P-full | 7 | 0 | 26 | 0 | 15 of 33 |
| P-def | 3 | 11 | 19 | 0 | 20 of 33 |

S1 false rejections of correct decisions: P-full k=1/3/5/10 = 37/16/11/8; P-def = 39/18/16/12. S2 false rejections / drift on correct decisions: P-full 17 / 5; P-def 14 / 3. Full table: `ERRORS.md`.

## 5. Writing style (correct / wrong)

| Style | n | P-full first-stage Hit@10 | P-full baseline | P-full S1@k=3 | P-full S2 | P-def first-stage Hit@10 | P-def baseline | P-def S1@k=3 | P-def S2 |
|---|---|---|---|---|---|---|---|---|---|
| reports_formal | 45 | 0.889 | 34/11 | 29/3 | 21/11 | 0.911 | 33/12 | 27/2 | 26/9 |
| developer | 25 | 0.72 | 14/11 | 9/2 | 10/9 | 0.68 | 16/9 | 11/2 | 16/5 |
| social | 20 | 0.9 | 13/7 | 9/1 | 11/8 | 0.8 | 10/10 | 6/2 | 8/10 |
| product_support | 10 | 0.8 | 6/4 | 4/0 | 6/2 | 0.9 | 8/2 | 5/1 | 7/2 |

Groups are small (10–45 items); differences of a few items are not reliable.

## 6. Answers

1. **Agreement with E5–E7.** Baseline behaviour agrees (P-full 67/100 vs 48/80 on dev; P-def 67/100 vs 51/80). S1 behaves **materially better** than on development data: on dev it removed correct and wrong decisions about 1:1 (precision ~0.69–0.73); here it removes far more wrong than correct decisions (e.g. P-full k=3: 27 wrong vs 16 correct). S2 is again net-negative in P-full and roughly neutral in P-def.
2. **Strict accepted-term precision.** Baseline 0.67 in both profiles. With S1: P-full 0.91 / 0.89 / 0.84 / 0.80 and P-def 0.97 / 0.88 / 0.84 / 0.76 for k = 1 / 3 / 5 / 10. S2: 0.62 (P-full), 0.69 (P-def).
3. **Coverage.** Baseline 0.67 in both; S1 P-full 0.30 / 0.51 / 0.56 / 0.59, P-def 0.28 / 0.49 / 0.51 / 0.55; S2 0.48 / 0.57.
4. **P-full vs P-def.** Equal at baseline (67 correct each). P-full has better first-stage ranking (MRR 0.65 vs 0.58) and slightly better S1 coverage at k ≥ 3; P-def's reranker both rescues (11) and loses (6) items. No clear winner on this pilot.
5. **Does S1 improve precision here?** Yes, clearly, at a coverage cost: k=3 reaches ~0.88–0.90 precision at ~0.50 coverage in both profiles. This is not a test of §7 (no negatives, no validated labels, a possibly easier selection of terms), and no k is chosen from it.
6. **S2.** Still not useful as frozen: in P-full it lowers precision and coverage; in P-def it corrects 7 wrong decisions but rejects 14 correct ones and changes 3 correct ones to wrong, for a net precision change of +0.02 at −0.10 coverage.
7. **Hardest style.** Developer questions/issues (P-full 14/11, P-def 16/9; lowest first-stage Hit@10, 0.72 / 0.68), followed by social/Saudi in P-def (10/10). Formal/report texts are easiest (34/11, 33/12).
8. **Dominant errors.** Still decision-stage near-neighbour confusions: 26/33 (P-full) and 19/33 (P-def, plus 11 reranker losses). Retrieval failures are few (7 and 3). 15 (P-full) and 20 (P-def) of the 33 wrong picks are neighbours of the gold entry and may be acceptable alternatives — this needs human annotation before precision can be stated non-strictly.
9. **Expected entry available but another term chosen.** P-full: 26 of 93 items where it was among the 30 candidates (28 %). P-def: 19 of 86 items where it was among the selector's 10 (22 %).
10. **What to investigate next (protocol unchanged):** (a) human acceptable-entry annotation of these 100 items (blind file exists) to separate genuine errors from acceptable alternatives; (b) source-grounded **negatives** (everyday-sense and vague technical) so that S1's false-specialization behaviour and §7 can be assessed; (c) a diagnostic of why S1 separates correct from wrong decisions far better here than on the development data (text style, concept familiarity, or the pilot's term selection); (d) a diagnostic of the reranker's 6 demotions of first-stage rank-1 entries. None of these changes the frozen protocol.

## 7. Ten most informative errors (analyst notes are judgement, not labels)

| item_id | profile | style | text | expected | baseline | S2 | first-stage rank | note |
|---|---|---|---|---|---|---|---|---|
| SG100-005 | P-full | developer | عندي عدة weak learners وأضيفها واحد وراء الثاني، وكل واحد يحاول يصلح أخطاء اللي قبله. هل هذا الأسلوب مناسب للتصنيف؟ | تعزيز تدرجي | تعزيز تَكَيُّفيّ | تعزيز تَكَيُّفيّ | 1 | Sequential weak learners correcting predecessors fits both gradient and adaptive boosting: likely gold ambiguity, not a clear error. |
| SG100-021 | P-full | developer | عندي مودل متعلم على مهمة قريبة من مشكلتي. هل أقدر أستفيد من اللي تعلمه وأكيّفه للمهمة الجديدة بدل أبدأ من الصفر؟ | تعلُّم منقول | ضبط دقيق | ضبط دقيق | 1 | Expected first-ranked, decision chose the related practice (fine-tuning). Near-neighbour decision error; possibly acceptable. |
| SG100-027 | P-def | social | بدل ما أحسب كل البيانات في كل خطوة، أستخدم جزء عشوائي يعطيني اتجاه تقريبي للتحديث. أسرع بس فيه تذبذب طبيعي. | تحسين عشوائي | نزول تدرجي عشوائي | نزول تدرجي عشوائي | 1 | First-stage rank 1, reranker dropped it to 11; selector chose the more specific SGD. Reranker + specificity error. |
| SG100-015 | P-def | social | بدل ما أحدد الـfeatures يدوي، أبي الشبكة تطلع التمثيلات المهمة من البيانات الخام بنفسها وتستخدمها لاحقًا في التصنيف. | تعلُّم الخصائص | تعلُّم عميق | NONE | 1 | First-stage rank 1, reranker moved it out of the top 10; selector chose the umbrella term (deep learning). |
| SG100-034 | P-full | reports_formal | في شجرة البحث الحالية، كل عقدة ممكن تنتج في المتوسط خمس حالات جديدة، وهذا يرفع عدد المسارات بسرعة كبيرة. | عامل التفرع | شجرة الأفكار | شجرة الأفكار | 1 | Expected first-ranked; decision chose a topically adjacent technique (tree of thoughts). Topic-over-concept error. |
| SG100-094 | P-full | reports_formal | نفترض في التحليل أن كل عينة لا تعتمد على الأخرى، وأن جميع العينات سُحبت من التوزيع الاحتمالي نفسه. | متغيرات مستقلة ومتطابقة التوزيع | أخذ عيِّنات البيانات | أخذ عيِّنات جزئية | 1 | Expected first-ranked; decision chose the generic data-sampling concept. Decision prefers a familiar generic term. |
| SG100-059 | P-def | social | جربت نموذج بسيط على مجموعة صور صغيرة لأرقام مكتوبة باليد من صفر إلى تسعة، واستخدمتها للتدريب والاختبار. | إم نيست | بيانات التدريب (أو مجموعة التدريب) | بيانات التحقق (أو مجموعة التحقق) | 11 | A named dataset (MNIST) described by its content; decision chose generic training/validation-data entries. |
| SG100-092 | P-full | reports_formal | استبدلنا الالتفاف الكامل بعملية على كل قناة بشكل مستقل ثم مزج القنوات، وانخفضت العمليات الحسابية بشكل واضح. | شبكة عصبية ترشيحية قابلة للفصل عمقًا | بث | ضغط المتجهات | 375 | Long, highly specific headword; first-stage rank 375 (783 in P-def). Clear retrieval failure. |
| SG100-009 | P-def | reports_formal | لوحظ بعد عدة أشهر من النشر تغير توزيع بعض متغيرات الإدخال مقارنة بخط الأساس، وتزامن ذلك مع تراجع ملحوظ في جودة التنبؤ. | انحراف الخصائص | انحراف النموذج | انحراف الخصائص | 1 | Decision chose model drift for feature drift; S2 corrected it to the gold — one of S2's 7 corrections in P-def. |
| SG100-001 | P-full | developer | شغلت المودل على الحساس نفسه بدل ما أرسل كل قراءة للسيرفر. الـlatency تحسن كثير، بس أبي أتأكد إن هذا مناسب للإنتاج. | نموذج طرفي | نموذج طرفي | ذكاء اصطناعي طرفي | 16 | Baseline correct in P-full; S2 drifted to the neighbour «ذكاء اصطناعي طرفي». In P-def S2 instead corrected the baseline to the gold. Illustrates S2's instability. |

## 8. Files
`summary.json`, `per_item_results.json`, `errors.json`, `ERRORS.md`, `style_breakdown.json`, `run_config.json`, `llm_calls_cache.json` (all calls).
