# First we initialize the model we want to use.
from langchain_anthropic import ChatAnthropic
import os
import json
import sqlite3
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from langgraph_sdk import get_sync_client
from langgraph_sdk.client import SyncLangGraphClient
from langgraph.checkpoint.sqlite import SqliteSaver
from typing import Optional


model = ChatAnthropic(temperature=0, model_name="claude-3-7-sonnet-latest")


def _ensure_env(var: str):
    if not os.environ.get(var):
        raise RuntimeError(f"{var} is not set. Please set it in your environment or .env file.")


_ensure_env("ANTHROPIC_API_KEY")

alice = get_sync_client(url="http://localhost:2024")
charlie = get_sync_client(url="http://localhost:2025")


def ask_agent(client: SyncLangGraphClient, agent: str, question: str, thread_id: Optional[str] = None) -> str:
    final_chunk = None
    for chunk in client.runs.stream(
        thread_id,  # Threadless run
        agent,  # Name of assistant. Defined in langgraph.json.
        input={
            "messages": [{
                "role": "human",
                "content": question,
            }],
        },
        stream_mode="updates",
    ):
        final_chunk = chunk
        #print(f"Receiving new event of type: {chunk.event}...")
        #print(chunk.data)

    return json.dumps(final_chunk.data)


@tool
def ask_alice(question: str, thread_id: Optional[str] = None) -> str:
    """Use this to ask Alice a question."""
    return ask_agent(alice, "alice", question, thread_id=thread_id)


@tool
def ask_charlie(question: str, thread_id: Optional[str] = None) -> str:
    """Use this to ask Charlie a question."""
    return ask_agent(charlie, "charlie", question, thread_id=thread_id)


tools = [ask_alice, ask_charlie]


# Define the graph
graph = create_react_agent(model, tools=tools)
