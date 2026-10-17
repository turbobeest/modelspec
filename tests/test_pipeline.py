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
from pipeline.export import Build, models_by_benchmark, write  # noqa: E402
from pipeline.load import (  # noqa: E402
    Benchmark,
    Catalogue,
    LoadError,
    Model,
    load_benchmarks,
    load_catalogue,
    load_models,
    split_front_matter,
)
from pipeline.render import (  # noqa: E402
    benchmark_chart,
    benchmark_page,
    benchmark_strip_asset,
    format_score,
    model_benchmark_strips,
    model_page,
)

# Parsing 1,143 cards and 1,106 pages costs seconds; the corpus does not change
# during a run, so load each once for the whole module.
_models = functools.lru_cache(maxsize=1)(load_models)
_benchmarks = functools.lru_cache(maxsize=1)(load_benchmarks)
_catalogue = functools.lru_cache(maxsize=1)(load_catalogue)
_coverage = functools.lru_cache(maxsize=1)(
    lambda: models_by_benchmark(_models(), _benchmarks()))


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


def test_the_build_day_matches_built_at_when_the_local_date_lags(monkeypatch) -> None:
    """Sitemap and page dates use the UTC day of built_at when the local date is behind."""
    from xml.etree.ElementTree import fromstring

    from pipeline import export as exporter
    from pipeline.render import sitemap

    local = date(2026, 4, 1)

    class LocalDay:
        @staticmethod
        def today() -> date:
            return local

        @staticmethod
        def fromisoformat(value: str) -> date:
            return date.fromisoformat(value)

    monkeypatch.setattr(builder, "date", LocalDay)
    monkeypatch.setattr(exporter, "date", LocalDay)
    monkeypatch.setattr("pipeline.render.date", LocalDay)
    built = Build(
        commit="a" * 40,
        built_at="2026-04-02T01:30:00+00:00",
        as_of=date(2026, 4, 1),
    )
    day = builder.build_day(built)
    assert day == date(2026, 4, 2)
    lastmod = fromstring(sitemap("https://modelspec.dev", ["/"], day)).findtext(
        "{http://www.sitemaps.org/schemas/sitemap/0.9}url/"
        "{http://www.sitemaps.org/schemas/sitemap/0.9}lastmod"
    )
    assert lastmod == "2026-04-02"


# ── derivation, not authorship ───────────────────────────────────────────────

def test_coverage_is_derived_from_the_cards() -> None:
    """Every coverage row must trace back to a score on that model's own card."""
    cards = {m.model_id: m for m in _models()}
    for key, rows in _coverage().items():
        for row in rows:
            card = cards[row["model_id"]]
            evidence = [r["score"] for r in card.front["benchmarks"].get("evidence") or []
                        if r["benchmark_id"] == key]
            if row["attribution"] == "verified":
                assert row["score"] in evidence
            else:
                assert evidence == [] and card.scores[key] == row["score"]


def test_coverage_is_ordered_by_score() -> None:
    coverage = _coverage()
    rows = coverage["swe_bench_verified"]
    assert [r["score"] for r in rows] == sorted((r["score"] for r in rows), reverse=True)


def test_legacy_card_scores_are_marked_unverified() -> None:
    """Card scores carry no per-score source, so they must never read as evidence."""
    rows = _coverage()["gpqa_diamond"]
    legacy = [r for r in rows if r["source_kind"] is None]
    assert legacy and all(r["attribution"] == "unverified-legacy" for r in legacy)


# ── coverage from evidence records ───────────────────────────────────────────

_BUILD = Build(commit="abc", built_at="2026-09-15T00:00:00Z", as_of=date(2026, 9, 15))


def _card(model_id: str, name: str = "", scores: dict | None = None,
          evidence: tuple[dict, ...] = ()) -> Model:
    return Model(model_id, Path(f"models/{model_id}.md"), {
        "model_id": model_id, "display_name": name or model_id.split("/")[-1],
        "provider": "demo", "provider_display": "Demo Lab",
        "benchmarks": {"scores": scores or {}, "evidence": list(evidence),
                       "benchmark_as_of": "2026-01-01", "benchmark_source": "card sources"},
    }, "")


