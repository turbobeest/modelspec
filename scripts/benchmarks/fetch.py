#!/usr/bin/env python3
"""Fetch a page through Firecrawl, with a local cache and a hard credit budget.

    python3 scripts/benchmarks/fetch.py <url>
    python3 scripts/benchmarks/fetch.py <url> --budget 20
    python3 scripts/benchmarks/fetch.py <url> --no-fetch
    python3 scripts/benchmarks/fetch.py --credit-usage

Default format is plain markdown (1 credit per page). JSON / extract / query /
highlight formats cost extra and are refused unless --allow-expensive-formats
is set.

PDF parsing is billed 1 credit per page. Firecrawl v2 accepts
`parsers: [{type: "pdf", maxPages: N}]` (N in 1..10000) and that N is this
process's worst-case cost. The guard refuses a request whose worst case would
exceed remaining `--budget`, and every scrape is sent with `maxPages` set to
at most that remainder unless `--allow-unbounded-cost` is passed.

A capped PDF that has more pages than `maxPages` comes back truncated, not
failed. Firecrawl's response reports `metadata.numPages` (pages parsed) and
`metadata.totalPages` (the document's real page count, when knowable); this
script flags `truncated: true` in the named-cache metadata whenever
totalPages exceeds numPages (or, lacking those fields, whenever the request
was billed at or above its own page cap) so a partial document is never
mistaken for a complete one downstream, and never replayed as one from
cache once more budget becomes available.

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

#: Firecrawl v2 `parsers[].maxPages` maximum (docs.firecrawl.dev scrape API).
FIRECRAWL_PDF_MAX_PAGES = 10000

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
        estimated: int | None = None,
    ) -> None:
        self.opening = opening
        self.remaining = remaining
        self.spent = spent
        self.budget = budget
        self.url = url
        self.estimated = estimated
        where = f" before {url}" if url else ""
        estimate = f" estimated={estimated}" if estimated is not None else ""
        super().__init__(
            f"Firecrawl credit budget exceeded{where}: "
            f"opening={opening} remaining={remaining} spent={spent} "
            f"budget={budget}{estimate}"
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
    last_request_cost: int | None = None
    request_costs: list[tuple[str, int]] = field(default_factory=list)

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

    def remaining_budget(self) -> int:
        return max(0, self.budget - self.spent())

    def record_request_cost(self, url: str, remaining_before: int, remaining_after: int) -> int:
        cost = max(0, remaining_before - remaining_after)
        self.last_remaining = remaining_after
        self.last_request_cost = cost
        self.request_costs.append((url, cost))
        return cost

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
                estimated=estimated,
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


def looks_like_pdf(url: str) -> bool:
    return urlparse(url).path.lower().endswith(".pdf")


#: Synthetic key stashed only in the on-disk hash-cache JSON (never in the
#: dict returned to callers) so a truncated response can't be replayed as a
#: complete one once more budget is available. See detect_truncation().
_HASH_CACHE_TRUNCATED_KEY = "_modelspec_truncated"


def detect_truncation(
    metadata: dict[str, Any],
    page_cap: int | None,
    cost: int,
    is_pdf: bool,
) -> tuple[bool, int | None, int | None]:
    """Whether a scrape returned fewer PDF pages than the source document has.

    Firecrawl's own response metadata is authoritative when present:
    `metadata.numPages` is "the number of pages parsed (capped by the parsers
    maxPages option)" and `metadata.totalPages` is "the document's true page
    count before any maxPages capping ... a totalPages greater than numPages
    indicates the result was truncated" (docs.firecrawl.dev/api-reference/
    endpoint/scrape). totalPages is "omitted when it cannot be determined",
    so when either field is missing we fall back to a cost heuristic: a PDF
    billed at or above its own page cap likely has pages we didn't pay for.
    """
    num_pages = metadata.get("numPages")
    total_pages = metadata.get("totalPages")
    if isinstance(total_pages, int) and isinstance(num_pages, int):
        return total_pages > num_pages, total_pages, num_pages
    if is_pdf and page_cap is not None and cost >= page_cap:
        return True, total_pages, num_pages
    return False, total_pages, num_pages


def scrape_payload(
    url: str,
    formats: list[str],
    wait_for_ms: int,
    max_pages: int | None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "url": url,
        "formats": formats,
        "onlyMainContent": True,
        "waitFor": wait_for_ms,
    }
    if max_pages is not None:
        payload["parsers"] = [{"type": "pdf", "maxPages": max_pages}]
    return payload


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


def hash_cache_path(url: str, formats: list[str], *, max_pages: int | None = None) -> Path:
    """Response cache path. Keys without an explicit page cap are unchanged,
    so responses cached before the page cap existed are still hits."""
    material = url + "|" + ",".join(formats)
    if max_pages is not None:
        material += f"|max_pages={max_pages}"
    digest = hashlib.sha256(material.encode()).hexdigest()[:24]
    return HASH_CACHE / (digest + ".json")


def scrape(
    url: str,
    formats: list[str] | None = None,
    *,
    guard: CreditGuard | None = None,
    allow_expensive: bool = False,
    wait_for_ms: int = 4000,
    named_cache_dir: Path | None = None,
    max_pages: int | None = None,
    allow_unbounded: bool = False,
) -> dict:
    """Scrape `url` as markdown. Honours the credit guard. Caches before return."""
    formats = list(formats or ["markdown"])
    if not allow_expensive:
        refuse_expensive_formats(formats)
    if allow_unbounded and max_pages is not None:
        raise ValueError("max_pages and allow_unbounded are mutually exclusive")
    if max_pages is not None and max_pages < 1:
        raise ValueError("max_pages must be >= 1")

    # Caches first: a cached response costs nothing and needs no key. A
    # response flagged truncated (see detect_truncation) is never served
    # from either cache -- it was cut short by whatever budget was live at
    # the time, and a later call may have room for the whole document.
    HASH_CACHE.mkdir(parents=True, exist_ok=True)
    key_path = hash_cache_path(url, formats, max_pages=max_pages)
    if key_path.exists():
        cached_raw = json.loads(key_path.read_text(encoding="utf-8"))
        if not cached_raw.pop(_HASH_CACHE_TRUNCATED_KEY, False):
            return cached_raw

    if named_cache_dir is not None:
        cached = load_named_cache(url, named_cache_dir, suffix=".md")
        if cached is not None and not cached.meta.get("truncated"):
            return {"markdown": cached.text, "from_cache": True, "fetched_at": cached.fetched_at}

    key = resolve_key()
    if not key:
        raise SystemExit(
            "no Firecrawl key: set FIRECRAWL_API_KEY or make ~/.local/bin/op-agent reachable"
        )
    if guard is None:
        guard = CreditGuard(key=key, budget=DEFAULT_BUDGET)
    if guard.opening is None:
        guard.start()
    else:
        guard.refresh()

    # Bound the worst case BEFORE sending. Firecrawl bills PDF parsing at
    # 1 credit per page up to parsers[].maxPages; a non-PDF page is 1 credit,
    # which maxPages >= 1 also covers. So page_cap is the worst-case cost.
    page_cap: int | None
    if allow_unbounded:
        # Explicit opt-in: no maxPages, so only the 1-credit floor is checked
        # up front and the real cost is read from the balance afterwards.
        page_cap = None
        estimated = 1
    else:
        if max_pages is None:
            page_cap = min(guard.remaining_budget(), FIRECRAWL_PDF_MAX_PAGES)
        else:
            page_cap = min(max_pages, FIRECRAWL_PDF_MAX_PAGES)
        # A zero cap means the budget is spent; the check below refuses it.
        estimated = max(1, page_cap)
        page_cap = estimated

    guard.assert_within_budget(url=url, estimated=estimated)

    remaining_before = guard.last_remaining
    body = json.dumps(scrape_payload(url, formats, wait_for_ms, page_cap)).encode()
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

    remaining_after = guard.refresh()
    cost = guard.record_request_cost(
        url,
        remaining_before if remaining_before is not None else remaining_after,
        remaining_after,
    )
    metadata = data.get("metadata") or {}
    content_type = str(metadata.get("contentType") or "")
    is_pdf = looks_like_pdf(url) or "pdf" in content_type.lower()
    kind = "pdf" if is_pdf else "page"
    truncated, total_pages, num_pages = detect_truncation(metadata, page_cap, cost, is_pdf)
    worst_case = estimated if page_cap is not None else "unbounded"
    print(
        f"credits request cost={cost} worst_case={worst_case} "
        f"max_pages={page_cap} kind={kind} url={url} "
        f"remaining={remaining_after} spent={guard.spent()}",
        file=sys.stderr,
    )
    if page_cap is not None and cost > page_cap:
        # Balance deltas include any concurrent spend on the same team key.
        print(
            f"credits WARNING request cost={cost} exceeded max_pages={page_cap}; "
            "another process may be spending on this key",
            file=sys.stderr,
        )
    if truncated:
        print(
            f"credits WARNING truncated=true url={url} max_pages={page_cap} "
            f"num_pages={num_pages} total_pages={total_pages}; "
            "downstream extraction will see a partial document",
            file=sys.stderr,
        )

    # A truncated response is cached (so a repeat call at the same budget
    # doesn't re-spend), but flagged so it is never handed back as if it
    # were the complete document (see the cache-read checks above).
    hash_cache_body = dict(data)
    hash_cache_body[_HASH_CACHE_TRUNCATED_KEY] = truncated
    key_path.write_text(json.dumps(hash_cache_body), encoding="utf-8")
    markdown = str(data.get("markdown") or "")
    if named_cache_dir is not None and markdown:
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
                "credits_spent": cost,
                "max_pages": page_cap,
                "truncated": truncated,
                "num_pages": num_pages,
                "total_pages": total_pages,
            },
        )
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
    bound = parser.add_mutually_exclusive_group()
    bound.add_argument(
        "--max-pages",
        type=int,
        default=None,
        help="cap PDF pages parsed (Firecrawl parsers.maxPages). Default: remaining --budget",
    )
    bound.add_argument(
        "--allow-unbounded-cost",
        action="store_true",
        help="omit the PDF page cap; a multi-page document may exceed --budget",
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
            max_pages=args.max_pages,
            allow_unbounded=args.allow_unbounded_cost,
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
