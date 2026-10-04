"""Local subscription jobs and private report PRs. Dry runs never launch a CLI."""

from __future__ import annotations

import argparse
import fcntl
import json
import os
import shlex
import subprocess
import tempfile
import time
import uuid
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from fnmatch import fnmatchcase
from pathlib import Path

import yaml

from qa import agent_harness, tui_harness
from qa.docker.entrypoint import refuse_vendor_auth
from qa.providers import Budget, redact, redact_structure
from qa.tui_auth import authentication_status
from qa.tui_docker import GEMINI_RETIRED, container_command, passed_environment
from qa.tui_isolation import isolation_result, receipt_file
from qa.tui_homes import home_config, state_directory
from qa.tui_providers import CLIS, build_command, prepare_workspace

AGENT_NAMES = {"claude": "claude", "codex": "openai", "gemini": "gemini", "grok": "grok"}
TRAILER = "Co-Authored-By: GPT-6.1 Sol <noreply@openai.com>"
DEFAULT_STATE = Path.home() / "Library/Application Support/ModelSpec/subscription-jobs"
REPORT_PATHS = {"scenarios": "reports/agent-scenarios", "ux": "reports/ux", "aeo": "aeo/runs"}
REPOSITORIES = {"scenarios": "turbobeest/modelspec-data", "ux": "turbobeest/modelspec-data",
                "aeo": "turbobeest/modelspec-business"}


def configuration(state: Path, *, browser_clis=(), quiet_hours=False, max_runs=None) -> dict:
    refuse_vendor_auth(os.environ)
    if os.environ.get("GITHUB_ACTIONS"):
        raise ValueError("Subscription jobs run locally, never in GitHub Actions")
    config = yaml.safe_load((tui_harness.HERE / "tui_config.yaml").read_text())
    state = tui_harness.private_output(state)
    config["_state_dir"] = str(state / ".tui-state")
    config["_state_dirs"] = {cli: str(state / ".tui-state-ux") for cli in browser_clis}
    for cli in browser_clis:
        config["clis"][cli]["image_variant"] = "ux"
    config["_quiet_hours"] = quiet_hours
    config["_receipt_max_age_days"] = 30
    if max_runs is not None:
        config["max_runs_per_cli"] = max_runs
    tui_harness.validate_config(config)
    return config


def require_ready(config: dict, clis: list[str], output: Path, *, max_age_days=30, now=None) -> dict:
    """Check all receipts and logins before any task; each launch checks again."""
    refuse_vendor_auth(os.environ)
    tui_harness.quiet_hours_guard(config.get("_quiet_hours", False), False)
    now = now or datetime.now(timezone.utc)
    evidence = {}
    for cli in clis:
        if cli == "gemini":
            raise ValueError(f"gemini: {GEMINI_RETIRED}")
        path = receipt_file(state_directory(cli, config))
        if path.is_symlink():
            raise ValueError(f"{cli}: doctor receipt must not be a symlink")
        try:
            receipt = json.loads(path.read_text())
            certified = datetime.fromisoformat(receipt["certified_at"])
            if certified.tzinfo is None or not timedelta(0) <= now - certified <= timedelta(days=max_age_days):
                raise ValueError("stale receipt")
        except (OSError, KeyError, TypeError, ValueError) as exc:
            raise ValueError(f"{cli}: missing or stale doctor receipt; rerun doctor after manual login") from exc
        info = isolation_result(cli, config)
        if not info["verified"]:
            raise ValueError(info["reason"])
        evidence[cli] = info
    for cli in clis:
        with tempfile.TemporaryDirectory(prefix=f"job-auth-{cli}-", dir=output) as d:
            workspace = Path(d)
            prepare_workspace(cli, config, workspace, mcp_enabled=False)
            auth = authentication_status(cli, config, workspace, passed_environment(config))
        if not auth.get("verified") or auth.get("logged_in") is not True:
            raise ValueError(f"{cli}: native subscription login required; no task started")
    return evidence


def preview(cli: str, config: dict, workspace: Path, prompt: str, *, purpose="scenario") -> list[str]:
    mcp = workspace / "modelspec-mcp.json"
    mcp.write_text(home_config(cli, config, enabled=purpose in ("scenario", "browser")))
    command = build_command(cli, config["clis"][cli], workspace, prompt, mcp,
                            config["turn_cap"], purpose=purpose)
    # The preview uses the command builder but never consults Docker.
    argv = container_command(cli, config, workspace, command, passed_environment(config), preview=True)
    print(shlex.join(argv[:-1]) + " '<private prompt>'")
    return argv


