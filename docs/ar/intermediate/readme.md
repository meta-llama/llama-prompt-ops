---
title: دليل تهيئة YAML
category: المتوسط
description: تعمّق في جميع خيارات تهيئة YAML لتحسين البرومبت
order: 20
icon: code
---

# الدليل المتوسط: تهيئة YAML لتحسين البرومبت

<div dir="rtl">

> **ملاحظة:** إذا كنت جديدًا على prompt-ops، ابدأ بـ [دليل البدء السريع](../basic/readme.md) قبل استكشاف هذه الخيارات المتقدمة.

## نظرة عامة

يستكشف هذا الدليل المتوسط خيارات التهيئة المتاحة لتحسين البرومبتات في مهمة تصنيف إدارة المرافق. سنفحص كل مكوّن من مكوّنات ملف تهيئة YAML بالتفصيل، ونشرح ما يفعله كل إعداد وكيفية تخصيصه لاحتياجاتك الخاصة.

تتضمن مهمة تصنيف إدارة المرافق تصنيف رسائل خدمة العملاء وفق:

1. مستوى الإلحاح
2. مشاعر العميل
3. فئات الخدمة ذات الصلة

---

## هيكل التهيئة الكاملة

أنشئ ملفًا باسم `facility.yaml` في دليل `configs` بالهيكل التالي. يوضح هذا المثال جميع الخيارات المتاحة:

```yaml
# تهيئة النموذج
model:
  name: "openrouter/meta-llama/llama-3.3-70b-instruct"
  api_base: "https://openrouter.ai/api/v1"
  temperature: 0.0
  max_tokens: 2048
  top_p: 0.95
  cache: false

# تهيئة مجموعة البيانات
dataset:
  adapter_class: "prompt_ops.core.datasets.ConfigurableJSONAdapter"
  path: "../use-cases/facility-support-analyzer/facility_v2_test.json"
  train_size: 0.7
  validation_size: 0.15
  input_field: ["fields", "input"]
  golden_output_field: "answer"
  seed: 42
  shuffle: true

# تهيئة البرومبت
prompt:
  file: "../use-cases/facility-support-analyzer/facility_prompt_sys.txt"
  inputs: ["question"]
  outputs: ["answer"]

# تهيئة المقياس
metric:
  class: "prompt_ops.core.metrics.FacilityMetric"
  strict_json: false
  output_field: "answer"

# إعدادات التحسين
optimization:
  strategy: "basic"
  max_rounds: 3
  max_examples_per_round: 5
  max_prompt_length: 2048
  num_candidates: 5
  bootstrap_examples: 4
  num_threads: 36
  max_errors: 5
  disable_progress_bar: false
  save_intermediate: false
  model_family: "llama"
```

---

## تهيئة النموذج

يُحدّد قسم `model` نموذج اللغة المستخدَم للاستدلال وتحسين البرومبتات:

```yaml
model:
  name: "openrouter/meta-llama/llama-3.3-70b-instruct"
  api_base: "https://openrouter.ai/api/v1"
  temperature: 0.0
  max_tokens: 2048
  top_p: 0.95
  cache: false
```

| المعامل | الوصف | القيم الموصى بها |
|---|---|---|
| `name` | معرّف النموذج بصيغة LiteLLM (`provider/model_name`) | لنماذج Llama: `openrouter/meta-llama/llama-3.3-70b-instruct` |
| `api_base` | نقطة نهاية API للمزوّد | OpenRouter: `https://openrouter.ai/api/v1` |
| `temperature` | يتحكم في العشوائية (0.0–1.0) | للتصنيف: `0.0` (حتمي) / للمهام الإبداعية: `0.7` |
| `max_tokens` | الحد الأقصى لطول الاستجابة | للمخرجات بصيغة JSON: `2048` |
| `top_p` | معامل أخذ العينات النووية (0.0–1.0) | `0.95` للنتائج المتوازنة |
| `cache` | ما إذا كان سيتم تخزين استجابات النموذج مؤقتًا | `true` لتوفير استدعاءات API خلال التطوير |

