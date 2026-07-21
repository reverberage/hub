# Model Catalog

The Qwen free quota provides 103M tokens across 81 LLM models, expiring September 28, 2026.

## Summary

| Category | Total | With Quota | Exhausted | Token Quota |
|----------|:-----:|:----------:|:---------:|:-----------:|
| LLM (text) | 91 | 81 | 10 | 1M tokens each |
| Vision (image/video) | 61 | 61 | 0 | Generations |
| Multimodal (omni) | 19 | 17 | 2 | 1M tokens each |
| Audio (ASR/TTS) | 41 | 40 | 1 | Seconds/chars |
| Embedding + Rerank | 5 | 5 | 0 | 1M tokens each |
| **Total** | **217** | **204** | **13** | |

## Key models (not exhausted)

### Flagship

| Model | Context | Vision | Thinking | Tool Use |
|-------|:-------:|:------:|:--------:|:--------:|
| `qwen3.7-max` | 1M | No | Yes | Yes |
| `qwen3.7-plus` | 1M | Yes | Yes | Yes |

### Coding

| Model | Context | Thinking | Tool Use |
|-------|:-------:|:--------:|:--------:|
| `qwen3-coder-plus` | 1M | Yes | Yes |
| `qwen3-coder-flash` | 1M | Yes | Yes |
| `qwen3-coder-next` | 256K | Yes | Yes |

### Audio comprehension

| Model | Context | Audio | Video |
|-------|:-------:|:-----:|:-----:|
| `qwen3.5-omni-plus` | 64K | Yes | Up to 1h |
| `qwen3.5-omni-flash` | 64K | Yes | Up to 1h |

### Third-party

| Model | Context | Thinking | Notes |
|-------|:-------:|:--------:|-------|
| `deepseek-v3.2` | 128K | Yes | Reasoning |
| `kimi-k2.7-code` | — | Yes | Coding |
| `glm-5.2` | 198K | Yes | General |

## Exhausted models (10)

| Model | Status |
|-------|--------|
| `qwen-plus` | Exhausted |
| `qwen-max` | Exhausted |
| `qwen-turbo` | Exhausted |
| `qwen-flash` | Exhausted |
| `deepseek-v4-pro` | Exhausted |
| `deepseek-v4-flash` | Exhausted |
| `qwen3.7-plus` (base) | Not Supported |
| `qwen3.7-max` (base) | Not Supported |
| `qwen-plus-character-ja` | No Free Quota |
| `qwen-plus-2025-01-25` | No Free Quota |

## Satellite model mapping

| Satellite | Primary Model | Fallback |
|-----------|--------------|----------|
| transcriber | Whisper (OpenAI/local) | — |
| verify | `qwen3-coder-plus` | `qwen3.7-plus` |
| transform | `qwen3-coder-plus` | `qwen3.6-flash` |
| hear | `qwen3.5-omni-plus` | — |
| see | `qwen3.7-plus` | — |
| speak | `cosyvoice-v3.5-plus` | — |
| summarize | `qwen3.6-flash` | — |
| translate | `qwen-mt-plus` | — |
| extract | `qwen3-coder-plus` | — |
| reason | `qwq-plus` | — |

## Quota rotation

The `scripts/qwen_fallback.py` script manages quota rotation for opencode:

```bash
# Check status of all models
python scripts/qwen_fallback.py --status

# Rotate to next available model
python scripts/qwen_fallback.py --rotate

# Force specific model
python scripts/qwen_fallback.py --rotate --model qwen3-coder-plus
```

## Full catalog

See [qwen-model-catalog.md](https://github.com/reverberage/hub/blob/main/docs/qwen-model-catalog.md) for the complete 217-model catalog with pricing and capabilities.

## Region

All free quota is in the **Singapore (International)** region. API keys are not interchangeable across regions.

**Endpoint**: `https://dashscope-intl.aliyuncs.com/compatible-mode/v1`

## Expiration

All free quota expires **September 28, 2026** (90-day validity from account activation).
