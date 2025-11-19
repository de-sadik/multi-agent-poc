# Multi‑Agent Banking POC (Haystack + Gemini)

Lightweight proof‑of‑concept demonstrating a small multi‑agent architecture that combines:
- a simple intent router,
- a SQLite-backed credit-card tool,
- optional Haystack pipelines, and
- a Gemini (google.generativeai) LLM integration.

Key files
- CLI demo and orchestrator: [`main.py`](main.py) (provides [`run_multi_agent_chat`](main.py) and `credit_card_tool`)
- Model helper: [`list_models.py`](list_models.py)
- Offline test harness (stubbed SDK): [`test_poc.py`](test_poc.py)
- Banking POC variant (Haystack + agent modules): [`haystack-banking-multi-agent-poc/src/main.py`](haystack-banking-multi-agent-poc/src/main.py)
- Haystack pipelines / agents:
  - [`CreditCardPipeline`](haystack-banking-multi-agent-poc/src/pipelines/credit_card_pipeline.py)
  - [`SQLPipeline`](haystack-banking-multi-agent-poc/src/pipelines/sql_pipeline.py)
  - [`RouterAgent`](haystack-banking-multi-agent-poc/src/agents/router_agent.py)

## Agent Diagram 
![Banking Agent Diagram](./agent_diagram.png)
## Architecture Diagram
![Architecture Diagram](./architecture.png)

> Regenerate with:
```bash
# Graphviz (from agent_diagram.dot)
dot -Tpng agent_diagram.dot -o agent_diagram.png
# or Mermaid (from agent_diagram.mmd)
mmdc -i agent_diagram.mmd -o agent_diagram.png
```

## Quickstart

1. Create virtual env and install deps
```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

2. Configure Environment
Create a .env file or export variables:
```bash
# .env
GEMINI_API_KEY="YOUR_API_KEY"
# Optional: override default model (see list_models.py)
MODEL_NAME="models/gemini-2.5-pro"
```
Notes:
- For the offline stubbed test, you can set a dummy key to satisfy import time checks:
  - export GEMINI_API_KEY="dummy"

## Architecture Overview
This project demonstrates a **Multi-Agent Orchestrator** integrating with **Haystack** concepts:
- **Router**: `route_intent` directs queries to specific agents (credit_card, faq, general).
- **Agents**:
  - `credit_card_agent`: Uses `credit_card_sql_tool` to query SQLite (`credit_cards.db`) for context.
  - `faq_agent`: Answers strictly from embedded FAQ snippets.
  - `general_agent`: Falls back to general chat.
- **Integration**: Shows how to combine custom tools, SQL databases, and LLMs (Gemini) in a cohesive workflow.

Render:
```bash
# Mermaid (requires @mermaid-js/mermaid-cli)
mmdc -i agent_diagram.mmd -o agent_diagram.png

# Graphviz
dot -Tpng agent_diagram.dot -o agent_diagram.png
```

## Run
```bash
# CLI demo (type 'exit' to quit)
python main.py
```
List available models (and pick one supporting generateContent):
```bash
export GEMINI_API_KEY="YOUR_API_KEY"
python list_models.py
# Optionally: export MODEL_NAME="models/<your-model>"
```

## Test
```bash
# with pytest (if installed)
python -m pytest -q

# or run directly
python test_poc.py
```

## Test (offline deterministic)
The test_poc.py stubs google.generativeai to run without network or real API calls.
```bash
# Ensure an env var is present (dummy is fine for offline test)
export GEMINI_API_KEY="dummy"
python test_poc.py
```
What it does:
- Injects a stub genai.GenerativeModel that returns predictable text.
- Forces MODEL_NAME=models/test-stub.
- Runs run_multi_agent_chat on a credit card query and asserts output:
  - intent == "credit_card"
  - answer starts with "STUBBED_RESPONSE"

## SQLite Demo Data
- Database file: credit_cards.db (auto-created on first run)
- Tables: credit_cards, transactions
- Seeded with a small sample of customers and recent transactions
Tips:
- To reset demo data, delete credit_cards.db and rerun main.py.

## Troubleshooting
- google.generativeai SDK versions differ; if list_models() is missing, use list_models.py to inspect attributes or use gcloud/Vertex listings.
- If genai.configure() fails at import time, ensure GEMINI_API_KEY is set correctly.
- Haystack imports are optional; minimal fallbacks are included.
- Graphviz/Mermaid are optional; install only if rendering diagrams.

## Diagrams
- Graphviz (DOT → PNG):
```bash
dot -Tpng agent_diagram.dot -o agent_diagram.png
```
- Mermaid (MMD → PNG):
```bash
mmdc -i agent_diagram.mmd -o agent_diagram.png
```
- Live editor: https://mermaid.live
