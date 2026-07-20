# SDD Design: hear

**Change ID**: `hear` | **Phase**: 4 — Design | **Date**: 2026-07-19

---

## 1. Component Architecture

```
rvrb-hear/                          ← satellite root (new package in workspace parent)
├── pyproject.toml                  ← hatchling build, entry points, deps
├── README.md                       ← basic usage docs
├── src/
│   └── rvrb_hear/                  ← Python package
│       ├── __init__.py             ← version, exports
│       ├── models.py               ← HearResult, MediaModality, MediaInput, MediaOutput, provider types
│       ├── provider.py             ← ModelProvider Protocol, DEFAULT_MODEL, DEFAULT_BASE_URL, get_provider()
│       ├── engine.py               ← HearEngine(provider).hear(audio, prompt) -> HearResult
│       ├── io.py                   ← read_media(path) -> MediaInput, write_media(output, path) -> None
│       ├── cli.py                  ← Typer CLI: rvrb-hear <audio> [--json] [--model] [--prompt] ...
│       └── mcp.py                  ← FastMCP server: rvrb-hear-mcp (gated import)
└── tests/
    ├── __init__.py                 ← empty
    ├── conftest.py                 ← MockProvider (structural, no inheritance)
    ├── test_engine.py              ← HearEngine tests with SpyProvider/MockProvider
    ├── test_cli.py                 ← CLI tests with CliRunner
    ├── test_io.py                  ← I/O tests with tmp_path
    ├── test_models.py              ← domain model validation
    └── test_provider.py            ← provider resolution tests
```

## 2. Data Structures

### HearResult (in models.py)

```python
class HearResult(BaseModel):
    analysis: str                  # The audio comprehension result
    model: str = ""                # Model ID used
    provider: str = ""             # Provider name used (e.g., "qwen", "openai") — NOT API key
    prompt: str = ""               # The prompt used, if any
    tokens_used: int | None = None # Token count if available
```

### Provider Interface Types (in models.py)

Same as rvrb-see: `ToolCall`, `ToolResult`, `ProviderError`, `QuotaExhaustedError`. Provider-agnostic — no Qwen-specific types.

## 3. Interface Specifications

### 3.1 HearEngine (engine.py)

```python
class HearEngine:
    def __init__(self, provider: ModelProvider):
        self.provider = provider

    def hear(
        self,
        audio: MediaInput | str,
        prompt: str | None = None,
    ) -> HearResult:
        """
        Analyze an audio file using the omni model.

        Parameters
        ----------
        audio : MediaInput | str
            MediaInput with path to audio, or string path.
        prompt : str | None
            Custom prompt. Default: "Analyze this audio in detail."

        Returns
        -------
        HearResult
            Structured result with analysis, model info, and token usage.
        """
```

**Implementation flow:**

1. Resolve `MediaInput` from `str` if needed
2. Read audio bytes from path
3. Detect format and MIME type from file extension (via io.py metadata)
4. Base64-encode audio bytes
5. Construct multimodal message:
   ```python
   messages = [
       {"role": "system", "content": "You are an audio analysis engine..."},
       {"role": "user", "content": [
           {"type": "input_audio", "input_audio": {
               "data": "<BASE64_ENCODED_AUDIO>",
               "format": "wav"
           }},
           {"type": "text", "text": prompt or "Analyze this audio in detail."},
       ]},
   ]
   ```
6. Call `self.provider.complete(messages, temperature=0, stream=True, modalities=["text"])`
   - `stream=True` is MANDATORY for qwen3.5-omni-plus
   - `modalities=["text"]` prevents TTS audio output
   - The provider handles SSE chunk accumulation internally
7. Return `HearResult(analysis=response, model=self.provider.model, provider=..., tokens_used=...)`
   - Provider field uses `self.provider.model` or a provider name string — NEVER `_api_key`

### 3.2 io.py

