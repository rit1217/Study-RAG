"""Root Legal RAG Agent — LoopAgent wrapping a SequentialAgent pipeline.

Pipeline: Query (parallel: SC + Law) → Judge → Conclude → Review
Loop: Retry if Reviewer confidence < 80%, max 3 iterations.
"""

from google.adk.agents import SequentialAgent, LoopAgent

from legal_agentic.sub_agents.query_agents import query_agents
from legal_agentic.sub_agents.judgement_agent import judgement_agent
from legal_agentic.sub_agents.conclusion_agent import conclusion_agent
from legal_agentic.sub_agents.reviewer_agent import reviewer_agent

# Sequential pipeline: query all stores → judge → conclude → review
legal_pipeline = SequentialAgent(
    name="legal_pipeline",
    sub_agents=[
        query_agents,        # ParallelAgent: SC query + Law query (general+specific)
        judgement_agent,      # Legal judgement (with specialist skills)
        conclusion_agent,     # Conclusion & recommendations
        reviewer_agent,       # Self-assessment scorer
    ],
)

# Outer loop: retry pipeline if reviewer confidence < 80%
root_agent = LoopAgent(
    name="legal_rag_loop",
    sub_agents=[legal_pipeline],
    max_iterations=3,
)
