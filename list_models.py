"""
Small helper to list available Generative AI models and their supported methods.

Usage:
  - Set environment variable `GEMINI_API_KEY` to your API key, or export it in the shell.
  - Run: `python list_models.py`

This script tries `genai.list_models()` and prints a readable summary. If that method isn't available
in your installed `google.generativeai` version, it prints available attributes on the module so you
can inspect the SDK.
"""
import os
import sys

try:
    import google.generativeai as genai
except Exception as e:
    print("Failed to import google.generativeai:", e)
    sys.exit(1)

API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    print("Environment variable GEMINI_API_KEY is not set. Please set it and re-run.")
    print("Example: export GEMINI_API_KEY=\"YOUR_KEY\" && python list_models.py")
    sys.exit(1)

try:
    genai.configure(api_key=API_KEY)
except Exception as e:
    print("genai.configure() raised:", e)

print("Attempting to list models via SDK...")

try:
    # Preferred simple call (works with many genai versions)
    models = genai.list_models()
    print("Models returned by genai.list_models():")
    for m in models:
        # models may be list of dicts or objects depending on SDK
        try:
            name = m.get("name") if isinstance(m, dict) else getattr(m, "name", str(m))
            supported = m.get("supportedMethods") if isinstance(m, dict) else getattr(m, "supportedMethods", None)
        except Exception:
            name = str(m)
            supported = None
        print(f" - {name}")
        if supported:
            print(f"    supportedMethods: {supported}")
except Exception as e:
    print("genai.list_models() failed:", e)
    print("Falling back to inspecting module attributes for possible listing functions...")
    print("genai module attributes:")
    print(sorted([a for a in dir(genai) if not a.startswith('_')]))
    print("\nIf your SDK lacks list_models(), consider using the Vertex AI REST API or `gcloud ai models list`.")

print('\nDone.')
