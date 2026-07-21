# FAQ

Common questions about rvrb-see.

## Supported formats

### What image formats are supported?

| Format | Extension | MIME Type |
|--------|-----------|-----------|
| PNG | `.png` | `image/png` |
| JPEG | `.jpg`, `.jpeg` | `image/jpeg` |
| GIF | `.gif` | `image/gif` |
| WebP | `.webp` | `image/webp` |

### Can I add more formats?

Yes. See [Development](Development) for details on adding formats to `MIME_MAP`.

### What about SVG or other vector formats?

Not currently supported. Convert to PNG or JPEG first:

```bash
# Convert SVG to PNG
convert image.svg image.png

# Then analyze
rvrb-see image.png
```

## Image size

### How large can images be?

The qwen3.7-plus model supports:
- Up to 2048 images per request
- Images up to 16 megapixels
- Very large images may be automatically resized

### What happens with very large images?

Large images are base64-encoded and sent as data URIs. The model may resize them internally. For best results, use images under 4096x4096 pixels.

### Can I process multiple images?

Not in a single call. Process images one at a time:

```bash
for img in *.png; do
    rvrb-see "$img" --output "${img%.png}.txt"
done
```

## Provider setup

### Which provider should I use?

**Qwen (default)** — Best for qwen3.7-plus vision model, free tier available.

**OpenAI** — Use if you have an OpenAI API key and prefer GPT-4o vision.

**Local** — Limited vision models available locally.

### How do I get a Qwen API key?

1. Go to [Alibaba Cloud Model Studio](https://dashscope.console.aliyun.com/)
2. Sign up for a free account (Singapore region)
3. Activate Model Studio
4. Generate an API key
5. Set `export DASHSCOPE_API_KEY="sk-..."`

Free tier: 1M tokens for qwen3.7-plus, 90-day validity.

## Vision capabilities

### What can rvrb-see do?

- **Scene description**: Describe what's in an image
- **OCR**: Extract text from images
- **Object detection**: List objects in an image
- **Chart analysis**: Describe charts, graphs, diagrams
- **Color analysis**: Identify color palettes
- **Screenshot analysis**: Describe UI elements

### Can it recognize faces?

The model can describe faces (e.g., "a person wearing glasses") but does not identify specific individuals.

### Can it read handwriting?

Yes, but accuracy varies. Printed text works best.

### Can it analyze videos?

No. rvrb-see is image-only. For video, extract frames first:

```bash
# Extract frames from video
ffmpeg -i video.mp4 -vf "fps=1" frame_%04d.png

# Analyze each frame
for frame in frame_*.png; do
    rvrb-see "$frame" --output "${frame%.png}.txt"
done
```

## Token costs

### How many tokens does analysis use?

Approximate usage per analysis:
- **Image encoding**: Varies by image size (base64 encoding)
- **Analysis**: 200-1000 tokens
- **Total**: 500-2000 tokens per analysis

### How can I reduce costs?

- Use smaller images
- Use local provider (no API costs)
- Batch process with custom scripts

## Offline usage

### Can I use rvrb-see offline?

Yes, with a local provider that supports vision:

```bash
# Install Ollama with vision model
# Use local provider
rvrb-see image.png --provider local
```

Note: Local vision models are limited compared to cloud models.

## Integration

### Can I use rvrb-see with other satellites?

Yes. Common pipelines:

```bash
# Analyze image → verify description
rvrb-see chart.png --json | jq -r '.description' | rvrb-verify

# Analyze multiple images
for img in *.png; do
    rvrb-see "$img" --json >> results.json
done
```

### Can I use rvrb-see in my application?

Yes. Install via pip and use the Python API:

```python
from rvrb_see import SeeEngine, get_provider

engine = SeeEngine(provider=get_provider())
result = engine.see("image.png")
```

## Troubleshooting

### Error: "File not found"

Check the image file path:

```bash
ls -l image.png
```

### Error: "Unsupported image format"

Check the file extension:

```bash
# Supported: png, jpg, jpeg, gif, webp
rvrb-see image.png  # OK
rvrb-see image.xyz  # Error
```

### Error: "DASHSCOPE_API_KEY is not set"

Set the environment variable:

```bash
export DASHSCOPE_API_KEY="sk-..."
```

Or use a different provider:

```bash
rvrb-see image.png --provider openai
```

### Description is empty or incorrect

- Check image quality (clear images work best)
- Try a different prompt
- Use a more capable model: `--model qwen3.7-plus`

### Error: "Image too large"

Resize the image:

```bash
# Resize to max 4096x4096
convert large.png -resize '4096x4096>' resized.png
rvrb-see resized.png
```

## Performance

### How long does analysis take?

Typical analysis time:
- **Small images (< 1MB)**: 1-3 seconds
- **Medium images (1-5MB)**: 3-5 seconds
- **Large images (5MB+)**: 5-10 seconds

### Can I speed up analysis?

- Use smaller images
- Use faster models (if available)
- Use local provider (no network latency)

## License

Apache-2.0 — same as the reverberage ecosystem.
