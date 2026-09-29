"""MODEL-219: use-case and comparison pages come from live decisions."""

from __future__ import annotations

import ast
import dataclasses
import html
import inspect
import re
from datetime import date
from pathlib import Path

import pytest

from decision.bands import BAND_PROBABILITY, THIN_INTERVAL_WIDTH, Distribution, p_at_least
from decision.contract import parse_spec
from decision.engine import decide
from decision.excluded import REMOVED_TEXT
from decision.registry import default
from decision.templates import load_catalogue
from decision.vocabulary import _template_rows
from pipeline import landing, uses

ROOT = Path(__file__).resolve().parents[1]
TODAY = date.today()


@pytest.fixture(scope="module")
def data() -> uses.Pages:
    return uses.build_data(str(ROOT), TODAY)


@pytest.fixture(scope="module")
def loaded():
    return landing.loaded_snapshot(str(ROOT), TODAY,
                                   landing.input_digest(ROOT, TODAY, snapshot_only=True))


@pytest.fixture(scope="module")
def pages(data: uses.Pages, tmp_path_factory) -> dict[str, str]:
    tree = tmp_path_factory.mktemp("site")
    written = uses.write(tree, data)
    return {path: (tree / path.strip("/") / "index.html").read_text(encoding="utf-8")
            for path in written["sitemap_paths"]}


def test_every_template_has_a_page_and_a_sitemap_entry(data: uses.Pages,
                                                      pages: dict[str, str]) -> None:
    ids = [row["id"] for row in load_catalogue()["templates"]]
    assert [use.id for use in data.uses] == ids
    for template_id in ids:
        assert f"/use/{template_id}/" in pages
    assert "/use/" in pages and "/compare/" in pages
    for pair in data.comparisons:
        assert pair.path in pages
    build = (ROOT / "pipeline" / "build.py").read_text(encoding="utf-8")
    assert 'ms_paths.extend(uses_counts["sitemap_paths"])' in build


def test_each_answer_is_the_engines_answer(data: uses.Pages, loaded) -> None:
    registry = default()
    catalogue = load_catalogue(registry=registry)
    availability = {row["id"]: row for row in
                    _template_rows(loaded, registry, catalogue["templates"])}
    for use, template in zip(data.uses, catalogue["templates"], strict=True):
        answer = decide(parse_spec(template["spec"] | {"explain": "none"}, facets=registry.facet),
                        loaded, facets=registry.facet)
        assert use.available == availability[use.id]["available"]
        assert use.reason == availability[use.id]["unavailable_reason"]
        bands = answer.bands
        if bands is None:
            assert (use.leader, use.best, use.rest, use.thin) == (None, (), (), ())
            continue
        assert use.leader == bands.leader
        for mine, theirs in ((use.best, bands.best), (use.rest, bands.rest),
                             (use.thin, bands.thin)):
            assert [row.model for row in mine] == [entry.model for entry in theirs]
            assert [(row.score, row.p_best, row.p_beats_leader, row.cost) for row in mine] == [
                (entry.score, entry.p_best, entry.p_beats_leader, entry.cost_per_task)
                for entry in theirs]
        assert [(term.share, term.p_best) for term in use.blend] == [
            (term.share, term.p_best) for term in answer.blend]


def test_comparisons_pair_only_banded_models_and_use_the_band_rule(data: uses.Pages,
                                                                   loaded) -> None:
    registry = default()
    assert data.comparisons
    for domain in {pair.domain for pair in data.comparisons}:
        spec = parse_spec({"spec_version": 1, "where": ["model.lifecycle = active"],
                           "optimize": {"max": domain}, "explain": "none"},
                          facets=registry.facet)
        bands = decide(spec, loaded, facets=registry.facet).bands
        banded = {entry.model: entry for entry in (*bands.best, *bands.rest)}
        for pair in (pair for pair in data.comparisons if pair.domain == domain):
            for side in (pair.a, pair.b):
                # Enough evidence to band: a thin model never gets a page.
                assert side.model in banded
                assert side.estimate.high - side.estimate.low <= THIN_INTERVAL_WIDTH
                assert side.p_best == banded[side.model].p_best
            assert pair.a.estimate.value >= pair.b.estimate.value
            assert pair.separated == (min(pair.p_a, pair.p_b) < BAND_PROBABILITY)
            # Against the domain's leader, the pair's P is the board's own p_beats_leader.
            if pair.a.model == bands.leader:
                assert pair.p_b == pytest.approx(banded[pair.b.model].p_beats_leader, abs=2e-4)


