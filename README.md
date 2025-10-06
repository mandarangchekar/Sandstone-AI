# AI-Powered NDA Document Redlining System

An intelligent document analysis system that uses LLMs and semantic search to identify legal issues in NDA documents based on a structured playbook.

## Key Features

- **AI-Driven Analysis**: GPT-4o-mini for intelligent clause analysis
- **Semantic Matching**: Sentence transformers + FAISS for accurate clause identification
- **Structured Output**: Instructor for guaranteed valid JSON
- **Benchmarking**: Pydantic Evals framework with 8 gold-standard test cases
- **Production-Ready**: Clean, modular, type-safe code with Pydantic models

## Quick Start

```bash
# Install dependencies
uv sync

# Create .env file with your OpenAI API key
echo "OPENAI_API_KEY=your_key_here" > .env

# Run the pipeline
python main.py

# Run evaluation benchmarks
python sandstone/tests/run_pydantic_evals.py
```

## Usage

```bash
# Basic usage (uses default files)
python main.py

# With verbose output
python main.py --verbose

# Custom files
python main.py --document path/to/doc.rtf --playbook path/to/playbook.json --output path/to/output.json
```

See [COMMANDS.md](COMMANDS.md) for all available commands and test options.

## Architecture

```
sandstone/
├── models/          # Pydantic data models (document, playbook, redline)
├── services/        # Core pipeline services
│   ├── document_parser.py      # RTF → structured clauses
│   ├── playbook_loader.py      # Playbook indexing with FAISS
│   ├── semantic_matcher.py     # Document ↔ Playbook matching
│   └── issue_analyzer.py       # LLM-based issue detection
├── prompts/         # LLM prompt engineering
├── evals/           # Pydantic Evals framework
│   ├── dataset.py              # 8 benchmark test cases
│   ├── task.py                 # Task function for evaluation
│   ├── evaluators.py           # Custom SemanticSimilarity evaluator
│   └── models.py               # Evaluation data models
├── tests/           # Component tests
└── config.py        # Configuration

main.py              # Main pipeline orchestration
```

## Pipeline

1. **Parse Document** → Extract clauses from RTF
2. **Load Playbook** → Index legal standards with embeddings
3. **Match Clauses** → Semantic similarity matching (FAISS)
4. **Analyze Issues** → LLM identifies problems and generates fixes
5. **Output Results** → Structured JSON redlines

## Output Format

```json
[
  {
    "text_snippet": "exact problematic text from document",
    "playbook_clause_reference": "Confidential Information",
    "suggested_fix": "recommended replacement text"
  }
]
```

## Evaluation

Benchmarking uses Pydantic Evals with dual validation:

1. **Semantic Similarity** (75% threshold) - Verifies correct text extraction
2. **LLM Judge** - Validates suggested fixes solve the legal issue

```bash
python sandstone/tests/run_pydantic_evals.py
```

## Technology Stack

- **LLM**: OpenAI GPT-4o-mini
- **Structured Output**: Instructor
- **Embeddings**: Sentence Transformers (`all-MiniLM-L6-v2`)
- **Vector Search**: FAISS
- **Evaluation**: Pydantic Evals
- **Data Validation**: Pydantic v2
- **CLI**: Rich

## Cost

- **~$0.05 per document** (18 clauses analyzed)
- **~$0.03 per evaluation run** (8 test cases with LLM judge)

## Requirements

- Python 3.13+
- OpenAI API key
- `uv` package manager