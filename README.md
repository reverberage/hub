# reverberage — hub

Composable, MCP-native toolkits for audio, video, and text processing.
Build pipelines. Not monoliths.

The governance meta-repository for the [reverberage](https://github.com/reverberage) ecosystem.

The hub is three things:

1. **Governance platform** — the single source of truth for the satellite protocol, architecture decisions, and roadmap
2. **Orchestration platform** — AI-assisted development tooling (Spec-Driven Development pipeline, agents, skills, judgment-day review)
3. **Satellite protocol** — the contract every reverberage satellite follows: build, package, naming, and MCP conventions

**This is not a runtime project.** The hub contains no application code. Satellites are separate, independently installable Python packages.

## Satellites

Each satellite is an independent `pip install`-able Python package — usable alone or composed into pipelines.

| Satellite | Package | Status |
|-----------|---------|--------|
| **transcriber** | `rvrb-transcriber` | ![alpha](https://img.shields.io/badge/maturity-alpha-crimson) |
| **verify** | `rvrb-verify` | ![alpha](https://img.shields.io/badge/maturity-alpha-crimson) |
| **transform** | `rvrb-transform` | ![alpha](https://img.shields.io/badge/maturity-alpha-crimson) |

See the [roadmap](./docs/roadmap.md) for planned satellites.

## Composition

Satellites compose via Unix pipelines — each writes to stdout, text-consuming
satellites read from stdin.

```bash
# Transcribe a meeting, verify the claims in the transcript
rvrb-transcriber meeting.mp3 | rvrb-verify

# Full audit trail: transcribe → JSON → verify with a specific model
rvrb-transcriber audio.mp3 | rvrb-verify --model qwen3.7-plus

# Three-satellite chain: transcribe → verify → transform
rvrb-transcriber meeting.mp3 | rvrb-verify | rvrb-transform "format as meeting minutes"

# Transform with JSON output
rvrb-transform "summarize" "The quick brown fox jumps over the lazy dog" --json
```

For programmatic composition, see the [Satellite Protocol v2](./docs/satellite-protocol-v2.md)
(`MediaInput`/`MediaOutput` API).

## Philosophy

- Each satellite does **one thing**. Audio in, text out. Claim in, verdict out.
- Each satellite is independently usable — no monolith, no framework lock-in.
- Each satellite can connect to any MCP-compatible agentic system.
- The hub exists to make satellites easy to build, consistent to use, and fast to compose.

## How to Contribute

1. Read the [Satellite Protocol](./docs/satellite-protocol.md)
2. Scaffold a new satellite: `/new-satellite <name>`
3. Run the SDD pipeline for changes: `/sdd-new <change description>`
4. See [CONTRIBUTING.md](./CONTRIBUTING.md) for full details

## Docs

| Doc | Description |
|-----|-------------|
| [Satellite Protocol](./docs/satellite-protocol.md) | Build, package, and naming conventions |
| [Satellite Protocol v2](./docs/satellite-protocol-v2.md) | Media I/O types, provider contract, engine spec |
| [Architecture](./docs/architecture.md) | Hub/satellite model and composition patterns |
| [Roadmap](./docs/roadmap.md) | Shipped satellites and planned priorities |

## License

Apache-2.0 © Juan Manuel Daza
