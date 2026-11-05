"""``python -m scripts.slo``: the daily coverage report and its alerts (MODEL-215).

``report`` measures every target and writes ``coverage.json``, ``index.html``
and ``summary.md``. A breach is not a failure of this command: the report
states it, and ``alert`` raises it. ``alert`` prints the issue changes it
would make, and makes them only with ``--apply``.

``workflows`` measures only ``workflow-health``: every scheduled workflow in
both repositories, its newest run on main, and whether it is red. It exits 1
when any is red or unreadable, so it doubles as a quick health check. Its
output is public-safe: a private repository appears only as counts. Inside
that repository's own run, ``--repo R --private-detail --issue`` names each
red workflow and its run, and keeps one issue there (MODEL-421). ``--quiet``
prints nothing and answers only by exit status: the public coverage workflow's
``private-health`` job, which holds the private token, runs it that way.

``--stage-breach TARGET`` adds a labelled synthetic finding to a target, and
``alert --now`` moves the clock, so the whole alert path can be proven on
GitHub without waiting for a real breach.
"""

from __future__ import annotations

import argparse
import contextlib
import io
import json
import os
import sys
from dataclasses import replace
from datetime import date, datetime
from pathlib import Path

from scripts.slo import alerts, health_issue, render
from scripts.slo.report import (
    RELEASE_STAGES,
    Finding,
    check_workflows,
    gh_cli,
    load_config,
    measure,
    now_utc,
    public_release_report,
    read_repo,
    read_workflow_health,
    release_report,
    report_from_json,
    settle,
)

ROOT = Path(__file__).resolve().parents[2]
STAGED = Finding("staged-breach", "a synthetic finding that proves the alert path "
                                  "(MODEL-215); not a real breach")
DATA_REPO = "turbobeest/modelspec-data"


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


def _self_key() -> str | None:
    """The workflow running this command, from ``GITHUB_WORKFLOW_REF``.

    It is left out of its own check: its newest completed run is yesterday's,
    which failed only because something else was red.
    """
    ref = os.environ.get("GITHUB_WORKFLOW_REF", "").split("@", 1)[0]
    parts = ref.split("/")
    if len(parts) >= 5 and parts[2:4] == [".github", "workflows"]:
        return f"{parts[1]}/{parts[-1]}"
    return None


def cmd_workflows(args: argparse.Namespace) -> int:
    if not args.quiet:
        return _workflows(args)
    # The pass/fail check inside a public job that holds the private token:
    # print nothing at all, not even a traceback, and answer by exit status.
    try:
        with contextlib.redirect_stdout(io.StringIO()):
            return _workflows(args)
    except Exception:  # noqa: BLE001 - a crash must not print private detail
        return 2


def _workflows(args: argparse.Namespace) -> int:
    config = load_config()
    if args.repo:
        unknown = set(args.repo) - {r.repo for r in config.workflow_repos}
        if unknown:
            sys.exit(f"--repo: not a watched repository: {sorted(unknown)}")
        config = replace(
            config,
            workflow_repos=tuple(r for r in config.workflow_repos if r.repo in args.repo),
            unscheduled=tuple(w for w in config.unscheduled if w.repo in args.repo))
    scope = {r.repo for r in config.workflow_repos}
    private = config.private_repos
    if args.issue and not args.private_detail:
        sys.exit("--issue files private detail; it needs --private-detail")
    if args.private_detail:
        # Put the limit in code: the detail of a private repository is printed
        # only inside that repository's own run, where the log is private too.
        here = os.environ.get("GITHUB_REPOSITORY")
        if not scope <= private:
            sys.exit("--private-detail needs --repo naming only private repositories")
        if here is not None and here not in scope:
            sys.exit(f"--private-detail refused in {here}: the detail may only be "
                     "printed in the repository it describes")
        private = frozenset()
    now = _now(args.now)
    watched, errors, runs = read_workflow_health(
        ROOT, config, dirs=_dirs(args.workflow_dir), skip=_self_key())
    result = settle(config.target("workflow-health"),
                    check_workflows(runs, watched, now, errors, private))
    shown = [w for w in watched if w.repo not in private]
    red = {f.subject for f in result.findings}
    print(f"workflow-health: {result.status.upper()} ({len(watched)} workflows, "
          f"{len(result.findings)} red finding(s), {len(result.errors)} error(s)) "
          f"at {now.isoformat()}")
    for w in shown:
        every = f"every {w.cadence_hours:g} h" if w.cadence_hours else "unscheduled"
        print(f"  {'RED  ' if w.key in red else 'green'} {w.key} ({every})")
    for repo in sorted(private & scope):
        n = sum(w.repo == repo for w in watched)
        print(f"  {repo.split('/')[-1]}: {n} scheduled workflow(s), private; counts only")
    for f in result.findings:
        print(f"- {f.subject}: {f.detail}")
    for e in result.errors:
        print(f"- error: {e}")
    if args.issue:
        (repo,) = scope
        for a in health_issue.sync(result, gh_cli, repo, now, _run_url()):
            print(f"issue: {a.kind} {'#' + str(a.issue) if a.issue else a.title}")
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
    if args.release_report:
        try:
            releases = public_release_report(
                json.loads(Path(args.release_report).read_text(encoding="utf-8")), config, now=now)
        except (ValueError, OSError):
            sys.exit("release counts could not be read or are not current")
        by_id = {r.target: r for r in releases.results}
        report = replace(report, results=tuple(by_id.get(r.target, r) for r in report.results),
                         release_coverage=releases.release_coverage)
    render.write(report, Path(args.out), config.report_url)
    print(render.markdown(report, config.report_url))
    return 0


