"""Judgement Agent — produces legal judgement using specialist skills as tools.

Specialist skills are auto-discovered from .claude/skills/legal_agentic/*-specialist/
directories. Adding a new specialist requires only creating a SKILL.md file.
"""

import pathlib

from google.adk.agents import Agent
from google.adk.skills import load_skill_from_dir
from google.adk.tools import skill_toolset

from config import AGENTIC_AI_MODEL, SKILLS_DIR
from skill import load_instruction

# ── Auto-discover specialist skills ──────────────────────────────────

skills_dir = pathlib.Path(SKILLS_DIR) / "legal_agentic"
specialist_skills = [
    load_skill_from_dir(p)
    for p in sorted(skills_dir.iterdir())
    if p.is_dir() and p.name.endswith("-specialist")
]

specialist_toolset = skill_toolset.SkillToolset(skills=specialist_skills)

# ── Main Judgement Agent ─────────────────────────────────────────────

judgement_agent = Agent(
    name="judgement_agent",
    model=AGENTIC_AI_MODEL,
    description="วินิจฉัยคำถามทางกฎหมายโดยอ้างอิงตัวบทกฎหมายและคำพิพากษาศาลฎีกา",
    instruction=load_instruction("legal_agentic", "legal-judgement"),
    tools=[specialist_toolset],
    output_key="judgement",
)
