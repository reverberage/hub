# SDD Spec: see

**Change ID**: `see` | **Phase**: 3 — Spec | **Date**: 2026-07-19

---

## 1. Goals

1. **Create `rvrb-see` satellite**: A new pip-installable Python package (`rvrb-see`, importable as `rvrb_see`) in the reverberage ecosystem that performs image understanding using qwen3.7-plus vision capabilities. Built with hatchling, Python >=3.11, Apache-2.0.

2. **Single-method vision engine**: `SeeEngine(provider).see(image: MediaInput | str, prompt: str | None = None) -> SeeResult`. One public method. The engine encodes images as base64 data URIs, constructs a multimodal message, calls `provider.complete()`, and returns structured text output.

3. **Mandatory kernel compliance**: Every module required by protocol v2 is present: `__init__.py` (package metadata, public API re-exports), `models.py` (domain types + `MediaModality` + `MediaInput` + `MediaOutput` + `SeeResult`), `provider.py` (`ModelProvider` Protocol + `DEFAULT_MODEL` + `DEFAULT_BASE_URL` + `get_provider()` factory), `engine.py` (`SeeEngine` with constructor-injected provider).

4. **io.py for image I/O**: Since `see` handles IMAGE modality, `io.py` is REQUIRED with `read_media(path) -> MediaInput` and `write_media(output, path) -> None`. `read_media()` detects image format from file extension. `write_media()` writes text output.

5. **Optional CLI**: Typer-based CLI at `rvrb-see <image_path>` with stdin fallback for text, `--json`, `--model`, `--provider`, `--output`, `--prompt` flags. Exit codes: 0 success, 1 failure.

6. **Optional MCP server**: `rvrb-see-mcp` entry point exposing the see functionality as an MCP tool via `mcp.server.FastMCP`. Gated import — MCP is optional.

7. **Protocol v2 provider contract**: Provider resolution follows standard satellite pattern: try `n3rverberage.providers.get_provider()` first, fall back to `_GenericProvider` (OpenAI-compatible client with env-var-driven defaults). No Qwen-specific logic outside `_PROVIDER_FALLBACKS` map. `--provider` CLI flag overrides `N3RVERBERAGE_PROVIDER`.

8. **Mock-ready testing**: Test suite includes a standalone `MockProvider` implementing `ModelProvider` by structure (no inheritance, no `MagicMock`). Engine tests pass with zero network calls. CLI tests use `typer.testing.CliRunner`. I/O tests use `tmp_path` fixture. All tests pass with `--offline`.

## 2. Non-Goals

| Item | Reason |
|------|--------|
| Video input support | YAGNI. Video→text extraction requires separate modality handling. Future. |
| Object detection / bounding box extraction | Natural language description covers this. Structured extraction is a `extract` satellite concern. |
| Multiple image inputs per call | Add when pipeline use case emerges. Single image per call for now. |
| Image output (generation/editing) | Different modality (TEXT→IMAGE). Future `image-gen` satellite. |
| OCR-specific mode | qwen3.7-plus handles OCR inline via natural language prompts. |
| Image preprocessing (resize, crop, rotate) | CLI-only satellite. Preprocessing is the user's job. |
| Local image model fallback | qwen3.7-plus is vision-capable. No local vision model for fallback. |
| Streaming output | Synchronous single response. No demand. |
| Batch/directory processing | Single image per invocation. Compose with `xargs` or external tooling. |

## 3. Acceptance Criteria

Every criterion is binary testable (pass/fail). Test command shown is the verification method.

### AC-1: Mandatory kernel modules present
**Verify**:
```bash
ls src/rvrb_see/__init__.py src/rvrb_see/models.py \
   src/rvrb_see/provider.py src/rvrb_see/engine.py
```
**Pass**: all four files exist with non-zero size. **Fail**: any file missing or empty.

### AC-2: io.py present (IMAGE modality)
**Verify**:
```bash
test -f src/rvrb_see/io.py
```
**Pass**: file exists. **Fail**: file missing.

### AC-3: __init__.py exports public API
**Verify**:
```python
from rvrb_see import SeeEngine, SeeResult, MediaModality, MediaInput, MediaOutput
from rvrb_see.provider import ModelProvider, get_provider, DEFAULT_MODEL, DEFAULT_BASE_URL
from rvrb_see.io import read_media, write_media
```
**Pass**: all 10 symbols importable. **Fail**: any symbol fails to import.

