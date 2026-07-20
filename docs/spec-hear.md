# SDD Spec: hear

**Change ID**: `hear` | **Phase**: 3 — Spec | **Date**: 2026-07-19

---

## 1. Goals

1. **Create `rvrb-hear` satellite**: A new pip-installable Python package (`rvrb-hear`, importable as `rvrb_hear`) in the reverberage ecosystem that performs audio comprehension using qwen3.5-omni-plus. Built with hatchling, Python >=3.11, Apache-2.0.

2. **Single-method audio comprehension engine**: `HearEngine(provider).hear(audio: MediaInput | str, prompt: str | None = None) -> HearResult`. One public method. The engine encodes audio as base64, constructs a multimodal message with `input_audio` content blocks, passes `stream=True` and `modalities=["text"]` to `provider.complete()`, and returns structured text output. The streaming is handled internally by the provider's `complete()` method — the Protocol returns a synchronous `str`.

3. **Mandatory kernel compliance**: Every module required by protocol v2 is present: `__init__.py` (package metadata, public API re-exports), `models.py` (domain types + `MediaModality` + `MediaInput` + `MediaOutput` + `HearResult`), `provider.py` (`ModelProvider` Protocol + `DEFAULT_MODEL` + `DEFAULT_BASE_URL` + `get_provider()` factory), `engine.py` (`HearEngine` with constructor-injected provider).

4. **io.py for audio I/O**: Since `hear` handles AUDIO modality, `io.py` is REQUIRED with `read_media(path) -> MediaInput` and `write_media(output, path) -> None`. `read_media()` detects audio format from file extension. Supported formats: wav, mp3, aac, flac, m4a, ogg, amr. `write_media()` writes text output.

5. **Optional CLI**: Typer-based CLI at `rvrb-hear <audio_path>` with `--json`, `--model`, `--provider`, `--output`, `--prompt` flags. Exit codes: 0 success, 1 failure.

6. **Optional MCP server**: `rvrb-hear-mcp` entry point exposing the hear functionality as an MCP tool via `mcp.server.FastMCP`. Gated import — MCP is optional.

7. **Protocol v2 provider contract**: Provider resolution follows standard satellite pattern: try `n3rverberage.providers.get_provider()` first, fall back to `_GenericProvider` (OpenAI-compatible client with env-var-driven defaults). No Qwen-specific logic outside `_PROVIDER_FALLBACKS` map. `--provider` CLI flag overrides `N3RVERBERAGE_PROVIDER`.

8. **Proper provider field in HearResult**: Unlike rvrb-see which leaks `_api_key` into the provider field, rvrb-hear must populate the provider field with the resolved provider name string (e.g., `"qwen"`, `"openai"`, `"local"`). Never expose API keys in output.

9. **Mock-ready testing**: Test suite includes a standalone `MockProvider` implementing `ModelProvider` by structure (no inheritance, no `MagicMock`). Engine tests pass with zero network calls. CLI tests use `typer.testing.CliRunner`. I/O tests use `tmp_path` fixture. All tests pass with `--offline`.

## 2. Non-Goals

| Item | Reason |
|------|--------|
| Video input support | YAGNI. Video→audio→text is a composed pipeline. Future `rvrb-watch` satellite. |
| ASR transcription-only output | `rvrb-transcriber` already covers ASR. Hear is comprehension (speaker intent, emotion, scene context, QA about audio), not just word-for-word transcription. |
| Streaming output to user | The engine handles streaming via SSE internally in the provider, but exposes synchronous `str` return. No user-visible streaming interface. |
| Batch/directory processing | Single audio file per invocation. Compose with `xargs` or external tooling. |
| Multiple audio inputs per call | Add when pipeline use case emerges. Single audio per call for now. |
| TTS output (text-to-speech) | Different modality (TEXT→AUDIO). Future `rvrb-speak` satellite. `modalities=["text"]` explicitly suppresses audio output. |
| Real-time/WebSocket audio | Synchronous single response. Real-time requires WebSocket infrastructure (future). |
| Audio preprocessing (resample, trim, normalize) | CLI-only satellite. Preprocessing is the user's job. |
| Local audio model fallback | qwen3.5-omni-plus is audio-capable. No local audio comprehension model for fallback. |
| Speaker diarization / voice separation | Model handles this inline via natural language understanding. |
| Music analysis / chord detection | Natural language comprehension covers music description. |

