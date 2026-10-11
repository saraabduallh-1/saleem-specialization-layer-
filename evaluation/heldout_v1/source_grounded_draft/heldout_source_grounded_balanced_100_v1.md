# Held-out source-grounded balanced 100 — Draft v1

**الحالة:** مسودة مولدة بمساعدة نموذج ومبنية على مصادر مستقلة. ليست مجمدة ولا تُشغَّل على النظام قبل المراجعة البشرية.

## فحص الجودة الآلي

- العدد: 100
- طول النصوص: 15–24 كلمة
- تسريب مباشر للمصطلح/الاختصارات المعروفة: 0
- أزواج متشابهة جدًا: 0
- جميع الحالات لها مصدر مستقل: نعم
- توزيع الأساليب المجمع: {'reports_formal': 45, 'developer': 25, 'social': 20, 'product_support': 10}

## SG100-001 — نموذج طرفي
- **النص:** شغلت المودل على الحساس نفسه بدل ما أرسل كل قراءة للسيرفر. الـlatency تحسن كثير، بس أبي أتأكد إن هذا مناسب للإنتاج.
- **الأسلوب:** developer_issue
- **المصدر:** Google AI Edge — LiteRT: High-Performance On-Device Machine Learning Framework
- **الرابط:** https://developers.google.com/edge/litert
- **عدد الكلمات:** 21

## SG100-002 — حوسبة طرفية
- **النص:** تعتمد البنية الحالية على تنفيذ جزء من المعالجة بالقرب من أجهزة المصنع بدل ترحيل جميع البيانات إلى مركز البيانات، بهدف تقليل التأخير وحركة الشبكة.
- **الأسلوب:** formal_technical
- **المصدر:** AWS — What is Edge Computing?
- **الرابط:** https://aws.amazon.com/what-is/edge-computing/
- **عدد الكلمات:** 24

## SG100-003 — خطوة ترشيحية
- **النص:** غيرت حركة الفلتر من 1 إلى 2 في طبقة الالتفاف، وفجأة صارت أبعاد الـoutput أصغر. هل هذا السلوك متوقع؟
- **الأسلوب:** developer_question
- **المصدر:** PyTorch — Conv2d documentation
- **الرابط:** https://docs.pytorch.org/docs/stable/generated/torch.nn.modules.conv.Conv2d.html
- **عدد الكلمات:** 19

## SG100-004 — قاعدة معرفة
- **النص:** ودي البوت ما يعتمد على كلامه بس؛ يكون عنده حقائق وقواعد مرتبة عن المجال ويرجع لها قبل ما يستنتج الإجابة.
- **الأسلوب:** social_tech
- **المصدر:** IBM — What Is Reasoning in AI?
- **الرابط:** https://www.ibm.com/think/topics/ai-reasoning
- **عدد الكلمات:** 20

## SG100-005 — تعزيز تدرجي
- **النص:** عندي عدة weak learners وأضيفها واحد وراء الثاني، وكل واحد يحاول يصلح أخطاء اللي قبله. هل هذا الأسلوب مناسب للتصنيف؟
- **الأسلوب:** developer_question
- **المصدر:** scikit-learn — Gradient Boosting
- **الرابط:** https://scikit-learn.org/stable/modules/ensemble.html#gradient-boosting
- **عدد الكلمات:** 20

## SG100-006 — تشذيب النموذج
- **النص:** المودل صار ثقيل على الجهاز، فشلت أوزان واتصالات تأثيرها ضعيف. الحجم نزل بشكل واضح والدقة تقريبًا ما تأثرت.
- **الأسلوب:** social_tech
- **المصدر:** PyTorch — Pruning Tutorial
- **الرابط:** https://docs.pytorch.org/tutorials/intermediate/pruning_tutorial
- **عدد الكلمات:** 18

## SG100-007 — جهاز روبوتي
- **النص:** النظام عبارة عن ذراع ميكانيكية مشغلة لتنفيذ مهمة محددة، إلا أن مستوى الاستقلالية والتحكم الذاتي فيها لا يرقى إلى تعريف الروبوت الكامل.
- **الأسلوب:** formal_technical
- **المصدر:** International Federation of Robotics / ISO 8373 — Service Robots: Definitions
- **الرابط:** https://ifr.org/img/worldrobotics/Definition_Service_Robots_2026.pdf
- **عدد الكلمات:** 22

## SG100-008 — خوارزمية كيو
- **النص:** الـagent يجرب أفعال مختلفة ويحدّث قيمة كل state-action، وبعد فترة يعرف وش الحركة اللي تعطيه أعلى عائد بالمستقبل.
- **الأسلوب:** social_saudi
- **المصدر:** IBM — What Is Reinforcement Learning?
- **الرابط:** https://www.ibm.com/think/topics/reinforcement-learning
- **عدد الكلمات:** 18

## SG100-009 — انحراف الخصائص
- **النص:** لوحظ بعد عدة أشهر من النشر تغير توزيع بعض متغيرات الإدخال مقارنة بخط الأساس، وتزامن ذلك مع تراجع ملحوظ في جودة التنبؤ.
- **الأسلوب:** report_technical
- **المصدر:** Google Cloud — Guidelines for developing high-quality, predictive ML solutions
- **الرابط:** https://docs.cloud.google.com/architecture/guidelines-for-developing-high-quality-ml-solutions
- **عدد الكلمات:** 22

## SG100-010 — بيانات ديموغرافية
- **النص:** يتضمن التقرير توزيع المشاركين حسب العمر والجنس ومستوى التعليم والدخل والحالة العملية، بهدف مقارنة خصائص الشرائح السكانية المختلفة.
- **الأسلوب:** report_technical
- **المصدر:** United Nations Statistics Division — Population Censuses' Datasets
- **الرابط:** https://unstats.un.org/unsd/demographic-social/products/dyb/dybcensusdata/
- **عدد الكلمات:** 18

## SG100-011 — أوامر نشطة
- **النص:** خلّيت الـLLM يجاوب السؤال أكثر من مرة، وأخذت الحالات اللي كان متردد فيها أكثر وكتبت لها أمثلة بشرية توضح طريقة الحل.
- **الأسلوب:** developer_issue
- **المصدر:** IBM — Build a procurement compliance agent with active prompting
- **الرابط:** https://www.ibm.com/think/tutorials/active-prompting
- **عدد الكلمات:** 21

