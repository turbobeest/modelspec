"""MODEL-181 decision comparisons and retained-generation resolution."""

from __future__ import annotations

import json
import os
from datetime import date

import pytest

from cli.modelspec.snapshot import resolve_decision_generation
from decision.compare import compare
from decision.contract import (
    CandidateValues,
    Contribution,
    Decision,
    OfferingRef,
    Result,
    ShownFact,
    parse_spec,
)
from decision.engine import decide
from decision.registry import facet
from decision.snapshot import (
    Snapshot,
    SnapshotInputs,
    build_snapshot,
    content_hash,
    load_snapshot_bytes,
    snapshot_id_for,
)
from tests.snapshot_records import SOURCES, fact, model, offering


def _decision(snapshot: str, rows: list[tuple[str, int, float]]) -> Decision:
    results, top = [], []
    for model_id, rank, price in rows:
        offering = OfferingRef(model=model_id)
        results.append(Result(rank=rank, offering=offering, contributions=[Contribution(
            dimension="-offering.cost_per_task", raw_value=price,
            unit="usd_per_task", records=[f"{model_id}#price"],
        )]))
        top.append(CandidateValues(offering=offering, facts=[ShownFact(
            facet="model.context_window", value=128000,
            unit="tokens", record_id=f"{model_id}#context",
        )]))
    return Decision(
        decision_id="dec_" + snapshot.removeprefix("snap_")[:24], snapshot=snapshot,
        spec_hash="sha256:" + "1" * 64, explain="full", status="answered",
        results=results, top=top,
    )


def _engine_snapshot(
    prices: dict[str, float],
    as_of: date,
    *,
    contexts: dict[str, int] | None = None,
):
    models = []
    offerings = []
    for name, price in prices.items():
        model_id = f"lab/{name}"
        model_facts = [
            fact("model", model_id, "model.class", "text-generator"),
            fact("model", model_id, "model.lifecycle", "active"),
        ]
        if contexts is not None:
            model_facts.append(
                fact("model", model_id, "model.context_window", contexts[name])
            )
        models.append(model(model_id, facts=model_facts))
        offering_id = f"p1/{model_id}/global/standard"
        offerings.append(offering(model_id, "p1", facts=[
            fact("offering", offering_id, "offering.price.input", price,
                 source="src-pricing"),
            fact("offering", offering_id, "offering.price.output", price,
                 source="src-pricing"),
        ]))
    built = build_snapshot(
        SnapshotInputs(models=models, offerings=offerings, sources=SOURCES),
        gate=False,
        as_of=as_of,
    )
    return load_snapshot_bytes(built.to_bytes(key=None), key=None, include_archive=True)


def test_price_change_and_new_model_name_exactly_those_models():
    old_index = _engine_snapshot({"a": 1.0, "b": 2.0}, date(2026, 9, 26))
    new_index = _engine_snapshot({"a": 1.2, "b": 2.0, "new": 3.0}, date(2026, 9, 27))
    spec = parse_spec({
        "spec_version": 1,
        "where": ["model.class = text-generator"],
        "optimize": {"min": "offering.cost_per_task"},
        "explain": "full",
    }, facets=facet)
    old = decide(spec, old_index, facets=facet)
    new = decide(spec, new_index, facets=facet)

    result = compare(old, new, old_as_of="2026-09-26", new_as_of="2026-09-27")

    assert [row["model"] for row in result["models"]] == ["lab/a", "lab/new"]
    assert result["counts"] == {"entered": 1, "left": 0, "rank_changed": 0,
                                "may_qualify_changed": 0, "models_changed": 2}
    price = result["models"][0]["values"]
    assert [(row["kind"], row["old"]["value"], row["new"]["value"])
            for row in price] == [("cost_per_task", 0.044, 0.0528)]
    assert set(price[0]["old"]["records"]) == {
        "p1/lab/a/global/standard#offering.price.input",
        "p1/lab/a/global/standard#offering.price.output",
    }


