"""OpenAI provider implementation."""

from __future__ import annotations

import json
import urllib.error
import urllib.request

from .base import BaseProvider, ProviderError


class OpenAIProvider(BaseProvider):
    def __init__(self, model: str, api_key: str) -> None:
        super().__init__(model)
        self.api_key = api_key

    def generate(self, prompt: str) -> str:
        url = "https://api.openai.com/v1/chat/completions"
        payload = json.dumps(
            {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.1,
            }
        ).encode("utf-8")
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        request = urllib.request.Request(url, data=payload, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                body = json.loads(response.read().decode("utf-8"))
                return body["choices"][0]["message"]["content"]
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="ignore")
            raise ProviderError(f"OpenAI error {exc.code}: {detail}") from exc
