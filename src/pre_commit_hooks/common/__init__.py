from __future__ import annotations

import string
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


def remove_ws_splitted_part(orig_line: str, s: str) -> str:
    to_replace = " " + s
    if to_replace not in orig_line:
        to_replace = s + " "
        if to_replace not in orig_line:
            msg = (
                "We split on whitespace, so there should be "
                "a space before or after the result. Are you "
                "using tabs or other whitespace?"
            )
            raise Exception(msg)  # noqa: TRY002
    return orig_line.replace(to_replace, "")


def is_valid_sha256(s: str) -> bool:
    return len(s) == 64 and all(c in string.hexdigits for c in s)  # noqa: PLR2004


def is_valid_sha1(s: str) -> bool:
    return len(s) == 40 and all(c in string.hexdigits for c in s)  # noqa: PLR2004