## 3. Acceptance Criteria

Every criterion is binary testable (pass/fail). Test command shown is the verification method.

### AC-1: Mandatory kernel modules present
**Verify**:
```bash
ls src/rvrb_hear/__init__.py src/rvrb_hear/models.py \
   src/rvrb_hear/provider.py src/rvrb_hear/engine.py
```
**Pass**: all four files exist with non-zero size. **Fail**: any file missing or empty.

### AC-2: io.py present (AUDIO modality)
**Verify**:
```bash
test -f src/rvrb_hear/io.py
```
**Pass**: file exists. **Fail**: file missing.

### AC-3: __init__.py exports public API
**Verify**:
```python
from rvrb_hear import HearEngine, HearResult, MediaModality, MediaInput, MediaOutput
from rvrb_hear.provider import ModelProvider, get_provider, DEFAULT_MODEL, DEFAULT_BASE_URL
from rvrb_hear.io import read_media, write_media
```
**Pass**: all 10 symbols importable. **Fail**: any symbol fails to import.

### AC-4: HearEngine constructor injection
**Verify**:
```python
from rvrb_hear.engine import HearEngine

class DummyProvider:
    model = "test"
    base_url = "http://test"
    def complete(self, messages, **kwargs): return "ok"
    def complete_structured(self, messages, output_type, **kwargs): return output_type()
    def complete_with_tools(self, messages, tools, **kwargs): return None

engine = HearEngine(provider=DummyProvider())
# Must succeed — no TypeError, no AttributeError
```
**Pass**: construction succeeds with a structurally-compatible provider. **Fail**: `TypeError`, `AttributeError`, or any exception.

### AC-5: Single public method — hear
**Verify**:
```python
engine = HearEngine(provider=DummyProvider())
result = engine.hear("What is being said in this audio?")
assert isinstance(result.analysis, str)
# dir(engine) must NOT contain other action methods besides 'hear' and 'provider'
```
**Pass**: single method call returns `HearResult`. No other public action methods exist. **Fail**: multiple action methods, wrong return type, or method missing.

### AC-6: Engine encodes audio as base64 with input_audio content type
**Verify**: Use SpyProvider in tests that captures messages:
```python
class SpyProvider:
    model = "spy"; base_url = "spy://"
    def __init__(self): self.captured_messages = None; self.captured_kwargs = {}
    def complete(self, messages, **kwargs):
        self.captured_messages = messages; self.captured_kwargs = kwargs; return "result"
    def complete_structured(self, messages, output_type, **kwargs): return output_type()
    def complete_with_tools(self, messages, tools, **kwargs): return None

spy = SpyProvider()
engine = HearEngine(provider=spy)
engine.hear("/tmp/test_audio.wav")
# spy.captured_messages must contain a user message with content that is a list
# containing an entry with type: "input_audio"
# and input_audio["data"] must be a base64 string
# and input_audio["format"] must be "wav"
```
**Pass**: audio is sent as `input_audio` content block with base64 data and correct format field. **Fail**: missing `input_audio` block, wrong content type, or raw bytes in message.

### AC-7: Engine accepts MediaInput
**Verify**:
```python
from rvrb_hear.models import MediaInput, MediaModality
spy = SpyProvider()
engine = HearEngine(provider=spy)
mi = MediaInput(path=Path("/tmp/test_audio.wav"), modality=MediaModality.AUDIO)
engine.hear(mi)
# Must succeed — same as passing string path
```
**Pass**: `MediaInput` accepted as `hear()` parameter. **Fail**: TypeError or wrong type handling.

### AC-8: Temperature 0
**Verify**: Same SpyProvider — capture kwargs:
```python
# spy.captured_kwargs["temperature"] must be 0 (or 0.0)
```
**Pass**: `complete()` called with `temperature=0` or `0.0`. **Fail**: temperature not set, or set to non-zero.

