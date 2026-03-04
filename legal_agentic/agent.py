import os
import asyncio

from config import *

import datetime

from google import genai
from google.genai import types
from google.adk.agents import Agent
from google.adk.tools import google_search

chat_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def get_current_time() -> dict:
    """
    Get the current time in a structured format.
    """
    return {
        "current_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }


agent = Agent(
    name="tool_agent",
    model="gemini-3-flash_preview",
    description="Tool Agent",
    instructions = """
    You are a helpful assistant that can use tools to answer questions. You have access to the following tool:
     - google_search
    """,
    tools=[google_search]
    
    # tools = [google_search, get_current_time] <- does not work, cannot holding two tools at the same time
    # especially one is custom and another is from tool library
)
