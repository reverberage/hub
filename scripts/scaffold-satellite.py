#!/usr/bin/env python3
"""Scaffold a new reverberage satellite package (protocol v2).

Usage: python scaffold-satellite.py <name> [output-dir]

Creates <output-dir>/<name>/ with mandatory kernel modules:
    __init__.py, models.py, provider.py, engine.py
Plus: cli.py, tests/, pyproject.toml, README.md

Satellite protocol v2: docs/satellite-protocol-v2.md
"""

import re
import sys
from pathlib import Path
from textwrap import dedent


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
    dependencies = [
        "typer>=0.12",
        "pydantic>=2",
        "openai>=1",
        "n3rverberage",
    ]

    [project.optional-dependencies]
    dev = [
        "pytest>=8",
        "ruff>=0.5",
        "mypy>=1.10",
        "mcp>=1.0",
    ]

    [project.scripts]
    rvrb-{name} = "{pkg}.cli:app"

    [tool.ruff]
    target-version = "py311"

    [tool.mypy]
    python_version = "3.11"
    strict = true

    [tool.pytest.ini_options]
    testpaths = ["tests"]
    """)


def _render_init(name: str, class_name: str, pkg: str) -> str:
    return dedent(f"""\
    \"\"\"reverberage satellite: {name}\"\"\"

    __version__ = "0.1.0"

    from {pkg}.engine import {class_name}Engine
    from {pkg}.models import MediaInput, MediaOutput, MediaModality

    __all__ = [
        "__version__",
        "{class_name}Engine",
        "MediaInput",
        "MediaOutput",
        "MediaModality",
    ]
    """)


def _render_models() -> str:
    return dedent("""\
    from enum import StrEnum
    from pathlib import Path

    from pydantic import BaseModel


    class MediaModality(StrEnum):
        \"\"\"Media modality enum — every satellite must define this.\"\"\"
        TEXT = "text"
        AUDIO = "audio"
        IMAGE = "image"
        VIDEO = "video"


    class MediaInput(BaseModel):
        \"\"\"Standard media input wrapper. Carries provenance through pipelines.\"\"\"
        path: Path | None = None
        modality: MediaModality = MediaModality.TEXT
        metadata: dict = {}
        # metadata examples: duration_seconds, width, height, language, sample_rate


    class MediaOutput(BaseModel):
        \"\"\"Standard media output wrapper.\"\"\"
        data: str | bytes
        modality: MediaModality = MediaModality.TEXT
        format: str = "text"  # json, srt, vtt, wav, mp3, png, mp4, etc.
    """)


def _render_provider() -> str:
    return dedent("""\
    import os
    from typing import Protocol

    from pydantic import BaseModel


    class ModelProvider(Protocol):
        \"\"\"Structural protocol — any object with these attributes is a valid provider.
        No ABC inheritance required. Duck-typing: if it quacks, it works.
        \"\"\"
        model: str
        base_url: str

        def complete(self, messages: list[dict], **kwargs) -> str: ...
        def complete_structured(self, messages: list[dict], output_type: type, **kwargs) -> object: ...
        def complete_with_tools(self, messages: list[dict], tools: list[dict], **kwargs) -> object: ...


    # Env-var-driven defaults with Qwen fallback for backward compatibility
    DEFAULT_MODEL: str = os.environ.get(
        "N3RVERBERAGE_DEFAULT_MODEL",
        "qwen3-coder-plus",
    )
    DEFAULT_BASE_URL: str = os.environ.get(
        "N3RVERBERAGE_DEFAULT_BASE_URL",
        "https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
    )

    # Provider fallback map: provider_type → (default_model, default_url, api_key_env_var)
    _PROVIDER_FALLBACKS: dict[str, tuple[str, str, str]] = {
        "qwen": (
            "qwen3-coder-plus",
            "https://dashscope-intl.aliyuncs.com/compatible-mode/v1",
            "DASHSCOPE_API_KEY",
        ),
        "openai": (
            "gpt-4",
            "https://api.openai.com/v1",
            "OPENAI_API_KEY",
        ),
        "local": (
            "qwen2.5",
            "http://127.0.0.1:11434/v1",
            "",
        ),
    }


    class _GenericProvider:
        \"\"\"Generic OpenAI-compatible fallback provider.

        Works with any OpenAI-compatible endpoint (Qwen/DashScope,
        OpenAI, Ollama, vLLM, etc.).  No provider-specific error
        handling — all API errors are wrapped as generic exceptions.
        \"\"\"

        def __init__(self, *, model: str, base_url: str, api_key: str) -> None:
            self.model = model
            self.base_url = base_url
            self._api_key = api_key

        def _client(self):
            from openai import OpenAI
            return OpenAI(api_key=self._api_key, base_url=self.base_url, timeout=60.0)

        def complete(self, messages: list[dict], **kwargs) -> str:
            max_tokens = kwargs.pop("max_tokens", 4096)
            try:
                response = self._client().chat.completions.create(
                    model=self.model, messages=messages, max_tokens=max_tokens, **kwargs,
                )
            except Exception as exc:
                status_code = getattr(exc, "status_code", 500) or 500
                raise RuntimeError(f"[{self.model}] HTTP {status_code}: {{exc}}") from exc
            return response.choices[0].message.content or ""

        def complete_structured(self, messages: list[dict], output_type: type, **kwargs) -> object:
            import json
            schema = output_type.model_json_schema()
            max_tokens = kwargs.pop("max_tokens", 4096)
            try:
                response = self._client().chat.completions.create(
                    model=self.model, messages=messages, max_tokens=max_tokens,
                    response_format={"type": "json_schema", "json_schema": {"name": output_type.__name__, "schema": schema, "strict": True}},
                )
            except Exception as exc:
                status_code = getattr(exc, "status_code", 500) or 500
                raise RuntimeError(f"[{self.model}] HTTP {status_code}: {{exc}}") from exc
            raw = response.choices[0].message.content
            if not raw:
                raise RuntimeError(f"[{{self.model}}] Empty structured response")
            try:
                return output_type.model_validate(json.loads(raw))
            except Exception as exc:
                raise RuntimeError(f"[{{self.model}}] Validation failed: {{exc}}") from exc

        def complete_with_tools(self, messages: list[dict], tools: list[dict], **kwargs) -> object:
            max_tokens = kwargs.pop("max_tokens", 4096)
            try:
                response = self._client().chat.completions.create(
                    model=self.model, messages=messages, tools=tools, tool_choice="auto", max_tokens=max_tokens, **kwargs,
                )
            except Exception as exc:
                status_code = getattr(exc, "status_code", 500) or 500
                raise RuntimeError(f"[{self.model}] HTTP {status_code}: {{exc}}") from exc
            return response.choices[0].message


    def get_provider(
        model: str | None = None,
        provider: str | None = None,
    ) -> ModelProvider:
        \"\"\"Resolve provider: n3rverberage if available, generic fallback otherwise.

        Parameters
        ----------
        model : str | None
            Override model ID.  Defaults to DEFAULT_MODEL.
        provider : str | None
            Provider name (qwen, openai, local).  Overrides
            ``N3RVERBERAGE_PROVIDER`` env var.
        \"\"\"
        resolved_model = model or DEFAULT_MODEL
        resolved_provider = provider or os.environ.get("N3RVERBERAGE_PROVIDER") or "qwen"

        try:
            from n3rverberage.providers import get_provider as n3rv_get_provider
            return n3rv_get_provider(name=f"{{resolved_provider}}:{{resolved_model}}")
        except ImportError:
            pass

        # Fallback: generic OpenAI-compatible provider
        provider_type = resolved_provider.strip().lower()
        if provider_type not in _PROVIDER_FALLBACKS:
            raise ValueError(f"Unknown provider: '{{provider_type}}'. Supported: {{', '.join(_PROVIDER_FALLBACKS)}}")

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
    from {pkg}.models import MediaInput, MediaOutput, MediaModality
    from {pkg}.provider import ModelProvider


    class {class_name}Engine:
        \"\"\"{name} engine — constructor-injected provider, mock-ready.

        Implements the satellite protocol v2 engine contract.
        \"\"\"

        def __init__(self, provider: ModelProvider):
            self.provider = provider

        def process(self, input_data: MediaInput | str, **options) -> MediaOutput:
            \"\"\"Main processing method. Replace with satellite-specific logic.\"\"\"
            if isinstance(input_data, str):
                input_data = MediaInput(modality=MediaModality.TEXT, metadata={{"text": input_data}})

            messages = [
                {{
                    "role": "system",
                    "content": f"You are the {class_name} engine. Process the input."
                }},
                {{
                    "role": "user",
                    "content": str(input_data.metadata.get("text", str(input_data.path or "")))
                }},
            ]

            result = self.provider.complete(messages)
            return MediaOutput(data=result, modality=MediaModality.TEXT, format="text")
    """)


def _render_cli(name: str, class_name: str, pkg: str) -> str:
    return dedent(f"""\
    import typer
    from pathlib import Path

    from {pkg} import __version__
    from {pkg}.engine import {class_name}Engine
    from {pkg}.provider import get_provider

    app = typer.Typer(
        name="rvrb-{name}",
        help="reverberage satellite: {name}",
    )


    @app.command()
    def version() -> None:
        \"\"\"Print the package version.\"\"\"
        typer.echo(__version__)


    @app.command()
    def main(
        input_path: Path = typer.Argument(..., help="Input file (use '-' for stdin)"),
        output: Path | None = typer.Option(
            None, "--output", "-o", help="Write output to file (default: stdout)"
        ),
        json: bool = typer.Option(
            False, "--json", help="Output as JSON"
        ),
        model: str | None = typer.Option(
            None, "--model", "-m", help="Override model ID (e.g., qwen3-coder-plus)"
        ),
        provider: str | None = typer.Option(
            None, "--provider",
            help="Provider name: qwen, openai, local.  Overrides N3RVERBERAGE_PROVIDER.",
        ),
    ) -> None:
        \"\"\"Process input and produce output.\"\"\"
        try:
            from {pkg}.models import MediaInput

            media_input = MediaInput(path=input_path)
            engine = {class_name}Engine(get_provider(model=model, provider=provider))
            result = engine.process(media_input)

            if json:
                typer.echo(result.model_dump_json(indent=2))
            elif output:
                output.write_text(result.data if isinstance(result.data, str) else result.data.decode())
            else:
                typer.echo(result.data)
        except Exception as e:
            typer.echo(f"Error: {{e}}", err=True)
            raise typer.Exit(code=1)


    if __name__ == "__main__":
        app()
    """)


def _render_conftest(pkg: str) -> str:
    return dedent("""\
    from __future__ import annotations

    from typing import Any

    from pydantic import BaseModel


    class MockProvider:
        \"\"\"Structural mock provider — no inheritance, just matches ModelProvider protocol.

        Use in engine tests to avoid real API calls.  Returns canned responses
        for all three completion methods.
        \"\"\"

        def __init__(self, model: str = "mock-model", base_url: str = "mock://"):
            self.model = model
            self.base_url = base_url

        def complete(self, messages: list[dict], **kwargs: Any) -> str:
            return "mock completion response"

        def complete_structured(
            self,
            messages: list[dict],
            output_type: type[BaseModel],
            **kwargs: Any,
        ) -> BaseModel:
            return output_type.model_validate({})

        def complete_with_tools(
            self,
            messages: list[dict],
            tools: list[dict],
            **kwargs: Any,
        ) -> object:
            from types import SimpleNamespace
            return SimpleNamespace(content="mock tool result", tool_calls=[])
    """)


def _render_test(name: str, pkg: str) -> str:
    return dedent(f"""\
    from typer.testing import CliRunner
    from {pkg}.cli import app
    from {pkg}.engine import {_class_name(name)}Engine
    from tests.conftest import MockProvider

    runner = CliRunner()


    def test_version() -> None:
        \"\"\"CLI version command prints the package version.\"\"\"
        result = runner.invoke(app, ["version"])
        assert result.exit_code == 0
        assert "0.1.0" in result.output


    def test_help() -> None:
        \"\"\"CLI --help shows usage.\"\"\"
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "Usage" in result.output or "Usage" in result.stderr


    def test_engine_with_mock_provider() -> None:
        \"\"\"Engine works with MockProvider — zero network calls.\"\"\"
        engine = {_class_name(name)}Engine(provider=MockProvider())
        result = engine.process("test input")
        assert result is not None
        assert "mock completion" in result.data
    """)


def _render_readme(name: str) -> str:
    return dedent(f"""\
    # rvrb-{name}

    reverberage satellite: {name}

    ## Install

    ```bash
    pip install -e ".[dev]"
    ```

    ## Usage

    ```bash
    rvrb-{name} --help
    rvrb-{name} version
    ```

    ## Develop

    ```bash
    pip install -e ".[dev]"
    pytest
    ```

    ## Satellite Protocol

    This satellite follows [satellite protocol v2](https://github.com/reverberage/hub/blob/main/docs/satellite-protocol-v2.md).

    For non-text modalities (audio, image, video), add an `io.py` module with
    `read_media()` and `write_media()` functions.
    """)


def scaffold(name: str, output_dir: Path | None = None) -> None:
    """Scaffold a new satellite package."""
    if output_dir is not None:
        target = Path(output_dir) / name
    else:
        hub_root = Path(__file__).resolve().parent.parent
        target = hub_root.parent / name

    if target.exists():
        print(f"Error: {target} already exists.")
        sys.exit(1)

    pkg = _pkg_name(name)
    class_name = _class_name(name)
    pkg_dir = target / "src" / pkg

    # Create directories
    (target / "tests").mkdir(parents=True)
    pkg_dir.mkdir(parents=True)

    # Write files
    (target / "pyproject.toml").write_text(_render_pyproject(name, pkg))
    (target / "README.md").write_text(_render_readme(name))
    (target / "tests" / "__init__.py").write_text("")
    (target / "tests" / "conftest.py").write_text(_render_conftest(pkg))
    (target / "tests" / f"test_{pkg}.py").write_text(_render_test(name, pkg))

    (pkg_dir / "__init__.py").write_text(_render_init(name, class_name, pkg))
    (pkg_dir / "models.py").write_text(_render_models())
    (pkg_dir / "provider.py").write_text(_render_provider())
    (pkg_dir / "engine.py").write_text(_render_engine(name, class_name, pkg))
    (pkg_dir / "cli.py").write_text(_render_cli(name, class_name, pkg))

    print(f"Scaffolded {target}")
    print(f"  cd {name}")
    print('  pip install -e ".[dev]"')
    print("  pytest")


if __name__ == "__main__":
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("Usage: python scaffold-satellite.py <name> [output-dir]")
        sys.exit(1)

    name = validate_name(sys.argv[1])
    output_dir = Path(sys.argv[2]) if len(sys.argv) == 3 else None
    scaffold(name, output_dir)
