from __future__ import annotations

import pytest
import responses

from pre_commit_hooks import set_euo_pipefail
from tests.base import TCBase


class TC(TCBase):
    hook_module = set_euo_pipefail

    def __init__(self, inp: str, retval: int) -> None:
        super().__init__(inp, retval, [inp])


test_cases = [
    TC("bad.sh", 1),
    TC("good.sh", 0),
]


@pytest.mark.parametrize(
    "test_case",
    test_cases,
    ids=repr,
)
@responses.activate
def test_set_euo_pipefail(test_case: TC) -> None:
    test_case.run()
