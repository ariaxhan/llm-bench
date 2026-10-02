"""Subscription-backed Codex control; same prompts, with CLI harness caveats.

Runs outside the repository with replacement instructions and no user config.
Temperature/max_tokens are unsupported by this CLI and are not enforced.
Any observed tool execution invalidates the response rather than earning credit.
"""

from __future__ import annotations

import asyncio
import json
import tempfile
import time
from pathlib import Path

from llm_bench.providers.base import BaseProvider, LLMResponse


def parse_events(stdout: str) -> tuple[str, int]:
    answers = []
    tokens = 0
    completed = False
    for line in stdout.splitlines():
        event = json.loads(line)
        kind = event.get("type")
        if kind in {"error", "turn.failed"}:
            raise RuntimeError(f"Codex failed: {event}")
        if kind == "item.completed":
            item = event["item"]
            if item["type"] == "agent_message":
                answers.append(item["text"])
            elif item["type"] != "reasoning":
                raise RuntimeError(f"Control used a tool/non-answer item: {item['type']}")
        if kind == "turn.completed":
            completed = True
            usage = event.get("usage", {})
            tokens = usage.get("input_tokens", 0) + usage.get("output_tokens", 0)
    if not completed or not answers:
        raise RuntimeError("Codex returned no completed answer")
    return answers[-1].strip(), tokens


class CodexCLIProvider(BaseProvider):
    name = "codex-cli"

    async def complete(self, model, system_prompt, user_prompt,
                       max_tokens=1024, temperature=0.0) -> LLMResponse:
        with tempfile.TemporaryDirectory(prefix="llm-bench-codex-") as directory:
            instructions = Path(directory) / "instructions.txt"
            instructions.write_text(system_prompt or "Answer the user's request.")
            cmd = [
                "codex", "exec", "--ignore-user-config", "--ephemeral",
                "--skip-git-repo-check", "--sandbox", "read-only", "--json",
                "--model", model, "--cd", directory,
                "-c", f"model_instructions_file={json.dumps(str(instructions))}",
                "-c", "project_doc_max_bytes=0",
                "-c", "suppress_unstable_features_warning=true",
                "-c", 'model_reasoning_effort="medium"',
                "-c", 'web_search="disabled"',
            ]
            for feature in ("shell_tool", "apps", "plugins", "hooks", "multi_agent",
                            "browser_use", "computer_use", "image_generation", "memories"):
                cmd += ["--disable", feature]
            cmd += ["--enable", "skip_host_skill_discovery", "-"]
            start = time.perf_counter()
            proc = await asyncio.create_subprocess_exec(
                *cmd, stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE,
            )
            try:
                stdout, stderr = await asyncio.wait_for(
                    proc.communicate(user_prompt.encode()), timeout=300,
                )
            except (asyncio.TimeoutError, asyncio.CancelledError):
                proc.kill()
                await proc.wait()
                raise
            if proc.returncode:
                raise RuntimeError(f"Codex exit {proc.returncode}: {stderr.decode()[-500:]}")
            content, tokens = parse_events(stdout.decode())
            return LLMResponse(
                content=content, latency_ms=(time.perf_counter() - start) * 1000,
                tokens_used=tokens, model=model,
            )

    async def list_models(self) -> list[str]:
        return ["gpt-6.1-sol"]

    async def is_available(self) -> bool:
        try:
            proc = await asyncio.create_subprocess_exec(
                "codex", "login", "status", stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            await asyncio.wait_for(proc.communicate(), timeout=10)
            return proc.returncode == 0
        except (OSError, asyncio.TimeoutError):
            return False
