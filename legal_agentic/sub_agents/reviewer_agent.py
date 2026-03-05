"""Reviewer/Scorer Agent — self-assesses legal opinion quality with SC context."""

from google.adk.agents import Agent

from config import AGENTIC_AI_MODEL
from skill import load_instruction

reviewer_agent = Agent(
    name="reviewer_agent",
    model=AGENTIC_AI_MODEL,
    description="ตรวจสอบคุณภาพความเห็นทางกฎหมายและให้คะแนนความมั่นใจ",
    instruction=load_instruction("legal_agentic", "legal-reviewer"),
    output_key="review_result",
)
