from __future__ import annotations

import pytest
import responses

from pre_commit_hooks import pccs
from tests.base import TCFormatterBase


class TC(TCFormatterBase):
    hook_module = pccs

    def __init__(self, inp: str) -> None:
        super().__init__(inp, [inp])


test_cases = [
    *TC.out_double("basic.yaml"),
    *TC.out_double("partial.yaml"),
    *TC.out_double("basic-existing-ci.yaml"),
    TC("good.yaml"),
    TC("keep-formatting.yaml"),
]


@pytest.mark.parametrize(
    "test_case",
    test_cases,
    ids=repr,
)
@responses.activate
def test_pccs(test_case: TC) -> None:
    test_case.run()
