from __future__ import annotations

import argparse
from abc import ABC, abstractmethod
from argparse import ArgumentParser
from pathlib import Path
from typing import TYPE_CHECKING

from pre_commit_hooks.logger import Logger


if TYPE_CHECKING:
    from collections.abc import Iterable, Sequence


class Args(argparse.Namespace):
    hook: str
    files: Sequence[Path]


class FileProcessor(ABC):
    def __init__(self, _args: Args) -> None:  # noqa: B027
        pass

    def process_files(self, files: Iterable[Path], *, logger_type: type[Logger]) -> int:
        retval = 0
        for file in files:
            retval |= self.process_file_path(file, logger_type=logger_type)
        return retval

    def process_file_path(self, file: Path, *, logger_type: type[Logger]) -> int:
        logger = logger_type.from_file(file)
        self.process_file_path_internal(file, logger=logger)
        return logger.retval

    # If files are changed, pre-commit doesn't need a non-zero exit code to
    #  mark the hook as failed, so we don't need an exit code here. Any
    #  non-modifying failures will be marked with `logger.invalid`.
    @abstractmethod
    def process_file_path_internal(self, file: Path, *, logger: Logger) -> None: ...

    @classmethod
    def add_arguments(cls, parser: ArgumentParser) -> None:
        parser.add_argument(
            "files",
            nargs="+",
            type=Path,
        )

    @classmethod
    def parse_args(cls, argv: Sequence[str] | None) -> Args:
        parser = ArgumentParser()
        cls.add_arguments(parser)
        return parser.parse_args(argv, namespace=Args())

    @classmethod
    def main(
        cls,
        argv: Sequence[str] | None = None,
        *,
        logger_type: type[Logger] = Logger,
    ) -> int:
        args = cls.parse_args(argv)
        processor = cls(args)
        return processor.process_files(args.files, logger_type=logger_type)


class FileContentProcessor(FileProcessor, ABC):
    def process_file_path_internal(self, file: Path, *, logger: Logger) -> None:
        content = file.read_text(encoding="utf-8")
        new_content = self.process_file_internal(content, logger=logger)
        if new_content is not None and new_content != content:
            file.write_text(new_content, encoding="utf-8")
            # See comment on abstract definition

    @abstractmethod
    def process_file_internal(self, content: str, *, logger: Logger) -> str | None: ...


class LineProcessor(FileContentProcessor, ABC):
    remove_comments = True

    def process_file_internal(self, content: str, *, logger: Logger) -> str:
        new_content = ""
        for lnr, line in enumerate(content.splitlines(keepends=True)):
            new_line = self.process_line(lnr, line, file_logger=logger)
            if new_line is not None:
                new_content += new_line
            else:
                new_content += line

        return new_content

    def process_line(
        self,
        lnr: int,
        line: str,
        *,
        file_logger: Logger,
    ) -> str | None:
        orig_line = line
        line = line.strip()

        allow = None
        if "# allow-" in line:
            line, rest = line.split("# allow-", maxsplit=1)
            if " " in rest:
                allow, after = rest.split(" ", maxsplit=1)
                line += after
            else:
                allow = rest
            line = line.strip()

        # Normally the logger handles allows, but with `allow-all`
        #  we can skip processing the entire line.
        if allow == "all":
            return None

        logger = file_logger.with_line(lnr, allow)

        if self.remove_comments:
            if "#" in line:
                line, _comment = line.split("#", maxsplit=1)
                line = line.strip()
        elif "  #" in line:
            line, _comment = line.split("  #", maxsplit=1)
            line = line.strip()

        ret = self.process_line_internal(orig_line, line, logger)
        file_logger.consume(logger)
        return ret

    @abstractmethod
    def process_line_internal(
        self, orig_line: str, line: str, logger: Logger
    ) -> str | None: ...
