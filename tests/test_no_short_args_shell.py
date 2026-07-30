from __future__ import annotations

import pytest
import responses

from pre_commit_hooks import no_short_args
from tests.base import TCBase


class TC(TCBase):
    hook_module = no_short_args
    test_data_dir_name = "no-short-args-shell"

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
def test_no_short_args_shell(test_case: TC) -> None:
    test_case.run()
