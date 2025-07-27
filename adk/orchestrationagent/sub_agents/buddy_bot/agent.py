from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool

from .group_forming_agent.agent import group_forming_agent
from .mentor_assigning_agent.agent import mentor_assigning_agent

from dotenv import load_dotenv
load_dotenv()

MODEL = "gemini-2.5-pro"

buddy_bot = Agent(
    name ="buddy_bot",
    model=MODEL,
    description="Assigns mentor to students and form groups for some activity that may be asked",
    instruction= """
    If the user question is about forming groups for a subject for some grade then use the group_forming_agent
    If the user question is about assigning a mentor to a student then use this mentor_assigning_agent

    Dont not use any other tools.
    """,
    tools=[
        AgentTool(agent=group_forming_agent),
        AgentTool(agent=mentor_assigning_agent)
    ]
)