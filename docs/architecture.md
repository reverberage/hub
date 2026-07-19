# Architecture

## Hub and satellite model

reverberage is a **hub-and-satellite** ecosystem:

- **Hub** (`reverberage/hub`): meta-repository. Contains documentation, roadmaps,
  scaffold scripts, and the N3RVERBERAGE orchestration agent. No runtime code.
- **Satellite**: independent, pip-installable Python package. Each satellite
  does exactly one thing and can be used alone or composed into pipelines.

## Satellite anatomy

Every satellite follows the [satellite protocol](./satellite-protocol.md):

- Built with `hatchling`, packaged as `rvrb-<name>`
- CLI via `typer`, data models via `pydantic` v2
- MCP-native: exposes tools/resources/prompts via `mcp.server.FastMCP`
- Python `>=3.11`, Apache-2.0 licensed

New satellites are scaffolded via:

```bash
python .opencode/scripts/scaffold-satellite.py <name>
```

## Composition pattern

Satellites compose into domain-specific workflows. Text-consuming satellites
accept stdin when no positional argument is given. Each satellite writes to
stdout by default. This enables Unix-style pipeline composition.

### Working pipeline examples

**Transcribe → Verify claims in the transcript:**

```bash
rvrb-transcriber meeting.mp3 | rvrb-verify
```

**Transcribe → JSON → Verify with model override:**

```bash
rvrb-transcriber audio.mp3 | rvrb-verify --model qwen3-coder-plus
```

**Multi-step chain (planned):**

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

Each satellite can connect to any MCP-compatible agentic system.
No framework lock-in. No "you must use our entire ecosystem."

Satellites that expose an MCP server do so via `mcp.run(transport='stdio')`,
making them compatible with Claude Desktop, Continue.dev, and any MCP client.

## Design constraints

- **No monolith**: each satellite is independently installable and usable
- **No framework lock-in**: satellites are plain Python packages, not plugins
- **Single responsibility**: one satellite, one job, one I/O contract
- **Independence**: you can use `rvrb-transcriber` without knowing `rvrb-verify` exists
