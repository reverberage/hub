"""Typer CLI for claim verification."""

from __future__ import annotations

import json
import sys

import typer

from rvrb_verify import verify
from rvrb_verify.models import Verdict

app = typer.Typer(
    name="rvrb-verify",
    help="Verify a claim using LLM-powered analysis.",
)


@app.command()
def verify_command(
    claim_text: str = typer.Argument(
        ..., help="The claim to verify."
    ),
    strategy: str = typer.Option(
        "fact-check",
        "--strategy",
        help="Verification strategy.",
    ),
    json_output: bool = typer.Option(
        False,
        "--json",
        help="Output as JSON.",
    ),
    model: str | None = typer.Option(
        None,
        "--model",
        help="Override model for both phases (e.g. 'qwen3.7-plus').",
    ),
    search_model: str | None = typer.Option(
        None,
        "--search-model",
        help="Override model for search phase only (e.g. 'qwen3-coder-plus').",
    ),
    judge_model: str | None = typer.Option(
        None,
        "--judge-model",
        help="Override model for judge phase only (e.g. 'qwen3.7-plus').",
    ),
) -> None:
    """Verify a claim using LLM-powered analysis."""
    try:
        verdict = verify(
            claim_text,
            strategy=strategy,
            model=model,
            search_model=search_model,
            judge_model=judge_model,
        )
    except ValueError as exc:
        _print_error(str(exc))
        raise typer.Exit(code=1) from exc
    except Exception as exc:
        _print_error(str(exc))
        raise typer.Exit(code=1) from exc

    if json_output:
        _print_json(verdict)
    else:
        _print_table(verdict)

    raise typer.Exit(code=0)


def _print_table(verdict: Verdict) -> None:
    """Print verdict as a human-readable table."""
    from rich.console import Console
    from rich.table import Table

    console = Console()

    table = Table(title="Verification Result")
    table.add_column("Field", style="bold")
    table.add_column("Value")

    table.add_row("Claim", verdict.claim)
    table.add_row("Verdict", verdict.verdict.value)
    table.add_row("Confidence", f"{verdict.confidence:.1%}")
    table.add_row("Summary", verdict.summary)
    table.add_row("Model", verdict.model_used or "—")

    console.print(table)

    if verdict.evidence:
        console.print("\n[bold]Evidence:[/bold]")
        for i, ev in enumerate(verdict.evidence, 1):
            supports = "✅ Supports" if ev.supports else "❌ Refutes"
            console.print(f"  {i}. {supports}: {ev.reasoning}")
            for src in ev.sources:
                console.print(f"     Source: {src.title} ({src.url})")


def _print_json(verdict: Verdict) -> None:
    """Print verdict as JSON."""
    data = verdict.model_dump(mode="json")
    json.dump(data, sys.stdout, indent=2, default=str)
    sys.stdout.write("\n")


def _print_error(message: str) -> None:
    """Print an error message to stderr."""
    import sys

    print(f"Error: {message}", file=sys.stderr)


def main() -> None:
    """Entry point for the CLI."""
    app()
