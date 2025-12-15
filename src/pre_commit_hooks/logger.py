from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Self

import colorama
from colorama import Fore


if TYPE_CHECKING:
    from pathlib import Path


colorama.init()


@dataclass
class Logger:
    file: Path
    lnr: int | None

    def __post_init__(self) -> None:
        self.retval = 0

    @classmethod
    def from_file(cls, file: Path) -> Self:
        return cls(file, None)

    def with_lnr(self, lnr: int) -> Self:
        if self.lnr is not None:
            msg = "lnr already set"
            raise ValueError(msg)
        return self.__class__(self.file, lnr)

    def consume(self, other: Self) -> None:
        self.retval |= other.retval

    def log(self, msg: str) -> None:
        if self.lnr is not None:
            print(f"({self.file}:{self.lnr + 1}) {msg}")
        else:
            print(f"({self.file}) {msg}")

    def invalid(self, error: Invalid | str) -> None:
        self.log(f"{Fore.LIGHTRED_EX}Error{Fore.RESET}: {error}")
        self.retval |= 1

    def warn(self, msg: str) -> None:
        self.log(f"{Fore.YELLOW}Warning{Fore.RESET}: {msg}")


@dataclass
class Invalid:
    id: str
    msg: str

    def __str__(self) -> str:
        return f"[{self.id}] {self.msg}"
