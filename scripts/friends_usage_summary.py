#!/usr/bin/env python3
"""Report friends-key usage from ACCESS daily counters, without writing to KV.

The counters expire two days after their last write. Save a snapshot each UTC
day, after 00:01 UTC, to retain the previous day's count outside ACCESS:

    python scripts/friends_usage_summary.py --month 2026-09 --snapshot > capture.json
    python scripts/friends_usage_summary.py --month 2026-09 --input capture.json

Repeat --input to combine daily captures. Repeated observations of a daily
counter use its maximum, never their sum. A report is partial until captures
cover every calendar day in the requested month. KV counters are eventually
consistent, so these totals have the same accuracy as the access meter.
Only keys carrying the friends tier when captured are included. No historical
tier changes can be reconstructed from the current key records.
"""

from __future__ import annotations

import argparse
import asyncio
import calendar
import json
import os
import re
import subprocess
import sys
from collections.abc import Callable, Sequence
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any, Protocol

SCRIPTS_ROOT = Path(__file__).resolve().parent
if str(SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_ROOT))

from api_key_operator import (  # noqa: E402
    DEFAULT_WRANGLER_CONFIG,
    WORKER_SRC,
    wrangler_target,
)

if str(WORKER_SRC) not in sys.path:
    sys.path.insert(0, str(WORKER_SRC))

import access_keys  # noqa: E402

Runner = Callable[[Sequence[str]], str]
_FINGERPRINT = re.compile(r"[0-9a-f]{64}")


class ReadStore(Protocol):
    async def get(self, name: str) -> str | None: ...

    async def list(self, options: dict[str, str]) -> dict[str, Any]: ...


def _month_days(month: str) -> set[str]:
    try:
        if re.fullmatch(r"[0-9]{4}-[0-9]{2}", month) is None:
            raise ValueError
        first = datetime.strptime(month + "-01", "%Y-%m-%d")
    except ValueError:
        raise ValueError("month must be a valid YYYY-MM") from None
    return {
        f"{month}-{day:02}" for day in range(1, calendar.monthrange(first.year, first.month)[1] + 1)
    }


async def _names(store: ReadStore, prefix: str) -> list[str]:
    names: set[str] = set()
    options = {"prefix": prefix}
    seen_cursors: set[str] = set()
    while True:
        page = await store.list(options)
        for row in page["keys"]:
            name = row["name"]
            if not isinstance(name, str) or not name.startswith(prefix):
                raise ValueError("ACCESS returned an invalid key listing")
            names.add(name)
        if page.get("list_complete", True):
            return sorted(names)
        cursor = page.get("cursor")
        if not isinstance(cursor, str) or not cursor or cursor in seen_cursors:
            raise ValueError("ACCESS returned an incomplete listing without a new cursor")
        seen_cursors.add(cursor)
        options = {"prefix": prefix, "cursor": cursor}


async def capture(store: ReadStore, month: str, *, now: datetime | None = None) -> dict[str, Any]:
    """Read friends records and retained daily counters into a private snapshot."""
    days = _month_days(month)
    started = (now or datetime.now(UTC)).astimezone(UTC)
    keys = []
    for name in await _names(store, "key:"):
        raw = await store.get(name)
        if raw is None:
            continue
        record = access_keys.KeyRecord.from_json(raw)
        if record.tier != "friends":
            continue
        fingerprint = name.removeprefix("key:")
        if _FINGERPRINT.fullmatch(fingerprint) is None or record.key_id != fingerprint[:12]:
            raise ValueError("ACCESS key record does not match its fingerprint")
        prefix = f"count:{record.key_id}:daily:"
        counts = {}
        for counter in await _names(store, prefix + month + "-"):
            day = counter.removeprefix(prefix)
            if day not in days:
                raise ValueError("ACCESS returned an invalid daily counter bucket")
            raw_count = await store.get(counter)
            if raw_count is None:
                continue
            if re.fullmatch(r"[0-9]+", raw_count.strip()) is None:
                raise ValueError("ACCESS contains an invalid daily counter")
            counts[day] = int(raw_count)
        keys.append(
            {
                "fingerprint": fingerprint,
                "key_id": record.key_id,
                "active": record.active,
                "days": counts,
            }
        )

    finished = (now or datetime.now(UTC)).astimezone(UTC)
    yesterday = (started - timedelta(days=1)).date().isoformat()
    # A previous-day counter cannot have expired yet. Older absent counters
    # might have expired, so absence cannot establish coverage for those days.
    complete = (
        started.date() == finished.date()
        and (started.hour, started.minute) >= (0, 1)
        and yesterday in days
    )
    return {
        "schema_version": 1,
        "month": month,
        "captured_at": finished.isoformat().replace("+00:00", "Z"),
        "complete_days": [yesterday] if complete else [],
        "keys": keys,
    }


