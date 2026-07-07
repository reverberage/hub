"""Tests for rvrb_verify.cli — Typer CLI interface."""

from __future__ import annotations

import json

from typer.testing import CliRunner

from rvrb_verify.cli import app
from rvrb_verify.models import Verdict, VerdictEnum

runner = CliRunner()


class TestCliBasic:
    def test_help_works(self) -> None:
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "CLAIM_TEXT" in result.stdout
        assert "--strategy" in result.stdout
        assert "--json" in result.stdout
        assert "--model" in result.stdout

    def test_no_claim_shows_error(self) -> None:
        result = runner.invoke(app, [])
        assert result.exit_code != 0


class TestCliWithVerify:
    """These tests mock at the verify() module level."""

    def test_verify_called(self, mocker) -> None:
        mock_verify = mocker.patch("rvrb_verify.cli.verify")
        mock_verify.return_value = Verdict(
            claim="Test claim",
            verdict=VerdictEnum.TRUE,
            confidence=0.95,
            summary="Test",
        )

        result = runner.invoke(app, ["Test claim"])
        assert result.exit_code == 0
        mock_verify.assert_called_once()

    def test_json_output(self, mocker) -> None:
        mock_verify = mocker.patch("rvrb_verify.cli.verify")
        mock_verify.return_value = Verdict(
            claim="Test claim",
            verdict=VerdictEnum.TRUE,
            confidence=0.95,
            summary="Test",
        )

        result = runner.invoke(app, ["Test claim", "--json"])
        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert data["verdict"] == "true"
        assert data["confidence"] == 0.95

    def test_strategy_flag(self, mocker) -> None:
        mock_verify = mocker.patch("rvrb_verify.cli.verify")
        mock_verify.return_value = Verdict(
            claim="Legal claim",
            verdict=VerdictEnum.FALSE,
            confidence=0.8,
            summary="Legal analysis",
        )

        result = runner.invoke(app, ["Legal claim", "--strategy", "legal"])
        assert result.exit_code == 0
        mock_verify.assert_called_once()
        _, kwargs = mock_verify.call_args
        assert kwargs.get("strategy") == "legal"

    def test_model_override(self, mocker) -> None:
        mock_verify = mocker.patch("rvrb_verify.cli.verify")
        mock_verify.return_value = Verdict(
            claim="Test",
            verdict=VerdictEnum.TRUE,
            confidence=0.9,
            summary="Test",
        )

        result = runner.invoke(app, ["Test", "--model", "qwen3.7-plus"])
        assert result.exit_code == 0, result.stderr
        mock_verify.assert_called_once()
        _, kwargs = mock_verify.call_args
        assert kwargs.get("model") == "qwen3.7-plus"

    def test_per_phase_model_override(self, mocker) -> None:
        mock_verify = mocker.patch("rvrb_verify.cli.verify")
        mock_verify.return_value = Verdict(
            claim="Test",
            verdict=VerdictEnum.TRUE,
            confidence=0.9,
            summary="Test",
        )

        result = runner.invoke(app, [
            "Test",
            "--search-model", "qwen3-coder-plus",
            "--judge-model", "qwen3.7-plus",
        ])
        assert result.exit_code == 0, result.stderr
        _, kwargs = mock_verify.call_args
        assert kwargs.get("search_model") == "qwen3-coder-plus"
        assert kwargs.get("judge_model") == "qwen3.7-plus"

    def test_error_exits_with_code_1(self, mocker) -> None:
        mock_verify = mocker.patch("rvrb_verify.cli.verify")
        mock_verify.side_effect = ValueError("Bad strategy")

        result = runner.invoke(app, ["Test claim"])
        assert result.exit_code == 1

    def test_unknown_strategy_shows_available(self, mocker) -> None:

        mock_verify = mocker.patch("rvrb_verify.cli.verify")
        mock_verify.side_effect = ValueError("Bad strategy")

        result = runner.invoke(app, ["Test", "--strategy", "nonexistent"])
        assert result.exit_code == 1