```python
MIME_MAP: dict[str, str] = {
    ".wav": "audio/wav",
    ".mp3": "audio/mpeg",
    ".aac": "audio/aac",
    ".flac": "audio/flac",
    ".m4a": "audio/mp4",
    ".ogg": "audio/ogg",
    ".amr": "audio/amr",
}

def read_media(path: Path) -> MediaInput:
    """Read an audio file and return a MediaInput."""
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    ext = path.suffix.lower()
    if ext not in MIME_MAP:
        supported = ", ".join(MIME_MAP)
        raise ValueError(f"Unsupported audio format: '{ext}'. Supported: {supported}")
    format_name = ext.lstrip(".")
    return MediaInput(
        path=path,
        modality=MediaModality.AUDIO,
        metadata={"mime_type": MIME_MAP[ext], "format": format_name},
    )

def write_media(output: MediaOutput, path: Path) -> None:
    """Write text output to a file."""
    if isinstance(output.data, str):
        path.write_text(output.data, encoding="utf-8")
    else:
        path.write_bytes(output.data)
```

### 3.3 Provider Contract (provider.py)

Copied from rvrb-see's `provider.py` with one change:

- `DEFAULT_MODEL` defaults to `"qwen3.5-omni-plus"` (audio-capable) instead of `"qwen3.7-plus"`
- `_PROVIDER_FALLBACKS` map: qwen → `qwen3.5-omni-plus`/DashScope/DASHSCOPE_API_KEY, openai → `gpt-4o`/OpenAI/OPENAI_API_KEY, local → `llama3`/localhost/empty
- `_GenericProvider.complete()` handles `stream=True` kwarg by accumulating SSE chunks and returning the concatenated text as `str`

**Streaming handling in _GenericProvider.complete():**

