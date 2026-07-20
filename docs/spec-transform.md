# SDD Spec: transform

**Change ID**: `transform` | **Phase**: 3 — Spec | **Date**: 2026-07-19

---

## 1. Goals

1. **Create `rvrb-transform` satellite**: A new pip-installable Python package (`rvrb-transform`, importable as `rvrb_transform`) in the reverberage ecosystem that transforms text based on natural language instructions. Built with hatchling, Python >=3.11, Apache-2.0.

2. **Single general-purpose transform engine**: `TransformEngine(provider).transform(text, instruction) -> str`. One public method. No modes, no enums, no strategy pattern. The engine constructs a system prompt + user message, calls `provider.complete()`, and returns the raw response.

3. **Mandatory kernel compliance**: Every module required by protocol v2 is present and correctly structured: `__init__.py` (package metadata, public API re-exports), `models.py` (domain types + `MediaModality` enum + `MediaInput` + `MediaOutput` + `TransformResult`), `provider.py` (`ModelProvider` Protocol + `DEFAULT_MODEL` + `DEFAULT_BASE_URL` + `get_provider()` factory), `engine.py` (`TransformEngine` with constructor-injected provider).

4. **Optional CLI**: Typer-based CLI at `rvrb-transform [TEXT] [INSTRUCTION...]` with stdin fallback, `--json`, `--model`, `--provider`, `--output` flags. Exit codes: 0 success, 1 failure.

5. **Optional MCP server**: `rvrb-transform-mcp` entry point exposing the transform as an MCP tool via `mcp.server.FastMCP`. Gated import — MCP is optional.

6. **Protocol v2 provider contract**: Provider resolution follows the standard satellite pattern: try `n3rverberage.providers.get_provider()` first, fall back to `_GenericProvider` (OpenAI-compatible client with env-var-driven defaults). No Qwen-specific logic outside `_PROVIDER_FALLBACKS` map. `--provider` CLI flag overrides `N3RVERBERAGE_PROVIDER`.

7. **Mock-ready testing**: Test suite includes a standalone `MockProvider` implementing `ModelProvider` by structure (no inheritance, no `MagicMock`). Engine tests pass with zero network calls. CLI tests use `typer.testing.CliRunner`. All tests pass with `--offline`.

## 2. Non-Goals

| Item | Reason |
|------|--------|
| Typed transform modes (`TransformMode` enum, `--mode` flag) | YAGNI. Single method covers all cases via natural language. |
| Composable pipeline subcommands (`rvrb-transform summarize`, etc.) | Over-engineered. Single invocation per transform, pipe for composition. |
| io.py module | TEXT->TEXT satellite. No file I/O beyond stdin/stdout. |
| Multiple model phases (search + judge like verify) | Single-phase transform. One LLM call per invocation. |
| Per-transform-type system prompts | Single prompt template. LLM understands natural language instructions. |
| rich/TUI dependency | Plain `typer.echo()`. No terminal formatting library. |
| n3rverberage as hard dependency | Optional import fallback pattern. Satellite works standalone. |
| Transform-specific error taxonomy | Provider errors bubble up with context. No custom error hierarchy. |
| Streaming output | Synchronous single response. No demand. |
| Batch/multi-file transforms | Single input, single output per invocation. Compose externally. |

## 3. Acceptance Criteria

Every criterion is binary testable (pass/fail). Test command shown is the verification method.

### AC-1: Mandatory kernel modules present
**Verify**:
```bash
ls src/rvrb_transform/__init__.py src/rvrb_transform/models.py \
   src/rvrb_transform/provider.py src/rvrb_transform/engine.py
```
**Pass**: all four files exist with non-zero size. **Fail**: any file missing or empty.

### AC-2: No io.py (text-only satellite)
**Verify**:
```bash
test ! -f src/rvrb_transform/io.py
```
**Pass**: file does not exist. **Fail**: `io.py` exists.

