"""Legal review verification strategy."""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any

from rvrb_verify.models import Verdict

SEARCH_STATUTES: dict[str, Any] = {
    "type": "function",
    "function": {
        "name": "search_statutes",
        "description": "Search for relevant statutes and regulations",
        "parameters": {
            "type": "object",
            "properties": {
                "q": {
                    "type": "string",
                    "description": "Search query",
                }
            },
            "required": ["q"],
        },
    },
}

SEARCH_CASE_LAW: dict[str, Any] = {
    "type": "function",
    "function": {
        "name": "search_case_law",
        "description": "Search for relevant case law and precedent",
        "parameters": {
            "type": "object",
            "properties": {
                "q": {
                    "type": "string",
                    "description": "Search query",
                }
            },
            "required": ["q"],
        },
    },
}

legal_strategy = SimpleNamespace(
    name="legal",
    system_prompt_search=(
        "You are a legal analyst. Search for relevant statutes, "
        "case law, and legal commentary about this claim."
    ),
    system_prompt_judge=(
        "You are a legal judge. Analyze the claim against the "
        "provided evidence. Consider jurisdiction, precedent, "
        "and statutory interpretation. Return a Verdict."
    ),
    tool_definitions=[SEARCH_STATUTES, SEARCH_CASE_LAW],
    verdict_schema=Verdict,
    thinking_config={"search": {}, "judge": {}},
    model_search="qwen3-coder-plus",
    model_judge="qwen3.7-plus",
)
