# SDD Design: rvrb-verify

**Change ID**: `rvrb-verify` | **Approach**: B (Two-Phase Pipeline + Strategy Protocol) | **Date**: 2026-07-07

## 1. Component Architecture

```
src/rvrb_verify/
├── __init__.py         ← Re-exports: verify(), Verdict, Source, Evidence, VerificationError, list_strategies
├── cli.py              ← Typer app: rvrb-verify "text" [--strategy] [--json] [--model] [--search-model] [--judge-model]
├── models.py           ← Claim, Source, Evidence, Verdict, VerdictEnum (pydantic v2)
├── engine.py           ← VerificationEngine (two-phase pipeline), VerificationError
├── tools.py            ← ToolGateway Protocol, MockToolGateway
├── mcp.py              ← FastMCP server: verify_claim, list_strategies
└── strategies/
    ├── __init__.py     ← REGISTRY dict, list_strategies()
    ├── base.py         ← VerificationStrategy Protocol
    ├── fact_check.py   ← FactCheckStrategy
    ├── legal.py        ← LegalReviewStrategy
    └── research.py     ← ResearchValidationStrategy
tests/
├── __init__.py
├── conftest.py         ← mock_provider fixture (MagicMock-returning ModelProvider)
├── test_models.py      ← Pure Pydantic model tests (no fixtures)
├── test_engine.py      ← Engine tests with mocked provider
├── test_cli.py         ← CliRunner tests
├── test_strategies.py  ← Strategy conformance tests
└── test_mcp.py         ← FastMCP test client
pyproject.toml           ← hatchling, rvrb-verify, dep on rvrb-providers>=0.1.0
```

**13 modules, 8 internal, ~1200 lines total.**

| Module | Responsibility |
|--------|---------------|
| `__init__.py` | Re-exports: `verify`, `Verdict`, `Source`, `Evidence`, `VerificationError`, `list_strategies`. Convenience `verify(claim_text, ...)` function. |
| `cli.py` | Typer app with single `verify` command. Flags: `--strategy`, `--json`, `--model`, `--search-model`, `--judge-model`. |
| `models.py` | `Claim`, `Source`, `Evidence`, `Verdict` Pydantic models. `VerdictEnum`. |
| `engine.py` | `VerificationEngine` — two-phase pipeline. `VerificationError(RuntimeError)`. |
| `tools.py` | `ToolGateway` Protocol (execute). `MockToolGateway` returns placeholder strings. |
| `mcp.py` | `FastMCP` server: tool `verify_claim`, tool `list_strategies`. Entry: `rvrb-verify-mcp`. |
| `strategies/base.py` | `VerificationStrategy` Protocol: 7 attributes (name, system_prompt_search, system_prompt_judge, tool_definitions, verdict_schema, thinking_config, model_search, model_judge). |
| `strategies/fact_check.py` | Fact-checking strategy. |
| `strategies/legal.py` | Legal review strategy. |
| `strategies/research.py` | Research validation strategy. |
| `strategies/__init__.py` | `REGISTRY: dict[str, VerificationStrategy]` with 3 entries. `list_strategies() -> list[str]`. |

## 2. Data Structures

### 2.1 Models (`models.py`)

```python
from __future__ import annotations

from datetime import datetime, timezone
from enum import StrEnum

from pydantic import BaseModel, Field, field_validator


class VerdictEnum(StrEnum):
    TRUE = "true"
    FALSE = "false"
    UNCERTAIN = "uncertain"
    OPINION = "opinion"
    UNVERIFIABLE = "unverifiable"


class Claim(BaseModel):
    """A claim to be verified."""

    text: str = Field(..., min_length=1, description="The claim text")
    domain: str = Field(default="fact-check", description="Verification domain")

    @field_validator("text")
    @classmethod
    def text_must_not_be_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Claim text cannot be empty")
        return v


class Source(BaseModel):
    """A source used as evidence for a claim."""

    title: str = Field(default="", description="Source title")
    url: str = Field(default="", description="Source URL")
    snippet: str = Field(default="", description="Relevant excerpt")
    retrieved_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="When this source was retrieved",
    )


class Evidence(BaseModel):
    """Evidence for or against a claim."""

    supports: bool = Field(default=True, description="Does this support the claim?")
    reasoning: str = Field(default="", description="Why this evidence is relevant")
    sources: list[Source] = Field(default_factory=list, description="Supporting sources")


class Verdict(BaseModel):
    """Final verdict on a claim."""

    claim: str = Field(..., description="The original claim text")
    verdict: VerdictEnum = Field(..., description="The verdict")
    confidence: float = Field(
        ..., ge=0.0, le=1.0, description="Confidence in the verdict (0.0-1.0)"
    )
    evidence: list[Evidence] = Field(
        default_factory=list, description="Evidence supporting the verdict"
    )
    summary: str = Field(default="", description="Human-readable explanation")
    model_used: str = Field(default="", description="Model used for judgment")
```

