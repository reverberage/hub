# Architecture

Internal design of rvrb-see.

## Module structure

```
src/rvrb_see/
    __init__.py      # Public API, exports
    cli.py           # Typer CLI entry point
    engine.py        # SeeEngine.see(image, prompt) -> SeeResult
    models.py        # SeeResult, MediaModality, MediaInput, MediaOutput
    provider.py      # ModelProvider Protocol, get_provider(), DEFAULT_MODEL
    io.py            # read_media(), write_media(), MIME_MAP
    mcp.py           # MCP server (FastMCP)
```

## Data flow

```
CLI (cli.py)
  │
  ├── io.read_media(image_path) → MediaInput
  │     └── Detects format, MIME type from extension
  │
  ├── get_provider() → ModelProvider
  │     └── Resolves from env vars or n3rverberage
  │
  ├── SeeEngine(provider).see(MediaInput, prompt)
  │     │
  │     ├── Read image bytes from path
  │     ├── Base64 encode image
  │     ├── Build data URI: data:{mime_type};base64,{data}
  │     ├── Build multimodal message:
  │     │     {
  │     │       "role": "user",
  │     │       "content": [
  │     │         {
  │     │           "type": "image_url",
  │     │           "image_url": {"url": "data:image/png;base64,..."}
  │     │         },
  │     │         {
  │     │           "type": "text",
  │     │           "text": prompt or "Describe this image in detail."
  │     │         }
  │     │       ]
  │     │     }
  │     │
  │     ├── provider.complete(messages, temperature=0)
  │     │     └── POST /v1/chat/completions
  │     │
  │     └── Return SeeResult(description=..., model=..., provider=...)
  │
  └── Output: text or JSON
```

## Key classes

### `SeeEngine` (engine.py)

```python
class SeeEngine:
    def __init__(self, provider: ModelProvider):
        self.provider = provider
    
    def see(self, image: MediaInput | str, prompt: str | None = None) -> SeeResult:
        # 1. Resolve MediaInput from str if needed
        # 2. Read image bytes
        # 3. Base64 encode
        # 4. Build data URI
        # 5. Build multimodal message with image_url block
        # 6. Call provider.complete(temperature=0)
        # 7. Return SeeResult
```

### `SeeResult` (models.py)

```python
class SeeResult(BaseModel):
    description: str
    model: str
    provider: str
    prompt: str = ""
    tokens_used: int | None = None
```

### `ModelProvider` Protocol (provider.py)

```python
class ModelProvider(Protocol):
    model: str
    base_url: str
    
    def complete(self, messages: list[dict], **kwargs) -> str: ...
    def complete_structured(self, messages: list[dict], output_type: type, **kwargs) -> BaseModel: ...
    def complete_with_tools(self, messages: list[dict], tools: list[dict], **kwargs) -> ToolResult: ...
```

## Image encoding

Images are encoded as base64 data URIs in the `image_url` content block:

```python
import base64

image_bytes = Path("image.png").read_bytes()
image_b64 = base64.b64encode(image_bytes).decode("utf-8")
mime_type = "image/png"  # Detected from extension

data_uri = f"data:{mime_type};base64,{image_b64}"

message = {
    "role": "user",
    "content": [
        {
            "type": "image_url",
            "image_url": {"url": data_uri}
        },
        {
            "type": "text",
            "text": "Describe this image"
        }
    ]
}
```

## Temperature 0

The engine always uses `temperature=0` for deterministic output. This ensures consistent descriptions for the same image.

```python
response = self.provider.complete(messages, temperature=0)
```

## Error handling

| Layer | Error type | Handling |
|-------|-----------|----------|
| CLI | `FileNotFoundError` | Exit 1, message to stderr |
| CLI | `ValueError` (unsupported format) | Exit 1, message to stderr |
| CLI | Other exceptions | Exit 1, message to stderr |
| Engine | Provider errors | Exception propagates to caller |

## Dependencies

### Runtime

| Package | Purpose |
|---------|---------|
| `openai>=2.0.0` | OpenAI-compatible API client |
| `pydantic>=2.0` | Data models |
| `typer>=0.12` | CLI framework |

### Optional

| Package | Extra | Purpose |
|---------|-------|---------|
| `mcp` | `[mcp]` | MCP server (FastMCP) |

### No n3rverberage dependency

rvrb-see does NOT require n3rverberage at runtime. The `provider.py` module follows the satellite-protocol-v2 pattern with a fallback provider.

## Protocol compliance

rvrb-see follows [satellite-protocol-v2](https://github.com/reverberage/hub/blob/main/docs/satellite-protocol-v2.md):

- **Mandatory kernel**: `__init__.py`, `models.py`, `provider.py`, `engine.py` ✓
- **`io.py`**: Required for IMAGE modality ✓
- **CLI**: Typer-based with `--prompt`, `--json`, `--model`, `--provider`, `--output` ✓
- **MCP**: Gated import, `FastMCP`, stdio transport ✓
- **MockProvider**: In `tests/conftest.py` for offline testing ✓
