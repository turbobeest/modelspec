#!/usr/bin/env python3
"""Curation watcher (MODEL-10 part 1): has any source on a benchmark page changed?

    python3 scripts/curation/watch.py --pages pilot
    python3 scripts/curation/watch.py --pages gpqa_diamond,hle
    python3 scripts/curation/watch.py --immediate-brief https://example.org/new-leaderboard
    python3 scripts/curation/watch.py --pages pilot --firecrawl-credit-cap 5

Every source is fetched with plain HTTP first (zero credits). Firecrawl is used
only for sources on hosts flagged as needing JavaScript (benchmarks/_curation/
js_hosts.yaml) that are also on the census scrape allowlist, only through
scripts/benchmarks/fetch.py's CreditGuard, and only when --firecrawl-credit-cap
is above 0. The default cap is 0.

Per-source state (hash, fetched_at, status, etag, last-modified and the last
good normalised text) lives under --state-dir. A failed fetch never overwrites
the last good state. The run writes change_report.json and change_report.md.
This script never edits a page, never runs git and never prints an API key.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Callable
from urllib.parse import urlparse

import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from scripts.curation.classify import classify  # noqa: E402

BENCH_DIR = ROOT / "benchmarks"
CURATION_DIR = BENCH_DIR / "_curation"
PILOT_FILE = CURATION_DIR / "pilot.txt"
JS_HOSTS_FILE = CURATION_DIR / "js_hosts.yaml"
CENSUS_SOURCES = BENCH_DIR / "_census" / "sources.yaml"
DEFAULT_STATE = CURATION_DIR / "state"
DEFAULT_REPORT = CURATION_DIR / "reports"
PILOT_SIZE = 25
USER_AGENT = "ModelSpecCensus/1.0 (+https://github.com/modelspec)"
#: Truncation guard: a body bigger than this is flagged truncated and never
#: replaces the last good hash, so a partial read is not mistaken for a change.
MAX_BYTES = 8 * 1024 * 1024
BINARY_EXT = (".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".zip", ".gz", ".tar", ".parquet")
RETRY_CODES = (429, 500, 502, 503, 504)


# ---------- pages ----------
def read_page(path: Path) -> tuple[dict, str]:
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", text, re.S)
    if not m:
        return {}, text
    return (yaml.safe_load(m.group(1)) or {}), m.group(2)


def all_pages(bench_dir: Path = BENCH_DIR) -> list[Path]:
    return sorted(p for p in bench_dir.glob("*.md")
                  if not p.name.startswith("_") and p.name not in {"AUTHORING.md", "LICENSE.md", "README.md"})


def select_pilot(bench_dir: Path = BENCH_DIR, size: int = PILOT_SIZE) -> list[str]:
    """Deterministic pilot: `status: active` pages with an http(s) leaderboard_url, first `size` by id."""
    ids = []
    for p in all_pages(bench_dir):
        fm, _ = read_page(p)
        if fm.get("status") == "active" and str(fm.get("leaderboard_url") or "").startswith("http"):
            ids.append(p.stem)
    return sorted(ids)[:size]


def page_sources(fm: dict) -> list[tuple[str, str]]:
    """(url, role) for every source on a page, deduplicated, binaries skipped."""
    out: list[tuple[str, str]] = []
    seen: set[str] = set()

    def add(url: object, role: str) -> None:
        u = str(url or "").strip()
        if not u.startswith(("http://", "https://")) or u in seen:
            return
        if urlparse(u).path.lower().endswith(BINARY_EXT):
            return
        seen.add(u)
        out.append((u, role))

    add(fm.get("leaderboard_url"), "leaderboard")
    add((fm.get("paper") or {}).get("url"), "paper")
    add((fm.get("dataset") or {}).get("url"), "dataset")
    add(fm.get("repo_url"), "repo")
    for s in fm.get("sources") or []:
        if isinstance(s, dict):
            add(s.get("url"), "source")
    return out


# ---------- fetching ----------
@dataclass
class FetchResult:
    url: str
    status: int | None           # HTTP status; None for a network error
    text: str = ""
    etag: str = ""
    last_modified: str = ""
    error: str = ""
    truncated: bool = False
    fetcher: str = "http"

    @property
    def ok(self) -> bool:
        return self.status is not None and 200 <= self.status < 300 and not self.error and not self.truncated


def http_fetch(url: str, timeout: int = 30, retries: int = 3) -> FetchResult:
    """Plain GET with backoff on 429/5xx. Zero Firecrawl credits."""
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    for attempt in range(retries + 1):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                raw = resp.read(MAX_BYTES + 1)
                return FetchResult(
                    url=url, status=resp.status,
                    text=raw[:MAX_BYTES].decode("utf-8", errors="replace"),
                    etag=resp.headers.get("ETag", "") or "",
                    last_modified=resp.headers.get("Last-Modified", "") or "",
                    truncated=len(raw) > MAX_BYTES,
                )
        except urllib.error.HTTPError as exc:
            if exc.code in RETRY_CODES and attempt < retries:
                time.sleep(2 ** attempt)
                continue
            return FetchResult(url=url, status=exc.code, error=f"HTTP {exc.code}")
        except Exception as exc:  # network error, timeout, TLS
            if attempt < retries:
                time.sleep(2 ** attempt)
                continue
            return FetchResult(url=url, status=None, error=type(exc).__name__)
    return FetchResult(url=url, status=None, error="unreachable")


def load_js_hosts() -> set[str]:
    if not JS_HOSTS_FILE.exists():
        return set()
    return set((yaml.safe_load(JS_HOSTS_FILE.read_text()) or {}).get("hosts") or [])


def load_scrape_allow() -> set[str]:
    try:
        return set(yaml.safe_load(CENSUS_SOURCES.read_text())["scrape_allow"])
    except Exception:
        return set()


def host_of(url: str) -> str:
    return urlparse(url).netloc.lower().removeprefix("www.")


@dataclass
class FirecrawlBudget:
    """Wraps fetch.py's guarded scrape. Cap 0 means Firecrawl is never called."""

    cap: int = 0
    allow: set[str] = field(default_factory=set)
    calls: int = 0
    stopped: bool = False
    _guard: object = None

    def fetch(self, url: str) -> FetchResult | None:
        if self.cap <= 0 or self.stopped or host_of(url) not in self.allow:
            return None
        from scripts.benchmarks import fetch as fc  # imported lazily: cap 0 never touches it
        try:
            key = fc.resolve_key()
            if not key:
                self.stopped = True
                return None
            if self._guard is None:
                self._guard = fc.CreditGuard(key=key, budget=self.cap)
            self.calls += 1
            data = fc.scrape(url, ["markdown"], guard=self._guard, max_pages=1)
        except fc.CreditBudgetExceeded:
            self.stopped = True  # stop cleanly; remaining JS sources keep their plain-HTTP reading
            return None
        except (Exception, SystemExit) as exc:
            return FetchResult(url=url, status=None, error=f"firecrawl {type(exc).__name__}", fetcher="firecrawl")
        return FetchResult(url=url, status=200, text=str(data.get("markdown") or ""), fetcher="firecrawl")


