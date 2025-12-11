from __future__ import annotations

import argparse
from argparse import ArgumentParser
from typing import TYPE_CHECKING

from pre_commit_hooks import docker, gha, pcad, sections, set_euo_pipefail, shfuncdecfmt
from pre_commit_hooks.logger import Logger


if TYPE_CHECKING:
    from collections.abc import Sequence
    from pathlib import Path

    from pre_commit_hooks.processors import FileProcessor


hooks: dict[str, type[FileProcessor]] = {
    "docker": docker.Processor,
    "gha": gha.Processor,
    "shfuncdecfmt": shfuncdecfmt.Processor,
    "set-euo-pipefail": set_euo_pipefail.Processor,
    "pcad": pcad.Processor,
    "sections": sections.Processor,
}


class Args(argparse.Namespace):
    hook: str
    files: Sequence[Path]


def parse_args(argv: Sequence[str] | None) -> Args:
    parser = ArgumentParser("pre-commit-hooks")

    sub = parser.add_subparsers(dest="hook", required=True)

    for hook, processor in hooks.items():
        p = sub.add_parser(hook)
        processor.add_arguments(p)

    return parser.parse_args(argv, namespace=Args())


def main(
    argv: Sequence[str] | None = None,
    *,
    logger_type: type[Logger] = Logger,
) -> int:
    args = parse_args(argv)

    processor = hooks[args.hook](args)

    retval = 0
    for file in args.files:
        content = file.read_text()

        ret = processor.process_file(file, content, logger_type=logger_type)
        if isinstance(ret, int):
            new_content = None
            file_retval = ret
        else:
            new_content, file_retval = ret

        if file_retval == 1:
            retval = 1
        if new_content is not None and new_content != content:
            file.write_text(new_content)
            retval = 1

    return retval
