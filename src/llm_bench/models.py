"""Data models for benchmark results and test definitions."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class Difficulty(Enum):
    TRIVIAL = 1
    EASY = 2
    MEDIUM = 3
    HARD = 4
    EXTREME = 5


@dataclass
class TestCase:
    id: str
    name: str
    category: str
    difficulty: Difficulty
    system_prompt: str
    user_prompt: str
    verify: str  # name of verification function
    reference_answer: str | None = None
    max_tokens: int = 1024
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class TestResult:
    test_id: str
    model: str
    provider: str
    score: float  # 0.0 to 1.0
    raw_output: str
    latency_ms: float
    tokens_used: int
    passed: bool
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class BenchmarkRun:
    model: str
    provider: str
    results: list[TestResult] = field(default_factory=list)
    total_score: float = 0.0
    total_latency_ms: float = 0.0
    tier_equivalent: str = ""

    def compute_totals(self) -> None:
        if not self.results:
            return
        self.total_score = sum(r.score for r in self.results) / len(self.results)
        self.total_latency_ms = sum(r.latency_ms for r in self.results)
        self.tier_equivalent = "uncalibrated"
