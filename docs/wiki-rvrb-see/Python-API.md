# Python API

## Quick start

```python
from rvrb_see import SeeEngine, get_provider

provider = get_provider()
engine = SeeEngine(provider=provider)
result = engine.see("photo.png")

print(result.description)
```

## `SeeEngine` class

```python
class SeeEngine:
    def __init__(self, provider: ModelProvider): ...
    
    def see(
        self,
        image: MediaInput | str,
        prompt: str | None = None,
    ) -> SeeResult:
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `image` | `MediaInput \| str` | required | Image file path or MediaInput |
| `prompt` | `str \| None` | `None` | Custom analysis prompt |

### Returns

`SeeResult` — Pydantic model with analysis result.

### Examples

```python
from rvrb_see import SeeEngine, get_provider

provider = get_provider()
engine = SeeEngine(provider=provider)

# Basic analysis
result = engine.see("photo.png")

# Custom prompt
result = engine.see("screenshot.png", prompt="What text is in this image?")

# With MediaInput
from rvrb_see.models import MediaInput, MediaModality
from pathlib import Path

mi = MediaInput(
    path=Path("image.png"),
    modality=MediaModality.IMAGE,
    metadata={"mime_type": "image/png"}
)
result = engine.see(mi)
```

## `SeeResult` model

```python
class SeeResult(BaseModel):
    description: str             # The image description
    model: str                   # Model ID used
    provider: str                # Provider name (e.g., "qwen")
    prompt: str                  # The prompt used
    tokens_used: int | None      # Token count if available
```

### Example

```python
result = engine.see("photo.png", prompt="Describe this image")

print(f"Description: {result.description}")
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
    path: Path                     # Path to image file
    modality: MediaModality        # Must be MediaModality.IMAGE
    metadata: dict                 # Optional metadata
```

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
from rvrb_see.io import read_media

mi = read_media(Path("image.png"))
# Returns MediaInput with modality=IMAGE and metadata
```

### `write_media()`

```python
from rvrb_see.io import write_media
from rvrb_see.models import MediaOutput

output = MediaOutput(data="image description", format="text")
write_media(output, Path("output.txt"))
```

## Provider

```python
from rvrb_see.provider import get_provider, DEFAULT_MODEL, DEFAULT_BASE_URL

# Get a provider
provider = get_provider(model="qwen3.7-plus", provider="qwen")

# Defaults
print(DEFAULT_MODEL)     # "qwen3.7-plus"
print(DEFAULT_BASE_URL)  # DashScope endpoint
```

## Pipeline composition

```python
from rvrb_see import SeeEngine, get_provider
from rvrb_verify import verify

# Analyze image
engine = SeeEngine(provider=get_provider())
result = engine.see("chart.png")

# Verify claims from description
verdict = verify(result.description)

print(f"Description: {result.description}")
print(f"Verification: {verdict.verdict.value} ({verdict.confidence:.1%})")
```
