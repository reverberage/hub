# Output Formats

rvrb-transcriber produces transcriptions in four formats. Choose based on your use case.

## Plain text

**CLI**: `--format text` (default)
**Python**: `result.text`

The full transcribed text as a single string. No timestamps, no structure.

```bash
rvrb-transcribe interview.mp3
# Output: Hello world this is a test of the transcription system
```

```python
result = transcribe("interview.mp3")
print(result.text)
# "Hello world this is a test of the transcription system"
```

**Use when**: You just need the words. Feeds into downstream processing (rvrb-verify, rvrb-transform).

## SRT (SubRip Subtitle)

**CLI**: `--format srt`
**Python**: `result.to_srt()`

Standard subtitle format supported by virtually all video players and editors.

```
1
00:00:00,000 --> 00:00:02,500
Hello world

2
00:00:02,500 --> 00:00:05,000
This is a test

3
00:00:05,000 --> 00:00:08,200
Of the transcription system
```

**Format rules**:
- Sequential numbering starting at 1
- Timestamps: `HH:MM:SS,mmm` (comma before milliseconds)
- Arrow: ` --> ` (space-arrow-space)
- One blank line between entries

**Use when**: Adding subtitles to video, feeding into video editors (Premiere, DaVinci, Final Cut).

## WebVTT

**CLI**: `--format vtt`
**Python**: `result.to_vtt()`

Web standard subtitle format. Used by HTML5 `<video>` elements and web players.

```
WEBVTT

00:00:00.000 --> 00:00:02.500
Hello world

00:00:02.500 --> 00:00:05.000
This is a test

00:00:05.000 --> 00:00:08.200
Of the transcription system
```

**Format rules**:
- Starts with `WEBVTT` header
- Timestamps: `HH:MM:SS.mmm` (dot before milliseconds)
- Arrow: ` --> ` (same as SRT)
- No sequential numbering needed

**Use when**: Web development, HTML5 video, JWPlayer, Video.js, or any web-based player.

## JSON

**CLI**: `--format json`
**Python**: `result.model_dump()` or `result.model_dump_json()`

Structured data with full metadata. Machine-readable.

```json
{
  "text": "Hello world this is a test",
  "segments": [
    {
      "start": 0.0,
      "end": 2.5,
      "text": "Hello world"
    },
    {
      "start": 2.5,
      "end": 5.0,
      "text": "this is a test"
    }
  ],
  "language": "en",
  "duration_seconds": 5.0
}
```

**Fields**:

| Field | Type | Description |
|-------|------|-------------|
| `text` | `string` | Full transcribed text |
| `segments` | `array` | Timed segments with start/end/text |
| `language` | `string` | Detected language code |
| `duration_seconds` | `number` | Audio duration in seconds |

**Segment fields**:

| Field | Type | Description |
|-------|------|-------------|
| `start` | `number` | Start time in seconds |
| `end` | `number` | End time in seconds |
| `text` | `string` | Text for this segment |

**Use when**: Programmatic processing, data analysis, feeding into other tools, building pipelines.

## Format selection guide

| Use case | Recommended format |
|----------|-------------------|
| Just need the text | `text` |
| Subtitles for video | `srt` |
| Web player subtitles | `vtt` |
| Data processing / analysis | `json` |
| Feeding into rvrb-verify | `text` |
| Building a subtitle editor | `json` (has timestamps) |
| Archive / storage | `json` (most complete) |
