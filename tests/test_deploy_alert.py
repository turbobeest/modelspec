"""MODEL-487: a red production deploy on main opens one public `alert` issue."""

from __future__ import annotations

import os
import re
import stat
import subprocess
from pathlib import Path

import pytest
import yaml

from scripts import deploy_alert
from scripts.deploy_alert import (
    JOB_NAME,
    TITLE,
    body,
    failure_class,
    fetch_annotations,
)
from scripts.deploy_retry import failure_line

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/rank-api.yml"
SHA = "0123456789abcdef0123456789abcdef01234567"
URL = "https://github.com/turbobeest/modelspec/actions/runs/123456789"


def _workflow() -> dict:
    return yaml.load(WORKFLOW.read_text(encoding="utf-8"), Loader=yaml.BaseLoader)


def _ann(message: str) -> dict:
    return {"annotation_level": "failure", "message": message, "title": None}


# ── the class ───────────────────────────────────────────────────────────────

@pytest.mark.parametrize("name", ("transient-exhausted", "rejected", "unknown"))
def test_a_known_class_is_read_from_the_annotation(name: str) -> None:
    annotations = [_ann("Process completed with exit code 1."), _ann(failure_line(name)[len("::error::"):])]
    assert failure_class(annotations) == name


@pytest.mark.parametrize(
    "annotations",
    (
        [],
        [_ann("Process completed with exit code 1.")],
        [_ann("deploy-failure-class=something-else")],
        [_ann("deploy-failure-class=rejected"), _ann("deploy-failure-class=unknown")],
        [_ann("see /accounts/abc123 for deploy-failure-class=rejected")],
        [{"message": None}, {"no": "message"}, {"message": 7}],
    ),
)
def test_anything_else_is_unknown(annotations: list) -> None:
    assert failure_class(annotations) == "unknown"


# ── the body ────────────────────────────────────────────────────────────────

def test_the_body_holds_only_the_four_public_fields() -> None:
    assert body("Rank API", URL, SHA, "transient-exhausted") == (
        "Workflow: Rank API\n"
        f"Run: {URL}\n"
        f"Commit: {SHA}\n"
        "Failure class: transient-exhausted\n"
    )


def test_a_class_outside_the_list_is_written_as_unknown() -> None:
    assert body("Rank API", URL, SHA, "token abc").endswith("Failure class: unknown\n")


@pytest.mark.parametrize(
    "workflow,run_url,commit",
    (
        ("Rank API\nsecret", URL, SHA),
        ("", URL, SHA),
        ("Rank API", "https://example.com/a/b/actions/runs/1", SHA),
        ("Rank API", URL + "?x=y", SHA),
        ("Rank API", URL, SHA[:7]),
        ("Rank API", URL, SHA.upper()),
    ),
)
def test_a_field_that_is_not_what_it_should_be_is_refused(workflow, run_url, commit) -> None:
    with pytest.raises(ValueError):
        body(workflow, run_url, commit, "unknown")


# ── reading the annotations ─────────────────────────────────────────────────

def test_the_annotations_come_from_the_one_failed_deploy_job() -> None:
    asked: list[str] = []

    def gh_api(path: str):
        asked.append(path)
        if "/jobs" in path:
            return {"jobs": [
                {"id": 1, "name": "Rank Worker bundle", "conclusion": "success"},
                {"id": 2, "name": JOB_NAME, "conclusion": "failure"},
            ]}
        return [_ann("deploy-failure-class=rejected")]

    result = fetch_annotations("turbobeest/modelspec", "42", gh_api=gh_api)
    assert failure_class(result) == "rejected"
    assert asked == [
        "repos/turbobeest/modelspec/actions/runs/42/jobs?per_page=100",
        "repos/turbobeest/modelspec/check-runs/2/annotations?per_page=100",
    ]


