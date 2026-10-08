"""MODEL-334: MCP-default decide bodies stay within the agent byte budget."""

import json
from pathlib import Path

import pytest

from decision import contract
from decision.bounded import (
    AGENT_BYTES,
    DEFAULT_FIELDS,
    EXPLAIN_ROW_FIELDS,
    MEMBER_EVIDENCE_ITEMS,
    RESPONSE_BYTES,
    SUMMARY_RESERVE_BYTES,
    agent_summary,
    compact_bytes,
    mcp_default_request,
    mcp_text_bytes,
)
from decision.templates import load_catalogue
from qa.agent_harness import load_scenarios
from qa.decide_budget import public_snapshot as build_public_snapshot
from qa.record_fixtures import scenario_spec
from tests.test_decide_worker import _load_service


@pytest.fixture(scope="module")
def service():
    return _load_service()


@pytest.fixture(scope="module")
def public_snapshot():
    return build_public_snapshot()


def _cases():
    catalogue = load_catalogue()["templates"]
    templates = {row["id"]: row["spec"] for row in catalogue}
    cases = [(f"template:{row['id']}", row["spec"]) for row in catalogue]
    cases.extend(
        (f"scenario:{scenario['id']}", scenario_spec(scenario, templates))
        for scenario in load_scenarios()
    )
    return cases


def collect_sizes(service, snapshot):
    """One row per template or scenario at each explain level, MCP default shape."""
    rows = []
    for label, spec in _cases():
        copied = json.loads(json.dumps(spec))
        for explain in ("none", "summary", "full"):
            request = mcp_default_request(copied | {"explain": explain})
            status, body = service.decide(request, snapshot)
            rows.append({
                "label": label,
                "explain": explain,
                "status": status,
                "body_bytes": compact_bytes(body),
                "mcp_bytes": mcp_text_bytes(body, status=status),
                "body": body,
            })
    return rows


def test_agent_budget_drops_whole_records(monkeypatch):
    from decision import bounded

    original = {
        "results": [
            {
                "rank": 1, "model": "lab/a", "offering": {"model": "lab/a"}, "warnings": [],
                "evidence": [{"items": [{"record_id": "r1"}, {"record_id": "r2"}]}],
                "contributions": [{"dimension": "software_engineering"}],
            },
            {
                "rank": 2, "model": "lab/b", "offering": {"model": "lab/b"}, "warnings": [],
                "evidence": [{"items": [{"record_id": "r3"}]}],
                "estimates": [1, 2, 3],
            },
        ],
        "may_qualify": [{"model": "lab/c"}, {"model": "lab/d"}],
        "answer": {"kind": "separated", "members": ["lab/a"]},
        "status": "answered",
        "warnings": [],
        "explanation": {"omitted": {}, "note": "n", "not_applied": []},
    }
    # The fetch pointer is ~200 bytes. A one-byte shortfall cannot pay for it,
    # so the extra row has to be larger than the pointer or the fit cannot both
    # keep the top explanation and stay inside the budget.
    original["results"][1]["estimates"] = ["x" * 400]
    dropped = json.loads(json.dumps(original))
    dropped["results"].pop()
    bounded._omit(dropped, "results")
    bounded._note_fetch(dropped)
    budget = compact_bytes(dropped)
    assert compact_bytes(original) > budget
    monkeypatch.setattr(bounded, "RESPONSE_BYTES", budget)
    body = json.loads(json.dumps(original))
    bounded._fit_agent_budget(body)
    assert compact_bytes(body) <= budget
    assert body["results"][0]["evidence"] == original["results"][0]["evidence"]
    assert body["results"][0]["contributions"] == original["results"][0]["contributions"]
    assert body["may_qualify"] == original["may_qualify"]
    assert body["answer"]["members"] == ["lab/a"]
    assert [row["model"] for row in body["results"]] == ["lab/a"]
    assert body["explanation"]["omitted"]["results"] == 1
    assert "evidence_for: lab/a" in body["explanation"]["fetch"]
    assert "POST /v1/decide without fields" in body["explanation"]["fetch"]

    monkeypatch.setattr(bounded, "RESPONSE_BYTES", 1)
    tight = json.loads(json.dumps(original))
    with pytest.raises(contract.SpecError, match="16 KB agent budget"):
        bounded._fit_agent_budget(tight)


