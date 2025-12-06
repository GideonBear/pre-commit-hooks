from __future__ import annotations

import argparse
from argparse import ArgumentParser
from pathlib import Path
from typing import TYPE_CHECKING

from pre_commit_hooks import docker, gha, pcad, set_euo_pipefail, shfuncdecfmt
from pre_commit_hooks.classes import Logger


if TYPE_CHECKING:
    from collections.abc import Callable, Sequence

    from pre_commit_hooks.processors import FileProcessor


hooks: dict[str, type[FileProcessor]] = {
    "docker": docker.Processor,
    "gha": gha.Processor,
    "shfuncdecfmt": shfuncdecfmt.Processor,
    "set-euo-pipefail": set_euo_pipefail.Processor,
    "pcad": pcad.Processor,
}


class Args(argparse.Namespace):
    hook: str
    files: Sequence[Path]


def parse_args(argv: Sequence[str] | None) -> Args:
    parser = ArgumentParser("pre-commit-hooks")

    sub = parser.add_subparsers(dest="hook", required=True)

    pcad = sub.add_parser("pcad")
    pcad.add_argument(
        "--configs",
        dest="files",
        nargs="*",
        default=[Path(".pre-commit-config.yaml")],
        type=Path,
    )
    pcad.add_argument(
        "--lockfile",
        type=Path,
        default=Path("uv.lock"),
    )

    for hook in hooks:
        if hook == "pcad":
            continue
        p = sub.add_parser(hook)
        p.add_argument(
            "files",
            nargs="+",
            type=Path,
        )

    return parser.parse_args(argv, namespace=Args())


def main(
    argv: Sequence[str] | None = None,
    *,
    logger_type: Callable[[Path, int], Logger] = Logger,
) -> int:
    args = parse_args(argv)

    processor = hooks[args.hook](args)

    retval = 0
    for file in args.files:
        content = file.read_text()

        new_content, file_retval = processor.process_file(
            file, content, logger_type=logger_type
        )

        if file_retval == 1:
            retval = 1
        if new_content != content:
            file.write_text(new_content)
            retval = 1

    return retval