### AC-4: SeeEngine constructor injection
**Verify**:
```python
from rvrb_see.engine import SeeEngine

class DummyProvider:
    model = "test"
    base_url = "http://test"
    def complete(self, messages, **kwargs): return "ok"
    def complete_structured(self, messages, output_type, **kwargs): return output_type()
    def complete_with_tools(self, messages, tools, **kwargs): return None

engine = SeeEngine(provider=DummyProvider())
# Must succeed — no TypeError, no AttributeError
```
**Pass**: construction succeeds with a structurally-compatible provider. **Fail**: `TypeError`, `AttributeError`, or any exception.

### AC-5: Single public method — see
**Verify**:
```python
engine = SeeEngine(provider=DummyProvider())
result = engine.see("Describe this image")
assert result.output_text == "ok"
# dir(engine) must NOT contain other action methods besides 'see' and 'provider'
```
**Pass**: single method call returns `SeeResult`. No other public action methods exist. **Fail**: multiple action methods, wrong return type, or method missing.

### AC-6: Engine encodes image as base64 data URI
**Verify**: Use SpyProvider in tests that captures messages:
```python
class SpyProvider:
    model = "spy"; base_url = "spy://"
    def __init__(self): self.captured_messages = None
    def complete(self, messages, **kwargs): self.captured_messages = messages; return "result"
    def complete_structured(self, messages, output_type, **kwargs): return output_type()
    def complete_with_tools(self, messages, tools, **kwargs): return None

spy = SpyProvider()
with open("/tmp/test_image.png", "wb") as f:
    f.write(b'\x89PNG\r\n\x1a\n' + b'\x00' * 100)  # minimal PNG
engine = SeeEngine(provider=spy)
engine.see("/tmp/test_image.png")
# spy.captured_messages must contain a message with content that is a list
# containing an entry with type: "image_url" and a data URI starting with "data:image/png;base64,"
```
**Pass**: image is sent as base64 data URI with correct MIME type. **Fail**: missing image_url block, wrong encoding, or raw bytes in message.

### AC-7: Engine accepts MediaInput
**Verify**:
```python
from rvrb_see.models import MediaInput, MediaModality
spy = SpyProvider()
engine = SeeEngine(provider=spy)
mi = MediaInput(path=Path("/tmp/test_image.png"), modality=MediaModality.IMAGE)
engine.see(mi)
# Must succeed — same as passing string path
```
**Pass**: `MediaInput` accepted as `see()` parameter. **Fail**: TypeError or wrong type handling.

### AC-8: Temperature 0
**Verify**: Same SpyProvider — capture kwargs:
```python
# spy must track kwargs passed to complete()
# assert spy.kwargs.get("temperature") in (0, 0.0)
```
**Pass**: `complete()` called with `temperature=0` or `0.0`. **Fail**: temperature not set, or set to non-zero.

### AC-9: No side effects in engine
**Verify**:
```python
# Engine must not call print(), open(), write(), or modify any global/module state
# Install a mock that raises on any I/O attempt
# engine.see() must complete without triggering the mock
```
**Pass**: `see()` does not write files, print to stdout, or modify global state. **Fail**: any I/O or global mutation.

### AC-10: MediaModality enum present
**Verify**:
```python
from rvrb_see.models import MediaModality
assert MediaModality.TEXT == "text"
assert MediaModality.AUDIO == "audio"
assert MediaModality.IMAGE == "image"
assert MediaModality.VIDEO == "video"
assert len(MediaModality) == 4
```
**Pass**: 4 members with correct lowercase string values. **Fail**: missing members, wrong values, extra members.

### AC-11: MediaInput model
**Verify**:
```python
from rvrb_see.models import MediaInput, MediaModality
from pathlib import Path
mi = MediaInput(path=Path("/tmp/test.png"), modality=MediaModality.IMAGE)
assert mi.path == Path("/tmp/test.png")
assert mi.modality == MediaModality.IMAGE
assert mi.metadata == {}
```
**Pass**: fields `path` (Path), `modality` (MediaModality), `metadata` (dict, default `{}`). **Fail**: wrong types or defaults.

