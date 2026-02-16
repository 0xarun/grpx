"""Anthropic Claude provider implementation."""

from __future__ import annotations

import json
import urllib.error
import urllib.request

from .base import BaseProvider, ProviderError


class ClaudeProvider(BaseProvider):
    def __init__(self, model: str, api_key: str) -> None:
        super().__init__(model)
        self.api_key = api_key

    def generate(self, prompt: str) -> str:
        url = "https://api.anthropic.com/v1/messages"
        payload = json.dumps(
            {
                "model": self.model,
                "max_tokens": 1024,
                "messages": [{"role": "user", "content": prompt}],
            }
        ).encode("utf-8")
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
        }
        request = urllib.request.Request(url, data=payload, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                body = json.loads(response.read().decode("utf-8"))
                return body["content"][0]["text"]
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="ignore")
            raise ProviderError(f"Claude error {exc.code}: {detail}") from exc
