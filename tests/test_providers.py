"""Provider response-parsing regressions."""

from __future__ import annotations

import httpx
import pytest

from llm_bench.providers.openai_compat import OpenAICompatProvider


def _mock_transport(message: dict) -> httpx.MockTransport:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={"choices": [{"message": message}], "usage": {"total_tokens": 7}},
        )

    return httpx.MockTransport(handler)


@pytest.mark.asyncio
async def test_missing_content_key_returns_empty_string(monkeypatch):
    """Reasoning models can exhaust max_tokens in the reasoning channel; the
    server then omits "content" entirely. That must be an empty answer, not a
    KeyError (which recorded score=0 / latency=0ms and hid the real cause)."""
    transport = _mock_transport({"role": "assistant", "reasoning": "thinking..."})
    orig_client = httpx.AsyncClient
    monkeypatch.setattr(
        httpx, "AsyncClient", lambda **kw: orig_client(transport=transport, **kw)
    )

    provider = OpenAICompatProvider(base_url="http://test/v1")
    resp = await provider.complete("m", "sys", "user")
    assert resp.content == ""


@pytest.mark.asyncio
async def test_harmony_markup_extracts_final_channel(monkeypatch):
    """mlx_lm.server returns gpt-oss's raw harmony stream as content. The
    verifier must see only the final-channel answer, not the analysis
    reasoning (which fails word counts and trips the prompt-echo detector)."""
    raw = (
        "<|channel|>analysis<|message|>The user wants X but developer says Y. "
        "Let me think about this at length...<|end|>"
        "<|start|>assistant<|channel|>final<|message|>THE ACTUAL ANSWER."
    )
    transport = _mock_transport({"role": "assistant", "content": raw})
    orig_client = httpx.AsyncClient
    monkeypatch.setattr(
        httpx, "AsyncClient", lambda **kw: orig_client(transport=transport, **kw)
    )

    provider = OpenAICompatProvider(base_url="http://test/v1")
    resp = await provider.complete("m", "sys", "user")
    assert resp.content == "THE ACTUAL ANSWER."


@pytest.mark.asyncio
async def test_harmony_reasoning_without_final_channel_is_empty(monkeypatch):
    raw = "<|channel|>analysis<|message|>ran out of budget while thinking"
    transport = _mock_transport({"role": "assistant", "content": raw})
    orig_client = httpx.AsyncClient
    monkeypatch.setattr(
        httpx, "AsyncClient", lambda **kw: orig_client(transport=transport, **kw)
    )

    provider = OpenAICompatProvider(base_url="http://test/v1")
    resp = await provider.complete("m", "sys", "user")
    assert resp.content == ""


@pytest.mark.asyncio
async def test_null_content_returns_empty_string(monkeypatch):
    transport = _mock_transport({"role": "assistant", "content": None})
    orig_client = httpx.AsyncClient
    monkeypatch.setattr(
        httpx, "AsyncClient", lambda **kw: orig_client(transport=transport, **kw)
    )

    provider = OpenAICompatProvider(base_url="http://test/v1")
    resp = await provider.complete("m", "sys", "user")
    assert resp.content == ""
