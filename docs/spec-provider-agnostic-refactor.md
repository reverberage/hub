# SDD Spec: provider-agnostic-refactor

**Change ID**: `provider-agnostic-refactor` | **Phase**: 3 — Spec | **Date**: 2026-07-13

---

## 1. Goals

1. **Configurable provider defaults**: Replace all hardcoded Qwen model/URL defaults in n3rverberage and satellites with env-var-driven configuration. System must resolve provider parameters (model, base URL, API key) from environment variables with sensible fallbacks, not from source-code constants.

2. **Provider-agnostic satellite fallbacks**: When n3rverberage is not installed, satellite fallback paths must work with any OpenAI-compatible provider (Qwen, OpenAI, local Ollama/vLLM), not just Qwen/DashScope.

3. **MockProvider in scaffold**: `scripts/scaffold-satellite.py` must generate a `MockProvider` class in the scaffolded test suite that implements the `ModelProvider` Protocol by structure (no inheritance), enabling engine tests with zero network calls.

4. **Remove Qwen-specific error handling from satellites**: Satellite code (`rvrb-transcriber`, `rvrb-verify`) must not contain Qwen-specific error codes (`AllocationQuota.FreeTierOnly`), Qwen-specific HTTP headers (`x-qwen-quota-remaining`), or any DashScope-specific API behavior.

5. **CLI `--provider` flag**: Satellites must accept a `--provider` CLI flag to select from available provider names (`qwen`, `openai`, `local`) at runtime, overriding `N3RVERBERAGE_PROVIDER`.

## 2. Non-Goals

What this change explicitly does NOT do:

| Item | Reason |
|------|--------|
| Rename `DASHSCOPE_API_KEY` | 100+ references, high blast radius, deferred |
| Generic TTS abstraction | Only Qwen-TTS used today, YAGNI |
| Plugin/registry provider system | Factory exists, 3 providers not enough to justify |
| Refactor `qwen_fallback.py` to multi-provider | Script's job is Qwen quota rotation specifically |
| Rename opencode template provider key `"qwen"` | Breaks init→template→fallback chain |
| Add non-Qwen TTS providers | No demand, add when needed |
| Cross-provider integration test pipeline | Requires multi-provider API keys, future work |
| Rename n3rverberage init template variables | Internal to init, separate change |

## 3. Acceptance Criteria

Every criterion is binary testable (pass/fail, no judgment calls). Test command shown is the verification method.

### AC-1: No hardcoded DEFAULT_MODEL in non-Qwen-specific code
**Verify**: `grep -r "DEFAULT_MODEL.*=.*qwen"` across n3rverberage and all satellite `src/` directories returns zero matches in files that are NOT QwenProvider itself.

**Pass**: zero matches outside `providers/qwen.py`. **Fail**: any match elsewhere.

### AC-2: No hardcoded dashscope BASE_URL in satellites (except fallback maps)
**Verify**: `grep -r "dashscope" src/rvrb_transcriber/ src/rvrb_verify/` returns zero matches in files
that are NOT `provider.py` fallback maps.

**Pass**: zero matches outside provider fallback maps. Satellite `_PROVIDER_FALLBACKS` maps MAY
contain the Qwen dashscope URL as the default for the `qwen` provider entry — this is required for
standalone operation.  **Fail**: any dashscope reference in engine code, CLI, models, or tests.

### AC-3: N3RVERBERAGE_DEFAULT_MODEL env var controls default model
**Verify**: 
```bash
N3RVERBERAGE_DEFAULT_MODEL=gpt-4 python -c "from rvrb_verify.provider import DEFAULT_MODEL; print(DEFAULT_MODEL)"
# Output must be: gpt-4
```
**Pass**: output matches env var. **Fail**: output is `qwen3-coder-plus` or any other value.

### AC-4: N3RVERBERAGE_DEFAULT_BASE_URL env var controls default base URL
**Verify**:
```bash
N3RVERBERAGE_DEFAULT_BASE_URL=https://api.openai.com/v1 python -c "from rvrb_verify.provider import DEFAULT_BASE_URL; print(DEFAULT_BASE_URL)"
# Output must be: https://api.openai.com/v1
```
**Pass**: output matches env var. **Fail**: output is `dashscope-intl.aliyuncs.com`.

