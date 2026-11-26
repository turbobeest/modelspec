"""MODEL-433: registry recipes select public pricing controls before capture."""

from __future__ import annotations

import json
import time
from types import SimpleNamespace

import pytest

from decision.sources import (
    MAX_RENDERED_REDIRECTS, RenderedFetcher, load_sources, rendered_preparation,
)


RECIPE = [
    {"action": "click", "selector": "#provider"},
    {"action": "select_option", "selector": "#region", "value": "us-east"},
    {"action": "scroll", "selector": "#prices"},
    {"action": "wait_text", "selector": "#prices", "text": "$4.00"},
]


def registry(tmp_path, interactions=RECIPE, **overrides):
    row = {
        "id": "fixture-pricing", "url": "https://fixture.example/prices",
        "fetch": "rendered", "rendered_interactions": interactions,
        "cited_regions": [{"id": "prices", "locator": {"kind": "css", "value": "#prices"}}],
        **overrides,
    }
    path = tmp_path / "sources.yaml"
    path.write_text(json.dumps({"schema_version": 1, "sources": [row]}))
    return load_sources(path)


def test_registry_loads_a_bounded_data_only_recipe(tmp_path):
    sources = registry(tmp_path)
    assert sources["fixture-pricing"].model_dump()["rendered_interactions"] == RECIPE


def test_empty_recipe_is_omitted_from_python_json_and_nested_serialization(tmp_path):
    from pydantic import TypeAdapter

    from decision.model import Source

    source = registry(tmp_path, interactions=[])["fixture-pricing"]
    assert "rendered_interactions" not in source.model_dump()
    assert "rendered_interactions" not in json.loads(source.model_dump_json())
    assert "rendered_interactions" not in TypeAdapter(list[Source]).dump_python([source])[0]


@pytest.mark.parametrize("attributes,text", [
    ('aria-label="Region"', "Accept all cookies"),
    ('aria-label="Region"', "Log in"),
    ('aria-label="Region"', "Submit"),
    ('aria-label="Region" value="Accept all cookies"', "Region"),
    ('aria-label="Region" value="Log in"', "Region"),
    ('aria-label="Region" value="Submit"', "Region"),
    ('aria-label="Accept all cookies"', "Region"),
])
def test_safe_label_cannot_hide_unsafe_text_or_value(tmp_path, browser, attributes, text):
    recipe = [{"action": "click", "selector": "#unsafe"}, RECIPE[-1]]
    result = render_fixture(
        browser, registry(tmp_path, recipe),
        f'<button id="unsafe" type="button" {attributes} '
        f'onclick="document.cookie=\'consent=yes\'">{text}</button>'
        '<div id="prices">$4.00</div>')
    assert browser._context.cookies() == []
    assert result.outcome == "unreachable"
    assert result.body == b""
    assert "unsafe" in result.error


@pytest.mark.parametrize("name", ["Accept all cookies", "Log in", "Submit"])
@pytest.mark.parametrize("naming", ["labelledby", "title", "image-alt"])
def test_recipe_refuses_unsafe_accessible_names(tmp_path, browser, name, naming):
    attributes = 'aria-labelledby="control-name"' if naming == "labelledby" else ""
    if naming == "title":
        attributes = f'title="{name}"'
    image = f'<img alt="{name}">' if naming == "image-alt" else ""
    result = render_fixture(
        browser, registry(tmp_path, [{"action": "click", "selector": "#unsafe"}, RECIPE[-1]]),
        f'<span id="control-name" hidden>{name}</span>'
        f'<button id="unsafe" type="button" {attributes} '
        f'onclick="document.cookie=\'consent=yes\'">Region{image}</button>'
        '<div id="prices">$4.00</div>')
    assert browser._context.cookies() == []
    assert result.outcome == "unreachable"
    assert result.body == b""
    assert "unsafe" in result.error


