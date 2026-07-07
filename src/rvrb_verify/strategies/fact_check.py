"""Fact-checking verification strategy."""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any

from rvrb_verify.models import Verdict

SEARCH_WEB: dict[str, Any] = {
    "type": "function",
    "function": {
        "name": "search_web",
        "description": "Search the web for information about a claim",
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

SEARCH_NEWS: dict[str, Any] = {
    "type": "function",
    "function": {
        "name": "search_news",
        "description": "Search recent news for information about a claim",
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

fact_check_strategy = SimpleNamespace(
    name="fact-check",
    system_prompt_search=(
        "You are a fact-checker. Search for reliable sources about "
        "this claim. Prioritize fact-checking organizations, academic "
        "sources, and official data."
    ),
    system_prompt_judge=(
        "You are a fact-checking judge. Evaluate the claim against "
        "the provided evidence. Consider source reliability, "
        "consistency, and factual accuracy. Return a Verdict with "
        "your analysis."
    ),
    tool_definitions=[SEARCH_WEB, SEARCH_NEWS],
    verdict_schema=Verdict,
    thinking_config={"search": {}, "judge": {}},
    model_search="qwen3-coder-plus",
    model_judge="qwen3.7-plus",
)
