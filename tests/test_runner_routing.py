"""Runner routing guard (MODEL-578).

PR test jobs may run on a third party's runner when the repository variable
MODELSPEC_PR_RUNNER names one, and only for `pull_request` events:

    runs-on: ${{ github.event_name == 'pull_request' && vars.MODELSPEC_PR_RUNNER
                 || 'ubuntu-latest' }}   (one line in the workflows)

Unset, or on push, schedule or dispatch, every job runs on GitHub's runner.

The lane is partitioned by WORKFLOW, not by job, so no data flow inside a
workflow has to be traced:

1. Only the workflows in MOVED_WORKFLOWS use the variable, and every job in
   them uses it. Each moved workflow is unprivileged on every trigger: no
   `secrets`, no permission beyond `contents: read` / `actions: read`
   (declared explicitly), no environment, no reusable-workflow call, no
   deploy or publish step, no private-data read, no privileged trigger.
2. Every other workflow keeps an allowed GitHub label and never names the
   variable.
3. Nothing a moved workflow produces can reach a privileged job in another
   workflow: no workflow may trigger on `workflow_run` or download artifacts
   from another run, and no job that is privileged on a `pull_request` event
   may restore a cache (a third-party runner can write any key in the PR's
   cache scope). Push-time caches are main-scope, which moved workflows never
   write, because of the event gate.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
WORKFLOWS = REPO_ROOT / ".github" / "workflows"

PR_RUNNER = (
    "${{ github.event_name == 'pull_request' && vars.MODELSPEC_PR_RUNNER || 'ubuntu-latest' }}"
)
ALLOWED_LABELS = frozenset({"ubuntu-latest"})

# Adding a workflow here is a reviewed decision: read every job and trigger.
MOVED_WORKFLOWS = frozenset({"chart-check.yml", "data-freeze.yml", "test.yml"})

# Jobs privileged on pull_request that restore a cache. Each names its ticket;
# the list may only shrink, and the variable stays unset while it is non-empty.
PR_CACHE_EXCEPTIONS: dict[tuple[str, str], str] = {
    ("validate-cards.yml", "validate"): "MODEL-582: pip cache under a pull-requests: write token",
}

READ_SCOPES = frozenset({"contents", "actions"})
PRIVILEGED_TRIGGERS = frozenset({"pull_request_target", "workflow_run"})
PRIVATE_DATA_MARKERS = ("modelspec-data", "MODELSPEC_DATA", "--private-data")
DEPLOY_ACTIONS = ("cloudflare/wrangler-action", "pypa/gh-action-pypi-publish")
CACHE_ACTIONS = ("actions/cache", "actions/cache/restore")
SETUP_ACTIONS = (
    "actions/setup-python",
    "actions/setup-node",
    "actions/setup-go",
    "actions/setup-java",
    "astral-sh/setup-uv",
)
CROSS_RUN_DOWNLOAD = re.compile(
    r"\bgh\s+run\s+download\b|actions/artifacts|actions/runs/.*?/artifacts"
    r"|listWorkflowRunArtifacts|downloadArtifact|getArtifact"
)
# `${{ github.event_name != 'pull_request' && secrets.X || '' }}` is empty on a PR.
PR_GATED_SECRET = re.compile(
    r"\$\{\{\s*github\.event_name\s*!=\s*'pull_request'\s*&&\s*secrets\.[A-Za-z0-9_]+"
    r"\s*\|\|\s*''\s*\}\}"
)
NOT_ON_PULL_REQUEST = re.compile(
    r"^(github\.ref\s*==\s*'refs/heads/main'"
    r"|github\.event_name\s*!=\s*'pull_request'"
    r"|github\.event_name\s*==\s*'(push|schedule|workflow_dispatch)')$"
)


def _workflows() -> dict[str, dict]:
    return {
        path.name: yaml.safe_load(path.read_text(encoding="utf-8"))
        for path in sorted(WORKFLOWS.iterdir())
        if path.suffix in {".yml", ".yaml"}
    }


def _triggers(workflow: dict) -> set[str]:
    on = workflow.get("on", workflow.get(True))  # PyYAML reads bare `on` as True
    if isinstance(on, str):
        return {on}
    if isinstance(on, list):
        return set(on)
    return set(on or {})


def _jobs(workflow: dict) -> dict[str, dict]:
    return workflow.get("jobs") or {}


def _dump(value) -> str:
    return yaml.safe_dump(value, sort_keys=True)


def _read_only(permissions) -> bool:
    if not isinstance(permissions, dict):
        return False  # None means the repository default; strings grant broadly
    return all(
        scope in READ_SCOPES and level in {"read", "none"} for scope, level in permissions.items()
    )


def _grants_write(permissions) -> bool:
    if permissions is None:
        return True  # the repository default may grant write
    if isinstance(permissions, str):
        return permissions != "read-all"
    return any(level not in {"read", "none"} for level in permissions.values())


def _deploy_steps(job: dict) -> list[str]:
    found = []
    for step in job.get("steps", []):
        uses = step.get("uses", "")
        if uses.startswith(DEPLOY_ACTIONS):
            found.append(uses)
        for line in str(step.get("run", "")).splitlines():
            if line.lstrip().startswith("#") or "--dry-run" in line:
                continue
            wrangler = re.search(r"wrangler", line, re.I) and re.search(
                r"\b(deploy|publish|pages|secret|kv|d1|r2|versions)\b", line
            )
            publish = re.search(
                r"\b(npm|uv|twine|poetry|hatch)\s+(publish|upload)\b|\bgh\s+release\b", line
            )
            if wrangler or publish:
                found.append(line.strip())
    return found


def _restores_cache(job: dict) -> bool:
    for step in job.get("steps", []):
        uses = step.get("uses", "").split("@", 1)[0]
        with_ = step.get("with") or {}
        if uses in CACHE_ACTIONS:
            return True
        if uses in SETUP_ACTIONS and (
            with_.get("cache") or with_.get("enable-cache") not in (None, False, "false")
        ):
            return True
    return False


def _cross_run_download(job: dict) -> bool:
    for step in job.get("steps", []):
        with_ = step.get("with") or {}
        if step.get("uses", "").startswith("actions/download-artifact") and (
            "run-id" in with_ or "github-token" in with_
        ):
            return True
        if CROSS_RUN_DOWNLOAD.search(str(step.get("run", "")) + str(with_.get("script", ""))):
            return True
    return False


def _split(expression: str, operator: str) -> list[str]:
    parts, depth, start, i = [], 0, 0, 0
    while i < len(expression):
        if expression[i] == "(":
            depth += 1
        elif expression[i] == ")":
            depth -= 1
        elif depth == 0 and expression.startswith(operator, i):
            parts.append(expression[start:i])
            start = i = i + len(operator)
            continue
        i += 1
    parts.append(expression[start:])
    return [part.strip() for part in parts]


def _runs_on_pull_request(workflow: dict, job: dict) -> bool:
    """False only if the workflow lacks pull_request, or every top-level `||`
    branch of the job's `if` has a top-level `&&` term false on a PR."""
    if "pull_request" not in _triggers(workflow):
        return False
    condition = str(job.get("if") or "").strip()
    if condition.startswith("${{") and condition.endswith("}}"):
        condition = condition[3:-2].strip()
    if not condition:
        return True
    return any(
        not any(NOT_ON_PULL_REQUEST.match(term) for term in _split(branch, "&&"))
        for branch in _split(condition, "||")
    )


