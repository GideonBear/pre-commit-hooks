from __future__ import annotations

import re
from typing import TYPE_CHECKING

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


def make_env_line(debian: str, depname: str, *, logger: Logger) -> str:
    version = get_version(debian, depname, logger=logger)
    if version is None:
        version = "<insert version here>"
    return f'ENV {envilize(depname)}="{version}"\n'


def make_renovate_line(debian: str, depname: str) -> str:
    return f"# renovate: suite={debian} depName={depname}\n"


def get_version(debian: str, depname: str, *, logger: Logger) -> str | None:
    if not is_connected():
        msg = "This function is only supposed to be called in connected contexts"
        raise Exception(msg)  # noqa: TRY002

    url = f"https://packages.debian.org/{debian}/{depname}"
    text = request(url, json=False)
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

debian_releases: Sequence[tuple[str | None, str, str | None]] = (
    (None, "sid", "unstable"),
    ("15", "duke", None),
    ("14", "forky", "testing"),
    ("13", "trixie", "stable"),
    ("12", "bookworm", "oldstable"),
    ("11", "bullseye", "oldoldstable"),
    ("10", "buster", None),
    ("9", "stretch", None),
    ("8", "jessie", None),
    ("7", "wheezy", None),
    ("6", "squeeze", None),
    ("5", "lenny", None),
    ("4", "etch", None),
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
        self.current_debian: str | None = None
        self.in_run: Bookmark | None = None
        self.in_install = False
        self.bump_version_next: tuple[str, str] | None = None
        self.indent = args.indent
        super().__init__(args)

    def process_line_internal(
        self, orig_line: str, line: str, logger: Logger
    ) -> str | None:
        if self.bump_version_next:
            debian, depname = self.bump_version_next
            self.bump_version_next = None
            if not line.startswith("ENV"):
                logger.error("line after renovate comment should start with `ENV`")
                return None

            return make_env_line(debian, depname, logger=logger)

        if line.startswith("FROM"):
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
        line = line.removeprefix("FROM").strip()
        for _version_no, codename, _suite_name in debian_releases:
            if codename in line:
                self.current_debian = codename
                return

        if not line.startswith("debian:"):
            self.current_debian = "stable"
            return
        line = line.removeprefix("debian:")
        match = re.match(r"[a-z0-9]+", line)
        if not match:
            return
        debian = match.group()
        for version_no, codename, suite_name in debian_releases:
            if debian == codename:
                break
            if debian == version_no:
                debian = codename
                break
            if debian == suite_name:
                if debian != "unstable":
                    logger.error(
                        id="dynamic-suite",
                        msg=f"using dynamic suite name ('{debian}'), which breaks this "
                        f"hook. Use the codename ('{codename}') "
                        f"{
                            f"or version number ('{version_no}') " if version_no else ''
                        }"
                        f"instead.",
                    )
                debian = codename
                break
        else:
            logger.error(
                id="unknown-debian-version",
                msg=f"unknown debian version '{debian}'",
            )
            return

        self.current_debian = debian

    def process_line_renovate(
        self, orig_line: str, match: re.Match[str], logger: Logger
    ) -> str | None:
        if self.current_debian is None:
            logger.error("No FROM line")
            return None

        debian = match.group("suite")
        depname = match.group("depName")

        numeric_debian = None
        for version_no, codename, suite_name in debian_releases:
            if debian in {codename, suite_name}:
                break
            if debian == version_no:
                numeric_debian = codename
        else:
            msg = f"unknown debian version '{debian}'"
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

        if debian != self.current_debian:
            logger.error(
                id="wrong-suite",
                msg=f"suite set to `{debian}`, while FROM image suggests suite "
                f"`{self.current_debian}`",
            )
            if is_connected():
                self.bump_version_next = (self.current_debian, depname)
                return line_replace(
                    orig_line, debian, self.current_debian, logger=logger
                )

        return None

    def process_line_in_run(  # noqa: C901, PLR0912
        self, orig_line: str, line: str, logger: Logger
    ) -> str | None:
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

        if self.in_install:  # noqa: PLR1702
            assert self.in_run is not None  # noqa: S101

            if self.current_debian is None:
                logger.error("No FROM line")
                return None

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
                        debian_codename = self.current_debian
                        for _version_no, codename, suite_name in debian_releases:
                            if self.current_debian == suite_name:
                                debian_codename = codename
                                break

                        self.in_run.write(
                            make_renovate_line(self.current_debian, arg)
                            + make_env_line(debian_codename, arg, logger=logger),
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

                            # Only if the original line ended in a backslash (this could
                            #  be the last line) add a backslash here as well
                            end = " \\\n" if orig_line.endswith("\\\n") else "\n"
                            indent = " " * self.indent * 2
                            new_lines.append(f"{indent}{replacement}{end}")
                else:
                    logger.error(
                        id="unexpected-install-arg",
                        msg=f"Unexpected argument to `apt install` found ('{arg}') "
                        f"that is not a valid package name",
                    )

            if new_lines:
                # If we removed all args from the line, and only a continuation remains,
                #  we remove the line entirely
                if orig_line.strip() != "\\":
                    new_lines = [orig_line, *new_lines]
                return "".join(new_lines)

        return None


main = Processor.main
