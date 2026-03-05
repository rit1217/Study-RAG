# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A RAG (Retrieval-Augmented Generation) project focused on Thai legal document Q&A for a private bank (KKP). Uses Google Gemini's File Search API to store and retrieve legal PDFs, then generates structured legal opinions evaluated against expert answers. Includes an automated eval review pipeline that compares human expert scores against LLM-based scorers and suggests prompt improvements.

## Architecture

### Notebooks

- **`gemini_file_search_local.ipynb`** — Local development version. Main notebook for running RAG queries and evaluations. Uses `os.getenv("GEMINI_API_KEY")` and local `./docs/` directory.
- **`gemini_file_search_cloud.ipynb`** — Original Colab-based notebook. Uses Google Drive for file storage and Colab's `userdata` for secrets.
- **`feedback_review.ipynb`** — Eval scorer review notebook. Loads eval results from a version folder, re-runs each scorer independently (reference, judgement, suggestion), compares against human scores, and suggests prompt improvements.
- **`maf_legal.ipynb`** — MAF (Mutually Assured Feedback) legal analysis utility notebook.

### RAG Pipeline (gemini_file_search notebooks)

1. **Gemini client init** → Create/select File Search Stores via `LegalRAGClient`
2. **Document upload** → Upload PDFs with metadata (law type, name, year) to Gemini File Search Stores
3. **Query** → `rag.ask()` sends a structured Thai legal prompt requiring 3-part answers (relevant statutes, judgement, conclusion/recommendations)
4. **Evaluation** → Braintrust `Eval` with custom LLM-based scorers

### Eval Review Pipeline (feedback_review notebook)

1. **Load eval results** → `EvalReviewClient.load_eval_folder()` reads all JSON files from `eval_results/eval_scorer_{version}/`
2. **Compare scores** → Show human vs auto scores side-by-side (skip entries with `None` human scores)
3. **Per-scorer review** (reference, judgement, suggestion independently):
   - Re-run scorer via `autoevals.LLMClassifier` → get score + rationale + choice
   - Compare re-run scores vs human scores
   - Summarize discrepancies (human feedback vs auto rationale)
   - Suggest improved scorer prompt for the next version

### Python Modules (`legal_rag/`)

- **`client.py`** — `LegalRAGClient`: Core RAG client wrapping Gemini File Search API. Key method: `ask(question, file_store_name_list, ...)` returns `(response, response_text)` with grounding citations.
- **`eval.py`** — Scorer factory functions using `autoevals.LLMClassifier`: `create_legal_reference_scorer`, `create_legal_judgement_scorer`, `create_legal_suggestion_scorer`, plus similarity/distance/factuality scorers.
- **`eval_review.py`** — `EvalReviewClient`: Loads eval results, re-runs scorers with rationale capture, compares human vs auto scores, analyzes discrepancies, and suggests prompt improvements.
- **`config.py`** — Pre-configured Gemini File Search Store IDs (General Law, Public Company Law, Supreme Court Statements).

### Skills (`skill.py` + `.claude/skills/`)

- **`skill.py`** (project root) — Two loader functions:
  - `load_skill(group, name)`: Loads current best skill from `.claude/skills/{group}/{name}/SKILL.md` (strips YAML frontmatter).
  - `load_prompt(agent_type, model, name, version)`: Loads versioned prompts from `skill_archive/` (backward compatibility).
- **`.claude/skills/legal_agentic/`** — Skills for the agentic pipeline agents (general-law-query, specific-law-query, sc-query, law-synthesizer, legal-judgement, deposit-specialist, lending-specialist, hp-specialist, legal-conclusion, legal-reviewer).
- **`.claude/skills/legal_rag/`** — Skills for single-agent RAG (legal-qa-flash, legal-qa-pro).

### Skill Archive (`skill_archive/`)

Versioned prompt snapshots, organized as `skill_archive/{agent_type}/{model}/{name}_{version}.md`:

- **`legal_qa/`** — System prompts for legal Q&A (instructs 3-part structured answers)
- **`eval_scorer/`** — LLMClassifier prompts for scoring model outputs (reference, judgement, suggestion, similarity, distance, factuality)
- **`eval_review/`** — Review prompts (discrepancy_summary, score_analysis, prompt_improvement)

Models: `gemini-3-flash-preview`, `gemini-3-pro-preview`. Versions: `v01`, `v02`, `v03`.

### Evaluation Scorers (via `autoevals.LLMClassifier`)

Three legal scorers (each scores 0, 0.5, or 1):
- **`legal_reference_scorer`** — Correctness of cited legal statutes (Section 1)
- **`legal_judgement_scorer`** — Legal judgement correctness (Section 2)
- **`legal_suggestion_scorer`** — Conclusion & suggestion quality (Section 3)

Plus similarity scorers: `gemini_distance`, `gemini_sim`, `gemini_fact`.

### Data

- **`docs/KKP/LNC/`** — Legal PDFs and evaluation outputs
- **`docs/KKP/test_cases/`** — Excel test cases (Deposit, Lending, HP domains) with columns: question, expected statutes, judgement, conclusion
- **`docs/KKP/LNC/eval_results/eval_scorer_{version}/`** — Braintrust eval result JSONs per model/domain

### Configuration (`config.py`)

```python
LEGAL_AI_MODEL          # Model for legal Q&A (e.g. "gemini-3-pro-preview")
LEGAL_AI_PROMPT_VERSION # Prompt version for Q&A (e.g. "v02")
LEGAL_AI_TEMP           # Temperature for Q&A generation
EVAL_AI_MODEL           # Model for eval scorers
EVAL_AI_PROMPT_VERSION  # Prompt version for scorers — also determines eval_results folder
REVIEW_AI_MODEL         # Model for review/analysis
REVIEW_AI_PROMPT_VERSION # Prompt version for review prompts
EVAL_RESULTS_ROOT_PATH  # Root path for eval results
TEST_CASE_PATH          # Path to test case Excel files
DOCUMENTS_PATH          # Path to legal documents
SKILLS_DIR              # Path to .claude/skills/ directory
SKILL_ARCHIVE_DIR       # Path to skill_archive/ directory (versioned prompts)
```

## Environment Setup

```bash
pip install -r requirements.txt
```

Requires `GEMINI_API_KEY` environment variable (or Colab `userdata` for the cloud notebook). Braintrust evaluation requires `BRAINTRUST_API_KEY`.

Note: `uvloop` and `appnope` in requirements.txt are platform-specific (Linux/macOS only) — skip on Windows.

## Key Dependencies

- `google-genai` — Gemini API client (File Search Stores, content generation)
- `braintrust` / `autoevals` — Evaluation framework with LLM-based scoring
- `langchain` / `langgraph` — LLM orchestration framework
- `pypdf` — PDF processing
- `pandas` / `openpyxl` — Data manipulation and Excel test case loading
- `python-dotenv` — Environment variable loading
