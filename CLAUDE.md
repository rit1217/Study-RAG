# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A RAG (Retrieval-Augmented Generation) project focused on Thai legal document Q&A for a private bank (KKP). Uses Google Gemini's File Search API to store and retrieve legal PDFs, then generates structured legal opinions evaluated against expert answers. Includes an automated eval review pipeline that compares human expert scores against LLM-based scorers and suggests prompt improvements.

## Architecture

### Agentic Pipeline (`legal_agentic/`)

Google ADK-based multi-agent pipeline:

```
LoopAgent (max 3)
└─ SequentialAgent
    ├─ query_agents (ParallelAgent)
    │   ├─ sc_query_agent → sc_results
    │   └─ law_query_agent → synthesized_law
    ├─ judgement_agent → judgement (with specialist SkillToolset)
    ├─ conclusion_agent → conclusion
    └─ reviewer_agent → review_result
```

Self-contained package with its own config, instructions, and skills:

- **`__init__.py`** — Exports `root_agent` and `app` (ADK `App` wrapper)
- **`agent.py`** — Root agent: `LoopAgent` wrapping `SequentialAgent` pipeline
- **`app.py`** — ADK `App` wrapper for stateful multi-agent sessions
- **`sub_agents/`** — All pipeline agents, tools, config, and skills:
  - **`config.py`** — Constants (`AGENTIC_AI_MODEL`, file store IDs, `SKILLS_DIR`)
  - **`tools.py`** — Gemini File Search wrappers
  - **`skills/`** — Specialist skills auto-discovered by ADK `SkillToolset`
  - **`query_agents/`**, **`judgement_agent/`**, **`conclusion_agent/`**, **`reviewer_agent/`** — Agent modules with hardcoded instructions

### Notebooks

- **`gemini_file_search_local.ipynb`** — Local development. Main notebook for running RAG queries and evaluations.
- **`gemini_file_search_cloud.ipynb`** — Original Colab-based notebook.
- **`feedback_review.ipynb`** — Eval scorer review. Re-runs scorers, compares against human scores, suggests prompt improvements.
- **`eval_review_agentic.ipynb`** — Agentic eval review with automated pipeline.
- **`agentic_maf_legal.ipynb`** — MAF (Mutually Assured Feedback) legal analysis.

### Python Modules

#### `legal_rag/` — RAG Client & Eval

- **`client.py`** — `LegalRAGClient`: Core RAG client wrapping Gemini File Search API. Key method: `ask(question, file_store_name_list, ...)` returns `(response, response_text)` with grounding citations.
- **`eval.py`** — Scorer factory functions using `autoevals.LLMClassifier`: `create_legal_reference_scorer`, `create_legal_judgement_scorer`, `create_legal_suggestion_scorer`, plus similarity/distance/factuality scorers.
- **`eval_review.py`** — `EvalReviewClient`: Loads eval results, re-runs scorers, compares human vs auto scores, analyzes discrepancies, suggests prompt improvements.
- **`config.py`** — Pre-configured Gemini File Search Store IDs.

#### `rag_agent/` — Base Client

- **`agent.py`** — `RAGClient`: Base class for Gemini client with file store management.

#### `skill.py` — Root Loader Functions

Two loader functions (for non-agentic modules):
- `load_instruction(group, name)`: Loads instructions from `instructions/{group}/{name}.md` (used by `legal_rag/`).
- `load_prompt(agent_type, name, version)`: Loads versioned prompts from `instruction_archive/{agent_type}/{name}_{version}.md`.

Note: `legal_agentic/` agents have instructions hardcoded directly in their Python files.

### Directory Layout

