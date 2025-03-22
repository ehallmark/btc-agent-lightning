from dotenv import load_dotenv
import getpass
import os
from typing import TypedDict, Literal
from langgraph.graph import StateGraph, MessagesState, START, END
from lightning_client.client import LightningClient
from my_agent.utils.nodes import call_model, should_continue, get_tool_node
from my_agent.utils.state import AgentState


load_dotenv()  # take environment variables from .env.


def _set_env(var: str):
    if not os.environ.get(var):
        os.environ[var] = getpass.getpass(f"{var}: ")


_set_env("ANTHROPIC_API_KEY")


alice = LightningClient(
    rpc_port=10001,
    cert_path=os.path.expanduser('~/Library/Application Support/Lnd/tls.cert'),
    macaroon_path=os.path.expanduser('~/repos/lightning-ai/dev/alice/data/chain/bitcoin/simnet/admin.macaroon')
)
charlie = LightningClient(
    rpc_port=10003,
    cert_path=os.path.expanduser('~/Library/Application Support/Lnd/tls.cert'),
    macaroon_path=os.path.expanduser('~/repos/lightning-ai/dev/charlie/data/chain/bitcoin/simnet/admin.macaroon')
)


# Define the config
class GraphConfig(TypedDict):
    model_name: Literal["anthropic", "openai"]


# Define a new graph
workflow = StateGraph(AgentState, config_schema=GraphConfig)


# Define the tool node
tool_node = get_tool_node(alice)

# Define the two nodes we will cycle between
workflow.add_node("agent", call_model(alice))
workflow.add_node("action", tool_node)

# Set the entrypoint as `agent`
# This means that this node is the first one called
workflow.set_entry_point("agent")

# We now add a conditional edge
workflow.add_conditional_edges(
    # First, we define the start node. We use `agent`.
    # This means these are the edges taken after the `agent` node is called.
    "agent",
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
        "continue": "action",
        # Otherwise we finish.
        "end": END,
    },
)

# We now add a normal edge from `tools` to `agent`.
# This means that after `tools` is called, `agent` node is called next.
workflow.add_edge("action", "agent")

# Finally, we compile it!
# This compiles it into a LangChain Runnable,
# meaning you can use it as you would any other runnable
graph = workflow.compile()

'''
invoice = None

# example with a multiple tool calls in succession
for chunk in app.stream(
    {"messages": [("human", "create an invoice with amount 100")]},
    stream_mode="values",
):
    if chunk["messages"][-1].name == 'create_invoice':
        invoice = chunk["messages"][-1].content
        print(f'found payment request: {invoice}')
    chunk["messages"][-1].pretty_print()

if invoice:
    invoice = json.loads(invoice)
    
    for chunk in app.stream(
        {"messages": [("human", f"check the status of payment request {invoice['r_hash_str']}")]},
        stream_mode="values",
    ):
        chunk["messages"][-1].pretty_print()

    for chunk in app.stream(
        {"messages": [("human", f"pay the invoice with payment request {invoice['payment_request']}")]},
        stream_mode="values",
    ):
        chunk["messages"][-1].pretty_print()

    for chunk in app.stream(
        {"messages": [("human", f"check the status of payment request {invoice['r_hash_str']}")]},
        stream_mode="values",
    ):
        chunk["messages"][-1].pretty_print()
'''
