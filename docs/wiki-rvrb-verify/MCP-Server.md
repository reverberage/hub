# MCP Server

rvrb-verify exposes an MCP (Model Context Protocol) server for integration with AI agents.

## Installation

```bash
pip install "rvrb-verify[mcp]"
```

## Tool definition

The MCP server exposes a single tool:

### `verify`

Verify a claim using the specified strategy.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|:--------:|-------------|
| `claim_text` | `str` | Yes | The claim to verify |
| `strategy` | `str` | No | Strategy name (default: `"fact-check"`) |

**Returns:** `dict` — Verdict as JSON-serializable dictionary.

## Usage

### Start the server

```bash
rvrb-verify-mcp
```

The server runs on stdio transport, compatible with any MCP client.

### Claude Desktop

Add to your Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "verify": {
      "command": "rvrb-verify-mcp",
      "env": {
        "DASHSCOPE_API_KEY": "sk-..."
      }
    }
  }
}
```

### Continue.dev

Add to your Continue config (`~/.continue/config.json`):

```json
{
  "mcpServers": [
    {
      "name": "verify",
      "command": "rvrb-verify-mcp",
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
    command="rvrb-verify-mcp",
    env={"DASHSCOPE_API_KEY": "sk-..."}
)

async with stdio_client(server_params) as (read, write):
    async with ClientSession(read, write) as session:
        await session.initialize()
        
        # Call the verify tool
        result = await session.call_tool(
            "verify",
            arguments={
                "claim_text": "The sky is blue",
                "strategy": "fact-check"
            }
        )
        
        print(result.content)
```

## JSON-RPC example

The MCP server uses JSON-RPC 2.0 over stdio:

```json
// Request
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/call",
  "params": {
    "name": "verify",
    "arguments": {
      "claim_text": "The sky is blue",
      "strategy": "fact-check"
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
        "text": "{\"verdict\": \"true\", \"confidence\": 0.95, ...}"
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

## Error handling

MCP tool calls return errors in the standard MCP format:

```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "error": {
    "code": -32000,
    "message": "Unknown strategy: invalid"
  }
}
```

## Integration with other satellites

Combine with other reverberage satellites in an MCP pipeline:

```json
{
  "mcpServers": {
    "transcriber": {
      "command": "rvrb-transcriber-mcp"
    },
    "verify": {
      "command": "rvrb-verify-mcp"
    },
    "transform": {
      "command": "rvrb-transform-mcp"
    }
  }
}
```

Example workflow:
1. Transcribe audio with `transcriber` tool
2. Extract claims from transcript
3. Verify each claim with `verify` tool
4. Format results with `transform` tool
