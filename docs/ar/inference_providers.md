---
title: مزودو الاستدلال
category: المتقدم
description: تهيئة OpenRouter وvLLM وNVIDIA NIMs وTogether AI ومزودين آخرين
order: 30
icon: zap
---

# استخدام مزودي الاستدلال المختلفين مع prompt-ops

<div dir="rtl">

يوضح هذا الدليل كيفية تهيئة prompt-ops للعمل مع مزودي استدلال متعددين، بما في ذلك OpenRouter وvLLM وNVIDIA NIMs. بتغيير تهيئة النموذج في ملفات YAML، يمكنك التبديل بسهولة بين الخلفيات المختلفة دون تعديل الكود.

---

## فهم تهيئة النموذج

في prompt-ops، تُحدَّد تهيئة النموذج في قسم `model` من ملف تهيئة YAML. التهيئة الأساسية تبدو كالتالي:

```yaml
model:
  name: "openrouter/meta-llama/llama-3.1-8b-instruct"
  temperature: 0.0
  max_tokens: 40960
```

**يستخدم prompt-ops [LiteLLM](https://docs.litellm.ai/docs/) كعميل API موحَّد** للتعامل مع جميع استدعاءات LLM API. يوفر LiteLLM اكتشافًا تلقائيًا للمزوّد استنادًا إلى بادئة اسم النموذج (مثل `openrouter/` و`groq/` و`together_ai/`) ويبحث عن متغير البيئة المقابل (مثل `OPENROUTER_API_KEY` و`GROQ_API_KEY` و`TOGETHERAI_API_KEY`).

---

## مزودو الاستدلال المتاحون

### 1. OpenRouter

يوفر [OpenRouter](https://openrouter.ai/) وصولًا إلى مجموعة واسعة من النماذج من مزودين مختلفين عبر API موحَّد.

```yaml
model:
  name: "openrouter/meta-llama/llama-3.1-8b-instruct"
  temperature: 0.0
  max_tokens: 40960
```

عيّن مفتاح API كمتغير بيئة (سيكتشفه LiteLLM تلقائيًا):

```bash
export OPENROUTER_API_KEY=your_openrouter_api_key_here
```

---

### 2. vLLM

[vLLM](https://github.com/vllm-project/vllm) هو مكتبة مفتوحة المصدر للاستدلال السريع لنماذج اللغة الكبيرة. مفيد بشكل خاص لتشغيل النماذج محليًا أو على بنيتك التحتية الخاصة.

```yaml
model:
  name: "hosted_vllm/meta-llama/Llama-3.1-8B-Instruct"
  api_base: "http://localhost:8000/v1"
  temperature: 0.0
  max_tokens: 4096
```

لتشغيل vLLM محليًا، ابدأ أولًا بتشغيل خادم vLLM:

```bash
pip install vllm
vllm serve meta-llama/Llama-3.1-8B-Instruct --tensor-parallel-size=1
```

---

### 3. NVIDIA NIMs

توفر [NVIDIA NIMs](https://docs.nvidia.com/nim/large-language-models/latest/introduction.html) (خدمات الاستدلال المصغَّرة من NVIDIA) حاويات محسَّنة لتشغيل نماذج اللغة الكبيرة على معالجات NVIDIA GPU.

```yaml
model:
  name: "openai/meta/llama-3.1-8b-instruct"  # الصيغة: openai/{model_name}
  api_base: "http://localhost:8000/v1"
  api_key: "any_string_for_localhost"  # يمكن أن يكون أي نص للنشر المحلي
  temperature: 0.0
  max_tokens: 4096
```

لتشغيل حاوية NIM محليًا:

```bash
docker run -it --rm --name=nim \
  --runtime=nvidia \
  --gpus 1 \
  --shm-size=16GB \
  -e NGC_API_KEY=<YOUR NGC API KEY> \
  -v "~/.cache/nim:/opt/nim/.cache" \
  -u $(id -u) \
  -p 8000:8000 \
  nvcr.io/nim/meta/llama-3.1-8b-instruct:1.5.0
```

---

### 4. Together AI

تُوفّر [Together AI](https://www.together.ai/) منصة لتشغيل نماذج مفتوحة المصدر متعددة بأداء محسَّن وأسعار تنافسية.

```yaml
model:
  name: "together_ai/meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8"
  temperature: 0.0
  max_tokens: 4096
```

للاستخدام مع Together AI:

1. سجّل حسابًا على [Together AI](https://www.together.ai/)
2. أنشئ مفتاح API من لوحة تحكم حسابك
3. عيّن مفتاح API كمتغير بيئة (سيكتشفه LiteLLM تلقائيًا):

```bash
export TOGETHERAI_API_KEY=your_api_key_here
```

ثم شغّل التحسين:

```bash
prompt-ops migrate
```

---

### 5. Groq

```yaml
model:
  task_model: groq/meta-llama/llama-4-maverick-17b-128e-instruct
  proposer_model: groq/meta-llama/llama-4-maverick-17b-128e-instruct
  api_base: https://api.groq.com/openai/v1
```

```bash
export GROQ_API_KEY=your_api_key_here
```

ثم شغّل التحسين:

```bash
prompt-ops migrate
```

---

## التهيئة المتقدمة

### استخدام نماذج مختلفة للمهمة والمقترح

يتيح لك prompt-ops تحديد نماذج مختلفة لتنفيذ المهمة وعملية اقتراح البرومبت:

```yaml
model:
  task_model: "openrouter/meta-llama/llama-3.1-8b-instruct"
  proposer_model: "openrouter/meta-llama/llama-3.3-70b-instruct"
  api_base: "https://openrouter.ai/api/v1"
  temperature: 0.0
  max_tokens: 4096
```

---

## تشغيل prompt-ops مع مزودين مختلفين

لتشغيل prompt-ops بتهيئتك:

```bash
# عيّن مفتاح API الخاص بمزوّدك
export OPENROUTER_API_KEY=your_key  # لنماذج OpenRouter (openrouter/...)
export GROQ_API_KEY=your_key        # لنماذج Groq (groq/...)
export TOGETHERAI_API_KEY=your_key  # لنماذج Together AI (together_ai/...)

# شغّل مع أي تهيئة
prompt-ops migrate --config configs/your_config.yaml
```

**كيف يعمل LiteLLM:** يكتشف LiteLLM المزوّد تلقائيًا من بادئة اسم النموذج (مثل `openrouter/model` و`groq/model` و`together_ai/model`) ويبحث عن متغير البيئة المقابل (`OPENROUTER_API_KEY` و`GROQ_API_KEY` و`TOGETHERAI_API_KEY`). لا حاجة لتوجيه API يدوي!

لمزيد من المعلومات حول المزودين المدعومين ومتغيرات البيئة وخيارات التهيئة، راجع [توثيق LiteLLM](https://docs.litellm.ai/docs/set_keys).

</div>