### 2.2 Strategy Protocol (`strategies/base.py`)

```python
from __future__ import annotations

from typing import Protocol, runtime_checkable

from pydantic import BaseModel


@runtime_checkable
class VerificationStrategy(Protocol):
    """A domain-specific verification strategy.

    Each strategy carries all configuration for one domain:
    prompts, tool definitions, verdict schema, thinking config,
    and per-phase model selection.
    """

    name: str
    system_prompt_search: str
    system_prompt_judge: str
    tool_definitions: list[dict]
    verdict_schema: type[BaseModel]  # BaseModel subclass (typically Verdict)
    thinking_config: dict  # {"search": dict, "judge": dict} — extra_body
    model_search: str | None  # None = provider default
    model_judge: str | None   # None = provider default
```

### 2.3 Engine Errors (`engine.py`)

```python
class VerificationError(RuntimeError):
    """Error during the verification pipeline."""

    def __init__(self, phase: str, message: str, model_id: str | None = None) -> None:
        self.phase = phase  # "search" or "judge"
        self.model_id = model_id
        super().__init__(f"[{phase}] {message}")
```

### 2.4 ToolGateway Protocol (`tools.py`)

```python
from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class ToolGateway(Protocol):
    """Interface for executing tool calls."""

    def execute(self, tool_name: str, arguments: dict) -> str:
        """Execute a tool call and return the result as text."""
        ...


class MockToolGateway:
    """Tool gateway that returns placeholder responses.

    Always returns ``"[mock] no real search configured: {name}({args})"``.
    Zero network I/O.
    """

    def execute(self, tool_name: str, arguments: dict) -> str:
        args_fmt = ", ".join(f"{k}={v!r}" for k, v in arguments.items())
        return f"[mock] no real search configured: {tool_name}({args_fmt})"
```

### 2.5 Registry (`strategies/__init__.py`)

```python
from rvrb_verify.strategies.base import VerificationStrategy
from rvrb_verify.strategies.fact_check import fact_check_strategy
from rvrb_verify.strategies.legal import legal_strategy
from rvrb_verify.strategies.research import research_strategy

REGISTRY: dict[str, VerificationStrategy] = {
    "fact-check": fact_check_strategy,
    "legal": legal_strategy,
    "research": research_strategy,
}


def list_strategies() -> list[str]:
    return sorted(REGISTRY.keys())
```

## 3. Interface Specifications

### 3.1 Engine (`engine.py`)

```python
class VerificationEngine:
    """Two-phase verification pipeline.

    Phase 1 (SEARCH): ``search_provider.complete_with_tools()`` → 
    ``tool_gateway.execute()`` on each tool call → build tool context.

    Phase 2 (JUDGE): ``judge_provider.complete_structured()`` with 
    combined (user messages + tool context + system prompt) → ``Verdict``.

    Both phases use the same model by default. Per-phase model selection
    is configured via the strategy's ``model_search`` / ``model_judge`` fields.
    """

    def __init__(
        self,
        *,
        search_provider: ModelProvider,
        judge_provider: ModelProvider,
        tool_gateway: ToolGateway | None = None,
    ) -> None:
        """Search/judge providers injected at construction.

        If ``tool_gateway`` is None, uses ``MockToolGateway``.
        Typically constructed via ``verify()`` factory function.
        """

    def verify(
        self,
        claim: str,
        strategy: VerificationStrategy | None = None,
        *,
        model: str | None = None,
        search_model: str | None = None,
        judge_model: str | None = None,
    ) -> Verdict:
        ...
```

### 3.2 Data Flow — `engine.verify()`

