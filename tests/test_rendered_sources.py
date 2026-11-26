"""Rendered preparation through fake Playwright pages, without a browser or network."""

from __future__ import annotations

import sys
from types import ModuleType, SimpleNamespace

import pytest

from decision.sources import (
    RENDERED_PREPARATIONS,
    CitedRegionWait,
    RenderedFetcher,
    rendered_preparation,
)


def name_terms_register(directory, monkeypatch, terms):
    """A synthetic private register in ``directory``, named for this test (MODEL-565)."""
    import json as _json

    from decision.retention import cite_only_hosts

    (directory / "registry").mkdir(parents=True, exist_ok=True)
    (directory / "registry" / "source-terms.json").write_text(_json.dumps(terms))
    (directory / "registry" / "sources.yaml").write_text(
        '{"schema_version": 1, "sources": []}')
    monkeypatch.setenv("MODELSPEC_DATA_DIR", str(directory))
    cite_only_hosts.cache_clear()


class PageError(Exception):
    pass


class PageTimeout(PageError):
    pass


class FakePage:
    def __init__(self, *, fail_at=None, status=200, idle_timeout=False):
        self.fail_at = fail_at
        self.status = status
        self.idle_timeout = idle_timeout
        self.events = []
        self.timeouts = []
        self.closed = False
        self.body = "<table></table>"

    def goto(self, url, *, wait_until, timeout):
        self.events.append("navigate")
        self.url = url
        return SimpleNamespace(
            status=self.status, url=url,
            request=SimpleNamespace(url=url, redirected_from=None),
        )

    def wait_for_load_state(self, state, *, timeout):
        self.events.append("idle")
        if self.idle_timeout:
            raise PageTimeout("network is still active")

    def get_by_role(self, role, *, name, exact):
        assert (role, name, exact) == ("tab", "Anthropic", True)
        return self

    def click(self, *, timeout):
        self.events.append("open Anthropic")
        self.timeouts.append(timeout)
        if self.fail_at == "tab":
            raise PageTimeout("Anthropic tab not found")

    def locator(self, selector):
        self.component_selector = selector
        return self

    def scroll_into_view_if_needed(self, *, timeout):
        self.events.append("scroll global prices")
        self.timeouts.append(timeout)
        if self.fail_at == "scroll":
            raise PageError("global pricing component not found")

    def wait_for_function(self, expression, *, arg, timeout):
        self.events.append("wait for prices")
        self.timeouts.append(timeout)
        self.condition = expression
        self.table_selector = arg
        if self.fail_at == "prices":
            raise PageTimeout("pricing cells did not populate")
        self.body = ("<table><tr><th>Anthropic models</th><th>Input</th><th>Output</th></tr>"
                     "<tr><td>Claude Opus 5.5</td><td>$4.00</td><td>$20.00</td></tr></table>")

    def content(self):
        self.events.append("capture")
        return self.body

    def close(self):
        self.closed = True


@pytest.fixture(autouse=True)
def fake_playwright(monkeypatch):
    package = ModuleType("playwright")
    sync_api = ModuleType("playwright.sync_api")
    sync_api.Error = PageError
    sync_api.TimeoutError = PageTimeout
    monkeypatch.setitem(sys.modules, "playwright", package)
    monkeypatch.setitem(sys.modules, "playwright.sync_api", sync_api)


@pytest.fixture(autouse=True)
def terms_register(tmp_path, monkeypatch):
    # The rendered path fetches nothing without a terms register (MODEL-565).
    name_terms_register(tmp_path / "terms", monkeypatch,
                        {"aws.amazon.com": "restricts", "app.example": "permits"})
    yield
    from decision.retention import cite_only_hosts
    cite_only_hosts.cache_clear()


def fetch(page, *, prepare=True, timeout=20):
    renderer = RenderedFetcher(timeout=timeout)
    renderer._context = SimpleNamespace(new_page=lambda: page)
    return renderer.fetch("https://aws.amazon.com/bedrock/pricing/",
                          prepare=RENDERED_PREPARATIONS["aws-pricing"] if prepare else None)


@pytest.mark.parametrize("idle_timeout", [False, True])
def test_preparation_populates_the_capture_after_opening_and_scrolling(idle_timeout):
    page = FakePage(idle_timeout=idle_timeout)
    result = fetch(page)
    assert (result.outcome, result.status, result.error) == ("ok", 200, None)
    assert result.body == (b"<table><tr><th>Anthropic models</th><th>Input</th><th>Output</th></tr>"
                           b"<tr><td>Claude Opus 5.5</td><td>$4.00</td><td>$20.00</td></tr></table>")
    assert page.events == ["navigate", "idle", "open Anthropic", "scroll global prices",
                           "wait for prices", "capture"]
    assert page.component_selector == (
        'div.aws-table[data-pricing-markup^="<h2>Global Cross-region Inference</h2>"]'
        '[data-pricing-markup*="<th>Anthropic models</th>"]')
    assert page.table_selector == page.component_selector + " table"
    assert page.closed


