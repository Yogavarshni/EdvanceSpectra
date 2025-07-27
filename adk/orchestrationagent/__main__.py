import os
import sys
import logging
import argparse
import uvicorn
import asyncio
from dotenv import load_dotenv

from orchestrationagent.agent import root_agent
from orchestrationagent.task_manager import TaskManager
from common.a2a_server import create_agent_server

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("orchestrationagent")

# Load .env
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path=dotenv_path, override=True)

def parse_args():
    parser = argparse.ArgumentParser(description="Start the Orchestration Agent A2A server")
    parser.add_argument("--host", default=os.getenv("HOST", "0.0.0.0"))
    parser.add_argument("--port", type=int, default=int(os.getenv("PORT", "8001")))
    return parser.parse_args()

async def main():
    logger.info("Booting Orchestration Agent...")
    agent = root_agent  # root_agent is not a coroutine in your code
    task_manager = TaskManager(agent)

    app = create_agent_server(
        name=agent.name,
        description=agent.description,
        task_manager=task_manager
    )

    args = parse_args()
    config = uvicorn.Config(app=app, host=args.host, port=args.port, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Shutting down orchestration agent.")
        sys.exit(0)
    except Exception as e:
        logger.exception(f"Unhandled error: {str(e)}")
        sys.exit(1)
