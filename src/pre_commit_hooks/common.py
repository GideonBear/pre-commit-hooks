from __future__ import annotations

import string

from pre_commit_hooks.logger import Error, Logger


def process_version(version: str) -> Error | None:
    version = version.removeprefix("v")  # Optional prefix
    parts = version.split(".")
    if len(parts) > 3:  # noqa: PLR2004
        # major.minor.patch.???
        return Error(
            id="weird-version",
            msg="version contains more than three parts (major.minor.patch.???)",
        )
    if len(parts) == 2:  # noqa: PLR2004
        # major.minor
        return Error(
            id="major-minor",
            msg="version contains only two parts (major.minor). "
            "Can the version be pinned further?",
        )
    if len(parts) == 1:
        if not parts[0].isdecimal():
            return Error(
                id="mutable-rev",
                msg="used revision is not a version. Can you use a tag instead?",
            )
        # major
        return Error(
            id="major",
            msg="version contains only one part (major). "
            "Can the version be pinned further?",
        )
    if len(parts) == 0:
        msg = "Unreachable"
        raise AssertionError(msg)

    return None


def line_replace(line: str, a: str, b: str, *, logger: Logger) -> str:  # noqa: ARG001
    if line.count(a) == 0:
        msg = f"Expected to find {a!r} in {line!r}"
        raise Exception(msg)  # noqa: TRY002

    return line.replace(a, b, 1)


def line_append(line: str, s: str) -> str:
    line_without_newline = line.rstrip("\r\n")
    return line_without_newline + s + line[len(line_without_newline) :]


def is_valid_sha256(s: str) -> bool:
    return len(s) == 64 and all(c in string.hexdigits for c in s)  # noqa: PLR2004


def is_valid_sha1(s: str) -> bool:
    return len(s) == 40 and all(c in string.hexdigits for c in s)  # noqa: PLR2004
