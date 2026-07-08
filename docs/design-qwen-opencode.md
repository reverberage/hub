# SDD Design: qwen-opencode

**Change ID**: `qwen-opencode` | **Approach**: C (Scripted Rotator) | **Date**: 2026-07-07

## 1. Component Architecture

```
hub/
├── opencode.template.json    ← Template (tracked, read-only)
├── opencode.json             ← Generated (gitignored, runtime)
├── scripts/
│   ├── qwen_fallback.py      ← Rotation CLI (tracked)
│   ├── .gitignore            ← Ignores *_state.json
│   └── .qwen_state.json      ← Rotation state (gitignored)
└── docs/
    └── stage-a-tracking.md   ← Usage log (tracked)
```

**Single component**: `scripts/qwen_fallback.py`. No runtime — on-demand CLI. No proxy, no daemon, no background process.

### Internal Modules (single file)

| Module | Responsibility |
|--------|---------------|
| `ModelCatalog` | Static list of 81 model IDs with tier assignments. Hardcoded SKIP set (6 exhausted + 4 unsupported). |
| `ProbeEngine` | Quota probing via OpenAI-compatible API call. 1-token request, detects `AllocationQuota.FreeTierOnly`. |
| `ConfigGenerator` | Reads `opencode.template.json`, replaces `{model}` with active model_id, writes `opencode.json`. |
| `TrackingWriter` | Creates/updates `docs/stage-a-tracking.md`. Rewrites summary, appends activity log entries. |
| `CLI` | argparse dispatcher for `--status`, `--rotate`, `--track`. State file management. |

## 2. Data Structures

### 2.1 ModelCatalog — Static Model List

```python
from dataclasses import dataclass, field
from enum import Enum

class Tier(Enum):
    CODER = 1          # Coding specialists
    FLAGSHIP = 2       # Best quality
    VALUE = 3          # Price/performance
    THIRD_PARTY = 4    # Non-Qwen (deepseek, kimi, glm)
    ALPHA = 5          # Remaining, alphabetical

class ModelStatus(Enum):
    UNKNOWN = "UNKNOWN"       # never probed
    ACTIVE = "ACTIVE"         # responded 200 OK to probe
    EXHAUSTED = "EXHAUSTED"   # 429 + FreeTierOnly
    SKIP = "SKIP"             # hardcoded exhausted/unsupported (never probe)
    ERROR = "ERROR"           # network/API error during probe

@dataclass
class ModelInfo:
    model_id: str
    tier: Tier
    priority: int            # position within tier (1-based)
    status: ModelStatus = ModelStatus.UNKNOWN
    remaining_tokens: int | None = None  # from x-qwen-quota-remaining header
```

SKIP_SET (10 models, never probed):
- 6 EXHAUSTED: `qwen-plus`, `qwen-max`, `qwen-turbo`, `qwen-flash`, `deepseek-v4-pro`, `deepseek-v4-flash`
- 4 UNSUPPORTED: `qwen3.7-plus`, `qwen3.7-max`, `qwen-plus-character-ja`, `qwen-plus-2025-01-25`

### 2.2 Tier Assignments (81 models)

**Tier 1 — Coders (8):**
`qwen3-coder-plus`, `qwen3-coder-flash`, `qwen3-coder-next`,
`qwen3-coder-plus-2025-07-22`, `qwen3-coder-plus-2025-09-23`,
`qwen3-coder-flash-2025-07-28`, `qwen3-coder-480b-a35b-instruct`,
`qwen3-coder-30b-a3b-instruct`

**Tier 2 — Flagships (6):**
`qwen3.7-plus-2026-05-26`, `qwen3.7-max-2026-06-08`,
`qwen3.7-max-2026-05-20`, `qwen3.7-max-preview`,
`qwen3.7-max-2026-05-17`, `qwen3.6-max-preview`

**Tier 3 — Value (6):**
`qwen3.6-plus-2026-04-02`, `qwen3.6-flash-2026-04-16`,
`qwen3.5-plus-2026-04-20`, `qwen3-max-2026-01-23`,
`qwen3.6-plus`, `qwen3.6-flash`