# ---------- normalisation and state ----------
_DROP = re.compile(r"<(script|style|noscript|svg|template)\b.*?</\1\s*>|<!--.*?-->", re.S | re.I)
#: Embedded JSON props (Hugging Face and similar) carry live counters and row samples.
_DATA_ATTR = re.compile(r"""\sdata-[\w-]+=(?:"[^"]*"|'[^']*')""", re.S)
_BLOCK = re.compile(r"</?(p|div|li|tr|h[1-6]|br|table|section|article|ul|ol|pre|td|th)\b[^>]*>", re.I)
_TAG = re.compile(r"<[^>]+>")
#: Volatile tokens that change on every request and would otherwise be noise.
_VOLATILE = [
    re.compile(r"\b\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}(:\d{2})?(\.\d+)?(Z|[+-]\d{2}:?\d{2})?\b"),
    re.compile(r"\b(nonce|csrf[-_]?token|request[-_]?id|cf-ray)\W+[\w-]+", re.I),
    re.compile(r"\b[0-9a-f]{32,64}\b", re.I),
    re.compile(r"\b(?:(?:about|almost|over|less than) )?(?:an?|a few|\d+) "
               r"(?:second|minute|hour|day|week|month|year)s? ago\b", re.I),
]


def normalise(text: str) -> str:
    t = _DROP.sub(" ", _DATA_ATTR.sub("", text))
    t = _BLOCK.sub("\n", t)
    t = html.unescape(_TAG.sub(" ", t))
    for rx in _VOLATILE:
        t = rx.sub("", t)
    lines = [re.sub(r"[ \t\r\f\v]+", " ", ln).strip() for ln in t.splitlines()]
    return "\n".join(ln for ln in lines if ln)


