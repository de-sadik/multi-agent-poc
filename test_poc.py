#!/usr/bin/env python3
"""
Simple test harness for the POC that stubs out the `google.generativeai`
client so you can run a deterministic offline test of the multi-agent flow.

Usage:
  python test_poc.py

This script:
 - Injects a stub `genai` with a `GenerativeModel` that returns a predictable
   `.text` value from `generate_content`.
 - Sets `main.MODEL_NAME` to a test value.
 - Calls `run_multi_agent_chat` with a query that should route to the
   `credit_card` agent.
 - Prints and asserts basic expectations about the result.
"""
from types import SimpleNamespace
import main


class StubModel:
    def __init__(self, name):
        self.name = name

    def generate_content(self, prompt):
        # Return a SimpleNamespace mimicking SDK response object with .text
        return SimpleNamespace(text=f"STUBBED_RESPONSE (model={self.name}) | prompt_len={len(prompt)}")


class StubGenai:
    GenerativeModel = StubModel

    @staticmethod
    def configure(api_key=None):
        # noop for tests
        return None


def run_stubbed_flow():
    # Inject our stub module into the main module
    main.genai = StubGenai
    main.MODEL_NAME = "models/test-stub"

    query = "What is my credit limit?"
    result = main.run_multi_agent_chat(query)

    print("--- Test Run Output ---")
    print("Query:", query)
    print("Result:", result)

    # Basic assertions to catch regressions
    assert isinstance(result, dict), "Result should be a dict"
    assert "intent" in result and "answer" in result, "Result must contain intent and answer"
    assert result["intent"] == "credit_card", f"Expected intent 'credit_card', got {result['intent']}"
    assert result["answer"].startswith("STUBBED_RESPONSE"), "Answer should come from stub model"

    print("\nTest passed: stubbed POC flow behaved as expected.")


if __name__ == "__main__":
    run_stubbed_flow()
