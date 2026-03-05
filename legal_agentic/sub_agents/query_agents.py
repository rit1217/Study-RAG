"""Parallel Query Agents — SC query + Law query (general & specific) simultaneously."""

from google.adk.agents import Agent, ParallelAgent

from config import AGENTIC_AI_MODEL
from skill import load_instruction
from legal_agentic.tools import search_general_law, search_specific_law, search_supreme_court

sc_query_agent = Agent(
    name="sc_query_agent",
    model=AGENTIC_AI_MODEL,
    description="ค้นหาคำพิพากษาศาลฎีกาที่เกี่ยวข้อง",
    instruction=load_instruction("legal_agentic", "sc-query"),
    tools=[search_supreme_court],
    output_key="sc_results",
)

law_query_agent = Agent(
    name="law_query_agent",
    model=AGENTIC_AI_MODEL,
    description="ค้นหาและรวบรวมตัวบทกฎหมายทั่วไปและเฉพาะ จัดลำดับความสำคัญโดยกฎหมายเฉพาะมาก่อน",
    instruction=load_instruction("legal_agentic", "law-query"),
    tools=[search_general_law, search_specific_law],
    output_key="synthesized_law",
)

query_agents = ParallelAgent(
    name="query_agents",
    sub_agents=[sc_query_agent, law_query_agent],
)
