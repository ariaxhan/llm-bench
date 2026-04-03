"""OpenCode CLI provider — free cloud models via opencode run."""

from __future__ import annotations

import asyncio
import json
import time

from llm_bench.providers.base import BaseProvider, LLMResponse


class OpenCodeProvider(BaseProvider):
    name = "opencode"

    async def complete(
        self,
        model: str,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 1024,
        temperature: float = 0.0,
    ) -> LLMResponse:
        # opencode run doesn't support system prompts directly,
        # so we prepend it to the user prompt
        full_prompt = user_prompt
        if system_prompt:
            full_prompt = (
                f"[System instruction: {system_prompt}]\n\n{user_prompt}"
            )

        model_flag = model if "/" in model else f"opencode/{model}"

        cmd = [
            "opencode", "run",
            "-m", model_flag,
            "--format", "json",
            full_prompt,
        ]

        start = time.perf_counter()
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=300)
        elapsed_ms = (time.perf_counter() - start) * 1000

        if proc.returncode != 0:
            error = stderr.decode().strip()
            raise RuntimeError(
                f"opencode failed (exit {proc.returncode}): {error}"
            )

        # Parse JSON lines output — extract text parts
        output_text = ""
        tokens_used = 0
        for line in stdout.decode().strip().split("\n"):
            if not line.strip():
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue

            if event.get("type") == "text":
                text = event.get("part", {}).get("text", "")
                output_text += text

            if event.get("type") == "step_finish":
                tokens_info = event.get("part", {}).get("tokens", {})
                tokens_used = tokens_info.get("total", 0)

        if not output_text:
            raise RuntimeError("opencode returned no text content")

        return LLMResponse(
            content=output_text.strip(),
            latency_ms=elapsed_ms,
            tokens_used=tokens_used,
            model=model,
        )

    async def list_models(self) -> list[str]:
        try:
            proc = await asyncio.create_subprocess_exec(
                "opencode", "models",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=15)
            models = []
            for line in stdout.decode().strip().split("\n"):
                line = line.strip()
                if line and "/" in line:
                    models.append(line)
            return models
        except Exception:
            return []

    async def is_available(self) -> bool:
        try:
            proc = await asyncio.create_subprocess_exec(
                "opencode", "--version",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            await asyncio.wait_for(proc.communicate(), timeout=5)
            return proc.returncode == 0
        except Exception:
            return False
