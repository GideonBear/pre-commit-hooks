from __future__ import annotations

from pre_commit_hooks.common import is_valid_sha256, process_version
from pre_commit_hooks.default_allows import with_default
from pre_commit_hooks.logger import Invalid, Logger
from pre_commit_hooks.processors import LineProcessor


class Processor(LineProcessor):
    # TODO(GideonBear): query and replace the version with latest, if online
    #  also add sha hashes to docker, etc.
    def process_line_internal(  # noqa: C901, PLR6301
        self, _orig_line: str, line: str, allow: str | None, logger: Logger
    ) -> None:
        if not line.strip().startswith(("image:", "FROM")):
            return

        line = line.removeprefix("image:").strip()
        line = line.removeprefix("FROM").strip()
        try:
            rest, digest = line.split("@")
        except ValueError:
            logger.invalid("no '@'")
            return
        try:
            image, version = rest.split(":")
        except ValueError:
            logger.invalid("no ':' in leading part")
            return

        allow = with_default(allow, image, logger, "docker")

        if version in {"latest", "stable"}:
            if allow != version:
                logger.invalid(
                    Invalid(
                        version,
                        f"uses dynamic tag '{version}' instead of pinned version",
                    )
                )
                return
        else:
            if "-" in version:
                version, _extra = version.split("-")
            error = process_version(version)
            if error:
                if error.id == allow:
                    pass
                else:
                    logger.invalid(error)
                    return

        if not digest.startswith("sha256:"):
            logger.invalid("invalid digest (doesn't start with 'sha256:')")
            return
        digest = digest.removeprefix("sha256:")
        if not is_valid_sha256(digest):
            logger.invalid(f"invalid sha256 digest ('{digest}')")


main = Processor.main