def _evidence(benchmark_id: str, score: float, **fields: str) -> dict:
    return {"benchmark_id": benchmark_id, "model_id_as_evaluated": "Demo Model",
            "score": score, "unit": "percent", "source_url": "https://src.example/run",
            "source_kind": "independent_evaluator", "evidence_date": "2026-09-01",
            "date_type": "evaluated", "verified_at": "2026-09-02",
            "benchmark_version": "v1", "configuration": "default", **fields}


def _page(benchmark_id: str, direction: str = "higher_is_better") -> Benchmark:
    return Benchmark(benchmark_id, Path(f"benchmarks/{benchmark_id}.md"),
                     {"id": benchmark_id, "name": benchmark_id,
                      "metric": {"direction": direction}}, "")


def _published(tmp_path: Path, models: list[Model],
               pages: list[Benchmark]) -> dict[str, list[dict]]:
    """`models_covered` as `/api/benchmarks/<id>.json` publishes it."""
    write(tmp_path, models, pages, Catalogue(as_of=date(2026, 9, 15)), _BUILD,
          parts=("benchmarks",))
    return {p.benchmark_id: json.loads(
        (tmp_path / "benchmarks" / f"{p.benchmark_id}.json").read_text(encoding="utf-8")
    )["models_covered"] for p in pages}


def test_a_benchmark_reported_only_in_evidence_records_has_coverage(tmp_path: Path) -> None:
    """A benchmark page listed no model although a card reported it in an evidence record."""
    card = _card("demo/astra", "Astra", evidence=(_evidence(
        "demo_bench", 41.4, model_id_as_evaluated="Astra",
        source_url="https://src.example/astra", source_kind="provider_self_report",
        evidence_date="2026-09-03", date_type="published", verified_at="2026-09-11",
        benchmark_version="DemoBench", configuration="launch table"),))
    rows = _published(tmp_path, [card], [_page("demo_bench")])["demo_bench"]
    assert rows == [{
        "model_id": "demo/astra", "display_name": "Astra",
        "provider": "demo", "provider_display": "Demo Lab",
        "score": 41.4, "unit": "percent",
        "as_of": "2026-09-03", "date_type": "published",
        "source": "https://src.example/astra", "source_kind": "provider_self_report",
        "model_id_as_evaluated": "Astra", "benchmark_version": "DemoBench",
        "configuration": "launch table", "verified_at": "2026-09-11",
        "attribution": "verified", "release_date": None,
    }]


def test_an_evidence_record_replaces_the_card_score_for_the_same_benchmark(
        tmp_path: Path) -> None:
    """The same measurement, checked. The ranking engine applies the same precedence."""
    cards = [_card("demo/checked", scores={"b": 51.2}, evidence=(_evidence("b", 40.81),)),
             _card("demo/legacy", scores={"b": 45.0})]
    rows = _published(tmp_path, cards, [_page("b")])["b"]
    assert [(r["model_id"], r["score"], r["as_of"], r.get("date_type"), r["source"],
             r["attribution"]) for r in rows] == [
        ("demo/legacy", 45.0, "2026-01-01", None, "card sources", "unverified-legacy"),
        ("demo/checked", 40.81, "2026-09-01", "evaluated", "https://src.example/run",
         "verified"),
    ]
    assert rows[0].keys() == rows[1].keys()


def test_each_evidence_record_is_its_own_row(tmp_path: Path) -> None:
    """A provider's claim and an independent run are both shown, each with its own date."""
    card = _card("demo/opus", scores={"b": 90.0}, evidence=(
        _evidence("b", 93.6, source_kind="provider_self_report",
                  evidence_date="2026-05-28", date_type="published"),
        _evidence("b", 92.02)))
    write(tmp_path, [card], [_page("b")], Catalogue(as_of=date(2026, 9, 15)), _BUILD,
          parts=("benchmarks", "catalogue"))
    rows = json.loads((tmp_path / "benchmarks/b.json").read_text())["models_covered"]
    assert [(r["score"], r["as_of"], r.get("date_type"), r.get("source_kind"),
             r["attribution"]) for r in rows] == [
        (93.6, "2026-05-28", "published", "provider_self_report", "verified"),
        (92.02, "2026-09-01", "evaluated", "independent_evaluator", "verified"),
    ]
    catalogue = json.loads((tmp_path / "catalogue.json").read_text())
    assert [(b["id"], b["models_covered"]) for b in catalogue["benchmarks"]] == [("b", 1)]


