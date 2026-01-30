from __future__ import annotations

import string


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
