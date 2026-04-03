"""Apple Intelligence provider via apfel CLI."""

from __future__ import annotations

import asyncio
import time

from llm_bench.providers.base import BaseProvider, LLMResponse


class ApfelProvider(BaseProvider):
    name = "apfel"

    async def complete(
        self,
        model: str,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 1024,
        temperature: float = 0.0,
    ) -> LLMResponse:
        cmd = ["apfel", "-o", "plain", "-q"]
        if system_prompt:
            cmd.extend(["-s", system_prompt])
        if max_tokens:
            cmd.extend(["--max-tokens", str(max_tokens)])
        if temperature > 0:
            cmd.extend(["--temperature", str(temperature)])
        cmd.append(user_prompt)

        start = time.perf_counter()
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=120)
        elapsed_ms = (time.perf_counter() - start) * 1000

        if proc.returncode != 0:
            error = stderr.decode().strip()
            raise RuntimeError(f"apfel failed (exit {proc.returncode}): {error}")

        content = stdout.decode().strip()
        # apfel doesn't report token counts — estimate from output
        estimated_tokens = len(content.split()) * 1.3

        return LLMResponse(
            content=content,
            latency_ms=elapsed_ms,
            tokens_used=int(estimated_tokens),
            model="apple-foundationmodel",
        )

    async def list_models(self) -> list[str]:
        try:
            proc = await asyncio.create_subprocess_exec(
                "apfel", "--model-info",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, _ = await proc.communicate()
            if "available:  yes" in stdout.decode():
                return ["apple-foundationmodel"]
            return []
        except Exception:
            return []

    async def is_available(self) -> bool:
        models = await self.list_models()
        return len(models) > 0
