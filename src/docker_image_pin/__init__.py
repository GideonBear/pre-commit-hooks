from __future__ import annotations

import argparse
from argparse import ArgumentParser
from pathlib import Path
from typing import TYPE_CHECKING

from docker_image_pin import docker, gha
from docker_image_pin.classes import Logger


if TYPE_CHECKING:
    from collections.abc import Sequence


class Args(argparse.Namespace):
    hook: str
    files: Sequence[Path]


def parse_args() -> Args:
    parser = ArgumentParser("docker-image-pin")

    parser.add_argument(
        "hook",
        type=str,
        choices=("docker", "gha"),
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

        for lnr, line in enumerate(content.splitlines()):
            line_retval = process_line(file, lnr, line, args.hook)
            if line_retval == 1:
                retval = 1

    return retval


def process_line(file: Path, lnr: int, line: str, type_: str) -> int:
    logger = Logger(file, lnr)

    line = line.strip()

    allow = None
    if "# allow-" in line:
        line, allow = line.split("# allow-")
        line = line.strip()

    if type_ != "gha":  # noqa: SIM102
        # Remove all other comments. GHA expects a comment.
        if "#" in line:
            line, _comment = line.split("#", maxsplit=1)

    if allow == "all":
        return 0

    if type_ == "docker":
        return docker.process_line(line, allow, logger)
    if type_ == "gha":
        return gha.process_line(line, allow, logger)
    raise AssertionError
