"""Ollama provider implementation."""

from __future__ import annotations

import json
import urllib.error
import urllib.request

from .base import BaseProvider, ProviderError


class OllamaProvider(BaseProvider):
    def __init__(self, model: str, base_url: str) -> None:
        super().__init__(model)
        self.base_url = base_url.rstrip("/")

    def generate(self, prompt: str) -> str:
        url = f"{self.base_url}/api/generate"
        payload = json.dumps({"model": self.model, "prompt": prompt, "stream": False}).encode("utf-8")
        request = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"}, method="POST")
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                body = json.loads(response.read().decode("utf-8"))
                return body.get("response", "")
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="ignore")
            raise ProviderError(f"Ollama error {exc.code}: {detail}") from exc
