"""Law Synthesizer Agent — merges and prioritizes results from General Law and Specific Law query agents."""

from google.adk.agents import Agent

from config import AGENTIC_AI_MODEL, AGENTIC_AI_PROMPT_VERSION
from legal_rag.prompts import load_prompt

synthesizer_agent = Agent(
    name="synthesizer_agent",
    model=AGENTIC_AI_MODEL,
    description="รวบรวมและจัดลำดับความสำคัญของตัวบทกฎหมายจากแหล่งข้อมูลทั่วไปและเฉพาะ",
    instruction=load_prompt(
        "legal_agentic", "synthesizer_agent",
        "synthesizer_agent", AGENTIC_AI_PROMPT_VERSION,
    ),
    output_key="synthesized_law",
)
