"""MODEL-339: a bounded non-pick offers a deterministic action, with no ranking."""

from dataclasses import FrozenInstanceError
from datetime import date
import json

import pytest

from decision.bounded import AGENT_BYTES, compact_bytes, mcp_text_bytes, project
from decision.contract import ResponseOptions, SpecError, parse_spec
from decision.engine import decide
from decision.registry import facet
from decision.next_move import (
    NEEDS_BYTES,
    NextMoveInput,
    build_next_move,
    next_move_input_from_bounded,
    next_move_input_from_decision,
)
from decision.summary import SUMMARY_BYTES, summarize
from tests.test_decision_summary import _decision, _row, _separated, _spec, _tied
from tests.test_decide_worker import snapshot, snapshot_bytes  # noqa: F401


STEPS = [
    "Collect 10 to 20 real examples of this task from your own work, each with the result you would accept.",
    "Write the pass or fail criteria before running any model.",
    "Run every candidate on the same examples with the same prompt and settings.",
    "Score each output without knowing which model produced it.",
    "Choose the candidate that passes most often. If candidates pass equally, choose on cost or on a provider you already use.",
]


def test_input_is_frozen_and_a_separated_pick_has_no_move():
    inp = NextMoveInput("answered", answer_kind="separated", answer_members=("lab/a",), task_type="review")
    assert build_next_move(inp) is None
    with pytest.raises(FrozenInstanceError):
        inp.status = "partial"
    body = project(_decision(answer=_separated("lab/a")), ResponseOptions(fields=["model"]),
                   spec=_spec(), not_applied=[])
    assert "next_move" not in body


def test_no_feasible_asks_in_spec_order_and_uses_literal_singular_copy():
    first = "model.context_window >= 1000000"
    second = "model.max_output_tokens >= 1000000"
    decision = _decision(status="no_feasible", results=[], answer=None, relax=[first, second],
                         relax_single={"status": "found", "gates": [
                             {"condition": second, "admits": 7}, {"condition": first, "admits": 1},
                         ], "together_admits": 9, "question_admits": False})
    inp = next_move_input_from_decision(decision, _spec(where=[first, second], task_type="review"))
    assert build_next_move(inp) == {
        "kind": "ask_user",
        "say": "Next step: which one of these requirements can change? ModelSpec will decide again with the rest kept as you set them.",
        "options": ["Drop model.context_window >= 1000000: 1 model qualifies.",
                    "Drop model.max_output_tokens >= 1000000: 7 models qualify."],
        "steps": [], "candidates": [], "candidates_total": 0,
    }


def test_no_single_drop_lists_every_hard_gate_in_order():
    decision = _decision(status="no_feasible", results=[], answer=None, relax=["model.class = transcriber"],
                         relax_single={"status": "none", "gates": [], "together_admits": 0,
                                       "question_admits": False})
    spec = _spec(where=["model.class = transcriber", "model.context_window >= 1000000",
                        "model.max_output_tokens >= 8000 soft(0.1)"])
    assert build_next_move(next_move_input_from_decision(decision, spec)) == {
        "kind": "ask_user",
        "say": "Next step: which of these requirements can change? No single change admits a model, so more than one has to give.",
        "options": ["Change model.class = transcriber.", "Change model.context_window >= 1000000."],
        "steps": [], "candidates": [], "candidates_total": 0,
    }


def test_partial_tie_tests_members_and_unknowns_alphabetically():
    decision = _decision(status="partial", answer=_tied(["lab/z", "lab/b"]),
                         may_qualify=[{"model": "lab/c", "unknown": ["reasoning"]},
                                      {"model": "lab/a", "unknown": ["licence.commercial_use"]},
                                      {"model": "lab/a", "unknown": ["reasoning"]}])
    assert build_next_move(next_move_input_from_decision(decision, _spec())) == {
        "kind": "decide_by_testing",
        "say": "Next step: ModelSpec lacks licence.commercial_use and reasoning values for some candidates, so decide by testing these 4 candidates on your own work.",
        "options": [], "steps": STEPS,
        "candidates": ["lab/a", "lab/b", "lab/c", "lab/z"], "candidates_total": 4,
    }


