from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from dotenv import load_dotenv
import os
import uuid

load_dotenv()

MODEL = "gemini-2.5-pro"

video_generator_agent = Agent(
    name="video_generator_agent",
    model=MODEL,
    description="Creates educational videos based on a topic and grade.",
    instruction=(
        "You are a helpful assistant that generates short educational videos based on a topic and grade level.\n\n"
    ),
)