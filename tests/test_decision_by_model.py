"""Flat per-result fields, the model-grouped view, and ``why_not`` (MODEL-180).

Gaps 10 and 11 of the CLI-for-agents brief: an agent reads model, offering, cost
and rank from flat fields, and asks "why not X" without searching three lists.
"""

from __future__ import annotations

from datetime import date

import pytest

from decision.contract import Decision, parse_spec
from decision.engine import decide
from decision.registry import facet as facets
from decision.snapshot import SnapshotInputs, build_snapshot, load_built_snapshot
from decision.why_not import why_not
from tests.snapshot_records import SOURCES, evidence, fact, model, offering

# model, context window (None: not published), quality, [(provider, price in, price out)]
LINEUP = [
    ("lab/alpha", 200_000, 92.0, [("fireworks-ai", 3.0, 12.0), ("nvidia-nim", 2.0, 8.0)]),
    ("lab/beta", 128_000, 72.0, [("fireworks-ai", 1.0, 4.0)]),
    ("lab/gamma", 64_000, 88.0, [("fireworks-ai", 2.0, 8.0)]),
    ("lab/delta", None, 80.0, [("fireworks-ai", 2.5, 10.0)]),
]


def built_snapshot():
    models, offerings, rows = [], [], []
    for mid, context, quality, sellers in LINEUP:
        models.append(model(mid, facts=[
            fact("model", mid, "model.class", "text-generator"),
            fact("model", mid, "model.lifecycle", "active"),
            fact("model", mid, "model.context_window", context,
                 state="known" if context is not None else "unknown"),
            fact("model", mid, "model.weights_openness", "closed_weights"),
        ]))
        for provider, price_in, price_out in sellers:
            oid = f"{provider}/{mid}/global/standard"
            offerings.append(offering(mid, provider, facts=[
                fact("offering", oid, "offering.price.input", price_in, source="src-pricing"),
                fact("offering", oid, "offering.price.output", price_out, source="src-pricing"),
            ]))
        rows.append(evidence(mid, "quality", quality))
    built = build_snapshot(
        SnapshotInputs(models=models, offerings=offerings, evidence=rows, sources=SOURCES,
                       benchmark_domains={"quality": [("software_engineering", "direct")]}),
        gate=False,
        as_of=date(2026, 9, 28),
    )
    return built


@pytest.fixture(scope="module")
def index():
    return load_built_snapshot(built_snapshot(), include_archive=True, source="by_model test build")


def spec(explain: str = "full", **updates):
    return parse_spec(
        {
            "spec_version": 1,
            "task_type": "refactor",
            "capabilities": {"software_engineering": "required"},
            "task_tokens": {"input": 40000, "output": 4000},
            "where": ["model.class = text-generator", "model.context_window >= 100000"],
            "optimize": {"weights": {"quality": 0.78, "-offering.cost_per_task": 0.22}},
            "explain": explain,
            "limit": 20,
        } | updates,
        facets=facets,
    )


def run(index, explain: str = "full", **updates) -> Decision:
    return decide(spec(explain, **updates), index, facets=facets)


# ── flat fields on each result ─────────────────────────────────────────────


def test_each_offering_result_names_its_model_rank_and_cost(index):
    decision = run(index)
    flat = [
        (r.offering.model, r.offering.provider, r.rank, r.model_rank) for r in decision.results
    ]
    assert flat == [
        ("lab/alpha", "nvidia-nim", 1, 1),
        ("lab/alpha", "fireworks-ai", 2, 1),
        ("lab/beta", "fireworks-ai", 3, 2),
    ]
    assert all(r.model == r.offering.model for r in decision.results)


def test_cost_per_task_is_the_priced_task_and_matches_its_contribution(index):
    decision = run(index)
    # 40k tokens in and 4k out: alpha@nvidia-nim at $2 / $8 per million tokens.
    assert decision.results[0].cost_per_task == pytest.approx(0.08 + 0.032)
    for result in decision.results:
        part = next(c for c in result.contributions if c.dimension == "-offering.cost_per_task")
        assert result.cost_per_task == part.raw_value


def test_the_flat_fields_do_not_depend_on_the_explanation_level(index):
    none = run(index, "none")
    full = run(index, "full")
    assert none.results[0].contributions == []
    assert [(r.model, r.model_rank, r.cost_per_task) for r in none.results] == [
        (r.model, r.model_rank, r.cost_per_task) for r in full.results
    ]


