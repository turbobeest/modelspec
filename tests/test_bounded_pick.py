"""MODEL-339: a bounded answer names its pick, and offers no tie-breaker beside a test.

Claude agents cited `answer.tie_breakers` in 17 of the 18 judged failures where
a no-pick tie was reported as a shortlist or a "start with" (runs 2026-10-08
and 2026-10-10). A tie-breaker chooses within a settled tie; a test or a
question as the next step means the tie is not settled for the request.
"""

from __future__ import annotations

from decision.bounded import project
from decision.contract import BoundedDecision, ResponseOptions
from tests.test_decision_summary import BASIS, _decision, _row, _spec

NULL_BREAKERS = {"cheapest": None, "open_weights": None, "most_independently_measured": None, "fastest": None}
TIE_COST = "Tie-breakers are conditional; cost order is not quality order."


def _tie(cheapest: str | None = "lab/b", measured: str | None = "lab/a") -> dict:
    return {
        "kind": "tied", "members": ["lab/a", "lab/b"], "basis": BASIS,
        "tie_breakers": {**NULL_BREAKERS, "cheapest": cheapest, "most_independently_measured": measured},
        "deterministic_order": ["lab/a", "lab/b"],
    }


def _separated(model: str = "lab/a") -> dict:
    return {
        "kind": "separated", "members": [model], "leader": model, "basis": BASIS,
        "tie_breakers": NULL_BREAKERS, "deterministic_order": [model],
    }


def _project(decision, spec=None) -> dict:
    body = project(decision, ResponseOptions(fields=["model"]), spec=spec or _spec(), not_applied=[])
    BoundedDecision.model_validate(body)
    return body


def test_partial_tie_withholds_tie_breakers_and_names_no_pick():
    decision = _decision(
        status="partial", answer=_tie(), results=[_row("lab/a"), _row("lab/b", 2)],
        may_qualify=[{"model": "lab/c", "unknown": ["software_engineering"]}],
    )
    body = _project(decision)
    assert body["bounded_version"] == "1.3"
    assert body["next_move"]["kind"] == "decide_by_testing"
    assert body["pick"] is None
    assert body["answer"]["tie_breakers"] == NULL_BREAKERS
    assert body["answer"]["members"] == ["lab/a", "lab/b"]
    assert body["explanation"]["omitted"]["answer.tie_breakers"] == 2
    assert body["explanation"]["fetch"].endswith("POST /v1/decide without fields for the complete Decision.")
    # The complete Decision keeps them.
    assert decision.answer.tie_breakers.cheapest == "lab/b"


def test_settled_tie_keeps_tie_breakers_beside_user_tiebreak():
    body = _project(_decision(answer=_tie(), results=[_row("lab/a"), _row("lab/b", 2)]))
    assert body["next_move"]["kind"] == "user_tiebreak"
    assert body["pick"] is None
    assert body["answer"]["tie_breakers"] == {**NULL_BREAKERS, "cheapest": "lab/b",
                                              "most_independently_measured": "lab/a"}
    assert "answer.tie_breakers" not in body["explanation"]["omitted"]
    assert TIE_COST in body["must_mention"]


def test_unmeasured_task_withholds_tie_breakers_and_their_caveat_on_an_answered_tie():
    body = _project(_decision(answer=_tie(), results=[_row("lab/a"), _row("lab/b", 2)]),
                    _spec(task_type="review"))
    assert body["status"] == "answered"
    assert body["next_move"]["kind"] == "decide_by_testing"
    assert body["answer"]["tie_breakers"] == NULL_BREAKERS
    assert body["explanation"]["omitted"]["answer.tie_breakers"] == 2
    assert TIE_COST not in body["must_mention"]


def test_tie_without_tie_breakers_counts_nothing():
    body = _project(_decision(status="partial", answer=_tie(None, None),
                              results=[_row("lab/a"), _row("lab/b", 2)]))
    assert body["answer"]["tie_breakers"] == NULL_BREAKERS
    assert "answer.tie_breakers" not in body["explanation"]["omitted"]


def test_answered_separated_pick_is_the_leader():
    body = _project(_decision(answer=_separated()))
    assert "next_move" not in body
    assert body["pick"] == "lab/a"


def test_partial_separated_leader_is_not_a_pick():
    body = _project(_decision(
        status="partial", answer=_separated(), results=[_row("lab/a"), _row("lab/b", 2)],
        may_qualify=[{"model": "lab/c", "unknown": ["software_engineering"]}],
    ))
    assert body["answer"]["leader"] == "lab/a"
    assert body["next_move"]["kind"] == "decide_by_testing"
    assert body["pick"] is None


def test_null_answer_has_a_null_pick():
    body = _project(_decision(status="partial", answer=None, results=[_row("lab/a"), _row("lab/b", 2)]))
    assert body["answer"] is None
    assert body["pick"] is None


def test_estate_tie_breakers_are_withheld_and_counted_separately():
    estate = {"status": "answered", "answer": _tie(measured=None),
              "gap": {"same_answer": True, "summary": "The estate reaches the same answer."}}
    body = _project(_decision(status="partial", answer=_tie(), with_estate=estate,
                              results=[_row("lab/a"), _row("lab/b", 2)]))
    assert body["with_estate"]["answer"]["tie_breakers"] == NULL_BREAKERS
    assert body["explanation"]["omitted"]["answer.tie_breakers"] == 2
    assert body["explanation"]["omitted"]["with_estate.answer.tie_breakers"] == 1
