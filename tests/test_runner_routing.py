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
   from another run.

Rule 4 holds on every trigger, with or without the variable (MODEL-582): a job
that holds a secret, a write scope, an environment, a reusable-workflow call or
a deploy step restores no cache. Nor does it take an artifact from a run that
has any cache-restoring job, or read `needs` outputs relayed from one.
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

READ_SCOPES = frozenset({"contents", "actions"})
PRIVILEGED_TRIGGERS = frozenset({"pull_request_target", "workflow_run"})
PRIVATE_DATA_MARKERS = ("modelspec-data", "MODELSPEC_DATA", "--private-data")
DEPLOY_ACTIONS = ("cloudflare/wrangler-action", "pypa/gh-action-pypi-publish")
# An action whose name holds "cache" restores one, whatever its inputs.
CACHE_ACTION_NAME = re.compile(r"cache", re.I)
# Any input whose name holds "cache" (cache, enable-cache, bundler-cache,
# package-manager-cache, ...) turns a cache on unless it is off. A negated input
# (cache-disabled, no-cache, skip-cache) turns it on unless it is true.
CACHE_INPUT = re.compile(r"cache", re.I)
NEGATED_INPUT = re.compile(r"disable|^no-|skip", re.I)
# These cache unless told not to (setup-uv's `auto`, setup-go's default).
CACHE_ON_BY_DEFAULT = {"astral-sh/setup-uv": "enable-cache", "actions/setup-go": "cache"}
OFF = (None, "", False, "false")
ON = (True, "true")
# Every action, at its exact pin, that may run in a workflow holding a
# privileged job, upstream jobs included: each was read for what it caches
# (MODEL-582). A new action, a new pin, a local action or a reusable workflow
# is opaque here: review it, then add it.
REVIEWED_ACTIONS = frozenset(
    {
        "actions/checkout@11d5960a326750d5838078e36cf38b85af677262",
        "actions/download-artifact@d3f86a106a0bac45b974a628896c90dbdf5c8093",
        "actions/github-script@f28e40c7f34bde8b3046d885e986cb6290c5673b",
        "actions/setup-node@49933ea5288caeca8642d1e84afbd3f7d6820020",  # v4: no default cache
        "actions/setup-python@a26af69be951a213d495a4c3e4e4022e16d87065",
        "actions/upload-artifact@ea165f8d65b6e75b540449e92b4886f43607fa02",
        "astral-sh/setup-uv@d0cc045d04ccac9d8b7881df0226f9e82c39688e",
        "cloudflare/wrangler-action@9acf94ace14e7dc412b076f2c5c20b8ce93c79cd",
        "peter-evans/create-pull-request@22a9089034f40e5a961c8808d113e2c98fb63676",
        "pypa/gh-action-pypi-publish@7245906fb61fa33a13554f9d5fb856fe61758086",
        # Detected as a cache wherever it appears.
        "actions/cache@0057852bfaa89a56745cba8c7296529d2fc39830",
    }
)
EXPRESSION = re.compile(r"\$\{\{(.*?)\}\}", re.S)
# Any use of the `needs` context except `needs.<job>.result` reads job data.
NEEDS_DATA = re.compile(r"\bneeds\b(?!\.[A-Za-z0-9_-]+\.result\b)")
CROSS_RUN_DOWNLOAD = re.compile(
    r"\bgh\s+run\s+download\b|actions/artifacts|actions/runs/.*?/artifacts"
    r"|listWorkflowRunArtifacts|downloadArtifact|getArtifact"
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
        if CACHE_ACTION_NAME.search(uses):
            return True
        for key, value in with_.items():
            if not CACHE_INPUT.search(str(key)):
                continue
            if (value not in ON) if NEGATED_INPUT.search(str(key)) else (value not in OFF):
                return True
        default_input = CACHE_ON_BY_DEFAULT.get(uses)
        if default_input and (default_input not in with_ or with_[default_input] not in OFF):
            return True
    return False


def _reads_needs_data(job: dict) -> bool:
    """True if any expression reads the `needs` context beyond `.result`."""
    rest = {key: value for key, value in job.items() if key != "needs"}
    texts = EXPRESSION.findall(_dump(rest))
    # `if:` conditions may omit the ${{ }} wrapper.
    texts += [str(job.get("if") or "")]
    texts += [str(step.get("if") or "") for step in job.get("steps", [])]
    return any(NEEDS_DATA.search(text) for text in texts)


def _opaque_actions(job: dict) -> list[str]:
    found = []
    if "uses" in job:
        found.append(f"reusable workflow {job['uses']}")
    for step in job.get("steps", []):
        uses = step.get("uses")
        if uses and uses not in REVIEWED_ACTIONS:
            found.append(uses)
    return found


def _needs(job: dict) -> list[str]:
    needs = job.get("needs") or []
    return [needs] if isinstance(needs, str) else list(needs)


def _ancestors(jobs: dict[str, dict], job_name: str) -> set[str]:
    seen, todo = set(), list(_needs(jobs[job_name]))
    while todo:
        name = todo.pop()
        if name not in seen and name in jobs:
            seen.add(name)
            todo.extend(_needs(jobs[name]))
    return seen


def _downloads_artifacts(job: dict) -> bool:
    return _cross_run_download(job) or any(
        step.get("uses", "").startswith("actions/download-artifact")
        for step in job.get("steps", [])
    )


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


def _holds_privilege(workflow: dict, job: dict) -> bool:
    """On any trigger: a PR-gated secret is still a secret on push."""
    body = _dump(job) + _dump(workflow.get("env") or {})
    permissions = job.get("permissions", workflow.get("permissions"))
    return (
        "secrets" in body
        or "environment" in job
        or "uses" in job
        or _grants_write(permissions)
        or bool(_deploy_steps(job))
    )


def cache_failures(name: str, workflow: dict) -> list[str]:
    """Rule 4: no cache, and nothing built under one, inside a privileged job."""
    failures = []
    jobs = _jobs(workflow)
    caching = {job_name for job_name, job in jobs.items() if _restores_cache(job)}
    if any(_holds_privilege(workflow, job) for job in jobs.values()):
        # What an upstream job runs can reach a privileged job, so every job counts.
        for job_name, job in jobs.items():
            for action in _opaque_actions(job):
                failures.append(f"{name}:{job_name}: unreviewed action beside a privileged job: {action}")
    for job_name, job in jobs.items():
        if not _holds_privilege(workflow, job):
            continue
        where = f"{name}:{job_name}"
        if job_name in caching:
            failures.append(f"{where}: privileged and restores a cache")
        if caching and _downloads_artifacts(job):
            failures.append(f"{where}: privileged and downloads artifacts in a run that caches")
        if caching and _reads_needs_data(job):
            # Data can relay what any ancestor computed or downloaded.
            upstream = _ancestors(jobs, job_name)
            if upstream & caching or any(_downloads_artifacts(jobs[u]) for u in upstream):
                failures.append(f"{where}: privileged and reads needs data built under a cache")
    return failures


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
            if _cross_run_download(job):
                failures.append(f"{name}:{job_name}: downloads artifacts from another run")
        failures.extend(cache_failures(name, workflow))
    return failures


def test_workflows_route_by_the_structural_rules() -> None:
    failures = routing_failures(_workflows(), MOVED_WORKFLOWS)
    assert not failures, "\n".join(failures)


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


PRIVILEGES = [
    {"permissions": {"pull-requests": "write"}},
    {"permissions": {"issues": "write"}},
    {"env": {"K": "${{ secrets.K }}"}},
    # A PR-gated secret is still a secret on push and dispatch.
    {"env": {"K": "${{ github.event_name != 'pull_request' && secrets.K || '' }}"}},
    {"environment": "production"},
    {"steps": [{"run": "npx wrangler deploy"}]},
]
CACHE_STEPS = [
    {"uses": "actions/setup-python@x", "with": {"cache": "pip"}},
    {"uses": "actions/setup-node@x", "with": {"cache": "npm"}},
    {"uses": "actions/setup-node@x", "with": {"package-manager-cache": True}},
    {"uses": "astral-sh/setup-uv@x", "with": {"enable-cache": True}},
    {"uses": "astral-sh/setup-uv@x", "with": {"enable-cache": "${{ vars.X != 'true' }}"}},
    {"uses": "astral-sh/setup-uv@x"},  # `auto` caches on GitHub's runners
    {"uses": "actions/setup-go@x"},  # caches unless told not to
    {"uses": "actions/setup-python@x", "with": {"cache": "pip", "cache-dependency-path": "p"}},
    {"uses": "actions/cache@x", "with": {"path": "p", "key": "k"}},
    {"uses": "actions/cache/restore@x", "with": {"path": "p", "key": "k"}},
]


_PINS = {uses.split("@", 1)[0]: uses for uses in REVIEWED_ACTIONS}


def _pin(step: dict) -> dict:
    """Swap a placeholder `name@x` for the reviewed pin of that action, if any."""
    uses = step.get("uses", "")
    if uses.endswith("@x") and uses[:-2] in _PINS:
        return {**step, "uses": _PINS[uses[:-2]]}
    return step


def _job(*steps, **extra) -> dict:
    job = {"runs-on": "ubuntu-latest", **extra}
    job["steps"] = [_pin(step) for step in [*steps, *extra.get("steps", [])]]
    return job


def _other(**jobs) -> dict:
    return {"on": {"push": {}, "workflow_dispatch": {}}, "permissions": {"contents": "read"}, "jobs": jobs}


@pytest.mark.parametrize("privilege", PRIVILEGES)
@pytest.mark.parametrize("cache_step", CACHE_STEPS)
@pytest.mark.parametrize("moved", [frozenset(), frozenset({"m.yml"})])
def test_the_guard_rejects_a_privileged_job_restoring_a_cache(privilege, cache_step, moved) -> None:
    # On any trigger, whether or not any workflow is in the PR-runner lane.
    workflows = {"o.yml": _other(j=_job(cache_step, **privilege))}
    if moved:
        workflows["m.yml"] = _wf()
    assert routing_failures(workflows, moved)
    assert _restores_cache(_job(cache_step))
    assert any("restores a cache" in f for f in cache_failures("o.yml", workflows["o.yml"]))


@pytest.mark.parametrize(
    "step",
    [
        {"uses": "actions/setup-python@x", "with": {"python-version": "3.11"}},
        {"uses": "actions/setup-node@x", "with": {"node-version": "22"}},
        {"uses": "astral-sh/setup-uv@x", "with": {"enable-cache": False}},
        {"uses": "astral-sh/setup-uv@x", "with": {"enable-cache": "false"}},
        {"uses": "actions/setup-node@x", "with": {"cache": ""}},
        {"uses": "actions/setup-python@x", "with": {"cache": ""}},
    ],
)
def test_the_guard_accepts_a_privileged_job_without_a_cache(step) -> None:
    workflow = _other(j=_job(step, environment="production", env={"K": "${{ secrets.K }}"}))
    assert routing_failures({"o.yml": workflow}, frozenset()) == []


def test_the_guard_accepts_a_cache_in_an_unprivileged_job_beside_a_privileged_one() -> None:
    build = _job({"uses": "actions/setup-node@x", "with": {"cache": "npm"}})
    deploy = _job({"run": "x"}, needs="build", environment="production", **{"if": "needs.build.result == 'success'"})
    assert routing_failures({"o.yml": _other(build=build, deploy=deploy)}, frozenset()) == []


def test_the_guard_rejects_a_privileged_job_taking_artifacts_from_a_run_that_caches() -> None:
    # Any job in the run can upload an artifact, needs or not.
    lint = _job({"uses": "actions/setup-node@x", "with": {"cache": "npm"}})
    build = _job({"uses": "actions/upload-artifact@x", "with": {"name": "site"}})
    deploy = _job(
        {"uses": "actions/download-artifact@x", "with": {"name": "site"}},
        needs="build",
        environment="production",
    )
    workflow = _other(lint=lint, build=build, deploy=deploy)
    assert routing_failures({"o.yml": workflow}, frozenset())
    del workflow["jobs"]["lint"]
    assert routing_failures({"o.yml": workflow}, frozenset()) == []


@pytest.mark.parametrize("relay", [False, True])
@pytest.mark.parametrize(
    "read",
    [
        "${{{{ needs.{0}.outputs.v }}}}",
        "${{{{ needs['{0}'].outputs.v }}}}",
        "${{{{ toJSON(needs) }}}}",
        "${{{{ needs.{0}.outputs['v'] }}}}",
    ],
)
def test_the_guard_rejects_a_privileged_job_reading_needs_data_built_under_a_cache(relay, read) -> None:
    cached = _job({"uses": "actions/setup-python@x", "with": {"cache": "pip"}}, outputs={"v": "x"})
    jobs = {"build": cached}
    if relay:
        jobs["relay"] = _job({"run": "x"}, needs="build", outputs={"v": "${{ needs.build.outputs.v }}"})
    source = "relay" if relay else "build"
    jobs["deploy"] = _job(
        {"run": "echo " + read.format(source)},
        needs=source,
        env={"K": "${{ secrets.K }}"},
    )
    assert routing_failures({"o.yml": _other(**jobs)}, frozenset())


def test_the_guard_accepts_a_privileged_job_reading_only_a_result() -> None:
    build = _job({"uses": "actions/setup-python@x", "with": {"cache": "pip"}}, outputs={"v": "x"})
    alert = _job(
        {"run": "x", "if": "needs.build.result == 'failure'"},
        needs="build",
        permissions={"issues": "write"},
        **{"if": "${{ always() && needs.build.result != 'skipped' }}"},
    )
    assert routing_failures({"o.yml": _other(build=build, alert=alert)}, frozenset()) == []


@pytest.mark.parametrize(
    "step",
    [
        {"uses": "actions/setup-dotnet@x", "with": {"cache": True}},
        {"uses": "ruby/setup-ruby@x", "with": {"bundler-cache": True}},
        {"uses": "Swatinem/rust-cache@x"},
        {"uses": "some/tool@x", "with": {"cache-disabled": False}},
        {"uses": "some/tool@x", "with": {"cache-disabled": "${{ vars.X }}"}},
    ],
)
def test_the_guard_reads_cache_inputs_on_any_action(step) -> None:
    assert _restores_cache(_job(step))


def test_a_negated_cache_input_set_to_true_is_off() -> None:
    assert not _restores_cache(_job({"uses": "some/tool@x", "with": {"cache-disabled": True}}))


@pytest.mark.parametrize(
    "upstream",
    [
        _job({"uses": "./.github/actions/setup"}, outputs={"v": "x"}),
        _job({"uses": "gradle/actions/setup-gradle@x"}, outputs={"v": "x"}),
        # A reviewed action at a new pin is opaque until reviewed again.
        _job({"uses": "actions/setup-node@v9"}, outputs={"v": "x"}),
    ],
)
def test_the_guard_rejects_an_unreviewed_action_upstream_of_a_privileged_job(upstream) -> None:
    deploy = _job({"run": "echo ${{ needs.build.outputs.v }}"}, needs="build", environment="production")
    assert routing_failures({"o.yml": _other(build=upstream, deploy=deploy)}, frozenset())


def test_the_guard_ignores_unreviewed_actions_in_a_workflow_without_privilege() -> None:
    lint = _job({"uses": "Swatinem/rust-cache@x"})
    assert routing_failures({"o.yml": _other(lint=lint)}, frozenset()) == []


@pytest.mark.parametrize(
    "job",
    [
        _job({"uses": "./.github/actions/setup"}, environment="production"),
        _job({"uses": "someone/new-action@x"}, permissions={"contents": "write"}),
        {"uses": "./.github/workflows/r.yml", "secrets": "inherit"},
    ],
)
def test_the_guard_rejects_an_unreviewed_action_in_a_privileged_job(job) -> None:
    assert routing_failures({"o.yml": _other(j=job)}, frozenset())
