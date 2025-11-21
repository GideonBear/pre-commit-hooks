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
    "gha": {
        # This action has a branch for each possible Rust version
        # (stable, nightly, 1.80, etc.), and does not use normal versioning.
        # Normal use includes
        # `dtolnay/rust-toolchain@stable` and `dtolnay/rust-toolchain@1.88`.
        # Let's give this a pass, even from the digest, to avoid making it
        # too confusing.
        "dtolnay/rust-toolchain": "no-digest-mutable-rev",
    },
}


def with_default(allow: str | None, key: str, logger: Logger, hook: str) -> str | None:
    """
    Replace `allow` with the default, if any.

    Returns:
        The new value for `allow`

    """
    default_allow = default_allows[hook].get(key)
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
