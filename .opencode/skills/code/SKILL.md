---
name: code
description: "Python language standards: type hints, error handling, logging, and style conventions."
compatibility: opencode
when_to_use: "When writing or reviewing *.py source files."
user-invocable: false
hub-skill-ids: [implementation, review, refactoring]
---

# Skill: Python — reverberage

## Rules

REJECT if:
- Missing type hints on public functions or methods
- Bare `except:` without a specific exception type
- `print()` used in production code (use `logging` instead)
- Mutable default arguments (e.g., `def f(x=[]):`)
- `try: ... except: pass` without at least logging

REQUIRE:
- `from __future__ import annotations` in all modules
- Type hints on all public functions and class attributes
- Pydantic v2 for data validation models
- Descriptive variable and function names

PREFER:
- Early returns over deeply nested conditionals
- `pathlib.Path` over `os.path` for filesystem operations
- Dataclasses or Pydantic over raw dicts for structured data

## reverberage Patterns

### Package Structure
```
src/<name>/
  __init__.py        — package metadata, version
  cli.py             — Typer app (CLI entry point)
  models.py          — Pydantic models
  <module>.py        — core logic
tests/
  conftest.py        — shared fixtures
  test_<module>.py   — pytest tests
pyproject.toml       — hatchling build config
```

### Pydantic v2 Models
- Use `BaseModel` with `model_validator` / `field_validator` for custom validation
- Serialize via `model_dump(mode='json')`, not `.dict()`
- Use `ConfigDict` for model config (frozen, extra, etc.)
- Use `Field(description=..., alias=...)` for schema metadata

### Typer CLI
- Use `typer.Typer()` with `@app.command()` decorators
- Use type hints for automatic argument parsing
- Use `typer.Option(help=..., prompt=True)` for required opts
- Use `typer.Argument(...)` for positional args
- Lazy import heavy dependencies inside commands, not at module level

### MCP Server (mcp SDK)
- Use `mcp.server.FastMCP` for MCP tool servers
- Register tools via `@mcp.tool()` decorator with typed parameters
- Resources via `@mcp.resource("uri://scheme")`
- Prompts via `@mcp.prompt()`
- Run with `mcp.run(transport='stdio')` for stdio transport
- Always document tool inputs/outputs in docstrings (MCP reads them)

### A2A Agent Registration
- Agents register with the N3RV hub via `n3rv_agent.register()`
- Each agent has: `id`, `name`, `skill_ids`, `description`
- Agent logic runs as a stateless function receiving a task dict
- Agent returns structured results with `status` and `output` keys


