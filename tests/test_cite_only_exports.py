"""Cite-only assurance survives the file exports and legacy rank endpoint."""

from datetime import date
import json
from pathlib import Path

import yaml
import pytest

from api.worker.src import rank_service
from pipeline import export, ranking
from pipeline.load import Benchmark, Catalogue, Disposition, load_models
from schema.card import ModelCard
from schema.graph import CollectingSink
from tests.snapshot_records import fact


URL = "https://docs.x.ai/docs/models"
HASH = "sha256:" + "1" * 64
FETCHED = "2026-10-19T12:00:00+00:00"
BUILD = export.Build("b" * 40, FETCHED, date(2026, 10, 19))


def card_tree(root: Path, url: str = URL) -> tuple[dict, Path]:
    record = fact("model", "lab/cited", "model.context_window", 128000)
    record["sources"][0].update(snapshot_ref=HASH, retrieved_at=FETCHED)
    front = {
        "model_id": "lab/cited", "display_name": "Cited model", "provider": "lab",
        "model_type": "llm-chat", "facts": [record],
        "modalities": {"text": {"context_window": 128000}},
        "benchmarks": {"scores": {"humaneval": 90, "swe_bench_verified": 70,
                                    "live_code_bench": 75, "scicode": 65}},
    }
    path = root / "models/lab/cited.md"
    path.parent.mkdir(parents=True)
    path.write_text("---\n" + yaml.safe_dump(front) + "---\nSynthetic fixture.\n")
    registry = root / "registry"
    registry.mkdir()
    (registry / "sources.yaml").write_text(yaml.safe_dump({
        "schema_version": 1, "sources": [{"id": "src-lab-docs", "url": url}],
    }))
    return front, path


def test_model_export_carries_citation_url_hash_and_fetch_date(tmp_path):
    original, path = card_tree(tmp_path)
    models = load_models(tmp_path)
    out = tmp_path / "export"
    export.write(out, models, [], Catalogue(BUILD.as_of), BUILD)
    result = json.loads((out / "models/lab/cited.json").read_text())
    published = result["card"]["facts"][0]
    assert published["verification"] is None
    assert published["state"] == "known"
    assert published["value"] == 128000
    assert published["citation"] == {
        "status": "cited", "sources": [{
            "source_id": "src-lab-docs", "url": URL, "snapshot_ref": HASH,
            "retrieved_at": FETCHED,
        }],
    }
    assert result["cited_facts"] == [published]
    assert result["build"]["export_schema_version"] == "3.0"
    assert yaml.safe_load(path.read_text().split("---")[1]) == original


def test_cited_fact_notice_survives_rank_export_and_worker(tmp_path):
    _, path = card_tree(tmp_path)
    models = load_models(tmp_path)
    out = tmp_path / "rank"
    ranking.write_export(out, [ModelCard.from_yaml_file(path)], CollectingSink(),
                         BUILD.to_json(), cited_facts={models[0].model_id: models[0].cited_facts})
    payload = json.loads((out / "candidates.json").read_text())
    status, response = rank_service.rank({"use_case": "coding"}, payload, None,
                                         "b" * 40, "https://modelspec.test")
    assert status == 200
    assert response["result"]
    result = response["result"][0]
    assert "cite_only_not_machine_verified" in result["warnings"]
    assert result["cited_facts"][0]["citation"]["sources"][0]["snapshot_ref"] == HASH
    assert result["context_window"] == 128000


def test_cited_benchmark_is_not_counted_as_verified(tmp_path):
    front, path = card_tree(tmp_path)
    front["benchmarks"]["evidence"] = [{
        "benchmark_id": "humaneval", "model_id_as_evaluated": "Cited model",
        "score": 90, "unit": "percent", "source_url": URL,
        "source_kind": "provider_self_report", "evidence_date": "2026-10-19",
        "date_type": "published", "verified_at": "2026-10-19",
    }]
    path.write_text("---\n" + yaml.safe_dump(front) + "---\nSynthetic fixture.\n")
    candidate = ranking.build_candidates([ModelCard.from_yaml_file(path)], CollectingSink())[0]
    assert candidate.benchmark_scores["humaneval"] == 90
    assert "humaneval" not in candidate.verified_benchmarks
    assert candidate.cited_benchmarks["humaneval"]["url"] == URL
    result = ranking.score(candidate, {"benchmark_weights": {"humaneval": 1}})
    assert result["verified_contributions"] == 0
    assert result["verified_benchmark_coverage"] == 0
    assert "cite_only_not_machine_verified" in result["warnings"]
    covered = export.models_by_benchmark(load_models(tmp_path), [])["humaneval"][0]
    assert covered["attribution"] != "verified"
    assert covered["citation"]["status"] == "cited"


def test_ordinary_host_export_keeps_existing_fact_verification(tmp_path):
    original, _ = card_tree(tmp_path, "https://lab.example/models")
    models = load_models(tmp_path)
    out = tmp_path / "export"
    export.write(out, models, [], Catalogue(BUILD.as_of), BUILD)
    result = json.loads((out / "models/lab/cited.json").read_text())
    assert result["card"] == original
    assert not result.get("cited_facts")


@pytest.mark.parametrize("with_ids", [True, False])
def test_citation_export_preserves_distinct_facts_with_the_same_facet(tmp_path, with_ids):
    front, path = card_tree(tmp_path)
    earlier = front["facts"][0]
    earlier["id"] += "-earlier"
    current = fact("model", "lab/cited", "model.context_window", 256000, source="ordinary")
    front["facts"].append(current)
    if not with_ids:
        earlier.pop("id")
        current.pop("id")
    path.write_text("---\n" + yaml.safe_dump(front) + "---\nSynthetic fixture.\n")
    registry = tmp_path / "registry/sources.yaml"
    sources = yaml.safe_load(registry.read_text())
    sources["sources"].append({"id": "ordinary", "url": "https://lab.example/models"})
    registry.write_text(yaml.safe_dump(sources))
    out = tmp_path / "export"
    export.write(out, load_models(tmp_path), [], Catalogue(BUILD.as_of), BUILD)
    rows = json.loads((out / "models/lab/cited.json").read_text())["card"]["facts"]
    assert [row.get("id") for row in rows] == [earlier.get("id"), current.get("id")]
    assert rows[0]["citation"]["status"] == "cited"
    assert rows[1] == current


