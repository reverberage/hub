# Getting Started

## Installation

```bash
pip install rvrb-verify
```

## Provider setup

rvrb-verify requires an LLM provider. Set one of:

| Provider | Environment Variable | Get it at |
|----------|---------------------|-----------|
| Qwen (default) | `DASHSCOPE_API_KEY` | [Alibaba Cloud](https://dashscope.console.aliyun.com/) |
| OpenAI | `OPENAI_API_KEY` | [platform.openai.com](https://platform.openai.com/api-keys) |
| Local | None | Ollama or vLLM running locally |

## First verification

### CLI

```bash
# Basic verification
export DASHSCOPE_API_KEY="sk-..."
rvrb-verify "The sky is blue"

# With specific strategy
rvrb-verify "Water boils at 100°C" --strategy fact-check

# JSON output
rvrb-verify "Python was created in 1991" --json

# Research strategy
rvrb-verify "Quantum computing breaks Moore's law" --strategy research

# Save to file
rvrb-verify "The Earth is flat" --output verdict.txt
```

### Python

```python
from rvrb_verify import verify

# Basic usage
verdict = verify("The sky is green")

print(f"Verdict: {verdict.verdict.value}")  # "false"
print(f"Confidence: {verdict.confidence:.1%}")  # 0.95
print(f"Summary: {verdict.summary}")

# With strategy
verdict = verify("Water boils at 100°C", strategy="fact-check")

# With model override
verdict = verify("Claim text", model="qwen3-coder-plus")
```

## Strategies

| Strategy | When to use | Example claims |
|----------|-------------|----------------|
| `fact-check` | General factual claims | "The sky is blue", "Water boils at 100°C" |
| `legal` | Legal/statutory claims | "GDPR requires consent for cookies" |
| `research` | Academic/scientific claims | "Quantum computing breaks Moore's law" |

## Output formats

| Format | CLI flag | Description |
|--------|----------|-------------|
| Plain text | (default) | Verdict, confidence, summary |
| JSON | `--json` | Full verdict with evidence and sources |

## What's next

- [CLI Reference](CLI-Reference) — all flags and options
- [Python API](Python-API) — programmatic usage
- [Strategies](Strategies) — deep dive into each strategy
- [MCP Server](MCP-Server) — integrate with AI agents
