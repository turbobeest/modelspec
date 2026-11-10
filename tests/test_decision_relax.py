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

import json
from datetime import date
from pathlib import Path

import pytest

from decision.contract import CONTRACT_VERSION, Decision, parse_spec
from decision.engine import decide
from decision.registry import facet as facets
from decision.snapshot import SnapshotInputs, build_snapshot, load_built_snapshot
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
    return load_built_snapshot(built, include_archive=True, source="relaxation test build")


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
        "where": ["model.class = vectoriser"],
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


def test_relax_to_remains_in_the_current_contract():
    assert CONTRACT_VERSION == "2.19"


def _counted_apply(monkeypatch):
    from decision import relax

    original = relax.apply
    calls = {"n": 0}

    def counted(*args, **kwargs):
        calls["n"] += 1
        return original(*args, **kwargs)

    monkeypatch.setattr(relax, "apply", counted)
    return calls


def test_duplicate_gates_stay_within_a_quadratic_filter_budget(monkeypatch):
    from decision import relax
    from decision.resolve import resolve
    from tests.snapshot_records import loaded_index

    count = 12
    where = ["model.context_window >= 100"] * count
    index = loaded_index({"lab/a": {"model.context_window": 1}})
    resolved = resolve(parse_spec({
        "spec_version": 1,
        "where": where,
        "optimize": {"max": "model.context_window"},
        "explain": "full",
    }, facets=facets), facets=facets)
    calls = _counted_apply(monkeypatch)
    assert relax.fewest(resolved, index, frozenset()) == where
    assert calls["n"] <= count * count


def test_distinct_gates_stay_within_a_quadratic_filter_budget(monkeypatch):
    from decision import relax
    from decision.resolve import resolve
    from tests.snapshot_records import loaded_index

    count = 12
    where = [f"model.context_window >= {100 + i}" for i in range(count)]
    index = loaded_index({"lab/a": {"model.context_window": 1}})
    resolved = resolve(parse_spec({
        "spec_version": 1,
        "where": where,
        "optimize": {"max": "model.context_window"},
        "explain": "none",
    }, facets=facets), facets=facets)
    calls = _counted_apply(monkeypatch)
    assert relax.fewest(resolved, index, frozenset()) == where
    assert calls["n"] <= count * count


def test_a_best_margin_does_not_change_which_gate_is_fewest():
    from decision import relax
    from decision.resolve import resolve
    from tests.snapshot_records import loaded_index

    index = loaded_index({
        "lab/high": {"model.context_window": 50},
        "lab/low": {"model.context_window": 10},
    })
    resolved = resolve(parse_spec({
        "spec_version": 1,
        "where": ["model.context_window >= 100", "model.context_window >= best(0)"],
        "optimize": {"max": "model.context_window"},
        "explain": "none",
    }, facets=facets), facets=facets)
    assert relax.fewest(resolved, index, frozenset()) == ["model.context_window >= 100"]


def test_a_best_gate_outside_the_relaxation_returns_the_other_gate():
    from decision import relax
    from tests.snapshot_records import loaded_index

    index = loaded_index({
        "lab/a": {"model.context_window": 8000, "model.max_output_tokens": 100},
        "lab/b": {"model.context_window": 1000, "model.max_output_tokens": 50},
    })
    where = ["model.context_window >= best(0)", "model.max_output_tokens >= 1000"]
    resolved = _resolved(where)
    assert relax.fewest(resolved, index, frozenset({"model.context_window"})) == [
        "model.max_output_tokens >= 1000",
    ]


def test_a_best_gate_on_a_requested_domain_stays_a_decision():
    snapshot = q10_snapshot()
    wheres = (
        ["offering.price.input <= 0.01", "chat_preference >= best(0)"],
        [
            "model.class = text-generator",
            "offering.price.input <= 0.20",
            "chat_preference >= best(0)",
        ],
        [
            "model.class = text-generator",
            "offering.price.input <= 0.20",
            "chat_preference >= best(0.5)",
            "model.context_window >= best(0)",
        ],
    )
    for where in wheres:
        spec = parse_spec({
            "spec_version": 1,
            "task_type": "analysis",
            "capabilities": {"chat_preference": "required"},
            "where": where,
            "optimize": {"max": "arena_elo_overall @independent"},
            "explain": "full",
        }, facets=facets)
        decision = decide(spec, snapshot, facets=facets)
        text = json.dumps(decision.model_dump(mode="json"), allow_nan=False)
        restored = Decision.model_validate_json(text)
        assert restored.status == "no_feasible"
        assert restored.relax == ["no complete objective values"]


