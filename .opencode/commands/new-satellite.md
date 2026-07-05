---
description: Scaffold a new reverberage satellite package
agent: n3rverberage
subtask: true
---

Generate a new reverberage satellite directory with boilerplate: pyproject.toml (hatchling),
Typer CLI, pytest tests, and README.

Scaffold script: `.opencode/scripts/scaffold-satellite.py`

The satellite is created as a sibling directory to the hub repo (e.g., `../<name>/`).

Usage: `/new-satellite <name>`

Rules for `<name>`:
- lowercase letters, digits, hyphens, underscores only
- Must start with a letter
- Examples: `verify`, `scout`, `cli-to-mcp`

After scaffolding:
1. `cd ../<name>`
2. `pip install -e ".[dev]"`
3. `pytest` — tests should pass
4. Create `reverberage/<name>` repo on GitHub and push

Execute: `!python3 .opencode/scripts/scaffold-satellite.py <name>`
