"""Law Synthesizer Agent — merges and prioritizes results from General Law and Specific Law query agents."""

from google.adk.agents import Agent

from config import AGENTIC_AI_MODEL
from skill import load_skill

synthesizer_agent = Agent(
    name="synthesizer_agent",
    model=AGENTIC_AI_MODEL,
    description="รวบรวมและจัดลำดับความสำคัญของตัวบทกฎหมายจากแหล่งข้อมูลทั่วไปและเฉพาะ",
    instruction=load_skill("legal_agentic", "law-synthesizer"),
    output_key="synthesized_law",
)
