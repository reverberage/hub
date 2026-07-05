"""Scaffold a new reverberage satellite package.

Usage: python scaffold-satellite.py <name>

Creates ../<name>/ with satellite boilerplate (pyproject.toml, CLI, tests).
Run from the hub repo root.
"""

import re
import sys
from pathlib import Path


def validate_name(name: str) -> str:
    if not re.match(r"^[a-z][a-z0-9_-]*$", name):
        print(
            f"Error: '{name}' is not a valid package name. "
            "Use lowercase letters, digits, hyphens, and underscores only."
        )
        sys.exit(1)
    return name


def scaffold(name: str) -> None:
    hub_root = Path(__file__).resolve().parent.parent.parent
    target = hub_root.parent / name

    if target.exists():
        print(f"Error: {target} already exists.")
        sys.exit(1)

    pkg_dir = target / "src" / name.replace("-", "_")

    # Create directories
    (target / "tests").mkdir(parents=True)

    # pyproject.toml
    (target / "pyproject.toml").write_text(f"""\
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
]

[project.optional-dependencies]
dev = [
    "pytest>=8",
    "ruff>=0.5",
    "mypy>=1.10",
    "mcp>=1.0",
]

[project.scripts]
rvrb-{name} = "rvrb_{name.replace("-", "_")}.cli:app"

[tool.ruff]
target-version = "py311"

[tool.mypy]
python_version = "3.11"
strict = true

[tool.pytest.ini_options]
testpaths = ["tests"]
""")

    # src/<pkg>/__init__.py
    (pkg_dir).mkdir(parents=True)
    (pkg_dir / "__init__.py").write_text("""\
__version__ = "0.1.0"
""")

    # src/<pkg>/cli.py
    (pkg_dir / "cli.py").write_text(f"""\
import typer

app = typer.Typer(
    name="rvrb-{name}",
    help="reverberage satellite: {name}",
)


@app.command()
def version() -> None:
    \"\"\"Print the package version.\"\"\"
    from rvrb_{name.replace("-", "_")} import __version__
    typer.echo(__version__)


if __name__ == "__main__":
    app()
""")

    # tests/__init__.py
    (target / "tests" / "__init__.py").write_text("")

    # tests/test_<name>.py
    (target / "tests" / f"test_{name.replace('-', '_')}.py").write_text(f"""\
from typer.testing import CliRunner
from rvrb_{name.replace("-", "_")}.cli import app

runner = CliRunner()


def test_version() -> None:
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "0.1.0" in result.output
""")

    # README.md
    (target / "README.md").write_text(f"""\
# rvrb-{name}

reverberage satellite: {name}

## Install

```bash
pip install -e ".[dev]"
```

## Usage

```bash
rvrb-{name} --help
```

## Develop

```bash
pip install -e ".[dev]"
pytest
```
""")

    print(f"Scaffolded {target}")
    print(f"  cd {name}")
    print('  pip install -e ".[dev]"')
    print("  pytest")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python scaffold-satellite.py <name>")
        sys.exit(1)
    scaffold(validate_name(sys.argv[1]))
