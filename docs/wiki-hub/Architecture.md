# Architecture

## Hub and satellite model

reverberage is a **hub-and-satellite** ecosystem:

- **Hub** (`reverberage/hub`): meta-repository. Contains documentation, roadmaps, scaffold scripts, and the N3RVERBERAGE orchestration agent. No runtime code.
- **Satellite**: independent, pip-installable Python package. Each satellite does exactly one thing and can be used alone or composed into pipelines.

## Satellite anatomy

Every satellite follows the [satellite protocol](Satellite-Protocol):

- Built with `hatchling`, packaged as `rvrb-<name>`
- CLI via `typer`, data models via `pydantic` v2
- MCP-native: exposes tools/resources/prompts via `mcp.server.FastMCP`
- Python `>=3.11`, Apache-2.0 licensed

New satellites are scaffolded via:

```bash
python scripts/scaffold-satellite.py <name>
```

## Composition pattern

Satellites compose into domain-specific workflows. Text-consuming satellites accept stdin when no positional argument is given. Each satellite writes to stdout by default. This enables Unix-style pipeline composition.

### Working pipeline examples

**Transcribe → Verify claims in the transcript:**

```bash
rvrb-transcriber meeting.mp3 | rvrb-verify
```

**Transcribe → JSON → Verify with model override:**

```bash
rvrb-transcriber audio.mp3 | rvrb-verify --model qwen3-coder-plus
```

**Working three-satellite chain:**

```
transcriber (audio → text)
    → verify (claim → verdict)
    → transform (text → formatted output)
```

The same satellites compose differently for other domains:

```
transcriber (meeting audio → text)
    → transform (text → meeting minutes)
    → verify (action items → accountability check)
```

## MCP-native design

Each satellite connects to any MCP-compatible agentic system. No framework lock-in. No "you must use our entire ecosystem."

Satellites that expose an MCP server do so via `mcp.run(transport='stdio')`, making them compatible with Claude Desktop, Continue.dev, and any MCP client.

## Design constraints

- **No monolith**: each satellite is independently installable and usable
- **No framework lock-in**: satellites are plain Python packages, not plugins
- **Single responsibility**: one satellite, one job, one I/O contract
- **Independence**: you can use `rvrb-transcriber` without knowing `rvrb-verify` exists

## Provider abstraction

All satellites use a provider-agnostic model. The `ModelProvider` Protocol allows switching between Qwen, OpenAI, and local providers without changing satellite code.

```python
from rvrb_verify import get_provider

# Qwen (default)
provider = get_provider(provider="qwen")

# OpenAI
provider = get_provider(provider="openai")

# Local (Ollama/vLLM)
provider = get_provider(provider="local")
```

## N3RVERBERAGE orchestration

The hub contains the N3RVERBERAGE orchestration agent, which coordinates SDD (Spec-Driven Development) workflows across satellites. It manages:

- SDD pipeline (explore → propose → spec → design → tasks → apply → verify → archive)
- Project board tracking
- Memory persistence via MAGI (ChromaDB + SQLite)
- A2A task routing

## Repository structure

```
hub/
├── docs/                    # Architecture, protocol specs, roadmap
├── scripts/                 # scaffold-satellite.py, qwen_fallback.py
├── tests/                   # Hub-level tests
├── .opencode/               # Agent definitions, skills, commands
├── AGENTS.md                # Coding standards
├── CONTRIBUTING.md          # Contribution guide
├── README.md                # Package overview
└── opencode.json            # opencode config (generated)
```
