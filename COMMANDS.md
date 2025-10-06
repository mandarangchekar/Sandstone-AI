# Sandstone NDA Redlining - Command Reference

## 🚀 Main Pipeline

```bash
# Run full redlining pipeline (default files)
python main.py

# Run with verbose output (shows detailed progress)
python main.py --verbose

# Run with custom files
python main.py --document path/to/doc.rtf --playbook path/to/playbook.json --output path/to/output.json
```

**What it does:** Parses document → Matches clauses → Analyzes with LLM → Generates redlines

---

## 🧪 Component Tests

### Test 1: Data Models
```bash
python sandstone/tests/test_models.py
```
**What it does:** Validates Pydantic models load from JSON files correctly

### Test 2A: Document Parser
```bash
python sandstone/tests/test_step2a.py
```
**What it does:** Tests RTF document parsing and clause extraction

### Test 2B: Playbook Loader
```bash
python sandstone/tests/test_step2b.py
```
**What it does:** Tests playbook loading, embeddings generation, and semantic search

### Test 3: Semantic Matcher
```bash
python sandstone/tests/test_step3.py
```
**What it does:** Tests matching document clauses to playbook clauses

### Test 4: LLM Issue Analyzer (Sample)
```bash
python sandstone/tests/test_step4.py
```
**What it does:** Tests LLM analysis on 5 sample clauses (~$0.01 API cost)

### Test 4 Full: Complete Analysis
```bash
python sandstone/tests/test_step4_full.py
```
**What it does:** Runs full analysis on all 18 clauses, compares with expected output (~$0.04 API cost)

---

## 📊 Evaluation & Benchmarking

```bash
# Run comprehensive evaluation with Pydantic Evals
python sandstone/tests/run_pydantic_evals.py
```
**What it does:** Runs 8 benchmark test cases, evaluates semantic similarity & LLM judge scores (~$0.03 API cost)

---

## 📁 Output Files

- `sandstone/output/redlines.json` - Generated redline issues from main.py
- Console output - Pretty tables and summaries for all commands

---

## 🎯 Demo Sequence (Recommended)

```bash
# 1. Quick validation
python sandstone/tests/test_models.py

# 2. Show one component (semantic matching)
python sandstone/tests/test_step3.py

# 3. Run main pipeline
python main.py --verbose

# 4. Show evaluation/benchmarking
python sandstone/tests/run_pydantic_evals.py
```

---

## ⚙️ Configuration

All file paths configured in `sandstone/config.py`:
- `BAD_DOCUMENT_FILE` - Default NDA document to analyze
- `PLAYBOOK_FILE` - Legal playbook with standard clauses
- `EXPECTED_OUTPUT_FILE` - Gold standard for evaluation

API key required in `.env`:
```
OPENAI_API_KEY=your_key_here
```

---

## 💡 Quick Tips

- All tests use Rich library for beautiful terminal output
- Add `--verbose` flag to main.py for detailed LLM analysis logs
- Evaluation framework uses both semantic similarity (objective) and LLM judge (subjective)
- Total API cost for full demo: ~$0.08
