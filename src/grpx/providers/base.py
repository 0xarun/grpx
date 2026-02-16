"""Provider abstraction layer for LLM backends."""

from __future__ import annotations

import json
import urllib.error
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


def format_http_error(provider_name: str, exc: urllib.error.HTTPError) -> str:
    """Return a normalized error message with actionable billing/auth hints."""
    detail = exc.read().decode("utf-8", errors="ignore")
    message = _extract_provider_message(detail)

    hints: list[str] = []
    lower_msg = message.lower()
    if exc.code in {401, 403}:
        hints.append("check API key validity and permissions")
    if exc.code == 429:
        hints.append("rate limit hit; retry later")
    if any(word in lower_msg for word in ["quota", "insufficient", "credit", "billing", "payment"]):
        hints.append("billing/quota issue: verify payment method, balance, and plan limits")

    hint_text = f" Hint: {'; '.join(hints)}." if hints else ""
    return f"{provider_name} error {exc.code}: {message}.{hint_text}".replace("..", ".")


def _extract_provider_message(raw_body: str) -> str:
    """Extract a concise message from common provider error payloads."""
    compact = " ".join(raw_body.split())
    if not compact:
        return "empty error response"

    try:
        payload = json.loads(raw_body)
    except json.JSONDecodeError:
        return compact[:500]

    if isinstance(payload, dict):
        error_obj = payload.get("error")
        if isinstance(error_obj, dict):
            for key in ["message", "type", "code"]:
                value = error_obj.get(key)
                if isinstance(value, str) and value.strip():
                    return value.strip()
        if isinstance(error_obj, str) and error_obj.strip():
            return error_obj.strip()

        for key in ["message", "detail"]:
            value = payload.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()

    return compact[:500]
