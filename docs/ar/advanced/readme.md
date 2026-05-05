---
title: المحوّلات والمقاييس المخصصة
category: المتقدم
description: إنشاء محوّلات مجموعات بيانات ومقاييس تقييم مخصصة لحالة استخدامك
order: 31
icon: code
---

# استخدام prompt-ops لحالتك الخاصة (مع أمثلة)

<div dir="rtl">

> **ملاحظة:** يشرح هذا الدليل كيفية إضافة حالات استخدام جديدة إلى prompt-ops إما عبر تهيئة المكوّنات الموجودة أو إنشاء مكوّنات مخصصة.

## نظرة عامة

عند إضافة حالة استخدامك إلى prompt-ops، ستحتاج إلى التعامل مع جانبين رئيسيين:

1. **معالجة مجموعة البيانات** — تحويل بياناتك إلى الصيغة الموحَّدة التي يعمل بها prompt-ops
2. **التقييم** — قياس مدى تطابق مخرجات النموذج مع النتائج المتوقعة

لكل جانب، لديك خياران:

- **استخدام محوّل مجموعة بيانات ومقياس موجود** مع التهيئة — أبسط وموصى به لمعظم الحالات
- **إنشاء محوّل ومقياس مخصص** — للمتطلبات المتخصصة التي لا يمكن التعامل معها بالمكوّنات الموجودة

---

## معالجة مجموعة البيانات: نهجان

### الخيار 1: استخدام محوّل موجود

يمكنك استخدام المحوّل المدمج إذا كانت مجموعة بياناتك تتبع إحدى الصيغ التالية:

#### المحوّلات المتاحة

| نوع المحوّل | صيغة مجموعة البيانات | متى تستخدمه |
|---|---|---|
| **StandardJSONAdapter** | `[{"question": "ما هو X؟", "answer": "Y"}]` | لمعظم مجموعات البيانات الشائعة ذات أزواج الإدخال/الإخراج البسيطة |
| **RAGJSONAdapter** | `[{"question": "...", "context": "...", "answer": "..."}]` | عندما تتضمن مجموعة البيانات سياقات استرداد |

راجع [دليل اختيار المحوّل التفصيلي](../../dataset_adapter_selection_guide.md) لمزيد من المعلومات. للعديد من مجموعات البيانات، يمكنك استخدام المحوّلات المدمجة مع تهيئة مخصصة في ملف YAML:

```yaml
dataset:
  adapter_class: "prompt_ops.core.datasets.StandardJSONAdapter"
  path: "/path/to/dataset.json"
  adapter_params:
    input_field: "question"
    output_field: "answer"
```

### الخيار 2: إنشاء محوّل مخصص

أنشئ محوّلًا مخصصًا عندما تتطلب مجموعة بياناتك معالجة متخصصة لا يمكن للمحوّلات الموجودة التعامل معها.

#### متى تُنشئ محوّلًا مخصصًا

أنشئ محوّلًا مخصصًا عندما:

1. **هيكل معقد** — لمجموعة البيانات هيكل متداخل أو غير قياسي
2. **معالجة خاصة** — تحتاج إلى معالجة أولية أو تطبيع خاص بالنطاق
3. **مصادر متعددة** — تدمج البيانات من ملفات أو مصادر متعددة
4. **تحقق مخصص** — تحتاج إلى التحقق من الأمثلة أو تصفيتها بناءً على قواعد محددة

---

## مقياس التقييم: نهجان

### الخيار 1: استخدام مقياس موجود

#### المقاييس المتاحة

| نوع المقياس | حالة الاستخدام | الصيغة المتوقعة | متى تستخدمه |
|---|---|---|---|
| **ExactMatchMetric** | مطابقة النص البسيطة | نص عادي | لمقارنة السلاسل النصية الدقيقة |
| **StandardJSONMetric** | تقييم منظَّم | كائنات JSON | لمقارنة حقول محددة في استجابات JSON منظَّمة |

راجع [دليل اختيار المقاييس التفصيلي](../../metric_selection_guide.md) لمزيد من المعلومات:

```yaml
metric:
  class: "prompt_ops.core.metrics.StandardJSONMetric"
  params:
    output_fields: ["categories", "sentiment"]
    required_fields: ["categories"]
```

### الخيار 2: إنشاء مقياس مخصص

أنشئ مقياسًا مخصصًا عندما تحتاج إلى منطق تقييم متخصص لا يمكن للمقاييس الموجودة التعامل معه.

#### متى تُنشئ مقياسًا مخصصًا

أنشئ مقياسًا مخصصًا عندما:

