"""Two-phase verification pipeline."""

from __future__ import annotations

from typing import Any, cast

from rvrb_providers import ModelProvider, ProviderError, QuotaExhaustedError
from rvrb_verify.models import Verdict
from rvrb_verify.strategies.base import VerificationStrategy
from rvrb_verify.tools import MockToolGateway, ToolGateway


class VerificationError(RuntimeError):
    """Error during the verification pipeline."""

    def __init__(
        self,
        phase: str,
        message: str,
        model_id: str | None = None,
    ) -> None:
        self.phase = phase  # "search" or "judge"
        self.model_id = model_id
        super().__init__(f"[{phase}] {message}")


class VerificationEngine:
    """Two-phase verification pipeline.

    Phase 1 (SEARCH): ``search_provider.complete_with_tools()`` →
    ``tool_gateway.execute()`` on each tool call → build tool context.

    Phase 2 (JUDGE): ``judge_provider.complete_structured()`` with
    combined (user messages + tool context) → ``Verdict``.

    Per-phase model selection is configured via the strategy's
    ``model_search`` / ``model_judge`` fields.
    """

    def __init__(
        self,
        *,
        search_provider: ModelProvider,
        judge_provider: ModelProvider,
        tool_gateway: ToolGateway | None = None,
    ) -> None:
        self._search_provider = search_provider
        self._judge_provider = judge_provider
        self._tool_gateway = tool_gateway or MockToolGateway()

    def verify(
        self,
        claim: str,
        strategy: VerificationStrategy | None = None,
    ) -> Verdict:
        """Run the two-phase verification pipeline.

        Parameters
        ----------
        claim : str
            The claim text to verify.
        strategy : VerificationStrategy | None
            Strategy to use. If ``None``, uses a basic fact-check prompt
            with no tool definitions.

        Returns
        -------
        Verdict
        """
        from rvrb_verify.strategies.fact_check import fact_check_strategy

        if strategy is None:
            strategy = fact_check_strategy

        # ---- Phase 1: SEARCH --------------------------------------------------
        search_messages = [
            {"role": "system", "content": strategy.system_prompt_search},
            {"role": "user", "content": f"Claim: {claim}"},
        ]

        tool_context = self._execute_search_phase(strategy, search_messages)

        # ---- Phase 2: JUDGE ---------------------------------------------------
        judge_messages = [
            {"role": "system", "content": strategy.system_prompt_judge},
            {
                "role": "user",
                "content": f"Claim: {claim}\n\nEvidence:\n{tool_context}",
            },
        ]

        return self._execute_judge_phase(strategy, judge_messages)

    def _execute_search_phase(
        self,
        strategy: VerificationStrategy,
        messages: list[dict[str, Any]],
    ) -> str:
        """Execute the search phase. Returns tool context string."""
        search_extra = strategy.thinking_config.get("search") or {}

        try:
            result = self._search_provider.complete_with_tools(
                messages,
                tools=strategy.tool_definitions,
                extra_body=search_extra if search_extra else None,
            )
        except QuotaExhaustedError as exc:
            raise VerificationError(
                phase="search",
                message=str(exc),
                model_id=exc.model_id,
            ) from exc
        except ProviderError as exc:
            raise VerificationError(
                phase="search",
                message=str(exc),
                model_id=exc.model_id,
            ) from exc

        # If model returned no tool calls, proceed with empty context
        if not result.tool_calls:
            return ""

        # Execute all tool calls and build context
        fragments: list[str] = []
        for tool_call in result.tool_calls:
            fragment = self._tool_gateway.execute(
                tool_call.name, tool_call.arguments
            )
            fragments.append(fragment)

        return "\n---\n".join(fragments)

    def _execute_judge_phase(
        self,
        strategy: VerificationStrategy,
        messages: list[dict[str, Any]],
    ) -> Verdict:
        """Execute the judgment phase. Returns a Verdict."""
        judge_extra = strategy.thinking_config.get("judge") or {}

        try:
            raw = self._judge_provider.complete_structured(
                messages,
                output_type=Verdict,
                extra_body=judge_extra if judge_extra else None,
            )
        except QuotaExhaustedError as exc:
            raise VerificationError(
                phase="judge",
                message=str(exc),
                model_id=exc.model_id,
            ) from exc
        except ProviderError as exc:
            raise VerificationError(
                phase="judge",
                message=str(exc),
                model_id=exc.model_id,
            ) from exc

        verdict = cast(Verdict, raw)

        # Ensure the verdict carries model info
        if not verdict.model_used:
            judge_model = getattr(self._judge_provider, "model", "")
            verdict.model_used = judge_model

        return verdict
