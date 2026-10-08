"""MODEL-339: the bounded summary is a deterministic report of the Decision."""

from __future__ import annotations

import re

from pathlib import Path

from decision.bounded import AGENT_BYTES, mcp_text_bytes, project
from decision.contract import Decision, ModelEvidence, ResponseOptions, parse_spec, render_condition
from decision.summary import (
    MUST_MENTION_ITEM_BYTES,
    MUST_MENTION_MAX,
    SUMMARY_BYTES,
    summarize,
)

BASIS = "leader-overlap score intervals; capability estimates use 80% intervals"
TIE_BREAKERS = {
    "cheapest": None,
    "open_weights": None,
    "most_independently_measured": None,
    "fastest": None,
}
ORDERING = ("better", "worse", "best", "top", "recommended", "leader", "first", "rank", "winner")
NO_FEASIBLE = "ModelSpec found no model that meets every requirement, so it names no pick."
PARTIAL = "ModelSpec's answer is incomplete, so it names no pick."
NULL_ANSWER = "ModelSpec has no answer for this request, so it names no pick."
ESTIMATES = "Some values are estimates, not measurements."
PROXY = (
    "The evidence for software_engineering is a general proxy (general_bench), not task-specific."
)
MISSING = (
    "lab/a has no leaderboard data for coding_quality; "
    "its position is estimated, not measured."
)
NOT_APPLIED = "eu_residency was not applied; ModelSpec did not check it."
EITHER = "model.weights_openness is not required (either acceptable)."
NO_CLASS = "No model class was required, so results span every class."
COST_ONLY = "This answer is ordered by cost only; it is not a quality ranking."
TIE_COST = "Tie-breakers are conditional; cost order is not quality order."
TIE_THREE = (
    "ModelSpec's answer is a tie among lab/a, lab/b, and lab/c; "
    "the evidence does not separate them."
)
LINEUP_3 = (
    "ModelSpec compared only the models in its lineup; "
    "3 active catalogue models are outside it."
)


def _evidence(directness: str = "proxy", benchmark: str = "general_bench", source: str | None = None) -> dict:
    return {
        "benchmark": benchmark,
        "value": 1.0,
        "measured_by": "independent",
        "date": "2026-09-20",
        "date_type": "observed",
        "source": source or "https://example.org/leaderboard",
        "directness": directness,
    }


def _row(model: str, rank: int = 1, **extra) -> dict:
    row = {"rank": rank, "offering": {"model": model}, "warnings": extra.pop("warnings", [])}
    row.update(extra)
    return row


def _decision(**overrides) -> Decision:
    base = {
        "contract_version": "2.14",
        "decision_id": "dec_01J8ZK3Q7Y",
        "snapshot": "snap_2026-09-24T06:00Z",
        "spec_hash": "sha256:" + "0" * 64,
        "explain": "summary",
        "status": "answered",
        "results": [_row("lab/a")],
        "relax": [],
        "warnings": [],
    }
    base.update(overrides)
    return Decision.model_validate(base)


def _separated(model: str):
    return {
        "kind": "separated",
        "members": [model],
        "leader": model,
        "basis": BASIS,
        "tie_breakers": TIE_BREAKERS,
        "deterministic_order": [model],
    }


def _tied(models: list[str]):
    return {
        "kind": "tied",
        "members": models,
        "basis": BASIS,
        "tie_breakers": TIE_BREAKERS,
        "deterministic_order": models,
    }


def _spec(**extra):
    raw = {"spec_version": 1, "optimize": {"max": "software_engineering"}, "where": []}
    raw.update(extra)
    return parse_spec(raw, facets=None)


def _answer_sentence(text: str) -> str:
    return text.split(". ", 1)[0]


def test_a_tie_names_every_member_and_does_not_order_them() -> None:
    models = ["lab/a", "lab/b", "lab/c"]
    evidence = [{"domain": "software_engineering", "items": [_evidence()]}]
    decision = _decision(
        results=[_row(model, rank, evidence=evidence) for rank, model in enumerate(models, 1)],
        answer=_tied(models),
    )
    spec = _spec(where=["model.class = text-generator"])
    text, mentions = summarize(decision, spec)
    assert text == (
        f"{TIE_THREE} Requirements applied: model.class = text-generator. "
        "No single winner: 3 models are tied. "
        f"{PROXY}"
    )
    assert mentions == ["No single winner: 3 models are tied.", PROXY]
    sentence = _answer_sentence(text)
    assert sentence == TIE_THREE.rstrip(".")
    for word in ORDERING:
        assert re.search(rf"\b{word}\b", sentence, re.I) is None
    assert "you must" not in text and "do not" not in text
    assert re.search(r"\bpresent\b", text, re.I) is None


