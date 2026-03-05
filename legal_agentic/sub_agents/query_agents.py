"""Parallel Query Agents — search all 3 legal document stores simultaneously."""

from google.adk.agents import Agent, ParallelAgent

from config import AGENTIC_AI_MODEL, AGENTIC_AI_PROMPT_VERSION
from legal_rag.prompts import load_prompt
from legal_agentic.tools import (
    search_general_law,
    search_specific_law,
    search_supreme_court,
)

sc_query_agent = Agent(
    name="sc_query_agent",
    model=AGENTIC_AI_MODEL,
    description="ค้นหาคำพิพากษาศาลฎีกาที่เกี่ยวข้องกับคำถามทางกฎหมาย",
    instruction=load_prompt(
        "legal_agentic", "sc_query_agent",
        "sc_query_agent", AGENTIC_AI_PROMPT_VERSION,
    ),
    tools=[search_supreme_court],
    output_key="sc_results",
)

general_law_query_agent = Agent(
    name="general_law_query_agent",
    model=AGENTIC_AI_MODEL,
    description="ค้นหาตัวบทกฎหมายทั่วไป เช่น ประมวลกฎหมายแพ่งและพาณิชย์ พ.ร.บ.ล้มละลาย พ.ร.บ.หลักประกันทางธุรกิจ",
    instruction=load_prompt(
        "legal_agentic", "general_law_query_agent",
        "general_law_query_agent", AGENTIC_AI_PROMPT_VERSION,
    ),
    tools=[search_general_law],
    output_key="general_law_results",
)

specific_law_query_agent = Agent(
    name="specific_law_query_agent",
    model=AGENTIC_AI_MODEL,
    description="ค้นหากฎหมายเฉพาะ เช่น พ.ร.บ.บริษัทมหาชนจำกัด ประกาศ สคบ.",
    instruction=load_prompt(
        "legal_agentic", "specific_law_query_agent",
        "specific_law_query_agent", AGENTIC_AI_PROMPT_VERSION,
    ),
    tools=[search_specific_law],
    output_key="specific_law_results",
)

query_agents = ParallelAgent(
    name="query_agents",
    sub_agents=[sc_query_agent, general_law_query_agent, specific_law_query_agent],
)