### AC-9: No side effects in engine
**Verify**:
```python
# Engine must not call print(), open(), write(), or modify any global/module state
# Install a mock that raises on any I/O attempt
# engine.hear() must complete without triggering the mock
```
**Pass**: `hear()` does not write files, print to stdout, or modify global state. **Fail**: any I/O or global mutation.

### AC-10: MediaModality enum present
**Verify**:
```python
from rvrb_hear.models import MediaModality
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
from rvrb_hear.models import MediaInput, MediaModality
from pathlib import Path
mi = MediaInput(path=Path("/tmp/test.wav"), modality=MediaModality.AUDIO)
assert mi.path == Path("/tmp/test.wav")
assert mi.modality == MediaModality.AUDIO
assert mi.metadata == {}
```
**Pass**: fields `path` (Path), `modality` (MediaModality), `metadata` (dict, default `{}`). **Fail**: wrong types or defaults.

### AC-12: MediaOutput model
**Verify**:
```python
from rvrb_hear.models import MediaOutput, MediaModality
mo = MediaOutput(data="audio comprehension result")
assert mo.data == "audio comprehension result"
assert mo.modality == MediaModality.TEXT
assert mo.format == "text"
```
**Pass**: `data` (str|bytes), `modality` (default TEXT), `format` (default "text"). **Fail**: wrong types or defaults.

### AC-13: HearResult model
**Verify**:
```python
from rvrb_hear.models import HearResult
result = HearResult(
    analysis="The speaker is explaining quantum computing concepts.",
    model="qwen3.5-omni-plus",
    provider="qwen",
    prompt="What is this audio about?",
    tokens_used=250
)
assert result.analysis == "The speaker is explaining quantum computing concepts."
assert result.tokens_used == 250
assert result.provider == "qwen"
```
**Pass**: fields: `analysis: str`, `model: str`, `provider: str`, `prompt: str = ""`, `tokens_used: int | None = None`. Provider field is a name string, not an API key. **Fail**: missing fields, wrong types, or provider field contains an API key format.

### AC-14: ModelProvider Protocol present
**Verify**:
```python
from rvrb_hear.provider import ModelProvider
import typing
# Must be a Protocol, not an ABC
# Verify model: str, base_url: str, complete(), complete_structured(), complete_with_tools()
```
**Pass**: `ModelProvider` is a `Protocol` with correct attributes and 3 methods. **Fail**: not a Protocol, missing attr/methods, inherits from ABC.

### AC-15: DEFAULT_MODEL is qwen3.5-omni-plus (audio comprehension model)
**Verify**:
```bash
unset N3RVERBERAGE_DEFAULT_MODEL
python -c "from rvrb_hear.provider import DEFAULT_MODEL; print(DEFAULT_MODEL)"
# Output: qwen3.5-omni-plus
```
**Pass**: default model is `qwen3.5-omni-plus`, not `qwen3-coder-plus` or `qwen3.7-plus`. **Fail**: wrong default.

### AC-16: DEFAULT_MODEL and DEFAULT_BASE_URL env-var-driven
**Verify**:
```bash
N3RVERBERAGE_DEFAULT_MODEL=gpt-4o \
N3RVERBERAGE_DEFAULT_BASE_URL=https://api.openai.com/v1 \
python -c "from rvrb_hear.provider import DEFAULT_MODEL, DEFAULT_BASE_URL; print(DEFAULT_MODEL); print(DEFAULT_BASE_URL)"
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
python -c "from rvrb_hear.provider import get_provider; p = get_provider(); print(p.base_url, p.model)"
# Output: https://api.openai.com/v1 gpt-4o
```
**Pass**: fallback provider uses configured OpenAI params. **Fail**: uses hardcoded Qwen defaults, or crashes.

### AC-18: No Qwen-specific logic outside _PROVIDER_FALLBACKS
**Verify**:
```bash
grep -r "FreeTierOnly\|AllocationQuota\|x-qwen-quota-remaining" src/rvrb_hear/
```
**Pass**: zero matches. **Fail**: any match.

