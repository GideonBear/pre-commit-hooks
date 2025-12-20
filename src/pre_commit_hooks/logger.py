from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Self

import colorama
from colorama import Fore

from pre_commit_hooks.default_allows import default_allows, infos


if TYPE_CHECKING:
    from pathlib import Path


colorama.init()


@dataclass
class Logger:
    file: Path
    lnr: int | None
    allow: str | None

    def __post_init__(self) -> None:
        self.retval = 0
        self.info: str | None = None

    @classmethod
    def from_file(cls, file: Path) -> Self:
        return cls(file, lnr=None, allow=None)

    def with_line(self, lnr: int, allow: str | None) -> Self:
        if self.lnr is not None:
            msg = "lnr already set"
            raise ValueError(msg)
        if self.allow is not None:
            msg = "allow already set"
            raise ValueError(msg)
        return self.__class__(self.file, lnr, allow)

    def use_defaults(self, hook: str, key_type: str, key: str) -> None:
        default_allow = default_allows[hook].get(key)
        if default_allow:
            if self.allow:
                self.warn(
                    "allow comment specified while "
                    f"there is a default allow for this {key_type}. "
                    "The allow comment will be ignored. "
                    f"(specified '{self.allow}', default '{default_allow}')"
                )
            self.allow = default_allow

        if self.info is not None:
            msg = "info already set"
            raise ValueError(msg)
        self.info = infos[hook].get(key)

    def consume(self, other: Self) -> None:
        self.retval |= other.retval

    def log_no_info(self, msg: str) -> None:
        if self.lnr is not None:
            print(f"({self.file}:{self.lnr + 1}) {msg}")
        else:
            print(f"({self.file}) {msg}")

    def log(self, msg: str) -> None:
        self.log_no_info(msg)
        if self.info is not None:
            self.log_no_info(f"{Fore.LIGHTBLUE_EX}Info{Fore.RESET}: {self.info}")

    # It's allowed to pass a string in here, which means some errors
    #  will not have ids. But `allow-all` will still block these, as
    #  the whole line is skipped then.
    def invalid(self, error: Invalid | str) -> bool:
        """
        Log an error.

        Returns:
            `True` if an autofix should be done if possible

        """
        if isinstance(error, Invalid) and error.id == self.allow:
            return False

        self.log(f"{Fore.LIGHTRED_EX}Error{Fore.RESET}: {error}")
        self.retval |= 1
        return True

    def warn(self, msg: str) -> None:
        self.log(f"{Fore.YELLOW}Warning{Fore.RESET}: {msg}")


@dataclass
class Invalid:
    id: str
    msg: str

    def __str__(self) -> str:
        return f"[{self.id}] {self.msg}"
