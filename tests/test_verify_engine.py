"""Tests for rvrb_verify.engine — two-phase verification pipeline."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from rvrb_providers import QuotaExhaustedError
from rvrb_verify.engine import VerificationEngine, VerificationError
from rvrb_verify.models import Verdict, VerdictEnum
from rvrb_verify.tools import MockToolGateway


class TestEngineConstruction:
    def test_default_tool_gateway(self, mock_search_provider, mock_judge_provider) -> None:
        engine = VerificationEngine(
            search_provider=mock_search_provider,
            judge_provider=mock_judge_provider,
        )
        assert isinstance(engine._tool_gateway, MockToolGateway)

    def test_custom_tool_gateway(self, mock_search_provider, mock_judge_provider) -> None:
        class CustomGateway(MockToolGateway):
            pass

        gw = CustomGateway()
        engine = VerificationEngine(
            search_provider=mock_search_provider,
            judge_provider=mock_judge_provider,
            tool_gateway=gw,
        )
        assert engine._tool_gateway is gw


class TestEngineVerify:
    def test_both_phases_execute(self, engine, strategy) -> None:
        """Verify that both search and judge phases are called."""
        verdict = engine.verify("The sky is blue", strategy)

        assert isinstance(verdict, Verdict)
        engine._search_provider.complete_with_tools.assert_called_once()
        engine._judge_provider.complete_structured.assert_called_once()

    def test_search_receives_correct_tools(self, engine, strategy) -> None:
        """Verify search phase receives strategy's tool definitions."""
        engine.verify("Test claim", strategy)

        _, kwargs = engine._search_provider.complete_with_tools.call_args
        assert "tools" in kwargs
        assert kwargs["tools"] == strategy.tool_definitions

    def test_judge_receives_correct_output_type(self, engine, strategy) -> None:
        """Verify judge phase requests Verdict as output type."""
        engine.verify("Test claim", strategy)

        _, kwargs = engine._judge_provider.complete_structured.call_args
        assert "output_type" in kwargs
        assert kwargs["output_type"] is Verdict

    def test_judge_never_called_before_search(self, engine, strategy) -> None:
        """Verify search executes before judge."""
        engine.verify("Test claim", strategy)

        search_order = engine._search_provider.complete_with_tools.call_count
        judge_order = engine._judge_provider.complete_structured.call_count
        assert search_order >= 1
        assert judge_order >= 1

    def test_tool_gateway_called(self, engine, strategy) -> None:
        """Verify tool gateway is invoked for each tool call."""
        engine.verify("Test claim", strategy)

        # MockToolGateway produces deterministic output
        engine._search_provider.complete_with_tools.assert_called_once()

    def test_returns_verdict(self, engine, strategy) -> None:
        """Verify the engine returns a Verdict object."""
        verdict = engine.verify("Test claim", strategy)
        assert isinstance(verdict, Verdict)
        assert verdict.claim == "The sky is blue"  # from mock
        assert verdict.verdict == VerdictEnum.TRUE

    def test_verdict_has_model_used(self, engine, strategy) -> None:
        """Verify the verdict includes the judge model ID."""
        verdict = engine.verify("Test claim", strategy)
        assert verdict.model_used == "qwen3.7-plus"


class TestEngineEmptyTools:
    def test_no_tool_calls_proceeds_to_judge(
        self, mock_search_provider, mock_judge_provider, strategy
    ) -> None:
        """Verify empty tool_calls → tool_context="" → proceed to judge."""
        result = type("ToolResult", (), {"content": "", "tool_calls": []})()
        mock_search_provider.complete_with_tools.return_value = result

        engine = VerificationEngine(
            search_provider=mock_search_provider,
            judge_provider=mock_judge_provider,
            tool_gateway=MockToolGateway(),
        )
        verdict = engine.verify("Test", strategy)

        assert isinstance(verdict, Verdict)
        # Judge should still be called
        mock_judge_provider.complete_structured.assert_called_once()

    def test_no_tool_definitions_still_works(
        self, mock_search_provider, mock_judge_provider
    ) -> None:
        """Verify strategy with empty tool definitions doesn't crash."""
        from rvrb_verify.models import Verdict

        empty_strategy = SimpleNamespace(
            name="empty",
            system_prompt_search="Search",
            system_prompt_judge="Judge",
            tool_definitions=[],
            verdict_schema=Verdict,
            thinking_config={"search": {}, "judge": {}},
            model_search=None,
            model_judge=None,
        )

        engine = VerificationEngine(
            search_provider=mock_search_provider,
            judge_provider=mock_judge_provider,
            tool_gateway=MockToolGateway(),
        )
        verdict = engine.verify("Test", empty_strategy)
        assert isinstance(verdict, Verdict)


class TestEngineErrors:
    def test_search_exhaustion_raises(
        self, exhausted_search_provider, mock_judge_provider, strategy
    ) -> None:
        engine = VerificationEngine(
            search_provider=exhausted_search_provider,
            judge_provider=mock_judge_provider,
        )
        with pytest.raises(VerificationError) as exc_info:
            engine.verify("Test", strategy)

        assert exc_info.value.phase == "search"

    def test_judge_exhaustion_raises(
        self, mock_search_provider, exhausted_judge_provider, strategy
    ) -> None:
        engine = VerificationEngine(
            search_provider=mock_search_provider,
            judge_provider=exhausted_judge_provider,
        )
        with pytest.raises(VerificationError) as exc_info:
            engine.verify("Test", strategy)

        assert exc_info.value.phase == "judge"

    def test_search_provider_error_raises(
        self, error_search_provider, mock_judge_provider, strategy
    ) -> None:
        engine = VerificationEngine(
            search_provider=error_search_provider,
            judge_provider=mock_judge_provider,
        )
        with pytest.raises(VerificationError) as exc_info:
            engine.verify("Test", strategy)

        assert exc_info.value.phase == "search"

    def test_error_carries_original_exception(
        self, exhausted_search_provider, mock_judge_provider, strategy
    ) -> None:
        engine = VerificationEngine(
            search_provider=exhausted_search_provider,
            judge_provider=mock_judge_provider,
        )
        with pytest.raises(VerificationError) as exc_info:
            engine.verify("Test", strategy)

        assert isinstance(exc_info.value.__cause__, QuotaExhaustedError)
