# Qwen Model Catalog — Complete Reference

> Pricing shown for **Singapore (International)** region unless noted. Beijing/HK/Frankfurt/US/JP pricing differs.
> Output pricing in Thinking mode = (chain of thought tokens + answer tokens), both at the listed output rate.
> `[CC]` = context cache discount available. `[Batch]` = 50% batch inference discount on input+output.

---

## 1. TEXT GENERATION MODELS

### Qwen3.7 Series (Current Flagship)

| Model ID | Context | Thinking | Vision | Tool Use | Structured Output |
|---|---|---|---|---|---|
| `qwen3.7-max` ★ | 1M | Yes | No (text only) | Yes | Yes |
| `qwen3.7-plus` ★ | 1M | Yes | Yes (2048 imgs, 64 vids) | Yes | Yes |

**Snapshots:**
- `qwen3.7-max` = `qwen3.7-max-2026-05-20`; also `qwen3.7-max-2026-06-08`, `qwen3.7-max-preview` (= `qwen3.7-max-2026-05-17`)
- `qwen3.7-plus` = `qwen3.7-plus-2026-05-26`

**Pricing (Singapore, per 1M tokens):**

| Model | Input (≤1M) | Output (non-thinking) | Output (thinking: CoT+answer) |
|---|---|---|---|
| `qwen3.7-max` [CC] | $2.50 | $7.50 | $7.50 |
| `qwen3.7-plus` [CC] (≤256K) | $0.40 | $1.60 | $1.60 |
| `qwen3.7-plus` [CC] (256K–1M) | $1.20 | $4.80 | $4.80 |

**Free quota:** 1M tokens for both models (Singapore, 90-day validity).

### Qwen3.6 Series

| Model ID | Context | Thinking | Vision | Tool Use | Structured Output |
|---|---|---|---|---|---|
| `qwen3.6-max-preview` | 256K | Yes | No | Yes (no built-in tools) | Yes |
| `qwen3.6-plus` | 1M | Yes | Yes (256 imgs, 64 vids) | Yes | Yes |
| `qwen3.6-flash` | 1M | Yes | Yes (256 imgs, 64 vids) | Yes | Yes |

**Snapshots:** `qwen3.6-plus-2026-04-02`, `qwen3.6-flash-2026-04-16`, `qwen3.6-35b-a3b`

**Pricing (Singapore, per 1M tokens):**

| Model | Input | Output (non-thinking) | Output (thinking) |
|---|---|---|---|
| `qwen3.6-max-preview` [CC] (≤128K) | $1.30 | $7.80 | $7.80 |
| `qwen3.6-max-preview` [CC] (128K–256K) | $2.00 | $12.00 | $12.00 |
| `qwen3.6-plus` (≤256K) | $0.50 | $3.00 | $3.00 |
| `qwen3.6-plus` (256K–1M) | $2.00 | $6.00 | $6.00 |

### Qwen3.5 Series

| Model ID | Context | Thinking | Vision | Tool Use | Structured Output |
|---|---|---|---|---|---|
| `qwen3.5-plus` | 1M | Yes | Yes (256 imgs, 64 vids) | Yes | Yes |
| `qwen3.5-flash` | 1M | Yes | Yes (256 imgs, 64 vids) | Yes | Yes |
| `qwen3.5-397b-a17b` | 256K | Yes | Yes (256 imgs, 64 vids) | Yes | Yes |
| `qwen3.5-122b-a10b` | 256K | Yes | Yes (256 imgs, 64 vids) | Yes | Yes |
| `qwen3.5-27b` | 256K | Yes | Yes (256 imgs, 64 vids) | Yes | Yes |
| `qwen3.5-35b-a3b` | 256K | Yes | Yes (256 imgs, 64 vids) | Yes | Yes |

**Snapshots:** `qwen3.5-plus-2026-04-20`, `qwen3.5-plus-2026-02-15`, `qwen3.5-flash-2026-02-23`

**Pricing (Singapore, per 1M tokens):**

| Model | Input | Output (non-thinking) | Output (thinking) |
|---|---|---|---|
| `qwen3.5-plus` (≤256K) | $0.40 | $2.40 | $2.40 |
| `qwen3.5-plus` (256K–1M) | $0.50 | $3.00 | $3.00 |


