# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A RAG (Retrieval-Augmented Generation) study project focused on Thai legal document Q&A for a private bank (KKP). Uses Google Gemini's File Search API to store and retrieve legal PDFs, then generates structured legal opinions evaluated against expert answers.

## Architecture

### Notebooks

- **`introduction_to_rag.ipynb`** — Original Colab-based notebook. Uses Google Drive for file storage and Colab's `userdata` for secrets.
- **`gemini_file_search_local.ipynb`** — Local development version. Uses `os.getenv("GEMINI_API_KEY")` and local `./documents/` directory for files.

Both notebooks share the same pipeline:
1. **Gemini client init** → Create/select File Search Stores
2. **Document upload** → Upload PDFs with metadata (law type, name, year) to Gemini File Search Stores
3. **Query** → `ask_legal_gemini()` sends a structured Thai legal prompt requiring 3-part answers (relevant statutes, judgement, conclusion/recommendations)
4. **Evaluation** → Braintrust `Eval` with custom LLM-based scorers using Gemini Pro

### Key Function

`ask_legal_gemini(client, question, file_search_store_name, with_grounding=True, gemini_model="gemini-3-flash-preview")` — Core RAG query function. Returns `(response, response_text)` with grounding source citations.

### Evaluation Scorers (via `autoevals.LLMClassifier`)

All scorers use `gemini-3-pro-preview`:
- `legal_judgement_scorer` — Thai legal judgement correctness
- `legal_suggestion_scorer` — Conclusion & suggestion quality
- `gemini_distance` — Semantic embedding similarity
- `gemini_sim` — Answer similarity
- `gemini_fact` — Factuality (subset/superset/conflict analysis)

### Data

- `documents/KKP/` — Legal PDFs organized by category (`General Law/`, `Public Company Law/`)
- `chroma/` — ChromaDB vector store (local embedding storage)
- Test cases loaded from Excel files with columns: question, expected summary, related laws

## Environment Setup

```bash
pip install -r requirements.txt
```

Requires `GEMINI_API_KEY` environment variable (or Colab `userdata` for the Colab notebook). Braintrust evaluation requires `BRAINTRUST_API_KEY`.

## Key Dependencies

- `google-genai` — Gemini API client (File Search Stores, content generation)
- `chromadb` — Local vector store
- `langchain` / `langgraph` — LLM orchestration framework
- `braintrust` / `autoevals` — Evaluation framework with LLM-based scoring
- `pypdf` — PDF processing
