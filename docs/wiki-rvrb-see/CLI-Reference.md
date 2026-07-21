# CLI Reference

## Synopsis

```
rvrb-see [OPTIONS] IMAGE_PATH
```

## Arguments

| Argument | Required | Description |
|----------|:--------:|-------------|
| `IMAGE_PATH` | Yes | Path to image file |

## Options

| Flag | Short | Default | Description |
|------|-------|---------|-------------|
| `--prompt` | `-p` | `""` | Custom analysis prompt |
| `--json` | | `False` | Output as JSON |
| `--model` | `-m` | `None` | Model override (e.g., `qwen3.7-plus`) |
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
rvrb-see photo.png
# Output: A detailed description of the image...
```

### Custom prompt

```bash
rvrb-see screenshot.png --prompt "What text is in this image?"
# Output: The image contains the following text...
```

### JSON output

```bash
rvrb-see chart.jpg --json
# Output:
# {
#   "description": "A bar chart showing quarterly revenue...",
#   "model": "qwen3.7-plus",
#   "provider": "qwen",
#   "prompt": "",
#   "tokens_used": 850
# }
```

### Save to file

```bash
rvrb-see diagram.png --output description.txt
```

### Model override

```bash
rvrb-see image.png --model qwen3.7-plus
```

### Provider override

```bash
N3RVERBERAGE_PROVIDER=qwen rvrb-see image.png --provider openai
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
| PNG | `.png` | `image/png` |
| JPEG | `.jpg`, `.jpeg` | `image/jpeg` |
| GIF | `.gif` | `image/gif` |
| WebP | `.webp` | `image/webp` |

## Image size limits

The qwen3.7-plus model supports up to 2048 images per request and images up to 16 megapixels. Very large images may be resized.
