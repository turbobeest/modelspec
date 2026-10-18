"""Regenerate MCP assessments from the Python checker with verified fixture snapshots.

Run from the repository root:
    PYTHONPATH=$PWD python mcp/test/fixtures/generate-hardware-fit.py
"""

from __future__ import annotations

import json
from pathlib import Path

from decision.hardware_fit import HardwareFitResponse, check
from tests.test_hardware_fit import (
    REQUEST, fixture_snapshot, hardware_fit_record, lower_bound_record,
)


def assessments():
    cases = []
    for basis, memory_gb, record in (
        ("full", 24, hardware_fit_record()),
        ("lower_bound", 32, lower_bound_record()),
    ):
        request = dict(REQUEST)
        status, body = check(request, fixture_snapshot([record], memory_gb=memory_gb))
        HardwareFitResponse.model_validate(body)
        cases.append({"basis": basis, "request": request, "status": status, "body": body})
    return {
        "_generated": "by mcp/test/fixtures/generate-hardware-fit.py; do not hand-edit",
        "cases": cases,
    }


if __name__ == "__main__":
    output = Path(__file__).with_name("hardware-fit.json")
    output.write_text(json.dumps(assessments(), indent=2) + "\n", encoding="utf-8")
