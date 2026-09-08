#!/usr/bin/env python3
"""Fetch a page as Markdown through Firecrawl, with a local cache.

    python3 scripts/benchmarks/fetch.py <url>            # prints markdown
    python3 scripts/benchmarks/fetch.py <url> --links    # prints the page's links, one per line

The key comes from FIRECRAWL_API_KEY or from 1Password through ~/.local/bin/op-agent
(item "API - Firecrawl", vault AI-LAN). The key is never printed. Results are cached under
benchmarks/_census/cache/ so repeated calls cost nothing.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CACHE = ROOT / "benchmarks" / "_census" / "cache"
OP_AGENT = Path.home() / ".local" / "bin" / "op-agent"


def resolve_key() -> str | None:
    key = os.environ.get("FIRECRAWL_API_KEY", "").strip()
    if key:
        return key
    if not OP_AGENT.is_file():
        return None
    try:
        r = subprocess.run([str(OP_AGENT), "item", "get", "API - Firecrawl", "--vault", "AI-LAN",
                            "--fields", "label=default", "--reveal"], capture_output=True, text=True, timeout=60, check=False)
    except (OSError, subprocess.TimeoutExpired):
        return None
    return r.stdout.strip() or None


def scrape(url: str, formats: list[str] | None = None) -> dict:
    formats = formats or ["markdown", "links"]
    CACHE.mkdir(parents=True, exist_ok=True)
    key_path = CACHE / (hashlib.sha256((url + "|" + ",".join(formats)).encode()).hexdigest()[:24] + ".json")
    if key_path.exists():
        return json.loads(key_path.read_text())
    key = resolve_key()
    if not key:
        raise SystemExit("no Firecrawl key: set FIRECRAWL_API_KEY or make ~/.local/bin/op-agent reachable")
    body = json.dumps({"url": url, "formats": formats, "onlyMainContent": True}).encode()
    for attempt in range(4):
        req = urllib.request.Request("https://api.firecrawl.dev/v2/scrape", data=body, method="POST",
                                     headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                data = json.load(resp)
            if data.get("success"):
                key_path.write_text(json.dumps(data.get("data", {})))
                return data.get("data", {})
            raise RuntimeError(str(data)[:300])
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503) and attempt < 3:
                time.sleep(2 ** attempt * 2)
                continue
            raise
    raise RuntimeError("firecrawl scrape failed after retries")


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    url = sys.argv[1]
    data = scrape(url)
    if "--links" in sys.argv:
        for link in data.get("links") or []:
            print(link)
    else:
        print(data.get("markdown") or "")
    return 0


if __name__ == "__main__":
    sys.exit(main())
