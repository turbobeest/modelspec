"""MODEL-508: Epoch AI's CC BY 4.0 credit travels with its data."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import pytest
import yaml

from decision.credit import EPOCH_CREDIT, EPOCH_LICENCE_URL, EPOCH_SOURCE_URL, credit_for, is_epoch_url
from pipeline import comparison_pages, ranking, render
from pipeline.export import Build, models_by_benchmark, write
from pipeline.load import Benchmark, Catalogue, Model
from scripts import refresh_leaderboards as refresh
from tests.test_leaderboard_refresh import _card

pytestmark = pytest.mark.usefixtures("terms_register_present")

EPOCH_PAGE = "https://epoch.ai/benchmarks/gpqa-diamond"
OTHER_PAGE = "https://example.test/gpqa"


@pytest.mark.parametrize("url", [
    "https://epoch.ai/benchmarks/gpqa-diamond", "https://epoch.ai/frontiermath",
    "https://data.epoch.ai/benchmarks/x", "HTTPS://EPOCH.AI/benchmarks/swe-bench-verified",
])
def test_epoch_pages_are_credited(url: str) -> None:
    assert is_epoch_url(url)
    assert credit_for(url) == "Epoch AI data, CC BY 4.0."


@pytest.mark.parametrize("url", [
    # The archive also holds the *_external files, which keep their own licences.
    "https://epoch.ai/data/benchmark_data.zip",
    "https://epoch.ai.example.test/benchmarks/x", "https://notepoch.ai/x",
    "https://example.test/?u=https://epoch.ai/x", "", None, 7,
])
def test_other_sources_are_not_credited(url: object) -> None:
    assert not is_epoch_url(url)
    assert credit_for(url) is None


def _board_run(monkeypatch, tmp_path: Path, url: str) -> dict:
    root, cache = tmp_path / "repo", tmp_path / "copies"
    for folder in ("models/lab", "registry", "verification"):
        (root / folder).mkdir(parents=True)
    (root / "registry" / "sources.yaml").write_text(
        f"""schema_version: 1
sources:
- id: fixture-source
  url: {url}
  fetch: http
  normaliser: text-default
  cited_regions:
  - id: rows
    locator: {{kind: page, value: ''}}