def write_pair(directory: Path, day: str, report: dict, markdown: str) -> None:
    directory = tui_harness.private_output(directory)
    directory.mkdir(parents=True, exist_ok=True)
    for suffix, content in (("json", json.dumps(redact_structure(report), indent=2) + "\n"),
                            ("md", redact(markdown))):
        path = directory / f"{day}.{suffix}"
        if path.is_symlink():
            raise ValueError("Report files must not be symlinks")
        path.write_text(content, encoding="utf-8")


def scenario_report(config, selected, scenarios, output, *, day, dry_run=False):
    needed = list(dict.fromkeys(selected + [tui_harness.judge_for(c, config["judges"]) for c in selected]))
    isolation = {} if dry_run else require_ready(config, needed, output)
    runner = tui_harness.Runner(config, output, isolation)
    rows = []
    for scenario in scenarios:
        for cli in selected:
            if dry_run:
                with tempfile.TemporaryDirectory(dir=output) as d:
                    preview(cli, config, Path(d), tui_harness.scenario_prompt(scenario))
                    judge = tui_harness.judge_for(cli, config["judges"])
                    preview(judge, config, Path(d), "Cross-family rubric judge", purpose="judge")
                row = tui_harness.empty_row(scenario, cli, config, "dry_run")
            else:
                row = runner.scenario(scenario, cli)
            row.update(agent=AGENT_NAMES[cli], cli=cli, agent_status=row["status"],
                       estimated_cost_usd=0.0, billing_calls=[], judges=[])
            if row["judge"]:
                opinion = {**row["judge"], "mode": "live", "strategy": "single", "agreed": True}
                row.update(judge=opinion, judges=[opinion])
            for call in row["model_calls"]:
                call["reported_cost_usd"] = call["cost_usd"]
                call["cost_usd"] = 0.0
            rows.append(row)
    metadata = {"agents": {AGENT_NAMES[c]: config["clis"][c] for c in selected},
                "judge": {"mode": "single", "routes": config["judges"]},
                "transport": "subscription-cli", "auth": "CLI subscription",
                "source_hashes": agent_harness.source_hashes(), "cli_invocations": runner.counts,
                "engine_sha": git_command(tui_harness.ROOT, "rev-parse", "HEAD"),
                "max_runs_per_cli": config["max_runs_per_cli"], "isolation": isolation}
    report = agent_harness.make_report(rows, scenarios, dry_run, Budget(0), day, metadata)
    report["partial"] = any(
        row["status"] == "quiet_hours" or row.get("judge_execution", {}).get("status") == "quiet_hours"
        for row in rows
    )
    report["evidence_note"] = (
        "Subscription CLI agents and separate cross-family CLI judges over ModelSpec MCP. "
        "API-shaped aggregates and unordered recall scoring are unchanged. Vendor API spend is zero; "
        "reported token-equivalent costs are separate. Unknown latency stays unknown. "
        + ("Dry-run command previews contain no measured results." if dry_run else "Measured subscription run.")
    )
    return report


def git_command(repository: Path, *args: str) -> str:
    result = subprocess.run(["git", "-C", str(repository), *args], text=True,
                            capture_output=True, check=True)
    return result.stdout.strip()


def scenario_summary(report: dict) -> str:
    header = "# Agent scenarios" + (" (partial: quiet_hours)" if report.get("partial") else "")
    lines = [header, "", "Vendor API spend: $0.00. Subscription CLI run.", "",
             "| Group | Success | Mean calls | API p50 ms | API p95 ms |",
             "| --- | ---: | ---: | ---: | ---: |"]
    for name, metrics in {"Overall": report["overall"], **report["per_family"], **report["per_agent"]}.items():
        numbers = [metrics["success_rate"], metrics["mean_tool_calls"], metrics["api_latency_p50_ms"], metrics["api_latency_p95_ms"]]
        formatted = ["n/a" if n is None else f"{n * 100:.1f}%" if i == 0 else f"{n:.2f}" for i, n in enumerate(numbers)]
        lines.append("| " + name + " | " + " | ".join(formatted) + " |")
    return "\n".join(lines) + "\n"


