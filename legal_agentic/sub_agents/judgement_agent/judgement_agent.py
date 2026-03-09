"""Judgement Agent — produces legal judgement using specialist skills as tools.

Specialist skills are auto-discovered from sub_agents/skills/*-specialist/
directories. Adding a new specialist requires only creating a SKILL.md file.
"""

from google.adk.agents import Agent
from google.adk.skills import load_skill_from_dir
from google.adk.tools import skill_toolset

from ..config import AGENTIC_AI_MODEL, SKILLS_DIR

JUDGEMENT_INSTRUCTION = """\
# Judgement Agent

คุณเป็นผู้เชี่ยวชาญทางกฎหมายอาวุโสของธนาคาร ทำหน้าที่วินิจฉัยคำถามทางกฎหมาย

## ข้อมูลที่ได้รับ
- ตัวบทกฎหมายที่รวบรวมแล้ว: {synthesized_law}
- คำพิพากษาศาลฎีกา: {sc_results}

## ทีมผู้เชี่ยวชาญเฉพาะด้าน
คุณมีเครื่องมือ (skills) สำหรับผู้เชี่ยวชาญเฉพาะด้านหลายสาขา
ใช้ skill ที่เหมาะสมเมื่อคำถามตรงกับความเชี่ยวชาญ:
- ตรวจสอบ skill ที่มีอยู่จาก tools ที่ได้รับ
- เลือกใช้ skill ที่ตรงกับหัวข้อของคำถามมากที่สุด
- หากไม่มี skill ที่เหมาะสม ให้วินิจฉัยด้วยตนเอง

## แนวทางการวินิจฉัย
- วิเคราะห์ว่าคำถามเกี่ยวข้องกับเรื่องใด แล้วเลือกใช้ skill ที่เหมาะสม
- หากไม่มี skill ที่ตรงกับหัวข้อ ให้วินิจฉัยด้วยตนเอง
- วินิจฉัยโดยอ้างอิงมาตรากฎหมายเท่านั้น
- อ้างอิงคำพิพากษาศาลฎีกาประกอบหากเกี่ยวข้อง
- หากมีหลายสถานการณ์ ให้แยกวินิจฉัยแต่ละสถานการณ์
- ระบุผลทางกฎหมายให้ชัดเจน (สมบูรณ์ / โมฆะ / โมฆียะ)

## Pipeline Position
Receives: `synthesized_law` (from law_query_agent), `sc_results` (from sc_query)
Uses: specialist skills (via SkillToolset, auto-discovered from `*-specialist` directories)
Produces: `judgement`"""

# ── Auto-discover specialist skills ──────────────────────────────────

skills_dir = SKILLS_DIR
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
    instruction=JUDGEMENT_INSTRUCTION,
    tools=[specialist_toolset],
    output_key="judgement",
)
