from __future__ import annotations

import argparse
import string
from argparse import ArgumentParser
from pathlib import Path
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from collections.abc import Sequence


default_allows = {
    "debian": "major-minor",
    "postgres": "major-minor",
    "atdr.meo.ws/archiveteam/warrior-dockerfile": "latest",
    "lukaszlach/docker-tc": "latest",
}


class Args(argparse.Namespace):
    files: Sequence[Path]


def parse_args() -> Args:
    parser = ArgumentParser("docker-image-pin")

    parser.add_argument(
        "files",
        nargs="+",
        type=Path,
    )

    return parser.parse_args(namespace=Args())


def process_line(file: Path, lnr: int, line: str) -> int:  # noqa: C901, PLR0911, PLR0912
    def log(msg: str) -> None:
        print(f"({file}:{lnr + 1}) {msg}")

    def invalid(msg: str) -> int:
        log(f"Invalid: {msg}")
        return 1

    def warn(msg: str) -> None:
        log(f"Warning: {msg}")

    line = line.strip()
    if not (line.startswith(("image:", "FROM"))):
        return 0

    allow = None
    if "#" in line:
        line, comment = line.split("#")
        line = line.strip()
        comment = comment.strip()
        if comment.startswith("allow-"):
            allow = comment.removeprefix("allow-")

    line = line.removeprefix("image:").strip()
    line = line.removeprefix("FROM").strip()
    try:
        rest, sha = line.split("@")
    except ValueError:
        return invalid("no '@'")
    try:
        image, version = rest.split(":")
    except ValueError:
        return invalid("no ':' in leading part")

    default_allow = default_allows.get(image)
    if default_allow:
        if allow:
            warn(
                "allow comment specified while "
                "there is a default allow for this image. "
                f"(specified '{allow}', default '{default_allow}')"
            )
        allow = default_allow

    if version in {"latest", "stable"}:
        if allow != version:
            return invalid(
                f"[{version}] uses dynamic tag '{version}' instead of pinned version"
            )
    else:
        if "-" in version:
            version, _extra = version.split("-")
        version = version.removeprefix("v")  # Optional prefix
        parts = version.split(".")
        if len(parts) > 3 and allow != "weird-version":  # noqa: PLR2004
            # major.minor.patch.???
            return invalid(
                "[weird-version] version contains more than three parts "
                "(major.minor.patch.???)"
            )
        if len(parts) == 2 and allow != "major-minor":  # noqa: PLR2004
            # major.minor
            return invalid(
                "[major-minor] version contains only two parts (major.minor). "
                "Can the version be pinned further?"
            )
        if len(parts) == 1 and allow != "major":
            # major
            return invalid(
                "[major] version contains only one part (major). "
                "Can the version be pinned further?"
            )
        if len(parts) == 0:
            msg = "Unreachable"
            raise AssertionError(msg)

    if not sha.startswith("sha256:"):
        return invalid("invalid hash (doesn't start with 'sha256:'")
    sha = sha.removeprefix("sha256:")
    if not is_valid_sha256(sha):
        return invalid("invalid sha256 digest")

    return 0


def main() -> int:
    args = parse_args()

    retval = 0
    for file in args.files:
        content = file.read_text()

        for lnr, line in enumerate(content.splitlines()):
            line_retval = process_line(file, lnr, line)
            if line_retval == 1:
                retval = 1

    return retval


def is_valid_sha256(s: str) -> bool:
    return len(s) == 64 and all(c in string.hexdigits for c in s)  # noqa: PLR2004
