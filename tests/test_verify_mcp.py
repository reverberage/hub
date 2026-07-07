"""Tests for rvrb_verify.mcp — MCP server interface."""

from __future__ import annotations

from rvrb_verify.mcp import HAS_MCP, list_available_strategies, verify_claim


class TestMcpTools:
    def test_list_strategies_returns_list(self) -> None:
        if not HAS_MCP:
            return  # skip if mcp not installed
        strategies = list_available_strategies()
        assert isinstance(strategies, list)
        assert len(strategies) == 3
        assert "fact-check" in strategies

    def test_verify_claim_with_mock(self, mocker) -> None:
        if not HAS_MCP:
            return

        from rvrb_verify.models import Verdict, VerdictEnum

        # Patch at the source (rvrb_verify.verify) since mcp imports from there
        mock_verify = mocker.patch("rvrb_verify.verify")
        mock_verify.return_value = Verdict(
            claim="Test claim",
            verdict=VerdictEnum.TRUE,
            confidence=0.95,
            summary="Test summary",
        )

        result = verify_claim("Test claim", strategy="fact-check")
        assert isinstance(result, dict)
        assert result["verdict"] == "true"
        assert result["confidence"] == 0.95

    def test_verify_claim_handles_error(self, mocker) -> None:
        if not HAS_MCP:
            return

        mock_verify = mocker.patch("rvrb_verify.verify")
        mock_verify.side_effect = ValueError("Bad strategy")

        result = verify_claim("Test", strategy="nonexistent")
        assert isinstance(result, dict)
        assert "error" in result

    def test_verify_claim_default_strategy(self, mocker) -> None:
        if not HAS_MCP:
            return

        from rvrb_verify.models import Verdict, VerdictEnum

        mock_verify = mocker.patch("rvrb_verify.verify")
        mock_verify.return_value = Verdict(
            claim="Test",
            verdict=VerdictEnum.TRUE,
            confidence=0.9,
            summary="OK",
        )

        result = verify_claim("Test")
        assert result["verdict"] == "true"
