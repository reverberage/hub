# Architecture

Internal design of rvrb-hear.

## Module structure

```
src/rvrb_hear/
    __init__.py      # Public API, exports
    cli.py           # Typer CLI entry point
    engine.py        # HearEngine.hear(audio, prompt) -> HearResult
    models.py        # HearResult, MediaModality, MediaInput, MediaOutput
    provider.py      # ModelProvider Protocol, get_provider(), DEFAULT_MODEL
    io.py            # read_media(), write_media(), MIME_MAP
    mcp.py           # MCP server (FastMCP)
```

## Data flow

```
CLI (cli.py)
  │
  ├── io.read_media(audio_path) → MediaInput
  │     └── Detects format, MIME type from extension
  │
  ├── get_provider() → ModelProvider
  │     └── Resolves from env vars or n3rverberage
  │
  ├── HearEngine(provider).hear(MediaInput, prompt)
  │     │
  │     ├── Read audio bytes from path
  │     ├── Base64 encode audio
  │     ├── Build multimodal message:
  │     │     {
  │     │       "role": "user",
  │     │       "content": [
  │     │         {
  │     │           "type": "input_audio",
  │     │           "input_audio": {
  │     │             "data": "<BASE64_AUDIO>",
  │     │             "format": "mp3"
  │     │           }
  │     │         },
  │     │         {
  │     │           "type": "text",
  │     │           "text": prompt or "Analyze this audio in detail."
  │     │         }
  │     │       ]
  │     │     }
  │     │
  │     ├── provider.complete(messages, temperature=0, stream=True, modalities=["text"])
  │     │     └── POST /v1/chat/completions with stream=True
  │     │     └── Internally accumulates SSE chunks
  │     │     └── Returns synchronous str
  │     │
  │     └── Return HearResult(analysis=..., model=..., provider=...)
  │
  └── Output: text or JSON
```

## Key classes

### `HearEngine` (engine.py)

```python
class HearEngine:
    def __init__(self, provider: ModelProvider):
        self.provider = provider
    
    def hear(self, audio: MediaInput | str, prompt: str | None = None) -> HearResult:
        # 1. Resolve MediaInput from str if needed
        # 2. Read audio bytes
        # 3. Base64 encode
        # 4. Build multimodal message with input_audio block
        # 5. Call provider.complete(stream=True, modalities=["text"])
        # 6. Return HearResult
```

### `HearResult` (models.py)

```python
class HearResult(BaseModel):
    analysis: str
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

## Audio encoding

Audio is encoded as base64 in the `input_audio` content block:

```python
import base64

audio_bytes = Path("audio.mp3").read_bytes()
audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")

message = {
    "role": "user",
    "content": [
        {
            "type": "input_audio",
            "input_audio": {
                "data": audio_b64,
                "format": "mp3"
            }
        },
        {
            "type": "text",
            "text": "Analyze this audio"
        }
    ]
}
```

## Streaming handling

The qwen3.5-omni-plus model requires `stream=True`. The `_GenericProvider.complete()` method handles this internally:

```python
def complete(self, messages, **kwargs):
    stream = kwargs.pop("stream", False)
    
    response = self._client().chat.completions.create(
        model=self.model,
        messages=messages,
        stream=stream,
        **kwargs
    )
    
    if stream:
        # Accumulate SSE chunks
        content_parts = []
        for chunk in response:
            delta = chunk.choices[0].delta if chunk.choices else None
            if delta and delta.content:
                content_parts.append(delta.content)
        return "".join(content_parts)
    else:
        return response.choices[0].message.content or ""
```

The Protocol signature is unchanged — `complete()` always returns `str`.

## `modalities=["text"]`

Always set to prevent the omni model from generating TTS audio output in parallel with text response. This saves tokens and bandwidth.

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

rvrb-hear does NOT require n3rverberage at runtime. The `provider.py` module follows the satellite-protocol-v2 pattern with a fallback provider.

## Protocol compliance

rvrb-hear follows [satellite-protocol-v2](https://github.com/reverberage/hub/blob/main/docs/satellite-protocol-v2.md):

- **Mandatory kernel**: `__init__.py`, `models.py`, `provider.py`, `engine.py` ✓
- **`io.py`**: Required for AUDIO modality ✓
- **CLI**: Typer-based with `--prompt`, `--json`, `--model`, `--provider`, `--output` ✓
- **MCP**: Gated import, `FastMCP`, stdio transport ✓
- **MockProvider**: In `tests/conftest.py` for offline testing ✓