### AC-19: io.py read_media reads audio files (wav)
**Verify**:
```python
from rvrb_hear.io import read_media
from rvrb_hear.models import MediaModality
from pathlib import Path
# Create a minimal fake wav file
with open("/tmp/test_hear.wav", "wb") as f:
    f.write(b'RIFF' + b'\x00' * 50)
mi = read_media(Path("/tmp/test_hear.wav"))
assert mi.path.name == "test_hear.wav"
assert mi.modality == MediaModality.AUDIO
assert "audio/wav" in str(mi.metadata.get("mime_type", ""))
```
**Pass**: correct modality AUDIO, mime_type `audio/wav` in metadata. **Fail**: wrong modality, missing mime_type, or error.

### AC-20: io.py read_media handles mp3
**Verify**:
```python
mi = read_media(Path("/tmp/test_hear.mp3"))  # fake mp3
assert mi.modality == MediaModality.AUDIO
assert "audio/mpeg" in str(mi.metadata.get("mime_type", ""))
```
**Pass**: MP3 files detected correctly with `audio/mpeg`. **Fail**: wrong mime type or modality.

### AC-21: io.py read_media supports all required formats
**Verify**:
```python
from rvrb_hear.io import MIME_MAP
required = {".wav", ".mp3", ".aac", ".flac", ".m4a", ".ogg", ".amr"}
assert set(MIME_MAP.keys()) == required
```
**Pass**: exactly 7 format entries matching the required list. **Fail**: missing format or wrong key set.

### AC-22: io.py read_media raises on unsupported format
**Verify**:
```python
import pytest
with pytest.raises(ValueError, match="unsupported|not supported"):
    read_media(Path("/tmp/test.xyz"))
```
**Pass**: `ValueError` raised for unknown extensions. **Fail**: no error, or wrong error type.

### AC-23: io.py read_media raises on missing file
**Verify**:
```python
import pytest
with pytest.raises(FileNotFoundError):
    read_media(Path("/tmp/nonexistent_audio.wav"))
```
**Pass**: `FileNotFoundError` raised. **Fail**: no error or wrong error.

### AC-24: io.py write_media writes text output
**Verify**:
```python
from rvrb_hear.io import write_media
from rvrb_hear.models import MediaOutput
import tempfile
with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
    pass
output = MediaOutput(data="audio comprehension result", format="text")
write_media(output, Path(f.name))
with open(f.name) as fh:
    content = fh.read()
assert content == "audio comprehension result"
```
**Pass**: file written with correct content. **Fail**: file not written or wrong content.

### AC-25: CLI entry point registered
**Verify**:
```bash
rvrb-hear --help
# Must show: AUDIO_PATH argument, --prompt, --json, --model, --provider, --output flags
```
**Pass**: all flags present with correct types. **Fail**: any flag missing.

### AC-26: CLI writes to stdout by default
**Verify**:
```bash
rvrb-hear /tmp/test_audio.wav 2>/dev/null
# Output goes to stdout, not stderr
```
**Pass**: output on stdout. **Fail**: output on stderr, or no output.

### AC-27: --json flag produces JSON output
**Verify**:
```bash
rvrb-hear /tmp/test_audio.wav --json 2>/dev/null | python -c "
import sys, json
d = json.load(sys.stdin)
assert 'analysis' in d and 'model' in d and 'provider' in d
"
```
**Pass**: valid JSON with HearResult schema. **Fail**: not valid JSON, missing fields.

### AC-28: --model flag overrides provider model
**Verify**:
```bash
rvrb-hear /tmp/test_audio.wav --model gpt-4o --json 2>/dev/null | python -c "
import sys, json; assert json.load(sys.stdin)['model'] == 'gpt-4o'
"
```
**Pass**: model in JSON matches `--model` flag. **Fail**: flag ignored.

### AC-29: --provider flag overrides env var
**Verify**:
```bash
N3RVERBERAGE_PROVIDER=qwen rvrb-hear /tmp/test_audio.wav --provider openai --json 2>/dev/null | python -c "
import sys, json; assert json.load(sys.stdin)['provider'] == 'openai'
"
```
**Pass**: provider field is `"openai"`, overriding env var. **Fail**: env var takes precedence.

