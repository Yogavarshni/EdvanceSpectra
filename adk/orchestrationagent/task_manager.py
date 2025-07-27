"""
Task Manager for the Orchestration Root Agent.
Handles incoming tasks and invokes the root agent using the ADK Runner.
"""

import logging
import uuid
from typing import Dict, Any, Optional

from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.artifacts.in_memory_artifact_service import InMemoryArtifactService
from google.genai import types as adk_types

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define app name
A2A_APP_NAME = "orchestration_root_app"


class TaskManager:
    """Task Manager for the Orchestration Root Agent in A2A mode."""

    def __init__(self, agent: Agent):
        logger.info(f"Initializing TaskManager for agent: {agent.name}")
        self.agent = agent

        # ADK session and artifact services
        self.session_service = InMemorySessionService()
        self.artifact_service = InMemoryArtifactService()

        # ADK runner
        self.runner = Runner(
            agent=self.agent,
            app_name=A2A_APP_NAME,
            session_service=self.session_service,
            artifact_service=self.artifact_service
        )
        logger.info(f"ADK Runner initialized for app '{self.runner.app_name}'")

    async def process_task(self, message: str, context: Dict[str, Any], session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Processes a task message through the root agent.
        """

        user_id = context.get("user_id", "default_a2a_user")

        if not session_id:
            session_id = str(uuid.uuid4())
            logger.info(f"Generated new session_id: {session_id}")

        # FIXED: Await async session methods
        session = await self.session_service.get_session(
            app_name=A2A_APP_NAME,
            user_id=user_id,
            session_id=session_id
        )

        if not session:
            session = await self.session_service.create_session(
                app_name=A2A_APP_NAME,
                user_id=user_id,
                session_id=session_id,
                state={}
            )
            logger.info(f"Created new session: {session_id}")

        request_content = adk_types.Content(role="user", parts=[adk_types.Part(text=message)])

        try:
            # Run agent using ADK runner
            events_async = self.runner.run_async(
                user_id=user_id,
                session_id=session_id,
                new_message=request_content
            )

            final_message = "(No response generated)"
            raw_events = []

            async for event in events_async:
                raw_events.append(event.model_dump(exclude_none=True))

                if event.is_final_response() and event.content and event.content.role == "model":
                    if event.content.parts and event.content.parts[0].text:
                        final_message = event.content.parts[0].text
                        logger.info(f"Final response: {final_message}")

            return {
                "message": final_message,
                "status": "success",
                "data": {
                    "raw_events": raw_events[-3:]
                },
                "session_id": session_id
            }

        except Exception as e:
            logger.error(f"Error during task processing: {str(e)}")
            return {
                "message": f"Error processing request: {str(e)}",
                "status": "error",
                "data": {"error_type": type(e).__name__},
                "session_id": session_id
            }
