"""MODEL-481: a red price re-read reaches a person, and its report fits."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import date
from pathlib import Path

import pytest
import yaml

from scripts import price_reread
from scripts.price_reread import FactResult, Status

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "private-writers" / "price-reread.yml"
TODAY = date(2026, 10, 6)
PYTHON = sys.executable
RUN_URL = "https://github.com/example/repo/actions/runs/481"
TITLE = "Price and plan re-read needs a person"


def _workflow() -> dict:
    return yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))


def _reread_steps() -> list[dict]:
    return _workflow()["jobs"]["reread"]["steps"]


def _step(name: str) -> dict:
    return next(step for step in _reread_steps() if step.get("name") == name)


def _fact(fact_id: str, source_ids: tuple[str, ...], status: Status, reason: str) -> FactResult:
    return FactResult(
        fact_id, "offering.subscription.price", "offerings/example.yaml", source_ids,
        status, "known", 1, reason=reason,
    )


def _comment_report() -> dict:
    facts = [
        _fact(f"zz-{index}", ("source-zz",), Status.UNREADABLE, "shell")
        for index in range(3)
    ]
    facts += [
        _fact(f"aa-{index}", ("source-aa",), Status.NEEDS_REVIEW, "review")
        for index in range(2)
    ]
    facts += [
        _fact(f"n-{index}", (f"source-{index:02d}",), Status.UNREACHABLE, "HTTP 503")
        for index in range(39)
    ]
    return price_reread.Report(TODAY, facts=facts).to_dict()


def test_alert_comment_counts_sources_without_cutting_a_row() -> None:
    text = price_reread.alert_comment(_comment_report(), RUN_URL)
    assert text.startswith(f"Run: {RUN_URL}\n")
    assert "| unchanged |" in text.splitlines()[2]
    rows = [line for line in text.splitlines() if line.startswith("| `source-")]
    assert rows[0] == "| `source-zz` | unreadable | 3 |"
    assert rows[1] == "| `source-aa` | needs_review | 2 |"
    assert len(rows) == 40
    assert all(line.count("|") == 4 for line in rows)
    assert "| `source-38` |" not in text
    assert "1 source row was left out" in text
    assert "price-reread-report" in text
    assert "head -c" not in text

    both = price_reread.Report(TODAY, facts=[
        _fact("both", ("left-source", "right-source"), Status.UNREADABLE, "shell"),
    ]).to_dict()
    counted = price_reread.alert_comment(both, RUN_URL)
    lines = counted.splitlines()
    note = "1 alert fact; a fact with several sources is counted under each."
    assert "| Source | Status | Fact-source pairs |" in lines
    assert note in lines
    assert lines.index(note) < lines.index("| Source | Status | Fact-source pairs |")
    assert "| `left-source` | unreadable | 1 |" in counted
    assert "| `right-source` | unreadable | 1 |" in counted


def _long_reason() -> str:
    tail = " (example-plans has 41823 characters of text)"
    return "cited region not found. " + ("m" * 200) + " UNIQUE-MIDDLE-TOKEN " + ("m" * 200) + tail


def test_json_keeps_the_whole_reason_and_markdown_keeps_the_trailing_count() -> None:
    reason = _long_reason()
    assert len(reason) > 120
    fact = _fact("example/fact", ("example-plans",), Status.UNREADABLE, reason)
    report = price_reread.Report(TODAY, facts=[fact])
    assert report.to_dict()["alerts"][0]["reason"] == reason
    body = price_reread.render_report(report)
    row = next(line for line in body.splitlines() if "`example/fact`" in line)
    why = row.split("|")[3].strip()
    assert why != reason
    assert len(why) <= 120
    assert "41823 characters of text" in why
    assert "UNIQUE-MIDDLE-TOKEN" not in why
    assert "…" in why and not why.endswith("…")
    assert why.startswith("cited region not found.")


def _markdown(*, alerts: int, diff: str, changes: int = 0) -> str:
    alert_rows = "\n".join(
        f"| `alert-{index}` | unreadable | a reason that is complete |"
        for index in range(alerts)
    )
    change_rows = "\n".join(
        f"| `change-{index}` | 1 | 2 | example-plans (`sha256:abc`) |"
        for index in range(changes)
    )
    parts = [
        "## Price and plan re-read, 2026-10-06",
        "",
        "| unchanged | unreadable |",
        "|---|---|",
        f"| 1 | {alerts} |",
        "",
        "Each unchanged value was verified again.",
        "",
    ]
    if changes:
        parts += [
            "### Changed values",
            "",
            "A person reviews every change here before it merges; none auto-merges.",
            "",
            "| Fact | Old | New | Source |",
            "|---|---|---|---|",
            change_rows,
            "",
        ]
    parts += [
        "### Needs a person",
        "",
        "The readers could not re-read these, so nothing was written for them.",
        "",
        "| Fact | Status | Why |",
        "|---|---|---|",
        alert_rows,
        "",
        "### Source diffs",
        "",
        "`example-plans` https://example.invalid/plans",
        "",
        "```diff",
        diff,
        "```",
        "",
    ]
    return "\n".join(parts)


def test_pull_request_body_under_the_limit_is_unchanged() -> None:
    body = "The weekly re-read found values.\n\n" + _markdown(alerts=1, diff="+ok")
    assert price_reread.fit_pull_request_body(body) == body


def test_pull_request_body_keeps_a_complete_table_or_leaves_it_out() -> None:
    body = _markdown(alerts=2, diff="+" + ("y" * 5000), changes=2)
    fitted = price_reread.fit_pull_request_body(body, limit=len(body) - 100)
    assert len(fitted) <= len(body) - 100
    assert "| `change-0` | 1 | 2 | example-plans (`sha256:abc`) |" in fitted
    assert "| `change-1` | 1 | 2 | example-plans (`sha256:abc`) |" in fitted
    assert "| `alert-0` | unreadable | a reason that is complete |" in fitted
    assert "| `alert-1` | unreadable | a reason that is complete |" in fitted
    assert "y" * 5000 not in fitted
    assert "Source diffs were left out" in fitted
    assert "price-reread-report" in fitted
    original_rows = [line for line in body.splitlines() if line.startswith("| `")]
    for line in fitted.splitlines():
        if not line.startswith("| `"):
            continue
        assert line in original_rows

    huge = _markdown(alerts=30, diff="+" + ("z" * 400))
    header, _, _ = huge.partition("### Needs a person")
    capped = price_reread.fit_pull_request_body(huge, limit=len(header) + 220)
    assert len(capped) <= len(header) + 220
    assert "| unchanged | unreadable |" in capped
    assert "alert-0" not in capped
    assert "30 alert rows were left out" in capped
    assert "Source diffs were left out" in capped
    assert "price-reread-report" in capped
    assert "z" * 400 not in capped


def test_the_reread_job_uploads_the_report_and_can_label_issues() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")
    job = _workflow()["jobs"]["reread"]
    assert job["permissions"] == {
        "contents": "write",
        "pull-requests": "write",
        "issues": "write",
        "actions": "read",
    }
    upload = next(
        step for step in job["steps"]
        if (step.get("with") or {}).get("name") == "price-reread-report"
    )
    assert upload["if"] == "always()"
    assert str(upload["uses"]).startswith("actions/upload-artifact@")
    uploaded = upload["with"]["path"]
    assert "report.md" in uploaded and "report.json" in uploaded
    names = [step.get("name") for step in job["steps"]]
    assert names.index("Re-read every page once") < names.index(upload["name"])
    assert "head -c" not in text
    prepare = _step("Prepare the pull-request body")
    assert "fit_pull_request_body" in prepare["run"]
    reconfirm = _step("Open the reconfirmation pull request")
    assert reconfirm["with"]["body-path"] == "${{ runner.temp }}/reconfirm-body.md"
    assert "fit_pull_request_body" in _step("Fit the reconfirmation pull-request body")["run"]
    fail = _step("Fail a run with alerts")
    assert fail["if"] == "steps.result.outputs.alerts != '0'"
    assert "exit 1" in fail["run"]
    rendered = (ROOT / ".github" / "private-writers" / "rendered-reread.yml").read_text(
        encoding="utf-8")
    assert "rendered-reread-report" not in rendered


def _gh_stub(mode: str) -> str:
    return f"""\
