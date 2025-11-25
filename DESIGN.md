# Technical Design Document
## Multi-Agent Translation System with Error Analysis

**Version:** 1.0
**Date:** 2025-11-25
**Project:** LLM Course HW3 - Turing Assignment

---

## 1. System Architecture Overview

### 1.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Orchestration Layer                       │
│                  (translation_pipeline.py)                   │
└───────────┬──────────────────────────────────┬───────────────┘
            │                                  │
            │ Input Prep                       │ Output Analysis
            ▼                                  ▼
┌───────────────────────┐         ┌───────────────────────────┐
│   Input Generator     │         │   Analysis Engine         │
│  - Test sentences     │         │  - Embedding generation   │
│  - Error injection    │         │  - Distance calculation   │
│  - Validation         │         │  - Visualization          │
└───────────────────────┘         └───────────────────────────┘
            │                                  ▲
            │                                  │
            ▼                                  │
┌────────────────────────────────────────────────────────────┐
│                    Agent Pipeline (Skills)                  │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐             │
│  │ Agent 1  │───▶│ Agent 2  │───▶│ Agent 3  │             │
│  │ EN → FR  │    │ FR → HE  │    │ HE → EN  │             │
│  └──────────┘    └──────────┘    └──────────┘             │
│        ▲               ▲               ▲                    │
│        │               │               │                    │
│        └───────────────┴───────────────┘                    │
│              Claude Code Skills API                         │
└────────────────────────────────────────────────────────────┘
            │
            ▼
┌────────────────────────────────────────────────────────────┐
│                  External Services                          │
│  - Claude API / OpenAI API                                  │
│  - Sentence Transformers (Embeddings)                       │
└────────────────────────────────────────────────────────────┘
```

### 1.2 Component Responsibilities

| Component | Responsibility | Input | Output |
|-----------|---------------|--------|---------|
| Input Generator | Create test sentences with errors | Configuration | Test cases with metadata |
| Agent 1 (EN→FR) | Translate English to French | English text | French text |
| Agent 2 (FR→HE) | Translate French to Hebrew | French text | Hebrew text |
| Agent 3 (HE→EN) | Translate Hebrew to English | Hebrew text | English text |
| Analysis Engine | Calculate semantic drift | Original + Final English | Distance metrics |
| Visualization Module | Generate graphs | Analysis results | PNG/PDF graphs |
| Orchestrator | Coordinate entire pipeline | User command | Complete results |

---

## 2. Detailed Component Design

### 2.1 Agent Architecture (Claude Code Skills)

Each agent is implemented as a Claude Code Skill with the following structure:

```yaml
# Skill Definition Template
name: "translation_agent_X"
description: "Translates text from Language A to Language B"
version: "1.0.0"
parameters:
  - name: input_text
    type: string
    required: true
    description: "Text to translate"
  - name: preserve_formatting
    type: boolean
    required: false
    default: true
instructions: |
  You are a translation specialist. Translate the provided text from
  [Source Language] to [Target Language].

  Rules:
  1. Maintain semantic meaning as much as possible
  2. Handle misspellings gracefully by inferring intent
  3. Preserve sentence structure where appropriate
  4. Return ONLY the translated text, no explanations
