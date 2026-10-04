"""Public coverage distinguishes catalogue cards from the board's admitted scope."""

import json
from collections import Counter
from datetime import date
from pathlib import Path

import pytest

from api import classes
from api.class_fit import CatalogueEvidence, class_fit
from decision import contract
from decision.engine import decide
from decision.registry import default
from decision.snapshot import SnapshotInputs, build_from_repo, build_snapshot, load_built_snapshot
from pipeline import coverage, public_data
from pipeline.class_export import class_fit_export
from pipeline.load import load_models
from tests.snapshot_records import SOURCES, fact, model, offering
from tests.test_decide_worker import _load_service

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def repo_snapshot():
    return load_built_snapshot(build_from_repo(
        ROOT, premier=ROOT / "premier/slice-1.yaml", as_of=date.today(), gate=False,
    ), source="coverage test")


@pytest.fixture(scope="module")
def covered_snapshot():
    models = [model("lab/" + name, facts=[
        fact("model", "lab/" + name, "model.class", "text-generator"),
    ]) for name in ("a", "b")]
    retired = model("lab/retired", lifecycle="retired", facts=[
        fact("model", "lab/retired", "model.class", "transcriber"),
    ])
    return load_built_snapshot(build_snapshot(
        SnapshotInputs(models=[*models, retired], sources=SOURCES),
        as_of=date(2026, 10, 3),
    ), source="coverage test", include_archive=True)


def test_coverage_counts_match_the_snapshot_and_catalogue(repo_snapshot):
    models = load_models(ROOT)
    payload = coverage.from_snapshot(repo_snapshot, models)
    catalogue_counts = Counter(classes.MODEL_TYPE_PLACEMENT[m.front["model_type"]] for m in models)
    board_counts = Counter(
        repo_snapshot.fact(cid, "model.class").value for cid in repo_snapshot.candidates()
        if repo_snapshot.kind(cid) == "model" and repo_snapshot.lifecycle(cid) != "retired"
        and repo_snapshot.fact(cid, "model.class").state == "known"
    )
    for row in payload["classes"]:
        assert row["decidable"] == board_counts[row["id"]]
        assert row["catalogued"] == catalogue_counts[row["id"]]
        assert row["catalogued_not_decidable"] == row["catalogued"] - row["decidable"]
    assert sum(row["catalogued"] for row in payload["classes"]) == len(models)
    assert payload["catalogue"]["models"] == len(models)
    assert payload["board"]["models"] == sum(board_counts.values())
    assert payload["snapshot"] == repo_snapshot.snapshot_id
    assert payload["as_of"] == repo_snapshot.as_of.isoformat()
    for model_type in ("audio-asr", "audio-tts"):
        row = next(row for row in payload["model_types"] if row["id"] == model_type)
        assert row["catalogued"] == sum(m.front["model_type"] == model_type for m in models)
        assert row["decidable"] == 0
        assert row["catalogued_not_decidable"] == row["catalogued"] > 0
    assert [row["id"] for row in payload["classes"]] == sorted(row["id"] for row in payload["classes"])
    serialised = json.dumps(payload)
    assert all(model.model_id not in serialised for model in models)


def test_covered_offerings_and_aggregators_are_counted_from_data(repo_snapshot):
    payload = coverage.from_snapshot(repo_snapshot, load_models(ROOT))
    counts = Counter(cid.split("/")[0] for cid in repo_snapshot.candidates()
                     if repo_snapshot.kind(cid) == "offering" and repo_snapshot.lifecycle(cid) != "retired")
    assert {row["id"]: row["offerings"] for row in payload["providers"]} == counts
    assert payload["board"]["offerings"] == sum(counts.values())
    assert sum(row["count"] for row in payload["offerings"]) == sum(counts.values())
    aggregator_ids = sorted(provider for provider in counts if default().provider(provider).kind == "aggregator")
    assert payload["aggregators"]["providers"] == aggregator_ids
    assert payload["aggregators"]["offerings"] == sum(counts[provider] for provider in aggregator_ids)


def test_an_aggregator_is_reported_when_its_offering_is_in_the_snapshot():
    card = next(model for model in load_models(ROOT) if model.front["model_type"] == "llm-chat")
    built = build_snapshot(SnapshotInputs(
        models=[model(card.model_id, facts=[fact("model", card.model_id, "model.class", "text-generator")])],
        offerings=[offering(card.model_id, provider="openrouter")], sources=SOURCES,
    ), as_of=date(2026, 10, 3))
    payload = coverage.from_snapshot(load_built_snapshot(built, source="aggregator test"), [card])
    assert payload["aggregators"] == {"providers": ["openrouter"], "offerings": 1}
    assert "openrouter" in coverage.provider_summary(payload)


