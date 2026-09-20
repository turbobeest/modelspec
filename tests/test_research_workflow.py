"""Daily research PRs must be opened with RESEARCH_PR_TOKEN, not GITHUB_TOKEN.

GitHub does not run workflows for pushes or pull requests made with
GITHUB_TOKEN, so required checks never report and those PRs stay blocked.
create-pull-request falls back to GITHUB_TOKEN when ``token`` is empty, so a
missing or expired secret must fail the job before that step runs.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
WORKFLOW_PATH = REPO_ROOT / ".github" / "workflows" / "daily-research.yml"
TOKEN_SECRET = "${{ secrets.RESEARCH_PR_TOKEN }}"
CREATE_PR_PREFIX = "peter-evans/create-pull-request@"


def _research_steps() -> list[dict[str, Any]]:
    workflow = yaml.safe_load(WORKFLOW_PATH.read_text(encoding="utf-8"))
    steps = workflow["jobs"]["research"]["steps"]
    assert isinstance(steps, list)
    return steps


def _create_pull_request_index(steps: list[dict[str, Any]]) -> int:
    for index, step in enumerate(steps):
        uses = step.get("uses") or ""
        if uses.startswith(CREATE_PR_PREFIX):
            return index
    raise AssertionError("create-pull-request step is missing")


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


def test_create_pull_request_uses_research_pr_token() -> None:
    steps = _research_steps()
    step = steps[_create_pull_request_index(steps)]
    assert (step.get("with") or {}).get("token") == TOKEN_SECRET


def test_research_pr_token_guard_runs_before_create_pull_request() -> None:
    steps = _research_steps()
    pr_index = _create_pull_request_index(steps)
    guard_indexes = [index for index, step in enumerate(steps) if _is_token_guard(step)]
    assert guard_indexes, "missing RESEARCH_PR_TOKEN empty-secret guard step"
    assert guard_indexes[0] < pr_index


def test_the_pull_request_commits_cards_and_nothing_else() -> None:
    """PR #106 carried survey.txt, validation.json and the attribution ledger
    because create-pull-request stages everything it finds. `add-paths` keeps
    the daily PR to the catalogue."""
    step = yaml.safe_load(WORKFLOW_PATH.read_text(encoding="utf-8"))
    steps = step["jobs"]["research"]["steps"]
    pr = next(s for s in steps if str(s.get("uses", "")).startswith("peter-evans/create-pull-request"))
    add_paths = [p for p in pr["with"]["add-paths"].split("\n") if p.strip()]
    assert add_paths == ["models/**"]