**خيارات متقدمة:**

- `top_k`: يحدّ من اختيار الرموز بأعلى K رموز احتمالًا
- `frequency_penalty`: يقلّل التكرار بمعاقبة الرموز التي ظهرت مسبقًا
- `presence_penalty`: يُشجّع التنوع بمعاقبة الرموز بناءً على وجودها

---

## تهيئة مجموعة البيانات

يُحدّد قسم `dataset` كيفية تحميل الأمثلة ومعالجتها:

```yaml
dataset:
  adapter_class: "prompt_ops.core.datasets.ConfigurableJSONAdapter"
  path: "/path/to/dataset.json"
  train_size: 0.7
  validation_size: 0.15
  seed: 42
  shuffle: true
  input_field: ["fields", "input"]
  golden_output_field: "answer"
```

| المعامل | الوصف | القيم الموصى بها |
|---|---|---|
| `adapter_class` | الفئة التي تتولى تحميل مجموعة البيانات | JSON قياسي: `prompt_ops.core.datasets.ConfigurableJSONAdapter` |
| `path` | مسار ملف مجموعة البيانات | يُفضَّل المسار المطلق |
| `train_size` | نسبة البيانات المستخدمة للتدريب | `0.7` (70%) |
| `validation_size` | نسبة البيانات المستخدمة للتحقق | `0.15` (15%) |
| `seed` | البذرة العشوائية لإعادة الإنتاج | أي عدد صحيح (مثل `42`) |
| `shuffle` | ما إذا كان سيتم خلط مجموعة البيانات | `true` لتعميم أفضل |
| `input_field` | موقع المدخل في كل مثال | للحقول المتداخلة: `["fields", "input"]` |
| `golden_output_field` | موقع الإخراج المتوقع | للاستجابات بصيغة JSON: `"answer"` |

---

## تهيئة البرومبت

يُحدّد قسم `prompt` البرومبت الأولي وكيفية تفاعله مع مجموعة البيانات. يمكنك توفير البرومبت بطريقتين:

```yaml
prompt:
  # الخيار 1: نص مضمّن
  text: |
    بالنظر إلى الرسالة التالية:
    ---
    {{question}}
    ---
    استخرج وأرجِع كائن JSON...

  # الخيار 2: مسار ملف
  file: "../use-cases/facility-support-analyzer/facility_prompt_sys.txt"
  inputs: ["question"]
  outputs: ["answer"]
```

| المعامل | الوصف | القيم الموصى بها |
|---|---|---|
| `text` | نص قالب البرومبت | أدرج تعليمات واضحة وصيغة الإخراج |
| `file` | بديل: مسار إلى ملف برومبت | استخدمه بدلًا من `text` للبرومبتات الطويلة |
| `inputs` | حقول مجموعة البيانات للإدراج في البرومبت | تطابق العناصر النائبة في برومبتك (مثل `["question"]`) |
| `outputs` | الحقول التي يجب التقاطها من استجابة النموذج | للمخرجات بصيغة JSON: `["answer"]` |

**نصائح لقوالب البرومبت:**

- استخدم عناصر نائبة مثل `{{question}}` سيتم استبدالها بقيم مجموعة البيانات
- بالنسبة لنماذج Llama، كن صريحًا بشأن متطلبات صيغة الإخراج
- أدرج أمثلة على صيغة الإخراج المتوقعة للحصول على نتائج أفضل

---

## تهيئة المقياس

يُحدّد قسم `metric` كيفية تقييم أداء البرومبت:

```yaml
metric:
  class: "prompt_ops.core.metrics.FacilityMetric"
  strict_json: false
  output_field: "answer"
```

| المعامل | الوصف | القيم الموصى بها |
|---|---|---|
| `class` | فئة المقياس المستخدمة | للـ JSON: `prompt_ops.core.metrics.StandardJSONMetric` |
| `strict_json` | ما إذا كان يجب أن يكون JSON دقيقًا | `false` يسمح باستخراج JSON من النص |
| `output_field` | الحقل الذي سيُلتقط من استجابة النموذج | للمخرجات بصيغة JSON: `"answer"` |