### AC-5: Backward compatibility — zero new env vars
**Verify**: With NO new env vars set (`unset N3RVERBERAGE_DEFAULT_MODEL N3RVERBERAGE_DEFAULT_BASE_URL`), run:
```bash
pytest  # n3rverberage
pytest  # transcriber
pytest  # verify
pytest tests/  # hub
```
**Pass**: 100% of existing tests pass. **Fail**: any test failure.

### AC-6: Satellite fallback without n3rverberage uses env-var provider (OpenAI)
**Verify**: In a venv WITHOUT n3rverberage:
```bash
N3RVERBERAGE_PROVIDER=openai \
OPENAI_API_KEY=sk-test \
N3RVERBERAGE_DEFAULT_BASE_URL=https://api.openai.com/v1 \
N3RVERBERAGE_DEFAULT_MODEL=gpt-4 \
python -c "from rvrb_verify.provider import get_provider; p = get_provider(); print(p.base_url, p.model)"
```
Output must reference `api.openai.com` and `gpt-4`, NOT `dashscope` or `qwen3-coder-plus`.

**Pass**: fallback provider uses configured OpenAI params. **Fail**: uses hardcoded Qwen defaults.

### AC-7: Satellite fallback without n3rverberage uses env-var provider (local)
**Verify**: Same as AC-6 but with:
```bash
N3RVERBERAGE_PROVIDER=local \
N3RVERBERAGE_DEFAULT_BASE_URL=http://localhost:11434/v1 \
N3RVERBERAGE_DEFAULT_MODEL=llama3
```
Output must reference `localhost:11434` and `llama3`.

**Pass**: fallback provider uses configured local params. **Fail**: rejects non-Qwen configuration.

### AC-8: No Qwen-specific error codes in satellite source
**Verify**: `grep -r "FreeTierOnly\|AllocationQuota.FreeTierOnly\|x-qwen-quota-remaining" src/rvrb_transcriber/ src/rvrb_verify/` returns zero matches.

**Pass**: zero matches. **Fail**: any match.

### AC-9: No Qwen-specific error codes in satellite tests
**Verify**: `grep -r "FreeTierOnly\|AllocationQuota.FreeTierOnly\|x-qwen-quota-remaining"` across transcriber/ and verify/ test directories returns zero matches.

**Pass**: zero matches. **Fail**: any match.

### AC-10: MockProvider in scaffolded test suite
**Verify**:
```bash
python scripts/scaffold-satellite.py test_satellite
grep -A 30 "class MockProvider" test_satellite/tests/conftest.py
```
Must contain a class named `MockProvider` with:
- Attribute: `model: str`
- Attribute: `base_url: str`
- Method: `complete(messages, **kwargs) -> str`
- Method: `complete_structured(messages, output_type, **kwargs) -> BaseModel`
- Method: `complete_with_tools(messages, tools, **kwargs) -> ToolResult`
- No inheritance (no parentheses after class name, or inherits only from `object`)

**Pass**: all 5 members present, no ABC/Protocol inheritance. **Fail**: missing method, or inherits from Protocol/ABC.

### AC-11: MockProvider works without network
**Verify**: In scaffolded satellite, add a test:
```python
def test_engine_with_mock_provider():
    from rvrb_test_satellite.engine import TestSatelliteEngine
    from tests.conftest import MockProvider
    engine = TestSatelliteEngine(provider=MockProvider())
    result = engine.action("test input")
    assert result is not None
```
Run with `pytest --offline` (or in an environment without network). Test must pass.

**Pass**: test passes, zero network activity. **Fail**: test fails or attempts HTTP call.

### AC-12: Scaffolded satellite fallback defaults use env-var-driven values
**Verify**: Run `python scripts/scaffold-satellite.py test_satellite`, then:
```bash
grep -r "qwen\|dashscope" test_satellite/src/
```
The fallback map in `provider.py` WILL reference Qwen defaults — this is required for standalone
operation when no env vars are set.

**Pass**: The only Qwen/dashscope references are in `provider.py`'s `_PROVIDER_FALLBACKS` map and/or
`DEFAULT_MODEL`/`DEFAULT_BASE_URL` env-var fallbacks. Engine code, CLI, models, and tests are
free of Qwen-specific logic. MockProvider returns `"mock-model"` — not a Qwen model ID.

**Fail**: Qwen/dashscope references appear outside the provider fallback map, or MockProvider
references a real model ID.