@pytest.mark.parametrize("task,quality", [("review", "review quality"), ("bug_fix", "bug fix quality")])
def test_unmeasured_task_precedes_partial_and_tiebreak(task, quality):
    inp = NextMoveInput("partial", answer_kind="tied", answer_members=("lab/b", "lab/a"),
                        may_qualify=(("lab/c", ("reasoning",)),), task_type=task,
                        not_applied=("eu_residency",))
    move = build_next_move(inp)
    assert move == {
        "kind": "decide_by_testing",
        "say": f"Next step: ModelSpec does not measure {quality} and eu_residency, so decide by testing these 3 candidates on your own work.",
        "options": [], "steps": STEPS,
        "candidates": ["lab/a", "lab/b", "lab/c"], "candidates_total": 3,
    }
    assert build_next_move(NextMoveInput("answered", answer_kind="tied", answer_members=("lab/a", "lab/b"),
                                         task_type="review"))["kind"] == "decide_by_testing"


def test_hardware_gate_uses_exact_hardware_steps_even_on_a_tie():
    spec = _spec(where=[{"facet": "model.fits_hardware", "in": ["nvidia_dgx_spark"]}])
    decision = _decision(answer=_tied(["lab/b", "lab/a"]))
    assert build_next_move(next_move_input_from_decision(decision, spec)) == {
        "kind": "decide_by_testing",
        "say": "Next step: ModelSpec does not measure fit on nvidia_dgx_spark for your quantization, context length and runtime, so decide by testing these 2 candidates on your own work.",
        "options": [],
        "steps": [
            "Load each candidate on your hardware at the quantization, context length and runtime you plan to use.",
            "Drop any candidate that fails to load or leaves no memory headroom under your real context length.",
            "Run 10 to 20 real examples on the rest and record pass or fail and speed.",
            "Choose the candidate that passes most often at a speed you accept.",
        ],
        "candidates": ["lab/a", "lab/b"], "candidates_total": 2,
    }


def test_null_answer_deduplicates_feasible_models_and_has_no_rank():
    inp = NextMoveInput("answered", feasible_models=("lab/z", "lab/a", "lab/z"),
                        may_qualify=(("lab/b", ("reasoning",)),))
    assert build_next_move(inp) == {
        "kind": "decide_by_testing",
        "say": "Next step: ModelSpec has no answer here, so decide by testing these 3 candidates on your own work.",
        "options": [], "steps": STEPS,
        "candidates": ["lab/a", "lab/b", "lab/z"], "candidates_total": 3,
    }


@pytest.mark.parametrize("models,total", [((), 0), (("lab/only",), 1)])
def test_fewer_than_two_candidates_never_names_one(models, total):
    assert build_next_move(NextMoveInput("answered", feasible_models=models)) == {
        "kind": "decide_by_testing",
        "say": "Next step: ModelSpec has no answer here, so decide by testing the models that meet your requirements on your own work.",
        "options": [], "steps": STEPS, "candidates": [], "candidates_total": total,
    }


def test_candidates_are_capped_after_sorting_and_total_is_full():
    move = build_next_move(NextMoveInput("answered", answer_kind="tied",
                                         answer_members=tuple(f"lab/m{i:02d}" for i in range(11, 0, -1))))
    assert move["candidates"] == ["lab/m01", "lab/m02", "lab/m03", "lab/m04", "lab/m05", "lab/m06", "lab/m07", "lab/m08"]
    assert move["candidates_total"] == 11
    assert move["say"] == "Next step: these 11 models tie on the evidence, so the choice is yours on something other than quality: a provider you already use, lower cost per task, or lower latency."


@pytest.mark.parametrize("where,status", [([], "answered"), (["model.max_output_tokens >= 8000"], "partial")])
def test_null_and_partial_candidates_use_all_feasible_models_before_rank_and_limit(where, status):
    from decision.snapshot import SnapshotInputs, build_snapshot, load_snapshot_bytes
    from tests.snapshot_records import SOURCES, fact, model

    models = []
    for index in range(1, 13):
        mid = f"lab/m{index:02d}"
        facts = [fact("model", mid, "model.context_window", index * 10000),
                 fact("model", mid, "model.parameters_total", index * 1000000)]
        if index != 2:
            facts.append(fact("model", mid, "model.max_output_tokens", 8000))
        models.append(model(mid, facts=facts))
    built = build_snapshot(SnapshotInputs(models=models, sources=SOURCES), as_of=date(2026, 9, 25))
    snapshot = load_snapshot_bytes(built.to_bytes(key=b"candidate-test"), key=b"candidate-test")
    bodies = []
    for limit in (3, 10):
        spec = _spec(task_type="review", where=where, limit=limit, optimize={"lexicographic": [
            {"max": "model.context_window"}, {"max": "model.parameters_total"},
        ]})
        decision = decide(spec, snapshot, facets=facet)
        assert decision.status == status
        assert decision.answer is None
        assert len(decision.results) == limit
        assert decision.results[0].offering.model == "lab/m12"
        assert "_feasible_models" not in decision.model_dump()
        bodies.append(project(decision, ResponseOptions(fields=["model"]), spec=spec, not_applied=[]))
    assert bodies[0]["next_move"] == bodies[1]["next_move"] == {
        "kind": "decide_by_testing",
        "say": "Next step: ModelSpec does not measure review quality, so decide by testing these 12 candidates on your own work.",
        "options": [], "steps": STEPS,
        "candidates": ["lab/m01", "lab/m02", "lab/m03", "lab/m04", "lab/m05", "lab/m06", "lab/m07", "lab/m08"],
        "candidates_total": 12,
    }


