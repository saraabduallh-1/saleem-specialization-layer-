# Qwen Domain Ablation Pilot

- Model: \`Qwen/Qwen3.5-4B\`
- Inputs: 15
- Conditions: D0_saleem_only, D1_domain_name, D2_domain_name_definition, D3_domain_guidance, D4_domain_guidance_examples
- Temperature: 0.0
- Max tokens: 256

## P01

**Input:** النموذج يتعلم من البيانات وبعدها يقدر يتوقع نتائج لبيانات جديدة.

### D0_saleem_only

Thinking Process:

1.  **Analyze the Request:**
    *   **Task:** Rewrite the given Arabic text to make it clearer and more accurate (أوضح وأدق) while preserving its meaning (مع الحفاظ على معناه).
    *   **Constraint 1:** Do not add facts or information not present in the original text (لا تضف حقائق أو معلومات غير موجودة في النص).
    *   **Constraint 2:** Output only the rewritten text, no explanation (أعد النص المصاغ فقط دون شرح).
    *   **Input Text:** "النموذج يتعلم من البيانات وبعدها يقدر يتوقع نتائج لبيانات جديدة." (The model learns from data and then it can predict results for new data.)

2.  **Analyze the Input Text:**
    *   "النموذج" (The model)
    *   "يتعلم من البيانات" (learns from data)
    *   "وبعدها" (and then/afterwards)
    *   "يقدر" (can/able to)
    *   "يتوقع" (predict)
    *   "نتائج لبيانات جديدة" (results for new

### D1_domain_name

Thinking Process:

1.  **Analyze the Request:**
    *   **Task:** Rewrite the given Arabic text to make it clearer and more accurate (أوضح وأدق) while preserving its meaning (مع الحفاظ على معناه).
    *   **Constraint 1:** Do not add facts or information not present in the original text (لا تضف حقائق أو معلومات غير موجودة في النص).
    *   **Constraint 2:** Output only the rewritten text, no explanation (أعد النص المصاغ فقط دون شرح).
    *   **Domain:** Artificial Intelligence (ذكاء اصطناعي).
    *   **Original Text:** "النموذج يتعلم من البيانات وبعدها يقدر يتوقع نتائج لبيانات جديدة." (The model learns from data and then it can predict results for new data.)

2.  **Analyze the Original Text:**
    *   "النموذج" (The model) - Subject.
    *   "يتعلم من البيانات" (learns from data) - Action 1.
    *   "وبعدها" (and then/afterwards) - Transition.
    *   "يقدر" (can) - Ability.

### D2_domain_name_definition

Thinking Process:

1.  **Analyze the Request:**
    *   **Task:** Rewrite the given Arabic text to make it clearer and more precise while maintaining its original meaning.
    *   **Constraint 1:** Do not add facts or information not present in the original text.
    *   **Constraint 2:** Output only the rewritten text, without explanation.
    *   **Domain:** Artificial Intelligence (ذكاء اصطناعي).
    *   **Input Text:**
        *   Definition of the field: "مجال يختص بالأنظمة الحاسوبية القادرة على استنتاج مخرجات، مثل التنبؤات أو المحتوى أو التوصيات أو القرارات، اعتمادًا على مدخلات تستقبلها، وقد تختلف هذه الأنظمة في مستويات الاستقلالية والتكيف بعد النشر."
        *   Text to improve: "النموذج يتعلم من البيانات وبعدها يقدر يتوقع نتائج لبيانات جديدة."

2.  **Analyze the Input Text to be Improved:**
    *   Original: "النموذج يتعلم من البيانات وبعدها يقدر يتوقع نتائج لبيانات جديدة."
    *   Issues:
        *   "بعدها"

### D3_domain_guidance

Thinking Process:

1.  **Analyze the Request:**
    *   **Task:** Rewrite the given Arabic text to be clearer and more accurate while preserving its meaning.
    *   **Constraint 1:** Do not add facts or information not present in the original text.
    *   **Constraint 2:** Output only the rewritten text, no explanation.
    *   **Domain:** Artificial Intelligence (AI).
    *   **Input Text:** "النموذج يتعلم من البيانات وبعدها يقدر يتوقع نتائج لبيانات جديدة." (The model learns from data and then estimates to predict results for new data.)
    *   **Guidelines:** Use precise terminology, maintain consistency, improve phrasing without changing facts/relationships/uncertainty, do not add mechanisms/capabilities/results/numbers, distinguish between close concepts, use clear sentences, describe capabilities accurately without overstating autonomy/uncertainty.

2.  **Analyze the Input Text:**
    *   "النموذج يتعلم من البيانات" (The model learns from data) - This is a standard description of training.
    *   "وبعدها" (and then/afterwards) - Indicates sequence.
    *

### D4_domain_guidance_examples

Thinking Process:

1.  **Analyze the Request:**
    *   **Task:** Rewrite the given Arabic text to make it clearer and more accurate while preserving its meaning.
    *   **Constraint 1:** Do not add facts or information not present in the original text.
    *   **Constraint 2:** Output only the rewritten text, no explanations.
    *   **Domain:** Artificial Intelligence (AI).
    *   **Input Text:** "النموذج يتعلم من البيانات وبعدها يقدر يتوقع نتائج لبيانات جديدة." (The model learns from data and then estimates to predict results for new data.)
    *   **Guidelines:** Use precise terminology, maintain consistency, improve phrasing without changing facts/relationships/uncertainty, avoid adding mechanisms/capabilities/results/numbers, distinguish between close concepts, use clear sentences, describe capabilities accurately without overstating autonomy/uncertainty.

2.  **Analyze the Input Text:**
    *   "النموذج يتعلم من البيانات" (The model learns from data) - This is a general statement about training.
    *   "وبعدها" (and then/afterwards) - Indicates sequence.
    *

## P02

**Input:** الهلوسة تصير لما النظام يعطي معلومات تبدو صحيحة لكنها غير موجودة أو غير دقيقة.

### D0_saleem_only

Thinking Process:

1.  **Analyze the Request:**
    *   **Task:** Rewrite the given Arabic text to make it clearer and more accurate (أعد صياغة النص العربي ليكون أوضح وأدق).
    *   **Constraint 1:** Maintain the original meaning (مع الحفاظ على معناه).
    *   **Constraint 2:** Do not add facts or information not present in the original text (لا تضف حقائق أو معلومات غير موجودة في النص).
    *   **Constraint 3:** Output only the rewritten text, no explanation (أعد النص المصاغ فقط دون شرح).

2.  **Analyze the Original Text:**
    *   Text: "الهلوسة تصير لما النظام يعطي معلومات تبدو صحيحة لكنها غير موجودة أو غير دقيقة."
    *   Meaning: "Hallucination occurs when the system provides information that appears correct but is either non-existent or inaccurate."
    *   Issues/Improvements needed:
        *   "الهلوسة تصير" (Hallucination becomes/happens) -> A bit colloquial or awkward. "تحدث" (happens) or "تكون" (is) or "تظهر" (appe

### D1_domain_name

Thinking Process:

1.  **Analyze the Request:**
    *   **Task:** Rewrite the given Arabic text to make it clearer and more accurate (أوضح وأدق) while preserving its meaning (مع الحفاظ على معناه).
    *   **Constraint 1:** Do not add facts or information not present in the original text (لا تضف حقائق أو معلومات غير موجودة في النص).
    *   **Constraint 2:** Output only the rewritten text, no explanation (أعد النص المصاغ فقط دون شرح).
    *   **Domain:** Artificial Intelligence (الذكاء الاصطناعي).
    *   **Original Text:** "الهلوسة تصير لما النظام يعطي معلومات تبدو صحيحة لكنها غير موجودة أو غير دقيقة." (Note: There's a typo in the original text "تصير" should be "تُصير" or "تُعد" or "تكون", but I need to focus on meaning and clarity).
    *   **Meaning of Original:** Hallucination is when the system provides information that appears correct but is actually non-existent or inaccurate.

2.  **Evaluate the Original Text:**
    *   "الهلوسة تصير لما النظام يع

### D2_domain_name_definition

Thinking Process:

1.  **Analyze the Request:**
    *   **Task:** Rewrite the given Arabic text to make it clearer and more accurate while preserving its meaning.
    *   **Constraint 1:** Do not add facts or information not present in the original text.
    *   **Constraint 2:** Output only the rewritten text, no explanation.
    *   **Domain:** Artificial Intelligence (ذكاء اصطناعي).
    *   **Input Text:**
        *   Definition of the field: "مجال يختص بالأنظمة الحاسوبية القادرة على استنتاج مخرجات، مثل التنبؤات أو المحتوى أو التوصيات أو القرارات، اعتمادًا على مدخلات تستقبلها، وقد تختلف هذه الأنظمة في مستويات الاستقلالية والتكيف بعد النشر."
        *   Target text to improve: "الهلوسة تصير لما النظام يعطي معلومات تبدو صحيحة لكنها غير موجودة أو غير دقيقة."

2.  **Analyze the Input Text (Target Text):**
    *   Original: "الهلوسة تصير لما النظام يعطي معلومات تبدو صحيحة لكنها غير موجودة أو غير دقيقة."
    *   Issues:
        *   "الهلوسة تصير لما

### D3_domain_guidance

Thinking Process:

1.  **Analyze the Request:**
    *   **Task:** Rewrite the given Arabic text to make it clearer and more precise while preserving its meaning.
    *   **Constraint 1:** Do not add facts or information not present in the original text.
    *   **Constraint 2:** Output only the rewritten text, no explanation.
    *   **Domain:** Artificial Intelligence (AI).
    *   **Input Text:** "الهلوسة تصير لما النظام يعطي معلومات تبدو صحيحة لكنها غير موجودة أو غير دقيقة." (Note: There seems to be a typo in the input text "الهلوسة تصير لما" which likely means "الهلوسة هي ما" or "الهلوسة تشير إلى ما". I need to interpret the intended meaning based on context while staying true to the original meaning without adding external knowledge, though correcting obvious typos for clarity is usually expected in "rewriting for clarity". However, the instruction says "preserve its meaning". The original sentence is grammatically broken: "الهلوسة تصير لما النظام يعطي..." -> "الهلوسة تصير" is not standard Arabic. It likely means "الهلوسة هي ما" or "الهلوسة تشير إلى

### D4_domain_guidance_examples

Thinking Process:

1.  **Analyze the Request:**
    *   **Task:** Rewrite the provided Arabic text to make it clearer and more accurate while preserving its meaning.
    *   **Constraint 1:** Do not add facts or information not present in the original text.
    *   **Constraint 2:** Output only the rewritten text, no explanations.
    *   **Domain:** Artificial Intelligence (AI).
    *   **Input Text:** "الهلوسة تصير لما النظام يعطي معلومات تبدو صحيحة لكنها غير موجودة أو غير دقيقة." (Hallucination turns into what the system gives information that appears correct but is not present or inaccurate.)
    *   **Guidelines:** Use precise terminology, maintain consistency, improve phrasing without changing facts/relationships/uncertainty, do not add mechanisms/capabilities/results/numbers, distinguish between close technical concepts, use clear sentences, describe capabilities accurately without overstating.

2.  **Analyze the Input Text:**
    *   Sentence: "الهلوسة تصير لما النظام يعطي معلومات تبدو صحيحة لكنها غير موجودة أو غير دقيقة."
    *   Meaning: Hallucination refers to when a system provides information that looks correct but is actually non-existent

## P03

**Input:** في التدريب نستخدم بيانات كثيرة عشان النموذج يتعلم الأنماط ويصير أداؤه أفضل.

### D0_saleem_only

Thinking Process:

1.  **Analyze the Request:**
    *   **Task:** Rewrite the given Arabic text to make it clearer and more precise (أوضح وأدق) while preserving its meaning (مع الحفاظ على معناه).
    *   **Constraint 1:** Do not add facts or information not present in the original text (لا تضف حقائق أو معلومات غير موجودة في النص).
    *   **Constraint 2:** Output only the rewritten text, no explanation (أعد النص المصاغ فقط دون شرح).
    *   **Input Text:** "في التدريب نستخدم بيانات كثيرة عشان النموذج يتعلم الأنماط ويصير أداؤه أفضل." (In training we use a lot of data so the model learns patterns and becomes better performance.)

2.  **Analyze the Input Text:**
    *   **Meaning:** During the training phase, we utilize large amounts of data. The purpose is for the model to learn patterns, resulting in improved performance.
    *   **Tone/Style:** Informal (colloquial Arabic). Words like "عشان" (so/for), "يصير" (becomes), "بيكون" (implied),

### D1_domain_name

Thinking Process:

1.  **Analyze the Request:**
    *   **Task:** Rewrite the given Arabic text to be clearer and more accurate (أوضح وأدق) while preserving its meaning (مع الحفاظ على معناه).
    *   **Constraint 1:** Do not add facts or information not present in the original text (لا تضف حقائق أو معلومات غير موجودة في النص).
    *   **Constraint 2:** Output only the rewritten text, no explanation (أعد النص المصاغ فقط دون شرح).
    *   **Domain:** Artificial Intelligence (الذكاء الاصطناعي).
    *   **Original Text:** "في التدريب نستخدم بيانات كثيرة عشان النموذج يتعلم الأنماط ويصير أداؤه أفضل." (In training we use a lot of data so the model learns patterns and becomes better performance.)

2.  **Analyze the Original Text:**
    *   "في التدريب" (In training) - Context: AI training phase.
    *   "نستخدم بيانات كثيرة" (we use a lot of data) - Action: Using large datasets.
    *   "عشان" (so that/in order to) - Purpose/Reason.

### D2_domain_name_definition

Thinking Process:

1.  **Analyze the Request:**
    *   **Task:** Rewrite the given Arabic text to be clearer and more accurate while preserving its meaning.
    *   **Constraint 1:** Do not add facts or information not present in the original text.
    *   **Constraint 2:** Output only the rewritten text, no explanation.
    *   **Domain:** Artificial Intelligence (ذكاء اصطناعي).
    *   **Input Text:** "في التدريب نستخدم بيانات كثيرة عشان النموذج يتعلم الأنماط ويصير أداؤه أفضل." (In training we use a lot of data so the model learns patterns and becomes better performance.)
    *   **Context:** The input text is a sentence about AI training, likely part of a larger document about the AI field defined in the first paragraph.

2.  **Analyze the Input Text:**
    *   "في التدريب" (In training) - Context: AI model training.
    *   "نستخدم بيانات كثيرة" (we use a lot of data) - Action: Using large datasets.
    *   "عشان" (so that/in order to) - Purpose/Reason.
    *   "

### D3_domain_guidance

Thinking Process:

1.  **Analyze the Request:**
    *   **Task:** Rewrite the given Arabic text to be clearer and more accurate while preserving its meaning.
    *   **Constraint 1:** Do not add facts or information not present in the original text.
    *   **Constraint 2:** Output only the rewritten text, no explanation.
    *   **Domain:** Artificial Intelligence (AI).
    *   **Guidelines:** Use precise technical terminology, maintain consistency in terminology, improve phrasing without changing facts/relationships/uncertainty levels, do not add mechanisms/capabilities/results/technical numbers, distinguish between close technical concepts based on context, use clear and direct sentences, describe AI system capabilities accurately without overstating understanding/independence/uncertainty.
    *   **Input Text:** "في التدريب نستخدم بيانات كثيرة عشان النموذج يتعلم الأنماط ويصير أداؤه أفضل." (In training we use a lot of data so the model learns patterns and becomes better performance.)

2.  **Analyze the Input Text:**
    *   **Content:** It describes the training process in AI/ML.
    *   **Key Points:**
        *   Action: Using a

### D4_domain_guidance_examples

Thinking Process:

1.  **Analyze the Request:**
    *   **Task:** Rewrite the given Arabic text to be clearer and more accurate while preserving its meaning.
    *   **Constraint 1:** Do not add facts or information not present in the original text.
    *   **Constraint 2:** Output only the rewritten text, no explanations.
    *   **Domain:** Artificial Intelligence (AI).
    *   **Guidelines:** Use precise technical terminology, maintain consistency in terminology, improve phrasing without changing facts/relationships/uncertainty levels, do not add mechanisms/capabilities/results/technical numbers, distinguish between close technical concepts based on context, use clear and direct sentences, describe AI system capabilities accurately without overstating understanding/independence/uncertainty.
    *   **Input Text:** "في التدريب نستخدم بيانات كثيرة عشان النموذج يتعلم الأنماط ويصير أداؤه أفضل." (In training we use a lot of data so the model learns patterns and becomes better performance.)

2.  **Analyze the Input Text:**
    *   **Content:** It describes the training process in AI/ML.
    *   **Key Points:**
        *   Action: Using a

## P04

**Input:** الوكيل يقدر ينفذ مجموعة خطوات ويستخدم أدوات مختلفة عشان يوصل للهدف المطلوب.

### D0_saleem_only

Thinking Process:

1.  **Analyze the Request:**
    *   **Task:** Rewrite the given Arabic text to make it clearer and more precise (أوضح وأدق) while preserving its meaning (مع الحفاظ على معناه).
    *   **Constraint 1:** Do not add facts or information not present in the original text (لا تضف حقائق أو معلومات غير موجودة في النص).
    *   **Constraint 2:** Output only the rewritten text, no explanation (أعد النص المصاغ فقط دون شرح).
    *   **Input Text:** "الوكيل يقدر ينفذ مجموعة خطوات ويستخدم أدوات مختلفة عشان يوصل للهدف المطلوب." (The agent can execute a set of steps and use different tools to reach the required goal.)

2.  **Analyze the Input Text:**
    *   **Subject:** الوكيل (The agent).
    *   **Action 1:** يقدر ينفذ (can execute).
    *   **Object 1:** مجموعة خطوات (a set of steps).
    *   **Action 2:** يستخدم (uses).
    *   **Object 2:** أدوات مختلفة (different tools).
    *   **Purpose:**

### D1_domain_name

Thinking Process:

1.  **Analyze the Request:**
    *   **Task:** Rewrite the given Arabic text to be clearer and more accurate (أدق) while preserving its meaning.
    *   **Constraint 1:** Do not add facts or information not present in the original text (لا تضف حقائق أو معلومات غير موجودة في النص).
    *   **Constraint 2:** Output only the rewritten text, no explanation (أعد النص المصاغ فقط دون شرح).
    *   **Domain:** Artificial Intelligence (ذكاء اصطناعي).
    *   **Original Text:** "الوكيل يقدر ينفذ مجموعة خطوات ويستخدم أدوات مختلفة عشان يوصل للهدف المطلوب." (The agent can execute a set of steps and uses different tools to reach the required goal.)

2.  **Analyze the Original Text:**
    *   **Subject:** الوكيل (The agent).
    *   **Action 1:** يقدر ينفذ مجموعة خطوات (can execute a set of steps).
    *   **Action 2:** يستخدم أدوات مختلفة (uses different tools).
    *   **Purpose:** عشان يوصل للهدف المطلوب (in order to reach the required goal

### D2_domain_name_definition

Thinking Process:

1.  **Analyze the Request:**
    *   **Task:** Rewrite the given Arabic text to make it clearer and more precise (أوضح وأدق) while preserving its meaning (مع الحفاظ على معناه).
    *   **Constraint 1:** Do not add facts or information not present in the original text (لا تضف حقائق أو معلومات غير موجودة في النص).
    *   **Constraint 2:** Output only the rewritten text, no explanation (أعد النص المصاغ فقط دون شرح).
    *   **Context:** The field is Artificial Intelligence (ذكاء اصطناعي).
    *   **Input Text to Improve:** "الوكيل يقدر ينفذ مجموعة خطوات ويستخدم أدوات مختلفة عشان يوصل للهدف المطلوب." (The agent can execute a set of steps and uses different tools to reach the required goal.)

2.  **Analyze the Input Text:**
    *   "الوكيل" (The agent): Refers to an AI agent.
    *   "يقدر ينفذ مجموعة خطوات" (can execute a set of steps): Can perform a sequence of actions.
    *   "ويستخدم أدوات مختلفة" (and uses different

### D3_domain_guidance

Thinking Process:

1.  **Analyze the Request:**
    *   **Task:** Rewrite the given Arabic text to be clearer and more accurate while preserving its meaning.
    *   **Constraint 1:** Do not add facts or information not present in the original text.
    *   **Constraint 2:** Output only the rewritten text, no explanation.
    *   **Domain:** Artificial Intelligence (AI).
    *   **Input Text:** "الوكيل يقدر ينفذ مجموعة خطوات ويستخدم أدوات مختلفة عشان يوصل للهدف المطلوب." (The agent can execute a set of steps and use different tools to reach the required goal.)
    *   **Guidelines:** Use precise terminology, maintain consistency, improve phrasing without changing facts/relationships/uncertainty, do not add mechanisms/capabilities/results/numbers, distinguish between close technical concepts based on context, use clear sentences, describe AI system capabilities accurately without overstating autonomy/uncertainty.

2.  **Analyze the Input Text:**
    *   "الوكيل" (The Agent): In the context of AI, "Agent" is a specific term. The input uses "الوكيل" which is correct.
    *

### D4_domain_guidance_examples

Thinking Process:

1.  **Analyze the Request:**
    *   **Task:** Rewrite the given Arabic text to be clearer and more accurate while preserving its meaning.
    *   **Constraint 1:** Do not add facts or information not present in the original text.
    *   **Constraint 2:** Output only the rewritten text, no explanations.
    *   **Domain:** Artificial Intelligence (AI).
    *   **Input Text:** "الوكيل يقدر ينفذ مجموعة خطوات ويستخدم أدوات مختلفة عشان يوصل للهدف المطلوب." (The agent can execute a set of steps and uses different tools to reach the required goal.)
    *   **Guidelines:** Use precise terminology, maintain consistency, improve phrasing without changing facts/relationships/uncertainty, do not add mechanisms/capabilities/results/numbers, distinguish between close technical concepts based on context, use clear and direct sentences, describe AI system capabilities accurately without overstating autonomy or certainty.

2.  **Analyze the Input Text:**
    *   "الوكيل" (The Agent): In the context of AI guidelines provided in the prompt, "Agents" are mentioned in the examples ("الوكلاء").
    *   "

## P05

**Input:** ممكن يكون فيه تحيز بالنتائج إذا البيانات اللي تدرب عليها النموذج ما كانت متوازنة.

### D0_saleem_only

Thinking Process:

1.  **Analyze the Request:**
    *   **Task:** Rewrite the given Arabic text to make it clearer and more accurate (أوضح وأدق) while preserving its meaning (مع الحفاظ على معناه).
    *   **Constraint 1:** Do not add facts or information not present in the original text (لا تضف حقائق أو معلومات غير موجودة في النص).
    *   **Constraint 2:** Output only the rewritten text, no explanation (أعد النص المصاغ فقط دون شرح).
    *   **Input Text:** "ممكن يكون فيه تحيز بالنتائج إذا البيانات اللي تدرب عليها النموذج ما كانت متوازنة." (It might have bias in the results if the data the model was trained on was not balanced.)

2.  **Analyze the Input Text:**
    *   **Meaning:** The text discusses potential bias in model results due to unbalanced training data.
    *   **Tone:** Informal/Colloquial ("ممكن" instead of "قد", "اللي" instead of "التي/التي", "ما كانت" instead of "لم تكن").
    *   **Clarity:** It's understandable

### D1_domain_name

Thinking Process:

1.  **Analyze the Request:**
    *   **Task:** Rewrite the given Arabic text to make it clearer and more accurate (أوضح وأدق) while preserving its meaning (مع الحفاظ على معناه).
    *   **Constraint 1:** Do not add facts or information not present in the original text (لا تضف حقائق أو معلومات غير موجودة في النص).
    *   **Constraint 2:** Output only the rewritten text, no explanation (أعد النص المصاغ فقط دون شرح).
    *   **Domain:** Artificial Intelligence (الذكاء الاصطناعي).
    *   **Original Text:** "ممكن يكون فيه تحيز بالنتائج إذا البيانات اللي تدرب عليها النموذج ما كانت متوازنة." (It might have bias in the results if the data the model is trained on was not balanced.)

2.  **Analyze the Original Text:**
    *   **Meaning:** The model's results could be biased if the training data is unbalanced.
    *   **Tone:** Informal ("ممكن", "فيه", "اللي").
    *   **Clarity:** It's understandable but could be more formal and precise.

### D2_domain_name_definition

Thinking Process:

1.  **Analyze the Request:**
    *   **Task:** Rewrite the given Arabic text to make it clearer and more accurate while preserving its meaning.
    *   **Constraint 1:** Do not add facts or information not present in the original text.
    *   **Constraint 2:** Output only the rewritten text, no explanation.
    *   **Domain:** Artificial Intelligence (ذكاء اصطناعي).
    *   **Input Text:** "ممكن يكون فيه تحيز بالنتائج إذا البيانات اللي تدرب عليها النموذج ما كانت متوازنة." (It might have bias in the results if the data the model is trained on was not balanced.)
    *   **Goal:** Improve clarity and accuracy (grammar, flow, vocabulary) without changing the core message.

2.  **Analyze the Input Text:**
    *   "ممكن يكون فيه تحيز بالنتائج" (It might have bias in the results) -> A bit colloquial ("ممكن" instead of "قد" or "من الممكن", "فيه" instead of "فيها" or "فيها").
    *   "إذا البيانات اللي تدرب عليها النموذج" (If the data

### D3_domain_guidance

Thinking Process:

1.  **Analyze the Request:**
    *   **Task:** Rewrite the given Arabic text to be clearer and more accurate while preserving its meaning.
    *   **Constraint 1:** Do not add facts or information not present in the original text.
    *   **Constraint 2:** Output only the rewritten text, no explanation.
    *   **Domain:** Artificial Intelligence (AI).
    *   **Input Text:** "ممكن يكون فيه تحيز بالنتائج إذا البيانات اللي تدرب عليها النموذج ما كانت متوازنة." (It might have bias in the results if the data the model is trained on was not balanced.)
    *   **Guidelines:** Use precise terminology, maintain consistency, improve phrasing without changing facts/relationships/uncertainty, do not add mechanisms/capabilities/results/numbers, distinguish between close technical concepts, use clear sentences, describe AI capabilities accurately without overstating.

2.  **Analyze the Input Text:**
    *   "ممكن يكون فيه تحيز بالنتائج" (It might have bias in the results) -> This expresses uncertainty ("might").
    *   "إذا البيانات اللي تدرب عليها النموذج" (If the data

### D4_domain_guidance_examples

Thinking Process:

1.  **Analyze the Request:**
    *   **Task:** Rewrite the given Arabic text to make it clearer and more precise while maintaining its original meaning.
    *   **Constraint 1:** Do not add facts or information not present in the original text.
    *   **Constraint 2:** Output only the rewritten text, no explanations.
    *   **Domain:** Artificial Intelligence (AI).
    *   **Guidelines:** Use precise terminology, maintain consistency, improve phrasing without changing facts/relationships/uncertainty levels, do not add mechanisms/capabilities/results/numbers, distinguish between close technical concepts based on context, use clear sentences, describe AI capabilities accurately without overstating autonomy/uncertainty.
    *   **Input Text:** "ممكن يكون فيه تحيز بالنتائج إذا البيانات اللي تدرب عليها النموذج ما كانت متوازنة." (It might have bias in the results if the data the model was trained on was not balanced.)

2.  **Analyze the Input Text:**
    *   **Meaning:** The text states a potential issue (bias in results) arising from a specific condition (unbalanced training data).
    *   **Tone:** Inform

## P06

**Input:** النماذج التوليدية تقدر تنتج نصوص وصور ومحتوى جديد اعتمادا على الأشياء اللي تعلمتها.

### D0_saleem_only

Thinking Process:

1.  **Analyze the Request:**
    *   **Task:** Rewrite the given Arabic text to make it clearer and more accurate (أوضح وأدق) while preserving its meaning (مع الحفاظ على معناه).
    *   **Constraint 1:** Do not add facts or information not present in the original text (لا تضف حقائق أو معلومات غير موجودة في النص).
    *   **Constraint 2:** Output only the rewritten text, no explanation (أعد النص المصاغ فقط دون شرح).
    *   **Input Text:** "النماذج التوليدية تقدر تنتج نصوص وصور ومحتوى جديد اعتمادا على الأشياء اللي تعلمتها." (Generative models can produce new texts, images, and content based on the things they learned.)

2.  **Analyze the Input Text:**
    *   **Subject:** النماذج التوليدية (Generative models).
    *   **Action:** تقدر تنتج (can produce) -> نصوص وصور ومحتوى جديد (texts, images, and new content).
    *   **Condition/Basis:** اعتمادا على (based on) -> الأشياء اللي تعلمتها (the things they

### D1_domain_name

Thinking Process:

1.  **Analyze the Request:**
    *   **Task:** Rewrite the given Arabic text to make it clearer and more accurate (أوضح وأدق) while preserving its meaning (مع الحفاظ على معناه).
    *   **Constraint 1:** Do not add facts or information not present in the original text (لا تضف حقائق أو معلومات غير موجودة في النص).
    *   **Constraint 2:** Output only the rewritten text, no explanation (أعد النص المصاغ فقط دون شرح).
    *   **Domain:** Artificial Intelligence (ذكاء اصطناعي).
    *   **Original Text:** "النماذج التوليدية تقدر تنتج نصوص وصور ومحتوى جديد اعتمادا على الأشياء اللي تعلمتها." (Generative models can produce new texts, images, and content based on the things they learned.)

2.  **Analyze the Original Text:**
    *   **Subject:** النماذج التوليدية (Generative models).
    *   **Action:** تقدر تنتج (can produce) -> نصوص وصور ومحتوى جديد (texts, images, and new content).
    *   **Condition/Basis:**

### D2_domain_name_definition

Thinking Process:

1.  **Analyze the Request:**
    *   **Task:** Rewrite the given Arabic text to make it clearer and more accurate (أوضح وأدق) while preserving its meaning (مع الحفاظ على معناه).
    *   **Constraint 1:** Do not add facts or information not present in the original text (لا تضف حقائق أو معلومات غير موجودة في النص).
    *   **Constraint 2:** Output only the rewritten text, no explanation (أعد النص المصاغ فقط دون شرح).
    *   **Context:** The field is Artificial Intelligence (الذكاء الاصطناعي).
    *   **Input Text to Improve:** "النماذج التوليدية تقدر تنتج نصوص وصور ومحتوى جديد اعتمادا على الأشياء اللي تعلمتها." (Generative models can produce new texts, images, and content based on the things they learned.)

2.  **Analyze the Input Text:**
    *   *Subject:* النماذج التوليدية (Generative models).
    *   *Action:* تقدر تنتج (can produce) -> نصوص وصور ومحتوى جديد (texts, images, and new content).
    *

### D3_domain_guidance

Thinking Process:

1.  **Analyze the Request:**
    *   **Task:** Rewrite the given Arabic text to be clearer and more accurate while preserving its meaning.
    *   **Constraint 1:** Do not add facts or information not present in the original text.
    *   **Constraint 2:** Output only the rewritten text, no explanation.
    *   **Domain:** Artificial Intelligence (AI).
    *   **Input Text:** "النماذج التوليدية تقدر تنتج نصوص وصور ومحتوى جديد اعتمادا على الأشياء اللي تعلمتها." (Generative models can produce new texts, images, and content based on the things they learned.)
    *   **Guidelines:** Use precise terminology, maintain consistency, improve phrasing without changing facts/relationships/uncertainty, do not add mechanisms/capabilities/results/numbers, distinguish between close concepts, use clear sentences, describe capabilities accurately without overstating autonomy/uncertainty.

2.  **Analyze the Input Text:**
    *   "النماذج التوليدية" (Generative models) - This is a specific AI term.
    *   "تقدر تنتج" (can produce) - Slightly

### D4_domain_guidance_examples

Thinking Process:

1.  **Analyze the Request:**
    *   **Task:** Rewrite the given Arabic text to be clearer and more accurate while preserving its meaning.
    *   **Constraint 1:** Do not add facts or information not present in the original text.
    *   **Constraint 2:** Output only the rewritten text, no explanations.
    *   **Domain:** Artificial Intelligence (AI).
    *   **Guidelines:** Use precise terminology, maintain consistency, improve phrasing without changing facts/relationships/uncertainty, do not add mechanisms/capabilities/results/technical numbers, distinguish between close concepts based on context, use clear sentences, describe capabilities accurately without overstating autonomy/uncertainty.
    *   **Input Text:** "النماذج التوليدية تقدر تنتج نصوص وصور ومحتوى جديد اعتمادا على الأشياء اللي تعلمتها." (Generative models can produce new texts, images, and content based on the things they learned.)

2.  **Analyze the Input Text:**
    *   **Subject:** النماذج التوليدية (Generative models).
    *   **Action:** تقدر تنتج (can produce) -> نصوص وصور

## P07

**Input:** التعلم المعزز يعتمد على المحاولة والتغذية الراجعة عشان يتعلم النظام وش التصرف الأفضل.

### D0_saleem_only

Thinking Process:

1.  **Analyze the Request:**
    *   **Task:** Rewrite the given Arabic text to make it clearer and more accurate (أوضح وأدق) while preserving its meaning (مع الحفاظ على معناه).
    *   **Constraint 1:** Do not add facts or information not present in the original text (لا تضف حقائق أو معلومات غير موجودة في النص).
    *   **Constraint 2:** Output only the rewritten text, no explanation (أعد النص المصاغ فقط دون شرح).
    *   **Input Text:** "التعلم المعزز يعتمد على المحاولة والتغذية الراجعة عشان يتعلم النظام وش التصرف الأفضل."

2.  **Analyze the Input Text:**
    *   **Meaning:** Reinforcement learning relies on trial and feedback so the system learns the best action.
    *   **Issues:**
        *   "عشان" is colloquial (for "لأنه" or "لكي").
        *   "ش" is colloquial (for "أفضل" or "ما").
        *   "التغذية الراجعة" is correct but could be phrased more formally depending on context,

### D1_domain_name

Thinking Process:

1.  **Analyze the Request:**
    *   **Task:** Rewrite the given Arabic text to make it clearer and more accurate (أوضح وأدق) while preserving its meaning (مع الحفاظ على معناه).
    *   **Constraint 1:** Do not add facts or information not present in the original text (لا تضف حقائق أو معلومات غير موجودة في النص).
    *   **Constraint 2:** Output only the rewritten text, no explanation (أعد النص المصاغ فقط دون شرح).
    *   **Domain:** Artificial Intelligence (الذكاء الاصطناعي).
    *   **Original Text:** "التعلم المعزز يعتمد على المحاولة والتغذية الراجعة عشان يتعلم النظام وش التصرف الأفضل." (Reinforcement learning relies on trial and feedback so the system learns what the best action is.)

2.  **Analyze the Original Text:**
    *   **Meaning:** Reinforcement learning (RL) works through trial and feedback. The goal is for the system to learn the best action/behavior.
    *   **Issues:**
        *   "عشان" (Eshan) is colloquial/informal.
        *

### D2_domain_name_definition

Thinking Process:

1.  **Analyze the Request:**
    *   **Task:** Rewrite the given Arabic text to make it clearer and more precise (أوضح وأدق) while preserving its meaning (مع الحفاظ على معناه).
    *   **Constraint 1:** Do not add facts or information not present in the original text (لا تضف حقائق أو معلومات غير موجودة في النص).
    *   **Constraint 2:** Output only the rewritten text, no explanation (أعد النص المصاغ فقط دون شرح).
    *   **Context:** The field is Artificial Intelligence (ذكاء اصطناعي).
    *   **Input Text:** "التعلم المعزز يعتمد على المحاولة والتغذية الراجعة عشان يتعلم النظام وش التصرف الأفضل." (Reinforcement learning relies on trial and feedback for the system to learn what the best action is.)

2.  **Analyze the Input Text:**
    *   **Subject:** التعلم المعزز (Reinforcement Learning).
    *   **Mechanism:** المحاولة والتغذية الراجعة (Trial and feedback).
    *   **Purpose/Goal:** يتعلم النظام وش التصرف الأفضل (The system learns what the best action is

### D3_domain_guidance

Thinking Process:

1.  **Analyze the Request:**
    *   **Task:** Rewrite the given Arabic text to be clearer and more accurate while preserving its meaning.
    *   **Constraint 1:** Do not add facts or information not present in the original text.
    *   **Constraint 2:** Output only the rewritten text, no explanation.
    *   **Domain:** Artificial Intelligence (AI).
    *   **Input Text:** "التعلم المعزز يعتمد على المحاولة والتغذية الراجعة عشان يتعلم النظام وش التصرف الأفضل." (Reinforcement learning relies on trial and feedback for the system to learn and the best action.)
    *   **Guidelines:** Use precise terminology, maintain consistency, improve phrasing without changing facts/relationships/uncertainty, do not add mechanisms/capabilities/results/numbers, distinguish between close technical concepts based on context, use clear sentences, describe AI capabilities accurately without overstating.

2.  **Analyze the Input Text:**
    *   "التعلم المعزز" (Reinforcement Learning - RL): This is a specific AI term.
    *   "يعتمد على المحاولة والتغذية الراجعة" (relies on trial

### D4_domain_guidance_examples

Thinking Process:

1.  **Analyze the Request:**
    *   **Task:** Rewrite the given Arabic text to be clearer and more accurate while preserving its meaning.
    *   **Constraint 1:** Do not add facts or information not present in the original text.
    *   **Constraint 2:** Output only the rewritten text, no explanations.
    *   **Domain:** Artificial Intelligence (AI).
    *   **Guidelines:** Use precise terminology, maintain consistency, improve phrasing without changing facts/relationships/uncertainty, do not add mechanisms/capabilities/results/numbers, distinguish between close technical concepts based on context, use clear/direct sentences, describe AI capabilities accurately without overstating autonomy/uncertainty.
    *   **Input Text:** "التعلم المعزز يعتمد على المحاولة والتغذية الراجعة عشان يتعلم النظام وش التصرف الأفضل." (Reinforcement learning relies on trial and feedback so the system learns what the best action is.)

2.  **Analyze the Input Text:**
    *   **Content:** It describes Reinforcement Learning (RL).
    *   **Key Concepts:** Trial and feedback (المحاولة والتغذية الراجعة), System learning (يت

## P08

**Input:** معالجة اللغة تساعد الكمبيوتر يفهم النصوص ويحلل معناها ويستخرج منها معلومات.

### D0_saleem_only

Thinking Process:

1.  **Analyze the Request:**
    *   **Task:** Rewrite the given Arabic text to make it clearer and more accurate (أوضح وأدق) while preserving its meaning (مع الحفاظ على معناه).
    *   **Constraint 1:** Do not add facts or information not present in the original text (لا تضف حقائق أو معلومات غير موجودة في النص).
    *   **Constraint 2:** Output only the rewritten text, no explanation (أعد النص المصاغ فقط دون شرح).
    *   **Input Text:** "معالجة اللغة تساعد الكمبيوتر يفهم النصوص ويحلل معناها ويستخرج منها معلومات." (Natural Language Processing helps the computer understand texts and analyze their meaning and extract information from them.)

2.  **Analyze the Input Text:**
    *   **Subject:** معالجة اللغة (Natural Language Processing - NLP).
    *   **Action:** تساعد (helps).
    *   **Object:** الكمبيوتر (the computer).
    *   **Functions:** يفهم النصوص (understand texts), ويحلل معناها (analyze their meaning), ويستخرج منها معلومات (extract information from them).
    *   **Grammar Issue:** "

### D1_domain_name

Thinking Process:

1.  **Analyze the Request:**
    *   **Task:** Rewrite the given Arabic text to make it clearer and more accurate (أوضح وأدق) while preserving its meaning (مع الحفاظ على معناه).
    *   **Constraint 1:** Do not add facts or information not present in the original text (لا تضف حقائق أو معلومات غير موجودة في النص).
    *   **Constraint 2:** Output only the rewritten text, no explanation (أعد النص المصاغ فقط دون شرح).
    *   **Domain:** Artificial Intelligence (ذكاء اصطناعي).
    *   **Original Text:** "معالجة اللغة تساعد الكمبيوتر يفهم النصوص ويحلل معناها ويستخرج منها معلومات." (Natural Language Processing helps the computer understand texts and analyze their meaning and extract information from them.)

2.  **Analyze the Original Text:**
    *   **Subject:** معالجة اللغة (Natural Language Processing - NLP).
    *   **Verb:** تساعد (helps).
    *   **Object:** الكمبيوتر (the computer).
    *   **Actions:** يفهم النصوص (understand texts), ويحلل معناها (analyze their meaning), ويستخرج منها

### D2_domain_name_definition

Thinking Process:

1.  **Analyze the Request:**
    *   **Task:** Rewrite the given Arabic text to make it clearer and more precise while maintaining its original meaning.
    *   **Constraint 1:** Do not add facts or information not present in the original text.
    *   **Constraint 2:** Output only the rewritten text, without explanation.
    *   **Input Text:** "معالجة اللغة تساعد الكمبيوتر يفهم النصوص ويحلل معناها ويستخرج منها معلومات." (Natural Language Processing helps the computer understand texts and analyze their meaning and extract information from them.)
    *   **Context:** The field is Artificial Intelligence (ذكاء اصطناعي).
    *   **Goal:** Improve clarity and precision (أوضح وأدق).

2.  **Analyze the Input Text:**
    *   "معالجة اللغة" (Natural Language Processing - NLP): This is a field/technology.
    *   "تساعد الكمبيوتر" (helps the computer): A bit informal. "تساعد" (helps) is okay, but "تمنح" (empowers) or "تتيح" (enables) might be better, but I must stick to the

### D3_domain_guidance

Thinking Process:

1.  **Analyze the Request:**
    *   **Task:** Rewrite the given Arabic text to make it clearer and more precise while maintaining its original meaning.
    *   **Constraint 1:** Do not add facts or information not present in the original text.
    *   **Constraint 2:** Output only the rewritten text, no explanation.
    *   **Domain:** Artificial Intelligence (AI).
    *   **Guidelines:** Use precise terminology, maintain consistency, improve phrasing without changing facts/relationships/uncertainty, do not add mechanisms/capabilities/results/numbers, distinguish between similar technical concepts based on context, use clear and direct sentences, describe AI system capabilities accurately without overstating understanding/independence/uncertainty.
    *   **Input Text:** "معالجة اللغة تساعد الكمبيوتر يفهم النصوص ويحلل معناها ويستخرج منها معلومات." (Natural Language Processing helps the computer understand texts and analyze their meaning and extract information from them.)

2.  **Analyze the Input Text:**
    *   **Subject:** معالجة اللغة (Natural Language Processing - NLP).
    *   **Action:** تساعد (helps) -> This is a bit weak. In the context of

### D4_domain_guidance_examples

Thinking Process:

1.  **Analyze the Request:**
    *   **Task:** Rewrite the given Arabic text to make it clearer and more accurate while preserving its meaning.
    *   **Constraint 1:** Do not add facts or information not present in the original text.
    *   **Constraint 2:** Output only the rewritten text, no explanation.
    *   **Domain:** Artificial Intelligence (AI).
    *   **Guidelines:** Use precise terminology, maintain consistency, improve phrasing without changing facts/relationships/uncertainty, do not add mechanisms/capabilities/results/numbers, distinguish between close technical concepts based on context, use clear/direct sentences, describe capabilities accurately without overstating independence/uncertainty.
    *   **Input Text:** "معالجة اللغة تساعد الكمبيوتر يفهم النصوص ويحلل معناها ويستخرج منها معلومات." (Natural Language Processing helps the computer understand texts and analyze their meaning and extract information from them.)

2.  **Analyze the Input Text:**
    *   **Subject:** معالجة اللغة (Natural Language Processing - NLP).
    *   **Action:** تساعد (helps) -> This is a bit informal. Better to say "تهدف إلى" (

## P09

**Input:** الرؤية الحاسوبية تستخدم نماذج لتحليل الصور والتعرف على الأشياء الموجودة فيها.

### D0_saleem_only

Thinking Process:

1.  **Analyze the Request:**
    *   **Task:** Rewrite the given Arabic text to make it clearer and more precise (أوضح وأدق) while preserving its meaning (مع الحفاظ على معناه).
    *   **Constraint 1:** Do not add facts or information not present in the original text (لا تضف حقائق أو معلومات غير موجودة في النص).
    *   **Constraint 2:** Output only the rewritten text, no explanation (أعد النص المصاغ فقط دون شرح).
    *   **Input Text:** "الرؤية الحاسوبية تستخدم نماذج لتحليل الصور والتعرف على الأشياء الموجودة فيها." (Computer vision uses models to analyze images and recognize the objects present in them.)

2.  **Analyze the Input Text:**
    *   Subject: الرؤية الحاسوبية (Computer Vision).
    *   Action: تستخدم نماذج (uses models).
    *   Purpose/Function: لتحليل الصور (to analyze images) والتعرف على الأشياء الموجودة فيها (and recognize the objects present in them).
    *   Meaning: Computer vision employs models for image analysis and object recognition.

3.  **Identify Areas for Improvement (Clarity & Precision

### D1_domain_name

Thinking Process:

1.  **Analyze the Request:**
    *   **Task:** Rewrite the given Arabic text to make it clearer and more precise (أوضح وأدق) while preserving its meaning (مع الحفاظ على معناه).
    *   **Constraint 1:** Do not add facts or information not present in the original text (لا تضف حقائق أو معلومات غير موجودة في النص).
    *   **Constraint 2:** Output only the rewritten text, no explanation (أعد النص المصاغ فقط دون شرح).
    *   **Domain:** Artificial Intelligence (ذكاء اصطناعي).
    *   **Original Text:** "الرؤية الحاسوبية تستخدم نماذج لتحليل الصور والتعرف على الأشياء الموجودة فيها." (Computer vision uses models to analyze images and recognize the objects present in them.)

2.  **Analyze the Original Text:**
    *   Subject: الرؤية الحاسوبية (Computer Vision).
    *   Action: تستخدم نماذج (uses models).
    *   Purpose/Function: لتحليل الصور (to analyze images) والتعرف على الأشياء الموجودة فيها (and recognize the objects present in them).
    *   Meaning: Computer vision employs models for image analysis and object recognition

### D2_domain_name_definition

Thinking Process:

1.  **Analyze the Request:**
    *   **Task:** Rewrite the given Arabic text to make it clearer and more precise while maintaining its original meaning.
    *   **Constraint 1:** Do not add facts or information not present in the original text.
    *   **Constraint 2:** Output only the rewritten text, without explanation.
    *   **Domain:** Artificial Intelligence (ذكاء اصطناعي).
    *   **Input Text:**
        *   Definition of the field: "مجال يختص بالأنظمة الحاسوبية القادرة على استنتاج مخرجات، مثل التنبؤات أو المحتوى أو التوصيات أو القرارات، اعتمادًا على مدخلات تستقبلها، وقد تختلف هذه الأنظمة في مستويات الاستقلالية والتكيف بعد النشر."
        *   Target Text to Improve: "الرؤية الحاسوبية تستخدم نماذج لتحليل الصور والتعرف على الأشياء الموجودة فيها."

2.  **Analyze the Input Text (Target Text):**
    *   "الرؤية الحاسوبية" (Computer Vision)
    *   "تستخدم نماذج" (uses models)
    *   "لتحليل الصور" (to analyze images)

### D3_domain_guidance

Thinking Process:

1.  **Analyze the Request:**
    *   **Task:** Rewrite the given Arabic text to be clearer and more precise while maintaining its original meaning.
    *   **Constraint 1:** Do not add facts or information not present in the original text.
    *   **Constraint 2:** Output only the rewritten text, no explanations.
    *   **Domain:** Artificial Intelligence (AI).
    *   **Input Text:** "الرؤية الحاسوبية تستخدم نماذج لتحليل الصور والتعرف على الأشياء الموجودة فيها." (Computer Vision uses models to analyze images and recognize objects present in them.)
    *   **Guidelines:** Use precise terminology, maintain consistency, improve phrasing without changing facts/relationships/uncertainty, do not add mechanisms/capabilities/results/numbers, distinguish between close concepts based on context, use clear sentences, describe capabilities accurately without overstating autonomy/uncertainty.

2.  **Analyze the Input Text:**
    *   "الرؤية الحاسوبية" (Computer Vision) - This is the domain/sub-field.
    *   "تستخدم نماذج" (uses models) - General statement about methodology.
    *   "لتحليل الصور"

### D4_domain_guidance_examples

Thinking Process:

1.  **Analyze the Request:**
    *   **Task:** Rewrite the given Arabic text to make it clearer and more precise while maintaining its original meaning.
    *   **Constraint 1:** Do not add facts or information not present in the original text.
    *   **Constraint 2:** Output only the rewritten text, no explanations.
    *   **Domain:** Artificial Intelligence (AI).
    *   **Guidelines:** Use precise terminology, maintain consistency, improve phrasing without changing facts/relationships/uncertainty, do not add mechanisms/capabilities/results/numbers, distinguish between close concepts based on context, use clear sentences, describe capabilities accurately without overstating autonomy/uncertainty.
    *   **Input Text:** "الرؤية الحاسوبية تستخدم نماذج لتحليل الصور والتعرف على الأشياء الموجودة فيها." (Computer Vision uses models to analyze images and recognize objects present in them.)

2.  **Analyze the Input Text:**
    *   **Subject:** الرؤية الحاسوبية (Computer Vision).
    *   **Action:** تستخدم نماذج (uses models).
    *   **Purpose:** لتحليل الصور (to analyze images) والتعرف على الأشياء الموجودة فيها (and

## P10

**Input:** إذا حفظ النموذج بيانات التدريب بشكل كبير ممكن يصير ممتاز عليها لكن ضعيف على بيانات جديدة.

### D0_saleem_only

Thinking Process:

1.  **Analyze the Request:**
    *   **Task:** Rewrite the given Arabic text to make it clearer and more accurate (أوضح وأدق) while preserving its meaning (مع الحفاظ على معناه).
    *   **Constraint 1:** Do not add facts or information not present in the original text (لا تضف حقائق أو معلومات غير موجودة في النص).
    *   **Constraint 2:** Output only the rewritten text, no explanation (أعد النص المصاغ فقط دون شرح).
    *   **Input Text:** "إذا حفظ النموذج بيانات التدريب بشكل كبير ممكن يصير ممتاز عليها لكن ضعيف على بيانات جديدة." (If the model saves/learns training data significantly, it can be excellent on them but weak on new data.)

2.  **Analyze the Input Text:**
    *   **Meaning:** The text describes a phenomenon in machine learning (overfitting). If a model memorizes or learns training data very well, it performs well on that specific data but poorly on unseen/new data.
    *   **Issues in Original:**
        *   "حفظ" (save) is slightly inaccurate terminology for "learning" or "memorizing

### D1_domain_name

Thinking Process:

1.  **Analyze the Request:**
    *   **Task:** Rewrite the given Arabic text to make it clearer and more accurate (أوضح وأدق) while preserving its meaning (مع الحفاظ على معناه).
    *   **Constraint 1:** Do not add facts or information not present in the original text (لا تضف حقائق أو معلومات غير موجودة في النص).
    *   **Constraint 2:** Output only the rewritten text, no explanation (أعد النص المصاغ فقط دون شرح).
    *   **Domain:** Artificial Intelligence (الذكاء الاصطناعي).
    *   **Original Text:** "إذا حفظ النموذج بيانات التدريب بشكل كبير ممكن يصير ممتاز عليها لكن ضعيف على بيانات جديدة." (If the model saves/learns training data significantly, it can become excellent on them but weak on new data.)

2.  **Analyze the Original Text:**
    *   **Meaning:** When a machine learning model is trained extensively on a specific dataset, it performs well on that same data (overfitting implication) but performs poorly on unseen/new data (generalization problem).
    *   **Issues:**
        *   "يحفظ" (s

### D2_domain_name_definition

Thinking Process:

1.  **Analyze the Request:**
    *   **Task:** Rewrite the given Arabic text to make it clearer and more accurate while preserving its meaning.
    *   **Constraint 1:** Do not add facts or information not present in the original text.
    *   **Constraint 2:** Output only the rewritten text, no explanation.
    *   **Context:** The field is Artificial Intelligence (AI).
    *   **Input Text to Improve:** "إذا حفظ النموذج بيانات التدريب بشكل كبير ممكن يصير ممتاز عليها لكن ضعيف على بيانات جديدة." (If the model saves training data significantly, it can become excellent on them but weak on new data.)

2.  **Analyze the Input Text:**
    *   **Meaning:** The sentence describes a phenomenon in machine learning (overfitting). It says if a model memorizes or stores training data extensively, it performs well on that specific data but poorly on new/unseen data.
    *   **Issues:**
        *   "إذا حفظ النموذج بيانات التدريب بشكل كبير" (If the model saves training data significantly): "حفظ" (save) is a bit colloquial or imprecise in this context. "

### D3_domain_guidance

Thinking Process:

1.  **Analyze the Request:**
    *   **Task:** Rewrite the given Arabic text to be clearer and more accurate while preserving its meaning.
    *   **Constraint 1:** Do not add facts or information not present in the original text.
    *   **Constraint 2:** Output only the rewritten text, no explanation.
    *   **Domain:** Artificial Intelligence (AI).
    *   **Guidelines:** Use precise terminology, maintain consistency, improve phrasing without changing facts/relationships/uncertainty, do not add mechanisms/capabilities/results/numbers, distinguish between similar technical concepts based on context, use clear sentences, describe AI capabilities accurately without overstating autonomy/uncertainty.
    *   **Input Text:** "إذا حفظ النموذج بيانات التدريب بشكل كبير ممكن يصير ممتاز عليها لكن ضعيف على بيانات جديدة." (If the model saves training data significantly it can become excellent on them but weak on new data.)

2.  **Analyze the Input Text:**
    *   **Meaning:** The text describes a phenomenon in machine learning/AI where a model performs well on training data (memorization/overfitting) but poorly on new/unseen data (generalization

### D4_domain_guidance_examples

Thinking Process:

1.  **Analyze the Request:**
    *   **Task:** Rewrite the given Arabic text to be clearer and more accurate while preserving its meaning.
    *   **Constraint 1:** Do not add facts or information not present in the original text.
    *   **Constraint 2:** Output only the rewritten text, no explanations.
    *   **Domain:** Artificial Intelligence (AI).
    *   **Guidelines:** Use precise terminology, maintain consistency, improve phrasing without changing facts/relationships/uncertainty, do not add mechanisms/capabilities/results/numbers, distinguish between similar technical concepts based on context, use clear sentences, describe capabilities accurately without overstating independence/uncertainty.
    *   **Input Text:** "إذا حفظ النموذج بيانات التدريب بشكل كبير ممكن يصير ممتاز عليها لكن ضعيف على بيانات جديدة." (If the model saves training data significantly it can become excellent on them but weak on new data.)

2.  **Analyze the Input Text:**
    *   **Meaning:** The text describes a phenomenon where a model performs well on training data (if it memorizes/saves it) but poorly on new/unseen data. This is essentially describing overfitting (

## P11

**Input:** دالة الخسارة تعطينا قيمة تبين الفرق بين ناتج النموذج والنتيجة المطلوبة أثناء التدريب.

### D0_saleem_only

Thinking Process:

1.  **Analyze the Request:**
    *   Task: Rewrite the given Arabic text to make it clearer and more accurate (أوضح وأدق) while preserving its meaning (مع الحفاظ على معناه).
    *   Constraint 1: Do not add facts or information not present in the original text (لا تضف حقائق أو معلومات غير موجودة في النص).
    *   Constraint 2: Output only the rewritten text, no explanation (أعد النص المصاغ فقط دون شرح).
    *   Input Text: "دالة الخسارة تعطينا قيمة تبين الفرق بين ناتج النموذج والنتيجة المطلوبة أثناء التدريب." (The loss function gives us a value that shows the difference between the model's output and the desired result during training.)

2.  **Analyze the Input Text:**
    *   Subject: دالة الخسارة (Loss function).
    *   Action: تعطينا قيمة (gives us a value).
    *   Purpose: تبين الفرق بين ناتج النموذج والنتيجة المطلوبة (shows the difference between the model's output and the desired result).
    *   Context: أثناء التدريب (during training).
    *   Meaning:

### D1_domain_name

Thinking Process:

1.  **Analyze the Request:**
    *   **Task:** Rewrite the given Arabic text to make it clearer and more accurate (أوضح وأدق) while preserving its meaning (مع الحفاظ على معناه).
    *   **Constraint 1:** Do not add facts or information not present in the original text (لا تضف حقائق أو معلومات غير موجودة في النص).
    *   **Constraint 2:** Output only the rewritten text, no explanation (أعد النص المصاغ فقط دون شرح).
    *   **Domain:** Artificial Intelligence (الذكاء الاصطناعي).
    *   **Original Text:** "دالة الخسارة تعطينا قيمة تبين الفرق بين ناتج النموذج والنتيجة المطلوبة أثناء التدريب." (The loss function gives us a value that shows the difference between the model's output and the desired result during training.)

2.  **Analyze the Original Text:**
    *   "دالة الخسارة" (Loss function) - Correct term.
    *   "تعطينا قيمة" (gives us a value) - A bit colloquial. "تُقدّم قيمة" or "تُحسب قيمة" might be

### D2_domain_name_definition

Thinking Process:

1.  **Analyze the Request:**
    *   **Task:** Rewrite the given Arabic text to make it clearer and more precise while maintaining its meaning.
    *   **Constraint 1:** Do not add facts or information not present in the original text.
    *   **Constraint 2:** Output only the rewritten text, without explanation.
    *   **Input Text:** "دالة الخسارة تعطينا قيمة تبين الفرق بين ناتج النموذج والنتيجة المطلوبة أثناء التدريب." (The loss function gives us a value that shows the difference between the model's output and the desired result during training.)
    *   **Context:** The field is Artificial Intelligence (ذكاء اصطناعي), and there's a provided definition of the field at the beginning, but the specific text to rewrite is the sentence about the loss function.
    *   **Goal:** Improve clarity and precision without altering the core meaning.

2.  **Analyze the Input Text:**
    *   "دالة الخسارة" (Loss function) - Correct term.
    *   "تعطينا قيمة" (gives us a value) - A bit colloquial. "تُقدّم قيمة"

### D3_domain_guidance

Thinking Process:

1.  **Analyze the Request:**
    *   **Task:** Rewrite the given Arabic text to be clearer and more precise while maintaining its original meaning.
    *   **Constraint 1:** Do not add facts or information not present in the original text.
    *   **Constraint 2:** Output only the rewritten text, no explanations.
    *   **Domain:** Artificial Intelligence (AI).
    *   **Input Text:** "دالة الخسارة تعطينا قيمة تبين الفرق بين ناتج النموذج والنتيجة المطلوبة أثناء التدريب." (Loss function gives us a value that shows the difference between the model's output and the desired result during training.)
    *   **Guidelines:** Use precise terminology, maintain consistency, improve phrasing without changing facts/relationships/uncertainty, do not add mechanisms/capabilities/results/numbers, distinguish between close technical concepts based on context, use clear sentences, describe capabilities accurately without overstating.

2.  **Analyze the Input Text:**
    *   "دالة الخسارة" (Loss function) - Technical term, keep as is.
    *   "تعطينا قيمة" (gives us a value) - Can be improved

### D4_domain_guidance_examples

Thinking Process:

1.  **Analyze the Request:**
    *   **Task:** Rewrite the given Arabic text to make it clearer and more precise while maintaining its original meaning.
    *   **Constraint 1:** Do not add facts or information not present in the original text.
    *   **Constraint 2:** Output only the rewritten text, no explanations.
    *   **Domain:** Artificial Intelligence (AI).
    *   **Guidelines:** Use precise technical terminology, maintain consistency in terminology, improve phrasing without changing facts/relationships/uncertainty levels, do not add mechanisms/capabilities/results/technical numbers, distinguish between close technical concepts based on context, use clear and direct sentences, describe AI system capabilities accurately without overstating understanding/independence/uncertainty.
    *   **Input Text:** "دالة الخسارة تعطينا قيمة تبين الفرق بين ناتج النموذج والنتيجة المطلوبة أثناء التدريب." (The loss function gives us a value that shows the difference between the model's output and the desired result during training.)

2.  **Analyze the Input Text:**
    *   **Subject:** دالة الخسارة (Loss Function).
    *   **Action:** تعطينا قيمة

## P12

**Input:** نحتاج نقيم النموذج بأكثر من مقياس لأن الدقة وحدها مو دائما كافية للحكم على الأداء.

### D0_saleem_only

Thinking Process:

1.  **Analyze the Request:**
    *   **Task:** Rewrite the given Arabic text to make it clearer and more accurate (أوضح وأدق) while preserving its meaning (مع الحفاظ على معناه).
    *   **Constraint 1:** Do not add facts or information not present in the original text (لا تضف حقائق أو معلومات غير موجودة في النص).
    *   **Constraint 2:** Output only the rewritten text, no explanation (أعد النص المصاغ فقط دون شرح).
    *   **Input Text:** "نحتاج نقيم النموذج بأكثر من مقياس لأن الدقة وحدها مو دائما كافية للحكم على الأداء."

2.  **Analyze the Input Text:**
    *   **Grammar/Spelling Errors:**
        *   "نحتاج نقيم" -> Should be "نحتاج أن نقيم" or "نحتاج إلى تقييم".
        *   "مو" -> Typo for "مُ" (مُ) or "مُ" (مُ). Context suggests "مُ" (not always).
        *   "أكثر من مقياس" -> "أكثر من مقياس" is

### D1_domain_name

Thinking Process:

1.  **Analyze the Request:**
    *   **Task:** Rewrite the given Arabic text to make it clearer and more accurate (أوضح وأدق) while preserving its meaning.
    *   **Constraint 1:** Do not add facts or information not present in the original text (لا تضف حقائق أو معلومات غير موجودة في النص).
    *   **Constraint 2:** Output only the rewritten text, no explanation (أعد النص المصاغ فقط دون شرح).
    *   **Domain:** Artificial Intelligence (ذكاء اصطناعي).
    *   **Original Text:** "نحتاج نقيم النموذج بأكثر من مقياس لأن الدقة وحدها مو دائما كافية للحكم على الأداء." (Note: There are typos in the original text: "نحتاج نقيم" should be "نحتاج أن نقيم", "مو" should be "مُ").

2.  **Analyze the Original Text:**
    *   *Meaning:* We need to evaluate the model using multiple metrics because accuracy alone is not always sufficient to judge performance.
    *   *Issues:*
        *   Grammar: "نحتاج نقيم" -> "نحتاج أن

### D2_domain_name_definition

Thinking Process:

1.  **Analyze the Request:**
    *   **Task:** Rewrite the given Arabic text to make it clearer and more accurate while preserving its meaning.
    *   **Constraint 1:** Do not add facts or information not present in the original text.
    *   **Constraint 2:** Output only the rewritten text, no explanation.
    *   **Input Text:**
        *   Field: Artificial Intelligence (المجال: الذكاء الاصطناعي)
        *   Definition: A field concerned with computer systems capable of inferring outputs, such as predictions, content, recommendations, or decisions, based on inputs they receive, and these systems may vary in levels of autonomy and adaptability after deployment. (المجال: مجال يختص بالأنظمة الحاسوبية القادرة على استنتاج مخرجات، مثل التنبؤات أو المحتوى أو التوصيات أو القرارات، اعتمادًا على مدخلات تستقبلها، وقد تختلف هذه الأنظمة في مستويات الاستقلالية والتكيف بعد النشر.)
        *   Text to Improve: We need to evaluate the model with more than one metric because accuracy alone is not always sufficient to judge performance. (نحتاج نقيم النموذج بأكثر من مقياس

### D3_domain_guidance

Thinking Process:

1.  **Analyze the Request:**
    *   **Task:** Rewrite the given Arabic text to be clearer and more accurate while preserving its meaning.
    *   **Constraint 1:** Do not add facts or information not present in the original text.
    *   **Constraint 2:** Output only the rewritten text, no explanation.
    *   **Domain:** Artificial Intelligence (AI).
    *   **Input Text:** "نحتاج نقيم النموذج بأكثر من مقياس لأن الدقة وحدها مو دائما كافية للحكم على الأداء." (Note: There are typos in the input: "نحتاج نقيم" should be "نحتاج أن نقيم", "مو" should be "مُ").
    *   **Guidelines:** Use precise terminology, maintain consistency, improve phrasing without changing facts/relationships/uncertainty, do not add mechanisms/capabilities/results/numbers, distinguish between close concepts, use clear sentences, describe capabilities accurately without overstating.

2.  **Analyze the Input Text:**
    *   "نحتاج نقيم النموذج بأكثر من مقياس" -> We need to evaluate the model with more than one metric.

### D4_domain_guidance_examples

Thinking Process:

1.  **Analyze the Request:**
    *   **Task:** Rewrite the given Arabic text to make it clearer and more precise while maintaining its original meaning.
    *   **Constraint 1:** Do not add facts or information not present in the original text.
    *   **Constraint 2:** Output only the rewritten text, no explanations.
    *   **Domain:** Artificial Intelligence (AI).
    *   **Guidelines:** Use precise terminology, maintain consistency, improve phrasing without changing facts/relationships/uncertainty levels, do not add mechanisms/capabilities/results/numbers, distinguish between close technical concepts based on context, use clear and direct sentences, describe AI capabilities accurately without overstating understanding/independence/uncertainty.
    *   **Input Text:** "نحتاج نقيم النموذج بأكثر من مقياس لأن الدقة وحدها مو دائما كافية للحكم على الأداء." (Note: There are typos in the input: "نحتاج نقيم" should be "نحتاج أن نقيم", "مو" should be "مُ").

2.  **Analyze the Input Text:**
    *   Sentence 1: "نحتاج نقيم النموذج بأكثر

## P13

**Input:** الشبكات العصبية فيها طبقات تعالج المدخلات بالتدريج إلى أن تنتج النتيجة النهائية.

### D0_saleem_only

Thinking Process:

1.  **Analyze the Request:**
    *   **Task:** Rewrite the given Arabic text to make it clearer and more accurate (أوضح وأدق) while preserving its meaning (مع الحفاظ على معناه).
    *   **Constraint 1:** Do not add facts or information not present in the original text (لا تضف حقائق أو معلومات غير موجودة في النص).
    *   **Constraint 2:** Output only the rewritten text, no explanation (أعد النص المصاغ فقط دون شرح).
    *   **Input Text:** "الشبكات العصبية فيها طبقات تعالج المدخلات بالتدريج إلى أن تنتج النتيجة النهائية." (Neural networks have layers that process inputs gradually to produce the final result.)

2.  **Analyze the Input Text:**
    *   **Subject:** الشبكات العصبية (Neural networks).
    *   **Structure:** فيها طبقات (have layers).
    *   **Action:** تعالج المدخلات بالتدريج (process inputs gradually/step-by-step).
    *   **Outcome:** إلى أن تنتج النتيجة النهائية (until they produce the final result).
    *   **Issues/A

### D1_domain_name

Thinking Process:

1.  **Analyze the Request:**
    *   **Task:** Rewrite the given Arabic text to make it clearer and more accurate (أوضح وأدق) while preserving its meaning (مع الحفاظ على معناه).
    *   **Constraint 1:** Do not add facts or information not present in the original text (لا تضف حقائق أو معلومات غير موجودة في النص).
    *   **Constraint 2:** Output only the rewritten text, no explanation (أعد النص المصاغ فقط دون شرح).
    *   **Domain:** Artificial Intelligence (ذكاء اصطناعي).
    *   **Original Text:** "الشبكات العصبية فيها طبقات تعالج المدخلات بالتدريج إلى أن تنتج النتيجة النهائية." (Neural networks have layers that process inputs gradually until the final result is produced.)

2.  **Analyze the Original Text:**
    *   Subject: الشبكات العصبية (Neural networks).
    *   Structure: فيها طبقات (have layers).
    *   Action: تعالج المدخلات بالتدريج (process inputs gradually).
    *   Outcome: إلى أن تنتج النتيجة النهائية (until the final result is

### D2_domain_name_definition

Thinking Process:

1.  **Analyze the Request:**
    *   **Task:** Rewrite the given Arabic text to make it clearer and more precise while maintaining its meaning.
    *   **Constraint 1:** Do not add facts or information not present in the original text.
    *   **Constraint 2:** Output only the rewritten text, without explanation.
    *   **Domain:** Artificial Intelligence (ذكاء اصطناعي).
    *   **Input Text:** "الشبكات العصبية فيها طبقات تعالج المدخلات بالتدريج إلى أن تنتج النتيجة النهائية." (Neural networks have layers that process inputs gradually to produce the final result.)

2.  **Analyze the Input Text:**
    *   **Subject:** الشبكات العصبية (Neural Networks).
    *   **Structure:** فيها طبقات (have layers).
    *   **Action:** تعالج المدخلات بالتدريج (process inputs gradually/sequentially).
    *   **Outcome:** إلى أن تنتج النتيجة النهائية (until they produce the final result).
    *   **Issues:** The sentence is a bit colloquial ("فيها طبقات", "إلى أن تنتج

### D3_domain_guidance

Thinking Process:

1.  **Analyze the Request:**
    *   **Task:** Rewrite the given Arabic text to be clearer and more accurate while preserving its meaning.
    *   **Constraint 1:** Do not add facts or information not present in the original text.
    *   **Constraint 2:** Output only the rewritten text, no explanation.
    *   **Domain:** Artificial Intelligence (AI).
    *   **Guidelines:** Use precise terminology, maintain consistency, improve phrasing without changing facts/relationships/uncertainty, do not add mechanisms/capabilities/results/numbers, distinguish between similar technical concepts based on context, use clear/direct sentences, describe AI system capabilities accurately without overstating autonomy/uncertainty.
    *   **Input Text:** "الشبكات العصبية فيها طبقات تعالج المدخلات بالتدريج إلى أن تنتج النتيجة النهائية." (Neural networks have layers that process inputs gradually to produce the final result.)

2.  **Analyze the Input Text:**
    *   **Subject:** الشبكات العصبية (Neural Networks).
    *   **Structure:** فيها طبقات (have layers).
    *   **Process:** تعالج المد

### D4_domain_guidance_examples

Thinking Process:

1.  **Analyze the Request:**
    *   **Task:** Rewrite the given Arabic text to be clearer and more accurate while preserving its meaning.
    *   **Constraint 1:** Do not add facts or information not present in the original text.
    *   **Constraint 2:** Output only the rewritten text, no explanation.
    *   **Domain:** Artificial Intelligence (AI).
    *   **Guidelines:** Use precise terminology, maintain consistency, improve phrasing without changing facts/relationships/uncertainty, do not add mechanisms/capabilities/results/numbers, distinguish between close concepts based on context, use clear/direct sentences, describe capabilities accurately without overstating.
    *   **Input Text:** "الشبكات العصبية فيها طبقات تعالج المدخلات بالتدريج إلى أن تنتج النتيجة النهائية." (Neural networks have layers that process inputs gradually to produce the final result.)

2.  **Analyze the Input Text:**
    *   **Subject:** الشبكات العصبية (Neural Networks).
    *   **Structure:** فيها طبقات (have layers).
    *   **Process:** تعالج المدخلات بالتدريج (process

## P14

**Input:** النموذج اللغوي يتعامل مع السياق الموجود في النص عشان يولد تكملة مناسبة.

### D0_saleem_only

Thinking Process:

1.  **Analyze the Request:**
    *   **Task:** Rewrite the given Arabic text to make it clearer and more accurate (أوضح وأدق) while preserving its meaning (مع الحفاظ على معناه).
    *   **Constraint 1:** Do not add facts or information not present in the original text (لا تضف حقائق أو معلومات غير موجودة في النص).
    *   **Constraint 2:** Output only the rewritten text, no explanation (أعد النص المصاغ فقط دون شرح).
    *   **Input Text:** "النموذج اللغوي يتعامل مع السياق الموجود في النص عشان يولد تكملة مناسبة." (The language model deals with the context existing in the text so that it generates a suitable continuation.)

2.  **Analyze the Input Text:**
    *   **Meaning:** Language models process the context within a text to generate an appropriate continuation.
    *   **Issues:**
        *   "عشان" (Eshan) is colloquial/informal. It should be replaced with a formal equivalent like "لكي" (liki) or "لأجل" (la'jil).
        *

### D1_domain_name

Thinking Process:

1.  **Analyze the Request:**
    *   **Task:** Rewrite the given Arabic text to be clearer and more accurate (أدق) while preserving its meaning.
    *   **Constraint 1:** Do not add facts or information not present in the original text.
    *   **Constraint 2:** Output only the rewritten text, no explanation.
    *   **Domain:** Artificial Intelligence (ذكاء اصطناعي).
    *   **Original Text:** "النموذج اللغوي يتعامل مع السياق الموجود في النص عشان يولد تكملة مناسبة." (The language model deals with the context existing in the text so that it generates a suitable continuation.)

2.  **Analyze the Original Text:**
    *   **Meaning:** Language models process the context within a text to generate an appropriate continuation.
    *   **Issues:**
        *   "عشان" (Eshan) is colloquial/informal (meaning "so that" or "in order to"). It should be replaced with formal Arabic like "لكي" or "لإنتاج".
        *   "يتعامل مع" (It deals with) is a bit generic.

### D2_domain_name_definition

Thinking Process:

1.  **Analyze the Request:**
    *   **Task:** Rewrite the given Arabic text to make it clearer and more precise (أوضح وأدق) while preserving its meaning (مع الحفاظ على معناه).
    *   **Constraint 1:** Do not add facts or information not present in the original text (لا تضف حقائق أو معلومات غير موجودة في النص).
    *   **Constraint 2:** Output only the rewritten text, no explanation (أعد النص المصاغ فقط دون شرح).
    *   **Domain:** Artificial Intelligence (ذكاء اصطناعي).
    *   **Input Text:** "النموذج اللغوي يتعامل مع السياق الموجود في النص عشان يولد تكملة مناسبة." (The language model deals with the context existing in the text to generate a suitable continuation.)

2.  **Analyze the Input Text:**
    *   **Subject:** النموذج اللغوي (Language Model).
    *   **Action:** يتعامل مع (deals with/interacts with) -> السياق الموجود في النص (the context existing in the text).
    *   **Purpose/Result:** عشان (in order to/so that) ->

### D3_domain_guidance

Thinking Process:

1.  **Analyze the Request:**
    *   **Task:** Rewrite the given Arabic text to make it clearer and more precise while preserving its meaning.
    *   **Constraint 1:** Do not add facts or information not present in the original text.
    *   **Constraint 2:** Output only the rewritten text, no explanation.
    *   **Domain:** Artificial Intelligence (AI).
    *   **Input Text:** "النموذج اللغوي يتعامل مع السياق الموجود في النص عشان يولد تكملة مناسبة." (The language model deals with the context existing in the text to generate a suitable continuation.)
    *   **Guidelines:** Use precise terminology, maintain consistency, improve phrasing without changing facts/relationships/uncertainty, do not add mechanisms/capabilities/results/numbers, distinguish between close technical concepts based on context, use clear and direct sentences, describe capabilities accurately without overstating independence or certainty.

2.  **Analyze the Input Text:**
    *   "النموذج اللغوي" (Language Model) - Technical term, keep it.
    *   "يتعامل مع" (deals with) - A bit informal. Better:

### D4_domain_guidance_examples

Thinking Process:

1.  **Analyze the Request:**
    *   **Task:** Rewrite the given Arabic text to be clearer and more accurate while preserving its meaning.
    *   **Constraint 1:** Do not add facts or information not present in the original text.
    *   **Constraint 2:** Output only the rewritten text, no explanations.
    *   **Domain:** Artificial Intelligence (AI).
    *   **Input Text:** "النموذج اللغوي يتعامل مع السياق الموجود في النص عشان يولد تكملة مناسبة." (The language model deals with the context existing in the text to generate a suitable continuation.)
    *   **Guidelines:** Use precise terminology, maintain consistency, improve phrasing without changing facts/relationships/uncertainty, do not add mechanisms/capabilities/results/numbers, distinguish between close technical concepts based on context, use clear and direct sentences, describe capabilities accurately without overstating independence or certainty.

2.  **Analyze the Input Text:**
    *   "النموذج اللغوي" (Language Model) - Correct terminology.
    *   "يتعامل مع" (deals with) - A bit informal. Better: "يعتمد على

## P15

**Input:** اختيار بيانات التدريب مهم لأن جودة البيانات تنعكس على جودة مخرجات النموذج.

### D0_saleem_only

Thinking Process:

1.  **Analyze the Request:**
    *   **Task:** Rewrite the given Arabic text to make it clearer and more precise (أوضح وأدق) while preserving its meaning (مع الحفاظ على معناه).
    *   **Constraint 1:** Do not add facts or information not present in the original text (لا تضف حقائق أو معلومات غير موجودة في النص).
    *   **Constraint 2:** Output only the rewritten text, no explanation (أعد النص المصاغ فقط دون شرح).
    *   **Input Text:** "اختيار بيانات التدريب مهم لأن جودة البيانات تنعكس على جودة مخرجات النموذج." (Choosing training data is important because data quality reflects on model output quality.)

2.  **Analyze the Input Text:**
    *   **Meaning:** Selecting training data is crucial because the quality of the data directly impacts the quality of the model's outputs.
    *   **Tone:** Informative, technical (AI/ML context).
    *   **Issues:** The sentence is grammatically correct but could be slightly more formal or precise. "تنعكس على" (reflects on) is okay, but "تحدد

### D1_domain_name

Thinking Process:

1.  **Analyze the Request:**
    *   **Task:** Rewrite the given Arabic text to make it clearer and more precise (أوضح وأدق) while preserving its meaning (مع الحفاظ على معناه).
    *   **Constraint 1:** Do not add facts or information not present in the original text (لا تضف حقائق أو معلومات غير موجودة في النص).
    *   **Constraint 2:** Output only the rewritten text, no explanation (أعد النص المصاغ فقط دون شرح).
    *   **Domain:** Artificial Intelligence (ذكاء اصطناعي).
    *   **Original Text:** "اختيار بيانات التدريب مهم لأن جودة البيانات تنعكس على جودة مخرجات النموذج." (Choosing training data is important because the quality of data reflects on the quality of the model's outputs.)

2.  **Analyze the Original Text:**
    *   **Meaning:** Selecting training data is crucial because data quality directly impacts model output quality.
    *   **Tone:** Informative, technical but simple.
    *   **Issues:** The sentence is grammatically correct but could be slightly more formal or precise in the context of AI. "تن

### D2_domain_name_definition

Thinking Process:

1.  **Analyze the Request:**
    *   **Task:** Rewrite the given Arabic text to make it clearer and more precise (أوضح وأدق) while preserving its meaning (مع الحفاظ على معناه).
    *   **Constraint 1:** Do not add facts or information not present in the original text (لا تضف حقائق أو معلومات غير موجودة في النص).
    *   **Constraint 2:** Output only the rewritten text, no explanation (أعد النص المصاغ فقط دون شرح).
    *   **Context:** The field is Artificial Intelligence (الذكاء الاصطناعي).
    *   **Input Text to Improve:** "اختيار بيانات التدريب مهم لأن جودة البيانات تنعكس على جودة مخرجات النموذج." (Choosing training data is important because the quality of data reflects on the quality of the model's outputs.)

2.  **Analyze the Input Text:**
    *   Sentence: "اختيار بيانات التدريب مهم لأن جودة البيانات تنعكس على جودة مخرجات النموذج."
    *   Meaning: Selecting training data is crucial because data quality impacts model output quality.
    *   Issues/Opportunities for Improvement:

### D3_domain_guidance

Thinking Process:

1.  **Analyze the Request:**
    *   **Task:** Rewrite the given Arabic text to make it clearer and more precise while maintaining its original meaning.
    *   **Constraint 1:** Do not add facts or information not present in the original text.
    *   **Constraint 2:** Output only the rewritten text, no explanation.
    *   **Domain:** Artificial Intelligence (AI).
    *   **Input Text:** "اختيار بيانات التدريب مهم لأن جودة البيانات تنعكس على جودة مخرجات النموذج." (Choosing training data is important because data quality reflects on model output quality.)
    *   **Guidelines:** Use precise terminology, maintain consistency, improve phrasing without changing facts/relationships/uncertainty, do not add mechanisms/capabilities/results/numbers, distinguish between close technical concepts based on context, use clear/direct sentences, describe AI system capabilities accurately without overstating.

2.  **Analyze the Input Text:**
    *   Sentence: "اختيار بيانات التدريب مهم لأن جودة البيانات تنعكس على جودة مخرجات النموذج."
    *   Meaning: Selecting training data is crucial because the quality of the data affects the quality of

### D4_domain_guidance_examples

Thinking Process:

1.  **Analyze the Request:**
    *   **Task:** Rewrite the given Arabic text to make it clearer and more precise while maintaining its original meaning.
    *   **Constraint 1:** Do not add facts or information not present in the original text.
    *   **Constraint 2:** Output only the rewritten text, no explanations.
    *   **Domain:** Artificial Intelligence (AI).
    *   **Guidelines:** Use precise technical terminology, maintain consistency in terminology, improve phrasing without changing facts/relationships/uncertainty levels, do not add mechanisms/capabilities/results/technical numbers, distinguish between close technical concepts based on context, use clear and direct sentences, describe AI system capabilities accurately without overstating understanding/independence/uncertainty.
    *   **Input Text:** "اختيار بيانات التدريب مهم لأن جودة البيانات تنعكس على جودة مخرجات النموذج." (Choosing training data is important because data quality reflects on model output quality.)

2.  **Analyze the Input Text:**
    *   **Sentence:** "اختيار بيانات التدريب مهم لأن جودة البيانات تنعكس على جودة مخرجات النموذج."
    *   **Meaning:** Selecting
