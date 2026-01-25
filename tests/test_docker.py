from __future__ import annotations

import pytest
import responses

from pre_commit_hooks import docker
from tests.base import TCBase


class TC(TCBase):
    hook_module = docker

    def __init__(self, inp: str, retval: int) -> None:
        super().__init__(inp, retval, [inp])


test_cases = [
    TC("docker-compose.yml", 1),
    TC("Dockerfile", 1),
]


@pytest.mark.parametrize(
    "test_case",
    test_cases,
    ids=repr,
)
@responses.activate
def test_docker(test_case: TC) -> None:
    test_case.run()
