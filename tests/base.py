from __future__ import annotations

import shutil
import tempfile
import urllib.parse
from abc import ABC, abstractmethod
from contextlib import nullcontext
from pathlib import Path
from typing import TYPE_CHECKING, Any, Self
from unittest.mock import patch

import responses

from pre_commit_hooks.logger import Logger


if TYPE_CHECKING:
    from collections.abc import Iterator, MutableSequence, Sequence
    from types import ModuleType


def fs_url_decode(s: str) -> str:
    return urllib.parse.unquote(s)


class ATestLogger(Logger, ABC):
    @property
    @abstractmethod
    def _logs(self) -> MutableSequence[tuple[Path, int, str]]: ...

    def log_no_info(self, msg: str) -> None:
        super().log_no_info(msg)
        self._logs.append((self.file, self.lnr, msg))


def make_test_logger(logs: MutableSequence[tuple[Path, int, str]]) -> type[ATestLogger]:
    class Sub(ATestLogger):
        _logs = logs

    return Sub


def extract_expected(inp: Path, inp_m: Path) -> Iterator[tuple[int | None, str]]:
    with inp_m.open("w", encoding="utf-8") as file:
        first_block = True
        for lineno, line in enumerate(inp.read_text(encoding="utf-8").splitlines()):
            if first_block:
                if line.startswith(("# Error:", "# Warning:", "# Info:")):
                    msg = line.removeprefix("# ")
                    yield None, msg
                    continue
                first_block = False

            diag_part = None
            for type_ in ("Error:", "Warning:", "Info:"):
                if f"# {type_}" in line:
                    line, diag_part = line.split(f"# {type_}", maxsplit=1)
                    line = line.rstrip(" ")
                    diag_part = type_ + diag_part
                    break
            if diag_part:
                yield from ((lineno, msg) for msg in diag_part.split(" |AND| "))
            file.write(line + "\n")


class TCBase(ABC):
    def __init__(
        self,
        inp: str,
        retval: int,
        args: Sequence[str],
    ) -> None:
        # Sanity check for accidents in parametrize
        assert inp in args

        self.inp = self.hookdir / inp
        self.retval = retval

        # Replace args
        self.args = [
            str(self.hookdir / arg) if (self.hookdir / arg).exists() else arg
            for arg in args
        ]

        self._offline = False
        self._out = None

    @property
    @abstractmethod
    def hook_module(self) -> ModuleType: ...

    @property
    def hook(self) -> str:
        return self.hook_module.__name__.split(".")[1].replace("_", "-")

    @property
    def hookdir(self) -> Path:
        return Path(__file__).parent / self.hook

    def out(self) -> Self:
        self._out = self.inp.with_stem(self.inp.stem + "-out")
        return self

    def offline(self) -> Self:
        self._offline = True
        return self

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}({self.inp.name}, {self.retval})"
            + (".out()" if self._out else "")
            + (f".offline({self._offline})" if self._offline else "")
        )

    def run(self) -> None:
        with (
            tempfile.NamedTemporaryFile() as tmp,
            tempfile.NamedTemporaryFile() as inp_m,
        ):
            tmp = Path(tmp.name)
            inp_m = Path(inp_m.name)

            # Replace inp with tmp
            args = [str(tmp) if arg == str(self.inp) else arg for arg in self.args]

            expected_logs = [
                (tmp, lnr, msg) for lnr, msg in extract_expected(self.inp, inp_m)
            ]
            shutil.copy(inp_m, tmp)

            logs = []

            for mock in (Path(__file__).parent / "mocks").iterdir():
                responses.get(
                    url=fs_url_decode(mock.name),
                    body=mock.read_text(),
                )

            with (
                patch(f"{self.hook_module.__name__}.is_connected", return_value=False)
                if self._offline
                else nullcontext(),
            ):
                assert (
                    self.hook_module.main(args, logger_type=make_test_logger(logs))
                    == self.retval
                )

            assert logs == expected_logs
            if self._out:
                assert Path(tmp).read_text(encoding="utf-8") == self._out.read_text()
            else:
                # Assert output is unchanged
                assert Path(tmp).read_text(encoding="utf-8") == inp_m.read_text()

    @classmethod
    def out_double(cls, *args: Any, **kwargs: Any) -> Iterator[TCBase]:  # noqa: ANN401
        """
        Return two test cases. One with out, and one on that out without out, to verify a second pass will not have any effect.

        Any kwargs will be passed to both test cases, any args only to the first.
        """  # noqa: DOC402
        first = cls(*args, **kwargs).out()
        yield first
        yield cls(first._out.name, retval=0, **kwargs)  # noqa: SLF001


class TCFormatterBase(TCBase, ABC):
    def __init__(self, inp: str, args: Sequence[str]) -> None:
        super().__init__(inp, 0, args)

    @classmethod
    def out_double(cls, *args: Any, **kwargs: Any) -> Iterator[TCBase]:  # noqa: ANN401
        first = cls(*args, **kwargs).out()
        yield first
        yield cls(first._out.name, **kwargs)  # noqa: SLF001
