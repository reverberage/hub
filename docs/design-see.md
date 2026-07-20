# SDD Design: see

**Change ID**: `see` | **Phase**: 4 — Design | **Date**: 2026-07-19

---

## 1. Component Architecture

```
rvrb-see/                          ← satelite root (new GitHub repo)
├── pyproject.toml                 ← hatchling build, entry points, deps
├── README.md                      ← basic usage docs
├── src/
│   └── rvrb_see/                  ← Python package
│       ├── __init__.py            ← version, exports
│       ├── models.py              ← SeeResult, MediaModality, MediaInput, MediaOutput, provider types
│       ├── provider.py            ← ModelProvider Protocol, DEFAULT_MODEL, DEFAULT_BASE_URL, get_provider()
│       ├── engine.py              ← SeeEngine(provider).see(image, prompt) -> SeeResult
│       ├── io.py                  ← read_media(path) -> MediaInput, write_media(output, path) -> None
│       ├── cli.py                 ← Typer CLI: rvrb-see <image> [--json] [--model] [--prompt] ...
│       └── mcp.py                 ← FastMCP server: rvrb-see-mcp (gated import)
└── tests/
    ├── __init__.py                ← empty
    ├── conftest.py                ← MockProvider (structural, no inheritance)
    ├── test_engine.py             ← SeeEngine tests with SpyProvider/MockProvider
    ├── test_cli.py                ← CLI tests with CliRunner
    ├── test_io.py                 ← I/O tests with tmp_path
    ├── test_models.py             ← domain model validation
    └── test_provider.py           ← provider resolution tests
```

## 2. Data Structures

### SeeResult (in models.py)

```python
class SeeResult(BaseModel):
    description: str                # The image description/analysis
    model: str = ""                 # Model ID used
    provider: str = ""              # Provider name used
    prompt: str = ""                # The prompt used, if any
    tokens_used: int | None = None  # Token count if available
```

### Provider Interface Types (in models.py)

Same as transform: `ToolCall`, `ToolResult`, `ProviderError`, `QuotaExhaustedError`. These are provider-agnostic — no Qwen-specific types.

## 3. Interface Specifications

### 3.1 SeeEngine (engine.py)

```python
class SeeEngine:
    def __init__(self, provider: ModelProvider):
        self.provider = provider

    def see(
        self,
        image: MediaInput | str,
        prompt: str | None = None,
    ) -> SeeResult:
        """
        Analyze an image using the vision model.

        Parameters
        ----------
        image : MediaInput | str
            MediaInput with path to image, or string path.
        prompt : str | None
            Custom prompt. Default: "Describe this image in detail."

        Returns
        -------
        SeeResult
            Structured result with description, model info, and token usage.
        """
```

**Implementation flow:**

1. Resolve `MediaInput` from `str` if needed
2. Read image bytes, detect mime type from file extension
3. Base64-encode image bytes
4. Construct multimodal message:
   ```python
   messages = [
       {"role": "system", "content": "You are an image analysis engine..."},
       {"role": "user", "content": [
           {"type": "image_url", "image_url": {"url": "data:image/png;base64,..."}},
           {"type": "text", "text": prompt or "Describe this image in detail."},
       ]},
   ]
   ```
5. Call `self.provider.complete(messages, temperature=0)`
6. Return `SeeResult(description=response, model=self.provider.model, provider=..., tokens_used=...)`

### 3.2 io.py

```python
MIME_MAP = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".gif": "image/gif",
    ".webp": "image/webp",
}

def read_media(path: Path) -> MediaInput:
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    ext = path.suffix.lower()
    if ext not in MIME_MAP:
        raise ValueError(f"Unsupported image format: {ext}. Supported: {', '.join(MIME_MAP)}")
    return MediaInput(
        path=path,
        modality=MediaModality.IMAGE,
        metadata={"mime_type": MIME_MAP[ext]},
    )

def write_media(output: MediaOutput, path: Path) -> None:
    mode = "wb" if isinstance(output.data, bytes) else "w"
    with open(path, mode) as f:
        f.write(output.data)  # type: ignore[arg-type]
```

### 3.3 Provider Contract (provider.py)

Same as `rvrb-transform/provider.py` — exact copy from the transform satellite, with one change:

- `DEFAULT_MODEL` defaults to `"qwen3.7-plus"` (vision-capable) instead of `"qwen3-coder-plus"`
- The `_PROVIDER_FALLBACKS` map stays identical (same provider types, the vision model is resolved via env var)

### 3.4 CLI (cli.py)

```python
@app.command()
def see_command(
    image_path: Path = typer.Argument(..., help="Path to image file"),
    prompt: str = typer.Option("", "--prompt", "-p", help="Custom analysis prompt"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    model: str | None = typer.Option(None, "--model", "-m", help="Override model ID"),
    provider: str | None = typer.Option(None, "--provider", help="Provider name"),
    output: Path | None = typer.Option(None, "--output", "-o", help="Write to file"),
) -> None:
```