@pytest.mark.parametrize("action,name,expected", [
    ("click", "Region", "ok"),
    ("reject_consent", "Reject all cookies", "ok"),
    ("reject_consent", "Accept all cookies", "unreachable"),
])
def test_recipe_checks_computed_name_when_rejecting_consent(
        tmp_path, browser, action, name, expected):
    text = "Reject all cookies" if action == "reject_consent" else "US East"
    result = render_fixture(
        browser, registry(tmp_path, [{"action": action, "selector": "#control"}, RECIPE[-1]]),
        f'<span id="control-name" hidden>{name}</span>'
        '<button id="control" type="button" aria-labelledby="control-name" '
        f'onclick="this.remove()">{text}</button><div id="prices">$4.00</div>')
    assert result.outcome == expected, result.error
    if expected == "ok":
        assert b'id="control"' not in result.body
    else:
        assert result.body == b""
        assert "unsafe" in result.error


@pytest.mark.parametrize("recipe, overrides", [
    ([{"action": "evaluate", "selector": "body", "code": "alert(1)"}], {}),
    ([{"action": "fill", "selector": "input", "value": "password"}], {}),
    ([{"action": "click", "selector": ""}], {}),
    ([{"action": "select_option", "selector": "select"}], {}),
    ([{"action": "wait_text", "selector": "#prices", "text": ""}], {}),
    (RECIPE * 5, {}),
    (RECIPE[:-1], {}),
    (RECIPE, {"fetch": "http"}),
    (RECIPE, {"normaliser": "text-default", "cited_regions": []}),
])
def test_registry_rejects_unsafe_or_incomplete_recipes(tmp_path, recipe, overrides):
    with pytest.raises(ValueError):
        registry(tmp_path, recipe, **overrides)


@pytest.fixture
def browser(tmp_path, monkeypatch):
    pytest.importorskip("playwright.sync_api")
    from decision.retention import cite_only_hosts

    # The rendered path fetches nothing without a terms register (MODEL-565). These
    # fixtures fulfil every request in a test route, which runs before the guard's.
    (tmp_path / "terms" / "registry").mkdir(parents=True)
    (tmp_path / "terms" / "registry" / "source-terms.json").write_text(
        json.dumps({"fixture.example": "permits"}))
    (tmp_path / "terms" / "registry" / "sources.yaml").write_text(
        '{"schema_version": 1, "sources": []}')
    monkeypatch.setenv("MODELSPEC_DATA_DIR", str(tmp_path / "terms"))
    cite_only_hosts.cache_clear()
    with RenderedFetcher(timeout=1, idle_timeout=0.01) as renderer:
        yield renderer
    cite_only_hosts.cache_clear()


HTML = """<!doctype html>
<button id="provider" type="button" onclick="document.querySelector('#region').hidden=false">
Provider</button>
<select id="region" hidden onchange="setTimeout(() => {
document.querySelector('#prices').textContent='Model A Input $4.00 Output $20.00';
}, 50)">
<option value="">Choose region</option><option value="us-east">US East</option></select>
<div id="prices"></div>
"""


def render_fixture(browser, sources, html=HTML):
    browser._context.route("https://fixture.example/**",
                           lambda route: route.fulfill(body=html, content_type="text/html"))
    return browser.fetch("https://fixture.example/prices",
                         prepare=rendered_preparation(sources, sources))


def test_recipe_captures_prices_after_click_selection_and_text_wait(tmp_path, browser):
    result = render_fixture(browser, registry(tmp_path))
    assert result.outcome == "ok", result.error
    assert b'<div id="prices">Model A Input $4.00 Output $20.00</div>' in result.body


@pytest.mark.parametrize("recipe", [
    [{"action": "click", "selector": "#missing"}, RECIPE[-1]],
    [{"action": "wait_text", "selector": "#prices", "text": "$999"}],
    [{"action": "click", "selector": "button"}, RECIPE[-1]],
])
def test_failed_recipe_never_captures_a_plausible_partial_page(tmp_path, browser, recipe):
    result = render_fixture(
        browser, registry(tmp_path, recipe),
        '<button type="button">A</button><button type="button">B</button>'
        '<div id="prices">Model A Input $4.00 Output $20.00</div>')
    assert result.outcome == "unreachable"
    assert result.body == b""
    assert "interaction" in result.error


