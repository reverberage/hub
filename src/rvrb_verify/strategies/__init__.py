"""Verification strategy registry."""

from __future__ import annotations

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