def test_pairwise_probability_is_the_engines_function(data: uses.Pages, loaded) -> None:
    candidate = {loaded.model_of(cid): cid for cid in loaded.candidates()}
    for pair in data.comparisons:
        a = loaded.capability_estimate(candidate[pair.a.model], pair.domain)
        b = loaded.capability_estimate(candidate[pair.b.model], pair.domain)
        assert pair.p_a == p_at_least(Distribution(a.value, a.sd), Distribution(b.value, b.sd))
        assert pair.p_b == p_at_least(Distribution(b.value, b.sd), Distribution(a.value, a.sd))


def _leaves(value):
    if dataclasses.is_dataclass(value):
        for field in dataclasses.fields(value):
            yield from _leaves(getattr(value, field.name))
    elif isinstance(value, tuple | list):
        for item in value:
            yield from _leaves(item)
    else:
        yield value


NUMBER = re.compile(r"[−-]?\$?\d[\d,]*(?:\.\d+)?%?")


def _text(page: str) -> str:
    body = page[page.index("<body>"):]
    return html.unescape(re.sub(r"<[^>]+>", " ", body))


def test_no_page_types_a_number(data: uses.Pages, pages: dict[str, str]) -> None:
    """Every number on a page is a data value through a formatter, or inside data text."""
    leaves = list(_leaves(data))
    strings = sorted({leaf for leaf in leaves if isinstance(leaf, str)}, key=len, reverse=True)
    numbers = {uses.when(data)}
    for leaf in leaves:
        if isinstance(leaf, bool) or leaf is None or isinstance(leaf, str):
            continue
        numbers |= {str(leaf), uses.num(leaf), uses.pct(leaf), uses.money(leaf)}
    numbers |= {str(pair.field) for pair in data.comparisons}
    for path, page in pages.items():
        text = _text(page)
        for value in strings:
            text = text.replace(value, " ")
        text = text.replace(uses.when(data), " ")
        stray = [token for token in NUMBER.findall(text) if token not in numbers]
        assert not stray, (path, stray)


def test_the_page_code_types_no_digits() -> None:
    """The copy in the renderers carries no digit of its own."""
    renderers = (uses._header, uses._page, uses._range, uses._evidence, uses._band_table,
                 uses._verdict, uses._blend, uses._conditions, uses.use_page, uses._side,
                 uses.compare_page, uses.use_index, uses.compare_index)
    allowed = {"width=device-width,initial-scale=1", "utf-8"}
    for function in renderers:
        tree = ast.parse(inspect.getsource(function).lstrip())
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                literal = node.value
                for text in allowed:
                    literal = literal.replace(text, "")
                literal = re.sub(r"</?h[1-6]\b", "", literal)
                assert not re.search(r"\d", literal), (function.__name__, node.value)


def test_pages_keep_the_neutrality_guardrails(pages: dict[str, str]) -> None:
    for path, page in pages.items():
        assert REMOVED_TEXT.search(page) is None, path
        lowered = page.lower()
        for phrase in ("affiliate", "sponsored", "utm_", "partner link", "dod",
                       "certified", "compliant with"):
            assert phrase not in lowered, (path, phrase)
        assert re.search(r"[?&](ref|via|aff)=", lowered) is None, path
        for href in re.findall(r'href="([^"]+)"', page):
            # Every link stays on modelspec.dev: no outbound, so nothing to be paid for.
            assert href.startswith(("/", "#", "https://modelspec.dev/")), (path, href)


def test_the_board_link_applies_the_template(data: uses.Pages, pages: dict[str, str]) -> None:
    for use in data.uses:
        page = pages[use.path]
        if use.available:
            assert f'href="/decide/?template={use.id}"' in page
        else:
            assert "?template=" not in page
            assert "No answer on this snapshot." in page


def test_thin_evidence_is_stated_plainly(data: uses.Pages, pages: dict[str, str]) -> None:
    for use in data.uses:
        if use.available and use.leader is None:
            assert "Not enough evidence to name a best model." in pages[use.path]
        if use.thin:
            assert "<h2>Not enough evidence</h2>" in pages[use.path]
    for pair in data.comparisons:
        page = pages[pair.path]
        verdict = ("The evidence separates them" if pair.separated
                   else "The evidence can't separate them")
        assert verdict in page
        for side in (pair.a, pair.b):
            if side.estimate.direct == 0:
                assert "rests on proxy benchmarks only" in page
