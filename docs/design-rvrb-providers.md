# SDD Design: rvrb-providers

**Change ID**: `rvrb-providers` | **Date**: 2026-07-07

## 1. Component Architecture

```
src/rvrb_providers/
├── __init__.py        ← Re-exports, __all__
├── models.py          ← ToolCall, ToolResult, error hierarchy
├── base.py            ← ModelProvider ABC (3 abstract methods)
├── qwen.py            ← QwenProvider — DashScope wrapper
├── openai.py          ← OpenAIProvider — native OpenAI
├── local.py           ← LocalProvider — Ollama/vLLM
├── fallback.py        ← FallbackProvider — chain-of-responsibility
└── factory.py         ← get_provider(), list_providers()
```

**7 modules, 8 classes, ~400 lines.**

| Module | Responsibility |
|--------|---------------|
| `__init__.py` | Re-exports: `get_provider`, `list_providers`, `ModelProvider`, `ProviderError`, `QuotaExhaustedError`, `AllProvidersExhaustedError`, `ToolCall`, `ToolResult` |
| `models.py` | Pydantic: `ToolCall`, `ToolResult`. Exception: `ProviderError(RuntimeError)`, `QuotaExhaustedError(ProviderError)`, `AllProvidersExhaustedError(Exception)` |
| `base.py` | `ModelProvider(ABC)` with `__init__(self, api_key, model, base_url)` + 3 `@abstractmethod`: `complete()`, `complete_structured()`, `complete_with_tools()` |
| `qwen.py` | `QwenProvider(ModelProvider)`. DashScope endpoint, timeout=60s, quota detection (429+FreeTierOnly), `last_quota_remaining` property |
| `openai.py` | `OpenAIProvider(ModelProvider)`. No quota logic, default model `gpt-4` |
| `local.py` | `LocalProvider(ModelProvider)`. Default `http://127.0.0.1:11434/v1`, model `qwen2.5`, no auth |
| `fallback.py` | `FallbackProvider(ModelProvider)`. Catches `QuotaExhaustedError`, tries next. `AllProvidersExhaustedError` when chain empty |
| `factory.py` | `get_provider(name=None) -> ModelProvider`, `list_providers() -> list[str]`, colon format parser |

## 2. Data Structures

### 2.1 Error Hierarchy

```
RuntimeError
  └── ProviderError(model_id: str, status_code: int, body: str | None = None)
        └── QuotaExhaustedError(model_id: str, status_code: int, body: str | None = None)
Exception
  └── AllProvidersExhaustedError(exhausted_model_ids: list[str])
```

- `status_code=0` for non-HTTP errors (timeout, connection failure)
- `FallbackProvider` uses `isinstance(exc, QuotaExhaustedError)` to decide chain vs propagate

### 2.2 ToolCall / ToolResult

```python
class ToolCall(BaseModel):
    id: str
    name: str
    arguments: dict

class ToolResult(BaseModel):
    content: str | None = None
    tool_calls: list[ToolCall] = Field(default_factory=list)
```

### 2.3 Provider State (QwenProvider)

| Attribute | Type | Initial |
|-----------|------|---------|
| `model` | `str` | constructor arg or `"qwen3-coder-plus"` |
| `last_quota_remaining` | `int \| None` (property) | `None` |

### 2.4 Factory Registry (internal)

```python
_PROVIDER_REGISTRY = {
    "qwen": "rvrb_providers.qwen.QwenProvider",
    "openai": "rvrb_providers.openai.OpenAIProvider",
    "local": "rvrb_providers.local.LocalProvider",
    "fallback": "rvrb_providers.fallback.FallbackProvider",
}
```

## 3. Interface Contracts

### 3.1 `complete(messages: list[dict], **kwargs) -> str`

Data flow:
```
Caller → complete(messages, temperature=0.7)
  → payload = {model, messages, max_tokens: kwargs.pop("max_tokens", 4096), **kwargs}
  → client.chat.completions.create(**payload)
  → 200: return response.choices[0].message.content
       QwenProvider also: self._last_quota_remaining = int(response.headers["x-qwen-quota-remaining"])
  → 429 + "AllocationQuota.FreeTierOnly" in body: raise QuotaExhaustedError
  → other errors: raise ProviderError
```

### 3.2 `complete_structured(messages: list[dict], output_type: type[BaseModel], **kwargs) -> BaseModel`

