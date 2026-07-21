# Engines

rvrb-transcriber supports two transcription engines. Choose based on your constraints.

## OpenAI Whisper API

**When to use**: Quick start, high accuracy, no local GPU needed.

```bash
pip install "rvrb-transcriber[openai]"
export OPENAI_API_KEY="sk-..."
rvrb-transcribe interview.mp3
```

### How it works

1. Sends audio file to OpenAI's Whisper API endpoint
2. Receives full transcription with timestamps
3. Returns `Transcript` with text, segments, language, duration

### Requirements

- `OPENAI_API_KEY` environment variable
- Internet connection
- OpenAI account with API access

### Characteristics

| Property | Value |
|----------|-------|
| Model | `whisper-1` (default, only option) |
| Accuracy | High — OpenAI's best Whisper variant |
| Speed | Fast (network-dependent) |
| Max file size | 25 MB |
| Supported formats | mp3, mp4, mpeg, mpga, m4a, wav, webm |
| Cost | Per-minute pricing at [openai.com/pricing](https://openai.com/pricing) |
| Language detection | Automatic (or pass `--language` hint) |

### Limitations

- 25 MB file size limit per request
- Requires internet connection
- Per-minute cost adds up for long audio
- No control over model size (always `whisper-1`)

## Local Whisper

**When to use**: Offline operation, no API costs, GPU recommended.

```bash
pip install "rvrb-transcriber[local]"
rvrb-transcribe interview.mp3 --engine local
```

### How it works

1. Downloads and loads Whisper model locally (first run)
2. Transcribes audio on your machine
3. Returns `Transcript` with text, segments, language, duration

### Requirements

- `openai-whisper` Python package (installed via `[local]` extra)
- Sufficient RAM (model-dependent)
- GPU recommended for `medium` and `large` models

### Model sizes

| Model | Parameters | VRAM | Speed | Accuracy |
|-------|:----------:|:----:|:-----:|:--------:|
| `tiny` | 39M | ~1 GB | Fastest | Lowest |
| `base` | 74M | ~1 GB | Fast | Good |
| `small` | 244M | ~2 GB | Medium | Better |
| `medium` | 769M | ~5 GB | Slow | Great |
| `large` | 1550M | ~10 GB | Slowest | Best |

Default: `base` (good balance of speed and accuracy).

### Limitations

- Model download on first use (~150 MB for `base`)
- CPU transcription is slow for `medium`/`large`
- No GPU = slow for anything above `base`
- Higher memory usage than API approach

## Comparison

| Aspect | OpenAI API | Local |
|--------|:----------:|:-----:|
| Accuracy | ★★★★★ | ★★★☆☆ to ★★★★★ |
| Speed (short audio) | Fast | Fast |
| Speed (long audio) | Fast | Slow (CPU) |
| Cost | Per-minute | Free |
| Privacy | Audio sent to OpenAI | Everything stays local |
| Offline | No | Yes |
| GPU required | No | Recommended |
| Max file size | 25 MB | Unlimited |
| Setup | API key | Model download |

## Recommendation

- **Start with `openai`** — fastest path to working transcription
- **Switch to `local`** when you need: offline, privacy, or cost control
- **Use `medium` or `large` local model** when accuracy matters more than speed
- **Use `tiny` or `base`** for quick tests and development

## Future: Multimodal audio understanding

The `ModelProvider` Protocol is defined in `provider.py` for future multimodal features (e.g., Qwen-VL audio understanding via DashScope). Currently unused — the transcriber uses Whisper directly. When multimodal audio understanding is added, it will go through `get_provider()`.
