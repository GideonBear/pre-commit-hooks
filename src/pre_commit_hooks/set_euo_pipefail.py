from __future__ import annotations

from typing import TYPE_CHECKING

from pre_commit_hooks.processors import LineProcessor


if TYPE_CHECKING:
    from pathlib import Path

    from pre_commit_hooks.classes import Logger


class Processor(LineProcessor):
    start_part: bool

    def process_file(self, file: Path, content: str) -> tuple[str, int]:
        self.reset()
        return super().process_file(file, content)

    def reset(self) -> None:
        self.start_part = True

    def process_line(
        self, _orig_line: str, line: str, _allow: str | None, logger: Logger
    ) -> tuple[str, int] | int:
        if not self.start_part:
            return 0
        if line.startswith("#") or not line:
            return 0

        self.start_part = False
        if line != "set -euo pipefail":
            return logger.invalid("No `set -euo pipefail` found at start of script")

        return 0