def test_a_long_tie_names_eight_and_counts_the_rest() -> None:
    models = [f"lab/m{i}" for i in range(1, 11)]
    decision = _decision(
        results=[_row(model, rank) for rank, model in enumerate(models, 1)],
        answer=_tied(models),
    )
    text, mentions = summarize(decision, _spec(optimize={"min": "offering.cost_per_task"}))
    assert _answer_sentence(text) == (
        "ModelSpec's answer is a tie among lab/m1, lab/m2, lab/m3, lab/m4, lab/m5, "
        "lab/m6, lab/m7, and lab/m8, and 2 more in answer.members; "
        "the evidence does not separate them"
    )
    assert text == (
        "ModelSpec's answer is a tie among lab/m1, lab/m2, lab/m3, lab/m4, lab/m5, "
        "lab/m6, lab/m7, and lab/m8, and 2 more in answer.members; "
        "the evidence does not separate them. "
        f"No single winner: 10 models are tied. {NO_CLASS} {COST_ONLY}"
    )
    assert mentions == [
        "No single winner: 10 models are tied.",
        NO_CLASS,
        COST_ONLY,
    ]
    for word in ("better", "worse", "best", "recommended"):
        assert word not in _answer_sentence(text)


def test_no_feasible_names_no_pick_and_keeps_the_relax_suggestions() -> None:
    relax = ["offering.region = eu", "model.class = text-generator"]
    decision = _decision(status="no_feasible", results=[], answer=None, relax=relax)
    spec = _spec(where=relax, optimize={"min": "offering.cost_per_task"})
    text, mentions = summarize(decision, spec)
    assert text == (
        f"{NO_FEASIBLE} These requirements together exclude every model: "
        "offering.region = eu; model.class = text-generator. "
        "Relaxing offering.region = eu and model.class = text-generator together "
        "would admit a model; that is an option, not an answer. "
        "Requirements applied: offering.region = eu; model.class = text-generator."
    )
    assert mentions == []
    assert "tied" not in text
    assert "lab/" not in text
    for word in ("top", "best", "recommended"):
        assert re.search(rf"\b{word}\b", text, re.I) is None


def test_three_relaxations_use_the_tie_list_in_one_option() -> None:
    relax = [
        "offering.region = eu",
        "model.context_window <= 100000",
        "offering.price.input <= 0.2",
    ]
    decision = _decision(status="no_feasible", results=[], answer=None, relax=relax)
    text, _mentions = summarize(decision, _spec(where=relax, optimize={"min": "offering.cost_per_task"}))
    assert (
        "Relaxing offering.region = eu, model.context_window <= 100000, "
        "and offering.price.input <= 0.2 together would admit a model; "
        "that is an option, not an answer."
    ) in text
    assert text.count("would admit a model") == 1


def test_a_covered_relaxation_stays_out_of_the_joint_option() -> None:
    decision = _decision(
        status="no_feasible",
        results=[],
        answer=None,
        relax=["offering.price.input <= 0.5", "offering.region = eu"],
        relax_to=[{
            "condition": "offering.price.input <= 0.5",
            "relaxed": "offering.price.input <= 0.75",
            "facet": "offering.price.input",
            "value": 0.75,
            "admits": 1,
        }],
    )
    text, _mentions = summarize(
        decision,
        _spec(where=["offering.price.input <= 0.5", "offering.region = eu"]),
    )
    assert (
        "Relaxing offering.price.input <= 0.5 to offering.price.input <= 0.75 "
        "would admit a model; that is an option, not an answer."
    ) in text
    assert (
        "Relaxing offering.region = eu would admit a model; that is an option, not an answer."
    ) in text
    assert "together would admit" not in text


def test_missing_objective_values_are_not_reported_as_a_gate_failure() -> None:
    decision = _decision(
        status="no_feasible",
        results=[],
        answer=None,
        relax=["no complete objective values"],
        may_qualify=[{"model": "lab/a", "unknown": ["offering.cost_per_task"]}],
    )
    spec = _spec(
        where=["model.class = text-generator"],
        optimize={"min": "offering.cost_per_task"},
    )
    text, mentions = summarize(decision, spec)
    missing = (
        "No model that meets the requirements has complete values for the objective "
        "(offering.cost_per_task), so ModelSpec cannot order them."
    )
    qualify = (
        "1 more model may qualify, but ModelSpec lacks its values "
        "for these requirements."
    )
    assert text == (
        f"{NO_FEASIBLE} {missing} "
        "Requirements applied: model.class = text-generator. "
        f"{qualify}"
    )
    assert "exclude every model" not in text
    assert "that is an option, not an answer." not in text
    assert "Relaxing " not in text
    assert "no complete objective values" not in text
    assert "no complete objective values" not in " ".join(mentions)
    assert qualify in mentions


