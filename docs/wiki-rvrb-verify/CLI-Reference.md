# CLI Reference

## Synopsis

```
rvrb-verify [OPTIONS] CLAIM_TEXT
```

## Arguments

| Argument | Required | Description |
|----------|:--------:|-------------|
| `CLAIM_TEXT` | Yes | The claim to verify |

## Options

| Flag | Short | Default | Description |
|------|-------|---------|-------------|
| `--strategy` | `-s` | `fact-check` | Verification strategy: `fact-check`, `legal`, `research` |
| `--json` | | `False` | Output as JSON |
| `--model` | `-m` | `None` | Model override (e.g., `qwen3-coder-plus`) |
| `--provider` | | `None` | Provider name: `qwen`, `openai`, `local`. Overrides `N3RVERBERAGE_PROVIDER` |
| `--output` | `-o` | `None` | Write output to file instead of stdout |

## Exit codes

| Code | Meaning |
|:----:|---------|
| 0 | Success |
| 1 | Error (missing API key, invalid strategy) |
| 2 | Verification failed (API error) |

## Examples

### Basic verification

```bash
rvrb-verify "The sky is blue"
# Output:
# Verdict: true
# Confidence: 95.0%
# Summary: The sky appears blue due to Rayleigh scattering...
```

### JSON output

```bash
rvrb-verify "Python was created in 1991" --json
# Output:
# {
#   "verdict": "true",
#   "confidence": 0.98,
#   "summary": "Python was indeed created by Guido van Rossum in 1991.",
#   "evidence": [
#     {
#       "text": "Python was created in 1991 by Guido van Rossum.",
#       "source": {"type": "web", "url": "https://python.org/history"}
#     }
#   ]
# }
```

### Strategy selection

```bash
# Fact-check (general)
rvrb-verify "Water boils at 100°C" --strategy fact-check

# Legal analysis
rvrb-verify "GDPR requires consent for cookies" --strategy legal

# Academic research
rvrb-verify "Quantum computing breaks Moore's law" --strategy research
```

### Model override

```bash
rvrb-verify "The Earth is round" --model qwen3.7-plus
```

### Provider override

```bash
N3RVERBERAGE_PROVIDER=qwen rvrb-verify "Claim" --provider openai
```

### Save to file

```bash
rvrb-verify "The sky is blue" --output verdict.txt
```

### Pipe composition

```bash
# Transcribe audio → verify claims
rvrb-transcribe meeting.mp3 | rvrb-verify

# Verify with JSON → extract confidence
rvrb-verify "Claim" --json | jq '.confidence'
```

## Environment variables

| Variable | Description |
|----------|-------------|
| `DASHSCOPE_API_KEY` | Required for Qwen provider. Your Alibaba Cloud API key. |
| `OPENAI_API_KEY` | Required for OpenAI provider. Your OpenAI API key. |
| `N3RVERBERAGE_PROVIDER` | Default provider (overridden by `--provider`) |
| `N3RVERBERAGE_DEFAULT_MODEL` | Default model ID |
