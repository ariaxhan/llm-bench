"""OpenAI-compatible provider — works with Ollama, LM Studio, vLLM, etc."""

from __future__ import annotations

import time

import httpx

from llm_bench.providers.base import BaseProvider, LLMResponse


class OpenAICompatProvider(BaseProvider):
    def __init__(self, base_url: str, api_key: str = "", name: str = "openai-compat"):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.name = name

    async def complete(
        self,
        model: str,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 1024,
        temperature: float = 0.0,
    ) -> LLMResponse:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": False,
        }

        start = time.perf_counter()
        async with httpx.AsyncClient(timeout=300) as client:
            url = f"{self.base_url}/chat/completions"
            resp = await client.post(url, json=payload, headers=headers)
            resp.raise_for_status()

        elapsed_ms = (time.perf_counter() - start) * 1000
        data = resp.json()
        content = data["choices"][0]["message"]["content"]
        tokens = data.get("usage", {}).get("total_tokens", 0)

        return LLMResponse(
            content=content,
            latency_ms=elapsed_ms,
            tokens_used=tokens,
            model=model,
            raw=data,
        )

    async def converse(
        self,
        model: str,
        system_prompt: str,
        messages: list[dict],
        max_tokens: int = 1024,
        temperature: float = 0.0,
    ) -> LLMResponse:
        """Multi-turn completion. ``messages`` is ``[{"role","text"}, ...]`` (harness format),
        mapped to OpenAI ``{"role","content"}`` chat messages."""
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        chat: list[dict] = []
        if system_prompt:
            chat.append({"role": "system", "content": system_prompt})
        for m in messages:
            chat.append({"role": m["role"], "content": m["text"]})
        # mutable params so we can adapt to provider quirks (gpt-5/o-series want
        # max_completion_tokens, some models reject a non-default temperature) and retry.
        params: dict = {"max_tokens": max_tokens, "temperature": temperature}

        start = time.perf_counter()
        backoff = 2.0
        async with httpx.AsyncClient(timeout=300) as client:
            for _ in range(6):
                payload = {"model": model, "messages": chat, "stream": False, **params}
                resp = await client.post(
                    f"{self.base_url}/chat/completions", json=payload, headers=headers
                )
                if resp.status_code == 400:
                    body = resp.text.lower()
                    adapted = False
                    if "max_completion_tokens" in body and "max_tokens" in params:
                        params["max_completion_tokens"] = params.pop("max_tokens")
                        adapted = True
                    if "temperature" in body and "temperature" in params and (
                        "unsupported" in body or "does not support" in body
                        or "only the default" in body):
                        params.pop("temperature")
                        adapted = True
                    if adapted:
                        continue
                if resp.status_code == 429:
                    import asyncio
                    await asyncio.sleep(backoff)
                    backoff = min(backoff * 2, 30)
                    continue
                resp.raise_for_status()
                break
            else:
                resp.raise_for_status()  # exhausted retries
        elapsed_ms = (time.perf_counter() - start) * 1000
        data = resp.json()
        content = data["choices"][0]["message"]["content"] or ""
        usage = data.get("usage", {}) or {}
        return LLMResponse(
            content=content,
            latency_ms=elapsed_ms,
            tokens_used=usage.get("total_tokens", 0),
            model=model,
            raw=data,
            input_tokens=usage.get("prompt_tokens"),
            output_tokens=usage.get("completion_tokens"),
        )

    async def list_models(self) -> list[str]:
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(f"{self.base_url}/models")
                resp.raise_for_status()
                data = resp.json()
                return [m["id"] for m in data.get("data", data.get("models", []))]
        except Exception:
            return []

    async def is_available(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                resp = await client.get(f"{self.base_url}/models")
                return resp.status_code == 200
        except Exception:
            return False
