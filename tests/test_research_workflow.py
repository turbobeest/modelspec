"""Daily research runs in the private repository with its own GITHUB_TOKEN."""

from __future__ import annotations

import os
import subprocess
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
    link_name = (
        "Link the data paths into the verified engine and put only the engine on the import path"
    )
    link = next(i for i, step in enumerate(steps) if step.get("name") == link_name)
    write = next(i for i, step in enumerate(steps) if step.get("name") == "Write the new cards")
    assert checkout < link < write < _create_pull_request_index(steps)


def test_the_pull_request_commits_cards_and_nothing_else() -> None:
    """PR #106 carried survey.txt, validation.json and the attribution ledger
    because create-pull-request stages everything it finds. `add-paths` keeps
    the daily PR to the catalogue."""
    step = yaml.safe_load(WORKFLOW_PATH.read_text(encoding="utf-8"))
    steps = step["jobs"]["research"]["steps"]
    pr = next(s for s in steps if str(s.get("uses", "")).startswith("peter-evans/create-pull-request"))
    add_paths = [p for p in pr["with"]["add-paths"].split("\n") if p.strip()]
    assert add_paths == ["models/**"]


SYNC_NAME = "Merge main into the open research branch, never force-push"
HEAD = "a" * 40
STUB_GH = """#!/usr/bin/env bash
printf '%s\\n' "$*" >> "$GH_LOG"
case "$*" in
  *"pulls?state=open"*) printf '%s' "$STUB_OPEN" ;;
  *"/compare/main..."*) printf '%s\\n' "$STUB_BEHIND" ;;
  *"-X PUT"*) exit "$STUB_PUT_EXIT" ;;
  "pr view"*) printf '%s\\n' "$STUB_HEAD_AFTER" ;;
  "pr comment"*) exit 0 ;;
  *) exit 99 ;;
esac
"""


def _workflow() -> dict[str, Any]:
    return yaml.safe_load(WORKFLOW_PATH.read_text(encoding="utf-8"))


def _run_sync(tmp_path: Path, *, open_prs: str, behind: str = "0",
              put_exit: int = 0) -> tuple[subprocess.CompletedProcess[str], list[str]]:
    step = next(s for s in _workflow()["jobs"]["sync"]["steps"] if s.get("name") == SYNC_NAME)
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    gh = bin_dir / "gh"
    gh.write_text(STUB_GH, encoding="utf-8")
    gh.chmod(0o755)
    log = tmp_path / "gh.log"
    log.touch()
    env = {
        **os.environ,
        **{key: value for key, value in step["env"].items() if "${{" not in value},
        "PATH": f"{bin_dir}{os.pathsep}{os.environ['PATH']}",
        "REPO": "owner/data",
        "OWNER": "owner",
        "GH_LOG": str(log),
        "STUB_OPEN": open_prs,
        "STUB_BEHIND": behind,
        "STUB_PUT_EXIT": str(put_exit),
        "STUB_HEAD_AFTER": "b" * 40,  # the head moves as soon as the update is requested
        "POLL_SECONDS": "0",
        "GITHUB_OUTPUT": str(tmp_path / "github-output"),
    }
    result = subprocess.run(["bash", "-c", step["run"]], env=env, capture_output=True,
                            text=True, check=False)
    return result, log.read_text(encoding="utf-8").splitlines()


def test_research_runs_on_its_schedule_and_the_sync_also_runs_on_every_push_to_main() -> None:
    workflow = _workflow()
    triggers = yaml.load(WORKFLOW_PATH.read_text(encoding="utf-8"), Loader=yaml.BaseLoader)["on"]
    assert triggers["push"] == {"branches": ["main"]}
    assert workflow["jobs"]["research"]["if"] == "github.event_name != 'push'"
    sync = workflow["jobs"]["sync"]
    assert sync["needs"] == "research"
    assert "github.event_name == 'push' && needs.research.result == 'skipped'" in sync["if"]
    assert sync["if"].startswith("${{ !cancelled() && !inputs.dry_run && ")
    assert "needs.research.result == 'success'" in sync["if"]
    assert sync["permissions"] == {"contents": "write", "pull-requests": "write"}
    assert "concurrency" not in workflow
    assert workflow["jobs"]["research"]["concurrency"] == {
        "group": "daily-research", "cancel-in-progress": False}
    assert sync["concurrency"] == {"group": "daily-research-sync", "cancel-in-progress": False}
    assert [s.get("uses") for s in sync["steps"]] == [None]
    assert sync["steps"][0]["env"]["BRANCH"] == "research/daily-models"


def test_sync_merges_main_into_a_branch_that_is_behind(tmp_path: Path) -> None:
    result, calls = _run_sync(tmp_path, open_prs=f"99 {HEAD}", behind="2")
    assert result.returncode == 0, result.stderr
    put = f"api -X PUT repos/owner/data/pulls/99/update-branch -f expected_head_sha={HEAD}"
    assert put in calls
    # The update is requested first; the head is then read (once, since the stub moves it at once).
    assert calls[-1] == "pr view 99 -R owner/data --json headRefOid --jq .headRefOid"
    assert calls.index(put) < calls.index(calls[-1])
    assert "Requested a merge of main into #99 (2 commits behind)." in result.stdout


def test_sync_names_the_open_branch_for_the_recall_dispatch_and_only_then(tmp_path: Path) -> None:
    result, _ = _run_sync(tmp_path, open_prs=f"99 {HEAD}", behind="0")
    assert result.returncode == 0, result.stderr
    assert (tmp_path / "github-output").read_text(encoding="utf-8") == "pr_branch=research/daily-models\n"
    quiet = tmp_path / "none"
    quiet.mkdir()
    result, _ = _run_sync(quiet, open_prs="")
    assert result.returncode == 0, result.stderr
    assert not (quiet / "github-output").exists() or (quiet / "github-output").read_text() == ""


def test_sync_leaves_an_up_to_date_branch_alone(tmp_path: Path) -> None:
    result, calls = _run_sync(tmp_path, open_prs=f"99 {HEAD}", behind="0")
    assert result.returncode == 0, result.stderr
    assert calls[-1] == f"api repos/owner/data/compare/main...{HEAD} --jq .behind_by"
    assert "#99 already contains main." in result.stdout


def test_sync_does_nothing_without_an_open_research_pull_request(tmp_path: Path) -> None:
    result, calls = _run_sync(tmp_path, open_prs="")
    assert result.returncode == 0, result.stderr
    assert len(calls) == 1
    assert "No open pull request from research/daily-models." in result.stdout


def test_sync_fails_loudly_when_main_does_not_merge(tmp_path: Path) -> None:
    result, calls = _run_sync(tmp_path, open_prs=f"99 {HEAD}", behind="3", put_exit=1)
    assert result.returncode == 1
    assert "::error::Could not merge main into research/daily-models (#99)." in result.stdout
    assert sum("-X PUT" in call for call in calls) == 1


def test_sync_refuses_to_choose_between_two_research_pull_requests(tmp_path: Path) -> None:
    result, calls = _run_sync(tmp_path, open_prs=f"99 {HEAD}\n100 {'b' * 40}", behind="1")
    assert result.returncode == 1
    assert "::error::More than one open pull request from research/daily-models." in result.stdout
    assert not any("-X PUT" in call for call in calls)
