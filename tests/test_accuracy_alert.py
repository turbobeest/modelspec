from __future__ import annotations

import json
from pathlib import Path

import yaml
import pytest

from scripts import accuracy_alert

RUN = "https://github.com/turbobeest/modelspec/actions/runs/37426044223"


def _report(status: str, sample: list[dict]) -> dict:
    return {
        "snapshot": "snap_da666e1f901c2821",
        "generated_at": "2026-10-06T06:55:39Z",
        "status": status,
        "layers": [
            {
                "name": "data_fidelity",
                "status": status,
                "gating": True,
                "summary": "Re-read 12 verified values; 1 did not verify.",
                "details": {"sample": sample},
            },
            {
                "name": "frozen_image_engine_recall",
                "status": "pass",
                "gating": False,
                "summary": "All 20 match.",
                "details": [],
            },
        ],
    }


def test_the_alert_names_each_value_that_did_not_verify_and_its_source() -> None:
    report = _report(
        "fail",
        [
            {
                "target": "fact:xai/subscription/supergrok#offering.subscription.usage_allowance",
                "outcome": "unreachable",
                "reason": "unreachable:model-173-xai-consumer-pricing#page",
                "source_urls": ["https://x.ai/pricing"],
            },
            {"target": "fact:a#b", "outcome": "verified", "reason": None, "source_urls": []},
            {"target": "fact:c#d", "outcome": "undetermined", "reason": "render_required",
             "source_urls": []},
        ],
    )

    assert accuracy_alert.body(report, RUN) == (
        "Snapshot `snap_da666e1f901c2821`, generated 2026-10-06T06:55:39Z.\n"
        "\n"
        "| Layer | Status | Gate | Summary |\n"
        "| --- | --- | --- | --- |\n"
        "| data_fidelity | fail | yes | Re-read 12 verified values; 1 did not verify. |\n"
        "| frozen_image_engine_recall | pass | no | All 20 match. |\n"
        "\n"
        "Values that did not verify:\n"
        "\n"
        "- `fact:xai/subscription/supergrok#offering.subscription.usage_allowance`: "
        "unreachable (unreachable:model-173-xai-consumer-pricing#page)\n"
        "  - https://x.ai/pricing\n"
        "\n"
        f"Run: {RUN}\n"
    )


def test_a_run_that_wrote_no_report_still_alerts(tmp_path: Path) -> None:
    out = tmp_path / "body.md"

    assert accuracy_alert.main(
        ["--report", str(tmp_path / "missing.json"), "--run-url", RUN, "--output", str(out)]
    ) == 0
    assert out.read_text() == (
        f"The nightly wrote no report: it failed before or during the run.\n\nRun: {RUN}\n"
    )


def test_the_alert_preserves_failure_transport_status_source_and_copies() -> None:
    report = _report("fail", [{
        "target": "fact:lab/blocked#context", "outcome": "unreachable",
        "reason": "unreachable:source#table", "source_urls": ["https://example.test/source"],
        "sources": [{
            "source_id": "source", "transport": "http", "declared_fetch": "http",
            "http_status": 403, "error_category": "http_error", "copy_ref": None,
            "cited_copy_ref": "sha256:" + "a" * 64,
        }],
    }])

    text = accuracy_alert.body(report, RUN)
    assert "fact:lab/blocked#context" in text
    assert "source `source`; transport `http`; HTTP 403; error `http_error`" in text
    assert "cited copy `sha256:" + "a" * 64 + "`; current copy `none`" in text


def test_main_reads_the_written_report(tmp_path: Path) -> None:
    path = tmp_path / "accuracy.json"
    path.write_text(json.dumps(_report("pass", [])))
    out = tmp_path / "body.md"

    accuracy_alert.main(["--report", str(path), "--run-url", RUN, "--output", str(out)])

    assert "Values that did not verify" not in out.read_text()
    assert out.read_text().endswith(f"Run: {RUN}\n")


def test_the_nightly_opens_and_closes_the_alert_issue() -> None:
    workflow = yaml.load(
        Path(".github/workflows/accuracy-nightly.yml").read_text(), Loader=yaml.BaseLoader
    )
    job = workflow["jobs"]["accuracy"]
    steps = {step.get("name"): step for step in job["steps"]}

    assert job["permissions"]["issues"] == "write"
    alert = steps["Alert the orchestrator"]
    assert alert["if"] == "failure() && github.ref == 'refs/heads/main'"
    assert "scripts/accuracy_alert.py" in alert["run"]
    assert "--label alert" in alert["run"]
    # An empty list must give no number, not "null" (the first alert would fail).
    assert "--jq '.[0].number // empty'" in alert["run"]
    clear = steps["Close the alert after a green night"]
    assert clear["if"] == "success() && github.ref == 'refs/heads/main'"


@pytest.mark.parametrize("list_status,numbers,close_status,expected_status,closed", [
    (42, "", 0, 42, []),
    (0, "", 0, 0, []),
    (0, "11\n22\n", 0, 0, ["11", "22"]),
    (0, "11\n22\n", 43, 43, ["11"]),
], ids=["list-failure", "empty", "closed", "close-failure"])
def test_nightly_close_alert_propagates_command_results(
    tmp_path, list_status, numbers, close_status, expected_status, closed,
):
    import os
    import subprocess

    workflow = yaml.safe_load(Path(".github/workflows/accuracy-nightly.yml").read_text())
    step = next(s for s in workflow["jobs"]["accuracy"]["steps"]
                if s.get("name") == "Close the alert after a green night")
    stub = '''gh() {
      if [ "$1 $2" = "issue list" ]; then
        printf '%s' "$ISSUES"
        return "$LIST_STATUS"
      fi
      if [ "$1 $2" = "issue close" ]; then
        printf '%s\\n' "$3" >> closed
        return "$CLOSE_STATUS"
      fi
      return 99
    }
'''
    result = subprocess.run(
        ["bash", "-e", "-c", stub + step["run"]], cwd=tmp_path, capture_output=True, text=True,
        env=os.environ | {"ISSUES": numbers, "LIST_STATUS": str(list_status),
                          "CLOSE_STATUS": str(close_status), "RUN_URL": "offline"},
    )
    assert result.returncode == expected_status, result.stdout + result.stderr
    calls = tmp_path / "closed"
    assert (calls.read_text().splitlines() if calls.exists() else []) == closed
