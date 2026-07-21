# reverberage hub

**Meta-repository for the reverberage ecosystem.** Documentation, roadmaps, scaffold scripts, and orchestration agent.

Part of the [reverberage](https://github.com/reverberage) ecosystem — composable MCP-native toolkits for audio, video, and text.

## What is reverberage?

reverberage is a **hub-and-satellite** ecosystem of composable, MCP-native Python packages. Each satellite does exactly one thing and can be used alone or composed into pipelines.

## Satellites

| Satellite | Package | Modality | Description |
|-----------|---------|----------|-------------|
| [transcriber](https://github.com/reverberage/rvrb-transcriber) | `rvrb-transcriber` | AUDIO→TEXT | Audio/video transcription |
| [verify](https://github.com/reverberage/rvrb-verify) | `rvrb-verify` | TEXT→TEXT | Claim verification |
| [transform](https://github.com/reverberage/rvrb-transform) | `rvrb-transform` | TEXT→TEXT | Text transformation |
| [hear](https://github.com/reverberage/rvrb-hear) | `rvrb-hear` | AUDIO→TEXT | Audio comprehension |
| [see](https://github.com/reverberage/rvrb-see) | `rvrb-see` | IMAGE→TEXT | Image understanding |

## Wiki pages

| Page | Description |
|------|-------------|
| [Architecture](Architecture) | Hub-and-satellite model |
| [Satellite Protocol](Satellite-Protocol) | Protocol v2 specification |
| [Roadmap](Roadmap) | Shipped and planned satellites |
| [Model Catalog](Model-Catalog) | Qwen free quota models |
| [Contributing](Contributing) | How to contribute |
| [Development](Development) | Hub development setup |
| [FAQ](FAQ) | Common questions |

## Quick start

```bash
# Install a satellite
pip install rvrb-transcriber

# Use it
rvrb-transcribe audio.mp3

# Compose satellites
rvrb-transcribe meeting.mp3 | rvrb-verify
```

## License

Apache-2.0