## SG100-012 — دالة المكافأة
- **النص:** صُممت آلية التقييم بحيث تمنح الوكيل قيمة أعلى عند تحقيق الهدف وتخفضها عند السلوك غير المرغوب، بما يوجه التعلم نحو التصرفات المطلوبة.
- **الأسلوب:** formal_technical
- **المصدر:** IBM — What Is Reinforcement Learning?
- **الرابط:** https://www.ibm.com/think/topics/reinforcement-learning
- **عدد الكلمات:** 22

## SG100-013 — تهيئة الأوزان
- **النص:** قبل ما يبدأ التدريب، وش أفضل طريقة أحدد فيها القيم الأولية للـweights؟ لاحظت إن البداية تأثر كثير على الاستقرار.
- **الأسلوب:** developer_question
- **المصدر:** PyTorch — torch.nn.init
- **الرابط:** https://docs.pytorch.org/docs/stable/nn.init
- **عدد الكلمات:** 19

## SG100-014 — إعادة ترتيب
- **النص:** بعد توليد قائمة المرشحين الأولية، تُطبَّق مرحلة نهائية لتعديل ترتيب العناصر وفق معايير إضافية مثل الحداثة والتنوع والقيود التجارية.
- **الأسلوب:** formal_technical
- **المصدر:** Google for Developers — Re-ranking
- **الرابط:** https://developers.google.com/machine-learning/recommendation/dnn/re-ranking
- **عدد الكلمات:** 19

## SG100-015 — تعلُّم الخصائص
- **النص:** بدل ما أحدد الـfeatures يدوي، أبي الشبكة تطلع التمثيلات المهمة من البيانات الخام بنفسها وتستخدمها لاحقًا في التصنيف.
- **الأسلوب:** social_tech
- **المصدر:** Bengio, Courville & Vincent — Representation Learning: A Review and New Perspectives
- **الرابط:** https://arxiv.org/abs/1206.5538
- **عدد الكلمات:** 18

## SG100-016 — تحيُّز المُختبِر
- **النص:** أحس الباحث جلس يغيّر الإعدادات ويعيد التجربة لين طلعت النتيجة اللي كان متوقعها من البداية، وكذا التقييم صار مو محايد.
- **الأسلوب:** social_saudi
- **المصدر:** American Psychological Association — APA Dictionary: experimenter bias
- **الرابط:** https://dictionary.apa.org/experimenter-bias
- **عدد الكلمات:** 20

## SG100-017 — اكتشاف الشذوذ
- **النص:** تم إعداد آلية مراقبة لتحديد القراءات التي تنحرف بدرجة كبيرة عن النمط المعتاد، مع رفع الحالات غير المألوفة للمراجعة.
- **الأسلوب:** report_technical
- **المصدر:** Google for Developers — Machine Learning Glossary
- **الرابط:** https://developers.google.com/machine-learning/glossary
- **عدد الكلمات:** 19

## SG100-018 — كسر القيود
- **النص:** رصد الفريق محاولات متكررة لصياغة مدخلات ملتوية بهدف تجاوز ضوابط الأمان ودفع النموذج إلى تنفيذ سلوك يفترض أن يرفضه.
- **الأسلوب:** report_technical
- **المصدر:** OWASP — LLM Prompt Injection Prevention Cheat Sheet
- **الرابط:** https://cheatsheetseries.owasp.org/cheatsheets/LLM_Prompt_Injection_Prevention_Cheat_Sheet.html
- **عدد الكلمات:** 19

## SG100-019 — إدارة الحوار
- **النص:** البوت فاهم الرسالة، لكن مشكلتنا كيف يقرر الخطوة الجاية: يسأل؟ ينفذ إجراء؟ أو يرد مباشرة حسب سياق المحادثة.
- **الأسلوب:** product_support
- **المصدر:** Kwan et al. — Survey on Task-Oriented Dialogue Policy Learning
- **الرابط:** https://arxiv.org/abs/2202.13675
- **عدد الكلمات:** 18

## SG100-020 — استماع الآلة
- **النص:** يهدف المكوّن إلى تحليل الإشارة الصوتية والتعرف على طبيعة الصوت أو الحدث الموجود فيها، وليس الاكتفاء بتحويل المحتوى المنطوق إلى نص.
- **الأسلوب:** formal_technical
- **المصدر:** MIT Media Lab — Skeleton — machine-listening and machine-learning tools
- **الرابط:** https://www.media.mit.edu/projects/skeleton/overview/
- **عدد الكلمات:** 21

## SG100-021 — تعلُّم منقول
- **النص:** عندي مودل متعلم على مهمة قريبة من مشكلتي. هل أقدر أستفيد من اللي تعلمه وأكيّفه للمهمة الجديدة بدل أبدأ من الصفر؟
- **الأسلوب:** developer_question
- **المصدر:** TensorFlow — Transfer learning and fine-tuning
- **الرابط:** https://www.tensorflow.org/tutorials/images/transfer_learning
- **عدد الكلمات:** 21

## SG100-022 — قابلية الرصد
- **النص:** الخدمة مرات تبطئ وما نعرف السبب. إذا جمعنا logs وmetrics وtraces بشكل مرتب نقدر نفهم وش يصير داخلها بدون تخمين.
- **الأسلوب:** social_tech
- **المصدر:** OpenTelemetry — Observability Primer
- **الرابط:** https://opentelemetry.io/docs/concepts/observability-primer/
- **عدد الكلمات:** 20

## SG100-023 — سيادة البيانات
- **النص:** يشترط التصميم أن تخضع المعلومات المخزنة والمعالجة داخل كل دولة للمتطلبات القانونية والتنظيمية السارية في تلك الدولة.
- **الأسلوب:** formal_technical
- **المصدر:** Microsoft Learn — Data controls: data sovereignty
- **الرابط:** https://learn.microsoft.com/en-us/azure/azure-sovereign-clouds/data-controls
- **عدد الكلمات:** 17