```
verify("The sky is blue")
  │ strategy="fact-check" (default)
  │
  ▼
Phase 1 — SEARCH
  │ Messages = [
  │   {"role": "system", "content": strategy.system_prompt_search},
  │   {"role": "user", "content": "Claim: The sky is blue"},
  │ ]
  │ search_provider.complete_with_tools(
  │   messages,
  │   tools=fact_check_strategy.tool_definitions,
  │   extra_body=fact_check_strategy.thinking_config.get("search"),
  │ )
  │   ├── 200 OK with tool_calls
  │   │   ▼
  │   │ tool_gateway.execute(tool.name, tool.arguments) for each call
  │   │   → tool_context = "Result 1: ...\nResult 2: ..."
  │   │
  │   └── 200 OK with no tool_calls (model chose not to search)
  │       → tool_context = ""
  │
  ▼
Phase 2 — JUDGE
  │ Messages = [
  │   {"role": "system", "content": strategy.system_prompt_judge},
  │   {"role": "user", "content": f"Claim: The sky is blue\n\nEvidence:\n{tool_context}"},
  │ ]
  │ judge_provider.complete_structured(
  │   messages,
  │   output_type=Verdict,
  │   extra_body=strategy.thinking_config.get("judge"),
  │ )
  │   → Verdict(verdict="true", confidence=0.95, ...)
  │
  ▼
Return Verdict
```

### 3.3 Factory — `verify()` convenience function

```python
def verify(
    claim_text: str,
    strategy: str = "fact-check",
    *,
    model: str | None = None,
    search_model: str | None = None,
    judge_model: str | None = None,
    search_provider: str | None = None,
    judge_provider: str | None = None,
    tool_gateway: ToolGateway | None = None,
) -> Verdict:
    """Verify a claim using the given strategy.

    Parameters
    ----------
    claim_text : str
    strategy : str
        Name from ``list_strategies()``.
    model : str | None
        Override model for both phases. Format: ``"qwen:model-id"``.
    search_model : str | None
        Override only the search phase model.
    judge_model : str | None
        Override only the judge phase model.
    search_provider : str | None
        Provider name for search phase. Default: ``"qwen:qwen3-coder-plus"``.
    judge_provider : str | None
        Provider name for judge phase. Default: ``"qwen:qwen3.7-plus"``.
    tool_gateway : ToolGateway | None
        Tool executor. Default: ``MockToolGateway()``.

    Returns
    -------
    Verdict
    """
```

### 3.4 CLI Contract (`cli.py`)

```
usage: rvrb-verify [OPTIONS] CLAIM_TEXT

Verify a claim using LLM-powered analysis.

Arguments:
  CLAIM_TEXT  The claim to verify  [required]

Options:
  --strategy TEXT      Verification strategy (fact-check, legal, research)
                       [default: fact-check]
  --json               Output as JSON  [default: False]
  --model TEXT         Override model for both phases (e.g., qwen:qwen3.7-plus)
  --search-model TEXT  Override model for search phase only
  --judge-model TEXT   Override model for judge phase only
  --help               Show this message and exit

Exit: 0 on success, 1 on error.
```

### 3.5 MCP Server (`mcp.py`)

```python
"""MCP server for claim verification."""

import mcp.server.stdio
import mcp.types as types
from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions

server = Server("rvrb-verify")


@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="verify_claim",
            description="Verify a claim using LLM-powered analysis",
            inputSchema={
                "type": "object",
                "properties": {
                    "claim_text": {"type": "string", "description": "The claim to verify"},
                    "strategy": {
                        "type": "string",
                        "enum": list_strategies(),
                        "default": "fact-check",
                        "description": "Verification strategy",
                    },
                },
                "required": ["claim_text"],
            },
        ),
        types.Tool(
            name="list_strategies",
            description="List available verification strategies",
            inputSchema={
                "type": "object",
                "properties": {},
            },
        ),
    ]


@server.call_tool()
async def handle_call_tool(
    name: str, arguments: dict | None
) -> list[types.TextContent]:
    ...


def main() -> None:
    """Entry point for ``rvrb-verify-mcp``."""
    ...
```

### 3.6 Strategy Implementations

Each strategy defines 7 Protocol attributes:

