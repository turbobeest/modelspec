from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

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


def test_the_alert_publishes_counts_for_values_that_did_not_verify() -> None:
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
    report["layers"][0]["counts"] = {
        "verified": 1, "mismatch": 0, "unreachable": 1, "undetermined": 1,
    }

    text = accuracy_alert.body(report, RUN)

    assert text == (
        "**Overall: FAIL**\n"
        "\n"
        "| Layer | Status | Gate | Summary |\n"
        "| --- | --- | --- | --- |\n"
        "| data_fidelity | FAIL | yes | failures 1; mismatches 0; unreachable 1; undetermined 1. |\n"
        "| frozen_image_engine_recall | PASS | no | failures 0; mismatches 0; unreachable 0; undetermined 0. |\n"
        "\n"
        "details are not published; run the nightly profile locally against the private data\n"
        "\n"
        f"Run: {RUN}\n"
    )
    assert "fact:" not in text
    assert "https://x.ai/pricing" not in text


def test_a_run_that_wrote_no_report_still_alerts(tmp_path: Path) -> None:
    out = tmp_path / "body.md"

    assert accuracy_alert.main(
        ["--report", str(tmp_path / "missing.json"), "--run-url", RUN, "--output", str(out)]
    ) == 0
    assert out.read_text() == (
        f"the run failed before a report was written\n\nRun: {RUN}\n"
    )


def test_python_is_installed_before_the_private_fetch() -> None:
    workflow = yaml.load(
        Path(".github/workflows/accuracy-nightly.yml").read_text(), Loader=yaml.BaseLoader
    )
    names = [step.get("name") for step in workflow["jobs"]["accuracy"]["steps"]]
    fetch = names.index("Read private verification records")
    assert names.index("Set up Python") < fetch
    assert names.index("Install dependencies") < fetch


def test_the_alert_builder_runs_when_yaml_cannot_be_imported(tmp_path: Path) -> None:
    report = {
        "status": "fail",
        "layers": [{
            "name": "data_fidelity",
            "status": "fail",
            "gating": True,
            "counts": {"mismatch": 1, "unreachable": 0, "undetermined": 0},
            "details": {"sample": [{"target": "fact:yaml-block-sentinel"}]},
        }],
    }
    report_path = tmp_path / "accuracy.json"
    report_path.write_text(json.dumps(report), encoding="utf-8")
    present = tmp_path / "present.md"
    missing = tmp_path / "missing.md"
    driver = tmp_path / "driver.py"
    root = str(Path(__file__).resolve().parents[1])
    driver.write_text(
        "import sys\n"
        "class BlockYaml:\n"
        "    def find_spec(self, fullname, path, target=None):\n"
        "        if fullname == 'yaml' or fullname.startswith('yaml.'):\n"
        "            raise ModuleNotFoundError(fullname)\n"
        "        return None\n"
        "sys.meta_path.insert(0, BlockYaml())\n"
        "try:\n"
        "    import yaml\n"
        "except ModuleNotFoundError:\n"
        "    pass\n"
        "else:\n"
        "    raise SystemExit('yaml imported')\n"
        "from scripts.accuracy_alert import main\n"
        f"present_code = main(['--report', {str(report_path)!r}, '--run-url', {RUN!r},"
        f" '--output', {str(present)!r}])\n"
        f"missing_code = main(['--report', {str(tmp_path / 'no-report.json')!r},"
        f" '--run-url', {RUN!r}, '--output', {str(missing)!r}])\n"
        "if present_code != 0 or missing_code != 0:\n"
        "    raise SystemExit(f'codes {present_code} {missing_code}')\n",
        encoding="utf-8",
    )
    env = os.environ.copy()
    env["PYTHONPATH"] = root
    result = subprocess.run(
        [sys.executable, str(driver)], cwd=root, capture_output=True, text=True, env=env,
    )

    assert result.returncode == 0, result.stderr + result.stdout
    present_text = present.read_text(encoding="utf-8")
    assert "fact:yaml-block-sentinel" not in present_text
    assert "FAIL" in present_text
    assert present_text.endswith(f"Run: {RUN}\n")
    assert missing.read_text(encoding="utf-8") == (
        f"the run failed before a report was written\n\nRun: {RUN}\n"
    )


def test_the_alert_omits_failure_transport_status_source_and_copies() -> None:
    report = _report("fail", [{
        "target": "fact:lab/blocked#context", "outcome": "unreachable",
        "reason": "unreachable:source#table", "source_urls": ["https://example.test/source"],
        "sources": [{
            "source_id": "source", "transport": "http", "declared_fetch": "http",
            "http_status": 403, "error_category": "http_error", "copy_ref": None,
            "cited_copy_ref": "sha256:" + "a" * 64,
        }],
    }])
    report["layers"][0]["counts"] = {
        "verified": 0, "mismatch": 0, "unreachable": 1, "undetermined": 0,
    }

    text = accuracy_alert.body(report, RUN)
    assert "FAIL" in text
    assert "unreachable 1" in text
    assert "fact:lab/blocked#context" not in text
    assert "source `source`" not in text
    assert "sha256:" not in text
    assert "https://example.test/source" not in text


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


