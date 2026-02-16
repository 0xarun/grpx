"""Provider factory for instantiating the configured backend."""

from __future__ import annotations

from .base import BaseProvider
from .claude import ClaudeProvider
from .ollama import OllamaProvider
from .openai import OpenAIProvider
from .openrouter import OpenRouterProvider


def build_provider(config: dict) -> BaseProvider:
    provider_cfg = config["provider"]
    name = provider_cfg["name"].lower()
    model = provider_cfg["model"]

    if name == "ollama":
        return OllamaProvider(model=model, base_url=provider_cfg["ollama_url"])
    if name == "openai":
        return OpenAIProvider(model=model, api_key=provider_cfg["openai_api_key"])
    if name == "claude":
        return ClaudeProvider(model=model, api_key=provider_cfg["claude_api_key"])
    if name == "openrouter":
        return OpenRouterProvider(
            model=model,
            api_key=provider_cfg["openrouter_api_key"],
            base_url=provider_cfg["openrouter_base_url"],
        )
    raise ValueError(f"Unsupported provider: {name}")
