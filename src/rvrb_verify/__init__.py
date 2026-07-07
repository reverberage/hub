"""Claim verification engine for reverberage."""

from __future__ import annotations

from rvrb_verify.models import Evidence, Source, Verdict
from rvrb_verify.tools import MockToolGateway, ToolGateway

__all__ = [
    "Verdict",
    "Evidence",
    "Source",
    "MockToolGateway",
    "ToolGateway",
    "list_strategies",
    "verify",
]

__version__ = "0.1.0"


def list_strategies() -> list[str]:
    """Return available verification strategy names."""
    from rvrb_verify.strategies import list_strategies as _ls

    return _ls()


def verify(
    claim_text: str,
    strategy: str = "fact-check",
    *,
    model: str | None = None,
    search_model: str | None = None,
    judge_model: str | None = None,
    search_provider_spec: str | None = None,
    judge_provider_spec: str | None = None,
    tool_gateway: ToolGateway | None = None,
) -> Verdict:
    """Verify a claim using the given strategy.

    Parameters
    ----------
    claim_text : str
        The claim to verify.
    strategy : str
        Strategy name from ``list_strategies()``. Default: ``"fact-check"``.
    model : str | None
        Override model for both phases (e.g. ``"qwen:qwen3.7-plus"``).
        Sets both search and judge if neither is specified.
    search_model : str | None
        Override only the search phase model.
    judge_model : str | None
        Override only the judge phase model.
    search_provider_spec : str | None
        Full provider spec for search. Default: inferred from strategy.
    judge_provider_spec : str | None
        Full provider spec for judge. Default: inferred from strategy.
    tool_gateway : ToolGateway | None
        Tool executor. Default: ``MockToolGateway()``.

    Returns
    -------
    Verdict
    """
    from rvrb_providers import get_provider
    from rvrb_verify.engine import VerificationEngine
    from rvrb_verify.strategies import REGISTRY

    strategy_obj = REGISTRY.get(strategy)
    if strategy_obj is None:
        raise ValueError(
            f"Unknown strategy: {strategy!r}. "
            f"Available: {', '.join(list_strategies())}"
        )

    # Model precedence: explicit per-phase > explicit model > strategy default > None
    actual_search_model = search_model or model or strategy_obj.model_search
    actual_judge_model = judge_model or model or strategy_obj.model_judge

    # Resolve provider specs
    sp_spec = search_provider_spec or (
        f"qwen:{actual_search_model}" if actual_search_model else "qwen"
    )
    jp_spec = judge_provider_spec or (
        f"qwen:{actual_judge_model}" if actual_judge_model else "qwen"
    )

    sp = get_provider(sp_spec)
    jp = get_provider(jp_spec)

    engine = VerificationEngine(
        search_provider=sp,
        judge_provider=jp,
        tool_gateway=tool_gateway or MockToolGateway(),
    )
    return engine.verify(claim_text, strategy_obj)
