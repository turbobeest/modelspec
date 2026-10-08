"""Render the MODEL-339 copy-gate examples from the public snapshot.

    PYTHONPATH=$PWD python scripts/render_summary_examples.py

Uses the same snapshot the budget tests build (as_of 2026-10-02). No vendor call.
Specs come from the recall set and the template registry. The script adds
``fields`` so the bounded response carries the summary. It does not add gates.
"""

from __future__ import annotations

import importlib.util
import json
from copy import deepcopy
from pathlib import Path

import yaml

from decision.bounded import mcp_text_bytes
from decision.templates import template_by_id
from qa.decide_budget import public_snapshot

ROOT = Path(__file__).resolve().parents[1]

FIELDS = [
    "model", "model_rank", "cost_per_task", "estimates", "p_best", "warnings", "evidence",
]

NO_FEASIBLE = "ModelSpec found no model that meets every requirement, so it names no pick."
PARTIAL = "ModelSpec's answer is incomplete, so it names no pick."
NULL_ANSWER = "ModelSpec has no answer for this request, so it names no pick."
NO_CLASS = "No model class was required, so results span every class"
COST_ONLY = "This answer is ordered by cost only; it is not a quality ranking."
TIE_COST = "Tie-breakers are conditional; cost order is not quality order."


def _sentences(paragraph: str) -> list[str]:
    parts = paragraph.split(". ")
    found: list[str] = []
    for index, part in enumerate(parts):
        if index < len(parts) - 1:
            found.append(part + ".")
        else:
            found.append(part if part.endswith(".") else part)
    return found


def _service():
    path = ROOT / "api/worker/src/decide_service.py"
    loader = importlib.util.spec_from_file_location("summary_examples_service", path)
    module = importlib.util.module_from_spec(loader)
    loader.loader.exec_module(module)
    return module


def _recall(name: str) -> dict:
    raw = yaml.safe_load((ROOT / "tests/recall/specs" / name).read_text())
    raw.pop("task_type", None)
    raw.pop("snapshot", None)
    raw["fields"] = ["model"]
    return raw


def examples() -> dict[str, dict]:
    regulated = deepcopy(template_by_id("regulated-best")["spec"])
    regulated["explain"] = "summary"
    regulated["limit"] = 8
    regulated["fields"] = list(FIELDS)
    return {
        "tie": regulated,
        "partial": _recall("Q01.yaml"),
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
            "fields": list(FIELDS),
        },
        "cost_only": {
            "spec_version": 1,
            "optimize": {"min": "offering.cost_per_task"},
            "explain": "full",
            "limit": 5,
            "fields": list(FIELDS),
        },
    }


def render(service, snapshot) -> list[dict]:
    rows = []
    for name, spec in examples().items():
        status, body = service.decide(spec, snapshot)
        if status != 200:
            raise SystemExit(
                f"{name} returned {status}: {json.dumps(body, ensure_ascii=False)[:2000]}"
            )
        answer = body.get("answer")
        rows.append({
            "name": name,
            "spec": spec,
            "decision_status": body.get("status"),
            "answer_kind": None if answer is None else answer.get("kind"),
            "answer_members": None if answer is None else answer.get("members"),
            "cheapest": (
                None if answer is None else (answer.get("tie_breakers") or {}).get("cheapest")
            ),
            "summary_for_user": body.get("summary_for_user"),
            "must_mention": body.get("must_mention"),
            "mcp_text_bytes": mcp_text_bytes(body),
        })
    return rows


def _check(rows: list[dict]) -> None:
    by_name = {row["name"]: row for row in rows}
    tie = by_name["tie"]
    if tie["decision_status"] != "answered" or tie["answer_kind"] != "tied":
        raise SystemExit("tie example is not an answered tie: " + json.dumps(tie)[:2000])
    if "software_engineering >= 0" in json.dumps(tie["spec"]):
        raise SystemExit("tie example added a gate")
    if not str(tie["summary_for_user"]).startswith("ModelSpec's answer is a tie among "):
        raise SystemExit("tie summary does not state the tie")
    if TIE_COST not in tie["summary_for_user"] or TIE_COST not in tie["must_mention"]:
        raise SystemExit("tie example did not name the cost tie-break")
    if COST_ONLY in (tie["summary_for_user"] or ""):
        raise SystemExit("quality tie was described as cost-only")

    partial = by_name["partial"]
    if partial["decision_status"] != "partial":
        raise SystemExit("Q01 was not partial: " + json.dumps(partial)[:2000])
    if not str(partial["summary_for_user"]).startswith(PARTIAL):
        raise SystemExit("partial summary names an answer")
    if "tied" in (partial["summary_for_user"] or ""):
        raise SystemExit("partial summary says tied")

    empty = by_name["no_feasible"]
    if empty["decision_status"] != "no_feasible" or empty["answer_members"] is not None:
        raise SystemExit("null example was not no_feasible: " + json.dumps(empty)[:2000])
    summary = empty["summary_for_user"] or ""
    if "tied" in summary or not summary.startswith(NO_FEASIBLE):
        raise SystemExit("no_feasible summary presents an answer")
    if "These are options, not an answer." not in summary:
        raise SystemExit("no_feasible summary does not list relaxations as options")

    constrained = by_name["constrained"]
    text = constrained["summary_for_user"] or ""
    if not text.startswith(NULL_ANSWER):
        raise SystemExit("null answer names a pick")
    if "not applied" not in text or "proxy" not in text:
        raise SystemExit("constrained example is missing a not-applied or proxy caveat")
    if "was not applied; ModelSpec did not check it." in text:
        raise SystemExit("constrained summary repeats a not-applied requirement")

    cost = by_name["cost_only"]
    shown = cost["summary_for_user"] or ""
    if COST_ONLY not in shown or COST_ONLY not in cost["must_mention"]:
        raise SystemExit("cost-only example did not say it is not a quality ranking")
    if NO_CLASS not in shown or not any(item.startswith(NO_CLASS) for item in cost["must_mention"]):
        raise SystemExit("cost-only example did not state the class scope")
    if shown.count(NO_CLASS) != 1:
        raise SystemExit("cost-only example repeats the class scope")
    if "where" in cost["spec"]:
        raise SystemExit("cost-only example has a gate")
    for row in rows:
        sentences = _sentences(row["summary_for_user"] or "")
        if len(sentences) != len(set(sentences)):
            raise SystemExit(row["name"] + " repeats a sentence: " + row["summary_for_user"])


def main() -> None:
    rows = render(_service(), public_snapshot())
    _check(rows)
    print(json.dumps(rows, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