def test_partial_names_no_pick_and_counts_models_that_may_qualify() -> None:
    decision = _decision(
        status="partial",
        answer=_separated("lab/a"),
        may_qualify=[{"model": "lab/maybe", "unknown": ["licence.commercial_use"]}],
    )
    text, mentions = summarize(decision, _spec(optimize={"min": "offering.cost_per_task"}))
    assert text == (
        f"{PARTIAL} What is missing: licence.commercial_use. "
        "1 more model may qualify, but ModelSpec lacks its values "
        "for these requirements. "
        f"{NO_CLASS} {COST_ONLY}"
    )
    assert text.count(
        "1 more model may qualify, but ModelSpec lacks its values "
        "for these requirements."
    ) == 1
    assert mentions == [
        NO_CLASS,
        COST_ONLY,
        "1 more model may qualify, but ModelSpec lacks its values for these requirements.",
    ]
    assert "tied" not in text
    assert "lab/a" not in text and "lab/maybe" not in text
    for word in ("top", "best", "recommended"):
        assert re.search(rf"\b{word}\b", text, re.I) is None


def test_an_unapplied_requirement_is_not_described_as_applied() -> None:
    decision = _decision(
        answer=_separated("lab/a"),
        results=[_row(
            "lab/a",
            estimates=[{"domain": "software_engineering", "value": 0.5, "interval": [0.4, 0.6]}],
        )],
    )
    spec = _spec(capabilities={"eu_residency": "required", "software_engineering": "required"})
    text, mentions = summarize(decision, spec, not_applied=["eu_residency"])
    unmeasured = (
        "lab/a has no leaderboard data for software_engineering; "
        "its position is estimated, not measured."
    )
    assert text == (
        "ModelSpec's answer is lab/a. "
        "Requirements applied: software_engineering is required. "
        "Requirements not applied (ModelSpec did not check them): eu_residency. "
        f"{NO_CLASS} {unmeasured} {ESTIMATES}"
    )
    assert NOT_APPLIED not in text
    assert mentions == [
        NO_CLASS,
        unmeasured,
        NOT_APPLIED,
        ESTIMATES,
    ]
    assert "eu_residency is required" not in text
    assert "you must" not in text and "do not" not in text
    assert re.search(r"\bpresent\b", text, re.I) is None


def test_either_weights_openness_is_echoed_as_not_required() -> None:
    decision = _decision(answer=_separated("lab/a"))
    spec = _spec(
        where=["model.weights_openness in {open_weights, closed_weights}"],
        optimize={"min": "offering.cost_per_task"},
    )
    text, mentions = summarize(decision, spec)
    assert text == (
        f"ModelSpec's answer is lab/a. {EITHER} {NO_CLASS} {COST_ONLY}"
    )
    assert mentions == [NO_CLASS, COST_ONLY]
    assert "closed_weights" not in text
    assert "open_weights = false" not in text
    assert "closed weights required" not in text


def test_negated_or_compound_openness_is_echoed_exactly() -> None:
    decision = _decision(answer=_separated("lab/a"))
    where = [
        "not(model.weights_openness in {open_weights, closed_weights})",
        "all(model.weights_openness in {open_weights, closed_weights}; "
        "model.weights_openness = closed_weights)",
        "model.weights_openness in {open_weights, closed_weights} unknown(fail)",
    ]
    spec = _spec(where=where, optimize={"min": "offering.cost_per_task"})
    text, _mentions = summarize(decision, spec)
    echoed = "; ".join(render_condition(condition) for condition in spec.where)
    assert text == (
        "ModelSpec's answer is lab/a. "
        f"Requirements applied: {echoed}. "
        f"{NO_CLASS} {COST_ONLY}"
    )
    assert EITHER not in text


def test_a_closed_weights_comparison_stays_a_hard_requirement() -> None:
    decision = _decision(answer=_separated("lab/a"))
    spec = _spec(
        where=["model.weights_openness = closed_weights"],
        optimize={"min": "offering.cost_per_task"},
    )
    text, _mentions = summarize(decision, spec)
    assert text == (
        "ModelSpec's answer is lab/a. "
        "Requirements applied: model.weights_openness = closed_weights. "
        f"{NO_CLASS} {COST_ONLY}"
    )


def test_a_preference_for_false_stays_false() -> None:
    decision = _decision(answer=_separated("lab/a"))
    spec = _spec(optimize={"weights": {"licence.commercial_use": {"prefer": False, "weight": 1}}})
    text, mentions = summarize(decision, spec)
    assert "licence.commercial_use prefers false" in text
    assert NO_CLASS in text and NO_CLASS in mentions
    assert COST_ONLY not in text
    assert "closed_weights" not in text


