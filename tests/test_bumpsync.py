from __future__ import annotations

import pytest
import responses

from pre_commit_hooks import bumpsync
from tests.base import TCFormatterBase


class TC(TCFormatterBase):
    hook_module = bumpsync

    def __init__(self, inp: str) -> None:
        super().__init__(inp, [inp, "--pyproject", "pyproject.toml"])


test_cases = [
    *TC.out_double("pre-commit.md"),
    *TC.out_double("single_line.py"),
]


@pytest.mark.parametrize(
    "test_case",
    test_cases,
    ids=repr,
)
@responses.activate
def test_bumpsync(test_case: TC) -> None:
    test_case.run()
