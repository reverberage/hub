---
description: No-op — hub has no typed Python code
agent: n3rverberage
subtask: true
---
This is a meta-repo with no typed Python code. No type checking needed.

The scaffold script (`.opencode/scripts/scaffold-satellite.py`) is the only Python file and has type hints but no test suite for type checking yet.

If a satellite needs type checking, run in that satellite's repo:
```
mypy .
```
