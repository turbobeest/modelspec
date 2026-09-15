"""Authoring guides on modelspec.dev model pages (MODEL-64)."""
from __future__ import annotations

import copy
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from pipeline.export import Build  # noqa: E402
from pipeline.load import Catalogue, Model, load_models  # noqa: E402
from pipeline.render import model_page  # noqa: E402

BUILD = Build(commit="abc", built_at="2026-09-15T00:00:00Z", as_of=date(2026, 9, 15))
FIXTURE = ROOT / "tests" / "fixtures" / "model_page_no_guide.html"

BASE_FRONT = {"display_name": "Tiny", "provider": "acme", "family": "tiny", "model_type": "llm",
              "status": "active", "benchmarks": {"scores": {"mmlu": 80.0}, "as_of": "2026-09-01"}}

SRC = {"url": "https://docs.acme.test/prompting", "title": "Prompting Tiny",
       "accessed": "2026-09-14", "kind": "provider_docs"}
GUIDE = {
    "applies_to": {"model_id": "acme/tiny", "version": "tiny-2"},
    "as_of": "2026-09-14",
    "status": "current",
    "sections": {
        "prompt_shape": [{"text": "Put the task first.", "sources": [SRC]}],
        "system_message": [],
        "reasoning_and_tools": [],
        "formatting": [{"text": "Ask for JSON explicitly.",
                        "sources": [{**SRC, "title": ""}]}],
        "failure_modes": [],
        "retry_advice": [],
    },
}


def _render(guide=None) -> str:
    front = copy.deepcopy(BASE_FRONT)
    if guide is not None:
        front["authoring_guide"] = guide
    model = Model("acme/tiny", Path("/r/models/acme/tiny.md"), front, "")
    return model_page(model, BUILD, {}, Catalogue(as_of=date(2026, 9, 15)))


def test_guided_card_renders_header_sections_claims_and_sources():
    html = _render(GUIDE)
    assert "<h2>Authoring guide</h2>" in html
    assert "reviewed 2026-09-14" in html
    assert '<span class="mono">tiny-2</span>' in html
    assert '<span class="pill active">current</span>' in html
    assert "<h3>Prompt shape</h3>" in html and "<h3>Formatting</h3>" in html
    assert "Put the task first." in html and "Ask for JSON explicitly." in html
    assert '<a href="https://docs.acme.test/prompting" rel="nofollow noopener">Prompting Tiny</a>' in html
    # Title falls back to the URL.
    assert ('<a href="https://docs.acme.test/prompting" rel="nofollow noopener">'
            "https://docs.acme.test/prompting</a>") in html
    assert "2026-09-14 &middot; provider_docs" in html
    assert "needs re-review" not in html


def test_stale_guide_shows_badge_and_rereview_line():
    html = _render({**GUIDE, "status": "stale"})
    assert '<span class="pill unverified">stale</span>' in html
    assert "This guide was written for an earlier version and needs re-review." in html


def test_empty_sections_are_omitted():
    html = _render(GUIDE)
    for label in ("System message", "Reasoning and tools", "Failure modes", "Retry advice"):
        assert f"<h3>{label}</h3>" not in html
    bare = _render({**GUIDE, "sections": {}})
    assert "<h2>Authoring guide</h2>" in bare
    assert "reviewed 2026-09-14" in bare
    assert "<h3>" not in bare


def test_authored_script_is_escaped():
    guide = copy.deepcopy(GUIDE)
    guide["sections"]["prompt_shape"][0]["text"] = "<script>alert(1)</script>"
    html = _render(guide)
    assert "<script>alert(1)</script>" not in html
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in html


def test_javascript_source_url_is_not_a_link():
    guide = copy.deepcopy(GUIDE)
    guide["sections"]["prompt_shape"][0]["sources"] = [
        {**SRC, "url": "javascript:alert(1)", "title": "evil"}]
    html = _render(guide)
    assert 'href="javascript:' not in html
    assert "evil" in html


def test_card_without_guide_is_byte_identical_to_main():
    # Fixture rendered from origin/main (e02237f) before this change.
    assert _render() == FIXTURE.read_text(encoding="utf-8")


def test_real_card_claude_opus_5_renders_guide():
    model = next(m for m in load_models(ROOT) if m.model_id == "anthropic/claude-opus-5")
    html = model_page(model, BUILD, {}, Catalogue(as_of=date(2026, 9, 15)))
    assert "<h2>Authoring guide</h2>" in html
    assert '<a href="https://platform.claude.com/docs/' in html
