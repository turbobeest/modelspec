"""One issue in a private repository that names its red workflows (MODEL-421).

The public coverage report shows a private repository only as counts. The
names, runs and reasons go here instead: one open issue labelled
``workflow-health`` in that repository, edited in place while anything is red
and closed with a comment once everything is green.
"""

from __future__ import annotations

from collections.abc import Sequence
from datetime import datetime

from scripts.slo.alerts import Action, Issue, open_issues
from scripts.slo.render import target_markdown
from scripts.slo.report import Gh, Result

LABEL = "workflow-health"
MARKER = "<!-- workflow-health MODEL-421 -->"
TITLE = "Scheduled workflows are red"


def body_for(result: Result, now: datetime, run_url: str | None) -> str:
    return "\n".join([
        MARKER,
        f"As of {now.isoformat()}, scheduled workflows in this repository are red or "
        "could not be read.",
        "",
        target_markdown(result, shown=100),
        f"Run: {run_url}" if run_url else "",
        "",
        "Written by `.github/workflows/workflow-health.yml` "
        "(`python -m scripts.slo workflows --private-detail --issue`). It closes "
        "itself when every scheduled workflow is green.",
    ]).rstrip() + "\n"


def plan(result: Result, issues: Sequence[Issue], now: datetime,
         run_url: str | None) -> list[Action]:
    ours = sorted((i for i in issues if MARKER in i.body), key=lambda i: i.number)
    actions: list[Action] = []
    for dup in ours[1:]:
        actions += [Action("comment", LABEL, dup.number, body=f"Duplicate of #{ours[0].number}."),
                    Action("close", LABEL, dup.number)]
    if result.status == "met":
        if ours:
            actions += [Action("comment", LABEL, ours[0].number,
                               body=f"Every scheduled workflow is green as of "
                                    f"{now.isoformat()}. Closing."),
                        Action("close", LABEL, ours[0].number)]
        return actions
    body = body_for(result, now, run_url)
    if not ours:
        actions.append(Action("create", LABEL, title=TITLE, body=body))
    elif _content(ours[0].body) != _content(body):
        actions.append(Action("edit", LABEL, ours[0].number, body=body))
    return actions


def _content(body: str) -> str:
    """The body without its timestamp line, so an unchanged state is no edit."""
    lines = body.replace("\r\n", "\n").strip().splitlines()
    return "\n".join(line for line in lines
                     if not line.startswith(("As of ", "Run: ")))


def sync(result: Result, gh: Gh, repo: str, now: datetime, run_url: str | None) -> list[Action]:
    actions = plan(result, open_issues(gh, LABEL, repo), now, run_url)
    if any(a.kind == "create" for a in actions):
        gh(["label", "create", LABEL, "--repo", repo, "--color", "B60205", "--force",
            "--description", "A scheduled workflow is red (MODEL-421)"])
    for a in actions:
        if a.kind == "create":
            gh(["issue", "create", "--repo", repo, "--title", a.title, "--label", LABEL,
                "--body-file", "-"], a.body)
        elif a.kind == "edit":
            gh(["issue", "edit", str(a.issue), "--repo", repo, "--body-file", "-"], a.body)
        elif a.kind == "comment":
            gh(["issue", "comment", str(a.issue), "--repo", repo, "--body-file", "-"], a.body)
        else:
            gh(["issue", "close", str(a.issue), "--repo", repo])
    return actions
