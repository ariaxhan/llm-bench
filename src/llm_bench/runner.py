"""Test runner — executes benchmarks against model endpoints."""

from __future__ import annotations

import traceback
from typing import Callable

from llm_bench.models import BenchmarkRun, TestCase, TestResult
from llm_bench.providers.base import BaseProvider
from llm_bench.verify import VERIFIERS


async def run_single_test(
    provider: BaseProvider,
    model: str,
    test: TestCase,
    on_progress: Callable[[str], None] | None = None,
) -> TestResult:
    """Run a single test case against a model."""
    if on_progress:
        on_progress(f"  Running: {test.name}...")

    try:
        response = await provider.complete(
            model=model,
            system_prompt=test.system_prompt,
            user_prompt=test.user_prompt,
            max_tokens=test.max_tokens,
            temperature=0.0,
        )

        # Verify the response
        verifier = VERIFIERS.get(test.verify)
        if verifier:
            score, details = verifier(response.content, test.metadata)
        else:
            score, details = 0.0, {"reason": f"no verifier for {test.verify}"}

        return TestResult(
            test_id=test.id,
            model=model,
            provider=provider.name,
            score=score,
            raw_output=response.content,
            latency_ms=response.latency_ms,
            tokens_used=response.tokens_used,
            passed=score >= 0.5,
            details=details,
        )

    except Exception as e:
        return TestResult(
            test_id=test.id,
            model=model,
            provider=provider.name,
            score=0.0,
            raw_output=f"ERROR: {e}\n{traceback.format_exc()}",
            latency_ms=0,
            tokens_used=0,
            passed=False,
            details={"error": str(e)},
        )


async def run_benchmark(
    provider: BaseProvider,
    model: str,
    tests: list[TestCase],
    on_progress: Callable[[str], None] | None = None,
) -> BenchmarkRun:
    """Run all tests sequentially against a model.

    Sequential because local models typically can't handle concurrent requests well,
    and we want accurate latency measurements.
    """
    run = BenchmarkRun(model=model, provider=provider.name)

    for test in tests:
        result = await run_single_test(provider, model, test, on_progress)
        run.results.append(result)
        if on_progress:
            status = "PASS" if result.passed else "FAIL"
            on_progress(
                f"  {status}: {test.name} — "
                f"score={result.score:.2f}, "
                f"latency={result.latency_ms:.0f}ms"
            )

    run.compute_totals()
    return run


async def run_multi_model(
    models: list[tuple[BaseProvider, str]],
    tests: list[TestCase],
    on_progress: Callable[[str], None] | None = None,
) -> list[BenchmarkRun]:
    """Run benchmarks across multiple models sequentially."""
    runs = []
    for provider, model in models:
        if on_progress:
            on_progress(f"\n{'='*50}")
            on_progress(f"Model: {model} ({provider.name})")
            on_progress(f"{'='*50}")

        run = await run_benchmark(provider, model, tests, on_progress)
        runs.append(run)

    return runs