| Attribute | Type | Fact Check | Legal | Research |
|-----------|------|------------|-------|----------|
| `name` | `str` | `"fact-check"` | `"legal"` | `"research"` |
| `system_prompt_search` | `str` | "You are a fact-checker..." | "You are a legal analyst..." | "You are a research validator..." |
| `system_prompt_judge` | `str` | "Evaluate the claim against evidence..." | "Evaluate legal claim..." | "Evaluate research claim..." |
| `tool_definitions` | `list[dict]` | `search_web`, `search_news` | `search_statutes`, `search_case_law` | `search_papers`, `search_arxiv` |
| `verdict_schema` | `type[BaseModel]` | `Verdict` | `Verdict` | `Verdict` |
| `thinking_config` | `dict` | `{"search": {}, "judge": {}}` | same | same |
| `model_search` | `str \| None` | `"qwen3-coder-plus"` | same | same |
| `model_judge` | `str \| None` | `"qwen3.7-plus"` | same | same |

**Note**: All three strategies share the same `model_search`/`model_judge` defaults. The `thinking_config` is empty (`{}`) for both phases by default — thinking mode is opt-in via strategy customization.

## 4. Error Handling Matrix

| Condition | Detection | Response |
|-----------|-----------|----------|
| Empty claim text | Pydantic `field_validator` | `ValidationError` → CLI prints error, exit 1 |
| Strategy not found | `REGISTRY` lookup | `ValueError` → CLI prints available strategies, exit 1 |
| Provider exhaustion during search | `QuotaExhaustedError` from `search_provider` | `VerificationError(phase="search", ...)` wraps with `__cause__` |
| Provider exhaustion during judge | `QuotaExhaustedError` from `judge_provider` | `VerificationError(phase="judge", ...)` wraps with `__cause__` |
| Provider error (non-quota) during search | `ProviderError` | Propagates as `VerificationError` wrapping original |
| Provider error (non-quota) during judge | `ProviderError` | Propagates as `VerificationError` wrapping original |
| Tool gateway error | Exception from `gateway.execute()` | Propagates immediately (not wrapped) — tool errors are infrastructure |
| Model returns empty tool_calls | `tool_calls == []` | `tool_context = ""`, proceed to judge. No error. |
| Model returns invalid structured output | `ValidationError` from `model_validate_json` | `ProviderError` → `VerificationError` |
| All providers exhausted | `AllProvidersExhaustedError` | Propagates as `VerificationError` |
| Fundemental provider failure (401) | `ProviderError(status_code=401)` | Propagates as `VerificationError` |

## 5. Edge Cases

| Edge | Behavior |
|------|----------|
| **Empty claim text** | `ValueError` at model construction. CLI catches and prints error. |
| **Claim too long (>100K tokens)** | Passes through to provider. Provider will handle context limits. No client-side truncation. |
| **Model returns no tool calls** | Empty tool_calls → tool_context="" → proceed to judge. Model reasons without external sources. |
| **Multiple tool calls returned** | Execute all in sequence, concatenate results with "\n---\n" separator. |
| **Single tool call, multiple arguments** | Passed as-is to gateway. Mock ignores them. Real gateway will process. |
| **Gateway.execute() fails** | Error propagates immediately without wrapping. Infrastructure failure, not verification failure. |
| **Both phases use same provider** | The engine supports two providers but they can be the same instance. Default uses same env config. |
| **Model override vs per-phase** | `model` overrides both `search_model` and `judge_model`. Per-phase is more specific. |
| **No API key set** | Provider construction fails with `ValueError`. Propagates before any API call. |
| **Thinking mode breaks structured output** | Some models can't do both. Configuring thinking for judge phase may cause JSON parse failure. Handled by `complete_structured`'s error path. |
| **--json + table output** | `--json` flag wins. Exit code remains 0 for success, 1 for error. |
| **MCP client disconnects mid-verify** | MCP server handles via FastMCP lifecycle. No special cleanup needed (sync, single-threaded). |
| **strategy_tool_definitions has no tools** | Phase 1 receives `tools=[]`. Provider behavior is model-dependent. Some models will still return tool_calls. |

## 6. Dependencies

| Package | Version | Type | Why |
|---------|---------|------|-----|
| `rvrb-providers` | `>=0.1.0` | hard | ModelProvider ABC, get_provider(), ToolResult, errors |
| `pydantic` | `>=2.0` | hard | All data models, structured output |
| `typer` | any | hard | CLI |
| `mcp` | any | optional? | MCP server — `rvrb-verify-mcp` entry point |
| `pytest` | any | dev | Tests |
| `pytest-mock` | any | dev | Mock ModelProvider interface |

**No direct `openai` dependency.** All provider interaction is through `rvrb-providers`.

## 7. Test Strategy

