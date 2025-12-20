from __future__ import annotations

import re
import tomllib
from pathlib import Path
from typing import TYPE_CHECKING

from pre_commit_hooks.common import line_replace
from pre_commit_hooks.logger import Error
from pre_commit_hooks.processors import LineProcessor


if TYPE_CHECKING:
    from argparse import ArgumentParser

    import pre_commit_hooks
    from pre_commit_hooks.logger import Logger

    class Args(pre_commit_hooks.processors.Args):
        lockfile: Path


def normalize_package(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


class Processor(LineProcessor):
    @classmethod
    def add_arguments(cls, parser: ArgumentParser) -> None:
        parser.add_argument(
            "--configs",
            dest="files",
            nargs="*",
            default=[Path(".pre-commit-config.yaml")],
            type=Path,
        )
        parser.add_argument(
            "--lockfile",
            type=Path,
            default=Path("uv.lock"),
        )

    def __init__(self, args: Args) -> None:
        super().__init__(args)

        with args.lockfile.open("rb") as f:
            data = tomllib.load(f)
        self.packages = {package["name"]: package for package in data["package"]}

        self.in_block = False

    def process_line_internal(  # noqa: PLR0911
        self, orig_line: str, line: str, logger: Logger
    ) -> str | None:
        if line == "additional_dependencies:":
            self.in_block = True
            return None

        if self.in_block:
            if not line.startswith("- "):
                self.in_block = False
                return None

            line = line.removeprefix("- ")
            if "==" in line:
                package, version = line.split("==")
            else:
                package = line
                version = None

            norm = normalize_package(package)
            if norm != package:
                logger.error(Error("unnormalized", f"{package} is not normalized"))
                orig_line = line_replace(orig_line, package, norm, logger=logger)
                line = line_replace(line, package, norm, logger=logger)
                package = norm

            if package not in self.packages:
                return orig_line

            target_version = self.packages[package]["version"]
            if target_version == version:
                return orig_line

            if version:
                fix = logger.error(
                    Error(
                        "out-of-sync",
                        f"{package} is {target_version} in lockfile, "
                        f"but {version} in pre-commit-config.yaml",
                    )
                )
            else:
                fix = logger.error(
                    Error(
                        "unsynced",
                        f"{package} is {target_version} in lockfile, "
                        f"but unpinned in pre-commit-config.yaml",
                    )
                )
            if fix:
                return line_replace(
                    orig_line, line, f"{package}=={target_version}", logger=logger
                )
            return orig_line

        return None


main = Processor.main
