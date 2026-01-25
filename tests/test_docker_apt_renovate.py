from __future__ import annotations

import pytest
import responses

from pre_commit_hooks import docker_apt_renovate
from tests.base import TCBase


class TC(TCBase):
    hook_module = docker_apt_renovate

    def __init__(self, inp: str, retval: int) -> None:
        super().__init__(inp, retval, [inp])


test_cases = [
    *TC.out_double("debian.Dockerfile", 1),
    TC("debian.Dockerfile", 1).offline(),
    *TC.out_double("alpine.Dockerfile", 1),
    TC("alpine.Dockerfile", 1).offline(),
    *TC.out_double("debian-extra-version.Dockerfile", 1),
    *TC.out_double("alpine-extra-version.Dockerfile", 1),
    *TC.out_double("debian-custom-version.Dockerfile", 1),
    *TC.out_double("alpine-custom-version.Dockerfile", 1),
    TC("debian-default-version.Dockerfile", 1),  # No out-check because of the warning
    *TC.out_double("debian-add.Dockerfile", 1),
    *TC.out_double("debian-update-suite.Dockerfile", 1),
    TC("debian-update-suite.Dockerfile", 1).offline(),
    *TC.out_double("alpine-update-suite.Dockerfile", 1),
    TC("alpine-update-suite.Dockerfile", 1).offline(),
    TC("debian-no-update.Dockerfile", 0),
    TC("errors.Dockerfile", 1),
]


@pytest.mark.parametrize(
    "test_case",
    test_cases,
    ids=repr,
)
@responses.activate
def test_docker_apt_renovate(test_case: TC) -> None:
    test_case.run()
