from __future__ import annotations

import importlib
from typing import TYPE_CHECKING, cast

from pre_commit_hooks.no_short_args import known
from pre_commit_hooks.processors import FileProcessor


if TYPE_CHECKING:
    from argparse import ArgumentParser
    from pathlib import Path

    import pre_commit_hooks
    from pre_commit_hooks.logger import Logger
    from pre_commit_hooks.no_short_args.backend import Backend

    class Args(pre_commit_hooks.processors.Args):
        backend: str


class Processor(FileProcessor):
    start_part: bool

    @classmethod
    def add_arguments(cls, parser: ArgumentParser) -> None:
        super().add_arguments(parser)
        parser.add_argument(
            "--backend",
            type=str,
            default=4,
        )

    def __init__(self, args: Args) -> None:
        super().__init__(args)
        self.backend: Backend = cast("Backend", importlib.import_module(args.backend))

    def process_file_path_internal(self, file: Path, *, logger: Logger) -> None:
        matches = self.backend.get_matches(file)

        for command in matches.iter():
            if command.command in known.allowed_commands:
                continue
            for arg in command.args:
                if arg.arg in known.allowed_args:
                    continue
                if arg.arg in known.allowed[command.command]:
                    continue

                if arg.arg in known.replacements[command.command]:
                    # TODO: logger error
                    arg.fix(known.replacements[command.command][arg.arg])


main = Processor.main
