from __future__ import annotations

import pytest
import responses

from pre_commit_hooks import sections
from tests.base import TCBase


class TC(TCBase):
    hook_module = sections

    def __init__(self, inp: str, retval: int) -> None:
        super().__init__(inp, retval, ["python", "--configs", inp])


test_cases = [
    TC("bad.yaml", 1),
    TC("good.yaml", 0),
]


@pytest.mark.parametrize(
    "test_case",
    test_cases,
    ids=repr,
)
@responses.activate
def test_sections(test_case: TC) -> None:
    test_case.run()
