"""Dated job comparisons preserve engine evidence without inventing a winner."""

import json
import socket
from copy import deepcopy
from datetime import date
from pathlib import Path

import pytest

from decision.excluded import REMOVED_TEXT, excluded_in
from pipeline import build
from pipeline.surface_lint import Page, publisher_subject

ROOT = Path(__file__).resolve().parents[1]
DAY = date(2026, 9, 23)


@pytest.fixture
def example():
    from decision.templates import load_templates

    template = load_templates()[0]
    entries = [
        {"model": model, "offering": {"model": model, "provider": "lab",
                                     "region": "global", "tier": "standard"},
         "score": score, "score_interval": [-0.123456789, 1.234567891],
         "p_best": probability, "p_beats_leader": against, "cost_per_task": cost,
         "estimates": [{"dimension": "software_engineering", "value": 1.3579,
                        "interval": [-0.2468, 2.9753], "benchmarks": 7,
                        "direct_benchmarks": 3}]}
        for model, score, probability, against, cost in (
            ("lab/z-leader", 0.812345, 0.56789123456789, None, 0.4321),
            ("lab/a-challenger", 0.75678, 0.12345678912345, 0.321987654, 0.01234),
            ("lab/next", 0.23456, 0.0456, 0.07654, None),
        )
    ]
    decision = {
        "decision_id": "dec_fixture", "snapshot": "snap_fixture", "status": "partial",
        "answer": {"kind": "tied", "members": [e["model"] for e in entries[:2]]},
        "results": [{"offering": e["offering"], "warnings": []} for e in entries],
        "bands": {"leader": entries[0]["model"], "best": entries[:2], "rest": entries[2:],
                  "thin": [], "basis": "fixture probability rule"},
    }
    comparison = {
        "snapshot": "snap_fixture", "models": [
            {"model": entry["model"], "facts": [
                {"facet": "model.release_date", "state": "not_disclosed", "value": None},
            ], "offerings": [{"offering": entry["offering"], "facts": [
                {"facet": "offering.speed.throughput", "state": "unknown", "value": None},
            ]}], "evidence": [
                {"benchmark": "swe_bench_pro", "record_id": entry["model"] + "#evidence",
                 "value": 71.23456789, "unit": "percent", "date": "2026-09-20",
                 "version": "fixture version", "interval": [70.123456, 72.345678],
                 "effort": "xhigh", "measured_by": "provider_self_report",
                 "subcategory": "python", "n": 123, "harness": "unregistered",
                 "source_ids": ["source-fixture"]},
            ]}
            for entry in sorted(entries[:2], key=lambda e: e["model"])
        ], "sources": [{"id": "source-fixture", "url": "https://example.org/evidence"}],
        "omitted": {"facts": 0, "offerings": 0, "evidence": 0},
    }
    return template, decision, comparison


def test_pairs_use_leader_ties_then_next_rank_and_canonical_order(example):
    from pipeline.comparison_pages import select_pairs, pair_path

    template, decision, _ = example
    pairs = select_pairs(decision)
    assert pairs == [("lab/a-challenger", "lab/z-leader"), ("lab/next", "lab/z-leader")]
    assert pair_path(template, pairs[0]) == "/compare/coding-best/lab--a-challenger-vs-lab--z-leader/"
    assert pair_path(template, pairs[0][::-1]) == pair_path(template, pairs[0])


def test_display_names_replace_ids_in_visible_copy_and_fall_back_when_absent(example):
    from pipeline.comparison_pages import comparison_page

    names = {"lab/z-leader": "Leader & Co", "lab/a-challenger": "Challenger <One>"}
    raw = comparison_page(*example, DAY, model_names=names)
    page = Page(raw)
    assert "Challenger <One> vs Leader & Co" in page.visible
    assert "Evidence for Leader & Co" in page.visible
    assert "Missing facts for Challenger <One>" in page.visible
    assert all(model not in page.visible for model in names)
    assert 'data-model="lab/z-leader"' in raw
    assert "Challenger &lt;One&gt;" in raw
    article = next(node for node in json.loads(page.ld[0])["@graph"] if node["@type"] == "Article")
    assert article["headline"] in page.visible
    assert "Challenger <One> vs Leader & Co" in article["headline"]
    del names["lab/a-challenger"]
    assert "lab/a-challenger vs Leader & Co" in Page(
        comparison_page(*example, DAY, model_names=names)
    ).visible


def test_pairs_are_capped_without_promoting_thin_or_prior_only_estimates(example):
    from pipeline.comparison_pages import select_pairs

    _, decision, _ = example
    best = decision["bands"]["best"]
    best.extend(dict(deepcopy(best[1]), model=f"lab/tie-{i}") for i in range(9))
    assert len(select_pairs(decision)) == 5
    best[1]["estimates"][0]["benchmarks"] = 0
    assert all("lab/a-challenger" not in pair for pair in select_pairs(decision))
    decision["bands"]["thin"] = decision["bands"]["rest"]
    decision["bands"]["rest"] = []
    assert all("lab/next" not in pair for pair in select_pairs(decision))
    best[0]["estimates"][0]["benchmarks"] = 0
    assert select_pairs(decision) == []


@pytest.mark.parametrize("missing", ["answer", "results"])
def test_unanswered_jobs_have_no_pairs(example, missing):
    from pipeline.comparison_pages import select_pairs

    _, decision, _ = example
    decision[missing] = None if missing == "answer" else []
    assert select_pairs(decision) == []


