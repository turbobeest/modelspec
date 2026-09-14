"""Auto-merge must queue with RESEARCH_PR_TOKEN, not GITHUB_TOKEN.

GitHub does not start workflow runs for events caused by GITHUB_TOKEN, so a
merge attributed to github-actions[bot] never deploys. An empty
RESEARCH_PR_TOKEN must fail the job before that merge, and PRs that change
workflow files must be skipped rather than merged by a PAT that lacks the
Workflows permission.
"""

from __future__ import annotations

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
    assert "!startsWith(github.head_ref, 'research/')" in job_if
