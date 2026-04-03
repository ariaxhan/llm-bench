"""Compare results from multiple benchmark runs."""

from __future__ import annotations

import json
from pathlib import Path

from rich.console import Console
from rich.table import Table

from llm_bench.models import CLAUDE_BASELINES

console = Console()


def compare_results(result_files: list[str]) -> None:
    """Load and compare results from JSON files."""
    all_runs = []
    for fpath in result_files:
        data = json.loads(Path(fpath).read_text())
        for run in data["runs"]:
            all_runs.append(run)

    if not all_runs:
        console.print("[red]No results to compare[/red]")
        return

    # Build comparison table
    table = Table(
        title="Model Comparison",
        show_header=True,
        header_style="bold cyan",
        border_style="dim",
    )

    table.add_column("Test", style="white", min_width=22)

    for run in all_runs:
        table.add_column(
            f"{run['model']}\n({run['provider']})",
            justify="center",
            min_width=12,
        )

    for tier in CLAUDE_BASELINES:
        table.add_column(f"Claude {tier}", justify="center", style="dim")

    # Gather all test IDs from first run
    test_ids = [r["test_id"] for r in all_runs[0]["results"]]

    for test_id in test_ids:
        row = [test_id]
        for run in all_runs:
            result = next(
                (r for r in run["results"] if r["test_id"] == test_id),
                None,
            )
            if result:
                score = result["score"]
                latency = result["latency_ms"]
                color = _score_color(score)
                lat_str = (
                    f"{latency / 1000:.1f}s"
                    if latency > 1000
                    else f"{latency:.0f}ms"
                )
                row.append(f"[{color}]{score:.2f}[/{color}]\n[dim]{lat_str}[/dim]")
            else:
                row.append("--")

        for _tier, base in CLAUDE_BASELINES.items():
            row.append(f"[dim]{base:.2f}[/dim]")

        table.add_row(*row)

    # Summary
    table.add_section()
    summary = ["[bold]AVERAGE[/bold]"]
    for run in all_runs:
        score = run["total_score"]
        color = _score_color(score)
        summary.append(f"[bold {color}]{score:.2f}[/bold {color}]")
    for _tier, base in CLAUDE_BASELINES.items():
        summary.append(f"[dim bold]{base:.2f}[/dim bold]")
    table.add_row(*summary)

    console.print()
    console.print(table)
    console.print()

    # Tier placement
    for run in all_runs:
        tier = run["tier_equivalent"]
        score = run["total_score"]
        latency = run["total_latency_ms"]
        color = _score_color(score)
        console.print(
            f"  {run['model']} ({run['provider']}): "
            f"[{color}]{tier}[/{color}] "
            f"— {score:.2f} avg, {latency / 1000:.1f}s total"
        )

    console.print()


def _score_color(score: float) -> str:
    if score >= 0.8:
        return "green"
    elif score >= 0.5:
        return "yellow"
    else:
        return "red"
