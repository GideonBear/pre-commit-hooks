from __future__ import annotations

import re
import shutil
import tempfile
import urllib.parse
from functools import partial
from pathlib import Path
from typing import TYPE_CHECKING

import pytest
import requests_mock

from pre_commit_hooks import main
from pre_commit_hooks.classes import Logger


if TYPE_CHECKING:
    from collections.abc import MutableSequence, Sequence


def remove_color(s: str) -> str:
    return re.sub(r"\x1b\[[0-9;]*m", "", s)


def fs_url_decode(s: str) -> str:
    return urllib.parse.unquote(s)


class ATestLogger(Logger):
    def __init__(
        self,
        *args,  # noqa: ANN002
        _logs: MutableSequence[tuple[Path, int, str]],
        **kwargs,  # noqa: ANN003
    ) -> None:
        super().__init__(*args, **kwargs)
        self._logs = _logs

    def log(self, msg: str) -> None:
        super().log(msg)
        self._logs.append((self.file, self.lnr, remove_color(msg)))


@pytest.mark.parametrize(
    ("hook", "inp", "out", "args"),
    [
        ("shfuncdecfmt", "readme.sh", "readme-out.sh", ["readme.sh"]),
        ("set-euo-pipefail", "basic.sh", None, ["basic.sh"]),
        (
            "pcad",
            "basic.yaml",
            "basic-out.yaml",
            ["--configs", "basic.yaml", "--lockfile", "basic-uv.lock"],
        ),
        ("docker", "docker-compose.yml", None, ["docker-compose.yml"]),
        ("docker", "Dockerfile", None, ["Dockerfile"]),
        ("gha", "workflow.yml", "workflow-out.yml", ["workflow.yml"]),
    ],
)
def test_pre_commit_hooks(
    hook: str, inp: str, out: str | None, args: Sequence[str]
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
        with requests_mock.Mocker() as m:
            for mock in (Path(__file__).parent / "mocks").iterdir():
                url = fs_url_decode(mock.name)
                m.get(url, text=mock.read_text())

            main((hook, *args), logger_type=partial(ATestLogger, _logs=logs))

        if out:
            assert Path(tmp).read_text(encoding="utf-8") == out.read_text()
        assert logs == expected_logs
