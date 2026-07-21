# Development

Contributing to rvrb-transcriber.

## Setup

```bash
git clone https://github.com/reverberage/rvrb-transcriber.git
cd rvrb-transcriber
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Run tests

```bash
# All tests (mocked, no network needed)
pytest

# With coverage
pytest --cov=rvrb_transcriber

# Verbose
pytest -v
```

## Linting

```bash
# Check
ruff check .

# Fix
ruff check --fix .

# Format check
ruff format --check .

# Format
ruff format .
```

## Type checking

```bash
mypy .
```

## Project structure

```
rvrb-transcriber/
├── src/rvrb_transcriber/
│   ├── __init__.py      # Public API, transcribe()
│   ├── cli.py           # Typer CLI
│   ├── engine.py        # OpenAI + Local Whisper engines
│   ├── models.py        # Transcript, Segment (Pydantic v2)
│   ├── provider.py      # ModelProvider Protocol (future)
│   └── mcp.py           # MCP server
├── tests/
│   ├── conftest.py      # MockProvider
│   ├── test_models.py   # Model tests
│   ├── test_engine.py   # Engine tests (mocked API)
│   ├── test_provider.py # Provider tests
│   └── test_transcriber.py  # Integration tests
├── pyproject.toml       # hatchling build
└── README.md
```

## Build

```bash
# Build wheel
python -m build

# Install locally
pip install -e ".[all]"

# Publish to PyPI
twine upload dist/*
```

## Commit conventions

Use conventional commits:

```
feat(engine): add support for batch transcription
fix(cli): handle missing file gracefully
docs(readme): update installation instructions
test(engine): add mock tests for local whisper
chore(deps): update pydantic to 2.10
```

## Adding a new engine

1. Create class inheriting from `TranscriptionEngine` in `engine.py`
2. Implement `transcribe(file_path, language) -> Transcript`
3. Add engine selection in `__init__.py` `transcribe()` function
4. Add CLI flag in `cli.py`
5. Add tests in `test_engine.py`
6. Update this wiki page

## Adding a new output format

1. Add method to `Transcript` class in `models.py`
2. Add format flag in `cli.py`
3. Add MCP tool variant in `mcp.py`
4. Add tests in `test_models.py`
5. Update [Output Formats](Output-Formats) wiki

## Release process

1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md` (if exists)
3. Create git tag: `git tag v0.2.0`
4. Push: `git push origin main --tags`
5. Build: `python -m build`
6. Publish: `twine upload dist/*`
