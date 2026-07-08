# Satellite Protocol v2

The contract every reverberage satellite follows. v2 adds mandatory kernel structure, media I/O types,
provider resolution, and mock-ready engine contracts. All v1 build/package requirements carry forward unchanged.

## 1. Build & Package (carried from v1)

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

### Entry points (`pyproject.toml`)

```toml
[project.scripts]
rvrb-<name> = "rvrb_<name>.cli:main"
rvrb-<name>-mcp = "rvrb_<name>.mcp:main"
```

## 2. Module Structure

### Mandatory Kernel (every satellite, every modality)

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
    io.py                # REQUIRED when MediaModality is not TEXT-only. read_media + write_media.
    cli.py               # Typer app. Standard --json and --model flags.
    mcp.py               # MCP server. Gated import (mcp is optional).
```

A text-only satellite (e.g., `transform`) may omit `io.py`. A library-only satellite (no CLI) may omit `cli.py`.
All other combinations are valid. The mandatory kernel is always present.

## 3. Data Models (`models.py`)

### MediaModality

```python
from enum import StrEnum

class MediaModality(StrEnum):
    TEXT = "text"
    AUDIO = "audio"
    IMAGE = "image"
    VIDEO = "video"
```

Every satellite must define this enum, even if it only uses `TEXT`.

### MediaInput

```python
from pathlib import Path
from pydantic import BaseModel

class MediaInput(BaseModel):
    path: Path
    modality: MediaModality
    metadata: dict = {}
    # metadata carries provenance: duration_seconds, width, height, language, sample_rate, etc.
    # The producing satellite populates it. The consuming satellite extends it.
```

### MediaOutput

```python
class MediaOutput(BaseModel):
    data: str | bytes
    modality: MediaModality = MediaModality.TEXT
    format: str = "text"  # json, srt, vtt, wav, mp3, png, mp4, etc.
```

For text-only satellites, `modality` is always `TEXT` and `data` is always `str`. The engine's public method may accept
`MediaInput | str` — a plain string is equivalent to `MediaInput(path=Path(), modality=TEXT, metadata={})`.

## 4. Provider Contract (`provider.py`)

### ModelProvider Protocol

```python
from typing import Protocol

class ModelProvider(Protocol):
    model: str
    base_url: str

    def complete(self, messages: list[dict], **kwargs) -> str: ...
    def complete_structured(self, messages: list[dict], output_type: type, **kwargs) -> BaseModel: ...
    def complete_with_tools(self, messages: list[dict], tools: list[dict], **kwargs) -> ToolResult: ...
```

This is a **structural** Protocol — any object with these attributes and methods is a valid provider.
No ABC inheritance. No `isinstance` checks. Satellites accept whatever matches the shape.

### Required Exports

Every satellite's `provider.py` must expose:

| Export | Type | Purpose |
|--------|------|---------|
| `ModelProvider` | `Protocol` | Type hint for engine constructor |
| `DEFAULT_MODEL` | `str` | e.g., `"qwen3-coder-plus"` |
| `DEFAULT_BASE_URL` | `str` | e.g., `"https://dashscope-intl.aliyuncs.com/compatible-mode/v1"` |
| `get_provider(model)` | `(str|None) -> ModelProvider` | Provider factory |

### get_provider() Resolution

```python
def get_provider(model_override: str | None = None) -> ModelProvider:
    """
    1. Try: from n3rverberage.providers import get_provider as n3rv_get_provider
            return n3rv_get_provider(name)   # reads N3RVERBERAGE_PROVIDER env var
    2. Fallback: openai.OpenAI(base_url=DEFAULT_BASE_URL, api_key=os.environ["DASHSCOPE_API_KEY"])
                 wrapped in an object matching ModelProvider Protocol
    """
```

The fallback exists so satellites remain independently `pip install`-able without requiring `n3rverberage`.
If `n3rverberage` IS installed, its provider chain (including fallback and quota detection) is used.

## 5. Engine Contract (`engine.py`)

### Pattern

```python
class <Satellite>Engine:
    def __init__(self, provider: ModelProvider):
        self.provider = provider

    def <action>(self, input: MediaInput | str, **options) -> MediaOutput | BaseModel:
        ...