def test_benchmark_catalogue_export_separates_citations_from_verified_results(tmp_path):
    cited = {"model_id": "lab/cited", "score": 90, "source_url": URL}
    verified = {"model_id": "lab/ordinary", "score": 80, "source_url": "https://lab.example/results"}
    bench = Benchmark("demo", Path("benchmarks/demo.md"), {}, "")
    catalogue = Catalogue(BUILD.as_of, {"demo": Disposition("active", "demo", results=(cited, verified))})
    export.write(tmp_path, [], [bench], catalogue, BUILD)
    disposition = json.loads((tmp_path / "benchmarks/demo.json").read_text())["disposition"]
    assert disposition["verified_results"] == [verified]
    assert disposition["cited_results"] == [{**cited, "citation": {"status": "cited", "url": URL}}]


def test_standalone_rank_report_preserves_fact_citation(tmp_path, monkeypatch, capsys):
    card_tree(tmp_path)
    monkeypatch.setattr(ranking, "__file__", str(tmp_path / "pipeline/ranking.py"))
    monkeypatch.setattr("sys.argv", ["ranking", "coding", "--json"])
    ranking.main()
    report = json.loads(capsys.readouterr().out)
    assert "cite_only_not_machine_verified" in report["ranked"][0]["warnings"]
    assert report["ranked"][0]["cited_facts"][0]["citation"]["sources"][0]["snapshot_ref"] == HASH
    monkeypatch.setattr("sys.argv", ["ranking", "coding"])
    ranking.main()
    assert "Cited, not machine-verified" in capsys.readouterr().out


@pytest.mark.parametrize("source,cited", [(URL, True), ("https://lab.example/scores", False)])
def test_flat_score_source_citation_survives_exports_rank_and_model_page(tmp_path, source, cited):
    from pipeline.render import model_page

    front, path = card_tree(tmp_path, "https://lab.example/models")
    front["benchmarks"]["benchmark_source"] = source
    front["benchmarks"]["evidence"] = [{
        "benchmark_id": "humaneval", "model_id_as_evaluated": "Cited model",
        "score": 95, "unit": "percent", "source_url": "https://lab.example/results",
        "source_kind": "provider_self_report", "evidence_date": "2026-10-19",
        "date_type": "published", "verified_at": "2026-10-19",
    }]
    path.write_text("---\n" + yaml.safe_dump(front) + "---\nSynthetic fixture.\n")
    candidate = ranking.build_candidates([ModelCard.from_yaml_file(path)], CollectingSink())[0]
    assert candidate.benchmark_scores["humaneval"] == 95
    assert candidate.verified_benchmarks == {"humaneval"}
    expected = {key: {"status": "cited", "url": source}
                for key in ("swe_bench_verified", "live_code_bench", "scicode")} if cited else {}
    assert candidate.cited_benchmarks == expected
    score = ranking.score(candidate, {"benchmark_weights": {"swe_bench_verified": 1}})
    assert ("cite_only_not_machine_verified" in score.get("warnings", [])) is cited
    assert score["verified_contributions"] == 0
    models = load_models(tmp_path)
    coverage = export.models_by_benchmark(models, [])
    assert "citation" not in coverage["humaneval"][0]
    assert coverage["humaneval"][0]["attribution"] == "verified"
    assert ("citation" in coverage["swe_bench_verified"][0]) is cited
    if cited:
        assert coverage["swe_bench_verified"][0]["citation"] == expected["swe_bench_verified"]
    out = tmp_path / "export"
    catalogue = Catalogue(BUILD.as_of)
    export.write(out, models, [], catalogue, BUILD)
    exported = json.loads((out / "models/lab/cited.json").read_text())["card"]["benchmarks"]
    assert ("scores_citation" in exported) is cited
    page = model_page(models[0], BUILD, {}, catalogue)
    score_section = page.split("<h2>Reported benchmark scores</h2>", 1)[1]
    assert ("Cited, not machine-verified" in score_section) is cited


@pytest.mark.parametrize("source", ["javascript://x.ai/%0aalert(1)", "JavaScript://docs.x.ai/"])
def test_javascript_benchmark_source_is_never_linked(tmp_path, monkeypatch, source):
    from pipeline.load import Model
    from pipeline.render import esc, model_page

    front, path = card_tree(tmp_path, "https://lab.example/models")
    front["benchmarks"]["benchmark_source"] = source
    path.write_text("---\n" + yaml.safe_dump(front) + "---\nSynthetic fixture.\n")
    model = load_models(tmp_path)[0]
    assert model.scores_citation is None
    page = model_page(model, BUILD, {}, Catalogue(BUILD.as_of))
    assert "javascript:" not in page.lower().replace(esc(source).lower(), "")
    # Even a citation that names a non-HTTP URL renders its link text only.
    monkeypatch.setattr(Model, "scores_citation",
                        property(lambda self: {"status": "cited", "url": source}))
    page = model_page(model, BUILD, {}, Catalogue(BUILD.as_of))
    notice = page.split("Cited, not machine-verified", 1)[1].split("</div>", 1)[0]
    assert "<a" not in notice
    assert "score source" in notice
    assert "href=\"javascript" not in page.lower()
