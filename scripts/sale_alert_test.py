#!/usr/bin/env python3
"""Send one Pushover test notice. Jamie runs this. CI does not.

    op run -- python scripts/sale_alert_test.py

Reads PUSHOVER_APP_TOKEN and PUSHOVER_USER_KEY from the environment and exits
before any network call when either is missing. Does not print those values.
Optional SALE_ALERT_TTL_SECONDS defaults to 5 and is clamped to 1–86400.
"""

from __future__ import annotations

import os
import sys
from urllib.parse import urlencode
from urllib.request import Request, urlopen

URL = "https://api.pushover.net/1/messages.json"
_TTL_DEFAULT = 5
_TTL_MIN = 1
_TTL_MAX = 86_400


def _required(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise SystemExit(f"{name} is required")
    return value


def _ttl() -> int:
    raw = os.environ.get("SALE_ALERT_TTL_SECONDS", "").strip()
    if not raw:
        return _TTL_DEFAULT
    try:
        value = int(raw)
    except ValueError:
        return _TTL_DEFAULT
    return min(_TTL_MAX, max(_TTL_MIN, value))


def main() -> None:
    token = _required("PUSHOVER_APP_TOKEN")
    user = _required("PUSHOVER_USER_KEY")
    body = urlencode({
        "token": token,
        "user": user,
        "title": "ModelSpec sale",
        "message": "$0.00 · sale alert test · card",
        "ttl": str(_ttl()),
        "priority": "0",
    }).encode("utf-8")
    request = Request(
        URL, data=body, method="POST",
        headers={"content-type": "application/x-www-form-urlencoded"})
    try:
        with urlopen(request, timeout=5) as response:
            response.read()
            status = int(response.status)
    except Exception:
        print("sale_alert_test failed", file=sys.stderr)
        raise SystemExit(1) from None
    if not 200 <= status < 300:
        raise SystemExit(f"pushover status {status}")
    print("sent")


if __name__ == "__main__":
    main()
