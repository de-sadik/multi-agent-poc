# ...existing code...
import os
import sqlite3
from typing import List, Dict, Any

# dotenv helper (optional)
try:
    from dotenv import load_dotenv
except Exception:
    def load_dotenv():
        return None

# Haystack 2.x imports with robust fallbacks. Some haystack
# distributions expose different names (e.g., `component` vs `Component`).
try:
    from haystack import Component, Pipeline
except Exception:
    # Try common alternatives, otherwise provide minimal fallbacks
    try:
        from haystack import component as Component  # type: ignore
    except Exception:
        class Component:  # minimal fallback
            def __init__(self, *a, **k):
                pass

    try:
        from haystack import pipeline as Pipeline  # type: ignore
    except Exception:
        class Pipeline:  # minimal fallback
            def __init__(self, *a, **k):
                pass

try:
    from haystack.utils import Secret
except Exception:
    class Secret:  # minimal fallback
        def __init__(self, *a, **k):
            pass

try:
    from haystack.components.builders import DynamicChatPromptBuilder
except Exception:
    DynamicChatPromptBuilder = None

try:
    from haystack.components.routers import ConditionalRouter
except Exception:
    ConditionalRouter = None

try:
    from haystack.components.writers import Writer
except Exception:
    Writer = None

# Minimal Tool shim — keep a tiny, predictable API and avoid relying
# on haystack's internal Component/Tool init signatures which vary
# across distributions.
class Tool:
    def __init__(self, name: str, description: str, fn):
        self.name = name
        self.description = description
        self.fn = fn

    def run(self, query: str):
        return {"results": self.fn(query)}

genai = None
try:
    import google.generativeai as genai_module
    genai = genai_module
except Exception:
    genai = None

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise RuntimeError("Set GEMINI_API_KEY in .env")

if genai is not None:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
    except Exception:
        # ignore configuration errors at import time; will raise at call time if needed
        pass

# Default model. Use an env var to override when needed (e.g. export MODEL_NAME="models/gemini-2.5-pro").
# The list_models helper shows available models; pick one that lists `generateContent` as supported.
MODEL_NAME = os.environ.get("MODEL_NAME", "models/gemini-2.5-pro")

# --------- SQLite setup (demo) ----------
DB_PATH = "credit_cards.db"

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS credit_cards (
    id INTEGER PRIMARY KEY,
    customer_name TEXT,
    card_number TEXT,
    credit_limit REAL,
    current_balance REAL,
    due_date TEXT,
    rewards_points INTEGER
);
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY,
    card_number TEXT,
    amount REAL,
    merchant TEXT,
    ts TEXT
);
"""

SEED_SQL = """
INSERT INTO credit_cards (customer_name, card_number, credit_limit, current_balance, due_date, rewards_points)
VALUES
 ('Alice Johnson','4111111111111111',5000,1234.56,'2025-12-05',3400),
 ('Bob Smith','4222222222222222',3000,2750.10,'2025-12-02',1200)
 ON CONFLICT(card_number) DO NOTHING;
INSERT INTO transactions (card_number, amount, merchant, ts) VALUES
 ('4111111111111111', 45.90, 'CoffeePlace', '2025-11-15T10:03:00'),
 ('4111111111111111', 199.00, 'ElectroShop', '2025-11-16T14:20:00'),
 ('4222222222222222', 15.25, 'GrocerySpot', '2025-11-16T09:05:00');