### AC-12: MediaOutput model
**Verify**:
```python
from rvrb_see.models import MediaOutput, MediaModality
mo = MediaOutput(data="image description")
assert mo.data == "image description"
assert mo.modality == MediaModality.TEXT
assert mo.format == "text"
```
**Pass**: `data` (str|bytes), `modality` (default TEXT), `format` (default "text"). **Fail**: wrong types or defaults.

### AC-13: SeeResult model
**Verify**:
```python
from rvrb_see.models import SeeResult
result = SeeResult(
    description="A cat sitting on a chair",
    model="qwen3.7-plus",
    provider="qwen",
    tokens_used=150
)
assert result.description == "A cat sitting on a chair"
assert result.tokens_used == 150
```
**Pass**: fields: `description: str`, `model: str`, `provider: str`, `tokens_used: int | None = None`. **Fail**: missing fields or wrong types.

### AC-14: ModelProvider Protocol present
**Verify**:
```python
from rvrb_see.provider import ModelProvider
import typing
# Must be a Protocol, not an ABC
# Verify model: str, base_url: str, complete(), complete_structured(), complete_with_tools()
```
**Pass**: `ModelProvider` is a `Protocol` with correct attributes and 3 methods. **Fail**: not a Protocol, missing attr/methods, inherits from ABC.

### AC-15: DEFAULT_MODEL is qwen3.7-plus (vision model)
**Verify**:
```bash
unset N3RVERBERAGE_DEFAULT_MODEL
python -c "from rvrb_see.provider import DEFAULT_MODEL; print(DEFAULT_MODEL)"
# Output: qwen3.7-plus
```
**Pass**: default model is `qwen3.7-plus`, not `qwen3-coder-plus`. **Fail**: wrong default.

### AC-16: DEFAULT_MODEL and DEFAULT_BASE_URL env-var-driven
**Verify**:
```bash
N3RVERBERAGE_DEFAULT_MODEL=gpt-4o \
N3RVERBERAGE_DEFAULT_BASE_URL=https://api.openai.com/v1 \
python -c "from rvrb_see.provider import DEFAULT_MODEL, DEFAULT_BASE_URL; print(DEFAULT_MODEL); print(DEFAULT_BASE_URL)"
# Output: gpt-4o\nhttps://api.openai.com/v1
```
**Pass**: env vars control values; fallback to Qwen defaults. **Fail**: env vars ignored or fallback wrong.

### AC-17: get_provider() fallback without n3rverberage
**Verify**:
```bash
N3RVERBERAGE_PROVIDER=openai \
OPENAI_API_KEY=sk-test \
N3RVERBERAGE_DEFAULT_BASE_URL=https://api.openai.com/v1 \
N3RVERBERAGE_DEFAULT_MODEL=gpt-4o \
python -c "from rvrb_see.provider import get_provider; p = get_provider(); print(p.base_url, p.model)"
# Output: https://api.openai.com/v1 gpt-4o
```
**Pass**: fallback provider uses configured OpenAI params. **Fail**: uses hardcoded Qwen defaults, or crashes.

### AC-18: No Qwen-specific logic outside _PROVIDER_FALLBACKS
**Verify**:
```bash
grep -r "FreeTierOnly\|AllocationQuota\|x-qwen-quota-remaining" src/rvrb_see/
```
**Pass**: zero matches. **Fail**: any match.

### AC-19: io.py read_media reads image files
**Verify**:
```python
from rvrb_see.io import read_media
from pathlib import Path
# Create a minimal valid PNG
with open("/tmp/test_read.png", "wb") as f:
    f.write(bytes([137, 80, 78, 71, 13, 10, 26, 10]) + b"\x00" * 50)
mi = read_media(Path("/tmp/test_read.png"))
assert mi.path.name == "test_read.png"
assert mi.modality == MediaModality.IMAGE  # from rvrb_see.models import MediaModality
assert "image/png" in str(mi.metadata.get("mime_type", ""))
```
**Pass**: correct modality IMAGE, mime_type in metadata. **Fail**: wrong modality, missing mime_type, or error.

### AC-20: io.py read_media handles JPEG
**Verify**:
```python
mi = read_media(Path("/tmp/test.jpeg"))  # fake jpeg
assert mi.modality == MediaModality.IMAGE
assert "image/jpeg" in str(mi.metadata.get("mime_type", ""))
```
**Pass**: JPEG files detected correctly. **Fail**: wrong mime type or modality.

