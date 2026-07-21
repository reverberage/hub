# Models

Data models used by rvrb-hear.

## `HearResult`

The core output type for audio comprehension.

```python
class HearResult(BaseModel):
    analysis: str                  # The audio comprehension result
    model: str                     # Model ID used (e.g., "qwen3.5-omni-plus")
    provider: str                  # Provider name (e.g., "qwen", "openai")
    prompt: str                    # The prompt used (default: "")
    tokens_used: int | None        # Token count if available
```

### Fields

| Field | Type | Description |
|-------|------|-------------|
| `analysis` | `str` | The comprehension result text |
| `model` | `str` | Model ID used for analysis |
| `provider` | `str` | Provider name (not API key) |
| `prompt` | `str` | The prompt used (empty string if default) |
| `tokens_used` | `int \| None` | Token count if available from provider |

### Example

```python
result = HearResult(
    analysis="The speaker is explaining quantum computing concepts...",
    model="qwen3.5-omni-plus",
    provider="qwen",
    prompt="What is this audio about?",
    tokens_used=250
)
```

## `MediaModality`

Enum representing media types.

```python
from enum import StrEnum

class MediaModality(StrEnum):
    TEXT = "text"
    AUDIO = "audio"
    IMAGE = "image"
    VIDEO = "video"
```

### Values

| Value | String | Description |
|-------|--------|-------------|
| `TEXT` | `"text"` | Text content |
| `AUDIO` | `"audio"` | Audio content |
| `IMAGE` | `"image"` | Image content |
| `VIDEO` | `"video"` | Video content |

### Example

```python
from rvrb_hear.models import MediaModality

modality = MediaModality.AUDIO
print(modality)  # "audio"
print(modality.value)  # "audio"
```

## `MediaInput`

Represents input media (audio file).

```python
class MediaInput(BaseModel):
    path: Path                     # Path to media file
    modality: MediaModality        # Must be AUDIO for rvrb-hear
    metadata: dict                 # Optional metadata
```

### Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `path` | `Path` | required | Path to the media file |
| `modality` | `MediaModality` | required | Media type (AUDIO for rvrb-hear) |
| `metadata` | `dict` | `{}` | Provenance metadata |

### Metadata fields

Common metadata fields (populated by `read_media()`):

| Field | Type | Description |
|-------|------|-------------|
| `mime_type` | `str` | MIME type (e.g., "audio/mpeg") |
| `format` | `str` | Format name (e.g., "mp3") |
| `duration_seconds` | `float` | Audio duration |
| `sample_rate` | `int` | Sample rate in Hz |

### Example

```python
from rvrb_hear.models import MediaInput, MediaModality
from pathlib import Path

mi = MediaInput(
    path=Path("audio.mp3"),
    modality=MediaModality.AUDIO,
    metadata={
        "mime_type": "audio/mpeg",
        "format": "mp3",
        "duration_seconds": 120.5
    }
)
```

## `MediaOutput`

Represents output media.

```python
class MediaOutput(BaseModel):
    data: str | bytes              # Output data
    modality: MediaModality        # Default: TEXT
    format: str                    # Default: "text"
```

### Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `data` | `str \| bytes` | required | Output content |
| `modality` | `MediaModality` | `TEXT` | Output type |
| `format` | `str` | `"text"` | Format identifier |

### Example

```python
from rvrb_hear.models import MediaOutput, MediaModality

output = MediaOutput(
    data="Audio analysis result...",
    modality=MediaModality.TEXT,
    format="text"
)
```

## Provider types

### `ModelProvider` Protocol

```python
class ModelProvider(Protocol):
    model: str
    base_url: str
    
    def complete(self, messages: list[dict], **kwargs) -> str: ...
    def complete_structured(self, messages: list[dict], output_type: type, **kwargs) -> BaseModel: ...
    def complete_with_tools(self, messages: list[dict], tools: list[dict], **kwargs) -> ToolResult: ...
```

### `ToolCall`

```python
class ToolCall(BaseModel):
    id: str
    name: str
    arguments: dict
```

### `ToolResult`

```python
class ToolResult(BaseModel):
    content: str
    tool_calls: list[ToolCall]
```

### `ProviderError`

```python
class ProviderError(Exception):
    model: str
    status_code: int | None
    message: str
```

### `QuotaExhaustedError`

```python
class QuotaExhaustedError(ProviderError):
    pass
```

## Serialization

All models support Pydantic v2 serialization:

```python
# To dict
data = result.model_dump()

# To JSON string
json_str = result.model_dump_json()

# From dict
result = HearResult.model_validate(data)

# From JSON string
result = HearResult.model_validate_json(json_str)
```
