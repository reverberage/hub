# MCP Server

rvrb-hear exposes an MCP (Model Context Protocol) server for integration with AI agents.

## Installation

```bash
pip install "rvrb-hear[mcp]"
```

## Tool definition

The MCP server exposes a single tool:

### `hear`

Analyze an audio file using the omni model.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|:--------:|-------------|
| `audio_path` | `str` | Yes | Path to audio file |
| `prompt` | `str` | No | Custom analysis prompt (default: `""`) |

**Returns:** `dict` — HearResult as JSON-serializable dictionary.

## Usage

### Start the server

```bash
rvrb-hear-mcp
```

The server runs on stdio transport, compatible with any MCP client.

### Claude Desktop

Add to your Claude Desktop config:

```json
{
  "mcpServers": {
    "hear": {
      "command": "rvrb-hear-mcp",
      "env": {
        "DASHSCOPE_API_KEY": "sk-..."
      }
    }
  }
}
```

### Continue.dev

Add to your Continue config:

```json
{
  "mcpServers": [
    {
      "name": "hear",
      "command": "rvrb-hear-mcp",
      "env": {
        "DASHSCOPE_API_KEY": "sk-..."
      }
    }
  ]
}
```

### Programmatic usage

```python
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

server_params = StdioServerParameters(
    command="rvrb-hear-mcp",
    env={"DASHSCOPE_API_KEY": "sk-..."}
)

async with stdio_client(server_params) as (read, write):
    async with ClientSession(read, write) as session:
        await session.initialize()
        
        result = await session.call_tool(
            "hear",
            arguments={
                "audio_path": "podcast.mp3",
                "prompt": "Summarize this audio"
            }
        )
        
        print(result.content)
```

## JSON-RPC example

```json
// Request
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "hear",
    "arguments": {
      "audio_path": "podcast.mp3",
      "prompt": "What is this audio about?"
    }
  }
}

// Response
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "content": [
      {
        "type": "text",
        "text": "{\"analysis\": \"...\", \"model\": \"qwen3.5-omni-plus\", ...}"
      }
    ]
  }
}
```

## Environment variables

| Variable | Description |
|----------|-------------|
| `DASHSCOPE_API_KEY` | Required for Qwen provider |
| `OPENAI_API_KEY` | Required for OpenAI provider |
| `N3RVERBERAGE_PROVIDER` | Default provider |
| `N3RVERBERAGE_DEFAULT_MODEL` | Default model ID |

## Integration with other satellites

Combine with other reverberage satellites:

```json
{
  "mcpServers": {
    "transcriber": {
      "command": "rvrb-transcriber-mcp"
    },
    "hear": {
      "command": "rvrb-hear-mcp"
    },
    "see": {
      "command": "rvrb-see-mcp"
    }
  }
}
```

Example workflow:
1. Transcribe audio with `transcriber` tool
2. Comprehend audio with `hear` tool (deeper analysis)
3. Analyze images with `see` tool
