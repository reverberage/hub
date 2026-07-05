# Satellite Protocol

The contract every reverberage satellite follows.

## Build & Package

| Property | Requirement |
|----------|-------------|
| **Build backend** | `hatchling` |
| **Package naming** | `rvrb-<name>` (pip), `rvrb_<name>` (Python import) |
| **Python** | `>=3.11` |
| **License** | `Apache-2.0` |
| **CLI framework** | `typer` (never `argparse` directly) |
| **Data models** | `pydantic` v2 `BaseModel` |
| **Test runner** | `pytest` with `typer.testing.CliRunner` |
| **Linting** | `ruff check` |
| **Type checking** | `mypy .` |

## `pyproject.toml` entry points

```toml
[project.scripts]
rvrb-<name> = "rvrb_<name>.cli:main"
```

For MCP servers, add a second entry point:

```toml
[project.scripts]
rvrb-<name>-mcp = "rvrb_<name>.mcp:main"
```

## Module structure

```
src/rvrb_<name>/
    __init__.py          # Package metadata and version
    cli.py               # Typer app — CLI entry point
    models.py            # Pydantic v2 models
    <module>.py          # Core logic
tests/
    conftest.py           # Shared fixtures
    test_<module>.py      # pytest tests
pyproject.toml            # hatchling build config
```

## MCP integration

Satellites MAY expose an MCP stdio server via `mcp.server.FastMCP`.

- Tools registered via `@mcp.tool()` with typed parameters
- Resources registered via `@mcp.resource("uri://scheme")`
- Prompts registered via `@mcp.prompt()`
- Transport: `mcp.run(transport='stdio')`

Each satellite connects to any MCP-compatible agentic system.
No framework lock-in.

## Satellite design principles

- **Single responsibility**: each satellite does ONE thing. Audio in, text out. Claim in, verdict out.
- **Independently usable**: each satellite is `pip install`-able and works standalone.
- **Composable**: satellites can be chained into pipelines (transcriber → verify → transform).
- **No monolith**: no "must use the entire ecosystem" constraint.
