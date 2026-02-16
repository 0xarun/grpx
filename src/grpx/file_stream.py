"""Utilities for streaming and filtering large files locally."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable


class FileStreamProcessor:
    """Stream files line-by-line and filter locally without LLM uploads."""

    def __init__(self, file_path: Path, include: str | None = None, exclude: str | None = None) -> None:
        self.file_path = file_path
        self.include = re.compile(include) if include else None
        self.exclude = re.compile(exclude) if exclude else None

    def iter_lines(self) -> Iterable[str]:
        with self.file_path.open("r", encoding="utf-8", errors="ignore") as fh:
            for line in fh:
                candidate = line.rstrip("\n")
                if self.include and not self.include.search(candidate):
                    continue
                if self.exclude and self.exclude.search(candidate):
                    continue
                yield candidate

    def summarize(self, max_lines: int = 5000) -> dict[str, int]:
        total = 0
        errors = 0
        warnings = 0
        for idx, line in enumerate(self.iter_lines()):
            if idx >= max_lines:
                break
            total += 1
            lowered = line.lower()
            if "error" in lowered:
                errors += 1
            if "warn" in lowered:
                warnings += 1
        return {"line_count": total, "error_lines": errors, "warning_lines": warnings}