def test_answered_tie_offers_only_nonquality_choices():
    assert build_next_move(NextMoveInput("answered", answer_kind="tied", answer_members=("lab/b", "lab/a"))) == {
        "kind": "user_tiebreak",
        "say": "Next step: these 2 models tie on the evidence, so the choice is yours on something other than quality: a provider you already use, lower cost per task, or lower latency.",
        "options": ["A provider you already use: a convenience choice, not a quality choice.",
                    "Lower cost per task: a cost choice, not a quality choice.",
                    "Lower latency: a speed choice, not a quality choice."],
        "steps": [], "candidates": ["lab/a", "lab/b"], "candidates_total": 2,
    }


@pytest.mark.parametrize("objective", [{"min": "offering.cost_per_task"},
                                       {"weights": {"-offering.price.input": 1, "-offering.price.output": 1}}])
def test_cost_only_tie_drops_the_cost_choice(objective):
    inp = next_move_input_from_decision(_decision(answer=_tied(["lab/b", "lab/a"])), _spec(optimize=objective))
    assert build_next_move(inp) == {
        "kind": "user_tiebreak",
        "say": "Next step: these 2 models tie on the evidence, so the choice is yours on something other than quality: a provider you already use, or lower latency.",
        "options": ["A provider you already use: a convenience choice, not a quality choice.",
                    "Lower latency: a speed choice, not a quality choice."],
        "steps": [], "candidates": ["lab/a", "lab/b"], "candidates_total": 2,
    }


@pytest.mark.parametrize("extra", [{}, {"where": ["model.context_window >= 1000000"]},
                                  {"optimize": {"max": "reasoning"}}, {"task_type": "review"}])
def test_both_adapters_build_the_same_move_when_candidates_are_retained(snapshot, extra):  # noqa: F811
    request = {"spec_version": 1, "optimize": {"max": "swe_bench_pro"}, "explain": "none", **extra}
    spec = parse_spec(request, facets=facet)
    decision = decide(spec, snapshot, facets=facet)
    inp = next_move_input_from_decision(decision, spec)
    body = project(decision, ResponseOptions(fields=["model"]), spec=spec, not_applied=[])
    assert build_next_move(next_move_input_from_bounded(request, body)) == build_next_move(inp)


def test_bounded_adapter_accepts_projected_rows_with_gaps_in_rank():
    decision = _decision(answer=_tied(["lab/a", "lab/b"]), results=[_row("lab/a"), _row("lab/b", 2)])
    spec = _spec()
    body = project(decision, ResponseOptions(fields=["model"]), spec=spec, not_applied=[])
    body["results"][1]["rank"] = 4
    assert next_move_input_from_bounded(spec.model_dump(mode="json"), body) == next_move_input_from_decision(decision, spec)


def test_summary_ending_and_next_move_survive_trim_and_drill_down():
    from decision.contract import ModelEvidence

    decision = _decision(
        answer=_tied(["lab/z", "lab/a"]),
        results=[_row("lab/z", evidence=[{"domain": "reasoning", "items": [{
            "benchmark": "gpqa_diamond", "value": 1, "measured_by": "independent", "date": "2026-09-20",
            "date_type": "observed", "directness": "direct", "source": "https://example.org/" + "x" * 20000,
        }]}]), _row("lab/a", 2)],
    )
    spec = _spec(task_type="review", where=[f"facet_{i} >= {i}" for i in range(40)])
    move = build_next_move(next_move_input_from_decision(decision, spec))
    text, _mentions = summarize(decision, spec, next_move=move)
    assert text.endswith("Next step: ModelSpec does not measure review quality, so decide by testing these 2 candidates on your own work.")
    assert len(text.encode()) <= SUMMARY_BYTES
    body = project(decision, ResponseOptions(fields=["evidence"]), spec=spec, not_applied=[])
    assert body["summary_for_user"] == text
    assert body["next_move"] == move
    assert "next_move" not in body["explanation"]["omitted"]
    assert body["explanation"]["omitted"]["results.evidence"] == 1
    assert compact_bytes(body) <= AGENT_BYTES
    assert mcp_text_bytes(body) <= AGENT_BYTES
    detail = ModelEvidence(model="lab/z", status="ranked", offering={"model": "lab/z"})
    drilled = project(decision, ResponseOptions(fields=["model"]), spec=spec, not_applied=[], detail=detail)
    assert drilled["next_move"] == move
    assert drilled["summary_for_user"] == text
    repeated = project(decision, ResponseOptions(fields=["evidence"]), spec=spec, not_applied=[])
    assert json.dumps(repeated, separators=(",", ":")).encode() == json.dumps(body, separators=(",", ":")).encode()


