"""The pipeline's promises, held to.

These guard the claims the sites make in public: that only verified benchmarks
are presented as current, that coverage tables are derived rather than authored,
and that a build cannot publish an active set it cannot justify.
"""

from __future__ import annotations

import functools
import json
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