### AC-21: io.py read_media raises on unsupported format
**Verify**:
```python
import pytest
with pytest.raises(ValueError, match="unsupported|not supported"):
    read_media(Path("/tmp/test.xyz"))
```
**Pass**: `ValueError` raised for unknown extensions. **Fail**: no error, or wrong error type.

### AC-22: io.py read_media raises on missing file
**Verify**:
```python
import pytest
with pytest.raises(FileNotFoundError):
    read_media(Path("/tmp/nonexistent_file.png"))
```
**Pass**: `FileNotFoundError` raised. **Fail**: no error or wrong error.

### AC-23: io.py write_media writes text output
**Verify**:
```python
from rvrb_see.io import write_media
from rvrb_see.models import MediaOutput
import tempfile
with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
    pass
output = MediaOutput(data="test description", format="text")
write_media(output, Path(f.name))
with open(f.name) as fh:
    content = fh.read()
assert content == "test description"
```
**Pass**: file written with correct content. **Fail**: file not written or wrong content.

### AC-24: CLI entry point registered
**Verify**:
```bash
rvrb-see --help
# Must show: IMAGE_PATH argument, --prompt, --json, --model, --provider, --output flags
```
**Pass**: all flags present with correct types. **Fail**: any flag missing.

### AC-25: CLI writes to stdout by default
**Verify**:
```bash
rvrb-see /tmp/test_image.png 2>/dev/null
# Output goes to stdout, not stderr
```
**Pass**: output on stdout. **Fail**: output on stderr, or no output.

### AC-26: --json flag produces JSON output
**Verify**:
```bash
rvrb-see /tmp/test_image.png --json 2>/dev/null | python -c "
import sys, json
d = json.load(sys.stdin)
assert 'description' in d and 'model' in d and 'provider' in d
"
```
**Pass**: valid JSON with SeeResult schema. **Fail**: not valid JSON, missing fields.

### AC-27: --model flag overrides provider model
**Verify**:
```bash
rvrb-see /tmp/test_image.png --model gpt-4o --json 2>/dev/null | python -c "
import sys, json; assert json.load(sys.stdin)['model'] == 'gpt-4o'
"
```
**Pass**: model in JSON matches `--model` flag. **Fail**: flag ignored.

### AC-28: --provider flag overrides env var
**Verify**:
```bash
N3RVERBERAGE_PROVIDER=qwen rvrb-see /tmp/test_image.png --provider openai --json 2>/dev/null | python -c "
import sys, json; assert json.load(sys.stdin)['provider'] == 'openai'
"
```
**Pass**: provider field is `"openai"`, overriding env var. **Fail**: env var takes precedence.

### AC-29: --output flag writes to file
**Verify**:
```bash
rvrb-see /tmp/test_image.png --output /tmp/test_see_output.txt
test -f /tmp/test_see_output.txt && cat /tmp/test_see_output.txt
# Output contains image description
```
**Pass**: file created with description text, nothing on stdout. **Fail**: file not created, or output on stdout.

### AC-30: --prompt flag provides custom instruction
**Verify**:
```bash
rvrb-see /tmp/test_image.png --prompt "What color is the sky?" --json 2>/dev/null | python -c "
import sys, json; assert json.load(sys.stdin).get('prompt', '') == 'What color is the sky?'
"
```
**Pass**: prompt stored in JSON output. **Fail**: prompt not captured or ignored.

### AC-31: Exit code 0 on success
**Verify**:
```bash
rvrb-see /tmp/test_image.png > /dev/null 2>&1; echo $?
```
**Pass**: 0. **Fail**: non-zero.

### AC-32: Exit code 1 on provider failure
**Verify**:
```bash
OPENAI_API_KEY=invalid rvrb-see /tmp/test_image.png 2>/dev/null; echo $?
```
**Pass**: exit 1, error message on stderr. **Fail**: exit 0, or crash/stack trace.

### AC-33: Exit code 1 with missing image
**Verify**:
```bash
rvrb-see /tmp/nonexistent.png 2>/dev/null; echo $?
```
**Pass**: exit 1, error on stderr about missing file. **Fail**: exit 0 or crash.

### AC-34: MCP entry point registered
**Verify**:
```bash
python -c "from rvrb_see.mcp import mcp, main; print(type(mcp).__name__)"
# Output: FastMCP
```
**Pass**: `mcp` is `FastMCP`, `main` exists. **Fail**: ImportError or wrong type.