```

### Rules

1. **Constructor injection**: the engine receives its provider at construction time. Never resolves it internally.
2. **Single public method**: named after the satellite's action (`transcribe`, `verify`, `transform`, `see`, `hear`, `speak`).
3. **Mock-ready**: the constructor parameter is typed as `ModelProvider` Protocol. Pass a `MockProvider` in tests.
4. **No side effects**: the engine does not write files, call `print`, or modify global state. I/O happens in `io.py` and `cli.py`.
5. **Error propagation**: provider errors (quota exhaustion, network failure) bubble up as raised exceptions. The engine wraps them with context (phase name, model_id) but does not silently swallow them.

## 6. I/O Contract (`io.py`)

Required only when the satellite handles non-text modalities. If the satellite's `MediaModality` usage is `TEXT`-only,
`io.py` may be omitted.

### Required Exports

```python
from pathlib import Path
from .models import MediaInput, MediaOutput

def read_media(path: Path) -> MediaInput:
    """
    Read a media file, detect format and modality, return MediaInput.
    Raises ValueError if format unsupported.
    Raises FileNotFoundError if path missing.
    """

def write_media(output: MediaOutput, path: Path) -> None:
    """
    Write MediaOutput to a file. Chooses binary/text mode based on modality.
    Writes to stdout if path is None.
    """
```

### Format Detection (internal, not exported)

`read_media()` should detect format from file extension or magic bytes. Common mappings:

| Extension | Modality | Format |
|-----------|----------|--------|
| .mp3, .wav, .flac, .m4a, .ogg | AUDIO | audio/mpeg, audio/wav, ... |
| .png, .jpg, .jpeg, .gif, .webp | IMAGE | image/png, image/jpeg, ... |
| .mp4, .webm, .mov | VIDEO | video/mp4, video/webm, ... |
| .txt, .md, .json, .csv | TEXT | text/plain, text/markdown, ... |

## 7. CLI Contract (`cli.py`)

### Standard Pattern

```python
import typer
from pathlib import Path

app = typer.Typer()

@app.command()
def main(
    input_path: Path = typer.Argument(..., help="Input file or directory"),
    output: Path | None = typer.Option(None, "--output", "-o", help="Write output to file (default: stdout)"),
    json: bool = typer.Option(False, "--json", help="Output as JSON"),
    model: str | None = typer.Option(None, "--model", "-m", help="Override model (e.g., qwen:qwen3-coder-plus)"),
) -> None:
    """<Satellite description>"""
```

### Required Flags

| Flag | Required | Purpose |
|------|:--------:|---------|
| `--json` | Yes | Structured output (JSON) instead of human-readable |
| `--model` / `-m` | Yes | Override provider model |
| `--output` / `-o` | Yes | Write to file instead of stdout |

### Exit Codes

| Code | Meaning |
|:----:|---------|
| 0 | Success |
| 1 | Error (validation, provider, I/O) |

## 8. MCP Contract (`mcp.py`)

### Gated Import

```python
try:
    from mcp.server import FastMCP
except ImportError:
    raise ImportError(
        "MCP support requires the 'mcp' extra. Install with: pip install rvrb-<name>[mcp]"
    )
```

### Tool Registration

```python
mcp = FastMCP("rvrb-<name>")

@mcp.tool()
def <action>(input_text: str, **options) -> dict:
    """<Action description>"""
    # Construct engine, resolve provider, call action, return dict
    ...

def main():
    mcp.run(transport="stdio")
```

MCP tools must accept JSON-serializable types (str, int, float, bool, list, dict). They may not accept
`Path` or `BaseModel` — the MCP client can't construct those. Wrap the engine call: convert `str` to
`MediaInput(text=...)` internally.

## 9. Testing Contract

### MockProvider Pattern

Every satellite's test suite must include a `MockProvider` that implements the `ModelProvider` Protocol.
This enables engine testing with zero network calls.

```python
# tests/conftest.py or tests/test_engine.py
from rvrb_<name>.provider import ModelProvider