### AC-13: `--provider` CLI flag exists
**Verify**: In any satellite: `rvrb-<name> --help` output includes:
```
--provider TEXT   Provider name: qwen, openai, local  [default: qwen]
```
Running `rvrb-<name> --provider openai ...` must resolve to the OpenAI provider path.

**Pass**: flag in help, functional resolution. **Fail**: flag missing or non-functional.

### AC-14: `--provider` CLI flag overrides env var
**Verify**:
```bash
N3RVERBERAGE_PROVIDER=qwen rvrb-verify --provider openai --help
# Provider resolution must use 'openai', not 'qwen'
```
**Pass**: CLI flag takes precedence over env var. **Fail**: env var takes precedence.

### AC-15: Qwen remains default when no config specified
**Verify**: With NO env vars set (no `N3RVERBERAGE_PROVIDER`, `N3RVERBERAGE_DEFAULT_MODEL`, `N3RVERBERAGE_DEFAULT_BASE_URL`), and n3rverberage installed:
```python
from n3rverberage.providers import get_provider
p = get_provider()
# p must be QwenProvider, base_url=dashscope, model=qwen3-coder-plus
```
**Pass**: default is Qwen/DashScope/qwen3-coder-plus. **Fail**: default changed or resolution fails.

### AC-16: qwen_fallback.py continues to function
**Verify**: `python scripts/qwen_fallback.py --status` runs to completion (with DASHSCOPE_API_KEY set). Outputs status table. Exits 0 or 1 (1 if all exhausted — still functional).

**Pass**: script runs without new errors. **Fail**: script crashes with change-related error.

### AC-17: opencode template chain intact
**Verify**:
```bash
python scripts/qwen_fallback.py --rotate --model qwen3-coder-plus
# Verify opencode.json exists and is valid JSON
python -c "import json; json.load(open('opencode.json'))"
# Verify opencode can start (or at minimum, the config parses)
```
**Pass**: template substitution works, resulting JSON is valid, `{model}` placeholder consumed. **Fail**: template broken, invalid JSON, or opencode fails to parse config.

### AC-18: verify strategies use configurable model IDs
**Verify**: 
```bash
N3RVERBERAGE_VERIFY_SEARCH_MODEL=gpt-4 \
N3RVERBERAGE_VERIFY_JUDGE_MODEL=gpt-4 \
python -c "
from rvrb_verify.strategies.fact_check import FactCheckStrategy
# The strategy's model_search and model_judge must be 'gpt-4'
"
```
**Pass**: strategy model IDs follow env vars. **Fail**: strategy ignores env var, uses Qwen defaults.

### AC-19: Centralized defaults in n3rverberage
**Verify**:
```python
from n3rverberage.config import DEFAULTS
assert hasattr(DEFAULTS, 'provider')   # "qwen"
assert hasattr(DEFAULTS, 'model')      # "qwen3-coder-plus"
assert hasattr(DEFAULTS, 'base_url')   # "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
```
Verify satellites do NOT duplicate these defaults as string literals OUTSIDE their provider fallback maps:
```bash
grep -r "qwen3-coder-plus" src/rvrb_verify/provider.py src/rvrb_transcriber/provider.py | grep -v "_PROVIDER_FALLBACKS\|_FALLBACKS"
# Must return zero (values sourced from config/env, not strings)
```

**Pass**: `DEFAULTS` exists with all three fields; satellites resolve from config/env, not strings. Satellite fallback maps MAY reference Qwen defaults as part of a multi-provider map — this is required for standalone operation without n3rverberage. **Fail**: DEFAULTS missing, or satellites hardcode model/URL strings outside their fallback maps.

### AC-20: New env vars documented in satellite protocol
**Verify**: `docs/satellite-protocol-v2.md` contains documentation for:
- `N3RVERBERAGE_DEFAULT_MODEL` (default: `qwen3-coder-plus`)
- `N3RVERBERAGE_DEFAULT_BASE_URL` (default: `https://dashscope-intl.aliyuncs.com/compatible-mode/v1`)
- `N3RVERBERAGE_VERIFY_SEARCH_MODEL` (default: `qwen3-coder-plus`)
- `N3RVERBERAGE_VERIFY_JUDGE_MODEL` (default: `qwen3.7-plus`)
- `N3RVERBERAGE_PROVIDER` (already documented, verify still present)

