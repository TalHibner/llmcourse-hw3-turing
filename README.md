# Multi-Agent Translation System with Error Analysis

A research project investigating the impact of spelling errors on semantic drift in sequential multi-agent translation pipelines.

**Course:** LLM Programming (HW3 - Turing Assignment)
**Institution:** M.Sc. Computer Science Program
**Date:** November 2025

---

## Table of Contents

- [Overview](#overview)
- [Research Question](#research-question)
- [System Architecture](#system-architecture)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Methodology](#methodology)
- [Results](#results)
- [Development](#development)
- [Documentation](#documentation)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgments](#acknowledgments)

---

## Overview

This project implements a three-agent translation pipeline that sequentially translates text through multiple languages:

```
English → French → Hebrew → English
```

The system analyzes how input quality (specifically, spelling error rate) affects semantic drift by comparing the original English text with the final English output using vector embeddings and distance metrics.

### Key Features

- **Multi-Agent Pipeline**: Three sequential translation agents using Claude Code Skills
- **Error Injection**: Systematic introduction of spelling errors at controlled rates (0-50%)
- **Semantic Analysis**: Vector embeddings and distance calculations to measure semantic drift
- **Visualization**: Publication-quality graphs showing error-distance relationships
- **Comprehensive Documentation**: Full PRD, technical design, and implementation guides

---

## Research Question

**How does the rate of spelling errors in input text affect semantic drift in multi-agent sequential translation systems?**

### Hypothesis

We hypothesize that:
1. Semantic distance increases as spelling error rate increases
2. The relationship may be non-linear due to LLMs' error correction capabilities
3. Certain error thresholds may cause dramatic increases in semantic drift

---

## System Architecture

### High-Level Overview

```
┌─────────────────┐
│  Input Text     │
│  (English with  │
│  spelling errors)│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Agent 1       │
│  EN → FR        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Agent 2       │
│  FR → HE        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Agent 3       │
│  HE → EN        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Final English  │
│  Translation    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Semantic        │
│ Distance        │
│ Calculation     │
└─────────────────┘
```

### Component Stack

- **Agent Framework**: Claude Code Skills
- **LLM Provider**: Anthropic Claude (configurable to OpenAI)
- **Embeddings**: sentence-transformers
- **Analysis**: NumPy, pandas
- **Visualization**: matplotlib, seaborn
- **Package Management**: UV

---

## Installation

### Prerequisites

- Python 3.10 or higher
- UV package manager
- Git
- Anthropic API key or OpenAI API key

### Step-by-Step Installation

#### 1. Clone the Repository

```bash
git clone https://github.com/TalHibner/llmcourse-hw3-turing.git
cd llmcourse-hw3-turing
```

#### 2. Install UV (if not already installed)

**On macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**On Windows:**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

#### 3. Create Virtual Environment and Install Dependencies

```bash
# Create virtual environment
uv venv

# Activate virtual environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate

# Install dependencies
uv pip install -e .
```

#### 4. Configure API Keys

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your API key
# nano .env  # or use your preferred editor
```

Add to `.env`:
```bash
ANTHROPIC_API_KEY=your_anthropic_key_here
# OR
OPENAI_API_KEY=your_openai_key_here
```

#### 5. Verify Installation

```bash
python -c "import sentence_transformers; print('Installation successful!')"
```

---

## Configuration

### Main Configuration File

Edit `config/config.yaml` to customize behavior:

```yaml
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
  error_rates: [0.0, 0.1, 0.25, 0.375, 0.5]

analysis:
  embedding_model: "sentence-transformers/all-MiniLM-L6-v2"
  distance_metric: "cosine"

visualization:
  output_format: "png"
  dpi: 300
```

### Environment Variables

Required variables in `.env`:

| Variable | Description | Required |
|----------|-------------|----------|
| `ANTHROPIC_API_KEY` | Claude API key | Yes (or OpenAI) |
| `OPENAI_API_KEY` | OpenAI API key | Yes (or Anthropic) |
| `EMBEDDING_MODEL` | Override embedding model | No |
| `LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING) | No |

---

## Usage

### Basic Usage

Run the complete pipeline:

```bash
python -m src.main
```

This will:
1. Load base sentences from `data/base_sentences.txt`
2. Generate test cases with various error rates
3. Execute translation pipeline for each test case
4. Calculate semantic distances
5. Generate visualization
6. Save all results to `results/` directory

### Advanced Usage

#### Custom Configuration

```bash
python -m src.main --config path/to/custom_config.yaml
```

#### Analyze Existing Results

```bash
python -m src.main --mode analyze --input results/translations.json
```

#### Generate Visualization Only

```bash
python -m src.main --mode visualize --input results/analysis.csv
```

#### Verbose Output

```bash
python -m src.main --verbose
```

#### Specific Error Rates

```bash
python -m src.main --error-rates 0.0,0.15,0.3,0.45
```

#### Limited Test Cases (for testing)

```bash
python -m src.main --limit 5
```

### Example Workflow

```bash
# 1. Run experiment with verbose logging
python -m src.main --verbose

# 2. Review results
ls -la results/

# 3. View the generated graph
open results/graphs/error_distance_graph.png  # macOS
xdg-open results/graphs/error_distance_graph.png  # Linux

# 4. Check analysis data
cat results/analysis.csv
```

---

## Project Structure

```
llmcourse-hw3-turing/
├── README.md                      # This file
├── PRD.md                         # Product Requirements Document
├── DESIGN.md                      # Technical Design Document
├── TASKS.md                       # Implementation Task Breakdown
├── STATUS.md                      # Project Status Tracker
├── pyproject.toml                 # UV dependencies and metadata
├── .env.example                   # Environment variable template
├── .gitignore                     # Git ignore rules
│
├── src/                           # Source code
│   ├── __init__.py
│   ├── main.py                    # CLI entry point
│   ├── agents/                    # Agent implementation
│   │   ├── skill_agent.py         # Skill wrapper
│   │   └── pipeline.py            # Translation pipeline
│   ├── input/                     # Input generation
│   │   ├── generator.py           # Test case generation
│   │   ├── error_injector.py      # Spelling error injection
│   │   └── validator.py           # Input validation
│   ├── analysis/                  # Analysis modules
│   │   ├── embeddings.py          # Semantic embeddings
│   │   ├── distance.py            # Distance calculations
│   │   └── statistics.py          # Statistical analysis
│   ├── visualization/             # Visualization
│   │   └── plots.py               # Graph generation
│   └── utils/                     # Utilities
│       ├── config.py              # Configuration loader
│       ├── logging.py             # Logging setup
│       └── io.py                  # File I/O
│
├── skills/                        # Claude Code Skill definitions
│   ├── en_to_fr.md                # English → French
│   ├── fr_to_he.md                # French → Hebrew
│   └── he_to_en.md                # Hebrew → English
│
├── config/                        # Configuration files
│   ├── config.yaml                # Main configuration
│   └── prompts.yaml               # Prompt library
│
├── data/                          # Input data
│   ├── base_sentences.txt         # Original sentences
│   └── test_cases.json            # Generated test cases
│
├── results/                       # Output directory
│   ├── translations/              # Translation outputs
│   ├── analysis/                  # Analysis results
│   │   ├── analysis.csv           # Distance data
│   │   └── summary.txt            # Summary statistics
│   └── graphs/                    # Visualizations
│       └── error_distance_graph.png
│
├── tests/                         # Unit tests
│   ├── test_error_injector.py
│   ├── test_embeddings.py
│   ├── test_distance.py
│   └── test_pipeline.py
│
├── docs/                          # Additional documentation
│   ├── test_sentences.md          # Test sentence documentation
│   └── prompt_engineering.md      # Prompt iteration log
│
└── logs/                          # Log files
    └── pipeline.log
```

---

## Methodology

### Input Generation

1. **Base Sentences**: 10-15 grammatically correct English sentences, each with ≥15 words
2. **Error Injection**: Systematic introduction of spelling errors using four methods:
   - Character swap: "hello" → "hlelo"
   - Character deletion: "hello" → "hllo"
   - Character insertion: "hello" → "helllo"
   - Character replacement: "hello" → "hallo"
3. **Error Rates**: Test at 0%, 10%, 25%, 37.5%, and 50% error rates
4. **Validation**: Ensure all inputs meet minimum word count requirements

### Translation Pipeline

Each test case flows through three sequential agents:

1. **Agent 1 (EN→FR)**: Translates potentially misspelled English to French
   - Must infer meaning from errors
   - Produces clean French output

2. **Agent 2 (FR→HE)**: Translates French to Hebrew
   - Works with clean French input
   - Handles right-to-left text

3. **Agent 3 (HE→EN)**: Translates Hebrew back to English
   - Final output for comparison
   - Goal: measure semantic drift

### Semantic Analysis

1. **Embedding Generation**: Use sentence-transformers to create vector representations
   - Model: `all-MiniLM-L6-v2` (384 dimensions)
   - Applied to both original and final English text

2. **Distance Calculation**: Compute semantic distance using:
   - **Cosine Distance**: Primary metric (0 = identical, 2 = opposite)
   - Formula: `distance = 1 - (A·B) / (||A|| ||B||)`

3. **Statistical Analysis**: Calculate correlation, trends, and outliers

### Visualization

Generate scatter plot with:
- X-axis: Spelling error rate (0-50%)
- Y-axis: Semantic distance
- Trend line: Polynomial fit to show relationship
- High resolution: 300 DPI for publication quality

---

## Results

### Expected Output

After running the experiment, you'll find:

#### 1. Translation Results (`results/translations/`)
- JSON file with all intermediate translations
- Metadata for each translation (duration, success status)

#### 2. Analysis Data (`results/analysis/`)
- `analysis.csv`: Error rates and corresponding distances
- `summary.txt`: Statistical summary

Example `analysis.csv`:
```csv
error_rate,distance,original,final,word_count
0.00,0.023,"The quick brown fox...",The rapid brown fox...",15
0.10,0.145,"The quik brwon fox...","The rapid tan fox...",15
0.25,0.287,"Teh qick bown fox...","A fast brown animal...",15
...
```

#### 3. Visualizations (`results/graphs/`)
- `error_distance_graph.png`: Main analysis graph
- Additional plots (if generated)

#### 4. Logs (`logs/`)
- Detailed execution log with timestamps

### Interpreting Results

- **Low Distance (0.0-0.2)**: Minimal semantic drift, meaning preserved
- **Medium Distance (0.2-0.5)**: Moderate drift, general meaning retained
- **High Distance (0.5+)**: Significant drift, meaning potentially lost

### Sample Findings

*Note: Actual results will vary based on test data and LLM responses*

Expected observations:
1. Non-linear relationship between error rate and distance
2. LLMs show resilience to low error rates (<15%)
3. Sharp increase in drift beyond ~25-30% errors
4. Individual sentence characteristics affect results

---

## Development

### Setting Up Development Environment

```bash
# Install with development dependencies
uv pip install -e ".[dev]"

# Install pre-commit hooks (optional)
pre-commit install
```

### Running Tests

The project includes comprehensive unit and integration tests covering all major components.

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=src --cov-report=html --cov-report=term

# View coverage report in browser
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux

# Run specific test file
pytest tests/test_error_injector.py
pytest tests/test_generator.py
pytest tests/test_embeddings.py
pytest tests/test_config.py
pytest tests/test_pipeline.py

# Run with verbose output
pytest -v

# Run only unit tests (fast)
pytest -m unit

# Run only integration tests
pytest -m integration

# Skip slow tests
pytest -m "not slow"

# Skip API tests (useful when offline)
pytest -m "not api"

# Run tests in parallel (requires pytest-xdist)
pytest -n auto

# Run specific test by name
pytest tests/test_error_injector.py::TestErrorInjector::test_inject_errors_25_percent
```

#### Test Coverage

Current test coverage by module:

| Module | Coverage | Tests |
|--------|----------|-------|
| `src.input.error_injector` | ~95% | 16 tests |
| `src.input.generator` | ~95% | 20 tests |
| `src.analysis.embeddings` | ~90% | 24 tests |
| `src.utils.config` | ~95% | 19 tests |
| `src.agents.pipeline` | ~85% | 12 integration tests |

#### Writing New Tests

When adding new features, follow these testing guidelines:

1. **Unit Tests**: Test individual functions in isolation
2. **Integration Tests**: Test component interactions
3. **Mock External APIs**: Use `pytest-mock` for API calls
4. **Use Fixtures**: Leverage `conftest.py` fixtures for common test data
5. **Test Edge Cases**: Include error conditions and boundary values

Example test structure:
```python
import pytest
from src.your_module import YourClass

class TestYourClass:
    @pytest.fixture
    def instance(self):
        return YourClass()

    def test_basic_functionality(self, instance):
        result = instance.method()
        assert result == expected_value
```

### Code Quality

```bash
# Format code
black src/ tests/

# Sort imports
isort src/ tests/

# Type checking
mypy src/

# Linting
pylint src/
```

### Adding New Features

1. Create feature branch: `git checkout -b feature/your-feature`
2. Implement changes following existing patterns
3. Add tests for new functionality
4. Update documentation
5. Run quality checks
6. Commit with descriptive messages
7. Push and create pull request

---

## Documentation

### Available Documents

| Document | Description |
|----------|-------------|
| **README.md** | Main user guide (this file) |
| **PRD.md** | Product Requirements Document - what and why |
| **DESIGN.md** | Technical Design Document - how |
| **TASKS.md** | Implementation task breakdown - roadmap |
| **STATUS.md** | Current project status - progress tracking |
| **docs/test_sentences.md** | Test sentence documentation |
| **docs/prompt_engineering.md** | Prompt iteration history |

### API Documentation

For detailed API documentation:

```bash
# Generate Sphinx docs (if configured)
cd docs/
make html
open _build/html/index.html
```

Or refer to inline docstrings in the code:

```python
from src.analysis.embeddings import SemanticAnalyzer
help(SemanticAnalyzer)
```

---

## Troubleshooting

### Common Issues

#### Issue: ImportError for sentence-transformers

**Solution:**
```bash
uv pip install sentence-transformers --upgrade
```

#### Issue: API Rate Limit Errors

**Solution:**
- Reduce batch size in config
- Add delays between requests
- Check API quota/billing

```yaml
# config/config.yaml
api:
  max_requests_per_minute: 20
  request_delay_seconds: 2.0
```

#### Issue: Hebrew Text Not Displaying

**Solution:**
- Ensure terminal supports UTF-8 encoding
- Use appropriate font with Hebrew characters
- Check output files instead of terminal display

#### Issue: Out of Memory During Embedding

**Solution:**
- Use smaller embedding model
- Process in smaller batches
- Reduce number of test cases

```yaml
analysis:
  embedding_model: "sentence-transformers/all-MiniLM-L6-v2"  # Smaller model
  batch_size: 10
```

#### Issue: Missing .env File

**Solution:**
```bash
cp .env.example .env
# Edit .env and add your API key
```

### Debug Mode

Enable detailed logging:

```bash
# Set environment variable
export LOG_LEVEL=DEBUG

# Or in .env file
LOG_LEVEL=DEBUG

# Run with verbose flag
python -m src.main --verbose
```

### Getting Help

1. Check logs in `logs/pipeline.log`
2. Review error messages carefully
3. Verify configuration in `config/config.yaml`
4. Ensure API keys are set correctly
5. Check STATUS.md for known issues

---

## Contributing

### How to Contribute

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Update documentation
7. Submit a pull request

### Code Standards

- Follow PEP 8 style guide
- Write docstrings for all public functions
- Add type hints
- Maintain test coverage above 70%
- Update documentation for user-facing changes

### Commit Message Format

```
<type>: <subject>

<body>

Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `test`: Adding tests
- `refactor`: Code refactoring
- `chore`: Maintenance tasks

---

## License

This project is developed as part of an academic assignment for M.Sc. Computer Science program.

**Academic Use**: Free to use for educational purposes with attribution.

**Commercial Use**: Please contact the author for permissions.

### Attribution

If you use this code or methodology in your work, please cite:

```
Multi-Agent Translation System with Error Analysis
LLM Programming Course, M.Sc. Computer Science
November 2025
https://github.com/TalHibner/llmcourse-hw3-turing
```

---

## Acknowledgments

### Technologies Used

- **Claude Code Skills** - Agent framework
- **Anthropic Claude** - Translation LLM
- **sentence-transformers** - Semantic embeddings (Reimers & Gurevych, 2019)
- **UV** - Modern Python package manager
- **matplotlib/seaborn** - Data visualization

### References

1. ISO/IEC 25010:2011 - Software Quality Model
2. Dr. Segal Yoram (2025) - Software Submission Guidelines for M.Sc.
3. Reimers & Gurevych (2019) - Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks
4. Nielsen's 10 Usability Heuristics

### Course Information

**Course**: LLM Programming
**Assignment**: HW3 - Turing Assignment
**Institution**: M.Sc. Computer Science Program
**Instructor**: [Course Instructor Name]
**Semester**: Fall 2025

---

## Project Status

For real-time project status, see [STATUS.md](STATUS.md).

Current Version: **1.0.0**

Last Updated: **2025-11-25**

---

## Contact

**Repository**: https://github.com/TalHibner/llmcourse-hw3-turing
**Issues**: https://github.com/TalHibner/llmcourse-hw3-turing/issues

For questions or issues:
1. Check documentation first
2. Review existing issues
3. Create new issue with detailed description

---

## Quick Start Checklist

- [ ] Python 3.10+ installed
- [ ] UV package manager installed
- [ ] Repository cloned
- [ ] Virtual environment created
- [ ] Dependencies installed
- [ ] API key configured in .env
- [ ] Base sentences prepared in data/
- [ ] Configuration reviewed
- [ ] Test run completed: `python -m src.main --limit 2`
- [ ] Results verified in results/ directory

**Ready to run full experiment!** 🚀

```bash
python -m src.main
```

---

Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
