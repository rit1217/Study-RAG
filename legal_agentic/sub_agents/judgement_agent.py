"""Judgement Agent — produces legal judgement with predefined topic sub-agents."""

from google.adk.agents import Agent

from legal_rag.config import AGENTIC_AI_MODEL, AGENTIC_AI_PROMPT_VERSION
from legal_rag.prompts import load_prompt

# ── Predefined Topic Sub-agents ──────────────────────────────────────

deposit_specialist = Agent(
    name="deposit_specialist",
    model=AGENTIC_AI_MODEL,
    description="ผู้เชี่ยวชาญด้านกฎหมายเงินฝากและบัญชีธนาคาร",
    instruction=load_prompt(
        "legal_agentic", "deposit_specialist",
        "deposit_specialist", AGENTIC_AI_PROMPT_VERSION,
    ),
)

lending_specialist = Agent(
    name="lending_specialist",
    model=AGENTIC_AI_MODEL,
    description="ผู้เชี่ยวชาญด้านกฎหมายสินเชื่อ ค้ำประกัน และหลักประกัน",
    instruction=load_prompt(
        "legal_agentic", "lending_specialist",
        "lending_specialist", AGENTIC_AI_PROMPT_VERSION,
    ),
)

hp_specialist = Agent(
    name="hp_specialist",
    model=AGENTIC_AI_MODEL,
    description="ผู้เชี่ยวชาญด้านกฎหมายเช่าซื้อและประกาศ สคบ.",
    instruction=load_prompt(
        "legal_agentic", "hp_specialist",
        "hp_specialist", AGENTIC_AI_PROMPT_VERSION,
    ),
)

# ── Main Judgement Agent ─────────────────────────────────────────────

judgement_agent = Agent(
    name="judgement_agent",
    model=AGENTIC_AI_MODEL,
    description="วินิจฉัยคำถามทางกฎหมายโดยอ้างอิงตัวบทกฎหมายและคำพิพากษาศาลฎีกา",
    instruction=load_prompt(
        "legal_agentic", "judgement_agent",
        "judgement_agent", AGENTIC_AI_PROMPT_VERSION,
    ),
    sub_agents=[deposit_specialist, lending_specialist, hp_specialist],
    output_key="judgement",
)