### AC-3: __init__.py exports public API
**Verify**:
```python
from rvrb_transform import TransformEngine, TransformResult, MediaModality, MediaInput, MediaOutput
from rvrb_transform.provider import ModelProvider, get_provider, DEFAULT_MODEL, DEFAULT_BASE_URL
```
**Pass**: all 8 symbols importable. **Fail**: any symbol fails to import.

### AC-4: TransformEngine constructor injection
**Verify**:
```python
from rvrb_transform.engine import TransformEngine

class DummyProvider:
    model = "test"
    base_url = "http://test"
    def complete(self, messages, **kwargs): return "ok"
    def complete_structured(self, messages, output_type, **kwargs): return output_type()
    def complete_with_tools(self, messages, tools, **kwargs): return None

engine = TransformEngine(provider=DummyProvider())
# Must succeed — no TypeError, no AttributeError
```
**Pass**: construction succeeds with a structurally-compatible provider. **Fail**: `TypeError`, `AttributeError`, or any exception.

### AC-5: Single public method — transform
**Verify**:
```python
engine = TransformEngine(provider=DummyProvider())
result = engine.transform("Hello world", "translate to Spanish")
assert result == "ok"
# dir(engine) must NOT contain other action methods besides 'transform' and 'provider'
```
**Pass**: single method call returns `str`. No other public action methods exist. **Fail**: multiple action methods, wrong return type, or method missing.

### AC-6: System prompt includes instruction
**Verify**: Use SpyProvider in tests that captures messages:
```python
class SpyProvider:
    model = "spy"; base_url = "spy://"
    def __init__(self): self.captured_messages = None
    def complete(self, messages, **kwargs):
        self.captured_messages = messages; return "result"
    def complete_structured(self, messages, output_type, **kwargs): return output_type()
    def complete_with_tools(self, messages, tools, **kwargs): return None

spy = SpyProvider()
TransformEngine(provider=spy).transform("Text to process", "make it uppercase")
# spy.captured_messages[0]["role"] == "system" and contains "transform"
# spy.captured_messages[1]["role"] == "user" and contains both "Text to process" and "make it uppercase"
```
**Pass**: system message describes transformation; user message contains both text and instruction. **Fail**: system prompt missing or empty, or user message missing text/instruction.

### AC-7: Temperature 0
**Verify**: Same SpyProvider — capture kwargs:
```python
# spy must track kwargs passed to complete()
# assert spy.kwargs["temperature"] in (0, 0.0)
```
**Pass**: `complete()` called with `temperature=0` or `0.0`. **Fail**: temperature not set, or set to non-zero.

### AC-8: No side effects in engine
**Verify**:
```python
# Engine must not call print(), open(), write(), or modify any global/module state
# Install a mock that raises on any I/O attempt
# engine.transform() must complete without triggering the mock
```
**Pass**: `transform()` does not write files, print to stdout, or modify global state. **Fail**: any I/O or global mutation.

### AC-9: MediaModality enum present
**Verify**:
```python
from rvrb_transform.models import MediaModality
assert MediaModality.TEXT == "text"
assert MediaModality.AUDIO == "audio"
assert MediaModality.IMAGE == "image"
assert MediaModality.VIDEO == "video"
assert len(MediaModality) == 4
```
**Pass**: 4 members with correct lowercase string values. **Fail**: missing members, wrong values, extra members.

### AC-10: MediaInput model
**Verify**:
```python
from rvrb_transform.models import MediaInput, MediaModality
from pathlib import Path
mi = MediaInput(path=Path("/tmp/test.txt"), modality=MediaModality.TEXT)
assert mi.path == Path("/tmp/test.txt")
assert mi.modality == MediaModality.TEXT
assert mi.metadata == {}
```
**Pass**: fields `path` (Path), `modality` (MediaModality), `metadata` (dict, default `{}`). **Fail**: wrong types or defaults.

### AC-11: MediaOutput model
**Verify**:
```python
from rvrb_transform.models import MediaOutput, MediaModality
mo = MediaOutput(data="transformed text")
assert mo.data == "transformed text"
assert mo.modality == MediaModality.TEXT
assert mo.format == "text"
```
**Pass**: `data` (str|bytes), `modality` (default TEXT), `format` (default "text"). **Fail**: wrong types or defaults.

