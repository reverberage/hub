# Architecture

Internal design of rvrb-verify. For users — no need to read this unless contributing or debugging.

## Module structure

```
src/rvrb_verify/
    __init__.py      # verify() function, public API
    cli.py           # Typer CLI entry point
    engine.py        # VerificationEngine (two-phase pipeline)
    models.py        # Verdict, Evidence, Source, MediaModality, MediaInput, MediaOutput
    provider.py      # ModelProvider Protocol, get_provider(), DEFAULT_MODEL
    tools.py         # ToolGateway, MockToolGateway
    mcp.py           # MCP server (FastMCP)
    strategies/      # Verification strategies
        __init__.py  # REGISTRY, list_strategies()
        fact_check.py
        legal.py
        research.py
```

## Data flow

```
CLI (cli.py)
  │
  ├── verify() function (__init__.py)
  │     │
  │     ├── Resolves strategy from REGISTRY
  │     ├── Resolves search_provider and judge_provider
  │     ├── Creates VerificationEngine
  │     └── Calls engine.verify()
  │           │
  │           ├── Search phase
  │           │     ├── Build search messages from strategy.search_prompt()
  │           │     ├── Call search_provider.complete_with_tools()
  │           │     ├── Execute tool calls via tool_gateway
  │           │     └── Collect evidence
  │           │
  │           ├── Judge phase
  │           │     ├── Build judge messages from strategy.judge_prompt()
  │           │     ├── Call judge_provider.complete_structured()
  │           │     └── Parse Verdict from structured output
  │           │
  │           └── Return Verdict
  │
  └── Output: text or JSON
```

## Key classes

### `Verdict` (models.py)

Pydantic v2 model. The core output type.

```python
class Verdict(BaseModel):
    verdict: VerdictValue
    confidence: float
    summary: str
    evidence: list[Evidence]
    sources: list[Source]
    model: str
    provider: str
    tokens_used: int | None
```

`VerdictValue` is an enum: `true`, `false`, `partially_true`, `inconclusive`.

### `VerificationEngine` (engine.py)

Two-phase verification pipeline.

```python
class VerificationEngine:
    def __init__(
        self,
        search_provider: ModelProvider,
        judge_provider: ModelProvider,
        tool_gateway: ToolGateway,
    ): ...
    
    def verify(self, claim: str, strategy: VerificationStrategy) -> Verdict:
        # Phase 1: Search for evidence
        # Phase 2: Judge claim based on evidence
        ...
```

**Phase 1 — Search:**
1. Build messages from `strategy.search_prompt(claim)`
2. Call `search_provider.complete_with_tools(messages, strategy.tools)`
3. Execute tool calls via `tool_gateway.execute()`
4. Collect evidence from tool responses

**Phase 2 — Judge:**
1. Build messages from `strategy.judge_prompt(claim, evidence)`
2. Call `judge_provider.complete_structured(messages, Verdict)`
3. Return parsed `Verdict`

### `ModelProvider` Protocol (provider.py)

Structural Protocol for LLM providers.

```python
class ModelProvider(Protocol):
    model: str
    base_url: str
    
    def complete(self, messages: list[dict], **kwargs) -> str: ...
    def complete_structured(self, messages: list[dict], output_type: type, **kwargs) -> BaseModel: ...
    def complete_with_tools(self, messages: list[dict], tools: list[dict], **kwargs) -> ToolResult: ...
```

### `ToolGateway` (tools.py)

Abstract interface for tool execution.

```python
class ToolGateway(Protocol):
    def execute(self, tool_name: str, arguments: dict) -> str: ...
```

`MockToolGateway` returns mock data for testing. Implement `RealToolGateway` for production use.

### `VerificationStrategy` (strategies/)

Base class for verification strategies.

```python
class VerificationStrategy:
    name: str
    description: str
    tools: list[ToolSpec]
    model_search: str
    model_judge: str
    
    def search_prompt(self, claim: str) -> list[dict]: ...
    def judge_prompt(self, claim: str, evidence: list) -> list[dict]: ...
```

Strategies are registered in `REGISTRY` and looked up by name.

## Two-phase pipeline

The verification uses a two-phase pipeline for accuracy:

**Phase 1 — Search:**
- Uses `complete_with_tools()` to search for evidence
- Tools: web search, news search, statute search, case law search, paper search, arXiv search
- Returns structured evidence with sources

**Phase 2 — Judge:**
- Uses `complete_structured()` to produce a `Verdict`
- Takes claim + evidence as input
- Returns verdict, confidence, summary

This separation allows different models for each phase (e.g., fast model for search, smart model for judge).

## Error handling

| Layer | Error type | Handling |
|-------|-----------|----------|
| CLI | `ValueError` | Exit 1, message to stderr |
| CLI | Other exceptions | Exit 2, message to stderr |
| Engine | Provider errors | Exception propagates to caller |
| Engine | Tool errors | Logged, search continues with available evidence |

## Dependencies

### Runtime

| Package | Purpose |
|---------|---------|
| `openai>=2.0.0` | OpenAI-compatible API client |
| `pydantic>=2.0` | Data models (Verdict, Evidence, Source) |
| `typer>=0.12` | CLI framework |

### Optional

| Package | Extra | Purpose |
|---------|-------|---------|
| `mcp` | `[mcp]` | MCP server (FastMCP) |

### No n3rverberage dependency

rvrb-verify does NOT require n3rverberage at runtime. The `provider.py` module follows the satellite-protocol-v2 pattern with a fallback provider.

## Protocol compliance

rvrb-verify follows [satellite-protocol-v2](https://github.com/reverberage/hub/blob/main/docs/satellite-protocol-v2.md):

- **Mandatory kernel**: `__init__.py`, `models.py`, `provider.py`, `engine.py` ✓
- **No `io.py`**: Text-only satellite, no file I/O ✓
- **CLI**: Typer-based with `--strategy`, `--json`, `--model`, `--provider`, `--output` ✓
- **MCP**: Gated import, `FastMCP`, stdio transport ✓
- **MockProvider**: In `tests/conftest.py` for offline testing ✓