@pytest.mark.parametrize("control", [
    '<a id="unsafe" href="/login">Sign in</a>',
    '<form><button id="unsafe">Submit</button></form>',
    '<input id="unsafe" type="submit">',
    '<button id="unsafe" type="button">Accept all cookies</button>',
    '<button id="unsafe" type="button">Log in</button>',
])
def test_recipe_refuses_navigation_forms_login_and_cookie_acceptance(tmp_path, browser, control):
    recipe = [{"action": "click", "selector": "#unsafe"}, RECIPE[-1]]
    result = render_fixture(browser, registry(tmp_path, recipe),
                            control + '<div id="prices">$4.00</div>')
    assert result.outcome == "unreachable"
    assert result.body == b""
    assert "unsafe" in result.error


def test_recipe_can_reject_optional_cookies(tmp_path, browser):
    recipe = [{"action": "reject_consent", "selector": "#reject"}, RECIPE[-1]]
    result = render_fixture(
        browser, registry(tmp_path, recipe),
        '<button id="reject" type="button" onclick="this.remove()">Reject all cookies</button>'
        '<div id="prices">$4.00</div>')
    assert result.outcome == "ok", result.error
    assert b'id="reject"' not in result.body


@pytest.mark.parametrize("selected", [False, True])
def test_wait_text_on_select_requires_the_selected_option(tmp_path, browser, selected):
    recipe = [{"action": "wait_text", "selector": "#region", "text": "East US"}]
    result = render_fixture(
        browser, registry(tmp_path, recipe),
        '<select id="region"><option value="east2">East US 2</option>'
        f'<option value="east" {"selected" if selected else ""}>East US</option></select>')
    assert result.outcome == ("ok" if selected else "unreachable")
    if not selected:
        assert result.body == b""


def test_recipe_cannot_accept_cookies_with_a_native_select(tmp_path, browser):
    recipe = [{"action": "select_option", "selector": "#consent", "value": "all"},
              RECIPE[-1]]
    result = render_fixture(browser, registry(tmp_path, recipe), """
        <div id="cookie-consent"><select id="consent">
        <option value="none">Reject all</option><option value="all">Accept all</option>
        </select></div><div id="prices">$4.00</div>""")
    assert result.outcome == "unreachable"
    assert result.body == b""


@pytest.mark.parametrize("action", [
    pytest.param("window.open('/action')", id="popup-navigation"),
    pytest.param("document.querySelector('#other').submit()", id="popup-form-post"),
    pytest.param("fetch('/action', {method:'POST'}).catch(() => {})", id="background-post"),
])
def test_recipe_blocks_requests_from_controls_and_discards_the_capture(
        tmp_path, browser, action):
    requests = []
    html = f"""
        <form id="other" action="/action" method="post" target="_blank"></form>
        <button id="control" type="button" onclick="{action}">US East</button>
        <div id="prices">Default region $4.00</div>"""

    def respond(route):
        requests.append((route.request.method, route.request.url))
        route.fulfill(body=html, content_type="text/html")

    browser._context.route("**/*", respond)
    sources = registry(tmp_path, [{"action": "click", "selector": "#control"}, RECIPE[-1]])
    result = browser.fetch("https://fixture.example/prices",
                           prepare=rendered_preparation(sources, sources))

    assert requests == [("GET", "https://fixture.example/prices")]
    assert result.outcome == "unreachable"
    assert result.body == b""
    assert "blocked" in result.error
    assert browser._context.pages == []