### AC-12: TransformResult model
**Verify**:
```python
from rvrb_transform.models import TransformResult
result = TransformResult(
    input_text="hello", instruction="uppercase",
    output_text="HELLO", model="qwen3-coder-plus", provider="qwen",
    tokens_used=150
)
assert result.output_text == "HELLO"
assert result.tokens_used == 150
```
**Pass**: 5 required str fields + optional `tokens_used: int | None = None`. **Fail**: missing fields or wrong types.

### AC-13: ModelProvider Protocol present
**Verify**:
```python
from rvrb_transform.provider import ModelProvider
import typing
# Must be a Protocol, not an ABC
# Verify model: str, base_url: str, complete(), complete_structured(), complete_with_tools()
```
**Pass**: `ModelProvider` is a `Protocol` with correct attributes and 3 methods. **Fail**: not a Protocol, missing attr/methods, inherits from ABC.

### AC-14: DEFAULT_MODEL and DEFAULT_BASE_URL env-var-driven
**Verify**:
```bash
N3RVERBERAGE_DEFAULT_MODEL=gpt-4 \
N3RVERBERAGE_DEFAULT_BASE_URL=https://api.openai.com/v1 \
python -c "from rvrb_transform.provider import DEFAULT_MODEL, DEFAULT_BASE_URL; print(DEFAULT_MODEL); print(DEFAULT_BASE_URL)"
# Output: gpt-4\nhttps://api.openai.com/v1

unset N3RVERBERAGE_DEFAULT_MODEL N3RVERBERAGE_DEFAULT_BASE_URL
python -c "from rvrb_transform.provider import DEFAULT_MODEL, DEFAULT_BASE_URL; print(DEFAULT_MODEL); print(DEFAULT_BASE_URL)"
# Output: qwen3-coder-plus\nhttps://dashscope-intl.aliyuncs.com/compatible-mode/v1
```
**Pass**: env vars control values; fallback to Qwen defaults. **Fail**: env vars ignored or fallback wrong.

### AC-15: get_provider() fallback without n3rverberage
**Verify**:
```bash
N3RVERBERAGE_PROVIDER=openai \
OPENAI_API_KEY=sk-test \
N3RVERBERAGE_DEFAULT_BASE_URL=https://api.openai.com/v1 \
N3RVERBERAGE_DEFAULT_MODEL=gpt-4 \
python -c "from rvrb_transform.provider import get_provider; p = get_provider(); print(p.base_url, p.model)"
# Output: https://api.openai.com/v1 gpt-4
```
**Pass**: fallback provider uses configured OpenAI params. **Fail**: uses hardcoded Qwen defaults, or crashes.

### AC-16: get_provider() with n3rverberage installed
**Verify**:
```bash
# With n3rverberage installed and DASHSCOPE_API_KEY set:
python -c "from rvrb_transform.provider import get_provider; p = get_provider(); print(type(p).__name__)"
# Output must contain 'QwenProvider' (real provider, not Generic)
```
**Pass**: n3rverberage provider chain used when available. **Fail**: always uses fallback.

### AC-17: No Qwen-specific logic outside _PROVIDER_FALLBACKS
**Verify**:
```bash
grep -r "FreeTierOnly\|AllocationQuota\|x-qwen-quota-remaining" src/rvrb_transform/
```
**Pass**: zero matches. **Fail**: any match.

### AC-18: CLI entry point registered
**Verify**:
```bash
rvrb-transform --help
# Must show: TEXT, INSTRUCTION args, --prompt, --json, --model, --provider, --output
```
**Pass**: all flags present with correct types. **Fail**: any flag missing.

### AC-19: CLI reads from stdin when TEXT omitted
**Verify**:
```bash
echo "Hello world" | rvrb-transform "uppercase"
# Output: HELLO WORLD
```
**Pass**: reads from stdin when no positional TEXT. **Fail**: crashes, hangs, or ignores stdin.

### AC-20: CLI writes to stdout by default
**Verify**:
```bash
rvrb-transform "Hello" "reverse" 2>/dev/null
# Output goes to stdout, not stderr
```
**Pass**: output on stdout. **Fail**: output on stderr, or no output.

