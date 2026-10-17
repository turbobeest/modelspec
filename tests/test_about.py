"""The /about/ facts page is the registry, rendered (MODEL-271)."""

from __future__ import annotations

import html
import json
import re
from html.parser import HTMLParser
from pathlib import Path

from api.ranking.engine import neutrality_commitment
from pipeline import entity, landing, live, method, pricing

ROOT = Path(__file__).resolve().parents[1]


def _norm(text: str) -> str:
    return " ".join(html.unescape(text).split())


class _MainBlocks(HTMLParser):
    """Visible text of each heading, paragraph and list item inside <main>."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._main = 0
        self._stack: list[str] = []
        self._buf: list[list[str]] = []
        self.blocks: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "main":
            self._main += 1
        if self._main and tag in {"h1", "h2", "p", "li"}:
            self._stack.append(tag)
            self._buf.append([])

    def handle_endtag(self, tag: str) -> None:
        if self._main and self._stack and tag == self._stack[-1]:
            self.blocks.append(_norm("".join(self._buf.pop())))
            self._stack.pop()
        if tag == "main" and self._main:
            self._main -= 1

    def handle_data(self, data: str) -> None:
        if self._stack:
            self._buf[-1].append(data)


def _blocks(page: str) -> list[str]:
    parser = _MainBlocks()
    parser.feed(page)
    return parser.blocks


def _expected(tiers: dict) -> list[str]:
    return [
        entity.ABOUT_HEADING,
        f"{entity.DISAMBIGUATION} {entity.ONE_SENTENCE}",
        entity.CLAIMS_HEADING,
        *[claim.statement for claim in entity.CLAIMS],
        entity.CALL_HEADING,
        *[call.statement for call in entity.CALLS],
        entity.COST_HEADING,
        *entity.cost_statements(tiers),
        entity.NEUTRALITY_LINK,
    ]


def test_raw_html_shows_the_sentence_disambiguation_first_and_every_claim() -> None:
    from pipeline import about

    tiers = pricing.load_tiers(ROOT)
    page = about.page(tiers, ROOT)
    blocks = _blocks(page)
    assert blocks == _expected(tiers)
    assert blocks[1].startswith(entity.DISAMBIGUATION)
    assert entity.ONE_SENTENCE in blocks[1]
    for claim in entity.CLAIMS:
        assert claim.statement in blocks
    assert "<h1" in page
    assert 'rel="canonical" href="https://modelspec.dev/about/"' in page
    assert "noindex" not in page
    assert live.visible_words(page) >= live.MIN_WORDS
    main = re.search(r"<main\b[^>]*>(.*)</main>", page, re.S)
    assert main is not None and "<script" not in main.group(1)


def test_every_about_string_is_a_registry_or_tier_string() -> None:
    """A hand-typed sentence in <main> is not on the allowed list, so this fails."""
    from pipeline import about

    tiers = pricing.load_tiers(ROOT)
    allowed = set(_expected(tiers))
    assert set(_blocks(about.page(tiers, ROOT))) <= allowed


def test_no_claim_or_call_appears_only_on_about(data_path: Path = ROOT) -> None:
    from pipeline import about

    data = landing.build_data(str(data_path), __import__("datetime").date.today())
    tiers = pricing.load_tiers(data_path)
    homes = " ".join((
        _norm(landing.render(data, variant="live")),
        _norm(method.page(data, method.SigningState((), None))),
        _norm(pricing.page(tiers, access_enforced=True, x402_live=False, billing_live=True)),
    ))
    about_text = " ".join(_blocks(about.page(tiers, data_path)))
    for claim in entity.CLAIMS:
        assert claim.statement in about_text
        assert claim.statement in homes, claim.id
    for call in entity.CALLS:
        assert call.statement in about_text
        assert call.statement in homes, call.id
    for line in entity.cost_statements(tiers):
        assert line in about_text
        for number in re.findall(r"\d[\d,]*", line):
            assert number in homes, (line, number)


def test_costs_are_read_from_tiers_and_not_typed() -> None:
    from pipeline import about

    source = (ROOT / "pipeline" / "about.py").read_text(encoding="utf-8")
    assert not re.search(r"\$\d", source)
    assert not re.search(r"\b\d{2,}\b", source)
    tiers = pricing.load_tiers(ROOT)
    original = about.page(tiers, ROOT)
    changed = json.loads(json.dumps(tiers))
    changed["credits"]["weights"]["decide.full"] = 17
    changed["billing"]["prices"]["price_1UP22XBPydVRHUBjk9rrxOxN"]["usd"] = 12345
    rendered = about.page(changed, ROOT)
    assert "A fully explained decision costs 17 credits." in rendered
    assert "17 credits" not in original
    assert "Solo costs $12345 a month for 2,500 credits." in rendered
    assert "$12345" not in original


def test_the_neutrality_commitment_is_linked_and_not_copied() -> None:
    from pipeline import about

    page = about.page(pricing.load_tiers(ROOT), ROOT)
    pledge = str(neutrality_commitment()["pledge"])
    assert pledge not in page
    assert f'href="{entity.NEUTRALITY_PATH}"' in page
    assert entity.NEUTRALITY_LINK in _blocks(page)


def test_organization_json_ld_matches_the_visible_text() -> None:
    from pipeline import about, structured_data

    page = about.page(pricing.load_tiers(ROOT), ROOT)
    blocks = re.findall(
        r'<script type="application/ld\+json" data-structured-data>(.*?)</script>', page, re.S)
    assert len(blocks) == 1
    nodes = json.loads(blocks[0])["@graph"]
    org = next(node for node in nodes if node.get("@type") == "Organization")
    visible = _norm(re.sub(r"<[^>]+>", " ", re.search(r"<body\b[^>]*>(.*)</body>", page, re.S).group(1)))
    assert org["description"] == entity.ONE_SENTENCE
    assert org["description"] in visible
    assert org["name"] in visible
    assert nodes == structured_data.graph("/about/", ROOT, ROOT)


def test_about_is_in_the_sitemap_with_a_lastmod() -> None:
    import xml.etree.ElementTree as ET

    xml = live.sitemap()
    namespace = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    rows = {
        node.findtext("s:loc", "", namespace): node.findtext("s:lastmod", "", namespace)
        for node in ET.fromstring(xml).findall("s:url", namespace)
    }
    stamp = rows["https://modelspec.dev/about/"]
    assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", stamp)
    assert "/about/" in live.PAGES
    assert "about" in live.KEEP_DIRS
    assert live.PAGE_SOURCES["/about/"]
    for source in live.PAGE_SOURCES["/about/"]:
        assert (ROOT / source).is_file(), source