@pytest.mark.parametrize("action, expected", [
    pytest.param(
        "fetch('https://telemetry.example/events?session=fixture', {method:'POST'}).catch(() => {})",
        "ok", id="listed-telemetry"),
    pytest.param(
        "fetch('https://telemetry.example/other', {method:'POST'}).catch(() => {})",
        "unreachable", id="unlisted-path"),
    pytest.param(
        "fetch('https://other.example/events', {method:'POST'}).catch(() => {})",
        "unreachable", id="unlisted-host"),
    pytest.param("window.open('https://telemetry.example/events')",
                 "unreachable", id="listed-navigation"),
    pytest.param("document.querySelector('#other').submit()",
                 "unreachable", id="listed-form-post"),
])
def test_recipe_blocks_listed_telemetry_without_discarding_selected_prices(
        tmp_path, browser, action, expected):
    requests = []
    html = f"""
        <form id="other" action="https://telemetry.example/events"
              method="post" target="_blank"></form>
        <button id="control" type="button" onclick="{action};
            document.querySelector('#prices').textContent='US East $8.00'">US East</button>
        <div id="prices">Default region $4.00</div>"""

    def respond(route):
        requests.append((route.request.method, route.request.url))
        route.fulfill(body=html, content_type="text/html")

    browser._context.route("**/*", respond)
    sources = registry(tmp_path, [
        {"action": "block_telemetry", "url": "https://telemetry.example/events"},
        {"action": "click", "selector": "#control"},
        {"action": "wait_text", "selector": "#prices", "text": "US East $8.00"},
    ])
    result = browser.fetch("https://fixture.example/prices",
                           prepare=rendered_preparation(sources, sources))

    assert requests == [("GET", "https://fixture.example/prices")]
    assert result.outcome == expected, result.error
    if expected == "ok":
        assert b'<div id="prices">US East $8.00</div>' in result.body
    else:
        assert result.body == b""
        assert "blocked" in result.error
    assert browser._context.pages == []


@pytest.mark.parametrize("url", [
    "not-a-url",
    "http://telemetry.example/events",
    "https://telemetry.example/events?session=fixture",
    "https://telemetry.example/events?",
    "https://telemetry.example/events#section",
    "https://telemetry.example/events#",
    "https://user:password@telemetry.example/events",
])
def test_registry_rejects_ambiguous_telemetry_endpoints(tmp_path, url):
    with pytest.raises(ValueError):
        registry(tmp_path, [{"action": "block_telemetry", "url": url}, RECIPE[-1]])


def test_conflicting_recipes_for_one_url_fail_closed(tmp_path, browser):
    sources = registry(tmp_path)
    sources.update(registry(tmp_path, [RECIPE[-1]], id="alias"))
    result = render_fixture(browser, sources)
    assert result.outcome == "unreachable"
    assert result.body == b""
    assert "conflicting" in result.error


def test_recipe_has_one_deadline_for_all_steps(tmp_path, browser):
    recipe = [
        {"action": "wait_text", "selector": "#first", "text": "ready"},
        {"action": "wait_text", "selector": "#second", "text": "ready"},
    ]
    started = time.monotonic()
    result = render_fixture(browser, registry(tmp_path, recipe), """
        <div id="first"></div><div id="second"></div><script>
        setTimeout(() => document.querySelector('#first').textContent='ready', 700);
        setTimeout(() => document.querySelector('#second').textContent='ready', 1400);
        </script>""")
    assert result.outcome == "unreachable"
    assert result.body == b""
    assert time.monotonic() - started < 2.5


def test_registry_recipe_takes_precedence_over_legacy_source_preparation(tmp_path):
    sources = registry(tmp_path, id="aws-pricing")
    from decision.sources import RENDERED_PREPARATIONS

    assert rendered_preparation(sources, sources) is not RENDERED_PREPARATIONS["aws-pricing"]


def test_recipe_closes_a_popup_created_while_the_capture_page_is_closing(
        tmp_path, browser, monkeypatch):
    context = browser._context
    existing_page = context.new_page()
    opened_pages = []

    def track_page(opened_page):
        opened_pages.append(opened_page)
        if len(opened_pages) == 1:
            close = opened_page.close
            popup_created = False

            def close_with_late_popup(*args, **kwargs):
                nonlocal popup_created
                close(*args, **kwargs)
                if not popup_created:
                    popup_created = True
                    with context.expect_page():
                        existing_page.evaluate("window.open('about:blank') !== null")

            monkeypatch.setattr(opened_page, "close", close_with_late_popup)

    unroute = context.unroute

    def unroute_after_pages_close(*args, **kwargs):
        assert len(opened_pages) == 2
        assert opened_pages[1].is_closed()
        return unroute(*args, **kwargs)

    context.on("page", track_page)
    monkeypatch.setattr(context, "unroute", unroute_after_pages_close)
    try:
        result = render_fixture(browser, registry(tmp_path, [RECIPE[-1]]),
                                '<div id="prices">$4.00</div>')

        assert result.outcome == "ok", result.error
        assert len(opened_pages) == 2
        assert opened_pages[1].is_closed()
        assert context.pages == [existing_page]
    finally:
        context.remove_listener("page", track_page)
        existing_page.close()


