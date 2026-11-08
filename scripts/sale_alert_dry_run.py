#!/usr/bin/env python3
"""Preview synthetic sale alerts; --send posts one notice directly to Pushover.

Requires PUSHOVER_APP_TOKEN and PUSHOVER_USER_KEY in the local environment.
SALE_ALERT_TTL_SECONDS defaults to 900 here. No payment or Worker is called.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from http.client import HTTPSConnection
from pathlib import Path
from urllib.parse import urlencode, urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "api" / "worker" / "src"))

from sale_alerts import PUSHOVER_URL, TIMEOUT_MS, build_payload  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--send", action="store_true", help="send exactly one Pushover notice")
    parser.add_argument("--channel", choices=("stripe", "x402"), default="stripe",
                        help="which synthetic sale to send, default: stripe; previews include both")
    args = parser.parse_args()

    token = os.environ.get("PUSHOVER_APP_TOKEN", "").strip()
    user = os.environ.get("PUSHOVER_USER_KEY", "").strip()
    if not token or not user:
        print("PUSHOVER_APP_TOKEN and PUSHOVER_USER_KEY are required", file=sys.stderr)
        return 2
    try:
        ttl = int(os.environ.get("SALE_ALERT_TTL_SECONDS", "").strip() or "900")
    except ValueError:
        print("SALE_ALERT_TTL_SECONDS must be an integer", file=sys.stderr)
        return 2

    payloads = {
        "stripe": build_payload(
            token=token, user=user, channel="card", product="dry-run 250-credit pack",
            amount_usd="5.00", ref="evt_dry_run_stripe", ttl=ttl,
        ),
        "x402": build_payload(
            token=token, user=user, channel="x402", product="dry-run paid result",
            amount_usd="0.02", ref="0x123456" + "ab" * 29, ttl=ttl,
        ),
    }
    print(json.dumps({
        channel: {**form, "token": "[REDACTED]", "user": "[REDACTED]"}
        for channel, form in payloads.items()
    }, indent=2, ensure_ascii=False))
    if not args.send:
        return 0

    form = payloads[args.channel]
    target = urlsplit(PUSHOVER_URL)
    connection = HTTPSConnection(target.hostname, timeout=TIMEOUT_MS // 1000)
    try:
        connection.request(
            "POST", target.path, body=urlencode(form).encode("utf-8"),
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        response = connection.getresponse()
        if not 200 <= response.status < 300 or json.loads(response.read()).get("status") != 1:
            raise ValueError("pushover rejected the message")
    except Exception:
        print("Pushover send failed; delivery is unconfirmed. No retry was attempted.",
              file=sys.stderr)
        return 1
    finally:
        connection.close()
    print(f"Pushover accepted one {args.channel} notice with ttl={form['ttl']} seconds. "
          "Check that it arrives and disappears after the TTL.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
