from __future__ import annotations

from typing import TYPE_CHECKING

import tomlkit
from packaging.specifiers import SpecifierSet

from pre_commit_hooks.processors import FileContentProcessor


if TYPE_CHECKING:
    from pre_commit_hooks.logger import Logger


class Processor(FileContentProcessor):
    def process_file_internal(  # noqa: PLR6301
        self,
        content: str,
        *,
        logger: Logger,
    ) -> str | None:
        data = tomlkit.loads(content)
        requires_python = data.get("project", {}).get("requires-python", None)
        if not requires_python:
            logger.invalid("Couldn't find project.requires-python")
            return None
        specs = SpecifierSet(requires_python)
        if len(specs) != 1:
            logger.invalid("Multiple specifiers")
            return None
        spec = next(iter(specs))

        if spec.version.count(".") == 2:  # noqa: PLR2004
            new_version = spec.version.rsplit(".", 1)[0]
            new = f"{spec.operator}{new_version}"
            data["project"]["requires-python"] = new  # type: ignore[index]  # we know it is because we got requires-python from it

        return tomlkit.dumps(data)
