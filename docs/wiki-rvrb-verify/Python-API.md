# Python API

## Quick start

```python
from rvrb_verify import verify

verdict = verify("The sky is blue")
print(f"Verdict: {verdict.verdict.value}")
print(f"Confidence: {verdict.confidence:.1%}")
```

## `verify()` function

```python
def verify(
    claim_text: str,
    strategy: str = "fact-check",
    *,
    model: str | None = None,
    provider: str | None = None,
    search_provider: ModelProvider | None = None,
    judge_provider: ModelProvider | None = None,
    tool_gateway: ToolGateway | None = None,
) -> Verdict:
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `claim_text` | `str` | required | The claim to verify |
| `strategy` | `str` | `"fact-check"` | Strategy name from `list_strategies()` |
| `model` | `str \| None` | `None` | Override model ID for both phases |
| `provider` | `str \| None` | `None` | Provider name (qwen, openai, local) |
| `search_provider` | `ModelProvider \| None` | `None` | Provider for search phase |
| `judge_provider` | `ModelProvider \| None` | `None` | Provider for judge phase |
| `tool_gateway` | `ToolGateway \| None` | `None` | Tool executor (default: MockToolGateway) |

### Returns

`Verdict` — Pydantic model with verification result.

### Raises

- `ValueError` — unknown strategy or invalid parameters

### Examples

```python
# Basic
verdict = verify("The sky is blue")

# With strategy
verdict = verify("Water boils at 100°C", strategy="fact-check")

# With model override
verdict = verify("Claim", model="qwen3-coder-plus")

# With provider override
verdict = verify("Claim", provider="openai")

# Custom providers for each phase
from rvrb_verify import get_provider
search = get_provider(model="qwen3-coder-plus")
judge = get_provider(model="qwen3.7-plus")
verdict = verify("Claim", search_provider=search, judge_provider=judge)
```

## `Verdict` model

```python
class Verdict(BaseModel):
    verdict: VerdictValue          # true, false, partially_true, inconclusive
    confidence: float              # 0.0 to 1.0
    summary: str                   # Human-readable summary
    evidence: list[Evidence]       # Supporting evidence
    sources: list[Source]          # Source references
    model: str                     # Model used
    provider: str                  # Provider name
    tokens_used: int | None        # Token count if available
```

### Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `model_dump()` | `dict` | Pydantic serialization to dict |
| `model_dump_json()` | `str` | Pydantic serialization to JSON string |

### Example

```python
verdict = verify("The sky is blue")

print(f"Verdict: {verdict.verdict.value}")
print(f"Confidence: {verdict.confidence:.1%}")
print(f"Summary: {verdict.summary}")
print(f"Evidence count: {len(verdict.evidence)}")
print(f"Sources: {len(verdict.sources)}")

# JSON serialization
import json
data = json.loads(verdict.model_dump_json())
print(json.dumps(data, indent=2))
```

## `Evidence` model

```python
class Evidence(BaseModel):
    text: str                      # Evidence text
    source: Source | None          # Source reference
    relevance: float | None        # Relevance score (0.0-1.0)
```

## `Source` model

```python
class Source(BaseModel):
    type: str                      # "web", "news", "paper", "statute", "case_law"
    url: str | None                # Source URL
    title: str | None              # Source title
    metadata: dict                 # Additional metadata
```

## Engine classes

### `VerificationEngine`

```python
from rvrb_verify.engine import VerificationEngine

engine = VerificationEngine(
    search_provider=get_provider(model="qwen3-coder-plus"),
    judge_provider=get_provider(model="qwen3.7-plus"),
)
verdict = engine.verify("The sky is blue", strategy="fact-check")
```

## Provider

```python
from rvrb_verify.provider import get_provider, DEFAULT_MODEL, DEFAULT_BASE_URL

# Get a provider
provider = get_provider(model="qwen3-coder-plus", provider="qwen")

# Defaults
print(DEFAULT_MODEL)     # "qwen3-coder-plus"
print(DEFAULT_BASE_URL)  # DashScope endpoint
```

## Pipeline composition

```python
from rvrb_transcriber import transcribe
from rvrb_verify import verify

# Transcribe audio
transcript = transcribe("meeting.mp3")

# Verify claims in transcript
for sentence in transcript.text.split(". "):
    if "?" not in sentence and len(sentence) > 20:
        verdict = verify(sentence)
        print(f"Claim: {sentence}")
        print(f"Verdict: {verdict.verdict.value} ({verdict.confidence:.1%})")
        print()
```
