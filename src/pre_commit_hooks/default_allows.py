from __future__ import annotations

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from pre_commit_hooks.classes import Logger


# TODO(GideonBear): populate these automatically from top X docker images and GH actions
default_allows = {
    "docker": {
        "debian": "major-minor",
        "postgres": "major-minor",
        "atdr.meo.ws/archiveteam/warrior-dockerfile": "latest",
        "lukaszlach/docker-tc": "latest",
    },
    "gha": {},
}


def with_default(allow: str | None, key: str, logger: Logger, type_: str) -> str | None:
    """
    Replace `allow` with the default, if any.

    Returns:
        The new value for `allow`

    """
    default_allow = default_allows[type_].get(key)
    if default_allow:
        if allow:
            logger.warn(
                "allow comment specified while "
                "there is a default allow for this image. "
                "The allow comment will be ignored. "
                f"(specified '{allow}', default '{default_allow}')"
            )
        allow = default_allow
    return allow
