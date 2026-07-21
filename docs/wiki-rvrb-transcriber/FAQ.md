# FAQ

## General

### What audio/video formats are supported?

**Audio**: mp3, wav, m4a, flac, ogg, aac
**Video**: mp4, webm, avi, mov, mkv

Video files have their audio track extracted automatically.

### Is there a file size limit?

- **OpenAI API**: 25 MB max per request
- **Local Whisper**: No limit (limited by RAM/VRAM)

For files over 25 MB with the OpenAI engine, split the audio first.

### What languages are supported?

Whisper supports 99 languages. Common ones: English, Spanish, Portuguese, German, French, Italian, Japanese, Chinese, Korean, Arabic, Hindi, and many more.

Pass `--language` for better accuracy when you know the language.

### Does it work offline?

- **OpenAI engine**: No, requires internet
- **Local engine**: Yes, fully offline after model download

## OpenAI engine

### Why do I get "OPENAI_API_KEY required"?

Set the environment variable:

```bash
export OPENAI_API_KEY="sk-..."
```

Or pass it programmatically:

```python
result = transcribe("audio.mp3", api_key="sk-...")
```

### How much does it cost?

OpenAI Whisper API pricing: see [openai.com/pricing](https://openai.com/pricing). Generally a few cents per minute of audio.

### Can I use a different OpenAI-compatible endpoint?

Not directly through the CLI. The OpenAI engine hardcodes the OpenAI endpoint. For other endpoints, use the `local` engine or the `ModelProvider` Protocol in Python.

## Local engine

### Why is transcription so slow?

Local Whisper on CPU is slow for models above `base`. Options:

1. Use a smaller model: `--model tiny` or `--model base`
2. Use GPU (CUDA): Install `torch` with CUDA support
3. Use the OpenAI API engine instead

### How do I use GPU?

Install PyTorch with CUDA:

```bash
pip install torch --index-url https://download.pytorch.org/whl/cu121
```

Whisper will automatically use GPU if available.

### Where are models stored?

Whisper stores models in `~/.cache/whisper/`. First run downloads the model.

## Output

### Why are my subtitles out of sync?

Whisper provides segment-level timestamps, not word-level. If segments are long, text within a segment appears at the same time. This is normal.

For tighter sync, use the JSON output and post-process with word-level alignment tools.

### Can I get word-level timestamps?

Not with the current Whisper API. The `verbose_json` response format provides segment-level timestamps only.

### What's the difference between SRT and VTT?

- **SRT**: `HH:MM:SS,mmm` (comma before ms), sequential numbering
- **VTT**: `HH:MM:SS.mmm` (dot before ms), `WEBVTT` header, no numbering required

Both are widely supported. Use SRT for desktop players, VTT for web.

## Integration

### How do I chain with other satellites?

```bash
# Transcribe → Verify claims
rvrb-transcribe meeting.mp3 | rvrb-verify

# Transcribe → Transform to summary
rvrb-transcribe lecture.wav | rvrb-transform "summarize the key points"
```

### How do I use the MCP server?

```bash
pip install "rvrb-transcriber[mcp]"
rvrb-transcribe-mcp
```

Then configure your MCP client to connect. See [MCP Server](MCP-Server) for details.

### Does it work with rvrb-verify?

Yes. Pipe the transcription text into verify:

```bash
rvrb-transcribe podcast.mp3 | rvrb-verify "Is the claim about climate change accurate?"
```

## Troubleshooting

### "No module named 'whisper'"

Install the local extra:

```bash
pip install "rvrb-transcriber[local]"
```

### "No module named 'openai'"

Install the openai extra:

```bash
pip install "rvrb-transcriber[openai]"
```

### "MCP support requires the 'mcp' extra"

Install the mcp extra:

```bash
pip install "rvrb-transcriber[mcp]"
```

### Transcription is empty or garbage

1. Check the audio file is valid: `file your_audio.mp3`
2. Try a different engine: `--engine local` vs `--engine openai`
3. Specify language: `--language en`
4. Check audio quality — background noise affects accuracy
