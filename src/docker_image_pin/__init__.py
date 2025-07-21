from __future__ import annotations

import argparse
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


def main() -> int:
    args = parse_args()

    retval = 0
    for file in args.files:
        content = file.read_text()

        new_content = content

        if new_content != content:
            file.write_text(new_content)
            retval = 1

    return retval