```python
def complete(self, messages, **kwargs):
    stream = kwargs.pop("stream", False)
    max_tokens = kwargs.pop("max_tokens", 4096)
    try:
        response = self._client().chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=max_tokens,
            stream=stream,
            **kwargs,
        )
    except Exception as exc:
        raise _wrap_error(self.model, exc) from exc

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

This is the only change to `_GenericProvider` from the rvrb-see version.

### 3.4 CLI (cli.py)

```python
@app.command()
def hear_command(
    audio_path: Path = typer.Argument(..., help="Path to audio file"),
    prompt: str = typer.Option("", "--prompt", "-p", help="Custom analysis prompt"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
    model: str | None = typer.Option(None, "--model", "-m", help="Override model ID"),
    provider: str | None = typer.Option(None, "--provider", help="Provider name"),
    output: Path | None = typer.Option(None, "--output", "-o", help="Write to file"),
) -> None:
```

Flow:
1. Validate audio path exists
2. Resolve provider via `get_provider(model=model, provider=provider)`
3. Create engine, call `engine.hear(audio_path, prompt=prompt)`
4. Output: plain text or JSON
5. Exit 0 on success, 1 on error

### 3.5 MCP (mcp.py)

```python
@mcp.tool()
def hear(audio_path: str, prompt: str = "") -> dict:
    """Analyze an audio file using the omni model."""
```

MCP tool uses `str` for `audio_path` (MCP client can't construct `Path`).

### 3.6 pyproject.toml Dependencies

```toml
dependencies = [
    "openai>=2.0.0",
    "pydantic>=2.0",
    "typer>=0.12",
]
```

No `n3rverberage` in hard deps. `mcp` in optional deps: `["mcp>=1.0.0"]`.

## 4. Data Flow

```
CLI: rvrb-hear audio.wav --json
  │
  ├── io.read_media(audio.wav) → MediaInput(modality=AUDIO, metadata={"mime_type":"audio/wav", "format":"wav"})
  │
  ├── get_provider() → ModelProvider (QwenProvider or _GenericProvider)
  │
  ├── HearEngine(provider).hear(MediaInput, prompt=None)
  │     │
  │     ├── Read audio bytes from path
  │     ├── Base64 encode
  │     ├── Build multimodal message with input_audio content block
  │     ├── provider.complete(messages, temperature=0, stream=True, modalities=["text"])
  │     │     └── POST /v1/chat/completions with stream=True to LLM API
  │     │         └── Provider internally accumulates SSE chunks
  │     └── Return HearResult(analysis=..., model=..., provider=...)
  │
  ├── Serialize: text to stdout, or HearResult.model_dump_json() for --json
  │
  └── Exit 0
```

## 5. Error Handling

| Condition | Detection | Response | Exit Code |
|-----------|-----------|----------|:---------:|
| Audio file not found | `path.exists()` check | "Error: File not found: {path}" | 1 |
| Unsupported audio format | Extension not in MIME_MAP | "Error: Unsupported audio format: {ext}" | 1 |
| API key not set | `get_provider()` raises ValueError | "Error: DASHSCOPE_API_KEY is not set" | 1 |
| Provider API error | `provider.complete()` raises | "Error: [model] HTTP {code}: {msg}" | 1 |
| Network timeout | Provider exception | "Error: [model] Connection timed out" | 1 |
| Audio >10MB raw bytes | Base64 size check | YAGNI for v1 — let API reject it | 1 |

## 6. Edge Cases

| Edge Case | Behavior |
|-----------|----------|
| Empty audio (0 bytes) | Read succeeds (bytes are valid), LLM returns analysis (likely "no audio content") |
| Very large audio (>10MB raw) | Base64 encoding may succeed, API may reject. V1 does no pre-flight size check. |
| Unreadable file (permissions) | `IOError` → caught, reported with path |
| Symlink to audio | Resolved by `Path.read_bytes()` — works transparently |
| Audio with no extension | Falls through to ValueError "Unsupported format" |
| Very long audio (>3 hours) | API enforces 3-hour limit. Error message from provider. |
| Non-audio with audio extension | API accepts but returns an error or empty analysis |

## 7. Implementation Files Summary

| File | Action | Lines | Purpose |
|------|--------|:-----:|---------|
| `pyproject.toml` | CREATE | ~55 | hatchling build, entry points, deps |
| `README.md` | CREATE | ~30 | Basic usage |
| `src/rvrb_hear/__init__.py` | CREATE | ~20 | Version, exports |
| `src/rvrb_hear/models.py` | CREATE | ~85 | HearResult, MediaModality, MediaInput, MediaOutput, provider types |
| `src/rvrb_hear/provider.py` | CREATE | ~310 | ModelProvider Protocol, get_provider(), _GenericProvider with stream handling |
| `src/rvrb_hear/engine.py` | CREATE | ~90 | HearEngine with audio encoding logic |
| `src/rvrb_hear/io.py` | CREATE | ~75 | read_media (audio), write_media (text), 7 audio formats |
| `src/rvrb_hear/cli.py` | CREATE | ~110 | Typer CLI |
| `src/rvrb_hear/mcp.py` | CREATE | ~75 | FastMCP server |
| `tests/__init__.py` | CREATE | 0 | Empty |
| `tests/conftest.py` | CREATE | ~36 | MockProvider |
| `tests/test_engine.py` | CREATE | ~140 | Engine tests |
| `tests/test_cli.py` | CREATE | ~70 | CLI tests |
| `tests/test_io.py` | CREATE | ~85 | I/O tests |
| `tests/test_models.py` | CREATE | ~85 | Model tests |
| `tests/test_provider.py` | CREATE | ~75 | Provider resolution tests |

## 8. Open Questions

1. **GitHub repo**: Should be `reverberage/hear` — but user hasn't mentioned it. Scaffold in workspace parent as `rvrb-hear/`.

2. **Streaming in n3rverberage's QwenProvider**: When n3rverberage IS installed, its `QwenProvider.complete()` must handle `stream=True` kwarg. If it doesn't, the call may fail. The `_GenericProvider` fallback handles it correctly. This is a constraint documented in the spec.

3. **Audio format restrictions**: The qwen3.5-omni-plus API supports fewer audio formats than our MIME_MAP lists. Unsupported formats will fail at API call time with a descriptive error. V1 does not do pre-flight format validation beyond extension check.
