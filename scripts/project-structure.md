## Project Structure Overview

The **llama-prompt-ops** project is designed as a **prompt optimization framework** specifically tailored for Llama models. It uses a **strategy pattern** with **DSPy's MIPROv2** optimizer underneath to automatically improve prompts based on training data and metrics.

### Key Architecture Patterns:
1. **Strategy Pattern**: Different optimization strategies (Basic, Llama-specific)
2. **Adapter Pattern**: For datasets, models, and metrics
3. **Chain of Responsibility**: For prompt processing
4. **Composition**: LlamaStrategy composes BasicOptimizationStrategy

## Execution Flow with File Dependencies

Here's exactly which files are touched during a typical `llama-prompt-ops migrate` command:

### Phase 1: Entry and Configuration
```
interfaces/cli.py (line 700+)
├── CLI command parsing (@cli.command migrate)
├── API key validation (check_api_key)
├── Configuration loading (load_config)
└── Logging setup
```

### Phase 2: Model Setup
```
interfaces/cli.py (line 433+: get_models_from_config)
└── core/model.py (setup_model function)
    ├── DSPyModelAdapter initialization
    ├── Model configuration with DSPy
    └── Global model registration
```

### Phase 3: Dataset Processing
```
interfaces/cli.py (line 410+: get_dataset_adapter_from_config)
└── core/datasets.py
    ├── ConfigurableJSONAdapter (most common)
    ├── RAGJSONAdapter (for RAG tasks)
    ├── Data loading (JSON/CSV/YAML)
    ├── Field mapping to standardized format
    └── Train/validation/test split
```

### Phase 4: Metric Creation
```
interfaces/cli.py (line 611+: get_metric)
└── core/metrics.py
    ├── DSPyMetricAdapter (default)
    ├── StandardJSONMetric
    ├── ExactMatchMetric
    └── Custom metric loading
```

### Phase 5: Strategy Selection
```
interfaces/cli.py (line 528+: get_strategy)
├── Auto-detection based on model name
└── Strategy instantiation:
    ├── core/prompt_strategies.py (BasicOptimizationStrategy)
    └── core/model_strategies.py (LlamaStrategy)
```

### Phase 6: Llama-Specific Processing (if LlamaStrategy)
```
core/model_strategies.py (LlamaStrategy.run)
└── core/prompt_processors.py
    ├── create_llama_processing_chain()
    ├── Formatting processors
    ├── Template processors
    └── Tips injection
```

### Phase 7: Main Optimization
```
core/migrator.py (PromptMigrator.optimize)
├── Llama tips injection (utils/llama_utils.py)
├── Strategy execution
└── core/prompt_strategies.py (BasicOptimizationStrategy.run)
    ├── Pre-optimization summary (utils/telemetry.py)
    ├── Baseline computation
    ├── DSPy signature creation
    ├── MIPROv2 optimizer setup
    ├── Custom instruction proposer injection
    └── optimize.compile() call
```

### Phase 8: Evaluation & Results
```
core/migrator.py
├── Optimized program validation
├── Results formatting
└── File saving (JSON + YAML)
```

## Key Design Principles

1. **Modular Architecture**: Each component has a clear responsibility
2. **Configuration-Driven**: YAML configs control behavior without code changes
3. **Extensible**: New adapters, strategies, and metrics can be added easily
4. **Llama-Optimized**: Special handling for Llama model quirks and best practices
5. **DSPy Integration**: Leverages DSPy's powerful optimization framework underneath

## Typical Execution Pattern

1. **CLI**: User runs `llama-prompt-ops migrate --config config.yaml`
2. **Setup**: Load config, validate API keys, configure models
3. **Data**: Load dataset, apply transformations, create train/val/test splits
4. **Strategy**: Auto-select or use configured optimization strategy
5. **Process**: Apply Llama-specific preprocessing (if LlamaStrategy)
6. **Optimize**: Run DSPy MIPROv2 with custom instruction generation
7. **Save**: Export optimized prompt and metadata to files

The system is designed to be **highly configurable** while providing **sensible defaults**, making it easy for users to get started with prompt optimization for Llama models while still allowing advanced customization.
