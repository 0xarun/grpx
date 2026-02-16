"""Built-in rule based detectors."""

from __future__ import annotations

import re
from pathlib import Path


_DETECTORS: dict[str, re.Pattern[str]] = {
    "ipv4": re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"),
    "email": re.compile(r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b"),
    "url": re.compile(r"https?://[^\s]+"),
}


def available_detectors() -> list[str]:
    return sorted(_DETECTORS)


def run_detector(name: str, file_path: str | None = None, text: str | None = None) -> list[str]:
    if name not in _DETECTORS:
        raise ValueError(f"Unknown detector '{name}'. Available: {', '.join(available_detectors())}")

    if file_path:
        content = Path(file_path).read_text(encoding="utf-8", errors="ignore")
    elif text is not None:
        content = text
    else:
        raise ValueError("Either file_path or text must be provided")

    return _DETECTORS[name].findall(content)
