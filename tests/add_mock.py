from __future__ import annotations

import re
import sys
from pathlib import Path

import requests


def fs_url_encode(s: str) -> str:
    return re.sub(r"[^A-Za-z0-9_-]", lambda m: "%" + format(ord(m.group(0)), "02X"), s)


url = sys.argv[1]

resp = requests.get(url, timeout=60)
resp.raise_for_status()

(Path(__file__).parent / "mocks" / fs_url_encode(url)).write_text(resp.text)