1. **تسجيل خاص بالنطاق** — تحتاج إلى قواعد تسجيل متخصصة
2. **تقييم معقد** — يتطلب تقييمك تقييمًا متعدد الخطوات أو متعدد الجوانب
3. **تحليل مخصص** — تحتاج إلى تحليل خاص لمخرجات النموذج
4. **صيغة إخراج متخصصة** — نموذجك يُخرج بصيغة غير مدعومة من المقاييس الموجودة

---

## تطبيق المكوّنات المخصصة

يمكنك إنشاء محوّلات ومقاييس مخصصة في ملف Python واحد يمكن الإشارة إليه في تهيئة YAML.

### الهيكل الأساسي

أنشئ ملف Python (مثل `my_custom_adapters.py`) بالهيكل التالي:

```python
from typing import Dict, List, Any, Union
from pathlib import Path
from prompt_ops.core.datasets import DatasetAdapter
from prompt_ops.core.metrics import MetricBase

class MyCustomAdapter(DatasetAdapter):
    """
    محوّل مخصص لتحويل صيغ مجموعات البيانات إلى صيغة موحَّدة.
    """

    def __init__(self, dataset_path: str, **kwargs):
        """
        تهيئة محوّل مجموعة البيانات بمسار ملف مجموعة البيانات.

        Args:
            dataset_path: مسار ملف مجموعة البيانات
            **kwargs: معاملات تهيئة إضافية من تهيئة YAML
        """
        super().__init__(dataset_path)
        # تهيئة أي معاملات مخصصة هنا

    def adapt(self) -> List[Dict[str, Any]]:
        """
        تحويل الصيغة الخاصة بمجموعة البيانات إلى الصيغة الموحَّدة.

        Returns:
            قائمة من الأمثلة الموحَّدة بالصيغة:
            [
                {
                    "inputs": {"question": "نص الإدخال هنا"},
                    "outputs": {"answer": "الإخراج المتوقع هنا"},
                    "metadata": {"optional": "بيانات وصفية"}  # اختياري
                },
                ...
            ]
        """
        # تنفيذك هنا
        pass

class MyCustomMetric(MetricBase):
    """
    مقياس مخصص لتقييم التوقعات.
    """

    def __init__(self, **kwargs):
        """
        تهيئة المقياس بمعاملات مخصصة.

        Args:
            **kwargs: معاملات التهيئة من تهيئة YAML
        """
        # تهيئة أي معاملات مخصصة هنا

    def __call__(self, gold: Any, pred: Any, trace: bool = False, **kwargs) -> Union[Dict[str, float], float]:
        """
        تقييم توقع مقابل الحقيقة الأرضية.

        Args:
            gold: مثال الحقيقة الأرضية
            pred: توقع النموذج للتقييم
            trace: ما إذا كان سيتم إرجاع نتائج مفصّلة
            **kwargs: معاملات إضافية

        Returns:
            نتيجة بين 0.0 و1.0 أو قاموس من النتائج
        """
        # تنفيذك هنا
        pass
```

### الصيغة الموحَّدة

تُحوّل طريقة `DatasetAdapter.adapt()` مجموعة البيانات المخصصة إلى صيغة موحَّدة:

```python
{
    "inputs": {
        # حقول الإدخال التي ستُمرَّر إلى النموذج
        "question": "نص الإدخال هنا",  # مطلوب
    },
    "outputs": {
        # حقول الإخراج المتوقعة للتقييم
        "answer": "الإخراج المتوقع هنا",  # مطلوب
    },
    "metadata": {  # اختياري
        "id": "example-123",
        "source": "training-set",
    }
}
```

---

## مثال عملي: تصنيف خدمة العملاء

لنستعرض مثالًا متكاملًا لإضافة حالة استخدام تصنيف خدمة العملاء إلى prompt-ops.

### الخطوة 1: تحليل مجموعة البيانات

افحص أولًا هيكل مجموعة البيانات لتحديد ما إذا كنت تحتاج إلى محوّل مخصص:

```json
[
  {
    "customer_message": "التدفئة في شقتي لا تعمل والجو بارد جدًا!",
    "priority": "high",
    "categories": {"maintenance": true, "heating": true},
    "sentiment": "negative"
  }
]
```

### الخطوة 2: اختيار نهجك

**الخيار أ: استخدام StandardJSONAdapter مع التهيئة**

```yaml
dataset:
  adapter_class: "prompt_ops.core.datasets.StandardJSONAdapter"
  path: "/path/to/customer_service.json"
  adapter_params:
    input_field: "customer_message"
    output_field: {"urgency": "priority", "categories": "categories", "sentiment": "sentiment"}
```

**الخيار ب: إنشاء محوّل مخصص للتحكم الكامل**