### Qwen3 Series (Original)

| Model ID | Context | Thinking | Tool Use | Structured Output |
|---|---|---|---|---|
| `qwen3-max` [CC] | 256K | Yes | Yes | Yes |
| `qwen3-235b-a22b` | 256K | Yes | No built-in tools | Yes |
| `qwen3-235b-a22b-thinking-2507` | 256K | Yes (only) | No built-in tools | No |
| `qwen3-235b-a22b-instruct-2507` | 256K | No | No built-in tools | Yes |
| `qwen3-next-80b-a3b-thinking` | 256K | Yes (only) | No built-in tools | No |
| `qwen3-next-80b-a3b-instruct` | 256K | No | No built-in tools | Yes |
| `qwen3-32b` | 256K | Yes | Yes | Yes |
| `qwen3-30b-a3b` | 256K | Yes | Yes | Yes |
| `qwen3-30b-a3b-thinking-2507` | 256K | Yes (only) | No built-in tools | No |
| `qwen3-30b-a3b-instruct-2507` | 256K | No | No built-in tools | Yes |
| `qwen3-14b` | 256K | Yes | Yes | Yes |
| `qwen3-8b` | 256K | Yes | Yes | Yes |
| `qwen3-4b` | 256K | Yes | Yes | Yes |
| `qwen3-1.7b` | 256K | Yes | Yes | Yes |
| `qwen3-0.6b` | 256K | Yes | Yes | Yes |

**Snapshots:** `qwen3-max` = `qwen3-max-2026-01-23`; also `qwen3-max-2025-09-23`, `qwen3-max-preview`

**Pricing (Singapore, per 1M tokens):**

| Model | Input | Output (non-thinking) | Output (thinking) |
|---|---|---|---|
| `qwen3-max` [CC] (≤32K) | $1.20 | $6.00 | $6.00 |
| `qwen3-max` [CC] (32K–128K) | $2.40 | $12.00 | $12.00 |
| `qwen3-max` [CC] (128K–256K) | $3.00 | $15.00 | $15.00 |

### Legacy Qwen Models

#### qwen-plus (Legacy)

**Snapshots:** `qwen-plus` = `qwen-plus-2025-12-01`; `qwen-plus-latest`, `qwen-plus-2025-09-11`, `qwen-plus-2025-07-28`, `qwen-plus-2025-07-14`, `qwen-plus-2025-04-28`, `qwen-plus-2025-01-25`, `qwen-plus-2025-01-12`, `qwen-plus-2024-12-20`

| Model | Context | Thinking | Vision | Tool Use | Structured Output |
|---|---|---|---|---|---|
| `qwen-plus` | 1M | Yes | No | Yes | Yes |

**Pricing (Singapore, per 1M tokens):**

| Model | Input | Output (non-thinking) | Output (thinking) |
|---|---|---|---|
| `qwen-plus` (≤256K) | $0.40 | $1.20 | $4.00 |
| `qwen-plus` (256K–1M) | $1.20 | $3.60 | $12.00 |

#### qwen-max (Legacy)

**Snapshots:** `qwen-max` = `qwen-max-2025-01-25`; also `qwen-max-2024-09-19`

| Model | Context | Thinking | Pricing (Singapore) |
|---|---|---|---|
| `qwen-max` [Batch] | 128K | No | Input: $1.60, Output: $6.40 |

#### qwen-turbo (Legacy)

| Model ID | Context | Thinking | Output (non-thinking) |
|---|---|---|---|
| `qwen-turbo` | 1M | Yes | Same as qwen-plus pricing tier |

**Snapshots:** `qwen-turbo-latest`, `qwen-turbo-2025-01-25`

#### qwen-flash (Legacy)

| Model ID | Context | Thinking | Output (non-thinking) |
|---|---|---|---|
| `qwen-flash` | 1M | Supported | Lower cost than turbo |

**Snapshots:** `qwen-flash-latest`, `qwen-flash-2025-01-25`

#### qwen-long (Long Context)

**Snapshots:** `qwen-long` = `qwen-long-2025-01-25`, `qwen-long-latest`

| Model | Context | Thinking | Pricing (Singapore) |
|---|---|---|---|
| `qwen-long` | **10M** | No | Input: $0.50, Output: $2.00 |

