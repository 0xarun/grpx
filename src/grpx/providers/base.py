"""Provider abstraction layer for LLM backends."""

from __future__ import annotations

from abc import ABC, abstractmethod


class ProviderError(RuntimeError):
    """Raised when an AI provider request fails."""


class BaseProvider(ABC):
    """Interface all provider implementations must follow."""

    def __init__(self, model: str) -> None:
        self.model = model

    @abstractmethod
    def generate(self, prompt: str) -> str:
        """Generate text for a prompt."""