@pytest.mark.parametrize(("direction", "expected"), [
    ("lower_is_better", [3.0, 4.0, 5.0]),
    ("higher_is_better", [5.0, 4.0, 3.0]),
])
def test_coverage_is_ordered_best_first_by_metric_direction(
        tmp_path: Path, direction: str, expected: list[float]) -> None:
    cards = [_card("demo/a", scores={"wer": 5.0}),
             _card("demo/b", evidence=(_evidence("wer", 3.0),)),
             _card("demo/c", scores={"wer": 4.0})]
    rows = _published(tmp_path, cards, [_page("wer", direction)])["wer"]
    assert [r["score"] for r in rows] == expected


def test_every_card_evidence_record_reaches_its_benchmark_page(tmp_path: Path) -> None:
    """Thirteen benchmarks were reported only in evidence records and listed no model."""
    records = [(m.model_id, rec) for m in _models()
               for rec in (m.front.get("benchmarks") or {}).get("evidence") or []]
    ids = {str(rec["benchmark_id"]) for _, rec in records}
    published = _published(tmp_path, _models(),
                           [b for b in _benchmarks() if b.benchmark_id in ids])
    shown = {key: {(r["model_id"], r["score"], r["as_of"], r.get("source_kind"),
                    r["attribution"]) for r in rows}
             for key, rows in published.items()}
    missing = [(model_id, rec["benchmark_id"]) for model_id, rec in records
               if (model_id, rec["score"], str(rec["evidence_date"]), rec["source_kind"],
                   "verified") not in shown[str(rec["benchmark_id"])]]
    assert missing == []


def test_benchgraph_headline_counts_evidence_only_scores() -> None:
    card = _card("demo/astra", evidence=(_evidence("demo_bench", 41.4),))
    stats = builder.benchgraph_headline_stats([card], [_page("demo_bench")])
    assert stats == {"pages": 1, "scored_benchmarks": 1, "scored_models": 1, "scores": 1}


def _coverage_cells(html: str) -> list[list[str]]:
    table = html.split("<h2>Models reporting this benchmark</h2>", 1)[1].split("<h2>", 1)[0]
    return [[" ".join(re.sub(r"<[^>]+>", " ", cell).split())
             for cell in re.findall(r"<td[^>]*>(.*?)</td>", row, re.S)]
            for row in re.findall(r"<tr><td.*?</tr>", table, re.S)]


def test_benchmark_page_shows_each_score_with_its_date_and_attribution(
        tmp_path: Path) -> None:
    from pipeline.render import benchmark_page

    cards = [_card("demo/astra", "Astra", evidence=(_evidence(
                 "b", 41.4, model_id_as_evaluated="Astra (max)",
                 source_kind="provider_self_report", evidence_date="2026-09-03",
                 date_type="published"),)),
             _card("demo/old", "Old", scores={"b": 30.0})]
    page = _page("b")
    rows = _published(tmp_path, cards, [page])["b"]
    html = benchmark_page(page, _BUILD, Catalogue(as_of=date(2026, 9, 15)), rows)
    assert "No model card in ModelSpec reports this benchmark yet." not in html
    assert _coverage_cells(html) == [
        ["Astra evaluated as Astra (max)", "Demo Lab", "41.4%", "2026-09-03 published",
         "verified provider self report source"],
        ["Old", "Demo Lab", "30.0", "2026-01-01 card", "unverified-legacy"],
    ]


def _chart_row(model_id: str, score: float, *, benchmark_id: str = "b",
               release_date: str = "2026-01-01", source: str | None = None,
               source_kind: str = "independent_evaluator", version: str = "v1",
               configuration: str = "default") -> dict:
    return {
        "model_id": model_id,
        "display_name": model_id.rsplit("/", 1)[-1],
        "provider": "demo",
        "provider_display": "Demo Lab",
        "score": score,
        "unit": "percent",
        "as_of": "2026-09-01",
        "date_type": "evaluated",
        "source": source or f"https://src.example/{model_id.replace('/', '-')}/{benchmark_id}",
        "source_kind": source_kind,
        "model_id_as_evaluated": model_id,
        "benchmark_version": version,
        "configuration": configuration,
        "verified_at": "2026-09-02",
        "attribution": "verified",
        "release_date": release_date,
    }


