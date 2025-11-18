# Project Overview

This repository contains a small proof-of-concept project and diagrams used for design and documentation.

## Files of interest
- `main.py` — main script
- `list_models.py` — utility script
- `test_poc.py` — test / proof-of-concept
- `agent_diagram.dot` — Graphviz DOT diagram
- `agent_diagram.mmd` — Mermaid diagram
- `agent_diagram.txt` — Plain-text diagram / notes

## Diagrams
- agent_diagram.dot: A Graphviz DOT file. Render with Graphviz:

```bash
dot -Tpng agent_diagram.dot -o agent_diagram.png
```

- agent_diagram.mmd: A Mermaid diagram. Render locally with a Mermaid CLI or view in Mermaid live editor (https://mermaid.live).

## How to use
1. (Optional) Create a Python virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt  # if you have one
```

2. Run the main script:

```bash
python main.py
```

## Git: Initialize, commit, and push
This repository currently appears not to be initialized as a Git repo in this environment. To initialize, commit, and push changes:

1. Initialize and commit locally:

```bash
git init
git branch -M main
git add .
git commit -m "chore: add README and include diagrams"
```

2. If you already have a remote repository, add it and push:

```bash
git remote add origin <REMOTE_URL>
git push -u origin main
```

3. If you want me to create a GitHub repo and push for you (requires `gh` CLI and authentication), I can run:

```bash
gh repo create --public --source=. --remote=origin --push
```

Replace `--public` with `--private` if you prefer a private repo.

If you'd like me to proceed with adding a remote and pushing, reply with the remote URL or permission to create a GitHub repo using the `gh` CLI.

---
Generated README to include diagrams and usage instructions.
