# CLI Reference

## Synopsis

```
rvrb-transcribe [OPTIONS] FILE_PATH
```

## Arguments

| Argument | Required | Description |
|----------|:--------:|-------------|
| `FILE_PATH` | Yes | Path to audio or video file |

## Options

| Flag | Short | Default | Description |
|------|-------|---------|-------------|
| `--engine` | `-e` | `openai` | Transcription engine: `openai` or `local` |
| `--provider` | | `None` | Provider name for LLM features: `qwen`, `openai`, `local`. Overrides `N3RVERBERAGE_PROVIDER` |
| `--language` | | `None` | Language code hint (e.g., `en`, `es`, `pt`, `de`) for better accuracy |
| `--model` | | `None` | Model override. For `openai`: `whisper-1`. For `local`: whisper model size (`tiny`, `base`, `small`, `medium`, `large`) |
| `--format` | | `text` | Output format: `text`, `srt`, `vtt`, `json` |
| `--output` | `-o` | `None` | Write output to file instead of stdout |

## Exit codes

| Code | Meaning |
|:----:|---------|
| 0 | Success |
| 1 | Error (file not found, missing API key, invalid engine) |
| 2 | Transcription failed (API error, model error) |

## Examples

### Basic transcription

```bash
rvrb-transcribe interview.mp3
# Output: Full text to stdout
```

### SRT subtitles

```bash
rvrb-transcribe video.mp4 --format srt
# Output:
# 1
# 00:00:00,000 --> 00:00:02,500
# Hello world
#
# 2
# 00:00:02,500 --> 00:00:05,000
# This is a test
```

### WebVTT subtitles

```bash
rvrb-transcribe video.mp4 --format vtt
# Output:
# WEBVTT
#
# 00:00:00.000 --> 00:00:02.500
# Hello world
#
# 00:00:02.500 --> 00:00:05.000
# This is a test
```

### JSON output (with segments)

```bash
rvrb-transcribe interview.mp3 --format json
# Output:
# {
#   "text": "Hello world this is a test",
#   "segments": [
#     {"start": 0.0, "end": 2.5, "text": "Hello world"},
#     {"start": 2.5, "end": 5.0, "text": "this is a test"}
#   ],
#   "language": "en",
#   "duration_seconds": 5.0
# }
```

### Save to file

```bash
rvrb-transcribe podcast.m4a --format srt --output subtitles.srt
# Creates subtitles.srt, prints "Saved to subtitles.srt"
```

### Local engine

```bash
rvrb-transcribe recording.wav --engine local
# Uses local Whisper model (default: base)
```

### Local engine with model size

```bash
rvrb-transcribe recording.wav --engine local --model medium
# Uses medium Whisper model (better accuracy, slower)
```

### Language hint

```bash
rvrb-transcribe spanish_interview.mp3 --language es
# Helps Whisper with language detection
```

### Pipe composition

```bash
# Transcribe → verify claims
rvrb-transcribe meeting.mp3 | rvrb-verify

# Transcribe → JSON → extract key points
rvrb-transcribe lecture.wav --format json | jq '.text'
```

## Environment variables

| Variable | Description |
|----------|-------------|
| `OPENAI_API_KEY` | Required for `--engine openai`. Your OpenAI API key. |
| `N3RVERBERAGE_PROVIDER` | Default provider for LLM features (overridden by `--provider`) |

## Supported input formats

Audio: `mp3`, `wav`, `m4a`, `flac`, `ogg`, `aac`
Video: `mp4`, `webm`, `avi`, `mov`, `mkv`

Video files are processed by extracting the audio track automatically.