### AC-21: --json flag produces JSON output
**Verify**:
```bash
rvrb-transform "hello" "uppercase" --json 2>/dev/null | python -c "
import sys, json
d = json.load(sys.stdin)
assert d['output_text'] == 'HELLO'
assert 'input_text' in d and 'instruction' in d and 'model' in d and 'provider' in d
"
```
**Pass**: valid JSON with TransformResult schema. **Fail**: not valid JSON, missing fields.

### AC-22: --model flag overrides provider model
**Verify**:
```bash
rvrb-transform "hello" "uppercase" --model gpt-4 --json 2>/dev/null | python -c "
import sys, json; assert json.load(sys.stdin)['model'] == 'gpt-4'
"
```
**Pass**: model in JSON matches `--model` flag. **Fail**: flag ignored.

### AC-23: --provider flag overrides env var
**Verify**:
```bash
N3RVERBERAGE_PROVIDER=qwen rvrb-transform "hello" "uppercase" --provider openai --json 2>/dev/null | python -c "
import sys, json; assert json.load(sys.stdin)['provider'] == 'openai'
"
```
**Pass**: provider field is `"openai"`, overriding env var. **Fail**: env var takes precedence.

### AC-24: --output flag writes to file
**Verify**:
```bash
rvrb-transform "hello" "uppercase" --output /tmp/test_transform.txt
test -f /tmp/test_transform.txt && cat /tmp/test_transform.txt
# Output: HELLO (from file, not stdout)
```
**Pass**: file created with transformed text, nothing on stdout. **Fail**: file not created, or output on stdout.

### AC-25: Exit code 0 on success
**Verify**:
```bash
rvrb-transform "hello" "uppercase" > /dev/null 2>&1; echo $?
```
**Pass**: 0. **Fail**: non-zero.

### AC-26: Exit code 1 on provider failure
**Verify**:
```bash
OPENAI_API_KEY=invalid rvrb-transform "hello" "uppercase" 2>/dev/null; echo $?
```
**Pass**: exit 1, error message on stderr. **Fail**: exit 0, or crash/stack trace.

### AC-27: Exit code 1 with missing instruction
**Verify**:
```bash
rvrb-transform "hello" 2>/dev/null; echo $?
```
**Pass**: exit 1, error on stderr about missing instruction. **Fail**: exit 0, hangs, or crashes.

### AC-28: No --mode flag (YAGNI)
**Verify**:
```bash
rvrb-transform --help | grep -c "\-\-mode"
```
**Pass**: output is `0`. **Fail**: `--mode` flag exists.

### AC-29: MCP entry point registered
**Verify**:
```bash
python -c "from rvrb_transform.mcp import mcp, main; print(type(mcp).__name__)"
# Output: FastMCP
```
**Pass**: `mcp` is `FastMCP`, `main` exists. **Fail**: ImportError or wrong type.

### AC-30: MCP tool registered
**Verify**: `mcp` has a tool named `transform` accepting `input_text: str, instruction: str` → `dict`.
**Pass**: tool registered with correct signature. **Fail**: no transform tool, wrong params.

### AC-31: MCP gated import
**Verify**:
```bash
pip uninstall mcp -y 2>/dev/null
python -c "from rvrb_transform.mcp import main" 2>&1
# Output must mention pip install rvrb-transform[mcp]
```
**Pass**: helpful ImportError with pip install guidance. **Fail**: raw ImportError, or module imports without mcp.

### AC-32: MockProvider in test suite
**Verify**:
```bash
grep -A 20 "class MockProvider" tests/conftest.py
```
Must contain: `model: str`, `base_url: str`, `complete()`, `complete_structured()`, `complete_with_tools()`. No ABC/Protocol inheritance. No MagicMock.
**Pass**: all 5 members present, structural class. **Fail**: missing method, inherits Protocol/ABC, or uses MagicMock.

