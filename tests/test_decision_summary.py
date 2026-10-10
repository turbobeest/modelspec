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
CHECKED_ONLY = "ModelSpec checked only the stated requirements; other needs were not checked."
HARDWARE = (
    "fits_hardware is an estimate; fit for a specific quantization, context length "
    "or runtime headroom is not established."
)
QUALIFY_ONE = (
    "1 more model may qualify, but ModelSpec lacks its values for these requirements."
)
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
        "contract_version": "2.15",
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
    tie = "lab/a, lab/b, and lab/c are tied; this is not a recommendation of any one of them."
    assert text == (
        f"{TIE_THREE} Requirements applied: model.class = text-generator. "
        "These 3 models are tied; this is not a recommendation of any one of them. "
        f"{PROXY} {CHECKED_ONLY}"
    )
    assert mentions == [tie, PROXY, CHECKED_ONLY]
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
    named = (
        "lab/m1, lab/m2, lab/m3, lab/m4, lab/m5, lab/m6, lab/m7, and lab/m8, "
        "and 2 more in answer.members are tied; "
        "this is not a recommendation of any one of them."
    )
    assert text == (
        "ModelSpec's answer is a tie among lab/m1, lab/m2, lab/m3, lab/m4, lab/m5, "
        "lab/m6, lab/m7, and lab/m8, and 2 more in answer.members; "
        "the evidence does not separate them. "
        "These 10 models are tied; this is not a recommendation of any one of them. "
        f"{NO_CLASS} {COST_ONLY} {CHECKED_ONLY}"
    )
    assert mentions == [
        named,
        NO_CLASS,
        COST_ONLY,
        CHECKED_ONLY,
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
        "Requirements applied: offering.region = eu; model.class = text-generator. "
        f"{CHECKED_ONLY}"
    )
    assert mentions == [CHECKED_ONLY]
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


def test_an_emitted_relax_single_gate_drops_the_option_that_names_it() -> None:
    condition = "offering.region = eu"
    decision = _decision(
        status="no_feasible",
        results=[],
        answer=None,
        relax=[condition],
        relax_single={
            "status": "found",
            "gates": [{"condition": condition, "admits": 2}],
            "together_admits": 2,
            "question_admits": False,
        },
    )
    text, _mentions = summarize(decision, _spec(where=[condition]))
    assert (
        "Removing only offering.region = eu would let 2 models qualify; "
        "every other requirement stays as you set it."
    ) in text
    assert (
        "Relaxing offering.region = eu would admit a model; that is an option, not an answer."
    ) not in text

    priced = _decision(
        status="no_feasible",
        results=[],
        answer=None,
        relax=["offering.price.input <= 0.5", condition],
        relax_to=[{
            "condition": "offering.price.input <= 0.5",
            "relaxed": "offering.price.input <= 0.75",
            "facet": "offering.price.input",
            "value": 0.75,
            "admits": 1,
        }],
        relax_single={
            "status": "found",
            "gates": [
                {"condition": "offering.price.input <= 0.5", "admits": 1},
                {"condition": condition, "admits": 2},
            ],
            "together_admits": 2,
            "question_admits": False,
        },
    )
    priced_text, _priced_mentions = summarize(
        priced, _spec(where=["offering.price.input <= 0.5", condition]),
    )
    assert (
        "Relaxing offering.price.input <= 0.5 to offering.price.input <= 0.75 "
        "would admit a model; that is an option, not an answer."
    ) in priced_text
    assert (
        "Relaxing offering.region = eu would admit a model; that is an option, not an answer."
    ) not in priced_text

    pair = ["offering.region = eu", "model.class = text-generator"]
    joint = _decision(
        status="no_feasible",
        results=[],
        answer=None,
        relax=pair,
        relax_single={
            "status": "found",
            "gates": [{"condition": pair[0], "admits": 2}],
            "together_admits": 2,
            "question_admits": False,
        },
    )
    joint_text, _joint_mentions = summarize(joint, _spec(where=pair))
    assert (
        "Relaxing offering.region = eu and model.class = text-generator together "
        "would admit a model; that is an option, not an answer."
    ) in joint_text


def test_a_single_gate_for_a_different_condition_keeps_the_option() -> None:
    decision = _decision(
        status="no_feasible",
        results=[],
        answer=None,
        relax=["offering.region = eu"],
        relax_single={
            "status": "found",
            "gates": [{"condition": "model.context_window >= 8192", "admits": 1}],
            "together_admits": 1,
            "question_admits": False,
        },
    )
    text, _mentions = summarize(
        decision,
        _spec(where=["offering.region = eu", "model.context_window >= 8192"]),
    )
    assert (
        "Relaxing offering.region = eu would admit a model; that is an option, not an answer."
    ) in text
    assert (
        "Removing only model.context_window >= 8192 would let 1 model qualify; "
        "every other requirement stays as you set it."
    ) in text

    conditions = [f"facet_{i:02d} >= {i}" for i in range(13)]
    beyond = _decision(
        status="no_feasible",
        results=[],
        answer=None,
        relax=[conditions[-1]],
        relax_single={
            "status": "found",
            "gates": [{"condition": name, "admits": 2} for name in conditions],
            "together_admits": 2,
            "question_admits": False,
        },
    )
    beyond_text, _beyond_mentions = summarize(beyond, _spec(where=conditions))
    assert (
        "Relaxing facet_12 >= 12 would admit a model; that is an option, not an answer."
    ) in beyond_text
    assert "Removing only facet_12 >= 12" not in beyond_text
    assert (
        "Removing only facet_00 >= 0 would let 2 models qualify; "
        "every other requirement stays as you set it."
    ) in beyond_text


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
        f"{qualify} {CHECKED_ONLY}"
    )
    assert "exclude every model" not in text
    assert "that is an option, not an answer." not in text
    assert "Relaxing " not in text
    assert "no complete objective values" not in text
    assert "no complete objective values" not in " ".join(mentions)
    assert qualify in mentions


