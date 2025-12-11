from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from argparse import ArgumentParser

    from pre_commit_hooks import Args
    from pre_commit_hooks.logger import Logger


class FileProcessor(ABC):
    def __init__(self, _args: Args) -> None:  # noqa: B027
        pass

    def process_file(
        self, file: Path, content: str, *, logger_type: type[Logger]
    ) -> tuple[str, int] | int:
        logger = logger_type.from_file(file)
        return self.process_file_internal(content, logger=logger)

    @abstractmethod
    def process_file_internal(
        self, content: str, *, logger: Logger
    ) -> tuple[str, int] | int: ...

    @classmethod
    def add_arguments(cls, parser: ArgumentParser) -> None:
        parser.add_argument(
            "files",
            nargs="+",
            type=Path,
        )


class LineProcessor(FileProcessor, ABC):
    remove_comments = True

    def process_file_internal(
        self, content: str, *, logger: Logger
    ) -> tuple[str, int] | int:
        new_content = ""
        retval = 0
        for lnr, line in enumerate(content.splitlines(keepends=True)):
            line_ret = self.process_line(lnr, line, logger=logger)
            if isinstance(line_ret, tuple):
                new_line, line_retval = line_ret
                new_content += new_line
            else:
                line_retval = line_ret
                new_content += line

            if line_retval == 1:
                retval = 1

        return new_content, retval

    def process_line(
        self,
        lnr: int,
        line: str,
        *,
        logger: Logger,
    ) -> tuple[str, int] | int:
        logger = logger.with_lnr(lnr)

        orig_line = line
        line = line.strip()

        allow = None
        if "# allow-" in line:
            line, allow = line.split("# allow-")
            line = line.strip()

        if self.remove_comments:
            if "#" in line:
                line, _comment = line.split("#", maxsplit=1)
                line = line.strip()
        elif "  #" in line:
            line, _comment = line.split("  #", maxsplit=1)
            line = line.strip()

        if allow == "all":
            return 0

        return self.process_line_internal(orig_line, line, allow, logger)

    @abstractmethod
    def process_line_internal(
        self, orig_line: str, line: str, allow: str | None, logger: Logger
    ) -> tuple[str, int] | int: ...
