from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from pathlib import Path


@dataclass
class Logger:
    file: Path
    lnr: int

    def log(self, msg: str) -> None:
        print(f"({self.file}:{self.lnr + 1}) {msg}")

    def invalid(self, error: Invalid | str) -> int:
        self.log(f"Invalid: {error}")
        return 1

    def warn(self, msg: str) -> None:
        self.log(f"Warning: {msg}")


@dataclass
class Invalid:
    id: str
    msg: str

    def __str__(self) -> str:
        return f"[{self.id}] {self.msg}"