#### Translation: qwen-mt

| Model | Context | Pricing (Singapore) |
|---|---|---|
| `qwen-mt-plus` | 16K | Input: $2.00, Output: $8.00 |
| `qwen-mt-turbo` | 16K | Input: $0.50, Output: $2.00 |
| `qwen-mt-flash` | 16K | Input: $0.15, Output: $0.60 |
| `qwen-mt-lite` | 16K | Input: $0.05, Output: $0.20 |

#### Role-playing

| Model | Context | Pricing (Singapore) |
|---|---|---|
| `qwen-plus-character` | 32K | — |
| `qwen-plus-character-ja` | 32K | — |
| `qwen-flash-character` | 8K | — |

#### Other Legacy

| Model | Context | Notes |
|---|---|---|
| `qwq-plus` | 128K | Thinking model, tool use, structured output |
| `qwen-omni-turbo` | 32K | Multimodal, text+audio+image |

---

## 2. VISION / MULTIMODAL MODELS

### Qwen3-VL (Native Vision-Language)

| Model ID | Context | Max Pixels/Image | Max Images | Max Videos | Max Video Duration | Tool Use | Structured Output |
|---|---|---|---|---|---|---|---|
| `qwen3-vl-plus` | 128K | 16M | 256 | 64 | 1h | Yes | Yes |
| `qwen3-vl-flash` | 128K | 16M | 256 | 64 | 1h | Yes | Yes |

**Snapshots:** `qwen3-vl-plus-2026-01-25`, `qwen3-vl-flash-2026-01-25`

### Qwen2.5-VL (via Model Studio)

| Model ID | Context | Vision |
|---|---|---|
| `qwen2.5-vl-72b-instruct` | 1M | Yes |
| `qwen2.5-vl-32b-instruct` | 1M | Yes |
| `qwen2.5-vl-7b-instruct` | 1M | Yes |
| `qwen2.5-vl-3b-instruct` | 1M | Yes |

### Qwen2.5-Omni (Multimodal)

| Model ID | Context | Notes |
|---|---|---|
| `qwen2.5-omni-7b` | 1M | Text+Image+Audio+Video, speech synthesis via Model Studio |

### Qwen3.5-Omni (Realtime Multimodal)

| Model ID | Context | Audio Input | Video Input | Notes |
|---|---|---|---|---|
| `qwen3.5-omni-plus` | 64K | Yes | Up to 1h, 512 vids | Text+Audio+Image+Video+Synthetic Speech |
| `qwen3.5-omni-plus-realtime` | Realtime | Yes | Yes | End-to-end voice conversation, WebSocket |
| `qwen3.5-omni-flash` | 64K | Yes | Up to 1h | Lighter variant |

### Qwen3-Omni (via Model Studio)

| Model ID | Context | Pricing (Singapore) |
|---|---|---|
| `qwen3-omni-flash` | — | Input: $0.15, Output: $0.60 |
| `qwen3-omni-flash-2025-10-22` | — | Same |

### Qwen-VL-OCR

| Model ID | Context |
|---|---|
| `qwen-vl-ocr` / `qwen-vl-ocr-latest` | 32K |
| `qwen-vl-ocr-2025-07-14` | 32K |

### QVQ (Visual Reasoning)

| Model ID | Context | Vision | Thinking |
|---|---|---|---|
| `qvq-max` | 128K | Yes | Yes (only) |
| `qvq-max-2025-08-28` | 128K | Yes | Yes |
| `qvq-plus` | 128K | Yes | Yes |
| `qvq-plus-2025-08-27` | 128K | Yes | Yes |

### Legacy Vision Models

- `qwen-vl-max` and snapshots
- `qwen-vl-plus` and snapshots

---

## 3. CODE-SPECIFIC MODELS

### Qwen3-Coder Series

| Model ID | Context | Thinking | Tool Use | Structured Output |
|---|---|---|---|---|
| `qwen3-coder-plus` | 1M | Yes | Yes | Yes |
| `qwen3-coder-flash` | 1M | Yes | Yes | Yes |
| `qwen3-coder-next` | 256K | Yes | Yes | Yes |
| `qwen3-coder-480b-a35b-instruct` | 256K | No | Yes | Yes |
| `qwen3-coder-30b-a3b-instruct` | 256K | No | Yes | Yes |