def test_benchmark_chart_uses_only_sourced_evidence_and_splits_series() -> None:
    rows = [
        _chart_row(
            f"demo/model-{i}", float(i),
            release_date=f"2025-{(i % 12) + 1:02d}-01",
            source_kind=(
                "benchmark_author", "independent_evaluator", "provider_self_report"
            )[i % 3],
            version="v1" if i < 10 else "v2",
            configuration="default" if i % 2 else "tools",
        )
        for i in range(20)
    ]
    rows.append({**rows[0], "model_id": "demo/legacy", "attribution": "unverified-legacy"})

    chart = benchmark_chart(_page("b"), rows)

    assert chart.count('class="chart-point') == 20
    assert "demo/legacy" not in chart
    assert "benchmark author" in chart
    assert "independent evaluator" in chart
    assert "provider self report" in chart
    assert "source-benchmark-author" in chart
    assert "source-independent-evaluator" in chart
    assert "source-provider-self-report" in chart
    assert chart.count("<g>") == 4
    assert "Benchmark version: v1" in chart and "Benchmark version: v2" in chart
    assert "Evidence date: 2026-09-01 (evaluated)" in chart
    assert "Configuration: default" in chart
    assert '<a class="point-trigger" href="#p1"' in chart
    assert '<a href="https://src.example/demo-model-0/b"' in chart
    assert "Sources drawn:" in chart
    assert ">source 20</a>" in chart


def test_benchmark_chart_needs_twenty_plottable_points() -> None:
    assert benchmark_chart(_page("b"), [
        _chart_row(f"demo/model-{i}", float(i)) for i in range(19)
    ]) == ""


def test_benchmark_chart_refuses_to_plot_evidence_without_a_source() -> None:
    rows = [_chart_row(f"demo/model-{i}", float(i)) for i in range(20)]
    rows[7]["source"] = ""
    with pytest.raises(ValueError, match="source_url"):
        benchmark_chart(_page("b"), rows)


def test_benchmark_page_points_disclose_details_without_javascript() -> None:
    rows = [
        _chart_row(
            f"demo/model-{i}", float(i),
            release_date=f"2025-{(i % 12) + 1:02d}-01",
        )
        for i in range(20)
    ]

    html = benchmark_page(
        _page("b"), _BUILD, Catalogue(as_of=date(2026, 9, 15)), rows,
    )

    assert (
        'class="point-trigger" href="#p1"'
        in html
    )
    assert 'aria-describedby="p1"' in html
    detail = html.split('id="p1" class="point-detail"', 1)[1]
    detail = detail.split("</g></g>", 1)[0]
    assert "Evidence date: 2026-09-01 (evaluated)" in detail
    assert "Configuration: default" in detail
    assert 'href="https://src.example/' in detail
    assert ".point-trigger:focus-visible~.point-detail" in html
    assert ".point-pair:focus-within>.point-detail" in html


def test_model_strip_compacts_comparison_points() -> None:
    model = _card("demo/focus", evidence=(_evidence("b", 70.0),))
    rows = [_chart_row("demo/focus", 70.0)] + [
        _chart_row(f"demo/model-{i}", float(i % 100)) for i in range(2_000)
    ]

    strip = model_benchmark_strips(model, {"b": _page("b")}, {"b": rows})
    asset = benchmark_strip_asset(rows)

    assert len(strip.encode("utf-8")) < 5_000
    assert strip.count('class="point-trigger"') == 0
    assert "2001 reporting models" in strip
    assert 'data="/assets/benchmark-strips/b.svg"' in strip
    geometry = asset.split('<g id="points">', 1)[1].split(
        '</g><g id="point-interactions">', 1,
    )[0]
    assert geometry.count("M") == 2_001
    assert asset.count('class="point-trigger"') == 2_001
    assert asset.count("Evidence date: 2026-09-01 (evaluated)") == 2_001
    assert asset.count('aria-label="Open evidence source"') == 2_001
    assert "source-independent-evaluator" in asset


