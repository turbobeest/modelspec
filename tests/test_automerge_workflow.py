"""Auto-merge must queue with RESEARCH_PR_TOKEN, not GITHUB_TOKEN.

GitHub does not start workflow runs for events caused by GITHUB_TOKEN, so a
merge attributed to github-actions[bot] never deploys. An empty
RESEARCH_PR_TOKEN must fail the job before that merge, and PRs that change
workflow files must be skipped rather than merged by a PAT that lacks the
Workflows permission.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
WORKFLOW_PATH = REPO_ROOT / ".github" / "workflows" / "automerge.yml"
TOKEN_SECRET = "${{ secrets.RESEARCH_PR_TOKEN }}"
GITHUB_TOKEN_SECRET = "${{ secrets.GITHUB_TOKEN }}"


def _workflow() -> dict[str, Any]:
    loaded = yaml.safe_load(WORKFLOW_PATH.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded


def _on_block(workflow: dict[str, Any]) -> dict[str, Any]:
    # PyYAML 1.1 treats the GitHub `on:` key as boolean True.
    on_block = workflow.get("on", workflow.get(True))
    assert isinstance(on_block, dict)
    return on_block


def _enable_job(workflow: dict[str, Any]) -> dict[str, Any]:
    job = workflow["jobs"]["enable"]
    assert isinstance(job, dict)
    return job


def _steps() -> list[dict[str, Any]]:
    steps = _enable_job(_workflow())["steps"]
    assert isinstance(steps, list)
    return steps


def _merge_index(steps: list[dict[str, Any]]) -> int:
    for index, step in enumerate(steps):
        script = step.get("run")
        if isinstance(script, str) and "gh pr merge" in script:
            return index
    raise AssertionError("gh pr merge step is missing")


def _is_token_guard(step: dict[str, Any]) -> bool:
    script = step.get("run")
    if not isinstance(script, str):
        return False
    env = step.get("env") or {}
    if env.get("RESEARCH_PR_TOKEN") != TOKEN_SECRET:
        return False
    empty = "-z" in script and "RESEARCH_PR_TOKEN" in script
    fails = "exit 1" in script
    return empty and fails


def _is_workflow_files_skip(step: dict[str, Any]) -> bool:
    script = step.get("run")
    if not isinstance(script, str):
        return False
    lists_files = "/pulls/" in script and "/files" in script
    checks_workflows = ".github/workflows/" in script
    logs_skip = "Skipping auto-merge" in script
    uses_title = "pull_request.title" in script
    return lists_files and checks_workflows and logs_skip and not uses_title


def test_merge_step_uses_research_pr_token_not_github_token() -> None:
    steps = _steps()
    step = steps[_merge_index(steps)]
    env = step.get("env") or {}
    script = step.get("run")
    assert env.get("GH_TOKEN") == TOKEN_SECRET
    assert GITHUB_TOKEN_SECRET not in env.values()
    assert isinstance(script, str)
    assert "gh pr merge --auto --squash" in script
    assert "GITHUB_TOKEN" not in script


def test_empty_token_guard_runs_before_merge() -> None:
    steps = _steps()
    merge_index = _merge_index(steps)
    guard_indexes = [index for index, step in enumerate(steps) if _is_token_guard(step)]
    assert guard_indexes, "missing RESEARCH_PR_TOKEN empty-secret guard step"
    assert guard_indexes[0] < merge_index


def test_workflow_file_changes_are_skipped_via_files_api() -> None:
    steps = _steps()
    merge_index = _merge_index(steps)
    skip_indexes = [
        index for index, step in enumerate(steps) if _is_workflow_files_skip(step)
    ]
    assert skip_indexes, "missing workflow-files skip that checks the files API"
    skip_index = skip_indexes[0]
    assert skip_index < merge_index
    merge_if = steps[merge_index].get("if")
    assert isinstance(merge_if, str)
    assert "workflow_files.outputs.skip" in merge_if


def test_existing_automerge_conditions_are_unchanged() -> None:
    workflow = _workflow()
    on_block = _on_block(workflow)
    job = _enable_job(workflow)
    job_if = job["if"]
    types = on_block["pull_request"]["types"]

    assert job.get("name") == "Queue squash auto-merge"
    assert types == ["opened", "reopened", "ready_for_review", "synchronize"]
    assert "github.event.pull_request.draft == false" in job_if
    assert (
        "github.event.pull_request.head.repo.full_name == github.repository" in job_if
    )
    assert "github.head_ref != 'research/daily-models'" in job_if


# --- MODEL-44: only research/daily-models is excluded -----------------------
#
# The job `if` is evaluated for concrete pull requests rather than grepped, so a
# prefix rule that sneaks back in (startsWith, contains, ...) fails the test
# either by excluding a branch it must not or by being an unknown clause.

_CLAUSE_EQ = re.compile(r"^(?P<lhs>[\w.]+)\s*(?P<op>==|!=)\s*(?P<rhs>'[^']*'|[\w.]+)$")


def _lookup(path: str, context: dict[str, Any]) -> Any:
    value: Any = context
    for part in path.split("."):
        value = value[part]
    return value


def _operand(token: str, context: dict[str, Any]) -> Any:
    if token.startswith("'"):
        return token[1:-1]
    if token in ("true", "false"):
        return token == "true"
    return _lookup(token, context)


def _job_runs(job_if: str, context: dict[str, Any]) -> bool:
    """Evaluate a conjunction of ==/!= comparisons, the only form allowed."""
    clauses = [clause.strip() for clause in job_if.split("&&")]
    for clause in clauses:
        match = _CLAUSE_EQ.match(clause)
        assert match, f"unsupported clause in automerge job if: {clause!r}"
        lhs = _operand(match["lhs"], context)
        rhs = _operand(match["rhs"], context)
        if (lhs == rhs) != (match["op"] == "=="):
            return False
    return True


def _pr_context(head_ref: str) -> dict[str, Any]:
    repo = "turbobeest/modelspec"
    return {
        "github": {
            "repository": repo,
            "head_ref": head_ref,
            "event": {
                "pull_request": {
                    "draft": False,
                    "head": {"repo": {"full_name": repo}},
                }
            },
        }
    }


def test_job_if_has_no_research_prefix_rule() -> None:
    job_if = _enable_job(_workflow())["if"]
    assert "startsWith" not in job_if


def test_daily_research_branch_is_still_excluded() -> None:
    job_if = _enable_job(_workflow())["if"]
    assert _job_runs(job_if, _pr_context("research/daily-models")) is False


def test_other_research_branches_are_not_excluded() -> None:
    job_if = _enable_job(_workflow())["if"]
    for branch in (
        "research/seeder-known-identities",
        "research/daily-models-followup",
        "research/anything",
    ):
        assert _job_runs(job_if, _pr_context(branch)) is True, branch


def test_ordinary_agent_branch_still_runs() -> None:
    job_if = _enable_job(_workflow())["if"]
    assert _job_runs(job_if, _pr_context("ci/model-44-52-workflow-hygiene")) is True


def test_draft_and_fork_pull_requests_are_still_excluded() -> None:
    job_if = _enable_job(_workflow())["if"]
    draft = _pr_context("ci/some-branch")
    draft["github"]["event"]["pull_request"]["draft"] = True
    assert _job_runs(job_if, draft) is False

    fork = _pr_context("ci/some-branch")
    fork["github"]["event"]["pull_request"]["head"]["repo"]["full_name"] = "someone/fork"
    assert _job_runs(job_if, fork) is False
