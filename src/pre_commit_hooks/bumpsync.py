from __future__ import annotations

import re
import tomllib
from pathlib import Path
from typing import TYPE_CHECKING

from pre_commit_hooks.processors import LineProcessor


if TYPE_CHECKING:
    from argparse import ArgumentParser

    import pre_commit_hooks
    from pre_commit_hooks.logger import Logger

    class Args(pre_commit_hooks.processors.Args):
        pyproject: Path


class Processor(LineProcessor):
    @classmethod
    def add_arguments(cls, parser: ArgumentParser) -> None:
        super().add_arguments(parser)
        parser.add_argument(
            "--pyproject",
            type=Path,
            default=Path("pyproject.toml"),
        )

    def __init__(self, args: Args) -> None:
        super().__init__(args)

        with args.pyproject.open("rb") as f:
            data = tomllib.load(f)
        self.version = data["project"]["version"]
        self.looking_for: list[tuple[str, str]] = []

    def process_line_internal(
        self, orig_line: str, _line: str, _logger: Logger
    ) -> str | None:
        match = re.search(r'bumpsync: "(.*?)"', orig_line)
        if match:
            m = match.group(1)
            self.looking_for.append((
                m.format(self.version),
                m.format(r"[0-9]+\.[0-9]+\.[0-9]+"),
            ))

        for replace_with, search_for in self.looking_for:
            new_line = re.sub(search_for, replace_with, orig_line)
            if new_line != orig_line:
                # Totally invalidating the iterator here, but we return anyway
                self.looking_for.remove((replace_with, search_for))
                return new_line

        return None


main = Processor.main