Flow:
1. Validate image path exists
2. Resolve provider via `get_provider(model=model, provider=provider)`
3. Create engine, call `engine.see(image_path, prompt=prompt)`
4. Output: plain text or JSON
5. Exit 0 on success, 1 on error

### 3.5 MCP (mcp.py)

```python
@mcp.tool()
def see(image_path: str, prompt: str = "") -> dict:
    """Analyze an image using a vision model."""
    # Read file, create engine, call see, return dict
```

MCP tool cannot accept `Path` — uses `str` for `image_path`.

### 3.6 pyproject.toml Dependencies

```toml
dependencies = [
    "openai>=2.0.0",
    "pydantic>=2.0",
    "typer>=0.12",
]
```

No `n3rverberage` in hard deps. `mcp` in optional deps. Same as transform.

## 4. Data Flow

```
CLI: rvrb-see photo.png --json
  │
  ├── io.read_media(photo.png) → MediaInput(modality=IMAGE, metadata={"mime_type":"image/png"})
  │
  ├── get_provider() → ModelProvider (QwenProvider or _GenericProvider)
  │
  ├── SeeEngine(provider).see(MediaInput, prompt=None)
  │     │
  │     ├── Read image bytes from path
  │     ├── Base64 encode
  │     ├── Build multimodal message with image_url data URI
  │     ├── provider.complete(messages, temperature=0)
  │     │     └── POST /v1/chat/completions to LLM API
  │     └── Return SeeResult(description=..., model=..., provider=...)
  │
  ├── Serialize: text to stdout, or SeeResult.model_dump_json() for --json
  │
  └── Exit 0
```

## 5. Error Handling

| Condition | Detection | Response | Exit Code |
|-----------|-----------|----------|:---------:|
| Image file not found | `path.exists()` check | "Error: File not found: {path}" | 1 |
| Unsupported image format | Extension not in MIME_MAP | "Error: Unsupported image format: {ext}" | 1 |
| API key not set | `get_provider()` raises ValueError | "Error: DASHSCOPE_API_KEY is not set" | 1 |
| Provider API error | `provider.complete()` raises | "Error: [model] HTTP {code}: {msg}" | 1 |
| Network timeout | Provider exception | "Error: [model] Connection timed out" | 1 |

## 6. Edge Cases

| Edge Case | Behavior |
|-----------|----------|
| Empty image (0 bytes) | Read succeeds (bytes are valid), LLM returns "empty image" description |
| Very large image (16MB+) | Base64 encoding succeeds, may hit token limit. LLM handles it gracefully (2048 image limit) |
| Unreadable file (permissions) | `IOError` → caught, reported with path |
| Symlink to image | Resolved by `Path.read_bytes()` — works transparently |
| Image with no extension | Falls through to ValueError "Unsupported format" |
| Non-image with image extension | Valid PNG header check could be added, but YAGNI for v1 |

## 7. Implementation Files Summary

| File | Action | Lines | Purpose |
|------|--------|:-----:|---------|
| `pyproject.toml` | CREATE | ~55 | hatchling build, entry points, deps |
| `README.md` | CREATE | ~30 | Basic usage |
| `src/rvrb_see/__init__.py` | CREATE | ~20 | Version, exports |
| `src/rvrb_see/models.py` | CREATE | ~100 | SeeResult, MediaModality, MediaInput, MediaOutput, provider types |
| `src/rvrb_see/provider.py` | CREATE | ~300 | ModelProvider Protocol, get_provider(), _GenericProvider |
| `src/rvrb_see/engine.py` | CREATE | ~80 | SeeEngine with image encoding logic |
| `src/rvrb_see/io.py` | CREATE | ~60 | read_media (image), write_media (text) |
| `src/rvrb_see/cli.py` | CREATE | ~110 | Typer CLI |
| `src/rvrb_see/mcp.py` | CREATE | ~75 | FastMCP server |
| `tests/__init__.py` | CREATE | 0 | Empty |
| `tests/conftest.py` | CREATE | ~36 | MockProvider |
| `tests/test_engine.py` | CREATE | ~120 | Engine tests |
| `tests/test_cli.py` | CREATE | ~60 | CLI tests |
| `tests/test_io.py` | CREATE | ~80 | I/O tests |
| `tests/test_models.py` | CREATE | ~80 | Model tests |
| `tests/test_provider.py` | CREATE | ~70 | Provider resolution tests |

## 8. Open Questions

1. **GitHub repo**: Should be `reverberage/see` — but the user hasn't said to create it there. I'll scaffold in the workspace parent dir as `rvrb-see/`.

2. **Model default**: The spec says `qwen3.7-plus` for vision. The `_PROVIDER_FALLBACKS` map uses `"qwen"` type defaults. The DEFAULT_MODEL env var overrides this. Qwen3.7-plus snapshot `qwen3.7-plus-2026-05-26` has 1M tokens free quota.
