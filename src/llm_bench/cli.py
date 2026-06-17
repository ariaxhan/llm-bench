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
@click.option("--agentic", is_flag=True, help="Run agentic capability tests only")
@click.option("--adversarial", is_flag=True, help="Run adversarial tests only")
@click.option("--messy", is_flag=True, help="Run real-world messy tests only")
@click.option("--full", is_flag=True, help="Run all tests (42 total)")
def run(
    models, provider, base_url, tests, details, output, category,
    hard, agentic, adversarial, messy, full,
):
    """Run benchmarks against one or more models.

    Examples:
        llm-bench run phi4:14b
        llm-bench run phi4:14b --hard
        llm-bench run phi4:14b --agentic
        llm-bench run phi4:14b --adversarial --messy
        llm-bench run phi4:14b --full --details
    """
    from llm_bench.tests import (
        ADVERSARIAL_TESTS,
        AGENTIC_TESTS,
        FULL_TESTS,
        HARD_TESTS,
        MESSY_TESTS,
    )

    # Resolve tests
    if tests:
        test_list = [get_test(t.strip()) for t in tests.split(",")]
        test_list = [t for t in test_list if t]
        if not test_list:
            console.print("[red]No valid tests found for given IDs[/red]")
            sys.exit(1)
    elif full:
        test_list = FULL_TESTS
    elif any([hard, agentic, adversarial, messy]):
        test_list = []
        if hard:
            test_list += HARD_TESTS
        if agentic:
            test_list += AGENTIC_TESTS
        if adversarial:
            test_list += ADVERSARIAL_TESTS
        if messy:
            test_list += MESSY_TESTS
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
        elif provider == "opencode" or model.startswith("opencode/"):
            p = get_provider("opencode")
            model_specs.append((p, model))
        elif provider == "claude-cli":
            p = get_provider("claude-cli")
            model_specs.append((p, model))
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
    from llm_bench.tests import (
        ADVERSARIAL_TESTS,
        AGENTIC_TESTS,
        FULL_TESTS,
        HARD_TESTS,
        MESSY_TESTS,
    )

    suites = [
        ("Standard Tests", ALL_TESTS, "cyan"),
        ("Hard Mode", HARD_TESTS, "red"),
        ("Agentic Capability", AGENTIC_TESTS, "magenta"),
        ("Adversarial", ADVERSARIAL_TESTS, "yellow"),
        ("Real-World Messy", MESSY_TESTS, "green"),
    ]

    for title, tests, color in suites:
        console.print(f"\n[bold]{title}[/bold] ({len(tests)} tests)\n")
        for t in tests:
            stars = "★" * t.difficulty.value
            console.print(
                f"  [{color}]{t.id:<30}[/{color}] "
                f"{stars:<6} [{t.category}] {t.name}"
            )

    console.print(f"\n  {len(FULL_TESTS)} tests total\n")


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


@main.command(name="score-certainty")
@click.argument("corpus", required=False)
@click.option("--json", "as_json", is_flag=True,
              help="Emit raw scored JSON instead of a markdown report")
def score_certainty(corpus, as_json):
    """Score a claims corpus on the earned-certainty axis (overconfidence lint).

    A DIFFERENT layer from `run`: `run` asks "how good is the model on a task";
    this asks "did an output earn its confidence" — performed authority vs
    earned support. Absorbed from the wrong-convergence sibling repo.

    Runs on a structured claims corpus (JSONL), NOT yet on raw `run` outputs —
    those don't carry the provenance/evidence fields it reads. See
    docs/consolidation.md. With no path, scores the bundled canonical corpus.

    Examples:
        llm-bench score-certainty
        llm-bench score-certainty my_claims.jsonl
        llm-bench score-certainty --json
    """
    from llm_bench.scoring.certainty_report import (
        default_corpus_path,
        load_claims,
        render_report,
        score_corpus,
    )

    path = corpus or default_corpus_path()
    try:
        claims = load_claims(path)
    except (OSError, ValueError) as e:
        console.print(f"[red]Could not load corpus '{path}': {e}[/red]")
        sys.exit(1)

    results = score_corpus(claims)
    if as_json:
        console.print_json(json.dumps(results))
    else:
        # plain print — the report is markdown, not Rich markup
        print(render_report(results))


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
