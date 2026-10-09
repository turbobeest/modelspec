"""One stated gate whose removal alone admits a model (MODEL-356).

`relax` on a reach is the first condition that emptied the lineup, which depends
on spec order and can name nothing. `relax_single` reruns each other hard
condition on its own, with every remaining condition and the same reach kept,
and counts the distinct models that then qualify.
"""

from __future__ import annotations

from datetime import date

from decision.bounded import project
from decision.contract import ResponseOptions, parse_spec
from decision.engine import decide
from decision.registry import facet as facets
from decision.snapshot import SnapshotInputs, build_snapshot, load_built_snapshot
from tests.snapshot_records import SOURCES, fact, model, offering

CONTEXT = "model.context_window >= 8192"
HARDWARE = "model.fits_hardware in {nvidia_rtx_5090}"
CLASS = "model.class = text-generator"


def _row(mid, cls, context, *, weights="open_weights", fits=None):
    facts = [
        fact("model", mid, "model.class", cls),
        fact("model", mid, "model.context_window", context),
        fact("model", mid, "model.weights_openness", weights),
    ]
    if fits is not None:
        facts.append(fact("model", mid, "model.fits_hardware", fits))
    return model(mid, facts=facts)


def _snapshot(models, offerings=None):
    built = build_snapshot(
        SnapshotInputs(models=models, offerings=offerings or [], sources=SOURCES),
        gate=False,
        as_of=date(2026, 10, 8),
    )
    return load_built_snapshot(built, include_archive=True, source="relax_single test")


def _decide(snapshot, where, **extra):
    spec = parse_spec(
        {
            "spec_version": 1,
            "where": where,
            "optimize": {"max": "model.context_window"},
            "explain": "none",
            **extra,
        },
        facets=facets,
    )
    return decide(spec, snapshot, facets=facets)


def _gates(decision):
    return decision.relax_single.model_dump()


def test_one_hardware_gate_names_the_models_it_admits():
    snapshot = _snapshot(
        [
            _row("lab/a", "text-generator", 8000, fits=["apple_m3_max"]),
            _row("lab/b", "text-generator", 8000, fits=["apple_m3_max"]),
            _row("lab/c", "text-generator", 8000, fits=["apple_m3_max"]),
            _row("lab/judge", "decider", 8000, fits=["nvidia_rtx_5090"]),
        ]
    )
    decision = _decide(snapshot, [CLASS, HARDWARE])
    assert decision.status == "no_feasible"
    assert _gates(decision) == {
        "status": "found",
        "gates": [{"condition": HARDWARE, "admits": 3}],
    }
    bounded = project(decision, ResponseOptions(fields=["cost_per_task"]), not_applied=[])
    assert bounded["relax_single"] == {
        "status": "found",
        "gates": [{"condition": HARDWARE, "admits": 3}],
    }


def test_two_floors_that_everyone_fails_admit_nothing():
    """Each floor excludes the whole lineup, so removing either one still leaves zero."""
    snapshot = _snapshot(
        [
            _row("lab/a", "text-generator", 1000),
            _row("lab/b", "text-generator", 2000),
        ]
    )
    decision = _decide(
        snapshot,
        [
            CLASS,
            "model.context_window >= 8192",
            "model.context_window >= 1000000",
        ],
    )
    assert decision.status == "no_feasible"
    assert _gates(decision) == {"status": "none", "gates": []}


def test_the_class_is_never_a_gate_even_when_dropping_it_would_admit_a_model():
    snapshot = _snapshot(
        [
            _row("lab/a", "text-generator", 1000),
            _row("lab/b", "text-generator", 2000),
            _row("lab/c", "text-generator", 4000),
            _row("lab/judge", "decider", 100_000),
        ]
    )
    decision = _decide(snapshot, [CLASS, CONTEXT])
    assert _gates(decision) == {
        "status": "found",
        "gates": [{"condition": CONTEXT, "admits": 3}],
    }
    assert CLASS not in [gate["condition"] for gate in _gates(decision)["gates"]]


