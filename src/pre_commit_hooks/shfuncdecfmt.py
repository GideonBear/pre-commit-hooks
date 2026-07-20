from __future__ import annotations

import re
from typing import TYPE_CHECKING

from pre_commit_hooks.processors import FileContentProcessor


if TYPE_CHECKING:
    from pre_commit_hooks.logger import Logger


class Processor(FileContentProcessor):
    def process_file_internal(  # ruff:ignore[no-self-use]
        self,
        content: str,
        *,
        logger: Logger,  # ruff:ignore[unused-method-argument]
    ) -> str | None:
        return re.sub(
            r"^(\s*)(function\s*)?([a-zA-Z_][a-zA-Z0-9_]*)\s*(?:\(\s*\))?\s*\{",
            r"\1\3() {",
            content,
            flags=re.MULTILINE,
        )


main = Processor.main
