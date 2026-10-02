"""Benchmark test definitions — practical workflow tests."""

from llm_bench.tests.adversarial_suite import ADVERSARIAL_TESTS
from llm_bench.tests.agentic_suite import AGENTIC_TESTS
from llm_bench.tests.hard_suite import HARD_TESTS
from llm_bench.tests.messy_suite import MESSY_TESTS
from llm_bench.tests.suite import ALL_TESTS, get_test, get_tests_by_category

FULL_TESTS = ALL_TESTS + HARD_TESTS + AGENTIC_TESTS + ADVERSARIAL_TESTS + MESSY_TESTS

__all__ = [
    "ALL_TESTS",
    "HARD_TESTS",
    "AGENTIC_TESTS",
    "ADVERSARIAL_TESTS",
    "MESSY_TESTS",
    "FULL_TESTS",
    "get_test",
    "get_tests_by_category",
]

# Task-shaped screening cohorts, not a measured production traffic distribution.
ROUTINE_IDS = {
    "tag-extraction", "novelty-rating", "fluff-strip", "thread-match",
    "draft-email", "code-gen", "bug-detection", "multi-step-plan", "instruction-follow",
    "messy-broken-json", "messy-typo-instructions", "messy-mixed-formats",
}
ROUTINE_TESTS = [t for t in FULL_TESTS if t.id in ROUTINE_IDS]
STRESS_TESTS = [t for t in FULL_TESTS if t.id not in ROUTINE_IDS]
BENCHMARK_REVISION = "2026-10-02-grading-v3"


def cohort_for(test_id: str) -> str:
    return "routine" if test_id in ROUTINE_IDS else "stress"