def test_model_page_writer_enforces_byte_budget(tmp_path: Path) -> None:
    destination = tmp_path / "index.html"

    with pytest.raises(ValueError, match="model page.*byte budget"):
        builder.write_model_page(destination, "x" * (builder.MODEL_PAGE_MAX_BYTES + 1))

    assert not destination.exists()


def test_model_strips_group_subsets_and_order_by_benchmark_coverage() -> None:
    model = _card("demo/focus", evidence=(
        _evidence("mmlu_anatomy", 70.0),
        _evidence("mmlu_marketing", 80.0),
        _evidence("multipl_e_rust", 60.0),
    ))
    pages = {
        "mmlu_anatomy": Benchmark(
            "mmlu_anatomy", Path("benchmarks/mmlu_anatomy.md"),
            {"id": "mmlu_anatomy", "name": "MMLU: Anatomy", "page_kind": "subset",
             "summary": "MMLU subject subset."}, ""),
        "mmlu_marketing": Benchmark(
            "mmlu_marketing", Path("benchmarks/mmlu_marketing.md"),
            {"id": "mmlu_marketing", "name": "MMLU: Marketing", "page_kind": "subset",
             "summary": "MMLU subject subset."}, ""),
        "multipl_e_rust": Benchmark(
            "multipl_e_rust", Path("benchmarks/multipl_e_rust.md"),
            {"id": "multipl_e_rust", "name": "MultiPL-E: Rust", "page_kind": "subset",
             "subcategory": "multilingual code generation",
             "summary": "The Rust subset of MultiPL-E: HumanEval and MBPP problems "
                        "translated into Rust and scored with pass@1."}, ""),
    }
    coverage = {
        "mmlu_anatomy": [_chart_row("demo/focus", 70.0, benchmark_id="mmlu_anatomy")]
                        + [_chart_row(f"demo/a-{i}", float(i), benchmark_id="mmlu_anatomy")
                           for i in range(9)],
        "mmlu_marketing": [_chart_row("demo/focus", 80.0, benchmark_id="mmlu_marketing")]
                          + [_chart_row(f"demo/m-{i}", float(i), benchmark_id="mmlu_marketing")
                             for i in range(4)],
        "multipl_e_rust": [_chart_row("demo/focus", 60.0, benchmark_id="multipl_e_rust")]
                          + [_chart_row(f"demo/r-{i}", float(i), benchmark_id="multipl_e_rust")
                             for i in range(6)],
    }

    strips = model_benchmark_strips(model, pages, coverage)

    assert strips.count('class="benchmark-strip"') == 3
    assert strips.count('class="strip-point focus ') == 3
    assert strips.count('<object class="benchmark-strip-asset"') == 3
    assert "MMLU subjects" in strips
    assert "MultiPL-E languages" in strips
    assert strips.index("MMLU: Anatomy") < strips.index("MMLU: Marketing")
    assert strips.index("MMLU: Marketing") < strips.index("MultiPL-E: Rust")
    assert 'href="/b/mmlu_anatomy/"' in strips
    assert 'class="strip-point focus ' in strips


def test_model_strips_group_production_multipl_e_metadata_as_languages() -> None:
    benchmark = next(
        bench for bench in _benchmarks() if bench.benchmark_id == "multipl_e_cpp"
    )
    model = _card("demo/focus", evidence=(
        _evidence(benchmark.benchmark_id, 70.0),
    ))
    coverage = {
        benchmark.benchmark_id: [
            _chart_row("demo/focus", 70.0, benchmark_id=benchmark.benchmark_id),
        ],
    }

    strips = model_benchmark_strips(
        model, {benchmark.benchmark_id: benchmark}, coverage,
    )

    assert "MultiPL-E languages" in strips


def test_model_strips_count_distinct_reporting_models_for_coverage() -> None:
    model = _card("demo/focus", evidence=(
        _evidence("low_coverage", 70.0),
        _evidence("high_coverage", 80.0),
    ))
    pages = {
        "low_coverage": _page("low_coverage"),
        "high_coverage": _page("high_coverage"),
    }
    coverage = {
        "low_coverage": [
            _chart_row("demo/focus", float(score), benchmark_id="low_coverage")
            for score in range(5)
        ] + [_chart_row("demo/other", 50.0, benchmark_id="low_coverage")],
        "high_coverage": [
            _chart_row("demo/focus", 80.0, benchmark_id="high_coverage"),
            _chart_row("demo/other", 75.0, benchmark_id="high_coverage"),
            _chart_row("demo/third", 70.0, benchmark_id="high_coverage"),
        ],
    }

    strips = model_benchmark_strips(model, pages, coverage)

    assert strips.index("high_coverage") < strips.index("low_coverage")


