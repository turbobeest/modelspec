"""The pipeline's promises, held to.

These guard the claims the sites make in public: that only verified benchmarks
are presented as current, that coverage tables are derived rather than authored,
and that a build cannot publish an active set it cannot justify.
"""

from __future__ import annotations

import functools
import json
import re
import sys
from datetime import date
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from pipeline import build as builder  # noqa: E402
from pipeline.export import models_by_benchmark  # noqa: E402
from pipeline.load import (  # noqa: E402
    Catalogue,
    LoadError,
    load_benchmarks,
    load_catalogue,
    load_models,
    split_front_matter,
)
from pipeline.render import format_score  # noqa: E402

# Parsing 1,143 cards and 1,106 pages costs seconds; the corpus does not change
# during a run, so load each once for the whole module.
_models = functools.lru_cache(maxsize=1)(load_models)
_benchmarks = functools.lru_cache(maxsize=1)(load_benchmarks)
_catalogue = functools.lru_cache(maxsize=1)(load_catalogue)
_coverage = functools.lru_cache(maxsize=1)(lambda: models_by_benchmark(_models()))


# ── loading ──────────────────────────────────────────────────────────────────

def test_front_matter_requires_a_mapping() -> None:
    with pytest.raises(LoadError):
        split_front_matter("---\n- a\n- b\n---\nbody\n")


def test_missing_front_matter_is_an_error() -> None:
    with pytest.raises(LoadError):
        split_front_matter("no front matter here")


def test_prose_beside_the_data_is_not_loaded_as_data() -> None:
    """models/LICENSE.md and benchmarks/LICENSE.md are prose, not records."""
    model_ids = {m.model_id for m in _models()}
    assert "LICENSE" not in model_ids
    benchmark_ids = {b.benchmark_id for b in _benchmarks()}
    assert "LICENSE" not in benchmark_ids
    assert "AUTHORING" not in benchmark_ids


def test_benchmark_ids_are_unique() -> None:
    benchmarks = _benchmarks()
    ids = [b.benchmark_id for b in benchmarks]
    assert len(ids) == len(set(ids))


# ── the catalogue contract ───────────────────────────────────────────────────

def test_an_unassessed_benchmark_is_not_active() -> None:
    """Absence of evidence is not a disposition, and never active."""
    catalogue = _catalogue()
    disposition = catalogue.for_benchmark("a-benchmark-nobody-has-ever-assessed")
    assert disposition.status == "unassessed"
    assert disposition.is_active is False


def test_active_set_comes_only_from_the_report() -> None:
    catalogue = _catalogue()
    report = json.loads(
        (REPO_ROOT / "benchmarks/_census/eligibility/current-report.json").read_text()
    )
    assert catalogue.active_ids == sorted(report["active_ids"])


def test_every_active_benchmark_has_a_page() -> None:
    """The catalogue cannot list a benchmark the site cannot render."""
    pages = {b.benchmark_id for b in _benchmarks()}
    assert set(_catalogue().active_ids) <= pages


def test_an_empty_report_yields_an_empty_active_set(tmp_path: Path) -> None:
    """A missing report must not fall back to treating the census as a catalogue."""
    catalogue = load_catalogue(tmp_path)
    assert catalogue.active_ids == []
    assert catalogue.for_benchmark("anything").status == "unassessed"


def test_future_dated_report_refuses_to_publish(tmp_path: Path, monkeypatch) -> None:
    """A visit cannot rejuvenate evidence, and a build cannot predate its own data."""
    monkeypatch.setattr(
        builder, "load_catalogue", lambda root: Catalogue(as_of=date(2999, 1, 1))
    )
    assert builder.main(["--out", str(tmp_path / "dist")]) == 2


# ── derivation, not authorship ───────────────────────────────────────────────

def test_coverage_is_derived_from_the_cards() -> None:
    """Every coverage row must trace back to a score on that model's own card."""
    models = _models()
    scores_by_model = {m.model_id: m.scores for m in models}
    coverage = models_by_benchmark(models)
    for key, rows in coverage.items():
        for row in rows:
            assert key in scores_by_model[row["model_id"]]
            assert scores_by_model[row["model_id"]][key] == row["score"]


def test_coverage_is_ordered_by_score() -> None:
    coverage = _coverage()
    rows = coverage["swe_bench_verified"]
    assert [r["score"] for r in rows] == sorted((r["score"] for r in rows), reverse=True)


def test_legacy_card_scores_are_marked_unverified() -> None:
    """Card scores carry no per-score source, so they must never read as evidence."""
    coverage = _coverage()
    rows = coverage["gpqa_diamond"]
    assert rows and all(r["attribution"] == "unverified-legacy" for r in rows)


# ── presentation ─────────────────────────────────────────────────────────────

@pytest.mark.parametrize(
    ("value", "unit", "expected"),
    [(56.0, "percent", "56.0%"), (12, "normalized Elo percent", "12 normalized Elo percent"),
     (5, None, "5"), (None, "percent", "—")],
)
def test_score_formatting(value: object, unit: object, expected: str) -> None:
    assert format_score(value, unit) == expected


# ── internal links must resolve to output ────────────────────────────────────

def test_a_dead_internal_href_is_reported(tmp_path: Path) -> None:
    tree = tmp_path / "site"
    tree.mkdir()
    (tree / "index.html").write_text('<a href="/m/Qwen/Qwen3-0.6B/">x</a>', encoding="utf-8")
    missing = builder.missing_internal_hrefs(tree)
    assert missing == [("index.html", "/m/Qwen/Qwen3-0.6B/")]