def test_a_diagnostic_is_an_objective_failure_only_when_gates_left_candidates() -> None:
    """``optimise([])`` still returns a diagnostic. The funnel says whether anyone passed."""
    excluded = _decision(
        status="no_feasible",
        results=[],
        answer=None,
        relax=["no complete objective values"],
        eliminated={"funnel": [{
            "condition": "model.class = vectoriser",
            "before": 3,
            "after": 0,
        }]},
    )
    text, _mentions = summarize(
        excluded,
        _spec(where=["model.class = vectoriser"], optimize={"max": "arena_elo_overall"}),
    )
    assert (
        "These requirements together exclude every model: model.class = vectoriser."
        in text
    )
    assert "complete values for the objective" not in text
    assert "no complete objective values" not in text
    assert "that is an option, not an answer." not in text

    admitted = _decision(
        status="no_feasible",
        results=[],
        answer=None,
        relax=["no model that meets the requirements has a value for chat_preference"],
        eliminated={"funnel": [{
            "condition": "model.class = text-generator",
            "before": 3,
            "after": 2,
        }]},
    )
    admitted_text, _mentions = summarize(
        admitted,
        _spec(where=["model.class = text-generator"], optimize={"max": "chat_preference"}),
    )
    assert (
        "No model that meets the requirements has complete values for the objective "
        "(chat_preference), so ModelSpec cannot order them."
        in admitted_text
    )
    assert "exclude every model" not in admitted_text


def test_a_supplied_feasible_count_is_used_when_the_funnel_is_absent() -> None:
    """``explain`` ``none`` records no funnel. The count is the optimiser's input."""
    decision = _decision(
        status="no_feasible",
        results=[],
        answer=None,
        relax=["no complete objective values"],
    )
    spec = _spec(where=["model.class = vectoriser"], optimize={"max": "arena_elo_overall"})
    excluded, _mentions = summarize(decision, spec, feasible=0)
    assert (
        "These requirements together exclude every model: model.class = vectoriser."
        in excluded
    )
    assert "complete values for the objective" not in excluded

    admitted, _mentions = summarize(decision, spec, feasible=2)
    assert (
        "No model that meets the requirements has complete values for the objective "
        "(arena_elo_overall), so ModelSpec cannot order them."
        in admitted
    )
    # No count and no funnel: the diagnostic stays an objective failure.
    unknown, _mentions = summarize(decision, spec)
    assert unknown == admitted

    contradicted = _decision(
        status="no_feasible",
        results=[],
        answer=None,
        relax=["no complete objective values"],
        eliminated={"funnel": [{
            "condition": "model.class = vectoriser",
            "before": 3,
            "after": 0,
        }]},
    )
    overridden, _mentions = summarize(contradicted, spec, feasible=2)
    assert overridden == admitted


def test_a_diagnostic_without_a_spec_names_the_objective_the_decision_carries() -> None:
    decision = _decision(
        status="no_feasible",
        results=[],
        answer=None,
        relax=["no complete objective values"],
        may_qualify=[{"model": "lab/a", "unknown": ["offering.cost_per_task"]}],
        eliminated={"funnel": [{
            "condition": "model.class = text-generator",
            "before": 2,
            "after": 1,
        }]},
    )
    text, _mentions = summarize(decision, None)
    assert (
        "No model that meets the requirements has complete values for the objective "
        "(offering.cost_per_task), so ModelSpec cannot order them."
        in text
    )
    assert "exclude every model" not in text


def test_a_diagnostic_without_an_objective_name_keeps_the_gate_sentence() -> None:
    decision = _decision(
        status="no_feasible",
        results=[],
        answer=None,
        relax=["no complete objective values"],
        eliminated={"funnel": [{
            "condition": "model.class = decider",
            "before": 4,
            "after": 1,
        }]},
    )
    text, _mentions = summarize(decision, None)
    assert "These requirements together exclude every model." in text
    assert "complete values for the objective" not in text
    assert "specify a benchmark" not in text


def test_partial_names_no_pick_and_counts_models_that_may_qualify() -> None:
    decision = _decision(
        status="partial",
        answer=_separated("lab/a"),
        may_qualify=[{"model": "lab/maybe", "unknown": ["licence.commercial_use"]}],
    )
    text, mentions = summarize(decision, _spec(optimize={"min": "offering.cost_per_task"}))
    partial = (
        "No model is established as the best fit: "
        "licence.commercial_use is unknown for lab/maybe."
    )
    assert text == (
        f"{PARTIAL} What is missing: licence.commercial_use. "
        "1 more model may qualify, but ModelSpec lacks its values "
        "for these requirements. "
        f"{NO_CLASS} {COST_ONLY} {CHECKED_ONLY}"
    )
    assert text.count(
        "1 more model may qualify, but ModelSpec lacks its values "
        "for these requirements."
    ) == 1
    assert mentions == [
        partial,
        NO_CLASS,
        COST_ONLY,
        CHECKED_ONLY,
    ]
    assert "tied" not in text
    assert "lab/a" not in text and "lab/maybe" not in text
    for word in ("top", "best", "recommended"):
        assert re.search(rf"\b{word}\b", text, re.I) is None


