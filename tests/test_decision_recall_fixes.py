"""The engine causes behind the first recall baseline (MODEL-157).

Each section pins one cause: the lineup a decision ranges over, ``@direct``
read against the capabilities asked about, an unregistered harness in an
explained decision, and a feasible model with no objective value.
"""

from __future__ import annotations

from datetime import date

import pytest
from pydantic import ValidationError

from decision.contract import Decision, EvidenceItem, parse_spec
from decision.engine import decide
from decision.registry import facet as facets
from decision.snapshot import SnapshotInputs, build_snapshot, load_snapshot_bytes
from tests.snapshot_records import SOURCES, evidence, fact, model, offering

AS_OF = date(2026, 9, 24)
TERMINAL = "terminal_bench_v4_0"
DOMAINS = {TERMINAL: [("agentic_tool_use", "direct"), ("software_engineering", "proxy")]}


def generator(mid: str, *, lifecycle: str = "active"):
    facts = [
        fact("model", mid, "model.class", "text-generator"),
        fact("model", mid, "model.context_window", 200000),
        fact("model", mid, "model.lifecycle", lifecycle),
    ]
    return model(mid, lifecycle=lifecycle, facts=facts)


def snapshot(models, *, rows=(), offerings=(), premier=None, domains=None):
    built = build_snapshot(
        SnapshotInputs(
            models=list(models),
            offerings=list(offerings),
            evidence=list(rows),
            sources=SOURCES,
            benchmark_domains=DOMAINS if domains is None else domains,
        ),
        premier=premier,
        gate=False,
        as_of=AS_OF,
    )
    return built, load_snapshot_bytes(built.to_bytes(key=None), key=None, include_archive=True)


def spec(*, where=("model.class = text-generator",), objective=None, capabilities=None,
         explain="none"):
    data = {
        "spec_version": 1,
        "where": list(where),
        "optimize": objective or {"max": f"{TERMINAL} @independent @direct"},
        "explain": explain,
    }
    if capabilities is not None:
        data["capabilities"] = capabilities
    return parse_spec(data, facets=facets)


# ── 1. the premier lineup ──────────────────────────────────────────────────


def test_a_premier_list_scopes_the_lineup_and_counts_the_rest():
    built, index = snapshot(
        [generator("lab/premier"), generator("lab/other"), generator("lab/another"),
         generator("lab/old", lifecycle="retired")],
        offerings=[offering("lab/premier"), offering("lab/other")],
        rows=[evidence("lab/premier", TERMINAL, 60.0), evidence("lab/other", TERMINAL, 90.0)],
        premier=["lab/premier"],
    )
    lineup = [c["id"] for c in built.content["lineup"]["candidates"]]
    archive = [c["id"] for c in built.content["archive"]["candidates"]]
    assert lineup == ["lab-api/lab/premier/global/standard", "lab/premier"]
    assert archive == ["lab/old"]
    assert built.content["out_of_lineup"] == 2
    assert index.out_of_lineup == 2
    # Models outside the lineup leave no evidence or retained records behind.
    assert "lab/other" not in built.content["lineup"]["evidence"]
    assert not any(rid.startswith("lab/other") for rid in built.content["fact_records"])

    decision = decide(spec(capabilities={"agentic_tool_use": "required"}), index,
                      facets=facets)
    assert decision.out_of_lineup == 2
    assert {r.offering.model for r in decision.results} == {"lab/premier"}
    assert "lab/other" not in {m.model for m in decision.may_qualify}


def test_without_a_premier_list_the_lineup_is_every_active_model():
    built, index = snapshot([generator("lab/a"), generator("lab/b")])
    assert [c["id"] for c in built.content["lineup"]["candidates"]] == ["lab/a", "lab/b"]
    assert built.content["out_of_lineup"] == 0
    assert index.out_of_lineup == 0


