# Development

Contributing to rvrb-see.

## Setup

```bash
# Clone the repository
git clone https://github.com/reverberage/rvrb-see.git
cd rvrb-see

# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install with dev dependencies
pip install -e ".[dev]"
```

## Commands

| Command | Purpose |
|---------|---------|
| `pytest` | Run tests |
| `ruff check .` | Lint code |
| `ruff format .` | Format code |
| `mypy .` | Type check |
| `ruff check . && ruff format --check . && mypy . && pytest` | Full quality gate |

## Testing

### Running tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=rvrb_see

# Run offline (no network)
pytest --offline

# Run specific test file
pytest tests/test_engine.py
```

### MockProvider

Tests use `MockProvider` from `tests/conftest.py`:

```python
from tests.conftest import MockProvider

provider = MockProvider()
engine = SeeEngine(provider=provider)
result = engine.see("image.png")
```

### SpyProvider

For testing message construction:

```python
class SpyProvider:
    def __init__(self):
        self.captured_messages = None
        self.captured_kwargs = {}
    
    def complete(self, messages, **kwargs):
        self.captured_messages = messages
        self.captured_kwargs = kwargs
        return "mock description"
    
    def complete_structured(self, messages, output_type, **kwargs):
        return output_type(...)
    
    def complete_with_tools(self, messages, tools, **kwargs):
        return ToolResult(...)

# Test that temperature=0 is set
spy = SpyProvider()
engine = SeeEngine(provider=spy)
engine.see("image.png")

assert spy.captured_kwargs.get("temperature") == 0
```

## Project structure

```
rvrb-see/
├── src/
│   └── rvrb_see/
│       ├── __init__.py      # Public API
│       ├── cli.py           # CLI
│       ├── engine.py        # SeeEngine
│       ├── models.py        # Data models
│       ├── provider.py      # Provider resolution
│       ├── io.py            # Image I/O
│       └── mcp.py           # MCP server
├── tests/
│   ├── conftest.py          # MockProvider, fixtures
│   ├── test_engine.py       # Engine tests
│   ├── test_cli.py          # CLI tests
│   ├── test_models.py       # Model tests
│   ├── test_provider.py     # Provider tests
│   └── test_io.py           # I/O tests
├── pyproject.toml           # Build config
└── README.md                # Package docs
```

## Code style

- Follow PEP 8
- Use type hints for all function signatures
- Write docstrings for all public functions and classes
- Keep functions focused and small
- Write tests for new functionality
- Use conventional commits: `type(scope): description`

## Adding image formats

To add support for a new image format:

1. Add to `MIME_MAP` in `io.py`:

```python
MIME_MAP = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    # ...
    ".bmp": "image/bmp",  # Add here
}
```

2. Add test in `tests/test_io.py`:

```python
def test_read_media_bmp(tmp_path):
    image_file = tmp_path / "test.bmp"
    image_file.write_bytes(b"fake image data")
    
    mi = read_media(image_file)
    assert mi.modality == MediaModality.IMAGE
    assert "image/bmp" in mi.metadata["mime_type"]
```

## License

Apache-2.0 — same as the reverberage ecosystem.
