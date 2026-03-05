# Legal QA (Pro Model)

Single-agent RAG approach that queries all 3 file stores and produces a structured legal opinion in one call using `gemini-3-pro-preview`. This is the **production default** model.

## How to Use

```python
from legal_rag.client import LegalRAGClient
from legal_rag.config import DEFAULT_FILE_STORES
from config import LEGAL_AI_MODEL, LEGAL_AI_PROMPT_VERSION, LEGAL_AI_TEMP

rag = LegalRAGClient()
prompt = rag.load_prompt("legal_qa", "legal_qa", LEGAL_AI_PROMPT_VERSION)

response, text = rag.ask(
    question="<LEGAL QUESTION>",
    file_store_name_list=DEFAULT_FILE_STORES,
    temperature=LEGAL_AI_TEMP,
    prompt_template=prompt,
    gemini_model=LEGAL_AI_MODEL,
)
```

## Prompt Structure (v02)

The prompt instructs the model to:

1. **มาตรากฎหมายที่เกี่ยวข้อง** — List all relevant statutes. Data from File Store only. Copy verbatim. Prioritize specific law over general law.
2. **คำวินิจฉัย** — Analyze using cited statutes only. Reference supreme court rulings. Separate analysis per scenario. State legal consequences clearly.
3. **ข้อสรุปและข้อเสนอแนะ** — Concise summary. Practical guidance for the bank. Legal risks and concerns.

## File Stores
- L&C-Public Company Law Documents (specific law)
- L&C-General Law Documents (general law)
- L&C-Supreme Court Statements (precedent)

Priority: Specific > General > Supreme Court

## Configuration (from config.py)
- Model: `gemini-3-pro-preview`
- Prompt version: `v02`
- Temperature: `0`