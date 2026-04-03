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
