# Python API

## Quick start

```python
from rvrb_hear import HearEngine, get_provider

provider = get_provider()
engine = HearEngine(provider=provider)
result = engine.hear("podcast.mp3")

print(result.analysis)
```

## `HearEngine` class

```python
class HearEngine:
    def __init__(self, provider: ModelProvider): ...
    
    def hear(
        self,
        audio: MediaInput | str,
        prompt: str | None = None,
    ) -> HearResult:
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `audio` | `MediaInput \| str` | required | Audio file path or MediaInput |
| `prompt` | `str \| None` | `None` | Custom analysis prompt |

### Returns

`HearResult` — Pydantic model with analysis result.

### Examples

```python
from rvrb_hear import HearEngine, get_provider

provider = get_provider()
engine = HearEngine(provider=provider)

# Basic analysis
result = engine.hear("podcast.mp3")

# Custom prompt
result = engine.hear("meeting.wav", prompt="What decisions were made?")

# With MediaInput
from rvrb_hear.models import MediaInput, MediaModality
from pathlib import Path

mi = MediaInput(
    path=Path("audio.mp3"),
    modality=MediaModality.AUDIO,
    metadata={"duration_seconds": 120.5}
)
result = engine.hear(mi)
```

## `HearResult` model

```python
class HearResult(BaseModel):
    analysis: str                  # The audio comprehension result
    model: str                     # Model ID used
    provider: str                  # Provider name (e.g., "qwen")
    prompt: str                    # The prompt used
    tokens_used: int | None        # Token count if available
```

### Example

```python
result = engine.hear("podcast.mp3", prompt="Summarize this audio")

print(f"Analysis: {result.analysis}")
print(f"Model: {result.model}")
print(f"Provider: {result.provider}")
print(f"Prompt: {result.prompt}")
print(f"Tokens: {result.tokens_used}")

# JSON serialization
import json
data = json.loads(result.model_dump_json())
print(json.dumps(data, indent=2))
```

## `MediaInput` model

```python
class MediaInput(BaseModel):
    path: Path                     # Path to audio file
    modality: MediaModality        # Must be MediaModality.AUDIO
    metadata: dict                 # Optional metadata (duration, format, etc.)
```

### Example

```python
from rvrb_hear.models import MediaInput, MediaModality
from pathlib import Path

mi = MediaInput(
    path=Path("audio.mp3"),
    modality=MediaModality.AUDIO,
    metadata={
        "duration_seconds": 120.5,
        "format": "mp3",
        "mime_type": "audio/mpeg"
    }
)
```

## `MediaOutput` model

```python
class MediaOutput(BaseModel):
    data: str | bytes              # Output data
    modality: MediaModality        # Default: TEXT
    format: str                    # Default: "text"
```

## I/O functions

### `read_media()`

```python
from rvrb_hear.io import read_media

mi = read_media(Path("audio.mp3"))
# Returns MediaInput with modality=AUDIO and metadata
```

### `write_media()`

```python
from rvrb_hear.io import write_media
from rvrb_hear.models import MediaOutput

output = MediaOutput(data="analysis text", format="text")
write_media(output, Path("output.txt"))
```

## Provider

```python
from rvrb_hear.provider import get_provider, DEFAULT_MODEL, DEFAULT_BASE_URL

# Get a provider
provider = get_provider(model="qwen3.5-omni-plus", provider="qwen")

# Defaults
print(DEFAULT_MODEL)     # "qwen3.5-omni-plus"
print(DEFAULT_BASE_URL)  # DashScope endpoint
```

## Pipeline composition

```python
from rvrb_transcriber import transcribe
from rvrb_hear import HearEngine, get_provider

# Transcribe audio
transcript = transcribe("meeting.mp3")

# Comprehend audio (deeper analysis)
engine = HearEngine(provider=get_provider())
result = engine.hear("meeting.mp3", prompt="What action items were assigned?")

# Combine results
print(f"Transcript: {transcript.text[:100]}...")
print(f"Analysis: {result.analysis}")
```