def test_the_archive_is_decided_only_when_the_spec_asks_for_retired_models():
    _, index = snapshot(
        [generator("lab/premier"), generator("lab/old", lifecycle="retired")],
        rows=[evidence("lab/premier", TERMINAL, 60.0), evidence("lab/old", TERMINAL, 70.0)],
        premier=["lab/premier"],
    )
    caps = {"agentic_tool_use": "required"}
    lineup_only = decide(spec(capabilities=caps), index, facets=facets)
    assert [r.offering.model for r in lineup_only.results] == ["lab/premier"]
    with_archive = decide(
        spec(where=("model.lifecycle in {active, retired}",), capabilities=caps),
        index, facets=facets,
    )
    assert [r.offering.model for r in with_archive.results] == ["lab/old", "lab/premier"]


def test_the_gate_still_runs_when_asked_and_can_be_skipped():
    from decision.snapshot import CompletenessError

    inputs = SnapshotInputs(models=[generator("lab/a")], sources=SOURCES)
    from decision.registry import default

    with pytest.raises(CompletenessError):
        build_snapshot(inputs, registry=default(), premier=["lab/a"], as_of=AS_OF)
    ungated = build_snapshot(inputs, registry=default(), premier=["lab/a"], as_of=AS_OF,
                             gate=False)
    assert [c["id"] for c in ungated.content["lineup"]["candidates"]] == ["lab/a"]


def test_out_of_lineup_is_an_additive_decision_field():
    base = {
        "decision_id": "dec_0123456789ab",
        "snapshot": "snap_0123456789abcdef",
        "spec_hash": "sha256:" + "0" * 64,
        "explain": "none",
        "status": "answered",
    }
    assert Decision.model_validate(base).out_of_lineup == 0
    assert Decision.model_validate(base | {"out_of_lineup": 5}).out_of_lineup == 5
    with pytest.raises(ValidationError):
        Decision.model_validate(base | {"out_of_lineup": -1})


# ── 2. @direct is relative to the capability asked about ───────────────────


def _two_generators():
    return snapshot(
        [generator("lab/a"), generator("lab/b")],
        rows=[evidence("lab/a", TERMINAL, 60.0), evidence("lab/b", TERMINAL, 70.0)],
    )


def test_direct_objective_admits_a_benchmark_direct_for_a_requested_capability():
    _, index = _two_generators()
    decision = decide(
        spec(capabilities={"agentic_tool_use": "required", "software_engineering": "preferred"}),
        index, facets=facets,
    )
    assert [r.offering.model for r in decision.results] == ["lab/b", "lab/a"]


def test_direct_objective_excludes_a_benchmark_that_is_only_a_proxy_for_the_request():
    _, index = _two_generators()
    decision = decide(spec(capabilities={"software_engineering": "required"}), index,
                      facets=facets)
    assert decision.results == []
    assert {m.model for m in decision.may_qualify} == {"lab/a", "lab/b"}


def test_direct_objective_without_capabilities_needs_a_direct_tag_in_some_domain():
    _, index = _two_generators()
    assert [r.offering.model for r in decide(spec(), index, facets=facets).results] == [
        "lab/b", "lab/a"]
    _, proxy_only = snapshot(
        [generator("lab/a")], rows=[evidence("lab/a", TERMINAL, 60.0)],
        domains={TERMINAL: [("software_engineering", "proxy")]},
    )
    assert decide(spec(), proxy_only, facets=facets).results == []


def test_direct_condition_reads_directness_against_the_request():
    _, index = _two_generators()
    where = ("model.class = text-generator", f"{TERMINAL} >= 65 @direct")
    objective = {"max": "model.context_window"}
    direct = decide(spec(where=where, objective=objective,
                         capabilities={"agentic_tool_use": "required"}), index, facets=facets)
    assert [r.offering.model for r in direct.results] == ["lab/b"]
    proxy = decide(spec(where=where, objective=objective,
                        capabilities={"software_engineering": "required"}), index, facets=facets)
    assert proxy.results == []
    assert {m.model for m in proxy.may_qualify} == {"lab/a", "lab/b"}