def _privileged_on_pull_request(workflow: dict, job: dict) -> bool:
    body = PR_GATED_SECRET.sub("", _dump(job) + _dump(workflow.get("env") or {}))
    permissions = job.get("permissions", workflow.get("permissions"))
    return (
        "secrets" in body
        or "environment" in job
        or "uses" in job
        or _grants_write(permissions)
        or bool(_deploy_steps(job))
    )


def unprivileged_failures(name: str, workflow: dict) -> list[str]:
    """Rule 1: a moved workflow holds no privilege on any trigger."""
    failures = []
    privileged = _triggers(workflow) & PRIVILEGED_TRIGGERS
    if privileged:
        failures.append(f"{name}: privileged trigger {sorted(privileged)}")
    if "pull_request" not in _triggers(workflow):
        failures.append(f"{name}: does not run on pull_request")
    if "secrets" in _dump(workflow.get("env") or {}):
        failures.append(f"{name}: workflow env references secrets")
    if not _read_only(workflow.get("permissions")):
        failures.append(f"{name}: workflow permissions are not explicit and read-only")
    for job_name, job in _jobs(workflow).items():
        where = f"{name}:{job_name}"
        body = _dump(job)
        if job.get("runs-on") != PR_RUNNER:
            failures.append(f"{where}: runs-on is not the PR runner expression")
        if "secrets" in body:
            failures.append(f"{where}: references secrets")
        if "environment" in job:
            failures.append(f"{where}: uses an environment")
        if "uses" in job:
            failures.append(f"{where}: calls a reusable workflow")
        if "permissions" in job and not _read_only(job["permissions"]):
            failures.append(f"{where}: permissions beyond contents/actions read")
        for marker in PRIVATE_DATA_MARKERS:
            if marker in body:
                failures.append(f"{where}: reads private data ({marker})")
        for step in _deploy_steps(job):
            failures.append(f"{where}: deploys or publishes: {step}")
    return failures