## SG100-024 — مقياس روج
- **النص:** أبي أقيّم الملخص الناتج بمقارنته مع ملخص بشري، خصوصًا من ناحية تداخل الكلمات والعبارات. وش المقياس المناسب لهالنوع من المقارنة؟
- **الأسلوب:** developer_question
- **المصدر:** ACL Anthology — Revisiting Summarization Evaluation for Scientific Articles
- **الرابط:** https://aclanthology.org/L16-1130/
- **عدد الكلمات:** 20

## SG100-025 — منحنى الخسارة
- **النص:** وأنا أراقب التدريب لاحظت إن الخطأ ينزل بسرعة بالبداية وبعدها تقريبًا يثبت. الرسم عبر الـepochs واضح جدًا.
- **الأسلوب:** social_tech
- **المصدر:** Google for Developers — Machine Learning Glossary
- **الرابط:** https://developers.google.com/machine-learning/glossary
- **عدد الكلمات:** 17

## SG100-026 — تجزئة النموذج
- **النص:** المودل ما يدخل في ذاكرة كرت واحد، فوزعت أجزاء من الـparameters على عدة كروت. التدريب اشتغل لكن التواصل بينهم زاد.
- **الأسلوب:** developer_issue
- **المصدر:** Hugging Face — FSDP2 — model sharding across GPUs
- **الرابط:** https://huggingface.co/docs/transformers/main/fsdp
- **عدد الكلمات:** 20

## SG100-027 — تحسين عشوائي
- **النص:** بدل ما أحسب كل البيانات في كل خطوة، أستخدم جزء عشوائي يعطيني اتجاه تقريبي للتحديث. أسرع بس فيه تذبذب طبيعي.
- **الأسلوب:** social_tech
- **المصدر:** Stanford University — Modern Statistical Learning — stochastic optimization resources
- **الرابط:** https://web.stanford.edu/class/stats315a/syllabus.html
- **عدد الكلمات:** 20

## SG100-028 — تفسير مغاير
- **النص:** يوضح التقرير أن تغيير الدخل قليلًا مع بقاء بقية المدخلات ثابتة كان سيغيّر قرار النموذج من الرفض إلى القبول.
- **الأسلوب:** report_technical
- **المصدر:** Wachter, Mittelstadt & Russell — Counterfactual Explanations without Opening the Black Box
- **الرابط:** https://arxiv.org/abs/1711.00399
- **عدد الكلمات:** 19

## SG100-029 — قصور ذاتي
- **النص:** طلعت لي قيمة عالية بعد التجميع. أفهم منها إن النقاط ما زالت بعيدة عن مراكز مجموعاتها؟ وكيف أستخدمها لاختيار عدد المجموعات؟
- **الأسلوب:** developer_question
- **المصدر:** scikit-learn — KMeans
- **الرابط:** https://scikit-learn.org/stable/modules/generated/sklearn.cluster.KMeans.html
- **عدد الكلمات:** 21

## SG100-030 — خاصية مستمرة
- **النص:** عندي متغير مثل درجة الحرارة ممكن يأخذ قيم كثيرة جدًا وبينها كسور، مو مجرد مجموعة خيارات محددة.
- **الأسلوب:** developer_question
- **المصدر:** Google for Developers — Machine Learning Glossary
- **الرابط:** https://developers.google.com/machine-learning/glossary
- **عدد الكلمات:** 17

## SG100-031 — روبوت ذكي
- **النص:** الروبوت يقرأ الحساسات، يفهم اللي حوله ويغيّر تصرفه حسب البيئة بدل ما يكرر نفس الحركة كل مرة.
- **الأسلوب:** social_tech
- **المصدر:** International Federation of Robotics / ISO 8373 — Service Robots: Definitions
- **الرابط:** https://ifr.org/img/worldrobotics/Definition_Service_Robots_2026.pdf
- **عدد الكلمات:** 17

## SG100-032 — استعلام متواز
- **النص:** أظهر ملف التنفيذ أن أجزاء من الطلب عولجت بواسطة عدة عمليات في الوقت نفسه، مما خفّض زمن التنفيذ على الجدول الكبير.
- **الأسلوب:** report_technical
- **المصدر:** PostgreSQL — Parallel Query
- **الرابط:** https://www.postgresql.org/docs/17/parallel-query.html
- **عدد الكلمات:** 21

## SG100-033 — درجة العشوائية
- **النص:** إذا رفعت الإعداد هذا، الردود تصير متنوعة ومفاجئة أكثر، وإذا نزلته تصير الإجابات ثابتة ومتوقعة. وش القيمة المناسبة للإنتاج؟
- **الأسلوب:** social_tech
- **المصدر:** Google for Developers — Machine Learning Glossary
- **الرابط:** https://developers.google.com/machine-learning/glossary
- **عدد الكلمات:** 19

## SG100-034 — عامل التفرع
- **النص:** في شجرة البحث الحالية، كل عقدة ممكن تنتج في المتوسط خمس حالات جديدة، وهذا يرفع عدد المسارات بسرعة كبيرة.
- **الأسلوب:** formal_technical
- **المصدر:** Google for Developers — Machine Learning Glossary
- **الرابط:** https://developers.google.com/machine-learning/glossary
- **عدد الكلمات:** 19

## SG100-035 — تَكَيُّف مشترك
- **النص:** الغريب إن بعض الـneurons كأنها متعودة على بعض؛ إذا عطلت جزء بسيط منها يطيح الأداء أكثر من المتوقع.
- **الأسلوب:** social_tech
- **المصدر:** JMLR — Dropout: A Simple Way to Prevent Neural Networks from Overfitting
- **الرابط:** https://jmlr.org/papers/v15/srivastava14a.html
- **عدد الكلمات:** 18

## SG100-036 — وكيل مُجسَّد
- **النص:** نبغى الـagent ما يكون مجرد شات؛ يكون له جسم افتراضي داخل المحاكاة يشوف البيئة ويتحرك ويتعلم من تفاعله معها.
- **الأسلوب:** product_support
- **المصدر:** IBM — What is a Multi-Agent System?
- **الرابط:** https://www.ibm.com/think/topics/multiagent-system
- **عدد الكلمات:** 19

