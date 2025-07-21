# Zendesk AutoQA Configuration

This README explains how to use the custom AutoQA components for evaluating customer service responses in the zendesk-prompt-ops project.

## Overview

The AutoQA system evaluates customer service responses across multiple dimensions:
- Greeting
- Closing
- Comprehension
- Empathy
- Grammar
- Readability
- Solution
- Tone

## Components

### 1. AutoQADatasetAdapter

The `AutoQADatasetAdapter` transforms the Zendesk customer service data into a standardized format for evaluation. It handles:
- Safe loading of dataset files
- Standardizing field names
- Error handling for missing fields
- Special handling for "null" string values

### 2. AutoQAMetric

The `AutoQAMetric` evaluates customer service responses by comparing model predictions against ground truth data. Key features:
- Robust JSON extraction from various formats
- Mapping between gold data and prediction data keys
- Comprehensive scoring across all evaluation dimensions
- Detailed trace output for debugging

## Configuration

A custom configuration file `config_autoqa.yaml` has been created to use these components:

```yaml
system_prompt:
  file: prompts/translate_optional_v4_system.md
  inputs:
  - question
  outputs:
  - answer
dataset:
  adapter:
    class: data.AutoQADatasetAdapter.AutoQADatasetAdapter
    path: data/dataset.json
  input_field: inputs.question
  golden_output_field: outputs.answer
model:
  task_model: openrouter/meta-llama/llama-3.3-70b-instruct
  proposer_model: openrouter/meta-llama/llama-3.3-70b-instruct
metric:
  class: data.AutoQAMetric.AutoQAMetric
  strict_json: false
  output_field: answer
  weights:
    Greeting: 0.1
    Closing: 0.1
    Comprehension: 0.2
    Empathy: 0.1
    Grammar: 0.1
    Readability: 0.1
    Solution: 0.2
    Tone: 0.1
optimization:
  strategy: llama
```

## Usage

To run the AutoQA evaluation:

```bash
python -m llama_prompt_ops.cli.run --config zendesk-prompt-ops/config_autoqa.yaml
```

To optimize the prompt:

```bash
python -m llama_prompt_ops.cli.optimize --config zendesk-prompt-ops/config_autoqa.yaml
```

## Customization

### Adjusting Weights

You can adjust the importance of each evaluation dimension by modifying the weights in the `config_autoqa.yaml` file:

```yaml
metric:
  weights:
    Greeting: 0.1
    Closing: 0.1
    Comprehension: 0.2
    Empathy: 0.1
    Grammar: 0.1
    Readability: 0.1
    Solution: 0.2
    Tone: 0.1
```

Ensure that the weights sum to 1.0.

### Using Different Datasets

To use a different dataset, update the path in the configuration:

```yaml
dataset:
  adapter:
    class: data.AutoQADatasetAdapter.AutoQADatasetAdapter
    path: data/your_custom_dataset.json
```

## Troubleshooting

If you encounter issues with JSON parsing, check that your model outputs are properly formatted according to the expected schema. The `AutoQAMetric` includes robust JSON extraction, but the output should still follow the format specified in the prompt.