python() {{
  if [ "{mode}" = builder ]; then
    echo 'ImportError: cannot import name alert_comment' >&2
    return 1
  fi
  if [ "$1" = "-I" ]; then
    shift
  fi
  command "{PYTHON}" "$@"
}}
gh() {{
  "{PYTHON}" -c 'import json,sys; print(json.dumps(sys.argv[1:]))' "$@" >> "$RUNNER_TEMP/gh-calls"
  if [ "$1" = label ] && [ "$2" = create ]; then
    if [ "{mode}" = exists ]; then
      echo 'label with name "alert" already exists' >&2
      return 1
    fi
    if [ "{mode}" = rate ]; then
      echo 'HTTP 403 rate limit' >&2
      return 1
    fi
    return 0
  fi
  if [ "$1" = issue ] && [ "$2" = list ]; then
    if [ -n "${{EXISTING_ISSUE:-}}" ]; then
      printf '%s\\n' "$EXISTING_ISSUE"
    fi
    return 0
  fi
  if [ "$1" = issue ] && [ "$2" = edit ] && [ "{mode}" = closed ]; then
    echo 'issue is closed' >&2
    return 1
  fi
  return 0
}}
"""


def _run_alert(tmp_path: Path, *, existing: str, mode: str) -> subprocess.CompletedProcess[str]:
    payload = {
        "counts": {"unchanged": 1, "unreadable": 2, "unreachable": 1},
        "alerts": [
            {"sources": ["source-a"], "status": "unreadable"},
            {"sources": ["source-a"], "status": "unreadable"},
            {"sources": ["source-b"], "status": "unreachable"},
        ],
    }
    (tmp_path / "report.json").write_text(json.dumps(payload), encoding="utf-8")
    (tmp_path / "gh-calls").write_text("", encoding="utf-8")
    step = _step("Open or update the alert issue")
    env = {
        **os.environ,
        "PYTHONPATH": str(ROOT),
        "RUNNER_TEMP": str(tmp_path),
        "REPO": "example/repo",
        "TITLE": TITLE,
        "RUN_URL": RUN_URL,
        "GH_TOKEN": "fixture",
        "EXISTING_ISSUE": existing,
    }
    return subprocess.run(
        ["bash", "-c", _gh_stub(mode) + step["run"]],
        cwd=tmp_path, capture_output=True, text=True, env=env, check=False,
    )


def _calls(tmp_path: Path) -> list[list[str]]:
    lines = (tmp_path / "gh-calls").read_text(encoding="utf-8").splitlines()
    return [json.loads(line) for line in lines if line]


def _run_step(name: str, tmp_path: Path, mode: str) -> subprocess.CompletedProcess[str]:
    (tmp_path / "gh-calls").write_text("", encoding="utf-8")
    step = _step(name)
    env = {
        **os.environ,
        "PYTHONPATH": str(ROOT),
        "RUNNER_TEMP": str(tmp_path),
        "REPO": "example/repo",
        "TITLE": TITLE,
        "RUN_URL": RUN_URL,
        "GH_TOKEN": "fixture",
        "EXISTING_ISSUE": "",
    }
    return subprocess.run(
        ["bash", "-c", _gh_stub(mode) + step["run"]],
        cwd=tmp_path, capture_output=True, text=True, env=env, check=False,
    )


@pytest.mark.parametrize("existing", ["", "17"])
def test_alert_issue_step_labels_create_and_an_existing_issue(tmp_path: Path, existing: str) -> None:
    result = _run_alert(tmp_path, existing=existing, mode="ok")
    assert result.returncode == 0, result.stderr
    body = (tmp_path / "issue-body.md").read_text(encoding="utf-8")
    assert body == price_reread.alert_comment(
        json.loads((tmp_path / "report.json").read_text(encoding="utf-8")), RUN_URL,
    )
    assert "| `source-a` | unreadable | 2 |" in body
    assert "| `source-b` | unreachable | 1 |" in body
    assert "head -c" not in body
    calls = _calls(tmp_path)
    assert ["label", "create", "alert"] == [call[:3] for call in calls if call[:2] == ["label", "create"]][0][:3]
    if existing:
        comment = next(call for call in calls if call[:2] == ["issue", "comment"])
        edit = next(call for call in calls if call[:2] == ["issue", "edit"])
        assert comment[2] == existing
        assert edit[2] == existing
        assert edit[edit.index("--add-label") + 1] == "alert"
        assert not any(call[:2] == ["issue", "create"] for call in calls)
    else:
        create = next(call for call in calls if call[:2] == ["issue", "create"])
        assert create[create.index("--label") + 1] == "alert"
        assert not any(call[:2] == ["issue", "edit"] for call in calls)


def test_a_label_failure_warns_and_leaves_the_alert_step_green(tmp_path: Path) -> None:
    result = _run_alert(tmp_path, existing="", mode="rate")
    assert result.returncode == 0, result.stderr
    assert "::warning::" in result.stdout
    calls = _calls(tmp_path)
    assert any(call[:2] == ["issue", "create"] for call in calls)
    exists = _run_alert(tmp_path, existing="17", mode="exists")
    assert exists.returncode == 0, exists.stderr
    assert "::warning::" not in exists.stdout
    closed = _run_alert(tmp_path, existing="17", mode="closed")
    assert closed.returncode == 0, closed.stderr
    assert "::warning::" in closed.stdout
    assert any(call[:2] == ["issue", "comment"] for call in _calls(tmp_path))


def test_workflow_pins_the_builder_fallback() -> None:
    alert = _step("Open or update the alert issue")["run"]
    assert "the alert summary could not be built" in alert
    assert "price-reread-report" in alert
    assert "::warning::" in alert
    for name in ("Prepare the pull-request body", "Fit the reconfirmation pull-request body"):
        step = _step(name)
        assert "::warning::" in step["run"]
        assert "price-reread-report" in step["run"]
        assert "RUN_URL" in step["run"]
        assert step["env"]["RUN_URL"]


def test_alert_survives_a_builder_import_error(tmp_path: Path) -> None:
    (tmp_path / "report.json").write_text("{}", encoding="utf-8")
    result = _run_step("Open or update the alert issue", tmp_path, "builder")
    assert result.returncode == 0, result.stderr
    text = (tmp_path / "issue-body.md").read_text(encoding="utf-8")
    assert f"Run: {RUN_URL}" in text
    assert "the alert summary could not be built" in text
    assert "price-reread-report" in text
    assert "ImportError: cannot import name alert_comment" in result.stdout
    assert any(call[:2] == ["issue", "create"] for call in _calls(tmp_path))


def test_alert_survives_a_report_without_counts(tmp_path: Path) -> None:
    (tmp_path / "report.json").write_text(
        json.dumps({"alerts": [{"sources": ["source-a"], "status": "unreadable"}]}),
        encoding="utf-8",
    )
    result = _run_step("Open or update the alert issue", tmp_path, "ok")
    assert result.returncode == 0, result.stderr
    text = (tmp_path / "issue-body.md").read_text(encoding="utf-8")
    assert f"Run: {RUN_URL}" in text
    assert "the alert summary could not be built" in text
    assert "price-reread-report" in text
    assert "KeyError" in result.stdout
    assert any(call[:2] == ["issue", "create"] for call in _calls(tmp_path))


@pytest.mark.parametrize("name,body_name", [
    ("Prepare the pull-request body", "pr-body.md"),
    ("Fit the reconfirmation pull-request body", "reconfirm-body.md"),
])
def test_pull_request_bodies_survive_a_fitter_error(
    tmp_path: Path, name: str, body_name: str,
) -> None:
    result = _run_step(name, tmp_path, "ok")
    assert result.returncode == 0, result.stderr
    text = (tmp_path / body_name).read_text(encoding="utf-8")
    assert f"Run: {RUN_URL}" in text
    assert "price-reread-report" in text
    assert "::warning::" in result.stdout
    assert "FileNotFoundError" in result.stdout
