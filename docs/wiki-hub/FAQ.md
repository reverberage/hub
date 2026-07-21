# FAQ

Common questions about the reverberage hub.

## General

### What is reverberage?

reverberage is a hub-and-satellite ecosystem of composable, MCP-native Python packages. Each satellite does exactly one thing (audio transcription, claim verification, text transformation, etc.) and can be used alone or composed into pipelines.

### What does "reverberage" mean?

It's a portmanteau of "reverberate" and "collage" — reflecting the composable, echoing nature of the satellite ecosystem.

### Is this related to any other project?

No. reverberage is an independent project. It uses Qwen models from Alibaba Cloud for its free quota, but is not affiliated with Alibaba.

## Satellites

### Which satellites are available?

| Satellite | Status | Description |
|-----------|--------|-------------|
| `rvrb-transcriber` | alpha | Audio/video transcription |
| `rvrb-verify` | alpha | Claim verification |
| `rvrb-transform` | alpha | Text transformation |
| `rvrb-hear` | alpha | Audio comprehension |
| `rvrb-see` | alpha | Image understanding |

### Are the satellites stable?

All satellites are in **alpha** status. Breaking changes are permitted. Use at your own risk.

### Can I use satellites without the hub?

Yes. Each satellite is independently `pip install`-able. The hub is only needed for development, scaffolding new satellites, and orchestration.

### Can I compose satellites?

Yes. Satellites compose via Unix-style pipelines:

```bash
rvrb-transcriber meeting.mp3 | rvrb-verify
```

## Models

### What models does reverberage use?

Primarily Qwen models from Alibaba Cloud's free quota. See [Model Catalog](Model-Catalog) for the full list.

### Do I need to pay for the models?

No. The Qwen free quota provides 103M tokens across 81 models, expiring September 28, 2026. No credit card required.

### Can I use OpenAI or local models?

Yes. All satellites support multiple providers via the `ModelProvider` Protocol:

```bash
rvrb-verify "claim" --provider openai
rvrb-verify "claim" --provider local
```

### What happens when the free quota expires?

The free quota expires September 28, 2026. After that, you'll need to use paid API keys or local models.

## Development

### How do I create a new satellite?

```bash
python scripts/scaffold-satellite.py <name>
```

This generates a complete satellite skeleton following [satellite protocol v2](Satellite-Protocol).

### How do I contribute?

See [Contributing](Contributing) for the full guide. In short: fork, branch, develop, test, PR.

### What is SDD?

Spec-Driven Development. An 8-phase pipeline for managing changes:

```
explore → propose → spec → design → tasks → apply → verify → archive
```

Run with `/sdd-new "description"` in opencode.

### What is N3RVERBERAGE?

The orchestration agent in the hub. It coordinates SDD workflows, manages the project board, and handles memory persistence.

## MCP

### What is MCP?

Model Context Protocol. A standard for connecting AI models to external tools and data sources. All satellites expose MCP servers for integration with Claude Desktop, Continue.dev, and other MCP clients.

### How do I use satellites with Claude Desktop?

Add to your Claude Desktop config:

```json
{
  "mcpServers": {
    "transcriber": {
      "command": "rvrb-transcriber-mcp"
    },
    "verify": {
      "command": "rvrb-verify-mcp"
    }
  }
}
```

### Can I use satellites without MCP?

Yes. Satellites work as CLI tools and Python libraries. MCP is optional.

## Provider setup

### How do I get a Qwen API key?

1. Go to [Alibaba Cloud Model Studio](https://dashscope.console.aliyun.com/)
2. Sign up (Singapore region, no credit card)
3. Activate Model Studio
4. Generate API key
5. Set `export DASHSCOPE_API_KEY="sk-..."`

### Can I use multiple providers?

Yes. Each satellite can use a different provider:

```python
from rvrb_verify import get_provider

qwen = get_provider(provider="qwen")
openai = get_provider(provider="openai")
```

### What if I don't set any API key?

The satellite will use the default provider (Qwen) and fail if `DASHSCOPE_API_KEY` is not set. Set the env var or use `--provider local` for offline operation.

## Troubleshooting

### Error: "DASHSCOPE_API_KEY is not set"

Set the environment variable:

```bash
export DASHSCOPE_API_KEY="sk-..."
```

### Error: "All models exhausted"

The Qwen free quota for a specific model is exhausted. Rotate to the next model:

```bash
python scripts/qwen_fallback.py --rotate
```

Or use a different provider:

```bash
rvrb-verify "claim" --provider openai
```

### Error: "Module not found"

Install the satellite:

```bash
pip install rvrb-<name>
```

### Satellite tests fail

Run the quality gate:

```bash
ruff check .
ruff format --check .
mypy .
pytest
```

Fix any issues before submitting a PR.

## License

### What license does reverberage use?

Apache-2.0 for all satellites and the hub.

### Can I use reverberage commercially?

Yes. Apache-2.0 permits commercial use, modification, and distribution.

### Do I need to attribute reverberage?

Apache-2.0 requires preserving copyright notices. Include the license in distributions.
