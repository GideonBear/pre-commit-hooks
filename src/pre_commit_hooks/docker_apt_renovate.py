from __future__ import annotations

import re
from copy import copy
from dataclasses import dataclass
from typing import TYPE_CHECKING, Self

from pre_commit_hooks.common import line_replace, remove_ws_splitted_part
from pre_commit_hooks.network import is_connected, request
from pre_commit_hooks.processors import Bookmark, LineProcessor


if TYPE_CHECKING:
    from argparse import ArgumentParser
    from collections.abc import Sequence

    import pre_commit_hooks
    from pre_commit_hooks.logger import Logger

    class Args(pre_commit_hooks.processors.Args):
        indent: int


def envilize(depname: str) -> str:
    return re.sub(r"[^a-z0-9]", "", depname).upper() + "_VERSION"


def make_env_line(debian: DebianRelease, depname: str, *, logger: Logger) -> str:
    version = get_version(debian, depname, logger=logger)
    if version is None:
        version = "<insert version here>"
    return f'ENV {envilize(depname)}="{version}"\n'


def make_renovate_line(debian: DebianRelease, depname: str) -> str:
    return f"# renovate: suite={debian} depName={depname}\n"


def get_version(debian: DebianRelease, depname: str, *, logger: Logger) -> str | None:
    if not is_connected():
        msg = "This function is only supposed to be called in connected contexts"
        raise Exception(msg)  # noqa: TRY002

    url = f"https://packages.debian.org/{debian.codename}/{depname}"
    text = request(url, json=False)
    # TODO(GideonBear): example gosu: 1.17-3 (what we currently get) isn't valid,
    #  1.17-3+b4 is expected. API has the same problem.
    match = re.search(
        rf"Package: {depname} \((?P<version>{DEB_VER_RE})( and others)?\)", text
    )
    if not match:
        logger.warn(f"getting version for package '{depname}' from url '{url}' failed")
        return None
    return match.group("version")


DEB_PAK_RE = r"[a-z0-9][a-z0-9+\-.]+"
DEB_VER_RE = r"[^\s]+?"  # Dirty, but doesn't matter
DEB_PAK_PINNED_RE = rf"{DEB_PAK_RE}={DEB_VER_RE}"


@dataclass
class DebianRelease:
    numeric: str | None
    codename: str
    suite: str | None
    priority: str | None = None

    def __str__(self) -> str:
        return self.priority or self.codename

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, DebianRelease):
            return NotImplemented
        return self.codename == other.codename

    def __hash__(self) -> int:
        return hash(self.codename)

    def with_priority(self, priority: str) -> Self:
        new = copy(self)
        new.priority = priority
        return new

    @classmethod
    def stable(cls) -> DebianRelease:
        for release in DEBIAN_RELEASES:
            if release.suite == "stable":
                return release.with_priority("stable")

        msg = "Invalid DEBIAN_RELEASES, didn't find 'stable' suite"
        raise AssertionError(msg)

    @classmethod
    def from_docker_tag(cls, tag: str, *, logger: Logger) -> DebianRelease | None:
        for release in DEBIAN_RELEASES:
            if tag == release.codename:
                return release
            if tag == release.numeric:
                return release
            if tag == release.suite:
                if tag != "unstable":
                    logger.error(
                        id="dynamic-suite",
                        msg=f"using dynamic suite name ('{tag}'), which breaks this "
                        f"hook. Use the codename ('{release.codename}') "
                        f"{
                            f"or version number ('{release.numeric}') "
                            if release.numeric
                            else ''
                        }"
                        f"instead.",
                    )
                return release

        logger.error(
            id="unknown-debian-version",
            msg=f"unknown debian version '{tag}'",
        )
        return None

    @classmethod
    def from_renovate(cls, renovate: str, *, logger: Logger) -> DebianRelease | None:
        numeric_debian = None
        for release in DEBIAN_RELEASES:
            if renovate == release.codename:
                return release
            if renovate == release.suite:
                return release.with_priority(renovate)
            if renovate == release.numeric:
                numeric_debian = release

        msg = f"unknown debian version '{renovate}'"
        if numeric_debian:
            msg += (
                f" (hint: this doesn't accept numeric versions. "
                f"Did you mean '{numeric_debian}'?)"
            )
        logger.error(
            id="renovate-unknown-debian-version",
            msg=msg,
        )
        return None


DEBIAN_RELEASES: Sequence[DebianRelease] = (
    DebianRelease(None, "sid", "unstable"),
    DebianRelease("15", "duke", None),
    DebianRelease("14", "forky", "testing"),
    DebianRelease("13", "trixie", "stable"),
    DebianRelease("12", "bookworm", "oldstable"),
    DebianRelease("11", "bullseye", "oldoldstable"),
    DebianRelease("10", "buster", None),
    DebianRelease("9", "stretch", None),
    DebianRelease("8", "jessie", None),
    DebianRelease("7", "wheezy", None),
    DebianRelease("6", "squeeze", None),
    DebianRelease("5", "lenny", None),
    DebianRelease("4", "etch", None),
)