### AC-30: --output flag writes to file
**Verify**:
```bash
rvrb-hear /tmp/test_audio.wav --output /tmp/test_hear_output.txt
test -f /tmp/test_hear_output.txt && cat /tmp/test_hear_output.txt
# Output contains audio analysis
```
**Pass**: file created with analysis text, nothing on stdout. **Fail**: file not created, or output on stdout.

### AC-31: --prompt flag provides custom instruction
**Verify**:
```bash
rvrb-hear /tmp/test_audio.wav --prompt "What is the speaker's emotional tone?" --json 2>/dev/null | python -c "
import sys, json; assert json.load(sys.stdin).get('prompt', '') == 'What is the speaker's emotional tone?'
"
```
**Pass**: prompt stored in JSON output. **Fail**: prompt not captured or ignored.

### AC-32: Exit code 0 on success
**Verify**:
```bash
rvrb-hear /tmp/test_audio.wav > /dev/null 2>&1; echo $?
```
**Pass**: 0. **Fail**: non-zero.

### AC-33: Exit code 1 on provider failure
**Verify**:
```bash
OPENAI_API_KEY=invalid rvrb-hear /tmp/test_audio.wav 2>/dev/null; echo $?
```
**Pass**: exit 1, error message on stderr. **Fail**: exit 0, or crash/stack trace.

### AC-34: Exit code 1 with missing audio file
**Verify**:
```bash
rvrb-hear /tmp/nonexistent.wav 2>/dev/null; echo $?
```
**Pass**: exit 1, error on stderr about missing file. **Fail**: exit 0 or crash.

### AC-35: MCP entry point registered
**Verify**:
```bash
python -c "from rvrb_hear.mcp import mcp, main; print(type(mcp).__name__)"
# Output: FastMCP
```
**Pass**: `mcp` is `FastMCP`, `main` exists. **Fail**: ImportError or wrong type.

### AC-36: MCP tool registered
**Verify**: `mcp` has a tool named `hear` accepting `audio_path: str, prompt: str = ""` → `dict`.
**Pass**: tool registered with correct signature. **Fail**: no hear tool, wrong params.

### AC-37: MCP gated import
**Verify**:
```bash
pip uninstall mcp -y 2>/dev/null
python -c "from rvrb_hear.mcp import main" 2>&1
# Output must mention pip install rvrb-hear[mcp]
```
**Pass**: helpful ImportError with pip install guidance. **Fail**: raw ImportError, or module imports without mcp.

### AC-38: MockProvider in test suite
**Verify**:
```bash
grep -A 20 "class MockProvider" tests/conftest.py
```
Must contain: `model: str`, `base_url: str`, `complete()`, `complete_structured()`, `complete_with_tools()`. No ABC/Protocol inheritance. No MagicMock.
**Pass**: all 5 members present, structural class. **Fail**: missing method, inherits Protocol/ABC, or uses MagicMock.

### AC-39: MockProvider works without network
**Verify**: Engine test with MockProvider passes with `--offline`. Zero network activity.
**Pass**: test passes, no HTTP calls. **Fail**: test fails or attempts HTTP.

### AC-40: CLI tests use CliRunner
**Verify**: `tests/test_cli.py` uses `typer.testing.CliRunner`, not `subprocess.run`.
**Pass**: CliRunner used. **Fail**: real subprocess calls.

### AC-41: I/O tests use tmp_path fixture
**Verify**: `tests/test_io.py` uses pytest `tmp_path` fixture, not hardcoded paths.
**Pass**: `tmp_path` used. **Fail**: hardcoded paths.

### AC-42: All tests pass with --offline
**Verify**:
```bash
pytest --offline
```
**Pass**: 100% pass, zero network activity. **Fail**: any test failure or network call.