def test_every_template_and_scenario_stays_within_the_agent_budget(service, public_snapshot):
    rows = collect_sizes(service, public_snapshot)
    failures = []
    for row in rows:
        label = f"{row['label']} explain={row['explain']} status={row['status']}"
        if row["mcp_bytes"] > AGENT_BYTES or row["body_bytes"] > AGENT_BYTES:
            failures.append(f"{label} body={row['body_bytes']} mcp={row['mcp_bytes']}")
            continue
        if row["status"] >= 400:
            if "16 KB agent budget" in json.dumps(row["body"]):
                failures.append(f"{label} refused because essentials exceed the agent budget")
            continue
        body = row["body"]
        if body.get("representation") != "bounded":
            failures.append(f"{label} is not bounded")
            continue
        if row["body_bytes"] > RESPONSE_BYTES:
            failures.append(f"{label} body {row['body_bytes']} > RESPONSE_BYTES {RESPONSE_BYTES}")
        omitted = (body.get("explanation") or {}).get("omitted") or {}
        fetch = (body.get("explanation") or {}).get("fetch")
        if omitted and (not fetch or "POST /v1/decide" not in fetch):
            failures.append(f"{label} trimmed without a fetch pointer")
        if not omitted and fetch:
            failures.append(f"{label} has fetch with nothing omitted")
        summary = agent_summary(body)
        if len(summary.encode()) > SUMMARY_RESERVE_BYTES:
            failures.append(
                f"{label} summary {len(summary.encode())} bytes exceeds reserve {SUMMARY_RESERVE_BYTES}"
            )
        if "status" not in body or "answer" not in body:
            failures.append(f"{label} dropped status or answer")
        answer = body.get("answer")
        members = answer.get("members") if isinstance(answer, dict) else None
        explained = row["explain"] in ("summary", "full") and bool(members)
        if explained:
            entries = body.get("member_evidence")
            if not isinstance(entries, list):
                failures.append(f"{label} explained answer has no member_evidence")
                continue
            if [entry.get("model") for entry in entries] != list(members):
                failures.append(f"{label} member_evidence is not answer.members in order")
            for entry in entries:
                if not isinstance(entry.get("omitted_items"), int) or entry["omitted_items"] < 0:
                    failures.append(f"{label} {entry.get('model')} omitted_items is not a count")
                    continue
                count = 0
                for group in entry.get("evidence") or []:
                    for item in group.get("items") or []:
                        count += 1
                        try:
                            contract.EvidenceItem.model_validate(item)
                        except Exception as exc:
                            failures.append(f"{label} {entry.get('model')} item: {exc}")
                if count > MEMBER_EVIDENCE_ITEMS:
                    failures.append(f"{label} {entry.get('model')} kept {count} items")
                if len(entries) != len(members):
                    failures.append(f"{label} dropped a member entry")
        elif "member_evidence" in body:
            failures.append(f"{label} has member_evidence without an explained answer")
    assert rows, "no templates or scenarios"
    assert not failures, "\n".join(failures[:40])


def test_fit_drops_other_records_before_the_top_explanation(monkeypatch):
    """A tail row and a reading must go before the top row's evidence."""
    from decision import bounded

    evidence = [{"items": [{"record_id": "r1"}, {"record_id": "r2"}]}]
    kept = {
        "results": [{
            "rank": 1, "model": "lab/a", "offering": {"model": "lab/a"}, "warnings": [],
            "evidence": evidence,
        }],
        "may_qualify": [],
        "answer": {"kind": "separated", "members": ["lab/a"]},
        "status": "answered",
        "warnings": [],
        "explanation": {
            "omitted": {"by_model": 3, "results": 1, "may_qualify": 1, "reading": 1},
            "note": "n",
            "not_applied": [],
        },
    }
    kept["explanation"]["fetch"] = bounded._fetch_text(kept)
    monkeypatch.setattr(bounded, "RESPONSE_BYTES", bounded.compact_bytes(kept))
    body = json.loads(json.dumps({
        "results": [
            kept["results"][0],
            {
                "rank": 2, "model": "lab/b", "offering": {"model": "lab/b"}, "warnings": [],
                "evidence": [{"items": [{"record_id": "x" * 200}]}],
            },
        ],
        "may_qualify": [{"model": "lab/c"}],
        "answer": kept["answer"],
        "status": "answered",
        "warnings": [],
        "reading": {"do_not_claim": ["y" * 200]},
        "explanation": {"omitted": {"by_model": 3}, "note": "n", "not_applied": []},
    }))
    bounded._fit_agent_budget(body)
    assert compact_bytes(body) <= bounded.RESPONSE_BYTES
    assert body["results"] == kept["results"]
    assert body["results"][0]["evidence"] == evidence
    assert body["may_qualify"] == []
    assert "reading" not in body
    assert body["explanation"]["omitted"]["results"] == 1
    assert body["explanation"]["omitted"]["may_qualify"] == 1
    assert body["explanation"]["omitted"]["reading"] == 1
    assert body["explanation"]["omitted"]["by_model"] == 3
    assert "results.evidence" not in body["explanation"]["omitted"]
    assert "POST /v1/decide without fields" in body["explanation"]["fetch"]


