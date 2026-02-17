# Study-RAG

A RAG (Retrieval-Augmented Generation) project focused on Thai legal document Q&A for a private bank (KKP). Uses Google Gemini's File Search API to store and retrieve legal documents (PDFs, DOCX), then generates structured legal opinions evaluated against expert answers.

## Pipeline

1. **Document Upload** — Upload legal PDFs/DOCX with metadata (law type, name, year) to Gemini File Search Stores
2. **Query** — `ask_legal_gemini()` sends a structured Thai legal prompt requiring 3-part answers:
   - Relevant statutes & supreme court rulings
   - Legal judgement
   - Conclusion & recommendations
3. **Evaluation** — Braintrust `Eval` with custom LLM-based scorers

## Notebooks

| Notebook | Description |
|---|---|
| `introduction_to_rag.ipynb` | Original Colab version (Google Drive + Colab secrets) |
| `gemini_file_search_local.ipynb` | Local development version |

## Evaluation Scorers

Custom `LLMClassifier` scorers via `autoevals`:

| Scorer | What it evaluates |
|---|---|
| `legal_reference_scorer` | Correctness of cited legal statutes (section 1) |
| `legal_judgement_scorer` | Legal judgement correctness (section 2) |
| `legal_suggestion_scorer` | Conclusion & suggestion quality (section 3) |
| `gemini_distance` | Semantic embedding similarity |
| `gemini_sim` | Answer similarity |
| `gemini_fact` | Factuality (subset/superset/conflict analysis) |

## Data

- `documents/KKP/LNC/` — Legal documents organized by category (General Law, Public Company Law, Supreme Court Statements)
- `documents/KKP/prompts/` — Prompt templates for QA and evaluation scorers
- `documents/KKP/test_cases/` — Test case Excel files (Deposit, Lending)

## Setup

```bash
pip install -r requirements.txt
```

Required environment variables (set in `.env`):
- `GEMINI_API_KEY`
- `BRAINTRUST_API_KEY`

## Key Dependencies

- `google-genai` — Gemini API client (File Search Stores, content generation)
- `braintrust` / `autoevals` — Evaluation framework with LLM-based scoring
- `chromadb` — Local vector store
- `langchain` / `langgraph` — LLM orchestration framework
- `pypdf` — PDF processing