```

#### 2.1.1 Agent 1: English → French
- **Input**: English text (potentially with spelling errors)
- **Processing**: Use LLM to interpret misspelled English and translate to French
- **Output**: Clean French translation
- **Error Handling**: If spelling errors are severe, infer from context

#### 2.1.2 Agent 2: French → Hebrew
- **Input**: French text from Agent 1
- **Processing**: Direct French to Hebrew translation
- **Output**: Hebrew translation
- **Special Considerations**: Ensure RTL (Right-to-Left) text handling

#### 2.1.3 Agent 3: Hebrew → English
- **Input**: Hebrew text from Agent 2
- **Processing**: Hebrew back to English
- **Output**: Final English translation
- **Goal**: Measure semantic drift from original

### 2.2 Sequential Communication Pattern

```python
# Pseudocode for agent communication
class TranslationPipeline:
    def __init__(self):
        self.agent1 = SkillAgent("en_to_fr")
        self.agent2 = SkillAgent("fr_to_he")
        self.agent3 = SkillAgent("he_to_en")

    def process(self, english_input: str) -> dict:
        # Agent 1: EN → FR
        french_output = self.agent1.execute(
            input_text=english_input
        )

        # Agent 2: FR → HE
        hebrew_output = self.agent2.execute(
            input_text=french_output
        )

        # Agent 3: HE → EN
        final_english = self.agent3.execute(
            input_text=hebrew_output
        )

        return {
            "original": english_input,
            "french": french_output,
            "hebrew": hebrew_output,
            "final": final_english
        }
```

### 2.3 Input Generation Module

```python
class InputGenerator:
    """Generate test sentences with controlled spelling errors."""

    def __init__(self, base_sentences: List[str]):
        self.base_sentences = base_sentences
        self.error_types = [
            "character_swap",      # "hello" → "hlelo"
            "character_deletion",  # "hello" → "hllo"
            "character_insertion", # "hello" → "helllo"
            "character_replacement" # "hello" → "hallo"
        ]

    def generate_test_cases(self, error_rates: List[float]) -> List[TestCase]:
        """Generate test cases for each error rate."""
        test_cases = []

        for sentence in self.base_sentences:
            for error_rate in error_rates:
                corrupted = self.inject_errors(sentence, error_rate)
                test_cases.append(TestCase(
                    original=sentence,
                    corrupted=corrupted,
                    error_rate=error_rate,
                    word_count=len(sentence.split())
                ))

        return test_cases

    def inject_errors(self, text: str, error_rate: float) -> str:
        """Inject spelling errors into text at specified rate."""
        words = text.split()
        num_errors = int(len(words) * error_rate)

        # Randomly select words to corrupt
        error_indices = random.sample(range(len(words)), num_errors)

        for idx in error_indices:
            words[idx] = self.corrupt_word(words[idx])

        return " ".join(words)

    def corrupt_word(self, word: str) -> str:
        """Apply random error to a single word."""
        if len(word) < 3:
            return word  # Don't corrupt very short words

        error_type = random.choice(self.error_types)
        # Implementation of each error type...
        return corrupted_word
```

### 2.4 Analysis Engine

```python
class SemanticAnalyzer:
    """Calculate semantic distance between text pairs."""

    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        from sentence_transformers import SentenceTransformer
        self.model = SentenceTransformer(model_name)

    def get_embedding(self, text: str) -> np.ndarray:
        """Generate semantic embedding for text."""
        return self.model.encode(text, convert_to_numpy=True)

    def calculate_distance(self, text1: str, text2: str,
                          metric: str = "cosine") -> float:
        """Calculate distance between two texts."""
        emb1 = self.get_embedding(text1)
        emb2 = self.get_embedding(text2)

        if metric == "cosine":
            # Cosine distance = 1 - cosine_similarity
            similarity = np.dot(emb1, emb2) / (
                np.linalg.norm(emb1) * np.linalg.norm(emb2)
            )
            return 1.0 - similarity

        elif metric == "euclidean":
            return np.linalg.norm(emb1 - emb2)

        else:
            raise ValueError(f"Unknown metric: {metric}")

    def batch_analyze(self, test_results: List[dict]) -> pd.DataFrame:
        """Analyze multiple test results."""
        results = []

        for result in test_results:
            distance = self.calculate_distance(
                result["original"],
                result["final"]
            )

            results.append({
                "error_rate": result["error_rate"],
                "distance": distance,
                "original": result["original"],
                "final": result["final"]
            })

        return pd.DataFrame(results)