def test_export_uses_the_published_signed_snapshot_and_its_date(tmp_path, monkeypatch):
    card = next(model for model in load_models(ROOT) if model.front["model_type"] == "llm-chat")
    snapshot = build_snapshot(SnapshotInputs(
        models=[model(card.model_id, facts=[fact("model", card.model_id, "model.class", "text-generator")])],
        sources=SOURCES,
    ), as_of=date(2026, 10, 3))
    snapshot.write(tmp_path / "decision/snapshot.json.gz", key=b"coverage-test-key")
    monkeypatch.setenv("MODELSPEC_SNAPSHOT_KEY", "coverage-test-key")
    payload = coverage.write_export(tmp_path, root=ROOT, models=[card], as_of=date(2026, 10, 4))
    assert payload["snapshot"] == snapshot.snapshot_id
    assert payload["as_of"] == "2026-10-03"
    assert payload["board"]["models"] == 1
    assert json.loads((tmp_path / "coverage.json").read_text()) == payload


@pytest.mark.parametrize("class_id", ["transcriber", "media-generator"])
@pytest.mark.parametrize("fields", [None, ["cost_per_task"]])
def test_speech_request_returns_typed_coverage_without_widening_status(covered_snapshot, class_id, fields):
    payload = {"spec_version": 1, "where": [f"model.class = {class_id}"],
               "optimize": {"min": "model.context_window"}, "explain": "none", "fields": fields}
    status, body = _load_service().decide(payload, covered_snapshot)
    assert status == 200
    assert body["status"] == "no_feasible"
    assert body["results"] == []
    refusal = contract.CoverageRefusal.model_validate(body["coverage"])
    assert refusal.kind == "out_of_coverage"
    assert refusal.requested_classes == [class_id]
    assert [row.model_dump() for row in refusal.classes] == [{"id": "text-generator", "models": 2}]
    assert refusal.as_of == "2026-10-03"
    assert refusal.url == "https://modelspec.dev/api/coverage.json"
    assert "text-generator (2 models)" in refusal.message
    assert "Catalogue presence is not decision coverage" in refusal.message


@pytest.mark.parametrize("requirements", [
    {"capabilities": {"speech": "required"}},
    {"optimize": {"max": "marketing_seo"}},
    {"where": ["marketing_seo >= 0.5"]},
    {"capabilities": {"speech": "required"}, "optimize": {"max": "not_a_facet"}},
])
def test_unsupported_domains_keep_their_existing_result_or_refusal(covered_snapshot, requirements):
    payload = {"spec_version": 1, "optimize": {"max": "model.context_window"},
               "explain": "none", **requirements}
    status, body = _load_service().decide(payload, covered_snapshot)
    assert status in (200, 400)
    refusal = contract.CoverageRefusal.model_validate(body["coverage"])
    assert refusal.requested_domains == (["marketing_seo"] if "capabilities" not in requirements else ["speech"])
    if status == 400:
        assert body["error"]["code"] == "invalid_spec"
        assert body["error"]["issues"]
        assert body["error"]["recovery"]


@pytest.mark.parametrize("where", [
    ["model.class != transcriber"],
    ["model.class != text-generator"],
    ["model.class in {text-generator, transcriber}"],
    [{"any": ["model.class = transcriber", "model.context_window >= 1"]}],
    ["model.class = transcriber soft(0.2)"],
])
def test_available_alternatives_and_soft_conditions_are_not_coverage_refusals(covered_snapshot, where):
    spec = contract.parse_spec({"spec_version": 1, "where": where,
                               "optimize": {"max": "model.context_window"}, "explain": "none"},
                              facets=default().facet)
    assert decide(spec, covered_snapshot).coverage is None


def test_coverage_names_only_the_unsupported_class_in_a_conflicting_request(covered_snapshot):
    spec = contract.parse_spec({
        "spec_version": 1,
        "where": ["model.class = text-generator", "model.class = transcriber"],
        "optimize": {"max": "model.context_window"}, "explain": "none",
    }, facets=default().facet)
    result = decide(spec, covered_snapshot)
    assert result.status == "no_feasible"
    assert result.coverage.requested_classes == ["transcriber"]
    assert [row.id for row in result.coverage.classes] == ["text-generator"]


def test_class_fit_preserves_class_selection_and_names_the_board_limit():
    answer = class_fit(task="speech to text", evidence=CatalogueEvidence(
        card_counts={"transcriber": 17, "media-generator": 12},
        decision_counts={"text-generator": 2},
    ))
    transcriber = next(row for row in answer["candidates"] if row["class"] == "transcriber")
    assert transcriber["catalogue"]["card_count"] == 17
    assert transcriber["decision_coverage"] == {"models": 0, "url": "https://modelspec.dev/api/coverage.json"}
    assert "no decidable model" in transcriber["next"]
    assert all("rank_score" not in row for row in answer["candidates"])


def test_class_fit_export_adds_board_counts_and_the_public_split_keeps_coverage(repo_snapshot, tmp_path):
    payload = coverage.from_snapshot(repo_snapshot, load_models(ROOT))
    exported = class_fit_export({}, model_type_counts={"audio-asr": 17}, coverage=payload)
    transcriber = next(row for row in exported["classes"] if row["id"] == "transcriber")
    assert transcriber["decision_coverage"]["models"] == 0
    assert transcriber["decision_coverage"]["snapshot"] == repo_snapshot.snapshot_id
    out = tmp_path / "api"
    out.mkdir()
    (out / "coverage.json").write_text(json.dumps(payload))
    (tmp_path / "_headers").write_text("")
    public_data.restrict(tmp_path)
    assert json.loads((out / "coverage.json").read_text()) == payload
