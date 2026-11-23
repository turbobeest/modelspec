"""MODEL-536 and MODEL-537: internal judge-blinding and baseline fields."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import pytest
from pydantic import ValidationError

from decision.excluded import REMOVED_HOSTS
from pipeline.export import Build, write
from pipeline.load import Benchmark, Catalogue, Model
from schema.benchmark import BenchmarkCard
from schema.evidence import BenchmarkEvidence
from scripts.coverage_report import claim_field_counts, generate_report

URL = "https://example.test/method"
BASE = {"id": "example", "name": "Example", "category": "coding"}
READING = {
    "benchmark_id": "example", "model_id_as_evaluated": "m", "score": 1.0, "unit": "%",
    "source_url": URL, "source_kind": "benchmark_author", "evidence_date": "2026-01-01",
    "date_type": "published", "verified_at": "2026-01-02",
}


def page(**extra):
    return BenchmarkCard(**BASE, **extra)


def test_absent_fields_are_valid():
    card = page()
    assert (card.scoring, card.judge_blind, card.scoring_source) == (None, None, "")
    assert BenchmarkEvidence(**READING).baseline is None
    assert "baseline" not in BenchmarkEvidence(**READING).model_dump()


@pytest.mark.parametrize("scoring", ["exact", "programmatic"])
def test_unjudged_scoring_needs_source_and_no_blinding(scoring):
    assert page(scoring=scoring, scoring_source=URL).scoring == scoring
    with pytest.raises(ValidationError):
        page(scoring=scoring)
    with pytest.raises(ValidationError):
        page(scoring=scoring, scoring_source=URL, judge_blind="blind")


@pytest.mark.parametrize("scoring", ["llm_judge", "human_judge", "mixed"])
@pytest.mark.parametrize("blind", ["blind", "not_blind", "not_stated"])
def test_judged_scoring_records_blinding(scoring, blind):
    assert page(scoring=scoring, judge_blind=blind, scoring_source=URL).judge_blind == blind
    with pytest.raises(ValidationError):
        page(scoring=scoring, scoring_source=URL)


def test_page_methodology_derivation_claims_no_source():
    card = page(scoring="exact", scoring_derivation="page_methodology")
    assert card.scoring_source == ""
    with pytest.raises(ValidationError):
        page(scoring="exact", scoring_derivation="page_methodology", scoring_source=URL)
    with pytest.raises(ValidationError):
        page(scoring_derivation="page_methodology")
    with pytest.raises(ValidationError):
        page(scoring="exact", scoring_derivation="guess")


def test_bad_scoring_values_and_orphans_are_refused():
    for bad in (dict(scoring="vibes", scoring_source=URL),
                dict(scoring="llm_judge", judge_blind="maybe", scoring_source=URL),
                dict(judge_blind="blind"), dict(scoring_source=URL),
                dict(scoring="exact", scoring_source="not a url")):
        with pytest.raises(ValidationError):
            page(**bad)


@pytest.mark.parametrize("kind", ["prior_version", "named_model"])
def test_model_baselines_need_label_and_source(kind):
    ok = BenchmarkEvidence(**READING, baseline={"kind": kind, "label": "m-1", "source": URL})
    assert ok.baseline.kind == kind
    for bad in ({"kind": kind, "source": URL}, {"kind": kind, "label": "m-1"}):
        with pytest.raises(ValidationError):
            BenchmarkEvidence(**READING, baseline=bad)


@pytest.mark.parametrize("kind", ["human", "random"])
def test_human_and_random_baselines_need_source(kind):
    assert BenchmarkEvidence(**READING, baseline={"kind": kind, "source": URL}).baseline.label == ""
    with pytest.raises(ValidationError):
        BenchmarkEvidence(**READING, baseline={"kind": kind})


def test_none_stated_is_a_real_value_without_source():
    assert BenchmarkEvidence(**READING, baseline={"kind": "none_stated"}).baseline.kind == "none_stated"
    with pytest.raises(ValidationError):
        BenchmarkEvidence(**READING, baseline={"kind": "none_stated", "source": URL})
    with pytest.raises(ValidationError):
        BenchmarkEvidence(**READING, baseline={"kind": "guess", "source": URL})


def test_exports_leave_both_fields_out(tmp_path: Path):
    front = {**BASE, "scoring": "llm_judge", "judge_blind": "blind", "scoring_source": URL, "scoring_derivation": "page_methodology"}
    bench = Benchmark("example", tmp_path / "example.md", front, "")
    card = {"model_id": "m", "provider": "p", "benchmarks": {"evidence": [
        {**READING, "baseline": {"kind": "none_stated"}}]}}
    model = Model("m", tmp_path / "p" / "m.md", card, "")
    catalogue = Catalogue(as_of=date(2026, 9, 1))
    build = Build(commit="abc123def456", built_at="2026-09-10T00:00:00+00:00", as_of=catalogue.as_of)
    out = tmp_path / "api"
    write(out, [model], [bench], catalogue, build)
    text = "".join(p.read_text(encoding="utf-8") for p in out.rglob("*.json"))
    for key in ("scoring", "judge_blind", "scoring_derivation", "baseline"):
        assert f'"{key}"' not in text
    assert json.loads((out / "benchmarks/example.json").read_text())["page"]["id"] == "example"
    assert "baseline" in model.front["benchmarks"]["evidence"][0]


def test_coverage_counts_are_counts_only():
    fronts = [
        {"scoring": "exact"}, {"scoring": "llm_judge", "judge_blind": "blind"},
        {"scoring": "mixed", "judge_blind": "not_stated"}, {},
    ]
    assert claim_field_counts(fronts) == {
        "pages": 4, "scoring_set": 3, "judged": 2, "judge_blind_known": 1}
    report = generate_report([], fronts)
    assert "Benchmark pages with scoring set | 3 of 4" in report
    assert "Judged pages with judge_blind known | 1 of 2" in report


def test_cite_only_reading_with_baseline_keeps_its_citation(tmp_path: Path):
    cited = {**READING, "source_url": "https://www.anthropic.com/news/x",
             "baseline": {"kind": "none_stated"}}
    card = {"model_id": "m", "provider": "p", "benchmarks": {"evidence": [cited]}}
    model = Model("m", tmp_path / "p" / "m.md", card, "")
    assert model.cited_evidence
    catalogue = Catalogue(as_of=date(2026, 9, 1))
    build = Build(commit="abc123def456", built_at="2026-09-10T00:00:00+00:00", as_of=catalogue.as_of)
    write(tmp_path / "api", [model], [], catalogue, build)
    row = json.loads((tmp_path / "api/models/m.json").read_text())["card"]["benchmarks"]["evidence"][0]
    assert row["citation"]["status"] == "cited"
    assert "baseline" not in row


def test_baseline_never_enters_a_snapshot(tmp_path: Path):
    from tests import test_decision_snapshot as t
    from tests.snapshot_records import evidence

    plain = t.build(tmp_path, "plain.json.gz")
    row = evidence("lab/alpha", "swe_bench_pro", 55.0)
    row["baseline"] = {"kind": "named_model", "label": "other", "source": URL}
    base_rows = t.inputs().evidence
    with_baseline = t.build(tmp_path, "with.json.gz", evidence=[row, *base_rows[1:]])
    import gzip
    a = json.loads(gzip.decompress(plain.read_bytes()))
    b = json.loads(gzip.decompress(with_baseline.read_bytes()))
    assert b["content"]["record_table"] == a["content"]["record_table"]
    assert b["content_hash"] == a["content_hash"]
    assert "baseline" not in json.dumps(b)


@pytest.mark.parametrize("host", list(REMOVED_HOSTS))
def test_excluded_sources_are_refused(host):
    url = f"https://{host}/x"
    with pytest.raises(ValidationError):
        page(scoring="exact", scoring_source=url)
    with pytest.raises(ValidationError):
        BenchmarkEvidence(**READING, baseline={"kind": "human", "source": url})


def test_baseline_count_skips_none_stated():
    from scripts.coverage_report import baseline_count
    from types import SimpleNamespace as NS

    def card(*kinds):
        ev = [BenchmarkEvidence(**READING, baseline={"kind": k, "source": URL} if k != "none_stated"
                                else {"kind": k}) for k in kinds]
        return ("f", NS(benchmarks=NS(evidence=ev)), None)

    assert baseline_count([card("human", "none_stated"), card(), ("f", None, "err")]) == 1
