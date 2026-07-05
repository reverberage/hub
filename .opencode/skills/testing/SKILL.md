---
name: testing
description: "pytest testing standards: naming, fixtures, isolation, and parametrize patterns."
compatibility: opencode
when_to_use: "When writing or reviewing test files in tests/ or matching *test*.py."
user-invocable: false
hub-skill-ids: [review]
---

# Skill: Testing — reverberage

## Framework

pytest — `python -m pytest` or `pytest`

## Rules

REQUIRE:
- Tests for all public functions and behavior changes
- Descriptive test names: `test_<subject>_<condition>_<expected_outcome>`
- Use `tmp_path` fixture for filesystem-touching tests
- Isolated tests: no shared mutable state between tests

REJECT if:
- Tests call external services without mocking
- Empty test body
- Tests depend on execution order

PREFER:
- `pytest.mark.parametrize` over repeated similar test functions
- Factory fixtures over inline setup in each test
- `conftest.py` for shared fixtures within a package

## Satellite Testing Patterns

### CLI Testing (Typer CliRunner)
```python
from typer.testing import CliRunner
from src.<satellite>.cli import app

runner = CliRunner()

def test_cli_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Usage" in result.output
```

### MCP Server Testing
- Test each `@mcp.tool()` function directly by calling it with typed args
- Mock external services (APIs, databases) with `unittest.mock` or `pytest-monkeypatch`
- Test error paths: invalid input, timeout, service unavailable

### Fixture Isolation
- Use `conftest.py` at package root for shared fixtures
- Use `scope="function"` by default (fresh state per test)
- Use `scope="session"` only for truly immutable resources (config, schema)

## Run

```bash
pytest
```