def cmd_alert(args: argparse.Namespace) -> int:
    config = load_config()
    report = report_from_json(json.loads(Path(args.report).read_text(encoding="utf-8")))
    repo = "turbobeest/modelspec"
    coverage = report.release_coverage
    if coverage and not coverage["counts_only"]:
        _private_release_context()
        if coverage.get("repository") != DATA_REPO:
            sys.exit("private release report must name its private repository")
        repo = DATA_REPO
    if args.issues_json:
        if args.apply:
            sys.exit("--issues-json is for a dry run only; --apply must read current issues")
        issues = [alerts.Issue(int(r["number"]), r["title"], r["body"])
                  for r in json.loads(Path(args.issues_json).read_text(encoding="utf-8"))]
    else:
        issues = alerts.open_issues(gh_cli, config.issue_label, repo=repo)
    actions = alerts.plan(report, config, issues, _now(args.now), only=args.only or None)
    print(alerts.describe(actions))
    if args.apply:
        alerts.apply(actions, gh_cli, config.issue_label, repo=repo)
    return 0


def _private_release_context() -> None:
    here = os.environ.get("GITHUB_REPOSITORY")
    if here is not None and here != DATA_REPO:
        sys.exit("private release detail is refused outside the private repository's run")


def cmd_releases(args: argparse.Namespace) -> int:
    from scripts.slo.releases import read_release_history

    if args.private_detail:
        _private_release_context()
    if set(args.stage_breach) - set(RELEASE_STAGES):
        sys.exit("--stage-breach must name a release stage")
    config = load_config()
    if args.window_days:
        config = replace(config, targets=tuple(
            replace(t, params={**t.params, "window_days": args.window_days})
            if t.id in RELEASE_STAGES else t for t in config.targets))
    history = read_release_history(
        Path(args.data_dir), ref=args.ref,
        discovery_paths=tuple(Path(p) for p in args.discovery),
        snapshot_paths=tuple(Path(p) for p in args.snapshot))
    now = _now(args.now)
    report = release_report(history, config, now=now,
                            counts_only=not args.private_detail, last=args.last)
    if args.counts_out:
        from scripts.slo.release_counts import counts_payload

        counts = release_report(history, config, now=now, last=args.last)
        path = Path(args.counts_out)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(counts_payload(counts.to_json(), now=now)) + "\n",
                        encoding="utf-8")
    if args.private_detail:
        report = replace(report, release_coverage={**report.release_coverage,
                                                   "repository": DATA_REPO})
    if args.stage_breach:
        report = replace(report, results=tuple(
            replace(r, status="breach", findings=r.findings + (STAGED,), errors=(),
                    measured=r.measured or 1) if r.target in args.stage_breach else r
            for r in report.results))
    render.write(report, Path(args.out), config.report_url)
    print(render.markdown(report, config.report_url))
    return 0


def cmd_release_counts(args: argparse.Namespace) -> int:
    import httpx

    from scripts.slo.release_counts import fetch_counts, read_counts

    now = _now(args.now)
    if args.github_output:
        output = os.environ.get("GITHUB_OUTPUT")
        if not output:
            sys.exit("--github-output requires GITHUB_OUTPUT")
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            with httpx.Client(timeout=30) as client:
                data = fetch_counts(os.environ.get("MODELSPEC_DATA_TOKEN", ""), now=now,
                                    client=client)
        with Path(output).open("a", encoding="utf-8") as stream:
            stream.write("counts=" + json.dumps(data, separators=(",", ":")) + "\n")
    else:
        if not args.out:
            sys.exit("--from-env requires --out")
        data = read_counts(os.environ.get("PRIVATE_RELEASE_COUNTS", ""), now=now)
        Path(args.out).write_text(json.dumps(data) + "\n", encoding="utf-8")
    return 0


