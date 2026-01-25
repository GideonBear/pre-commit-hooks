from __future__ import annotations

import pytest
import responses

from pre_commit_hooks import shfuncdecfmt
from tests.base import TCFormatterBase


class TC(TCFormatterBase):
    hook_module = shfuncdecfmt

    def __init__(self, inp: str) -> None:
        super().__init__(inp, [inp])


test_cases = [
    *TC.out_double("readme.sh"),
]


@pytest.mark.parametrize(
    "test_case",
    test_cases,
    ids=repr,
)
@responses.activate
def test_shfuncdecfmt(test_case: TC) -> None:
    test_case.run()
