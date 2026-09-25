"""Relaxation never changes what the question is about (MODEL-153).

Recall Q10 asks for a chat model at no more than $0.20 per million input
tokens. Nothing in the lineup is that cheap, and the engine's `relax` said to
drop `model.class = text-generator`, because the one model under the cap is a
decider. The page offered it as a one-click button, which would have answered
a different question.

`relax` still names the fewest conditions whose removal gives a feasible
answer, but never the class or a condition on a requested capability domain,
and among equally few it prefers a numeric cap or floor. `relax_to` (contract
1.5) states for each numeric cap or floor the smallest change that admits a
model: the relaxed condition, the new threshold and its unit.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path

from decision.contract import CONTRACT_VERSION, parse_spec
from decision.engine import decide
from decision.registry import facet as facets
from decision.snapshot import SnapshotInputs, build_snapshot, load_snapshot_bytes
from tests.snapshot_records import SOURCES, evidence, fact, model, offering

ARENA = "arena_elo_overall"
Q10 = Path(__file__).resolve().parent / "recall" / "specs" / "Q10.yaml"


def member(mid: str, cls: str, *, context: int = 200_000):
    return model(mid, facts=[
        fact("model", mid, "model.class", cls),
        fact("model", mid, "model.context_window", context),
        fact("model", mid, "model.weights_openness", "closed_weights"),
    ])


def q10_snapshot():
    """Q10's shape: generators all over the cap, one decider under it."""
    built = build_snapshot(
        SnapshotInputs(
            models=[member("lab/cheap-chat", "text-generator"),
                    member("lab/dear-chat", "text-generator"),
                    member("lab/judge", "decider")],
            offerings=[offering("lab/cheap-chat", price=2.0),
                       offering("lab/dear-chat", price=10.0),
                       offering("lab/judge", price=0.1)],
            evidence=[evidence("lab/cheap-chat", ARENA, 1400.0),
                      evidence("lab/dear-chat", ARENA, 1450.0),
                      evidence("lab/judge", ARENA, 1300.0)],
            sources=SOURCES,
            benchmark_domains={ARENA: [("chat_preference", "direct")]},
        ),
        gate=False,
        as_of=date(2026, 9, 25),
    )
    return load_snapshot_bytes(built.to_bytes(key=None), key=None, include_archive=True)


def q10(explain: str = "none"):
    spec = parse_spec(Q10.read_text(encoding="utf-8"), facets=facets)
    return spec.model_copy(update={"explain": explain})


def test_q10_never_suggests_dropping_the_class():
    decision = decide(q10(), q10_snapshot(), facets=facets)
    assert decision.status == "no_feasible"
    assert "model.class = text-generator" not in decision.relax
    assert decision.relax == ["offering.price.input <= 0.2"]


def test_q10_states_the_smallest_price_change_in_real_units():
    decision = decide(q10(), q10_snapshot(), facets=facets)
    assert [r.model_dump() for r in decision.relax_to] == [{
        "condition": "offering.price.input <= 0.2",
        "relaxed": "offering.price.input <= 2",
        "facet": "offering.price.input",
        "value": 2.0,
        "unit": "usd_per_1m_tokens",
        "admits": 1,
    }]


def test_the_smallest_change_admits_only_what_it_must():
    """A floor lowers to the best value that fails it, not further."""
    snapshot = q10_snapshot()
    spec = parse_spec({
        "spec_version": 1,
        "where": ["model.class = text-generator", f"{ARENA} >= 1500"],
        "optimize": {"max": ARENA},
    }, facets=facets)
    decision = decide(spec, snapshot, facets=facets)
    assert decision.relax == [f"{ARENA} >= 1500"]
    [floor] = decision.relax_to
    assert (floor.relaxed, floor.value, floor.admits) == (f"{ARENA} >= 1450", 1450.0, 1)


def test_when_only_the_class_would_admit_a_model_relax_says_why_instead():
    snapshot = q10_snapshot()
    spec = parse_spec({
        "spec_version": 1,
        "where": ["model.class = embedder"],
        "optimize": {"max": ARENA},
    }, facets=facets)
    decision = decide(spec, snapshot, facets=facets)
    assert decision.status == "no_feasible"
    assert all("model.class" not in r for r in decision.relax)
    assert decision.relax  # the contract requires a reason when nothing can be dropped
    assert decision.relax_to == []


def test_an_answered_decision_suggests_nothing():
    snapshot = q10_snapshot()
    spec = parse_spec({
        "spec_version": 1,
        "where": ["model.class = text-generator"],
        "optimize": {"max": ARENA},
    }, facets=facets)
    decision = decide(spec, snapshot, facets=facets)
    assert decision.status != "no_feasible"
    assert decision.relax == [] and decision.relax_to == []


def test_relax_to_remains_in_contract_1_6():
    assert CONTRACT_VERSION == "1.7"
