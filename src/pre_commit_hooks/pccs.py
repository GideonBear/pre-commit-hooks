from __future__ import annotations

from typing import TYPE_CHECKING

from ruamel.yaml import YAML

from pre_commit_hooks.processors import FileProcessor


if TYPE_CHECKING:
    from pathlib import Path

    from pre_commit_hooks.logger import Logger


yaml = YAML()
yaml.preserve_quotes = True
yaml.indent(mapping=2, sequence=4, offset=2)


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
            pos = keys.index("ci") + 1
            key = next(iter(data["ci"].keys()))
            data["ci"].ca.items[key] = None
            data["ci"]["skip"] = to_skip

        key_after = keys[pos]
        data.yaml_set_comment_before_after_key(  # adds a blank line after
            key_after, before="\n"
        )

        with file.open("wb") as f:
            yaml.dump(data, f)


main = Processor.main