**Snapshots:** `qwen3-coder-plus-2025-09-23`, `qwen3-coder-plus-2025-07-22`, `qwen3-coder-flash-2025-07-28`

**Pricing (Singapore — Coding Plan):**

Coding Plan is a subscription model:
- Standard: 25,000 credits/seat/month
- Pro: 100,000 credits/seat/month
- Max: 250,000 credits/seat/month

Integrates with Qwen Code, VS Code, Cline, Claude Code, Cursor, OpenCode, etc.

---

## 4. AUDIO MODELS

### Speech Recognition (ASR)

| Model ID | Type | Pricing (Singapore) |
|---|---|---|
| `fun-asr-realtime` | Real-time ASR | Per audio hour |
| `fun-asr` | Batch ASR | Per audio hour |

Also available via multimodal: `qwen3.5-omni-plus-realtime`, `qwen3.5-omni-plus`

### Text-to-Speech (TTS)

| Model ID | Pricing |
|---|---|
| `cosyvoice-v3.5-plus` | Per character |
| `qwen-tts` (via DashScope API) | Per character |

### Music Generation

| Model ID | Pricing |
|---|---|
| `fun-music-v1` | Per generation |

### Qwen3-Omni-Captioner (Audio Captioning)

Available via Alibaba Cloud Model Studio API.

---

## 5. VIDEO GENERATION (Wan / HappyHorse Series)

### Wan2.7 Image

| Model ID | Notes |
|---|---|
| `wan2.7-image-pro` | Text-to-Image, highest quality |
| `wan2.6-t2i` | Text-to-Image (Qwen Cloud) |

### HappyHorse Video Generation

| Model ID | Type | Notes |
|---|---|---|
| `happyhorse-1.1-t2v` | Text-to-Video | Semantic understanding, cinematic shot control |
| `happyhorse-1.1-i2v` | Image-to-Video | Character ID consistency, audio-visual sync |
| `happyhorse-1.1-r2v` | Reference-to-Video | Reference-guided generation |
| `happyhorse-1.0-video-edit` | Video Editing | Natural language editing |

### Qwen-Image-2.0

| Model ID | Notes |
|---|---|
| `qwen-image-2.0-pro` | Full-featured: generation + editing, 1000-token prompts, text rendering |

**Pricing (video):** Per-second or per-generation based, varies by resolution and model. Check console for current rates.

---

## 6. EMBEDDING & RERANK MODELS

### Text Embedding

| Model ID | Dimensions | Max Input | Pricing (Singapore, per 1M tokens) |
|---|---|---|---|
| `text-embedding-v4` | 64–2048 (default 1024) | 8,192 | Input: $0.05 |
| `text-embedding-v3` | 512–1024 (default 1024) | 8,192 | Input: $0.05 |

### Multimodal Embedding

| Model ID | Dimensions | Max Input | Type | Pricing (Singapore) |
|---|---|---|---|---|
| `qwen3-vl-embedding` | 256–2560 (default 2560) | 32,000 | Fused + Independent vectors | Input: $0.15/1M tokens |
| `tongyi-embedding-vision-plus` | 64–1152 (default 1152) | 1,024 | Independent vectors only | Input: $0.15/1M tokens |
| `tongyi-embedding-vision-flash` | 64–768 (default 768) | 1,024 | Independent vectors only | Lower cost |

### Rerank

| Model ID | Max Tokens per Doc | Pricing (Singapore) |
|---|---|---|
| `qwen3-rerank` | 4,000 | Per document |
| `qwen3-vl-rerank` | 8,000 | Per document (multimodal) |

---

## 7. OPEN-WEIGHT MODELS (Hugging Face, Apache 2.0)

### Qwen3 Series (April 2025)

All Apache 2.0. All support hybrid thinking (Thinking + Non-Thinking mode in one model).