### AC-33: MockProvider works without network
**Verify**: Engine test with MockProvider passes with `--offline`. Zero network activity.
**Pass**: test passes, no HTTP calls. **Fail**: test fails or attempts HTTP.

### AC-34: CLI tests use CliRunner
**Verify**: `tests/test_cli.py` uses `typer.testing.CliRunner`, not `subprocess.run`.
**Pass**: CliRunner used. **Fail**: real subprocess calls.

### AC-35: All tests pass with --offline
**Verify**:
```bash
pytest --offline
```
**Pass**: 100% pass, zero network activity. **Fail**: any test failure or network call.

### AC-36: pyproject.toml configured correctly
**Verify**:
```python
import tomllib
with open('pyproject.toml', 'rb') as f: cfg = tomllib.load(f)
assert cfg['build-system']['build-backend'] == 'hatchling'
assert cfg['project']['name'] == 'rvrb-transform'
assert cfg['project']['requires-python'] == '>=3.11'
assert cfg['project']['license'] == 'Apache-2.0'
scripts = cfg['project']['scripts']
assert 'rvrb-transform' in scripts
assert 'rvrb-transform-mcp' in scripts
```
**Pass**: all assertions pass. **Fail**: any assertion fails.

### AC-37: MCP extra dependency declared
**Verify**:
```python
assert 'mcp' in cfg['project'].get('optional-dependencies', {})
```
**Pass**: `mcp` extra with `["mcp"]` value. **Fail**: missing optional-dependencies or mcp key.

### AC-38: No n3rverberage in hard dependencies
**Verify**:
```python
deps = cfg['project'].get('dependencies', [])
for dep in deps:
    assert 'n3rverberage' not in dep.lower(), f'n3rverberage found in hard dep: {dep}'
```
**Pass**: no n3rverberage in dependencies. **Fail**: n3rverberage listed as hard dep.

### AC-39: No rich dependency
**Verify**:
```python
for dep in deps:
    assert 'rich' not in dep.lower(), f'rich found in dep: {dep}'
```
**Pass**: no rich dependency. **Fail**: rich listed.

### AC-40: Linting passes
**Verify**:
```bash
ruff check src/rvrb_transform/ tests/
```
**Pass**: zero errors. **Fail**: any linting violation.

### AC-41: Type checking passes
**Verify**:
```bash
mypy src/rvrb_transform/
```
**Pass**: zero errors. **Fail**: any type error.

### AC-42: Pipe composition works
**Verify**:
```bash
echo "hello world" | rvrb-transform "capitalize" | rvrb-transform "reverse"
```
**Pass**: pipeline completes, exit 0, output is reverse of "Hello World". **Fail**: non-zero exit or broken pipeline.

### AC-43: JSON output is pipe-readable
**Verify**:
```bash
rvrb-transform "hello" "uppercase" --json | python -c "import sys, json; json.load(sys.stdin); print('valid')"
```
**Pass**: stdout contains valid JSON, exit 0. **Fail**: invalid JSON or JSON mixed with non-JSON.

## 4. Constraints

1. **Protocol v2 compliance**: Must follow every mandatory requirement in `docs/satellite-protocol-v2.md`. Kernel modules must be present and correctly named. `ModelProvider` must be a structural Protocol. `get_provider()` must use the n3rverberage-first fallback pattern.

2. **Provider-agnostic**: Must comply with all relevant acceptance criteria from `docs/spec-provider-agnostic-refactor.md` (ACs 1–20). No hardcoded Qwen model IDs outside `_PROVIDER_FALLBACKS` map. Default model resolved from `N3RVERBERAGE_DEFAULT_MODEL` env var.

3. **Single method engine**: `TransformEngine` must have exactly one public action method: `transform(text, instruction) -> str`. No mode dispatcher, no strategy pattern, no sub-methods.

4. **No side effects**: Engine must not write files, print to stdout/stderr, or modify module-level state. I/O happens in CLI layer only.

5. **No n3rverberage hard dependency**: `pyproject.toml` `dependencies` must not list `n3rverberage`. The provider resolution uses `try/except ImportError` at call time.

