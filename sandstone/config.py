"""Configuration and environment setup."""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
DOCS_DIR = PROJECT_ROOT / "docs"
OUTPUT_DIR = PROJECT_ROOT / "sandstone" / "output"

# Input files
PLAYBOOK_FILE = DOCS_DIR / "playbook.json"
BAD_DOCUMENT_FILE = DOCS_DIR / "bad_document.txt.rtf"
EXPECTED_OUTPUT_FILE = DOCS_DIR / "expected_output.json"

# Output files
REDLINES_OUTPUT_FILE = OUTPUT_DIR / "redlines.json"

# API Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
MODEL_NAME = "gpt-4o-mini"  # Cost-effective model
EMBEDDING_MODEL = "all-MiniLM-L6-v2"  # Fast and efficient embeddings

# Model parameters
TEMPERATURE = 0.1  # Low temperature for consistency
MAX_TOKENS = 2000
TOP_K_MATCHES = 3  # Number of candidate clauses to consider