---

## إعدادات التحسين

يتحكم قسم `optimization` في كيفية تعامل prompt-ops مع عملية التحسين:

```yaml
optimization:
  strategy: "llama"
  max_rounds: 3
  max_examples_per_round: 5
  max_prompt_length: 2048
  num_candidates: 5
  bootstrap_examples: 4
  num_threads: 36
  max_errors: 5
  disable_progress_bar: false
  save_intermediate: false
  model_family: "llama"
```

| المعامل | الوصف | القيم الموصى بها |
|---|---|---|
| `strategy` | نهج التحسين | للنتائج السريعة: `"basic"` / لتحسين Llama (تجريبي): `"llama"` |
| `max_rounds` | عدد جولات التحسين | `3` للاستراتيجية الأساسية |
| `max_examples_per_round` | الأمثلة المستخدمة في كل جولة | `5` للنتائج الأسرع |
| `max_prompt_length` | الحد الأقصى لطول البرومبت المحسَّن | `2048` لمعظم المهام |
| `num_candidates` | أشكال البرومبت المُجرَّبة | `5` للاستكشاف المتوازن |
| `bootstrap_examples` | الأمثلة المُدرَجة في البرومبت | `4` للتعلم من أمثلة قليلة |
| `num_threads` | خيوط المعالجة المتوازية | `36` للمعالجة الأسرع |
| `max_errors` | الأخطاء قبل التوقف | `5` لتجنب إهدار استدعاءات API |
| `disable_progress_bar` | إخفاء شريط التقدم | `false` لرؤية التقدم |
| `save_intermediate` | حفظ النتائج المؤقتة | `true` لأغراض التشخيص |
| `model_family` | تحسينات خاصة بالنموذج | `"llama"` لنماذج Llama |

**شرح خيارات الاستراتيجية:**

- `basic`: يُجري تغييرات بسيطة للحفاظ على هيكل البرومبت الأصلي (الأسرع)
- `llama`: تحسين خاص بـ Llama (موصى به)
- `advanced`: تعديلات أكثر شمولًا لتحقيق أقصى أداء (الأبطأ)

---

## التشغيل بالتهيئة المتقدمة

لتشغيل prompt-ops بتهيئتك المتقدمة:

```bash
# إنشاء ملف .env مع مفتاح API
echo "OPENROUTER_API_KEY=your_key_here" > .env

# تشغيل التحسين
prompt-ops migrate --config configs/facility.yaml
```

يمكنك تجاوز قيم تهيئة معينة عبر سطر الأوامر:

```bash
# تجاوز النموذج بنقطة نهاية Llama مختلفة
prompt-ops migrate --config configs/facility.yaml --model together/meta-llama/Llama-3-70b-chat

# تجاوز مسار مجموعة البيانات
prompt-ops migrate --config configs/facility.yaml --dataset-path /path/to/new/dataset.json
```

---

## ملفات الإخراج

بعد التحسين، يُنشئ prompt-ops ملفات إخراج مفصّلة:

1. **ملف JSON للنتائج**: يحتوي على مقاييس الأداء والبرومبت المحسَّن
   - الموقع: `results/facility_TIMESTAMP.json`

2. **تهيئة YAML**: تهيئة محسَّنة جاهزة للاستخدام
   - الموقع: `results/facility_TIMESTAMP.yaml`

يتضمن البرومبت المحسَّن عادةً:
- برومبت نظام مُحسَّن
- أمثلة قليلة مختارة من مجموعة البيانات الخاصة بك
- تحسينات في التنسيق لتوافق أفضل مع النموذج

---

## الخاتمة

غطّى هذا الدليل المتوسط خيارات التهيئة الرئيسية المتاحة في prompt-ops. بفهم هذه الإعدادات وتخصيصها، يمكنك تحقيق نتائج أفضل لحالة استخدامك المحددة.

لحالات الاستخدام الأكثر تقدمًا، كإنشاء محوّلات ومقاييس مخصصة، راجع [الدليل المتقدم](../advanced/readme.md).

</div>