def _fat_item(record_id: str, weight: float) -> dict:
    return {
        "record_id": record_id,
        "estimate_weight": weight,
        "directness": "direct",
        "requested_domain": "software_engineering",
        "note": "N" * 400,
    }


def _member(model: str, weights: list[float]) -> dict:
    return {
        "model": model,
        "omitted_items": 0,
        "evidence": [{
            "domain": "software_engineering",
            "items": [_fat_item(f"{model}#{weight:g}", weight) for weight in weights],
        }],
    }


def _budget_body() -> dict:
    return {
        "results": [
            {
                "rank": 1, "model": "lab/a", "offering": {"model": "lab/a"}, "warnings": [],
                "evidence": [{"items": ["A" * 500]}],
                "contributions": [{"dimension": "software_engineering", "pad": "C" * 500}],
                "estimates": ["E" * 80],
            },
            {
                "rank": 2, "model": "lab/b", "offering": {"model": "lab/b"}, "warnings": [],
                "evidence": [{"items": ["B" * 500]}],
                "contributions": [{"dimension": "software_engineering", "pad": "D" * 200}],
            },
            {
                "rank": 3, "model": "lab/c", "offering": {"model": "lab/c"}, "warnings": [],
                "evidence": [{"items": ["Z" * 500]}],
            },
        ],
        "may_qualify": [{"model": "lab/d", "pad": "M" * 300}],
        "answer": {"kind": "tied", "members": ["lab/a", "lab/b"]},
        "member_evidence": [_member("lab/a", [10, 5, 1]), _member("lab/b", [9, 4, 2])],
        "status": "answered",
        "warnings": [],
        "reading": {"do_not_claim": ["R" * 400]},
        "explanation": {"omitted": {}, "note": "n", "not_applied": []},
    }


def _ids(entry: dict) -> list[str]:
    return [item["record_id"] for group in entry["evidence"] for item in group["items"]]


def test_member_evidence_budget_drops_rows_before_items(monkeypatch):
    """Non-member rows go first. Member rows then lose evidence and contributions.

    may_qualify and the member items stay while that is enough.
    """
    from decision import bounded

    original = _budget_body()
    target = json.loads(json.dumps(original))
    target["results"].pop()
    bounded._omit(target, "results")
    models = {"lab/a", "lab/b"}
    while any(name in row for row in target["results"] for name in ("evidence", "contributions")):
        assert bounded._drop_member_row_evidence(target, target["results"], models)
    bounded._note_fetch(target)
    monkeypatch.setattr(bounded, "RESPONSE_BYTES", compact_bytes(target))
    body = json.loads(json.dumps(original))
    bounded._fit_agent_budget(body)
    assert compact_bytes(body) <= bounded.RESPONSE_BYTES
    assert [row["model"] for row in body["results"]] == ["lab/a", "lab/b"]
    assert "evidence" not in body["results"][0]
    assert "contributions" not in body["results"][0]
    assert body["results"][0]["estimates"] == ["E" * 80]
    assert body["results"][0]["warnings"] == []
    assert "evidence" not in body["results"][1]
    assert "contributions" not in body["results"][1]
    assert body["may_qualify"] == original["may_qualify"]
    assert "reading" in body
    assert _ids(body["member_evidence"][0]) == ["lab/a#10", "lab/a#5", "lab/a#1"]
    assert _ids(body["member_evidence"][1]) == ["lab/b#9", "lab/b#4", "lab/b#2"]
    assert body["explanation"]["omitted"]["results"] == 1
    assert body["explanation"]["omitted"]["results.evidence"] == 2
    assert body["explanation"]["omitted"]["results.contributions"] == 2
    assert "member_evidence.items" not in body["explanation"]["omitted"]