AZURE_TABLES = ("GPT-6 Series", "GPT-5.6 Series", "GPT 5.4 Series")


def azure_fixture(tmp_path, *, late_table=None, cell=None, currency="usd", region="us-east"):
    recipe = [
        {"action": "select_option", "selector": "#region-selector", "value": region},
        {"action": "select_option", "selector": "#currency-selector", "value": currency},
        *({"action": "wait_text", "selector": f'table[aria-label="{label}"] tbody', "text": "$"}
          for label in AZURE_TABLES),
    ]
    html = '''<select id="region-selector" onchange="updateTables()">
      <option value="us-west">West US</option><option value="us-east">East US</option>
      </select><select id="currency-selector">
      <option value="usd">USD</option><option value="cad">CAD</option></select>'''
    default_cell = '''<span class="price-data"
      data-amount='{"regional":{"us-east":4,"us-west":99}}'>
      <span class="price-value">$99</span></span>'''
    for label in AZURE_TABLES:
        html += f'<table aria-label="{label}"><tbody><tr><td>{cell or default_cell}</td></tr></tbody></table>'
    if cell is None:
        html += '''<script>
          function updateTables() {
            for (const table of document.querySelectorAll('table')) {
              const delay = table.getAttribute('aria-label') === %s ? 300 : 0;
              setTimeout(() => table.querySelector('.price-value').textContent = '$4', delay);
            }
          }
        </script>''' % json.dumps(late_table)
    else:
        html += '<script>function updateTables() {}</script>'
    return registry(tmp_path, recipe, id="azure-pricing"), html


@pytest.mark.parametrize("late_table", AZURE_TABLES)
def test_azure_recipe_waits_for_delayed_region_table_content(tmp_path, browser, late_table):
    sources, html = azure_fixture(tmp_path, late_table=late_table)
    result = render_fixture(browser, sources, html)
    assert result.outcome == "ok", result.error
    assert result.body.count(b'class="price-value">$4<') == 3
    assert b">$99<" not in result.body


@pytest.mark.parametrize("cell", [
    '<span class="price-data" data-amount=\'{"regional":{"us-east":4}}\'><span class="price-value">$99</span></span>',
    '<span class="price-data" data-amount=\'{"regional":{"us-west":4}}\'><span class="price-value">$4</span></span>',
    '<span class="price-data" data-amount=\'{"regional":{"us-east":null}}\'><span class="price-value">$4</span></span>',
    '<span class="price-data" data-amount="invalid"><span class="price-value">$4</span></span>',
    '<span class="price-data"><span class="price-value">$4</span></span>',
    '<span class="price-data" data-amount=\'{"regional":{"us-east":4}}\'>$4</span>',
    '<span class="price-data" data-amount=\'{"regional":{"us-east":4}}\'><span class="price-value"></span>$4</span>',
    '$4',
])
def test_azure_recipe_refuses_unconfirmed_table_content(tmp_path, browser, cell):
    sources, html = azure_fixture(tmp_path, cell=cell)
    result = render_fixture(browser, sources, html)
    assert result.outcome == "unreachable"
    assert result.body == b""


@pytest.mark.parametrize("amount,rendered", [(0, "$0"), (1234.5, "$1,234.50"), (0.025, "$0.025")])
def test_azure_recipe_accepts_selected_usd_amounts(tmp_path, browser, amount, rendered):
    metadata = json.dumps({"regional": {"us-east": amount}})
    cell = f'<span class="price-data" data-amount=\'{metadata}\'><span class="price-value">{rendered}</span></span>'
    sources, html = azure_fixture(tmp_path, cell=cell)
    result = render_fixture(browser, sources, html)
    assert result.outcome == "ok", result.error