@pytest.mark.parametrize(
    "jobs",
    (
        {"jobs": []},
        {"jobs": [{"id": 2, "name": JOB_NAME, "conclusion": "success"}]},
        {"jobs": [{"id": 2, "name": JOB_NAME, "conclusion": "failure"},
                  {"id": 3, "name": JOB_NAME, "conclusion": "failure"}]},
        {"jobs": [{"id": "2", "name": JOB_NAME, "conclusion": "failure"}]},
        {},
    ),
)
def test_no_single_failed_deploy_job_means_no_annotations(jobs) -> None:
    def gh_api(path: str):
        if "/jobs" in path:
            return jobs
        raise AssertionError("annotations asked for")

    assert fetch_annotations("turbobeest/modelspec", "42", gh_api=gh_api) == []


@pytest.mark.parametrize("error", (subprocess.CalledProcessError(1, "gh"), OSError("x"), ValueError("x")))
def test_a_failed_api_read_is_not_a_failed_alert(error) -> None:
    def gh_api(path: str):
        raise error

    assert fetch_annotations("turbobeest/modelspec", "42", gh_api=gh_api) == []


@pytest.mark.parametrize("repo,run_id", (("a b/c", "1"), ("a/b/c", "1"), ("a/b", "1; rm"), ("a/b", "")))
def test_a_repository_or_run_id_that_is_not_plain_is_never_sent(repo: str, run_id: str) -> None:
    def gh_api(path: str):
        raise AssertionError("must not call")

    assert fetch_annotations(repo, run_id, gh_api=gh_api) == []


