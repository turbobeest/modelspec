"""Source registry and deterministic change detection (MODEL-137).

Every test runs against local fixtures through ``httpx.MockTransport``: no
test touches the network, and none needs an agent.
"""

from __future__ import annotations

import ast
import subprocess
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

import httpx
import pytest

from decision.normalise import (
    NORMALISERS,
    Locator,
    canonical_url,
    normalise_document,
    select_region,
)
from decision.sources import (
    DEFAULT_INTERVALS,
    Citation,
    CitedRegion,
    CopyStore,
    FactKind,
    Fetcher,
    FetchMode,
    RegionStatus,
    Source,
    SourceState,
    due,
    load_sources,
    recheck,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURES = Path(__file__).parent / "fixtures" / "sources"
URL = "https://lab.example.com/pricing"
T0 = datetime(2026, 9, 24, 12, 0, tzinfo=UTC)


def test_source_recheck_uses_the_shared_domain_types() -> None:
    from decision.model import Source as DomainSource
    from decision.model import SourceSnapshot as DomainSourceSnapshot
    from decision.sources import SourceSnapshot as RecheckSourceSnapshot

    assert Source is DomainSource
    assert RecheckSourceSnapshot is DomainSourceSnapshot


def test_source_registry_rejects_xpath_instead_of_dropping_the_region(tmp_path: Path) -> None:
    path = tmp_path / "sources.yaml"
    path.write_text(
        """schema_version: 1
sources:
  - id: source
    url: https://example.test/page
    fetch: conditional_http
    normaliser: html-default
    cited_regions:
      - id: result
        locator: {kind: xpath, value: "//table[1]"}
"""
    )
    with pytest.raises(ValueError, match="xpath cited-region locators are not supported"):
        load_sources(path)


def fixture(name: str) -> bytes:
    return (FIXTURES / name).read_bytes()


def pricing_source(**kw: object) -> Source:
    defaults: dict[str, object] = {
        "id": "example-lab-pricing",
        "url": URL,
        "fetch": FetchMode.CONDITIONAL_HTTP,
        "normaliser": "html-default",
        "cited_regions": (
            CitedRegion(id="price-table", locator={"kind": "table", "value": "0"}),
            CitedRegion(id="rate-limits", locator={"kind": "heading", "value": "rate-limits"}),
            CitedRegion(id="data-handling", locator={"kind": "heading", "value": "Data handling"}),
        ),
    }
    defaults.update(kw)
    return Source(**defaults)  # type: ignore[arg-type]


CITATIONS = (
    Citation(
        "fact:example-large/price-input", "example-lab-pricing", "price-table", FactKind.PRICE
    ),
    Citation(
        "fact:example-small/price-output", "example-lab-pricing", "price-table", FactKind.PRICE
    ),
    Citation(
        "fact:example-large/rate-limit", "example-lab-pricing", "rate-limits", FactKind.RATE_LIMIT
    ),
    Citation(
        "fact:example-large/data-retention",
        "example-lab-pricing",
        "data-handling",
        FactKind.GOVERNANCE,
    ),
)


class Server:
    """A scripted origin: each request pops the next response (or exception)."""

    def __init__(self, *responses: object) -> None:
        self.responses = list(responses)
        self.requests: list[httpx.Request] = []

    def __call__(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        if not self.responses:
            raise AssertionError(f"unexpected request to {request.url}")
        nxt = self.responses.pop(0)
        if isinstance(nxt, Exception):
            raise nxt
        if callable(nxt):
            return nxt(request)  # type: ignore[no-any-return]
        return nxt  # type: ignore[return-value]


def html(
    body: bytes, *, etag: str | None = None, last_modified: str | None = None
) -> httpx.Response:
    headers = {"content-type": "text/html; charset=utf-8"}
    if etag:
        headers["etag"] = etag
    if last_modified:
        headers["last-modified"] = last_modified
    return httpx.Response(200, headers=headers, content=body)


class FakeClock:
    def __init__(self) -> None:
        self.now = 1000.0
        self.sleeps: list[float] = []

    def monotonic(self) -> float:
        return self.now

    def sleep(self, seconds: float) -> None:
        self.sleeps.append(seconds)
        self.now += seconds


def fetcher_for(server: Server, clock: FakeClock | None = None, **kw: object) -> Fetcher:
    clock = clock or FakeClock()
    client = httpx.Client(transport=httpx.MockTransport(server))
    return Fetcher(client, sleep=clock.sleep, clock=clock.monotonic, **kw)  # type: ignore[arg-type]


def run(
    server: Server,
    store: CopyStore,
    states: dict[str, SourceState] | None = None,
    *,
    sources: tuple[Source, ...] | None = None,
    now: datetime = T0,
    **kw: object,
):
    sources = sources or (pricing_source(),)
    return recheck(
        sources,
        states or {},
        CITATIONS,
        fetcher=fetcher_for(server),
        store=store,
        now=now,
        **kw,  # type: ignore[arg-type]
    )


@pytest.fixture
def store(tmp_path: Path) -> CopyStore:
    return CopyStore(tmp_path / "copies")


def baseline(store: CopyStore, body: bytes = b"", **headers: str):
    report = run(Server(html(body or fixture("pricing_v1.html"), **headers)), store)
    return report.states


def statuses(report) -> dict[str, RegionStatus]:
    return {r.region_id: r.status for r in report.regions}


# --- acceptance: cosmetic, table edit, 304, unreachable ---------------------------------------


def test_cosmetic_change_is_unchanged(store: CopyStore) -> None:
    states = baseline(store)
    report = run(
        Server(html(fixture("pricing_v1_cosmetic.html"))), store, states, now=T0 + timedelta(days=7)
    )

    assert set(statuses(report).values()) == {RegionStatus.UNCHANGED}
    assert report.requeue == []
    assert report.alerts == []
    assert sorted(report.reconfirmed) == sorted(c.ref for c in CITATIONS)
    # Ads, footer, timestamps, attribute order, whitespace and tracking strings are
    # all normalised away, so even the page fingerprint holds.
    new = report.states["example-lab-pricing"].snapshot
    assert new.page_fingerprint == states["example-lab-pricing"].snapshot.page_fingerprint


def test_table_edit_requeues_exactly_the_facts_citing_it(store: CopyStore) -> None:
    states = baseline(store)
    report = run(Server(html(fixture("pricing_v2_table_edit.html"))), store, states)

    assert statuses(report) == {
        "price-table": RegionStatus.CHANGED,
        "rate-limits": RegionStatus.UNCHANGED,
        "data-handling": RegionStatus.UNCHANGED,
    }
    assert report.requeue == [
        "fact:example-large/price-input",
        "fact:example-small/price-output",
    ]
    assert "fact:example-large/rate-limit" in report.reconfirmed
    assert report.alerts == []  # no governance region changed
    # The unrelated changelog edit moves the page fingerprint but no decision uses it.
    result = report.states["example-lab-pricing"]
    assert (
        result.snapshot.page_fingerprint != states["example-lab-pricing"].snapshot.page_fingerprint
    )


def test_governance_region_change_emits_an_alert(store: CopyStore) -> None:
    states = baseline(store)
    report = run(Server(html(fixture("pricing_v3_retention_edit.html"))), store, states)

    assert report.requeue == ["fact:example-large/data-retention"]
    [alert] = report.alerts
    assert alert.source_id == "example-lab-pricing"
    assert alert.region_id == "data-handling"
    assert alert.refs == ("fact:example-large/data-retention",)
    assert (
        alert.previous_fingerprint
        == states["example-lab-pricing"].snapshot.region_fingerprints["data-handling"]
    )
    assert alert.current_fingerprint != alert.previous_fingerprint
    assert alert.previous_copy_ref != alert.current_copy_ref
    assert store.get(alert.previous_copy_ref) == fixture("pricing_v1.html")
    assert alert.to_dict()["event"] == "governance_source_changed"


def test_304_is_unchanged_without_refetching_the_body(store: CopyStore) -> None:
    states = baseline(store, etag='"v1"', last_modified="Sun, 20 Sep 2026 14:02:11 GMT")
    before = states["example-lab-pricing"].snapshot

    def not_modified(request: httpx.Request) -> httpx.Response:
        assert request.headers["if-none-match"] == '"v1"'
        assert request.headers["if-modified-since"] == "Sun, 20 Sep 2026 14:02:11 GMT"
        return httpx.Response(304, headers={"etag": '"v1"'})

    server = Server(not_modified)
    report = run(server, store, states, now=T0 + timedelta(days=7))

    assert len(server.requests) == 1
    assert set(statuses(report).values()) == {RegionStatus.UNCHANGED}
    assert report.requeue == []
    after = report.states["example-lab-pricing"].snapshot
    assert after.region_fingerprints == before.region_fingerprints
    assert after.copy_ref == before.copy_ref
    assert after.retrieved_at == T0 + timedelta(days=7)


def test_plain_http_mode_never_sends_conditional_headers(store: CopyStore) -> None:
    src = pricing_source(fetch=FetchMode.HTTP)
    states = run(
        Server(html(fixture("pricing_v1.html"), etag='"v1"')), store, sources=(src,)
    ).states

    def check(request: httpx.Request) -> httpx.Response:
        assert "if-none-match" not in request.headers
        return html(fixture("pricing_v1.html"), etag='"v1"')

    report = run(Server(check), store, states, sources=(src,))
    assert set(statuses(report).values()) == {RegionStatus.UNCHANGED}


def test_404_is_unreachable_then_quarantined_after_grace(store: CopyStore) -> None:
    states = baseline(store)
    all_refs = sorted(c.ref for c in CITATIONS)

    for attempt in (1, 2):
        report = run(Server(httpx.Response(404)), store, states, grace=3)
        assert set(statuses(report).values()) == {RegionStatus.UNREACHABLE}
        states = report.states
        assert states["example-lab-pricing"].consecutive_failures == attempt
        assert not states["example-lab-pricing"].quarantined
        assert report.quarantine == []
        assert report.requeue == []

    report = run(Server(httpx.Response(404)), store, states, grace=3)
    assert report.states["example-lab-pricing"].quarantined
    assert report.quarantine == all_refs
    # The last good snapshot is kept for the re-crawl.
    assert report.states["example-lab-pricing"].snapshot == states["example-lab-pricing"].snapshot

    # Recovery: the page answers again and is unchanged.
    report = run(Server(html(fixture("pricing_v1.html"))), store, report.states)
    state = report.states["example-lab-pricing"]
    assert (state.consecutive_failures, state.quarantined) == (0, False)
    assert set(statuses(report).values()) == {RegionStatus.UNCHANGED}


def test_timeout_retries_with_backoff_then_is_unreachable(store: CopyStore) -> None:
    states = baseline(store)
    clock = FakeClock()
    server = Server(*(httpx.ReadTimeout("slow") for _ in range(3)))
    report = recheck(
        (pricing_source(),),
        states,
        CITATIONS,
        fetcher=fetcher_for(server, clock, retries=2, backoff=0.5, min_host_interval=0),
        store=store,
        now=T0,
    )
    assert len(server.requests) == 3
    assert clock.sleeps == [0.5, 1.0]
    assert set(statuses(report).values()) == {RegionStatus.UNREACHABLE}
    [result] = [r for r in report.regions if r.region_id == "price-table"]
    assert "timeout" in (result.detail or "").lower()


def test_transient_503_is_retried_and_recovers(store: CopyStore) -> None:
    states = baseline(store)
    server = Server(
        httpx.Response(503, headers={"retry-after": "2"}), html(fixture("pricing_v1.html"))
    )
    clock = FakeClock()
    report = recheck(
        (pricing_source(),),
        states,
        CITATIONS,
        fetcher=fetcher_for(server, clock),
        store=store,
        now=T0,
    )
    assert clock.sleeps == [2.0]
    assert set(statuses(report).values()) == {RegionStatus.UNCHANGED}


def test_404_is_not_retried(store: CopyStore) -> None:
    server = Server(httpx.Response(404))
    run(server, store)
    assert len(server.requests) == 1


# --- fetch modes and content types -------------------------------------------------------------


def test_rendered_sources_are_recorded_not_fetched(store: CopyStore) -> None:
    src = pricing_source(fetch=FetchMode.RENDERED)
    server = Server()  # any request fails the test
    report = run(server, store, sources=(src,))
    assert server.requests == []
    assert report.regions == []
    [skip] = report.skipped
    assert (skip.source_id, skip.reason) == ("example-lab-pricing", "rendered_fetch_required")
    assert FetchMode.RENDERED.relative_cost > FetchMode.CONDITIONAL_HTTP.relative_cost


def test_pdf_is_recorded_as_unsupported(store: CopyStore) -> None:
    src = pricing_source(
        id="system-card", url="https://lab.example.com/system-card.pdf", cited_regions=()
    )
    server = Server(
        httpx.Response(200, headers={"content-type": "application/pdf"}, content=b"%PDF-1.7 ...")
    )
    report = run(server, store, sources=(src,))
    [skip] = report.skipped
    assert (skip.source_id, skip.reason) == ("system-card", "unsupported_content:pdf")
    assert report.regions == []


def test_plain_text_sources_fingerprint_the_whole_page(store: CopyStore) -> None:
    src = pricing_source(
        url="https://lab.example.com/LICENSE.txt",
        normaliser="text-default",
        cited_regions=(CitedRegion(id="licence", locator={"kind": "page"}),),
    )
    cites = (Citation("fact:m/licence", src.id, "licence", FactKind.GOVERNANCE),)
    text = b"Example Licence 1.0\n\nYou may use the weights commercially.\n"
    reformatted = b"Example   Licence 1.0\r\n\r\n\r\nYou may use the weights commercially.  \n"

    def go(server: Server, states=None):
        return recheck(
            (src,), states or {}, cites, fetcher=fetcher_for(server), store=store, now=T0
        )

    states = go(
        Server(httpx.Response(200, headers={"content-type": "text/plain"}, content=text))
    ).states
    report = go(
        Server(httpx.Response(200, headers={"content-type": "text/plain"}, content=reformatted)),
        states,
    )
    assert statuses(report) == {"licence": RegionStatus.UNCHANGED}


def test_text_rule_sets_accept_only_page_locators() -> None:
    with pytest.raises(ValueError, match="page"):
        pricing_source(
            normaliser="text-default",
            cited_regions=(CitedRegion(id="t", locator={"kind": "table", "value": "0"}),)
        )


def test_unknown_rule_set_is_rejected() -> None:
    with pytest.raises(ValueError, match="normaliser"):
        pricing_source(normaliser="no-such-rules")


def test_polite_rate_limit_per_host(store: CopyStore) -> None:
    a = pricing_source(id="a", url="https://lab.example.com/a", cited_regions=())
    b = pricing_source(id="b", url="https://lab.example.com/b", cited_regions=())
    c = pricing_source(id="c", url="https://other.example.org/c", cited_regions=())
    body = fixture("pricing_v1.html")
    server = Server(html(body), html(body), html(body))
    clock = FakeClock()
    recheck(
        (a, c, b),
        {},
        (),
        fetcher=fetcher_for(server, clock, min_host_interval=2.0),
        store=store,
        now=T0,
    )
    # Only the second request to lab.example.com waits; the other host does not.
    assert clock.sleeps == [2.0]


# --- normaliser and locators -------------------------------------------------------------------


def test_normaliser_strips_volatile_text() -> None:
    doc = normalise_document(
        b"""<html><body><script>var t=1</script><style>p{}</style>
        <nav>Home</nav><div class="cookie-consent">Cookies!</div>
        <p>Price   is  <b>$3</b>\n per   MTok</p>
        <p>Posted 3 days ago. Updated 2 hours ago.</p>
        <p>Last modified: 2026-09-20 14:02 UTC</p>
        <p>Released 2026-09-01.</p>
        <p>Docs: https://x.example.com/a?utm_source=y&amp;id=7&amp;fbclid=z</p>
        </body></html>""",
        NORMALISERS["html-default"],
    )
    text = doc.text
    assert "var t" not in text and "Home" not in text and "Cookies" not in text
    assert "Price is $3 per MTok" in text
    assert "ago" not in text and "2026-09-20" not in text
    assert "Released 2026-09-01." in text  # a date that is data is kept
    assert "https://x.example.com/a?id=7" in text


def test_canonical_url_drops_tracking_parameters() -> None:
    assert (
        canonical_url("https://a.example/p?utm_source=x&b=2&gclid=1&a=1#top")
        == "https://a.example/p?b=2&a=1"
    )
    assert canonical_url("https://a.example/p") == "https://a.example/p"


def test_locators_select_regions() -> None:
    doc = normalise_document(fixture("pricing_v1.html"), NORMALISERS["html-default"])
    table = select_region(doc, Locator.table(0))
    assert table is not None
    assert "Example Small | 0.25 | 1.25" in table
    css = select_region(doc, Locator.css("table.prices tbody tr"))
    assert css is not None and css.splitlines()[0] == "Example Large | 3.00 | 15.00"
    heading = select_region(doc, Locator.heading("rate-limits"))
    assert heading is not None
    assert heading.startswith("Rate limits")
    assert "50 requests per minute" in heading
    assert "Data handling" not in heading  # stops at the next heading of the same level
    assert select_region(doc, Locator.heading("#rate-limits")) == heading
    assert select_region(doc, Locator.table(5)) is None
    assert select_region(doc, Locator.css("#nope")) is None


def test_bad_css_selector_is_rejected_at_registration() -> None:
    with pytest.raises(ValueError, match="selector"):
        Locator.css("div:has(> p)")


def test_missing_region_is_changed(store: CopyStore) -> None:
    states = baseline(store)
    stripped = fixture("pricing_v1.html").replace(b'<h2 id="rate-limits">Rate limits</h2>', b"")
    report = run(Server(html(stripped)), store, states)
    [r] = [r for r in report.regions if r.region_id == "rate-limits"]
    assert r.status is RegionStatus.CHANGED
    assert r.current is None
    assert "fact:example-large/rate-limit" in report.requeue


def test_first_check_has_no_baseline_so_everything_is_changed(store: CopyStore) -> None:
    report = run(Server(html(fixture("pricing_v1.html"))), store)
    assert set(statuses(report).values()) == {RegionStatus.CHANGED}
    assert all(r.previous is None for r in report.regions)


# --- retained copies ---------------------------------------------------------------------------


def test_copy_store_is_content_addressed(tmp_path: Path) -> None:
    store = CopyStore(tmp_path)
    ref = store.put(b"hello")
    assert ref == "sha256:2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"
    assert store.put(b"hello") == ref
    assert store.get(ref) == b"hello"
    assert store.path(ref).is_relative_to(tmp_path)
    assert store.has(ref) and not store.has("sha256:" + "0" * 64)


def test_copy_store_defaults_outside_the_repository(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("MODELSPEC_SOURCE_CACHE", raising=False)
    root = CopyStore().root
    assert root == Path.home() / ".cache" / "modelspec" / "sources"
    assert not root.resolve().is_relative_to(REPO_ROOT)
    monkeypatch.setenv("MODELSPEC_SOURCE_CACHE", "/var/tmp/ms")
    assert CopyStore().root == Path("/var/tmp/ms")


def test_snapshot_state_round_trips(store: CopyStore) -> None:
    states = baseline(store, etag='"v1"')
    state = states["example-lab-pricing"]
    assert SourceState.from_dict(state.to_dict()) == state


# --- schedule ----------------------------------------------------------------------------------


def test_intervals_match_the_design_table() -> None:
    week = timedelta(days=7)
    assert DEFAULT_INTERVALS[FactKind.PRICE] == week
    assert DEFAULT_INTERVALS[FactKind.RATE_LIMIT] == week
    assert DEFAULT_INTERVALS[FactKind.GOVERNANCE] == week
    assert DEFAULT_INTERVALS[FactKind.LIVE_LEADERBOARD] == week
    assert DEFAULT_INTERVALS[FactKind.MODEL_SPEC] == timedelta(days=30)
    assert DEFAULT_INTERVALS[FactKind.STATIC_EVIDENCE] >= timedelta(days=90)


def test_due_uses_the_shortest_interval_of_the_citing_facts(store: CopyStore) -> None:
    src = pricing_source()
    state = baseline(store)[src.id]
    static_only = (Citation("ev:x", src.id, "price-table", FactKind.STATIC_EVIDENCE),)

    assert due(src, T0, state=None, citations=CITATIONS)  # never checked
    assert not due(src, T0 + timedelta(days=6), state=state, citations=CITATIONS)
    assert due(src, T0 + timedelta(days=7), state=state, citations=CITATIONS)
    assert not due(src, T0 + timedelta(days=30), state=state, citations=static_only)
    assert due(src, T0 + timedelta(days=92), state=state, citations=static_only)
    assert not due(src, T0 + timedelta(days=400), state=state, citations=())  # nothing cites it
    fast = {**DEFAULT_INTERVALS, FactKind.PRICE: timedelta(days=1)}
    assert due(src, T0 + timedelta(days=1), state=state, citations=CITATIONS, intervals=fast)


# --- no agent anywhere -------------------------------------------------------------------------


def test_recheck_over_unchanged_sources_makes_zero_agent_calls(store: CopyStore) -> None:
    states = baseline(store, etag='"v1"')
    server = Server(
        httpx.Response(304),
    )
    report = run(server, store, states, now=T0 + timedelta(days=7))
    assert report.requeue == [] and report.alerts == [] and report.quarantine == []
    assert set(statuses(report).values()) == {RegionStatus.UNCHANGED}
    # The only outbound calls were the plain fetches themselves.
    assert [str(r.url) for r in server.requests] == [URL]


def test_change_detection_has_no_llm_or_agent_hook() -> None:
    """Importing the module pulls in no LLM client, agent or paid-scrape code."""
    forbidden = ("anthropic", "openai", "researcher", "firecrawl", "litellm", "google.generativeai")
    probe = (
        "import sys, decision.sources, decision.normalise;"
        f"bad = [m for m in sys.modules if m.split('.')[0] in {forbidden!r} or m in {forbidden!r}];"
        "print(','.join(bad))"
    )
    out = subprocess.run(
        [sys.executable, "-c", probe],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=True,
        env={"PYTHONPATH": str(REPO_ROOT), "PATH": "/usr/bin:/bin"},
    )
    assert out.stdout.strip() == ""
    # And statically: the modules import the standard library, httpx and each other only.
    for name in ("sources.py", "normalise.py"):
        tree = ast.parse((REPO_ROOT / "decision" / name).read_text())
        imported = {
            (node.module if isinstance(node, ast.ImportFrom) else alias.name).split(".")[0]
            for node in ast.walk(tree)
            if isinstance(node, (ast.Import, ast.ImportFrom))
            and (not isinstance(node, ast.ImportFrom) or node.module)
            for alias in node.names
        }
        third_party = imported - set(sys.stdlib_module_names) - {"__future__", "decision"}
        assert third_party <= {"httpx", "yaml"}, f"{name} imports {third_party}"
