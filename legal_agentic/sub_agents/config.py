"""Configuration constants and helpers for the legal_agentic pipeline."""

import pathlib

_SUB_AGENTS_DIR = pathlib.Path(__file__).resolve().parent
SKILLS_DIR = _SUB_AGENTS_DIR / "skills"

# Model configuration
AGENTIC_AI_MODEL = "gemini-3-flash-preview"
AGENTIC_AI_PROMPT_VERSION = "v01"

# Gemini File Search Store IDs
GENERAL_LAW_FILE_STORE = "fileSearchStores/lcgeneral-law-documents-8uyfomy1ah0b"
SPECIFIC_LAW_FILE_STORE = "fileSearchStores/lcspecific-law-documents-chja6cb21834"
SUPREME_COURT_STATEMENT_FILE_STORE = "fileSearchStores/lcsupreme-court-statements-v0oghu9g8b7f"