def test_main_writes_the_body_for_an_unreadable_class(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(deploy_alert, "_gh_api", lambda path: (_ for _ in ()).throw(OSError("no gh")))
    out = tmp_path / "alert.md"
    assert deploy_alert.main([
        "--workflow", "Rank API", "--run-url", URL, "--commit", SHA,
        "--repo", "turbobeest/modelspec", "--run-id", "123456789", "--output", str(out),
    ]) == 0
    assert out.read_text() == (
        f"Workflow: Rank API\nRun: {URL}\nCommit: {SHA}\nFailure class: unknown\n"
    )


# ── the workflow ────────────────────────────────────────────────────────────

def test_the_deploy_step_runs_the_wrapper_around_the_unchanged_command() -> None:
    steps = _workflow()["jobs"]["deploy"]["steps"]
    deploy = [s for s in steps if s.get("name") == "Deploy"]
    assert len(deploy) == 1
    assert deploy[0]["working-directory"] == "api/worker"
    assert deploy[0]["run"].strip() == (
        'python3 "$GITHUB_WORKSPACE/scripts/deploy_retry.py" -- '
        'uv run --project . pywrangler deploy --var "BUILD_COMMIT:${GITHUB_SHA}"'
    )
    assert set(deploy[0]) == {"name", "working-directory", "run"}


def test_the_staging_deploy_is_unchanged() -> None:
    steps = _workflow()["jobs"]["deploy-staging"]["steps"]
    staging = next(s for s in steps if s.get("name") == "Deploy staging")
    assert staging["run"].strip() == (
        'uv run --project . pywrangler deploy --env staging --var "BUILD_COMMIT:${GITHUB_SHA}"'
    )


def _alert_job() -> dict:
    return _workflow()["jobs"]["deploy-alert"]


def test_the_alert_job_has_issues_write_and_nothing_else() -> None:
    job = _alert_job()
    assert job["permissions"] == {"issues": "write"}
    assert "environment" not in job
    assert "outputs" not in job
    assert "env" not in job


def test_the_alert_job_needs_only_the_deploy_result_and_names_no_private_value() -> None:
    job = _alert_job()
    assert job["needs"] == "deploy"
    text = yaml.safe_dump(job)
    assert not re.search(r"needs\.deploy\.(?!result\b)", text)
    assert "needs." not in re.sub(r"needs\.deploy\.result", "", text)
    assert "toJSON" not in text and "secrets" not in text
    assert "MODELSPEC_DATA" not in text.upper() and "modelspec-data" not in text
    assert "download" not in text.lower()
    tokens = re.findall(r"\$\{\{\s*([^}]*?)\s*\}\}", text)
    assert "github.token" in tokens
    assert all(
        t.startswith(("github.", "needs.deploy.result")) for t in tokens
    ), tokens


def test_the_alert_job_runs_after_a_red_deploy_on_main_only() -> None:
    job = _alert_job()
    assert job["if"] == (
        "always() && github.ref == 'refs/heads/main' && "
        "(needs.deploy.result == 'failure' || needs.deploy.result == 'success')"
    )


def _step(name_start: str) -> dict:
    return next(s for s in _alert_job()["steps"] if s.get("name", "").startswith(name_start))


def _fake_gh(tmp_path: Path, listed: str) -> Path:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    gh = bin_dir / "gh"
    gh.write_text(
        "#!/bin/sh\n"
        'printf "%s\\n" "$*" >> "$GH_LOG"\n'
        'if [ "$1 $2" = "issue list" ] && [ -n "$GH_LISTED" ]; then printf "%s\\n" "$GH_LISTED"; fi\n'
    )
    gh.chmod(gh.stat().st_mode | stat.S_IEXEC)
    return bin_dir


def _run_step(step: dict, tmp_path: Path, listed: str) -> list[str]:
    bin_dir = _fake_gh(tmp_path, listed)
    (tmp_path / "scripts").mkdir()
    for name in ("deploy_alert.py", "deploy_retry.py"):
        (tmp_path / "scripts" / name).write_text((ROOT / "scripts" / name).read_text())
    log = tmp_path / "gh.log"
    env = {
        "PATH": f"{bin_dir}{os.pathsep}{os.environ['PATH']}",
        "GH_LOG": str(log),
        "GH_LISTED": listed,
        "GH_REPO": "turbobeest/modelspec",
        "RUN_ID": "123456789",
        "RUN_URL": URL,
        "COMMIT": SHA,
        "WORKFLOW": "Rank API",
        "RUNNER_TEMP": str(tmp_path),
        "HOME": str(tmp_path),
    }
    done = subprocess.run(
        ["bash", "-e", "-c", step["run"]], cwd=tmp_path, env=env,
        capture_output=True, text=True, check=False,
    )
    assert done.returncode == 0, done.stderr
    return log.read_text().splitlines() if log.exists() else []


def test_a_red_deploy_creates_one_alert_issue_with_the_fixed_title(tmp_path: Path) -> None:
    step = _step("Open or update")
    assert step["if"] == "needs.deploy.result == 'failure'"
    calls = _run_step(step, tmp_path, listed="")
    assert any(c.startswith("label create alert") for c in calls)
    creates = [c for c in calls if c.startswith("issue create")]
    assert len(creates) == 1
    assert f'--title {TITLE} --label alert' in creates[0].replace('"', "")
    assert not any(c.startswith("issue comment") for c in calls)
    assert (tmp_path / "alert.md").read_text().splitlines() == [
        "Workflow: Rank API", f"Run: {URL}", f"Commit: {SHA}", "Failure class: unknown",
    ]


def test_a_second_red_deploy_updates_the_open_issue(tmp_path: Path) -> None:
    calls = _run_step(_step("Open or update"), tmp_path, listed="77")
    assert [c for c in calls if c.startswith("issue comment")] == ["issue comment 77 --body-file alert.md"]
    assert not any(c.startswith("issue create") for c in calls)


def test_the_listing_matches_the_exact_title_so_the_nightly_alert_is_left_alone() -> None:
    run = _step("Open or update")["run"]
    assert f'select(.title == "{TITLE}")' in run
    assert "Accuracy nightly failed" not in run


def test_a_green_deploy_closes_the_open_alert(tmp_path: Path) -> None:
    step = _step("Close the alert")
    assert step["if"] == "needs.deploy.result == 'success'"
    calls = _run_step(step, tmp_path, listed="77\n78")
    closes = [c for c in calls if c.startswith("issue close")]
    assert [c.split()[2] for c in closes] == ["77", "78"]
    assert all(f"Green again: {URL}" in c for c in closes)


def test_a_green_deploy_with_nothing_open_closes_nothing(tmp_path: Path) -> None:
    calls = _run_step(_step("Close the alert"), tmp_path, listed="")
    assert not any(c.startswith("issue close") for c in calls)
