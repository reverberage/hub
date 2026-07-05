# reverberage — hub

The meta-repository for the [reverberage](https://github.com/reverberage) ecosystem.

**Composable Python tools for natural language workflows.** Ingest, generate, verify, transform — across audio, video, and text.

## Satellites

Each satellite is an independent Python package — usable alone or together.

| Satellite | Repo | Package | Status |
|-----------|------|---------|--------|
| **transcriber** | [reverberage/transcriber](https://github.com/reverberage/transcriber) | `rvrb-transcriber` | ![alpha](https://img.shields.io/badge/maturity-alpha-crimson) |
| **verify** | — | `rvrb-verify` | planned |
| **transform** | — | `rvrb-transform` | planned |
| **scout** | — | `rvrb-scout` | planned |

## Demos

- [**lo6 — Newsroom OS**](./demos/lo6/) — A conceptual demo showcasing how reverberage satellites compose into an AI-powered newsroom workflow (triage → research → draft → review → publish).

## Philosophy

- Each satellite does ONE thing. Audio in, text out. Claim in, verdict out.
- Each satellite is independently `pip install`-able and usable.
- Each satellite can connect to any MCP-compatible agentic system.
- No monolith. No framework lock-in. No "you must use our entire ecosystem."

## Docs

| Doc | Description |
|-----|-------------|
| [Satellite Protocol](./docs/satellite-protocol.md) | Build, package, and naming conventions |
| [Architecture](./docs/architecture.md) | Hub/satellite model and composition patterns |
| [Roadmap](./docs/roadmap.md) | Shipped satellites and planned priorities |

## License

Apache-2.0 © Juan Manuel Daza