```python
# customer_service.py
import json
from typing import Dict, List, Any
from prompt_ops.core.datasets import DatasetAdapter
from prompt_ops.core.metrics import MetricBase

class CustomerServiceAdapter(DatasetAdapter):
    """محوّل لمجموعات بيانات خدمة العملاء."""

    def __init__(self, dataset_path: str, **kwargs):
        super().__init__(dataset_path)

    def adapt(self) -> List[Dict[str, Any]]:
        """تحويل بيانات خدمة العملاء إلى الصيغة الموحَّدة."""
        with open(self.dataset_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        standardized_data = []
        for item in data:
            urgency = self._map_priority(item.get("priority", ""))
            example = {
                "inputs": {
                    "question": item.get("customer_message", "")
                },
                "outputs": {
                    "answer": {
                        "urgency": urgency,
                        "categories": item.get("categories", {}),
                        "sentiment": item.get("sentiment", "")
                    }
                }
            }
            standardized_data.append(example)
        return standardized_data

    def _map_priority(self, priority: str) -> str:
        """تعيين قيم الأولوية إلى مستويات الإلحاح الموحَّدة."""
        priority_map = {
            "critical": "high",
            "high": "high",
            "medium": "medium",
            "low": "low"
        }
        return priority_map.get(priority.lower(), "medium")


class CustomerServiceMetric(MetricBase):
    """مقياس لتقييم توقعات خدمة العملاء."""

    def __init__(self, weights: Dict[str, float] = None, **kwargs):
        self.weights = weights or {
            "categories": 0.5,
            "sentiment": 0.3,
            "urgency": 0.2
        }

    def __call__(self, gold: Any, pred: Any, trace: bool = False, **kwargs):
        """تقييم التوقع مقابل الحقيقة الأرضية."""
        if isinstance(pred, str):
            try:
                pred = json.loads(pred)
            except json.JSONDecodeError:
                return 0.0

        gold_data = gold.get("answer", gold)
        category_score = self._evaluate_categories(gold_data, pred)
        sentiment_score = self._evaluate_sentiment(gold_data, pred)
        urgency_score = self._evaluate_urgency(gold_data, pred)

        total_score = (
            self.weights["categories"] * category_score +
            self.weights["sentiment"] * sentiment_score +
            self.weights["urgency"] * urgency_score
        )

        if trace:
            return {
                "categories": category_score,
                "sentiment": sentiment_score,
                "urgency": urgency_score,
                "overall": total_score
            }
        return total_score

    def _evaluate_categories(self, gold, pred):
        """تقييم توقعات الفئات باستخدام نتيجة F1."""
        return 1.0  # عنصر نائب

    def _evaluate_sentiment(self, gold, pred):
        """تقييم توقع المشاعر."""
        return 1.0  # عنصر نائب

    def _evaluate_urgency(self, gold, pred):
        """تقييم توقع الإلحاح."""
        return 1.0  # عنصر نائب
```

### الخطوة 3: إنشاء ملف التهيئة

```yaml
# customer_service_config.yaml
dataset:
  adapter_class: "path.to.your.module.CustomerServiceAdapter"
  path: "/path/to/customer_service.json"

metric:
  class: "path.to.your.module.CustomerServiceMetric"
  params:
    weights:
      categories: 0.5
      sentiment: 0.3
      urgency: 0.2

model:
  name: "openrouter/meta-llama/llama-3.3-70b-instruct"
  api_base: "https://openrouter.ai/api/v1"

prompt:
  text: |
    حلّل رسالة خدمة العملاء التالية وقدّم:
    1. مستوى الإلحاح (high، medium، أو low)
    2. المشاعر (positive، negative، أو neutral)
    3. الفئات المنطبقة (صيانة، فواتير، إلخ)

    الرسالة: {{question}}

    أجب بصيغة JSON بالهيكل التالي:
    {"urgency": "...", "sentiment": "...", "categories": {"category1": true, ...}}
```

### الخطوة 4: تشغيل prompt-ops

```bash
# تعيين مفتاح API
export OPENROUTER_API_KEY=your_key_here

# تشغيل prompt-ops بتهيئتك
prompt-ops migrate --config path/to/customer_service_config.yaml
```

---

## الخاتمة

عند إضافة حالة استخدام جديدة إلى prompt-ops، لديك نهجان:

1. **تهيئة المكوّنات الموجودة** — أبسط وكافٍ لمعظم الحالات الشائعة
2. **إنشاء مكوّنات مخصصة** — للمتطلبات المتخصصة التي تحتاج إلى معالجة مخصصة

هندسة برومبت موفقة!

</div>