def test_the_public_issue_lists_mismatch_and_unreachable_counts_only() -> None:
    report = {
        "snapshot": "snap_da666e1f901c2821",
        "generated_at": "2026-10-06T06:55:39Z",
        "status": "fail",
        "layers": [
            {
                "name": "data_fidelity",
                "status": "fail",
                "gating": True,
                "summary": "Re-read 12 verified values; 1 did not verify.",
                "counts": {"verified": 10, "mismatch": 1, "unreachable": 2, "undetermined": 3},
                "details": {"sample": [
                    {
                        "target": "fact:lab/blocked#context",
                        "outcome": "mismatch",
                        "reason": "value_disagreed",
                        "source_urls": ["https://example.test/source"],
                        "sources": [{
                            "source_id": "source",
                            "transport": "http",
                            "http_status": 403,
                            "error_category": "http_error",
                            "cited_copy_ref": "sha256:" + "a" * 64,
                            "copy_ref": "sha256:" + "b" * 64,
                        }],
                    },
                    {
                        "target": "evidence:lab/model#mmlu#1",
                        "outcome": "unreachable",
                        "reason": "unreachable:source#table",
                        "source_urls": ["https://example.test/other"],
                        "sources": [],
                    },
                ]},
            },
        ],
    }

    text = accuracy_alert.body(report, RUN)

    assert text == (
        "**Overall: FAIL**\n"
        "\n"
        "| Layer | Status | Gate | Summary |\n"
        "| --- | --- | --- | --- |\n"
        "| data_fidelity | FAIL | yes | failures 3; mismatches 1; unreachable 2; undetermined 3. |\n"
        "\n"
        "details are not published; run the nightly profile locally against the private data\n"
        "\n"
        f"Run: {RUN}\n"
    )
    assert "fact:lab/blocked#context" not in text
    assert "evidence:lab/model#mmlu#1" not in text
    assert "sha256:" not in text
    assert "https://example.test/source" not in text
    assert "https://example.test/other" not in text


def test_nightly_fetch_does_not_print_the_private_commit_or_the_report(tmp_path: Path) -> None:
    workflow = yaml.load(
        Path(".github/workflows/accuracy-nightly.yml").read_text(), Loader=yaml.BaseLoader
    )
    steps = workflow["jobs"]["accuracy"]["steps"]
    assert not any(
        (step.get("with") or {}).get("repository") == "turbobeest/modelspec-data"
        for step in steps
    )
    fetch = next(step for step in steps if step.get("name") == "Read private verification records")
    run = fetch["run"]
    assert fetch["if"] == "vars.DATA_SPLIT_ENABLED == 'true'"
    assert fetch["env"]["DATA_TOKEN"] == "${{ secrets.MODELSPEC_DATA_TOKEN }}"
    assert "http.extraheader" in run
    assert "echo" not in run
    assert "set -x" not in run and "xtrace" not in run
    git_lines = [line.strip() for line in run.splitlines() if re.search(r"\bgit\b", line)]
    assert git_lines
    for line in git_lines:
        assert ">/dev/null" in line and "2>&1" in line
        assert re.search(r"\b(log|rev-parse)\b", line) is None
    assert "--depth=1" in run or "--depth 1" in run
    assert "refs/heads/main" in run
    for step in steps:
        uses = step.get("uses") or ""
        assert "upload-artifact" not in uses
        assert "upload-pages-artifact" not in uses
        script = step.get("run") or ""
        assert "set -x" not in script and "xtrace" not in script
        assert "GITHUB_STEP_SUMMARY" not in script
        for line in script.splitlines():
            prints = re.search(r"\b(cat|jq|echo|printf)\b", line)
            names_report = re.search(r"accuracy\.(json|md)", line)
            if prints and names_report:
                pytest.fail(line)

    bindir = tmp_path / "bin"
    bindir.mkdir()
    recorded = tmp_path / "git-args"
    git = bindir / "git"
    git.write_text(
        "#!/bin/sh\n"
        f"printf '%s\\n' \"$*\" >> {recorded}\n"
        "cmd=$1\n"
        "if [ \"$cmd\" = \"-C\" ]; then shift 2; cmd=$1; fi\n"
        "while [ \"$cmd\" = \"-c\" ]; do shift 2; cmd=$1; done\n"
        "if [ \"$cmd\" = fetch ]; then exit \"${FETCH_STATUS:-0}\"; fi\n"
        "exit 0\n"
    )
    git.chmod(0o755)
    token = "secret-token-sentinel"
    result = subprocess.run(
        ["bash", "-c", run], cwd=tmp_path, capture_output=True, text=True,
        env=os.environ | {
            "PATH": f"{bindir}:{os.environ.get('PATH', '')}",
            "DATA_TOKEN": token,
            "FETCH_STATUS": "0",
            "GIT_TERMINAL_PROMPT": "0",
        },
    )
    assert result.returncode == 0, result.stderr
    assert result.stdout == ""
    assert result.stderr == ""
    assert token not in result.stdout + result.stderr
    log = recorded.read_text()
    assert token not in log
    assert "\nfetch " in f"\n{log}" or log.startswith("fetch ") or " fetch " in log
    assert re.search(r"(^|\s)(log|rev-parse)(\s|$)", log) is None

    failed = subprocess.run(
        ["bash", "-c", run], cwd=tmp_path, capture_output=True, text=True,
        env=os.environ | {
            "PATH": f"{bindir}:{os.environ.get('PATH', '')}",
            "DATA_TOKEN": token,
            "FETCH_STATUS": "7",
            "GIT_TERMINAL_PROMPT": "0",
        },
    )
    assert failed.returncode == 7
    assert failed.stdout == ""
    assert token not in failed.stderr
