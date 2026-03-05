"""Judgement Agent — produces legal judgement with predefined topic sub-agents."""

from google.adk.agents import Agent

from config import AGENTIC_AI_MODEL
from skill import load_skill

# ── Predefined Topic Sub-agents ──────────────────────────────────────

deposit_specialist = Agent(
    name="deposit_specialist",
    model=AGENTIC_AI_MODEL,
    description="ผู้เชี่ยวชาญด้านกฎหมายเงินฝากและบัญชีธนาคาร",
    instruction=load_skill("legal_agentic", "deposit-specialist"),
)

lending_specialist = Agent(
    name="lending_specialist",
    model=AGENTIC_AI_MODEL,
    description="ผู้เชี่ยวชาญด้านกฎหมายสินเชื่อ ค้ำประกัน และหลักประกัน",
    instruction=load_skill("legal_agentic", "lending-specialist"),
)

hp_specialist = Agent(
    name="hp_specialist",
    model=AGENTIC_AI_MODEL,
    description="ผู้เชี่ยวชาญด้านกฎหมายเช่าซื้อและประกาศ สคบ.",
    instruction=load_skill("legal_agentic", "hp-specialist"),
)

# ── Main Judgement Agent ─────────────────────────────────────────────

judgement_agent = Agent(
    name="judgement_agent",
    model=AGENTIC_AI_MODEL,
    description="วินิจฉัยคำถามทางกฎหมายโดยอ้างอิงตัวบทกฎหมายและคำพิพากษาศาลฎีกา",
    instruction=load_skill("legal_agentic", "legal-judgement"),
    sub_agents=[deposit_specialist, lending_specialist, hp_specialist],
    output_key="judgement",
)
