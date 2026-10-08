"""MODEL-339: the bounded summary is a deterministic report of the Decision."""

from __future__ import annotations

import re

from decision.bounded import AGENT_BYTES, mcp_text_bytes, project
from decision.contract import Decision, ModelEvidence, ResponseOptions, parse_spec
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
NO_ANSWER = "ModelSpec's answer is that there is no answer."
PROXY = (
    "The evidence for software_engineering is a general proxy (general_bench), not task-specific."
)
MISSING = "lab/a has no coding_quality data on the tracked boards; its position is not measured."
NOT_APPLIED = "eu_residency was not applied; ModelSpec did not check it."
EITHER = "model.weights_openness is not required (either acceptable)."
TIE_THREE = (
    "ModelSpec's answer is a tie among lab/a, lab/b, and lab/c, "
    "and the evidence does not separate them."
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
        f"{TIE_THREE} Hard requirements: model.class = text-generator. "
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
        "lab/m6, lab/m7, and lab/m8, and 2 more in answer.members, "
        "and the evidence does not separate them"
    )
    assert mentions == ["No single winner: 10 models are tied."]
    for word in ("better", "worse", "best", "recommended"):
        assert word not in _answer_sentence(text)


def test_no_feasible_names_no_pick_and_keeps_the_relax_suggestions() -> None:
    relax = ["offering.region = eu", "model.class = text-generator"]
    decision = _decision(status="no_feasible", results=[], answer=None, relax=relax)
    spec = _spec(where=relax, optimize={"min": "offering.cost_per_task"})
    text, mentions = summarize(decision, spec)
    assert text == (
        f"{NO_ANSWER} These requirements together exclude every model: "
        "offering.region = eu; model.class = text-generator. "
        "Relax suggestions: offering.region = eu; model.class = text-generator. "
        "Hard requirements: offering.region = eu; model.class = text-generator."
    )
    assert mentions == []
    assert "lab/" not in text
    for word in ("top", "best", "recommended"):
        assert re.search(rf"\b{word}\b", text, re.I) is None


def test_partial_names_no_pick_and_counts_models_that_may_qualify() -> None:
    decision = _decision(
        status="partial",
        answer=_separated("lab/a"),
        may_qualify=[{"model": "lab/maybe", "unknown": ["licence.commercial_use"]}],
    )
    text, mentions = summarize(decision, _spec(optimize={"min": "offering.cost_per_task"}))
    assert text == (
        f"{NO_ANSWER} What is missing: licence.commercial_use. "
        "1 model may qualify; unknown values. "
        "1 model may qualify; unknown values."
    )
    assert mentions == ["1 model may qualify; unknown values."]
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
    assert text == (
        "ModelSpec's answer is lab/a. "
        "Hard requirements: software_engineering is required. "
        "Not applied and not enforced: eu_residency. "
        f"{NOT_APPLIED} "
        "Estimates are estimates, not measurements."
    )
    assert mentions == [NOT_APPLIED, "Estimates are estimates, not measurements."]
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
    assert text == f"ModelSpec's answer is lab/a. {EITHER}"
    assert mentions == []
    assert "closed_weights" not in text
    assert "open_weights = false" not in text
    assert "closed weights required" not in text


def test_a_closed_weights_comparison_stays_a_hard_requirement() -> None:
    decision = _decision(answer=_separated("lab/a"))
    spec = _spec(
        where=["model.weights_openness = closed_weights"],
        optimize={"min": "offering.cost_per_task"},
    )
    text, _mentions = summarize(decision, spec)
    assert text == (
        "ModelSpec's answer is lab/a. "
        "Hard requirements: model.weights_openness = closed_weights."
    )


def test_a_preference_for_false_stays_false() -> None:
    decision = _decision(answer=_separated("lab/a"))
    spec = _spec(optimize={"weights": {"licence.commercial_use": {"prefer": False, "weight": 1}}})
    text, _mentions = summarize(decision, spec)
    assert "licence.commercial_use prefers false" in text
    assert "closed_weights" not in text


def test_missing_board_data_is_named_for_the_answer_member() -> None:
    decision = _decision(
        answer=_separated("lab/a"),
        results=[_row("lab/a", contributions=[{"dimension": "coding_quality", "value": None}])],
    )
    text, mentions = summarize(decision, _spec(optimize={"max": "coding_quality"}))
    assert text == f"ModelSpec's answer is lab/a. {MISSING}"
    assert mentions == [MISSING]


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
    clipped = "requirement_" + ("x" * 180) + "_0 wa…"
    assert len(mentions) == MUST_MENTION_MAX
    assert mentions[0] == "No single winner: 2 models are tied."
    assert mentions[1] == PROXY
    assert mentions[2] == clipped
    assert mentions[-1] == "and 10 more."
    assert "Outside the board." in mentions
    assert "1 model may qualify; unknown values." in mentions
    assert "3 active models are out of the lineup." in mentions
    assert (
        "fits_hardware is an estimate, not a measured fit for a quantization or context workload."
        in mentions
    )
    assert "Estimates are estimates, not measurements." in mentions
    assert all(len(item.encode("utf-8")) <= MUST_MENTION_ITEM_BYTES for item in mentions)
    assert len(text.encode("utf-8")) <= SUMMARY_BYTES
    assert text.startswith(
        "ModelSpec's answer is a tie among lab/a and lab/b, and the evidence does not separate them."
    )
    assert "Not applied and not enforced:" in text and "; and 11 more." in text
    assert PROXY in text and "No single winner: 2 models are tied." in text

    where = [f"facet_{i:02d} >= {i}" for i in range(40)]
    huge = _decision(status="no_feasible", results=[], answer=None, relax=where)
    huge_text, _huge_mentions = summarize(
        huge, _spec(where=where, optimize={"min": "offering.cost_per_task"}),
    )
    assert len(huge_text.encode("utf-8")) <= SUMMARY_BYTES
    assert huge_text.startswith(NO_ANSWER)
    assert "facet_00 >= 0" in huge_text
    assert "Relax suggestions:" in huge_text
    assert "and 16 more" in huge_text
    assert "lab/" not in huge_text


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
    # The overflow fixture's evidence is on lab/a and lab/b, which are no longer
    # answer members, so recompute from this decision. The name list is the
    # worst case the paragraph is allowed to spell out.
    text, mentions = summarize(fat, spec, not_applied=unapplied)
    assert len(mentions) == MUST_MENTION_MAX
    assert text.startswith("ModelSpec's answer is a tie among lab/m1, lab/m2,")
    assert "and 2 more in answer.members" in text
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
