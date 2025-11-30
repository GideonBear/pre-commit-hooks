from __future__ import annotations

import tomllib
from pathlib import Path
from typing import TYPE_CHECKING

from pre_commit_hooks.classes import Invalid
from pre_commit_hooks.common import line_replace
from pre_commit_hooks.processors import LineProcessor


if TYPE_CHECKING:
    from pre_commit_hooks.classes import Logger


class Processor(LineProcessor):
    lock = Path("uv.lock")

    def __init__(self) -> None:
        super().__init__()

        with self.lock.open("rb") as f:
            data = tomllib.load(f)
        self.packages = {package["name"]: package for package in data["package"]}

        self.in_block = False

    def process_line(  # noqa: PLR0911
        self, orig_line: str, line: str, allow: str | None, logger: Logger
    ) -> tuple[str, int] | int:
        if line == "additional_dependencies:":
            self.in_block = True
            return 0

        if self.in_block:
            if not line.startswith("- "):
                self.in_block = False
                return 0

            line = line.removeprefix("- ")
            if "==" in line:
                if allow == "out-of-sync":
                    return 0
                package, version = line.split("==")
            else:
                if allow == "unsynced":
                    return 0
                package = line
                version = None

            if package not in self.packages:
                return 0

            target_version = self.packages[package]["version"]
            if target_version == version:
                return 0

            if version:
                logger.invalid(
                    Invalid(
                        "out-of-sync",
                        f"{package} is {target_version} in lockfile, "
                        f"but {version} in pre-commit-config.yaml",
                    )
                )
            else:
                logger.invalid(
                    Invalid(
                        "unsynced",
                        f"{package} is {target_version} in lockfile, "
                        f"but unpinned in pre-commit-config.yaml",
                    )
                )
            return line_replace(
                orig_line, line, f"{package}=={target_version}", logger
            ), 0

        return 0
