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
async def test_null_content_returns_empty_string(monkeypatch):
    transport = _mock_transport({"role": "assistant", "content": None})
    orig_client = httpx.AsyncClient
    monkeypatch.setattr(
        httpx, "AsyncClient", lambda **kw: orig_client(transport=transport, **kw)
    )

    provider = OpenAICompatProvider(base_url="http://test/v1")
    resp = await provider.complete("m", "sys", "user")
    assert resp.content == ""