### AC-43: pyproject.toml configured correctly
**Verify**:
```python
import tomllib
with open('pyproject.toml', 'rb') as f: cfg = tomllib.load(f)
assert cfg['build-system']['build-backend'] == 'hatchling'
assert cfg['project']['name'] == 'rvrb-hear'
assert cfg['project']['requires-python'] == '>=3.11'
assert cfg['project']['license'] == 'Apache-2.0'
scripts = cfg['project']['scripts']
assert 'rvrb-hear' in scripts
assert 'rvrb-hear-mcp' in scripts
```
**Pass**: all assertions pass. **Fail**: any assertion fails.

### AC-44: MCP extra dependency declared
**Verify**:
```python
assert 'mcp' in cfg['project'].get('optional-dependencies', {})
```
**Pass**: `mcp` extra with `["mcp>=1.0.0"]` value. **Fail**: missing optional-dependencies or mcp key.

### AC-45: No n3rverberage in hard dependencies
**Verify**:
```python
deps = cfg['project'].get('dependencies', [])
for dep in deps:
    assert 'n3rverberage' not in dep.lower(), f'n3rverberage found in hard dep: {dep}'
```
**Pass**: no n3rverberage in dependencies. **Fail**: n3rverberage listed as hard dep.

### AC-46: Linting passes
**Verify**:
```bash
ruff check src/rvrb_hear/ tests/
```
**Pass**: zero errors. **Fail**: any linting violation.

### AC-47: Type checking passes
**Verify**:
```bash
mypy src/rvrb_hear/
```
**Pass**: zero errors. **Fail**: any type error.

### AC-48: HearResult contains prompt field
**Verify**:
```python
from rvrb_hear.models import HearResult
result = HearResult(analysis="test", model="m", provider="p", prompt="What is this?")
assert result.prompt == "What is this?"
assert result.prompt is not None
```
**Pass**: `prompt: str = ""` field exists with default empty string. **Fail**: missing field.

### AC-49: Default prompt is empty string
**Verify**:
```python
result = HearResult(analysis="test", model="m", provider="p")
assert result.prompt == ""
```
**Pass**: default value is `""`. **Fail**: default is `None` or any other value.

### AC-50: stream=True passed to provider.complete()
**Verify**: SpyProvider captures kwargs:
```python
spy = SpyProvider()
engine = HearEngine(provider=spy)
engine.hear("/tmp/test_audio.wav")
# assert spy.captured_kwargs.get("stream") is True
```
**Pass**: `complete()` called with `stream=True`. **Fail**: stream not set, or set to False.

### AC-51: modalities=["text"] set in kwargs
**Verify**: SpyProvider captures kwargs:
```python
spy = SpyProvider()
engine = HearEngine(provider=spy)
engine.hear("/tmp/test_audio.wav")
# assert spy.captured_kwargs.get("modalities") == ["text"]
```
**Pass**: `complete()` called with `modalities=["text"]` to suppress TTS audio output. **Fail**: modalities not set, set to wrong value, or includes "audio".

### AC-52: HearResult provider field is proper name, not API key
**Verify**:
```python
from rvrb_hear.models import HearResult
result = HearResult(analysis="test", model="qwen3.5-omni-plus", provider="qwen")
# provider must be "qwen" (provider name), not "sk-..." (API key)
assert result.provider == "qwen"
assert not result.provider.startswith("sk-")
assert "." not in result.provider  # domain name? wrong.
```
**Pass**: `provider` field contains provider name string. **Fail**: provider contains API key or domain name pattern.

### AC-53: _GenericProvider complete() handles stream=True internally
**Verify**: When `_GenericProvider.complete()` receives `stream=True`, it accumulates SSE chunks and returns the concatenated text synchronously (no generator, no `yield`).
```python
from rvrb_hear.provider import _GenericProvider
import openai
# Mock the OpenAI client to return SSE chunks
# complete() must return str, not a generator
result = provider.complete(messages=[...], stream=True, modalities=["text"])
assert isinstance(result, str)
```
**Pass**: `complete()` returns `str` even when `stream=True` is passed. **Fail**: returns generator, or fails on stream kwarg.