def test_model_without_evidence_has_no_benchmark_strip_frame() -> None:
    assert model_benchmark_strips(_card("demo/empty"), {}, {}) == ""


def test_model_page_passes_coverage_to_benchmark_strips() -> None:
    model = _card("demo/focus", evidence=(_evidence("b", 70.0),))
    benchmark = _page("b")
    coverage = {
        "b": [
            _chart_row("demo/focus", 70.0),
            _chart_row("demo/other", 65.0),
        ],
    }

    html = model_page(
        model,
        _BUILD,
        {"b": benchmark},
        Catalogue(as_of=date(2026, 9, 15)),
        evidence_coverage=coverage,
    )

    assert "Benchmark standing" in html
    assert 'href="/b/b/"' in html
    assert html.count('class="strip-point focus ') == 1
    assert html.count('data="/assets/benchmark-strips/b.svg"') == 1
    assert 'class="point-trigger"' not in html


def test_model_page_without_evidence_omits_benchmark_strip_frame() -> None:
    html = model_page(
        _card("demo/empty"),
        _BUILD,
        {"b": _page("b")},
        Catalogue(as_of=date(2026, 9, 15)),
        evidence_coverage={"b": [_chart_row("demo/other", 65.0)]},
    )

    assert "Benchmark standing" not in html
    assert 'class="strip-groups"' not in html


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
    assert stats["scored_models"] == len(
        {r["model_id"] for rows in _coverage().values() for r in rows})
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


# MODEL-219: dated template examples are another static build output.
@pytest.fixture
def use_case_template():
    from decision.templates import load_templates

    return load_templates()[0]


@pytest.fixture
def use_case_decision():
    return {
        "decision_id": "dec_fixture", "snapshot": "snap_fixture", "status": "answered",
        "answer": {
            "kind": "tied", "members": ["lab/strong", "lab/cheap"],
            "basis": "fixture evidence basis", "deterministic_order": ["lab/strong", "lab/cheap"],
            "tie_breakers": {"cheapest": "lab/cheap", "fastest": None,
                             "open_weights": "lab/strong", "most_independently_measured": None},
        },
        "bands": {
            "basis": "fixture evidence basis", "best": [
                {"model": "lab/strong", "score": 0.812345, "score_interval": [-0.12345, 1.23456],
                 "p_best": 0.56789, "cost_per_task": 0.4321,
                 "estimates": [{"dimension": "software_engineering", "value": 1.3579,
                                "interval": [-0.2468, 2.9753], "benchmarks": 7,
                                "direct_benchmarks": 3}]},
                {"model": "lab/cheap", "score": 0.75678, "score_interval": [0.1, 1.3],
                 "p_best": None, "cost_per_task": 0.01234, "estimates": []},
            ], "rest": [], "thin": [
                {"model": "lab/unknown", "score": 0.5, "score_interval": None,
                 "p_best": None, "cost_per_task": None, "estimates": []}],
        },
        "results": [{"model": "lab/strong"}], "warnings": ["fixture_warning"],
        "truncated": {"offerings": 4, "models": 2},
    }


def test_use_case_page_preserves_engine_values_and_registry_copy(use_case_template, use_case_decision):
    from pipeline.surface_lint import Page

    page = Page(builder.use_case_page(use_case_template, use_case_decision, date(2026, 9, 23)))
    for value in (use_case_template["name"], use_case_template["tradeoff"],
                  use_case_template["purpose"], use_case_template["teaches"],
                  *[row["reason"] for row in use_case_template["where"]],
                  *[row["reason"] for row in use_case_template["weights"].values()]):
        assert value in page.visible
    for value in ("lab/strong", "lab/cheap", "lab/unknown", "0.812345", "-0.12345",
                  "1.23456", "0.56789", "0.4321", "1.3579", "-0.2468", "2.9753"):
        assert value in page.visible
    assert "P(best)" in page.visible
    assert "null" in page.visible
    assert "fixture_warning" in page.visible


