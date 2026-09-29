"""``python -m scripts.slo``: the daily coverage report and its alerts (MODEL-215).

``report`` measures every target and writes ``coverage.json``, ``index.html``
and ``summary.md``. A breach is not a failure of this command: the report
states it, and ``alert`` raises it. ``alert`` prints the issue changes it
would make, and makes them only with ``--apply``.

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
    gh_cli,
    load_config,
    measure,
    now_utc,
    read_repo,
    report_from_json,
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
    inputs = read_repo(ROOT, as_of, models_dev=models_dev)
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
    rep.set_defaults(func=cmd_report)
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
