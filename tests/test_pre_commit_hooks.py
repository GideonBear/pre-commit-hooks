from __future__ import annotations

import re
import shutil
import tempfile
import urllib.parse
from abc import ABC, abstractmethod
from contextlib import nullcontext
from pathlib import Path
from typing import TYPE_CHECKING
from unittest.mock import patch

import pytest
import responses

from pre_commit_hooks import main
from pre_commit_hooks.classes import Logger


if TYPE_CHECKING:
    from collections.abc import MutableSequence, Sequence


def remove_color(s: str) -> str:
    return re.sub(r"\x1b\[[0-9;]*m", "", s)


def fs_url_decode(s: str) -> str:
    return urllib.parse.unquote(s)


class ATestLogger(Logger, ABC):
    @property
    @abstractmethod
    def _logs(self) -> MutableSequence[tuple[Path, int, str]]: ...

    def log(self, msg: str) -> None:
        super().log(msg)
        self._logs.append((self.file, self.lnr, remove_color(msg)))


def make_test_logger(logs: MutableSequence[tuple[Path, int, str]]) -> type[ATestLogger]:
    class Sub(ATestLogger):
        _logs = logs

    return Sub


@pytest.mark.parametrize(
    ("hook", "inp", "out", "args", "offline", "retval"),
    [
        ("shfuncdecfmt", "readme.sh", "readme-out.sh", ["readme.sh"], False, 1),
        ("set-euo-pipefail", "bad.sh", None, ["bad.sh"], False, 1),
        ("set-euo-pipefail", "good.sh", None, ["good.sh"], False, 0),
        (
            "pcad",
            "basic.yaml",
            "basic-out.yaml",
            ["--configs", "basic.yaml", "--lockfile", "basic-uv.lock"],
            False,
            1,
        ),
        ("docker", "docker-compose.yml", None, ["docker-compose.yml"], False, 1),
        ("docker", "Dockerfile", None, ["Dockerfile"], False, 1),
        ("gha", "workflow.yml", "workflow-out.yml", ["workflow.yml"], False, 1),
        ("gha", "workflow-offline.yml", None, ["workflow-offline.yml"], True, 1),
    ],
)
@responses.activate
def test_pre_commit_hooks(  # noqa: PLR0913, PLR0917
    hook: str,
    inp: str,
    out: str | None,
    args: Sequence[str],
    offline: bool,
    retval: int,
) -> None:
    hookdir = Path(__file__).parent / hook
    inp = hookdir / inp
    if out:
        out = hookdir / out

    args = [str(hookdir / arg) if (hookdir / arg).exists() else arg for arg in args]

    with tempfile.NamedTemporaryFile() as tmp:
        tmp = Path(tmp.name)
        shutil.copy(inp, tmp)

        # Replace inp with tmp
        args = [str(tmp) if arg == str(inp) else arg for arg in args]

        expected_logs = []
        for lineno, line in enumerate(inp.read_text(encoding="utf-8").splitlines()):
            try:
                _, comment = line.split("  # ")
            except ValueError:
                continue
            if comment.startswith(("Error:", "Warning:")):
                expected_logs.extend(
                    (tmp, lineno, msg) for msg in comment.split(" |AND| ")
                )

        logs = []

        for mock in (Path(__file__).parent / "mocks").iterdir():
            responses.get(
                url=fs_url_decode(mock.name),
                body=mock.read_text(),
            )
        with (
            patch(f"pre_commit_hooks.{hook}.is_connected", return_value=False)
            if offline
            else nullcontext(),
        ):
            assert main((hook, *args), logger_type=make_test_logger(logs)) == retval

        if out:
            assert Path(tmp).read_text(encoding="utf-8") == out.read_text()
        else:
            assert Path(tmp).read_text(encoding="utf-8") == inp.read_text()
        assert logs == expected_logs
