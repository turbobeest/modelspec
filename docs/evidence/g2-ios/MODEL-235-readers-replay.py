"""Replay saved price pages without fetching, writing data, or allowing connects.

The plain-copy artifact has no URL manifest. Canonical HTML URLs are used where
available; the six explicit assignments below identify redirects or text pages.
A missing response is reported as missing, never invented as an HTTP status.
"""

from __future__ import annotations

import argparse
import json
import re
import socket
from contextlib import nullcontext
from datetime import date
from pathlib import Path
from unittest.mock import patch

from decision.normalise import canonical_url
from decision.sources import CopyStore, FetchResult, load_sources
from scripts.price_reread import RenderedReplayFetcher, run, tracked_facts

ASSIGNMENTS = {
    "model-201-minimax-token-plan": "66eef9",
    "model-205-cursor-models-and-pricing": "abf649",
    "model-205-github-copilot-plans": "2c91fe",
    "typesafe-models": "15351a",
    "meta-model-api-pricing": "18dddd",
    "zai-pricing": "e78c0f",
}


def blocked(*args, **kwargs):
    raise AssertionError("Network connects are forbidden during replay")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-root", type=Path, required=True)
    parser.add_argument("--copies", type=Path, required=True)
    parser.add_argument("--rendered", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--fact", action="append", help="Replay only these exact fact IDs")
    parser.add_argument("--today", type=date.fromisoformat, default=date(2026, 10, 14))
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    sources = load_sources(args.data_root / "registry/sources.yaml")
    files = sorted(args.copies.glob("*/*"))
    by_url = {}
    for path in files:
        for tag in re.findall(r"<link\b[^>]*>", path.read_text()):
            if 'rel="canonical"' in tag and (m := re.search(r'href="([^"]+)"', tag)):
                by_url[canonical_url(m[1]).rstrip("/")] = path
    for sid, prefix in ASSIGNMENTS.items():
        matches = [p for p in files if p.name.startswith(prefix)]
        if len(matches) != 1:
            raise ValueError(f"{sid}: expected one saved copy starting with {prefix}")
        by_url[canonical_url(str(sources[sid].url)).rstrip("/")] = matches[0]

    class SavedFetcher:
        def fetch(self, url):
            path = by_url.get(canonical_url(url).rstrip("/"))
            if path is None:
                return FetchResult("unreachable", error=f"no saved plain response for {url}")
            return FetchResult("ok", 200, body=path.read_bytes())

    selection = (
        patch(
            "scripts.price_reread.tracked_facts",
            lambda root: [fact for fact in tracked_facts(root) if fact.fact["id"] in args.fact],
        )
        if args.fact
        else nullcontext()
    )
    with (
        selection,
        patch.object(socket.socket, "connect", blocked),
        patch.object(socket.socket, "connect_ex", blocked),
        patch.object(socket, "create_connection", blocked),
    ):
        report = run(
            root=args.data_root,
            fetcher=SavedFetcher(),
            store=CopyStore(args.out / "copies"),
            today=args.today,
            rendered=RenderedReplayFetcher(args.rendered),
        )
    (args.out / "url-map.json").write_text(
        json.dumps({url: path.name for url, path in sorted(by_url.items())}, indent=2) + "\n"
    )
    (args.out / "report.json").write_text(json.dumps(report.to_dict(), indent=2) + "\n")
    (args.out / "facts.json").write_text(
        json.dumps([f.to_dict() for f in report.facts], indent=2) + "\n"
    )
    print(json.dumps(report.counts()))
    for fact in report.facts:
        if fact.status.value == "unreadable":
            print(fact.fact_id, fact.reason)


if __name__ == "__main__":
    main()
