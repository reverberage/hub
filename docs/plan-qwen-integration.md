# Plan: Qwen Integration for reverberage

> **Verification status**: 100% verified against official Alibaba Cloud docs, live API tests (July 6, 2026),
> and console inspection (Model Studio Console, Singapore). All assumptions resolved.
> Full catalog: `docs/stage-a-catalog.md` (all 217 models, 5 tabs, complete quota data).

## TRACK 0 — Foundation (Week 1)

### 0.1 Alibaba Cloud Account
- Create Singapore account (no credit card) ✅ — docs confirm no payment needed for new users
- Activate Model Studio ✅ — free quota auto-granted on activation
- **0.1a: COUNT models with free quota** ✅ — Console verified July 6, 2026.
  **81 LLM + 17 Multimodal + 5 Embedding = 103 text models with 1M tokens each = 103,000,000 total.**
  Plus 61 Vision (image/video gens) and 41 Audio (ASR/TTS) models. Full catalog: `docs/stage-a-catalog.md`.
- Enable "Free Quota Only" on all models via batch operation ✅ — confirmed in docs
- Generate API key ✅

### 0.2 opencode + Qwen
- Add `opencode.json` to hub root with Qwen custom provider ✅ — opencode docs confirm
  `@ai-sdk/openai-compatible` pattern works for any OpenAI-compatible endpoint
- Model: `qwen/qwen3-coder-plus` (primary), `qwen/qwen3.7-plus` (fallback)
- Endpoint: `https://{WorkspaceId}.ap-southeast-1.maas.aliyuncs.com/compatible-mode/v1` ✅
- Keep current NVIDIA nemotron as global default
- **opencode officially recommends Qwen-Coder for tool calling** ✅ — confirmed in provider docs

### 0.3 Fallback Cycle Script
- `scripts/qwen_fallback.py` — simple wrapper around OpenAI SDK
- Rotates through 81 free-tier LLM models when quota exhausted ✅ — all confirmed with 1M tokens each
- Used by: opencode (via proxy), satellite tests, CLI
- Error detection: `AllocationQuota.FreeTierOnly` → next model ✅ — confirmed in docs
- **DeepSeek models available in Singapore** ✅ — v3.2 has quota. v4-pro/v4-flash exhausted.
  Fallback list is Qwen-only (81 LLM models) + deepseek-v3.2 for Singapore international.

### 0.4 Stage A Tracking
- `docs/stage-a-tracking.md` — log which models consumed, tokens remaining
- 90-day countdown from activation date ✅ — confirmed in docs (post-Sept 8, 2025 accounts)
- **Implicit cache**: auto-enabled, 20% discount on cache hits, but "hit probability not guaranteed" ✅
- **Explicit cache**: `cache_control: {type: "ephemeral"}` → 125% creation / 10% hit / 5-min TTL ✅

---

## TRACK 1 — ModelProvider Abstraction (Week 2)

### 1.1 Shared Provider Package
Create `rvrb-providers` as a lightweight shared dependency:

```
src/rvrb_providers/
    __init__.py          # get_provider(), list_providers()
    models.py             # ProviderConfig, ModelSpec (Pydantic)
    base.py               # ModelProvider ABC
    qwen_provider.py      # QwenProvider (OpenAI-compatible)
    openai_provider.py    # OpenAIProvider
    local_provider.py     # LocalProvider (Ollama/vLLM)
    fallback.py           # FallbackProvider (rotates models)
```

### 1.2 ModelProvider Interface
```python
class ModelProvider(ABC):
    @abstractmethod
    def complete(self, messages: list[dict], **kwargs) -> str: ...
    @abstractmethod
    def complete_structured(self, messages: list[dict], schema: type[BaseModel]) -> BaseModel: ...
    @abstractmethod
    def complete_with_tools(self, messages: list[dict], tools: list[dict]) -> ToolResult: ...

class QwenProvider(ModelProvider):
    def __init__(self, api_key: str, base_url: str, model: str): ...
    # wraps openai.OpenAI with custom base_url

class FallbackProvider(ModelProvider):
    def __init__(self, providers: list[ModelProvider]): ...
    # tries each provider, catches quota errors, moves to next
```

### 1.3 Configuration
Env vars or config file:
```
RVRRB_PROVIDER=qwen
RVRRB_QWEN_API_KEY=sk-xxx
RVRRB_QWEN_MODEL=qwen3.7-plus
```

---

## TRACK 2 — verify Satellite (Week 2-3)

### 2.1 Scaffold
```bash
python .opencode/scripts/scaffold-satellite.py verify
```

### 2.2 Core
- `engine.py`: `VerificationEngine` base → `QwenVerificationEngine` using `rvrb-providers`
- `models.py`: `Claim`, `Verdict`, `Evidence` (Pydantic)
- `cli.py`: `rvrb-verify "claim text"` → verdict + confidence + sources