def test_models_that_share_a_dimension_set_share_one_leaderboard_sentence() -> None:
    models = ["lab/b", "lab/a", "lab/c"]
    decision = _decision(
        answer=_tied(models),
        results=[
            _row("lab/b", 1, contributions=[
                {"dimension": "coding_quality", "value": None},
                {"dimension": "chat_preference", "value": 0.2, "raw_value": 10.0, "unit": "percent"},
            ]),
            _row("lab/a", 2, contributions=[
                {"dimension": "coding_quality", "value": None},
                {"dimension": "chat_preference", "value": 0.3, "raw_value": 12.0, "unit": "percent"},
            ]),
            _row("lab/c", 3, contributions=[
                {"dimension": "coding_quality", "value": 0.4, "raw_value": 20.0, "unit": "percent"},
                {"dimension": "chat_preference", "value": None},
            ]),
        ],
    )
    text, mentions = summarize(
        decision,
        _spec(optimize={"weights": {"coding_quality": 0.5, "chat_preference": 0.5}}),
    )
    shared = (
        "lab/b and lab/a have no leaderboard data for coding_quality; "
        "their positions are estimated, not measured."
    )
    alone = (
        "lab/c has no leaderboard data for chat_preference; "
        "its position is estimated, not measured."
    )
    assert shared in mentions and shared in text
    assert alone in mentions and alone in text
    assert text.index(shared) < text.index(alone)
    assert text.count("has no leaderboard data") == 1
    assert text.count("have no leaderboard data") == 1


def test_three_models_use_the_tie_list_in_one_leaderboard_sentence() -> None:
    models = ["lab/a", "lab/b", "lab/c"]
    decision = _decision(
        answer=_tied(models),
        results=[
            _row(model, rank, contributions=[{"dimension": "coding_quality", "value": None}])
            for rank, model in enumerate(models, 1)
        ],
    )
    text, mentions = summarize(decision, _spec(optimize={"max": "coding_quality"}))
    sentence = (
        "lab/a, lab/b, and lab/c have no leaderboard data for coding_quality; "
        "their positions are estimated, not measured."
    )
    assert sentence in mentions
    assert sentence in text
    assert text.count(sentence) == 1


def test_a_long_leaderboard_name_list_keeps_the_fixed_wording() -> None:
    models = [f"lab/{'m' * 30}-{index:02d}" for index in range(12)]
    decision = _decision(
        answer=_tied(models),
        results=[
            _row(model, rank, contributions=[{"dimension": "coding_quality", "value": None}])
            for rank, model in enumerate(models, 1)
        ],
    )
    _text, mentions = summarize(decision, _spec(optimize={"max": "coding_quality"}))
    item = next(entry for entry in mentions if "leaderboard data" in entry)
    assert item == (
        "lab/mmmmmmmmmmmmmmmmmmmmmmmmmmmmmm-00 and "
        "lab/mmmmmmmmmmmmmmmmmmmmmmmmmmmmmm-01, and 10 more "
        "have no leaderboard data for coding_quality; "
        "their positions are estimated, not measured."
    )
    assert "…" not in item
    assert len(item.encode("utf-8")) <= MUST_MENTION_ITEM_BYTES


def test_missing_board_data_is_named_for_the_answer_member() -> None:
    decision = _decision(
        answer=_separated("lab/a"),
        results=[_row("lab/a", contributions=[{"dimension": "coding_quality", "value": None}])],
    )
    text, mentions = summarize(decision, _spec(optimize={"max": "coding_quality"}))
    assert text == f"ModelSpec's answer is lab/a. {NO_CLASS} {MISSING}"
    assert mentions == [NO_CLASS, MISSING]


def test_no_class_gate_states_the_scope_and_names_other_classes() -> None:
    decision = _decision(
        answer=_separated("typesafe/jev-1-13"),
        results=[_row("typesafe/jev-1-13"), _row("lab/a", rank=2)],
        top=[
            {
                "offering": {"model": "typesafe/jev-1-13"},
                "facts": [{"facet": "model.class", "value": "decider"}],
            },
            {
                "offering": {"model": "lab/a"},
                "facts": [{"facet": "model.class", "value": "text-generator"}],
            },
        ],
    )
    text, mentions = summarize(decision, _spec(optimize={"min": "offering.cost_per_task"}))
    scope = "No model class was required, so results span every class, including decider."
    assert scope in text
    assert text.count(scope) == 1
    assert "text-generator" not in text
    assert scope in mentions


def test_a_class_gate_is_echoed_exactly() -> None:
    decision = _decision(answer=_separated("lab/a"))
    text, mentions = summarize(decision, _spec(where=["model.class = text-generator"]))
    assert text == (
        "ModelSpec's answer is lab/a. Requirements applied: model.class = text-generator."
    )
    assert mentions == []
    assert "No model class was required" not in text


