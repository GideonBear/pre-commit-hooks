from __future__ import annotations

from pre_commit_hooks.common import is_valid_sha256, process_version
from pre_commit_hooks.logger import Invalid, Logger
from pre_commit_hooks.processors import LineProcessor


class Processor(LineProcessor):
    # TODO(GideonBear): query and replace the version with latest, if online
    #  also add sha hashes to docker, etc.
    def process_line_internal(  # noqa: PLR6301
        self, _orig_line: str, line: str, logger: Logger
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

        logger.use_defaults("docker", "image", image)

        if version in {"latest", "stable"}:
            logger.invalid(
                Invalid(
                    version,
                    f"uses dynamic tag '{version}' instead of pinned version",
                )
            )
        else:
            if "-" in version:
                version, _extra = version.split("-")
            error = process_version(version)
            if error:
                logger.invalid(error)

        if not digest.startswith("sha256:"):
            logger.invalid("invalid digest (doesn't start with 'sha256:')")
            return
        digest = digest.removeprefix("sha256:")
        if not is_valid_sha256(digest):
            logger.invalid(f"invalid sha256 digest ('{digest}')")


main = Processor.main
