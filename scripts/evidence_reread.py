"""Rolling weekly re-read of the evidence rows no live-board collector reads (MODEL-534).

Each run takes the verified benchmark rows whose latest check is oldest, up to
WEEKLY_ROW_CAP rows, fetches each cited page once, keeps a copy where the host's
terms allow it, and re-verifies the row with the same deterministic reader that
verified it (``structured-row-match@1``). It never edits a card.

- A row that no longer matches is logged as ``mismatch`` and listed in the report.
- A page that is gone (404 or 410) is logged as ``unreachable``.
- A timeout, a 5xx, a rate limit or a refused redirect writes nothing: the row stays
  oldest and is read again next week.
- A cite-only host keeps no bytes. The read is a ``cited`` check with its date.
- A host that is neither a cite-only host nor classed ``permits`` or
  ``restricts`` in ``registry/source-terms.json`` is not requested at all.
  That includes a redirect target. Such hosts are listed for the owner.

No paid client is used, and no model is called.
"""

from __future__ import annotations

import argparse
import gzip
import json
import time
from collections import Counter, defaultdict
from dataclasses import dataclass, field, replace
from datetime import UTC, date, datetime
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import urljoin, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

from decision.retention import cite_only_origin_restrictive

METHOD = "structured-row-match@1"
#: The most rows one run re-verifies. A group of rows that share a page is taken whole.
WEEKLY_ROW_CAP = 400
#: Rows verified more recently than this are left to the collector that just read them.
MIN_AGE_DAYS = 14
#: A source the live-board refresh wrote to this recently is the refresh's to read.
REFRESH_WINDOW_DAYS = 30
REFRESH_COLLECTOR = "weekly-live-board-refresh"
#: Pages whose retained copy is a table the live-board refresh builds from a dataset or an
#: API (parquet files, a JSON backend). The page itself does not hold the rows.
OWNED_BY_REFRESH_PREFIXES = (
    "https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset",
    "https://mteb-leaderboard-backend.hf.space/",
)
#: The pause between two requests to one host.
HOST_DELAY_SECONDS = 2.0
MAX_BODY_BYTES = 8 * 1024 * 1024
MAX_HOPS = 3
TIMEOUT_SECONDS = 60
USER_AGENT = "ModelSpec-Evidence-Reread/1.0 (+https://modelspec.dev)"
COPIES_DIRECTORY = "reports/evidence-reread/source-copies"
RETAINING_CLASSES = frozenset({"permits", "restricts"})
GONE = frozenset({404, 410})


# --- host class --------------------------------------------------------------------------------


def cite_only(url: str, resolved=()) -> bool:
    """Whether the engine's policy forbids keeping bytes from any of these origins."""
    return cite_only_origin_restrictive(url, tuple(resolved))


def load_terms(root: Path) -> dict[str, str]:
    path = root / "registry" / "source-terms.json"
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}


def host_of(url: str) -> str:
    return (urlsplit(url).hostname or "").lower().rstrip(".")


def host_class(url: str, terms: dict[str, str]) -> str:
    """``forbids``, ``cite-only``, ``retaining`` or ``unclassed``.

    ``forbids`` (the private register) is kept apart from ``cite-only`` (the public list);
    the engine keeps no bytes for either. A page of either may be read as an origin, to cite
    it. Neither is ever requested as a redirect target, and an ``unclassed`` host is
    never requested at all.

    A malformed or non-HTTP origin is ``unclassed``. A host the register marks ``forbids``
    is ``forbids`` even though the engine's cite-only policy also covers it.
    """
    if urlsplit(url).scheme not in {"http", "https"} or not host_of(url):
        return "unclassed"
    if terms.get(host_of(url)) == "forbids":
        return "forbids"
    if terms.get(host_of(url)) == "cite-only" or cite_only(url):
        # The register's own ``cite-only`` class (the owner holds the host until counsel
        # reads its terms) is read like the public list, with or without a data directory.
        return "cite-only"
    return "retaining" if terms.get(host_of(url)) in RETAINING_CLASSES else "unclassed"


