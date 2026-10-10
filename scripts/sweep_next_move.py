"""Offline next_move budget proof over the public snapshot and decision fixtures.

    PYTHONPATH=$PWD python scripts/sweep_next_move.py --output /tmp/next-move-sweep.txt

Reuses the MODEL-334 template/scenario sweep and MODEL-351 reproductions.
No model calls, API keys, network requests, or private QA reports.
"""

from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
from typing import get_args

import yaml

from decision.bounded import AGENT_BYTES, compact_bytes, mcp_default_request, mcp_text_bytes, project
from decision.contract import Decision, ResponseOptions, TaskType, parse_spec
from decision.next_move import build_next_move, next_move_input_from_decision
from decision.summary import SUMMARY_BYTES
from qa.decide_budget import public_snapshot, public_spec
from scripts.render_summary_examples import examples, _service
from tests.test_decide_agent_budget import _cases

ROOT = Path(__file__).resolve().parents[1]


def sweep() -> dict:
    snapshot = public_snapshot()
    service = _service()
    cases = list(_cases())
    for path in sorted((ROOT / "tests/recall/specs").glob("*.yaml")):
        spec = yaml.safe_load(path.read_text())
        spec.pop("snapshot", None)
        cases.append(("recall:" + path.stem, spec))
    cases.extend(("example:" + name, spec) for name, spec in examples().items())
    cases.extend(("task_type:" + task, public_spec() | {"task_type": task}) for task in get_args(TaskType))
    # Every public domain and measured benchmark as a quality objective.
    cases.extend(("objective:" + dimension, {
        "spec_version": 1, "optimize": {"max": dimension},
    }) for dimension in sorted(set(snapshot.domain_ids()) | set(snapshot.benchmark_ids())))

    kinds = Counter()
    sources = Counter()
    statuses = Counter()
    refusals = Counter()
    failures = []
    maximum_body = maximum_mcp = maximum_summary = 0
    count = 0

    def record(label: str, body: dict) -> None:
        nonlocal maximum_body, maximum_mcp, maximum_summary, count
        body_bytes = compact_bytes(body)
        mcp_bytes = mcp_text_bytes(body)
        summary_bytes = len(body["summary_for_user"].encode("utf-8"))
        maximum_body = max(maximum_body, body_bytes)
        maximum_mcp = max(maximum_mcp, mcp_bytes)
        maximum_summary = max(maximum_summary, summary_bytes)
        assert body_bytes <= AGENT_BYTES, (label, body_bytes)
        assert mcp_bytes <= AGENT_BYTES, (label, mcp_bytes)
        assert summary_bytes <= SUMMARY_BYTES, (label, summary_bytes)
        move = body.get("next_move")
        if move is not None:
            assert move["kind"] != "ask_user" or move["options"], (label, move)
            assert body["summary_for_user"].endswith(move["say"]), label
            assert move["candidates"] == sorted(set(move["candidates"])), label
            assert len(move["candidates"]) <= 8, label
            assert len(move["candidates"]) != 1, label
            assert move["candidates_total"] >= len(move["candidates"]), label
            assert not ({"rank", "score", "leader"} & move.keys()), label
            kinds[move["kind"]] += 1
        else:
            assert body["status"] == "answered" and body["answer"]["kind"] == "separated", label
            kinds["absent_separated"] += 1
        statuses[body["status"]] += 1
        sources[label.partition(":")[0]] += 1
        count += 1

    for label, spec in cases:
        for explain in ("none", "summary", "full"):
            request = mcp_default_request(spec | {"explain": explain})
            try:
                status, body = service.decide(request, snapshot)
                if status != 200:
                    assert "byte budget" not in json.dumps(body), (label, body)
                    refusals[str(status)] += 1
                    continue
                record(label + ":" + explain, body)
            except Exception as exc:
                failures.append(f"{label} explain={explain}: {type(exc).__name__}: {exc}")

    fixtures = json.loads((ROOT / "tests/fixtures/decision/model-351-repros.json").read_text())
    for row in fixtures:
        for explain in ("none", "summary", "full"):
            label = "MODEL-351:" + row["name"] + ":" + explain
            try:
                decision = Decision.model_validate({
                    "contract_version": "2.15", "decision_id": row["decision_id"],
                    "snapshot": snapshot.snapshot_id, "spec_hash": "sha256:" + "0" * 64,
                    "explain": explain, **row["decision"],
                })
                spec = parse_spec(row["spec"], facets=None)
                inp = next_move_input_from_decision(decision, spec)
                body = project(decision, ResponseOptions(fields=["model", "evidence", "contributions"]),
                               spec=spec, not_applied=[])
                record(label, body)
                assert body.get("next_move") == build_next_move(inp), label
                again = project(decision, ResponseOptions(fields=["model", "evidence", "contributions"]),
                                spec=spec, not_applied=[])
                assert json.dumps(body, ensure_ascii=False).encode() == json.dumps(again, ensure_ascii=False).encode(), label
            except Exception as exc:
                failures.append(f"{label}: {type(exc).__name__}: {exc}")

    return {
        "decisions": count, "next_move_kinds": dict(sorted(kinds.items())),
        "sources": dict(sorted(sources.items())), "statuses": dict(sorted(statuses.items())),
        "request_refusals": dict(sorted(refusals.items())),
        "max_bounded_body_bytes": maximum_body, "max_mcp_text_bytes": maximum_mcp,
        "max_summary_bytes": maximum_summary, "exceptions": len(failures), "failures": failures,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = sweep()
    rendered = json.dumps(result, indent=2) + "\n"
    if args.output is not None:
        args.output.write_text(rendered)
    print(rendered, end="")
    return 1 if result["exceptions"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
