from __future__ import annotations

from pre_commit_hooks.logger import Error


def process_version(version: str) -> Error | None:
    version = version.removeprefix("v")  # Optional prefix
    parts = version.split(".")
    if len(parts) > 3:  # noqa: PLR2004
        # major.minor.patch.???
        return Error(
            id="weird-version",
            msg="version contains more than three parts (major.minor.patch.???)",
        )
    if len(parts) == 2:  # noqa: PLR2004
        # major.minor
        return Error(
            id="major-minor",
            msg="version contains only two parts (major.minor). "
            "Can the version be pinned further?",
        )
    if len(parts) == 1:
        if not parts[0].isdecimal():
            return Error(
                id="mutable-rev",
                msg="used revision is not a version. Can you use a tag instead?",
            )
        # major
        return Error(
            id="major",
            msg="version contains only one part (major). "
            "Can the version be pinned further?",
        )
    if len(parts) == 0:
        msg = "Unreachable"
        raise AssertionError(msg)

    assert len(parts) == 3  # noqa: PLR2004, S101
    return None