| Model | Params | Act. Params | Type | Layers | Native Context | Extended Context |
|---|---|---|---|---|---|---|
| `Qwen3-0.6B` | 0.6B | — | Dense | 28 | 32K | 128K (YaRN) |
| `Qwen3-1.7B` | 1.7B | — | Dense | 28 | 32K | 128K (YaRN) |
| `Qwen3-4B` | 4B | — | Dense | 36 | 32K | 128K (YaRN) |
| `Qwen3-8B` | 8B | — | Dense | 36 | 128K | — |
| `Qwen3-14B` | 14B | — | Dense | 40 | 128K | — |
| `Qwen3-32B` | 32B | — | Dense | 64 | 128K | — |
| `Qwen3-30B-A3B` | 30B | 3B | MoE (128/8) | 48 | 128K | — |
| `Qwen3-235B-A22B` | 235B | 22B | MoE (128/8) | 94 | 33K native | 131K (YaRN) |

**Also available:** Base models (non-instruct), FP8, AWQ, GPTQ, GGUF quantizations, MLX variants. Instruct-2507 and Thinking-2507 variants (separate Instruct-only and Thinking-only models).

### Qwen3.5 Series (Open-Weight)

| Model | Params | Act. Params | Type | Context |
|---|---|---|---|---|
| `Qwen3.5-0.8B` | 0.8B | — | Dense | — |
| `Qwen3.5-2B` | 2B | — | Dense | — |
| `Qwen3.5-4B` | 4B | — | Dense | — |
| `Qwen3.5-8B` | 8B | — | Dense | — |
| `Qwen3.5-14B` | 14B | — | Dense | — |
| `Qwen3.5-27B` | 27B | — | Dense | — |
| `Qwen3.5-32B` | 32B | — | Dense | — |
| `Qwen3.5-35B-A3B` | 35B | 3B | MoE | — |
| `Qwen3.5-122B-A10B` | 122B | 10B | MoE | — |
| `Qwen3.5-397B-A17B` | 397B | 17B | MoE | — |

### Qwen3-Next (Open-Weight)

| Model | Params | Act. Params | Type | Context |
|---|---|---|---|---|
| `Qwen3-Next-80B-A3B` | 80B | 3B | MoE | 256K |

### Qwen3-Coder (Open-Weight)

| Model | Params | Act. Params | Type | Context |
|---|---|---|---|---|
| `Qwen3-Coder-480B-A35B` | 480B | 35B | MoE | 256K native, 1M extrapolated |
| `Qwen3-Coder-30B-A3B` | 30B | 3B | MoE | 256K |

### Qwen2.5 Series (Open-Weight)

| Model | Params | Type | Context |
|---|---|---|---|
| `Qwen2.5-0.5B` | 0.5B | Dense | 32K |
| `Qwen2.5-1.5B` | 1.5B | Dense | 32K |
| `Qwen2.5-3B` | 3B | Dense | 32K |
| `Qwen2.5-7B` | 7B | Dense | 128K |
| `Qwen2.5-14B` | 14B | Dense | 128K |
| `Qwen2.5-32B` | 32B | Dense | 128K |
| `Qwen2.5-72B` | 72B | Dense | 128K |

**Qwen2.5-1M variants:** `Qwen2.5-7B-Instruct-1M`, `Qwen2.5-14B-Instruct-1M` (1M context via Model Studio API)

### Qwen2.5-Coder (Open-Weight)

| Model | Params | Context |
|---|---|---|
| `Qwen2.5-Coder-1.5B` | 1.5B | 32K |
| `Qwen2.5-Coder-3B` | 3B | 32K |
| `Qwen2.5-Coder-7B` | 7B | 128K |
| `Qwen2.5-Coder-14B` | 14B | 128K |
| `Qwen2.5-Coder-32B` | 32B | 128K |

### Qwen2.5-Math (Open-Weight)

| Model | Params | Context |
|---|---|---|
| `Qwen2.5-Math-1.5B` | 1.5B | 4K |
| `Qwen2.5-Math-3B` | 3B | 4K |
| `Qwen2.5-Math-7B` | 7B | 4K |
| `Qwen2.5-Math-72B` | 72B | 4K |

### Qwen2.5-VL (Open-Weight, Multimodal)

| Model | Params | Context | Vision |
|---|---|---|---|
| `Qwen2.5-VL-3B` | 3B | 128K | Image+Video |
| `Qwen2.5-VL-7B` | 7B | 128K | Image+Video |
| `Qwen2.5-VL-32B` | 32B | 128K | Image+Video |
| `Qwen2.5-VL-72B` | 72B | 128K | Image+Video |