**Tier 4 — Third-party (4):**
`deepseek-v3.2`, `kimi-k2.7-code`, `glm-5.2`, `glm-5.1`

**Tier 5 — Alphabetical (57):** All remaining from catalog sorted by model_id.
Total: 8 + 6 + 6 + 4 + 57 = 81.

### 2.3 Rotation State (on-disk)

```python
@dataclass
class RotationState:
    active_model_index: int       # index into MODELS list
    active_model_id: str          # convenience copy
    exhausted_set: list[str]      # model_ids discovered exhausted via probing
    last_rotation: str            # ISO timestamp
```

State file: `scripts/.qwen_state.json` — written by all commands, gitignored via `scripts/.gitignore`.

### 2.4 Tracking Entry

```python
@dataclass
class TrackingEntry:
    timestamp: str              # ISO 8601
    model_id: str
    action: str                 # activate | exhaust | skip | probe_ok
    remaining_estimate: int     # from x-qwen-quota-remaining, -1 if unknown
    notes: str = ""
```

## 3. Interface Specifications

### 3.1 CLI Contract

```
usage: qwen_fallback.py [--status | --rotate | --track] [--force] [--json]
                        [--model MODEL] [--dry-run]

--status    Probe all 81 models, output availability table
--rotate    Test active model; if exhausted, switch to next; regen opencode.json
--track     Update docs/stage-a-tracking.md from current state (no probing)
--force     Force rotation regardless of current model status
--json      Output as JSON (for automation/scripting)
--model M   Override active model directly, skip rotation logic
--dry-run   Show what would happen without touching files
```

Default (no flags): `--status --json`.

### 3.2 `--status` Command

Probing logic per model:
1. In SKIP_SET → status=SKIP, no API call
2. In state.exhausted_set → status=EXHAUSTED, no API call
3. POST `/v1/chat/completions` with `max_tokens=1`, `model=model_id`
4. 200 OK → ACTIVE, capture `x-qwen-quota-remaining`
5. 429 + `"code":"AllocationQuota.FreeTierOnly"` → EXHAUSTED, add to exhausted_set
6. Other errors → ERROR. Timeout: 10s.

Output (text mode):
```
Model                                    Status      Remaining
────────────────────────────────────────────────────────────────
qwen3-coder-plus                         ACTIVE        999,986
qwen3-coder-flash                        ACTIVE        999,986
...
qwen-plus                                SKIP              —
deepseek-v4-pro                          SKIP              —
────────────────────────────────────────────────────────────────
Summary: 68/81 available, 6 exhausted, 7 skipped
Active model: qwen3-coder-plus (Tier 1)
Est. remaining: ~68,000,000 tokens
```

JSON output: `{"summary": {"total": 81, "active": 68, ...}, "models": [...], "active_model": "...", "estimated_remaining": 68000000}`

Exit 0 if any model ACTIVE, exit 1 if all exhausted/skipped/error.

### 3.3 `--rotate` Command

1. If `--model M` → set active model to M, regen opencode.json, exit 0. No probing.
2. If not `--force` → probe active model.
   - 200 OK → "No rotation needed", exit 0. Do NOT regenerate.
   - 429 FreeTierOnly → mark exhausted, proceed.
   - Error → warn, proceed (transient network issue).
3. Iterate `state.active_model_index + 1` through 80.
   - Skip SKIP_SET + exhausted_set.
   - Probe each. First 200 OK → new active model.
4. Read template → `str.replace("{model}", new_model_id)` → write opencode.json.
5. Append tracking entry.
6. Write state file.
7. Print: "Rotated to {model_id} (Tier {tier}). opencode.json updated."
8. Exit 0.

If no model found (all 81 exhausted): preserve opencode.json, print CRITICAL, exit 1.

### 3.4 `--track` Command

1. Calculate `days_remaining` to 2026-09-28.
2. Count active/exhausted from cached state (no probing).
3. Rewrite `docs/stage-a-tracking.md` with current summary + appended activity entries.
4. Exit 0.

