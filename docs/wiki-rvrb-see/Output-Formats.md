# Output Formats

rvrb-see supports two output formats: plain text (default) and JSON.

## Plain text

Default output format. Human-readable description.

```bash
rvrb-see photo.png
```

Output:
```
The image shows a cat sitting on a wooden chair in a sunlit room. The cat is
orange and white with green eyes...
```

### Structure

- **Description**: Detailed description of the image
- No metadata (model, provider, tokens) in plain text output

## JSON

Structured output with full result details.

```bash
rvrb-see photo.png --json
```

Output:
```json
{
  "description": "The image shows a cat sitting on a wooden chair...",
  "model": "qwen3.7-plus",
  "provider": "qwen",
  "prompt": "",
  "tokens_used": 150
}
```

### JSON schema

```python
{
  "description": str,        # The image description
  "model": str,              # Model ID used
  "provider": str,           # Provider name
  "prompt": str,             # The prompt used
  "tokens_used": int | None  # Token count if available
}
```

## Python API

```python
from rvrb_see import SeeEngine, get_provider

engine = SeeEngine(provider=get_provider())
result = engine.see("photo.png")

# Access fields
print(result.description)    # "The image shows..."
print(result.model)          # "qwen3.7-plus"
print(result.provider)       # "qwen"
print(result.prompt)         # ""
print(result.tokens_used)    # 150

# Serialization
data = result.model_dump()       # dict
json_str = result.model_dump_json()  # JSON string
```

## Examples by use case

### Photo description

```bash
rvrb-see vacation.jpg
# Output: Detailed description of the scene, people, objects, colors
```

### OCR (text extraction)

```bash
rvrb-see document.png --prompt "Extract all text from this image"
# Output: All text content from the document
```

### Chart analysis

```bash
rvrb-see chart.png --prompt "What data does this chart show?"
# Output: Description of chart type, axes, data points, trends
```

### Object detection

```bash
rvrb-see scene.jpg --prompt "List all objects in this image"
# Output: List of identified objects with descriptions
```

### Color analysis

```bash
rvrb-see design.png --prompt "What is the color palette?"
# Output: Description of colors used in the image
```

### Screenshot analysis

```bash
rvrb-see screenshot.png --prompt "What application is shown and what is it doing?"
# Output: Description of the UI and activity
```

## Pipe composition

```bash
# Extract description from JSON
rvrb-see image.png --json | jq -r '.description'

# Extract model info
rvrb-see image.png --json | jq '{model, provider}'

# Count tokens
rvrb-see image.png --json | jq '.tokens_used'

# Chain with verify
rvrb-see chart.png --json | jq -r '.description' | rvrb-verify
```

## Save to file

```bash
# Plain text
rvrb-see image.png --output description.txt

# JSON
rvrb-see image.png --json --output description.json
```
