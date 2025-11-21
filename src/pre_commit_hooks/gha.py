from __future__ import annotations

from typing import TYPE_CHECKING

from pre_commit_hooks.classes import Invalid
from pre_commit_hooks.common import (
    is_valid_sha1,
    line_append,
    line_replace,
    process_version,
)
from pre_commit_hooks.default_allows import with_default
from pre_commit_hooks.network import is_connected, request


if TYPE_CHECKING:
    from pre_commit_hooks.classes import Logger


def process_line(  # noqa: PLR0911, C901, PLR0912
    orig_line: str, line: str, allow: str | None, logger: Logger
) -> tuple[str, int] | int:
    line = line.strip().removeprefix("- ")
    if not line.startswith("uses: "):
        return 0
    line = line.removeprefix("uses: ")

    try:
        action_digest, version = line.split("#")
    except ValueError:
        try:
            action, digest_or_version = line.split("@")
        except ValueError:
            return logger.invalid("no '@'")

        allow = with_default(allow, action, logger, "gha")

        if is_valid_sha1(digest_or_version):
            if allow == "no-version":
                return 0
            digest = digest_or_version
            retval = logger.invalid(
                Invalid(
                    "no-version",
                    "no '#' but using digest; add a comment with a tag",
                )
            )
            full_version = get_full_version(action, digest, logger=logger)
            if full_version is None:
                return retval
            return line_append(orig_line, f" # {full_version}"), retval

        if "v" in digest_or_version:
            if allow == "no-digest":
                return 0
            return logger.invalid(
                Invalid(
                    "no-digest",
                    f"no '#', using version ({digest_or_version}) instead of digest. "
                    "Renovate will fix this when using 'config:best-practices'",
                )
            )

        if allow == "no-digest-mutable-rev":
            return 0
        return logger.invalid(
            Invalid(
                "no-digest-mutable-rev",
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
        elif error.id in {"major-minor", "major", "mutable-rev"}:
            retval = logger.invalid(error)
            full_version = get_full_version(action, digest, logger=logger)
            if full_version is None:
                return retval
            if full_version == version:
                logger.warn(
                    f"Autofix found no further expanded versions. "
                    f"Consider adding '# allow-{error.id}'."
                )
                return retval
            return (
                line_replace(
                    orig_line,
                    version,
                    full_version,
                    logger=logger,
                ),
                retval,
            )
        else:
            return logger.invalid(error)

    if not is_valid_sha1(digest):
        return logger.invalid(f"invalid sha1 digest ('{digest}')")

    return 0


def get_full_version(action: str, digest: str, logger: Logger) -> str | None:
    if not is_connected():
        return None

    tags = request(f"https://api.github.com/repos/{action}/tags")
    matching_tags: list[str] = [t["name"] for t in tags if t["commit"]["sha"] == digest]

    if len(matching_tags) == 0:
        logger.warn(
            f"Could not find a tag matching commit {digest}. "
            f"Consider adding `# allow-something`."
        )
        return None
    if len(matching_tags) == 1:
        return matching_tags[0]

    for tag in matching_tags:
        if process_version(tag) is None:
            return tag

    logger.warn(
        f"Found multiple tags for commit {digest}: "
        f"{', '.join(matching_tags)}; but all of them do not satisfy"
    )

    return None
