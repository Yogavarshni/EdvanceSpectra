from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool

from .time_table_summarization_agent.agent import time_table_summarization_agent
from .time_table_updator_agent.agent import time_table_updator_agent
from .class_planner_agent.agent import class_planner_agent

schedule_agent = Agent(
    name="schedule_agent",
    model="gemini-2.5-pro",
    description="Handles scheduling requests by summarizing or updating timetable.",
    instruction=(
        "You are the scheduler assistant. Delegate summarization to the summarize agent and updates to the updator agent."
        "Examples:\n"
        "- User says: 'What are today’s classes?' → Call time_table_summarization_agent.\n"
        "- User says: 'Add a History class at 2 PM tomorrow.' → Call time_table_updator_agent.\n"
    ),
    tools=[
        AgentTool(agent=time_table_summarization_agent),
        AgentTool(agent=time_table_updator_agent),
        AgentTool(agent=class_planner_agent)],  # treating agents as tools
)