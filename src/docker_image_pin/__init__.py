from __future__ import annotations

import argparse
import string
from argparse import ArgumentParser
from pathlib import Path
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from collections.abc import Sequence


default_allows = {
    "debian": "major-minor",
    "postgres": "major-minor",
    "atdr.meo.ws/archiveteam/warrior-dockerfile": "latest",
    "lukaszlach/docker-tc": "latest",
}


class Args(argparse.Namespace):
    files: Sequence[Path]


def parse_args() -> Args:
    parser = ArgumentParser("docker-image-pin")

    parser.add_argument(
        "files",
        nargs="+",
        type=Path,
    )

    return parser.parse_args(namespace=Args())


def main() -> int:  # noqa: C901, PLR0912, PLR0915, FIX002, TD003  # TODO(GideonBear): extract line to function
    args = parse_args()

    retval = 0
    for file in args.files:
        content = file.read_text()

        for lnr, line in enumerate(content.splitlines()):

            def log(msg: str) -> None:
                print(f"({file}:{lnr + 1}) {msg}")  # noqa: B023

            def invalid(msg: str) -> None:
                nonlocal retval
                retval = 1
                log(f"Invalid: {msg}")

            def warn(msg: str) -> None:
                log(f"Warning: {msg}")

            line = line.strip()
            if not (line.startswith(("image:", "FROM"))):
                continue

            allow = None
            if "#" in line:
                line, comment = line.split("#")
                line = line.strip()
                comment = comment.strip()
                if comment.startswith("allow-"):
                    allow = comment.removeprefix("allow-")

            line = line.removeprefix("image:").strip()
            line = line.removeprefix("FROM").strip()
            try:
                rest, sha = line.split("@")
            except ValueError:
                invalid("no '@'")
                continue
            try:
                image, version = rest.split(":")
            except ValueError:
                invalid("no ':' in leading part")
                continue

            default_allow = default_allows.get(image)
            if default_allow:
                if allow:
                    warn(
                        "allow comment specified while "
                        "there is a default allow for this image. "
                        f"(specified '{allow}', default '{default_allow}')"
                    )
                allow = default_allow

            if version in {"latest", "stable"}:
                if allow != version:
                    invalid(
                        f"[{version}] uses dynamic tag '{version}' "
                        f"instead of pinned version"
                    )
                    continue
            else:
                if "-" in version:
                    version, _extra = version.split("-")
                version = version.removeprefix("v")  # Optional prefix
                parts = version.split(".")
                if len(parts) == 3:  # noqa: PLR2004
                    # major.minor.patch
                    continue
                if len(parts) > 3 and allow != "weird-version":  # noqa: PLR2004
                    # major.minor.patch.???0
                    invalid(
                        "[weird-version] version contains more than three parts "
                        "(major.minor.patch.???)"
                    )
                    continue
                if len(parts) == 2 and allow != "major-minor":  # noqa: PLR2004
                    # major.minor
                    invalid(
                        "[major-minor] version contains only two parts (major.minor). "
                        "Can the version be pinned further?"
                    )
                    continue
                if len(parts) == 1 and allow != "major":
                    # major
                    invalid(
                        "[major] version contains only one part (major). "
                        "Can the version be pinned further?"
                    )
                    continue
                if len(parts) == 0:
                    msg = "Unreachable"
                    raise AssertionError(msg)

            if not sha.startswith("sha256:"):
                invalid("invalid hash (doesn't start with 'sha256:'")
                continue
            sha = sha.removeprefix("sha256:")
            if not is_valid_sha256(sha):
                invalid("invalid sha256 digest")
                continue

    return retval


def is_valid_sha256(s: str) -> bool:
    return len(s) == 64 and all(c in string.hexdigits for c in s)  # noqa: PLR2004