class MockProvider:
    def __init__(self, model: str = "mock", base_url: str = "mock://"):
        self.model = model
        self.base_url = base_url

    def complete(self, messages, **kwargs) -> str:
        return "mock response"

    def complete_structured(self, messages, output_type, **kwargs):
        # Return a valid instance of output_type with mock data
        return output_type(...)

    def complete_with_tools(self, messages, tools, **kwargs):
        # Return ToolResult with appropriate mock content
        return ToolResult(content="mock tool result", tool_calls=[])
```

`MockProvider` IS a `ModelProvider` by structure — no inheritance needed. This proves the Protocol works.

### Test Isolation

- Engine tests use `MockProvider` — never real providers
- CLI tests use `typer.testing.CliRunner` — never real subprocess calls
- I/O tests use `tmp_path` fixture — never real filesystem paths
- All tests pass with `--offline` (no network)

## 10. Composition

Satellites compose into pipelines via their I/O contracts. Each satellite's `MediaOutput` feeds into
the next satellite's `MediaInput`. The `metadata` dict carries provenance through the chain.

### Multimodal Pipeline Example

```
transcriber          verify              transform
 ┌─────────┐        ┌─────────┐         ┌──────────┐
 │ audio→  │ text   │ text→   │ text    │ text→    │
 │  text   ├────────► verdict ├─────────► formatted │
 │         │        │         │         │   text    │
 └─────────┘        └─────────┘         └──────────┘
  io.read_media()    engine.verify()     engine.transform()
  MediaInput(AUDIO)  Claim(TEXT)         formatted text
  Transcript(TEXT)   Verdict(TEXT)       MediaOutput(TEXT)
  MediaOutput(TEXT)
```

### Text-Only Pipeline

```
transform            verify
 ┌──────────┐       ┌─────────┐
 │ text→    │ text  │ text→   │
 │  text    ├───────► verdict  │
 │          │       │         │
 └──────────┘       └─────────┘
  (no io.py)         engine.verify()
```

Each satellite is independently `pip install`-able. Pipelines are consumer concerns — the protocol
defines the I/O contract, not the orchestration.

## 11. Migration Guide (v1 → v2)

Existing satellites (transcriber, verify) are **alpha** — breaking changes are permitted. To migrate a v1 satellite to v2:

### Step-by-step

1. **Add `provider.py`**: Extract provider resolution from wherever it lives (CLI, engine, `__init__.py`)
   into `provider.py` with the standard `get_provider()` function and `ModelProvider` Protocol.
   If the satellite already has a `_default_provider` module, merge it.

2. **Add `models.py` types**: Add `MediaModality`, `MediaInput`, `MediaOutput` to `models.py`.
   For transcriber: `modality=AUDIO` for input, `modality=TEXT` for output.
   For verify: `modality=TEXT` for both (or omit `io.py` entirely since it's text-only).

3. **Restructure layout**: Ensure mandatory kernel modules exist (`__init__.py`, `models.py`, `provider.py`,
   `engine.py`). Move existing logic into these modules if necessary.

4. **Add `io.py` if multimodal**: Transcriber needs it (reads audio files). Verify does not (text-only).

5. **Update CLI**: Add `--json` and `--model` flags if missing. Ensure exit codes are 0/1.

6. **Add MockProvider to tests**: Replace any `MagicMock` patterns with the standard `MockProvider`. Verify
   engine tests pass without network.

7. **Update `pyproject.toml`**: Add MCP entry point if not present. Verify `rvrb-<name>-mcp` works.

### Checklist

- [ ] `provider.py` exists with `ModelProvider`, `DEFAULT_MODEL`, `get_provider()`
- [ ] `models.py` has `MediaModality`, `MediaInput`, `MediaOutput`
- [ ] Mandatory kernel modules present: `__init__.py`, `models.py`, `provider.py`, `engine.py`
- [ ] `io.py` present if modality != TEXT
- [ ] CLI has `--json` and `--model` flags
- [ ] Exit codes: 0 for success, 1 for error
- [ ] `MockProvider` in tests, no real providers in engine tests
- [ ] MCP entry point in `pyproject.toml`
- [ ] `ruff check` passes, `mypy .` passes, `pytest` passes zero network