def _positive(value: str) -> int:
    number = int(value)
    if number <= 0:
        raise argparse.ArgumentTypeError("must be greater than zero")
    return number


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m scripts.slo", description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="command", required=True)
    rep = sub.add_parser("report", help="measure every target and write the report")
    rep.add_argument("--out", required=True, help="directory for the report files")
    rep.add_argument("--as-of", help="YYYY-MM-DD; default today (UTC)")
    rep.add_argument("--now", help="ISO time for workflow ages; default now (UTC)")
    rep.add_argument("--models-dev", help="read this models.dev payload instead of fetching")
    rep.add_argument("--release-report", help="today's counts-only coverage.json from `releases`")
    rep.add_argument("--stage-breach", action="append", default=[], metavar="TARGET")
    rep.add_argument("--workflow-dir", action="append", default=[], metavar="REPO=PATH",
                     help="read OWNER/REPO's workflow files from this checkout")
    rep.set_defaults(func=cmd_report)
    rel = sub.add_parser("releases", help="measure release stages from local main history")
    rel.add_argument("--data-dir", required=True,
                     help="local catalogue checkout, complete history")
    rel.add_argument("--ref", default="HEAD", help="main history tip in that checkout")
    rel.add_argument("--out", required=True)
    rel.add_argument("--counts-out", help="write a separate bounded counts-only JSON file")
    rel.add_argument("--now", help="ISO time; default now (UTC)")
    rel.add_argument("--last", type=_positive, help="limit to the newest N discoveries")
    rel.add_argument("--window-days", type=_positive,
                     help="override the rolling window for an audit")
    rel.add_argument("--discovery", action="append", default=[], metavar="PATH",
                     help="retained release-watch or signal artifact (repeatable)")
    rel.add_argument("--snapshot", action="append", default=[], metavar="PATH",
                     help="retained dated decision snapshot (repeatable)")
    rel.add_argument("--private-detail", action="store_true",
                     help="include names and timings; local or private repository runs only")
    rel.add_argument("--stage-breach", action="append", default=[], metavar="TARGET")
    rel.set_defaults(func=cmd_releases)
    counts = sub.add_parser("release-counts", help="transfer validated private release counts")
    source = counts.add_mutually_exclusive_group(required=True)
    source.add_argument("--github-output", action="store_true",
                        help="quietly fetch private counts and write the audited job output")
    source.add_argument("--from-env", action="store_true",
                        help="read the counts-only PRIVATE_RELEASE_COUNTS handoff")
    counts.add_argument("--out", help="file to write with --from-env")
    counts.add_argument("--now", help="ISO time; default now (UTC)")
    counts.set_defaults(func=cmd_release_counts)
    wf = sub.add_parser("workflows", help="measure only workflow-health and print it")
    wf.add_argument("--now", help="ISO time for workflow ages; default now (UTC)")
    wf.add_argument("--workflow-dir", action="append", default=[], metavar="REPO=PATH",
                    help="read OWNER/REPO's workflow files from this checkout")
    wf.add_argument("--repo", action="append", default=[], metavar="OWNER/REPO",
                    help="watch only this repository (repeatable)")
    wf.add_argument("--private-detail", action="store_true",
                    help="name a private repository's workflows and runs; refused "
                         "outside that repository's own Actions run")
    wf.add_argument("--quiet", action="store_true",
                    help="print nothing; exit 0 when every watched workflow is green")
    wf.add_argument("--issue", action="store_true",
                    help="with --private-detail, keep one workflow-health issue in "
                         "that repository")
    wf.set_defaults(func=cmd_workflows)
    al = sub.add_parser("alert", help="open, update, escalate and close breach issues")
    al.add_argument("--report", required=True, help="coverage.json from `report`")
    al.add_argument("--apply", action="store_true", help="make the changes on GitHub")
    al.add_argument("--issues-json", help="read an issue list for an offline dry run")
    al.add_argument("--now", help="ISO time for escalation; default now (UTC)")
    al.add_argument("--only", action="append", default=[], metavar="TARGET",
                    help="touch only these targets' issues")
    al.set_defaults(func=cmd_alert)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
