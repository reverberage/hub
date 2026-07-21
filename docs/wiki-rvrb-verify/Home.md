# rvrb-verify

**Claim verification engine.** Claim in, verdict out.

Part of the [reverberage](https://github.com/reverberage) ecosystem — composable MCP-native toolkits for audio, video, and text.

## What it does

Takes a claim text and produces a verdict with confidence score, summary, evidence, and sources. Uses a two-phase pipeline: search (with tools) → judge (verdict).

## Quick start

```bash
pip install rvrb-verify
export DASHSCOPE_API_KEY="sk-..."
rvrb-verify "The sky is blue"
```

## Wiki pages

| Page | Description |
|------|-------------|
| [Getting Started](Getting-Started) | Installation, provider setup, first verification |
| [CLI Reference](CLI-Reference) | All flags, options, and examples |
| [Python API](Python-API) | Programmatic usage from Python code |
| [Strategies](Strategies) | fact-check, legal, and research strategies |
| [Output Formats](Output-Formats) | Text and JSON output details |
| [MCP Server](MCP-Server) | Integrate with MCP-compatible agents |
| [Architecture](Architecture) | Internal design, two-phase pipeline |
| [Development](Development) | Contributing, testing, adding strategies |
| [FAQ](FAQ) | Common questions and troubleshooting |

## Strategies

| Strategy | Description | Tools |
|----------|-------------|-------|
| `fact-check` | General claim verification | Web search, news search |
| `legal` | Legal analysis | Statute search, case law search |
| `research` | Academic validation | Paper search, arXiv search |

## License

Apache-2.0 — same as the reverberage ecosystem.