# ── 3. an unregistered harness in an explained decision ────────────────────


def test_unregistered_harness_evidence_is_explained_without_crashing():
    _, index = snapshot(
        [generator("lab/a")],
        rows=[evidence("lab/a", TERMINAL, 60.0, harness="unregistered")],
    )
    decision = decide(spec(capabilities={"agentic_tool_use": "required"}, explain="full"),
                      index, facets=facets)
    (item,) = decision.results[0].evidence[0].items
    assert item.harness is None
    assert item.harness_unregistered is True


def test_harness_unregistered_is_additive_and_consistent():
    base = {
        "benchmark": TERMINAL, "value": 60.0, "measured_by": "independent",
        "date": "2026-09-01", "date_type": "observed",
        "source": "https://board.example.org/results", "directness": "direct",
    }
    assert EvidenceItem.model_validate(base).harness_unregistered is False
    assert EvidenceItem.model_validate(base | {"harness_unregistered": True}).harness is None
    with pytest.raises(ValidationError):
        EvidenceItem.model_validate(base | {"harness": "unregistered"})
    with pytest.raises(ValidationError, match="harness"):
        EvidenceItem.model_validate(
            base | {"harness": "claude-code@2.1", "harness_unregistered": True})


# ── 4. no objective value: may qualify, never ranked ───────────────────────


def test_a_feasible_model_without_an_objective_value_may_qualify_and_is_not_ranked():
    _, index = snapshot(
        [generator("lab/a"), generator("lab/b"), generator("lab/none")],
        rows=[evidence("lab/a", TERMINAL, 60.0), evidence("lab/b", TERMINAL, 70.0)],
    )
    decision = decide(spec(capabilities={"agentic_tool_use": "required"}, explain="full"),
                      index, facets=facets)
    assert [r.offering.model for r in decision.results] == ["lab/b", "lab/a"]
    assert [(m.model, m.unknown) for m in decision.may_qualify] == [("lab/none", [TERMINAL])]
    assert decision.status == "partial"
    assert "lab/none" not in {m.model for m in decision.eliminated.models}


def test_when_no_model_has_the_objective_value_all_of_them_may_qualify():
    _, index = snapshot([generator("lab/a"), generator("lab/b")])
    decision = decide(spec(capabilities={"agentic_tool_use": "required"}), index,
                      facets=facets)
    assert decision.status == "no_feasible"
    assert decision.results == []
    assert [(m.model, m.unknown) for m in decision.may_qualify] == [
        ("lab/a", [TERMINAL]), ("lab/b", [TERMINAL])]


# ── 5. sets on a set-valued facet (Q14, Q15, Q17) ──────────────────────────


def _set_run(where: str):
    from decision.filter import apply
    from decision.resolve import resolve
    from tests.snapshot_records import loaded_index

    index = loaded_index({
        "lab/cn": {"origin.lab_jurisdiction": ["CN"], "model.input_modalities": ["text"]},
        "lab/us": {"origin.lab_jurisdiction": ["US"],
                   "model.input_modalities": ["image", "text"]},
        "lab/both": {"origin.lab_jurisdiction": ["CN", "US"],
                     "model.input_modalities": ["audio"]},
    })
    parsed = parse_spec({"spec_version": 1, "where": [where],
                         "optimize": {"max": "model.context_window"}}, facets=facets)
    return apply(resolve(parsed, facets=facets), index)


def test_in_on_a_set_facet_passes_when_the_sets_share_a_value():
    assert _set_run("model.input_modalities in {image}").feasible == ("lab/us",)
    assert _set_run("model.input_modalities in {image, audio}").feasible == ("lab/both", "lab/us")


def test_not_in_on_a_set_facet_passes_only_when_no_value_is_shared():
    # A governance filter must never pass a model it names (design §3, principle 2).
    assert _set_run("origin.lab_jurisdiction not in {CN}").feasible == ("lab/us",)
    assert _set_run("origin.lab_jurisdiction in {US}").feasible == ("lab/both", "lab/us")
