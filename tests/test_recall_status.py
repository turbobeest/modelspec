"""MODEL-476: a dispatched recall run reports its result as a commit status.

GitHub does not count the check run of a `workflow_dispatch` run in a pull request's
checks; a commit status posted through the REST API does count. `recall-private.yml`
therefore gets two small jobs that run only for `workflow_dispatch`, are the only ones
holding `statuses: write`, and post the truth about the recall job. The recall job runs
code from the branch under test and keeps its permissions (it holds no write permission).
"""

from __future__ import annotations

import os
import stat
import subprocess
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
RECALL_PATH = ROOT / ".github" / "private-writers" / "recall-private.yml"
CONTEXT = "Approved answers on private data"
PENDING = "status-pending"
FINAL = "status-final"
STATUS_JOBS = (PENDING, FINAL)
DISPATCH_ONLY = "github.event_name == 'workflow_dispatch'"

# The recall job's step names, in order, as they were before this change.
RECALL_STEPS = [
    "Check out private data",
    "Verify the engine pin is on modelspec main",
    "Refuse an engine pin older than the base branch pin",
    "Check out the pinned public engine",
    "Confirm the engine checkout is the verified pin",
    "Set up Python",
    "Refuse code and symlinks in linked data paths",
    "Compose engine code with private data",
    "Install engine dependencies",
    "Check public writer mirrors",
    "Run broader data tests",
    "Load the private merge-base baseline",
    "Score the approved answers on private data",
    "Compare private baselines and summarise aggregate verdicts",
]


