#!/usr/bin/env python3
"""Watch primary sources for model releases and file discoveries (MODEL-216).

    python scripts/release_watch.py               # dry run: print what it would file
    python scripts/release_watch.py --post        # file to $SIGNALS_ORIGIN/v1/signals/discovered
    python scripts/release_watch.py --rebaseline  # re-take every source's baseline
    python scripts/release_watch.py --rebaseline --source hf-qwen

Exit status 1 means at least one source or the signal endpoint failed. The
report names each one; the workflow turns that into an issue. Sources that did
answer still file their discoveries on the same run.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from collections.abc import Sequence
from datetime import UTC, datetime
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from release_signals.contract import ReleaseSignal  # noqa: E402
from release_signals.watch import (  # noqa: E402
    BASELINE,
    REGISTRY,
    Fetch,
    Response,
    SourceRun,
    allowed_by_robots,
    discoveries,
    extract,
    load_baseline,
    load_catalogue,
    load_registry,
    run_all,
    write_baseline,
)


def http_fetch(user_agent: str) -> Fetch:
    client = httpx.Client(
        headers={"User-Agent": user_agent}, follow_redirects=True, timeout=30,
    )

    def fetch(url: str) -> Response:
        # One retry, so a single slow answer is not an outage alert. A second
        # failure is, and it reaches the report as `unreachable`.
        for attempt in (1, 2):
            try:
                response = client.get(url)
            except httpx.TransportError:
                if attempt == 2:
                    raise
            else:
                if response.status_code < 500 or attempt == 2:
                    return Response(response.status_code, response.content)
            time.sleep(5)
        raise AssertionError("unreachable")

    return fetch


def post_discoveries(
    signals: Sequence[ReleaseSignal], *, origin: str, read_key: str,
    client: httpx.Client | None = None,
) -> list[dict]:
    """POST each discovery. 202 is new, 200 is filed before; anything else fails."""
    client = client or httpx.Client(timeout=30)
    outcomes = []
    for signal in signals:
        try:
            response = client.post(
                f"{origin.rstrip('/')}/v1/signals/discovered",
                content=json.dumps(signal.to_dict(), separators=(",", ":")).encode(),
                headers={
                    "Authorization": f"Bearer {read_key}",
                    "Content-Type": "application/json",
                },
            )
            status, detail = response.status_code, response.text[:300]
        except httpx.HTTPError as exc:
            status, detail = 0, f"{type(exc).__name__}: {exc}"
        outcomes.append({
            "signal_id": signal.signal_id,
            "status": status,
            "ok": status in (200, 202),
            "filed": status == 202,
            "detail": "" if status in (200, 202) else detail,
        })
    return outcomes


def report(runs: Sequence[SourceRun], signals: Sequence[ReleaseSignal],
           posted: Sequence[dict] | None, now: datetime) -> dict:
    return {
        "observed_at": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "sources": [
            {
                "id": run.source.id,
                "url": run.source.url,
                "status": run.status,
                "detail": run.detail,
                "listed": run.listed,
                "new": [seen.key for seen in run.new],
            }
            for run in runs
        ],
        "discoveries": [signal.to_dict() for signal in signals],
        "posted": list(posted) if posted is not None else None,
    }


def failures(result: dict) -> list[str]:
    lines = [
        f"- `{row['id']}` {row['status']}: {row['detail']} ({row['url']})"
        for row in result["sources"] if row["status"] != "ok"
    ]
    lines.extend(
        f"- signal endpoint refused `{row['signal_id']}`: HTTP {row['status']} {row['detail']}"
        for row in result["posted"] or [] if not row["ok"]
    )
    return lines


def summary(result: dict) -> str:
    ok = sum(row["status"] == "ok" for row in result["sources"])
    lines = [
        f"## Release watch {result['observed_at']}",
        "",
        f"{ok} of {len(result['sources'])} sources answered. "
        f"{len(result['discoveries'])} discoveries.",
    ]
    if result["discoveries"]:
        lines += ["", "| Signal | Model | Lab | Seen at |", "| --- | --- | --- | --- |"]
        lines += [
            f"| `{row['signal_id']}` | {row['model_name']} | {row['provider']} | "
            f"{row['first_seen_url']} |"
            for row in result["discoveries"]
        ]
    broken = failures(result)
    if broken:
        lines += ["", "### Outages", "", *broken]
    return "\n".join(lines) + "\n"


def rebaseline(registry_path: Path, baseline_path: Path, only: Sequence[str], now: datetime) -> int:
    registry = load_registry(registry_path)
    fetch = http_fetch(registry.user_agent)
    baseline = (
        {key: set(value) for key, value in load_baseline(baseline_path).items()}
        if baseline_path.is_file() else {}
    )
    status = 0
    for source in registry.sources:
        if only and source.id not in only:
            continue
        if not allowed_by_robots(source.url, registry.user_agent, fetch):
            print(f"{source.id}: robots.txt disallows {source.url}", file=sys.stderr)
            status = 1
            continue
        response = fetch(source.url)
        if response.status != 200:
            print(f"{source.id}: HTTP {response.status}", file=sys.stderr)
            status = 1
            continue
        baseline[source.id] = set(extract(source, response.body, registry))
        print(f"{source.id}: {len(baseline[source.id])} IDs")
    known = {source.id for source in registry.sources}
    write_baseline(baseline_path, {k: v for k, v in baseline.items() if k in known}, now)
    return status


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--registry", type=Path, default=REGISTRY)
    parser.add_argument("--baseline", type=Path, default=BASELINE)
    parser.add_argument("--report", type=Path, help="write the JSON report here")
    parser.add_argument("--summary", type=Path, help="write a Markdown summary here")
    parser.add_argument(
        "--post", action="store_true",
        help="file discoveries; needs SIGNALS_ORIGIN and MODELSPEC_SIGNALS_READ_KEY",
    )
    parser.add_argument("--rebaseline", action="store_true")
    parser.add_argument("--source", action="append", default=[],
                        help="with --rebaseline, limit to this source ID (repeatable)")
    args = parser.parse_args(argv)
    now = datetime.now(UTC).replace(microsecond=0)

    if args.rebaseline:
        return rebaseline(args.registry, args.baseline, args.source, now)

    registry = load_registry(args.registry)
    runs = run_all(
        registry, load_baseline(args.baseline),
        fetch=http_fetch(registry.user_agent), now=now, catalogued=load_catalogue(ROOT).catalogued,
    )
    signals = discoveries(runs, now)
    posted = None
    if args.post:
        origin = os.environ.get("SIGNALS_ORIGIN", "")
        read_key = os.environ.get("MODELSPEC_SIGNALS_READ_KEY", "")
        if not origin or not read_key:
            parser.error("--post needs SIGNALS_ORIGIN and MODELSPEC_SIGNALS_READ_KEY")
        posted = post_discoveries(signals, origin=origin, read_key=read_key)
    result = report(runs, signals, posted, now)
    if args.report:
        args.report.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    text = summary(result)
    if args.summary:
        args.summary.write_text(text, encoding="utf-8")
    print(text)
    return 1 if failures(result) else 0


if __name__ == "__main__":
    raise SystemExit(main())