```

### 2.5 Visualization Module

```python
class Visualizer:
    """Generate graphs and charts for analysis results."""

    def __init__(self, output_dir: str = "results"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

    def plot_error_distance_relationship(self,
                                        df: pd.DataFrame,
                                        output_file: str = "error_distance_graph.png"):
        """Generate main analysis graph."""
        import matplotlib.pyplot as plt
        import seaborn as sns

        # Set style
        sns.set_style("whitegrid")
        plt.figure(figsize=(12, 8))

        # Scatter plot with trend line
        ax = sns.scatterplot(data=df, x="error_rate", y="distance",
                            s=100, alpha=0.6, color="steelblue")

        # Add trend line
        z = np.polyfit(df["error_rate"], df["distance"], 2)
        p = np.poly1d(z)
        x_trend = np.linspace(df["error_rate"].min(),
                             df["error_rate"].max(), 100)
        plt.plot(x_trend, p(x_trend), "r--", linewidth=2,
                label="Trend Line")

        # Labels and formatting
        plt.xlabel("Spelling Error Rate (%)", fontsize=14, fontweight="bold")
        plt.ylabel("Semantic Distance (Cosine)", fontsize=14, fontweight="bold")
        plt.title("Impact of Spelling Errors on Translation Semantic Drift",
                 fontsize=16, fontweight="bold", pad=20)

        # Convert error_rate to percentage for x-axis
        ax.set_xticklabels([f"{int(x*100)}%" for x in ax.get_xticks()])

        plt.legend(fontsize=12)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()

        # Save
        output_path = self.output_dir / output_file
        plt.savefig(output_path, dpi=300, bbox_inches="tight")
        print(f"Graph saved to: {output_path}")

        return output_path
```

---

## 3. Data Flow Diagram

### 3.1 End-to-End Data Flow

```
┌─────────────────┐
│  Configuration  │
│  - Base sente   │
│  - Error rates  │
│  - Parameters   │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────┐
│  1. Input Generation            │
│  For each base sentence:        │
│    For each error rate:         │
│      - Inject spelling errors   │
│      - Validate word count      │
│      - Create TestCase object   │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│  2. Translation Pipeline        │
│  For each TestCase:             │
│    original_en = TestCase.text  │
│    french = Agent1(original_en) │
│    hebrew = Agent2(french)      │
│    final_en = Agent3(hebrew)    │
│    Store all intermediate steps │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│  3. Semantic Analysis           │
│  For each result:               │
│    emb_orig = embed(original)   │
│    emb_final = embed(final_en)  │
│    distance = calc_dist(e1,e2)  │
│    Store with error_rate        │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│  4. Aggregation & Analysis      │
│  - Group by error_rate          │
│  - Calculate statistics         │
│  - Identify trends              │
│  - Generate summary table       │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│  5. Visualization               │
│  - Create scatter plot          │
│  - Add trend line               │
│  - Generate summary stats       │
│  - Save as PNG/PDF              │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│  6. Results Output              │
│  - results/translations.json    │
│  - results/analysis.csv         │
│  - results/graph.png            │
│  - results/summary.txt          │
└─────────────────────────────────┘
```

---

## 4. Project Structure

```
llmcourse-hw3-turing/
├── .github/
│   └── workflows/
│       └── tests.yml              # CI/CD (optional)
├── src/
│   ├── __init__.py
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── skill_agent.py         # Skill wrapper class
│   │   └── pipeline.py            # Translation pipeline orchestrator
│   ├── input/
│   │   ├── __init__.py
│   │   ├── generator.py           # Test case generation
│   │   ├── validator.py           # Input validation
│   │   └── error_injector.py      # Spelling error injection
│   ├── analysis/
│   │   ├── __init__.py
│   │   ├── embeddings.py          # Semantic embeddings
│   │   ├── distance.py            # Distance calculations
│   │   └── statistics.py          # Statistical analysis
│   ├── visualization/
│   │   ├── __init__.py
│   │   └── plots.py               # Graph generation
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── config.py              # Configuration management
│   │   ├── logging.py             # Logging setup
│   │   └── io.py                  # File I/O utilities
│   └── main.py                    # CLI entry point
├── skills/
│   ├── en_to_fr.md                # Agent 1 skill definition
│   ├── fr_to_he.md                # Agent 2 skill definition
│   └── he_to_en.md                # Agent 3 skill definition
├── tests/
│   ├── __init__.py
│   ├── test_input_generation.py
│   ├── test_agents.py
│   ├── test_analysis.py
│   └── test_integration.py
├── data/
│   ├── base_sentences.txt         # Original clean sentences
│   └── test_cases.json            # Generated test cases
├── results/
│   ├── translations/              # All translation outputs
│   ├── analysis/                  # Analysis results
│   └── graphs/                    # Generated visualizations
├── config/
│   ├── config.yaml                # Main configuration
│   └── prompts.yaml               # Agent prompts library
├── docs/
│   ├── PRD.md                     # Product Requirements
│   ├── DESIGN.md                  # This document
│   ├── TASKS.md                   # Implementation tasks
│   └── API.md                     # API documentation
├── .env.example                   # Environment variable template
├── .gitignore
├── pyproject.toml                 # UV/Poetry dependencies
├── README.md                      # Main documentation
├── STATUS.md                      # Project status tracker
└── requirements.txt               # Fallback dependencies
```

---

## 5. Technology Stack

### 5.1 Core Technologies

| Category | Technology | Version | Purpose |
|----------|-----------|---------|----------|
| Language | Python | 3.10+ | Main implementation |
| Package Manager | UV | Latest | Dependency management |
| LLM API | Claude/OpenAI | Latest | Agent translation |
| Embeddings | sentence-transformers | 2.x | Semantic vectors |
| Data Processing | pandas | 2.x | Data manipulation |
| Visualization | matplotlib | 3.x | Graph generation |
| Visualization | seaborn | 0.12+ | Statistical plots |
| Numerical | numpy | 1.24+ | Mathematical operations |
| Testing | pytest | 7.x | Unit testing |
| Type Checking | mypy | 1.x | Static type checking |

### 5.2 Development Tools

- **Code Formatter**: black (line length: 88)
- **Import Sorter**: isort (compatible with black)
- **Linter**: pylint, flake8
- **Documentation**: Sphinx (optional, for API docs)
- **Version Control**: Git + GitHub

---

## 6. API Design

### 6.1 Main CLI Interface

```bash
# Run full experiment
python -m src.main --config config/config.yaml

# Run with specific error rates
python -m src.main --error-rates 0.0,0.1,0.25,0.5 --sentences 20

# Analyze existing results
python -m src.main --mode analyze --input results/translations.json

# Generate graph only
python -m src.main --mode visualize --input results/analysis.csv
```

### 6.2 Internal Python API

```python
# Main orchestration API
from src.agents.pipeline import TranslationPipeline
from src.input.generator import InputGenerator
from src.analysis.embeddings import SemanticAnalyzer

# Setup
pipeline = TranslationPipeline()
generator = InputGenerator(base_sentences)
analyzer = SemanticAnalyzer()

# Generate inputs
test_cases = generator.generate_test_cases([0.0, 0.1, 0.25, 0.5])

# Run translations
results = []
for test_case in test_cases:
    result = pipeline.process(test_case.corrupted)
    result["error_rate"] = test_case.error_rate
    result["original_clean"] = test_case.original
    results.append(result)

# Analyze
analysis_df = analyzer.batch_analyze(results)

# Visualize
from src.visualization.plots import Visualizer
viz = Visualizer()
viz.plot_error_distance_relationship(analysis_df)
```

---

## 7. Configuration Management

### 7.1 Configuration File Structure (YAML)

```yaml
# config/config.yaml
project:
  name: "Multi-Agent Translation System"
  version: "1.0.0"

agents:
  agent1:
    skill_file: "skills/en_to_fr.md"
    source_lang: "en"
    target_lang: "fr"
  agent2:
    skill_file: "skills/fr_to_he.md"
    source_lang: "fr"
    target_lang: "he"
  agent3:
    skill_file: "skills/he_to_en.md"
    source_lang: "he"
    target_lang: "en"

input:
  base_sentences_file: "data/base_sentences.txt"
  min_words: 15
  min_sentences: 2
  error_rates: [0.0, 0.1, 0.25, 0.375, 0.5]
  error_types:
    - "character_swap"
    - "character_deletion"
    - "character_insertion"
    - "character_replacement"

analysis:
  embedding_model: "sentence-transformers/all-MiniLM-L6-v2"
  distance_metric: "cosine"  # or "euclidean"
  cache_embeddings: true

visualization:
  output_format: "png"  # or "pdf", "svg"
  dpi: 300
  figure_size: [12, 8]
  style: "whitegrid"
  color_palette: "steelblue"

output:
  results_dir: "results"
  save_intermediates: true
  save_format: "json"  # or "csv"

api:
  provider: "claude"  # or "openai"
  model: "claude-3-sonnet-20240229"
  max_retries: 3
  timeout: 30

logging:
  level: "INFO"  # DEBUG, INFO, WARNING, ERROR
  file: "logs/translation_pipeline.log"
  console: true
```

### 7.2 Environment Variables (.env)

```bash
# API Keys (NEVER commit these)
ANTHROPIC_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here

# Optional: Model Configuration
DEFAULT_MODEL=claude-3-sonnet-20240229
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Optional: Rate Limiting
MAX_REQUESTS_PER_MINUTE=60
REQUEST_DELAY_SECONDS=1.0
```

---

## 8. Error Handling and Logging

### 8.1 Error Handling Strategy

```python
class TranslationError(Exception):
    """Base exception for translation errors."""
    pass

class AgentCommunicationError(TranslationError):
    """Raised when agents fail to communicate."""
    pass

class ValidationError(TranslationError):
    """Raised when input validation fails."""
    pass

# Usage with retry logic
def translate_with_retry(agent, text, max_retries=3):
    """Execute translation with exponential backoff."""
    for attempt in range(max_retries):
        try:
            return agent.execute(text)
        except APIError as e:
            if attempt == max_retries - 1:
                raise AgentCommunicationError(f"Failed after {max_retries} attempts") from e

            wait_time = 2 ** attempt  # Exponential backoff
            logger.warning(f"Attempt {attempt+1} failed, retrying in {wait_time}s...")
            time.sleep(wait_time)
```

### 8.2 Logging Configuration

```python
import logging
from pathlib import Path

def setup_logging(log_file: str = "logs/pipeline.log", level: str = "INFO"):
    """Configure logging for the application."""

    # Create logs directory
    Path(log_file).parent.mkdir(exist_ok=True)

    # Configure format
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    # File handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(logging.Formatter(log_format, date_format))

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(log_format, date_format))

    # Root logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, level.upper()))
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
```

---

## 9. Security Considerations

### 9.1 API Key Management
- Store all API keys in environment variables
- Use `.env` file with `.gitignore` entry
- Provide `.env.example` with dummy values
- Never log API keys or tokens
- Rotate keys periodically

### 9.2 Data Privacy
- No personal or sensitive data in test sentences
- Clear data retention policy
- Option to delete intermediate results

### 9.3 Input Validation
- Sanitize user inputs
- Limit input length to prevent abuse
- Validate file paths to prevent directory traversal

---

## 10. Performance Considerations

### 10.1 Optimization Strategies
1. **Caching**: Cache embeddings for identical texts
2. **Batch Processing**: Process multiple test cases in parallel where possible
3. **API Rate Limiting**: Implement token bucket algorithm
4. **Lazy Loading**: Load models only when needed

### 10.2 Expected Performance Metrics
- **Translation Speed**: ~5-10 seconds per sentence (3 agents)
- **Embedding Generation**: ~0.5 seconds per text
- **Total Experiment Time**: ~10-15 minutes for 20 test cases

---

## 11. Testing Strategy

### 11.1 Unit Tests
- Test error injection produces correct error rates
- Test distance calculations are mathematically correct
- Test each agent in isolation (mock LLM responses)

### 11.2 Integration Tests
- Test full pipeline end-to-end
- Test error handling and retry logic
- Test configuration loading

### 11.3 Validation Tests
- Verify all test sentences meet word count requirements
- Verify error rates are within expected ranges
- Verify output files are generated correctly

---

## 12. Deployment and Execution

### 12.1 Installation Steps
```bash
# Clone repository
git clone https://github.com/TalHibner/llmcourse-hw3-turing.git
cd llmcourse-hw3-turing

