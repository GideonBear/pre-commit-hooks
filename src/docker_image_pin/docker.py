from __future__ import annotations

from docker_image_pin.classes import Invalid, Logger
from docker_image_pin.common import is_valid_sha256, process_version
from docker_image_pin.default_allows import with_default


def process_line(line: str, allow: str | None, logger: Logger) -> int:  # noqa: C901, PLR0911
    if not line.strip().startswith(("image:", "FROM")):
        return 0

    line = line.removeprefix("image:").strip()
    line = line.removeprefix("FROM").strip()
    try:
        rest, digest = line.split("@")
    except ValueError:
        return logger.invalid("no '@'")
    try:
        image, version = rest.split(":")
    except ValueError:
        return logger.invalid("no ':' in leading part")

    allow = with_default(allow, image, logger, "docker")

    if version in {"latest", "stable"}:
        if allow != version:
            return logger.invalid(
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
            if error.id == allow:
                pass
            else:
                return logger.invalid(error)

    if not digest.startswith("sha256:"):
        return logger.invalid("invalid digest (doesn't start with 'sha256:'")
    digest = digest.removeprefix("sha256:")
    if not is_valid_sha256(digest):
        return logger.invalid(f"invalid sha256 digest ('{digest}')")

    return 0
