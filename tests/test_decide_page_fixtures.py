"""The decide page fixtures are the engine's own answers (MODEL-163).

`web/src/decide/__fixtures__/compact-full.json` and `compact-summary.json` are
what the Worker's `decide_service` returns for the page's default spec on a
synthetic snapshot: four models sold by one provider, ranked on a synthetic
`quality` benchmark. The page's adapter tests read them, so a change to the
decision's shape reaches those tests. Regenerate with
`MODELSPEC_WRITE_FIXTURES=1 pytest tests/test_decide_page_fixtures.py`.
"""

from __future__ import annotations

import importlib.util
import json
import os
from datetime import date
from pathlib import Path

import pytest

from decision.snapshot import SnapshotInputs, build_snapshot, load_built_snapshot
from tests.snapshot_records import SOURCES, evidence, fact, model, offering

REPO = Path(__file__).resolve().parents[1]
WEB = REPO / "web" / "src" / "decide" / "__fixtures__"

# model, context, openness, quality, price in, price out, throughput, ttft, retention
LINEUP = [
    ("lab/alpha", 200_000, "closed_weights", 92.0, 3.0, 12.0, 95, 420, 0),
    ("lab/beta", 128_000, "open_weights", 72.0, 1.0, 4.0, 55, 780, 30),
    ("lab/gamma", 256_000, "open_weights", 88.0, 2.0, 8.0, 80, 510, 30),
    ("lab/delta", 64_000, "closed_weights", 36.0, 0.5, 2.0, 30, 1200, 30),
]


# Measurement intervals that make alpha and gamma overlap, so the engine answers "tied".
TIED_INTERVALS = {"lab/alpha": [86.0, 98.0], "lab/gamma": [82.0, 94.0]}


def _snapshot(intervals=None):
    intervals = intervals or {}
    models, offerings, rows = [], [], []
    for mid, context, openness, quality, price_in, price_out, tps, ttft, days in LINEUP:
        models.append(model(mid, facts=[
            fact("model", mid, "model.class", "text-generator"),
            fact("model", mid, "model.lifecycle", "active"),
            fact("model", mid, "model.context_window", context),
            fact("model", mid, "model.weights_openness", openness),
            fact("model", mid, "licence.user_cap", "unbounded"),
        ]))
        oid = f"cloud/{mid}/global/standard"
        offerings.append(offering(mid, "cloud", facts=[
            fact("offering", oid, "offering.price.input", price_in, source="src-pricing"),
            fact("offering", oid, "offering.price.output", price_out, source="src-pricing"),
            fact("offering", oid, "offering.speed.throughput", tps),
            fact("offering", oid, "offering.speed.time_to_first_token", ttft),
            fact("offering", oid, "offering.data.retention", days),
        ]))
        rows.append(evidence(mid, "quality", quality, interval=intervals.get(mid)))
    built = build_snapshot(
        SnapshotInputs(models=models, offerings=offerings, evidence=rows, sources=SOURCES,
                       benchmark_domains={"quality": [("software_engineering", "direct")]}),
        gate=False,
        as_of=date(2026, 9, 25),
    )
    return load_built_snapshot(built, include_archive=True, source="page fixture build")


def _service():
    source = REPO / "api" / "worker" / "src" / "decide_service.py"
    loader = importlib.util.spec_from_file_location("modelspec_decide_service_fixtures", source)
    module = importlib.util.module_from_spec(loader)
    loader.loader.exec_module(module)
    return module


def _spec(explain):
    """What `toDecisionSpec` sends for the default task on the small vocabulary."""
    return {
        "spec_version": 1,
        "snapshot": "latest",
        "task_type": "refactor",
        "capabilities": {"software_engineering": "required"},
        "task_tokens": {"input": 40000, "output": 4000},
        "where": ["model.class = text-generator", "quality >= 60 @independent"],
        "optimize": {"weights": {"quality": 0.78, "-offering.cost_per_task": 0.22}},
        "unknowns": "default",
        "explain": explain,
        "limit": 20,
    }


@pytest.mark.parametrize("explain", ["full", "summary"])
def test_the_page_fixture_is_the_engines_answer(explain):
    service = _service()
    status, body = service.decide(_spec(explain), _snapshot())
    assert status == 200, body
    path = WEB / f"compact-{explain}.json"
    fresh = json.dumps(body, indent=2, ensure_ascii=False) + "\n"
    if os.environ.get("MODELSPEC_WRITE_FIXTURES"):
        path.write_text(fresh, encoding="utf-8")
    assert path.read_text(encoding="utf-8") == fresh, (
        f"{path.name} is stale; regenerate with "
        "MODELSPEC_WRITE_FIXTURES=1 pytest tests/test_decide_page_fixtures.py"
    )


def test_the_tied_page_fixture_is_the_engines_answer():
    service = _service()
    status, body = service.decide(_spec("full"), _snapshot(TIED_INTERVALS))
    assert status == 200, body
    assert body["answer"]["kind"] == "tied"
    path = WEB / "compact-tied-full.json"
    fresh = json.dumps(body, indent=2, ensure_ascii=False) + "\n"
    if os.environ.get("MODELSPEC_WRITE_FIXTURES"):
        path.write_text(fresh, encoding="utf-8")
    assert path.read_text(encoding="utf-8") == fresh, (
        f"{path.name} is stale; regenerate with "
        "MODELSPEC_WRITE_FIXTURES=1 pytest tests/test_decide_page_fixtures.py"
    )


# ── MODEL-200: decisions with `access` ────────────────────────────────────

PLAN_SPECS = {
    # A Max 20x holder in Claude Code: plan routes with a break-even, and the
    # estate answer through the plan at $0 with its coverage.
    "plans-coding-full": ({"kind": "coding_tool", "harness": "claude-code"},
                          {"plans": ["anthropic/subscription/max-20x"]}),
    # The same holder for their own software: pay-per-use, a plan route with a
    # null price and no break-even, and the estate warning.
    "plans-own-software-full": ("own_software", {"plans": ["anthropic/subscription/max-20x"]}),
}


@pytest.mark.parametrize("name", sorted(PLAN_SPECS))
def test_the_plan_page_fixtures_are_the_engines_answer(name):
    from tests.plan_records import CONTEXT, inputs

    access, estate = PLAN_SPECS[name]
    snapshot = load_built_snapshot(build_snapshot(inputs(max_coverage=True), as_of=date(2026, 9, 29)),
                                   include_archive=True, source="plan page fixture build")
    status, body = _service().decide(
        {"spec_version": 1, "optimize": {"max": CONTEXT}, "explain": "full",
         "access": access, "estate": estate},
        snapshot,
    )
    assert status == 200, body
    assert any(result.get("plans") for result in body["results"])
    path = WEB / f"{name}.json"
    fresh = json.dumps(body, indent=2, ensure_ascii=False) + "\n"
    if os.environ.get("MODELSPEC_WRITE_FIXTURES"):
        path.write_text(fresh, encoding="utf-8")
    assert path.read_text(encoding="utf-8") == fresh, (
        f"{path.name} is stale; regenerate with "
        "MODELSPEC_WRITE_FIXTURES=1 pytest tests/test_decide_page_fixtures.py"
    )
