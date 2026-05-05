---
title: دليل البدء السريع
category: الأساسيات
description: حسِّن برومبتك الأول في 5 دقائق عبر شرح موجَّه خطوة بخطوة
order: 2
icon: zap
---

# دليل البدء السريع: تحسين البرومبتات في 5 دقائق

<div dir="rtl">

## ما الذي ستبنيه

في هذا الدليل السريع، ستحسّن برومبتًا لتصنيف رسائل خدمة العملاء ببضعة أوامر فقط. سيستخرج النظام:

- **مستوى الإلحاح**: عالٍ، متوسط، أو منخفض
- **المشاعر**: إيجابية، محايدة، أو سلبية
- **الفئات**: فئات الخدمة ذات الصلة من قائمة محددة مسبقًا

يمكنك استكشاف مجموعة البيانات والبرومبت الكاملَين في دليل `use-cases/facility-support-analyzer`.

---

## فهم محلّل دعم المرافق

قبل التثبيت، لنلقِ نظرة على مكوّنات حالة الاستخدام هذه. ستجد الملفات ذات الصلة في دليل [`use-cases/facility-support-analyzer`](../../../use-cases/facility-support-analyzer/):

- [`facility_prompt_sys.txt`](../../../use-cases/facility-support-analyzer/facility_prompt_sys.txt) — برومبت النظام للمهمة
- [`facility_v2_test.json`](../../../use-cases/facility-support-analyzer/facility_v2_test.json) — مجموعة البيانات مع رسائل خدمة العملاء
- [`facility-simple.yaml`](../../../use-cases/facility-support-analyzer/facility-simple.yaml) — ملف التهيئة البسيط
- [`eval.ipynb`](../../../use-cases/facility-support-analyzer/eval.ipynb) — دفتر التقييم

### برومبت النظام الحالي

يوجّه برومبت النظام نموذج اللغة لتحليل رسائل خدمة العملاء واستخراج معلومات منظَّمة بصيغة JSON:

```
أنت مساعد مفيد. استخرج وأرجِع كائن JSON يحتوي على المفاتيح والقيم التالية:
- "urgency" بإحدى القيم: `high`، `medium`، `low`
- "sentiment" بإحدى القيم: `negative`، `neutral`، `positive`
- "categories" قاموس بالفئات كمفاتيح وقيم منطقية (True/False)...
يجب أن تكون رسالتك الكاملة سلسلة JSON صالحة تُقرأ مباشرةً.
```

### صيغة مجموعة البيانات

تتكوّن مجموعة البيانات من رسائل خدمة عملاء بصيغة JSON. كل إدخال يحتوي على:

1. حقل إدخال يضم رسالة العميل (عادةً بريد إلكتروني أو تذكرة دعم)
2. حقل إجابة يضم الإخراج المتوقع بصيغة JSON

مثال على إدخال:

```json
{
  "fields": {
    "input": "الموضوع: إصلاح عاجل لنظام التدفئة والتهوية\n\nمرحبًا، أتواصل معكم بشأن مشكلة عاجلة تحتاج إلى اهتمام فوري..."
  },
  "answer": "{\"categories\": {\"emergency_repair_services\": true, ...}, \"sentiment\": \"positive\", \"urgency\": \"high\"}"
}
```

### حساب المقياس

يقيّم FacilityMetric مخرجات النموذج بمقارنتها مع الإجابات الصحيحة. يتحقق من:

1. **تصنيف الإلحاح**: دقة تحديد ما إذا كان الطلب عالي أو متوسط أو منخفض الأولوية
2. **تحليل المشاعر**: دقة تصنيف نبرة العميل
3. **وسوم الفئات**: الدقة والاسترجاع في تحديد فئات الخدمة الصحيحة

---

## الخطوة 1: التثبيت

```bash
# إنشاء بيئة افتراضية
conda create -n prompt-ops python=3.10
conda activate prompt-ops

# التثبيت من المصدر (موصى به)
git clone https://github.com/meta-llama/prompt-ops.git
cd prompt-ops
pip install -e .

# أو التثبيت من PyPI
pip install prompt-ops
```

## الخطوة 2: إنشاء مشروع نموذجي

بشكل افتراضي، سيُنشئ هذا الأمر الملفات اللازمة لمحلّل دعم المرافق في الدليل الحالي باسم `my-project`:

```bash
prompt-ops create my-project
cd my-project
```

### الإخراج

سيُنشأ الدليل بتهيئة نموذجية ومجموعة بيانات في المجلد الحالي:

```
my-project
├── .env
├── README.md
├── config.yaml
├── data
│   └── dataset.json
├── prompts
│   └── prompt.txt
└── results
```

## الخطوة 3: إعداد مفتاح API

أضف مفتاح API إلى ملف `.env`:

```bash
OPENROUTER_API_KEY=your_key_here
```

يمكنك الحصول على مفتاح OpenRouter بإنشاء حساب على [OpenRouter](https://openrouter.ai/). لمزيد من خيارات مزودي الاستدلال، راجع [دليل مزودي الاستدلال](../inference_providers.md).

## الخطوة 4: تشغيل التحسين

```bash
prompt-ops migrate  # يستخدم config.yaml افتراضيًا إذا لم يُحدَّد --config
```

اكتمل الأمر! سيُحفظ البرومبت المحسَّن في دليل `results` مع مقاييس أداء تقارن بين النسخة الأصلية والمحسَّنة.

---

## مثال على الإخراج

سيُحفظ البرومبت المحسَّن في دليل `results/` باسم مثل `facility-simple_YYYYMMDD_HHMMSS.yaml`. عند فتح هذا الملف، ستجد شيئًا كالتالي:

```yaml
system: |-
  حلّل رسالة العميل وحدد مستوى الإلحاح والمشاعر والفئات ذات الصلة.
  استخرج وأرجِع كائن JSON بالمفاتيح "urgency" و"sentiment" و"categories"...

  أمثلة:
  المثال 1:
      السؤال: دورة المياه في مكتبنا تحتاج إلى تنظيف عاجل. المراحيض مسدودة...
      الإجابة: {"urgency": "high", "sentiment": "negative", ...}
```

---

## الخطوات التالية

**استكشف [دليل التهيئة المتوسط](../intermediate/readme.md)** للتعرف على خيارات التهيئة المتقدمة، بما في ذلك إعدادات النماذج المخصصة ومعاملات مجموعة البيانات وضبط FacilityMetric.

</div>