### Qwen2.5-Omni (Open-Weight)

| Model | Params | Context | Modalities |
|---|---|---|---|
| `Qwen2.5-Omni-7B` | 7B | — | Text+Image+Audio+Video+Speech |

### Qwen2 Series (Open-Weight)

| Model | Params | Context |
|---|---|---|
| `Qwen2-0.5B` | 0.5B | 32K |
| `Qwen2-1.5B` | 1.5B | 32K |
| `Qwen2-7B` | 7B | 128K |
| `Qwen2-57B-A14B` | 57B (14B act.) | 128K (MoE) |
| `Qwen2-72B` | 72B | 128K |

### Qwen2-VL (Open-Weight, Multimodal)

| Model | Params | Vision |
|---|---|---|
| `Qwen2-VL-2B` | 2B | Image+Video |
| `Qwen2-VL-7B` | 7B | Image+Video |
| `Qwen2-VL-72B` | 72B | Image+Video |

### Qwen2-Audio (Open-Weight)

| Model | Params | Notes |
|---|---|---|
| `Qwen2-Audio-7B` | 7B | Audio understanding |

### Qwen2-Math (Open-Weight)

| Model | Params |
|---|---|
| `Qwen2-Math-1.5B` | 1.5B |
| `Qwen2-Math-7B` | 7B |
| `Qwen2-Math-72B` | 72B |

### QwQ Series (Reasoning-Focused, Open-Weight)

| Model | Params | Context | Notes |
|---|---|---|---|
| `QwQ-32B` | 32B | 128K | Thinking-only reasoning model |
| `QwQ-Max-Preview` | — | — | API-only predecessor |

### Specialized Open-Weight Models

| Model | Params | Type | Notes |
|---|---|---|---|
| `Qwen-AgentWorld-35B-A3B` | 35B (3B act.) | MoE | Agent world model for general agents |
| `Qwen-Image-Bench` | 27B | Vision-LM | Image evaluation benchmark model |
| `Qwen-Image` | 20B | MMDiT | Image generation foundation model |
| `Qwen-Image-Edit` | 20B | MMDiT | Image editing model |
| `Qwen-VLo` | — | Multimodal | Unified understanding + generation |
| `Qwen3-ASR-0.6B` | 0.6B | ASR | Speech recognition |
| `Qwen3-ASR-1.7B` | 1.7B | ASR | Speech recognition |
| `Qwen3-ForcedAligner-0.6B` | 0.6B | Token Classification | Phoneme alignment |
| `Qwen3-TTS` | — | TTS | Text-to-speech |
| `Qwen3Guard` | — | Safety | Safety classifier for prompt/response |
| `Qwen3-Embedding` | — | Embedding | Text embedding (open-source) |
| `Qwen3-Reranker` | — | Reranking | Text reranking (open-source) |
| `Qwen3-VL-Embedding` | — | VL Embedding | Multimodal embedding (open-source) |
| `Qwen3-VL-Reranker` | — | VL Reranking | Multimodal reranking (open-source) |

---

## 8. THIRD-PARTY MODELS (via Model Studio)

### DeepSeek

| Model ID | Context | Thinking | Notes |
|---|---|---|---|
| `deepseek-v4-pro` | 1M | Yes | Function calling |
| `deepseek-v4-flash` | 1M | Yes | Function calling |
| `deepseek-v3.2` | 128K | Yes | Function calling, structured output |
| `deepseek-v3.2-exp` | 128K | Yes | Experimental |
| `deepseek-v3.1` | 128K | Yes | |
| `deepseek-v3` | 128K | No | Function calling, structured output |
| `deepseek-r1` | 128K | Yes | Function calling, structured output |
| `deepseek-r1-0528` | 128K | Yes | |

### DeepSeek R1 Distill (via Model Studio)

| Model | Context | Thinking | Base |
|---|---|---|---|
| `deepseek-r1-distill-qwen-32b` | 128K | Yes | Qwen-32B |
| `deepseek-r1-distill-qwen-14b` | 128K | Yes | Qwen-14B |
| `deepseek-r1-distill-qwen-7b` | 128K | Yes | Qwen-7B |
| `deepseek-r1-distill-qwen-1.5b` | 128K | Yes | Qwen-1.5B |
| `deepseek-r1-distill-llama-70b` | 128K | Yes | Llama-70B |
| `deepseek-r1-distill-llama-8b` | 128K | Yes | Llama-8B |