**Pass**: all 5 env vars documented with defaults. **Fail**: any missing.

## 4. Constraints

1. **Backward compatibility**: When no new env vars are set (`N3RVERBERAGE_DEFAULT_MODEL`, `N3RVERBERAGE_DEFAULT_BASE_URL`, etc.), behavior must be 100% identical to current behavior. Qwen/DashScope remains the implicit default.

2. **Existing tests**: All existing test suites (n3rverberage, hub, transcriber, verify) must pass without modification. Test assertion changes ARE permitted if the assertion was testing for the hardcoded Qwen string (e.g., `assert model == "qwen3-coder-plus"` → `assert model == os.environ.get("N3RVERBERAGE_DEFAULT_MODEL", "qwen3-coder-plus")`).

3. **opencode template chain**: `opencode.template.json` → `qwen_fallback.py` → `opencode.json` must remain fully functional. The `{model}` substitution must continue to work. The provider block named `"qwen"` must NOT be renamed.

4. **qwen_fallback.py scope**: This script manages Qwen/DashScope quota rotation. It must NOT be refactored into a generic multi-provider rotator. Its Qwen-specific nature is intentional and correct for its purpose.

5. **n3rverberage init templates**: Templates in `n3rverberage/init/templates/` may receive new variables for default config injection, but must not change their output format or naming conventions.

6. **No new dependencies**: Satellites must not gain new runtime dependencies. env-var resolution and provider construction must use stdlib + `openai` package only (same as current).

7. **API key env vars**: `DASHSCOPE_API_KEY`, `OPENAI_API_KEY` names stay as-is. No generic `API_KEY` unification.

## 5. Out of Scope

| Item | Reason |
|------|--------|
| Renaming `DASHSCOPE_API_KEY` to generic name | 100+ references, high blast radius, low value. Future change. |
| Generic TTS interface (`TTSProvider` ABC) | Only Qwen-TTS used today. YAGNI. Add when second TTS provider needed. |
| Plugin/provider registry system | ModelProvider factory already exists. Overkill for 3 providers. |
| Refactoring `qwen_fallback.py` to multi-provider rotation | Script manages Qwen-specific quota pools. Different problem. |
| opencode template provider naming (`"qwen"` key) | Breaks init→template→fallback chain. Requires coordinated change. |
| Cross-provider integration test pipeline | Requires multi-provider API keys. Infrastructure work. Future. |
| Non-Qwen TTS providers (OpenAI TTS, ElevenLabs) | No demand. Add when needed. |
| Modifying n3rverberage init context.json variable names | Internal to init. Separate change_id. |
| Adding providers for Anthropic, Google, Mistral, etc. | Only 3 providers exist. Add when satellite demand exists. |
| Scaffolded satellite --provider flag | Satellites inherit from protocol; scaffold generates pattern. |

## 6. Traceability Matrix

| AC | Title | Property Tested |
|:--:|-------|----------------|
| AC-1 | No hardcoded DEFAULT_MODEL outside QwenProvider | Configurability |
| AC-2 | No hardcoded dashscope URL in satellites | Decoupling |
| AC-3 | N3RVERBERAGE_DEFAULT_MODEL env var | Configurability |
| AC-4 | N3RVERBERAGE_DEFAULT_BASE_URL env var | Configurability |
| AC-5 | Zero env vars backward compat | Stability |
| AC-6 | Satellite fallback OpenAI without n3rverberage | Decoupling |
| AC-7 | Satellite fallback local without n3rverberage | Decoupling |
| AC-8 | No Qwen errors in satellite src | Decoupling |
| AC-9 | No Qwen errors in satellite tests | Decoupling |
| AC-10 | MockProvider in scaffold | Testability |
| AC-11 | MockProvider works offline | Testability |
| AC-12 | Scaffolded satellite no Qwen defaults | Configurability |
| AC-13 | --provider CLI flag | Usability |
| AC-14 | --provider overrides env var | Usability |
| AC-15 | Qwen default preserved | Stability |
| AC-16 | qwen_fallback.py intact | Stability |
| AC-17 | opencode template chain intact | Stability |
| AC-18 | verify strategies configurable | Configurability |
| AC-19 | Centralized DEFAULTS config | Architecture |
| AC-20 | Protocol docs updated | Documentation |
