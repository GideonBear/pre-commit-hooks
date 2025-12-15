from __future__ import annotations

import re
from typing import TYPE_CHECKING

from pre_commit_hooks.processors import FileContentProcessor


if TYPE_CHECKING:
    from pre_commit_hooks.logger import Logger


class Processor(FileContentProcessor):
    def process_file_internal(  # noqa: PLR6301
        self,
        content: str,
        *,
        logger: Logger,  # noqa: ARG002
    ) -> str | None:
        return re.sub(
            r"^(\s*)(function\s*)?([a-zA-Z_][a-zA-Z0-9_]*)\s*(?:\(\s*\))?\s*\{",
            r"\1\3() {",
            content,
            flags=re.MULTILINE,
        )
