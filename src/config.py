"""Shared paths and model settings for every entry point."""
import os
from pathlib import Path
from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")
GROQ_MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "models/gemini-embedding-001")
# Embeddings from different models cannot be mixed; preserve the old database.
KNOWLEDGE_MODE = os.getenv("KNOWLEDGE_MODE", "production")
if KNOWLEDGE_MODE not in {"sample", "production"}:
    raise ValueError("KNOWLEDGE_MODE must be sample or production")
VECTORSTORE_DIR = str(PROJECT_ROOT / ("db_sample_live" if KNOWLEDGE_MODE == "sample" else "db_gemini_embedding_001"))
KNOWLEDGE_FILE = PROJECT_ROOT / "data" / ("sample.txt" if KNOWLEDGE_MODE == "sample" else "agency.txt")
SAMPLE_NOTICE = "SAMPLE DATA - REVIEW BEFORE SENDING: This draft uses fictional business information. Verify and replace sample prices and policies before sending."