def routing_failures(workflows: dict[str, dict], moved: frozenset[str]) -> list[str]:
    failures = []
    for name in sorted(moved - set(workflows)):
        failures.append(f"{name}: listed as moved but missing")
    for name, workflow in workflows.items():
        if name in moved:
            failures.extend(unprivileged_failures(name, workflow))
        else:
            if "MODELSPEC_PR_RUNNER" in _dump(workflow):
                failures.append(f"{name}: not a moved workflow but names MODELSPEC_PR_RUNNER")
            for job_name, job in _jobs(workflow).items():
                if job.get("runs-on") not in ALLOWED_LABELS:
                    failures.append(f"{name}:{job_name}: runs-on {job.get('runs-on')!r}")
        # Rule 3, across workflows.
        if "workflow_run" in _triggers(workflow):
            failures.append(f"{name}: workflow_run trigger")
        for job_name, job in _jobs(workflow).items():
            where = f"{name}:{job_name}"
            if _cross_run_download(job):
                failures.append(f"{where}: downloads artifacts from another run")
            if (
                moved
                and name not in moved
                and _runs_on_pull_request(workflow, job)
                and _restores_cache(job)
                and _privileged_on_pull_request(workflow, job)
                and (name, job_name) not in PR_CACHE_EXCEPTIONS
            ):
                failures.append(f"{where}: privileged on pull_request and restores a cache")
    return failures


def test_workflows_route_by_the_structural_rules() -> None:
    failures = routing_failures(_workflows(), MOVED_WORKFLOWS)
    assert not failures, "\n".join(failures)


def test_each_cache_exception_is_still_needed() -> None:
    workflows = _workflows()
    for name, job_name in PR_CACHE_EXCEPTIONS:
        workflow = workflows[name]
        job = _jobs(workflow)[job_name]
        assert _runs_on_pull_request(workflow, job), (name, job_name)
        assert _restores_cache(job), (name, job_name)
        assert _privileged_on_pull_request(workflow, job), (name, job_name)


# The guard itself.


def _wf(job: dict | None = None, **extra) -> dict:
    base = {
        "on": {"pull_request": {}, "push": {}},
        "permissions": {"contents": "read"},
        "jobs": {"j": job if job is not None else {"runs-on": PR_RUNNER, "steps": [{"run": "t"}]}},
    }
    base.update(extra)
    return base


def _lane_job(**extra) -> dict:
    return {"runs-on": PR_RUNNER, "steps": [{"run": "pytest -q"}], **extra}


def test_the_guard_accepts_an_unprivileged_moved_workflow() -> None:
    assert routing_failures({"m.yml": _wf()}, frozenset({"m.yml"})) == []


@pytest.mark.parametrize(
    "workflow",
    [
        _wf(_lane_job(env={"K": "${{ secrets.K }}"})),
        _wf(_lane_job(steps=[{"run": "x", "env": {"K": "${{ secrets.K }}"}}])),
        # A PR-gated secret is still a secret on push: the whole workflow stays.
        _wf(_lane_job(env={"K": "${{ github.event_name != 'pull_request' && secrets.K || '' }}"})),
        _wf(env={"K": "${{ secrets.K }}"}),
        _wf(_lane_job(environment="production")),
        _wf({"uses": "./.github/workflows/r.yml", "secrets": "inherit"}),
        _wf(_lane_job(permissions={"pull-requests": "write"})),
        _wf(_lane_job(permissions={"pull-requests": "read"})),
        _wf(_lane_job(permissions={"id-token": "write"})),
        _wf(permissions=None),
        _wf(permissions="read-all"),
        _wf(_lane_job(steps=[{"run": "npx wrangler deploy"}])),
        _wf(_lane_job(steps=[{"uses": "cloudflare/wrangler-action@x"}])),
        _wf(_lane_job(steps=[{"uses": "pypa/gh-action-pypi-publish@x"}])),
        _wf(_lane_job(steps=[{"run": "git clone https://github.com/turbobeest/modelspec-data"}])),
        _wf(on={"pull_request_target": {}}),
        _wf(on={"schedule": [{"cron": "0 0 * * *"}]}),
        _wf({"runs-on": "ubuntu-latest"}),  # a job left behind in a moved workflow
        _wf({"runs-on": "${{ vars.MODELSPEC_PR_RUNNER || 'ubuntu-latest' }}"}),  # no event gate
    ],
)
def test_the_guard_rejects_a_privileged_moved_workflow(workflow) -> None:
    assert routing_failures({"m.yml": workflow}, frozenset({"m.yml"}))


