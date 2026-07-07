"""Tool gateway interface for executing tool calls during verification."""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class ToolGateway(Protocol):
    """Interface for executing tool calls."""

    def execute(self, tool_name: str, arguments: dict[str, Any]) -> str:
        """Execute a tool call and return the result as text."""
        ...


class MockToolGateway:
    """Tool gateway that returns placeholder responses.

    Always returns ``"[mock] no real search configured: {name}({args})"``.
    Zero network I/O.
    """

    def execute(self, tool_name: str, arguments: dict[str, Any]) -> str:
        args_fmt = ", ".join(f"{k}={v!r}" for k, v in arguments.items())
        return f"[mock] no real search configured: {tool_name}({args_fmt})"
