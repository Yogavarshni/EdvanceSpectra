from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool
from dotenv import load_dotenv
load_dotenv()

from .sub_agents.buddy_bot.agent import buddy_bot
from .sub_agents.content_generator.agent import content_generator
from .sub_agents.schedule_agent.agent import schedule_agent

root_agent = Agent(
    name = "orchestrationagent",
    model = "gemini-2.5-pro",
    description = "An educational orchestration agent that coordinates sub agents like content generation, evaluation, scheduling, and mentorship",
    instruction = """
    You are the orchestration agent, that routes to agents based on the user query.

    If its about image and video generation, create games, worksheet and materials, or about explaining a complex topic then handoff to content_generator

    If its about scheduling an event or planning a class then handoff to scheduling_agent.

    If its about mentor assigning or group forming then handoff to buddy_bot
    """,
    sub_agents = [content_generator, schedule_agent, buddy_bot]
)