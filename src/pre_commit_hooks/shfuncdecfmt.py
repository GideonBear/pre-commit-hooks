from __future__ import annotations

import re


def process_file(content: str) -> str:
    return re.sub(
        r"^(\s*)(function\s*)?([a-zA-Z_][a-zA-Z0-9_]*)\s*(?:\(\s*\))?\s*\{",
        r"\1\3() {",
        content,
        flags=re.MULTILINE,
    )
