"""Render the three MODEL-339 copy-gate examples from the public snapshot.

    PYTHONPATH=$PWD python scripts/render_summary_examples.py

Uses the same snapshot the budget tests build (as_of 2026-10-02). No vendor call.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

from decision.bounded import mcp_text_bytes
from qa.decide_budget import public_snapshot

ROOT = Path(__file__).resolve().parents[1]

FIELDS = [
    "model", "model_rank", "cost_per_task", "estimates", "p_best", "warnings", "evidence",
]

EXAMPLES = {
    # Five models have no software_engineering value. unknown(fail) excludes
    # them, so the decision is answered and the tie is the answer. Without
    # that gate the same four models are tied and status is partial.
    "tie": {
        "spec_version": 1,
        "where": [
            "model.class = text-generator",
            "software_engineering >= 0 unknown(fail)",
        ],
        "capabilities": {
            "software_engineering": "required",
            "agentic_tool_use": "required",
        },
        "optimize": {"max": "software_engineering"},
        "explain": "summary",
        "limit": 8,
        "fields": FIELDS,
    },
    "no_feasible": {
        "spec_version": 1,
        "where": ["model.max_output_tokens >= 1000000000"],
        "optimize": {"min": "offering.cost_per_task"},
        "explain": "none",
        "limit": 5,
        "fields": ["model"],
    },
    "constrained": {
        "spec_version": 1,
        "where": ["model.class = text-generator", "reasoning >= 0 unknown(fail)"],
        "capabilities": {"thread_safety": "required"},
        "optimize": {"max": "reasoning"},
        "explain": "summary",
        "limit": 5,
        "fields": FIELDS,
    },
}


def _service():
    path = ROOT / "api/worker/src/decide_service.py"
    loader = importlib.util.spec_from_file_location("summary_examples_service", path)
    module = importlib.util.module_from_spec(loader)
    loader.loader.exec_module(module)
    return module


def render(service, snapshot) -> list[dict]:
    rows = []
    for name, spec in EXAMPLES.items():
        status, body = service.decide(spec, snapshot)
        if status != 200:
            raise SystemExit(f"{name} returned {status}: {json.dumps(body, ensure_ascii=False)[:2000]}")
        answer = body.get("answer")
        rows.append({
            "name": name,
            "spec": spec,
            "decision_status": body.get("status"),
            "answer_kind": None if answer is None else answer.get("kind"),
            "answer_members": None if answer is None else answer.get("members"),
            "summary_for_user": body.get("summary_for_user"),
            "must_mention": body.get("must_mention"),
            "mcp_text_bytes": mcp_text_bytes(body),
        })
    return rows


def main() -> None:
    rows = render(_service(), public_snapshot())
    tie, empty, constrained = rows
    if tie["answer_kind"] != "tied" or not tie["answer_members"]:
        raise SystemExit("tie example did not tie: " + json.dumps(tie, ensure_ascii=False)[:2000])
    if empty["decision_status"] != "no_feasible" or empty["answer_members"] is not None:
        raise SystemExit("null example was not no_feasible: " + json.dumps(empty, ensure_ascii=False)[:2000])
    if "not applied" not in (constrained["summary_for_user"] or ""):
        raise SystemExit("constrained example did not say not applied: " + json.dumps(constrained, ensure_ascii=False)[:2000])
    text = json.dumps(rows, ensure_ascii=False, indent=2)
    print(text)
    if tie["answer_kind"] != "tied" or not tie["answer_members"]:
        raise SystemExit("tie example did not tie")
    if empty["decision_status"] != "no_feasible" or empty["answer_members"] is not None:
        raise SystemExit("null example was not no_feasible")
    summary = constrained["summary_for_user"] or ""
    if "not applied" not in summary or "proxy" not in summary:
        raise SystemExit("constrained example is missing a not-applied or proxy caveat")


if __name__ == "__main__":
    main()