@pytest.mark.parametrize("amount,rendered", [
    (0.025, "$0.03"), (1.005, "$1.01"), (1234.567, "$1,234.57"),
    (0.022, "$0.03"), (1.1, "$1.10"),
])
def test_azure_recipe_uses_declared_display_precision(tmp_path, browser, amount, rendered):
    metadata = json.dumps({"regional": {"us-east": amount}})
    cell = (f'<span class="price-data" data-decimals="2" data-amount=\'{metadata}\'>'
            f'<span class="price-value">{rendered}</span></span>')
    sources, html = azure_fixture(tmp_path, cell=cell)
    result = render_fixture(browser, sources, html)
    assert result.outcome == "ok", result.error


@pytest.mark.parametrize("overrides", [{"region": "us-west"}, {"currency": "cad"}])
def test_azure_recipe_refuses_wrong_table_selection(tmp_path, browser, overrides):
    cell = '<span class="price-data" data-amount=\'{"regional":{"us-east":4,"us-west":4}}\'><span class="price-value">$4</span></span>'
    sources, html = azure_fixture(tmp_path, cell=cell, **overrides)
    result = render_fixture(browser, sources, html)
    assert result.outcome == "unreachable"
    assert result.body == b""


# --- MODEL-565: every rendered request and redirect hop is admitted before it is sent ---------

CLASSED, OTHER, UNCLASSED, CITE_ONLY = "127.0.0.1", "127.0.0.2", "127.0.0.3", "127.0.0.4"


@pytest.fixture
def hosts(tmp_path, monkeypatch):
    """Three loopback hosts on synthetic servers; the terms register classes the first two."""
    import threading
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

    from decision.retention import cite_only_hosts

    hits, servers, ports = [], [], {}

    def url(host, path):
        return f"http://{host}:{ports[host]}{path}"

    redirects = {
        "/to-other": (OTHER, "/page"), "/to-unclassed": (UNCLASSED, "/page"),
        "/to-other-then-unclassed": (OTHER, "/to-unclassed"),
        "/script-to-unclassed": (UNCLASSED, "/s.js"),
        "/loop-a": (OTHER, "/loop-b"), "/loop-b": (CLASSED, "/loop-a"),
        "/back": (CLASSED, "/again"),
    }
    served = {}

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def do_GET(self):
            host = self.server.server_address[0]
            hits.append(host + self.path)
            served[self.path] = served.get(self.path, 0) + 1
            if self.path == "/again" and served[self.path] == 1:
                self.path = "/again-first"
                redirects[self.path] = (OTHER, "/back")
            if self.path == "/slow.png":
                time.sleep(1)  # holds the load event while a popup opens
            if self.path == "/to-tricky":  # a browser reads the backslash as a slash
                self.send_response(302)
                self.send_header("Location", url(CLASSED, "") + "\\@" + url(UNCLASSED, "/page")[7:])
                self.end_headers()
                return
            if self.path in redirects:
                self.send_response(302)
                self.send_header("Location", url(*redirects[self.path]))
                self.end_headers()
                return
            if self.path.endswith(".js"):
                body = f"document.body.setAttribute('data-from-{host[-1]}', '1');"
                kind = "text/javascript"
            else:
                body, kind = pages.get(self.path, "<div id=prices>$4.00</div>"), "text/html"
            data = body.encode()
            self.send_response(200)
            self.send_header("Content-Type", kind)
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

    pages = {}
    for host in (CLASSED, OTHER, UNCLASSED, CITE_ONLY):
        try:
            server = ThreadingHTTPServer((host, 0), Handler)
        except OSError:
            pytest.skip(f"loopback address {host} is not available")
        servers.append(server)
        ports[host] = server.server_address[1]
        threading.Thread(target=server.serve_forever, daemon=True).start()
    registry_dir = tmp_path / "data" / "registry"
    registry_dir.mkdir(parents=True)
    (registry_dir / "source-terms.json").write_text(
        json.dumps({CLASSED: "permits", OTHER: "restricts", CITE_ONLY: "cite-only"}))
    # The unclassed host is no registered source's: its start must be refused anyway.
    (registry_dir / "sources.yaml").write_text(json.dumps({"schema_version": 1, "sources": [
        {"url": url(CLASSED, "/page")}]}))
    monkeypatch.setenv("MODELSPEC_DATA_DIR", str(tmp_path / "data"))
    cite_only_hosts.cache_clear()
    try:
        yield SimpleNamespace(url=url, hits=hits, pages=pages)
    finally:
        for server in servers:
            server.shutdown()
            server.server_close()
        cite_only_hosts.cache_clear()