# --- projectors --------------------------------------------------------------------------------

OLL_PREFIXES = {
    "v1": "https://huggingface.co/datasets/open-llm-leaderboard-old/results/resolve/",
    "v2": "https://huggingface.co/datasets/open-llm-leaderboard/results/resolve/",
}


def project_oll(url: str, body: bytes, observed_at: date) -> bytes | None:
    """The row table the verifier reads, from an Open LLM Leaderboard result file.

    The first verification read this projection of the file, not the file. The metric
    maths is the engine's (``scripts.migrate_oll_evidence``). Returns ``None`` for any
    other URL. The page itself, not this projection, is what a run keeps.
    """
    version = next((v for v, prefix in OLL_PREFIXES.items() if url.startswith(prefix)), None)
    if version is None:
        return None
    from scripts import migrate_oll_evidence as oll  # noqa: PLC0415

    path = url.split("/resolve/", 1)[1].split("/", 1)[1]
    data = json.loads(body)
    identity, evaluated, scores = (oll.extract_v1_scores(data, path) if version == "v1"
                                   else oll.extract_v2_scores(data, path))
    row = {"model": identity, "date": evaluated.isoformat(),
           **{key: f"{value}%" for key, value in scores.items()}}
    payload = {"source_url": url, "read_date": observed_at.isoformat(), "rows": [row],
               "provenance": {"projection": "OLL result metrics as percent; aggregates are "
                                            "arithmetic means of the published subtasks"}}
    return (json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n").encode()


def readable(url: str, body: bytes, observed_at: date) -> bytes:
    """The bytes the verifier reads: a projection where the first read used one."""
    try:
        projected = project_oll(url, body, observed_at)
    except (ValueError, KeyError, TypeError):
        return body  # not the file it was; the reader then finds no row
    return body if projected is None else projected


# --- the read ----------------------------------------------------------------------------------


@dataclass
class Fetched:
    #: ``ok``, ``gone``, ``deferred`` (try again next week) or ``blocked`` (unclassed redirect).
    kind: str
    body: bytes = b""
    resolved: tuple[str, ...] = ()
    reason: str = ""
    blocked_host: str | None = None


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


def request_once(url: str) -> tuple[int, str | None, bytes]:
    """One request with redirects off: the status, the Location header and the body."""
    opener = build_opener(_NoRedirect)
    try:
        with opener.open(Request(url, headers={"User-Agent": USER_AGENT}),
                         timeout=TIMEOUT_SECONDS) as response:
            body = response.read(MAX_BODY_BYTES + 1)
            return response.status, None, body
    except HTTPError as error:
        return error.code, error.headers.get("Location"), b""


def fetch(url: str, terms: dict[str, str], *, request=None) -> Fetched:
    """Read ``url``, following at most MAX_HOPS redirects, each to a classed host.

    ``request`` defaults to the module's ``request_once``, looked up at call time.
    """
    request = request or request_once
    resolved: list[str] = []
    current = url
    for _ in range(MAX_HOPS + 1):
        try:
            status, location, body = request(current)
        except Exception as error:  # a network failure is not evidence that the page is gone
            return Fetched("deferred", resolved=tuple(resolved),
                           reason=f"{type(error).__name__}")
        if 300 <= status < 400 and location:
            target = urljoin(current, location)
            target_class = host_class(target, terms)
            if target_class != "retaining":
                # Nothing was read: the row waits, and the owner sees the host.
                return Fetched("blocked", resolved=tuple(resolved),
                               reason=f"redirect to a {target_class} host; not requested",
                               blocked_host=host_of(target) or "?")
            resolved.append(target)
            current = target
            continue
        if status in GONE:
            return Fetched("gone", resolved=tuple(resolved), reason=f"HTTP {status}")
        if status != 200:
            return Fetched("deferred", resolved=tuple(resolved), reason=f"HTTP {status}")
        if len(body) > MAX_BODY_BYTES:
            return Fetched("deferred", resolved=tuple(resolved), reason="body over the size limit")
        return Fetched("ok", body, tuple(resolved))
    return Fetched("deferred", resolved=tuple(resolved), reason="too many redirects")


class Pacer:
    """At least HOST_DELAY_SECONDS between two requests to the same host."""

    def __init__(self, delay: float = HOST_DELAY_SECONDS, *, sleep=time.sleep,
                 clock=time.monotonic) -> None:
        self.delay, self.sleep, self.clock = delay, sleep, clock
        self.last: dict[str, float] = {}

    def wait(self, host: str) -> None:
        if host in self.last:
            remaining = self.delay - (self.clock() - self.last[host])
            if remaining > 0:
                self.sleep(remaining)
        self.last[host] = self.clock()


# --- the window --------------------------------------------------------------------------------


@dataclass
class Row:
    claim: object
    last_verified: date
    urls: tuple[str, ...]


@dataclass
class Window:
    rows: list[Row] = field(default_factory=list)
    #: Rows left out because a source host is unclassed, by host.
    unclassed: Counter = field(default_factory=Counter)
    #: Eligible rows left for a later week.
    waiting: int = 0
    #: Verified rows of another method, or whose filed claim is not the verified value.
    other_method: int = 0
    stale_claim: int = 0
    too_fresh: int = 0
    #: Rows on a source the live-board refresh read within REFRESH_WINDOW_DAYS.
    covered: int = 0
    owned_by_refresh: int = 0


def select_window(root: Path, sources, terms: dict[str, str], today: date, *,
                  cap: int = WEEKLY_ROW_CAP, min_age_days: int = MIN_AGE_DAYS) -> Window:
    """The oldest-verified rows first, whole page groups, at most ``cap`` rows."""
    from decision import verify as v
    from decision.model import verification_value_hash

    directory = root / "verification"
    filed = v.Queue(directory).filed()
    log = v.VerificationLog(directory)
    window = Window()
    eligible: list[Row] = []
    covered_sources: set[str] = set()
    for record in log.records():
        if (record.collector.method.startswith(REFRESH_COLLECTOR)
                and (today - record.date).days <= REFRESH_WINDOW_DAYS
                and record.target.kind == "evidence"):
            read = filed.get(("evidence", record.target.id))
            if read:
                covered_sources.update(s.source_id for s in read.sources)
    for (kind, target_id), record in log.latest().items():
        if kind != "evidence" or record.outcome != "verified":
            continue
        if record.method != METHOD:
            window.other_method += 1
            continue
        claim = filed.get((kind, target_id))
        if claim is None or verification_value_hash(
                v.claim_verification_value(claim), unordered=False) != record.target.value_hash:
            window.stale_claim += 1
            continue
        if covered_sources & {s.source_id for s in claim.sources}:
            window.covered += 1
            continue
        urls = tuple(sources[s.source_id].url for s in claim.sources if s.source_id in sources)
        if len(urls) != len(claim.sources):
            window.stale_claim += 1
            continue
        if any(str(url).startswith(OWNED_BY_REFRESH_PREFIXES) for url in urls):
            window.owned_by_refresh += 1
            continue
        classes = {url: host_class(str(url), terms) for url in urls}
        blocked = [host_of(str(url)) for url, cls in classes.items() if cls == "unclassed"]
        if blocked:
            window.unclassed[blocked[0]] += 1
            continue
        if (today - record.date).days < min_age_days:
            window.too_fresh += 1
            continue
        eligible.append(Row(claim, record.date, tuple(str(u) for u in urls)))
    groups: dict[tuple[str, ...], list[Row]] = defaultdict(list)
    for row in eligible:
        groups[row.urls].append(row)
    ordered = sorted(groups.values(), key=lambda g: (min(r.last_verified for r in g),
                                                     g[0].urls))
    for group in ordered:
        if len(window.rows) + len(group) <= cap:
            window.rows.extend(sorted(group, key=lambda r: r.claim.target.id))
        else:
            window.waiting += len(group)
    return window


# --- the run -----------------------------------------------------------------------------------


@dataclass
class Report:
    observed_at: str
    dry_run: bool
    cap: int = WEEKLY_ROW_CAP
    selected: int = 0
    counts: Counter = field(default_factory=Counter)
    by_host: dict[str, Counter] = field(default_factory=lambda: defaultdict(Counter))
    bytes_retained: int = 0
    copies_retained: int = 0
    copies_already_kept: int = 0
    pages: int = 0
    mismatches: list[str] = field(default_factory=list)
    unreachable: list[str] = field(default_factory=list)
    blocked_hosts: Counter = field(default_factory=Counter)
    unclassed_hosts: dict[str, int] = field(default_factory=dict)
    waiting: int = 0
    unread: list[str] = field(default_factory=list)

    def note(self, outcome: str, host: str, target_id: str = "") -> None:
        self.counts[outcome] += 1
        self.by_host[host][outcome] += 1

    def to_dict(self) -> dict:
        return {
            "observed_at": self.observed_at, "dry_run": self.dry_run, "cap": self.cap,
            "method": METHOD, "selected_rows": self.selected, "pages_read": self.pages,
            "counts": {k: self.counts.get(k, 0) for k in (
                "verified", "mismatch", "unreachable", "cited", "deferred", "unread")},
            "by_host": {h: dict(c) for h, c in sorted(self.by_host.items())},
            "bytes_retained": self.bytes_retained, "copies_retained": self.copies_retained,
            "copies_already_kept": self.copies_already_kept,
            "mismatches": sorted(self.mismatches), "unreachable": sorted(self.unreachable),
            "unread": sorted(self.unread),
            "blocked_redirect_hosts": dict(self.blocked_hosts),
            "unclassed_hosts_not_requested": self.unclassed_hosts,
            "rows_waiting_for_a_later_week": self.waiting,
        }


def run(root: Path, *, observed_at: date, dry_run: bool, store_root: Path,
        cap: int = WEEKLY_ROW_CAP, request=None, pacer: Pacer | None = None,
        min_age_days: int = MIN_AGE_DAYS) -> Report:
    from decision import verify as v
    from decision.sources import CopyStore, load_sources

    pacer = pacer or Pacer()
    terms = load_terms(root)
    sources = load_sources(root / "registry" / "sources.yaml")
    window = select_window(root, sources, terms, observed_at, cap=cap,
                           min_age_days=min_age_days)
    report = Report(observed_at.isoformat(), dry_run, cap, selected=len(window.rows),
                    waiting=window.waiting, unclassed_hosts=dict(window.unclassed))
    store = CopyStore(store_root)
    regions = v.StoredRegions(store, sources, cache_documents=True)
    extractors = [v.StructuredDataExtractor()]
    queue, log = v.Queue(root / "verification"), v.VerificationLog(root / "verification")
    at = datetime.combine(observed_at, datetime.min.time(), UTC)

    pages: dict[str, Fetched] = {}
    refs: dict[str, str] = {}
    for row in window.rows:
        for url in row.urls:
            if url in pages:
                continue
            pacer.wait(host_of(url))
            result = pages[url] = fetch(url, terms, request=request)
            report.pages += 1
            if result.kind == "blocked":
                report.blocked_hosts[result.blocked_host] += 1
            if result.kind != "ok":
                continue
            page_ref = store.put(result.body, source_url=url, retrieved_at=at,
                                 resolved_urls=result.resolved)
            read = readable(url, result.body, observed_at)
            refs[url] = page_ref if read is result.body else store.put(
                read, source_url=url, retrieved_at=at, resolved_urls=result.resolved)
            if store.citation(page_ref) is not None or cite_only(url, result.resolved):
                continue
            digest = page_ref.split(":", 1)[1]
            target = root / COPIES_DIRECTORY / digest[:2] / f"{digest}.gz"
            if target.exists():
                report.copies_already_kept += 1
            elif dry_run:
                report.copies_retained += 1
                report.bytes_retained += len(gzip.compress(result.body, mtime=0))
            else:
                # Only a host whose terms allow a copy reaches this line (checked above).
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(gzip.compress(result.body, mtime=0))
                report.copies_retained += 1
                report.bytes_retained += target.stat().st_size

    for row in window.rows:
        claim, host = row.claim, host_of(row.urls[0])
        results = [pages[url] for url in row.urls]
        bad = next((r for r in results if r.kind != "ok"), None)
        if bad is not None:
            if bad.kind == "gone":
                outcome = v.Result(
                    claim.target, "unreachable",
                    v._verification(claim, v.REGION_LOOKUP, "unreachable", observed_at),
                    reason=bad.reason)
                report.unreachable.append(claim.target.id)
                _record(outcome, queue, log, at, dry_run)
                report.note("unreachable", host)
            else:
                report.note("deferred", host)
            continue
        pinned = replace(claim, sources=tuple(
            s.model_copy(update={"snapshot_ref": refs[url]})
            for s, url in zip(claim.sources, row.urls, strict=True)))
        result = v.verify(pinned, regions, extractors, today=observed_at)
        if result.outcome in {"verified", "mismatch"}:
            _record(result, queue, log, at, dry_run)
            if result.outcome == "mismatch":
                report.mismatches.append(claim.target.id)
        elif result.outcome == "cited":
            if not dry_run:
                queue.checked(result, at=at)
        elif result.outcome == "unreachable":
            _record(result, queue, log, at, dry_run)
            report.unreachable.append(claim.target.id)
        else:
            report.unread.append(claim.target.id)
            report.note("unread", host)
            continue
        report.note(result.outcome, host)
    return report


def _record(result, queue, log, at: datetime, dry_run: bool) -> None:
    """A mismatch or an unreachable page is written down, never overwritten."""
    if dry_run:
        return
    if result.verification is not None:
        log.append(result.verification)
    queue.checked(result, at=at)


def render(report: Report) -> str:
    data = report.to_dict()
    lines = [f"## Evidence re-read ({METHOD}), {data['observed_at']}"
             + (" (dry run)" if data["dry_run"] else ""), ""]
    lines.append(f"- Rows in this window: {data['selected_rows']} of at most {data['cap']}; "
                 f"{data['pages_read']} pages read; {data['rows_waiting_for_a_later_week']} "
                 "eligible rows wait for a later week.")
    lines.append("- Outcomes: " + ", ".join(f"{k} {n}" for k, n in data["counts"].items()) + ".")
    lines.append(f"- Copies kept: {data['copies_retained']} new "
                 f"({data['bytes_retained']} bytes), {data['copies_already_kept']} already kept.")
    for host, counts in data["by_host"].items():
        lines.append(f"- {host}: " + ", ".join(f"{k} {n}" for k, n in sorted(counts.items())))
    if data["mismatches"]:
        lines += ["", "### Mismatch: these rows no longer match their source", ""]
        lines += [f"- {target}" for target in data["mismatches"]]
    if data["unreachable"]:
        lines += ["", "### Unreachable: the page is gone", ""]
        lines += [f"- {target}" for target in data["unreachable"]]
    if data["blocked_redirect_hosts"] or data["unclassed_hosts_not_requested"]:
        lines += ["", "### Hosts not requested (unclassed, for the owner)", ""]
        for host, n in {**data["unclassed_hosts_not_requested"],
                        **data["blocked_redirect_hosts"]}.items():
            lines.append(f"- {host}: {n}")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--observed-at", default=date.today().isoformat())
    parser.add_argument("--source-cache", type=Path, required=True)
    parser.add_argument("--report-json", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    report = run(args.root.resolve(), observed_at=date.fromisoformat(args.observed_at),
                 dry_run=args.dry_run, store_root=args.source_cache)
    print(render(report))
    if args.report_json:
        args.report_json.write_text(json.dumps(report.to_dict(), indent=2, sort_keys=True) + "\n",
                                    encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
