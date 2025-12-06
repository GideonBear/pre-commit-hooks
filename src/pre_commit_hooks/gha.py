from __future__ import annotations

from typing import TYPE_CHECKING

from pre_commit_hooks.classes import Invalid
from pre_commit_hooks.common import (
    is_valid_sha1,
    line_replace,
    process_version,
)
from pre_commit_hooks.default_allows import with_default
from pre_commit_hooks.network import is_connected, request
from pre_commit_hooks.processors import LineProcessor


if TYPE_CHECKING:
    from pre_commit_hooks.classes import Logger


class Processor(LineProcessor):
    remove_comments = False  # GHA expects a comment.

    def process_line(  # noqa: PLR6301
        self, orig_line: str, line: str, allow: str | None, logger: Logger
    ) -> tuple[str, int] | int:
        line = line.strip().removeprefix("- ")
        if not line.startswith("uses: "):
            return 0
        line = line.removeprefix("uses: ")

        try:
            action_digest, version = line.split("#")
        except ValueError:
            return process_line_no_comment(orig_line, line, allow, logger)

        version = version.strip()
        action_digest = action_digest.strip()
        try:
            action, digest = action_digest.split("@")
        except ValueError:
            return logger.invalid("no '@'")

        if not is_valid_sha1(digest):
            return logger.invalid(f"invalid sha1 digest ('{digest}')")

        allow = with_default(allow, action, logger, "gha")

        ret = process_version_gha(
            orig_line, action, digest, version, allow, logger=logger
        )
        if ret:
            return ret

        return 0


def process_line_no_comment(  # noqa: PLR0911
    orig_line: str, line: str, allow: str | None, logger: Logger
) -> tuple[str, int] | int:
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
        return line_replace(
            orig_line, line, f"{line} # {full_version}", logger=logger
        ), retval

    if "v" in digest_or_version:
        if allow == "no-digest":
            return 0
        version = digest_or_version
        retval = logger.invalid(
            Invalid(
                "no-digest",
                f"no '#', using version ({version}) instead of digest.",
            )
        )
        digest_ret = get_digest(action, version, logger=logger)
        if digest_ret is None:
            ret = process_version_gha(
                orig_line, action, None, version, allow, logger=logger
            )
            return retval
        digest = digest_ret
        orig_line = line_replace(
            orig_line, version, f"{digest} # {version}", logger=logger
        )
        ret = process_version_gha(
            orig_line, action, digest, version, allow, logger=logger
        )
        if isinstance(ret, tuple):
            return ret
        return orig_line, retval

    if allow == "no-digest-mutable-rev":
        return 0
    return logger.invalid(
        Invalid(
            "no-digest-mutable-rev",
            f"no '#', using mutable rev ({digest_or_version}) "
            "instead of digest; "
            "use a tag if possible, otherwise pin to digest only",
        )
    )


def process_version_gha(  # noqa: PLR0913
    orig_line: str,
    action: str,
    digest: str | None,
    version: str,
    allow: str | None,
    *,
    logger: Logger,
) -> tuple[str, int] | int:
    error = process_version(version)
    if not error or error.id == allow:
        return 0

    if error.id in {"major-minor", "major", "mutable-rev"}:
        retval = logger.invalid(error)
        if digest is None:
            return retval
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

    return logger.invalid(error)


def get_full_version(action: str, digest: str, *, logger: Logger) -> str | None:
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


def get_digest(action: str, version: str, *, logger: Logger) -> str | None:  # noqa: ARG001
    if not is_connected():
        return None

    data = request(f"https://api.github.com/repos/{action}/git/ref/tags/{version}")
    return data["object"]["sha"]  # type: ignore[no-any-return]
