"""The weekly coverage report must keep exactly one open issue (MODEL-52).

The old lookup updated the newest open "Weekly Coverage Report" issue and never
looked at the rest, so an older duplicate (#2) sat open for months. The script
now updates the newest match and closes every older open match with a comment
pointing at the one kept.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
WORKFLOW_PATH = REPO_ROOT / ".github" / "workflows" / "card-stats.yml"


def _workflow() -> dict[str, Any]:
    loaded = yaml.safe_load(WORKFLOW_PATH.read_text(encoding="utf-8"))
    assert isinstance(loaded, dict)
    return loaded


def _issue_script() -> str:
    steps = _workflow()["jobs"]["coverage"]["steps"]
    for step in steps:
        uses = step.get("uses", "")
        if isinstance(uses, str) and uses.startswith("actions/github-script@"):
            script = step["with"]["script"]
            assert isinstance(script, str)
            return script
    raise AssertionError("github-script step that manages the report issue is missing")


def _index(script: str, needle: str) -> int:
    position = script.find(needle)
    assert position >= 0, f"missing from issue script: {needle!r}"
    return position


def test_permissions_and_token_are_unchanged() -> None:
    workflow = _workflow()
    assert workflow["permissions"] == {"contents": "read", "issues": "write"}
    for step in workflow["jobs"]["coverage"]["steps"]:
        with_block = step.get("with") or {}
        assert "github-token" not in with_block
        assert "secrets." not in str(step.get("env") or {})


def test_lookup_collects_every_open_match_newest_first() -> None:
    script = _issue_script()
    assert "github.paginate(github.rest.issues.listForRepo" in script
    assert "state: 'open'" in script
    assert "labels: 'coverage-report'" in script
    assert "i.title === title" in script
    assert "!i.pull_request" in script
    assert "b.number - a.number" in script, "matches must be sorted newest first"
    assert "const [existing, ...extras] = matches;" in script
    assert "issues.find(" not in script, "single-match lookup leaves duplicates open"


def test_newest_match_is_updated_or_a_new_issue_created() -> None:
    script = _issue_script()
    assert "issue_number: existing.number" in script
    assert "keptNumber = existing.number" in script
    assert "github.rest.issues.create(" in script
    assert "keptNumber = newIssue.number" in script


def test_older_matches_are_commented_then_closed() -> None:
    script = _issue_script()
    loop = _index(script, "for (const extra of extras)")
    comment = _index(script, "github.rest.issues.createComment(")
    close = _index(script, "state: 'closed'")

    assert loop < comment < close, "comment must be posted before closing each extra"
    assert loop > _index(script, "keptNumber = newIssue.number"), (
        "extras are closed only after the kept issue number is known"
    )
    loop_body = script[loop:]
    assert "issue_number: extra.number" in loop_body
    assert "#${keptNumber}" in loop_body, "comment must point at the kept issue"
