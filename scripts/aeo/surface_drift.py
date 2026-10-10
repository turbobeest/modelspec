"""Maintain one GitHub issue for the weekly surface lint (MODEL-255)."""

from __future__ import annotations

import argparse
import json
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from pipeline.surface_lint import Finding

TITLE = "AEO surface drift"
MAX_BODY = 60_000


@dataclass(frozen=True)
class Action:
    verb: str
    number: int | None = None
    body: str = ""


def issue_actions(report: dict[str, Any], issues: list[dict[str, Any]]) -> list[Action]:
    """Reuse the oldest matching issue, including after it has been closed."""
    matches = sorted(
        (issue for issue in issues if issue["title"] == TITLE), key=lambda issue: issue["number"]
    )
    findings = report["findings"]
    if not findings:
        return [Action("close", issue["number"]) for issue in matches if issue["state"] == "OPEN"]
    lines = [Finding(**finding).line() for finding in findings]
    body = (
        f"Surface lint found {len(lines)} findings at {report['origin']}.\n\n"
        + "```text\n"
        + "\n".join(lines)
        + "\n```\n"
    )
    if report.get("notices"):
        body += "\n" + "\n".join(report["notices"]) + "\n"
    if len(body) > MAX_BODY:
        trailer = "\n```\n\nReport truncated. The workflow log contains every finding.\n"
        body = body[: MAX_BODY - len(trailer)] + trailer
    if not matches:
        return [Action("create", body=body)]
    first, *duplicates = matches
    actions = [Action("close", issue["number"]) for issue in duplicates if issue["state"] == "OPEN"]
    if first["state"] != "OPEN":
        actions.append(Action("reopen", first["number"]))
    return [*actions, Action("edit", first["number"], body)]


def gh(arguments: list[str]) -> str:
    return subprocess.run(["gh", *arguments], check=True, capture_output=True, text=True).stdout


def sync(report: dict[str, Any], issues: list[dict[str, Any]], repo: str, *, dry_run: bool) -> None:
    for action in issue_actions(report, issues):
        print(
            f"{action.verb}: {repo}#{action.number}"
            if action.number
            else f"{action.verb}: {repo}, {TITLE}"
        )
        if dry_run:
            if action.body:
                print(action.body)
            continue
        arguments = ["issue", action.verb]
        if action.number:
            arguments.append(str(action.number))
        arguments.extend(["--repo", repo])
        if action.verb == "create":
            arguments.extend(["--title", TITLE])
        if action.body:
            # gh receives the exact multiline report; no shell interpolation.
            with tempfile.TemporaryDirectory(prefix="surface-drift-") as temporary:
                body = Path(temporary) / "body.md"
                body.write_text(action.body, encoding="utf-8")
                gh([*arguments, "--body-file", str(body)])
        else:
            gh(arguments)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument("--repo", required=True)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--issues", type=Path, help="saved gh issue list JSON for an offline dry-run"
    )
    args = parser.parse_args(argv)
    report = json.loads(args.report.read_text(encoding="utf-8"))
    if args.issues:
        if not args.dry_run:
            parser.error("--issues requires --dry-run")
        issues = json.loads(args.issues.read_text(encoding="utf-8"))
    else:
        issues = json.loads(
            gh(
                [
                    "issue",
                    "list",
                    "--repo",
                    args.repo,
                    "--state",
                    "all",
                    "--search",
                    TITLE + " in:title",
                    "--limit",
                    "100",
                    "--json",
                    "number,title,state",
                ]
            )
        )
    sync(report, issues, args.repo, dry_run=args.dry_run)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
