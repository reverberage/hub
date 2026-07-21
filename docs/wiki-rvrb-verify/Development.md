# Development

Contributing to rvrb-verify.

## Setup

```bash
# Clone the repository
git clone https://github.com/reverberage/rvrb-verify.git
cd rvrb-verify

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate  # Windows

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
pytest --cov=rvrb_verify

# Run specific test file
pytest tests/test_engine.py

# Run offline (no network)
pytest --offline
```

### MockProvider

Tests use `MockProvider` from `tests/conftest.py` to avoid network calls:

```python
from tests.conftest import MockProvider

provider = MockProvider()
engine = VerificationEngine(
    search_provider=provider,
    judge_provider=provider,
    tool_gateway=MockToolGateway(),
)
verdict = engine.verify("Claim", strategy="fact-check")
```

### MockToolGateway

`MockToolGateway` returns mock tool responses for testing:

```python
from rvrb_verify.tools import MockToolGateway

gateway = MockToolGateway()
result = gateway.execute("web_search", {"query": "test"})
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
        return "mock response"
    
    def complete_structured(self, messages, output_type, **kwargs):
        self.captured_messages = messages
        return output_type(...)
    
    def complete_with_tools(self, messages, tools, **kwargs):
        self.captured_messages = messages
        return ToolResult(...)
```

## Adding a new strategy

1. Create `src/rvrb_verify/strategies/my_strategy.py`:

```python
from .base import VerificationStrategy, ToolSpec

class MyStrategy(VerificationStrategy):
    name = "my-strategy"
    description = "Custom verification strategy"
    
    tools = [
        ToolSpec(name="my_search", description="Search my database"),
    ]
    
    model_search = "qwen3-coder-plus"
    model_judge = "qwen3.7-plus"
    
    def search_prompt(self, claim: str) -> list[dict]:
        return [
            {"role": "system", "content": "Search for evidence..."},
            {"role": "user", "content": claim},
        ]
    
    def judge_prompt(self, claim: str, evidence: list) -> list[dict]:
        return [
            {"role": "system", "content": "Judge the claim..."},
            {"role": "user", "content": f"Claim: {claim}\nEvidence: {evidence}"},
        ]
```

2. Register in `src/rvrb_verify/strategies/__init__.py`:

```python
from .my_strategy import MyStrategy

REGISTRY.register(MyStrategy())
```

3. Add tests in `tests/test_strategies.py`:

```python
def test_my_strategy():
    verdict = verify("Claim", strategy="my-strategy")
    assert verdict.verdict in ("true", "false", "partially_true", "inconclusive")
```

## Project structure

```
rvrb-verify/
├── src/
│   └── rvrb_verify/
│       ├── __init__.py      # Public API
│       ├── cli.py           # CLI
│       ├── engine.py        # VerificationEngine
│       ├── models.py        # Data models
│       ├── provider.py      # Provider resolution
│       ├── tools.py         # Tool gateways
│       ├── mcp.py           # MCP server
│       └── strategies/      # Verification strategies
├── tests/
│   ├── conftest.py          # MockProvider, fixtures
│   ├── test_engine.py       # Engine tests
│   ├── test_cli.py          # CLI tests
│   ├── test_models.py       # Model tests
│   ├── test_provider.py     # Provider tests
│   └── test_strategies.py   # Strategy tests
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

## License

Apache-2.0 — same as the reverberage ecosystem.
