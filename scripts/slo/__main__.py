"""``python -m scripts.slo``: the daily coverage report and its alerts (MODEL-215).

``report`` measures every target and writes ``coverage.json``, ``index.html``
and ``summary.md``. A breach is not a failure of this command: the report
states it, and ``alert`` raises it. ``alert`` prints the issue changes it
would make, and makes them only with ``--apply``.

``workflows`` measures only ``workflow-health``: every scheduled workflow in
both repositories, its newest run on main, and whether it is red. It exits 1
when any is red or unreadable, so it doubles as a quick health check.

``--stage-breach TARGET`` adds a labelled synthetic finding to a target, and
``alert --now`` moves the clock, so the whole alert path can be proven on
GitHub without waiting for a real breach.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import date, datetime
from pathlib import Path

from scripts.slo import alerts, render
from scripts.slo.report import (
    Finding,
    check_workflows,
    gh_cli,
    load_config,
    measure,
    now_utc,
    read_repo,
    read_workflow_health,
    report_from_json,
    settle,
)

ROOT = Path(__file__).resolve().parents[2]
STAGED = Finding("staged-breach", "a synthetic finding that proves the alert path "
                                  "(MODEL-215); not a real breach")


def _now(value: str | None) -> datetime:
    return datetime.fromisoformat(value) if value else now_utc()


def _run_url() -> str | None:
    server, repo, run = (os.environ.get(k) for k in
                         ("GITHUB_SERVER_URL", "GITHUB_REPOSITORY", "GITHUB_RUN_ID"))
    return f"{server}/{repo}/actions/runs/{run}" if server and repo and run else None


def _dirs(values: list[str]) -> dict[str, Path]:
    out = {}
    for value in values:
        repo, sep, path = value.partition("=")
        if not sep:
            sys.exit(f"--workflow-dir wants OWNER/REPO=PATH, not {value!r}")
        out[repo] = Path(path)
    return out


def cmd_workflows(args: argparse.Namespace) -> int:
    config = load_config()
    now = _now(args.now)
    watched, errors, runs = read_workflow_health(ROOT, config, dirs=_dirs(args.workflow_dir))
    result = settle(config.target("workflow-health"),
                    check_workflows(runs, watched, now, errors))
    red = {f.subject for f in result.findings}
    print(f"workflow-health: {result.status.upper()} ({len(watched)} workflows, "
          f"{len(red)} red, {len(result.errors)} unreadable) at {now.isoformat()}")
    for w in watched:
        every = f"every {w.cadence_hours:g} h" if w.cadence_hours else "unscheduled"
        print(f"  {'RED  ' if w.key in red else 'green'} {w.key} ({every})")
    for f in result.findings:
        print(f"- {f.subject}: {f.detail}")
    for e in result.errors:
        print(f"- error: {e}")
    return 0 if result.status == "met" else 1


def cmd_report(args: argparse.Namespace) -> int:
    config = load_config()
    now = _now(args.now)
    as_of = date.fromisoformat(args.as_of) if args.as_of else now.date()
    unknown = set(args.stage_breach) - {t.id for t in config.targets}
    if unknown:
        sys.exit(f"--stage-breach: unknown target(s) {sorted(unknown)}")
    models_dev = None
    if args.models_dev:
        models_dev = (json.loads(Path(args.models_dev).read_text(encoding="utf-8")), None)
    inputs = read_repo(ROOT, as_of, models_dev=models_dev,
                       workflow_dirs=_dirs(args.workflow_dir))
    inputs.extra_findings = {t: (STAGED,) for t in args.stage_breach}
    report = measure(inputs, config, as_of=as_of, now=now,
                     commit=os.environ.get("GITHUB_SHA"), run_url=_run_url())
    render.write(report, Path(args.out), config.report_url)
    print(render.markdown(report, config.report_url))
    return 0


def cmd_alert(args: argparse.Namespace) -> int:
    config = load_config()
    report = report_from_json(json.loads(Path(args.report).read_text(encoding="utf-8")))
    issues = alerts.open_issues(gh_cli, config.issue_label)
    actions = alerts.plan(report, config, issues, _now(args.now), only=args.only or None)
    print(alerts.describe(actions))
    if args.apply:
        alerts.apply(actions, gh_cli, config.issue_label)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m scripts.slo", description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    rep = sub.add_parser("report", help="measure every target and write the report")
    rep.add_argument("--out", required=True, help="directory for the report files")
    rep.add_argument("--as-of", help="YYYY-MM-DD; default today (UTC)")
    rep.add_argument("--now", help="ISO time for workflow ages; default now (UTC)")
    rep.add_argument("--models-dev", help="read this models.dev payload instead of fetching")
    rep.add_argument("--stage-breach", action="append", default=[], metavar="TARGET")
    rep.add_argument("--workflow-dir", action="append", default=[], metavar="REPO=PATH",
                     help="read OWNER/REPO's workflow files from this checkout")
    rep.set_defaults(func=cmd_report)
    wf = sub.add_parser("workflows", help="measure only workflow-health and print it")
    wf.add_argument("--now", help="ISO time for workflow ages; default now (UTC)")
    wf.add_argument("--workflow-dir", action="append", default=[], metavar="REPO=PATH",
                    help="read OWNER/REPO's workflow files from this checkout")
    wf.set_defaults(func=cmd_workflows)
    al = sub.add_parser("alert", help="open, update, escalate and close breach issues")
    al.add_argument("--report", required=True, help="coverage.json from `report`")
    al.add_argument("--apply", action="store_true", help="make the changes on GitHub")
    al.add_argument("--now", help="ISO time for escalation; default now (UTC)")
    al.add_argument("--only", action="append", default=[], metavar="TARGET",
                    help="touch only these targets' issues")
    al.set_defaults(func=cmd_alert)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