"""

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    for stmt in SCHEMA_SQL.strip().split(";"):
        if stmt.strip():
            cur.execute(stmt)
    for stmt in SEED_SQL.strip().split(";"):
        if stmt.strip():
            try:
                cur.execute(stmt)
            except Exception:
                pass
    conn.commit()
    conn.close()

init_db()

# --------- Gemini wrapper ----------
def gemini_chat(messages: List[Dict[str, str]]) -> str:
    """
    messages: [{"role":"user"/"system"/"assistant","content":"..."}]
    """
    model = genai.GenerativeModel(MODEL_NAME)
    # Consolidate into simple prompt (Gemini supports multi-turn if needed)
    prompt_parts = []
    for m in messages:
        role = m["role"]
        content = m["content"]
        prompt_parts.append(f"{role.upper()}:\n{content}\n")
    prompt = "\n".join(prompt_parts)
    resp = model.generate_content(prompt)
    return resp.text

# --------- Credit Card SQL Tool ----------
def run_credit_card_query(user_query: str) -> List[Dict[str, Any]]:
    """
    Very naive mapping: pick intent & run predefined SQL.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    q = user_query.lower()

    if "limit" in q:
        cur.execute("SELECT customer_name, card_number, credit_limit FROM credit_cards")
    elif "balance" in q or "due" in q:
        cur.execute("SELECT customer_name, card_number, current_balance, due_date FROM credit_cards")
    elif "reward" in q or "points" in q:
        cur.execute("SELECT customer_name, card_number, rewards_points FROM credit_cards")
    elif "transaction" in q or "spend" in q or "recent" in q:
        cur.execute("""SELECT card_number, amount, merchant, ts
                       FROM transactions
                       ORDER BY ts DESC LIMIT 5""")
    else:
        # fallback: show summary
        cur.execute("SELECT customer_name, card_number, current_balance, credit_limit FROM credit_cards")

    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows

credit_card_tool = Tool(
    name="credit_card_sql_tool",
    description="Executes predefined credit card related SQL queries over the card & transaction tables.",
    fn=run_credit_card_query
)

# --------- Simple Router Logic ----------
CREDIT_CARD_KEYWORDS = {"credit", "card", "limit", "balance", "due", "transaction", "reward", "points"}
FAQ_KEYWORDS = {"hours", "support", "contact", "help", "fee", "charges"}

def route_intent(user_text: str) -> str:
    lt = user_text.lower()
    if any(k in lt for k in CREDIT_CARD_KEYWORDS):
        return "credit_card"
    if any(k in lt for k in FAQ_KEYWORDS):
        return "faq"
    return "general"

# --------- Agent execution functions ----------
def credit_card_agent(user_text: str) -> str:
    sql_results = credit_card_tool.run(user_text)["results"]
    # Build context for LLM
    context_lines = ["SQL Results:"]
    for r in sql_results:
        context_lines.append(str(r))
    context = "\n".join(context_lines)
    messages = [
        {"role": "system", "content": "You are a banking assistant specializing in credit card queries. Be concise."},
        {"role": "user", "content": f"User question: {user_text}\nData:\n{context}\nCraft a helpful answer."}
    ]
    return gemini_chat(messages)

FAQ_SNIPPETS = [
    "Support hours: 9am-6pm Mon-Fri.",
    "Late payment fee: $25.",
    "International transaction fee: 2%.",
    "Lost card: Call 1-800-XXX-XXXX immediately."
]

def faq_agent(user_text: str) -> str:
    joined = "\n".join(FAQ_SNIPPETS)
    messages = [
        {"role": "system", "content": "You answer banking FAQs from provided snippets only."},
        {"role": "user", "content": f"Question: {user_text}\nFAQ Data:\n{joined}\nAnswer strictly from data."}
    ]
    return gemini_chat(messages)

def general_agent(user_text: str) -> str:
    messages = [
        {"role": "system", "content": "General banking virtual assistant. If unsure ask clarifying question."},
        {"role": "user", "content": user_text}
    ]
    return gemini_chat(messages)

# --------- Orchestrator (Multi-Agent) ----------
def run_multi_agent_chat(user_text: str) -> Dict[str, Any]:
    intent = route_intent(user_text)
    if intent == "credit_card":
        answer = credit_card_agent(user_text)
    elif intent == "faq":
        answer = faq_agent(user_text)
    else:
        answer = general_agent(user_text)

    return {
        "intent": intent,
        "answer": answer
    }

# --------- CLI Demo ----------
def main():
    print("Banking Multi-Agent Chat (Gemini) - Type 'exit' to quit.")
    while True:
        user_text = input("You: ").strip()
        if user_text.lower() in {"exit", "quit"}:
            break
        result = run_multi_agent_chat(user_text)
        print(f"[intent={result['intent']}] {result['answer']}\n")

if __name__ == "__main__":
    main()
# 