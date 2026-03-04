"""Reviewer/Scorer Agent — self-assesses legal opinion quality with SC context."""

from google.adk.agents import Agent

from legal_rag.config import AGENTIC_AI_MODEL, AGENTIC_AI_PROMPT_VERSION
from legal_rag.prompts import load_prompt

reviewer_agent = Agent(
    name="reviewer_agent",
    model=AGENTIC_AI_MODEL,
    description="ตรวจสอบคุณภาพความเห็นทางกฎหมายและให้คะแนนความมั่นใจ",
    instruction=load_prompt(
        "legal_agentic", AGENTIC_AI_MODEL,
        "reviewer_agent", AGENTIC_AI_PROMPT_VERSION,
    ),
    output_key="review_result",
)