```
RAG/
├── legal_agentic/                   # Self-contained ADK agentic pipeline
│   ├── __init__.py                  # Exports root_agent, app
│   ├── agent.py                     # Root agent (LoopAgent)
│   ├── app.py                       # ADK App wrapper (stateful)
│   └── sub_agents/                  # Pipeline agents + config + tools
│       ├── config.py                # Model config, file store IDs, SKILLS_DIR
│       ├── tools.py                 # Gemini File Search wrappers
│       ├── skills/                  # Specialist skills (auto-discovered by ADK)
│       │   ├── deposit-specialist/SKILL.md
│       │   ├── lending-specialist/SKILL.md
│       │   └── hp-specialist/SKILL.md
│       ├── query_agents/            # SC + Law query (instructions hardcoded)
│       ├── judgement_agent/         # Legal judgement (instructions hardcoded)
│       ├── conclusion_agent/        # Conclusion & recommendations (instructions hardcoded)
│       └── reviewer_agent/          # Quality reviewer (instructions hardcoded)
├── instructions/                    # Non-agentic instructions
│   └── legal_rag/
│       ├── legal-qa-flash.md
│       └── legal-qa-pro.md
├── instruction_archive/             # Versioned prompt snapshots (flat, no model subdirs)
│   ├── eval_scorer/{name}_{version}.md
│   ├── eval_review/{name}_{version}.md
│   ├── legal_qa/{name}_{version}.md
│   └── legal_agentic/{agent}/{name}_{version}.md
├── legal_rag/                       # RAG client, eval scorers, eval review
├── rag_agent/                       # Base RAG client
├── config.py                        # Non-agentic configuration constants
└── skill.py                         # Root load_instruction(), load_prompt()
```

### Evaluation Scorers (via `autoevals.LLMClassifier`)

Three legal scorers (each scores 0, 0.5, or 1):
- **`legal_reference_scorer`** — Correctness of cited legal statutes (Section 1)
- **`legal_judgement_scorer`** — Legal judgement correctness (Section 2)
- **`legal_suggestion_scorer`** — Conclusion & suggestion quality (Section 3)

Plus similarity scorers: `gemini_distance`, `gemini_sim`, `gemini_fact`.

### Data

- **`docs/KKP/LNC/`** — Legal PDFs and evaluation outputs
- **`docs/KKP/test_cases/`** — Excel test cases (Deposit, Lending, HP domains)
- **`docs/KKP/LNC/eval_results/eval_scorer_{version}/`** — Braintrust eval result JSONs

### Configuration (`config.py`)

Root `config.py` (non-agentic):
```python
LEGAL_AI_MODEL          # Model for legal Q&A
LEGAL_AI_PROMPT_VERSION # Prompt version for Q&A
LEGAL_AI_TEMP           # Temperature for Q&A generation
EVAL_AI_MODEL           # Model for eval scorers
EVAL_AI_PROMPT_VERSION  # Prompt version for scorers
REVIEW_AI_MODEL         # Model for review/analysis
REVIEW_AI_PROMPT_VERSION # Prompt version for review prompts
EVAL_RESULTS_ROOT_PATH  # Root path for eval results
TEST_CASE_PATH          # Path to test case Excel files
DOCUMENTS_PATH          # Path to legal documents
INSTRUCTION_ARCHIVE_DIR # Path to instruction_archive/ (versioned prompts)
INSTRUCTIONS_DIR        # Path to instructions/ (non-agentic instructions)
```

`legal_agentic/sub_agents/config.py` (self-contained):
```python
AGENTIC_AI_MODEL                    # Model for agentic pipeline agents
AGENTIC_AI_PROMPT_VERSION           # Prompt version for agentic agents
GENERAL_LAW_FILE_STORE              # Gemini File Search Store ID
SPECIFIC_LAW_FILE_STORE             # Gemini File Search Store ID
SUPREME_COURT_STATEMENT_FILE_STORE  # Gemini File Search Store ID
```

## Environment Setup

```bash
pip install -r requirements.txt
```

Requires `GEMINI_API_KEY` environment variable (or Colab `userdata` for the cloud notebook). Braintrust evaluation requires `BRAINTRUST_API_KEY`.

Note: `uvloop` and `appnope` in requirements.txt are platform-specific (Linux/macOS only) — skip on Windows.

## Key Dependencies

- `google-adk` — Google Agent Development Kit (SkillToolset for specialist skill auto-discovery)
- `google-genai` — Gemini API client (File Search Stores, content generation)
- `braintrust` / `autoevals` — Evaluation framework with LLM-based scoring
- `pypdf` — PDF processing
- `pandas` / `openpyxl` — Data manipulation and Excel test case loading
- `python-dotenv` — Environment variable loading
