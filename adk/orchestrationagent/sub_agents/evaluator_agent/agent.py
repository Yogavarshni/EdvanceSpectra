from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool

from dotenv import load_dotenv
load_dotenv()

from .read_assessment_agent.agent import read_assessment_agent
from .worksheet_corrector_agent.agent import worksheet_corrector_agent

evaluator_agent = Agent(
    name = "evaluator_agent",
    
)