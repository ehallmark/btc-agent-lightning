# Agent Lightning

A LangGraph implementation of a ReAct agent connecting to a Bitcoin Lightning MCP Server.

### Prerequisites

+ Python >= 3.12
+ `uv` for package management
+ You must have a running Lightning MCP Server by following this repository (https://github.com/ehallmark/btc-lightning-mcp-server)
+ Update `.env` file with the proper configuration (see `.env.sample` for more info)

### Running the Alice agent

```bash
cd alice/
uv run langgraph dev --config langgraph-alice.json --port 2024
```

### Running the Charlie agent

```bash
cd charlie/
uv run langgraph dev --config langgraph-charlie.json --port 2025
```

### Running the Coordinator agent

```bash
uv run langgraph dev --config langgraph.json --port 2026
```

### Testing the Coordinator agent

```bash
uv run testing.py
```