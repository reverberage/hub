# Roadmap

## Shipped

| Satellite | Package | Status | Modality | Description |
|-----------|---------|--------|----------|-------------|
| **transcriber** | `rvrb-transcriber` | alpha | AUDIO→TEXT | AI-powered audio transcription |
| **verify** | `rvrb-verify` | alpha | TEXT→TEXT | Claim verification engine (two-phase pipeline) |
| **transform** | `rvrb-transform` | alpha | TEXT→TEXT | General-purpose text transformation |

## Planned — Tier 1 (Core Modalities)

| # | Satellite | Modality | Model | What |
|---|-----------|----------|-------|------|
| 1 | **see** | IMAGE→TEXT | `qwen3.7-plus` | Image understanding, OCR, visual description |
| 2 | **hear** | AUDIO→TEXT | `qwen3.5-omni-plus` | Multimodal audio comprehension |
| 3 | **speak** | TEXT→AUDIO | `cosyvoice-v3.5-plus` | Text-to-speech via DashScope API |

## Planned — Tier 2 (Composable Pipelines)

| # | Satellite | Modality | Model | What |
|---|-----------|----------|-------|------|
| 4 | **summarize** | TEXT→TEXT | `qwen3.6-flash` | Long-document summarization (1M context) |
| 5 | **translate** | TEXT→TEXT | `qwen-mt-plus` | High-quality translation |
| 6 | **extract** | TEXT→TEXT | `qwen3-coder-plus` | Structured data extraction |
| 7 | **reason** | TEXT→TEXT | `qwq-plus` | Multi-hop reasoning and chain-of-thought |

## Planned — Tier 3 (Specialized)

| # | Satellite | Modality | Model | What |
|---|-----------|----------|-------|------|
| 8 | **codegen** | TEXT→TEXT | `qwen3-coder-plus` | Code generation with tool calling |
| 9 | **review** | TEXT→TEXT | `qwen3.7-plus` | Code review against standards |
| 10 | **detect** | IMAGE→TEXT | `qwen3.7-plus` | Object detection, scene analysis |
| 11 | **subtitles** | AUDIO→TEXT | `qwen3-asr-flash` | Subtitle generation (SRT/VTT) |

## Infrastructure

| Item | Status | Description |
|------|--------|-------------|
| **Satellite protocol v2** | done | Multimodal I/O contracts, provider resolution, mock patterns |
| **Scaffold script** | done | `scripts/scaffold-satellite.py` — generates v2 skeletons |
| **Qwen fallback rotation** | done | `scripts/qwen_fallback.py` — 81-model quota rotation |
| **opencode Qwen config** | done | Multimodal models in `/models`, auto-fallback |

## Model Strategy

The Qwen free quota (103M tokens across 81 LLM models, expiring Sept 2026) is the fuel. Each satellite targets a specific model family.

| Tier | Models Used | Token Budget |
|------|------------|:------------:|
| Tier 1 (core) | qwen3-coder-plus, qwen3.7-plus, qwen3.5-omni-plus | ~4M tokens |
| Tier 2 (compose) | qwen3.6-flash, qwen-mt-plus, qwq-plus | ~4M tokens |
| Tier 3 (specialize) | qwen3-asr-flash, qwen3.7-plus | ~2M tokens |
| Development (opencode) | qwen3-coder-plus | ~20M tokens |

See [Model Catalog](Model-Catalog) for the complete list of available models.

## North Star

Every satellite is a composable, MCP-native Python package. No monolith. Each exploits a specific Qwen model family capability. Together they form a multimodal toolkit for text, audio, image, video, and speech — all running on zero-cost Alibaba Cloud free quota.
