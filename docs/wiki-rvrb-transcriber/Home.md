# rvrb-transcriber

**Atomic audio/video transcription.** Audio in, text out.

Part of the [reverberage](https://github.com/reverberage) ecosystem — composable MCP-native toolkits for audio, video, and text.

## What it does

Takes an audio or video file and produces a time-aligned transcription with full text, timed segments, detected language, and duration. Exports to plain text, SRT subtitles, WebVTT, or structured JSON.

## Quick start

```bash
pip install "rvrb-transcriber[openai]"
export OPENAI_API_KEY="sk-..."
rvrb-transcribe interview.mp3
```

## Wiki pages

| Page | Description |
|------|-------------|
| [Getting Started](Getting-Started) | Installation, first transcription, output formats |
| [CLI Reference](CLI-Reference) | All flags, options, and examples |
| [Python API](Python-API) | Programmatic usage from Python code |
| [Engines](Engines) | OpenAI Whisper API vs local Whisper |
| [Output Formats](Output-Formats) | SRT, WebVTT, JSON details |
| [MCP Server](MCP-Server) | Integrate with MCP-compatible agents |
| [Architecture](Architecture) | Internal design, module structure |
| [Development](Development) | Contributing, testing, linting |
| [FAQ](FAQ) | Common questions and troubleshooting |

## Supported formats

| Input | Output |
|-------|--------|
| mp3, wav, m4a, flac, ogg, webm, mp4, avi, mov | Plain text, SRT, WebVTT, JSON |

## Engines

| Engine | When to use |
|--------|-------------|
| `openai` | Quick start, high accuracy, no local GPU needed |
| `local` | Offline, no API costs, GPU recommended |

## License

Apache-2.0 — same as the reverberage ecosystem.
