"""Rich terminal output for benchmark results."""

from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from llm_bench.models import BenchmarkRun

console = Console()


def display_results(runs: list[BenchmarkRun], show_details: bool = False) -> None:
    """Display benchmark results as a rich table with Claude tier comparison."""
    if not runs:
        console.print("[red]No results to display[/red]")
        return

    # Main results table
    table = Table(
        title="LLM Benchmark Results",
        show_header=True,
        header_style="bold cyan",
        border_style="dim",
        pad_edge=True,
    )

    table.add_column("Test", style="white", min_width=22)
    table.add_column("Diff", justify="center", min_width=6)

    for run in runs:
        table.add_column(
            f"{run.model}\n({run.provider})",
            justify="center",
            min_width=12,
        )

    # Populate rows
    test_ids = [r.test_id for r in runs[0].results] if runs else []
    for test_id in test_ids:
        row = []
        row.append(test_id)

        # Difficulty indicator
        from llm_bench.tests.suite import get_test

        test_def = get_test(test_id)
        diff_stars = "★" * test_def.difficulty.value if test_def else ""
        row.append(diff_stars)

        # Model scores
        for run in runs:
            result = next((r for r in run.results if r.test_id == test_id), None)
            if result:
                score_text = _score_cell(result.score, result.latency_ms)
                row.append(score_text)
            else:
                row.append("—")

        table.add_row(*row)

    # Summary row
    table.add_section()
    summary_row = ["[bold]TOTAL[/bold]", ""]
    for run in runs:
        color = _score_color(run.total_score)
        summary_row.append(f"[bold {color}]{run.total_score:.2f}[/bold {color}]")
    table.add_row(*summary_row)

    console.print()
    console.print(table)
    console.print()

    console.print("[dim]PASS = full grader score; partial scores are not passes. "
                  "No inferred frontier equivalence.[/dim]")
    # Measured cohort summaries
    from llm_bench.tests import cohort_for

    for run in runs:
        for cohort in ("routine", "stress"):
            rows = [r for r in run.results if cohort_for(r.test_id) == cohort]
            if rows:
                mean = sum(r.score for r in rows) / len(rows)
                full = sum(r.score == 1.0 for r in rows)
                console.print(f"  {run.model} {cohort}: {mean:.3f} mean; "
                              f"{full}/{len(rows)} full scores")

    # Overall diagnostic only
    for run in runs:
        color = _score_color(run.total_score)
        console.print(
            f"  {run.model} ({run.provider}): "
            f"[{color}]{run.tier_equivalent}[/{color}] "
            f"— {run.total_score:.2f} avg, "
            f"{run.total_latency_ms / 1000:.1f}s total"
        )

    console.print()

    # Detailed breakdown if requested
    if show_details:
        _display_details(runs)


def display_progress(message: str) -> None:
    """Print a progress message."""
    console.print(f"  {message}")


def _display_details(runs: list[BenchmarkRun]) -> None:
    """Show per-test details including raw output snippets."""
    for run in runs:
        console.print(
            Panel(
                f"[bold]{run.model}[/bold] ({run.provider})",
                border_style="cyan",
            )
        )
        for result in run.results:
            status = "[green]PASS[/green]" if result.passed else "[red]FAIL[/red]"
            console.print(f"  {status} {result.test_id} (score={result.score:.2f})")
            if result.details:
                for k, v in result.details.items():
                    console.print(f"    {k}: {v}")
            # Truncated output
            snippet = result.raw_output[:200].replace("\n", " ")
            console.print(f"    [dim]output: {snippet}...[/dim]")
            console.print()


def _score_cell(score: float, latency_ms: float) -> str:
    """Format a score cell with color and latency."""
    color = _score_color(score)
    latency_str = f"{latency_ms / 1000:.1f}s" if latency_ms > 1000 else f"{latency_ms:.0f}ms"
    return f"[{color}]{score:.2f}[/{color}]\n[dim]{latency_str}[/dim]"


def _score_color(score: float) -> str:
    if score >= 0.8:
        return "green"
    elif score >= 0.5:
        return "yellow"
    else:
        return "red"
