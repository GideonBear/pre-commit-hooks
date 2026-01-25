from __future__ import annotations

import importlib
from pathlib import Path

import pytest


this = Path(__file__)
here = this.parent


def get_used_files() -> set[Path]:
    used_files = set()
    for file in here.iterdir():
        if file.is_dir() or not file.name.startswith("test_") or file == this:
            continue
        test_cases = importlib.import_module(f"tests.{file.stem}").test_cases
        used_files.update(test_case.inp for test_case in test_cases)
    return used_files


def test_all_test_files_are_used() -> None:
    # All files must be used as input once, except...
    allow_unused_files = {
        # Any unmodifiable files entered with special args (e.g. --pyproject)
        here / "bumpsync/pyproject.toml",
        here / "pcad/pyproject.toml",
        here / "pcad/remove-pyproject.toml",
        here / "pcad/uv.lock",
        # Any tests whose output is not clean
        here / "gha/workflow-out.yml",
    }

    for file in allow_unused_files:
        assert file.exists()

    used_files = get_used_files()

    weird_files = used_files & allow_unused_files
    if weird_files:
        pytest.fail(
            f"files {', '.join(map(str, weird_files))} were assumed to not be used as input"
        )

    unused_files = set()
    for hook in here.iterdir():
        if not hook.is_dir() or hook.name in {"mocks", "__pycache__"}:
            continue
        unused_files.update(file for file in hook.iterdir())

    bad_files = unused_files - used_files - allow_unused_files
    if bad_files:
        pytest.fail(
            f"files {', '.join(map(str, bad_files))} are not used in test parameters. "
            f"If these are output files, try adding a test verifying putting the output files back in "
            f"leaves them unchanged and returns exit code 0. (with TC.out_double)"
        )
