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

from pre_commit_hooks import (
    bumpsync,
    docker,
    docker_apt_renovate,
    gha,
    pcad,
    pccs,
    requires_python,
    sections,
    set_euo_pipefail,
    shfuncdecfmt,
)
from pre_commit_hooks.logger import Logger


if TYPE_CHECKING:
    from collections.abc import MutableSequence, Sequence
    from types import ModuleType


def remove_color(s: str) -> str:
    return re.sub(r"\x1b\[[0-9;]*m", "", s)


def fs_url_decode(s: str) -> str:
    return urllib.parse.unquote(s)


class ATestLogger(Logger, ABC):
    @property
    @abstractmethod
    def _logs(self) -> MutableSequence[tuple[Path, int, str]]: ...

    def log_no_info(self, msg: str) -> None:
        super().log_no_info(msg)
        self._logs.append((self.file, self.lnr, remove_color(msg)))


def make_test_logger(logs: MutableSequence[tuple[Path, int, str]]) -> type[ATestLogger]:
    class Sub(ATestLogger):
        _logs = logs

    return Sub


# *: changed files, relies on pre-commit to see modifications
@pytest.mark.parametrize(
    ("hook_module", "inp", "out", "args", "offline", "retval"),
    [
        (shfuncdecfmt, "readme.sh", "readme-out.sh", ["readme.sh"], False, 0),  # *
        (shfuncdecfmt, "readme-out.sh", None, ["readme-out.sh"], False, 0),
        (set_euo_pipefail, "bad.sh", None, ["bad.sh"], False, 1),
        (set_euo_pipefail, "good.sh", None, ["good.sh"], False, 0),
        (
            pcad,
            "basic.yaml",
            "basic-out.yaml",
            ["--configs", "basic.yaml", "--lockfile", "basic-uv.lock"],
            False,
            1,
        ),
        (
            pcad,
            "basic-out.yaml",
            None,
            ["--configs", "basic-out.yaml", "--lockfile", "basic-uv.lock"],
            False,
            0,
        ),
        (pccs, "basic.yaml", "basic-out.yaml", ["basic.yaml"], False, 0),  # *
        (pccs, "basic-out.yaml", None, ["basic-out.yaml"], False, 0),
        (pccs, "partial.yaml", "partial-out.yaml", ["partial.yaml"], False, 0),  # *
        (pccs, "partial-out.yaml", None, ["partial-out.yaml"], False, 0),
        (
            pccs,
            "basic-existing-ci.yaml",
            "basic-existing-ci-out.yaml",
            ["basic-existing-ci.yaml"],
            False,
            0,  # *
        ),
        (
            pccs,
            "basic-existing-ci-out.yaml",
            None,
            ["basic-existing-ci-out.yaml"],
            False,
            0,
        ),
        (pccs, "good.yaml", None, ["good.yaml"], False, 0),
        (docker, "docker-compose.yml", None, ["docker-compose.yml"], False, 1),
        (docker, "Dockerfile", None, ["Dockerfile"], False, 1),
        (gha, "workflow.yml", "workflow-out.yml", ["workflow.yml"], False, 1),
        (gha, "workflow-offline.yml", None, ["workflow-offline.yml"], True, 1),
        (sections, "bad.yaml", None, ["python", "--configs", "bad.yaml"], False, 1),
        (sections, "good.yaml", None, ["python", "--configs", "good.yaml"], False, 0),
        (requires_python, "bad.toml", "bad-out.toml", ["bad.toml"], False, 0),  # *
        (requires_python, "bad-out.toml", None, ["bad-out.toml"], False, 0),
        (requires_python, "good.toml", None, ["good.toml"], False, 0),
        (
            requires_python,
            "invalid-major.toml",
            None,
            ["invalid-major.toml"],
            False,
            0,
        ),
        (requires_python, "none.toml", None, ["none.toml"], False, 1),
        (
            requires_python,
            "uv-lock.toml",
            "uv-lock-out.toml",
            ["uv-lock.toml"],
            False,
            0,  # *
        ),
        (
            requires_python,
            "uv-lock-out.toml",
            None,
            ["uv-lock-out.toml"],
            False,
            0,
        ),
        (
            bumpsync,
            "pre-commit.md",
            "pre-commit-out.md",
            ["pre-commit.md", "--pyproject", "pyproject.toml"],
            False,
            0,  # *
        ),
        (
            bumpsync,
            "pre-commit-out.md",
            None,
            ["pre-commit-out.md", "--pyproject", "pyproject.toml"],
            False,
            0,
        ),
        (
            bumpsync,
            "single_line.py",
            "single_line-out.py",
            ["single_line.py", "--pyproject", "pyproject.toml"],
            False,
            0,  # *
        ),
        (
            bumpsync,
            "single_line-out.py",
            None,
            ["single_line-out.py", "--pyproject", "pyproject.toml"],
            False,
            0,
        ),
        (
            docker_apt_renovate,
            "debian.Dockerfile",
            "debian-out.Dockerfile",
            ["debian.Dockerfile"],
            False,
            1,
        ),
        (
            docker_apt_renovate,
            "debian-out.Dockerfile",
            None,
            ["debian-out.Dockerfile"],
            False,
            0,
        ),
        (
            docker_apt_renovate,
            "debian.Dockerfile",
            None,
            ["debian.Dockerfile"],
            True,
            1,
        ),
        (
            docker_apt_renovate,
            "debian-extra-debian.Dockerfile",
            "debian-extra-debian-out.Dockerfile",
            ["debian-extra-debian.Dockerfile"],
            False,
            1,
        ),
        (
            docker_apt_renovate,
            "debian-extra-debian-out.Dockerfile",
            None,
            ["debian-extra-debian-out.Dockerfile"],
            False,
            0,
        ),
        (
            docker_apt_renovate,
            "debian-custom-debian.Dockerfile",
            "debian-custom-debian-out.Dockerfile",
            ["debian-custom-debian.Dockerfile"],
            False,
            1,
        ),
        (
            docker_apt_renovate,
            "debian-custom-debian-out.Dockerfile",
            None,
            ["debian-custom-debian-out.Dockerfile"],
            False,
            0,
        ),
        (
            docker_apt_renovate,
            "debian-default-debian.Dockerfile",
            "debian-default-debian-out.Dockerfile",
            ["debian-default-debian.Dockerfile"],
            False,
            1,
        ),
        # No out-check because of the warning
        (
            docker_apt_renovate,
            "debian-add.Dockerfile",
            "debian-add-out.Dockerfile",
            ["debian-add.Dockerfile"],
            False,
            1,
        ),
        (
            docker_apt_renovate,
            "debian-add-out.Dockerfile",
            None,
            ["debian-add-out.Dockerfile"],
            False,
            0,
        ),
        (
            docker_apt_renovate,
            "debian-update-suite.Dockerfile",
            "debian-update-suite-out.Dockerfile",
            ["debian-update-suite.Dockerfile"],
            False,
            1,
        ),
        (
            docker_apt_renovate,
            "debian-update-suite-out.Dockerfile",
            None,
            ["debian-update-suite-out.Dockerfile"],
            False,
            0,
        ),
        (
            docker_apt_renovate,
            "debian-update-suite.Dockerfile",
            None,
            ["debian-update-suite.Dockerfile"],
            True,
            1,
        ),
        (
            docker_apt_renovate,
            "debian-no-update.Dockerfile",
            None,
            ["debian-no-update.Dockerfile"],
            False,
            0,
        ),
        (
            docker_apt_renovate,
            "errors.Dockerfile",
            None,
            ["errors.Dockerfile"],
            False,
            1,
        ),
    ],
)
@responses.activate
def test_pre_commit_hooks(  # noqa: PLR0913, PLR0917
    hook_module: ModuleType,
    inp: str,
    out: str | None,
    args: Sequence[str],
    offline: bool,
    retval: int,
) -> None:
    assert inp in args  # Sanity check for accidents in parametrize

    hook = hook_module.__name__.split(".")[1].replace("_", "-")
    hookdir = Path(__file__).parent / hook
    inp = hookdir / inp
    if out:
        out = hookdir / out

    args = [str(hookdir / arg) if (hookdir / arg).exists() else arg for arg in args]

    with tempfile.NamedTemporaryFile() as tmp, tempfile.NamedTemporaryFile() as inp_m:
        tmp = Path(tmp.name)
        inp_m = Path(inp_m.name)

        # Replace inp with tmp
        args = [str(tmp) if arg == str(inp) else arg for arg in args]

        with inp_m.open("w") as file:
            expected_logs = []
            first_block = True
            for lineno, line in enumerate(inp.read_text(encoding="utf-8").splitlines()):
                if first_block:
                    if line.startswith(("# Error:", "# Warning:", "# Info:")):
                        msg = line.removeprefix("# ")
                        expected_logs.append((tmp, None, msg))
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
                    expected_logs.extend(
                        (tmp, lineno, msg) for msg in diag_part.split(" |AND| ")
                    )
                file.write(line + "\n")

        shutil.copy(inp_m, tmp)

        logs = []

        for mock in (Path(__file__).parent / "mocks").iterdir():
            responses.get(
                url=fs_url_decode(mock.name),
                body=mock.read_text(),
            )

        with (
            patch(f"{hook_module.__name__}.is_connected", return_value=False)
            if offline
            else nullcontext(),
        ):
            assert hook_module.main(args, logger_type=make_test_logger(logs)) == retval

        assert logs == expected_logs
        if out:
            assert Path(tmp).read_text(encoding="utf-8") == out.read_text()
        else:
            assert Path(tmp).read_text(encoding="utf-8") == inp_m.read_text()
