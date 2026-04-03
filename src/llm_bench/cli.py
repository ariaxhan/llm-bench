"""CLI entry point for llm-bench."""

from __future__ import annotations

import asyncio
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import click
from rich.console import Console

from llm_bench.display import display_progress, display_results
from llm_bench.models import BenchmarkRun
from llm_bench.providers import get_provider
from llm_bench.runner import run_multi_model
from llm_bench.tests.suite import ALL_TESTS, get_test

console = Console()


@click.group()
@click.version_option()
def main():
    """llm-bench: Benchmark local/OSS LLMs against Claude tiers."""
    pass


@main.command()
@click.argument("models", nargs=-1, required=True)
@click.option("--provider", "-p", default="ollama", help="Provider: ollama, apfel, lmstudio")
@click.option("--base-url", "-u", default=None, help="Custom endpoint URL")
@click.option("--tests", "-t", default=None, help="Comma-separated test IDs (default: all)")
@click.option("--details", "-d", is_flag=True, help="Show detailed output per test")
@click.option("--output", "-o", default=None, help="Save results to JSON file")
@click.option("--category", "-c", default=None, help="Run only tests in this category")
@click.option("--hard", is_flag=True, help="Run hard mode tests only")
@click.option("--full", is_flag=True, help="Run all tests (standard + hard)")
def run(models, provider, base_url, tests, details, output, category, hard, full):
    """Run benchmarks against one or more models.

    Examples:
        llm-bench run phi4:14b qwen3.5:4b
        llm-bench run phi4:14b --hard
        llm-bench run phi4:14b --full --details
        llm-bench run apple-foundationmodel -p apfel
        llm-bench run phi4:14b -t code-gen,bug-detection
    """
    from llm_bench.tests import FULL_TESTS, HARD_TESTS

    # Resolve tests
    if tests:
        test_list = [get_test(t.strip()) for t in tests.split(",")]
        test_list = [t for t in test_list if t]
        if not test_list:
            console.print("[red]No valid tests found for given IDs[/red]")
            sys.exit(1)
    elif hard:
        test_list = HARD_TESTS
    elif full:
        test_list = FULL_TESTS
    elif category:
        test_list = [t for t in FULL_TESTS if t.category == category]
        if not test_list:
            console.print(f"[red]No tests in category '{category}'[/red]")
            sys.exit(1)
    else:
        test_list = ALL_TESTS

    console.print(f"\n[bold]llm-bench[/bold] — {len(test_list)} tests, {len(models)} model(s)\n")

    # Build model list
    model_specs = []
    for model in models:
        if model == "apple-foundationmodel" or provider == "apfel":
            p = get_provider("apfel")
            model_specs.append((p, "apple-foundationmodel"))
        else:
            kwargs = {}
            if base_url:
                kwargs["base_url"] = base_url
            p = get_provider(provider, **kwargs)
            model_specs.append((p, model))

    # Run
    runs = asyncio.run(run_multi_model(model_specs, test_list, on_progress=display_progress))

    # Display
    display_results(runs, show_details=details)

    # Save if requested
    if output:
        _save_results(runs, output)


@main.command()
@click.option("--provider", "-p", default="ollama", help="Provider to check")
@click.option("--base-url", "-u", default=None, help="Custom endpoint URL")
def models(provider, base_url):
    """List available models from a provider."""
    kwargs = {}
    if base_url:
        kwargs["base_url"] = base_url
    p = get_provider(provider, **kwargs)

    async def _list():
        available = await p.is_available()
        if not available:
            console.print(f"[red]{provider} is not available[/red]")
            return
        model_list = await p.list_models()
        console.print(f"\n[bold]{provider}[/bold] — {len(model_list)} model(s):\n")
        for m in model_list:
            console.print(f"  {m}")
        console.print()

    asyncio.run(_list())


@main.command(name="list-tests")
def list_tests():
    """List all available benchmark tests."""
    from llm_bench.tests import FULL_TESTS, HARD_TESTS

    console.print("\n[bold]Standard Tests[/bold]\n")
    for t in ALL_TESTS:
        stars = "★" * t.difficulty.value
        console.print(f"  [cyan]{t.id:<24}[/cyan] {stars:<6} [{t.category}] {t.name}")

    console.print("\n[bold]Hard Mode Tests[/bold]\n")
    for t in HARD_TESTS:
        stars = "★" * t.difficulty.value
        console.print(f"  [red]{t.id:<24}[/red] {stars:<6} [{t.category}] {t.name}")

    total = len(FULL_TESTS)
    std = len(ALL_TESTS)
    hrd = len(HARD_TESTS)
    console.print(f"\n  {total} tests total ({std} standard + {hrd} hard)\n")


@main.command()
@click.argument("test_id")
def show(test_id):
    """Show details of a specific test."""
    test = get_test(test_id)
    if not test:
        console.print(f"[red]Test '{test_id}' not found[/red]")
        sys.exit(1)

    console.print(f"\n[bold cyan]{test.name}[/bold cyan] ({test.id})")
    console.print(f"Category: {test.category}")
    console.print(f"Difficulty: {'★' * test.difficulty.value}")
    console.print(f"\n[bold]System prompt:[/bold]\n{test.system_prompt}")
    console.print(f"\n[bold]User prompt:[/bold]\n{test.user_prompt}")
    if test.reference_answer:
        console.print(f"\n[bold]Reference answer:[/bold]\n{test.reference_answer}")
    console.print()


@main.command()
@click.argument("models_arg", nargs=-1, required=True)
@click.option("--provider", "-p", default="ollama")
def quick(models_arg, provider):
    """Quick benchmark — runs only 3 key tests (tag extraction, code gen, instruction follow)."""
    quick_tests = [get_test(t) for t in ["tag-extraction", "code-gen", "instruction-follow"]]
    quick_tests = [t for t in quick_tests if t]

    console.print(f"\n[bold]llm-bench quick[/bold] — 3 tests, {len(models_arg)} model(s)\n")

    model_specs = []
    for model in models_arg:
        if provider == "apfel":
            p = get_provider("apfel")
            model_specs.append((p, "apple-foundationmodel"))
        else:
            p = get_provider(provider)
            model_specs.append((p, model))

    runs = asyncio.run(run_multi_model(model_specs, quick_tests, on_progress=display_progress))
    display_results(runs)


@main.command()
@click.argument("files", nargs=-1, required=True)
def compare(files):
    """Compare results from multiple benchmark JSON files.

    Examples:
        llm-bench compare results/*.json
    """
    from llm_bench.compare import compare_results

    compare_results(list(files))


def _save_results(runs: list[BenchmarkRun], path: str) -> None:
    """Save results to JSON."""
    output = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "runs": [],
    }
    for run in runs:
        run_data = {
            "model": run.model,
            "provider": run.provider,
            "total_score": run.total_score,
            "total_latency_ms": run.total_latency_ms,
            "tier_equivalent": run.tier_equivalent,
            "results": [
                {
                    "test_id": r.test_id,
                    "score": r.score,
                    "passed": r.passed,
                    "latency_ms": r.latency_ms,
                    "tokens_used": r.tokens_used,
                    "details": r.details,
                }
                for r in run.results
            ],
        }
        output["runs"].append(run_data)

    out_path = Path(path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(output, indent=2))
    console.print(f"\n[dim]Results saved to {path}[/dim]")


if __name__ == "__main__":
    main()