def test_use_case_tie_is_not_a_cost_recommendation(use_case_template, use_case_decision):
    from pipeline.surface_lint import Page

    page = Page(builder.use_case_page(use_case_template, use_case_decision, date(2026, 9, 23)))
    assert "Tied" in page.visible
    assert "fixture evidence basis" in page.visible
    assert "Cheapest tie-breaker: lab/cheap" in page.visible
    assert "Fastest tie-breaker: null" in page.visible
    assert "Open-weights tie-breaker: lab/strong" in page.visible
    assert "Most independently measured tie-breaker: null" in page.visible
    assert "undetermined" in page.visible
    assert "cheapest model is best" not in page.visible.lower()


@pytest.mark.parametrize("state", ["empty", "fully-undetermined"])
def test_use_case_without_answer_is_noindex_and_absent_from_sitemap(
    state, tmp_path, monkeypatch, use_case_template, use_case_decision,
):
    from pipeline.surface_lint import Page

    use_case_decision["answer"] = None
    if state == "empty":
        use_case_decision["results"] = []
        use_case_decision["bands"] = None
    else:
        use_case_decision["bands"]["thin"] += use_case_decision["bands"]["best"]
        use_case_decision["bands"]["best"] = []
    page = Page(builder.use_case_page(use_case_template, use_case_decision, date(2026, 9, 23)))
    assert "No recommendation" in page.visible
    assert "noindex" in page.meta["robots"]
    catalogue = {"categories": [{"id": "coding", "name": "Coding", "kind": "use"}],
                 "templates": [use_case_template]}
    monkeypatch.setattr(builder, "use_case_decisions",
                        lambda root: (catalogue, [use_case_decision], date(2026, 9, 23)))
    result = builder.write_use_case_pages(tmp_path, REPO_ROOT)
    assert result["sitemap_paths"] == ["/use-cases/"]
    assert (tmp_path / "use-cases/coding/coding-best/index.html").is_file()


def test_use_case_neutrality_and_access(use_case_template, use_case_decision):
    from pipeline.surface_lint import Page

    raw = builder.use_case_page(use_case_template, use_case_decision, date(2026, 9, 23))
    page = Page(raw)
    assert "/legal/neutrality/" in page.links
    assert "/decide/?template=coding-best" in page.links
    assert "Human lookup is free" in page.visible
    assert "CLI, API, and MCP access requires a key" in page.visible
    for forbidden in ("artificial analysis", "zapier", "openrouter", "litellm", "portkey",
                      "not diamond", "routellm", "affiliate", "paid placement", "keyless"):
        assert forbidden not in raw.lower()


def test_use_case_has_entity_lead_and_visible_dated_jsonld(use_case_template, use_case_decision):
    from pipeline import entity, surface_lint

    raw = builder.use_case_page(use_case_template, use_case_decision, date(2026, 9, 23))
    page = surface_lint.Page(raw)
    assert page.first_paragraph.startswith(entity.ONE_SENTENCE)
    assert "as of 2026-09-23, from the public data image" in page.visible
    assert not surface_lint.structured_data({"use-cases/coding/coding-best/index.html": raw})
    nodes = [node for block in page.ld for node in surface_lint.objects(json.loads(block))]
    assert any(node.get("@type") == "Article" and node["dateModified"] == "2026-09-23"
               for node in nodes)


@pytest.mark.parametrize("injection", ["instructions for AI", "AI assistants should"])
def test_use_case_surface_lint_rejects_ai_instructions(injection):
    from pipeline import surface_lint

    findings = surface_lint.lexicon(
        {"use-cases/coding/coding-best/index.html": f"<p>{injection}</p>"}, {}, {},
    )
    assert any(finding.check == "lexicon.ai-instructions" for finding in findings)


def test_use_case_surface_lint_covers_noindex_pages():
    from pipeline import surface_lint

    findings = surface_lint.presence({
        "use-cases/coding/coding-best/index.html": '<meta name="robots" content="noindex"><p>Wrong lead</p>',
    })
    assert any(finding.surface == "use-cases/coding/coding-best/index.html"
               and finding.check == "presence.lead" for finding in findings)