## SG100-037 — دافع داخلي
- **النص:** استمر الوكيل في استكشاف حالات جديدة حتى عند غياب مكافأة خارجية مباشرة، لأن آلية داخلية شجعته على الفضول واكتشاف المجهول.
- **الأسلوب:** report_technical
- **المصدر:** Aubret, Matignon & Hassas — A survey on intrinsic motivation in reinforcement learning
- **الرابط:** https://arxiv.org/abs/1908.06976
- **عدد الكلمات:** 20

## SG100-038 — تجميع بالمتوسط
- **النص:** عندي بيانات بدون labels وأبي أقسمها إلى أربع مجموعات بناءً على القرب من مراكز تتحدث مع كل دورة. هل هذا مناسب؟
- **الأسلوب:** developer_question
- **المصدر:** scikit-learn — KMeans
- **الرابط:** https://scikit-learn.org/stable/modules/generated/sklearn.cluster.KMeans.html
- **عدد الكلمات:** 21

## SG100-039 — مُحرِّك استنتاج
- **النص:** يقارن المكوّن الحقائق المتاحة بالقواعد المخزنة ثم يطبق منطق الاستدلال لاستخلاص نتائج جديدة يمكن للنظام استخدامها في القرار.
- **الأسلوب:** formal_technical
- **المصدر:** IBM — What Is Reasoning in AI?
- **الرابط:** https://www.ibm.com/think/topics/ai-reasoning
- **عدد الكلمات:** 18

## SG100-040 — جدول مرحلي
- **النص:** قبل ما أدخل البيانات لجداول الإنتاج، أبي أحطها مؤقتًا بمكان أنظفها وأطبق التحويلات وبعدها أنقلها. وش أفضل تصميم؟
- **الأسلوب:** developer_question
- **المصدر:** Microsoft Learn — Tables in Fabric Data Warehouse
- **الرابط:** https://learn.microsoft.com/en-us/fabric/data-warehouse/tables
- **عدد الكلمات:** 18

## SG100-041 — جبر خطي
- **النص:** كل ما دخلت أكثر في ML ألقى مصفوفات ومتجهات وأنظمة معادلات بكل مكان. واضح لازم أراجع الأساس الرياضي هذا من جديد.
- **الأسلوب:** social_saudi
- **المصدر:** Stanford University — Modern Statistical Learning — stochastic optimization resources
- **الرابط:** https://web.stanford.edu/class/stats315a/syllabus.html
- **عدد الكلمات:** 21

## SG100-042 — بيانات وصفيّة
- **النص:** عندنا ملفات كثيرة، وكل ملف معه معلومات عن النوع والتاريخ والمالك والبنية. هي مو المحتوى نفسه لكنها تسهّل فهمه وتنظيمه.
- **الأسلوب:** social_saudi
- **المصدر:** NIST — Metadata — CSRC Glossary
- **الرابط:** https://csrc.nist.gov/glossary/term/metadata
- **عدد الكلمات:** 20

## SG100-043 — استرجاع سياقي
- **النص:** قبل الفهرسة أضفنا لكل مقطع وصفًا قصيرًا يوضح مكانه ومعناه داخل المستند الكامل، ثم استخدمناه مع البحث المتجهي والكلمات المفتاحية.
- **الأسلوب:** report_technical
- **المصدر:** Anthropic — Introducing Contextual Retrieval
- **الرابط:** https://www.anthropic.com/engineering/contextual-retrieval
- **عدد الكلمات:** 20

## SG100-044 — مخزن الخصائص
- **النص:** نحتاج مكان مركزي يحفظ قيم الـfeatures وتعريفاتها بحيث تستخدمها فرق التدريب والخدمة بدون ما كل فريق يعيد بناءها بطريقته.
- **الأسلوب:** product_support
- **المصدر:** Google Cloud — Vertex AI Feature Store overview
- **الرابط:** https://cloud.google.com/vertex-ai/docs/featurestore/latest/overview
- **عدد الكلمات:** 19

## SG100-045 — نموذج ثابت
- **النص:** النسخة الحالية تدربت مرة واحدة على لقطة محددة من البيانات، وما تتحدث تلقائيًا حتى لو تغيرت البيانات بعد النشر.
- **الأسلوب:** report_technical
- **المصدر:** Google for Developers — Machine Learning Glossary
- **الرابط:** https://developers.google.com/machine-learning/glossary
- **عدد الكلمات:** 19

## SG100-046 — تغيُّر المجال
- **النص:** أداء النموذج ممتاز على بيانات المصدر لكنه يهبط على البيئة الجديدة لأن توزيع البيانات هناك مختلف بوضوح عن توزيع التدريب.
- **الأسلوب:** report_technical
- **المصدر:** Moreno-Torres et al. — A unifying view on dataset shift in classification
- **الرابط:** https://www.sciencedirect.com/science/article/pii/S0031320311002901
- **عدد الكلمات:** 20

## SG100-047 — تلخيص تلقائي
- **النص:** عندي مستندات طويلة جدًا وأبي النظام يطلع منها نسخة قصيرة تحافظ على الأفكار الأساسية بدون ما أختصرها يدويًا.
- **الأسلوب:** social_tech
- **المصدر:** ACL Anthology — Re-evaluating Evaluation in Text Summarization
- **الرابط:** https://aclanthology.org/2020.emnlp-main.751/
- **عدد الكلمات:** 18

## SG100-048 — بيانات مظلمة
- **النص:** وجد التدقيق كميات كبيرة من المعلومات التي تجمعها الأنظمة يوميًا وتبقى مخزنة لسنوات دون أن تدخل في أي تحليل أو قرار.
- **الأسلوب:** report_technical
- **المصدر:** IBM — What Is Dark Data?
- **الرابط:** https://www.ibm.com/think/topics/dark-data
- **عدد الكلمات:** 21

## SG100-049 — موجّه النماذج
- **النص:** أبي الطلب البسيط يروح لخيار سريع ورخيص، والطلب المعقد يتحول تلقائيًا لخيار أقوى حسب الجودة والتكلفة وزمن الاستجابة.
- **الأسلوب:** product_support
- **المصدر:** Cloudflare — AI Gateway Features — Auto Router and Dynamic Routing
- **الرابط:** https://developers.cloudflare.com/ai-gateway/features/
- **عدد الكلمات:** 18