def test_partial_cross_domain_unknown_names_the_objective_refinement() -> None:
    decision = _decision(
        status="partial",
        answer=_separated("lab/a"),
        may_qualify=[{"model": "lab/maybe", "unknown": ["any"]}],
    )
    spec = _spec(optimize={"weights": {"any/factuality_hallucination": 1}})
    text, mentions = summarize(decision, spec)
    assert text == (
        f"{PARTIAL} What is missing: factuality_hallucination. {QUALIFY_ONE} "
        f"{NO_CLASS} {CHECKED_ONLY}"
    )
    assert mentions == [
        "No model is established as the best fit: "
        "factuality_hallucination is unknown for lab/maybe.",
        NO_CLASS,
        CHECKED_ONLY,
    ]
    for rendered in [text, *mentions]:
        assert re.search(r"\bany\b", rendered) is None
        assert "any/" not in rendered
    assert decision.may_qualify[0].unknown == ["any"]


def test_partial_cross_domain_unknown_without_a_spec_uses_the_fallback() -> None:
    decision = _decision(
        status="partial",
        answer=_separated("lab/a"),
        may_qualify=[{"model": "lab/maybe", "unknown": ["any"]}],
    )
    text, mentions = summarize(decision)
    assert text == (
        f"{PARTIAL} What is missing: complete objective values for some candidates. "
        f"{QUALIFY_ONE}"
    )
    assert mentions == [
        "No model is established as the best fit: some candidates lack values ModelSpec needs.",
    ]
    for rendered in [text, *mentions]:
        assert re.search(r"\bany\b", rendered) is None
        assert "any/" not in rendered
    assert decision.may_qualify[0].unknown == ["any"]


def test_partial_cross_domain_unknown_without_a_matching_objective_uses_the_fallback() -> None:
    decision = _decision(
        status="partial",
        answer=_separated("lab/a"),
        may_qualify=[{"model": "lab/maybe", "unknown": ["any"]}],
    )
    text, mentions = summarize(decision, _spec())
    assert text == (
        f"{PARTIAL} What is missing: complete objective values for some candidates. "
        f"{QUALIFY_ONE} {NO_CLASS} {CHECKED_ONLY}"
    )
    assert mentions == [
        "No model is established as the best fit: some candidates lack values ModelSpec needs.",
        NO_CLASS,
        CHECKED_ONLY,
    ]


def test_partial_cross_domain_unknown_names_each_objective_refinement() -> None:
    decision = _decision(
        status="partial",
        may_qualify=[{"model": "lab/maybe", "unknown": ["any", "licence.commercial_use"]}],
    )
    spec = _spec(optimize={"weights": {
        "-any/factuality_hallucination": 0.5,
        "any/instruction_following": 0.5,
    }})
    text, mentions = summarize(decision, spec)
    assert text == (
        f"{PARTIAL} What is missing: factuality_hallucination; instruction_following; "
        f"licence.commercial_use. {QUALIFY_ONE} {NO_CLASS} {CHECKED_ONLY}"
    )
    assert mentions == [
        "No model is established as the best fit: factuality_hallucination, "
        "instruction_following, and licence.commercial_use are unknown for lab/maybe.",
        NO_CLASS,
        CHECKED_ONLY,
    ]


def test_cross_domain_objective_failure_names_the_refinement_and_keeps_real_parents() -> None:
    decision = _decision(
        status="no_feasible", results=[], answer=None,
        relax=["no complete objective values"],
    )
    spec = _spec(
        where=["model.class = text-generator"],
        optimize={"weights": {
            "-any/factuality_hallucination": 0.5, "software_engineering/rust": 0.5,
        }},
    )
    text, mentions = summarize(decision, spec)
    assert text == (
        f"{NO_FEASIBLE} No model that meets the requirements has complete values for the objective "
        "(factuality_hallucination, software_engineering), so ModelSpec cannot order them. "
        f"Requirements applied: model.class = text-generator. {CHECKED_ONLY}"
    )
    assert mentions == [CHECKED_ONLY]


def test_cross_domain_objective_failure_without_a_spec_uses_the_no_name_fallback() -> None:
    decision = _decision(
        status="no_feasible", results=[], answer=None,
        relax=["no complete objective values"],
        may_qualify=[{"model": "lab/maybe", "unknown": ["any"]}],
    )
    text, mentions = summarize(decision)
    assert text == f"{NO_FEASIBLE} These requirements together exclude every model. {QUALIFY_ONE}"
    assert mentions == [QUALIFY_ONE]


