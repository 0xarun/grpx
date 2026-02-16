"""Configuration management for grpx."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

CONFIG_DIR = Path.home() / ".grpx"
CONFIG_FILE = CONFIG_DIR / "config.json"

DEFAULT_CONFIG: dict[str, Any] = {
    "provider": {
        "name": "ollama",
        "model": "llama3",
        "ollama_url": "http://localhost:11434",
        "openai_api_key": "",
        "claude_api_key": "",
        "openrouter_api_key": "",
        "openrouter_base_url": "https://openrouter.ai/api/v1",
    },
    "threat_intel": {
        "virustotal_api_key": "",
        "abuseipdb_api_key": "",
        "ipinfo_api_key": "",
    },
    "execution": {
        "allow_content_to_ai": False,
        "max_lines": 10000,
    },
}


class ConfigManager:
    """Load and persist grpx configuration in a single JSON file."""

    def __init__(self, path: Path = CONFIG_FILE) -> None:
        self.path = path

    def load(self) -> dict[str, Any]:
        if not self.path.exists():
            self.save(DEFAULT_CONFIG)
            return json.loads(json.dumps(DEFAULT_CONFIG))

        with self.path.open("r", encoding="utf-8") as fh:
            user_cfg = json.load(fh)

        merged = json.loads(json.dumps(DEFAULT_CONFIG))
        self._deep_update(merged, user_cfg)
        return merged

    def save(self, data: dict[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2, sort_keys=True)
            fh.write("\n")

    def update(self, path: list[str], value: Any) -> dict[str, Any]:
        config = self.load()
        current: Any = config
        for key in path[:-1]:
            current = current.setdefault(key, {})
        current[path[-1]] = value
        self.save(config)
        return config

    @staticmethod
    def _deep_update(target: dict[str, Any], source: dict[str, Any]) -> None:
        for key, value in source.items():
            if isinstance(value, dict) and isinstance(target.get(key), dict):
                ConfigManager._deep_update(target[key], value)
            else:
                target[key] = value
