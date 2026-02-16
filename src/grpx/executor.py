"""Execution layer for file tasks and prompt application."""

from __future__ import annotations

import json
from pathlib import Path

from grpx.file_stream import FileStreamProcessor
from grpx.providers import BaseProvider


class PromptExecutor:
    """Execute prompt workflows with local-first file processing."""

    def __init__(self, provider: BaseProvider, allow_content_to_ai: bool = False) -> None:
        self.provider = provider
        self.allow_content_to_ai = allow_content_to_ai

    def apply_to_file(
        self,
        file_path: str,
        prompt: str,
        include: str | None = None,
        exclude: str | None = None,
        max_lines: int = 5000,
    ) -> str:
        processor = FileStreamProcessor(Path(file_path), include=include, exclude=exclude)

        if self.allow_content_to_ai:
            lines = []
            for idx, line in enumerate(processor.iter_lines()):
                if idx >= max_lines:
                    break
                lines.append(line)
            model_input = (
                f"User prompt:\n{prompt}\n\n"
                f"File: {file_path}\n"
                "Content excerpt follows:\n"
                + "\n".join(lines)
            )
        else:
            summary = processor.summarize(max_lines=max_lines)
            model_input = (
                f"User prompt:\n{prompt}\n\n"
                f"File: {file_path}\n"
                "Local analysis summary (raw content not shared):\n"
                f"{json.dumps(summary, indent=2)}\n"
                "Provide recommendations based on this metadata only."
            )

        return self.provider.generate(model_input)
