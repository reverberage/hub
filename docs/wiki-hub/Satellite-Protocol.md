# Satellite Protocol

The contract every reverberage satellite follows. v2 adds mandatory kernel structure, media I/O types, provider resolution, and mock-ready engine contracts.

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

## Module Structure

### Mandatory Kernel (every satellite)

```
src/rvrb_<name>/
    __init__.py          # Package metadata, version, public API re-exports
    models.py            # Pydantic v2 models: domain types + MediaInput + MediaOutput
    provider.py          # ModelProvider Protocol + get_provider() factory
    engine.py            # <Satellite>Engine with constructor-injected provider
```

### Optional Modules

```
src/rvrb_<name>/
    io.py                # REQUIRED when MediaModality is not TEXT-only
    cli.py               # Typer app. Standard --json and --model flags.
    mcp.py               # MCP server. Gated import (mcp is optional).
```

## Data Models

### MediaModality

```python
from enum import StrEnum

class MediaModality(StrEnum):
    TEXT = "text"
    AUDIO = "audio"
    IMAGE = "image"
    VIDEO = "video"
```

### MediaInput

```python
class MediaInput(BaseModel):
    path: Path
    modality: MediaModality
    metadata: dict = {}
```

### MediaOutput

```python
class MediaOutput(BaseModel):
    data: str | bytes
    modality: MediaModality = MediaModality.TEXT
    format: str = "text"
```

## Provider Contract

### ModelProvider Protocol

```python
class ModelProvider(Protocol):
    model: str
    base_url: str

    def complete(self, messages: list[dict], **kwargs) -> str: ...
    def complete_structured(self, messages: list[dict], output_type: type, **kwargs) -> BaseModel: ...
    def complete_with_tools(self, messages: list[dict], tools: list[dict], **kwargs) -> ToolResult: ...
```

### Required Exports

Every satellite's `provider.py` must expose:

| Export | Type | Purpose |
|--------|------|---------|
| `ModelProvider` | `Protocol` | Type hint for engine constructor |
| `DEFAULT_MODEL` | `str` | From `N3RVERBERAGE_DEFAULT_MODEL` env var |
| `DEFAULT_BASE_URL` | `str` | From `N3RVERBERAGE_DEFAULT_BASE_URL` env var |
| `get_provider(model, provider)` | Factory | Provider resolution |

### Environment Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `N3RVERBERAGE_PROVIDER` | `qwen` | Provider name |
| `N3RVERBERAGE_DEFAULT_MODEL` | `qwen3-coder-plus` | Default model ID |
| `N3RVERBERAGE_DEFAULT_BASE_URL` | DashScope URL | Default base URL |

## Engine Contract

```python
class <Satellite>Engine:
    def __init__(self, provider: ModelProvider):
        self.provider = provider

    def <action>(self, input: MediaInput | str, **options) -> MediaOutput | BaseModel:
        ...
```

### Rules

1. **Constructor injection**: provider received at construction time
2. **Single public method**: named after the satellite's action
3. **Mock-ready**: typed as `ModelProvider` Protocol
4. **No side effects**: no file writes, no print, no global state
5. **Error propagation**: provider errors bubble up with context

## CLI Contract

```python
@app.command()
def main(
    input_path: Path = typer.Argument(...),
    output: Path | None = typer.Option(None, "--output", "-o"),
    json: bool = typer.Option(False, "--json"),
    model: str | None = typer.Option(None, "--model", "-m"),
    provider: str | None = typer.Option(None, "--provider"),
) -> None:
```

### Required Flags

| Flag | Required | Purpose |
|------|:--------:|---------|
| `--json` | Yes | Structured output |
| `--model` / `-m` | Yes | Override model |
| `--provider` | No | Override provider |
| `--output` / `-o` | Yes | Write to file |

## MCP Contract

```python
try:
    from mcp.server import FastMCP
except ImportError:
    raise ImportError("pip install rvrb-<name>[mcp]")

mcp = FastMCP("rvrb-<name>")

@mcp.tool()
def <action>(input_text: str, **options) -> dict:
    ...

def main():
    mcp.run(transport="stdio")
```

## Testing Contract

### MockProvider

```python
class MockProvider:
    def __init__(self, model="mock", base_url="mock://"):
        self.model = model
        self.base_url = base_url

    def complete(self, messages, **kwargs) -> str:
        return "mock response"

    def complete_structured(self, messages, output_type, **kwargs):
        return output_type(...)

    def complete_with_tools(self, messages, tools, **kwargs):
        return ToolResult(...)
```

### Test Isolation

- Engine tests use `MockProvider` — never real providers
- CLI tests use `typer.testing.CliRunner` — never real subprocess
- I/O tests use `tmp_path` fixture — never real filesystem
- All tests pass with `--offline`

## Full specification

See [satellite-protocol-v2.md](https://github.com/reverberage/hub/blob/main/docs/satellite-protocol-v2.md) for the complete specification.
