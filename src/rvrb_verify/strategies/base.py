"""Verification strategy protocol."""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable

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
    tool_definitions: list[dict[str, Any]]
    verdict_schema: type[BaseModel]
    thinking_config: dict[str, Any]
    model_search: str | None
    model_judge: str | None