### AC-54: Engine builds audio message with correct structure
**Verify**: SpyProvider captures the message list. The user message content must be a list containing exactly:
- An `input_audio` block with `data` (base64 string) and `format` (audio format string)
- A `text` block with the prompt
```python
spy = SpyProvider()
engine = HearEngine(provider=spy)
engine.hear("/tmp/test_audio.wav", "Summarize this audio")
messages = spy.captured_messages
# messages[0]["role"] == "system"
# messages[1]["role"] == "user"
# content = messages[1]["content"] (must be a list)
# content[0]["type"] == "input_audio"
# content[0]["input_audio"]["data"] is a base64 string
# content[0]["input_audio"]["format"] == "wav"
# content[1]["type"] == "text"
# content[1]["text"] == "Summarize this audio"
```
**Pass**: correct multimodal audio message structure with `input_audio` and `text` blocks. **Fail**: missing blocks, wrong order, or incorrect content type.

## 4. Constraints

1. **Protocol v2 compliance**: Must follow every mandatory requirement in `docs/satellite-protocol-v2.md`. Kernel modules must be present and correctly named. `ModelProvider` must be a structural Protocol. `get_provider()` must use the n3rverberage-first fallback pattern.

2. **Provider-agnostic**: Must comply with all relevant acceptance criteria from `docs/spec-provider-agnostic-refactor.md` (ACs 1–20). No hardcoded Qwen model IDs outside `_PROVIDER_FALLBACKS` map. Default model resolved from `N3RVERBERAGE_DEFAULT_MODEL` env var.

3. **Single method engine**: `HearEngine` must have exactly one public action method: `hear(audio: MediaInput | str, prompt: str | None = None) -> HearResult`. No mode dispatcher, no strategy pattern.

4. **No side effects**: Engine must not write files, print to stdout/stderr, or modify module-level state. I/O happens in `io.py` and `cli.py` only.

5. **No n3rverberage hard dependency**: `pyproject.toml` `dependencies` must not list `n3rverberage`. The provider resolution uses `try/except ImportError` at call time.

6. **Temperature 0**: The engine must set `temperature=0` on the LLM call for deterministic output.

7. **Audio encoding**: Audio must be base64-encoded as a string (not data URI — the `input_audio` content block uses separate `data` and `format` fields). The base64 data is placed in the `input_audio.data` field, and the audio format (e.g., `"wav"`) is placed in `input_audio.format`.

8. **Stream handling**: The `_GenericProvider.complete()` method must handle `stream=True` internally by accumulating SSE chunks from the OpenAI-compatible API and returning the concatenated text as a synchronous `str`. The `ModelProvider.complete()` Protocol signature is unchanged — it returns `str`. No generator/yield in the Protocol.

9. **modalities=["text"] constraint**: The engine must always pass `modalities=["text"]` in the completion call. This prevents the omni model from generating TTS audio output in parallel with the text response, which would waste tokens and bandwidth.

10. **Provider field must not leak credentials**: The `HearResult.provider` field must contain the provider name string (e.g., `"qwen"`, `"openai"`, `"local"`), not any API key, base URL, or domain. This is a bug in rvrb-see that must not be replicated.

11. **Python >=3.11**: Minimum Python version constraint. Use `StrEnum` from stdlib `enum` (available since 3.11), not `str, Enum` workaround.

12. **Apache-2.0 license**: As per satellite protocol.

13. **Hatchling build backend**: As per satellite protocol. Python package build must use hatchling.

## 5. Out of Scope

| Item | Reason |
|------|--------|
| Video input | Different modality. Future `rvrb-watch` satellite. |
| ASR/transcription-only mode | `rvrb-transcriber` covers speech-to-text. Hear is comprehension, not transcription. |
| Streaming output to user | Synchronous `str` response. Streaming is internal to the provider. |
| TTS audio output | `modalities=["text"]` suppresses it. `rvrb-speak` handles TEXT→AUDIO. |
| Real-time/WebSocket audio | Synchronous batch API. Real-time requires WebSocket infrastructure (future). |
| Audio preprocessing (resample, trim) | User's responsibility. Satellite takes audio as-is. |
| Speaker diarization API | Model handles via natural language prompts. |
| Batch/directory processing | Single audio per invocation. Compose externally. |
| Multiple audio inputs per call | Single audio for now. Add when pipeline emerges. |
| Non-omni model fallback (qwen3.7-plus) | omni model is purpose-built for audio. Text-only models can't accept `input_audio` content. |
| Integration tests with real audio | MockProvider for unit tests. Real API tests are infrastructure work (future change). |
| Audio duration limits | Model handles up to its context limit. Satellite imposes no artificial cap. |