## SG100-050 — تحديد المرجع
- **النص:** في الجملة «وصلت سارة ثم قالت إنها جاهزة»، أبي النظام يعرف أن «إنها» تشير إلى سارة نفسها.
- **الأسلوب:** developer_question
- **المصدر:** Stanford NLP — Coreference Resolution
- **الرابط:** https://nlp.stanford.edu/projects/coref.shtml
- **عدد الكلمات:** 17

## SG100-051 — بحث دلالي
- **النص:** المستخدم يكتب «جوال بطاريته تعيش طويل»، وأبي النتائج تجيب المنتجات المناسبة حتى لو الكلمات نفسها مو موجودة حرفيًا في الوصف.
- **الأسلوب:** product_support
- **المصدر:** Elastic — Semantic search for text
- **الرابط:** https://www.elastic.co/docs/solutions/search/semantic-search
- **عدد الكلمات:** 20

## SG100-052 — ذكاء السرب
- **النص:** تعتمد الآلية على عدد كبير من العناصر البسيطة التي تتخذ قرارات محلية وتتبادل الإشارات، بينما يظهر السلوك المنظم على مستوى المجموعة.
- **الأسلوب:** formal_technical
- **المصدر:** IBM — What are Agent Swarms and How Do They Work?
- **الرابط:** https://www.ibm.com/think/topics/agent-swarm
- **عدد الكلمات:** 21

## SG100-053 — ذكاء المستندات
- **النص:** نبغى المستخدم يرفع فاتورة أو نموذج، والسيستم يستخرج النص والجداول والحقول المهمة ويرجعها لنا بشكل منظم مباشرة.
- **الأسلوب:** product_support
- **المصدر:** Microsoft Learn — What Is Azure Document Intelligence?
- **الرابط:** https://learn.microsoft.com/azure/ai-services/document-intelligence/overview
- **عدد الكلمات:** 17

## SG100-054 — بحيرة البيانات
- **النص:** عندنا بيانات جاية من كل مكان وبصيغ مختلفة، ونبغى نخزنها خام أول وبعدين نقرر كيف نحللها حسب الحاجة.
- **الأسلوب:** social_saudi
- **المصدر:** AWS — What is a Data Lake?
- **الرابط:** https://aws.amazon.com/what-is/data-lake/
- **عدد الكلمات:** 18

## SG100-055 — انحدار لوجستي
- **النص:** عندي target ثنائي وأبي الناتج يكون احتمال بين صفر وواحد بدل قيمة خطية مفتوحة. وش النموذج البسيط المناسب؟
- **الأسلوب:** developer_question
- **المصدر:** Google for Developers — Logistic regression
- **الرابط:** https://developers.google.com/machine-learning/crash-course/logistic-regression
- **عدد الكلمات:** 18

## SG100-056 — أخلاقيات البيانات
- **النص:** قبل بدء المشروع راجع الفريق أسئلة الخصوصية والعدالة والشفافية ومدى ملاءمة جمع المعلومات ومشاركتها واستخدامها.
- **الأسلوب:** report_technical
- **المصدر:** UK Government — Data and AI Ethics Framework
- **الرابط:** https://www.gov.uk/government/publications/data-ethics-framework/data-and-ai-ethics-framework
- **عدد الكلمات:** 15

## SG100-057 — إنصاف فردي
- **النص:** يركز التقييم على ما إذا كان شخصان متشابهان في الخصائص ذات الصلة يحصلان على قرارات متقاربة من النظام.
- **الأسلوب:** formal_technical
- **المصدر:** Zhang et al. — Individual Fairness under Uncertainty
- **الرابط:** https://arxiv.org/abs/2302.08015
- **عدد الكلمات:** 18

## SG100-058 — صيغة جيسون
- **النص:** الـAPI يرجع لي كائنات نصية فيها مفاتيح وقيم وأقواس متداخلة، وأقدر أفكها بسهولة بين الخدمات المختلفة.
- **الأسلوب:** developer_issue
- **المصدر:** IETF — RFC 8259 — The JavaScript Object Notation Data Interchange Format
- **الرابط:** https://www.rfc-editor.org/rfc/rfc8259
- **عدد الكلمات:** 16

## SG100-059 — إم نيست
- **النص:** جربت نموذج بسيط على مجموعة صور صغيرة لأرقام مكتوبة باليد من صفر إلى تسعة، واستخدمتها للتدريب والاختبار.
- **الأسلوب:** social_tech
- **المصدر:** Yann LeCun et al. — The MNIST Database
- **الرابط:** http://yann.lecun.com/exdb/mnist/
- **عدد الكلمات:** 17

## SG100-060 — تكامل البيانات
- **النص:** تم توحيد سجلات العملاء القادمة من قاعدة البيانات ونظام المبيعات وملفات خارجية ضمن عرض واحد متسق للاستخدام التحليلي.
- **الأسلوب:** report_technical
- **المصدر:** IBM — What Is Data Integration?
- **الرابط:** https://www.ibm.com/think/topics/data-integration
- **عدد الكلمات:** 18

## SG100-061 — إطار تحديد
- **النص:** المودل يرجع أربع إحداثيات حول كل سيارة بالصورة، وأبي أرسم منها مستطيل يوضح مكان الجسم المكتشف.
- **الأسلوب:** developer_question
- **المصدر:** TensorFlow — Object Detection API
- **الرابط:** https://www.tensorflow.org/hub/tutorials/tf2_object_detection
- **عدد الكلمات:** 16

## SG100-062 — مؤشر راند
- **النص:** قارنّا نتيجتي تجميع مختلفتين عبر أزواج النقاط لنقيس مدى اتفاق الطريقتين في وضع العناصر معًا أو فصلها.
- **الأسلوب:** report_technical
- **المصدر:** scikit-learn — Adjusted Rand score
- **الرابط:** https://scikit-learn.org/stable/modules/generated/sklearn.metrics.adjusted_rand_score.html
- **عدد الكلمات:** 17