def test_equally_few_relaxations_prefer_a_numeric_cap():
    from decision import relax
    from decision.resolve import resolve
    from tests.snapshot_records import loaded_index

    index = loaded_index({
        "lab/wide": {"model.context_window": 200, "licence.commercial_use": "prohibited"},
        "lab/permitted": {"model.context_window": 10, "licence.commercial_use": "permitted"},
    })
    where = ["model.context_window >= 100", "licence.commercial_use = permitted"]
    resolved = resolve(parse_spec({
        "spec_version": 1,
        "where": where,
        "optimize": {"max": "model.context_window"},
        "explain": "none",
    }, facets=facets), facets=facets)
    assert relax.fewest(resolved, index, frozenset()) == ["model.context_window >= 100"]


def _resolved(where):
    from decision.resolve import resolve

    return resolve(parse_spec({
        "spec_version": 1,
        "where": where,
        "optimize": {"max": "model.context_window"},
        "explain": "none",
    }, facets=facets), facets=facets)


def _per_index(resolved, snapshot) -> list[str]:
    """The old search: size ascending, caps first, then index order."""
    from itertools import combinations

    from decision.contract import render_condition
    from decision.filter import apply
    from decision.relax import _cap_or_floor, _relaxable
    from decision.resolve import without

    conditions = resolved.conditions
    hard = _relaxable(resolved, frozenset())
    for size in range(1, len(hard) + 1):
        groups = sorted(
            combinations(hard, size),
            key=lambda group: -sum(_cap_or_floor(conditions[index]) for index in group),
        )
        for dropped in groups:
            if apply(without(resolved, dropped), snapshot).feasible:
                return [render_condition(conditions[index]) for index in dropped]
    return []


@pytest.mark.parametrize("count", [12, 14, 16])
def test_caps_with_a_best_margin_stay_within_the_filter_budget(count, monkeypatch):
    from decision import relax
    from tests.snapshot_records import loaded_index

    where = [f"model.context_window >= {100 + i}" for i in range(count)]
    where.append("model.context_window >= best(0)")
    index = loaded_index({"lab/a": {"model.context_window": 1}})
    calls = _counted_apply(monkeypatch)
    assert relax.fewest(_resolved(where), index, frozenset()) == where[:-1]
    assert calls["n"] <= 32


def _many_blocking_sets(copies: int):
    from tests.snapshot_records import loaded_index

    levels = (500, 1500, 2500, 3500, 4500, 5500, 6500, 7500)
    floors = (1000, 2000, 3000, 4000, 5000, 6000, 7000)
    rows = {
        f"lab/m{i}{j}": {"model.context_window": ctx, "model.max_output_tokens": out}
        for i, ctx in enumerate(levels)
        for j, out in enumerate(levels)
        if not (ctx == levels[-1] and out == levels[-1])
    }
    base = list(rows.items())
    extra = 0
    while len(rows) < copies:
        for key, value in base:
            if len(rows) >= copies:
                break
            rows[f"lab/e{extra}"] = value
            extra += 1
    where = [f"model.context_window >= {bound}" for bound in floors]
    where += [f"model.max_output_tokens >= {bound}" for bound in floors]
    where.append("model.max_output_tokens >= best(10000)")
    return where, loaded_index(rows)


@pytest.mark.parametrize("copies", [63, 120])
def test_one_gate_among_many_blocking_sets_stays_inside_a_fixed_bound(copies, monkeypatch):
    from decision import relax
    from decision.filter import _has_best
    from decision.relax import _candidate_blocks, _equivalent_groups, _relaxable

    where, index = _many_blocking_sets(copies)
    resolved = _resolved(where)
    hard = _relaxable(resolved, frozenset())
    groups = [
        group for group in _equivalent_groups(resolved.conditions, hard)
        if not _has_best(resolved.conditions[group[0]])
    ]
    blocking = {
        indexes
        for indexes, _bit in _candidate_blocks(
            resolved, index, resolved.conditions, hard, groups,
        )
    }
    assert len(blocking) >= 63
    calls = _counted_apply(monkeypatch)
    assert relax.fewest(resolved, index, frozenset()) == ["model.context_window >= 7000"]
    assert calls["n"] <= 8


def test_a_feasible_duplicate_gate_drops_one_copy():
    from decision import relax
    from tests.snapshot_records import loaded_index

    where = ["model.context_window >= 1", "model.context_window >= 1"]
    index = loaded_index({"lab/a": {"model.context_window": 100}})
    assert relax.fewest(_resolved(where), index, frozenset()) == ["model.context_window >= 1"]


def test_a_feasible_tie_prefers_the_numeric_cap():
    from decision import relax
    from tests.snapshot_records import loaded_index

    index = loaded_index({
        "lab/wide": {
            "model.context_window": 200,
            "licence.commercial_use": "permitted",
        },
    })
    where = ["licence.commercial_use = permitted", "model.context_window >= 10"]
    assert relax.fewest(_resolved(where), index, frozenset()) == ["model.context_window >= 10"]


