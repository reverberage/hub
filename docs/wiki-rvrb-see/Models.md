# Models

Data models used by rvrb-see.

## `SeeResult`

The core output type for image understanding.

```python
class SeeResult(BaseModel):
    description: str             # The image description/analysis
    model: str                   # Model ID used (e.g., "qwen3.7-plus")
    provider: str                # Provider name (e.g., "qwen", "openai")
    prompt: str                  # The prompt used (default: "")
    tokens_used: int | None      # Token count if available
```

### Fields

| Field | Type | Description |
|-------|------|-------------|
| `description` | `str` | The image description text |
| `model` | `str` | Model ID used for analysis |
| `provider` | `str` | Provider name (not API key) |
| `prompt` | `str` | The prompt used (empty string if default) |
| `tokens_used` | `int \| None` | Token count if available from provider |

### Example

```python
result = SeeResult(
    description="A cat sitting on a chair",
    model="qwen3.7-plus",
    provider="qwen",
    prompt="Describe this image",
    tokens_used=150
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
from rvrb_see.models import MediaModality

modality = MediaModality.IMAGE
print(modality)  # "image"
print(modality.value)  # "image"
```

## `MediaInput`

Represents input media (image file).

```python
class MediaInput(BaseModel):
    path: Path                     # Path to media file
    modality: MediaModality        # Must be IMAGE for rvrb-see
    metadata: dict                 # Optional metadata
```

### Fields

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `path` | `Path` | required | Path to the media file |
| `modality` | `MediaModality` | required | Media type (IMAGE for rvrb-see) |
| `metadata` | `dict` | `{}` | Provenance metadata |

### Metadata fields

Common metadata fields (populated by `read_media()`):

| Field | Type | Description |
|-------|------|-------------|
| `mime_type` | `str` | MIME type (e.g., "image/png") |
| `width` | `int` | Image width in pixels |
| `height` | `int` | Image height in pixels |

### Example

```python
from rvrb_see.models import MediaInput, MediaModality
from pathlib import Path

mi = MediaInput(
    path=Path("image.png"),
    modality=MediaModality.IMAGE,
    metadata={
        "mime_type": "image/png",
        "width": 1920,
        "height": 1080
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
from rvrb_see.models import MediaOutput, MediaModality

output = MediaOutput(
    data="Image description...",
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
result = SeeResult.model_validate(data)

# From JSON string
result = SeeResult.model_validate_json(json_str)
```
