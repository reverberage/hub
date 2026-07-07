"""Shared fixtures for rvrb_providers and rvrb_verify tests."""

from __future__ import annotations

from unittest.mock import MagicMock

import httpx
import pytest
from openai import APIStatusError

from rvrb_providers import ProviderError, QuotaExhaustedError, ToolCall, ToolResult
from rvrb_verify.models import Verdict, VerdictEnum
from rvrb_verify.strategies.fact_check import fact_check_strategy
from rvrb_verify.tools import MockToolGateway


def make_mock_response(
    content: str = "",
    tool_calls: list | None = None,
    headers: dict | None = None,
) -> MagicMock:
    """Create a mock completion response.

    Args:
        content: Message content string.
        tool_calls: Optional list of tool call dicts.

    Returns:
        A MagicMock structured like an OpenAI ChatCompletion response.
    """
    choice = MagicMock()
    choice.message.content = content
    choice.finish_reason = "stop"

    if tool_calls:
        mock_tcs = []
        for tc in tool_calls:
            m = MagicMock()
            m.id = tc.get("id", "call_1")
            m.type = "function"
            m.function.name = tc.get("name", "test_tool")
            m.function.arguments = tc.get("arguments", "{}")
            mock_tcs.append(m)
        choice.message.tool_calls = mock_tcs
    else:
        choice.message.tool_calls = None

    response = MagicMock()
    response.choices = [choice]
    response.headers = headers or {}
    response.model_dump.return_value = {
        "choices": [{"message": {"content": content}}]
    }
    return response


def make_429_error(body: str = "") -> APIStatusError:
    """Create a mock 429 APIStatusError."""
    response = MagicMock(spec=httpx.Response)
    response.status_code = 429
    response.headers = {}
    response.text = body
    return APIStatusError(
        message="Rate limit exceeded",
        response=response,  # type: ignore[arg-type]
        body=body,
    )


def make_tool_call(id: str, name: str, arguments: str = "{}") -> dict:
    """Create a tool call dict."""
    return {"id": id, "name": name, "arguments": arguments}


@pytest.fixture
def mock_openai_client(mocker):
    """Patch openai.OpenAI to return a mock client.

    Used by all provider tests (qwen, openai, local) to avoid
    real API calls.
    """
    mock_client = mocker.MagicMock()
    mocker.patch("openai.OpenAI", return_value=mock_client)
    return mock_client


@pytest.fixture
def mock_search_provider(mocker):
    """Returns a MagicMock for the search-phase ModelProvider."""
    provider = mocker.MagicMock(spec=["complete_with_tools", "complete_structured", "complete"])
    result = ToolResult(
        content="",
        tool_calls=[
            ToolCall(id="call_1", name="search_web", arguments={"q": "sky color"})
        ],
    )
    provider.complete_with_tools.return_value = result
    return provider


@pytest.fixture
def mock_judge_provider(mocker):
    """Returns a MagicMock for the judge-phase ModelProvider."""
    provider = mocker.MagicMock(spec=["complete_with_tools", "complete_structured", "complete"])
    provider.complete_structured.return_value = Verdict(
        claim="The sky is blue",
        verdict=VerdictEnum.TRUE,
        confidence=0.95,
        summary="The sky appears blue due to Rayleigh scattering.",
    )
    provider.model = "qwen3.7-plus"
    return provider


@pytest.fixture
def engine(mock_search_provider, mock_judge_provider):
    """Pre-wired VerificationEngine with mocked providers."""
    from rvrb_verify.engine import VerificationEngine

    return VerificationEngine(
        search_provider=mock_search_provider,
        judge_provider=mock_judge_provider,
        tool_gateway=MockToolGateway(),
    )


@pytest.fixture
def exhausted_search_provider(mocker):
    """Returns a mock provider that raises QuotaExhaustedError on search."""
    provider = mocker.MagicMock(spec=["complete_with_tools", "complete_structured", "complete"])
    provider.complete_with_tools.side_effect = QuotaExhaustedError(
        model_id="qwen3-coder-plus",
        status_code=429,
        body='{"code":"AllocationQuota.FreeTierOnly"}',
    )
    return provider


@pytest.fixture
def exhausted_judge_provider(mocker):
    """Returns a mock provider that raises QuotaExhaustedError on judge."""
    provider = mocker.MagicMock(spec=["complete_with_tools", "complete_structured", "complete"])
    provider.complete_structured.side_effect = QuotaExhaustedError(
        model_id="qwen3.7-plus",
        status_code=429,
        body='{"code":"AllocationQuota.FreeTierOnly"}',
    )
    return provider


@pytest.fixture
def error_search_provider(mocker):
    """Returns a mock provider that raises a non-quota ProviderError on search."""
    provider = mocker.MagicMock(spec=["complete_with_tools", "complete_structured", "complete"])
    provider.complete_with_tools.side_effect = ProviderError(
        model_id="qwen3-coder-plus",
        status_code=401,
        body="Unauthorized",
    )
    return provider


@pytest.fixture
def strategy():
    """Returns the default fact-check strategy."""
    return fact_check_strategy