def test_cross_domain_leaderboard_caveat_names_the_refinement() -> None:
    decision = _decision(
        answer=_separated("lab/a"),
        results=[_row("lab/a", contributions=[{
            "dimension": "any", "refinement": "factuality_hallucination", "value": None,
        }])],
    )
    spec = _spec(optimize={"weights": {"any/factuality_hallucination": 1}})
    text, mentions = summarize(decision, spec)
    caveat = (
        "lab/a has no leaderboard data for factuality_hallucination; "
        "its position is estimated, not measured."
    )
    assert text == f"ModelSpec's answer is lab/a. {NO_CLASS} {caveat} {CHECKED_ONLY}"
    assert mentions == [NO_CLASS, caveat, CHECKED_ONLY]
    for rendered in [text, *mentions]:
        assert re.search(r"\bany\b", rendered) is None
        assert "any/" not in rendered


def test_cross_domain_record_count_and_proxy_caveats_name_the_refinement() -> None:
    decision = _decision(
        answer=_separated("lab/a"),
        results=[_row("lab/a", contributions=[{
            "dimension": "any", "refinement": "factuality_hallucination",
            "value": 1.0, "unit": "latent capability",
            "evidence": [_evidence()],
        }])],
    )
    text, mentions = summarize(
        decision,
        _spec(optimize={"weights": {"any/factuality_hallucination": 1}}),
        record_counts={"lab/a": {"any/factuality_hallucination": (4, 1)}},
    )
    proxy = (
        "The evidence for factuality_hallucination is a general proxy "
        "(general_bench), not task-specific."
    )
    position = (
        "lab/a's position on factuality_hallucination is estimated from "
        "4 records, 1 of them a proxy."
    )
    assert text == f"ModelSpec's answer is lab/a. {NO_CLASS} {proxy} {position} {CHECKED_ONLY}"
    assert mentions == [NO_CLASS, proxy, position, CHECKED_ONLY]


def test_every_rankable_cross_domain_refinement_has_no_raw_parent_in_its_summary() -> None:
    from decision.bounded import DEFAULT_FIELDS
    from decision.capability import ANY_PARENT
    from decision.refinements import RANKABLE, evidence_state, lineup, split_dimension
    from qa.decide_budget import public_snapshot
    from tests.test_decide_worker import _load_service

    snapshot = public_snapshot()
    candidates = lineup(snapshot)
    keys = [
        key for key in snapshot.refinement_keys()
        if split_dimension(key)[0] == ANY_PARENT
        and evidence_state(
            snapshot, candidates, snapshot.refinement_benchmarks(key),
            snapshot.refinement_eligible_classes(key),
        )[0] in RANKABLE
    ]
    assert keys
    # A single model avoids the unrelated "any one of them" tie wording.
    sizes: dict[int | float, set[str]] = {}
    for candidate in candidates:
        if snapshot.fact(candidate, "model.class").value != "text-generator":
            continue
        size = snapshot.fact(candidate, "model.parameters_total").value
        if isinstance(size, (int, float)):
            sizes.setdefault(size, set()).add(snapshot.model_of(candidate))
    size = next(size for size, models in sizes.items() if len(models) == 1)
    service = _load_service()
    leaks = []
    for key in keys:
        status, body = service.decide({
            "spec_version": 1,
            "where": [
                "model.class = text-generator",
                "known(model.parameters_total)",
                {"facet": "model.parameters_total", "op": "=", "value": size},
            ],
            "optimize": {"weights": {key: 1}},
            "explain": "none",
            "fields": list(DEFAULT_FIELDS),
        }, snapshot)
        assert status == 200, (key, body)
        answer = body["answer"]
        assert answer is None or answer["kind"] == "separated", (key, answer)
        for rendered in [body["summary_for_user"], *body["must_mention"]]:
            if re.search(r"\bany\b", rendered) or "any/" in rendered:
                leaks.append((key, rendered))
        assert len(body["summary_for_user"].encode("utf-8")) <= SUMMARY_BYTES
        assert all(
            len(item.encode("utf-8")) <= MUST_MENTION_ITEM_BYTES for item in body["must_mention"]
        )
    print(f"Cross-domain sweep: {len(keys)} rankable keys; {len(leaks)} text leaks.")
    print("Keys: " + ", ".join(keys))
    assert leaks == []


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
        f"{NO_CLASS} {unmeasured} {ESTIMATES} {CHECKED_ONLY}"
    )
    assert NOT_APPLIED not in text
    assert mentions == [
        NO_CLASS,
        unmeasured,
        NOT_APPLIED,
        ESTIMATES,
        CHECKED_ONLY,
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
        f"ModelSpec's answer is lab/a. {EITHER} {NO_CLASS} {COST_ONLY} {CHECKED_ONLY}"
    )
    assert mentions == [NO_CLASS, COST_ONLY, CHECKED_ONLY]
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
        f"{NO_CLASS} {COST_ONLY} {CHECKED_ONLY}"
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
        f"{NO_CLASS} {COST_ONLY} {CHECKED_ONLY}"
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
    assert text == f"ModelSpec's answer is lab/a. {NO_CLASS} {MISSING} {CHECKED_ONLY}"
    assert mentions == [NO_CLASS, MISSING, CHECKED_ONLY]


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
        "ModelSpec's answer is lab/a. Requirements applied: model.class = text-generator. "
        f"{CHECKED_ONLY}"
    )
    assert mentions == [CHECKED_ONLY]
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
        "Requirements applied: offering.price.input <= 0.5; model.class = text-generator. "
        f"{CHECKED_ONLY}"
    )
    assert mentions == [CHECKED_ONLY]
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
    assert (
        "lab/a and lab/b are tied; this is not a recommendation of any one of them."
        in partial_text
    )
    assert partial_mentions == [
        "lab/a and lab/b are tied; this is not a recommendation of any one of them.",
        "No model is established as the best fit: "
        "licence.commercial_use is unknown for lab/maybe.",
        CHECKED_ONLY,
    ]


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
        "lab/a's position on chat_preference is estimated from 1 record, "
        "not a proxy."
    )
    text, mentions = summarize(
        latent, _spec(where=["model.class = text-generator"], optimize={"max": "chat_preference"}),
    )
    assert text == (
        "ModelSpec's answer is lab/a. "
        f"Requirements applied: model.class = text-generator. {expected} {CHECKED_ONLY}"
    )
    assert mentions == [expected, CHECKED_ONLY]

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
    assert measured_mentions == [ESTIMATES, CHECKED_ONLY]

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
        CHECKED_ONLY,
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
        "its position is estimated, not measured.",
        CHECKED_ONLY,
    ]


