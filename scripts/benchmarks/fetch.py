#!/usr/bin/env python3
"""Fetch a page through Firecrawl, with a local cache and a hard credit budget.

    python3 scripts/benchmarks/fetch.py <url>
    python3 scripts/benchmarks/fetch.py <url> --budget 20
    python3 scripts/benchmarks/fetch.py <url> --no-fetch
    python3 scripts/benchmarks/fetch.py --credit-usage

Default format is plain markdown (1 credit per page). JSON / extract / query /
highlight formats cost extra and are refused unless --allow-expensive-formats
is set.

The credit guard reads https://api.firecrawl.dev/v2/team/credit-usage before
the first scrape, records remainingCredits, and aborts when spend since that
opening snapshot reaches the budget. A number in a prompt is not a budget;
this check is.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[2]
HASH_CACHE = ROOT / "benchmarks" / "_census" / "cache"
RAW_CACHE = ROOT / "benchmarks" / "_census" / "ranking_evidence" / "raw"
OP_AGENT = Path.home() / ".local" / "bin" / "op-agent"

CREDIT_USAGE_URL = "https://api.firecrawl.dev/v2/team/credit-usage"
SCRAPE_URL = "https://api.firecrawl.dev/v2/scrape"

#: Conservative default: a handful of markdown scrapes, not a research binge.
DEFAULT_BUDGET = 20

#: Firecrawl bills these at a 4-credit surcharge on top of the scrape.
EXPENSIVE_FORMATS = frozenset(
    {
        "json",
        "extract",
        "screenshot",
        "changeTracking",
        "summary",
        "query",
        "question",
        "highlight",
        "branding",
    }
)

_NON_SLUG = re.compile(r"[^a-z0-9-]+")
_MULTI_HYPHEN = re.compile(r"-+")


class CreditBudgetExceeded(RuntimeError):
    """Spend since the opening snapshot has reached the configured budget."""

    def __init__(
        self,
        opening: int,
        remaining: int,
        spent: int,
        budget: int,
        url: str | None = None,
    ) -> None:
        self.opening = opening
        self.remaining = remaining
        self.spent = spent
        self.budget = budget
        self.url = url
        where = f" before {url}" if url else ""
        super().__init__(
            f"Firecrawl credit budget exceeded{where}: "
            f"opening={opening} remaining={remaining} spent={spent} budget={budget}"
        )


@dataclass
class CreditGuard:
    """Abort a run when Firecrawl spend since start reaches `budget`.

    `start()` must be called once, before the first scrape. Every scrape calls
    `assert_within_budget` which re-reads remainingCredits.
    """

    key: str
    budget: int
    opening: int | None = None
    last_remaining: int | None = None

    def start(self) -> int:
        remaining = remaining_credits(self.key)
        self.opening = remaining
        self.last_remaining = remaining
        return remaining

    def refresh(self) -> int:
        remaining = remaining_credits(self.key)
        self.last_remaining = remaining
        return remaining

    def spent(self) -> int:
        if self.opening is None:
            raise RuntimeError("CreditGuard.start() was not called")
        remaining = self.last_remaining
        if remaining is None:
            remaining = self.refresh()
        return self.opening - remaining

    def assert_within_budget(self, url: str | None = None, estimated: int = 1) -> None:
        if self.opening is None:
            self.start()
        remaining = self.refresh()
        spent = self.opening - remaining
        if spent >= self.budget or spent + estimated > self.budget or remaining < estimated:
            raise CreditBudgetExceeded(
                opening=self.opening,
                remaining=remaining,
                spent=spent,
                budget=self.budget,
                url=url,
            )


@dataclass
class CachedPage:
    url: str
    path: Path
    text: str
    fetched_at: str
    from_cache: bool
    meta: dict[str, Any] = field(default_factory=dict)

    @property
    def observation_date(self) -> str:
        """Date the page was actually fetched, never the parse-pass date."""
        return self.fetched_at


def resolve_key() -> str | None:
    key = os.environ.get("FIRECRAWL_API_KEY", "").strip()
    if key:
        return key
    if not OP_AGENT.is_file():
        return None
    try:
        r = subprocess.run(
            [
                str(OP_AGENT),
                "item",
                "get",
                "API - Firecrawl",
                "--vault",
                "AI-LAN",
                "--fields",
                "label=default",
                "--reveal",
            ],
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    return r.stdout.strip() or None


def remaining_credits(key: str) -> int:
    """Live remainingCredits from the team credit-usage endpoint."""
    req = urllib.request.Request(
        CREDIT_USAGE_URL,
        method="GET",
        headers={"Authorization": f"Bearer {key}"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            payload = json.load(resp)
    except urllib.error.HTTPError as exc:
        raise RuntimeError(f"credit-usage HTTP {exc.code}") from exc
    data = payload.get("data") if isinstance(payload, dict) else None
    if not isinstance(data, dict) or "remainingCredits" not in data:
        raise RuntimeError(f"credit-usage response missing remainingCredits: {payload!r}"[:300])
    return int(data["remainingCredits"])


def refuse_expensive_formats(formats: list[str]) -> None:
    costly = [fmt for fmt in formats if fmt.split(":")[0] in EXPENSIVE_FORMATS]
    if costly:
        raise ValueError(
            "refusing expensive Firecrawl formats "
            f"{costly} (JSON / query / highlight add 4 credits per page). "
            "Pass --allow-expensive-formats only when markdown cannot be parsed."
        )


def cache_stem(url: str) -> str:
    parsed = urlparse(url)
    host = parsed.netloc.replace("www.", "").replace(".", "-")
    tail = parsed.path.strip("/").replace("/", "-") or "index"
    stem = _MULTI_HYPHEN.sub("-", _NON_SLUG.sub("-", f"{host}-{tail}".lower())).strip("-")
    return stem or "page"


def named_paths(url: str, cache_dir: Path, suffix: str = ".md") -> tuple[Path, Path]:
    stem = cache_stem(url)
    return cache_dir / f"{stem}{suffix}", cache_dir / f"{stem}.meta.json"


def write_named_cache(
    url: str,
    text: str,
    cache_dir: Path,
    *,
    fetched_at: str,
    suffix: str = ".md",
    extra_meta: dict[str, Any] | None = None,
) -> CachedPage:
    cache_dir.mkdir(parents=True, exist_ok=True)
    path, meta_path = named_paths(url, cache_dir, suffix=suffix)
    now = datetime.now(UTC)
    meta: dict[str, Any] = {
        "url": url,
        "fetched_at": fetched_at,
        "fetched_at_utc": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "path": str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path),
        "bytes": len(text.encode("utf-8")),
    }
    if extra_meta:
        meta.update(extra_meta)
    path.write_text(text, encoding="utf-8")
    meta_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return CachedPage(url=url, path=path, text=text, fetched_at=fetched_at, from_cache=False, meta=meta)


def load_named_cache(url: str, cache_dir: Path, suffix: str = ".md") -> CachedPage | None:
    path, meta_path = named_paths(url, cache_dir, suffix=suffix)
    if not path.is_file():
        return None
    text = path.read_text(encoding="utf-8")
    meta: dict[str, Any] = {}
    if meta_path.is_file():
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
    fetched_at = str(meta.get("fetched_at") or "")
    if not fetched_at:
        # A cached file without metadata has no honest observation date.
        fetched_at = datetime.fromtimestamp(path.stat().st_mtime, tz=UTC).date().isoformat()
        meta["fetched_at"] = fetched_at
        meta["fetched_at_source"] = "mtime_fallback"
    return CachedPage(url=url, path=path, text=text, fetched_at=fetched_at, from_cache=True, meta=meta)


def hash_cache_path(url: str, formats: list[str]) -> Path:
    digest = hashlib.sha256((url + "|" + ",".join(formats)).encode()).hexdigest()[:24]
    return HASH_CACHE / (digest + ".json")


def scrape(
    url: str,
    formats: list[str] | None = None,
    *,
    guard: CreditGuard | None = None,
    allow_expensive: bool = False,
    wait_for_ms: int = 4000,
    named_cache_dir: Path | None = None,
) -> dict:
    """Scrape `url` as markdown. Honours the credit guard. Caches before return."""
    formats = list(formats or ["markdown"])
    if not allow_expensive:
        refuse_expensive_formats(formats)
    HASH_CACHE.mkdir(parents=True, exist_ok=True)
    key_path = hash_cache_path(url, formats)
    if key_path.exists():
        return json.loads(key_path.read_text(encoding="utf-8"))

    if named_cache_dir is not None:
        cached = load_named_cache(url, named_cache_dir, suffix=".md")
        if cached is not None:
            return {"markdown": cached.text, "from_cache": True, "fetched_at": cached.fetched_at}

    key = resolve_key()
    if not key:
        raise SystemExit(
            "no Firecrawl key: set FIRECRAWL_API_KEY or make ~/.local/bin/op-agent reachable"
        )
    if guard is None:
        guard = CreditGuard(key=key, budget=DEFAULT_BUDGET)
        guard.start()
    guard.assert_within_budget(url=url, estimated=1)

    remaining_before = guard.last_remaining
    body = json.dumps(
        {
            "url": url,
            "formats": formats,
            "onlyMainContent": True,
            "waitFor": wait_for_ms,
        }
    ).encode()
    data: dict[str, Any] | None = None
    for attempt in range(4):
        req = urllib.request.Request(
            SCRAPE_URL,
            data=body,
            method="POST",
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                payload = json.load(resp)
            if payload.get("success"):
                data = payload.get("data") or {}
                break
            raise RuntimeError(str(payload)[:300])
        except urllib.error.HTTPError as exc:
            if exc.code in (429, 500, 502, 503) and attempt < 3:
                time.sleep(2 ** attempt * 2)
                continue
            raise
    if data is None:
        raise RuntimeError("firecrawl scrape failed after retries")

    key_path.write_text(json.dumps(data), encoding="utf-8")
    markdown = str(data.get("markdown") or "")
    if named_cache_dir is not None and markdown:
        remaining_after = guard.refresh()
        write_named_cache(
            url,
            markdown,
            named_cache_dir,
            fetched_at=datetime.now(UTC).date().isoformat(),
            suffix=".md",
            extra_meta={
                "fetcher": "firecrawl",
                "formats": formats,
                "credits_remaining_before": remaining_before,
                "credits_remaining_after": remaining_after,
            },
        )
    else:
        guard.refresh()
    return data


def http_get(url: str, timeout: int = 120) -> tuple[str, str]:
    """Direct GET. Zero Firecrawl credits. Follows redirects."""
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "ModelSpecCensus/1.0 (+https://github.com/modelspec)"},
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read()
        final = resp.geturl()
    return raw.decode("utf-8", errors="replace"), final


def load_or_get(
    url: str,
    cache_dir: Path,
    *,
    fetch: bool,
    suffix: str = ".html",
) -> CachedPage:
    """Cache-first page load. Direct GET, not Firecrawl."""
    cached = load_named_cache(url, cache_dir, suffix=suffix)
    if cached is not None:
        return cached
    if not fetch:
        path, _meta = named_paths(url, cache_dir, suffix=suffix)
        raise FileNotFoundError(f"no cached page for {url} at {path}")
    text, final_url = http_get(url)
    fetched_at = datetime.now(UTC).date().isoformat()
    return write_named_cache(
        url,
        text,
        cache_dir,
        fetched_at=fetched_at,
        suffix=suffix,
        extra_meta={"fetcher": "http_get", "final_url": final_url},
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url", nargs="?")
    parser.add_argument(
        "--budget",
        type=int,
        default=DEFAULT_BUDGET,
        help=f"max Firecrawl credits this process may spend (default {DEFAULT_BUDGET})",
    )
    parser.add_argument("--no-fetch", action="store_true", help="only read the named cache")
    parser.add_argument(
        "--cache-dir",
        default=str(RAW_CACHE),
        help="named markdown cache (default: ranking_evidence/raw)",
    )
    parser.add_argument("--credit-usage", action="store_true", help="print remainingCredits and exit")
    parser.add_argument("--links", action="store_true", help="print links instead of markdown")
    parser.add_argument(
        "--allow-expensive-formats",
        action="store_true",
        help="permit JSON/query/highlight formats (5x credit cost)",
    )
    parser.add_argument("--formats", default="markdown", help="comma-separated Firecrawl formats")
    args = parser.parse_args(argv)

    key = resolve_key()
    if args.credit_usage:
        if not key:
            print("no Firecrawl key", file=sys.stderr)
            return 2
        remaining = remaining_credits(key)
        print(json.dumps({"remainingCredits": remaining}))
        return 0

    if not args.url:
        parser.print_help()
        return 2

    cache_dir = Path(args.cache_dir)
    if not cache_dir.is_absolute():
        cache_dir = ROOT / cache_dir

    if args.no_fetch:
        cached = load_named_cache(args.url, cache_dir, suffix=".md")
        if cached is None:
            print(f"no cached scrape for {args.url}", file=sys.stderr)
            return 2
        print(cached.text)
        return 0

    formats = [part.strip() for part in args.formats.split(",") if part.strip()]
    if not key:
        print(
            "no Firecrawl key: set FIRECRAWL_API_KEY or make ~/.local/bin/op-agent reachable",
            file=sys.stderr,
        )
        return 2
    guard = CreditGuard(key=key, budget=args.budget)
    opening = guard.start()
    print(f"credits opening={opening} budget={args.budget}", file=sys.stderr)
    try:
        data = scrape(
            args.url,
            formats=formats,
            guard=guard,
            allow_expensive=args.allow_expensive_formats,
            named_cache_dir=cache_dir,
        )
    except CreditBudgetExceeded as exc:
        print(str(exc), file=sys.stderr)
        return 3
    remaining = guard.last_remaining
    spent = guard.spent()
    print(f"credits remaining={remaining} spent={spent} closing={remaining}", file=sys.stderr)
    if args.links:
        for link in data.get("links") or []:
            print(link)
    else:
        print(data.get("markdown") or "")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