| Test File | Classes/Tests | Coverage | Mock Strategy |
|-----------|--------------|----------|---------------|
| `test_models.py` | `TestClaim`, `TestSource`, `TestEvidence`, `TestVerdict`, `TestVerdictEnum` | AC-2 | None — pure Pydantic |
| `test_engine.py` | `TestEngineSearch`, `TestEngineJudge`, `TestEngineBothPhases`, `TestEngineEmptyTools`, `TestEngineErrors` | AC-3, AC-6, AC-7 | Mock `ModelProvider` via `MagicMock` returning `ToolResult`/`Verdict` |
| `test_cli.py` | `TestCliBasic`, `TestCliJson`, `TestCliStrategy`, `TestCliModelOverride`, `TestCliErrors` | AC-8 | Mock `verify()` at module level |
| `test_strategies.py` | `TestStrategyConformance` (parametrized over 3 strategies) | AC-9 | None — check Protocol attributes |
| `test_mcp.py` | `TestMcpTools`, `TestMcpCall` | AC-10 | Mock `verify()` in MCP handler |

### Key Fixtures

```python
# tests/conftest.py
@pytest.fixture
def mock_search_provider(mocker):
    """Returns a MagicMock for the search-phase ModelProvider."""
    provider = mocker.MagicMock(spec=ModelProvider)
    result = ToolResult(content="", tool_calls=[
        ToolCall(id="call_1", name="search_web", arguments={"q": "sky color"})
    ])
    provider.complete_with_tools.return_value = result
    return provider


@pytest.fixture
def mock_judge_provider(mocker):
    """Returns a MagicMock for the judge-phase ModelProvider."""
    provider = mocker.MagicMock(spec=ModelProvider)
    provider.complete_structured.return_value = Verdict(
        claim="The sky is blue",
        verdict=VerdictEnum.TRUE,
        confidence=0.95,
        summary="The sky appears blue due to Rayleigh scattering.",
    )
    return provider


@pytest.fixture
def engine(mock_search_provider, mock_judge_provider):
    """Pre-wired VerificationEngine with mocked providers."""
    return VerificationEngine(
        search_provider=mock_search_provider,
        judge_provider=mock_judge_provider,
        tool_gateway=MockToolGateway(),
    )
```

## 8. Traceability Matrix

| AC | Title | Design Coverage |
|:--:|-------|----------------|
| AC-1 | Package layout | §1: 13 module structure, `pyproject.toml` with deps and entry points |
| AC-2 | Model validation | §2.1: Claim (min_length), VerdictEnum, confidence range, Source auto-retrieved_at |
| AC-3 | Two-phase pipeline | §3.2: Search → Gateway → Judge data flow, sequential phases |
| AC-4 | MockToolGateway | §2.4: Returns deterministic placeholder, zero network |
| AC-5 | Thinking config isolation | §2.2: `thinking_config.search`/`thinking_config.judge`, `extra_body` injection |
| AC-6 | Error wrapping | §4: `QuotaExhaustedError` → `VerificationError(phase)`, `__cause__` chain |
| AC-7 | Empty tool_calls | §5: `tool_context=""`, proceed to judge without error |
| AC-8 | CLI interface | §3.4: Flags, JSON output, strategy selection, model overrides, exit codes |
| AC-9 | Strategy Protocol | §2.2: 7 fields, 3 implementations (fact_check, legal, research), registry |
| AC-10 | MCP server | §3.5: `verify_claim` + `list_strategies` tools, `rvrb-verify-mcp` entry |

## 9. Implementation Notes

### 9.1 Single `verify()` Factory

The `verify()` function in `__init__.py` is the primary entry point. It:
1. Resolves strategy from `REGISTRY`
2. Constructs search/judge providers via `get_provider()`
3. Constructs `VerificationEngine`
4. Calls `engine.verify()`
5. Returns `Verdict`

All construction logic is in the factory — `VerificationEngine` receives already-configured providers.

### 9.2 Provider Construction

```python
def verify(...) -> Verdict:
    strategy_obj = REGISTRY.get(strategy)
    if strategy_obj is None:
        raise ValueError(f"Unknown strategy: {strategy!r}. Available: {list_strategies()}")

    # Resolve model IDs (CLI flag > strategy default > provider default)
    actual_search_model = search_model or strategy_obj.model_search
    actual_judge_model = judge_model or strategy_obj.model_judge

    # Resolve provider names with model overrides
    search_provider_name = f"qwen:{actual_search_model}" if actual_search_model else "qwen"
    judge_provider_name = f"qwen:{actual_judge_model}" if actual_judge_model else "qwen"

    sp = get_provider(search_provider_name)
    jp = get_provider(judge_provider_name)

    engine = VerificationEngine(
        search_provider=sp,
        judge_provider=jp,
        tool_gateway=tool_gateway or MockToolGateway(),
    )
    return engine.verify(claim, strategy_obj)
```

