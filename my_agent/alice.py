from dotenv import load_dotenv
import getpass
import os
from lightning_client import LightningClient
from my_agent.utils.agent_workflow import create_workflow


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

workflow = create_workflow("alice", alice)

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