### AC-35: MCP tool registered
**Verify**: `mcp` has a tool named `see` accepting `image_path: str, prompt: str = ""` → `dict`.
**Pass**: tool registered with correct signature. **Fail**: no see tool, wrong params.

### AC-36: MCP gated import
**Verify**:
```bash
pip uninstall mcp -y 2>/dev/null
python -c "from rvrb_see.mcp import main" 2>&1
# Output must mention pip install rvrb-see[mcp]
```
**Pass**: helpful ImportError with pip install guidance. **Fail**: raw ImportError, or module imports without mcp.

### AC-37: MockProvider in test suite
**Verify**:
```bash
grep -A 20 "class MockProvider" tests/conftest.py
```
Must contain: `model: str`, `base_url: str`, `complete()`, `complete_structured()`, `complete_with_tools()`. No ABC/Protocol inheritance. No MagicMock.
**Pass**: all 5 members present, structural class. **Fail**: missing method, inherits Protocol/ABC, or uses MagicMock.

### AC-38: MockProvider works without network
**Verify**: Engine test with MockProvider passes with `--offline`. Zero network activity.
**Pass**: test passes, no HTTP calls. **Fail**: test fails or attempts HTTP.

### AC-39: CLI tests use CliRunner
**Verify**: `tests/test_cli.py` uses `typer.testing.CliRunner`, not `subprocess.run`.
**Pass**: CliRunner used. **Fail**: real subprocess calls.

### AC-40: I/O tests use tmp_path fixture
**Verify**: `tests/test_io.py` uses pytest `tmp_path` fixture, not hardcoded paths.
**Pass**: `tmp_path` used. **Fail**: hardcoded paths.

### AC-41: All tests pass with --offline
**Verify**:
```bash
pytest --offline
```
**Pass**: 100% pass, zero network activity. **Fail**: any test failure or network call.

### AC-42: pyproject.toml configured correctly
**Verify**:
```python
import tomllib
with open('pyproject.toml', 'rb') as f: cfg = tomllib.load(f)
assert cfg['build-system']['build-backend'] == 'hatchling'
assert cfg['project']['name'] == 'rvrb-see'
assert cfg['project']['requires-python'] == '>=3.11'
assert cfg['project']['license'] == 'Apache-2.0'
scripts = cfg['project']['scripts']
assert 'rvrb-see' in scripts
assert 'rvrb-see-mcp' in scripts
```
**Pass**: all assertions pass. **Fail**: any assertion fails.

### AC-43: MCP extra dependency declared
**Verify**:
```python
assert 'mcp' in cfg['project'].get('optional-dependencies', {})
```
**Pass**: `mcp` extra with `["mcp>=1.0.0"]` value. **Fail**: missing optional-dependencies or mcp key.

### AC-44: No n3rverberage in hard dependencies
**Verify**:
```python
deps = cfg['project'].get('dependencies', [])
for dep in deps:
    assert 'n3rverberage' not in dep.lower(), f'n3rverberage found in hard dep: {dep}'
```
**Pass**: no n3rverberage in dependencies. **Fail**: n3rverberage listed as hard dep.

### AC-45: Linting passes
**Verify**:
```bash
ruff check src/rvrb_see/ tests/
```
**Pass**: zero errors. **Fail**: any linting violation.

### AC-46: Type checking passes
**Verify**:
```bash
mypy src/rvrb_see/
```
**Pass**: zero errors. **Fail**: any type error.

### AC-47: SeeResult contains prompt field
**Verify**:
```python
from rvrb_see.models import SeeResult
result = SeeResult(description="test", model="m", provider="p", prompt="What is this?")
assert result.prompt == "What is this?"
assert result.prompt is not None
```
**Pass**: `prompt: str = ""` field exists with default empty string. **Fail**: missing field.

### AC-48: Default prompt is empty string
**Verify**:
```python
result = SeeResult(description="test", model="m", provider="p")
assert result.prompt == ""
```
**Pass**: default value is `""`. **Fail**: default is `None` or any other value.

## 4. Constraints

1. **Protocol v2 compliance**: Must follow every mandatory requirement in `docs/satellite-protocol-v2.md`. Kernel modules must be present and correctly named. `ModelProvider` must be a structural Protocol. `get_provider()` must use the n3rverberage-first fallback pattern.

