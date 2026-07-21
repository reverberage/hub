# rvrb-hear

**Audio comprehension engine.** Audio in, understanding out.

Part of the [reverberage](https://github.com/reverberage) ecosystem — composable MCP-native toolkits for audio, video, and text.

## What it does

Takes an audio file and produces a deep comprehension analysis using the qwen3.5-omni-plus model. Goes beyond simple transcription to understand speaker intent, emotion, context, and answer questions about the audio.

## Quick start

```bash
pip install rvrb-hear
export DASHSCOPE_API_KEY="sk-..."
rvrb-hear podcast.mp3
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
| wav, mp3, aac, flac, m4a, ogg, amr | Plain text, JSON |

## License

Apache-2.0 — same as the reverberage ecosystem.
