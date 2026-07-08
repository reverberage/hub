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


    class ModelProvider(Protocol):
        \"\"\"Structural protocol — any object with these attributes is a valid provider.
        No ABC inheritance required. Duck-typing: if it quacks, it works.
        \"\"\"
        model: str
        base_url: str

        def complete(self, messages: list[dict], **kwargs) -> str: ...
        def complete_structured(self, messages: list[dict], output_type: type, **kwargs) -> object: ...
        def complete_with_tools(self, messages: list[dict], tools: list[dict], **kwargs) -> object: ...


    DEFAULT_MODEL = "qwen3-coder-plus"
    DEFAULT_BASE_URL = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"


    class _DefaultProvider:
        \"\"\"Inline OpenAI fallback when n3rverberage is not installed.\"\"\"

        def __init__(self, model: str | None = None):
            self.model = model or DEFAULT_MODEL
            self.base_url = DEFAULT_BASE_URL

        def complete(self, messages: list[dict], **kwargs) -> str:
            return self._chat(messages, **kwargs)

        def complete_structured(self, messages: list[dict], output_type: type, **kwargs) -> object:
            return self._chat(messages, response_format=output_type, **kwargs)

        def complete_with_tools(self, messages: list[dict], tools: list[dict], **kwargs) -> object:
            return self._chat(messages, tools=tools, **kwargs)

        def _chat(self, messages, **kwargs):
            from openai import OpenAI
            client = OpenAI(
                api_key=os.environ.get("DASHSCOPE_API_KEY", ""),
                base_url=self.base_url,
            )
            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                **kwargs,
            )
            return response.choices[0].message.content or ""


    def get_provider(model_override: str | None = None) -> ModelProvider:
        \"\"\"Resolve provider: n3rverberage if available, inline OpenAI fallback otherwise.\"\"\"
        try:
            from n3rverberage.providers import get_provider as n3rv_get_provider  # type: ignore
            provider = n3rv_get_provider(model_override)
            return provider
        except ImportError:
            return _DefaultProvider(model=model_override)
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
            None, "--model", "-m", help="Override model (e.g., qwen:qwen3-coder-plus)"
        ),
    ) -> None:
        \"\"\"Process input and produce output.\"\"\"
        try:
            from {pkg}.models import MediaInput

            media_input = MediaInput(path=input_path)
            provider = get_provider(model)
            engine = {class_name}Engine(provider)
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


def _render_test(name: str, pkg: str) -> str:
    return dedent(f"""\
    from typer.testing import CliRunner
    from {pkg}.cli import app

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
