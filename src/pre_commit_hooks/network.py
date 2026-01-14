from __future__ import annotations

import socket
from functools import cache
from typing import Any, Literal, overload

import ghtoken
import requests
from termcolor import colored


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
            colored("Warning", "yellow") + f": no network connection detected "
            f"(error: {err}), running without autofixes. "
            f"If you're seeing this in CI, you can fix most "
            f"of these errors automatically by running this hook "
            f"locally."
        )

    return False


@overload
def request(
    url: str, params: frozenset[tuple[str, str]] | None = None, *, json: Literal[False]
) -> str: ...
@overload
def request(  # type: ignore[explicit-any]
    url: str, params: frozenset[tuple[str, str]] | None = None, *, json: Literal[True]
) -> Any: ...  # noqa: ANN401
@overload
def request(  # type: ignore[explicit-any]
    url: str, params: frozenset[tuple[str, str]] | None = None
) -> Any: ...  # noqa: ANN401
@cache
def request(  # type: ignore[explicit-any, misc]
    url: str, params: frozenset[tuple[str, str]] | None = None, *, json: bool = True
) -> Any:
    headers = {}
    if url.startswith("https://api.github.com"):
        token = gh_token()
        if token:
            headers["Authorization"] = f"token {token}"

    resp = requests.get(url, timeout=60, headers=headers, params=params)
    resp.raise_for_status()
    if json:
        return resp.json()
    return resp.text


@cache
def gh_token() -> str | None:
    try:
        return ghtoken.get_ghtoken()
    except ghtoken.GHTokenNotFound:
        return None