def _record(record_id: str, directness: str, benchmark: str) -> dict:
    item = _evidence(directness=directness, benchmark=benchmark)
    item["record_id"] = record_id
    return item


def _latent(model: str, dimension: str, evidence: list[dict], rank: int = 1) -> dict:
    return _row(model, rank, contributions=[{
        "dimension": dimension,
        "value": 1.0,
        "raw_value": 1.0,
        "unit": "latent capability",
        "formula": "monotone domain evidence estimate",
        "evidence": evidence,
    }])


def test_an_estimate_names_how_many_records_it_came_from() -> None:
    dimension = "software_engineering"
    three = [
        _record("direct", "direct", "cursorbench_4"),
        _record("proxy-a", "proxy", "proxy_a"),
        _record("proxy-b", "proxy", "proxy_b"),
        _record("proxy-a", "proxy", "proxy_a"),
    ]
    two = [
        _record("proxy-a", "proxy", "proxy_a"),
        _record("proxy-b", "proxy", "proxy_b"),
    ]
    one = [_record("direct", "direct", "cursorbench_4")]
    three_sentence = (
        "lab/three's position on software_engineering is estimated from 3 records, "
        "2 of them proxies."
    )
    three_again = (
        "lab/three-again's position on software_engineering is estimated from 3 records, "
        "2 of them proxies."
    )
    all_proxy = (
        "lab/two's position on software_engineering is estimated from 2 records, "
        "all of them proxies."
    )
    none_proxy = (
        "lab/one's position on software_engineering is estimated from 1 record, "
        "not a proxy."
    )
    none = (
        "lab/zero has no leaderboard data for software_engineering; "
        "its position is estimated, not measured."
    )
    decision = _decision(
        answer=_tied(["lab/three", "lab/three-again", "lab/two", "lab/one", "lab/zero"]),
        results=[
            _latent("lab/three", dimension, three, 1),
            _latent("lab/three-again", dimension, three[:-1], 2),
            _latent("lab/two", dimension, two, 3),
            _latent("lab/one", dimension, one, 4),
            _row("lab/zero", 5, contributions=[{"dimension": dimension, "value": None}]),
        ],
    )
    text, mentions = summarize(decision, _spec(optimize={"max": dimension}))
    proxy = (
        "The evidence for software_engineering is a general proxy (proxy_a, proxy_b), "
        "not task-specific."
    )
    assert mentions == [
        "lab/three, lab/three-again, lab/two, lab/one, and lab/zero are tied; "
        "this is not a recommendation of any one of them.",
        NO_CLASS,
        proxy,
        three_sentence,
        three_again,
        all_proxy,
        none_proxy,
        none,
        CHECKED_ONLY,
    ]
    for sentence in (three_sentence, three_again, all_proxy, none_proxy, none):
        assert sentence in text
    assert "positions on" not in text
    assert (
        text.index(three_sentence) < text.index(three_again) < text.index(all_proxy)
        < text.index(none_proxy) < text.index(none)
    )


def test_one_proxy_among_several_records_uses_the_singular_clause() -> None:
    evidence = [
        _record("direct", "direct", "cursorbench_4"),
        _record("proxy-a", "proxy", "proxy_a"),
    ]
    decision = _decision(
        answer=_separated("lab/a"),
        results=[_latent("lab/a", "software_engineering", evidence)],
    )
    expected = (
        "lab/a's position on software_engineering is estimated from 2 records, "
        "1 of them a proxy."
    )
    text, mentions = summarize(decision, _spec(optimize={"max": "software_engineering"}))
    assert mentions == [NO_CLASS, expected, CHECKED_ONLY]
    assert expected in text