## 6. Traceability Matrix

| AC | Title | Property Tested |
|:--:|-------|----------------|
| AC-1 | Kernel modules present | Structure |
| AC-2 | io.py present | Structure |
| AC-3 | __init__.py exports | Structure |
| AC-4 | Constructor injection | Engine |
| AC-5 | Single public method | Engine |
| AC-6 | Base64 audio encoding | Engine |
| AC-7 | MediaInput accepted | Engine |
| AC-8 | Temperature 0 | Engine |
| AC-9 | No side effects | Engine |
| AC-10 | MediaModality enum | Models |
| AC-11 | MediaInput model | Models |
| AC-12 | MediaOutput model | Models |
| AC-13 | HearResult model | Models |
| AC-14 | ModelProvider Protocol | Provider |
| AC-15 | Default model qwen3.5-omni-plus | Provider |
| AC-16 | Env-var-driven defaults | Provider |
| AC-17 | get_provider() fallback | Provider |
| AC-18 | No Qwen hardcoding | Provider |
| AC-19 | read_media WAV | I/O |
| AC-20 | read_media MP3 | I/O |
| AC-21 | All 7 audio formats | I/O |
| AC-22 | read_media unsupported | I/O |
| AC-23 | read_media missing file | I/O |
| AC-24 | write_media text | I/O |
| AC-25 | CLI entry point | CLI |
| AC-26 | stdout output | CLI |
| AC-27 | --json flag | CLI |
| AC-28 | --model flag | CLI |
| AC-29 | --provider flag | CLI |
| AC-30 | --output flag | CLI |
| AC-31 | --prompt flag | CLI |
| AC-32 | Exit 0 success | CLI |
| AC-33 | Exit 1 failure | CLI |
| AC-34 | Exit 1 missing file | CLI |
| AC-35 | MCP entry point | MCP |
| AC-36 | MCP tool registered | MCP |
| AC-37 | MCP gated import | MCP |
| AC-38 | MockProvider in tests | Testing |
| AC-39 | MockProvider no network | Testing |
| AC-40 | CliRunner for CLI tests | Testing |
| AC-41 | tmp_path for I/O tests | Testing |
| AC-42 | All tests offline | Testing |
| AC-43 | pyproject.toml config | Build |
| AC-44 | MCP extra dependency | Build |
| AC-45 | No n3rverberage hard dep | Build |
| AC-46 | Linting passes | Quality |
| AC-47 | Type checking passes | Quality |
| AC-48 | HearResult prompt field | Models |
| AC-49 | Default prompt empty | Models |
| AC-50 | stream=True passed | Engine |
| AC-51 | modalities=["text"] set | Engine |
| AC-52 | Provider field is name, not API key | Models |
| AC-53 | _GenericProvider handles stream internally | Provider |
| AC-54 | Audio message structure | Engine |

**Total**: 54 acceptance criteria across 10 categories.

## 7. Key Differences from rvrb-see

These are the implementation-critical points where hear diverges from the see reference:

| Area | rvrb-see | rvrb-hear |
|------|---------|-----------|
| Default model | `qwen3.7-plus` | `qwen3.5-omni-plus` |
| Content type | `image_url` data URI | `input_audio` with separate `data` + `format` fields |
| Encoding | `data:{mime};base64,{b64}` | Base64 string in `input_audio.data` field |
| Extra kwargs | None | `stream=True`, `modalities=["text"]` |
| Streaming | Not used | Internal SSE accumulation in provider |
| Provider field | LEAKS `_api_key` (bug) | Uses provider name string |
| Supported formats | png, jpg, jpeg, gif, webp | wav, mp3, aac, flac, m4a, ogg, amr |
| System prompt | Image analysis context | Audio comprehension context |
| Result field | `description` | `analysis` |
| Engine method | `see()` | `hear()` |