def test_a_privileged_job_anywhere_keeps_its_whole_workflow_on_github() -> None:
    workflow = _wf()
    workflow["jobs"]["deploy"] = {
        "runs-on": "ubuntu-latest",
        "if": "github.ref == 'refs/heads/main'",
        "env": {"K": "${{ secrets.K }}"},
        "steps": [{"run": "x"}],
    }
    assert routing_failures({"m.yml": workflow}, frozenset({"m.yml"}))


@pytest.mark.parametrize(
    "job",
    [
        {"runs-on": PR_RUNNER},
        {"runs-on": "self-hosted"},
        {"runs-on": "ubicloud-standard-4"},
        {"runs-on": "ubuntu-latest", "env": {"R": "${{ vars.MODELSPEC_PR_RUNNER }}"}},
    ],
)
def test_the_guard_rejects_the_variable_or_a_new_label_outside_moved_workflows(job) -> None:
    assert routing_failures({"o.yml": _wf(job)}, frozenset())


@pytest.mark.parametrize(
    "step",
    [
        {"uses": "actions/download-artifact@x", "with": {"run-id": "1"}},
        {"uses": "actions/download-artifact@x", "with": {"github-token": "${{ github.token }}"}},
        {"run": "gh run download 123 -n x"},
        {"run": "gh api repos/o/r/actions/artifacts/1/zip"},
        {"run": "gh api repos/o/r/actions/runs/${{ inputs.run_id }}/artifacts"},
        {
            "uses": "actions/github-script@x",
            "with": {"script": "github.rest.actions.downloadArtifact()"},
        },
    ],
)
def test_the_guard_rejects_every_cross_run_artifact_download(step) -> None:
    job = {"runs-on": "ubuntu-latest", "steps": [step]}
    assert routing_failures({"o.yml": _wf(job)}, frozenset())


def test_the_guard_rejects_a_workflow_run_trigger() -> None:
    workflow = _wf({"runs-on": "ubuntu-latest"}, on={"workflow_run": {"workflows": ["Test suite"]}})
    assert routing_failures({"o.yml": workflow}, frozenset())


@pytest.mark.parametrize(
    "privilege",
    [
        {"permissions": {"pull-requests": "write"}},
        {"env": {"K": "${{ secrets.K }}"}},
        {"environment": "production"},
    ],
)
@pytest.mark.parametrize(
    "cache_step",
    [
        {"uses": "actions/setup-python@x", "with": {"cache": "pip"}},
        {"uses": "actions/setup-node@x", "with": {"cache": "npm"}},
        {"uses": "astral-sh/setup-uv@x", "with": {"enable-cache": True}},
        {"uses": "actions/cache@x", "with": {"path": "p", "key": "k"}},
        {"uses": "actions/cache/restore@x", "with": {"path": "p", "key": "k"}},
    ],
)
def test_the_guard_rejects_a_privileged_pr_job_restoring_a_cache(privilege, cache_step) -> None:
    other = {"runs-on": "ubuntu-latest", "steps": [cache_step], **privilege}
    workflows = {"m.yml": _wf(), "o.yml": _wf(other)}
    assert routing_failures(workflows, frozenset({"m.yml"}))


def test_the_guard_allows_cache_restore_by_a_job_that_is_privileged_only_off_pr() -> None:
    gated = "${{ github.event_name != 'pull_request' && secrets.K || '' }}"
    build = {
        "runs-on": "ubuntu-latest",
        "steps": [{"uses": "actions/setup-python@x", "with": {"cache": "pip"}}],
        "env": {"K": gated},
    }
    deploy = {
        "runs-on": "ubuntu-latest",
        "if": "github.ref == 'refs/heads/main' && github.event_name != 'pull_request'",
        "env": {"K": "${{ secrets.K }}"},
        "steps": [{"uses": "actions/setup-node@x", "with": {"cache": "npm"}}],
    }
    other = _wf(build)
    other["jobs"]["deploy"] = deploy
    assert routing_failures({"m.yml": _wf(), "o.yml": other}, frozenset({"m.yml"})) == []