def test_a_multi_dimension_objective_names_each_position() -> None:
    coding = [
        _record("direct", "direct", "cursorbench_4"),
        _record("proxy-a", "proxy", "proxy_a"),
    ]
    chat = [_record("arena", "proxy", "arena")]
    decision = _decision(
        answer=_separated("lab/a"),
        results=[_row("lab/a", contributions=[
            {
                "dimension": "coding_quality",
                "value": 1.0,
                "raw_value": 1.0,
                "unit": "latent capability",
                "formula": "monotone domain evidence estimate",
                "evidence": coding,
            },
            {
                "dimension": "chat_preference",
                "value": 1.0,
                "raw_value": 1.0,
                "unit": "latent capability",
                "formula": "monotone domain evidence estimate",
                "evidence": chat,
            },
        ])],
    )
    coding_sentence = (
        "lab/a's position on coding_quality is estimated from 2 records, "
        "1 of them a proxy."
    )
    chat_sentence = "lab/a's position on chat_preference is estimated from 1 record, a proxy."
    text, mentions = summarize(
        decision,
        _spec(optimize={"weights": {"coding_quality": 0.6, "chat_preference": 0.4}}),
    )
    assert coding_sentence in mentions
    assert chat_sentence in mentions
    assert mentions.index(coding_sentence) < mentions.index(chat_sentence)
    assert "positions on" not in text
    joined = " ".join(mentions)
    assert "positions on" not in joined


def test_a_refinement_key_is_named_in_the_record_count() -> None:
    decision = _decision(
        answer=_separated("lab/a"),
        results=[_row("lab/a", contributions=[{
            "dimension": "software_engineering",
            "refinement": "python",
            "value": 1.0,
            "raw_value": 1.0,
            "unit": "latent capability",
            "formula": "monotone domain evidence estimate",
        }])],
    )
    expected = (
        "lab/a's position on software_engineering/python is estimated from "
        "4 records, 1 of them a proxy."
    )
    text, mentions = summarize(
        decision,
        _spec(optimize={"weights": {"software_engineering/python": 1}}),
        record_counts={"lab/a": {"software_engineering/python": (4, 1)}},
    )
    assert expected in mentions
    assert expected in text


def test_a_limit_cut_tie_member_uses_the_captured_record_counts() -> None:
    shown = "lab/shown"
    cut = "lab/cut"
    decision = _decision(
        answer=_tied([shown, cut]),
        results=[_row(shown, contributions=[{"dimension": "software_engineering", "value": None}])],
        bands={
            "basis": BASIS,
            "band_probability": 0.8,
            "thin_interval_width": 0.5,
            "leader": cut,
            "best": [{
                "model": cut,
                "offering": {"model": cut},
                "score": 1.0,
                "score_interval": [0.5, 1.5],
                "estimates": [{
                    "dimension": "software_engineering",
                    "value": 1.0,
                    "interval": [0.5, 1.5],
                    "benchmarks": 99,
                    "direct_benchmarks": 1,
                }],
            }],
        },
    )
    spec = _spec(optimize={"max": "software_engineering"})
    without, without_mentions = summarize(decision, spec)
    shared_zero = (
        "lab/shown and lab/cut have no leaderboard data for software_engineering; "
        "their positions are estimated, not measured."
    )
    assert shared_zero in without and shared_zero in without_mentions
    assert "99" not in without

    text, mentions = summarize(
        decision, spec, record_counts={"lab/cut": {"software_engineering": (3, 2)}},
    )
    shown_sentence = (
        "lab/shown has no leaderboard data for software_engineering; "
        "its position is estimated, not measured."
    )
    cut_sentence = (
        "lab/cut's position on software_engineering is estimated from 3 records, "
        "2 of them proxies."
    )
    assert shown_sentence in mentions and shown_sentence in text
    assert cut_sentence in mentions and cut_sentence in text
    assert text.index(shown_sentence) < text.index(cut_sentence)
    assert "99" not in text


def test_cost_only_is_not_a_quality_ranking_and_a_cost_tie_break_says_so() -> None:
    decision = _decision(answer=_separated("lab/a"))
    text, mentions = summarize(decision, _spec(optimize={"min": "offering.cost_per_task"}))
    assert text == f"ModelSpec's answer is lab/a. {NO_CLASS} {COST_ONLY} {CHECKED_ONLY}"
    assert text.count(COST_ONLY) == 1
    assert mentions == [NO_CLASS, COST_ONLY, CHECKED_ONLY]

    infeasible = _decision(status="no_feasible", answer=None, results=[], relax=["model.context_window >= 10"])
    _text, infeasible_mentions = summarize(infeasible, _spec(optimize={"min": "offering.cost_per_task"}))
    assert infeasible_mentions == [NO_CLASS, CHECKED_ONLY]

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
    assert tie_mentions == [
        "lab/a and lab/b are tied; this is not a recommendation of any one of them.",
        TIE_COST,
        CHECKED_ONLY,
    ]
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
        f"{NULL_ANSWER} Requirements applied: model.class = text-generator. {CHECKED_ONLY}"
    )
    assert mentions == [CHECKED_ONLY]
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
    assert mentions[0] == (
        "lab/a and lab/b are tied; this is not a recommendation of any one of them."
    )
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
    assert mentions[-1] == "and 12 more."
    assert "Outside the board." in mentions
    assert (
        "1 more model may qualify, but ModelSpec lacks its values "
        "for these requirements."
    ) in mentions
    assert LINEUP_3 in mentions
    assert HARDWARE in mentions
    assert ESTIMATES in mentions
    assert all(len(item.encode("utf-8")) <= MUST_MENTION_ITEM_BYTES for item in mentions)
    assert len(text.encode("utf-8")) <= SUMMARY_BYTES
    assert text.startswith(
        "ModelSpec's answer is a tie among lab/a and lab/b; the evidence does not separate them."
    )
    assert "Requirements not applied (ModelSpec did not check them):" in text
    assert "; and 11 more." in text
    assert "was not applied; ModelSpec did not check it." not in text
    assert PROXY in text
    assert "These 2 models are tied; this is not a recommendation of any one of them." in text

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
    # The exclude list explains the empty answer; its repeat under
    # "Requirements applied" shortens first.
    shown = ", ".join(f"facet_{i:02d} >= {i}" for i in range(11)).replace(", ", "; ")
    assert f"exclude every model: {shown}; and 29 more." in huge_text
    assert "Requirements applied: facet_00 >= 0; and 39 more." in huge_text
    assert CHECKED_ONLY in huge_text
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