def state_key(url: str) -> str:
    return hashlib.sha256(url.encode()).hexdigest()[:24]


def load_state(state_dir: Path, url: str) -> tuple[dict | None, str]:
    meta = state_dir / f"{state_key(url)}.json"
    if not meta.exists():
        return None, ""
    txt = state_dir / f"{state_key(url)}.txt"
    return json.loads(meta.read_text()), (txt.read_text(encoding="utf-8") if txt.exists() else "")


def save_state(state_dir: Path, url: str, meta: dict, text: str | None) -> None:
    state_dir.mkdir(parents=True, exist_ok=True)
    (state_dir / f"{state_key(url)}.json").write_text(json.dumps(meta, indent=1, sort_keys=True))
    if text is not None:
        (state_dir / f"{state_key(url)}.txt").write_text(text, encoding="utf-8")


# ---------- the watch ----------
def watch(
    page_ids: list[str],
    state_dir: Path,
    *,
    bench_dir: Path = BENCH_DIR,
    fetcher: Callable[[str], FetchResult] = http_fetch,
    firecrawl: FirecrawlBudget | None = None,
    js_hosts: set[str] | None = None,
    max_workers: int = 8,
    now: str | None = None,
) -> dict:
    now = now or datetime.now(UTC).isoformat(timespec="seconds")
    firecrawl = firecrawl or FirecrawlBudget(cap=0)
    js_hosts = load_js_hosts() if js_hosts is None else js_hosts

    work: dict[str, list[tuple[str, str, dict]]] = {}
    for pid in page_ids:
        path = bench_dir / f"{pid}.md"
        fm, _ = read_page(path)
        for url, role in page_sources(fm):
            work.setdefault(url, []).append((pid, role, fm))

    urls = sorted(work)
    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        results = dict(zip(urls, pool.map(fetcher, urls)))

    changes, failures, baselines, needs_js = [], [], [], []
    unchanged = 0
    for url in urls:
        res = results[url]
        if host_of(url) in js_hosts:
            fc = firecrawl.fetch(url)  # None when the cap is 0, spent, or host not allowlisted
            if fc is not None:
                res = fc
            else:
                needs_js.append(url)
        prev, prev_text = load_state(state_dir, url)
        pages = [{"page": pid, "role": role} for pid, role, _ in work[url]]
        if not res.ok:
            # Keep the last good hash and text; record only the failure.
            meta = dict(prev or {})
            meta.update({"url": url, "last_error": res.error or "truncated", "last_status": res.status,
                         "last_attempt": now})
            save_state(state_dir, url, meta, None)
            kinds = classify(url=url, roles=[p["role"] for p in pages], old="", new="",
                             status=res.status, prev_status=(prev or {}).get("status"))
            failures.append({"url": url, "pages": pages, "status": res.status,
                             "error": res.error or "truncated", "kinds": kinds,
                             "had_good_state": bool(prev and prev.get("hash"))})
            continue
        text = normalise(res.text)
        digest = hashlib.sha256(text.encode()).hexdigest()
        meta = {"url": url, "hash": digest, "fetched_at": now, "status": res.status, "etag": res.etag,
                "last_modified": res.last_modified, "fetcher": res.fetcher, "last_error": "",
                "last_status": res.status, "last_attempt": now}
        if prev is None or not prev.get("hash"):
            baselines.append(url)
            save_state(state_dir, url, meta, text)
        elif prev["hash"] == digest:
            unchanged += 1
            save_state(state_dir, url, meta, None)
        else:
            kinds = classify(url=url, roles=[p["role"] for p in pages], old=prev_text, new=text,
                             status=res.status, prev_status=prev.get("status"))
            changes.append({"url": url, "pages": pages, "kinds": kinds, "previous_fetched_at": prev.get("fetched_at"),
                            "fetched_at": now, "old_hash": prev["hash"], "new_hash": digest})
            save_state(state_dir, url, meta, text)

    return {
        "axis": "benchmarks",
        "run_at": now,
        "pages": page_ids,
        "sources_checked": len(urls),
        "unchanged": unchanged,
        "baselined": len(baselines),
        "changes": changes,
        "failures": failures,
        "needs_js_not_rendered": needs_js,
        "firecrawl": {"cap": firecrawl.cap, "calls": firecrawl.calls, "stopped": firecrawl.stopped},
    }