class Processor(LineProcessor):
    remove_comments = False  # renovate comments

    @classmethod
    def add_arguments(cls, parser: ArgumentParser) -> None:
        super().add_arguments(parser)
        parser.add_argument(
            "--indent",
            type=int,
            default=4,
        )

    def __init__(self, args: Args) -> None:
        self.current_debian: DebianRelease | None = None
        self.in_run: Bookmark | None = None
        self.in_install = False
        self.bump_version_next: str | None = None
        self.indent = args.indent
        super().__init__(args)

    def process_line_internal(
        self, orig_line: str, line: str, logger: Logger
    ) -> str | None:
        if self.bump_version_next:
            depname = self.bump_version_next
            self.bump_version_next = None
            if not line.startswith("ENV"):
                logger.error("line after renovate comment should start with `ENV`")
                return None

            # We checked when setting bump_version_next
            assert self.current_debian is not None  # noqa: S101

            return make_env_line(self.current_debian, depname, logger=logger)

        if line.startswith(("FROM", "# docker-apt-renovate: FROM")):
            self.process_line_from(line, logger)
            return None

        if match := re.match(
            r"#\s*renovate:\s*?suite=(?P<suite>.*?)\s*depName=(?P<depName>.*?)($|\s)",
            line,
        ):
            return self.process_line_renovate(orig_line, match, logger)

        if line.startswith("RUN"):
            # The first command can be on the same line as RUN, so we pass it along too
            self.in_run = self.bookmark()
            self.in_install = False
            line = line.removeprefix("RUN").strip()

        if self.in_run:
            return self.process_line_in_run(orig_line, line, logger)

        return None

    def process_line_from(self, line: str, logger: Logger) -> None:
        # If we find this comment, we can process the line like normal
        line = line.removeprefix("# docker-apt-renovate: ")
        line = line.removeprefix("FROM").strip()
        for release in DEBIAN_RELEASES:
            # For images like python-bookworm.
            # When using debian:bookworm, that should also get caught by below but is
            #  unintentionally also done here.
            if release.codename in line:
                self.current_debian = release
                return

        if not line.startswith("debian:"):
            # If we don't know the version, assume stable so we have something at least
            self.current_debian = DebianRelease.stable()
            return
        line = line.removeprefix("debian:")
        # Try to find the tag
        match = re.match(r"[a-z0-9]+", line)
        if not match:
            logger.error("couldn't find tag for debian image")
            return
        self.current_debian = DebianRelease.from_docker_tag(
            match.group(), logger=logger
        )

    def process_line_renovate(
        self, orig_line: str, match: re.Match[str], logger: Logger
    ) -> str | None:
        if self.current_debian is None:
            logger.error("No FROM line")
            return None

        debian = match.group("suite")
        depname = match.group("depName")

        debian = DebianRelease.from_renovate(debian, logger=logger)
        if debian is None:
            return None
        if debian != self.current_debian:
            logger.error(
                id="wrong-suite",
                msg=f"suite set to `{debian}`, while FROM image suggests suite "
                f"`{self.current_debian}`",
            )
            if is_connected():
                self.bump_version_next = depname
                return line_replace(
                    orig_line,
                    debian.codename,
                    self.current_debian.codename,
                    logger=logger,
                )

        return None

    def process_line_in_run(  # noqa: C901, PLR0912
        self, orig_line: str, line: str, logger: Logger
    ) -> str | None:
        in_run = self.in_run
        if line[-1] == "\\":
            line = line.removesuffix("\\").strip()
        else:
            self.in_run = None
            # Don't reset in_install, but we don't use that when `in_run = False`,
            #  and when setting `in_run = True`, we set `in_install = False`.

        if line.startswith("&&"):
            line = line.removeprefix("&&").strip()
            # If we were in an install, it's ended now
            self.in_install = False

        if not self.in_install and line.startswith("apt-get install"):
            line = line.removeprefix("apt-get install").strip()
            self.in_install = True

        if self.in_install:
            assert in_run is not None  # noqa: S101

            if self.current_debian is None:
                logger.error("No FROM line")
                return None

            # Kind of a hack
            if self.current_debian.priority == "stable":
                logger.warn(
                    f"assuming Debian 'stable' (currently "
                    f"'{self.current_debian.codename}'). Use an image with the Debian "
                    f"codename in the tag (like python:3.14-bookworm), or put a "
                    f"comment after the `FROM` line, like `# docker-apt-renovate: "
                    f"FROM debian:{self.current_debian.codename}`, "
                    f"to make the Debian version explicit."
                )

            if line.startswith("#"):
                return None

            args = line.split()
            new_lines = []
            for arg in args:
                if arg.startswith("-"):
                    # Some argument, like -y or --no-install-recommends
                    # (packages can't start with a dash)
                    pass
                elif re.match(DEB_PAK_PINNED_RE, arg):
                    # An already pinned package
                    pass
                elif re.match(DEB_PAK_RE, arg):
                    logger.error(id="unpinned", msg=f"'{arg}' is unpinned")

                    if is_connected():
                        in_run.write(
                            make_renovate_line(self.current_debian, arg)
                            + make_env_line(self.current_debian, arg, logger=logger),
                        )

                        replacement = f"{arg}=${{{envilize(arg)}}}"
                        if line == arg:  # If this is the only thing on this line
                            # Early return is safe here. `line == arg`, so
                            #  `len(args) == 1`, so this is the only iteration
                            return line_replace(
                                orig_line, arg, replacement, logger=logger
                            )
                        else:  # If it isn't the only thing on this line  # noqa: RET505
                            # Remove it from the line, keeping the rest intact
                            orig_line = remove_ws_splitted_part(orig_line, arg)
                            indent = " " * self.indent * 2
                            new_lines.append(f"{indent}{replacement} \\\n")
                else:
                    logger.error(
                        id="unexpected-install-arg",
                        msg=f"Unexpected argument to `apt install` found ('{arg}') "
                        f"that is not a valid package name",
                    )

            if new_lines:
                # If the original line didn't end in a backslash, remove the backslash
                #  from the last line
                if not orig_line.endswith("\\\n"):
                    new_lines[-1] = new_lines[-1].replace(" \\\n", "\n")
                # If we removed all args from the line, and nothing (or only a
                # continuation) remains, we remove the line entirely
                if orig_line.strip() not in {"\\", ""}:
                    new_lines = [orig_line, *new_lines]
                return "".join(new_lines)

        return None


main = Processor.main