def test_tied_page_formats_probabilities_and_keeps_other_engine_numbers_and_equal_rows(example):
    from pipeline.comparison_pages import comparison_page

    template, decision, comparison = example
    original = deepcopy(example)
    raw = comparison_page(template, decision, comparison, DAY)
    page = Page(raw)
    assert "The evidence can't separate them for this job." in page.visible
    for value in ("-0.123456789", "1.234567891", "57%", "12%", "32%",
                  "0.4321", "0.01234", "71.23456789", "70.123456",
                  "model.release_date", "not_disclosed", "offering.speed.throughput"):
        assert value in page.visible
    assert "full ranked lineup for this job" in page.visible
    assert "lab/a-challenger has a 32% chance of matching or beating lab/z-leader on this job's objective." in page.visible
    assert "Separation from this challenger" not in page.visible
    for exact in ("0.56789123456789", "0.12345678912345", "0.321987654"):
        assert exact not in page.visible
    assert "winner" not in raw.lower()
    assert "lab/next" not in raw
    assert raw.count('class="comparison-model"') == 2
    assert 'href="https://example.org/evidence"' in raw
    assert example == original


def test_separated_verdict_states_job_date_and_probability_scope(example):
    from pipeline.comparison_pages import comparison_page

    template, decision, comparison = example
    challenger = decision["bands"]["best"].pop()
    decision["bands"]["rest"].insert(0, challenger)
    decision["answer"] = {"kind": "separated", "members": ["lab/z-leader"], "leader": "lab/z-leader"}
    page = Page(comparison_page(template, decision, comparison, DAY))
    assert "The evidence separates them" in page.visible
    assert ("The evidence separates them: lab/z-leader leads for Coding (best available), "
            "with a 57% chance of being the best model in the full lineup for this job, "
            "as of 2026-09-23.") in page.visible
    assert "full ranked lineup for this job" in page.visible


def test_measurements_keep_returned_conditions_and_probability_excludes_unranked(example):
    from pipeline.comparison_pages import comparison_page

    page = Page(comparison_page(*example, DAY))
    for value in ("xhigh", "provider_self_report", "python", "123", "unregistered"):
        assert value in page.visible
    assert "Models with unknown objective values remain unranked" in page.visible


def test_unsupported_pair_is_noindex_and_does_not_claim_separation(example):
    from pipeline.comparison_pages import comparison_page

    template, decision, comparison = example
    decision["bands"]["best"][1]["estimates"][0]["benchmarks"] = 0
    page = Page(comparison_page(template, decision, comparison, DAY))
    assert page.meta["robots"] == "noindex, follow"
    assert "No comparison" in page.visible
    assert "The evidence separates them" not in page.visible


def test_page_uses_registry_copy_keyed_access_and_consistent_jsonld(example):
    from pipeline import entity
    from pipeline.comparison_pages import comparison_page

    template, decision, comparison = example
    raw = comparison_page(template, decision, comparison, DAY)
    page = Page(raw)
    assert page.first_paragraph == entity.ONE_SENTENCE
    for value in (template["purpose"], template["tradeoff"], template["teaches"],
                  *[row["reason"] for row in template["where"]]):
        assert value in page.visible
    assert "CLI, API, and MCP access requires a key" in page.visible
    assert 'href="/legal/neutrality/"' in raw
    assert 'href="/decide/details/?template=coding-best"' in raw
    assert not REMOVED_TEXT.search(raw)
    assert excluded_in(publisher_subject("compare/index.html", raw)) is False
    nodes = json.loads(page.ld[0])["@graph"]
    article = next(node for node in nodes if node["@type"] == "Article")
    assert article["headline"] in page.visible
    assert article["description"] in page.visible
    assert article["dateModified"] == DAY.isoformat()
    crumbs = next(node for node in nodes if node["@type"] == "BreadcrumbList")
    assert crumbs["itemListElement"][1]["item"] == "https://modelspec.dev/compare/"


def test_real_image_is_public_offline_deterministic_and_bounded(tmp_path, monkeypatch):
    from decision import registry
    from pipeline import comparison_pages

    def no_network(*args, **kwargs):
        pytest.fail("comparison generation attempted network access")

    monkeypatch.setattr(socket, "create_connection", no_network)
    monkeypatch.setenv("MODELSPEC_DATA_DIR", str(tmp_path / "private-must-not-be-read"))
    saved = registry.REPO_ROOT
    private = tmp_path / "private-default-must-not-be-read"
    registry.use_root(private)
    try:
        first = comparison_pages.write(tmp_path / "first", ROOT)
        assert registry.REPO_ROOT == private
        second = comparison_pages.write(tmp_path / "second", ROOT)
        assert registry.REPO_ROOT == private
    finally:
        registry.use_root(saved)
    assert first == second
    assert len(first["sitemap_paths"]) == 41
    assert set(first["sitemap_dates"].values()) == {build.use_case_image_date(ROOT).isoformat()}
    pages = {p.relative_to(tmp_path / "first"): p.read_bytes()
             for p in (tmp_path / "first").rglob("*.html")}
    assert len(pages) == 41
    index = Page(pages[Path("compare/index.html")].decode())
    assert "Claude Opus 5.5 vs Claude Sonnet 5.5" in index.visible
    assert "anthropic/claude-opus-5-5" not in index.visible
    assert pages == {p.relative_to(tmp_path / "second"): p.read_bytes()
                     for p in (tmp_path / "second").rglob("*.html")}
    assert not any("retrieval-private/" in str(path) for path in pages)
    for path, raw in pages.items():
        page = Page(raw.decode())
        assert page.meta["robots"] == "index, follow"
        assert "CLI, API, and MCP access requires a key" in page.visible
        assert not REMOVED_TEXT.search(raw.decode())
        assert excluded_in(publisher_subject("compare/index.html", raw.decode())) is False
        if str(path) != "compare/index.html":
            assert "can't separate them" in page.visible or "The evidence separates them" in page.visible

