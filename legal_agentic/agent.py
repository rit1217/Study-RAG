import os
import asyncio

from google import genai
from google.genai import types

from agent_framework import  ChatAgent

chat_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

agent = ChatAgent(
    chat_client = chat_client,
    instructions = 
)