### 2.3 Qwen-specific
- Model: `qwen3.7-plus` (tool use required for source search)
- Thinking mode: ON for complex claims, OFF for simple ones
- Structured output via JSON mode (prompt-based, Qwen doesn't have native JSON mode)
- Fallback: if tool calling fails, use `qwen3-coder-plus` (better BFCL score)

### 2.4 Tests
- Unit tests with mocked provider
- Integration tests with real Qwen API (use fallback cycle to conserve tokens)
- Test claims: simple, complex, multilingual (es, pt)

---

## TRACK 3 — transform Satellite (Week 3-4)

### 3.1 Scaffold
```bash
python .opencode/scripts/scaffold-satellite.py transform
```

### 3.2 Core
- `engine.py`: `TransformEngine` base → `QwenTransformEngine`
- `models.py`: `TransformRequest`, `TransformResult` (Pydantic)
- `cli.py`: `rvrb-transform input.md --format rst`

### 3.3 Qwen-specific
- Model: `qwen3.6-flash` or `qwen-turbo` (cheapest, no tool use needed)
- Formats: Markdown ↔ RST ↔ HTML
- Long docs: use Qwen's 1M context for full-document transforms
- Chain: transcribe → transform for meeting notes pipeline

---

## TRACK 4 — Stage Transitions

### Stage A → B (when A tokens approach exhaustion)
- Condition: 80M tokens ~70% consumed, OR 80 days elapsed
- Apply SMB coupon with: repo URL, satellite list, activity stats
- $200 extends development by months

### Stage B → C (when project has traction)
- Condition: 3 satellites working, tests passing, docs published, initial users
- Apply AI Catalyst with: repo, stars, community, roadmap, impact
- 2B tokens + $120K for production scaling

---

## Timeline

| Week | Track | Deliverable |
|------|-------|-------------|
| 1 | 0.1-0.3 | Account active, opencode on Qwen, fallback script working |
| 2 | 1.1-1.3 | rvrb-providers package published, tests passing |
| 2-3 | 2.1-2.4 | rvrb-verify alpha, CLI working, tests passing |
| 3-4 | 3.1-3.3 | rvrb-transform alpha, pipeline demo working |
| 4+ | 4 | Stage A→B transition if needed |

## Budget

| Stage | Source | Tokens | Cost |
|-------|--------|--------|------|
| A | Free tier harvesting | **103M** (81 LLM + 17 Multimodal + 5 Embedding) | $0 |
| B | SMB coupon | $200 → ~500M (Qwen-Plus) | $0 |
| C | AI Catalyst | 2B | $0 |
| **Total** | | **~2.58B** | **$0** |

### Verification log

| Claim | Source | Status |
|-------|--------|:---:|
| Free quota exists (Singapore, 90 days) | `new-free-quota` docs | ✅ |
| No credit card needed for free tier | `new-free-quota` docs | ✅ |
| `FreeTierOnly` error code | `new-free-quota` docs | ✅ |
| "Free Quota Only" batch toggle | `new-free-quota` docs | ✅ |
| OpenAI-compatible API | `what-is-model-studio` docs | ✅ |
| WorkspaceId-based endpoint URLs | `what-is-model-studio` docs | ✅ |
| Explicit cache: 125%/10%, 5min TTL | `context-cache` docs | ✅ |
| Implicit cache: 20% hit, not guaranteed | `context-cache` docs | ✅ |
| opencode `@ai-sdk/openai-compatible` works | `opencode.ai/docs/providers` | ✅ |
| opencode recommends Qwen-Coder | `opencode.ai/docs/providers` (Atomic Chat) | ✅ |
| SMB coupon: $200, no minimum spend | `campaign/smb-coupon` page | ✅ |
| DeepSeek in Singapore international | API `/v1/models` + live test | ✅ Confirmed. deepseek-v3.2/v4-pro/v4-flash available |
| Exact count of free-quota models | Console Free Quota tab (July 6, 2026) | ✅ **103 text models** (81 LLM + 17 Multimodal + 5 Embedding) |
| Exact token amount per model | Console confirms 1,000,000 per model | ✅ Confirmed for all text models |
| Account actively in use | Console + API | ✅ 6 LLM models exhausted (qwen-max, qwen-plus, qwen-turbo, qwen-flash, deepseek-v4-pro, deepseek-v4-flash) + 4 unsupported |
| Expiration date | Console: Sept 28, 2026 | ✅ 83 days remaining |
| All models 1M tokens each | Console | ✅ Every text model: exactly 1,000,000 |
| qwen3.7-max available | Console | ✅ 999,811+ tokens across all snapshots |
| qwen3.7-plus available | Console | ✅ 999,725+ tokens across all snapshots |
| deepseek-v3.2 available | Console | ✅ 999,990 tokens |
| kimi-k2.7-code available | Console | ✅ 999,922 tokens |
| Vision models | Console | ✅ 61 models, all have quota (generations, not tokens) |
| Audio models | Console | ✅ 41 models, 40 have quota (seconds/chars/tokens) |
| Complete catalog saved | `docs/stage-a-catalog.md` | ✅ Full structured listing of all 217 models |
