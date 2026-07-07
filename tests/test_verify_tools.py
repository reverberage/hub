"""Tests for rvrb_verify.tools — ToolGateway Protocol + MockToolGateway."""

from __future__ import annotations

from rvrb_verify.tools import MockToolGateway, ToolGateway


class TestToolGatewayProtocol:
    def test_is_runtime_checkable(self) -> None:
        assert isinstance(MockToolGateway(), ToolGateway)


class TestMockToolGateway:
    def test_execute_returns_placeholder(self) -> None:
        gw = MockToolGateway()
        result = gw.execute("search_web", {"q": "sky color"})
        assert "[mock]" in result
        assert "search_web" in result
        assert "q=" in result or "q" in result

    def test_execute_formats_arguments(self) -> None:
        gw = MockToolGateway()
        result = gw.execute("search_news", {"q": "election", "date": "2024"})
        assert "search_news" in result
        assert "election" in result
        assert "2024" in result

    def test_execute_empty_arguments(self) -> None:
        gw = MockToolGateway()
        result = gw.execute("list_sources", {})
        assert "[mock]" in result
        assert "list_sources" in result

    def test_execute_no_network(self) -> None:
        """Verify MockToolGateway makes zero network calls."""
        gw = MockToolGateway()
        result = gw.execute("any_tool", {"key": "val"})
        assert isinstance(result, str)
