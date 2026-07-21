# Getting Started

## Installation

```bash
pip install rvrb-hear
```

## Provider setup

rvrb-hear requires an LLM provider with audio comprehension capabilities.

| Provider | Environment Variable | Get it at |
|----------|---------------------|-----------|
| Qwen (default) | `DASHSCOPE_API_KEY` | [Alibaba Cloud](https://dashscope.console.aliyun.com/) |
| OpenAI | `OPENAI_API_KEY` | [platform.openai.com](https://platform.openai.com/api-keys) |
| Local | None | Ollama or vLLM running locally |

## First analysis

### CLI

```bash
# Basic audio analysis
export DASHSCOPE_API_KEY="sk-..."
rvrb-hear podcast.mp3

# Custom prompt
rvrb-hear meeting.wav --prompt "What decisions were made?"

# JSON output
rvrb-hear lecture.mp3 --json

# Save to file
rvrb-hear interview.m4a --output analysis.txt
```

### Python

```python
from rvrb_hear import HearEngine, get_provider

# Create engine
provider = get_provider()
engine = HearEngine(provider=provider)

# Analyze audio
result = engine.hear("podcast.mp3")

print(f"Analysis: {result.analysis}")
print(f"Model: {result.model}")
print(f"Provider: {result.provider}")
```

## Custom prompts

```bash
# Summarize the audio
rvrb-hear meeting.mp3 --prompt "Summarize the key points"

# Extract action items
rvrb-hear meeting.mp3 --prompt "What action items were assigned?"

# Analyze emotion
rvrb-hear interview.mp3 --prompt "What is the speaker's emotional tone?"

# Answer specific questions
rvrb-hear lecture.mp3 --prompt "What is the main thesis?"
```

## Output formats

| Format | CLI flag | Description |
|--------|----------|-------------|
| Plain text | (default) | Analysis text |
| JSON | `--json` | Full result with metadata |

## What's next

- [CLI Reference](CLI-Reference) — all flags and options
- [Python API](Python-API) — programmatic usage
- [Models](Models) — data model details
- [MCP Server](MCP-Server) — integrate with AI agents