def test_a_relaxed_gate_is_an_option_and_partial_is_not_a_tie() -> None:
    decision = _decision(
        status="no_feasible",
        results=[],
        answer=None,
        relax=["offering.price.input <= 0.5"],
        relax_to=[{
            "condition": "offering.price.input <= 0.5",
            "relaxed": "offering.price.input <= 0.75",
            "facet": "offering.price.input",
            "value": 0.75,
            "admits": 2,
        }],
    )
    spec = _spec(
        where=["offering.price.input <= 0.5", "model.class = text-generator"],
        optimize={"min": "offering.cost_per_task"},
    )
    text, mentions = summarize(decision, spec)
    assert text == (
        f"{NO_FEASIBLE} These requirements together exclude every model: "
        "offering.price.input <= 0.5; model.class = text-generator. "
        "Relaxing offering.price.input <= 0.5 to offering.price.input <= 0.75 "
        "would admit a model; that is an option, not an answer. "
        "Requirements applied: offering.price.input <= 0.5; model.class = text-generator."
    )
    assert mentions == []
    assert "tied" not in text and "tied" not in " ".join(mentions)
    assert "Relaxing offering.price.input <= 0.5 would admit a model;" not in text

    repeated = _decision(
        status="no_feasible",
        results=[],
        answer=None,
        relax=["offering.price.input <= 0.5"],
        relax_to=[
            {
                "condition": "offering.price.input <= 0.5",
                "relaxed": "offering.price.input <= 0.5",
                "facet": "offering.price.input",
                "value": 0.5,
                "admits": 1,
            },
            {
                "condition": "offering.price.input <= 0.5",
                "relaxed": "offering.price.input <= 0.75",
                "facet": "offering.price.input",
                "value": 0.75,
                "admits": 2,
            },
        ],
    )
    repeated_text, _repeated_mentions = summarize(
        repeated,
        _spec(where=["offering.price.input <= 0.5"], optimize={"min": "offering.cost_per_task"}),
    )
    assert (
        "Relaxing offering.price.input <= 0.5 to offering.price.input <= 0.5 "
        "would admit a model; that is an option, not an answer."
    ) in repeated_text
    assert (
        "Relaxing offering.price.input <= 0.5 to offering.price.input <= 0.75 "
        "would admit a model; that is an option, not an answer."
    ) in repeated_text
    assert "Relaxing offering.price.input <= 0.5 would admit a model;" not in repeated_text
    same = _decision(
        status="no_feasible",
        results=[],
        answer=None,
        relax=["offering.price.input <= 0.5"],
        relax_to=[{
            "condition": "offering.price.input <= 0.5",
            "relaxed": "offering.price.input <= 0.5",
            "facet": "offering.price.input",
            "value": 0.5,
            "admits": 1,
        }],
    )
    same_text, _same_mentions = summarize(
        same, _spec(where=["offering.price.input <= 0.5"]),
    )
    assert (
        "Relaxing offering.price.input <= 0.5 to offering.price.input <= 0.5 "
        "would admit a model; that is an option, not an answer."
    ) in same_text
    assert "Relaxing offering.price.input <= 0.5 would admit a model;" not in same_text

    partial = _decision(
        status="partial",
        answer=_tied(["lab/a", "lab/b"]),
        may_qualify=[{"model": "lab/maybe", "unknown": ["licence.commercial_use"]}],
    )
    partial_text, partial_mentions = summarize(
        partial, _spec(where=["model.class = text-generator"]),
    )
    assert partial_text.startswith(PARTIAL)
    assert "tied" not in partial_text
    assert "tie" not in partial_text.lower()
    assert all("tied" not in item and "tie" not in item.lower() for item in partial_mentions)


def test_an_estimated_position_is_not_leaderboard_data() -> None:
    latent = _decision(
        answer=_separated("lab/a"),
        results=[_row("lab/a", contributions=[{
            "dimension": "chat_preference",
            "value": 1.0,
            "raw_value": 1.58,
            "unit": "latent capability",
            "formula": "monotone domain evidence estimate",
            "evidence": [_evidence(directness="direct", benchmark="arena_webdev")],
        }])],
    )
    expected = (
        "lab/a has no leaderboard data for chat_preference; "
        "its position is estimated, not measured."
    )
    text, mentions = summarize(
        latent, _spec(where=["model.class = text-generator"], optimize={"max": "chat_preference"}),
    )
    assert text == (
        "ModelSpec's answer is lab/a. "
        f"Requirements applied: model.class = text-generator. {expected}"
    )
    assert mentions == [expected]

    measured = _decision(
        answer=_separated("openai/gpt-6-astra"),
        results=[_row(
            "openai/gpt-6-astra",
            estimates=[{"domain": "software_engineering", "value": 0.5, "interval": [0.4, 0.6]}],
            contributions=[{
                "dimension": "terminal_bench_v4_0",
                "value": 1.0,
                "raw_value": 58.18,
                "unit": "percent",
                "evidence": [_evidence(directness="direct", benchmark="terminal_bench_v4_0")],
            }],
        )],
    )
    measured_text, measured_mentions = summarize(
        measured,
        _spec(where=["model.class = text-generator"], optimize={"max": "terminal_bench_v4_0"}),
    )
    assert "no leaderboard data" not in measured_text
    assert measured_mentions == [ESTIMATES]

    estimated = _decision(
        answer=_separated("lab/a"),
        results=[_row(
            "lab/a",
            estimates=[{"domain": "coding_quality", "value": 0.4, "interval": [0.2, 0.6]}],
        )],
    )
    _, estimated_mentions = summarize(
        estimated,
        _spec(where=["model.class = text-generator"], optimize={"max": "coding_quality"}),
    )
    assert estimated_mentions == [
        MISSING,
        ESTIMATES,
    ]

    top = _decision(
        answer=_separated("lab/measured"),
        results=[
            _row("lab/estimated", rank=1, contributions=[{
                "dimension": "coding_quality",
                "value": 1.0,
                "unit": "latent capability",
                "formula": "monotone domain evidence estimate",
            }]),
            _row("lab/measured", rank=2, contributions=[{
                "dimension": "coding_quality",
                "value": 0.5,
                "raw_value": 40.0,
                "unit": "percent",
            }]),
        ],
    )
    _, top_mentions = summarize(
        top, _spec(where=["model.class = text-generator"], optimize={"max": "coding_quality"}),
    )
    assert top_mentions == [
        "lab/estimated has no leaderboard data for coding_quality; "
        "its position is estimated, not measured."
    ]


