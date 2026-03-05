"""Conclusion Agent — produces conclusion summary and practical recommendations."""

from google.adk.agents import Agent

from config import AGENTIC_AI_MODEL
from skill import load_instruction

conclusion_agent = Agent(
    name="conclusion_agent",
    model=AGENTIC_AI_MODEL,
    description="จัดทำข้อสรุปและข้อเสนอแนะที่เป็นรูปธรรมสำหรับธนาคาร",
    instruction=load_instruction("legal_agentic", "legal-conclusion"),
    output_key="conclusion",
)
