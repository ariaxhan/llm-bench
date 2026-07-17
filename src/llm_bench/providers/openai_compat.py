"""OpenAI-compatible provider — works with Ollama, LM Studio, vLLM, etc."""

from __future__ import annotations

import time

import httpx

from llm_bench.providers.base import BaseProvider, LLMResponse

_HARMONY_FINAL = "<|channel|>final<|message|>"


def _extract_final_answer(content: str) -> str:
    """Unwrap raw gpt-oss harmony channel markup if the server didn't.

    Some servers (e.g. mlx_lm.server) return the raw harmony token stream as
    content: analysis-channel reasoning first, then the final channel. Grading
    the whole blob fails strict verifiers on answers that are actually correct.
    If there is no final channel, the model never finished answering — return
    empty so the verifier records an honest fail. Content without channel
    markup passes through untouched.
    """
    if _HARMONY_FINAL in content:
        final = content.rsplit(_HARMONY_FINAL, 1)[1]
        for stop in ("<|end|>", "<|return|>", "<|start|>"):
            final = final.split(stop, 1)[0]
        return final.strip()
    if "<|channel|>" in content:
        return ""
    return content


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
        # Reasoning models (gpt-oss, gemma-4, GLM) can exhaust max_tokens inside
        # the reasoning channel; servers then omit "content" entirely. Treat that
        # as an empty answer (honest fail) instead of crashing with KeyError.
        content = data["choices"][0]["message"].get("content") or ""
        content = _extract_final_answer(content)
        tokens = data.get("usage", {}).get("total_tokens", 0)

        return LLMResponse(
            content=content,
            latency_ms=elapsed_ms,
            tokens_used=tokens,
            model=model,
            raw=data,
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
