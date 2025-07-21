from __future__ import annotations

import argparse
import string
from argparse import ArgumentParser
from pathlib import Path
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from collections.abc import Sequence


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


def main() -> int:  # noqa: C901
    args = parse_args()

    retval = 0
    for file in args.files:

        def invalid(msg: str) -> None:
            nonlocal retval
            retval = 1
            print(f"({file}) Invalid: {msg}")  # noqa: B023

        content = file.read_text()

        for line in content.splitlines():
            line = line.strip()
            if not line.startswith("image:"):
                continue

            if "#" in line:
                line, comment = line.split("#")
                line = line.strip()
                comment = comment.strip()
                if not comment.startswith("allow-"):
                    invalid("comment on image did not start with 'allow-'")
                    continue
                allow = comment.removeprefix("allow-")
            else:
                allow = None

            line = line.removeprefix("image:").strip()
            try:
                rest, sha = line.split("@")
            except ValueError:
                invalid("no '@'")
                continue
            try:
                _url, version = rest.split(":")
            except ValueError:
                invalid("no ':' in leading part")
                continue

            if version in {"latest", "stable"} and allow != version:
                invalid(f"uses dynamic tag '{version}' instead of pinned version")
                continue

            if not sha.startswith("sha256:"):
                invalid("invalid hash (doesn't start with 'sha256:'")
                continue
            sha = sha.removeprefix("sha256:")
            if not is_valid_sha256(sha):
                invalid("invalid sha256 digest")
                continue

    return retval


def is_valid_sha256(s: str) -> bool:
    return len(s) == 64 and all(c in string.hexdigits for c in s)  # noqa: PLR2004