### Kimi (Moonshot)

| Model ID | Context | Thinking | Notes |
|---|---|---|---|
| `kimi-k2.7-code` | — | Yes | Coding-focused |
| `kimi-k2.6` | 256K | Yes | Function calling |
| `kimi-k2.5` | 256K | Yes | |
| `kimi-k2-thinking` | 256K | Yes | |
| `Moonshot-Kimi-K2-Instruct` | 256K | No | |

### GLM (Zhipu AI)

| Model ID | Context | Thinking | Structured Output |
|---|---|---|---|
| `glm-5.2` | 198K | Yes | Yes |
| `glm-5.1` | 198K | Yes | Yes |
| `glm-5` | 198K | Yes | Yes |
| `glm-4.7` | 198K | Yes | Yes |
| `glm-4.5` | 198K | Yes | Yes |
| `glm-4.5-air` | 198K | Yes | Yes |

### MiniMax

| Model ID | Context | Thinking |
|---|---|---|
| `MiniMax-M2.7` | 200K | Yes |
| `MiniMax-M2.5` | 192K | Yes |
| `MiniMax-M2.1` | 200K | Yes |

---

## 9. QUICK REFERENCE — PRICING SUMMARY (Singapore, per 1M tokens)

| Model | Input | Output (Non-Thinking) | Output (Thinking) |
|---|---|---|---|
| `qwen3.7-max` | $2.50 | $7.50 | $7.50 |
| `qwen3.7-plus` (≤256K) | $0.40 | $1.60 | $1.60 |
| `qwen3.7-plus` (256K–1M) | $1.20 | $4.80 | $4.80 |
| `qwen3.6-max-preview` (≤128K) | $1.30 | $7.80 | $7.80 |
| `qwen3.6-plus` (≤256K) | $0.50 | $3.00 | $3.00 |
| `qwen3.6-plus` (256K–1M) | $2.00 | $6.00 | $6.00 |
| `qwen3.5-plus` (≤256K) | $0.40 | $2.40 | $2.40 |
| `qwen3-max` (≤32K) | $1.20 | $6.00 | $6.00 |
| `qwen-plus` (≤256K) | $0.40 | $1.20 | $4.00 |
| `qwen-max` | $1.60 | $6.40 | — |
| `qwen-long` | $0.50 | $2.00 | — |
| `qwen-mt-plus` | $2.00 | $8.00 | — |
| `qwen-mt-turbo` | $0.50 | $2.00 | — |
| `text-embedding-v4` | $0.05 | — | — |
| `text-embedding-v3` | $0.05 | — | — |
| `qwen3-vl-embedding` | $0.15 | — | — |

---

## 10. REGION AVAILABILITY

| Region | Endpoint Pattern | Notes |
|---|---|---|
| **Singapore** | `https://{WorkspaceId}.ap-southeast-1.maas.aliyuncs.com/compatible-mode/v1` | Full model catalog |
| **China (Beijing)** | `https://{WorkspaceId}.cn-beijing.maas.aliyuncs.com/compatible-mode/v1` | DeepSeek available |
| **China (Hong Kong)** | `https://{WorkspaceId}.cn-hongkong.maas.aliyuncs.com/compatible-mode/v1` | Global deployment |
| **US (Virginia)** | `https://dashscope-us.aliyuncs.com/compatible-mode/v1` | US-specific pricing |
| **Germany (Frankfurt)** | `https://{WorkspaceId}.eu-central-1.maas.aliyuncs.com/compatible-mode/v1` | EU deployment |
| **Japan (Tokyo)** | `https://{WorkspaceId}.ap-northeast-1.maas.aliyuncs.com/compatible-mode/v1` | JP deployment |

> API keys are **not interchangeable** across regions. Free quota only in Singapore (international scope).

---

*Compiled from Alibaba Cloud Model Studio docs, Qwen Cloud, Hugging Face Qwen org, Qwen blog, and Qwen readthedocs. Prices as of July 2026. Verify current pricing at [modelstudio.console.alibabacloud.com](https://modelstudio.console.alibabacloud.com/).*
