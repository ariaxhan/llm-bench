"""Benchmark test definitions — practical workflow tests."""

from llm_bench.tests.hard_suite import HARD_TESTS
from llm_bench.tests.suite import ALL_TESTS, get_test, get_tests_by_category

FULL_TESTS = ALL_TESTS + HARD_TESTS

__all__ = ["ALL_TESTS", "HARD_TESTS", "FULL_TESTS", "get_test", "get_tests_by_category"]
