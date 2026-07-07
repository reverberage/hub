"""Tests for rvrb_verify.strategies — conformance checks for all strategies."""

from __future__ import annotations

import pytest

from rvrb_verify.strategies import REGISTRY, list_strategies
from rvrb_verify.strategies.base import VerificationStrategy


class TestRegistry:
    def test_has_three_strategies(self) -> None:
        assert len(REGISTRY) == 3

    def test_list_strategies_returns_sorted(self) -> None:
        names = list_strategies()
        assert names == sorted(names)
        assert len(names) == 3

    def test_registry_keys_match_names(self) -> None:
        for name, strategy in REGISTRY.items():
            assert strategy.name == name

    def test_all_strategies_conform_to_protocol(self) -> None:
        for strategy in REGISTRY.values():
            assert isinstance(strategy, VerificationStrategy), (
                f"{strategy.name} does not conform to VerificationStrategy"
            )


CONFORMANCE_PARAMS = [
    (name, strategy) for name, strategy in REGISTRY.items()
]


class TestStrategyConformance:
    @pytest.mark.parametrize("name,strategy", CONFORMANCE_PARAMS)
    def test_has_name(self, name: str, strategy: VerificationStrategy) -> None:
        assert isinstance(strategy.name, str)
        assert len(strategy.name) > 0

    @pytest.mark.parametrize("name,strategy", CONFORMANCE_PARAMS)
    def test_has_system_prompt_search(self, name: str, strategy: VerificationStrategy) -> None:
        assert isinstance(strategy.system_prompt_search, str)
        assert len(strategy.system_prompt_search) > 0

    @pytest.mark.parametrize("name,strategy", CONFORMANCE_PARAMS)
    def test_has_system_prompt_judge(self, name: str, strategy: VerificationStrategy) -> None:
        assert isinstance(strategy.system_prompt_judge, str)
        assert len(strategy.system_prompt_judge) > 0

    @pytest.mark.parametrize("name,strategy", CONFORMANCE_PARAMS)
    def test_has_tool_definitions(self, name: str, strategy: VerificationStrategy) -> None:
        assert isinstance(strategy.tool_definitions, list)
        assert len(strategy.tool_definitions) > 0
        for tool in strategy.tool_definitions:
            assert "type" in tool
            assert "function" in tool

    @pytest.mark.parametrize("name,strategy", CONFORMANCE_PARAMS)
    def test_has_verdict_schema(self, name: str, strategy: VerificationStrategy) -> None:
        from rvrb_verify.models import Verdict

        assert strategy.verdict_schema is Verdict

    @pytest.mark.parametrize("name,strategy", CONFORMANCE_PARAMS)
    def test_has_thinking_config(self, name: str, strategy: VerificationStrategy) -> None:
        assert isinstance(strategy.thinking_config, dict)
        assert "search" in strategy.thinking_config
        assert "judge" in strategy.thinking_config

    @pytest.mark.parametrize("name,strategy", CONFORMANCE_PARAMS)
    def test_has_model_search(self, name: str, strategy: VerificationStrategy) -> None:
        assert isinstance(strategy.model_search, str) or strategy.model_search is None

    @pytest.mark.parametrize("name,strategy", CONFORMANCE_PARAMS)
    def test_has_model_judge(self, name: str, strategy: VerificationStrategy) -> None:
        assert isinstance(strategy.model_judge, str) or strategy.model_judge is None