""", encoding="utf-8")
    card = root / "models" / "lab" / "new.md"
    card.write_text("---\nmodel_id: lab/new\ndisplay_name: New Model\nversion: new-model\n"
                    "benchmarks:\n  scores: {}\n  evidence: []\n---\n", encoding="utf-8")
    (root / "models" / "lab" / "template.md").write_text(
        _card("2026-09-25").replace("lab/model", "lab/template").replace(
            "Stable Model", "Template Model").replace("prose\n", "").replace(
            "https://example.test/leaderboard.json", url), encoding="utf-8")
    store = refresh.CopyStore(cache)
    projection = refresh.readers.document(
        [{"model": "New Model", "score": "81.5%"}], url=url,
        page_ref="sha256:" + "b" * 64, read_date="2026-09-26", note="fixture")
    board = refresh._reading_from_projection(
        key="fixture", source_id="fixture-source", benchmarks=("fixture_benchmark",),
        source_url=url, projected=projection, observed_at="2026-09-26",
        value_field="score", store=store)
    monkeypatch.setattr(refresh, "collect_readings", lambda *_a, **_k: ([board], []))
    report = refresh.run(observed_at="2026-09-26", dry_run=False, root=root, source_cache=cache,
                         model_ids=("lab/new",), add_missing=True)
    assert report.added == 1 and report.quarantined == []
    front = yaml.safe_load(card.read_text(encoding="utf-8").split("---", 2)[1])
    return front["benchmarks"]["evidence"][0]


def test_the_add_path_writes_the_epoch_credit_for_an_epoch_board(monkeypatch, tmp_path: Path) -> None:
    row = _board_run(monkeypatch, tmp_path, EPOCH_PAGE)
    assert row["limitations"] == EPOCH_CREDIT


def test_the_add_path_leaves_other_boards_without_a_credit(monkeypatch, tmp_path: Path) -> None:
    row = _board_run(monkeypatch, tmp_path, "https://example.test/leaderboard.json")
    assert row["limitations"] == ""


def _model(model_id: str, url: str, name: str = "One") -> Model:
    return Model(model_id, Path(f"/x/{model_id}.md"), {
        "model_id": model_id, "display_name": name, "provider": "prov", "provider_display": "Prov",
        "family": "f", "status": "active", "model_type": "llm-chat",
        "release_date": "2026-01-01",
        "benchmarks": {"scores": {}, "evidence": [{
            "benchmark_id": "gpqa_diamond", "model_id_as_evaluated": name, "score": 50.0,
            "unit": "percent", "source_url": url, "source_kind": "independent_evaluator",
            "evidence_date": "2026-02-01", "date_type": "evaluated", "verified_at": "2026-02-02",
        }]},
    }, "body")


def _bench() -> Benchmark:
    return Benchmark("gpqa_diamond", Path("/x/gpqa_diamond.md"),
                     {"id": "gpqa_diamond", "name": "GPQA Diamond", "category": "reasoning"}, "")


def _page_inputs(url: str):
    model, bench = _model("prov/one", url), _bench()
    catalogue = Catalogue(as_of=date(2026, 9, 1))
    build = Build(commit="abc123def456", built_at="2026-09-10T00:00:00+00:00", as_of=catalogue.as_of)
    return model, bench, catalogue, build, models_by_benchmark([model], [bench])


def _has_credit(html: str) -> bool:
    return ("Epoch AI data" in html and EPOCH_LICENCE_URL in html and EPOCH_SOURCE_URL in html
            and "CC BY 4.0" in html)


def test_the_model_page_credits_epoch_with_licence_and_source_links() -> None:
    model, bench, catalogue, build, coverage = _page_inputs(EPOCH_PAGE)
    page = render.model_page(model, build, {"gpqa_diamond": bench}, catalogue,
                             evidence_coverage=coverage)
    assert _has_credit(page)


def test_the_model_page_for_another_source_carries_no_credit() -> None:
    model, bench, catalogue, build, coverage = _page_inputs(OTHER_PAGE)
    page = render.model_page(model, build, {"gpqa_diamond": bench}, catalogue,
                             evidence_coverage=coverage)
    assert "Epoch AI data" not in page and EPOCH_LICENCE_URL not in page


def test_the_benchmark_page_credits_epoch_and_other_boards_do_not() -> None:
    model, bench, catalogue, build, coverage = _page_inputs(EPOCH_PAGE)
    assert _has_credit(render.benchmark_page(bench, build, catalogue, coverage["gpqa_diamond"]))
    model, bench, catalogue, build, coverage = _page_inputs(OTHER_PAGE)
    assert "Epoch AI data" not in render.benchmark_page(bench, build, catalogue,
                                                        coverage["gpqa_diamond"])


def test_the_coverage_export_credits_only_epoch_rows(tmp_path: Path) -> None:
    epoch, other = _model("prov/one", EPOCH_PAGE), _model("prov/two", OTHER_PAGE, "Two")
    rows = models_by_benchmark([epoch, other], [_bench()])["gpqa_diamond"]
    by_model = {row["model_id"]: row for row in rows}
    assert by_model["prov/one"]["credit"] == EPOCH_CREDIT
    assert "credit" not in by_model["prov/two"]
    out = tmp_path / "api"
    catalogue = Catalogue(as_of=date(2026, 9, 1))
    write(out, [epoch, other], [_bench()], catalogue,
          Build(commit="abc", built_at="2026-09-10T00:00:00+00:00", as_of=catalogue.as_of))
    covered = json.loads((out / "benchmarks/gpqa_diamond.json").read_text())["models_covered"]
    assert sorted(row["model_id"] for row in covered if row.get("credit") == EPOCH_CREDIT) == ["prov/one"]


def test_the_strip_asset_describes_its_epoch_credit() -> None:
    rows = models_by_benchmark([_model("prov/one", EPOCH_PAGE)], [_bench()])["gpqa_diamond"]
    asset = render.benchmark_strip_asset(rows)
    assert EPOCH_CREDIT in asset and "<desc>" in asset
    rows = models_by_benchmark([_model("prov/one", OTHER_PAGE)], [_bench()])["gpqa_diamond"]
    assert "Epoch AI data" not in render.benchmark_strip_asset(rows)


def test_the_compare_page_evidence_credits_epoch() -> None:
    model = {"evidence": [{"benchmark": "gpqa_diamond", "version": None, "value": 50, "unit": "percent",
                           "interval": None, "date": "2026-02-01", "source_ids": ["s"]}]}
    assert _has_credit(comparison_pages._evidence(model, {"s": EPOCH_PAGE}))
    assert "Epoch AI data" not in comparison_pages._evidence(model, {"s": OTHER_PAGE})


def test_the_rank_exports_list_the_credit_when_a_score_came_from_epoch() -> None:
    assert ranking.credit_record() == {
        "credit": EPOCH_CREDIT, "licence_url": EPOCH_LICENCE_URL, "source_url": EPOCH_SOURCE_URL}


def test_a_decision_credits_an_epoch_source_in_its_source_title() -> None:
    from types import SimpleNamespace

    from decision import explain

    urls = {"epoch": EPOCH_PAGE, "other": OTHER_PAGE}
    records = {"r1": {"kind": "evidence", "verification": {"date": "2026-09-20"},
                      "sources": [{"source_id": "epoch"}, {"source_id": "other"}]}}
    snapshot = SimpleNamespace(source_url=urls.__getitem__, record=records.__getitem__)
    decision = SimpleNamespace(
        number_origins=[SimpleNamespace(records=["r1"])], top=[])
    cited = {source.id: source for source in explain.cited_sources(decision, snapshot)}
    assert cited["epoch"].title == f"{EPOCH_CREDIT} Licence: {EPOCH_LICENCE_URL} Source: {EPOCH_SOURCE_URL}"
    assert cited["other"].title is None


def test_a_named_comparison_titles_only_its_epoch_source() -> None:
    from types import SimpleNamespace

    from decision import contract
    from decision.model_comparison import update_sources

    urls = {"epoch": EPOCH_PAGE, "other": OTHER_PAGE}
    row = {"facts": [{"source_ids": ["other"]}], "offerings": [],
           "evidence": [{"source_ids": ["epoch"]}]}
    body = {"models": [row], "sources": []}
    update_sources(body, SimpleNamespace(source_url=urls.__getitem__))
    assert body["sources"] == [
        {"id": "epoch", "url": EPOCH_PAGE,
         "title": f"{EPOCH_CREDIT} Licence: {EPOCH_LICENCE_URL} Source: {EPOCH_SOURCE_URL}"},
        {"id": "other", "url": OTHER_PAGE},
    ]
    assert contract.MODEL_COMPARISON_VERSION == "1.3"
    parsed = [contract.ComparisonSource.model_validate(s) for s in body["sources"]]
    assert "title" not in parsed[1].model_dump(mode="json")
    assert parsed[0].model_dump(mode="json")["title"].startswith(EPOCH_CREDIT)
