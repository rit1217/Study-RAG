"""Custom tools wrapping Gemini File Search API for ADK agents."""

import os

from google import genai
from google.genai import types

from ..config import (
    GENERAL_LAW_FILE_STORE,
    SPECIFIC_LAW_FILE_STORE,
    SUPREME_COURT_STATEMENT_FILE_STORE,
)

_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

MODEL = "gemini-3-flash-preview"


def _search_file_store(query: str, file_store_name: str) -> dict:
    """Internal helper: search a single Gemini File Search store."""
    response = _client.models.generate_content(
        model=MODEL,
        contents=query,
        config=types.GenerateContentConfig(
            temperature=0,
            tools=[
                types.Tool(
                    file_search=types.FileSearch(
                        file_search_store_names=[file_store_name],
                    )
                )
            ],
        ),
    )

    # Extract grounding sources
    sources = []
    grounding = response.candidates[0].grounding_metadata
    if grounding:
        sources = list({c.retrieved_context.title for c in grounding.grounding_chunks})

    return {
        "results": response.text,
        "sources": sources,
    }


def search_general_law(query: str) -> dict:
    """Search general law documents including the Civil and Commercial Code,
    Bankruptcy Act, Business Collateral Act, and Building Control Act.
    Use this tool when the question involves general Thai civil/commercial law."""
    return _search_file_store(query, GENERAL_LAW_FILE_STORE)


def search_specific_law(query: str) -> dict:
    """Search specific law documents including the Public Company Act and
    OCPD regulations. Use this tool when the question involves public company
    law or specific regulatory provisions."""
    return _search_file_store(query, SPECIFIC_LAW_FILE_STORE)


def search_supreme_court(query: str) -> dict:
    """Search Supreme Court statements and precedents categorized by legal topics
    such as banking/accounts, seals, minors' capacity, estate administrators,
    and corporate binding. Use this tool to find court rulings as supporting
    references for legal analysis."""
    return _search_file_store(query, SUPREME_COURT_STATEMENT_FILE_STORE)