def test_cost_only_is_not_a_quality_ranking_and_a_cost_tie_break_says_so() -> None:
    decision = _decision(answer=_separated("lab/a"))
    text, mentions = summarize(decision, _spec(optimize={"min": "offering.cost_per_task"}))
    assert text == f"ModelSpec's answer is lab/a. {NO_CLASS} {COST_ONLY}"
    assert text.count(COST_ONLY) == 1
    assert mentions == [NO_CLASS, COST_ONLY]

    infeasible = _decision(status="no_feasible", answer=None, results=[], relax=["model.context_window >= 10"])
    _text, infeasible_mentions = summarize(infeasible, _spec(optimize={"min": "offering.cost_per_task"}))
    assert infeasible_mentions == [NO_CLASS]

    mixed = _decision(
        answer=_separated("lab/a"),
        reading={"do_not_claim": ["Do not claim a quality rank from this objective."]},
    )
    mixed_text, mixed_mentions = summarize(
        mixed,
        _spec(optimize={"weights": {"-offering.cost_per_task": 0.7, "chat_preference": 0.3}}),
    )
    assert COST_ONLY not in mixed_text
    assert COST_ONLY not in mixed_mentions
    assert NO_CLASS in mixed_mentions

    tied = _tied(["lab/a", "lab/b"])
    tied["tie_breakers"] = {**TIE_BREAKERS, "cheapest": "lab/a"}
    tie = _decision(
        results=[_row("lab/a"), _row("lab/b", rank=2)],
        answer=tied,
    )
    tie_text, tie_mentions = summarize(tie, _spec(where=["model.class = text-generator"]))
    assert TIE_COST in tie_text
    assert tie_mentions == ["No single winner: 2 models are tied.", TIE_COST]
    assert COST_ONLY not in tie_text


def test_every_monetary_offering_objective_is_cost_only_and_a_mix_is_not() -> None:
    decision = _decision(answer=_separated("lab/a"))
    monetary = (
        "offering.price.input",
        "offering.price.output",
        "offering.price.cached_input",
        "offering.price.batch_input",
        "offering.price.batch_output",
        "offering.cost_per_task",
        "offering.plan.price_monthly",
    )
    for facet_id in monetary:
        text, mentions = summarize(decision, _spec(optimize={"min": facet_id}))
        assert COST_ONLY in text and COST_ONLY in mentions, facet_id
    speed_text, speed_mentions = summarize(
        decision, _spec(optimize={"min": "offering.speed.throughput"}),
    )
    assert COST_ONLY not in speed_text and COST_ONLY not in speed_mentions
    mixed_text, mixed_mentions = summarize(
        decision,
        _spec(optimize={"weights": {
            "offering.price.cached_input": 0.5,
            "software_engineering": 0.5,
        }}),
    )
    assert COST_ONLY not in mixed_text and COST_ONLY not in mixed_mentions
    prices_text, prices_mentions = summarize(
        decision,
        _spec(optimize={"weights": {
            "offering.price.cached_input": 0.4,
            "offering.price.batch_output": 0.6,
        }}),
    )
    assert COST_ONLY in prices_text and COST_ONLY in prices_mentions


def test_an_answered_decision_with_a_null_answer_names_no_pick() -> None:
    text, mentions = summarize(
        _decision(answer=None), _spec(where=["model.class = text-generator"]),
    )
    assert text == (
        f"{NULL_ANSWER} Requirements applied: model.class = text-generator."
    )
    assert mentions == []
    assert "lab/a" not in text


def test_counts_use_thousands_separators_in_both_fields() -> None:
    decision = _decision(
        answer=_separated("lab/a"),
        out_of_lineup=1328,
        may_qualify=[
            {"model": f"lab/m{index}", "unknown": ["licence.commercial_use"]}
            for index in range(1328)
        ],
    )
    text, mentions = summarize(decision, _spec(where=["model.class = text-generator"]))
    lineup = (
        "ModelSpec compared only the models in its lineup; "
        "1,328 active catalogue models are outside it."
    )
    qualify = (
        "1,328 more models may qualify, but ModelSpec lacks their values "
        "for these requirements."
    )
    assert lineup in mentions and text.count(lineup) == 1
    assert qualify in mentions and text.count(qualify) == 1

    one, one_mentions = summarize(
        _decision(answer=_separated("lab/a"), out_of_lineup=1),
        _spec(where=["model.class = text-generator"]),
    )
    singular = (
        "ModelSpec compared only the models in its lineup; "
        "1 active catalogue model is outside it."
    )
    assert singular in one_mentions and one.count(singular) == 1


