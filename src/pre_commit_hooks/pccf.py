from __future__ import annotations

from typing import TYPE_CHECKING

from more_itertools import peekable

from pre_commit_hooks.processors import FileContentProcessor


if TYPE_CHECKING:
    from pre_commit_hooks.logger import Logger


class Processor(FileContentProcessor):
    def process_file_internal(  # noqa: C901, PLR6301
        self,
        content: str,
        *,
        logger: Logger,  # noqa: ARG002
    ) -> str | None:
        output = ""
        it = peekable(content.splitlines(keepends=True))
        while line := next(it, None):  # noqa: PLR1702
            if line.startswith("#"):
                output += line
                continue
            if line == "\n":
                continue
            output += line
            if line.strip().endswith(":"):
                newlines = line.strip().endswith("repos:")

                while line := it.peek(None):
                    if (not line.startswith("  ")) and (line != "\n"):
                        break
                    line = next(it)
                    if line == "\n":
                        continue
                    output += line
                    if line.startswith("  - "):
                        while line := it.peek(None):
                            if (not line.startswith("    ")) and (line != "\n"):
                                break
                            line = next(it)
                            if line == "\n":
                                continue
                            output += line
                        if newlines:
                            output += "\n"

            # Newline between top-level keys
            output += "\n"

        # Make sure it ends in a single newline
        return output.strip() + "\n"


main = Processor.main
