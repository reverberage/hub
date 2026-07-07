"""Research validation verification strategy."""

from __future__ import annotations

from types import SimpleNamespace
from typing import Any

from rvrb_verify.models import Verdict

SEARCH_PAPERS: dict[str, Any] = {
    "type": "function",
    "function": {
        "name": "search_papers",
        "description": "Search for peer-reviewed papers and academic sources",
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

SEARCH_ARXIV: dict[str, Any] = {
    "type": "function",
    "function": {
        "name": "search_arxiv",
        "description": "Search arXiv preprints for research results",
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

research_strategy = SimpleNamespace(
    name="research",
    system_prompt_search=(
        "You are a research validator. Search for peer-reviewed "
        "papers, preprints, and academic sources related to this claim."
    ),
    system_prompt_judge=(
        "You are a research judge. Evaluate the claim against the "
        "published literature. Note consensus, controversy, and "
        "methodological quality. Return a Verdict."
    ),
    tool_definitions=[SEARCH_PAPERS, SEARCH_ARXIV],
    verdict_schema=Verdict,
    thinking_config={"search": {}, "judge": {}},
    model_search="qwen3-coder-plus",
    model_judge="qwen3.7-plus",
)
