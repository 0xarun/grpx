"""OpenRouter provider implementation."""

from __future__ import annotations

import json
import urllib.error
import urllib.request

from .base import BaseProvider, ProviderError


class OpenRouterProvider(BaseProvider):
    def __init__(self, model: str, api_key: str, base_url: str) -> None:
        super().__init__(model)
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")

    def generate(self, prompt: str) -> str:
        url = f"{self.base_url}/chat/completions"
        payload = json.dumps({"model": self.model, "messages": [{"role": "user", "content": prompt}]}).encode("utf-8")
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "https://github.com/grpx/grpx",
            "X-Title": "grpx",
        }
        request = urllib.request.Request(url, data=payload, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                body = json.loads(response.read().decode("utf-8"))
                return body["choices"][0]["message"]["content"]
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="ignore")
            raise ProviderError(f"OpenRouter error {exc.code}: {detail}") from exc