Data flow:
```
Caller → complete_structured(messages, MyModel)
  → schema = output_type.model_json_schema()
  → response_format = {"type":"json_schema", "json_schema":{"name":..., "schema":schema, "strict":true}}
  → client.chat.completions.create(model=..., messages=..., response_format=response_format, **kwargs)
  → 200: return output_type.model_validate_json(response.choices[0].message.content)
       JSON parse failure or pydantic ValidationError → ProviderError
```

Does NOT call `self.complete()` — injects `response_format` directly.

### 3.3 `complete_with_tools(messages: list[dict], tools: list[dict], **kwargs) -> ToolResult`

Data flow:
```
Caller → complete_with_tools(messages, tools=[{type:"function", function:{...}}])
  → payload + tools + tool_choice="auto"
  → 200:
    ├─ .tool_calls non-empty → ToolResult(content=msg.content, tool_calls=[ToolCall(...)])
    └─ .tool_calls empty → ToolResult(content=msg.content, tool_calls=[])
```

Edge: `json.loads("{}")` on empty arguments → `{}`. Defensive catch for malformed JSON.

## 4. Factory: Colon-Separated Name Format

`get_provider(name: str | None) -> ModelProvider`

| Input | Result |
|-------|--------|
| `None` | Read `RVRRB_PROVIDER` env, default `"qwen"` |
| `"qwen"` | `QwenProvider()` with env defaults |
| `"qwen:qwen3.7-plus"` | `QwenProvider(model="qwen3.7-plus")` |
| `"openai:gpt-4-turbo"` | `OpenAIProvider(model="gpt-4-turbo")` |
| `"local:llama3"` | `LocalProvider(model="llama3")` |
| `"fallback"` | Parse `RVRB_FALLBACK_PROVIDERS` env, recursive `get_provider()` per entry, wrap `FallbackProvider` |
| `"fallback:anything"` | `ValueError` — fallback doesn't accept model override |
| `"a:b:c"` | `ValueError` — only 1-2 parts allowed |
| `"nonexistent"` | `ValueError("Unknown provider: 'nonexistent'")` |

Name is case-insensitive. Split on `:`, max 2 parts. Fallback entry does not pass model override to children — the comma-separated env var entries each use their own colon format.

**Fallback env parsing** (`RVRRB_FALLBACK_PROVIDERS="qwen:qwen3-coder-plus,qwen:qwen3-coder-flash,openai"`):
1. Split on `,`, strip whitespace
2. For each entry: `get_provider(entry.strip())`
3. `FallbackProvider(providers)`
4. If env var empty/unset: `ValueError`

## 5. Env Var Reference

| Variable | Provider | Default |
|----------|----------|---------|
| `RVRB_PROVIDER` | factory | `"qwen"` |
| `DASHSCOPE_API_KEY` | QwenProvider | (required) |
| `OPENAI_API_KEY` | OpenAIProvider | (required) |
| `RVRB_LOCAL_BASE_URL` | LocalProvider | `"http://127.0.0.1:11434/v1"` |
| `RVRB_FALLBACK_PROVIDERS` | FallbackProvider | (required) |

## 6. Provider Construction

### QwenProvider

```python
QwenProvider(api_key=None, model="qwen3-coder-plus", base_url=None)
```
- `api_key` → `os.environ["DASHSCOPE_API_KEY"]` (raises ValueError if missing)
- `base_url` → `"https://dashscope-intl.aliyuncs.com/compatible-mode/v1"`
- `timeout=60.0`, `max_tokens=4096`
- Quota detection: catch `openai.APIStatusError`, check body string for `"AllocationQuota.FreeTierOnly"`

### OpenAIProvider

```python
OpenAIProvider(api_key=None, model="gpt-4", base_url=None)
```
- `api_key` → `os.environ["OPENAI_API_KEY"]` (raises ValueError if missing)
- `base_url=None` → OpenAI default endpoint
- No quota logic

### LocalProvider

```python
LocalProvider(api_key=None, model="qwen2.5", base_url=None)
```
- `base_url` → `os.environ["RVRB_LOCAL_BASE_URL"]` or `"http://127.0.0.1:11434/v1"`
- `api_key` not enforced — uses `"not-needed"` placeholder

### FallbackProvider

```python
FallbackProvider(providers: list[ModelProvider])
```
- `FallbackProvider([])` → `ValueError`
- `complete()` loop: catch `QuotaExhaustedError` → try next. Other errors propagate.
- Logs each fallback step to stderr: `[fallback] {model_id} exhausted, trying next.`
- All exhausted → `AllProvidersExhaustedError([model_ids])`

## 7. Error Handling Matrix

