from __future__ import annotations

import pytest
import responses

from pre_commit_hooks import pccf
from tests.base import TCFormatterBase


class TC(TCFormatterBase):
    hook_module = pccf

    def __init__(self, inp: str) -> None:
        super().__init__(inp, [inp])


test_cases = [
    *TC.out_double("basic.yaml"),
    *TC.out_double("pccs-basic.yaml"),
    *TC.out_double("pccs-partial.yaml"),
    *TC.out_double("pccs-basic-existing-ci.yaml"),
]


@pytest.mark.parametrize(
    "test_case",
    test_cases,
    ids=repr,
)
@responses.activate
def test_pccf(test_case: TC) -> None:
    test_case.run()
