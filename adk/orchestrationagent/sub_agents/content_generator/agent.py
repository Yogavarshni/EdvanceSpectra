from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool

from .game_generator_agent.agent import game_generator_agent
from .image_generator_agent.agent import image_generator_agent
from .material_generator_agent.agent import material_generator_agent
from .video_generator_agent.agent import video_generator_agent
from .worksheet_generator_agent.agent import worksheet_generator_agent

content_generator = Agent(
    name = "content_generator",
    model = "gemini-2.5-pro",
    description = "Answers and generates content",
    instruction = """
    You are an content generator agent.
    If user input is about some question then answer it in detailed steps which is understandable to the grade specified,
    If the user input is about some image generation then use the image_generator_agent which is understandable to the grade specified and related to the topic given,
    If the user input is about some video generation then use the video_generator_agent which is understandable to the grade specified and related to the topic given,
    If the user input is about some game generation then use the game_generator_agent which is understandable to the grade specified and related to the topic given,
    If the user input is about some worksheet generation then use the worksheet_generator_agent which is related to the grade specified,
    If the user input is about some material generation then use the material_generator_agent which is understandable to the grade specified
    """, 
    tools = [
        AgentTool(agent=game_generator_agent),
        AgentTool(agent=video_generator_agent),
        AgentTool(agent=image_generator_agent),
        AgentTool(agent=worksheet_generator_agent),
        AgentTool(agent=material_generator_agent)
    ]
)