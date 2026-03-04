"""Conclusion Agent — produces conclusion summary and practical recommendations."""

from google.adk.agents import Agent

from legal_rag.config import AGENTIC_AI_MODEL, AGENTIC_AI_PROMPT_VERSION
from legal_rag.prompts import load_prompt

conclusion_agent = Agent(
    name="conclusion_agent",
    model=AGENTIC_AI_MODEL,
    description="จัดทำข้อสรุปและข้อเสนอแนะที่เป็นรูปธรรมสำหรับธนาคาร",
    instruction=load_prompt(
        "legal_agentic", AGENTIC_AI_MODEL,
        "conclusion_agent", AGENTIC_AI_PROMPT_VERSION,
    ),
    output_key="conclusion",
)
