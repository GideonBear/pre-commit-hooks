from __future__ import annotations

import argparse
from argparse import ArgumentParser
from pathlib import Path
from typing import TYPE_CHECKING

from pre_commit_hooks import docker, gha, shfuncdecfmt


if TYPE_CHECKING:
    from collections.abc import Sequence

    from pre_commit_hooks.processors import FileProcessor


hooks: dict[str, type[FileProcessor]] = {
    "docker": docker.Processor,
    "gha": gha.Processor,
    "shfuncdecfmt": shfuncdecfmt.Processor,
}


class Args(argparse.Namespace):
    hook: str
    files: Sequence[Path]


def parse_args() -> Args:
    parser = ArgumentParser("pre-commit-hooks")

    sub = parser.add_subparsers(dest="hook", required=True)

    for hook in hooks:
        p = sub.add_parser(hook)
        p.add_argument(
            "files",
            nargs="+",
            type=Path,
        )

    return parser.parse_args(namespace=Args())


def main() -> int:
    args = parse_args()

    processor_type = hooks[args.hook]

    retval = 0
    for file in args.files:
        content = file.read_text()

        new_content, file_retval = processor_type().process_file(file, content)

        if file_retval == 1:
            retval = 1
        if new_content != content:
            file.write_text(new_content)
            retval = 1

    return retval