## SG100-063 — تعلُّم تدريجي
- **النص:** البيانات توصلنا يوميًا وما نقدر نعيد التدريب كامل كل مرة؛ نحتاج النموذج يحدث نفسه على الدفعات الجديدة بالتتابع.
- **الأسلوب:** developer_issue
- **المصدر:** scikit-learn — Out-of-core learning / incremental learning
- **الرابط:** https://scikit-learn.org/stable/computing/scaling_strategies.html#scaling-with-instances-using-out-of-core-learning
- **عدد الكلمات:** 18

## SG100-064 — خسارة مفصلية
- **النص:** في المصنف الحالي لا نعاقب الخطأ فقط؛ حتى التنبؤ الصحيح القريب جدًا من حد القرار يأخذ عقوبة حتى يكبر الهامش.
- **الأسلوب:** formal_technical
- **المصدر:** scikit-learn — hinge_loss
- **الرابط:** https://scikit-learn.org/stable/modules/generated/sklearn.metrics.hinge_loss.html
- **عدد الكلمات:** 20

## SG100-065 — تقطير النموذج
- **النص:** درّبنا نسخة أصغر لتقلد مخرجات النموذج الكبير، والهدف نحافظ على أكبر قدر من الجودة مع تكلفة تشغيل أقل.
- **الأسلوب:** report_technical
- **المصدر:** Hinton, Vinyals & Dean — Distilling the Knowledge in a Neural Network
- **الرابط:** https://arxiv.org/abs/1503.02531
- **عدد الكلمات:** 18

## SG100-066 — سياسة الاحتفاظ بالبيانات
- **النص:** تحدد الوثيقة مدة بقاء كل فئة من المعلومات في الأنظمة، ومتى يجب حذفها أو أرشفتها وفق المتطلبات القانونية والتشغيلية.
- **الأسلوب:** formal_technical
- **المصدر:** European Union — General Data Protection Regulation
- **الرابط:** https://eur-lex.europa.eu/eli/reg/2016/679/oj
- **عدد الكلمات:** 19

## SG100-067 — تشويش (أو بيانات مشوِّشة)
- **النص:** الـdataset فيها قيم عشوائية وأخطاء قياس كثيرة ما تضيف معنى، وصارت تخرب الإشارة اللي نحاول نتعلم منها.
- **الأسلوب:** social_tech
- **المصدر:** Google for Developers — Machine Learning Glossary
- **الرابط:** https://developers.google.com/machine-learning/glossary
- **عدد الكلمات:** 17

## SG100-068 — نظام متعدد الوكلاء
- **النص:** قسّمنا المهمة على عدة agents؛ واحد يبحث، الثاني يتحقق، والثالث ينسق النتيجة، وكلهم يتبادلون المعلومات أثناء التنفيذ.
- **الأسلوب:** product_support
- **المصدر:** IBM — What is a Multi-Agent System?
- **الرابط:** https://www.ibm.com/think/topics/multiagent-system
- **عدد الكلمات:** 17

## SG100-069 — مخطط عند القراءة
- **النص:** نخزن الملفات أولًا بصيغتها الخام، وما نفرض بنية ثابتة عليها إلا وقت الاستعلام بحسب طريقة التحليل المطلوبة.
- **الأسلوب:** formal_technical
- **المصدر:** AWS — What is a Data Lake?
- **الرابط:** https://aws.amazon.com/what-is/data-lake/
- **عدد الكلمات:** 17

## SG100-070 — انعدام تأثير الحجم
- **النص:** اختبرنا الصور بعد تكبير الجسم وتصغيره، وظلت استجابة النموذج متقاربة رغم اختلاف الحجم داخل الإطار.
- **الأسلوب:** report_technical
- **المصدر:** Google for Developers — Machine Learning Glossary
- **الرابط:** https://developers.google.com/machine-learning/glossary
- **عدد الكلمات:** 15

## SG100-071 — تقاطع على الاتحاد
- **النص:** في التقييم نقارن مساحة التداخل بين المستطيل المتوقع والحقيقي بمساحة تغطيتهما الكلية، وكلما ارتفعت النسبة كان التموضع أدق.
- **الأسلوب:** report_technical
- **المصدر:** Google for Developers — Machine Learning Glossary
- **الرابط:** https://developers.google.com/machine-learning/glossary
- **عدد الكلمات:** 18

## SG100-072 — مخزن الخصائص الآني
- **النص:** نحتاج قيم الـfeatures تكون جاهزة بزمن منخفض وقت وصول طلب التنبؤ، مو بس محفوظة لاستخدام التدريب الدفعي.
- **الأسلوب:** product_support
- **المصدر:** Google Cloud — Vertex AI Feature Store overview
- **الرابط:** https://cloud.google.com/vertex-ai/docs/featurestore/latest/overview
- **عدد الكلمات:** 17

## SG100-073 — ضبط تسوية أقصى
- **النص:** أضفت قيدًا يمنع متجه أوزان الطبقة من تجاوز حد معين، وإذا زاد حجمه يُعاد ضبطه بعد التحديث.
- **الأسلوب:** developer_issue
- **المصدر:** Keras — Layer weight constraints
- **الرابط:** https://keras.io/api/layers/constraints/
- **عدد الكلمات:** 17

## SG100-074 — ذكاء اصطناعي تحاوري
- **النص:** تتيح الخدمة للمستخدم التفاعل نصيًا أو صوتيًا مع النظام، مع فهم المقصد والسياق وإنتاج ردود طبيعية تشبه الحوار البشري.
- **الأسلوب:** formal_technical
- **المصدر:** IBM — What is Conversational AI?
- **الرابط:** https://www.ibm.com/think/topics/conversational-ai
- **عدد الكلمات:** 19

## SG100-075 — حوكمة البيانات المُتَّحِدة
- **النص:** تظل كل وحدة أعمال مسؤولة عن معلوماتها محليًا، مع التزام جميع الوحدات بمعايير مشتركة للجودة والأمن والوصول على مستوى المؤسسة.
- **الأسلوب:** report_technical
- **المصدر:** Microsoft Learn — Data mesh architecture
- **الرابط:** https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/scenarios/cloud-scale-analytics/architectures/data-mesh
- **عدد الكلمات:** 20

