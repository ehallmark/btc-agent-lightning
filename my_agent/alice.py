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
