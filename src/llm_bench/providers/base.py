"""Base provider interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class LLMResponse:
    content: str
    latency_ms: float
    tokens_used: int
    model: str
    raw: dict | None = None


class BaseProvider(ABC):
    name: str

    @abstractmethod
    async def complete(
        self,
        model: str,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 1024,
        temperature: float = 0.0,
    ) -> LLMResponse:
        ...

    @abstractmethod
    async def list_models(self) -> list[str]:
        ...

    @abstractmethod
    async def is_available(self) -> bool:
        ...
