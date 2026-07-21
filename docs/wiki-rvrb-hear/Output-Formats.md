# Output Formats

rvrb-hear supports two output formats: plain text (default) and JSON.

## Plain text

Default output format. Human-readable analysis.

```bash
rvrb-hear podcast.mp3
```

Output:
```
The podcast discusses the evolution of artificial intelligence, starting from early expert systems
to modern deep learning approaches. The speaker emphasizes the importance of...
```

### Structure

- **Analysis**: Detailed comprehension of the audio content
- No metadata (model, provider, tokens) in plain text output

## JSON

Structured output with full result details.

```bash
rvrb-hear podcast.mp3 --json
```

Output:
```json
{
  "analysis": "The podcast discusses the evolution of artificial intelligence...",
  "model": "qwen3.5-omni-plus",
  "provider": "qwen",
  "prompt": "",
  "tokens_used": 1234
}
```

### JSON schema

```python
{
  "analysis": str,           # The comprehension result
  "model": str,              # Model ID used
  "provider": str,           # Provider name
  "prompt": str,             # The prompt used
  "tokens_used": int | None  # Token count if available
}
```

## Python API

```python
from rvrb_hear import HearEngine, get_provider

engine = HearEngine(provider=get_provider())
result = engine.hear("podcast.mp3")

# Access fields
print(result.analysis)       # "The podcast discusses..."
print(result.model)          # "qwen3.5-omni-plus"
print(result.provider)       # "qwen"
print(result.prompt)         # ""
print(result.tokens_used)    # 1234

# Serialization
data = result.model_dump()       # dict
json_str = result.model_dump_json()  # JSON string
```

## Examples by use case

### Podcast analysis

```bash
rvrb-hear podcast.mp3
# Output: Detailed summary of podcast content, topics discussed, key points
```

### Meeting comprehension

```bash
rvrb-hear meeting.wav --prompt "What decisions were made and what action items were assigned?"
# Output: List of decisions and action items
```

### Lecture analysis

```bash
rvrb-hear lecture.mp3 --prompt "What is the main thesis and supporting arguments?"
# Output: Main thesis and key arguments
```

### Interview analysis

```bash
rvrb-hear interview.mp3 --prompt "What is the speaker's emotional tone and key messages?"
# Output: Emotional analysis and key messages
```

### Music analysis

```bash
rvrb-hear song.mp3 --prompt "Describe the genre, mood, and instrumentation"
# Output: Genre, mood, and instrumentation description
```

## Pipe composition

```bash
# Extract analysis from JSON
rvrb-hear audio.mp3 --json | jq -r '.analysis'

# Extract model info
rvrb-hear audio.mp3 --json | jq '{model, provider}'

# Count tokens
rvrb-hear audio.mp3 --json | jq '.tokens_used'
```

## Save to file

```bash
# Plain text
rvrb-hear audio.mp3 --output analysis.txt

# JSON
rvrb-hear audio.mp3 --json --output analysis.json
```