@pytest.fixture
def guarded():
    pytest.importorskip("playwright.sync_api")
    with RenderedFetcher(timeout=5, idle_timeout=0.2) as renderer:
        yield renderer


def unclassed_hits(hosts):
    return [hit for hit in hosts.hits if hit.startswith(UNCLASSED)]


def test_unclassed_start_host_is_refused_before_any_request(hosts, guarded):
    result = guarded.fetch(hosts.url(UNCLASSED, "/page"))
    assert (result.outcome, result.error) == ("unreachable", f"redirect_unclassified:{UNCLASSED}")
    assert hosts.hits == []


@pytest.mark.parametrize("path", ["/to-unclassed", "/to-other-then-unclassed"])
def test_redirect_to_an_unclassed_host_is_never_requested(hosts, guarded, path):
    result = guarded.fetch(hosts.url(CLASSED, path))
    assert (result.outcome, result.body) == ("unreachable", b"")
    assert result.error == f"redirect_unclassified:{UNCLASSED}"
    assert unclassed_hits(hosts) == []
    assert hosts.hits[0] == CLASSED + path


def test_redirects_between_classed_hosts_are_followed_and_recorded_hop_by_hop(hosts, guarded):
    result = guarded.fetch(hosts.url(CLASSED, "/to-other"))
    assert result.outcome == "ok", result.error
    assert b"$4.00" in result.body
    assert result.resolved_urls == (hosts.url(CLASSED, "/to-other"), hosts.url(OTHER, "/page"))
    assert hosts.hits == [CLASSED + "/to-other", OTHER + "/page"]


def test_subresources_frames_and_their_redirects_never_reach_an_unclassed_host(hosts, guarded):
    hosts.pages["/page"] = (
        f'<div id="prices">$4.00</div><img src="{hosts.url(UNCLASSED, "/pixel.png")}">'
        f'<iframe src="{hosts.url(UNCLASSED, "/frame")}"></iframe>'
        f'<script src="{hosts.url(OTHER, "/ok.js")}"></script>'
        f'<script src="{hosts.url(CLASSED, "/script-to-unclassed")}"></script>'
        f'<script>fetch("{hosts.url(UNCLASSED, "/data")}").catch(() => {{}})</script>')
    result = guarded.fetch(hosts.url(CLASSED, "/page"))
    assert result.outcome == "ok", result.error
    assert b'data-from-2="1"' in result.body  # the classed host's script ran
    assert unclassed_hits(hosts) == []
    assert CLASSED + "/script-to-unclassed" in hosts.hits


def test_a_navigation_after_load_to_an_unclassed_host_refuses_the_capture(hosts, guarded):
    hosts.pages["/page"] = (
        '<div id="prices">$4.00</div>'
        f'<script>setTimeout(() => location.href = "{hosts.url(UNCLASSED, "/page")}", 0)</script>')
    result = guarded.fetch(hosts.url(CLASSED, "/page"))
    assert (result.outcome, result.body) == ("unreachable", b"")
    assert result.error == f"redirect_unclassified:{UNCLASSED}"
    assert unclassed_hits(hosts) == []


def test_with_no_terms_register_nothing_is_fetched(hosts, guarded, monkeypatch):
    monkeypatch.delenv("MODELSPEC_DATA_DIR")
    result = guarded.fetch(hosts.url(CLASSED, "/page"))
    assert (result.outcome, result.error) == ("unreachable", "terms_register_unreadable")
    assert hosts.hits == []


