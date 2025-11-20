from __future__ import annotations

from typing import TYPE_CHECKING

from pre_commit_hooks.classes import Invalid
from pre_commit_hooks.common import is_valid_sha1, process_version
from pre_commit_hooks.default_allows import with_default


if TYPE_CHECKING:
    from pre_commit_hooks.classes import Logger


def process_line(line: str, allow: str | None, logger: Logger) -> int:  # noqa: PLR0911
    line = line.strip().removeprefix("- ")
    if not line.startswith("uses: "):
        return 0
    line.removeprefix("uses: ")

    try:
        action_digest, version = line.split("#")
    except ValueError:
        try:
            _, digest_or_version = line.split("@")
        except ValueError:
            return logger.invalid("no '@'")

        if is_valid_sha1(digest_or_version):
            return logger.invalid(
                Invalid(
                    "no-version",
                    "no '#' but using digest; add a comment with the used tag",
                )
            )
        if "v" in digest_or_version:
            return logger.invalid(
                Invalid(
                    "no-digest",
                    f"no '#', using version ({digest_or_version}) instead of digest. "
                    "Renovate will fix this when using 'config:best-practices'",
                )
            )
        return logger.invalid(
            Invalid(
                "mutable-rev",
                f"no '#', using mutable rev ({digest_or_version}) instead of digest; "
                "use a tag if possible, otherwise pin to digest only",
            )
        )

    version = version.strip()
    action_digest = action_digest.strip()
    try:
        action, digest = action_digest.split("@")
    except ValueError:
        return logger.invalid("no '@'")

    allow = with_default(allow, action, logger, "gha")

    error = process_version(version)
    if error:
        if error.id == allow:
            pass
        else:
            return logger.invalid(error)

    if not is_valid_sha1(digest):
        return logger.invalid(f"invalid sha1 digest ('{digest}')")

    return 0
