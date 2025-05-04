import sqlite3
from contextlib import asynccontextmanager
from dotenv import load_dotenv
import os
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.checkpoint.sqlite import SqliteSaver

from lightning_agent.utils.agent_workflow import create_workflow

load_dotenv()  # take environment variables from .env.


user = 'alice'


def _ensure_env(var: str):
    if not os.environ.get(var):
        raise RuntimeError(f"{var} is not set. Please set it in your environment or .env file.")


_ensure_env("ANTHROPIC_API_KEY")


@asynccontextmanager
async def make_graph():
    async with MultiServerMCPClient(
        {
            'lightning': {
                'url': os.environ['ALICE_MCP_URL'],
                'transport': 'sse',
            }
        }
    ) as lightning_mcp:
        workflow = create_workflow(user, lightning_mcp)
        conn = sqlite3.connect(f"{user}.db")
        memory = SqliteSaver(conn)
        graph = workflow.compile(checkpointer=memory)
        yield graph
