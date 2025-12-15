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

    def process_file(self, content: str, *, logger: Logger) -> str | None:
        return self.process_file_internal(content, logger=logger)

    @abstractmethod
    def process_file_internal(self, content: str, *, logger: Logger) -> str | None: ...

    @classmethod
    def add_arguments(cls, parser: ArgumentParser) -> None:
        parser.add_argument(
            "files",
            nargs="+",
            type=Path,
        )


class LineProcessor(FileProcessor, ABC):
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
        logger = file_logger.with_lnr(lnr)

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
            return None

        ret = self.process_line_internal(orig_line, line, allow, logger)
        file_logger.consume(logger)
        return ret

    @abstractmethod
    def process_line_internal(
        self, orig_line: str, line: str, allow: str | None, logger: Logger
    ) -> str | None: ...
