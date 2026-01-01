from __future__ import annotations

import socket
import subprocess
from functools import cache
from subprocess import CalledProcessError
from typing import Any

import requests
from colorama import Fore


REMOTE_SERVER = "one.one.one.one"


@cache
def is_connected() -> bool:
    try:
        # See if we can resolve the host name - tells us if there is
        # A DNS listening
        host = socket.gethostbyname(REMOTE_SERVER)
        # Connect to the host - tells us if the host is actually reachable
        s = socket.create_connection((host, 80), 2)
        s.close()
        return True  # noqa: TRY300
    except Exception as err:  # noqa: BLE001
        print(
            f"{Fore.YELLOW}Warning{Fore.RESET}: no network connection detected "
            f"(error: {err}), running without autofixes. "
            f"If you're seeing this in CI, you can fix most "
            f"of these errors automatically by running this hook "
            f"locally."
        )

    return False


@cache
def request(url: str, params: frozenset[tuple[str, str]] | None = None) -> Any:  # type: ignore[explicit-any, misc]  # noqa: ANN401
    headers = {}
    if url.startswith("https://api.github.com"):
        token = gh_token()
        if token:
            headers["Authorization"] = f"token {token}"

    resp = requests.get(url, timeout=60, headers=headers, params=params)
    resp.raise_for_status()
    return resp.json()


@cache
def gh_token() -> str | None:
    try:
        return (
            subprocess
            .run(
                ["gh", "auth", "token"],  # noqa: S607
                check=True,
                stdout=subprocess.PIPE,
            )
            .stdout.decode()
            .strip()
        )
    except FileNotFoundError:
        return None
    except CalledProcessError:
        return None
