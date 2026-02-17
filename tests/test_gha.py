from __future__ import annotations

import pytest
import responses

from pre_commit_hooks import gha
from pre_commit_hooks.default_allows import default_allows
from tests.base import TCBase


class TC(TCBase):
    hook_module = gha

    def __init__(self, inp: str, retval: int) -> None:
        super().__init__(inp, retval, [inp])

    def run(self, *args, **kwargs) -> None:  # noqa: ANN002, ANN003
        removed = {
            "dawidd6/action-homebrew-bump-formula": default_allows["gha"].pop(
                "dawidd6/action-homebrew-bump-formula"
            ),
        }
        super().run(*args, **kwargs)
        default_allows["gha"].update(removed)


test_cases = [
    # One of the few test outputs that doesn't pass
    TC("workflow.yml", 1).out(),
    TC("workflow-offline.yml", 1).offline(),
]


@pytest.mark.parametrize(
    "test_case",
    test_cases,
    ids=repr,
)
@responses.activate
def test_gha(test_case: TC) -> None:
    test_case.run()
