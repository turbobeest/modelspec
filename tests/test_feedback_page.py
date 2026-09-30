"""MODEL-221: /feedback/, and the Feedback control on every built page."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import pytest

from pipeline import feedback_page

REPO_ROOT = Path(__file__).resolve().parent.parent
PAGE = ("<!doctype html><html><head><title>x</title></head>"
        "<body><main>hi</main></body></html>")


def test_the_control_is_a_link_that_works_without_javascript() -> None:
    page = feedback_page.inject(PAGE)
    assert '<a class="ms-fb-launch" href="/feedback/" data-feedback-launch>Feedback</a>' in page
    assert page.index("feedback.css") < page.index("</head>")
    assert page.index("data-feedback-launch") > page.index("<main>")
    assert page.endswith("</body></html>")


def test_injecting_twice_changes_nothing_and_a_fragment_is_left_alone() -> None:
    once = feedback_page.inject(PAGE)
    assert feedback_page.inject(once) == once
    assert feedback_page.inject("<svg></svg>") == "<svg></svg>"


def test_inject_tree_reaches_every_page(tmp_path) -> None:
    for rel in ("index.html", "method/index.html", "legal/privacy/index.html", "404.html"):
        (tmp_path / rel).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / rel).write_text(PAGE, encoding="utf-8")
    assert feedback_page.inject_tree(tmp_path) == 4
    assert all(feedback_page.MARKER in p.read_text() for p in tmp_path.rglob("*.html"))
    assert feedback_page.inject_tree(tmp_path) == 0


def test_the_page_publishes_the_form_the_agent_path_and_the_schema(tmp_path) -> None:
    counts = feedback_page.write(tmp_path, REPO_ROOT)
    assert counts["sitemap_paths"] == ["/feedback/"]
    html = (tmp_path / "feedback" / "index.html").read_text(encoding="utf-8")
    for needle in ("data-feedback-inline", "https://api.modelspec.dev/v1/feedback",
                   "https://modelspec.dev/api/feedback/v1.schema.json",
                   "https://api.modelspec.dev/mcp", 'id="privacy"',
                   "Feedback storage is switched off", 'id="changes"',
                   '<link rel="canonical" href="https://modelspec.dev/feedback/">',
                   "/feedback-assets/feedback.js"):
        assert needle in html, needle
    assert "modelspec feedback DECISION_ID" not in html
    assert (tmp_path / "feedback-assets" / "feedback.js").is_file()
    published = json.loads((tmp_path / "api" / "feedback" / "v1.schema.json").read_text())
    assert published["$id"] == "https://modelspec.dev/api/feedback/v1.schema.json"


def test_what_we_changed_lists_entries_newest_first_and_escapes_them(tmp_path) -> None:
    (tmp_path / "docs" / "feedback").mkdir(parents=True)
    (tmp_path / "docs" / "feedback" / "changes.yaml").write_text(
        "changes:\n"
        "  - {date: 2026-10-01, told: 'Bands <b>confusing</b>', changed: 'Explained them'}\n"
        "  - {date: 2026-10-08, told: 'Pricing unclear', changed: 'Added a unit',"
        " link: 'https://github.com/turbobeest/modelspec/pull/1'}\n", encoding="utf-8")
    rows = feedback_page.load_changes(tmp_path)
    assert [r["date"] for r in rows] == [date(2026, 10, 8), date(2026, 10, 1)]
    html = feedback_page.page(rows)
    assert "Bands &lt;b&gt;confusing&lt;/b&gt;" in html
    assert html.index("Pricing unclear") < html.index("Bands")


def test_a_changes_entry_without_what_changed_is_refused(tmp_path) -> None:
    (tmp_path / "docs" / "feedback").mkdir(parents=True)
    (tmp_path / "docs" / "feedback" / "changes.yaml").write_text(
        "changes:\n  - {date: 2026-10-01, told: 'x'}\n", encoding="utf-8")
    with pytest.raises(ValueError, match="missing"):
        feedback_page.load_changes(tmp_path)


def test_the_committed_ledger_is_valid_and_honest_while_storage_is_off() -> None:
    assert feedback_page.load_changes(REPO_ROOT) == []