2. **Provider-agnostic**: Must comply with all relevant acceptance criteria from `docs/spec-provider-agnostic-refactor.md` (ACs 1–20). No hardcoded Qwen model IDs outside `_PROVIDER_FALLBACKS` map. Default model resolved from `N3RVERBERAGE_DEFAULT_MODEL` env var.

3. **Single method engine**: `SeeEngine` must have exactly one public action method: `see(image: MediaInput | str, prompt: str | None = None) -> SeeResult`. No mode dispatcher, no strategy pattern.

4. **No side effects**: Engine must not write files, print to stdout/stderr, or modify module-level state. I/O happens in `io.py` and `cli.py` only.

5. **No n3rverberage hard dependency**: `pyproject.toml` `dependencies` must not list `n3rverberage`. The provider resolution uses `try/except ImportError` at call time.

6. **Temperature 0**: The engine must set `temperature=0` on the LLM call for deterministic output.

7. **Image encoding**: Images must be base64-encoded as data URIs in the format `data:{mime_type};base64,{base64_data}` for the multimodal API.

8. **Python >=3.11**: Minimum Python version constraint. Use `StrEnum` from stdlib `enum` (available since 3.11), not `str, Enum` workaround.

9. **Apache-2.0 license**: As per satellite protocol.

10. **Hatchling build backend**: As per satellite protocol. Python package build must use hatchling.

## 5. Out of Scope

| Item | Reason |
|------|--------|
| Video input | Different modality handling. Future `rvrb-watch` satellite. |
| Image generation/editing | Text-to-image is a different satellite. |
| Object detection / bounding boxes | Natural language covers. Structured extraction is `extract`. |
| OCR-specific mode | Model handles OCR inline via prompt. |
| Image preprocessing | User's responsibility. Satellite takes the image as-is. |
| Batch/directory processing | Single image per call. Compose externally. |
| Streaming | Synchronous response. No demand. |

## 6. Traceability Matrix

| AC | Title | Property Tested |
|:--:|-------|----------------|
| AC-1 | Kernel modules present | Structure |
| AC-2 | io.py present | Structure |
| AC-3 | __init__.py exports | Structure |
| AC-4 | Constructor injection | Engine |
| AC-5 | Single public method | Engine |
| AC-6 | Base64 image encoding | Engine |
| AC-7 | MediaInput accepted | Engine |
| AC-8 | Temperature 0 | Engine |
| AC-9 | No side effects | Engine |
| AC-10 | MediaModality enum | Models |
| AC-11 | MediaInput model | Models |
| AC-12 | MediaOutput model | Models |
| AC-13 | SeeResult model | Models |
| AC-14 | ModelProvider Protocol | Provider |
| AC-15 | Default model qwen3.7-plus | Provider |
| AC-16 | Env-var-driven defaults | Provider |
| AC-17 | get_provider() fallback | Provider |
| AC-18 | No Qwen hardcoding | Provider |
| AC-19 | read_media PNG | I/O |
| AC-20 | read_media JPEG | I/O |
| AC-21 | read_media unsupported | I/O |
| AC-22 | read_media missing file | I/O |
| AC-23 | write_media text | I/O |
| AC-24 | CLI entry point | CLI |
| AC-25 | stdout output | CLI |
| AC-26 | --json flag | CLI |
| AC-27 | --model flag | CLI |
| AC-28 | --provider flag | CLI |
| AC-29 | --output flag | CLI |
| AC-30 | --prompt flag | CLI |
| AC-31 | Exit 0 success | CLI |
| AC-32 | Exit 1 failure | CLI |
| AC-33 | Exit 1 missing file | CLI |
| AC-34 | MCP entry point | MCP |
| AC-35 | MCP tool registered | MCP |
| AC-36 | MCP gated import | MCP |
| AC-37 | MockProvider in tests | Testing |
| AC-38 | MockProvider no network | Testing |
| AC-39 | CliRunner for CLI tests | Testing |
| AC-40 | tmp_path for I/O tests | Testing |
| AC-41 | All tests offline | Testing |
| AC-42 | pyproject.toml config | Build |
| AC-43 | MCP extra dependency | Build |
| AC-44 | No n3rverberage hard dep | Build |
| AC-45 | Linting passes | Quality |
| AC-46 | Type checking passes | Quality |
| AC-47 | SeeResult prompt field | Models |
| AC-48 | Default prompt empty | Models |

**Total**: 48 acceptance criteria across 9 categories.
