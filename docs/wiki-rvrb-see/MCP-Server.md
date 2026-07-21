# MCP Server

rvrb-see exposes an MCP (Model Context Protocol) server for integration with AI agents.

## Installation

```bash
pip install "rvrb-see[mcp]"
```

## Tool definition

The MCP server exposes a single tool:

### `see`

Analyze an image using a vision model.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|:--------:|-------------|
| `image_path` | `str` | Yes | Path to image file |
| `prompt` | `str` | No | Custom analysis prompt (default: `""`) |

**Returns:** `dict` — SeeResult as JSON-serializable dictionary.

## Usage

### Start the server

```bash
rvrb-see-mcp
```

The server runs on stdio transport, compatible with any MCP client.

### Claude Desktop

Add to your Claude Desktop config:

```json
{
  "mcpServers": {
    "see": {
      "command": "rvrb-see-mcp",
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
      "name": "see",
      "command": "rvrb-see-mcp",
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
    command="rvrb-see-mcp",
    env={"DASHSCOPE_API_KEY": "sk-..."}
)

async with stdio_client(server_params) as (read, write):
    async with ClientSession(read, write) as session:
        await session.initialize()
        
        result = await session.call_tool(
            "see",
            arguments={
                "image_path": "photo.png",
                "prompt": "Describe this image"
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
    "name": "see",
    "arguments": {
      "image_path": "photo.png",
      "prompt": "What objects are in this image?"
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
        "text": "{\"description\": \"...\", \"model\": \"qwen3.7-plus\", ...}"
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
    "see": {
      "command": "rvrb-see-mcp"
    },
    "hear": {
      "command": "rvrb-hear-mcp"
    },
    "verify": {
      "command": "rvrb-verify-mcp"
    }
  }
}
```

Example workflow:
1. Analyze images with `see` tool
2. Analyze audio with `hear` tool
3. Verify claims with `verify` tool
