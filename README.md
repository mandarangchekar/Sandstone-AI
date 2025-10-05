# AI-Powered NDA Document Redlining System

An intelligent document analysis system that uses LLMs and semantic search to identify legal issues in NDA documents based on a structured playbook.

## Project Overview

This system analyzes Non-Disclosure Agreements (NDAs) against legal best practices defined in a playbook and identifies problematic clauses that need revision.

### Key Features

- ✅ **AI-Driven Analysis**: Uses GPT-4o-mini for intelligent clause analysis
- ✅ **Semantic Matching**: Leverages sentence transformers for accurate clause identification
- ✅ **Structured Output**: Uses Instructor for guaranteed valid JSON output
- ✅ **Production-Ready**: Clean, modular, type-safe code with Pydantic models
- ✅ **Performance Evaluation**: Built-in evaluation against expected output

## Architecture

```
sandstone/
├── models/          # Pydantic data models
├── services/        # Core processing services
│   ├── document_parser.py      # RTF parsing
│   ├── playbook_loader.py      # Playbook indexing with FAISS
│   ├── semantic_matcher.py     # Semantic clause matching
│   ├── issue_analyzer.py       # LLM-based issue detection
│   └── evaluator.py            # Performance evaluation
├── prompts/         # LLM prompt templates
└── config.py        # Configuration

main.py              # Main orchestration script
```

## Installation

### Prerequisites

- Python 3.13+
- OpenAI API key

### Setup

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync

# Create .env file
echo "OPENAI_API_KEY=your_key_here" > .env
```

## Usage

### Basic Usage

```bash
# Run with default files
uv run python main.py

# With evaluation
uv run python main.py --evaluate

# With verbose output
uv run python main.py --evaluate --verbose
```

### Custom Files

```bash
uv run python main.py \
  --document path/to/document.rtf \
  --playbook path/to/playbook.json \
  --output path/to/output.json
```

### Command Line Options

- `--document PATH`: Path to RTF document (default: `docs/bad_document.txt.rtf`)
- `--playbook PATH`: Path to playbook JSON (default: `docs/playbook.json`)
- `--output PATH`: Output file path (default: `sandstone/output/redlines.json`)
- `--evaluate`: Run evaluation against expected output
- `--verbose`: Show detailed progress

## Output Format

The system generates a JSON array of issues:

```json
[
  {
    "text_snippet": "exact problematic text from document",
    "playbook_clause_reference": "Confidential Information",
    "suggested_fix": "ideal clause text from playbook"
  }
]
```

## Performance Metrics

**Latest Evaluation Results:**

- ✅ **Recall: 100.0%** - Found all expected issues
- ✅ **Precision: 72.7%** - High accuracy
- ✅ **F1 Score: 84.2%** - Excellent balance
- ✅ **ROUGE-1: 71.5%** - Strong text similarity

**Pass Criteria:**
- Recall ≥ 80% ✅
- Precision ≥ 60% ✅
- ROUGE-1 ≥ 50% ✅

**Status: ✅ SYSTEM PASSES**

## Technology Stack

- **LLM**: OpenAI GPT-4o-mini (cost-effective, high quality)
- **Structured Output**: Instructor (guaranteed valid responses)
- **Embeddings**: Sentence Transformers (`all-MiniLM-L6-v2`)
- **Vector Search**: FAISS (fast similarity search)
- **Document Parsing**: striprtf
- **Data Validation**: Pydantic v2
- **CLI**: Rich (beautiful terminal output)

## Cost Efficiency

- **Per document**: ~$0.04 (18 clauses × $0.002 per analysis)
- **Model**: GPT-4o-mini at $0.15/1M input tokens
- **Well under budget**: $50 API limit

## Pipeline Steps

1. **Document Parsing** - Extract clauses from RTF document
2. **Playbook Loading** - Index legal playbook with semantic embeddings
3. **Semantic Matching** - Match document clauses to playbook clauses
4. **Issue Analysis** - Use LLM to detect problems and extract snippets
5. **Output Generation** - Create structured JSON redlines
6. **Evaluation** - Compare against expected output (optional)

## Project Structure

```
.
├── main.py                    # Main orchestration script
├── sandstone/
│   ├── config.py              # Configuration
│   ├── models/                # Pydantic models
│   │   ├── document.py
│   │   ├── playbook.py
│   │   ├── redline.py
│   │   └── evaluation.py
│   ├── services/              # Core services
│   │   ├── document_parser.py
│   │   ├── playbook_loader.py
│   │   ├── semantic_matcher.py
│   │   ├── issue_analyzer.py
│   │   └── evaluator.py
│   └── prompts/               # LLM prompts
│       └── issue_detector.py
├── docs/                      # Input files
│   ├── bad_document.txt.rtf
│   ├── playbook.json
│   └── expected_output.json
├── pyproject.toml             # Dependencies
└── README.md                  # This file
```

## Design Principles

1. **Type Safety**: Full Pydantic models throughout
2. **Modularity**: Single-responsibility services
3. **Testability**: Each component independently testable
4. **Cost-Conscious**: Efficient LLM usage with caching
5. **Production-Ready**: Error handling, logging, CLI

## Testing

```bash
# Test individual components
uv run python test_step2a.py    # Document parser
uv run python test_step2b.py    # Playbook loader
uv run python test_step3.py     # Semantic matcher
uv run python test_step4.py     # Issue analyzer
uv run python test_evaluation.py # Evaluation

# Full pipeline test
uv run python test_step4_full.py
```

## Development Notes

### Engineering Standards

- ✅ Uses `uv` for dependency management
- ✅ Virtual environment: `.venv`
- ✅ Type hints throughout
- ✅ Pydantic for data validation
- ✅ Instructor for structured LLM outputs
- ✅ Clean, modular architecture

### Key Design Decisions

1. **Top-1 Matching**: Analyze only best semantic match per clause (cost-efficient, accurate)
2. **Low Temperature**: 0.1 for consistent LLM responses
3. **Semantic Pre-filtering**: FAISS reduces LLM calls by ~70%
4. **Structured Output**: Instructor eliminates JSON parsing errors

## Assignment Compliance

This project fulfills the requirements:

✅ **Task 1: Redlining Script**
- Input: `bad_document.txt.rtf`
- Output: JSON list of issues
- LLM integration: GPT-4o-mini with Instructor

✅ **Task 2: Performance Evaluation**
- Precision, Recall, F1 metrics
- ROUGE text similarity scores
- Comparison with `expected_output.json`

✅ **Submission Requirements**
- Code: Complete, documented, modular
- Output: `sandstone/output/redlines.json`
- Performance: 100% recall, 72.7% precision, 71.5% ROUGE-1

## License

This is an academic project for the MLE Take-Home Assignment.
