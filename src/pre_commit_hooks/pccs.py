from __future__ import annotations

from typing import TYPE_CHECKING

from pre_commit_hooks.processors import FileProcessor
from pre_commit_hooks.yaml import yaml


if TYPE_CHECKING:
    from pathlib import Path

    from pre_commit_hooks.logger import Logger


class Processor(FileProcessor):
    def process_file_path_internal(  # noqa: PLR6301
        self,
        file: Path,
        *,
        logger: Logger,  # noqa: ARG002
    ) -> None:
        with file.open("rb") as f:
            data = yaml.load(f)

        to_skip = [
            hook["id"]
            for repo in data["repos"]
            for hook in repo["hooks"]
            if "language" in hook and hook["language"] in {"unsupported", "system"}
        ]
        if not to_skip:
            return

        keys = list(data.keys())
        if "ci" not in data:
            if "minimum_pre_commit_version" in keys:
                pos = keys.index("minimum_pre_commit_version") + 1
            else:
                pos = 0
            data.insert(pos, "ci", {"skip": to_skip})
        else:
            # If the correct data is already present
            if data["ci"].get("skip") == to_skip:
                # Don't write it for performance, and to keep formatting
                return
            data["ci"]["skip"] = to_skip

        with file.open("wb") as f:
            yaml.dump(data, f)


main = Processor.main
