# CLI Reference

## Synopsis

```
rvrb-hear [OPTIONS] AUDIO_PATH
```

## Arguments

| Argument | Required | Description |
|----------|:--------:|-------------|
| `AUDIO_PATH` | Yes | Path to audio file |

## Options

| Flag | Short | Default | Description |
|------|-------|---------|-------------|
| `--prompt` | `-p` | `""` | Custom analysis prompt |
| `--json` | | `False` | Output as JSON |
| `--model` | `-m` | `None` | Model override (e.g., `qwen3.5-omni-plus`) |
| `--provider` | | `None` | Provider name: `qwen`, `openai`, `local`. Overrides `N3RVERBERAGE_PROVIDER` |
| `--output` | `-o` | `None` | Write output to file instead of stdout |

## Exit codes

| Code | Meaning |
|:----:|---------|
| 0 | Success |
| 1 | Error (file not found, missing API key, invalid format) |

## Examples

### Basic analysis

```bash
rvrb-hear podcast.mp3
# Output: Detailed analysis of the audio content...
```

### Custom prompt

```bash
rvrb-hear meeting.wav --prompt "What decisions were made?"
# Output: The following decisions were made...
```

### JSON output

```bash
rvrb-hear lecture.mp3 --json
# Output:
# {
#   "analysis": "The lecture covers...",
#   "model": "qwen3.5-omni-plus",
#   "provider": "qwen",
#   "prompt": "",
#   "tokens_used": 1234
# }
```

### Save to file

```bash
rvrb-hear interview.m4a --output analysis.txt
```

### Model override

```bash
rvrb-hear audio.wav --model qwen3.5-omni-plus
```

### Provider override

```bash
N3RVERBERAGE_PROVIDER=qwen rvrb-hear audio.mp3 --provider openai
```

## Environment variables

| Variable | Description |
|----------|-------------|
| `DASHSCOPE_API_KEY` | Required for Qwen provider. Your Alibaba Cloud API key. |
| `OPENAI_API_KEY` | Required for OpenAI provider. Your OpenAI API key. |
| `N3RVERBERAGE_PROVIDER` | Default provider (overridden by `--provider`) |
| `N3RVERBERAGE_DEFAULT_MODEL` | Default model ID |

## Supported input formats

| Format | Extension | MIME Type |
|--------|-----------|-----------|
| WAV | `.wav` | `audio/wav` |
| MP3 | `.mp3` | `audio/mpeg` |
| AAC | `.aac` | `audio/aac` |
| FLAC | `.flac` | `audio/flac` |
| M4A | `.m4a` | `audio/mp4` |
| OGG | `.ogg` | `audio/ogg` |
| AMR | `.amr` | `audio/amr` |

## Audio duration limits

The qwen3.5-omni-plus model supports up to 3 hours of audio. Very long audio files may be truncated.
