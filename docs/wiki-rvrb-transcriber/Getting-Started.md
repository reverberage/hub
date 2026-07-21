# Getting Started

## Installation

### OpenAI API (recommended for quick start)

```bash
pip install "rvrb-transcriber[openai]"
```

Requires an `OPENAI_API_KEY` environment variable. Get one at [platform.openai.com](https://platform.openai.com/api-keys).

### Local Whisper (offline, no API calls)

```bash
pip install "rvrb-transcriber[local]"
```

Runs Whisper on your machine. GPU recommended for reasonable speed. No API key needed.

### Both engines

```bash
pip install "rvrb-transcriber[all]"
```

## First transcription

### CLI

```bash
# Transcribe with OpenAI API
export OPENAI_API_KEY="sk-..."
rvrb-transcribe interview.mp3

# Transcribe locally (no API key)
rvrb-transcribe interview.mp3 --engine local

# Specify language for better accuracy
rvrb-transcribe meeting.wav --language en

# Get SRT subtitles
rvrb-transcribe video.mp4 --format srt

# Save to file
rvrb-transcribe podcast.m4a --output transcript.txt
```

### Python

```python
from rvrb_transcriber import transcribe

# Basic usage
result = transcribe("interview.mp3")
print(result.text)

# With language hint
result = transcribe("meeting.wav", language="es")

# Timed segments
for segment in result.segments:
    print(f"[{segment.start:.1f}s → {segment.end:.1f}s] {segment.text}")

# Export formats
print(result.to_srt())   # SubRip subtitles
print(result.to_vtt())   # WebVTT subtitles
print(result.model_dump_json(indent=2))  # JSON
```

## Output formats

| Format | CLI flag | Python method | Description |
|--------|----------|---------------|-------------|
| Plain text | `--format text` | `result.text` | Full transcribed text |
| SRT | `--format srt` | `result.to_srt()` | SubRip subtitle format |
| WebVTT | `--format vtt` | `result.to_vtt()` | WebVTT subtitle format |
| JSON | `--format json` | `result.model_dump()` | Structured data with segments |

## What's next

- [CLI Reference](CLI-Reference) — all flags and options
- [Python API](Python-API) — programmatic usage
- [Engines](Engines) — OpenAI vs local Whisper trade-offs
- [MCP Server](MCP-Server) — integrate with AI agents
