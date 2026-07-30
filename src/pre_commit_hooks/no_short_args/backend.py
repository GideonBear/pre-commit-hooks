from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Protocol


if TYPE_CHECKING:
    from collections.abc import Iterable, Sequence
    from pathlib import Path


class Backend(Protocol):
    def get_matches(self, path: Path) -> Matches: ...

    @property
    def supports_fixes(self) -> bool: ...


class Matches(ABC):
    def __init__(self, path: Path) -> None:
        self.path = path

    @abstractmethod
    def iter(self) -> Iterable[Command]: ...


class Command(ABC):
    @property
    @abstractmethod
    def line(self) -> int: ...

    @property
    @abstractmethod
    def command(self) -> str: ...

    @property
    @abstractmethod
    def args(self) -> Sequence[Arg]: ...


class Arg(ABC):
    @property
    @abstractmethod
    def arg(self) -> str: ...

    @abstractmethod
    def fix(self, new: str) -> None: ...
