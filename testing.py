from langgraph_sdk import get_sync_client
import uuid


thread = str(uuid.uuid4())

coordinator = get_sync_client(url="http://localhost:2026")

coordinator.threads.create(
    thread_id=thread,
    if_exists='do_nothing'
)

for chunk in coordinator.runs.stream(
    thread,  # Threadless run
    "coordinator",  # Name of assistant. Defined in langgraph.json.
    input={
        "messages": [{
            "role": "human",
            "content": "can you have alice pay charlie 110 sats?",
        }],
    },
    stream_mode="updates",
):
    print(f"Receiving new event of type: {chunk.event}...")
    print(chunk.data)

for chunk in coordinator.runs.stream(
    thread,  # Threadless run
    "coordinator",  # Name of assistant. Defined in langgraph.json.
    input={
        "messages": [{
            "role": "human",
            "content": "can you verify charlie received the payment?",
        }],
    },
    stream_mode="updates",
):
    print(f"Receiving new event of type: {chunk.event}...")
    print(chunk.data)