# Architecture

Internal design of rvrb-transcriber. For users — no need to read this unless contributing or debugging.

## Module structure

```
src/rvrb_transcriber/
    __init__.py      # Public API, transcribe() function
    cli.py           # Typer CLI entry point
    engine.py        # Transcription engines (OpenAI, Local)
    models.py        # Pydantic models (Transcript, Segment)
    provider.py      # ModelProvider Protocol (reserved for future)
    mcp.py           # MCP server (FastMCP)
```

## Data flow

```
CLI (cli.py)
  │
  ├── transcribe() function (__init__.py)
  │     │
  │     ├── Validates file exists
  │     ├── Resolves engine (openai/local)
  │     ├── Creates engine instance
  │     └── Calls engine.transcribe()
  │           │
  │           ├── OpenAIWhisperEngine
  │           │     └── openai.Audio.transcriptions.create()
  │           │
  │           └── LocalWhisperEngine
  │                 └── whisper.load_model().transcribe()
  │
  └── Returns Transcript
        │
        ├── result.text        → plain text
        ├── result.to_srt()    → SRT subtitles
        ├── result.to_vtt()    → WebVTT subtitles
        └── result.model_dump() → JSON dict
```

## Key classes

### `Transcript` (models.py)

Pydantic v2 model. The core output type.

```python
class Transcript(BaseModel):
    text: str
    segments: list[Segment]
    language: str
    duration_seconds: float
```

Methods: `to_srt()`, `to_vtt()`, `model_dump()`, `model_dump_json()`

### `Segment` (models.py)

Individual timed segment.

```python
class Segment(BaseModel):
    start: float    # seconds
    end: float      # seconds
    text: str
```

Properties: `duration`, `start_timedelta`, `end_timedelta`

### `TranscriptionEngine` (engine.py)

Base class. Not abstract — just raises `NotImplementedError`.

```python
class TranscriptionEngine:
    def transcribe(self, file_path, language=None) -> Transcript:
        raise NotImplementedError
```

### `OpenAIWhisperEngine` (engine.py)

Calls OpenAI's Whisper API.

```python
class OpenAIWhisperEngine(TranscriptionEngine):
    def __init__(self, api_key, model="whisper-1"): ...
    def transcribe(self, file_path, language=None) -> Transcript: ...
```

Internal flow:
1. Creates `openai.OpenAI` client
2. Calls `client.audio.transcriptions.create()` with `response_format="verbose_json"`
3. Parses response segments into `Segment` objects
4. Returns `Transcript`

### `LocalWhisperEngine` (engine.py)

Runs Whisper locally via `openai-whisper` package.

```python
class LocalWhisperEngine(TranscriptionEngine):
    def __init__(self, model="base"): ...
    def transcribe(self, file_path, language=None) -> Transcript: ...
```

Internal flow:
1. Lazy-loads `whisper.load_model()` on first call
2. Calls `model.transcribe()` with file path
3. Parses segments from Whisper's output format
4. Returns `Transcript`

### `ModelProvider` Protocol (provider.py)

Reserved for future multimodal features. Not used by current transcription engines.

```python
class ModelProvider(Protocol):
    model: str
    base_url: str
    def complete(self, messages, **kwargs) -> str: ...
    def complete_structured(self, messages, output_type, **kwargs) -> BaseModel: ...
    def complete_with_tools(self, messages, tools, **kwargs) -> Any: ...
```

## SRT time formatting

```python
def _format_srt_time(td: timedelta) -> str:
    # Input: timedelta object
    # Output: "HH:MM:SS,mmm" (comma before milliseconds)
    # Example: timedelta(seconds=65.5) → "00:01:05,500"
```

## VTT time formatting

```python
def _format_vtt_time(td: timedelta) -> str:
    # Input: timedelta object
    # Output: "HH:MM:SS.mmm" (dot before milliseconds)
    # Example: timedelta(seconds=65.5) → "00:01:05.500"
```

Key difference from SRT: dot (`.`) instead of comma (`,`) before milliseconds.

## Error handling

| Layer | Error type | Handling |
|-------|-----------|----------|
| CLI | `FileNotFoundError` | Exit 1, message to stderr |
| CLI | `ValueError` | Exit 1, message to stderr |
| CLI | Other exceptions | Exit 2, message to stderr |
| Engine | API errors | Exception propagates to caller |
| Engine | Missing API key | `ValueError` raised before API call |

## Dependencies

### Runtime

| Package | Purpose |
|---------|---------|
| `pydantic>=2.0` | Data models (Transcript, Segment) |
| `typer>=0.9` | CLI framework |

### Optional

| Package | Extra | Purpose |
|---------|-------|---------|
| `openai>=1` | `[openai]` | OpenAI Whisper API client |
| `openai-whisper` | `[local]` | Local Whisper model |
| `mcp` | `[mcp]` | MCP server (FastMCP) |

### No n3rverberage dependency

rvrb-transcriber does NOT require n3rverberage at runtime. The `provider.py` module follows the satellite-protocol-v2 pattern with a fallback provider, but the current engine uses Whisper directly. The `ModelProvider` Protocol is defined for future multimodal features.

## Protocol compliance

rvrb-transcriber follows [satellite-protocol-v2](https://github.com/reverberage/hub/blob/main/docs/satellite-protocol-v2.md):

- **Mandatory kernel**: `__init__.py`, `models.py`, `provider.py`, `engine.py` ✓
- **No `io.py`**: Audio I/O is handled by the engine directly (Whisper API accepts file paths)
- **CLI**: Typer-based with `--format`, `--output`, `--engine`, `--model`, `--provider` ✓
- **MCP**: Gated import, `FastMCP`, stdio transport ✓
- **MockProvider**: In `tests/conftest.py` for offline testing ✓
