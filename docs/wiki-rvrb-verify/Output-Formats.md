# Output Formats

rvrb-verify supports two output formats: plain text (default) and JSON.

## Plain text

Default output format. Human-readable verdict summary.

```bash
rvrb-verify "The sky is blue"
```

Output:
```
Verdict: true
Confidence: 95.0%
Summary: The sky appears blue due to Rayleigh scattering of sunlight by molecules in Earth's atmosphere.
```

### Structure

- **Verdict**: `true`, `false`, `partially_true`, or `inconclusive`
- **Confidence**: Percentage (0-100%)
- **Summary**: Human-readable explanation

## JSON

Structured output with full verdict details, evidence, and sources.

```bash
rvrb-verify "The sky is blue" --json
```

Output:
```json
{
  "verdict": "true",
  "confidence": 0.95,
  "summary": "The sky appears blue due to Rayleigh scattering...",
  "evidence": [
    {
      "text": "Rayleigh scattering causes the sky to appear blue.",
      "source": {
        "type": "web",
        "url": "https://en.wikipedia.org/wiki/Rayleigh_scattering",
        "title": "Rayleigh scattering - Wikipedia",
        "metadata": {}
      },
      "relevance": 0.98
    }
  ],
  "sources": [
    {
      "type": "web",
      "url": "https://en.wikipedia.org/wiki/Rayleigh_scattering",
      "title": "Rayleigh scattering - Wikipedia",
      "metadata": {}
    }
  ],
  "model": "qwen3-coder-plus",
  "provider": "qwen",
  "tokens_used": 1234
}
```

### JSON schema

```python
{
  "verdict": str,              # "true", "false", "partially_true", "inconclusive"
  "confidence": float,         # 0.0 to 1.0
  "summary": str,              # Human-readable summary
  "evidence": [                # List of evidence items
    {
      "text": str,             # Evidence text
      "source": {              # Source reference (optional)
        "type": str,           # "web", "news", "paper", "statute", "case_law"
        "url": str | None,     # Source URL
        "title": str | None,   # Source title
        "metadata": dict       # Additional metadata
      },
      "relevance": float | None  # Relevance score (0.0-1.0)
    }
  ],
  "sources": [                 # List of all sources
    {
      "type": str,
      "url": str | None,
      "title": str | None,
      "metadata": dict
    }
  ],
  "model": str,                # Model ID used
  "provider": str,             # Provider name
  "tokens_used": int | None    # Token count if available
}
```

## Python API

```python
from rvrb_verify import verify

verdict = verify("The sky is blue")

# Access fields
print(verdict.verdict.value)      # "true"
print(verdict.confidence)         # 0.95
print(verdict.summary)            # "The sky appears blue..."

# Evidence
for evidence in verdict.evidence:
    print(f"Evidence: {evidence.text}")
    if evidence.source:
        print(f"Source: {evidence.source.url}")

# Serialization
data = verdict.model_dump()       # dict
json_str = verdict.model_dump_json()  # JSON string
```

## Pipe composition

```bash
# Extract confidence from JSON
rvrb-verify "Claim" --json | jq '.confidence'

# Extract verdict value
rvrb-verify "Claim" --json | jq -r '.verdict'

# Count evidence items
rvrb-verify "Claim" --json | jq '.evidence | length'

# Extract all source URLs
rvrb-verify "Claim" --json | jq -r '.sources[].url'
```

## Save to file

```bash
# Plain text
rvrb-verify "Claim" --output verdict.txt

# JSON
rvrb-verify "Claim" --json --output verdict.json
```