def test_a_redirect_loop_stops_at_the_limit_without_leaving_classed_hosts(hosts, guarded):
    result = guarded.fetch(hosts.url(CLASSED, "/loop-a"))
    assert (result.outcome, result.body) == ("unreachable", b"")
    assert "redirect limit" in result.error
    assert unclassed_hits(hosts) == []
    assert len(hosts.hits) == MAX_RENDERED_REDIRECTS + 1


def test_the_hop_chain_keeps_a_url_requested_twice(hosts, guarded):
    result = guarded.fetch(hosts.url(CLASSED, "/again"))
    assert result.outcome == "ok", result.error
    assert result.resolved_urls == (hosts.url(CLASSED, "/again"), hosts.url(OTHER, "/back"),
                                    hosts.url(CLASSED, "/again"))


def test_a_popup_and_its_websocket_are_checked_and_the_popup_closes_with_the_fetch(
        hosts, guarded):
    hosts.pages["/page"] = (
        f'<div id="prices">$4.00</div><script>window.open("{hosts.url(OTHER, "/popup")}")</script>'
        f'<img src="{hosts.url(CLASSED, "/slow.png")}">')
    hosts.pages["/popup"] = (
        f'<script>window.open("{hosts.url(OTHER, "/popup-2")}")</script>'
        f'<img src="{hosts.url(UNCLASSED, "/pixel.png")}">'
        f'<script>new WebSocket("ws://{UNCLASSED}:{hosts.url(UNCLASSED, "").rsplit(":", 1)[1]}/ws")'
        '</script>')
    result = guarded.fetch(hosts.url(CLASSED, "/page"))
    assert result.outcome == "ok", result.error
    assert OTHER + "/popup" in hosts.hits  # the popup ran, through the guard
    assert OTHER + "/popup-2" in hosts.hits  # and opened one of its own
    assert unclassed_hits(hosts) == []  # neither its image nor its WebSocket was sent
    assert guarded._context.pages == []


def test_a_retained_page_takes_no_frame_or_fetch_from_a_cite_only_host(hosts, guarded):
    hosts.pages["/page"] = (
        '<div id="prices">$4.00</div>'
        f'<iframe src="{hosts.url(CITE_ONLY, "/frame")}"></iframe>'
        f'<script>fetch("{hosts.url(CITE_ONLY, "/data")}").then(r => r.text())'
        '.then(t => document.body.append(t)).catch(() => {})</script>'
        f'<img src="{hosts.url(CLASSED, "/slow.png")}">')
    result = guarded.fetch(hosts.url(CLASSED, "/page"))
    assert result.outcome == "ok", result.error
    assert [hit for hit in hosts.hits if hit.startswith(CITE_ONLY)] == []


def test_a_cite_only_page_keeps_no_bytes_so_its_own_host_serves_its_parts(hosts, guarded):
    hosts.pages["/page"] = (f'<div id="prices">$4.00</div><img src="{hosts.url(CITE_ONLY, "/a.png")}">'
                            f'<img src="{hosts.url(UNCLASSED, "/b.png")}">')
    result = guarded.fetch(hosts.url(CITE_ONLY, "/page"))
    assert result.outcome == "ok", result.error
    assert CITE_ONLY + "/a.png" in hosts.hits
    assert unclassed_hits(hosts) == []


def test_pages_get_no_webrtc(hosts, guarded):
    hosts.pages["/page"] = (
        '<div id="rtc"></div><script>document.querySelector("#rtc").textContent ='
        ' [typeof RTCPeerConnection, typeof webkitRTCPeerConnection].join("/")</script>')
    result = guarded.fetch(hosts.url(CLASSED, "/page"))
    assert result.outcome == "ok", result.error
    assert b'<div id="rtc">undefined/undefined</div>' in result.body


def test_a_redirect_another_parser_could_read_differently_is_refused(hosts, guarded):
    result = guarded.fetch(hosts.url(CLASSED, "/to-tricky"))
    assert (result.outcome, result.error) == ("unreachable", "ambiguous URL")
    assert hosts.hits == [CLASSED + "/to-tricky"]
