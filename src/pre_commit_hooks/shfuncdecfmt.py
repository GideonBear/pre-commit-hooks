from __future__ import annotations

import re
from typing import TYPE_CHECKING

from pre_commit_hooks.processors import FileProcessor


if TYPE_CHECKING:
    from pathlib import Path


class Processor(FileProcessor):
    def process_file(self, _file: Path, content: str) -> tuple[str, int]:  # noqa: PLR6301
        return re.sub(
            r"^(\s*)(function\s*)?([a-zA-Z_][a-zA-Z0-9_]*)\s*(?:\(\s*\))?\s*\{",
            r"\1\3() {",
            content,
            flags=re.MULTILINE,
        ), 0