def test_member_evidence_trims_the_fullest_member_down_to_one_item(monkeypatch):
    """The later member loses an item first on a tie. Reading stays until items are at one."""
    from decision import bounded

    original = _budget_body()
    target = json.loads(json.dumps(original))
    target["results"].pop()
    bounded._omit(target, "results")
    models = {"lab/a", "lab/b"}
    while any(name in row for row in target["results"] for name in ("evidence", "contributions")):
        assert bounded._drop_member_row_evidence(target, target["results"], models)
    while target["may_qualify"]:
        target["may_qualify"].pop()
        bounded._omit(target, "may_qualify")
    while any(bounded._member_item_count(entry) > 1 for entry in target["member_evidence"]):
        assert bounded._trim_member_item(target, floor=1)
    bounded._note_fetch(target)
    monkeypatch.setattr(bounded, "RESPONSE_BYTES", compact_bytes(target))
    body = json.loads(json.dumps(original))
    bounded._fit_agent_budget(body)
    assert compact_bytes(body) <= bounded.RESPONSE_BYTES
    assert body["may_qualify"] == []
    assert "reading" in body
    assert [row["model"] for row in body["results"]] == ["lab/a", "lab/b"]
    assert _ids(body["member_evidence"][0]) == ["lab/a#10"]
    assert _ids(body["member_evidence"][1]) == ["lab/b#9"]
    assert body["member_evidence"][0]["evidence"][0]["items"][0]["note"] == "N" * 400
    assert body["member_evidence"][0]["omitted_items"] == 2
    assert body["member_evidence"][1]["omitted_items"] == 2
    assert body["explanation"]["omitted"]["member_evidence.items"] == 4
    assert body["explanation"]["omitted"]["may_qualify"] == 1
    assert len(body["member_evidence"]) == 2


def test_member_evidence_reaches_zero_items_only_after_every_other_cut(monkeypatch):
    from decision import bounded

    original = {
        "results": [{
            "rank": 1, "model": "lab/a", "offering": {"model": "lab/a"}, "warnings": [],
        }],
        "may_qualify": [],
        "answer": {"kind": "tied", "members": ["lab/a", "lab/b"]},
        "member_evidence": [_member("lab/a", [10, 1]), _member("lab/b", [9, 2])],
        "status": "answered",
        "warnings": [],
        "reading": {"do_not_claim": ["R" * 400]},
        "explanation": {"omitted": {}, "note": "n", "not_applied": []},
    }
    held = json.loads(json.dumps(original))
    while any(bounded._member_item_count(entry) > 1 for entry in held["member_evidence"]):
        assert bounded._trim_member_item(held, floor=1)
    bounded._note_fetch(held)
    monkeypatch.setattr(bounded, "RESPONSE_BYTES", compact_bytes(held))
    body = json.loads(json.dumps(original))
    bounded._fit_agent_budget(body)
    assert _ids(body["member_evidence"][0]) == ["lab/a#10"]
    assert _ids(body["member_evidence"][1]) == ["lab/b#9"]
    assert "reading" in body

    empty = json.loads(json.dumps(held))
    while any(bounded._member_item_count(entry) > 0 for entry in empty["member_evidence"]):
        assert bounded._trim_member_item(empty, floor=0)
    empty.pop("reading")
    bounded._omit(empty, "reading")
    bounded._note_fetch(empty)
    monkeypatch.setattr(bounded, "RESPONSE_BYTES", compact_bytes(empty))
    again = json.loads(json.dumps(original))
    bounded._fit_agent_budget(again)
    assert again["member_evidence"][0]["evidence"] == []
    assert again["member_evidence"][1]["evidence"] == []
    assert again["member_evidence"][0]["model"] == "lab/a"
    assert again["member_evidence"][1]["model"] == "lab/b"
    assert again["member_evidence"][0]["omitted_items"] == 2
    assert again["member_evidence"][1]["omitted_items"] == 2
    assert "reading" not in again
    assert [row["model"] for row in again["results"]] == ["lab/a"]


def test_default_decide_request_matches_the_shared_fixture():
    """Pins mcp_default_request and agent_summary to the MCP fixture."""
    fixture = json.loads(
        (Path(__file__).resolve().parents[1] / "mcp/test/fixtures/default-decide-request.json")
        .read_text(encoding="utf-8")
    )
    assert list(DEFAULT_FIELDS) == fixture["default_fields"]
    assert list(EXPLAIN_ROW_FIELDS) == fixture["explain_row_fields"]
    for case in fixture["requests"]:
        assert mcp_default_request(case["spec"]) == case["request"], case["name"]
    for case in fixture["summaries"]:
        assert agent_summary(case["body"]) == case["text"], case["name"]
