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

from decision.snapshot import build_snapshot, load_built_snapshot
from tests.snapshot_records import TIED_INTERVALS, build_lineup_snapshot

REPO = Path(__file__).resolve().parents[1]
WEB = REPO / "web" / "src" / "decide" / "__fixtures__"

def _snapshot(intervals=None):
    return load_built_snapshot(build_lineup_snapshot(intervals), include_archive=True,
                               source="page fixture build")


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

MAX_20X = {"plans": ["anthropic/subscription/max-20x"]}

PLAN_SPECS = {
    # A Max 20x holder in Claude Code: plan routes with a break-even, and the
    # estate answer through the plan at $0 with its coverage.
    "plans-coding-full": ({"kind": "coding_tool", "harness": "claude-code"}, MAX_20X, True),
    # The same holder for their own software: pay-per-use, a plan route with a
    # null price and no break-even, and the estate warning.
    "plans-own-software-full": ("own_software", MAX_20X, True),
    # MODEL-202: the board's other access answers. A chat-app holder whose
    # plans' coverage is sourced: plan routes priced by the month.
    "plans-chat-app-full": ("chat_app", MAX_20X, True),
    # Today's catalogue: no plan's coverage is verified yet, so a chat-app
    # answer is all may-qualify, and the held Max 20x may cover each row.
    "plans-chat-app-unverified-full": ("chat_app", MAX_20X, False),
    # The same in a coding tool: pay-per-use ranks; the plan may cover it.
    "plans-coding-unverified-full": ("coding_tool", MAX_20X, False),
    # Own hardware: only self-hostable rows, reached through a held device.
    "plans-own-hardware-full": ("own_hardware", {"devices": ["apple_m3_max"]}, True),
    # No access ("Doesn't matter"): every route, the cheapest named per model.
    "plans-any-full": (None, {"plans": ["anthropic/subscription/max-20x"],
                              "devices": ["apple_m3_max"]}, True),
    # MODEL-205: a Cursor Pro holder in a coding tool. Cursor sells no
    # pay-per-use, so its plan reaches each covered model's own row.
    "plans-vendor-coding-full": ("coding_tool", {"plans": ["cursor/subscription/pro"]},
                                 "vendor"),
}


@pytest.mark.parametrize("name", sorted(PLAN_SPECS))
def test_the_plan_page_fixtures_are_the_engines_answer(name):
    from tests.plan_records import CONTEXT, inputs, vendor_inputs

    access, estate, max_coverage = PLAN_SPECS[name]
    records = vendor_inputs() if max_coverage == "vendor" else inputs(max_coverage=max_coverage)
    snapshot = load_built_snapshot(
        build_snapshot(records, as_of=date(2026, 9, 29)),
        include_archive=True, source="plan page fixture build")
    spec = {"spec_version": 1, "optimize": {"max": CONTEXT}, "explain": "full", "estate": estate}
    if access is not None:
        spec["access"] = access
    status, body = _service().decide(spec, snapshot)
    assert status == 200, body
    assert body["with_estate"] is not None
    path = WEB / f"{name}.json"
    fresh = json.dumps(body, indent=2, ensure_ascii=False) + "\n"
    if os.environ.get("MODELSPEC_WRITE_FIXTURES"):
        path.write_text(fresh, encoding="utf-8")
    assert path.read_text(encoding="utf-8") == fresh, (
        f"{path.name} is stale; regenerate with "
        "MODELSPEC_WRITE_FIXTURES=1 pytest tests/test_decide_page_fixtures.py"
    )


def test_the_vendor_vocabulary_fixture_is_the_builders_output():
    """MODEL-205: the page parses a real vocabulary carrying ``vendors``
    (``vendor-vocabulary.test.ts``), so a schema that refused the field fails there."""
    from decision.vocabulary import build_vocabulary
    from tests.plan_records import vendor_inputs

    snapshot = load_built_snapshot(
        build_snapshot(vendor_inputs(), as_of=date(2026, 9, 29)),
        include_archive=True, source="vendor vocabulary fixture build")
    vocabulary = build_vocabulary(snapshot)
    assert vocabulary["vendors"]["cursor"] == "Cursor"
    path = WEB / "vocabulary-vendors.json"
    fresh = json.dumps(vocabulary, indent=2, ensure_ascii=False) + "\n"
    if os.environ.get("MODELSPEC_WRITE_FIXTURES"):
        path.write_text(fresh, encoding="utf-8")
    assert path.read_text(encoding="utf-8") == fresh, (
        f"{path.name} is stale; regenerate with "
        "MODELSPEC_WRITE_FIXTURES=1 pytest tests/test_decide_page_fixtures.py"
    )
