from __future__ import annotations

import argparse
from argparse import ArgumentParser
from pathlib import Path
from typing import TYPE_CHECKING

from pre_commit_hooks import docker, gha, shfuncdecfmt
from pre_commit_hooks.classes import Logger


if TYPE_CHECKING:
    from collections.abc import Sequence


class Args(argparse.Namespace):
    hook: str
    files: Sequence[Path]


def parse_args() -> Args:
    parser = ArgumentParser("pre-commit-hooks")

    parser.add_argument(
        "hook",
        type=str,
        choices=("docker", "gha", "shfuncdecfmt"),
    )

    parser.add_argument(
        "files",
        nargs="+",
        type=Path,
    )

    return parser.parse_args(namespace=Args())


def main() -> int:
    args = parse_args()

    retval = 0
    for file in args.files:
        content = file.read_text()

        if args.hook == "shfuncdecfmt":
            new_content = shfuncdecfmt.process_file(content)
        else:
            new_content = ""
            for lnr, line in enumerate(content.splitlines(keepends=True)):
                line_ret = process_line(file, lnr, line, args.hook)
                if isinstance(line_ret, tuple):
                    new_line, line_retval = line_ret
                    new_content += new_line
                else:
                    line_retval = line_ret
                    new_content += line

                if line_retval == 1:
                    retval = 1

        if new_content != content:
            file.write_text(new_content)
            retval = 1

    return retval


def process_line(file: Path, lnr: int, line: str, hook: str) -> tuple[str, int] | int:
    """
    Process a line.

    Returns:
        int: the return value (0 or 1)
        str: the new line (implies return value
            of 1 if it is different than the original line)

    """  # noqa: DOC501 the AssertionError is unreachable
    logger = Logger(file, lnr)

    orig_line = line
    line = line.strip()

    allow = None
    if "# allow-" in line:
        line, allow = line.split("# allow-")
        line = line.strip()

    if hook != "gha":  # noqa: SIM102
        # Remove all other comments. GHA expects a comment.
        if "#" in line:
            line, _comment = line.split("#", maxsplit=1)

    if allow == "all":
        return 0

    if hook == "docker":
        return docker.process_line(orig_line, line, allow, logger)
    if hook == "gha":
        return gha.process_line(orig_line, line, allow, logger)
    raise AssertionError