# Install UV (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e .

# Copy environment template
cp .env.example .env
# Edit .env and add your API keys

# Run the experiment
python -m src.main
```

### 12.2 Execution Flow
1. Load configuration from `config/config.yaml`
2. Load base sentences from `data/base_sentences.txt`
3. Generate test cases with errors
4. Execute translation pipeline for each test case
5. Calculate semantic distances
6. Generate visualizations
7. Save all results to `results/` directory

---

## 13. Maintenance and Extensibility

### 13.1 Adding New Agents
To add a new language pair:
1. Create new skill file in `skills/` directory
2. Add agent configuration to `config/config.yaml`
3. Update pipeline to include new agent

### 13.2 Changing Distance Metrics
To use alternative distance metrics:
1. Implement new metric in `src/analysis/distance.py`
2. Update configuration to specify new metric
3. Re-run analysis

### 13.3 Supporting New Visualizations
To add new charts:
1. Add method to `src/visualization/plots.py`
2. Call from main orchestration
3. Save to results directory

---

## 14. Dependencies and Versions

See `pyproject.toml` for complete dependency list. Key dependencies:

```toml
[project]
name = "llmcourse-hw3-turing"
version = "1.0.0"
requires-python = ">=3.10"

dependencies = [
    "anthropic>=0.18.0",
    "openai>=1.0.0",
    "sentence-transformers>=2.3.0",
    "numpy>=1.24.0",
    "pandas>=2.0.0",
    "matplotlib>=3.7.0",
    "seaborn>=0.12.0",
    "pyyaml>=6.0",
    "python-dotenv>=1.0.0",
    "tqdm>=4.65.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
    "black>=23.7.0",
    "isort>=5.12.0",
    "mypy>=1.4.0",
    "pylint>=2.17.0",
]
```

---

## 15. Known Limitations and Constraints

1. **API Rate Limits**: Subject to Claude/OpenAI rate limits
2. **Cost**: Multiple LLM calls per test case can be expensive
3. **Hebrew Support**: Quality depends on LLM's Hebrew capabilities
4. **Embedding Model**: Limited to languages supported by chosen embedding model
5. **Determinism**: LLM outputs may vary between runs

---

## 16. Future Enhancements

### Phase 2 Possibilities (Post-Assignment)
1. **Parallel Translation Paths**: Compare direct EN→EN vs. sequential chain
2. **Multiple Embedding Models**: Compare different semantic representations
3. **Error Type Analysis**: Categorize which error types cause most drift
4. **Confidence Scores**: Add LLM confidence tracking
5. **Interactive Dashboard**: Web UI for real-time experimentation

---

## 17. References and Standards

- **Architecture**: C4 Model for software architecture
- **Code Style**: PEP 8 (Python Enhancement Proposal)
- **Documentation**: PEP 257 (Docstring Conventions)
- **API Design**: RESTful principles adapted for Skills
- **Testing**: pytest conventions
- **Version Control**: Git Flow methodology

---

## Document History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-11-25 | Student | Initial design document |

---

**Review and Approval:**
- Technical Review: Pending
- Security Review: Pending
- Final Approval: Pending
