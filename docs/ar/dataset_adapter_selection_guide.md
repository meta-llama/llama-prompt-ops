---
title: دليل اختيار محوّل مجموعة البيانات
category: الأدلة
description: تهيئة محوّلات مجموعات البيانات للصيغ والهياكل المختلفة
order: 11
icon: file-text
---

# دليل اختيار محوّل مجموعة البيانات

<div dir="rtl">

يساعدك هذا الدليل على اختيار محوّل مجموعة البيانات المناسب لحالة استخدامك، أو تحديد متى يجب إنشاء محوّل مخصص.

## مصفوفة مقارنة المحوّلات

| نوع المحوّل | حالة الاستخدام | هيكل مجموعة البيانات | متى تستخدمه |
|---|---|---|---|
| **StandardJSONAdapter** | معالجة JSON للأغراض العامة | `[{"question": "...", "answer": "..."}]` | عندما تحتوي مجموعة البيانات على هيكل بسيط بأزواج إدخال/إخراج قابلة للتعيين بالتهيئة |
| **RAGJSONAdapter** | الجيل المعزّز بالاسترداد | `[{"question": "...", "context": "...", "answer": "..."}]` | عندما تتضمن مجموعة البيانات سياقات استرداد أو وثائق إلى جانب الأسئلة والأجوبة |
| **محوّل DatasetAdapter مخصص** | صيغ أو معالجة متخصصة | أي هيكل مخصص | عندما لا تلبّي المحوّلات الموجودة احتياجاتك حتى مع التهيئة |

---

## مخطط قرار اختيار المحوّل

1. **هل مجموعة بياناتك بصيغة JSON؟**
   - **نعم**: انتقل إلى السؤال التالي
   - **لا**: هل هي CSV أو YAML؟ استخدم StandardJSONAdapter مع معامل `file_format` المناسب

2. **هل تحتوي مجموعة بياناتك على حقول question وcontext وanswer؟**
   - **نعم**: استخدم RAGJSONAdapter
   - **لا**: أنشئ محوّلًا مخصصًا

---

## التهيئة مقابل محوّل DatasetAdapter المخصص

في كثير من الحالات، يمكنك استخدام StandardJSONAdapter مع تهيئة مخصصة بدلًا من إنشاء محوّل جديد:

```yaml
dataset:
  adapter_class: "prompt_ops.core.datasets.StandardJSONAdapter"
  path: "path/to/dataset.json"
  adapter_params:
    input_field: ["nested", "field", "path"]
    output_field: "answer"
```

أنشئ محوّل مجموعة بيانات مخصصًا فقط عندما لا تكون هذه الدرجة من التهيئة كافية لاحتياجاتك.

---

## متى تُنشئ محوّل DatasetAdapter مخصصًا

أنشئ محوّل مجموعة بيانات مخصصًا عندما:

1. **هيكل معقد**: تحتوي مجموعة بياناتك على هيكل معقد لا يمكن التعامل معه عبر تهيئة المحوّلات الموجودة
2. **معالجة خاصة**: تحتاج إلى منطق معالجة خاص يتجاوز استخراج الحقول البسيطة وتحويلها
3. **منطق خاص بالنطاق**: يتطلب نطاقك تحققًا أو تطبيعًا أو إثراءً محددًا
4. **مصادر بيانات متعددة**: تحتاج إلى دمج أو ربط بيانات من مصادر متعددة

---

## مثال على تطبيق محوّل DatasetAdapter مخصص

```python
from prompt_ops.core.datasets import DatasetAdapter

class MyCustomAdapter(DatasetAdapter):
    def __init__(self, dataset_path, **kwargs):
        super().__init__(dataset_path)
        # تهيئة أي معاملات مخصصة
        self.special_param = kwargs.get('special_param')

    def adapt(self):
        # تحميل البيانات الخام
        raw_data = self.load_raw_data()

        # تحويلها إلى الصيغة الموحَّدة
        standardized_data = []
        for item in raw_data:
            # منطق التحويل المخصص الخاص بك هنا
            # هذا هو المكان الذي يمكنك فيه تطبيق أي معالجة خاصة

            standardized_example = {
                "inputs": {
                    "question": self._process_question(item),
                    # أضف أي حقول إدخال أخرى
                },
                "outputs": {
                    "answer": self._process_answer(item),
                    # أضف أي حقول إخراج أخرى
                },
                "metadata": self._extract_metadata(item)
            }
            standardized_data.append(standardized_example)

        return standardized_data

    def _process_question(self, item):
        # منطق معالجة السؤال المخصص
        pass

    def _process_answer(self, item):
        # منطق معالجة الإجابة المخصص
        pass

    def _extract_metadata(self, item):
        # استخراج أي بيانات وصفية ذات صلة
        return {}
```

</div>