def test_a_tight_relax_budget_keeps_option_endings_and_the_joint() -> None:
    """Six long gates, three with a nearer threshold. Dropped options stay in a sentence."""
    stem = "y" * 140
    conditions = [f"facet_{i}_{stem} >= {i}" for i in range(6)]
    assert all(140 <= len(condition) <= 170 for condition in conditions)
    decision = _decision(
        status="no_feasible",
        results=[],
        answer=None,
        relax=list(conditions),
        relax_to=[
            {
                "condition": conditions[i],
                "relaxed": f"facet_{i}_{stem} >= {i + 5}",
                "facet": f"facet_{i}_{stem}",
                "value": float(i + 5),
                "admits": 1,
            }
            for i in range(3)
        ],
    )
    text, _mentions = summarize(
        decision,
        _spec(where=conditions, optimize={"min": "offering.cost_per_task"}),
    )
    ending = "that is an option, not an answer."
    sentences = text.split(". ")
    option_sentences = [part for part in sentences if "would admit a model" in part]
    assert len(text.encode("utf-8")) <= SUMMARY_BYTES
    assert f"together would admit a model; {ending}" in text
    assert option_sentences
    assert all(ending.rstrip(".") in part for part in option_sentences)
    assert any(
        part.startswith("Relaxing facet_0_") and " to facet_0_" in part and part.endswith("…")
        for part in sentences
    )
    assert not any(re.fullmatch(r"and [\d,]+ more\.?", part) for part in sentences)


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
    assert text.endswith("and 10 more.")
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


def test_a_partial_tie_says_it_is_not_a_recommendation() -> None:
    """Every failing tie in the 2026-10-08 run was partial (MODEL-351).

    The answer sentence names no members, so the paragraph keeps the named item.
    """
    decision = _decision(
        status="partial",
        answer=_tied(["openai/gpt-6-astra", "openai/gpt-6-sol", "openai/gpt-5-6-sol"]),
        may_qualify=[{"model": "lab/maybe", "unknown": ["maths"]}],
    )
    text, mentions = summarize(decision, _spec(where=["model.class = text-generator"]))
    tie = (
        "openai/gpt-6-astra, openai/gpt-6-sol, and openai/gpt-5-6-sol are tied; "
        "this is not a recommendation of any one of them."
    )
    partial = "No model is established as the best fit: maths is unknown for lab/maybe."
    assert text == (
        f"{PARTIAL} What is missing: maths. {QUALIFY_ONE} "
        "Requirements applied: model.class = text-generator. "
        f"{tie} {CHECKED_ONLY}"
    )
    assert mentions == [tie, partial, CHECKED_ONLY]


def test_a_long_tie_names_only_what_fits_in_the_item() -> None:
    models = [f"lab/{'m' * 40}-{index:02d}" for index in range(8)]
    decision = _decision(
        answer=_tied(models),
        results=[_row(model, rank) for rank, model in enumerate(models, 1)],
    )
    _text, mentions = summarize(decision, _spec())
    item = (
        "lab/mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm-00 and "
        "lab/mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm-01, and 6 more in answer.members "
        "are tied; this is not a recommendation of any one of them."
    )
    assert mentions[0] == item
    assert len(mentions[0].encode("utf-8")) == 188
    assert len(mentions[0].encode("utf-8")) <= MUST_MENTION_ITEM_BYTES
    assert "lab/mmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmmm-02" not in mentions[0]

    huge = ["lab/" + ("q" * 180), "lab/" + ("r" * 180)]
    _text, clipped_mentions = summarize(
        _decision(
            answer=_tied(huge),
            results=[_row(model, rank) for rank, model in enumerate(huge, 1)],
        ),
        _spec(),
    )
    assert clipped_mentions[0] == (
        "lab/qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq"
        "qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq"
        "qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq, and 1 more…"
    )
    assert len(clipped_mentions[0].encode("utf-8")) <= MUST_MENTION_ITEM_BYTES


