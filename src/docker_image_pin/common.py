from __future__ import annotations

import string

from docker_image_pin.classes import Invalid


# TODO(GideonBear): query and replace the version with latest, if online
#  also add sha hashes to docker, etc.
def process_version(version: str) -> Invalid | None:
    version = version.removeprefix("v")  # Optional prefix
    parts = version.split(".")
    if len(parts) > 3:  # noqa: PLR2004
        # major.minor.patch.???
        return Invalid(
            "weird-version",
            "version contains more than three parts (major.minor.patch.???)",
        )
    if len(parts) == 2:  # noqa: PLR2004
        # major.minor
        return Invalid(
            "major-minor",
            "version contains only two parts (major.minor). "
            "Can the version be pinned further?",
        )
    if len(parts) == 1:
        # major
        return Invalid(
            "major",
            "version contains only one part (major). "
            "Can the version be pinned further?",
        )
    if len(parts) == 0:
        msg = "Unreachable"
        raise AssertionError(msg)

    return None


def is_valid_sha256(s: str) -> bool:
    return len(s) == 64 and all(c in string.hexdigits for c in s)  # noqa: PLR2004


def is_valid_sha1(s: str) -> bool:
    return len(s) == 40 and all(c in string.hexdigits for c in s)  # noqa: PLR2004
