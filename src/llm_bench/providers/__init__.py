"""Provider backends for talking to LLM endpoints."""

from llm_bench.providers.apfel import ApfelProvider
from llm_bench.providers.openai_compat import OpenAICompatProvider

__all__ = ["OpenAICompatProvider", "ApfelProvider", "get_provider"]


def get_provider(name: str, **kwargs):
    """Factory for provider instances."""
    providers = {
        "ollama": lambda: OpenAICompatProvider(
            base_url=kwargs.get("base_url", "http://localhost:11434/v1"),
            name="ollama",
        ),
        "apfel": lambda: ApfelProvider(),
        "openai-compat": lambda: OpenAICompatProvider(
            base_url=kwargs["base_url"],
            api_key=kwargs.get("api_key", ""),
            name=kwargs.get("name", "custom"),
        ),
        "lmstudio": lambda: OpenAICompatProvider(
            base_url=kwargs.get("base_url", "http://localhost:1234/v1"),
            name="lmstudio",
        ),
    }
    if name not in providers:
        raise ValueError(f"Unknown provider: {name}. Available: {list(providers.keys())}")
    return providers[name]()