def test_summary_guard_refuses_an_invalid_unbounded_ending_instead_of_clipping_it():
    decision = _decision(answer=_tied(["lab/a", "lab/b"]))
    with pytest.raises(SpecError, match="next_move say and answer statement exceed"):
        summarize(decision, _spec(), next_move={"say": "x" * 1500})


def test_objective_without_values_tests_may_qualify_models_even_with_hard_gates():
    decision = _decision(status="no_feasible", results=[], answer=None,
                         relax=["no values for ai2d"],
                         may_qualify=[{"model": "lab/z", "unknown": ["ai2d"]},
                                      {"model": "lab/a", "unknown": ["ai2d"]}])
    spec = _spec(optimize={"max": "ai2d"}, where=["model.class = text-generator"], task_type="review")
    assert build_next_move(next_move_input_from_decision(decision, spec)) == {
        "kind": "decide_by_testing",
        "say": "Next step: ModelSpec lacks ai2d values for every model that meets your requirements, so decide by testing these 2 candidates on your own work.",
        "options": [], "steps": STEPS,
        "candidates": ["lab/a", "lab/z"], "candidates_total": 2,
    }


def test_hardware_skus_are_one_need_joined_as_alternatives():
    spec = _spec(where=[{"facet": "model.fits_hardware", "in": [
        "apple_m4", "apple_m5_max", "nvidia_dgx_spark",
    ]}])
    move = build_next_move(next_move_input_from_decision(_decision(answer=_tied(["lab/a", "lab/b"])), spec))
    assert move["say"] == "Next step: ModelSpec does not measure fit on apple_m4, apple_m5_max or nvidia_dgx_spark for your quantization, context length and runtime, so decide by testing these 2 candidates on your own work."


def test_hardware_skus_are_alphabetical_and_count_devices_after_the_first_three():
    spec = _spec(where=[{"facet": "model.fits_hardware", "in": [
        "nvidia_dgx_spark", "apple_m5_max", "apple_m4", "apple_m5_max", "amd_rx_7900_xt",
    ]}])
    move = build_next_move(next_move_input_from_decision(_decision(answer=_tied(["lab/a", "lab/b"])), spec))
    assert move["say"] == "Next step: ModelSpec does not measure fit on amd_rx_7900_xt, apple_m4, apple_m5_max or 1 more device for your quantization, context length and runtime, so decide by testing these 2 candidates on your own work."


@pytest.mark.parametrize("gate", [
    {"facet": "model.fits_hardware", "in": ["nvidia_dgx_spark"], "soft": {"penalty": 0.1}},
    {"all": [{"facet": "model.fits_hardware", "in": ["nvidia_dgx_spark"]},
             {"facet": "model.context_window", "op": ">=", "value": 8000}], "soft": {"penalty": 0.1}},
])
def test_soft_hardware_does_not_add_a_need_or_hardware_steps(gate):
    decision = _decision(status="partial", answer=None,
                         may_qualify=[{"model": "lab/b", "unknown": ["reasoning"]}])
    move = build_next_move(next_move_input_from_decision(decision, _spec(where=[gate])))
    assert move == {
        "kind": "decide_by_testing",
        "say": "Next step: ModelSpec lacks reasoning values for some candidates, so decide by testing these 2 candidates on your own work.",
        "options": [], "steps": STEPS,
        "candidates": ["lab/a", "lab/b"], "candidates_total": 2,
    }


def test_only_three_needs_are_shown_and_the_rest_are_counted():
    move = build_next_move(NextMoveInput("answered", answer_kind="tied", answer_members=("lab/a", "lab/b"),
                                         task_type="review", not_applied=("eu_residency", "privacy", "safety", "eu_residency")))
    assert move["say"] == "Next step: ModelSpec does not measure review quality and eu_residency and privacy and 1 more, so decide by testing these 2 candidates on your own work."