def test_gates_are_ordered_by_how_many_models_they_admit_then_spec_order():
    wider = _snapshot(
        [
            _row("lab/wide-1", "text-generator", 1000, fits=["nvidia_rtx_5090"]),
            _row("lab/wide-2", "text-generator", 2000, fits=["nvidia_rtx_5090"]),
            _row("lab/tall", "text-generator", 20000, fits=["apple_m3_max"]),
        ]
    )
    # The fit gate is earlier in the spec and admits fewer models.
    decision = _decide(wider, [CLASS, HARDWARE, CONTEXT])
    assert _gates(decision) == {
        "status": "found",
        "gates": [
            {"condition": CONTEXT, "admits": 2},
            {"condition": HARDWARE, "admits": 1},
        ],
    }
    tied = _snapshot(
        [
            _row("lab/needs-context", "text-generator", 1000, fits=["nvidia_rtx_5090"]),
            _row("lab/needs-fit", "text-generator", 20000, fits=["apple_m3_max"]),
        ]
    )
    decision = _decide(tied, [CLASS, HARDWARE, CONTEXT])
    assert _gates(decision) == {
        "status": "found",
        "gates": [
            {"condition": HARDWARE, "admits": 1},
            {"condition": CONTEXT, "admits": 1},
        ],
    }


def test_an_access_reach_counts_only_the_models_inside_it():
    snapshot = _reach_snapshot()
    decision = _decide(
        snapshot,
        [CLASS, CONTEXT],
        access={"kind": "own_hardware"},
    )
    assert decision.relax == [CONTEXT]
    assert _gates(decision) == {
        "status": "found",
        "gates": [{"condition": CONTEXT, "admits": 2}],
    }


def test_an_estate_keeps_the_access_reach_on_the_returned_decision():
    snapshot = _reach_snapshot()
    decision = _decide(
        snapshot,
        [CLASS, CONTEXT],
        access={"kind": "own_hardware"},
        estate={"devices": ["nvidia_rtx_5090"]},
    )
    assert _gates(decision) == {
        "status": "found",
        "gates": [{"condition": CONTEXT, "admits": 2}],
    }


def test_an_answered_decision_has_no_relax_single_key():
    snapshot = _snapshot(
        [
            _row("lab/a", "text-generator", 16000),
            _row("lab/b", "text-generator", 32000),
        ]
    )
    decision = _decide(snapshot, [CLASS, CONTEXT])
    assert decision.status == "answered"
    assert "relax_single" not in decision.model_dump(mode="json")


def test_an_objective_with_no_values_omits_relax_single():
    snapshot = _snapshot([_row("lab/a", "text-generator", 16000)])
    spec = parse_spec(
        {
            "spec_version": 1,
            "where": [CLASS],
            "optimize": {"max": "arena_elo_overall"},
            "explain": "none",
        },
        facets=facets,
    )
    decision = decide(spec, snapshot, facets=facets)
    assert decision.status == "no_feasible"
    assert decision.relax == [
        "no model that meets the requirements has a value for arena_elo_overall",
    ]
    assert "relax_single" not in decision.model_dump(mode="json")


def _reach_snapshot():
    """Two self-hostable models and one sold model an own-hardware reach cannot hold."""
    return _snapshot(
        [
            _row("lab/local-5090", "text-generator", 1000, fits=["nvidia_rtx_5090"]),
            _row("lab/local-m3", "text-generator", 2000, fits=["apple_m3_max"]),
            _row("lab/hosted", "text-generator", 4000, weights="closed_weights"),
        ],
        [offering("lab/hosted", price=1.0)],
    )


def test_estate_probes_do_not_compute_relax_single(monkeypatch):
    """with_estate reruns the question per reach and reads only status and answer."""
    import decision.engine as engine

    calls = []
    real = engine.single_gates

    def counting(*args, **kwargs):
        calls.append(1)
        return real(*args, **kwargs)

    monkeypatch.setattr(engine, "single_gates", counting)
    decision = _decide(
        _reach_snapshot(),
        [CLASS, CONTEXT],
        access={"kind": "own_hardware"},
        estate={"devices": ["nvidia_rtx_5090"]},
    )
    assert decision.status == "no_feasible"
    assert len(calls) == 1
