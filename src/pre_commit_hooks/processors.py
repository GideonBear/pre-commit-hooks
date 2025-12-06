from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from collections.abc import Callable
    from pathlib import Path

    from pre_commit_hooks import Args
    from pre_commit_hooks.classes import Logger


class FileProcessor(ABC):
    def __init__(self, _args: Args) -> None:  # noqa: B027
        pass

    @abstractmethod
    def process_file(
        self, file: Path, content: str, *, logger_type: Callable[[Path, int], Logger]
    ) -> tuple[str, int]: ...


class LineProcessor(FileProcessor, ABC):
    remove_comments = True

    def process_file(
        self, file: Path, content: str, *, logger_type: Callable[[Path, int], Logger]
    ) -> tuple[str, int]:
        new_content = ""
        retval = 0
        for lnr, line in enumerate(content.splitlines(keepends=True)):
            line_ret = self.process_line_full(file, lnr, line, logger_type=logger_type)
            if isinstance(line_ret, tuple):
                new_line, line_retval = line_ret
                new_content += new_line
            else:
                line_retval = line_ret
                new_content += line

            if line_retval == 1:
                retval = 1

        return new_content, retval

    def process_line_full(
        self,
        file: Path,
        lnr: int,
        line: str,
        *,
        logger_type: Callable[[Path, int], Logger],
    ) -> tuple[str, int] | int:
        logger = logger_type(file, lnr)

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

        return self.process_line(orig_line, line, allow, logger)

    @abstractmethod
    def process_line(
        self, orig_line: str, line: str, allow: str | None, logger: Logger
    ) -> tuple[str, int] | int: ...
