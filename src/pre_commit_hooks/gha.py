from __future__ import annotations

from typing import TYPE_CHECKING

from pre_commit_hooks.common import is_valid_sha1, line_replace
from pre_commit_hooks.common.versions import process_version
from pre_commit_hooks.logger import Error
from pre_commit_hooks.network import is_connected, request
from pre_commit_hooks.processors import LineProcessor


if TYPE_CHECKING:
    from pre_commit_hooks.logger import Logger


class Processor(LineProcessor):
    remove_comments = False  # GHA expects a comment.

    def process_line_internal(  # noqa: PLR6301
        self, orig_line: str, line: str, logger: Logger
    ) -> str | None:
        line = line.strip().removeprefix("- ")
        if not line.startswith("uses: "):
            return None
        line = line.removeprefix("uses: ")

        try:
            action_digest, version = line.split("#")
        except ValueError:
            return process_line_no_comment(orig_line, line, logger)

        version = version.strip()
        action_digest = action_digest.strip()
        try:
            action, digest = action_digest.split("@")
        except ValueError:
            logger.error("no '@'")
            return None

        if not is_valid_sha1(digest):
            logger.error(f"invalid sha1 digest ('{digest}')")
            return None

        logger.use_defaults("gha", "action", action)

        return process_version_gha(orig_line, action, digest, version, logger=logger)


def process_line_no_comment(  # noqa: PLR0911
    orig_line: str, line: str, logger: Logger
) -> str | None:
    try:
        action, digest_or_version = line.split("@")
    except ValueError:
        logger.error("no '@'")
        return None

    logger.use_defaults("gha", "action", action)

    if is_valid_sha1(digest_or_version):
        digest = digest_or_version
        if logger.error(
            id="no-version",
            msg="no '#' but using digest; add a comment with a tag",
        ):
            full_version = get_full_version(action, digest, "no-version", logger=logger)
            if full_version is not None:
                return line_replace(
                    orig_line, line, f"{line} # {full_version}", logger=logger
                )
        return None

    version = digest_or_version
    if logger.error(
        id="no-digest",
        msg=f"no '#', using tag or branch ({version}) instead of digest.",
    ):
        digest_ret = get_digest(action, version, logger=logger)
        if digest_ret is None:
            process_version_gha(orig_line, action, None, version, logger=logger)
            return None
        digest = digest_ret
        orig_line = line_replace(
            orig_line, version, f"{digest} # {version}", logger=logger
        )
        ret = process_version_gha(orig_line, action, digest, version, logger=logger)
        if ret is not None:
            return ret
        return orig_line
    return process_version_gha(orig_line, action, None, version, logger=logger)


def process_version_gha(  # noqa: PLR0911
    orig_line: str,
    action: str,
    digest: str | None,
    version: str,
    *,
    logger: Logger,
) -> str | None:
    # When allowing `main` or `master`, there's no use in trying to find a tag,
    #  as we want should be using `main` or `master` anyway. Most likely this
    #  is a `mutable-rev` error with a default allow of `main` or `master`.
    if logger.allow in {"main", "master"}:
        if version != logger.allow:
            logger.error(
                id=f"not-{logger.allow}",
                msg=f"expected {logger.allow}, as it was specified with "
                f"an `allow-` comment, or a default allow.",
            )
        return None

    error = process_version(version)
    if not error:
        return None

    if error.id in {"major-minor", "major", "mutable-rev"}:
        if version in {"main", "master"}:
            error = Error(
                id=version, msg=f"using '{version}' branch. Can you use a tag instead?"
            )

        if logger.error(error) and digest is not None:
            full_version = get_full_version(action, digest, error.id, logger=logger)
            if full_version is None:
                return None
            if full_version == version:
                logger.warn(
                    f"Autofix found no further expanded versions. "
                    f"Consider adding '# allow-{error.id}'."
                )
                return None
            return line_replace(
                orig_line,
                version,
                full_version,
                logger=logger,
            )
        return None

    logger.error(error)
    return None


def get_full_version(
    action: str,
    digest: str,
    id: str,  # noqa: A002
    *,
    logger: Logger,
) -> str | None:
    if not is_connected():
        return None

    tags = request(f"https://api.github.com/repos/{action}/tags")
    matching_tags: list[str] = [t["name"] for t in tags if t["commit"]["sha"] == digest]

    if len(matching_tags) == 0:
        logger.warn(
            f"Could not find a tag matching commit {digest}. "
            f"Consider adding `# allow-{id}`."
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


def get_digest(action: str, ref: str, *, logger: Logger) -> str | None:  # noqa: ARG001
    if not is_connected():
        return None

    data = request(f"https://api.github.com/repos/{action}/commits/{ref}")
    return data["sha"]  # type: ignore[no-any-return]


main = Processor.main
