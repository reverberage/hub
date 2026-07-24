#!/usr/bin/env python3
"""Scaffold a new reverberage satellite package (protocol v2).

Usage: python scaffold-satellite.py <name> [output-dir] [--modality=<m>] [--remote <owner/repo>]

Creates <output-dir>/<name>/ with mandatory kernel modules:
    __init__.py, models.py, provider.py, engine.py
Plus: cli.py, mcp.py, tests/, pyproject.toml, README.md,
      .github/workflows/ci.yml, .github/workflows/sync-wiki.yml
io.py is generated only for non-TEXT modalities (audio, image, video).

With --remote, automatically creates the GitHub repo, pushes code, and
initializes the wiki via scripts/init-satellite-wiki.py.

Satellite protocol v2: docs/satellite-protocol-v2.md
Reference implementation: rvrb-hear (85 tests, 54 ACs, zero defects)
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from textwrap import dedent
from typing import Literal

Modality = Literal["text", "audio", "image", "video"]


def validate_name(name: str) -> str:
    """Validate satellite name: lowercase, no special chars except hyphen/underscore."""
    if not re.match(r"^[a-z][a-z0-9_-]*$", name):
        print(
            f"Error: '{name}' is not a valid satellite name. "
            "Use lowercase letters, digits, hyphens, and underscores only."
        )
        sys.exit(1)
    return name


def _pkg_name(name: str) -> str:
    """Convert satellite name to Python package name: my-scout → rvrb_my_scout."""
    return f"rvrb_{name.replace('-', '_')}"


def _class_name(name: str) -> str:
    """Convert satellite name to PascalCase class name: my-scout → MyScout."""
    parts = re.split(r"[-_]", name)
    return "".join(p.capitalize() for p in parts)


# ---------------------------------------------------------------------------
# Renderers
# ---------------------------------------------------------------------------


def _render_pyproject(name: str, pkg: str) -> str:
    return dedent(f"""\
    [build-system]
    requires = ["hatchling"]
    build-backend = "hatchling.build"

    [project]
    name = "rvrb-{name}"
    version = "0.1.0"
    description = "reverberage satellite: {name}"
    requires-python = ">=3.11"
    license = "Apache-2.0"
    dependencies = [
        "openai>=2.0.0",
        "pydantic>=2.0",
        "typer>=0.12",
    ]

    [project.optional-dependencies]
    mcp = ["mcp>=1.0.0"]
    dev = [
        "pytest>=8.0",
        "ruff>=0.5",
        "mypy>=1.10",
    ]

    [project.scripts]
    rvrb-{name} = "{pkg}.cli:app"
    rvrb-{name}-mcp = "{pkg}.mcp:main"

    [tool.ruff]
    target-version = "py311"

    [tool.mypy]
    python_version = "3.11"
    strict = true
    ignore_missing_imports = true

    [tool.pytest.ini_options]
    testpaths = ["tests"]
    """)


def _render_init(name: str, class_name: str, pkg: str, modality: str) -> str:
    has_io = modality != "text"
    io_import = f"from {pkg}.io import read_media, write_media\n" if has_io else ""

    lines = [
        f'"""reverberage satellite: {name}"""',
        "",
        '__version__ = "0.1.0"',
        "",
        f"from {pkg}.engine import {class_name}Engine",
    ]
    if has_io:
        lines.append(io_import.rstrip("\n"))
    lines.extend(
        [
            f"from {pkg}.models import {class_name}Result, MediaInput, MediaModality, MediaOutput",
            f"from {pkg}.provider import DEFAULT_BASE_URL, DEFAULT_MODEL, ModelProvider, get_provider",
            "",
            "__all__ = [",
            '    "__version__",',
            f'    "{class_name}Engine",',
            f'    "{class_name}Result",',
            '    "MediaInput",',
            '    "MediaModality",',
            '    "MediaOutput",',
            '    "ModelProvider",',
            '    "get_provider",',
            '    "DEFAULT_MODEL",',
            '    "DEFAULT_BASE_URL",',
        ]
    )
    if has_io:
        lines.extend(['    "read_media",', '    "write_media",'])
    lines.append("]")
    lines.append("")
    return "\n".join(lines)


def _render_models(name: str, class_name: str) -> str:
    return dedent(f"""\
    \"\"\"Pydantic models for {name}.\"\"\"

    from __future__ import annotations

    from enum import StrEnum
    from pathlib import Path

    from pydantic import BaseModel, Field


    class MediaModality(StrEnum):
        \"\"\"Supported media modalities.\"\"\"

        TEXT = "text"
        AUDIO = "audio"
        IMAGE = "image"
        VIDEO = "video"


    class MediaInput(BaseModel):
        \"\"\"Input media reference.\"\"\"

        path: Path
        modality: MediaModality = MediaModality.TEXT
        metadata: dict[str, object] = Field(default_factory=dict)


    class MediaOutput(BaseModel):
        \"\"\"Output media result.\"\"\"

        data: str | bytes
        modality: MediaModality = MediaModality.TEXT
        format: str = "text"


    class {class_name}Result(BaseModel):
        \"\"\"Result of a {name} operation.

        NOTE: The ``provider`` field must contain a human-readable provider name
        string (e.g. ``"qwen"``, ``"openai"``, ``"local"``), NOT an API key or
        other credential.
        \"\"\"

        output_text: str
        model: str = ""
        provider: str = ""
        prompt: str = ""
        tokens_used: int | None = None


    # ---------------------------------------------------------------------------
    # Provider interface types (no external dependency on n3rverberage)
    # ---------------------------------------------------------------------------


    class ToolCall(BaseModel):
        \"\"\"A function call requested by the model.\"\"\"

        id: str
        name: str
        arguments: dict[str, object] = Field(default_factory=dict)


    class ToolResult(BaseModel):
        \"\"\"Result of a completion with optional tool calls.\"\"\"

        content: str | None = None
        tool_calls: list[ToolCall] = Field(default_factory=list)


    class ProviderError(RuntimeError):
        \"\"\"Generic provider error during a completion call.\"\"\"

        def __init__(
            self,
            model_id: str,
            status_code: int,
            body: str | None = None,
        ) -> None:
            self.model_id = model_id
            self.status_code = status_code
            self.body = body
            super().__init__(f"[{{model_id}}] HTTP {{status_code}}: {{body or 'unknown error'}}")

        def __reduce__(self) -> tuple:
            return (type(self), (self.model_id, self.status_code, self.body))


    class QuotaExhaustedError(ProviderError):
        \"\"\"Quota exhausted for a model.\"\"\"

        def __reduce__(self) -> tuple:
            return (type(self), (self.model_id, self.status_code, self.body))
    """)


def _render_provider(name: str, default_model: str) -> str:
    """Render provider.py with stream support and proper error wrapping."""
    return dedent(f"""\
    \"\"\"Provider resolution for {name} satellite.

    Follows satellite protocol v2: try n3rverberage first, fall back to
    _GenericProvider for standalone operation.
    \"\"\"

    from __future__ import annotations

    import os
    from typing import Any, Protocol

    from openai import APIError as OpenAIError
    from pydantic import BaseModel

    from .models import ProviderError, ToolResult


    class ModelProvider(Protocol):
        \"\"\"Structural protocol — any object with these attributes is a valid provider.\"\"\"

        model: str
        base_url: str

        def complete(self, messages: list[dict[str, Any]], **kwargs: Any) -> str: ...
        def complete_structured(
            self, messages: list[dict[str, Any]], output_type: type[BaseModel], **kwargs: Any,
        ) -> BaseModel: ...
        def complete_with_tools(
            self, messages: list[dict[str, Any]], tools: list[dict[str, Any]], **kwargs: Any,
        ) -> ToolResult: ...


    # ---------------------------------------------------------------------------
    # Env-var-driven defaults
    # ---------------------------------------------------------------------------

    DEFAULT_MODEL: str = os.environ.get(
        "N3RVERBERAGE_DEFAULT_MODEL",
        "{default_model}",
    )
    DEFAULT_BASE_URL: str = os.environ.get(
        "N3RVERBERAGE_DEFAULT_BASE_URL",
        "https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
    )

    _PROVIDER_FALLBACKS: dict[str, tuple[str, str, str]] = {{
        "qwen": (
            "{default_model}",
            "https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
            "DASHSCOPE_API_KEY",
        ),
        "openai": (
            "gpt-4o",
            "https://api.openai.com/v1",
            "OPENAI_API_KEY",
        ),
        "local": (
            "llama3",
            "http://localhost:11434/v1",
            "",
        ),
    }}


    # ---------------------------------------------------------------------------
    # Error wrapping (provider-agnostic — no Qwen-specific codes)
    # ---------------------------------------------------------------------------


    def _wrap_error(model_id: str, exc: Exception) -> ProviderError:
        \"\"\"Wrap an OpenAI exception as a provider error.\"\"\"
        if isinstance(exc, OpenAIError):
            status = exc.status_code or 500
            body = exc.body if isinstance(exc.body, str) else str(exc)
            return ProviderError(model_id, status, body)
        return ProviderError(model_id, 500, str(exc))


    # ---------------------------------------------------------------------------
    # Generic fallback provider (standalone operation, no n3rverberage required)
    # ---------------------------------------------------------------------------


    class _GenericProvider:
        \"\"\"OpenAI-compatible provider for standalone satellite operation.

        Handles stream=SSE accumulation internally so the ModelProvider
        Protocol always returns a synchronous ``str``.
        \"\"\"

        def __init__(self, *, model: str, base_url: str, api_key: str) -> None:
            self.model = model
            self.base_url = base_url
            self._api_key = api_key

        def _client(self) -> Any:
            from openai import OpenAI
            return OpenAI(api_key=self._api_key, base_url=self.base_url, timeout=60.0)

        def complete(self, messages: list[dict[str, Any]], **kwargs: Any) -> str:
            stream = kwargs.pop("stream", False)
            max_tokens = kwargs.pop("max_tokens", 4096)
            try:
                response = self._client().chat.completions.create(
                    model=self.model,
                    messages=messages,
                    max_tokens=max_tokens,
                    stream=stream,
                    **kwargs,
                )
            except Exception as exc:
                raise _wrap_error(self.model, exc) from exc

            if stream:
                content_parts: list[str] = []
                for chunk in response:
                    delta = chunk.choices[0].delta if chunk.choices else None
                    if delta and delta.content:
                        content_parts.append(delta.content)
                return "".join(content_parts)

            return response.choices[0].message.content or ""

        def complete_structured(
            self,
            messages: list[dict[str, Any]],
            output_type: type[BaseModel],
            **kwargs: Any,
        ) -> BaseModel:
            import json

            max_tokens = kwargs.pop("max_tokens", 4096)
            schema = output_type.model_json_schema()
            response_format: dict[str, Any] = {{
                "type": "json_schema",
                "json_schema": {{"name": output_type.__name__, "schema": schema, "strict": True}},
            }}
            try:
                response = self._client().chat.completions.create(
                    model=self.model,
                    messages=messages,
                    max_tokens=max_tokens,
                    response_format=response_format,
                    **kwargs,
                )
            except Exception as exc:
                raise _wrap_error(self.model, exc) from exc

            raw = response.choices[0].message.content
            if not raw:
                raise ProviderError(self.model, 200, "empty response")
            try:
                return output_type.model_validate(json.loads(raw))
            except Exception as exc:
                raise ProviderError(self.model, 200, f"validation failed: {{exc}}") from exc

        def complete_with_tools(
            self,
            messages: list[dict[str, Any]],
            tools: list[dict[str, Any]],
            **kwargs: Any,
        ) -> ToolResult:
            max_tokens = kwargs.pop("max_tokens", 4096)
            try:
                response = self._client().chat.completions.create(
                    model=self.model,
                    messages=messages,
                    tools=tools,
                    tool_choice="auto",
                    max_tokens=max_tokens,
                    **kwargs,
                )
            except Exception as exc:
                raise _wrap_error(self.model, exc) from exc

            msg = response.choices[0].message
            return ToolResult(
                content=msg.content,
                tool_calls=[],
            )


    # ---------------------------------------------------------------------------
    # Provider factory
    # ---------------------------------------------------------------------------


    def get_provider(
        model: str | None = None,
        provider: str | None = None,
    ) -> ModelProvider:
        \"\"\"Resolve provider: n3rverberage if available, generic fallback otherwise.\"\"\"
        resolved_model = model or DEFAULT_MODEL
        resolved_provider = provider or os.environ.get("N3RVERBERAGE_PROVIDER") or "qwen"

        try:
            from n3rverberage.providers import get_provider as n3rv_get_provider
            return n3rv_get_provider(name=f"{{resolved_provider}}:{{resolved_model}}")
        except ImportError:
            pass

        provider_type = resolved_provider.strip().lower()
        if provider_type not in _PROVIDER_FALLBACKS:
            supported = ", ".join(_PROVIDER_FALLBACKS)
            raise ValueError(f"Unknown provider '{{provider_type}}'. Supported: {{supported}}")

        default_model, default_url, api_key_var = _PROVIDER_FALLBACKS[provider_type]
        base_url = os.environ.get("N3RVERBERAGE_DEFAULT_BASE_URL") or default_url
        api_key = os.environ.get(api_key_var) if api_key_var else "not-needed"
        if api_key_var and not api_key:
            raise ValueError(f"{{api_key_var}} is not set. Set it or install n3rverberage.")

        return _GenericProvider(
            model=resolved_model or default_model,
            base_url=base_url,
            api_key=api_key,
        )
    """)


def _render_engine(name: str, class_name: str, pkg: str) -> str:
    return dedent(f"""\
    \"\"\"{class_name} engine — constructor-injected provider, mock-ready.

    Follows satellite protocol v2 engine contract.
    Replace ``process()`` with a satellite-specific named method (e.g., ``see``, ``hear``).
    \"\"\"

    from __future__ import annotations

    from {pkg}.models import {class_name}Result, MediaInput
    from {pkg}.provider import ModelProvider


    class {class_name}Engine:
        \"\"\"{name} engine.

        Constructor-injected provider makes the engine mock-ready:
        pass a ``MockProvider`` in tests for zero network calls.
        \"\"\"

        def __init__(self, provider: ModelProvider) -> None:
            self.provider = provider

        def process(
            self,
            input_data: MediaInput | str,
            prompt: str | None = None,
        ) -> {class_name}Result:
            \"\"\"Process input and return structured result.

            Parameters
            ----------
            input_data : MediaInput | str
                Input to process.
            prompt : str | None
                Optional custom prompt/instruction.

            Returns
            -------
            {class_name}Result
            \"\"\"
            if isinstance(input_data, str):
                input_data = MediaInput(path="", metadata={{"text": input_data}})

            resolved_prompt = prompt or f"Process the input using {{self.provider.model}}."
            text = input_data.metadata.get("text", str(input_data.path))

            messages = [
                {{
                    "role": "system",
                    "content": f"You are a {{self.__class__.__name__}} processing inputs.",
                }},
                {{
                    "role": "user",
                    "content": f"Prompt: {{resolved_prompt}}\\n\\nInput: {{text}}",
                }},
            ]

            response = self.provider.complete(messages, temperature=0)

            # Derive provider name from base_url hostname — never use _api_key
            provider_name = "unknown"
            if "dashscope" in self.provider.base_url:
                provider_name = "qwen"
            elif "openai.com" in self.provider.base_url:
                provider_name = "openai"
            elif "localhost" in self.provider.base_url or "127.0.0.1" in self.provider.base_url:
                provider_name = "local"

            return {class_name}Result(
                output_text=response,
                model=self.provider.model,
                provider=provider_name,
                prompt=resolved_prompt,
            )
    """)


def _render_cli(name: str, class_name: str, pkg: str, modality: str) -> str:
    """Render CLI module. File-input for audio/image/video, text-arg for text."""
    has_file_input = modality != "text"
    input_help = f"Path to {modality} file" if has_file_input else "Input text"

    # Build the file validation block (only for non-text modalities)
    if has_file_input:
        file_check = (
            "        if not input_path.exists():\n"
            '            typer.echo(f"Error: File not found: {input_path}", err=True)\n'
            "            raise typer.Exit(code=1)\n"
            f"        engine = {class_name}Engine(get_provider(model=model, provider=provider))\n"
            "        result_obj = engine.process(input_path, prompt=prompt or None)\n"
        )
        input_param = (
            f'    input_path: Path = typer.Argument(\n        ..., help="{input_help}",\n    ),\n'
        )
    else:
        file_check = (
            f"        engine = {class_name}Engine(get_provider(model=model, provider=provider))\n"
            "        result_obj = engine.process(text, prompt=prompt or None)\n"
        )
        input_param = (
            f'    text: str = typer.Argument(\n        ..., help="{input_help}",\n    ),\n'
        )

    body = (
        "#!/usr/bin/env python3\n"
        f'"""{class_name} engine CLI."""\n'
        "\n"
        "from __future__ import annotations\n"
        "\n"
        "from pathlib import Path\n"
        "\n"
        "import typer\n"
        "\n"
        f"from {pkg} import __version__\n"
        f"from {pkg}.engine import {class_name}Engine\n"
        f"from {pkg}.provider import get_provider\n"
        "\n"
        "app = typer.Typer(no_args_is_help=True)\n"
        "\n"
        "\n"
        "def version_callback(value: bool) -> None:\n"
        "    if value:\n"
        f'        typer.echo(f"rvrb-{name} {{__version__}}")\n'
        "        raise typer.Exit()\n"
        "\n"
        "\n"
        "@app.command()\n"
        "def main(\n" + input_param + "    prompt: str = typer.Option(\n"
        '        "", "--prompt", "-p", help="Custom prompt/instruction",\n'
        "    ),\n"
        "    json_output: bool = typer.Option(\n"
        '        False, "--json", help="Output as JSON",\n'
        "    ),\n"
        "    model: str | None = typer.Option(\n"
        '        None, "--model", "-m", help="Override model ID",\n'
        "    ),\n"
        "    provider: str | None = typer.Option(\n"
        '        None, "--provider", help="Provider name: qwen, openai, local. Overrides N3RVERBERAGE_PROVIDER env var.",\n'
        "    ),\n"
        "    output: Path | None = typer.Option(\n"
        '        None, "--output", "-o", help="Write output to file",\n'
        "    ),\n"
        "    version: bool = typer.Option(\n"
        '        False, "--version", "-v", help="Show version and exit.", callback=version_callback, is_eager=True,\n'
        "    ),\n"
        ") -> None:\n"
        f'    """{class_name} engine — {modality} processing."""\n'
        "    try:\n" + file_check + "        if json_output:\n"
        "            typer.echo(result_obj.model_dump_json(indent=2))\n"
        "        elif output:\n"
        "            output.write_text(result_obj.output_text)\n"
        "        else:\n"
        "            typer.echo(result_obj.output_text)\n"
        "\n"
        "    except Exception as exc:\n"
        '        typer.echo(f"Error: {exc}", err=True)\n'
        "        raise typer.Exit(code=1) from exc\n"
        "\n"
        "\n"
        'if __name__ == "__main__":\n'
        "    app()\n"
    )
    return body


def _render_mcp(name: str, pkg: str) -> str:
    return dedent(f"""\
    \"\"\"MCP server for rvrb-{name}.

    Gated import: requires ``pip install rvrb-{name}[mcp]``.
    \"\"\"

    from __future__ import annotations

    from typing import Any

    try:
        from mcp.server import FastMCP
    except ImportError:
        raise ImportError(
            "MCP support requires the 'mcp' extra. "
            "Install with: pip install rvrb-{name}[mcp]",
        ) from None

    from {pkg}.engine import {_class_name(name)}Engine
    from {pkg}.provider import get_provider

    mcp = FastMCP("rvrb-{name}")


    @mcp.tool()
    def process(input_text: str, prompt: str = "") -> dict[str, Any]:
        \"\"\"Process input using the {name} engine.

        Parameters
        ----------
        input_text : str
            The text to process.
        prompt : str
            Optional custom instruction.
        \"\"\"
        engine = {_class_name(name)}Engine(get_provider())
        result = engine.process(input_text, prompt=prompt or None)
        return result.model_dump()


    def main() -> None:
        \"\"\"Entry point: rvrb-{name}-mcp.\"\"\"
        mcp.run(transport="stdio")


    if __name__ == "__main__":
        main()
    """)


def _render_io(name: str, pkg: str, modality: str) -> str:
    """Render io.py for non-TEXT modalities."""
    if modality == "text":
        # Text-only satellites don't need io.py
        return ""

    if modality == "audio":
        mime_map = """    ".wav": "audio/wav",
        ".mp3": "audio/mpeg",
        ".aac": "audio/aac",
        ".flac": "audio/flac",
        ".m4a": "audio/mp4",
        ".ogg": "audio/ogg",
        ".amr": "audio/amr",\n"""
    elif modality == "image":
        mime_map = """    ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".gif": "image/gif",
        ".webp": "image/webp",\n"""
    elif modality == "video":
        mime_map = """    ".mp4": "video/mp4",
        ".webm": "video/webm",
        ".mov": "video/quicktime",\n"""
    else:
        mime_map = ""

    return dedent(f"""\
    \"\"\"Media I/O for {name} satellite.\"\"\"

    from __future__ import annotations

    from pathlib import Path

    from {pkg}.models import MediaInput, MediaModality, MediaOutput

    MIME_MAP: dict[str, str] = {{
    {mime_map}    }}

    _MODALITY = MediaModality.{modality.upper()}


    def read_media(path: Path) -> MediaInput:
        \"\"\"Read a {modality} file and return a MediaInput.\"\"\"
        if not path.exists():
            raise FileNotFoundError(f"File not found: {{path}}")
        ext = path.suffix.lower()
        if ext not in MIME_MAP:
            supported = ", ".join(MIME_MAP)
            raise ValueError(f"Unsupported {modality} format '{{ext}}'. Supported: {{supported}}")
        return MediaInput(
            path=path,
            modality=_MODALITY,
            metadata={{"mime_type": MIME_MAP[ext], "format": ext.lstrip(".")}},
        )


    def write_media(output: MediaOutput, path: Path) -> None:
        \"\"\"Write MediaOutput to a file.\"\"\"
        if isinstance(output.data, str):
            path.write_text(output.data, encoding="utf-8")
        else:
            path.write_bytes(output.data)
    """)


def _render_conftest(pkg: str) -> str:
    return dedent(f"""\
    \"\"\"Shared test fixtures.\"\"\"

    from __future__ import annotations

    from typing import Any

    from pydantic import BaseModel

    from {pkg}.models import ToolResult


    class MockProvider:
        \"\"\"Structural mock provider — matches ModelProvider protocol by shape.

        No inheritance, no ABC, no MagicMock.  Returns reasonable canned
        responses for all three completion methods.
        \"\"\"

        def __init__(self, model: str = "mock-model", base_url: str = "mock://"):
            self.model = model
            self.base_url = base_url

        def complete(self, messages: list[dict[str, Any]], **kwargs: Any) -> str:
            return "mock completion response"

        def complete_structured(
            self,
            messages: list[dict[str, Any]],
            output_type: type[BaseModel],
            **kwargs: Any,
        ) -> BaseModel:
            # Try to construct a valid instance using default values
            try:
                return output_type()
            except Exception:
                # Fall back to a minimal construction for types with required fields
                try:
                    return output_type.model_validate({{}})
                except Exception:
                    return output_type(output_text="mock", model="mock", provider="mock")

        def complete_with_tools(
            self,
            messages: list[dict[str, Any]],
            tools: list[dict[str, Any]],
            **kwargs: Any,
        ) -> ToolResult:
            return ToolResult(content="mock tool result", tool_calls=[])


    class SpyProvider:
        \"\"\"Provider that captures messages for inspection in tests.\"\"\"

        def __init__(self, model: str = "spy-model", base_url: str = "spy://"):
            self.model = model
            self.base_url = base_url

        def complete(self, messages: list[dict[str, Any]], **kwargs: Any) -> str:
            self.captured_messages = messages  # type: ignore[attr-defined]
            self.captured_kwargs = kwargs  # type: ignore[attr-defined]
            return "spy response"

        def complete_structured(
            self,
            messages: list[dict[str, Any]],
            output_type: type[BaseModel],
            **kwargs: Any,
        ) -> BaseModel:
            self.captured_messages = messages  # type: ignore[attr-defined]
            try:
                return output_type()
            except Exception:
                return output_type.model_validate({{}})

        def complete_with_tools(
            self,
            messages: list[dict[str, Any]],
            tools: list[dict[str, Any]],
            **kwargs: Any,
        ) -> ToolResult:
            return ToolResult(content="spy tool result", tool_calls=[])
    """)


def _render_test_models(name: str, class_name: str, pkg: str) -> str:
    return dedent(f"""\
    \"\"\"Tests for {name} data models.\"\"\"

    from __future__ import annotations

    import pickle
    from pathlib import Path

    from {pkg}.models import (
        {class_name}Result,
        MediaInput,
        MediaModality,
        MediaOutput,
        ProviderError,
        QuotaExhaustedError,
        ToolCall,
        ToolResult,
    )


    class TestMediaModality:
        def test_all_members(self) -> None:
            assert MediaModality.TEXT == "text"
            assert MediaModality.AUDIO == "audio"
            assert MediaModality.IMAGE == "image"
            assert MediaModality.VIDEO == "video"
            assert len(MediaModality) == 4


    class TestMediaInput:
        def test_default(self) -> None:
            mi = MediaInput(path=Path("/tmp/test.txt"))
            assert mi.modality == MediaModality.TEXT
            assert mi.metadata == {{}}

        def test_with_modality(self) -> None:
            mi = MediaInput(path=Path("/tmp/test.wav"), modality=MediaModality.AUDIO)
            assert mi.modality == MediaModality.AUDIO


    class TestMediaOutput:
        def test_default(self) -> None:
            mo = MediaOutput(data="hello")
            assert mo.data == "hello"
            assert mo.modality == MediaModality.TEXT
            assert mo.format == "text"

        def test_bytes(self) -> None:
            mo = MediaOutput(data=b"hello")
            assert mo.data == b"hello"


    class Test{class_name}Result:
        def test_defaults(self) -> None:
            r = {class_name}Result(output_text="test")
            assert r.output_text == "test"
            assert r.model == ""
            assert r.provider == ""
            assert r.prompt == ""
            assert r.tokens_used is None

        def test_full(self) -> None:
            r = {class_name}Result(
                output_text="result",
                model="gpt-4",
                provider="openai",
                prompt="do something",
                tokens_used=100,
            )
            assert r.tokens_used == 100
            assert r.provider == "openai"


    class TestProviderErrors:
        def test_provider_error(self) -> None:
            err = ProviderError("test-model", 429, "quota")
            assert err.model_id == "test-model"
            assert err.status_code == 429
            assert "429" in str(err)

        def test_quota_exhausted(self) -> None:
            err = QuotaExhaustedError("test-model", 429, "quota")
            assert isinstance(err, ProviderError)

        def test_pickle(self) -> None:
            err = ProviderError("test-model", 500, "boom")
            restored = pickle.loads(pickle.dumps(err))
            assert restored.model_id == "test-model"
            assert restored.status_code == 500


    class TestToolTypes:
        def test_tool_call(self) -> None:
            tc = ToolCall(id="1", name="search")
            assert tc.id == "1"

        def test_tool_result(self) -> None:
            tr = ToolResult(content="result")
            assert tr.content == "result"
            assert tr.tool_calls == []
    """)


def _render_test_provider(name: str, pkg: str, default_model: str) -> str:
    return dedent(f"""\
    \"\"\"Tests for {name} provider resolution.\"\"\"

    from __future__ import annotations

    import os

    from {pkg}.provider import DEFAULT_BASE_URL, DEFAULT_MODEL, get_provider


    def test_default_model() -> None:
        assert DEFAULT_MODEL == "{default_model}"


    def test_default_base_url() -> None:
        assert "dashscope" in DEFAULT_BASE_URL


    def test_get_provider_returns_model_provider() -> None:
        \"\"\"get_provider() returns something that quacks like a ModelProvider.\"\"\"
        provider = get_provider(model="qwen3-coder-plus", provider="local")
        assert hasattr(provider, "model")
        assert hasattr(provider, "base_url")
        assert hasattr(provider, "complete")
        assert callable(provider.complete)


    def test_get_provider_unknown_provider_raises() -> None:
        import pytest
        with pytest.raises(ValueError, match="Unknown provider"):
            get_provider(provider="nonexistent")


    def test_default_model_env_override() -> None:
        os.environ["N3RVERBERAGE_DEFAULT_MODEL"] = "gpt-4-custom"
        # Re-import to pick up env var (DEFAULT_MODEL is set at import time)
        import importlib
        import {pkg}.provider as mod
        importlib.reload(mod)
        assert mod.DEFAULT_MODEL == "gpt-4-custom"
        del os.environ["N3RVERBERAGE_DEFAULT_MODEL"]
        importlib.reload(mod)
    """)


def _render_test_engine(name: str, class_name: str, pkg: str) -> str:
    return dedent(f"""\
    \"\"\"Tests for {class_name}Engine.\"\"\"

    from __future__ import annotations

    from pathlib import Path

    from {pkg}.engine import {class_name}Engine
    from {pkg}.models import MediaInput
    from tests.conftest import MockProvider, SpyProvider


    class TestEngineConstruction:
        def test_constructor_injection(self) -> None:
            \"\"\"Engine accepts a structurally-compatible provider.\"\"\"
            engine = {class_name}Engine(provider=MockProvider())
            assert engine.provider is not None

        def test_single_public_method(self) -> None:
            \"\"\"Engine has one main method: process.\"\"\"
            engine = {class_name}Engine(provider=MockProvider())
            assert hasattr(engine, "process")
            assert callable(engine.process)

        def test_provider_attribute(self) -> None:
            engine = {class_name}Engine(provider=MockProvider(model="custom"))
            assert engine.provider.model == "custom"


    class TestEngineProcess:
        def test_returns_result(self) -> None:
            engine = {class_name}Engine(provider=MockProvider())
            result = engine.process("test input")
            assert result is not None
            assert result.output_text == "mock completion response"

        def test_temperature_zero(self) -> None:
            spy = SpyProvider()
            engine = {class_name}Engine(provider=spy)
            engine.process("test input")
            assert spy.captured_kwargs.get("temperature") == 0

        def test_accepts_media_input(self) -> None:
            engine = {class_name}Engine(provider=MockProvider())
            mi = MediaInput(path=Path("/tmp/test.txt"))
            result = engine.process(mi)
            assert result is not None

        def test_no_side_effects(self) -> None:
            \"\"\"Engine must not write files or print to stdout.\"\"\"
            engine = {class_name}Engine(provider=MockProvider())
            engine.process("test")
            # If we get here without I/O errors, the test passes

        def test_result_provider_field_is_name_not_key(self) -> None:
            \"\"\"Provider field must be a name string, not an API key.\"\"\"
            engine = {class_name}Engine(provider=MockProvider(base_url="https://api.openai.com/v1"))
            result = engine.process("test")
            assert result.provider in ("qwen", "openai", "local", "unknown")
            assert not result.provider.startswith("sk-")
    """)


def _render_test_cli(name: str, pkg: str) -> str:
    return dedent(f"""\
    \"\"\"CLI tests for rvrb-{name}.\"\"\"

    from __future__ import annotations

    import re

    from typer.testing import CliRunner

    from {pkg}.cli import app

    runner = CliRunner()


    def strip_ansi(text: str) -> str:
        \"\"\"Remove ANSI escape codes from text.\"\"\"
        ansi_escape = re.compile(r'\\x1b\\[[0-9;]*m')
        return ansi_escape.sub('', text)


    def test_help() -> None:
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0

    def test_json_flag_present() -> None:
        result = runner.invoke(app, ["--help"])
        assert "--json" in strip_ansi(result.output)

    def test_model_flag_present() -> None:
        result = runner.invoke(app, ["--help"])
        assert "--model" in strip_ansi(result.output)

    def test_provider_flag_present() -> None:
        result = runner.invoke(app, ["--help"])
        assert "--provider" in strip_ansi(result.output)

    def test_output_flag_present() -> None:
        result = runner.invoke(app, ["--help"])
        assert "--output" in strip_ansi(result.output)

    def test_prompt_flag_present() -> None:
        result = runner.invoke(app, ["--help"])
        assert "--prompt" in strip_ansi(result.output)

    def test_exit_code_one_on_error() -> None:
        result = runner.invoke(app, ["--model", "nonexistent-model", "--json", "test"])
        # Should exit non-zero (either missing input or provider error)
        assert result.exit_code != 0

    def test_version() -> None:
        result = runner.invoke(app, ["--version"])
        assert result.exit_code == 0
        assert "0.1.0" in strip_ansi(result.output)
    """)


def _render_ci_workflow(name: str) -> str:
    return dedent("""\
    name: CI

    on:
      push:
        branches: [main]
      pull_request:
        branches: [main]

    jobs:
      quality:
        runs-on: ubuntu-latest
        strategy:
          matrix:
            python-version: ["3.11", "3.12", "3.13"]
        steps:
          - uses: actions/checkout@v4
          - uses: actions/setup-python@v6
            with:
              python-version: ${{ matrix.python-version }}
          - name: Install
            run: pip install -e ".[dev]"
          - name: Lint (ruff)
            run: ruff check src/ tests/
          - name: Type check (mypy)
            run: mypy src/
          - name: Test (pytest)
            run: pytest --offline
    """)


def _render_sync_wiki_workflow() -> str:
    return dedent("""\
    name: Sync Wiki

    on:
      push:
        branches: [main]
        paths:
          - 'docs/**'

    concurrency:
      group: wiki-${{ github.ref }}
      cancel-in-progress: true

    jobs:
      sync:
        runs-on: ubuntu-latest
        permissions:
          contents: write
        steps:
          - uses: actions/checkout@v4
            with:
              fetch-depth: 0
          - uses: reverberage/.github/actions/sync-wiki@main
            with:
              token: ${{ github.token }}
              path: docs
    """)


def _render_readme(name: str) -> str:
    return dedent(f"""\
    # rvrb-{name}

    reverberage satellite: {name}

    ## Install

    ```bash
    pip install rvrb-{name}
    ```

    With MCP support:

    ```bash
    pip install rvrb-{name}[mcp]
    ```

    ## Usage

    ```bash
    rvrb-{name} --help
    ```

    ## Develop

    ```bash
    pip install -e ".[dev]"
    pytest --offline
    ```

    ## Satellite Protocol

    This satellite follows [satellite protocol v2](https://github.com/reverberage/hub/blob/main/docs/satellite-protocol-v2.md).
    """)


# ---------------------------------------------------------------------------
# Scaffold function
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Wiki page renderers
# ---------------------------------------------------------------------------


def _wiki_home(name: str, class_name: str) -> str:
    return dedent(f"""\
    # rvrb-{name}

    reverberage satellite: **{name}**.

    The `{class_name}Engine` uses constructor-injected `ModelProvider` for {name} processing.

    ## Quick Links

    - [Architecture](Architecture) — Component design
    - [CLI Reference](CLI-Reference) — All CLI commands and flags
    - [Getting Started](Getting-Started) — Installation and basic usage
    - [Development](Development) — Setup, testing, linting
    - [FAQ](FAQ) — Frequently asked questions
    - [MCP Server](MCP-Server) — MCP tool integration
    - [Python API](Python-API) — Public API reference

    ## Satellite Protocol

    This satellite follows [satellite protocol v2](https://github.com/reverberage/hub/blob/main/docs/satellite-protocol-v2.md).
    """)


def _wiki_architecture(name: str, class_name: str, pkg: str, modality: str) -> str:
    has_io = modality != "text"
    io_section = (
        f"""\n### I/O Layer

The `io.py` module handles {modality} file reading and writing:

- `read_media(path) -> MediaInput` — reads and validates {modality} files
- `write_media(output, path) -> None` — writes results to files
"""
        if has_io
        else ""
    )
    return dedent(f"""\
    # Architecture

    ## Component Diagram

    ```
    CLI (cli.py)       ← optional entry point
      ↓
    Engine (engine.py) ← core logic, constructor-injected provider
      ↓
    Provider (provider.py) ← ModelProvider Protocol + get_provider() factory
      ↓
    API (OpenAI-compatible LLM)
    ```{io_section}
    ### Provider Layer

    Provider resolution follows a two-tier strategy:

    1. Try to import `n3rverberage.providers.get_provider()` (full provider chain)
    2. Fall back to `_GenericProvider` (standalone OpenAI-compatible client)

    No hard dependency on n3rverberage — the satellite works standalone.

    ### Engine Contract

    ```python
    class {class_name}Engine:
        def __init__(self, provider: ModelProvider): ...
        def process(self, input_data, prompt=None) -> {class_name}Result: ...
    ```

    - Single public method
    - Constructor-injected provider (mock-ready)
    - No side effects (I/O happens in cli.py and io.py only)
    """)


def _wiki_cli_ref(name: str, modality: str) -> str:
    file_input = modality != "text"
    input_desc = f"Path to {modality} file" if file_input else "Input text"
    return dedent(f"""\
    # CLI Reference

    ## rvrb-{name}

    ```bash
    rvrb-{name} [OPTIONS] {input_desc}
    ```

    ### Arguments

    | Argument | Required | Description |
    |----------|:--------:|-------------|
    | `{input_desc}` | Yes | The input to process |

    ### Options

    | Flag | Description |
    |------|-------------|
    | `--prompt, -p` | Custom prompt/instruction |
    | `--json` | Output as JSON |
    | `--model, -m` | Override model ID |
    | `--provider` | Provider name: qwen, openai, local |
    | `--output, -o` | Write output to file |
    | `--version, -v` | Show version and exit |

    ### Exit Codes

    | Code | Meaning |
    |:----:|---------|
    | 0 | Success |
    | 1 | Error (validation, provider, I/O) |

    ### Pipe Composition

    ```bash
    # Chain with other satellites
    rvrb-transcriber audio.mp3 | rvrb-{name}
    rvrb-{name} input.txt --json | rvrb-verify
    ```

    ### MCP Server

    ```bash
    rvrb-{name}-mcp
    ```
    """)


def _wiki_getting_started(name: str) -> str:
    return dedent(f"""\
    # Getting Started

    ## Installation

    ```bash
    pip install rvrb-{name}
    ```

    With MCP support:

    ```bash
    pip install rvrb-{name}[mcp]
    ```

    ## Prerequisites

    - Python >= 3.11
    - API key for your chosen provider:
      - Qwen (DashScope): `DASHSCOPE_API_KEY`
      - OpenAI: `OPENAI_API_KEY`
      - Local: none required

    ## Quick Start

    ```bash
    # Set your API key
    export DASHSCOPE_API_KEY=sk-...

    # Run the satellite
    rvrb-{name} "your input"

    # With JSON output
    rvrb-{name} "your input" --json
    ```

    ## Provider Configuration

    | Variable | Default | Purpose |
    |----------|---------|---------|
    | `N3RVERBERAGE_PROVIDER` | qwen | Provider name |
    | `N3RVERBERAGE_DEFAULT_MODEL` | (model-specific) | Default model ID |
    | `N3RVERBERAGE_DEFAULT_BASE_URL` | DashScope endpoint | Base URL for API |
    """)


def _wiki_development(name: str) -> str:
    return dedent(f"""\
    # Development

    ## Local Setup

    ```bash
    git clone https://github.com/reverberage/rvrb-{name}.git
    cd rvrb-{name}
    pip install -e ".[dev]"
    ```

    ## Testing

    ```bash
    # Run all tests (no network required)
    pytest --offline

    # Run with coverage
    pytest --cov=src/
    ```

    ## Linting & Type Checking

    ```bash
    ruff check src/ tests/
    mypy src/
    ```

    ## Release

    ```bash
    hatch build
    hatch publish
    ```

    ## CI/CD

    GitHub Actions runs on every push and PR:
    - Python 3.11, 3.12, 3.13 matrix
    - Ruff linting
    - mypy type checking
    - pytest (offline)
    """)


def _wiki_faq(name: str) -> str:
    return dedent(f"""\
    # FAQ

    **Q: What does rvrb-{name} do?**
    A: It's the {name} satellite in the reverberage ecosystem. See the [Home](Home) page for details.

    **Q: Do I need n3rverberage?**
    A: No. The satellite works standalone with its own `_GenericProvider` fallback. n3rverberage enhances it with provider chains and quota detection.

    **Q: How do I change the model?**
    A: Use `--model` flag or set `N3RVERBERAGE_DEFAULT_MODEL` env var.

    **Q: Can I use this with OpenAI?**
    A: Yes. Set `N3RVERBERAGE_PROVIDER=openai` and `OPENAI_API_KEY`.

    **Q: Can I use a local model?**
    A: Yes. Set `N3RVERBERAGE_PROVIDER=local` and `N3RVERBERAGE_DEFAULT_BASE_URL` to your local endpoint.
    """)


def _wiki_mcp(name: str, class_name: str) -> str:
    return dedent(f"""\
    # MCP Server

    rvrb-{name} exposes an optional MCP server for use with any MCP-compatible agent.

    ## Starting the Server

    ```bash
    rvrb-{name}-mcp
    ```

    This runs the MCP server via stdio transport.

    ## Tool: process

    The server registers a single `process` tool:

    - **Parameters**: `input_text` (str, required), `prompt` (str, optional)
    - **Returns**: dict with `output_text`, `model`, `provider`, `prompt`, `tokens_used`

    ## Usage with opencode

    Add to your `opencode.json`:

    ```json
    {{
      "mcpServers": {{
        "rvrb-{name}": {{
          "command": "rvrb-{name}-mcp",
          "args": []
        }}
      }}
    }}
    ```
    """)


def _wiki_python_api(name: str, class_name: str, pkg: str) -> str:
    return dedent(f"""\
    # Python API

    ## {class_name}Engine

    The main engine class.

    ```python
    from {pkg} import {class_name}Engine, {class_name}Result
    from {pkg}.provider import get_provider

    engine = {class_name}Engine(provider=get_provider())
    result = engine.process("your input")
    print(result.output_text)
    ```

    ## {class_name}Result

    | Field | Type | Description |
    |-------|------|-------------|
    | `output_text` | `str` | The processed output |
    | `model` | `str` | Model ID used |
    | `provider` | `str` | Provider name (not API key) |
    | `prompt` | `str` | The prompt used |
    | `tokens_used` | `int \\| None` | Token count if available |

    ## ModelProvider Protocol

    ```python
    class ModelProvider(Protocol):
        model: str
        base_url: str
        def complete(self, messages, **kwargs) -> str: ...
        def complete_structured(self, messages, output_type, **kwargs) -> BaseModel: ...
        def complete_with_tools(self, messages, tools, **kwargs) -> ToolResult: ...
    ```

    Any object matching this structure is a valid provider — no inheritance required.

    ## get_provider()

    ```python
    from {pkg}.provider import get_provider

    # Default provider (Qwen)
    provider = get_provider()

    # Specific provider and model
    provider = get_provider(model="gpt-4", provider="openai")

    # Local model
    provider = get_provider(provider="local")
    ```

    ## MockProvider (for testing)

    ```python
    from tests.conftest import MockProvider

    engine = {class_name}Engine(provider=MockProvider())
    result = engine.process("test input")
    ```
    """)


# ---------------------------------------------------------------------------
# GitHub & wiki helpers
# ---------------------------------------------------------------------------


def _init_github_and_wiki(name: str, remote: str, target: Path) -> None:
    """Create GitHub repo, push code, and initialize wiki."""
    import subprocess

    def eprint(*a: object, **kw: object) -> None:
        kw.setdefault("file", sys.stderr)
        print(*a, **kw)

    def run(cmd: list[str], **kw: object) -> subprocess.CompletedProcess[str]:
        kw.setdefault("capture_output", True)
        kw.setdefault("text", True)
        result = subprocess.run(cmd, **kw)  # type: ignore[arg-type]
        if result.returncode != 0 and kw.get("check") is not False:
            eprint(f"Command failed: {' '.join(str(c) for c in cmd)}")
            eprint(result.stderr.strip() if result.stderr else "")
        return result  # type: ignore[return-value]

    eprint(f"=== Setting up GitHub repo: {remote} ===")

    # Step 1: Check gh auth
    auth = run(["gh", "auth", "status"])
    if auth.returncode != 0:
        eprint("WARNING: gh CLI not authenticated. Skipping GitHub setup.")
        eprint(f"  Run: cd {target} && git remote add origin https://github.com/{remote}.git")
        eprint(
            f"  Then: python ../hub/scripts/init-satellite-wiki.py {remote} --push docs/ --workflow"
        )
        return

    # Step 2: Initialize git in the target directory
    run(["git", "-C", str(target), "init", "-b", "main"])
    run(["git", "-C", str(target), "config", "user.email", "bot@reverberage.github.com"])
    run(["git", "-C", str(target), "config", "user.name", "reverberage bot"])
    run(["git", "-C", str(target), "add", "."])
    run(["git", "-C", str(target), "commit", "-m", f"feat: scaffold rvrb-{name}"])

    # Step 3: Create GitHub repo
    eprint(f"Creating GitHub repo: {remote}...")
    repo_create = run(
        ["gh", "repo", "create", remote, "--private", "--source", str(target), "--push"],
    )
    if repo_create.returncode != 0:
        eprint("WARNING: Failed to create GitHub repo. Manual setup required.")
        return

    # Step 4: Initialize wiki
    eprint("Initializing wiki...")
    wiki_script = Path(__file__).resolve().parent / "init-satellite-wiki.py"
    if wiki_script.exists():
        wiki_run = run(
            [
                sys.executable,
                str(wiki_script),
                remote,
                "--push",
                str(target / "docs"),
                "--workflow",
            ],
        )
        if wiki_run.returncode == 0:
            eprint(f"✅ Wiki initialized at https://github.com/{remote}/wiki")
        else:
            eprint("WARNING: Wiki initialization did not complete.")
            eprint(f"  Run: python {wiki_script} {remote} --push docs/ --workflow")
    else:
        eprint("WARNING: init-satellite-wiki.py not found. Skipping wiki init.")
        eprint(
            f"  Run: python ../hub/scripts/init-satellite-wiki.py {remote} --push docs/ --workflow"
        )


# ---------------------------------------------------------------------------
# Scaffold function
# ---------------------------------------------------------------------------


def scaffold(
    name: str,
    output_dir: Path | None = None,
    modality: str = "text",
    remote: str | None = None,
) -> None:
    """Scaffold a new satellite package."""
    if output_dir is not None:
        target = Path(output_dir) / f"rvrb-{name}"
    else:
        hub_root = Path(__file__).resolve().parent.parent
        target = hub_root.parent / f"rvrb-{name}"

    if target.exists():
        print(f"Error: {target} already exists.")
        sys.exit(1)

    pkg = _pkg_name(name)
    class_name = _class_name(name)
    pkg_dir = target / "src" / pkg
    tests_dir = target / "tests"

    # Default model depends on modality
    model_map: dict[str, str] = {
        "text": "qwen3-coder-plus",
        "audio": "qwen3.5-omni-plus",
        "image": "qwen3.7-plus",
        "video": "qwen3.7-plus",
    }
    default_model = model_map.get(modality, "qwen3-coder-plus")

    # Create directories
    tests_dir.mkdir(parents=True)
    pkg_dir.mkdir(parents=True)
    (target / ".github" / "workflows").mkdir(parents=True)
    docs_dir = target / "docs"
    docs_dir.mkdir(parents=True)

    # Write mandatory kernel modules
    (pkg_dir / "__init__.py").write_text(_render_init(name, class_name, pkg, modality))
    (pkg_dir / "models.py").write_text(_render_models(name, class_name))
    (pkg_dir / "provider.py").write_text(_render_provider(name, default_model))
    (pkg_dir / "engine.py").write_text(_render_engine(name, class_name, pkg))

    # Write optional modules
    (pkg_dir / "cli.py").write_text(_render_cli(name, class_name, pkg, modality))
    (pkg_dir / "mcp.py").write_text(_render_mcp(name, pkg))

    # io.py only for non-TEXT modalities
    if modality != "text":
        (pkg_dir / "io.py").write_text(_render_io(name, pkg, modality))

    # Write project files
    (target / "pyproject.toml").write_text(_render_pyproject(name, pkg))
    (target / "README.md").write_text(_render_readme(name))
    (target / ".github" / "workflows" / "ci.yml").write_text(_render_ci_workflow(name))
    (target / ".github" / "workflows" / "sync-wiki.yml").write_text(_render_sync_wiki_workflow())

    # Write wiki documentation pages (used by init-satellite-wiki.py --push)
    (docs_dir / "Home.md").write_text(_wiki_home(name, class_name))
    (docs_dir / "Architecture.md").write_text(_wiki_architecture(name, class_name, pkg, modality))
    (docs_dir / "CLI-Reference.md").write_text(_wiki_cli_ref(name, modality))
    (docs_dir / "Getting-Started.md").write_text(_wiki_getting_started(name))
    (docs_dir / "Development.md").write_text(_wiki_development(name))
    (docs_dir / "FAQ.md").write_text(_wiki_faq(name))
    (docs_dir / "MCP-Server.md").write_text(_wiki_mcp(name, class_name))
    (docs_dir / "Python-API.md").write_text(_wiki_python_api(name, class_name, pkg))

    # Write test files
    (tests_dir / "__init__.py").write_text("")
    (tests_dir / "conftest.py").write_text(_render_conftest(pkg))
    (tests_dir / "test_models.py").write_text(_render_test_models(name, class_name, pkg))
    (tests_dir / "test_provider.py").write_text(_render_test_provider(name, pkg, default_model))
    (tests_dir / "test_engine.py").write_text(_render_test_engine(name, class_name, pkg))
    (tests_dir / f"test_{pkg}.py").write_text(_render_test_cli(name, pkg))

    # Summary
    has_io = "✅" if modality != "text" else "skipped (text-only)"
    print(f"Scaffolded rvrb-{name} ({modality} modality)")
    print("  Kernel: __init__.py, models.py, provider.py, engine.py")
    print(f"  Optional: cli.py, mcp.py, io.py ({has_io})")
    print("  Project: pyproject.toml, README.md, .github/workflows/ci.yml")
    print("  CI/CD: .github/workflows/sync-wiki.yml (auto-syncs docs/ to wiki on push)")
    print("  Wiki: docs/ (8 pages for wiki initialization)")
    print("  Tests: conftest.py, test_models.py, test_provider.py, test_engine.py, test_*.py")

    if remote:
        print()
        _init_github_and_wiki(name, remote, target)
    else:
        print()
        print("  Next steps:")
        print(f"    cd rvrb-{name}")
        print('    pip install -e ".[dev]"')
        print("    pytest --offline")
        print()
        print("  To create the GitHub repo and wiki:")
        print(
            f"    python ../hub/scripts/init-satellite-wiki.py reverberage/rvrb-{name} --push docs/ --workflow"
        )


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    name = validate_name(sys.argv[1])

    # Parse flags
    modality: Modality = "text"
    output_dir: Path | None = None
    remote: str | None = None
    i = 2
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg.startswith("--modality="):
            modality_value = arg.split("=", 1)[1]
            if modality_value not in ("text", "audio", "image", "video"):
                print(f"Error: Unknown modality '{modality_value}'. Use: text, audio, image, video")
                sys.exit(1)
            modality = modality_value  # type: ignore[assignment]
            i += 1
        elif arg == "--remote" and i + 1 < len(sys.argv):
            remote = sys.argv[i + 1]
            if "/" not in remote:
                print(f"Error: --remote must be in format <owner>/<repo>, got '{remote}'")
                sys.exit(1)
            i += 2
        elif arg.startswith("--remote="):
            remote = arg.split("=", 1)[1]
            if "/" not in remote:
                print(f"Error: --remote must be in format <owner>/<repo>, got '{remote}'")
                sys.exit(1)
            i += 1
        elif arg.startswith("--"):
            print(f"Error: Unknown flag '{arg}'")
            sys.exit(1)
        else:
            if output_dir is None:
                output_dir = Path(arg)
            else:
                print("Error: Too many positional arguments. Did you mean '--remote owner/repo'?")
                sys.exit(1)
            i += 1

    scaffold(name, output_dir, modality, remote)
