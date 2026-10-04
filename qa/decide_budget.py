"""Regenerate the real public-catalogue responses used by MCP size tests.

    python -m qa.decide_budget
"""
from __future__ import annotations

import importlib.util
import json
from datetime import date
from pathlib import Path

from decision.bounded import DEFAULT_FIELDS
from decision.excluded import excluded_sources
from decision.registry import default as registry
from decision.snapshot import build_snapshot, collect_repo, load_premier, load_snapshot_bytes

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "mcp/test/fixtures/decide-budget.json"
KEY = b"model-293-public-budget-fixture"


def public_snapshot():
    built = build_snapshot(
        collect_repo(ROOT), registry=registry(),
        premier=load_premier(ROOT / "premier/slice-1.yaml"), as_of=date(2026, 10, 2),
        guard=excluded_sources(), gate=False,
    )
    return load_snapshot_bytes(built.to_bytes(key=KEY), key=KEY, source="public budget fixture")


def public_spec():
    return {"spec_version": 1, "capabilities": {"software_engineering": "required"},
            "optimize": {"max": "software_engineering"}, "explain": "none", "limit": 10}


def responses(service, snapshot):
    spec = {**public_spec(), "fields": list(DEFAULT_FIELDS)}
    status, body = service.decide(spec, snapshot)
    assert status == 200
    target = body["results"][0]["model"]
    status, detail = service.decide({**spec, "evidence_for": target}, snapshot)
    assert status == 200
    speech_spec = {"spec_version": 1, "where": ["model.class = transcriber"],
                   "optimize": {"min": "offering.cost_per_task"},
                   "explain": "none", "fields": list(DEFAULT_FIELDS), "limit": 10}
    status, speech = service.decide(speech_spec, snapshot)
    assert status == 200 and speech["coverage"]["kind"] == "out_of_coverage"
    return {"request": spec, "default": body, "drill_down": detail,
            "speech_request": speech_spec, "speech": speech}


def main():
    loader = importlib.util.spec_from_file_location("decide_budget_service", ROOT / "api/worker/src/decide_service.py")
    service = importlib.util.module_from_spec(loader)
    loader.loader.exec_module(service)
    FIXTURE.parent.mkdir(parents=True, exist_ok=True)
    FIXTURE.write_text(json.dumps(responses(service, public_snapshot()), ensure_ascii=False, indent=2) + "\n")
    print(f"wrote {FIXTURE.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