def decide_health(report: dict) -> dict:
    """Count decide answers the key could not fund or did not authorise."""
    counts = {"decide_answers": 0, "credits_exhausted": 0, "partial": 0, "unauthorised": 0}
    for run in report["runs"]:
        for call in run.get("tool_calls") or []:
            response = report["tool_responses"].get(call.get("response_ref"))
            if call.get("name") != "decide" or not response:
                continue
            for block in response.get("content") or []:
                try:
                    envelope = json.loads(block.get("text", ""))
                except (ValueError, TypeError, AttributeError):
                    continue
                if not isinstance(envelope, dict) or not isinstance(envelope.get("body"), dict):
                    continue
                body = envelope["body"]
                counts["decide_answers"] += 1
                counts["unauthorised"] += envelope.get("status") in (401, 402, 403)
                counts["credits_exhausted"] += (body.get("credits") or {}).get("exhausted") is True
                counts["partial"] += body.get("status") == "partial"
    return counts


def require_funded_key(report: dict) -> dict:
    """A keyed run whose decides were refused or unfunded measures the key, not the agents."""
    health = decide_health(report)
    if health["credits_exhausted"] or health["unauthorised"]:
        raise ValueError(
            f"ModelSpec key unusable: {health['credits_exhausted']} credits.exhausted and "
            f"{health['unauthorised']} unauthorised of {health['decide_answers']} decide answers. "
            "Report kept locally, not published; fix the key and rerun."
        )
    return health


@contextmanager
def report_worktree(repository: Path, job: str, day: str, root: Path):
    """Keep a failed publication for recovery; never switch the caller's branch."""
    repository = repository.expanduser().resolve()
    expected = REPOSITORIES[job]
    remote = git_command(repository, "remote", "get-url", "origin")
    if not remote.endswith((expected + ".git", expected)):
        raise ValueError(f"Expected the private {expected} origin")
    branch = f"{'aeo/visibility' if job == 'aeo' else 'qa/ux-report' if job == 'ux' else 'data/agent-scenarios'}-{day}-{uuid.uuid4().hex[:8]}"
    destination = root / (job + "-" + uuid.uuid4().hex[:8])
    git_command(repository, "fetch", "origin", "main")
    git_command(repository, "worktree", "add", "-b", branch, str(destination), "origin/main")
    try:
        yield destination, branch
    except BaseException:
        print(f"Publication incomplete; private worktree retained at {destination} on {branch}")
        raise
    else:
        git_command(repository, "worktree", "remove", str(destination))


def publish(worktree: Path, job: str, branch: str, day: str, body: str) -> str:
    title = f"{'AEO visibility run' if job == 'aeo' else 'qa: private decide UX report' if job == 'ux' else 'data: agent scenario report'} {day} (MODEL-309)"
    git_command(worktree, "add", "--", REPORT_PATHS[job])
    git_command(worktree, "commit", "--signoff", "-m", title + "\n\n" + TRAILER)
    git_command(worktree, "push", "-u", "origin", branch)
    with tempfile.TemporaryDirectory(prefix="job-pr-body-") as d:
        path = Path(d) / "body.md"
        path.write_text(body, encoding="utf-8")
        result = subprocess.run(["gh", "pr", "create", "--repo", REPOSITORIES[job], "--base", "main",
                                 "--head", branch, "--title", title, "--body-file", str(path)],
                                cwd=worktree, capture_output=True, text=True, check=True)
    return result.stdout.strip()


