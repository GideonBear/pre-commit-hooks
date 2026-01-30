from __future__ import annotations

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from pre_commit_hooks.logger import Logger


def line_replace(line: str, a: str, b: str, *, logger: Logger) -> str:  # noqa: ARG001
    if line.count(a) == 0:
        msg = f"Expected to find {a!r} in {line!r}"
        raise Exception(msg)  # noqa: TRY002

    return line.replace(a, b, 1)


def line_append(line: str, s: str) -> str:
    line_without_newline = line.rstrip("\r\n")
    return line_without_newline + s + line[len(line_without_newline) :]
