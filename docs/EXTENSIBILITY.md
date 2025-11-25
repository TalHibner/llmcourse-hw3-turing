# Extensibility and Plugin Architecture

**Document Version:** 1.0
**Date:** 2025-11-25
**Project:** Multi-Agent Translation System

---

## Table of Contents

1. [Overview](#overview)
2. [Extension Points](#extension-points)
3. [Plugin Development Guide](#plugin-development)
4. [Custom Components](#custom-components)
5. [Configuration Extensions](#configuration-extensions)
6. [Examples](#examples)

---

## 1. Overview

The Multi-Agent Translation System is designed with extensibility in mind, allowing researchers and developers to:

- Add new translation agents for different language pairs
- Implement custom error injection strategies
- Create alternative semantic analysis methods
- Develop new visualization types
- Extend the analysis pipeline

### Design Principles

- **Modular Architecture**: Each component (agents, analyzers, visualizers) is independent
- **Interface-Based**: Well-defined interfaces enable easy substitution
- **Configuration-Driven**: Many extensions possible through configuration alone
- **Plugin-Friendly**: Support for custom plugins without modifying core code

---

## 2. Extension Points

### 2.1 Translation Agents

**Extension Point:** `skills/*.md`

Add new translation agents by creating skill definition files:

```markdown
# [Source] to [Target] Translation Agent

## Role
You are an expert translator...

## Instructions
...
```

**Configuration:** Update `config/config.yaml`:

```yaml
agents:
  agent4:
    skill_file: "skills/custom_translation.md"
    source_lang: "es"
    target_lang: "de"
```

**Integration:** Modify `src/agents/pipeline.py` to include the new agent in the pipeline.

---

### 2.2 Error Injection Strategies

**Extension Point:** `src/input/error_injector.py`

Create custom error injection methods by extending `ErrorInjector`:

```python
from src.input.error_injector import ErrorInjector

class CustomErrorInjector(ErrorInjector):
    """Custom error injection with domain-specific errors."""

    def _corrupt_word(self, word: str) -> str:
        """Override to implement custom corruption logic."""
        # Your custom logic here
        return corrupted_word
```

**Hook:** Configure in `config/config.yaml`:

```yaml
input:
  error_injector_class: "custom_module.CustomErrorInjector"
```

---

### 2.3 Semantic Analysis Methods

**Extension Point:** `src/analysis/embeddings.py`

Implement alternative distance metrics or embedding models:

```python
from src.analysis.embeddings import SemanticAnalyzer

class CustomSemanticAnalyzer(SemanticAnalyzer):
    """Analyzer with custom embedding model."""

    def __init__(self, model_name: str = "custom-model"):
        super().__init__(model_name)

    def calculate_distance(self, text1: str, text2: str) -> float:
        """Override to use custom distance metric."""
        # Your custom metric (e.g., Manhattan, Euclidean)
        return distance
```

---

### 2.4 Visualization Plugins

**Extension Point:** `src/visualization/plots.py`

Add new visualization types:

```python
from src.visualization.plots import Visualizer

class CustomVisualizer(Visualizer):
    """Custom visualizations for research."""

    def create_heatmap(self, data, output_path):
        """Create custom heatmap visualization."""
        # Implementation
        pass

    def create_3d_plot(self, data, output_path):
        """Create 3D visualization of results."""
        # Implementation
        pass
```

---

### 2.5 Pipeline Hooks

The translation pipeline supports pre/post processing hooks:

```python
# In src/agents/pipeline.py
class TranslationPipeline:
    def __init__(self, config):
        self.pre_translation_hooks = []
        self.post_translation_hooks = []

    def register_pre_hook(self, hook_func):
        """Register function to run before translation."""
        self.pre_translation_hooks.append(hook_func)

    def register_post_hook(self, hook_func):
        """Register function to run after translation."""
        self.post_translation_hooks.append(hook_func)
```

**Usage:**

```python
def log_translation(text, metadata):
    """Custom logging hook."""
    logger.info(f"Translating: {text[:50]}...")

pipeline = TranslationPipeline(config)
pipeline.register_pre_hook(log_translation)
```

---

## 3. Plugin Development Guide

### 3.1 Creating a Custom Plugin

**Step 1:** Create plugin directory structure

```
plugins/
└── my_plugin/
    ├── __init__.py
    ├── plugin.py
    └── README.md
```

**Step 2:** Implement plugin interface

```python
# plugins/my_plugin/plugin.py
from abc import ABC, abstractmethod

class TranslationPlugin(ABC):
    """Base class for translation plugins."""

    @abstractmethod
    def initialize(self, config):
        """Initialize plugin with configuration."""
        pass

    @abstractmethod
    def process(self, text, metadata):
        """Process text with plugin logic."""
        pass
```

**Step 3:** Register plugin

```python
# In your main code
from plugins.my_plugin.plugin import MyPlugin

plugin = MyPlugin()
plugin.initialize(config)
pipeline.register_plugin(plugin)
```

---

### 3.2 Plugin Best Practices

1. **Documentation**: Include comprehensive README with plugin
2. **Dependencies**: List all dependencies in `requirements.txt`
3. **Configuration**: Use configuration files for parameters
4. **Error Handling**: Gracefully handle errors without crashing pipeline
5. **Testing**: Include unit tests for plugin functionality
6. **Logging**: Use standard logging for debugging

---

## 4. Custom Components

### 4.1 Custom Test Case Generator

Create specialized test case generators:

```python
from src.input.generator import TestCaseGenerator

class DomainSpecificGenerator(TestCaseGenerator):
    """Generate test cases for specific domain (medical, legal, etc.)."""

    def generate_sentences(self, domain: str, count: int):
        """Generate domain-specific sentences."""
        # Load domain corpus
        # Generate appropriate sentences
        return sentences
```

---

### 4.2 Custom Analysis Metrics

Add new metrics for analysis:

```python
# src/analysis/custom_metrics.py
def calculate_bleu_score(original: str, translated: str) -> float:
    """Calculate BLEU score between texts."""
    # Implementation
    return score

def calculate_perplexity(text: str, model) -> float:
    """Calculate perplexity of translated text."""
    # Implementation
    return perplexity
```

**Integration:**

```python
from src.analysis.custom_metrics import calculate_bleu_score

# In analysis pipeline
results['bleu_score'] = calculate_bleu_score(original, final)
```

---

## 5. Configuration Extensions

### 5.1 Custom Configuration Schema

Extend configuration with custom sections:

```yaml
# config/config.yaml
project:
  name: "Custom Translation Project"

custom:
  plugins:
    - name: "quality_checker"
      enabled: true
      params:
        threshold: 0.8

    - name: "cost_monitor"
      enabled: true
      params:
        budget: 10.0
        alert_threshold: 8.0

  experiments:
    parameter_sweep:
      error_rates: [0.0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3]
      models: ["claude-3", "gpt-4"]
      repeat_count: 3
```

---

### 5.2 Environment-Specific Configuration

Support multiple environments:

```yaml
# config/production.yaml
agents:
  retry_count: 5
  timeout: 300

logging:
  level: WARNING

api:
  rate_limit: 100
```

```yaml
# config/development.yaml
agents:
  retry_count: 2
  timeout: 60

logging:
  level: DEBUG

api:
  rate_limit: 10
```

---

## 6. Examples

### 6.1 Example: Adding Spanish-German Translation

**1. Create skill file:** `skills/es_to_de.md`

```markdown
# Spanish to German Translation Agent

## Role
You are an expert Spanish-to-German translator.

## Instructions
Translate the provided Spanish text to German, preserving meaning and style.
```

**2. Update configuration:** `config/config.yaml`

```yaml
agents:
  agent4:
    skill_file: "skills/es_to_de.md"
    source_lang: "es"
    target_lang: "de"
```

**3. Modify pipeline:** `src/agents/pipeline.py`

```python
def run_four_agent_pipeline(self, text: str):
    # EN -> FR -> HE -> ES -> DE
    fr = self.translate(text, self.agents['agent1'])
    he = self.translate(fr, self.agents['agent2'])
    es = self.translate(he, self.agents['agent3'])
    de = self.translate(es, self.agents['agent4'])
    return de
```

---

### 6.2 Example: Custom Visualizer for 3D Plots

```python
# plugins/viz3d/visualizer.py
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

class ThreeDVisualizer:
    """Create 3D visualizations of error rate, distance, and time."""

    def create_3d_scatter(self, data, output_path):
        """Generate 3D scatter plot."""
        fig = plt.figure(figsize=(12, 8))
        ax = fig.add_subplot(111, projection='3d')

        ax.scatter(
            data['error_rate'],
            data['distance'],
            data['processing_time'],
            c=data['distance'],
            cmap='viridis',
            s=100
        )

        ax.set_xlabel('Error Rate')
        ax.set_ylabel('Semantic Distance')
        ax.set_zlabel('Processing Time (s)')
        ax.set_title('3D Analysis of Translation Pipeline')

        plt.savefig(output_path, dpi=300)
```

---

### 6.3 Example: Cost Monitoring Plugin

```python
# plugins/cost_monitor/monitor.py
class CostMonitor:
    """Monitor and alert on API costs."""

    def __init__(self, budget: float):
        self.budget = budget
        self.current_cost = 0.0

    def track_request(self, tokens: int, model: str):
        """Track cost of API request."""
        cost_per_token = self.get_pricing(model)
        request_cost = tokens * cost_per_token
        self.current_cost += request_cost

        if self.current_cost > self.budget * 0.8:
            self.alert(f"Cost approaching budget: ${self.current_cost:.2f}")

    def alert(self, message: str):
        """Send cost alert."""
        logger.warning(f"COST ALERT: {message}")
```

**Integration:**

```python
cost_monitor = CostMonitor(budget=10.0)
pipeline.register_plugin(cost_monitor)
```

---

## Best Practices for Extensions

1. **Maintain Interface Compatibility**: Don't break existing interfaces
2. **Use Dependency Injection**: Pass dependencies through constructors
3. **Follow Project Structure**: Place extensions in appropriate directories
4. **Document Thoroughly**: Include docstrings and README files
5. **Test Extensively**: Write tests for all custom components
6. **Version Control**: Track extension versions separately
7. **Configuration Over Code**: Use config files for parameters
8. **Graceful Degradation**: Handle errors without breaking pipeline

---

## Getting Help

For questions about extending the system:

1. Review existing implementations in `src/` directory
2. Check inline documentation and docstrings
3. Refer to `DESIGN.md` for architecture details
4. Create an issue on GitHub with `enhancement` label

---

**Generated with Claude Code**

Co-Authored-By: Claude <noreply@anthropic.com>
