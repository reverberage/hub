# FAQ

Common questions about rvrb-hear.

## Supported formats

### What audio formats are supported?

| Format | Extension | MIME Type |
|--------|-----------|-----------|
| WAV | `.wav` | `audio/wav` |
| MP3 | `.mp3` | `audio/mpeg` |
| AAC | `.aac` | `audio/aac` |
| FLAC | `.flac` | `audio/flac` |
| M4A | `.m4a` | `audio/mp4` |
| OGG | `.ogg` | `audio/ogg` |
| AMR | `.amr` | `audio/amr` |

### Can I add more formats?

Yes. See [Development](Development) for details on adding formats to `MIME_MAP`.

### What about video files?

rvrb-hear is audio-only. For video, extract the audio track first:

```bash
# Extract audio from video
ffmpeg -i video.mp4 -vn -acodec libmp3lame audio.mp3

# Then analyze
rvrb-hear audio.mp3
```

## Audio duration

### How long can audio files be?

The qwen3.5-omni-plus model supports up to 3 hours of audio. Very long files may be truncated.

### Can I process longer audio?

Split long audio into chunks:

```bash
# Split into 30-minute chunks
ffmpeg -i long_audio.mp3 -f segment -segment_time 1800 -c copy chunk_%03d.mp3

# Process each chunk
for chunk in chunk_*.mp3; do
    rvrb-hear "$chunk" --output "${chunk%.mp3}.txt"
done
```

## Provider setup

### Which provider should I use?

**Qwen (default)** — Best for qwen3.5-omni-plus, free tier available.

**OpenAI** — Use if you have an OpenAI API key and prefer GPT-4o.

**Local** — Limited audio comprehension models available locally.

### How do I get a Qwen API key?

1. Go to [Alibaba Cloud Model Studio](https://dashscope.console.aliyun.com/)
2. Sign up for a free account (Singapore region)
3. Activate Model Studio
4. Generate an API key
5. Set `export DASHSCOPE_API_KEY="sk-..."`

Free tier: 1M tokens for qwen3.5-omni-plus, 90-day validity.

## Streaming

### Why does rvrb-hear use streaming?

The qwen3.5-omni-plus model requires `stream=True` for audio comprehension. The streaming is handled internally — the API returns a synchronous `str` result.

### Can I disable streaming?

No. Streaming is required by the model and handled transparently.

### What is `modalities=["text"]`?

This prevents the omni model from generating TTS audio output in parallel with text response. It saves tokens and bandwidth.

## Token costs

### How many tokens does analysis use?

Approximate usage per analysis:
- **Audio encoding**: Varies by duration (base64 encoding)
- **Analysis**: 500-2000 tokens
- **Total**: 1000-3000 tokens per analysis

### How can I reduce costs?

- Use shorter audio files
- Use local provider (no API costs)
- Batch process with custom scripts

## Offline usage

### Can I use rvrb-hear offline?

Yes, with a local provider that supports audio comprehension:

```bash
# Install Ollama with audio model
# Use local provider
rvrb-hear audio.mp3 --provider local
```

Note: Local audio comprehension models are limited compared to cloud models.

## Integration

### Can I use rvrb-hear with other satellites?

Yes. Common pipelines:

```bash
# Transcribe → comprehend
rvrb-transcriber meeting.mp3 | rvrb-hear meeting.mp3

# Comprehend → verify
rvrb-hear podcast.mp3 --json | jq -r '.analysis' | rvrb-verify
```

### Can I use rvrb-hear in my application?

Yes. Install via pip and use the Python API:

```python
from rvrb_hear import HearEngine, get_provider

engine = HearEngine(provider=get_provider())
result = engine.hear("audio.mp3")
```

## Troubleshooting

### Error: "File not found"

Check the audio file path:

```bash
ls -l audio.mp3
```

### Error: "Unsupported audio format"

Check the file extension:

```bash
# Supported: wav, mp3, aac, flac, m4a, ogg, amr
rvrb-hear audio.mp3  # OK
rvrb-hear audio.xyz  # Error
```

### Error: "DASHSCOPE_API_KEY is not set"

Set the environment variable:

```bash
export DASHSCOPE_API_KEY="sk-..."
```

Or use a different provider:

```bash
rvrb-hear audio.mp3 --provider openai
```

### Analysis is empty or incorrect

- Check audio quality (clear audio works best)
- Try a different prompt
- Use a more capable model: `--model qwen3.5-omni-plus`

### Error: "stream=True required"

This is handled internally. If you see this error, it's a bug — please report it.

## Performance

### How long does analysis take?

Typical analysis time:
- **Short audio (< 1 min)**: 2-5 seconds
- **Medium audio (1-10 min)**: 5-15 seconds
- **Long audio (10+ min)**: 15-60 seconds

### Can I speed up analysis?

- Use shorter audio files
- Use faster models (if available)
- Use local provider (no network latency)

## License

Apache-2.0 — same as the reverberage ecosystem.