def effective_firecrawl_cap(requested: int, key_from_env: bool, env: dict | None = None) -> tuple[int, str]:
    """In CI the key comes only from FIRECRAWL_API_KEY. Empty key: cap 0, plain HTTP only, never a failure."""
    env = os.environ if env is None else env
    if requested > 0 and key_from_env and not str(env.get("FIRECRAWL_API_KEY") or "").strip():
        return 0, f"FIRECRAWL_API_KEY is empty: plain HTTP only (Firecrawl cap {requested} -> 0)"
    return requested, ""


def export_source_texts(report: dict, state_dir: Path, report_dir: Path) -> None:
    """Copy each changed source's new normalised text next to the report, for the drafter job."""
    out = report_dir / "sources"
    for c in report["changes"]:
        _, text = load_state(state_dir, c["url"])
        out.mkdir(parents=True, exist_ok=True)
        (out / f"{state_key(c['url'])}.txt").write_text(text or "", encoding="utf-8")
        c["source_text"] = f"sources/{state_key(c['url'])}.txt"


def resolve_pages(spec: str, bench_dir: Path = BENCH_DIR) -> list[str]:
    if spec == "pilot":
        if PILOT_FILE.exists() and bench_dir == BENCH_DIR:
            return [ln.strip() for ln in PILOT_FILE.read_text().splitlines() if ln.strip() and not ln.startswith("#")]
        return select_pilot(bench_dir)
    if spec == "all":
        return [p.stem for p in all_pages(bench_dir)]
    ids = [s.strip() for s in spec.split(",") if s.strip()]
    missing = [i for i in ids if not (bench_dir / f"{i}.md").exists()]
    if missing:
        raise SystemExit(f"unknown page ids: {missing}")
    return ids


def immediate_brief(target: str, bench_dir: Path = BENCH_DIR) -> tuple[list[str], list[str]]:
    """A page id, or a URL. A URL matches pages citing it (exact or as prefix); no match is a census lead."""
    if not target.startswith(("http://", "https://")):
        return resolve_pages(target, bench_dir), []
    hits = []
    for p in all_pages(bench_dir):
        fm, _ = read_page(p)
        if any(u == target or u.startswith(target.rstrip("/") + "/") for u, _ in page_sources(fm)):
            hits.append(p.stem)
    return hits, ([] if hits else [target])


