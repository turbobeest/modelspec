"""One description of ModelSpec, on every surface that describes it (MODEL-252)."""

from __future__ import annotations

import html
import json
import re
from datetime import date
from pathlib import Path

import pytest

from pipeline import agent_ready, brand, entity, landing, method, structured_data
from pipeline.build import llms_txt
from pipeline.export import Build
from pipeline.load import load_benchmarks, load_models

ROOT = Path(__file__).resolve().parents[1]
BUILD = Build(commit="0" * 40, built_at="2026-10-01T00:00:00+00:00", as_of=date(2026, 10, 1))


def _visible(page: str) -> str:
    """What a reader sees of an inline fragment: tags dropped, entities decoded, spaces collapsed."""
    text = re.sub(r"<(script|style)\b.*?</\1>", " ", page, flags=re.S)
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", text)))


def _meta(page: str, attr: str, key: str) -> str:
    match = re.search(rf'<meta {attr}="{re.escape(key)}" content="([^"]*)"', page)
    assert match, key
    return html.unescape(match.group(1))


@pytest.fixture(scope="module")
def data() -> landing.LandingData:
    return landing.build_data(str(ROOT), date.today())


@pytest.fixture(scope="module")
def surfaces(data: landing.LandingData) -> dict[str, str]:
    live = landing.render(data, variant="live")
    return {
        "landing": live,
        "landing holding": landing.render(data, variant="holding"),
        "method": method.page(data, method.SigningState((), None)),
        "llms.txt": llms_txt(site="ModelSpec", base="https://modelspec.dev", build=BUILD),
        "index.md": agent_ready.modelspec_landing_markdown(
            load_models(ROOT), load_benchmarks(ROOT), BUILD),
        "SKILL.md": agent_ready.skill_markdown(),
    }


def test_the_landing_says_the_sentence_in_its_meta_and_its_lead(surfaces: dict[str, str]) -> None:
    for name in ("landing", "landing holding"):
        page = surfaces[name]
        assert f"<title>{entity.TITLE}</title>" in page
        assert _meta(page, "name", "description") == f"{entity.ONE_SENTENCE} Nobody pays to rank higher."
        assert _meta(page, "property", "og:description").startswith(entity.ONE_SENTENCE)
        lead = re.search(r'<p class="close">(.*?)</p>', page, re.S)
        assert lead and _visible(lead.group(1)).strip().startswith(entity.ONE_SENTENCE), name


def test_the_method_page_opens_with_the_sentence_then_the_disambiguation(surfaces: dict[str, str]) -> None:
    first = re.search(r"<h1>How ModelSpec decides\.</h1><p>(.*?)</p>", surfaces["method"], re.S)
    assert first is not None
    assert _visible(first.group(1)).startswith(f"{entity.ONE_SENTENCE} {entity.DISAMBIGUATION} ")


@pytest.mark.parametrize("name", ["llms.txt", "index.md", "SKILL.md"])
def test_agent_files_open_with_the_sentence_and_the_disambiguation(surfaces: dict[str, str], name: str) -> None:
    assert f"{entity.ONE_SENTENCE} {entity.DISAMBIGUATION}" in surfaces[name]
    assert brand.POSITIONING.startswith(entity.ONE_SENTENCE)


def test_the_mcp_card_carries_the_short_form() -> None:
    assert agent_ready.mcp_card()["description"] == entity.SHORT


def test_the_organization_json_ld_describes_and_links_the_entity() -> None:
    org = structured_data.organization(ROOT)
    assert org["description"] == entity.ONE_SENTENCE
    assert org["sameAs"][0] == entity.REPOSITORY


def test_the_readme_opens_with_the_sentence() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    prose = next(line for line in readme.splitlines() if line.startswith("ModelSpec "))
    assert prose.startswith(entity.ONE_SENTENCE)


def test_no_superseded_one_liner_survives_on_any_surface(surfaces: dict[str, str]) -> None:
    rendered = {
        **surfaces,
        "mcp.json": json.dumps(agent_ready.mcp_card()),
        "json-ld": json.dumps(structured_data.organization(ROOT)),
        "README.md": (ROOT / "README.md").read_text(encoding="utf-8"),
    }
    hits = [(name, old) for name, text in rendered.items()
            for old in entity.SUPERSEDED if old.lower() in text.lower()]
    assert hits == []


def test_registry_strings_fit_their_surfaces() -> None:
    assert len(entity.TITLE) <= 60
    assert len(entity.SHORT) <= agent_ready.MCP_DESCRIPTION_MAX
    for text in (entity.ONE_SENTENCE, entity.TITLE, entity.SHORT, entity.DISAMBIGUATION):
        assert not set(text) & set('"<>&'), text  # safe in an attribute and in text


def test_the_disambiguation_names_all_three_collisions() -> None:
    for name in ("OpenAI's Model Spec", "CNCF ModelPack", "Python package named modelspec"):
        assert name in entity.DISAMBIGUATION


def test_claims_say_only_what_the_service_does_today() -> None:
    text = " ".join(c.statement for c in entity.CLAIMS).lower()
    for unshipped in ("x402", "bazaar", "pay per call", "without an api key", "cli"):
        assert unshipped not in text, unshipped
    ties = next(c for c in entity.CLAIMS if c.id == "ties-declared").statement
    assert "returns the tie" in ties and "returns the cheapest" not in ties
    assert len({c.id for c in entity.CLAIMS}) == len(entity.CLAIMS)
    assert all(c.proof.startswith(entity.SITE) for c in entity.CLAIMS)


def test_linked_keeps_the_visible_text_and_refuses_a_missing_phrase() -> None:
    out = entity.linked(entity.ONE_SENTENCE, {"real cost": "/cost", "shows its work": "/method/"})
    assert out.count("<a ") == 2
    assert _visible(out) == entity.ONE_SENTENCE
    with pytest.raises(ValueError, match="must occur exactly once"):
        entity.linked(entity.ONE_SENTENCE, {"every benchmark": "/x"})


def test_the_method_page_says_what_is_public_in_both_data_states(
        data: landing.LandingData, monkeypatch: pytest.MonkeyPatch) -> None:
    """MODEL-247 makes the fresh snapshot private; the page must not promise it then."""
    def public_data(flag: str) -> str:
        monkeypatch.setenv("DATA_SPLIT_ENABLED", flag)
        page = method.page(data, method.SigningState((), None))
        return _visible(re.search(r'<section class="public-data">(.*?)</section>', page, re.S).group(1))

    split = public_data("true")
    assert "free to fetch" not in split
    assert "snapshot.json.gz" not in split
    assert "frozen public image" in split
    assert "public, versioned and free to fetch" in public_data("false")
