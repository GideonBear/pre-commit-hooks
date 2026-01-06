from __future__ import annotations

import re
from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import cache
from re import Pattern
from typing import TYPE_CHECKING, ClassVar, Self

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


class OsRelease(ABC):
    types: ClassVar[list[type[OsRelease]]] = []
    # Intentionally violate types, this is an abstract classvar.
    #  Subclasses should override this.
    # noinspection PyClassVar
    releases: ClassVar[Sequence[Self]] = None  # type: ignore[assignment]

    def __init_subclass__(cls) -> None:
        cls.types.append(cls)
        super().__init_subclass__()

    @abstractmethod
    def __str__(self) -> str: ...

    @abstractmethod
    def identifier(self) -> str: ...

    def __eq__(self, other: object) -> bool:
        # This does not exclude any subclasses, since the reverse is also tried
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.identifier() == other.identifier()

    def __hash__(self) -> int:
        return hash(self.identifier())

    @abstractmethod
    def foreign_image_identifier(self) -> str: ...

    # This could be a classvar, but that's hard
    @staticmethod
    @abstractmethod
    def docker_image() -> str: ...

    # This could be a classvar, but that's hard
    @staticmethod
    @abstractmethod
    def install_command() -> str: ...

    @classmethod
    def from_from_line(cls, line: str, *, logger: Logger) -> OsRelease | None:
        for type_ in cls.types:
            ret = type_._from_from_line_single(line, logger=logger)  # noqa: SLF001
            if ret:
                return ret

        return None

    @classmethod
    def _from_from_line_single(cls, line: str, *, logger: Logger) -> OsRelease | None:
        for release in cls.releases:
            # For images like python-bookworm.
            # When using debian:bookworm, that should also get caught by from_docker_tag
            #  but is unintentionally also done here.
            if release.foreign_image_identifier() in line:
                return release

        if not line.startswith(f"{cls.docker_image()}:"):
            return None
        line = line.removeprefix(f"{cls.docker_image()}:")
        # Try to find the tag
        match = re.match(r"[a-z0-9]+", line)
        if not match:
            logger.error(f"couldn't find tag for {cls.docker_image()} image")
            return None
        return cls.from_docker_tag(match.group(), logger=logger)

    @classmethod
    @abstractmethod
    def from_docker_tag(cls, tag: str, *, logger: Logger) -> OsRelease | None: ...

    def make_env_line(self, depname: str, *, logger: Logger) -> str:
        version = self.get_version(depname, logger=logger)
        if version is None:
            version = "<insert version here>"
        return f'ENV {envilize(depname)}="{version}"\n'

    @abstractmethod
    def make_renovate_line(self, depname: str) -> str: ...

    @abstractmethod
    def get_version(self, depname: str, *, logger: Logger) -> str | None: ...

    @abstractmethod
    def from_renovate(self, os: str, *, logger: Logger) -> OsRelease | None: ...

    @staticmethod
    @abstractmethod
    def renovate_re() -> Pattern[str]: ...


DEB_PAK_RE = r"[a-z0-9][a-z0-9+\-.]+"
DEB_VER_RE = r"[^\s]+?"  # Dirty, but doesn't matter
DEB_PAK_PINNED_RE = rf"{DEB_PAK_RE}={DEB_VER_RE}"


@dataclass
class DebianRelease(OsRelease):
    numeric: str | None
    codename: str
    suite: str | None

    @staticmethod
    def docker_image() -> str:
        return "debian"

    @staticmethod
    def install_command() -> str:
        return "apt-get install"

    def identifier(self) -> str:
        return self.codename

    def __str__(self) -> str:
        return self.codename

    def foreign_image_identifier(self) -> str:
        return self.codename

    @staticmethod
    @cache
    def renovate_re() -> Pattern[str]:
        return re.compile(
            r"#\s*renovate:\s*?suite=(?P<osRelease>.*?)\s*depName=(?P<depName>.*?)($|\s)"
        )

    @classmethod
    def from_docker_tag(cls, tag: str, *, logger: Logger) -> DebianRelease | None:
        for release in cls.releases:
            if tag in {release.codename, release.numeric}:
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
        for release in cls.releases:
            if renovate in {release.codename, release.suite}:
                return release
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

    def make_renovate_line(self, depname: str) -> str:
        return f"# renovate: suite={self} depName={depname}\n"

    def get_version(self, depname: str, *, logger: Logger) -> str | None:
        if not is_connected():
            msg = "This function is only supposed to be called in connected contexts"
            raise Exception(msg)  # noqa: TRY002

        url = f"https://packages.debian.org/{self.codename}/{depname}"
        text = request(url, json=False)
        # TODO(GideonBear): example gosu: 1.17-3 (what we currently get) isn't valid,
        #  1.17-3+b4 is expected. API has the same problem.
        match = re.search(
            rf"Package: {depname} \((?P<version>{DEB_VER_RE})( and others)?\)", text
        )
        if not match:
            logger.warn(
                f"getting version for package '{depname}' from url '{url}' failed"
            )
            return None
        return match.group("version")


DebianRelease.releases = (
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


UNKNOWN_OS_MSG = (
    "the hook doesn't know what version of Debian this is. "
    "Use an image with the Debian codename in the tag (like python:3.14-trixie), "
    "or put a comment after the `FROM` line, like "
    "`# docker-apt-renovate: FROM debian:trixie`, to make the Debian version explicit."
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
        self.current_os: OsRelease | None = None
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
            assert self.current_os is not None  # noqa: S101

            return self.current_os.make_env_line(depname, logger=logger)

        if line.startswith(("FROM", "# docker-apt-renovate: FROM")):
            self.process_line_from(line, logger)
            return None

        if self.current_os and (match := self.current_os.renovate_re().match(line)):
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
        self.current_os = OsRelease.from_from_line(line, logger=logger)

    def process_line_renovate(
        self, orig_line: str, match: re.Match[str], logger: Logger
    ) -> str | None:
        if self.current_os is None:
            logger.error(UNKNOWN_OS_MSG)
            return None

        os_s = match.group("osRelease")
        depname = match.group("depName")

        os = self.current_os.from_renovate(os_s, logger=logger)
        if os is None:
            return None
        if os != self.current_os:
            logger.error(
                id="wrong-suite",
                msg=f"suite set to `{os}`, while FROM image suggests suite "
                f"`{self.current_os}`",
            )
            if is_connected():
                self.bump_version_next = depname
                return line_replace(
                    orig_line,
                    os_s,
                    str(self.current_os),
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

        if self.current_os is None:
            for os in OsRelease.types:
                if line.startswith(os.install_command()):
                    logger.error(UNKNOWN_OS_MSG)
                    return None

            return None

        if not self.in_install and line.startswith(self.current_os.install_command()):
            line = line.removeprefix(self.current_os.install_command()).strip()
            self.in_install = True

        if self.in_install:
            assert in_run is not None  # noqa: S101

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
                            self.current_os.make_renovate_line(arg)
                            + self.current_os.make_env_line(arg, logger=logger),
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
                        msg=f"Unexpected argument to "
                        f"`{self.current_os.install_command()}` found ('{arg}') "
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
