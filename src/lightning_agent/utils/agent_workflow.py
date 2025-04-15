from typing import Literal, TypedDict
from lightning_agent.utils.nodes import call_model, should_continue, get_tool_node
from lightning_agent.utils.state import AgentState
from langgraph.graph import StateGraph, MessagesState, START, END
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.pregel import RetryPolicy


# Define the config
class GraphConfig(TypedDict):
    model_name: Literal["anthropic", "openai"]


def create_workflow(name: str, lightning_client: MultiServerMCPClient):
    # Define a new graph
    workflow = StateGraph(AgentState, config_schema=GraphConfig)

    # Define the tool node
    tool_node = get_tool_node(lightning_client)

    # Define the two nodes we will cycle between
    workflow.add_node(f"agent-{name}", call_model(lightning_client))
    workflow.add_node(f"action-{name}", tool_node, retry=RetryPolicy(max_attempts=3))

    # Set the entrypoint as `agent`
    # This means that this node is the first one called
    workflow.set_entry_point(f"agent-{name}")

    # We now add a conditional edge
    workflow.add_conditional_edges(
        # First, we define the start node. We use `agent`.
        # This means these are the edges taken after the `agent` node is called.
        f"agent-{name}",
        # Next, we pass in the function that will determine which node is called next.
        should_continue,
        # Finally we pass in a mapping.
        # The keys are strings, and the values are other nodes.
        # END is a special node marking that the graph should finish.
        # What will happen is we will call `should_continue`, and then the output of that
        # will be matched against the keys in this mapping.
        # Based on which one it matches, that node will then be called.
        {
            # If `tools`, then we call the tool node.
            "continue": f"action-{name}",
            # Otherwise we finish.
            "end": END,
        },
    )

    # We now add a normal edge from `tools` to `agent`.
    # This means that after `tools` is called, `agent` node is called next.
    workflow.add_edge(f"action-{name}", f"agent-{name}")
    return workflow