@contextmanager
def job_lock(state: Path, *, timeout=6 * 60 * 60, poll_interval=5 * 60):
    state.mkdir(parents=True, exist_ok=True, mode=0o700)
    path = state / "subscription-jobs.lock"
    if path.is_symlink():
        raise ValueError("Job lock must not be a symlink")
    with path.open("a") as lock:
        started = time.monotonic()
        waiting = False
        while True:
            try:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except BlockingIOError as exc:
                elapsed = time.monotonic() - started
                remaining = timeout - elapsed
                if remaining <= 0:
                    raise ValueError(f"Timed out after {timeout}s waiting for the subscription job lock") from exc
                delay = min(poll_interval, remaining)
                print(f"Another subscription job is running; waiting {delay:.0f}s for the lock "
                      f"({elapsed:.0f}s elapsed, {remaining:.0f}s remaining)", flush=True)
                waiting = True
                time.sleep(delay)
        if waiting:
            print(f"Subscription job lock acquired after {time.monotonic() - started:.0f}s", flush=True)
        yield


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("job", choices=REPORT_PATHS)
    parser.add_argument("--data-repo", type=Path, default=Path.home() / "dev/modelspec-data")
    parser.add_argument("--business-repo", type=Path, default=Path.home() / "dev/modelspec-business")
    parser.add_argument("--state-dir", type=Path, default=DEFAULT_STATE,
                        help="The same private --out used for doctor")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--scheduled", action="store_true", help="Always enforces quiet hours")
    parser.add_argument("--quiet-hours", action="store_true")
    parser.add_argument("--cli", choices=CLIS, action="append")
    parser.add_argument("--scenario", action="append", help="Scenario ID glob; repeatable")
    parser.add_argument("--max-runs-per-cli", type=int)
    parser.add_argument("--date", default=datetime.now(timezone.utc).date().isoformat())
    parser.add_argument("--base-url", default="https://modelspec.dev/decide/")
    args = parser.parse_args(argv)
    try:
        datetime.strptime(args.date, "%Y-%m-%d")
        # Gemini CLI no longer serves Google AI Pro; see GEMINI_RETIRED.
        scenario_clis = tuple(cli for cli in CLIS if cli != "gemini")
        selected = list(dict.fromkeys(args.cli or (("codex", "grok") if args.job == "ux" else scenario_clis)))
        config = configuration(args.state_dir, browser_clis=selected if args.job == "ux" else (),
                               quiet_hours=args.scheduled or args.quiet_hours,
                               max_runs=args.max_runs_per_cli if args.max_runs_per_cli is not None else {"scenarios": 400, "ux": 40, "aeo": 64}[args.job])
        state = tui_harness.private_output(args.state_dir)
        with job_lock(state):
            if not args.dry_run:
                needed = list(dict.fromkeys(selected + [config["judges"][c] for c in selected])) if args.job != "aeo" else selected
                require_ready(config, needed, state)
            repository = args.business_repo if args.job == "aeo" else args.data_repo

            def execute(tree):
                output = tree / REPORT_PATHS[args.job]
                output.mkdir(parents=True, exist_ok=True)
                if args.job == "scenarios":
                    scenarios = [s for s in agent_harness.load_scenarios() if not args.scenario or any(fnmatchcase(s["id"], p) for p in args.scenario)]
                    if not scenarios:
                        raise ValueError("Scenario filter matched nothing")
                    report = scenario_report(config, selected, scenarios, state, day=args.date, dry_run=args.dry_run)
                    write_pair(output, args.date, report, agent_harness.markdown(report))
                    if not args.dry_run and os.environ.get(config.get("mcp_token_env") or ""):
                        health = require_funded_key(report)
                        print("Decide answers: {decide_answers}; partial (wide intervals or "
                              "coverage): {partial}; credits exhausted: 0.".format(**health))
                    return scenario_summary(report)
                if args.job == "ux":
                    from qa.subscription_ux import run
                    return run(tree if not args.dry_run else repository, output, state, config, selected, args.base_url, args.date, dry_run=args.dry_run)
                from qa.subscription_aeo import run
                return run(tree / "aeo/prompts.yaml", tree / "aeo/engines.yaml", output, state, config, args.date, dry_run=args.dry_run, clis=selected)

            if args.dry_run:
                tree = state / "dry-run" / args.job
                tree.mkdir(parents=True, exist_ok=True)
                if args.job == "aeo":
                    # Only inventory/config are read from the private checkout; nothing is mutated there.
                    from qa.subscription_aeo import run
                    run(repository / "aeo/prompts.yaml", repository / "aeo/engines.yaml", tree / "aeo/runs", state, config, args.date, dry_run=True, clis=selected)
                else:
                    execute(tree)
                print(f"Dry-run reports: {tree}. No CLI, git mutation, or PR call.")
            else:
                with report_worktree(repository, args.job, args.date, state) as (tree, branch):
                    body = execute(tree)
                    print(publish(tree, args.job, branch, args.date, body))
        return 0
    except (ValueError, OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired) as exc:
        print(f"Subscription job refused/failed: {redact(str(exc))}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