def test_the_same_decision_renders_the_same_bytes() -> None:
    decision = _decision(
        answer=_separated("lab/a"),
        results=[_row("lab/a", contributions=[{"dimension": "coding_quality", "value": None}])],
    )
    spec = _spec(optimize={"max": "coding_quality"})
    first = summarize(decision, spec, not_applied=["eu_residency"])
    second = summarize(decision, spec, not_applied=["eu_residency"])
    assert first[0].encode("utf-8") == second[0].encode("utf-8")
    assert first[1] == second[1]


def _overflow() -> tuple[Decision, object, list[str]]:
    requirement = "requirement_" + ("x" * 180)
    unapplied = [f"{requirement}_{i}" for i in range(12)]
    evidence = [{"domain": "software_engineering", "items": [_evidence()]}]
    estimate = {"domain": "software_engineering", "value": 0.2, "interval": [0.1, 0.3]}
    models = ["lab/a", "lab/b"]
    decision = _decision(
        results=[
            _row(model, rank, evidence=evidence, estimates=[estimate])
            for rank, model in enumerate(models, 1)
        ],
        answer=_tied(models),
        may_qualify=[{"model": "lab/maybe", "unknown": ["licence.commercial_use"]}],
        out_of_lineup=3,
        coverage={
            "kind": "out_of_coverage",
            "message": "Outside the board.",
            "snapshot": "snap_2026-09-24T06:00Z",
            "as_of": "2026-10-02",
            "classes": [{"id": "text-generator", "models": 1}],
            "domains": ["software_engineering"],
        },
        reading={"estimates": ["model.fits_hardware", "results.estimates"]},
    )
    return decision, _spec(where=["model.class = text-generator"]), unapplied


def test_must_mention_and_the_paragraph_stay_inside_their_byte_caps() -> None:
    decision, spec, unapplied = _overflow()
    text, mentions = summarize(decision, spec, not_applied=unapplied)
    caveat = " was not applied; ModelSpec did not check it."
    item = mentions[3]
    assert len(mentions) == MUST_MENTION_MAX
    assert mentions[0] == "No single winner: 2 models are tied."
    assert mentions[1] == PROXY
    assert mentions[2] == (
        "lab/a and lab/b have no leaderboard data for software_engineering; "
        "their positions are estimated, not measured."
    )
    assert item.endswith(caveat)
    assert item.startswith("requirement_")
    assert "…" in item.split(caveat, 1)[0]
    assert len(item.encode("utf-8")) <= MUST_MENTION_ITEM_BYTES
    assert not item.endswith("wa…")
    assert mentions[-1] == "and 11 more."
    assert "Outside the board." in mentions
    assert (
        "1 more model may qualify, but ModelSpec lacks its values "
        "for these requirements."
    ) in mentions
    assert LINEUP_3 in mentions
    assert (
        "fits_hardware is an estimate, not a measured fit for a quantization or context workload."
        in mentions
    )
    assert ESTIMATES in mentions
    assert all(len(item.encode("utf-8")) <= MUST_MENTION_ITEM_BYTES for item in mentions)
    assert len(text.encode("utf-8")) <= SUMMARY_BYTES
    assert text.startswith(
        "ModelSpec's answer is a tie among lab/a and lab/b; the evidence does not separate them."
    )
    assert "Requirements not applied (ModelSpec did not check them):" in text
    assert "; and 10 more." in text
    assert "was not applied; ModelSpec did not check it." not in text
    assert PROXY in text and "No single winner: 2 models are tied." in text

    where = [f"facet_{i:02d} >= {i}" for i in range(40)]
    huge = _decision(status="no_feasible", results=[], answer=None, relax=where)
    huge_text, _huge_mentions = summarize(
        huge, _spec(where=where, optimize={"min": "offering.cost_per_task"}),
    )
    assert len(huge_text.encode("utf-8")) <= SUMMARY_BYTES
    assert huge_text.startswith(NO_FEASIBLE)
    assert NO_CLASS in huge_text
    assert huge_text.count(NO_CLASS) == 1
    assert COST_ONLY not in huge_text
    assert huge_text.count("facet_00 >= 0; facet_01 >= 1; facet_02 >= 2; facet_03 >= 3; "
                           "facet_04 >= 4; facet_05 >= 5; facet_06 >= 6; facet_07 >= 7; "
                           "and 32 more.") == 2
    listed = ", ".join(where[:-1]) + ", and " + where[-1]
    assert (
        f"Relaxing {listed} together would admit a model; that is an option, not an answer."
        in huge_text
    )
    assert huge_text.count("would admit a model") == 1
    assert "Relaxing facet_00 >= 0 would admit a model;" not in huge_text
    assert "These are options, not an answer." not in huge_text
    assert "Nearest relaxations" not in huge_text
    assert "tied" not in huge_text
    assert "lab/" not in huge_text