## SG100-076 — ذكاء ضيق اصطناعي
- **النص:** النظام ممتاز في مهمة محددة جدًا، لكن إذا طلبت منه شيء خارج المجال ما يقدر يعمم قدرته مثل الإنسان.
- **الأسلوب:** social_saudi
- **المصدر:** Google for Developers — Machine Learning Glossary
- **الرابط:** https://developers.google.com/machine-learning/glossary
- **عدد الكلمات:** 19

## SG100-077 — علامة مائية للمحتوى المولد بالذكاء الاصطناعي
- **النص:** تُضمَّن إشارة خفية يمكن للأدوات اكتشافها لاحقًا داخل الصورة المنشأة آليًا للمساعدة في إثبات مصدر المحتوى أو تتبع أصله.
- **الأسلوب:** formal_technical
- **المصدر:** NIST — Reducing Risks Posed by Synthetic Content
- **الرابط:** https://www.nist.gov/publications/reducing-risks-posed-synthetic-content-overview-technical-approaches-digital-content
- **عدد الكلمات:** 19

## SG100-078 — تَعرُّف على الوجوه
- **النص:** يستقبل النظام صورة أو لقطة فيديو ثم يقارن ملامح الوجه بهويات مسجلة لتحديد الشخص المحتمل.
- **الأسلوب:** report_technical
- **المصدر:** NIST — Face Recognition Technology Evaluation
- **الرابط:** https://www.nist.gov/programs-projects/face-recognition-technology-evaluation-frte
- **عدد الكلمات:** 15

## SG100-079 — ترجمة الآلة العصبية
- **النص:** تعالج المنظومة الجملة كاملة باستخدام شبكة عميقة وتتنبأ بتسلسل الكلمات في اللغة الهدف بدل ترجمة كل عبارة بشكل منفصل.
- **الأسلوب:** formal_technical
- **المصدر:** Google Research — Google's Neural Machine Translation System
- **الرابط:** https://research.google/pubs/googles-neural-machine-translation-system-bridging-the-gap-between-human-and-machine-translation/
- **عدد الكلمات:** 19

## SG100-080 — نموذج خطي مُعمَّم
- **النص:** نحتاج إطار انحدار يسمح بتوزيعات مختلفة للمتغير الناتج ويربط المتوسط بالمتغيرات التفسيرية عبر دالة ربط مناسبة.
- **الأسلوب:** report_technical
- **المصدر:** statsmodels — Generalized Linear Models
- **الرابط:** https://www.statsmodels.org/stable/glm.html
- **عدد الكلمات:** 16

## SG100-081 — وحدة خطية مصححة (ريلو)
- **النص:** حطيت activation ترجع صفر لأي قيمة سالبة وتخلي القيم الموجبة مثل ما هي. هل فيه سبب ما أستخدمها بكل الطبقات؟
- **الأسلوب:** developer_question
- **المصدر:** PyTorch — ReLU
- **الرابط:** https://docs.pytorch.org/docs/stable/generated/torch.nn.ReLU
- **عدد الكلمات:** 20

## SG100-082 — تعلُّم الآلة المستمر
- **النص:** المودل في الإنتاج يستقبل أمثلة جديدة طول الوقت ونبغاه يتحدث تدريجيًا بدل انتظار دورة تدريب كاملة كل أسبوع.
- **الأسلوب:** developer_issue
- **المصدر:** scikit-learn — Out-of-core learning / incremental learning
- **الرابط:** https://scikit-learn.org/stable/computing/scaling_strategies.html#scaling-with-instances-using-out-of-core-learning
- **عدد الكلمات:** 18

## SG100-083 — مربع الخسارة المفصلية
- **النص:** جرّبت نسخة تربيع عقوبة الهامش، وصارت الأمثلة المخالفة أو البعيدة عن الحد المطلوب تتلقى عقوبة أكبر بكثير.
- **الأسلوب:** developer_question
- **المصدر:** scikit-learn — hinge_loss
- **الرابط:** https://scikit-learn.org/stable/modules/generated/sklearn.metrics.hinge_loss.html
- **عدد الكلمات:** 17

## SG100-084 — انحدار المربعات الصغرى
- **النص:** قُدرت معاملات الخط المستقيم باختيار القيم التي تقلل مجموع مربعات الفروق بين القيم المرصودة والمتوقعة.
- **الأسلوب:** report_technical
- **المصدر:** statsmodels — Ordinary Least Squares
- **الرابط:** https://www.statsmodels.org/stable/generated/statsmodels.regression.linear_model.OLS.html
- **عدد الكلمات:** 15

## SG100-085 — قاعدة بيانات تشغيلية
- **النص:** تستقبل المنصة تحديثات المعاملات لحظيًا وتخدم قراءات وكتابات التطبيق اليومية بزمن قصير، وليست مخصصة للتحليلات التاريخية الثقيلة.
- **الأسلوب:** formal_technical
- **المصدر:** Microsoft Learn — Relational vs. NoSQL data
- **الرابط:** https://learn.microsoft.com/en-us/dotnet/architecture/cloud-native/relational-vs-nosql-data
- **عدد الكلمات:** 17

## SG100-086 — تخزين البيانات غير النشطة
- **النص:** ننقل الملفات اللي نادر نرجع لها إلى طبقة أرخص؛ الوصول لها أبطأ لكن تكلفة الاحتفاظ الطويل تنخفض كثير.
- **الأسلوب:** social_tech
- **المصدر:** AWS — Amazon S3 Glacier storage classes
- **الرابط:** https://aws.amazon.com/s3/storage-classes/glacier/
- **عدد الكلمات:** 18

## SG100-087 — حوكمة الذكاء الاصطناعي
- **النص:** اعتمدت المؤسسة سياسات وأدوارًا وضوابط لمراجعة المخاطر والشفافية والسلامة والمسؤوليات طوال دورة حياة أنظمة الذكاء الاصطناعي.
- **الأسلوب:** report_technical
- **المصدر:** NIST — AI Risk Management Framework
- **الرابط:** https://www.nist.gov/itl/ai-risk-management-framework
- **عدد الكلمات:** 16

## SG100-088 — تعلُّم التوصيف المعرفي
- **النص:** استخدم الفريق النصوص المتاحة لاستخراج المفاهيم والعلاقات واقتراح بنية معرفية منظمة بصورة آلية وشبه آلية.
- **الأسلوب:** formal_technical
- **المصدر:** Du et al. — A Short Review for Ontology Learning
- **الرابط:** https://arxiv.org/abs/2404.14991
- **عدد الكلمات:** 15