## 4. Data Flow — Rotation (primary path)

```
User: scripts/qwen_fallback.py --rotate
  │
  ▼
Read state file ──► scripts/.qwen_state.json
  │ active_model_index=0 (qwen3-coder-plus)
  ▼
Probe active model ──► POST /v1/chat/completions
  │ model=qwen3-coder-plus, max_tokens=1
  │
  ├── 200 OK → "No rotation needed." Exit 0.
  │
  └── 429 FreeTierOnly
       │
       ▼
     Mark EXHAUSTED in state.exhausted_set
       │
       ▼
     Iterate MODELS[1:] ──► skip SKIP/exhausted
       │ ──► probe each candidate
       ▼
     Found: qwen3-coder-flash (200 OK)
       │
       ▼
     Read opencode.template.json
     "{model}" → "qwen3-coder-flash"
       │
       ▼
     Write opencode.json (generated)
       │
       ▼
     Append to docs/stage-a-tracking.md
       │
       ▼
     Write scripts/.qwen_state.json
       │
       ▼
     "Rotated to qwen3-coder-flash (Tier 1)." Exit 0.
```

## 5. Template & opencode.json Generation

### 5.1 opencode.template.json (tracked)

```json
{
  "model": "qwen/{model}",
  "provider": {
    "qwen": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "Qwen (Alibaba Model Studio)",
      "options": {
        "baseURL": "https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
        "apiKey": "{env:DASHSCOPE_API_KEY}"
      },
      "models": {
        "qwen3-coder-plus": { "name": "Qwen3 Coder Plus" },
        "qwen3-coder-flash": { "name": "Qwen3 Coder Flash" },
        "qwen3.7-plus": { "name": "Qwen3.7 Plus" },
        "qwen3.7-max": { "name": "Qwen3.7 Max" },
        "qwen3.6-plus": { "name": "Qwen3.6 Plus" },
        "deepseek-v3.2": { "name": "DeepSeek V3.2" }
      }
    }
  }
}
```

Substitution: `template_str.replace("{model}", model_id)`. Single-pass, single token. The `{model}` placeholder appears in `"model": "qwen/{model}"`. After generation, the string `{model}` must not appear anywhere in the output (AC-2).

### 5.2 opencode.json Example (generated, gitignored)

After `--rotate` sets active model to `qwen3-coder-flash`:

```json
{
  "model": "qwen/qwen3-coder-flash",
  "provider": {
    "qwen": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "Qwen (Alibaba Model Studio)",
      "options": {
        "baseURL": "https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
        "apiKey": "{env:DASHSCOPE_API_KEY}"
      },
      "models": {
        "qwen3-coder-plus": { "name": "Qwen3 Coder Plus" },
        "qwen3-coder-flash": { "name": "Qwen3 Coder Flash" },
        "qwen3.7-plus": { "name": "Qwen3.7 Plus" },
        "qwen3.7-max": { "name": "Qwen3.7 Max" },
        "qwen3.6-plus": { "name": "Qwen3.6 Plus" },
        "deepseek-v3.2": { "name": "DeepSeek V3.2" }
      }
    }
  }
}
```

Note: only `"model": "qwen/{model}"` changes. The static `models` map is convenience-only — opencode auto-discovers models via `/v1/models` anyway.

## 6. Quota Detection Protocol

### 6.1 Probe Request

```python
client = OpenAI(
    api_key=os.environ["DASHSCOPE_API_KEY"],
    base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
    timeout=10.0,
)
response = client.chat.completions.create(
    model=model_id,
    messages=[{"role": "user", "content": "."}],
    max_tokens=1,
    temperature=0,
)
```

Cost: ~2 tokens per probe. Full status of 71 unknown models: ~142 tokens. Negligible.

### 6.2 Response Handling