def summarize(snapshots: Sequence[dict[str, Any]], month: str) -> dict[str, Any]:
    """Merge observations by fingerprint and day, disclosing missing coverage."""
    days = _month_days(month)
    covered: set[str] = set()
    merged: dict[str, dict[str, Any]] = {}
    for snapshot in snapshots:
        if (
            not isinstance(snapshot, dict)
            or snapshot.get("schema_version") != 1
            or snapshot.get("month") != month
        ):
            raise ValueError("snapshot schema or month does not match the requested month")
        try:
            captured = datetime.fromisoformat(snapshot["captured_at"].replace("Z", "+00:00"))
            if captured.tzinfo is None:
                raise ValueError
            captured = captured.astimezone(UTC)
            complete_days = snapshot["complete_days"]
            previous_day = (captured - timedelta(days=1)).date().isoformat()
            if (
                not isinstance(complete_days, list)
                or len(complete_days) > 1
                or any(day not in days or day != previous_day for day in complete_days)
                or (complete_days and (captured.hour, captured.minute) < (0, 1))
            ):
                raise ValueError
            covered.update(complete_days)
            if not isinstance(snapshot["keys"], list):
                raise ValueError
            for key in snapshot["keys"]:
                fingerprint = key["fingerprint"]
                if (
                    not isinstance(fingerprint, str)
                    or _FINGERPRINT.fullmatch(fingerprint) is None
                    or key["key_id"] != fingerprint[:12]
                    or type(key["active"]) is not bool
                    or not isinstance(key["days"], dict)
                ):
                    raise ValueError
                existing = merged.setdefault(
                    fingerprint,
                    {
                        "key_id": key["key_id"],
                        "active": key["active"],
                        "captured_at": captured,
                        "days": {},
                    },
                )
                if captured >= existing["captured_at"]:
                    existing.update(active=key["active"], captured_at=captured)
                for day, count in key["days"].items():
                    if day not in days or type(count) is not int or count < 0:
                        raise ValueError
                    existing["days"][day] = max(existing["days"].get(day, 0), count)
        except (KeyError, TypeError, ValueError, AttributeError):
            raise ValueError(
                "snapshot contains invalid coverage, key records or daily counts"
            ) from None
    rows = [
        {"key_id": key["key_id"], "active": key["active"], "requests": sum(key["days"].values())}
        for _, key in sorted(merged.items())
    ]
    missing = sorted(days - covered)
    return {
        "month": month,
        "partial": bool(missing),
        "covered_days": sorted(covered),
        "missing_days": missing,
        "total_requests": sum(row["requests"] for row in rows),
        "keys": rows,
    }


def _run_wrangler(command: Sequence[str]) -> str:
    env = dict(os.environ, CI="1", WRANGLER_SEND_METRICS="false")
    result = subprocess.run(
        command, capture_output=True, text=True, stdin=subprocess.DEVNULL, env=env, check=False
    )
    if result.returncode:
        # Wrangler can echo stored values into its diagnostics. The exit code
        # identifies the failure without copying owner labels or credentials.
        raise ValueError(f"Wrangler exited {result.returncode}")
    return result.stdout


class WranglerStore:
    """The operator's read-only ACCESS adapter. Wrangler lists all pages."""

    def __init__(self, config: Path, environment: str | None, run: Runner) -> None:
        self.target = (["--env", environment] if environment else []) + wrangler_target(config)
        self.run = run

    async def get(self, name: str) -> str | None:
        value = self.run(["npx", "wrangler", "kv", "key", "get", name, "--text", *self.target])
        return value.strip() or None

    async def list(self, options: dict[str, str]) -> dict[str, Any]:
        value = json.loads(
            self.run(
                [
                    "npx",
                    "wrangler",
                    "kv",
                    "key",
                    "list",
                    "--prefix",
                    options["prefix"],
                    *self.target,
                ]
            )
        )
        if not isinstance(value, list):
            raise ValueError("Wrangler returned an invalid key listing")
        return {"keys": value, "list_complete": True}


def main(argv: list[str] | None = None, *, run: Runner | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--month", required=True, help="UTC calendar month, YYYY-MM")
    parser.add_argument(
        "--snapshot",
        action="store_true",
        help="emit a filtered snapshot for daily operator capture",
    )
    parser.add_argument(
        "--input",
        action="append",
        type=Path,
        default=[],
        help="saved snapshot to merge; repeat for each file, with no remote reads",
    )
    parser.add_argument("--config", type=Path, default=DEFAULT_WRANGLER_CONFIG)
    parser.add_argument("--env", help="Wrangler environment, for example staging")
    args = parser.parse_args(argv)
    if args.snapshot and args.input:
        parser.error("--snapshot and --input cannot be combined")
    try:
        _month_days(args.month)
        if args.input:
            snapshots = [json.loads(path.read_text(encoding="utf-8")) for path in args.input]
        else:
            store = WranglerStore(args.config, args.env, run or _run_wrangler)
            snapshots = [asyncio.run(capture(store, args.month))]
        result = snapshots[0] if args.snapshot else summarize(snapshots, args.month)
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
