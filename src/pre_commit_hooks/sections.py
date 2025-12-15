from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from pre_commit_hooks.processors import FileContentProcessor


if TYPE_CHECKING:
    from argparse import ArgumentParser

    import pre_commit_hooks
    from pre_commit_hooks.logger import Logger

    class Args(pre_commit_hooks.Args):
        language: str


class Processor(FileContentProcessor):
    @classmethod
    def add_arguments(cls, parser: ArgumentParser) -> None:
        parser.add_argument(
            "language",
            type=str,
        )
        parser.add_argument(
            "--configs",
            dest="files",
            nargs="*",
            default=[Path(".pre-commit-config.yaml")],
            type=Path,
        )

    def __init__(self, args: Args) -> None:
        super().__init__(args)

        self.language = args.language

    def process_file_internal(
        self,
        content: str,
        *,
        logger: Logger,
    ) -> str | None:
        expected = f"# {self.language.capitalize()}"
        if not any(line.strip() == expected for line in content.splitlines()):
            logger.invalid(f"doesn't contain `{expected}` section of hooks")
            return None

        return None
