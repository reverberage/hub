# SDD Tasks: see

**Change ID**: `see` | **Phase**: 5 — Tasks | **Date**: 2026-07-19

---

## Task List

Ordered implementation steps. Each task is atomic and independently testable.

### Task 1: Scaffold the pyproject.toml and package skeleton
- Create `rvrb-see/` directory in the workspace parent (alongside transform/verify)
- Write `pyproject.toml` with hatchling build, entry points (`rvrb-see`, `rvrb-see-mcp`), Apache-2.0, Python >=3.11
- Dependencies: `openai>=2.0.0`, `pydantic>=2.0`, `typer>=0.12`
- Optional deps: `mcp=["mcp>=1.0.0"]`, `dev=[...]`
- Verify: `python -c "import tomllib; cfg=tomllib.load(open('pyproject.toml','rb')); assert cfg['project']['name']=='rvrb-see'"`
- **Verification**: `python -c "import tomllib; d=tomllib.load(open('pyproject.toml','rb')); assert d['project']['scripts']['rvrb-see']; print('OK')"`

### Task 2: Create models.py
- Write `rvrb_see/models.py` with:
  - `MediaModality(StrEnum)` — TEXT, AUDIO, IMAGE, VIDEO
  - `MediaInput(BaseModel)` — path, modality, metadata
  - `MediaOutput(BaseModel)` — data, modality, format
  - `SeeResult(BaseModel)` — description, model, provider, prompt, tokens_used
  - `ToolCall`, `ToolResult`, `ProviderError`, `QuotaExhaustedError` (same as transform)
- **Verification**: `python -c "from rvrb_see.models import MediaModality, MediaInput, MediaOutput, SeeResult; print('OK')"`

### Task 3: Create provider.py
- Write `rvrb_see/provider.py` with:
  - `ModelProvider(Protocol)` — model, base_url, complete(), complete_structured(), complete_with_tools()
  - `DEFAULT_MODEL` = env `N3RVERBERAGE_DEFAULT_MODEL` or `"qwen3.7-plus"`
  - `DEFAULT_BASE_URL` = env `N3RVERBERAGE_DEFAULT_BASE_URL` or `"https://dashscope-intl.aliyuncs.com/compatible-mode/v1"`
  - `_PROVIDER_FALLBACKS` map: qwen/openai/local (same as transform, but with vision context)
  - `get_provider()` — try n3rverberage first, fallback to _GenericProvider
  - `_GenericProvider` — OpenAI-compatible with error wrapping
- **Verification**: `python -c "from rvrb_see.provider import ModelProvider, get_provider, DEFAULT_MODEL; print('OK')"`

### Task 4: Create io.py
- Write `rvrb_see/io.py` with:
  - `MIME_MAP` dict: .png, .jpg, .jpeg, .gif, .webp
  - `read_media(path) -> MediaInput` — validates path, detects extension, returns IMAGE modality with mime_type in metadata
  - `write_media(output, path) -> None` — writes text/binary output to file
- **Verification**: Create temp PNG/JPG files, test read/write, test errors for missing/unsupported

### Task 5: Create engine.py
- Write `rvrb_see/engine.py` with:
  - `SeeEngine.__init__(provider)` — stores provider
  - `SeeEngine.see(image: MediaInput | str, prompt: str | None = None) -> SeeResult`
  - Logic: resolve MediaInput → read image bytes → base64 encode → build multimodal message → call provider.complete(messages, temperature=0) → return SeeResult
- **Verification**: Unit tests with SpyProvider (captures messages to verify data URI format) and MockProvider (no network)

### Task 6: Create cli.py
- Write `rvrb_see/cli.py` with:
  - Typer app: `rvrb-see <image_path> [--prompt] [--json] [--model] [--provider] [--output]`
  - Validate image path exists
  - Resolve provider, create engine, call engine.see()
  - Output: plain text or JSON, exit 0/1
- **Verification**: `rvrb-see --help` shows all flags, exit codes correct

### Task 7: Create __init__.py
- Write `rvrb_see/__init__.py` with:
  - `__version__ = "0.1.0"`
  - Re-export all public API: SeeEngine, SeeResult, MediaModality, MediaInput, MediaOutput, ModelProvider, get_provider, DEFAULT_MODEL, DEFAULT_BASE_URL
- **Verification**: `python -c "from rvrb_see import *; print('OK')"`

### Task 8: Create mcp.py
- Write `rvrb_see/mcp.py` with:
  - Gated import for `mcp` (try/except ImportError)
  - `mcp = FastMCP("rvrb-see")` if available
  - tool `see(image_path: str, prompt: str = "") -> dict`
  - `main()` entry point
- **Verification**: `python -c "from rvrb_see.mcp import mcp, main; print(type(mcp).__name__)"` (with mcp installed)

### Task 9: Create test suite
- Write `tests/__init__.py` (empty)
- Write `tests/conftest.py` with `MockProvider` (no inheritance, 5 members)
- Write `tests/test_models.py` — MediaModality, MediaInput, MediaOutput, SeeResult, ProviderError, pickling
- Write `tests/test_provider.py` — get_provider(), DEFAULT_MODEL, env var resolution
- Write `tests/test_engine.py` — construction, see() with SpyProvider (data URI), temperature 0, error propagation
- Write `tests/test_cli.py` — help, missing args, --json, --model, --provider flags, exit codes
- Write `tests/test_io.py` — read/write with tmp_path, format detection, errors
- **Verification**: `pytest --offline` passes with 100% pass rate

### Task 10: Final verification
- Run `ruff check src/rvrb_see/ tests/` — zero errors
- Run `mypy src/rvrb_see/` — zero errors (with `ignore_missing_imports = true` in pyproject.toml)
- Run `pytest --offline` — 100% pass
- Verify all 48 ACs pass
- **Verification**: All three commands pass

---

## Execution Order

```
Task 1 (pyproject.toml + dirs) → Task 2 (models) → Task 3 (provider) → Task 4 (io) →
Task 5 (engine) → Task 6 (cli) → Task 7 (__init__) → Task 8 (mcp) → Task 9 (tests) → Task 10 (final verify)
```