def test_newly_passed_and_failed_musts_include_both_values_and_records():
    old_index = _engine_snapshot(
        {"entered": 1.0, "left": 1.0},
        date(2026, 9, 26),
        contexts={"entered": 100, "left": 200},
    )
    new_index = _engine_snapshot(
        {"entered": 1.0, "left": 1.0},
        date(2026, 9, 27),
        contexts={"entered": 200, "left": 100},
    )
    spec = parse_spec({
        "spec_version": 1,
        "where": ["model.context_window >= 150"],
        "optimize": {"min": "offering.cost_per_task"},
        "explain": "full",
    }, facets=facet)

    result = compare(
        decide(spec, old_index, facets=facet),
        decide(spec, new_index, facets=facet),
    )

    rows = {row["model"]: row for row in result["models"]}
    assert rows["lab/entered"]["entered"] is True
    assert rows["lab/left"]["left"] == {"reason": "model.context_window >= 150"}
    for model_id, old_value, new_value in (
        ("lab/entered", 100, 200),
        ("lab/left", 200, 100),
    ):
        assert rows[model_id]["values"] == [{
            "kind": "facet",
            "facet": "model.context_window",
            "offering": {"model": model_id, "provider": "p1", "region": "global",
                         "tier": "standard"},
            "old": {"value": old_value, "unit": "tokens",
                    "records": [f"{model_id}#model.context_window"]},
            "new": {"value": new_value, "unit": "tokens",
                    "records": [f"{model_id}#model.context_window"]},
        }]


def test_a_newly_unknown_must_keeps_the_old_value_and_provenance():
    old_index = _engine_snapshot(
        {"a": 1.0}, date(2026, 9, 26), contexts={"a": 200}
    )
    new_index = _engine_snapshot({"a": 1.0}, date(2026, 9, 27))
    spec = parse_spec({
        "spec_version": 1,
        "where": ["model.context_window >= 150"],
        "optimize": {"min": "offering.cost_per_task"},
        "explain": "full",
    }, facets=facet)

    result = compare(
        decide(spec, old_index, facets=facet),
        decide(spec, new_index, facets=facet),
    )

    row, = result["models"]
    assert row["may_qualify"] == {"old": None, "new": ["model.context_window"]}
    value, = row["values"]
    assert value["old"] == {
        "value": 200,
        "unit": "tokens",
        "records": ["lab/a#model.context_window"],
    }
    assert value["new"] == {"value": None, "unit": None, "records": []}


def test_comparing_a_snapshot_to_itself_has_no_changes():
    decision = _decision("snap_" + "a" * 64, [("lab/a", 1, 0.10)])
    result = compare(decision, decision, old_as_of="2026-09-27", new_as_of="2026-09-27")
    assert result["changed"] is False
    assert result["models"] == []


def _generation(cache, as_of: str) -> str:
    content = {
        "format_version": 1, "as_of": as_of, "facet_subjects": {},
        "lineup": {"candidates": [], "facets": {}, "evidence": {}},
        "archive": {"candidates": [], "facets": {}, "evidence": {}},
        "out_of_lineup": 0, "benchmark_domains": {}, "capability": {},
        "sources": {}, "excluded": {},
    }
    digest = content_hash(content)
    snapshot_id = snapshot_id_for(digest)
    generation = cache / "decision" / snapshot_id
    generation.mkdir(parents=True)
    Snapshot(content, digest, snapshot_id).write(generation / "snapshot.json.gz", key=None)
    (generation / "vocabulary.json").write_text(json.dumps({"snapshot": snapshot_id}))
    return snapshot_id


def test_previous_resolves_the_retained_non_current_generation(tmp_path):
    old = _generation(tmp_path, "2026-09-26")
    new = _generation(tmp_path, "2026-09-27")
    os.utime(tmp_path / "decision" / old, (1, 1))
    os.utime(tmp_path / "decision" / new, (2, 2))
    (tmp_path / "decision" / "current").write_text(new + "\n")
    assert resolve_decision_generation("previous", tmp_path).parent.name == old


def test_unknown_snapshot_lists_the_cached_ids(tmp_path):
    first = _generation(tmp_path, "2026-09-26")
    second = _generation(tmp_path, "2026-09-27")
    (tmp_path / "decision" / "current").write_text(second + "\n")
    with pytest.raises(ValueError) as caught:
        resolve_decision_generation("snap_missing", tmp_path)
    assert first in str(caught.value) and second in str(caught.value)
