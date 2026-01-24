from __future__ import annotations

import re
import tomllib
from pathlib import Path
from typing import TYPE_CHECKING

from packaging.requirements import Requirement

from pre_commit_hooks.processors import FileProcessor
from pre_commit_hooks.yaml import yaml


if TYPE_CHECKING:
    from argparse import ArgumentParser

    from ruamel.yaml import CommentedMap  # type: ignore[attr-defined]

    import pre_commit_hooks
    from pre_commit_hooks.logger import Logger

    class Args(pre_commit_hooks.processors.Args):
        pyproject: Path
        lockfile: Path


def normalize_package(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


class Processor(FileProcessor):
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
            "--pyproject",
            type=Path,
            default=Path("pyproject.toml"),
        )
        parser.add_argument(
            "--lockfile",
            type=Path,
            default=Path("uv.lock"),
        )

    def __init__(self, args: Args) -> None:
        super().__init__(args)

        with args.pyproject.open("rb") as f:
            pyproject_data = tomllib.load(f)

        requirements = list(map(Requirement, pyproject_data["project"]["dependencies"]))
        for requirement in requirements:
            if requirement.url:
                msg = "Requirement urls not supported"
                raise Exception(msg)  # noqa: TRY002
            if requirement.marker:
                msg = "Requirement markers not supported"
                raise Exception(msg)  # noqa: TRY002

        if (
            "dependency-groups" in pyproject_data
            and "typecheck" in pyproject_data["dependency-groups"]
        ):
            self.typecheck_requirements = list(
                map(Requirement, pyproject_data["dependency-groups"]["typecheck"])
            )
        else:
            self.typecheck_requirements = []

        with args.lockfile.open("rb") as f:
            lockfile_data = tomllib.load(f)
        lockfile_packages = {
            package["name"]: package for package in lockfile_data["package"]
        }

        self.additional_deps = [
            self.get_dep(requirement.name, lockfile_packages)
            for requirement in requirements
        ]

    def get_dep(self, pak: str, lockfile_packages: dict[str, dict[str, str]]) -> str:
        for tc_req in self.typecheck_requirements:
            # Normally types-X, sometimes types-X-ts
            if pak.lower() in tc_req.name.lower():
                pak = tc_req.name
                break

        lockfile_version = lockfile_packages[pak.lower()]["version"]

        return f"{pak}=={lockfile_version}"

    def process_file_path_internal(self, file: Path, *, logger: Logger) -> None:  # noqa: ARG002
        with file.open("rb") as f:
            data = yaml.load(f)

        repos = data["repos"]
        mypy: CommentedMap
        mypy = next(
            hook
            for repo_i, repo in enumerate(repos)
            for hook in repo["hooks"]
            if hook["id"] == "mypy"
        )

        additional_dependencies = self.additional_deps or None
        # If the correct data is already present
        if mypy.get("additional_dependencies") == additional_dependencies:
            # Don't write it for performance, and to keep formatting
            return

        if additional_dependencies:
            mypy["additional_dependencies"] = additional_dependencies
        else:
            mypy.pop("additional_dependencies")

        with file.open("wb") as f:
            yaml.dump(data, f)


main = Processor.main
