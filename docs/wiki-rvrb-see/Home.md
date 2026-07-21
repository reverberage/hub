# rvrb-see

**Image understanding engine.** Image in, description out.

Part of the [reverberage](https://github.com/reverberage) ecosystem — composable MCP-native toolkits for audio, video, and text.

## What it does

Takes an image file and produces a detailed description using the qwen3.7-plus vision model. Supports OCR, scene analysis, object identification, and custom prompts.

## Quick start

```bash
pip install rvrb-see
export DASHSCOPE_API_KEY="sk-..."
rvrb-see photo.png
```

## Wiki pages

| Page | Description |
|------|-------------|
| [Getting Started](Getting-Started) | Installation, provider setup, first analysis |
| [CLI Reference](CLI-Reference) | All flags, options, and examples |
| [Python API](Python-API) | Programmatic usage from Python code |
| [Models](Models) | Data models and types |
| [Output Formats](Output-Formats) | Text and JSON output details |
| [MCP Server](MCP-Server) | Integrate with MCP-compatible agents |
| [Architecture](Architecture) | Internal design, module structure |
| [Development](Development) | Contributing, testing |
| [FAQ](FAQ) | Common questions and troubleshooting |

## Supported formats

| Input | Output |
|-------|--------|
| png, jpg, jpeg, gif, webp | Plain text, JSON |

## License

Apache-2.0 — same as the reverberage ecosystem.