def test_use_case_image_date_never_falls_back_to_build_clock(tmp_path):
    with pytest.raises((ValueError, FileNotFoundError)):
        builder.use_case_image_date(tmp_path)
    report = tmp_path / "benchmarks/_census/eligibility/current-report.json"
    report.parent.mkdir(parents=True)
    report.write_text('{"as_of":"2026-09-23"}')
    assert builder.use_case_image_date(tmp_path) == date(2026, 9, 23)
    (tmp_path / "data-image.json").write_text('{"as_of":"2026-01-17"}')
    assert builder.use_case_image_date(tmp_path) == date(2026, 1, 17)


def test_use_case_pages_are_stable_and_index_groups_registry_kinds(
    tmp_path, monkeypatch, use_case_template, use_case_decision,
):
    from pipeline import entity

    other = dict(use_case_template, id="regulated-fixture", category="regulated", name="Fixture regulated")
    catalogue = {"categories": [{"id": "coding", "name": "Coding", "kind": "use"},
                                {"id": "regulated", "name": "Regulated data", "kind": "constraint"}],
                 "templates": [use_case_template, other]}
    monkeypatch.setattr(builder, "use_case_decisions", lambda root: (
        catalogue, [use_case_decision, use_case_decision], date(2026, 9, 23)))
    first = builder.write_use_case_pages(tmp_path / "first", REPO_ROOT)
    second = builder.write_use_case_pages(tmp_path / "second", REPO_ROOT)
    assert first == second
    for page in (tmp_path / "first").rglob("*.html"):
        assert page.read_bytes() == (tmp_path / "second" / page.relative_to(tmp_path / "first")).read_bytes()
    index = (tmp_path / "first/use-cases/index.html").read_text()
    assert 'data-kind="use"' in index and 'data-kind="constraint"' in index
    assert entity.ONE_SENTENCE in index
    assert "/use-cases/coding/coding-best/" in index
    assert "/use-cases/regulated/regulated-fixture/" in index
    assert first["sitemap_dates"] == {path: "2026-09-23" for path in first["sitemap_paths"]}


def test_use_case_complete_and_bounded_contracts_stay_pinned():
    from decision.contract import BOUNDED_VERSION, CONTRACT_VERSION

    assert CONTRACT_VERSION == "2.18"
    assert BOUNDED_VERSION == "1.5"


def test_use_case_decisions_use_public_image_and_the_shared_engine(monkeypatch, tmp_path):
    import socket

    from decision import engine, registry, snapshot
    from decision.contract import parse_spec

    monkeypatch.setenv("MODELSPEC_DATA_DIR", str(tmp_path / "private-must-not-be-read"))
    calls = []
    build_snapshot = snapshot.build_from_repo
    loaded = []
    load_snapshot = snapshot.load_built_snapshot

    def collect(root, **kwargs):
        calls.append((root, kwargs["as_of"]))
        return build_snapshot(root, **kwargs)

    def load(built, **kwargs):
        result = load_snapshot(built, **kwargs)
        loaded.append(result)
        return result

    def forbid_network(*args, **kwargs):
        pytest.fail("Static examples must not access the network")

    monkeypatch.setattr(snapshot, "build_from_repo", collect)
    monkeypatch.setattr(snapshot, "load_built_snapshot", load)
    monkeypatch.setattr(socket, "create_connection", forbid_network)
    saved_root = registry.REPO_ROOT
    private_root = tmp_path / "poison-private-default"
    registry.use_root(private_root)
    try:
        catalogue, decisions, as_of = builder.use_case_decisions(REPO_ROOT)
        assert registry.REPO_ROOT == private_root
    finally:
        registry.use_root(saved_root)
    expected_date = builder.use_case_image_date(REPO_ROOT)
    assert calls == [(REPO_ROOT, expected_date)]
    assert len(decisions) == len(catalogue["templates"])
    public_registry = registry.load(REPO_ROOT / "registry", repo_root=REPO_ROOT)
    template = catalogue["templates"][0]
    expected = engine.decide(parse_spec(template["spec"], facets=public_registry.facet),
                             loaded[0], facets=public_registry.facet).model_dump(mode="json")
    assert decisions[0] == expected
    assert as_of == expected_date