def test_preparation_actions_share_one_timeout_budget(monkeypatch):
    ticks = iter([0.0, 0.25, 0.75, 1.0])
    monkeypatch.setattr("decision.sources.time.monotonic", lambda: next(ticks))
    page = FakePage()
    assert fetch(page, timeout=2).outcome == "ok"
    assert page.timeouts == [1750.0, 1250.0, 1000.0]


@pytest.mark.parametrize(("stage", "message"), [
    ("tab", "Anthropic tab not found"),
    ("scroll", "global pricing component not found"),
    ("prices", "pricing cells did not populate"),
])
def test_preparation_failure_retains_html_and_records_the_error(stage, message):
    page = FakePage(fail_at=stage)
    result = fetch(page)
    assert result.outcome == "ok"
    assert result.body == b"<table></table>"
    assert result.error == f"rendered preparation failed: {message}"
    assert page.events[-1] == "capture"
    assert page.closed


def test_fetch_without_preparation_keeps_passive_rendering():
    page = FakePage()
    result = fetch(page, prepare=False)
    assert (result.outcome, result.body, result.error) == ("ok", b"<table></table>", None)
    assert page.events == ["navigate", "idle", "capture"]
    assert page.closed


def test_unsuccessful_navigation_does_not_prepare_or_capture():
    page = FakePage(status=503)
    result = fetch(page)
    assert (result.outcome, result.status, result.error) == ("unreachable", 503, "HTTP 503")
    assert page.events == ["navigate"]
    assert page.closed


# --- MODEL-423: wait for cited regions a client-side app mounts late ------------------------


class MountingPage(FakePage):
    """A client-side app: each region mounts after the network idles, or never."""

    def __init__(self, mounts):
        super().__init__()
        self.body = "<main></main>"
        self.mounts = mounts
        self.waited = []

    def wait_for_function(self, expression, *, arg, timeout):
        assert "document.querySelector(selector)" in expression
        self.events.append(f"wait for {arg}")
        self.waited.append((arg, timeout))
        if self.mounts.get(arg) is None:
            raise PageTimeout(f"{arg} stayed empty")
        self.body = self.body.replace("</main>", self.mounts[arg] + "</main>")


def source(source_id, *locators):
    from decision.model import Source

    return Source.model_validate({
        "id": source_id, "url": "https://app.example/plans", "fetch": "rendered",
        "cited_regions": [{"id": f"r{i}", "locator": {"kind": kind, "value": value}}
                          for i, (kind, value) in enumerate(locators)],
    })


def render(page, preparation):
    renderer = RenderedFetcher(timeout=20)
    renderer._context = SimpleNamespace(new_page=lambda: page)
    return renderer.fetch("https://app.example/plans", prepare=preparation)


def test_every_cited_css_region_of_a_shared_url_is_waited_for():
    sources = {
        "plans-html": source("plans-html", ("page", ""), ("css", "#plans"),
                             ("css", "#faq li::own")),
        "plans-alias": source("plans-alias", ("css", "#plans"),
                              ("css", "#terms::excerpt=Billed monthly.")),
    }
    preparation = rendered_preparation(["plans-alias", "plans-html"], sources)
    assert preparation == CitedRegionWait(("#plans", "#terms", "#faq li"))

    page = MountingPage({"#plans": "<p>Pro $20/month</p>", "#terms": "<p>Billed monthly.</p>",
                         "#faq li": "<li>Cancel any time.</li>"})
    result = render(page, preparation)
    assert (result.outcome, result.error) == ("ok", None)
    assert result.body == (b"<main><p>Pro $20/month</p><p>Billed monthly.</p>"
                           b"<li>Cancel any time.</li></main>")
    assert page.events == ["navigate", "idle", "wait for #plans", "wait for #terms",
                           "wait for #faq li", "capture"]


def test_a_region_that_never_mounts_is_captured_as_is_for_the_readers_to_report():
    page = MountingPage({"#terms": "<p>Billed monthly.</p>"})
    result = render(page, CitedRegionWait(("#plans", "#terms")))
    assert (result.outcome, result.error, result.body) == ("ok", None, b"<main></main>")
    assert [selector for selector, _ in page.waited] == ["#plans"]


def test_region_waits_share_one_timeout_budget(monkeypatch):
    ticks = iter([0.0, 0.5, 19.0, 20.5])
    monkeypatch.setattr("decision.sources.time.monotonic", lambda: next(ticks))
    page = MountingPage({"#a": "<p>a</p>", "#b": "<p>b</p>", "#c": "<p>c</p>"})
    render(page, CitedRegionWait(("#a", "#b", "#c")))
    assert page.waited == [("#a", 19500.0), ("#b", 1000.0)]


