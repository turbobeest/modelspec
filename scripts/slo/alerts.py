"""One GitHub issue per breached target, updated in place (MODEL-215).

Release stages keep one issue per target and release (MODEL-450). Counts-only
reports leave those issues to the private repository's detailed report.

Each issue carries a marker naming its target, when the breach began and
whether it has been escalated. A run edits the body only when it changed,
comments once with the ``notify`` mentions when a breach passes
``escalate_after_hours``, and closes the issue with a comment when the target
is met again. A target not in force never opens an issue.
"""

from __future__ import annotations

import json
import re
from collections.abc import Iterable, Sequence
from dataclasses import dataclass, replace
from datetime import datetime
from typing import Literal
from urllib.parse import quote, unquote

from scripts.slo.render import target_markdown
from scripts.slo.report import REPO, Config, Gh, Report, Result

MARKER = re.compile(
    r"<!-- coverage-slo target=(?P<target>[a-z0-9-]+) since=(?P<since>\S+) "
    r"escalated=(?P<escalated>[01])(?: release=(?P<release>\S+))? -->")
ALERTING = ("breach", "error")
RELEASE_TARGETS = frozenset({"release-card-lag", "release-price-lag",
                             "release-score-lag", "release-decidable-lag"})
ISSUE_LIMIT = 1000


@dataclass(frozen=True)
class Issue:
    number: int
    title: str
    body: str


@dataclass(frozen=True)
class Action:
    kind: Literal["create", "edit", "comment", "close"]
    target: str
    issue: int | None = None
    title: str = ""
    body: str = ""


def title_for(target: str, release: str | None = None) -> str:
    return f"Coverage SLO breach: {target}" + (f": {release}" if release else "")


def marker(target: str, since: datetime, escalated: bool,
           release: str | None = None) -> str:
    return (f"<!-- coverage-slo target={target} since={since.isoformat()} "
            f"escalated={int(escalated)}"
            + (f" release={quote(release, safe='')}" if release is not None else "") + " -->")


def body_for(r: Result, report: Report, config: Config, since: datetime,
             escalated: bool, release: str | None = None) -> str:
    what = "could not be measured" if r.status == "error" else "is in breach"
    return "\n".join([
        marker(r.target, since, escalated, release),
        f"Coverage target `{r.target}` {what} as of {report.as_of.isoformat()} "
        f"(since {since.isoformat()}).",
        "",
        target_markdown(r),
        f"Report: {config.report_url}#{r.target} · JSON: {config.report_url}coverage.json"
        + (f" · Run: {report.run_url}" if report.run_url else ""),
        "",
        "Targets: `docs/method/coverage-slo.md`. This issue is written by "
        "`.github/workflows/coverage-slo.yml`; it closes itself when the target is met.",
    ])


def plan(report: Report, config: Config, issues: Iterable[Issue], now: datetime,
         only: Sequence[str] | None = None) -> list[Action]:
    """The issue changes that bring GitHub in line with ``report``."""
    by_target: dict[tuple[str, str | None], list[tuple[Issue, datetime, bool]]] = {}
    for issue in sorted(issues, key=lambda i: i.number):
        m = MARKER.search(issue.body)
        if m:
            release = unquote(m["release"]) if m["release"] is not None else None
            by_target.setdefault((m["target"], release), []).append(
                (issue, datetime.fromisoformat(m["since"]), m["escalated"] == "1"))
    actions: list[Action] = []
    results: list[tuple[Result, str | None]] = []
    for r in report.results:
        if r.target not in RELEASE_TARGETS:
            results.append((r, None))
            continue
        if (report.release_coverage or {}).get("counts_only"):
            continue
        subjects = {f.subject for f in r.findings}
        previous = {release for target, release in by_target
                    if target == r.target and release is not None}
        for subject in sorted(subjects | previous):
            findings = tuple(sorted({f for f in r.findings if f.subject == subject},
                                    key=lambda f: f.detail))
            if not findings and r.status == "error":
                continue
            status = r.status
            if r.status in ALERTING:
                status = "breach" if findings else "met"
            results.append((replace(r, findings=findings, errors=(), status=status), subject))
        # An unreadable stage is a target-level error, never evidence that an
        # existing release breach has resolved. Retire its error issue only
        # after the stage can be measured again.
        if r.status == "error" or (r.target, None) in by_target:
            results.append((replace(r, findings=(), status=(
                "error" if r.status == "error" else "met")), None))
    for r, release in results:
        if only is not None and r.target not in only:
            continue
        existing = by_target.get((r.target, release), [])
        for dup, _, _ in existing[1:]:
            actions += [Action("comment", r.target, dup.number,
                               body=f"Duplicate of #{existing[0][0].number}; closing."),
                        Action("close", r.target, dup.number)]
        if r.status not in ALERTING:
            if existing:
                issue = existing[0][0]
                actions += [Action("comment", r.target, issue.number,
                                   body=f"Target `{r.target}` is {r.status.replace('_', ' ')} "
                                        f"as of {report.as_of.isoformat()}. Closing."),
                            Action("close", r.target, issue.number)]
            continue
        if not existing:
            actions.append(Action("create", r.target, title=title_for(r.target, release),
                                  body=body_for(r, report, config, now, False, release)))
            continue
        issue, since, escalated = existing[0]
        hours = (now - since).total_seconds() / 3600
        escalate = not escalated and hours >= config.escalate_after_hours
        body = body_for(r, report, config, since, escalated or escalate, release)
        if body.strip() != issue.body.replace("\r\n", "\n").strip():
            actions.append(Action("edit", r.target, issue.number, body=body))
        if escalate:
            who = " ".join(config.notify)
            actions.append(Action(
                "comment", r.target, issue.number,
                body=f"{who} coverage target `{r.target}` has been missed for "
                     f"{hours:.0f} hours (since {since.isoformat()}), past the "
                     f"{config.escalate_after_hours:.0f}-hour limit. "
                     f"Report: {config.report_url}#{r.target}"))
    return actions


def open_issues(gh: Gh, label: str, repo: str = REPO) -> list[Issue]:
    rows = json.loads(gh(["issue", "list", "--repo", repo, "--label", label, "--state",
                          "open", "--limit", str(ISSUE_LIMIT), "--json", "number,title,body"]))
    if len(rows) >= ISSUE_LIMIT:
        raise ValueError(f"issue listing reached its {ISSUE_LIMIT}-issue limit; "
                         "refusing to plan against a possibly incomplete listing")
    return [Issue(int(r["number"]), str(r["title"]), str(r["body"])) for r in rows]


def apply(actions: Sequence[Action], gh: Gh, label: str, repo: str = REPO) -> None:
    if any(a.kind == "create" for a in actions):
        gh(["label", "create", label, "--repo", repo, "--color", "B60205", "--force",
            "--description", "A coverage target is missed (MODEL-215)"])
    for a in actions:
        if a.kind == "create":
            gh(["issue", "create", "--repo", repo, "--title", a.title, "--label", label,
                "--body-file", "-"], a.body)
        elif a.kind == "edit":
            gh(["issue", "edit", str(a.issue), "--repo", repo, "--body-file", "-"], a.body)
        elif a.kind == "comment":
            gh(["issue", "comment", str(a.issue), "--repo", repo, "--body-file", "-"], a.body)
        else:
            gh(["issue", "close", str(a.issue), "--repo", repo])


def describe(actions: Sequence[Action]) -> str:
    if not actions:
        return "No issue changes."
    return "\n".join(f"{a.kind} {'#' + str(a.issue) if a.issue else a.title} ({a.target})"
                     for a in actions)