6. **No rich dependency**: CLI must use `typer.echo()` directly. No `rich.console.Console`, `rich.table.Table`, or similar.

7. **Temperature 0**: The engine must set `temperature=0` on the LLM call for deterministic output.

8. **Python >=3.11**: Minimum Python version constraint. Use `StrEnum` from stdlib `enum` (available since 3.11), not `str, Enum` workaround.

9. **Apache-2.0 license**: As per satellite protocol.

10. **Hatchling build backend**: As per satellite protocol. Python package build must use hatchling.

## 5. Out of Scope

| Item | Reason |
|------|--------|
| `io.py` module | TEXT->TEXT satellite. No audio/image/video I/O. |
| File format detection (magic bytes, mimetypes) | io.py is omitted entirely. |
| Typed transform modes (`TransformMode` enum, `--mode` flag) | Natural language covers all cases. YAGNI. |
| Per-mode optimized system prompts | Single prompt template. LLM handles variation. |
| Multi-model transform pipeline (search→judge like verify) | Single-phase transform. One call. |
| Streaming/chunked output | Synchronous response. No demand. |
| Batch processing (directory of files) | Single invocation, single output. Compose externally. |
| Token counting / quota management engine-side | Provider handles this. Engine reports `tokens_used` if available. |
| Progress bars or spinners | No rich dependency. |
| Satellite-specific MCP resources or prompts | Tool only, matching protocol v2 minimum. Resources/prompts deferred. |
| Custom error hierarchy beyond provider error wrapping | Provider errors bubble up with phase context. No transform-specific error types. |
| Configuration file support (toml/yaml) | CLI flags + env vars only. |
| Multilingual transform detection | User specifies language in instruction. LLM handles it. |
| Integration tests with real LLM | MockProvider for unit tests. Real LLM tests are infrastructure work (future change). |

## 6. Traceability Matrix

| AC | Title | Property Tested |
|:--:|-------|----------------|
| AC-1 | Mandatory kernel modules present | Structure |
| AC-2 | No io.py | Structure |
| AC-3 | __init__.py exports | Structure |
| AC-4 | Constructor injection | Engine |
| AC-5 | Single public method | Engine |
| AC-6 | System prompt includes instruction | Engine |
| AC-7 | Temperature 0 | Engine |
| AC-8 | No side effects | Engine |
| AC-9 | MediaModality enum | Models |
| AC-10 | MediaInput model | Models |
| AC-11 | MediaOutput model | Models |
| AC-12 | TransformResult model | Models |
| AC-13 | ModelProvider Protocol | Provider |
| AC-14 | Env-var-driven defaults | Provider |
| AC-15 | get_provider() fallback | Provider |
| AC-16 | get_provider() with n3rverberage | Provider |
| AC-17 | No Qwen hardcoding | Provider |
| AC-18 | CLI entry point | CLI |
| AC-19 | stdin fallback | CLI |
| AC-20 | stdout output | CLI |
| AC-21 | --json flag | CLI |
| AC-22 | --model flag | CLI |
| AC-23 | --provider flag | CLI |
| AC-24 | --output flag | CLI |
| AC-25 | Exit 0 on success | CLI |
| AC-26 | Exit 1 on failure | CLI |
| AC-27 | Exit 1 missing instruction | CLI |
| AC-28 | No --mode flag | CLI |
| AC-29 | MCP entry point | MCP |
| AC-30 | MCP tool registered | MCP |
| AC-31 | MCP gated import | MCP |
| AC-32 | MockProvider in tests | Testing |
| AC-33 | MockProvider no network | Testing |
| AC-34 | CliRunner for CLI tests | Testing |
| AC-35 | All tests offline | Testing |
| AC-36 | pyproject.toml config | Build |
| AC-37 | MCP extra dependency | Build |
| AC-38 | No n3rverberage hard dep | Build |
| AC-39 | No rich dependency | Build |
| AC-40 | Linting passes | Quality |
| AC-41 | Type checking passes | Quality |
| AC-42 | Pipe composition | Integration |
| AC-43 | JSON pipe-readable | Integration |

**Total**: 43 acceptance criteria across 9 categories.
