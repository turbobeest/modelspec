"""Daily research runs in the private repository with its own GITHUB_TOKEN."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
WORKFLOW_PATH = REPO_ROOT / ".github" / "private-writers" / "daily-research.yml"
TOKEN_SECRET = "${{ secrets.GITHUB_TOKEN }}"
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


def test_create_pull_request_uses_private_repository_token() -> None:
    steps = _research_steps()
    step = steps[_create_pull_request_index(steps)]
    assert step["with"]["token"] == TOKEN_SECRET
    assert step["with"]["path"] == "data"


def test_private_checkout_precedes_writes_and_pull_request() -> None:
    steps = _research_steps()
    checkout = next(i for i, step in enumerate(steps)
                    if step.get("uses", "").startswith("actions/checkout")
                    and step.get("with", {}).get("path") == "data")
    prepare = next(i for i, step in enumerate(steps)
                   if "prepare_data_writer.py" in step.get("run", ""))
    write = next(i for i, step in enumerate(steps) if step.get("name") == "Write the new cards")
    assert checkout < prepare < write < _create_pull_request_index(steps)


def test_the_pull_request_commits_cards_and_nothing_else() -> None:
    """PR #106 carried survey.txt, validation.json and the attribution ledger
    because create-pull-request stages everything it finds. `add-paths` keeps
    the daily PR to the catalogue."""
    step = yaml.safe_load(WORKFLOW_PATH.read_text(encoding="utf-8"))
    steps = step["jobs"]["research"]["steps"]
    pr = next(s for s in steps if str(s.get("uses", "")).startswith("peter-evans/create-pull-request"))
    add_paths = [p for p in pr["with"]["add-paths"].split("\n") if p.strip()]
    assert add_paths == ["models/**"]
