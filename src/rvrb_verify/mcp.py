"""MCP server for claim verification."""

from __future__ import annotations

from typing import Any

from rvrb_verify.strategies import list_strategies

try:
    from mcp.server.fastmcp import FastMCP as FastMCPType

    HAS_MCP = True
except ImportError:  # pragma: no cover
    FastMCPType = None  # type: ignore[misc,assignment]
    HAS_MCP = False


def verify_claim(
    claim_text: str,
    strategy: str = "fact-check",
) -> dict[str, Any]:
    """Verify a claim using LLM-powered analysis.

    Args:
        claim_text: The claim to verify.
        strategy: Verification strategy name (default: fact-check).
    """
    from rvrb_verify import verify as _verify

    try:
        verdict = _verify(claim_text, strategy=strategy)
        return verdict.model_dump(mode="json")
    except ValueError as exc:
        return {"error": str(exc)}
    except Exception as exc:
        return {"error": str(exc)}


def list_available_strategies() -> list[str]:
    """List available verification strategies."""
    return list_strategies()


def _build_server() -> Any:
    """Create and return a configured MCP server instance.

    Returns None if the ``mcp`` package is not installed.
    """
    if not HAS_MCP or FastMCPType is None:
        return None

    mcp = FastMCPType("rvrb-verify")

    @mcp.tool()
    def _verify_claim_tool(
        claim_text: str,
        strategy: str = "fact-check",
    ) -> dict[str, Any]:
        """Verify a claim using LLM-powered analysis."""
        return verify_claim(claim_text, strategy=strategy)

    @mcp.tool()
    def _list_strategies_tool() -> list[str]:
        """List available verification strategies."""
        return list_available_strategies()

    return mcp


_SERVER: Any = None


def main() -> None:
    """Entry point for ``rvrb-verify-mcp``."""
    global _SERVER
    if _SERVER is None:
        _SERVER = _build_server()

    if _SERVER is None:
        msg = "mcp package is required. Install with: pip install mcp"
        raise ImportError(msg)

    _SERVER.run(transport="stdio")