## SG100-089 — ذكاء اصطناعي مرتكز على الإنسان
- **النص:** يركز التصميم على أن تعزز التقنية قدرات المستخدم وتحافظ على رفاهيته وقيمه وحقوقه، بدل أن تجعل الإنسان عنصرًا ثانويًا في القرار.
- **الأسلوب:** formal_technical
- **المصدر:** NIST — Human-Centered AI
- **الرابط:** https://www.nist.gov/artificial-intelligence
- **عدد الكلمات:** 21

## SG100-090 — نفور من الخوارزميات
- **النص:** مع إن توصيات النظام كانت أدق من تقديرات الفريق، كثير منهم ظل يفضل حكم الموظف البشري وما يثق بالقرار الآلي.
- **الأسلوب:** social_saudi
- **المصدر:** Mahmud et al. — What influences algorithmic decision-making? A review on algorithm aversion
- **الرابط:** https://www.sciencedirect.com/science/article/pii/S0040162521008210
- **عدد الكلمات:** 20

## SG100-091 — نموذج غير علائقي
- **النص:** البيانات عندي مرنة ومتشعبة وما تناسب جداول ثابتة وعلاقات تقليدية، لذلك أفكر بتخزينها كمستندات أو أزواج مفتاح وقيمة.
- **الأسلوب:** developer_question
- **المصدر:** Microsoft Learn — Relational vs. NoSQL data
- **الرابط:** https://learn.microsoft.com/en-us/dotnet/architecture/cloud-native/relational-vs-nosql-data
- **عدد الكلمات:** 18

## SG100-092 — شبكة عصبية ترشيحية قابلة للفصل عمقًا
- **النص:** استبدلنا الالتفاف الكامل بعملية على كل قناة بشكل مستقل ثم مزج القنوات، وانخفضت العمليات الحسابية بشكل واضح.
- **الأسلوب:** report_technical
- **المصدر:** TensorFlow — tf.keras.layers.SeparableConv2D
- **الرابط:** https://www.tensorflow.org/api_docs/python/tf/keras/layers/SeparableConv2D
- **عدد الكلمات:** 17

## SG100-093 — تقليل المخاطر التجريبي
- **النص:** تختار عملية التدريب النموذج الذي يحقق أقل متوسط خسارة ممكن على العينة التدريبية المتاحة، ثم نقيّم قدرته على التعميم منفصلًا.
- **الأسلوب:** formal_technical
- **المصدر:** Stanford University — Learning theory / empirical risk minimization course material
- **الرابط:** https://web.stanford.edu/class/cs229/
- **عدد الكلمات:** 20

## SG100-094 — متغيرات مستقلة ومتطابقة التوزيع
- **النص:** نفترض في التحليل أن كل عينة لا تعتمد على الأخرى، وأن جميع العينات سُحبت من التوزيع الاحتمالي نفسه.
- **الأسلوب:** formal_technical
- **المصدر:** Stanford University — Introduction to Probability for Computer Scientists
- **الرابط:** https://web.stanford.edu/class/cs109/
- **عدد الكلمات:** 18

## SG100-095 — بوابة الذكاء الاصطناعي
- **النص:** نبي نقطة وسيطة واحدة تمر عبرها طلبات النماذج عشان نراقب التكلفة والأخطاء ونطبق حدود الاستخدام والتوجيه بين المزودين.
- **الأسلوب:** product_support
- **المصدر:** Cloudflare — AI Gateway Features
- **الرابط:** https://developers.cloudflare.com/ai-gateway/features/
- **عدد الكلمات:** 18

## SG100-096 — تحقق تقاطعي عن طريق عزل نقطة
- **النص:** عندي 80 عينة فقط؛ كل مرة أدرب على 79 وأختبر على العينة المتبقية، وأكرر العملية حتى تمر كل عينة مرة كاختبار.
- **الأسلوب:** developer_question
- **المصدر:** scikit-learn — LeaveOneOut
- **الرابط:** https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.LeaveOneOut.html
- **عدد الكلمات:** 21

## SG100-097 — دالة القاعدة الشعاعية
- **النص:** أحتاج تحويلًا تكون قيمته أعلى كلما كانت النقطة أقرب للمركز وتنخفض بسلاسة مع زيادة المسافة عنه.
- **الأسلوب:** developer_question
- **المصدر:** scikit-learn — RBF kernel
- **الرابط:** https://scikit-learn.org/stable/modules/generated/sklearn.gaussian_process.kernels.RBF.html
- **عدد الكلمات:** 16

## SG100-098 — تعرُّف آلي على الحروف
- **النص:** عندنا صور فواتير ممسوحة ضوئيًا ونبغى نستخرج الكلمات المكتوبة فيها إلى نص قابل للبحث والمعالجة آليًا.
- **الأسلوب:** product_support
- **المصدر:** Google Cloud — Detect and extract text from images
- **الرابط:** https://docs.cloud.google.com/vision/docs/ocr
- **عدد الكلمات:** 16

## SG100-099 — وحدة معالجة الرسوميات
- **النص:** تستخدم المنصة عتادًا ينفذ عددًا كبيرًا من العمليات بالتوازي، لذلك يسرّع تدريب الشبكات ومعالجة المصفوفات مقارنة بالمعالج العام في هذه الأحمال.
- **الأسلوب:** report_technical
- **المصدر:** NVIDIA — What Is a GPU?
- **الرابط:** https://www.nvidia.com/en-us/glossary/gpu/
- **عدد الكلمات:** 21

## SG100-100 — مشكلة انفجار التدرج
- **النص:** أثناء تدريب الشبكة بدأت قيم الـgradients تكبر بسرعة لدرجة أن تحديثات الأوزان صارت ضخمة والتدريب فقد الاستقرار.
- **الأسلوب:** developer_issue
- **المصدر:** Pascanu, Mikolov & Bengio — On the difficulty of training Recurrent Neural Networks
- **الرابط:** https://arxiv.org/abs/1211.5063
- **عدد الكلمات:** 17
