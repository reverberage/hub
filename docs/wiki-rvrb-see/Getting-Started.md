# Getting Started

## Installation

```bash
pip install rvrb-see
```

## Provider setup

rvrb-see requires an LLM provider with vision capabilities.

| Provider | Environment Variable | Get it at |
|----------|---------------------|-----------|
| Qwen (default) | `DASHSCOPE_API_KEY` | [Alibaba Cloud](https://dashscope.console.aliyun.com/) |
| OpenAI | `OPENAI_API_KEY` | [platform.openai.com](https://platform.openai.com/api-keys) |
| Local | None | Ollama or vLLM running locally |

## First analysis

### CLI

```bash
# Basic image analysis
export DASHSCOPE_API_KEY="sk-..."
rvrb-see photo.png

# Custom prompt
rvrb-see screenshot.png --prompt "What text is in this image?"

# JSON output
rvrb-see chart.jpg --json

# Save to file
rvrb-see diagram.png --output description.txt
```

### Python

```python
from rvrb_see import SeeEngine, get_provider

# Create engine
provider = get_provider()
engine = SeeEngine(provider=provider)

# Analyze image
result = engine.see("photo.png")

print(f"Description: {result.description}")
print(f"Model: {result.model}")
print(f"Provider: {result.provider}")
```

## Custom prompts

```bash
# OCR - extract text
rvrb-see document.png --prompt "Extract all text from this image"

# Object detection
rvrb-see scene.jpg --prompt "List all objects in this image"

# Scene description
rvrb-see landscape.png --prompt "Describe the scene in detail"

# Chart analysis
rvrb-see chart.png --prompt "What data does this chart show?"

# Color analysis
rvrb-see design.png --prompt "What is the color palette?"
```

## Output formats

| Format | CLI flag | Description |
|--------|----------|-------------|
| Plain text | (default) | Description text |
| JSON | `--json` | Full result with metadata |

## What's next

- [CLI Reference](CLI-Reference) — all flags and options
- [Python API](Python-API) — programmatic usage
- [Models](Models) — data model details
- [MCP Server](MCP-Server) — integrate with AI agents