| HTTP | Body Condition | Verdict |
|------|----------------|---------|
| 200 | — | ACTIVE. Capture `x-qwen-quota-remaining` header. |
| 429 | body contains `"code":"AllocationQuota.FreeTierOnly"` | EXHAUSTED |
| 429 | other code or no code | ERROR (rate-limited, not quota). Retryable. |
| 401 | — | ERROR. Fatal: bad API key. Exit immediately. |
| 4xx | — | ERROR. Model may not support chat/completions. |
| 5xx | — | ERROR. Server-side issue. Retryable. |
| Timeout | >10s | ERROR. Retryable. |

## 7. Tracking Doc Structure (docs/stage-a-tracking.md)

```markdown
# Qwen Free Quota Tracking

> **Started**: 2026-07-06 | **Expires**: 2026-09-28 | **Days remaining**: 83
> **Account**: Singapore International | **Total text quota**: 103,000,000 tokens

## Summary

| Metric | Value |
|--------|-------|
| Total models (LLM) | 81 |
| Available | 68 |
| Exhausted | 6 |
| Skipped | 7 |
| Est. remaining tokens | ~68,000,000 |

## Activity Log

| Date | Model | Action | Est. Remaining | Notes |
|------|-------|--------|:---:|-------|
| 2026-07-06 | qwen3-coder-plus | activate | 999,986 | Initial setup |
| 2026-07-15 | qwen3-coder-plus | exhaust | 0 | Quota exhausted, rotated |
| 2026-07-15 | qwen3-coder-flash | activate | 999,986 | — |

## Model Roster

| # | Tier | Model | Status | Initial Tokens |
|---|------|-------|--------|:---:|
| 1 | 1 | qwen3-coder-plus | EXHAUSTED | 1,000,000 |
| 2 | 1 | qwen3-coder-flash | ACTIVE | 1,000,000 |
| 3 | 1 | qwen3-coder-next | ACTIVE | 1,000,000 |
| ... | ... | ... | ... | ... |
```

`--track` does a full rewrite each time: reads existing doc, extracts Activity Log rows, prepends new entries, rebuilds Summary and Roster tables from current state file. This ensures consistency between all sections.

## 8. Error Handling Matrix

| Condition | Detection | Response | Exit |
|-----------|-----------|----------|:--:|
| `DASHSCOPE_API_KEY` not set | KeyError on env access | "FATAL: DASHSCOPE_API_KEY not set." | 1 |
| `opencode.template.json` missing | FileNotFoundError | "FATAL: opencode.template.json not found." | 1 |
| Template invalid JSON | JSONDecodeError | "FATAL: template not valid JSON: {error}" | 1 |
| Template has no `{model}` | count(`{model}`) == 0 after gen | "WARNING: template contains no {model} placeholder." | 0 |
| Network timeout probing | httpx.ReadTimeout >10s | Mark model ERROR, continue. | 0 (if any ACTIVE) |
| All models ERROR (network down) | 0 ACTIVE, all ERROR | "Cannot reach DashScope API." | 1 |
| All models EXHAUSTED | 0 ACTIVE, some EXHAUSTED | "All models exhausted. Preserving opencode.json." | 1 |
| All models EXHAUSTED+SKIP | 0 ACTIVE, all SKIP/EXHAUSTED | "0/81 models available." | 1 |
| 401 Unauthorized | HTTP 401 | "FATAL: Invalid API key." | 1 |
| State file corrupted | JSONDecodeError on read | "WARNING: state file corrupted, reinitializing." Reset to index 0. | 0 |
| State file dir missing | FileNotFoundError | Create `scripts/` directory, write state. | 0 |
| Docs dir missing | FileNotFoundError | Create `docs/` directory, write tracking doc. | 0 |
| opencode.json write denied | PermissionError | "ERROR: Cannot write opencode.json." | 1 |

## 9. Edge Cases

### 9.1 Fresh Install (No State File)
First run: no `.qwen_state.json`. Initialize: `active_model_index=0`, `exhausted_set=list(SKIP_SET)`, all status=UNKNOWN. `--rotate` probes model 0 first; `--status` probes all 71 unknown models.

### 9.2 Template Has Multiple `{model}` Tokens
`str.replace("{model}", model_id)` replaces all occurrences. AC-2: verify count = 0 after generation.