def test_model_rank_counts_models_not_offerings(index):
    decision = run(index)
    ranks = sorted({r.model_rank for r in decision.results})
    assert ranks == list(range(1, len(ranks) + 1))
    assert len(ranks) == 2


# ── by_model ───────────────────────────────────────────────────────────────


def test_by_model_has_one_row_per_model_ranked_then_may_qualify_then_eliminated(index):
    decision = run(index)
    assert [(row.model, row.status, row.rank) for row in decision.by_model] == [
        ("lab/alpha", "ranked", 1),
        ("lab/beta", "ranked", 2),
        ("lab/delta", "may_qualify", None),
        ("lab/gamma", "eliminated", None),
    ]


def test_a_ranked_models_offerings_are_listed_best_first_with_flat_cost(index):
    alpha = run(index).by_model[0]
    assert [(o.offering.provider, o.status, o.rank) for o in alpha.offerings] == [
        ("nvidia-nim", "ranked", 1),
        ("fireworks-ai", "ranked", 2),
    ]
    assert alpha.offerings[0].cost_per_task == pytest.approx(0.112)
    assert alpha.offerings[1].cost_per_task == pytest.approx(0.168)


def test_by_model_says_why_an_offering_is_not_ranked(index):
    rows = {row.model: row for row in run(index).by_model}
    (unknown,) = rows["lab/delta"].offerings
    assert unknown.status == "may_qualify" and unknown.unknown == ["model.context_window"]
    (failed,) = rows["lab/gamma"].offerings
    assert failed.status == "eliminated" and failed.reason.startswith("model.context_window >=")
    assert failed.rank is None


def test_by_model_lists_eliminated_models_only_when_the_explanation_carries_them(index):
    summary = run(index, "summary")
    assert [(row.model, row.status) for row in summary.by_model] == [
        ("lab/alpha", "ranked"), ("lab/beta", "ranked"), ("lab/delta", "may_qualify"),
    ]
    assert run(index, "full").by_model[-1].status == "eliminated"


def test_by_model_agrees_with_results_on_every_model_rank(index):
    decision = run(index)
    by_rank = {row.model: row.rank for row in decision.by_model if row.status == "ranked"}
    assert by_rank == {r.model: r.model_rank for r in decision.results}


# ── why_not ────────────────────────────────────────────────────────────────


def test_why_not_an_eliminated_model_names_the_must_it_failed(index):
    answer = why_not(run(index), "lab/gamma")
    assert answer.verdict == "eliminated"
    assert answer.model_rank is None
    (failed,) = answer.failed
    assert failed.condition.startswith("model.context_window >=")
    assert failed.value == 64_000
    (cost,) = answer.constraint_costs
    assert cost.condition == failed.condition and cost.admits >= 1
    assert "model.context_window" in answer.summary


def test_why_not_a_may_qualify_model_lists_what_is_unknown(index):
    answer = why_not(run(index), "lab/delta")
    assert answer.verdict == "may_qualify"
    assert answer.unknown == ["model.context_window"]
    assert answer.failed == []
    assert "not known" in answer.summary


def test_why_not_a_ranked_model_says_where_it_ranked_and_what_moves_it_up(index):
    decision = run(index)
    answer = why_not(decision, "lab/beta")
    assert answer.verdict == "ranked"
    assert answer.model_rank == 2
    assert [(o.offering.provider, o.rank) for o in answer.offerings] == [("fireworks-ai", 3)]
    assert answer.tipping_points, "beta only takes the top at some weight"
    assert {p.new_top for p in answer.tipping_points} == {"lab/beta"}
    assert "#2" in answer.summary


def test_why_not_the_leader_says_it_is_first(index):
    answer = why_not(run(index), "lab/alpha")
    assert (answer.verdict, answer.model_rank) == ("ranked", 1)
    assert answer.tipping_points == []


def test_why_not_a_model_the_decision_never_saw_says_so(index):
    answer = why_not(run(index), "lab/nowhere")
    assert answer.verdict == "not_in_decision"
    assert "lab/nowhere" in answer.summary


def test_why_not_a_model_cut_by_the_limit_says_the_limit_did_it(index):
    decision = run(index, limit=1)
    assert decision.truncated.models == 1
    answer = why_not(decision, "lab/beta")
    assert answer.verdict == "not_in_decision"
    assert "limit" in answer.summary