def test_maximum_length_needs_and_an_oversized_need_fit_the_summary():
    decision = _decision(answer=_tied(["lab/a", "lab/b"]))
    needs = ["a" * 190, "b" * 190, "c" * 199, "d"]
    move = build_next_move(next_move_input_from_decision(decision, _spec(), not_applied=needs))
    expected_needs = "a" * 190 + " and " + "b" * 190 + " and " + "c" * 199 + " and 1 more"
    assert len(expected_needs.encode()) == NEEDS_BYTES == 600
    assert move["say"] == "Next step: ModelSpec does not measure " + expected_needs + ", so decide by testing these 2 candidates on your own work."
    body = project(decision, ResponseOptions(fields=["model"]), spec=_spec(), not_applied=needs)
    assert body["next_move"] == move
    assert body["summary_for_user"].endswith(move["say"])
    assert len(body["summary_for_user"].encode()) <= SUMMARY_BYTES
    oversized = project(decision, ResponseOptions(fields=["model"]), spec=_spec(task_type="review"),
                        not_applied=["x" * 1500])
    assert oversized["next_move"]["say"] == "Next step: ModelSpec does not measure review quality and 1 more, so decide by testing these 2 candidates on your own work."
    assert len(oversized["summary_for_user"].encode()) <= SUMMARY_BYTES


@pytest.mark.parametrize("inp", [
    NextMoveInput("answered", answer_kind="tied", answer_members=("lab/a", "lab/b"),
                  not_applied=("x" * 1500,)),
    NextMoveInput("partial", may_qualify=(("lab/a", ("x" * 1500,)),)),
])
def test_a_need_that_cannot_be_shown_is_refused_instead_of_showing_only_a_count(inp):
    with pytest.raises(SpecError, match="next_move needs exceed"):
        build_next_move(inp)


@pytest.mark.parametrize("spec,expected", [
    (_spec(optimize={"max": "reasoning"}), "Next step: ModelSpec lacks reasoning values for some candidates, so decide by testing these 2 candidates on your own work."),
    (None, "Next step: ModelSpec has no answer here, so decide by testing these 2 candidates on your own work."),
])
def test_missing_dimension_falls_back_to_the_objective_then_null(spec, expected):
    decision = _decision(status="partial", answer=None,
                         may_qualify=[{"model": "lab/b", "unknown": []}])
    assert build_next_move(next_move_input_from_decision(decision, spec))["say"] == expected


def test_oversized_decision_preserves_reporting_fields_and_counts_removed_records():
    decision = _decision(
        answer=_tied(["lab/a", "lab/b"]),
        results=[_row(model, rank, evidence=[{"domain": "reasoning", "items": [{
            "benchmark": "gpqa_diamond", "value": 1, "measured_by": "independent", "date": "2026-09-20",
            "date_type": "observed", "directness": "direct", "source": "https://example.org/" + "x" * 20000,
        }]}]) for rank, model in enumerate(["lab/a", "lab/b"] + [f"lab/m{i}" for i in range(10)], 1)],
        may_qualify=[{"model": f"lab/unknown{i}", "unknown": ["reasoning"]} for i in range(15)],
    )
    spec = _spec()
    move = build_next_move(next_move_input_from_decision(decision, spec))
    summary, mentions = summarize(decision, spec, next_move=move)
    expected = {"next_move": move, "summary_for_user": summary, "must_mention": mentions}
    body = project(decision, ResponseOptions(fields=["evidence"]), spec=spec, not_applied=[])
    actual = {key: body[key] for key in expected}
    assert json.dumps(actual, ensure_ascii=False, separators=(",", ":")).encode() == json.dumps(expected, ensure_ascii=False, separators=(",", ":")).encode()
    assert compact_bytes(body) <= AGENT_BYTES
    assert mcp_text_bytes(body) <= AGENT_BYTES
    assert len(body["results"]) == 1
    assert body["results"][0]["model"] == "lab/a"
    assert body["may_qualify"] == []
    assert "evidence" not in body["results"][0]
    omitted = body["explanation"]["omitted"]
    assert omitted == {"results": 11, "may_qualify": 15, "results.evidence": 1}
    assert omitted["results"] == len(decision.results) - len(body["results"])
    assert omitted["may_qualify"] == len(decision.may_qualify) - len(body["may_qualify"])
    retained_models = {row["model"] for row in body["results"]}
    removed_evidence = sum(len(row.evidence) for row in decision.results if row.offering.model in retained_models)
    removed_evidence -= sum(len(row.get("evidence", [])) for row in body["results"])
    assert omitted["results.evidence"] == removed_evidence