### 9.3 opencode.json Already Exists (Manual Edits)
`--rotate` unconditionally overwrites. Warning: "Regenerating opencode.json from template. Manual edits will be lost." Use `--model` to set desired model after updating template.

### 9.4 opencode Running During Rotation
opencode reads config at startup. Mid-session changes ignored. No conflict. Restart opencode to pick up new model.

### 9.5 Model Responds OK to Probe But Fails for Real Requests
Probe is minimal (1 token). Some models may fail with larger context or thinking mode. Recovery: `--force` to skip to next model.

### 9.6 Post-Expiry (after 2026-09-28)
All models return `AllocationQuota.FreeTierOnly`. `--status`: 0 ACTIVE, exit 1. `--rotate`: can't find available model, exit 1. Tracking doc shows `days_remaining = 0`.

### 9.7 VL/MT/Character Models in LLM Catalog
Models like `qwen-vl-*`, `qwen-mt-*`, `qwq-*`, `qvq-*`, `*-character` appear in the console's LLM tab. They respond to `/v1/chat/completions`. For pure-text opencode, they work. If a specific model fails in practice: `--force` rotates past it.

### 9.8 Concurrent Execution
Two terminals running script simultaneously: race condition on state file. Last write wins. Acceptable — script is manual, not automated.

## 10. Traceability Matrix

| AC | Title | Design Coverage |
|:--:|-------|----------------|
| AC-1 | opencode.json generation | §5.1-5.2: Correct npm/baseURL/apiKey/model in generated output |
| AC-2 | Template placeholder | §5.1: Single `{model}` token, post-generation verification |
| AC-3 | Quota exhaustion detection | §6.1-6.2: Probe + 429/FreeTierOnly detection protocol |
| AC-4 | Rotation priority order | §2.1-2.2: 5-tier ModelCatalog, SKIP_SET for 10 excluded models |
| AC-5 | --status command | §3.2: Probe + table/JSON output, exit 0 or 1 |
| AC-6 | --track command | §3.4, §7: Timestamped entries, creates on first run |
| AC-7 | Tracking doc structure | §7: Header/countdown/summary/log/roster format |
| AC-8 | Self-contained script | §1: Single file, `openai` only dep, no venv/pyproject |
| AC-9 | .gitignore compliance | §5.2: opencode.json gitignored; template/script/tracking tracked |
| AC-10 | Idempotent rotation | §3.3: Probe first, skip regeneration if active |
| AC-11 | Full exhaustion | §3.3, §8: Preserve opencode.json, exit 1, CRITICAL message |

## 11. Implementation Notes

### 11.1 Single File
`scripts/qwen_fallback.py`, ~350 lines. Deps: `openai` (system v2.44.0) + stdlib (`json`, `os`, `sys`, `argparse`, `datetime`, `dataclasses`, `enum`, `pathlib`, `textwrap`).

### 11.2 Paths & Execution
- Script: `scripts/qwen_fallback.py` from project root
- Shebang: `#!/usr/bin/env python3`
- Invocation: `python scripts/qwen_fallback.py --status`
- Env required: `DASHSCOPE_API_KEY`

### 11.3 State File
- `scripts/.qwen_state.json` — gitignored via `scripts/.gitignore` (pattern: `*_state.json`)
- NOT in `.opencode/` — that directory is opencode's internal npm state

### 11.4 Template Pre-existence
`opencode.template.json` tracked in git. Must exist before any `--rotate`. First-time clone provides it. Missing → hard error.

## 12. Files Summary

| File | Action | Git | Purpose |
|------|--------|:--:|---------|
| `opencode.template.json` | CREATE | Tracked | Template with `{model}` token |
| `scripts/qwen_fallback.py` | CREATE | Tracked | Rotation CLI |
| `scripts/.gitignore` | CREATE | Tracked | Ignore `*_state.json` |
| `scripts/.qwen_state.json` | AUTO | Gitignored | Rotation state |
| `docs/stage-a-tracking.md` | AUTO | Tracked | Usage log + countdown |
| `.gitignore` | NO CHANGE | — | Already has opencode.json and .opencode/ entries |
