from __future__ import annotations

from typing import TYPE_CHECKING

from packaging.specifiers import SpecifierSet
from tomlkit.toml_file import TOMLFile

from pre_commit_hooks.processors import FileProcessor


if TYPE_CHECKING:
    from pathlib import Path

    from pre_commit_hooks.logger import Logger


class Processor(FileProcessor):
    def process_file_path_internal(  # noqa: PLR6301
        self,
        file: Path,
        *,
        logger: Logger,
    ) -> None:
        toml_file = TOMLFile(file)
        data = toml_file.read()

        requires_python = data.get("requires-python", None) or data.get(
            "project", {}
        ).get("requires-python", None)
        if requires_python is None:
            logger.error("Couldn't find `requires-python` or `project.requires-python`")
            return
        specs = SpecifierSet(requires_python)
        if len(specs) != 1:
            logger.error("Multiple specifiers")
            return
        spec = next(iter(specs))

        if spec.version.count(".") == 2:  # noqa: PLR2004
            new_version = spec.version.rsplit(".", 1)[0]
            new = f"{spec.operator}{new_version}"
            if data.get("requires-python") is not None:
                # If the correct data is already present
                if data.get("requires-python") == new:
                    # Don't write it for performance, and to keep formatting
                    return
                data["requires-python"] = new
            else:
                # Can't use `Container` for some reason
                assert isinstance(data["project"], dict)  # noqa: S101  # we know it is because we got requires-python from it
                # If the correct data is already present
                if data["project"].get("requires-python") == new:
                    # Don't write it for performance, and to keep formatting
                    return
                data["project"]["requires-python"] = new

        toml_file.write(data)


main = Processor.main
