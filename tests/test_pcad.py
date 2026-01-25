from __future__ import annotations

import pytest
import responses

from pre_commit_hooks import pcad
from tests.base import TCFormatterBase


class TC(TCFormatterBase):
    hook_module = pcad

    def __init__(self, inp: str, *, pyproject: str = "pyproject.toml") -> None:
        super().__init__(
            inp, ["--configs", inp, "--pyproject", pyproject, "--lockfile", "uv.lock"]
        )


test_cases = [
    *TC.out_double("add.yaml"),
    *TC.out_double("remove.yaml", pyproject="remove-pyproject.toml"),
    *TC.out_double("sort.yaml"),
    *TC.out_double("extra.yaml"),
]


@pytest.mark.parametrize(
    "test_case",
    test_cases,
    ids=repr,
)
@responses.activate
def test_pcad(test_case: TC) -> None:
    test_case.run()