def test_a_partial_answer_names_shared_and_differing_unknowns() -> None:
    shared = _decision(
        status="partial",
        may_qualify=[
            {"model": "qwen/qwen3-8-max-0902", "unknown": ["maths"]},
            {"model": "qwen/qwen3-8-max-0902", "unknown": ["maths"]},
            {"model": "anthropic/claude-sonnet-5-5", "unknown": ["maths"]},
            {"model": "openai/gpt-6-luna", "unknown": ["maths"]},
            {"model": "qwen/qwen3-8-flash-next", "unknown": ["maths"]},
        ],
    )
    _text, shared_mentions = summarize(shared, _spec())
    assert shared_mentions[0] == (
        "No model is established as the best fit: maths is unknown for "
        "qwen/qwen3-8-max-0902, anthropic/claude-sonnet-5-5, openai/gpt-6-luna, "
        "and qwen/qwen3-8-flash-next."
    )
    assert shared_mentions[0] not in _text

    reordered = _decision(
        status="partial",
        may_qualify=[
            {"model": "lab/a", "unknown": ["code", "maths"]},
            {"model": "lab/b", "unknown": ["maths", "code"]},
        ],
    )
    _reordered_text, reordered_mentions = summarize(reordered, _spec())
    assert reordered_mentions[0] == (
        "No model is established as the best fit: code and maths are unknown for lab/a and lab/b."
    )

    differing = _decision(
        status="partial",
        may_qualify=[
            {"model": "lab/a", "unknown": ["maths"]},
            {"model": "lab/b", "unknown": ["code"]},
        ],
    )
    differing_text, differing_mentions = summarize(differing, _spec())
    assert differing_mentions[0] == (
        "No model is established as the best fit: maths and code are unknown for one or more of "
        "lab/a and lab/b."
    )
    assert differing_mentions[0] not in differing_text

    empty = _decision(
        status="partial",
        may_qualify=[{"model": "lab/a", "unknown": []}],
    )
    _empty_text, empty_mentions = summarize(empty, _spec())
    assert empty_mentions[0] == (
        "No model is established as the best fit: some candidates lack values ModelSpec needs."
    )


def test_fits_hardware_is_an_estimate_with_and_without_a_gate() -> None:
    plain = _decision(
        answer=_separated("lab/a"),
        reading={"estimates": ["model.fits_hardware"]},
    )
    plain_text, plain_mentions = summarize(plain, _spec())
    assert plain_mentions == [NO_CLASS, HARDWARE, CHECKED_ONLY]
    assert HARDWARE in plain_text

    gated_text, gated_mentions = summarize(
        _decision(answer=_separated("lab/a")),
        _spec(where=["model.fits_hardware in {nvidia_rtx_4090}"]),
    )
    gate = (
        "model.fits_hardware in {nvidia_rtx_4090} is an estimate; "
        "fit for a specific quantization, context length or runtime headroom is not established."
    )
    assert gated_mentions == [NO_CLASS, gate, CHECKED_ONLY]
    assert gated_text == (
        "ModelSpec's answer is lab/a. "
        "Requirements applied: model.fits_hardware in {nvidia_rtx_4090}. "
        f"{NO_CLASS} {gate} {CHECKED_ONLY}"
    )


def test_own_hardware_without_a_device_says_fit_was_not_required() -> None:
    not_required = (
        "model.fits_hardware was not required, so no model is established to fit "
        "the target hardware."
    )
    decision = _decision(answer=_separated("lab/a"))
    _text, mentions = summarize(
        decision, _spec(where=["model.class = text-generator"], access="own_hardware"),
    )
    assert mentions == [not_required, CHECKED_ONLY]

    # A device in the estate is fitted through with_estate, so the estimate caveat stays.
    _text, estate_mentions = summarize(
        decision,
        _spec(
            where=["model.class = text-generator"], access="own_hardware",
            estate={"devices": ["nvidia_rtx_4090"]},
        ),
    )
    assert estate_mentions == [HARDWARE, CHECKED_ONLY]


def test_task_type_is_reported_as_not_applied() -> None:
    decision = _decision(answer=_separated("lab/a"))
    spec = _spec(task_type="review", where=["model.class = text-generator"])
    text, mentions = summarize(decision, spec, not_applied=["eu_residency"])
    task = "task_type = review was not applied; ModelSpec did not check it."
    assert mentions == [NOT_APPLIED, task, CHECKED_ONLY]
    assert text == (
        "ModelSpec's answer is lab/a. "
        "Requirements applied: model.class = text-generator. "
        "Requirements not applied (ModelSpec did not check them): "
        "eu_residency; task_type = review. "
        f"{CHECKED_ONLY}"
    )
    again_text, again_mentions = summarize(decision, spec, not_applied=["task_type = review"])
    assert again_mentions == [task, CHECKED_ONLY]
    assert again_text.count("task_type = review") == 1


def test_unchecked_needs_say_whether_any_requirement_was_applied() -> None:
    answered = _decision(answer=_separated("lab/a"))
    gated_text, gated_mentions = summarize(
        answered, _spec(where=["model.class = text-generator"]),
    )
    assert gated_mentions == [CHECKED_ONLY]
    assert gated_text == (
        "ModelSpec's answer is lab/a. "
        "Requirements applied: model.class = text-generator. "
        f"{CHECKED_ONLY}"
    )
    open_text, open_mentions = summarize(answered, _spec())
    assert open_mentions == [NO_CLASS, CHECKED_ONLY]
    assert open_text == f"ModelSpec's answer is lab/a. {NO_CLASS} {CHECKED_ONLY}"
    bare_text, bare_mentions = summarize(answered, None)
    assert bare_text == "ModelSpec's answer is lab/a."
    assert bare_mentions == []