def _document() -> dict:
    loaded = yaml.safe_load(RECALL_PATH.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded


def _jobs() -> dict:
    return _document()["jobs"]


def _walk(value):
    if isinstance(value, dict):
        for key, item in value.items():
            yield key
            yield from _walk(item)
    elif isinstance(value, list):
        for item in value:
            yield from _walk(item)
    else:
        yield value


def _script(job: str) -> str:
    steps = _jobs()[job]["steps"]
    assert len(steps) == 1, f"{job}: exactly one step"
    return steps[0]["run"]


def test_the_recall_workflow_has_exactly_the_recall_job_and_two_status_jobs() -> None:
    assert set(_jobs()) == {"recall", *STATUS_JOBS}


def test_the_recall_job_keeps_its_permissions_and_its_steps() -> None:
    document = _document()
    recall = document["jobs"]["recall"]
    # No job-level block: the job inherits the workflow's read-only block.
    assert "permissions" not in recall
    assert document["permissions"] == {"contents": "read"}
    assert recall["name"] == CONTEXT
    assert [step["name"] for step in recall["steps"]] == RECALL_STEPS
    assert "needs" not in recall
    assert "if" not in recall


def test_only_the_status_jobs_hold_statuses_write_and_nothing_else() -> None:
    document = _document()
    assert "statuses" not in document["permissions"]
    for name, job in document["jobs"].items():
        if name in STATUS_JOBS:
            assert job["permissions"] == {"statuses": "write"}, name
        else:
            assert "statuses" not in (job.get("permissions") or {}), name
    text = RECALL_PATH.read_text(encoding="utf-8")
    assert text.count("statuses: write") == len(STATUS_JOBS)
    assert "write" not in {
        value for value in _walk(document["permissions"]) if isinstance(value, str)
    }


def test_no_job_that_runs_branch_code_holds_any_write_permission() -> None:
    recall = _jobs()["recall"]
    assert "write" not in str(recall.get("permissions", {}))
    assert "write" not in str(_document()["permissions"])
    assert any(str(s.get("uses", "")).startswith("actions/checkout") for s in recall["steps"])
    for job in STATUS_JOBS:
        assert not any(
            str(s.get("uses", "")).startswith("actions/checkout") for s in _jobs()[job]["steps"]
        )


@pytest.mark.parametrize("job", STATUS_JOBS)
def test_a_status_job_has_no_checkout_no_uses_no_secret_and_no_expression_in_run(job: str) -> None:
    body = _jobs()[job]
    assert len(body["steps"]) == 1
    step = body["steps"][0]
    assert "uses" not in step and "working-directory" not in step
    assert "${{" not in step["run"]
    assert "secrets." not in yaml.safe_dump(body)
    assert "defaults" not in body
    assert body["timeout-minutes"] <= 5
    assert body["runs-on"] == "ubuntu-latest"
    assert "continue-on-error" not in body  # a failed post must turn the job red


@pytest.mark.parametrize("job", STATUS_JOBS)
def test_a_status_job_takes_only_the_fixed_inputs_through_env(job: str) -> None:
    env = _jobs()[job]["steps"][0]["env"]
    expected = {
        "GH_TOKEN": "${{ github.token }}",
        "SHA": "${{ github.sha }}",
        "REPO": "${{ github.repository }}",
        "RUN_ID": "${{ github.run_id }}",
        "CONTEXT": CONTEXT,
    }
    if job == FINAL:
        expected["RECALL_RESULT"] = "${{ needs.recall.result }}"
    assert env == expected


def test_the_status_jobs_run_only_for_workflow_dispatch_and_the_final_one_always() -> None:
    pending, final = _jobs()[PENDING], _jobs()[FINAL]
    assert pending["if"] == DISPATCH_ONLY
    assert final["if"] == f"always() && {DISPATCH_ONLY}"
    assert "needs" not in pending
    assert sorted(final["needs"]) == ["recall", PENDING]
    assert "if" not in _jobs()["recall"]


def test_the_triggers_are_unchanged() -> None:
    document = _document()
    triggers = document.get("on") or document.get(True)
    assert set(triggers) == {"pull_request", "schedule", "workflow_dispatch"}
    assert triggers["workflow_dispatch"] is None


def _evaluate(expression: str, event: str) -> bool:
    """Evaluate the only expression shapes used in `if:` for a given event name."""
    always = "always()"
    expression = expression.replace(always, "True")
    expression = expression.replace("github.event_name == 'workflow_dispatch'", repr(event == "workflow_dispatch"))
    expression = expression.replace("&&", " and ")
    return bool(eval(expression, {"__builtins__": {}}))  # noqa: S307 - fixed test input only


@pytest.mark.parametrize("event", ["pull_request", "schedule"])
def test_the_status_jobs_do_not_run_on_pull_request_or_schedule(event: str) -> None:
    for job in STATUS_JOBS:
        assert _evaluate(_jobs()[job]["if"], event) is False


def test_the_status_jobs_run_on_workflow_dispatch() -> None:
    for job in STATUS_JOBS:
        assert _evaluate(_jobs()[job]["if"], "workflow_dispatch") is True


def _gh(tmp_path: Path, *, fail: bool) -> tuple[dict[str, str], Path]:
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    log = tmp_path / "gh.log"
    log.touch()
    gh = bin_dir / "gh"
    gh.write_text(
        "#!/usr/bin/env bash\n"
        'printf "%s\\n" "$*" >> "$GH_LOG"\n'
        'if [ -n "${FAIL_API:-}" ]; then echo "HTTP 403" >&2; exit 1; fi\n'
        "exit 0\n",
        encoding="utf-8",
    )
    gh.chmod(gh.stat().st_mode | stat.S_IXUSR)
    env = {
        "PATH": f"{bin_dir}{os.pathsep}{os.environ['PATH']}",
        "GH_LOG": str(log),
        "GH_TOKEN": "test-token",
        "GITHUB_SERVER_URL": "https://github.com",
        "SHA": "0123456789abcdef0123456789abcdef01234567",
        "REPO": "owner/data",
        "RUN_ID": "4242",
        "CONTEXT": CONTEXT,
    }
    if fail:
        env["FAIL_API"] = "1"
    return env, log


def _post(tmp_path: Path, job: str, result: str | None = None, *, fail: bool = False):
    env, log = _gh(tmp_path, fail=fail)
    if result is not None:
        env["RECALL_RESULT"] = result
    done = subprocess.run(
        ["bash", "-c", _script(job)], env=env, cwd=tmp_path, capture_output=True, text=True, check=False,
    )
    return done, log.read_text(encoding="utf-8").splitlines()


def _fields(call: str) -> dict[str, str]:
    # The stub logs the argument list joined with spaces; fields are `key=value` tokens.
    parts = call.split(" -f ")
    fields = {}
    for part in parts[1:]:
        key, _, value = part.partition("=")
        fields[key] = value.strip()
    return fields


def test_the_pending_job_posts_pending_on_the_head_sha_with_the_check_name(tmp_path: Path) -> None:
    done, calls = _post(tmp_path, PENDING)
    assert done.returncode == 0, done.stderr
    assert len(calls) == 1
    assert calls[0].startswith("api --method POST repos/owner/data/statuses/0123456789abcdef0123456789abcdef01234567")
    fields = _fields(calls[0])
    assert fields["state"] == "pending"
    assert fields["context"] == CONTEXT
    assert fields["target_url"] == "https://github.com/owner/data/actions/runs/4242"
    assert "writer" in fields["description"]
    assert len(fields["description"]) <= 140


@pytest.mark.parametrize(
    ("result", "state"),
    [
        ("success", "success"),
        ("failure", "failure"),
        ("cancelled", "error"),
        ("skipped", "error"),
        ("", "error"),
        ("something-new", "error"),
        ("SUCCESS", "error"),
        ("success ", "error"),
    ],
)
def test_each_recall_result_maps_to_the_true_state(tmp_path: Path, result: str, state: str) -> None:
    done, calls = _post(tmp_path, FINAL, result)
    assert done.returncode == 0, done.stderr
    assert len(calls) == 1
    fields = _fields(calls[0])
    assert fields["state"] == state
    assert fields["context"] == CONTEXT
    assert fields["target_url"] == "https://github.com/owner/data/actions/runs/4242"
    assert len(fields["description"]) <= 140


def test_an_unset_result_is_an_error_never_a_success(tmp_path: Path) -> None:
    done, calls = _post(tmp_path, FINAL, None)
    assert done.returncode == 0, done.stderr
    assert _fields(calls[0])["state"] == "error"


def test_only_a_success_result_posts_success(tmp_path: Path) -> None:
    for index, result in enumerate(["failure", "cancelled", "skipped", "", "x"]):
        sub = tmp_path / str(index)
        sub.mkdir()
        _, calls = _post(sub, FINAL, result)
        assert _fields(calls[0])["state"] != "success", result


@pytest.mark.parametrize("job", STATUS_JOBS)
def test_a_failed_api_call_fails_the_job(tmp_path: Path, job: str) -> None:
    done, calls = _post(tmp_path, job, "success", fail=True)
    assert done.returncode != 0
    assert len(calls) == 1


@pytest.mark.parametrize("missing", ["SHA", "REPO", "RUN_ID", "CONTEXT"])
@pytest.mark.parametrize("job", STATUS_JOBS)
def test_a_missing_input_posts_nothing_and_fails(tmp_path: Path, job: str, missing: str) -> None:
    env, log = _gh(tmp_path, fail=False)
    env["RECALL_RESULT"] = "success"
    env.pop(missing)
    done = subprocess.run(
        ["bash", "-c", _script(job)], env=env, cwd=tmp_path, capture_output=True, text=True, check=False,
    )
    assert done.returncode != 0
    assert log.read_text(encoding="utf-8") == ""


@pytest.mark.parametrize("job", STATUS_JOBS)
def test_the_status_scripts_pass_shellcheck(tmp_path: Path, job: str) -> None:
    import shutil

    if shutil.which("shellcheck") is None:
        pytest.skip("shellcheck is not installed")
    path = tmp_path / "step.sh"
    path.write_text("#!/usr/bin/env bash\n" + _script(job), encoding="utf-8")
    done = subprocess.run(["shellcheck", "-s", "bash", str(path)], capture_output=True, text=True, check=False)
    assert done.returncode == 0, done.stdout