def test_a_negated_best_gate_matches_the_per_index_search():
    from decision import relax
    from tests.snapshot_records import loaded_index

    index = loaded_index({
        "lab/a": {"model.context_window": 100, "licence.commercial_use": "permitted"},
        "lab/b": {"model.context_window": 40, "licence.commercial_use": "prohibited"},
    })
    specs = (
        ["model.context_window <= 50", "not(model.context_window >= best(30))"],
        ["not(model.context_window >= best(30))", "model.context_window <= 50"],
        [
            "model.context_window <= 50",
            "any(not(model.context_window >= best(30)); licence.commercial_use = permitted)",
        ],
    )
    for where in specs:
        resolved = _resolved(where)
        assert relax.fewest(resolved, index, frozenset()) == _per_index(resolved, index)


def test_fewest_matches_the_per_index_search_on_generated_cases():
    import random

    from decision import relax
    from tests.snapshot_records import loaded_index

    pool = [
        "model.context_window >= 50",
        "model.context_window >= 80",
        "model.context_window >= 150",
        "model.context_window <= 30",
        "model.context_window <= 90",
        "model.context_window <= 200",
        "licence.commercial_use = permitted",
        "licence.commercial_use = prohibited",
        "model.context_window >= best(0)",
        "model.context_window >= best(10)",
        "model.context_window >= best(40)",
        "not(model.context_window >= best(0))",
        "not(model.context_window >= best(30))",
        "any(not(model.context_window >= best(0)); model.context_window <= 30)",
    ]
    lineups = [
        loaded_index({
            "lab/a": {"model.context_window": 100, "licence.commercial_use": "permitted"},
            "lab/b": {"model.context_window": 40, "licence.commercial_use": "prohibited"},
        }),
        loaded_index({
            "lab/a": {"model.context_window": 10, "licence.commercial_use": "prohibited"},
            "lab/b": {"model.context_window": 20, "licence.commercial_use": "prohibited"},
        }, lifecycle={"lab/a": "retired"}),
    ]
    rng = random.Random(458)
    mismatches = []
    for lineup in lineups:
        for _ in range(240):
            count = rng.randint(1, 4)
            where = [rng.choice(pool) for _ in range(count)]
            if rng.random() < 0.4:
                where.append(rng.choice(where))
            resolved = _resolved(where)
            got = relax.fewest(resolved, lineup, frozenset())
            expected = _per_index(resolved, lineup)
            if got != expected:
                mismatches.append((where, got, expected))
    assert mismatches == []


def test_excluded_bits_match_who_the_filter_can_admit():
    from decision.filter import _Run, apply
    from decision.relax import _excluded_bits
    from tests.snapshot_records import loaded_index

    def feasible_ids(index, where):
        resolved = _resolved(where)
        run = _Run(resolved, index)
        retired, structural = _excluded_bits(run)
        feasible = apply(resolved, index).feasible
        bits = 0
        for cid in feasible:
            bits |= 1 << run.pos[cid]
        assert bits & structural == 0
        if resolved.include_retired:
            assert bits & retired == retired & ~structural
        else:
            assert bits & retired == 0
        return set(feasible)

    active = loaded_index({
        "lab/open": {"model.weights_openness": "open_weights", "model.context_window": 10},
        "lab/closed": {"model.weights_openness": "closed_weights", "model.context_window": 10},
    })
    assert feasible_ids(active, []) == {"lab/open"}

    retired = loaded_index({
        "lab/old": {
            "model.weights_openness": "open_weights",
            "model.context_window": 10,
            "model.lifecycle": "retired",
        },
        "lab/open": {"model.weights_openness": "open_weights", "model.context_window": 10},
    }, lifecycle={"lab/old": "retired"})
    assert feasible_ids(retired, []) == {"lab/open"}
    assert feasible_ids(retired, ["model.lifecycle = retired"]) == {"lab/old"}

    closed_retired = loaded_index({
        "lab/old": {
            "model.weights_openness": "closed_weights",
            "model.context_window": 10,
            "model.lifecycle": "retired",
        },
    }, lifecycle={"lab/old": "retired"})
    assert feasible_ids(closed_retired, ["model.lifecycle = retired"]) == set()

    hosted = loaded_index({
        "lab/open": {"model.weights_openness": "open_weights", "model.context_window": 10},
    }, hosted=True)
    admitted = feasible_ids(hosted, [])
    assert "lab/open" not in admitted
    assert any(cid.startswith("sambanova/") for cid in admitted)
