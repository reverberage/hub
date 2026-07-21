# MCP Server

rvrb-transcriber exposes its transcription capabilities as an MCP (Model Context Protocol) server, making it available to any MCP-compatible AI agent.

## Installation

```bash
pip install "rvrb-transcriber[mcp]"
```

This installs the `mcp` extra alongside the base package.

## Running

```bash
rvrb-transcribe-mcp
```

Starts the MCP server with stdio transport. Connect from any MCP client (Claude Desktop, Continue.dev, etc.).

## Tools

### `transcribe`

Transcribe an audio or video file.

**Parameters**:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `file_path` | `str` | required | Path to audio/video file |
| `engine` | `str` | `"openai"` | `"openai"` or `"local"` |
| `language` | `str \| None` | `None` | Language code hint |
| `model` | `str \| None` | `None` | Model override |

**Returns**: `dict` with keys:
- `text` — full transcribed text
- `segments` — list of `{start, end, text}` dicts
- `language` — detected language code
- `duration_seconds` — audio duration
- `srt` — SRT formatted subtitles
- `vtt` — WebVTT formatted subtitles

**Example**:

```json
{
  "file_path": "/path/to/interview.mp3",
  "engine": "openai",
  "language": "en"
}
```

### `transcribe_to_srt`

Transcribe audio/video and return SRT subtitles.

**Parameters**:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `file_path` | `str` | required | Path to audio/video file |
| `output_path` | `str \| None` | `None` | Write SRT to this file |
| `engine` | `str` | `"openai"` | `"openai"` or `"local"` |
| `language` | `str \| None` | `None` | Language code hint |

**Returns**: `str` — SRT formatted subtitles

### `transcribe_to_vtt`

Transcribe audio/video and return WebVTT subtitles.

**Parameters**:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `file_path` | `str` | required | Path to audio/video file |
| `output_path` | `str \| None` | `None` | Write VTT to this file |
| `engine` | `str` | `"openai"` | `"openai"` or `"local"` |
| `language` | `str \| None` | `None` | Language code hint |

**Returns**: `str` — WebVTT formatted subtitles

## Resources

### `transcriber://info`

Returns service information (version, supported engines, formats).

## MCP client configuration

### Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "rvrb-transcriber": {
      "command": "rvrb-transcribe-mcp",
      "env": {
        "OPENAI_API_KEY": "sk-..."
      }
    }
  }
}
```

### Continue.dev

Add to `~/.continue/config.json`:

```json
{
  "mcpServers": [
    {
      "name": "rvrb-transcriber",
      "command": "rvrb-transcribe-mcp",
      "env": {
        "OPENAI_API_KEY": "sk-..."
      }
    }
  ]
}
```

### Any MCP client

```bash
# The server communicates via stdio
rvrb-transcribe-mcp
# stdin/stdout JSON-RPC 2.0
```

## Agent usage examples

### Transcribe and summarize

```
User: Transcribe this meeting and summarize the action items
Agent: [calls transcribe tool] → gets text → [calls rvrb-transform or processes directly]
```

### Generate subtitles

```
User: Create SRT subtitles for my video
Agent: [calls transcribe_to_srt tool] → returns SRT content
```

### Multilingual transcription

```
User: Transcribe this Spanish interview
Agent: [calls transcribe with language="es"] → returns Spanish transcription
```

## Error handling

| Error | Cause | Solution |
|-------|-------|----------|
| `FileNotFoundError` | File doesn't exist | Check file path |
| `ValueError: OPENAI_API_KEY required` | Missing API key | Set `OPENAI_API_KEY` env var |
| `ImportError: MCP support requires...` | Missing mcp extra | `pip install rvrb-transcriber[mcp]` |
| API errors | Network or auth issues | Check API key, network connection |

## Relationship to other satellites

The MCP server makes rvrb-transcriber composable with other reverberage satellites:

```
rvrb-transcriber (MCP) → rvrb-verify (MCP) → rvrb-transform (MCP)
     audio → text         text → verdict       text → formatted
```

Each satellite runs as its own MCP server. An agent can chain them by calling tools in sequence.