def test_a_named_preparation_wins_and_page_regions_need_no_wait():
    sources = {"aws-pricing": source("aws-pricing", ("css", "table")),
               "plain": source("plain", ("page", ""), ("heading", "pricing"))}
    assert rendered_preparation(["aws-pricing", "plain"], sources) \
        is RENDERED_PREPARATIONS["aws-pricing"]
    assert rendered_preparation(["plain"], sources) is None
    assert rendered_preparation(["unregistered"], sources) is None


# --- MODEL-565: the start host is checked before a page is opened -----------------------------


@pytest.mark.parametrize(("terms", "expected"), [
    ('{"other.example": "permits"}', "redirect_unclassified:aws.amazon.com"),
    ("not json", "terms_register_unreadable"),
    (None, "terms_register_unreadable"),  # no register named: fail closed
])
def test_rendered_fetch_refuses_the_start_host_before_opening_a_page(tmp_path, monkeypatch,
                                                                      terms, expected):
    from decision.retention import cite_only_hosts

    (tmp_path / "registry").mkdir()
    if terms is None:
        monkeypatch.delenv("MODELSPEC_DATA_DIR")
    else:
        (tmp_path / "registry" / "source-terms.json").write_text(terms)
        monkeypatch.setenv("MODELSPEC_DATA_DIR", str(tmp_path))
    # No registered source here: an unregistered start host still needs a class.
    (tmp_path / "registry" / "sources.yaml").write_text('{"schema_version": 1, "sources": []}')
    cite_only_hosts.cache_clear()
    renderer = RenderedFetcher()
    renderer._context = SimpleNamespace(new_page=lambda: pytest.fail("a page was opened"))
    try:
        result = renderer.fetch("https://aws.amazon.com/bedrock/pricing/")
    finally:
        cite_only_hosts.cache_clear()
    assert (result.outcome, result.error) == ("unreachable", expected)



@pytest.mark.parametrize("url", [
    "http://a.test\\@b.test/",
    "https://user@aws.amazon.com/bedrock/pricing/",
    "https://aws%2eamazon.com/bedrock/pricing/",
    "https://aws.amazon%2Ecom/bedrock/pricing/",
    "https://bücher.test/",
    "https://xn--bcher-kva.test./",
    "https://aws.amazon.com./bedrock/pricing/",
    "https://AWS.amazon.com/bedrock/pricing/",
    "https://aws..amazon.com/bedrock/pricing/",
    "https://aws.amazon.com/bedrock pricing/",
    "https://aws.amazon.com/\tbedrock/",
])
def test_a_url_another_parser_could_read_differently_is_refused_before_a_page_opens(url):
    from decision.sources import _ambiguous_url

    assert _ambiguous_url(url) == "ambiguous URL"
    renderer = RenderedFetcher()
    renderer._context = SimpleNamespace(new_page=lambda: pytest.fail("a page was opened"))
    assert (renderer.fetch(url).outcome, renderer.fetch(url).error) == ("unreachable", "ambiguous URL")


@pytest.mark.parametrize("url", [
    "https://aws.amazon.com/bedrock/pricing/", "https://aws.amazon.com:443/bedrock/pricing/",
    "https://xn--bcher-kva.test/", "http://127.0.0.1:8080/page",
])
def test_a_url_the_browser_reads_as_written_is_not_ambiguous(url):
    from decision.sources import _ambiguous_url

    assert _ambiguous_url(url) is None


@pytest.mark.parametrize("change", ["url", "hop"])
def test_a_navigation_during_capture_refuses_it(change):
    page = FakePage()
    renderer = RenderedFetcher(timeout=20)
    renderer._context = SimpleNamespace(new_page=lambda: page)
    serialise = page.content

    def content():
        body = serialise()
        if change == "url":
            page.url = "https://aws.amazon.com/elsewhere"
        else:
            renderer._guard.hops.append("https://aws.amazon.com/elsewhere")
        return body

    page.content = content
    result = renderer.fetch("https://aws.amazon.com/bedrock/pricing/")
    assert (result.outcome, result.body, result.error) == (
        "unreachable", b"", "navigation during capture")


def test_a_final_url_on_a_cite_only_host_refuses_a_retained_capture(tmp_path, monkeypatch):
    name_terms_register(tmp_path / "cite", monkeypatch,
                        {"aws.amazon.com": "restricts", "mirror.example": "cite-only"})
    page = FakePage()
    renderer = RenderedFetcher(timeout=20)
    renderer._context = SimpleNamespace(new_page=lambda: page)

    def goto(url, **kwargs):
        response = FakePage.goto(page, url, **kwargs)
        renderer._guard.hops.append(url)  # what the routed request records
        page.url = "https://mirror.example/pushed"  # a same-document change, no request
        return response

    page.goto = goto
    result = renderer.fetch("https://aws.amazon.com/bedrock/pricing/")
    assert (result.outcome, result.body, result.error) == (
        "unreachable", b"", "final URL is cite-only")