def test_script_string_templates_are_not_treated_as_hrefs(tmp_path: Path) -> None:
    tree = tmp_path / "site"
    tree.mkdir()
    (tree / "index.html").write_text(
        '<a href="/">home</a><script>h = \'<a href="/m/\' + id + \'/">\';</script>',
        encoding="utf-8",
    )
    assert builder.missing_internal_hrefs(tree) == []


def test_an_existing_page_is_not_a_dead_href(tmp_path: Path) -> None:
    tree = tmp_path / "site"
    (tree / "m" / "qwen" / "qwen3-0-6b").mkdir(parents=True)
    (tree / "m" / "qwen" / "qwen3-0-6b" / "index.html").write_text("ok", encoding="utf-8")
    (tree / "index.html").write_text(
        '<a href="/m/qwen/qwen3-0-6b/">Qwen3 0.6B</a>', encoding="utf-8"
    )
    assert builder.missing_internal_hrefs(tree) == []


def test_wizard_discloses_per_result_evidence_basis() -> None:
    src = (REPO_ROOT / "web3d/downselect.v2.html").read_text(encoding="utf-8")
    assert "evidence_basis" in src
    for term in ("verified", "partial-verified", "mixed", "unverified-legacy", "none"):
        assert term in src
    assert "coverage" in src
    assert "wizard_min_benchmark_coverage" in src
    assert "unranked for insufficient evidence" in src
    assert "<!-- catalogue-freshness -->" in src


def test_wizard_hardware_filter_checks_key_presence_not_truthiness() -> None:
    """MODEL-53: c.fits[id] can be `null` for a non-token model that fits.

    `!(c.fits && c.fits[s.hardware])` would treat that the same as "does not
    fit" and silently drop it from a hardware-filtered wizard search. The
    filter must check whether the key is present, not whether its value is
    truthy.
    """
    src = (REPO_ROOT / "web3d/downselect.v2.html").read_text(encoding="utf-8")
    assert "hasOwnProperty" in src
    assert "!(c.fits && c.fits[s.hardware])" not in src


def test_landing_injects_catalogue_freshness() -> None:
    html = builder.wire_landing(
        '<nav><a href="https://github.com/turbobeest/modelspec">GitHub</a></nav>'
        "<footer>end</footer>",
        {"models": 1, "providers": 1, "edges": 1, "benchmarks": 1, "fields": 1},
        freshness='<p class="meta">Catalogue eligibility as of <strong>2026-09-01</strong></p>',
    )
    assert "2026-09-01" in html
    assert html.index("2026-09-01") < html.index("<footer>")


def test_benchgraph_headline_counts_pages_apart_from_scored_keys() -> None:
    """164 scored keys used to ship as '164 benchmarks' against 1,000+ pages."""
    stats = builder.benchgraph_headline_stats(_models(), _benchmarks(), _coverage())
    assert stats["pages"] == len(_benchmarks())
    assert stats["scored_benchmarks"] == len(_coverage())
    assert stats["scored_models"] == sum(1 for m in _models() if m.scores)
    assert stats["scores"] == sum(len(rows) for rows in _coverage().values())
    assert stats["pages"] > stats["scored_benchmarks"]
    from pipeline.render import catalogue_headline
    today = catalogue_headline(stats)
    assert "benchmarks with reported scores" in today
    assert "benchmark pages" in today
    assert f'<b>{stats["pages"]:,}</b>' in today
    assert f'<b>{stats["scored_benchmarks"]:,}</b>' in today
    assert "{{N_PAGES}}" not in today and "{{N_BENCH}}" not in today


def _bench_html(front: dict) -> str:
    from pipeline.export import Build
    from pipeline.load import Benchmark
    from pipeline.render import benchmark_page

    bench = Benchmark("demo", Path("benchmarks/demo.md"), {"name": "Demo", **front}, "")
    build = Build(commit="abc", built_at="2026-09-15T00:00:00Z", as_of=date(2026, 9, 15))
    return benchmark_page(bench, build, Catalogue(as_of=date(2026, 9, 15)), [])


def test_benchmark_page_renders_sources_and_links() -> None:
    html = _bench_html({
        "leaderboard_url": "https://lb.example/",
        "paper": {"title": "Demo <paper>", "url": "", "arxiv": "2401.00001"},
        "repo_url": "https://github.com/x/demo",
        "sources": [{"url": "https://src.example/a", "title": "Source A", "accessed": "2026-09-14"},
                    {"url": "https://src.example/b", "title": "", "accessed": "2026-09-13"}],
    })
    assert "<h2>Sources</h2>" in html and "<h2>Links</h2>" in html
    assert '<a href="https://src.example/a" rel="nofollow noopener">Source A</a>' in html
    assert ">https://src.example/b</a>" in html and "read 2026-09-14" in html
    assert 'href="https://lb.example/"' in html
    assert 'href="https://arxiv.org/abs/2401.00001"' in html and "Demo &lt;paper&gt;" in html
    assert 'href="https://github.com/x/demo"' in html


def test_benchmark_page_omits_empty_links_and_sources() -> None:
    html = _bench_html({"leaderboard_url": "", "paper": {"title": "", "url": "", "arxiv": ""},
                        "repo_url": "", "sources": []})
    assert "<h2>Sources</h2>" not in html and "<h2>Links</h2>" not in html
    assert 'href=""' not in html


def test_benchmark_page_does_not_link_non_http_urls() -> None:
    html = _bench_html({"leaderboard_url": "javascript:alert(1)",
                        "sources": [{"url": "ftp://x/y", "title": "FTP", "accessed": "2026-09-14"}]})
    assert 'href="javascript:' not in html and 'href="ftp:' not in html
    assert "javascript:alert(1)" in html and "FTP" in html
