from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import colorama
from colorama import Fore


if TYPE_CHECKING:
    from pathlib import Path


colorama.init()


@dataclass
class Logger:
    file: Path
    lnr: int

    def log(self, msg: str) -> None:
        print(f"({self.file}:{self.lnr + 1}) {msg}")

    def invalid(self, error: Invalid | str) -> int:
        self.log(f"{Fore.LIGHTRED_EX}Error{Fore.RESET}: {error}")
        return 1

    def warn(self, msg: str) -> None:
        self.log(f"{Fore.YELLOW}Warning{Fore.RESET}: {msg}")


@dataclass
class Invalid:
    id: str
    msg: str

    def __str__(self) -> str:
        return f"[{self.id}] {self.msg}"