| Condition | Response |
|-----------|----------|
| Missing API key at construct | `ValueError` |
| HTTP 429 + FreeTierOnly (Qwen) | `QuotaExhaustedError(model_id, 429, body)` → triggers fallback |
| HTTP 429 without FreeTierOnly | `ProviderError(model_id, 429, body)` → propagates, no fallback |
| HTTP 401 | `ProviderError(model_id, 401, body)` → propagates |
| HTTP 5xx | `ProviderError(model_id, status_code, body)` → propagates |
| Network timeout | `ProviderError(model_id, 0, str(exc))` → propagates |
| Invalid JSON in structured response | `ProviderError(model_id, 200, "Invalid JSON: ...")` |
| Validation failure structured | `ProviderError(model_id, 200, "Validation failed: ...")` |
| Unknown provider name | `ValueError` |
| All fallback providers exhausted | `AllProvidersExhaustedError([model_ids])` |

## 8. Edge Cases

1. **Empty messages** → pass to API, let it 400 → `ProviderError`
2. **QwenProvider with non-Qwen model** → API rejects, caller's responsibility
3. **max_tokens=0 or None in kwargs** → overrides default 4096 (intentional)
4. **Fallback with mixed types** → Qwen raises QuotaExhaustedError, OpenAI 429 is ProviderError → chain stops correctly
5. **Tool calls with empty arguments** → `{}` default
6. **`RVRRB_PROVIDER` set but explicit name given** → explicit name wins
7. **Concurrent `last_quota_remaining` reads** → safe (read-only property)

## 9. Test Strategy

All mocked. No real API calls. Coverage: all public methods, all error paths, factory with all name formats.

| Test File | Classes |
|-----------|---------|
| `test_models.py` | `TestProviderError`, `TestToolResult` |
| `test_base.py` | `TestModelProvider` — ABC enforcement |
| `test_qwen.py` | `TestQwenProvider`, `TestQwenComplete`, `TestQwenQuotaExhausted`, `TestQwenHeaderCapture`, `TestQwenStructured`, `TestQwenTools` |
| `test_openai.py` | `TestOpenAIProvider` |
| `test_local.py` | `TestLocalProvider` |
| `test_fallback.py` | `TestFallbackProvider`, `TestAllExhausted`, `TestEmptyChain`, `TestNonQuotaPropagation` |
| `test_factory.py` | `TestGetProvider`, `TestColonFormat`, `TestFallbackFactory`, `TestListProviders`, `TestUnknownProvider`, `TestCaseInsensitive` |

Key fixture: `mock_openai_client` patches `openai.OpenAI().chat.completions.create`.

## 10. Traceability

| AC | Coverage |
|:--:|----------|
| AC-1 | §1 module structure, `__init__.py` exports, `pyproject.toml` |
| AC-2 | §3.1 `complete()` data flow, §6 QwenProvider construction |
| AC-3 | §2.1 error hierarchy, §3.1 quota detection, §7 error matrix |
| AC-4 | §2.3 `last_quota_remaining` property, §3.1 header capture |
| AC-5 | §3.2 complete_structured flow, `strict:true`, model_validate_json |
| AC-6 | §3.3 complete_with_tools, §2.2 ToolResult/ToolCall models |
| AC-7 | §6 FallbackProvider, §8.5 mixed types, §7 error matrix |
| AC-8 | §4 colon format table, §5 env vars, §6 per-provider defaults |
| AC-9 | §4 fallback env var parsing, recursive get_provider() |
| AC-10 | §9 test matrix, mock_openai_client fixture, zero real API calls |

## 11. Files

| File | Action |
|------|--------|
| `src/rvrb_providers/__init__.py` | CREATE |
| `src/rvrb_providers/models.py` | CREATE |
| `src/rvrb_providers/base.py` | CREATE |
| `src/rvrb_providers/qwen.py` | CREATE |
| `src/rvrb_providers/openai.py` | CREATE |
| `src/rvrb_providers/local.py` | CREATE |
| `src/rvrb_providers/fallback.py` | CREATE |
| `src/rvrb_providers/factory.py` | CREATE |
| `tests/conftest.py` | CREATE |
| `tests/test_models.py` | CREATE |
| `tests/test_base.py` | CREATE |
| `tests/test_qwen.py` | CREATE |
| `tests/test_openai.py` | CREATE |
| `tests/test_local.py` | CREATE |
| `tests/test_fallback.py` | CREATE |
| `tests/test_factory.py` | CREATE |
| `pyproject.toml` | CREATE |
