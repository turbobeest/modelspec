"""Runner routing guard (MODEL-578).

PR test jobs may run on a third party's runner when the repository variable
MODELSPEC_PR_RUNNER names one, and only for `pull_request` events. Unset, or on
any other event (push to main, schedule, dispatch), they run on GitHub's
runner, so deleting the variable rolls every job back and nothing a trusted
trigger runs, caches or deploys ever comes from the third party.

A job on the variable must never see a secret, the private data or a deploy
credential: no `secrets` reference (workflow env included), no environment,
no write permission, no deploy command and no private-data checkout.

Three channels could carry a third-party runner's output into a privileged
job, and each is checked:
- artifacts and job outputs (`needs`) inside the workflow;
- artifacts across runs (`workflow_run` triggers, `download-artifact` with a
  `run-id`), which no workflow may use;
- caches. A PR's cache scope is shared by every workflow that runs on that
  PR, so a job that holds a write token or a secret on `pull_request` must not
  restore a cache, unless it is a reviewed exception below.
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

# The PR test lane. Adding a job here is a reviewed decision: read its steps.
PR_LANE = frozenset(
    {
        ("accuracy.yml", "accuracy"),
        ("chart-check.yml", "check-evidence-charts"),
        ("data-freeze.yml", "freeze"),
        ("deploy-sites.yml", "decide-browser"),
        ("mcp.yml", "test"),
        ("rank-api.yml", "bundle"),
        ("rank-api.yml", "memory"),
        ("test.yml", "package-smoke"),
        ("test.yml", "pytest-perf-and-collection"),
        ("test.yml", "pytest-shards"),
        ("test.yml", "required-pytest"),
    }
)

# PR-privileged jobs that restore a cache the lane can write. Each needs a
# reason and a ticket; the list may only shrink.
PR_CACHE_EXCEPTIONS: dict[tuple[str, str], str] = {
    ("validate-cards.yml", "validate"): (
        "MODEL-578 follow-up: restores the pip cache with a pull-requests: write token. "
        "Drop its `cache: 'pip'` (a non-runs-on edit) before MODELSPEC_PR_RUNNER is set."
    ),
}


def test_cache_exceptions_name_real_jobs() -> None:
    workflows = _workflows()
    for name, job in PR_CACHE_EXCEPTIONS:
        assert job in (workflows[name].get("jobs") or {}), (name, job)


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
# `${{ github.event_name != 'pull_request' && secrets.X || '' }}` is empty on a PR.
PR_GATED_SECRET = re.compile(
    r"\$\{\{\s*github\.event_name\s*!=\s*'pull_request'\s*&&\s*secrets\.[A-Za-z0-9_]+\s*\|\|\s*''\s*\}\}"
)


def _load(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def _workflows() -> dict[str, dict]:
    return {
        path.name: _load(path)
        for path in sorted(WORKFLOWS.iterdir())
        if path.suffix in {".yml", ".yaml"}
    }


def _triggers(workflow: dict) -> set[str]:
    # PyYAML reads the bare key `on` as True.
    on = workflow.get("on", workflow.get(True))
    if isinstance(on, str):
        return {on}
    if isinstance(on, list):
        return set(on)
    return set(on or {})


def _dump(value) -> str:
    return yaml.safe_dump(value, sort_keys=True)


def _has_write_permission(permissions) -> bool:
    if permissions is None:
        return True  # the repository default may grant write
    if isinstance(permissions, str):
        return permissions != "read-all"
    return any(str(level) not in {"read", "none"} for level in permissions.values())


def _deploy_commands(job: dict) -> list[str]:
    found = []
    for step in job.get("steps", []):
        uses = step.get("uses", "")
        if uses.startswith(DEPLOY_ACTIONS):
            found.append(uses)
        for line in str(step.get("run", "")).splitlines():
            code = "" if line.lstrip().startswith("#") else line
            wrangler = re.search(r"wrangler", code, re.I) and re.search(
                r"\b(deploy|publish|pages|secret|kv|d1|r2|versions)\b", code
            )
            publish = re.search(
                r"\b(npm|uv|twine|poetry|hatch)\s+(publish|upload)\b|\bgh\s+release\b", code
            )
            if (wrangler or publish) and "--dry-run" not in code:
                found.append(code.strip())
    return found


def _restores_cache(job: dict) -> bool:
    for step in job.get("steps", []):
        uses = step.get("uses", "").split("@", 1)[0]
        if uses in CACHE_ACTIONS:
            return True
        if uses in SETUP_ACTIONS:
            with_ = step.get("with") or {}
            if with_.get("cache") or with_.get("enable-cache") not in (None, False, "false"):
                return True
    return False


def _privileged(workflow: dict, job: dict, *, on_pull_request: bool) -> bool:
    """Holds a secret, a write token, an environment or deploys, for that event."""
    body = _dump(job) + _dump(workflow.get("env") or {})
    if on_pull_request:
        body = PR_GATED_SECRET.sub("", body)
    permissions = job.get("permissions", workflow.get("permissions"))
    return (
        "secrets" in body
        or "environment" in job
        or _has_write_permission(permissions)
        or bool(_deploy_commands(job))
    )


def _top_level_split(expression: str, operator: str) -> list[str]:
    parts, depth, start, i = [], 0, 0, 0
    while i < len(expression):
        char = expression[i]
        if char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
        elif depth == 0 and expression.startswith(operator, i):
            parts.append(expression[start:i])
            start = i + len(operator)
            i += len(operator)
            continue
        i += 1
    parts.append(expression[start:])
    return [part.strip() for part in parts]


NOT_ON_PULL_REQUEST = re.compile(
    r"^(github\.ref\s*==\s*'refs/heads/main'"
    r"|github\.event_name\s*!=\s*'pull_request'"
    r"|github\.event_name\s*==\s*'(push|schedule|workflow_dispatch)')$"
)


def _runs_on_pull_request(job: dict) -> bool:
    """False only when every top-level `||` branch of the job's `if` has a
    top-level `&&` term that cannot hold on a pull_request event."""
    condition = str(job.get("if", "") or "").strip()
    if condition.startswith("${{") and condition.endswith("}}"):
        condition = condition[3:-2].strip()
    if not condition:
        return True
    for branch in _top_level_split(condition, "||"):
        terms = _top_level_split(branch, "&&")
        if not any(NOT_ON_PULL_REQUEST.match(term) for term in terms):
            return True
    return False


def _needs(job: dict) -> list[str]:
    needs = job.get("needs") or []
    return [needs] if isinstance(needs, str) else list(needs)


def routing_failures(workflows: dict[str, dict]) -> list[str]:
    """Every rule this guard enforces, as a list of failures (empty = pass)."""
    failures = []
    on_variable: dict[str, set[str]] = {}
    for name, workflow in workflows.items():
        triggers = _triggers(workflow)
        if "workflow_run" in triggers:
            failures.append(f"{name}: workflow_run can consume artifacts of PR runs")
        for job_name, job in (workflow.get("jobs") or {}).items():
            where = f"{name}:{job_name}"
            for step in job.get("steps", []):
                if step.get("uses", "").startswith("actions/download-artifact") and "run-id" in (
                    step.get("with") or {}
                ):
                    failures.append(f"{where}: downloads artifacts from another run")
            runs_on = job.get("runs-on")
            if runs_on is None:
                failures.append(f"{where}: no runs-on")
                continue
            if runs_on == PR_RUNNER:
                on_variable.setdefault(name, set()).add(job_name)
            elif not (isinstance(runs_on, str) and runs_on in ALLOWED_LABELS):
                failures.append(
                    f"{where}: runs-on {runs_on!r} is neither {PR_RUNNER} nor an allowed label"
                )
                continue
            if "MODELSPEC_PR_RUNNER" in _dump({k: v for k, v in job.items() if k != "runs-on"}):
                failures.append(f"{where}: MODELSPEC_PR_RUNNER used outside runs-on")
            if runs_on != PR_RUNNER:
                continue
            body = _dump(job)
            if "secrets" in body:
                failures.append(f"{where}: on the PR runner but references secrets")
            if "secrets" in _dump(workflow.get("env") or {}):
                failures.append(
                    f"{where}: on the PR runner in a workflow whose env references secrets"
                )
            if "environment" in job:
                failures.append(f"{where}: on the PR runner but uses a deployment environment")
            permissions = job.get("permissions", workflow.get("permissions"))
            if permissions is None:
                failures.append(f"{where}: on the PR runner without explicit read-only permissions")
            elif _has_write_permission(permissions):
                failures.append(f"{where}: on the PR runner with write permission {permissions!r}")
            for marker in PRIVATE_DATA_MARKERS:
                if marker in body:
                    failures.append(
                        f"{where}: on the PR runner but mentions private data ({marker})"
                    )
            for command in _deploy_commands(job):
                failures.append(f"{where}: on the PR runner but deploys or publishes: {command}")
            privileged_triggers = triggers & PRIVILEGED_TRIGGERS
            if privileged_triggers:
                failures.append(
                    f"{where}: on the PR runner in a {sorted(privileged_triggers)} workflow"
                )
            if "pull_request" not in triggers:
                failures.append(
                    f"{where}: on the PR runner but its workflow does not run on pull_request"
                )

    lane_exists = any(on_variable.values())
    for name, workflow in workflows.items():
        lane = on_variable.get(name, set())
        on_pr = "pull_request" in _triggers(workflow)
        for job_name, job in (workflow.get("jobs") or {}).items():
            if job_name in lane or not _runs_on_pull_request(job):
                # The lane is PR-only: a job that never runs on pull_request
                # only ever sees GitHub-runner artifacts and main-ref caches.
                continue
            where = f"{name}:{job_name}"
            # Within the workflow: no artifacts or outputs from the lane (direct or transitive).
            upstream, frontier = set(), _needs(job)
            jobs = workflow.get("jobs") or {}
            while frontier:
                item = frontier.pop()
                if item not in upstream:
                    upstream.add(item)
                    frontier.extend(_needs(jobs.get(item, {})))
            tainted = upstream & lane
            if tainted and _privileged(workflow, job, on_pull_request=True):
                body = _dump(job)
                for source in sorted(tainted):
                    if f"needs.{source}.outputs" in body:
                        failures.append(
                            f"{where}: privileged job reads outputs of PR-runner job {source}"
                        )
                if "actions/download-artifact" in body:
                    failures.append(
                        f"{where}: privileged job downloads artifacts after PR-runner"
                        f" jobs {sorted(tainted)}"
                    )
            # Across workflows: the PR cache scope.
            if (
                lane_exists
                and on_pr
                and _restores_cache(job)
                and _privileged(workflow, job, on_pull_request=True)
            ):
                if (name, job_name) not in PR_CACHE_EXCEPTIONS:
                    failures.append(
                        f"{where}: privileged on pull_request and restores a cache"
                        " the PR runner can write"
                    )
    return failures


def _lane(workflows: dict[str, dict]) -> set[tuple[str, str]]:
    return {
        (name, job_name)
        for name, workflow in workflows.items()
        for job_name, job in (workflow.get("jobs") or {}).items()
        if job.get("runs-on") == PR_RUNNER
    }


def test_every_workflow_job_routes_by_the_approved_rules() -> None:
    failures = routing_failures(_workflows())
    assert not failures, "\n".join(failures)


def test_the_pr_runner_lane_is_exactly_the_reviewed_job_list() -> None:
    assert _lane(_workflows()) == PR_LANE


def test_the_runner_expression_falls_back_on_every_trusted_event() -> None:
    # The expression only picks the variable on pull_request; push, schedule
    # and dispatch runs keep GitHub's runner even with the variable set.
    assert PR_RUNNER.startswith(
        "${{ github.event_name == 'pull_request' && vars.MODELSPEC_PR_RUNNER || "
    )


# The guard itself must catch each way a privileged job could reach the PR runner.


def _workflow(job: dict, **extra) -> dict:
    base = {"on": {"pull_request": {}}, "permissions": {"contents": "read"}, "jobs": {"j": job}}
    base.update(extra)
    return {"fixture.yml": base}


def _job(**extra) -> dict:
    job = {"runs-on": PR_RUNNER, "steps": [{"run": "pytest -q"}]}
    job.update(extra)
    return job


def test_the_guard_accepts_a_plain_pr_test_job() -> None:
    assert routing_failures(_workflow(_job())) == []


def test_the_guard_accepts_a_secret_that_is_empty_on_pull_request() -> None:
    secret = "${{ github.event_name != 'pull_request' && secrets.K || '' }}"
    workflows = {
        "fixture.yml": {
            "on": {"pull_request": {}, "push": {}},
            "permissions": {"contents": "read"},
            "jobs": {
                "lane": _job(),
                "build": {
                    "runs-on": "ubuntu-latest",
                    "needs": "lane",
                    "steps": [
                        {"uses": "actions/setup-python@x", "with": {"cache": "pip"}},
                        {"run": "make", "env": {"K": secret}},
                    ],
                },
            },
        }
    }
    assert routing_failures(workflows) == []


@pytest.mark.parametrize(
    "workflows",
    [
        _workflow(_job(env={"TOKEN": "${{ secrets.DEPLOY_TOKEN }}"})),
        _workflow(_job(steps=[{"run": "x", "env": {"K": "${{ secrets.K }}"}}])),
        _workflow(_job(secrets="inherit")),
        _workflow(_job(), env={"K": "${{ secrets.K }}"}),
        _workflow(_job(environment="production")),
        _workflow(_job(permissions={"contents": "write"})),
        _workflow(_job(permissions={"id-token": "write"})),
        _workflow(_job(permissions="write-all")),
        _workflow(_job(), permissions=None),
        _workflow(_job(steps=[{"run": "npx wrangler deploy"}])),
        _workflow(_job(steps=[{"run": "uv run pywrangler deploy --env staging"}])),
        _workflow(_job(steps=[{"uses": "cloudflare/wrangler-action@" + "a" * 40}])),
        _workflow(_job(steps=[{"uses": "pypa/gh-action-pypi-publish@" + "a" * 40}])),
        _workflow(
            _job(steps=[{"run": "git clone https://github.com/turbobeest/modelspec-data.git"}])
        ),
        _workflow(_job(steps=[{"run": "python vendor.py --data-dir d --private-data"}])),
        _workflow(_job(), on={"pull_request_target": {}}),
        _workflow(_job(), on={"schedule": [{"cron": "0 0 * * *"}]}),
        _workflow({"runs-on": "${{ vars.MODELSPEC_PR_RUNNER || 'ubuntu-latest' }}"}),  # every event
        _workflow({"runs-on": "${{ vars.OTHER || 'ubuntu-latest' }}"}),
        _workflow({"runs-on": "self-hosted"}),
        _workflow({"runs-on": "ubicloud-standard-4"}),
        _workflow({"runs-on": "ubuntu-latest", "env": {"R": "${{ vars.MODELSPEC_PR_RUNNER }}"}}),
        _workflow({"runs-on": "ubuntu-latest"}, on={"workflow_run": {"workflows": ["x"]}}),
        _workflow(
            {
                "runs-on": "ubuntu-latest",
                "steps": [
                    {
                        "uses": "actions/download-artifact@x",
                        "with": {"run-id": "${{ github.event.workflow_run.id }}"},
                    }
                ],
            }
        ),
    ],
)
def test_the_guard_rejects_each_privileged_route(workflows) -> None:
    assert routing_failures(workflows)


@pytest.mark.parametrize(
    "consumer",
    [
        {
            "needs": ["lane"],
            "steps": [
                {"uses": "actions/download-artifact@" + "a" * 40},
                {"run": "x", "env": {"K": "${{ secrets.K }}"}},
            ],
        },
        {
            "needs": "lane",
            "env": {"K": "${{ secrets.K }}"},
            "steps": [{"run": "echo ${{ needs.lane.outputs.mode }}"}],
        },
        {
            "needs": "middle",
            "permissions": {"contents": "write"},  # transitive
            "steps": [{"uses": "actions/download-artifact@" + "a" * 40}],
        },
    ],
)
def test_the_guard_rejects_a_privileged_job_that_trusts_the_pr_runner(consumer) -> None:
    consumer = {"runs-on": "ubuntu-latest", **consumer}
    workflows = {
        "fixture.yml": {
            "on": {"pull_request": {}},
            "permissions": {"contents": "read"},
            "jobs": {
                "lane": _job(),
                "middle": {"runs-on": "ubuntu-latest", "needs": "lane"},
                "consumer": consumer,
            },
        }
    }
    assert routing_failures(workflows)


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
def test_the_guard_rejects_a_privileged_pr_job_restoring_a_shared_cache(
    privilege, cache_step
) -> None:
    other = {"runs-on": "ubuntu-latest", "steps": [cache_step], **privilege}
    workflows = {
        "lane.yml": {
            "on": {"pull_request": {}},
            "permissions": {"contents": "read"},
            "jobs": {"lane": _job()},
        },
        "other.yml": {
            "on": {"pull_request": {}},
            "permissions": {"contents": "read"},
            "jobs": {"other": other},
        },
    }
    assert routing_failures(workflows)
