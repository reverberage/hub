# Python API

## Quick start

```python
from rvrb_transcriber import transcribe

result = transcribe("interview.mp3")
print(result.text)
```

## `transcribe()` function

```python
def transcribe(
    file_path: str,
    engine: str = "openai",
    language: str | None = None,
    model: str | None = None,
    api_key: str | None = None,
) -> Transcript:
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `file_path` | `str` | required | Path to audio/video file |
| `engine` | `str` | `"openai"` | `"openai"` (API) or `"local"` (local Whisper) |
| `language` | `str \| None` | `None` | Language code hint (`"en"`, `"es"`, etc.) |
| `model` | `str \| None` | `None` | Model override (engine-specific) |
| `api_key` | `str \| None` | `None` | OpenAI API key. Falls back to `OPENAI_API_KEY` env var. |

### Returns

`Transcript` — Pydantic model with full transcription result.

### Raises

- `FileNotFoundError` — file does not exist
- `ValueError` — unknown engine, missing API key, or invalid parameters

### Examples

```python
# Basic
result = transcribe("meeting.mp3")

# With language hint
result = transcribe("spanish.wav", language="es")

# Local engine
result = transcribe("podcast.wav", engine="local")

# Local with larger model
result = transcribe("podcast.wav", engine="local", model="medium")

# Explicit API key
result = transcribe("audio.mp3", api_key="sk-...")
```

## `Transcript` model

```python
class Transcript(BaseModel):
    text: str                    # Full transcribed text
    segments: list[Segment]      # Timed segments
    language: str                # Detected language code
    duration_seconds: float      # Audio duration in seconds
```

### Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `to_srt()` | `str` | Export as SubRip subtitle format |
| `to_vtt()` | `str` | Export as WebVTT subtitle format |
| `model_dump()` | `dict` | Pydantic serialization to dict |
| `model_dump_json()` | `str` | Pydantic serialization to JSON string |

### Example

```python
result = transcribe("interview.mp3")

# Full text
print(result.text)

# Language detected
print(f"Language: {result.language}")

# Duration
print(f"Duration: {result.duration_seconds:.1f}s")

# Number of segments
print(f"Segments: {len(result.segments)}")

# SRT output
with open("subtitles.srt", "w") as f:
    f.write(result.to_srt())

# VTT output
with open("subtitles.vtt", "w") as f:
    f.write(result.to_vtt())

# JSON serialization
import json
data = json.loads(result.model_dump_json())
print(json.dumps(data, indent=2))
```

## `Segment` model

```python
class Segment(BaseModel):
    start: float    # Start time in seconds
    end: float      # End time in seconds
    text: str       # Transcribed text for this segment
```

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `duration` | `float` | `end - start` in seconds |
| `start_timedelta` | `timedelta` | Start time as `datetime.timedelta` |
| `end_timedelta` | `timedelta` | End time as `datetime.timedelta` |

### Example

```python
result = transcribe("meeting.wav")

for seg in result.segments:
    mins = int(seg.start // 60)
    secs = seg.start % 60
    print(f"[{mins:02d}:{secs:05.2f}] {seg.text}")
    print(f"  Duration: {seg.duration:.1f}s")
```

## Engine classes

### `OpenAIWhisperEngine`

```python
from rvrb_transcriber.engine import OpenAIWhisperEngine

engine = OpenAIWhisperEngine(api_key="sk-...", model="whisper-1")
result = engine.transcribe("audio.mp3", language="en")
```

### `LocalWhisperEngine`

```python
from rvrb_transcriber.engine import LocalWhisperEngine

engine = LocalWhisperEngine(model="base")
result = engine.transcribe("audio.mp3", language="en")
```

## Provider (for future use)

```python
from rvrb_transcriber.provider import get_provider, DEFAULT_MODEL, DEFAULT_BASE_URL

# Get a provider (reserved for future multimodal features)
provider = get_provider(model="qwen3.5-omni-plus", provider="qwen")

# Defaults
print(DEFAULT_MODEL)     # "qwen3.5-omni-plus"
print(DEFAULT_BASE_URL)  # DashScope endpoint
```

> **Note**: The `ModelProvider` Protocol is defined but currently unused by the transcriber engine. It's reserved for future multimodal audio understanding features.

## Pipeline composition

```python
from rvrb_transcriber import transcribe

# Transcribe → process
result = transcribe("meeting.mp3")

# Filter segments by duration
long_segments = [s for s in result.segments if s.duration > 5.0]

# Get text only
full_text = result.text

# Export for video editing
with open("timeline.srt", "w") as f:
    f.write(result.to_srt())
```
