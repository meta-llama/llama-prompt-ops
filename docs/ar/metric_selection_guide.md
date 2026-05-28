---
title: دليل اختيار المقياس
category: الأدلة
description: اختر مقاييس التقييم المناسبة لحالة استخدامك في التحسين
order: 10
icon: settings
---

# دليل اختيار المقياس

<div dir="rtl">

يساعدك هذا الدليل على اختيار مقياس التقييم المناسب لحالة استخدامك، أو تحديد متى يجب إنشاء مقياس مخصص.

## مصفوفة مقارنة المقاييس

| نوع المقياس | حالة الاستخدام | الصيغة المتوقعة | متى تستخدمه |
|---|---|---|---|
| **ExactMatchMetric** | المطابقة النصية البسيطة | نصوص عادية | عند الحاجة إلى مطابقة دقيقة للسلاسل النصية بين التوقع والحقيقة الأرضية |
| **StandardJSONMetric** | تقييم JSON الهيكلي | كائنات JSON أو نصوص | عند تقييم استجابات JSON منظَّمة بحقول محددة للمقارنة |
| **مقياس مخصص** | احتياجات تقييم متخصصة | أي صيغة مخصصة | عندما لا تلبّي المقاييس الموجودة احتياجاتك |

---

## متى تُنشئ مقياسًا مخصصًا

أنشئ مقياسًا مخصصًا عندما:

1. **منطق تقييم معقد**: يتطلب تقييمك منطقًا معقدًا لا يمكن التعامل معه عبر تهيئة المقاييس الموجودة
2. **تسجيل خاص بالنطاق**: تحتاج إلى قواعد تسجيل أو تطبيع خاصة بالنطاق
3. **تقييم متعدد الخطوات**: تتضمن عملية التقييم خطوات أو مقارنات متعددة
4. **تحليل مخصص**: تحتاج إلى منطق تحليل خاص لتوقعاتك أو حقيقتك الأرضية
5. **صيغة إخراج متخصصة**: نموذجك يُخرج بصيغة غير مدعومة من المقاييس الموجودة

---

## مثال على تطبيق مقياس مخصص

```python
from prompt_ops.core.metrics import MetricBase

class MyCustomMetric(MetricBase):
    def __init__(self, custom_param=None, **kwargs):
        # تهيئة أي معاملات مخصصة
        self.custom_param = custom_param

    def __call__(self, gold, pred, trace=False, **kwargs):
        """
        تقييم التوقع مقابل الحقيقة الأرضية.

        Args:
            gold: مثال الحقيقة الأرضية
            pred: المثال المُتوقَّع
            trace: ما إذا كان سيتم تفعيل التتبع لأغراض التشخيص

        Returns:
            إما قاموس يحتوي على نتائج المقاييس أو نتيجة float واحدة
        """
        # استخراج القيم من gold وpred
        gold_value = self.extract_value(gold, "answer", gold)
        pred_value = self.extract_value(pred, "answer", pred)

        # منطق التقييم المخصص الخاص بك هنا
        score = self._calculate_score(gold_value, pred_value)

        if trace:
            # إرجاع نتائج مفصّلة لأغراض التشخيص
            return {
                "score": score,
                "details": {
                    "gold": gold_value,
                    "pred": pred_value,
                    # أضف أي تفاصيل أخرى
                }
            }

        # إرجاع نتيجة واحدة للاستخدام العادي
        return score

    def _calculate_score(self, gold, pred):
        # طبّق منطق التسجيل المخصص هنا
        # أرجِع نتيجة float بين 0.0 و1.0
        pass
```

---

## أمثلة التهيئة

### تهيئة ExactMatchMetric

```yaml
metric:
  class: "prompt_ops.core.metrics.ExactMatchMetric"
  params:
    case_sensitive: false
    strip_whitespace: true
```

### تهيئة StandardJSONMetric

```yaml
metric:
  class: "prompt_ops.core.metrics.StandardJSONMetric"
  params:
    output_fields: ["categories", "sentiment", "urgency"]
    required_fields: ["categories"]
    nested_fields:
      categories: ["cleaning_services", "maintenance", "security"]
    field_weights:
      categories: 0.6
      sentiment: 0.2
      urgency: 0.2
    evaluation_mode: "selected_fields_comparison"
```

### تهيئة FacilityMetric

```yaml
metric:
  class: "prompt_ops.core.metrics.FacilityMetric"
  params:
    output_field: "answer"
    strict_json: false
```

---

## أمثلة على تطبيقات المقاييس

لاحتياجات التقييم الأكثر تعقيدًا، يمكنك تطبيق مقاييس متخصصة. على سبيل المثال:

- يوضح [مقياس HotpotQA](../../src/prompt_ops/datasets/hotpotqa/metric.py) كيفية تطبيق تقييم متخصص للإجابة على الأسئلة متعددة الخطوات، بما في ذلك معالجة دقة الإجابة والتحقق من الحقائق الداعمة.

</div>