def render_md(report: dict) -> str:
    lines = [f"# Curation change report ({report['axis']})", "",
             f"Run at {report['run_at']}. Pages: {len(report['pages'])}. Sources checked: "
             f"{report['sources_checked']}. Unchanged: {report['unchanged']}. Baselined: {report['baselined']}. "
             f"Changed: {len(report['changes'])}. Failed: {len(report['failures'])}. "
             f"Firecrawl calls: {report['firecrawl']['calls']} (cap {report['firecrawl']['cap']}).", ""]
    if report["firecrawl"].get("note"):
        lines += [f"**Firecrawl:** {report['firecrawl']['note']}", ""]
    if report.get("census_leads"):
        lines += ["## Census leads (immediate brief matched no page)", ""]
        lines += [f"- {u}" for u in report["census_leads"]] + [""]
    lines += ["## Changes", ""]
    for c in report["changes"]:
        pages = ", ".join(p["page"] for p in c["pages"])
        kinds = "; ".join(f"{k['kind']} ({k['evidence']})" for k in c["kinds"])
        lines.append(f"- {c['url']} [{pages}]: {kinds}")
    lines += ["", "## Failures", ""]
    for f in report["failures"]:
        pages = ", ".join(p["page"] for p in f["pages"])
        kinds = ", ".join(k["kind"] for k in f["kinds"])
        lines.append(f"- {f['url']} [{pages}]: {f['error']} {kinds}")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--axis", default="benchmarks", choices=["benchmarks", "models"])
    ap.add_argument("--pages", default="pilot", help="pilot | all | comma-separated ids")
    ap.add_argument("--immediate-brief", default="", help="a page id or a URL to watch right now")
    ap.add_argument("--state-dir", type=Path, default=DEFAULT_STATE)
    ap.add_argument("--report-dir", type=Path, default=DEFAULT_REPORT)
    ap.add_argument("--firecrawl-credit-cap", type=int, default=0)
    ap.add_argument("--firecrawl-key-from-env", action="store_true",
                    help="CI: take the key only from FIRECRAWL_API_KEY; empty means plain HTTP only (cap 0)")
    ap.add_argument("--max-workers", type=int, default=8)
    ap.add_argument("--write-pilot", action="store_true", help="recompute and record the pilot list")
    args = ap.parse_args(argv)

    if args.axis == "models":
        print("axis=models is not wired yet (MODEL-5 moves here later); see docs/curation-loop.md", file=sys.stderr)
        return 2
    if args.write_pilot:
        ids = select_pilot()
        PILOT_FILE.write_text("# MODEL-10 pilot: status active + leaderboard_url, first 25 by id\n" + "\n".join(ids) + "\n")
        print(f"wrote {len(ids)} ids to {PILOT_FILE.relative_to(ROOT)}")
        return 0

    leads: list[str] = []
    if args.immediate_brief:
        page_ids, leads = immediate_brief(args.immediate_brief)
    else:
        page_ids = resolve_pages(args.pages)
    cap, note = effective_firecrawl_cap(args.firecrawl_credit_cap, args.firecrawl_key_from_env)
    fc = FirecrawlBudget(cap=cap, allow=load_scrape_allow())
    report = watch(page_ids, args.state_dir, firecrawl=fc, max_workers=args.max_workers)
    report["firecrawl"]["requested_cap"] = args.firecrawl_credit_cap
    report["firecrawl"]["note"] = note
    report["census_leads"] = leads
    args.report_dir.mkdir(parents=True, exist_ok=True)
    export_source_texts(report, args.state_dir, args.report_dir)
    (args.report_dir / "change_report.json").write_text(json.dumps(report, indent=1))
    (args.report_dir / "change_report.md").write_text(render_md(report))
    print(render_md(report).split("\n## Changes")[0].strip())
    return 0


if __name__ == "__main__":
    sys.exit(main())
