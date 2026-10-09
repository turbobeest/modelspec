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
from decision.summary import summarize
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


def _spec(where, **extra):
    return parse_spec(
        {
            "spec_version": 1,
            "where": where,
            "optimize": {"max": "model.context_window"},
            "explain": "none",
            **extra,
        },
        facets=facets,
    )


def _decide(snapshot, where, **extra):
    return decide(_spec(where, **extra), snapshot, facets=facets)


def _summary(snapshot, where, **extra) -> str:
    spec = _spec(where, **extra)
    decision = decide(spec, snapshot, facets=facets)
    text, _mentions = summarize(decision, spec)
    return text


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
        "together_admits": 3,
        "question_admits": True,
    }
    bounded = project(decision, ResponseOptions(fields=["cost_per_task"]), not_applied=[])
    assert bounded["relax_single"] == {
        "status": "found",
        "gates": [{"condition": HARDWARE, "admits": 3}],
        "together_admits": 3,
        "question_admits": True,
    }


def test_two_floors_that_everyone_fails_admit_nothing():
    """Each floor excludes the whole lineup, so removing either one still leaves zero.

    Removing both floors together leaves the class, which these models meet.
    """
    where = [
        CLASS,
        "model.context_window >= 8192",
        "model.context_window >= 1000000",
    ]
    snapshot = _snapshot(
        [
            _row("lab/a", "text-generator", 1000),
            _row("lab/b", "text-generator", 2000),
        ]
    )
    decision = _decide(snapshot, where)
    assert decision.status == "no_feasible"
    assert _gates(decision) == {
        "status": "none",
        "gates": [],
        "together_admits": 2,
        "question_admits": False,
    }
    text, _mentions = summarize(decision, _spec(where))
    assert (
        "No single requirement is the blocker: removing any one of them "
        "on its own still leaves no model."
    ) in text


def test_a_class_with_no_model_of_that_class_is_not_a_stated_gate_blocker():
    """The class is not a relaxable gate, and nothing else is stated."""
    where = ["model.class = decider"]
    snapshot = _snapshot([_row("lab/a", "text-generator", 16000)])
    decision = _decide(snapshot, where)
    assert decision.status == "no_feasible"
    assert _gates(decision) == {
        "status": "none",
        "gates": [],
        "together_admits": 0,
        "question_admits": True,
    }
    assert "No single requirement is the blocker" not in _summary(snapshot, where)


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
        "together_admits": 3,
        "question_admits": True,
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
        "together_admits": 3,
        "question_admits": False,
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
        "together_admits": 2,
        "question_admits": False,
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
        "together_admits": 2,
        "question_admits": False,
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
        "together_admits": 2,
        "question_admits": False,
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


def test_the_summary_names_a_gate_that_alone_admits_several_models():
    snapshot = _snapshot(
        [
            _row("lab/a", "text-generator", 8000, fits=["apple_m3_max"]),
            _row("lab/b", "text-generator", 8000, fits=["apple_m3_max"]),
            _row("lab/c", "text-generator", 8000, fits=["apple_m3_max"]),
            _row("lab/judge", "decider", 8000, fits=["nvidia_rtx_5090"]),
        ]
    )
    text = _summary(snapshot, [CLASS, HARDWARE])
    sentence = (
        "Removing only model.fits_hardware in {nvidia_rtx_5090} would let 3 models qualify; "
        "every other requirement stays as you set it."
    )
    assert sentence in text
    assert text.index("These requirements together exclude every model:") < text.index(sentence)
    assert text.index(sentence) < text.index("Requirements applied:")


def test_the_summary_names_gates_in_order_and_uses_the_singular_for_one_model():
    snapshot = _snapshot(
        [
            _row("lab/wide-1", "text-generator", 1000, fits=["nvidia_rtx_5090"]),
            _row("lab/wide-2", "text-generator", 2000, fits=["nvidia_rtx_5090"]),
            _row("lab/tall", "text-generator", 20000, fits=["apple_m3_max"]),
        ]
    )
    text = _summary(snapshot, [CLASS, HARDWARE, CONTEXT])
    several = (
        "Removing only model.context_window >= 8192 would let 2 models qualify; "
        "every other requirement stays as you set it."
    )
    one = (
        "Removing only model.fits_hardware in {nvidia_rtx_5090} would let 1 model qualify; "
        "every other requirement stays as you set it."
    )
    assert several in text
    assert one in text
    assert text.index(several) < text.index(one)
    assert "1 models" not in text


def test_the_summary_says_when_no_single_requirement_is_the_blocker():
    snapshot = _snapshot(
        [
            _row("lab/a", "text-generator", 1000),
            _row("lab/b", "text-generator", 2000),
        ]
    )
    where = [CLASS, "model.context_window >= 8192", "model.context_window >= 1000000"]
    decision = _decide(snapshot, where)
    assert decision.relax_single.question_admits is False
    text, _mentions = summarize(decision, _spec(where))
    assert (
        "No single requirement is the blocker: removing any one of them "
        "on its own still leaves no model."
    ) in text
    assert "Removing only" not in text


def test_none_is_withheld_when_removing_the_class_alone_admits_a_model():
    """Two floors exclude every decider. One text-generator clears both.

    Removing either floor still leaves the other, so no relaxable gate admits
    a model. Removing the class alone admits the text-generator.
    """
    where = [
        "model.class = decider",
        "model.context_window >= 8192",
        "model.context_window >= 1000000",
    ]
    snapshot = _snapshot([
        _row("lab/d1", "decider", 1000),
        _row("lab/d2", "decider", 1000),
        _row("lab/t", "text-generator", 2_000_000),
    ])
    decision = _decide(snapshot, where)
    assert decision.status == "no_feasible"
    assert _gates(decision) == {
        "status": "none",
        "gates": [],
        "together_admits": 2,
        "question_admits": True,
    }
    text, _mentions = summarize(decision, _spec(where))
    assert (
        "No single requirement is the blocker: removing any one of them "
        "on its own still leaves no model."
    ) not in text


def test_gate_sentences_trim_before_the_requirement_lists():
    """Class plus eight hardware gates: the exclude list stays whole, one gate sentence remains."""
    hardware = [
        "nvidia_rtx_5090",
        "apple_m3_max",
        "amd_instinct_mi210",
        "amd_instinct_mi250x",
        "amd_instinct_mi300x",
        "amd_instinct_mi325x",
        "apple_m4_max",
        "apple_m2_ultra",
    ]
    rows = []
    for index, device in enumerate(hardware):
        fits = [other for other in hardware if other != device]
        for copy in range(index + 1):
            rows.append(_row(f"lab/m{index}-{copy}", "text-generator", 100000, fits=fits))
    where = [CLASS, *[f"model.fits_hardware in {{{device}}}" for device in hardware]]
    text = _summary(_snapshot(rows), where)
    listed = "; ".join(where)
    assert f"These requirements together exclude every model: {listed}." in text
    assert text.count("Removing only") == 1
    assert (
        "Removing only model.fits_hardware in {apple_m2_ultra} would let 8 models qualify; "
        "every other requirement stays as you set it."
    ) in text


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
    text, _mentions = summarize(decision, spec)
    assert (
        "No model that meets the requirements has complete values for the objective "
        "(arena_elo_overall), so ModelSpec cannot order them."
    ) in text
    assert "Removing only" not in text
    assert "No single requirement is the blocker:" not in text


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
