# Roadmap

## Shipped

| Satellite | Package | Status | Modality | Description |
|-----------|---------|--------|----------|-------------|
| **transcriber** | `rvrb-transcriber` | alpha | AUDIO→TEXT | AI-powered audio transcription |
| **verify** | `rvrb-verify` | alpha | TEXT→TEXT | Claim verification engine (two-phase pipeline) |

## The Harvest — Satellites by Modality

Every Qwen model family maps to a satellite capability. Each satellite exploits a specific
model's strengths. All follow [satellite protocol v2](./satellite-protocol-v2.md).

### Tier 1 — Core Modalities (build next)

| # | Satellite | Modality | Model | What |
|---|-----------|----------|-------|------|
| 1 | **transform** | TEXT→TEXT | `qwen3-coder-plus` | Format conversion, summarization, restructuring |
| 2 | **see** | IMAGE→TEXT | `qwen3.7-plus` | Image understanding, OCR, visual description |
| 3 | **hear** | AUDIO→TEXT | `qwen3.5-omni-plus` | Multimodal audio comprehension (beyond ASR) |
| 4 | **speak** | TEXT→AUDIO | `cosyvoice-v3.5-plus` | Text-to-speech via DashScope native API |

### Tier 2 — Composable Pipelines

| # | Satellite | Modality | Model | What |
|---|-----------|----------|-------|------|
| 5 | **summarize** | TEXT→TEXT | `qwen3.6-flash` | Long-document summarization (1M context) |
| 6 | **translate** | TEXT→TEXT | `qwen-mt-plus` | High-quality translation |
| 7 | **extract** | TEXT→TEXT | `qwen3-coder-plus` | Structured data extraction from unstructured text |
| 8 | **reason** | TEXT→TEXT | `qwq-plus` | Multi-hop reasoning and chain-of-thought |

### Tier 3 — Specialized

| # | Satellite | Modality | Model | What |
|---|-----------|----------|-------|------|
| 9 | **codegen** | TEXT→TEXT | `qwen3-coder-plus` | Code generation with tool calling |
| 10 | **review** | TEXT→TEXT | `qwen3.7-plus` | Code review against standards |
| 11 | **detect** | IMAGE→TEXT | `qwen3.7-plus` | Object detection, scene analysis |
| 12 | **subtitles** | AUDIO→TEXT | `qwen3-asr-flash` | Subtitle generation (SRT/VTT) |

### Killed

| Satellite | Reason |
|-----------|--------|
| **scout** | Scraping/crawling infrastructure belongs elsewhere. Replaced by tiered modality harvest. |

## Model Strategy

Our Qwen free quota (103M tokens across 81 LLM models, expiring Sept 2026) is the fuel.
Each satellite targets a specific model family:

| Tier | Models Used | Token Budget |
|------|------------|:------------:|
| Tier 1 (core) | qwen3-coder-plus, qwen3.7-plus, qwen3.5-omni-plus, cosyvoice-v3.5-plus | ~4M tokens |
| Tier 2 (compose) | qwen3.6-flash, qwen-mt-plus, qwq-plus | ~4M tokens |
| Tier 3 (specialize) | qwen3-asr-flash, qwen3.7-plus | ~2M tokens |
| Development (opencode) | qwen3-coder-plus | ~20M tokens |

See `docs/stage-a-catalog.md` for the complete 217-model catalog with quotas.

## Infrastructure (hub)

| Item | Status | Description |
|------|--------|-------------|
| **Satellite protocol v2** | done | Multimodal I/O contracts, provider resolution, mock patterns |
| **Scaffold script** | done | `scripts/scaffold-satellite.py` — generates v2 skeletons |
| **Qwen fallback rotation** | done | `scripts/qwen_fallback.py` — 81-model quota rotation |
| **opencode Qwen config** | done | Multimodal models in `/models`, auto-fallback |

## North Star

Every satellite is a composable, MCP-native Python package. No monolith.
Each exploits a specific Qwen model family capability. Together they form a
multimodal toolkit for text, audio, image, video, and speech — all running on
zero-cost Alibaba Cloud free quota.
