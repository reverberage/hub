# SDD Tasks: hear

**Change ID**: `hear` | **Phase**: 5 — Tasks | **Date**: 2026-07-19

---

## Task List

Ordered implementation steps. Each task is atomic and independently testable.

### Task 1: Scaffold the pyproject.toml and package skeleton
- Create `rvrb-hear/` directory in the workspace parent (alongside see)
- Write `pyproject.toml` with hatchling build, entry points (`rvrb-hear`, `rvrb-hear-mcp`), Apache-2.0, Python >=3.11
- Dependencies: `openai>=2.0.0`, `pydantic>=2.0`, `typer>=0.12`
- Optional deps: `mcp=["mcp>=1.0.0"]`, `dev=["pytest>=8.0", "ruff>=0.5", "mypy>=1.10", "mcp>=1.0.0"]`
- Verify: `python -c "import tomllib; d=tomllib.load(open('pyproject.toml','rb')); assert d['project']['scripts']['rvrb-hear']; print('OK')"`
- **Verification**: `python -c "import tomllib; d=tomllib.load(open('pyproject.toml','rb')); assert d['project']['scripts']['rvrb-hear']; print('OK')"`

### Task 2: Create models.py
- Write `rvrb_hear/models.py` with:
  - `MediaModality(StrEnum)` — TEXT, AUDIO, IMAGE, VIDEO
  - `MediaInput(BaseModel)` — path, modality, metadata
  - `MediaOutput(BaseModel)` — data, modality, format
  - `HearResult(BaseModel)` — analysis, model, provider, prompt, tokens_used (NO API key leak)
  - `ToolCall`, `ToolResult`, `ProviderError`, `QuotaExhaustedError`
- **Verification**: `python -c "from rvrb_hear.models import MediaModality, MediaInput, MediaOutput, HearResult; print('OK')"`

### Task 3: Create provider.py
- Write `rvrb_hear/provider.py` with:
  - `ModelProvider(Protocol)` — model, base_url, complete(), complete_structured(), complete_with_tools()
  - `DEFAULT_MODEL` = env `N3RVERBERAGE_DEFAULT_MODEL` or `"qwen3.5-omni-plus"`
  - `DEFAULT_BASE_URL` = env `N3RVERBERAGE_DEFAULT_BASE_URL` or `"https://dashscope-intl.aliyuncs.com/compatible-mode/v1"`
  - `_PROVIDER_FALLBACKS` map: qwen/openai/local (same as see, but with `qwen3.5-omni-plus`)
  - `get_provider()` — try n3rverberage first, fallback to _GenericProvider
  - `_GenericProvider` — OpenAI-compatible with stream handling in complete():
    - Pop `stream` from kwargs, pass to create() with stream=stream
    - If stream=True, accumulate SSE chunks and return concatenated text
    - If stream=False/absent, return single response content
- **Verification**: `python -c "from rvrb_hear.provider import ModelProvider, get_provider, DEFAULT_MODEL; assert DEFAULT_MODEL == 'qwen3.5-omni-plus'; print('OK')"`

### Task 4: Create io.py
- Write `rvrb_hear/io.py` with:
  - `MIME_MAP` dict: .wav, .mp3, .aac, .flac, .m4a, .ogg, .amr
  - `read_media(path) -> MediaInput` — validates path, detects extension, returns AUDIO modality with mime_type AND format in metadata
  - `write_media(output, path) -> None` — writes text/binary output to file
- **Verification**: Create temp WAV/MP3 files, test read/write, test errors for missing/unsupported

### Task 5: Create engine.py
- Write `rvrb_hear/engine.py` with:
  - `HearEngine.__init__(provider)` — stores provider
  - `HearEngine.hear(audio: MediaInput | str, prompt: str | None = None) -> HearResult`
  - Logic: resolve MediaInput → read audio bytes → base64 encode → build multimodal message with `input_audio` content block → call `provider.complete(messages, temperature=0, stream=True, modalities=["text"])` → return HearResult
  - Provider field in HearResult uses provider name, NOT `_api_key` (fix see's bug)
- **Verification**: Unit tests with SpyProvider (captures messages to verify input_audio format) and MockProvider (no network)

### Task 6: Create cli.py
- Write `rvrb_hear/cli.py` with:
  - Typer app: `rvrb-hear <audio_path> [--prompt] [--json] [--model] [--provider] [--output]`
  - Validate audio path exists
  - Resolve provider, create engine, call engine.hear()
  - Output: plain text or JSON, exit 0/1
- **Verification**: `rvrb-hear --help` shows all flags, exit codes correct

### Task 7: Create __init__.py
- Write `rvrb_hear/__init__.py` with:
  - `__version__ = "0.1.0"`
  - Re-export all public API: HearEngine, HearResult, MediaModality, MediaInput, MediaOutput, ModelProvider, get_provider, DEFAULT_MODEL, DEFAULT_BASE_URL
- **Verification**: `python -c "from rvrb_hear import *; print('OK')"`

### Task 8: Create mcp.py
- Write `rvrb_hear/mcp.py` with:
  - Gated import for `mcp` (try/except ImportError with pip install guidance)
  - `mcp = FastMCP("rvrb-hear")` if available
  - tool `hear(audio_path: str, prompt: str = "") -> dict`
  - `main()` entry point
- **Verification**: `python -c "from rvrb_hear.mcp import mcp, main; print(type(mcp).__name__)"` (with mcp installed)

### Task 9: Create test suite
- Write `tests/__init__.py` (empty)
- Write `tests/conftest.py` with `MockProvider` (no inheritance, 5 members: model, base_url, complete, complete_structured, complete_with_tools)
- Write `tests/test_models.py` — MediaModality, MediaInput, MediaOutput, HearResult, ProviderError, pickling
- Write `tests/test_provider.py` — get_provider(), DEFAULT_MODEL, env var resolution
- Write `tests/test_engine.py` — construction, hear() with SpyProvider (input_audio format), temperature 0, stream=True, modalities=["text"], error propagation
- Write `tests/test_cli.py` — help, missing args, --json, --model, --provider flags, exit codes
- Write `tests/test_io.py` — read/write with tmp_path, format detection, errors
- **Verification**: `pytest --offline` passes with 100% pass rate

### Task 10: Final verification
- Run `ruff check src/rvrb_hear/ tests/` — zero errors
- Run `mypy src/rvrb_hear/` — zero errors (with `ignore_missing_imports = true` in pyproject.toml)
- Run `pytest --offline` — 100% pass
- Verify all 54 ACs pass
- **Verification**: All three commands pass

---

## Execution Order

```
Task 1 (pyproject.toml + dirs) → Task 2 (models) → Task 3 (provider) → Task 4 (io) →
Task 5 (engine) → Task 6 (cli) → Task 7 (__init__) → Task 8 (mcp) → Task 9 (tests) → Task 10 (final verify)
```