def test_a_long_joint_relaxation_keeps_the_fixed_ending() -> None:
    """Twenty long conditions stay one option, and the ending is not clipped."""
    conditions = [f"facet_{i:02d}_{'x' * 60} >= {i}" for i in range(20)]
    decision = _decision(status="no_feasible", results=[], answer=None, relax=conditions)
    text, _mentions = summarize(
        decision, _spec(where=conditions, optimize={"min": "offering.cost_per_task"}),
    )
    ending = "together would admit a model; that is an option, not an answer."
    assert len(text.encode("utf-8")) <= SUMMARY_BYTES
    assert text.startswith(NO_FEASIBLE)
    assert ending in text
    listed = text.split("Relaxing ", 1)[1].split(ending, 1)[0]
    assert ", and " in listed
    assert listed.rstrip().endswith("more")
    assert sum(condition in listed for condition in conditions) < len(conditions)
    assert "…" not in listed
    assert text.count("would admit a model") == 1


def test_the_api_reference_names_the_summary_fields_on_the_bounded_representation() -> None:
    reference = Path(__file__).resolve().parents[1].joinpath("docs/api.md").read_text(encoding="utf-8")
    bullet = next(
        line for line in reference.splitlines()
        if "decide-api.md" in line and "summary_for_user" in line
    )
    assert "bounded representation" in bullet
    assert "Adds `summary_for_user` and `must_mention`." not in bullet


def test_bounded_responses_keep_the_summary_through_trim_and_drill_down() -> None:
    models = [f"lab/m{i}" for i in range(1, 11)]
    decision, spec, unapplied = _overflow()
    # The longest name list the paragraph spells out, plus rows the budget drops.
    raw = decision.model_dump(mode="json")
    raw["answer"] = _tied(models)
    raw["results"] = [
        *[_row(model, rank) for rank, model in enumerate(models, 1)],
        *[
            _row(
                f"lab/e{index:02d}",
                rank,
                evidence=[{
                    "domain": "software_engineering",
                    "items": [_evidence(source="https://example.org/" + ("a" * 8000))],
                }],
            )
            for rank, index in enumerate(range(25), len(models) + 1)
        ],
    ]
    fat = Decision.model_validate(raw)
    # lab/a and lab/b no longer carry the fixture evidence, so recompute.
    text, mentions = summarize(fat, spec, not_applied=unapplied)
    assert len(mentions) == MUST_MENTION_MAX
    assert text.startswith(
        "ModelSpec's answer is a tie among lab/m1, lab/m2, lab/m3, lab/m4, lab/m5, "
        "lab/m6, lab/m7, and lab/m8, and 2 more in answer.members; "
        "the evidence does not separate them."
    )
    assert text.endswith("and 9 more.")
    assert len(text.encode("utf-8")) <= SUMMARY_BYTES

    body = project(
        fat, ResponseOptions(fields=["model", "evidence"]), not_applied=unapplied, spec=spec,
    )
    assert body["summary_for_user"] == text
    assert body["must_mention"] == mentions
    assert body["explanation"]["omitted"]["results"] == 25
    assert len(body["results"]) < len(fat.results)
    assert mcp_text_bytes(body) <= AGENT_BYTES

    detail = ModelEvidence.model_validate({
        "model": "lab/m1",
        "status": "ranked",
        "offering": {"model": "lab/m1"},
        "rank": 1,
        "evidence": [{
            "domain": "software_engineering",
            "items": [
                _evidence(source="https://example.org/" + ("b" * 4000))
                for _ in range(40)
            ],
        }],
    })
    drilled = project(
        fat, ResponseOptions(fields=["model"]), detail=detail,
        not_applied=unapplied, spec=spec,
    )
    assert drilled["summary_for_user"] == text
    assert drilled["must_mention"] == mentions
    assert drilled["results"] == []
    assert drilled["explanation"]["omitted"]["model_evidence.evidence.items"] > 0
    assert mcp_text_bytes(drilled) <= AGENT_BYTES


def test_a_huge_tie_and_objective_keep_the_leaderboard_item_bounded_and_fast() -> None:
    import time

    from decision.summary import _board_sentence

    models = [f"lab/model-{i:04d}" for i in range(500)]
    dimensions = [f"dimension_{i:04d}" for i in range(2_000)]
    started = time.perf_counter()
    text = _board_sentence(models, dimensions)
    assert time.perf_counter() - started < 0.5
    assert len(text.encode("utf-8")) <= MUST_MENTION_ITEM_BYTES
    assert text.endswith("; their positions are estimated, not measured.")
    assert text.startswith("lab/model-0000")