### 9.3 Thinking Mode

`thinking_config` is a dict with optional `search` and `judge` keys. Each value is a dict that gets passed as `extra_body` if non-empty.

```python
# No thinking (default)
thinking_config = {"search": {}, "judge": {}}  # no extra_body sent

# Thinking on judge only (fact-check needs deep reasoning)
thinking_config = {
    "search": {},
    "judge": {"enable_thinking": True, "thinking_max_tokens": 1024},
}
```

Provider call pattern:
```python
search_extra = strategy.thinking_config.get("search") or {}
result = self.search_provider.complete_with_tools(
    messages,
    tools=strategy.tool_definitions,
    extra_body=search_extra if search_extra else None,
)
```

### 9.4 MCP Server Entry

```python
# pyproject.toml
[project.scripts]
rvrb-verify = "rvrb_verify.cli:main"
rvrb-verify-mcp = "rvrb_verify.mcp:main"
```

MCP server uses `FastMCP` for v0. If `mcp` package is not desired as a hard dependency, gate the import:

```python
try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    FastMCP = None  # MCP server unavailable
```

### 9.5 Strategy Prompt Recommendations

The prompts are the core of each domain's behavior. Recommendations:

**Fact Check**:
- Search prompt: "Search for reliable sources about this claim. Prioritize fact-checking organizations, academic sources, and official data."
- Judge prompt: "Evaluate the claim against the provided evidence. Consider source reliability, consistency, and factual accuracy."

**Legal**:
- Search prompt: "Search for relevant statutes, case law, and legal commentary."
- Judge prompt: "Analyze the legal claim. Consider jurisdiction, precedent, statutory interpretation."

**Research**:
- Search prompt: "Search for peer-reviewed papers, preprints, and academic sources."
- Judge prompt: "Evaluate the claim against the published literature. Note consensus, controversy, and methodological quality."

## 10. Files Summary

| File | Action | Git | Purpose |
|------|--------|:--:|---------|
| `src/rvrb_verify/__init__.py` | CREATE | Tracked | Package init, `verify()` factory, public exports |
| `src/rvrb_verify/cli.py` | CREATE | Tracked | Typer CLI |
| `src/rvrb_verify/models.py` | CREATE | Tracked | Claim, Source, Evidence, Verdict, VerdictEnum |
| `src/rvrb_verify/engine.py` | CREATE | Tracked | VerificationEngine, VerificationError |
| `src/rvrb_verify/tools.py` | CREATE | Tracked | ToolGateway Protocol, MockToolGateway |
| `src/rvrb_verify/mcp.py` | CREATE | Tracked | MCP server |
| `src/rvrb_verify/strategies/__init__.py` | CREATE | Tracked | Registry, list_strategies() |
| `src/rvrb_verify/strategies/base.py` | CREATE | Tracked | VerificationStrategy Protocol |
| `src/rvrb_verify/strategies/fact_check.py` | CREATE | Tracked | FactCheckStrategy |
| `src/rvrb_verify/strategies/legal.py` | CREATE | Tracked | LegalReviewStrategy |
| `src/rvrb_verify/strategies/research.py` | CREATE | Tracked | ResearchStrategy |
| `tests/__init__.py` | CREATE | Tracked | Test package |
| `tests/conftest.py` | CREATE | Tracked | Fixtures: mock_search_provider, mock_judge_provider, engine |
| `tests/test_models.py` | CREATE | Tracked | Model tests (AC-2) |
| `tests/test_engine.py` | CREATE | Tracked | Engine tests (AC-3, AC-6, AC-7) |
| `tests/test_cli.py` | CREATE | Tracked | CLI tests (AC-8) |
| `tests/test_strategies.py` | CREATE | Tracked | Strategy conformance (AC-9) |
| `tests/test_mcp.py` | CREATE | Tracked | MCP tests (AC-10) |
| `pyproject.toml` | CREATE | Tracked | hatchling, rvrb-verify, deps |
