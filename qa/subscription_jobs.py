"""Local subscription jobs and private report PRs. Dry runs never launch a CLI."""

from __future__ import annotations

import argparse
import fcntl
import hashlib
import json
import os
import re
import shlex
import subprocess
import tempfile
import time
import urllib.error
import urllib.request
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
API_HEALTH_URL = "https://api.modelspec.dev/v1/health"
INTERNET_PROBE_URL = "https://www.cloudflare.com/cdn-cgi/trace"
_TRANSPORT_SIGNATURES = (
    "ECONNRESET",
    "ECONNREFUSED",
    "ETIMEDOUT",
    "ENOTFOUND",
    "EAI_AGAIN",
    "ENETUNREACH",
    "EHOSTUNREACH",
    "getaddrinfo",
    "connection reset by peer",
    "connection refused",
    "network is unreachable",
    "socket hang up",
    "stream disconnected",
    "TLS handshake",
    "502 Bad Gateway",
    "503 Service Unavailable",
    "504 Gateway Timeout",
)
NETWORK_ERROR = re.compile(
    "|".join(rf"\b{re.escape(signature)}\b" for signature in _TRANSPORT_SIGNATURES),
    re.IGNORECASE,
)
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
    from qa.tui_providers import PROMPT_MARKER

    mcp = workspace / "modelspec-mcp.json"
    mcp.write_text(home_config(cli, config, enabled=purpose in ("scenario", "browser")))
    command = build_command(cli, config["clis"][cli], workspace, prompt, mcp,
                            config["turn_cap"], purpose=purpose)
    # The preview uses the command builder but never consults Docker.
    argv = container_command(cli, config, workspace, command, passed_environment(config), preview=True)
    # Gemini is the only preview whose argv still contains the prompt text.
    shown = [PROMPT_MARKER if part == prompt else part for part in argv] if cli == "gemini" else argv
    line = shlex.join(shown)
    if cli in ("claude", "codex"):
        line += " < " + shlex.quote(PROMPT_MARKER)
    print(line)
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


def modelspec_key_present(config: dict) -> bool:
    return bool(os.environ.get(config.get("mcp_token_env") or ""))


def _scenario_checkpoint(output: Path, selected, scenarios, day: str, engine_sha: str, *, config: dict) -> Path:
    digest = hashlib.sha256(json.dumps({
        "clis": selected,
        "scenarios": [scenario["id"] for scenario in scenarios],
        "engine_sha": engine_sha,
        "day": day,
        "modelspec_key": modelspec_key_present(config),
    }, sort_keys=True).encode()).hexdigest()[:16]
    directory = output / "checkpoints"
    if directory.is_symlink():
        raise ValueError(f"Checkpoint directory must not be a symlink: {directory}")
    directory.mkdir(parents=True, exist_ok=True, mode=0o700)
    directory.chmod(0o700)
    path = directory / f"scenarios-{day}-{digest}.jsonl"
    if path.is_symlink():
        raise ValueError(f"Checkpoint file must not be a symlink: {path}")
    return path


def _read_checkpoint(path: Path) -> list[dict]:
    """Load finished rows. A torn final line is dropped; any earlier bad line refuses the run."""
    if path.is_symlink():
        raise ValueError(f"Checkpoint file must not be a symlink: {path}")
    raw = path.read_bytes()
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError(f"Malformed checkpoint line in {path}") from exc
    rows, kept = [], []
    lines = text.splitlines(keepends=True)
    for index, line in enumerate(lines):
        body = line.rstrip("\r\n")
        try:
            parsed = json.loads(body)
        except json.JSONDecodeError:
            if index == len(lines) - 1:
                break
            raise ValueError(f"Malformed checkpoint line {index + 1} in {path}") from None
        if not isinstance(parsed, dict) or "scenario" not in parsed or "cli" not in parsed:
            raise ValueError(f"Malformed checkpoint line {index + 1} in {path}")
        rows.append(parsed)
        kept.append(body)
    repaired = "".join(body + "\n" for body in kept).encode()
    if repaired != raw:
        with path.open("r+b") as handle:
            handle.write(repaired)
            handle.truncate()
            handle.flush()
            os.fsync(handle.fileno())
    return rows


def _append_checkpoint(path: Path, row: dict) -> None:
    if path.is_symlink():
        raise ValueError(f"Checkpoint file must not be a symlink: {path}")
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(redact_structure(row)) + "\n")
        handle.flush()
        os.fsync(handle.fileno())


def _require_checkpoint_resume_state(path: Path, *, resume: bool) -> None:
    if resume and not path.exists():
        raise ValueError(
            f"No checkpoint at {path}. The CLIs, scenarios, --date, engine commit and "
            "ModelSpec key presence must match the interrupted run."
        )
    if path.exists() and not resume:
        raise ValueError(
            f"Checkpoint already exists at {path}. "
            "Pass --resume to continue it or delete it to start over."
        )


def _selected_scenarios(patterns) -> list[dict]:
    scenarios = [
        scenario for scenario in agent_harness.load_scenarios()
        if not patterns or any(fnmatchcase(scenario["id"], pattern) for pattern in patterns)
    ]
    if not scenarios:
        raise ValueError("Scenario filter matched nothing")
    return scenarios


def network_probe(timeout: float = 5.0) -> dict:
    """Ask two public endpoints whether this machine can open a connection. Never raises."""
    checks = []
    for url in (API_HEALTH_URL, INTERNET_PROBE_URL):
        started = time.perf_counter()
        status, error, reachable = None, None, False
        try:
            request = urllib.request.Request(
                url, headers={"User-Agent": "modelspec-qa-network-probe"},
            )
            with urllib.request.urlopen(request, timeout=timeout) as response:
                status, reachable = response.status, True
        except urllib.error.HTTPError as exc:
            # HTTPError subclasses URLError; a status line means the host answered.
            status, reachable = exc.code, True
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            error = type(exc).__name__
        except Exception as exc:
            error = type(exc).__name__
        checks.append({
            "url": url,
            "reachable": reachable,
            "status": status,
            "error": error,
            "ms": (time.perf_counter() - started) * 1000,
        })
    return {
        "reachable": all(check["reachable"] for check in checks),
        "checks": checks,
        "checked_at": datetime.now(timezone.utc).isoformat(),
    }


def _probe_target_reachable(probe: dict, url: str) -> bool:
    for check in probe.get("checks") or []:
        if check.get("url") == url:
            return bool(check.get("reachable"))
    return False


def network_tag(row: dict, probe=None) -> dict:
    """Tag a failed row. ``probe`` defaults to the module-level ``network_probe``."""
    failed = {"cli_error", "timeout", "transcript_error", "empty_answer"}
    judge = row.get("judge_execution") or {}
    agent_failed = row["status"] in failed
    judge_failed = judge.get("status") in failed
    if not agent_failed and not judge_failed:
        return {"class": "not_checked"}
    signature = bool(NETWORK_ERROR.search(" ".join(
        str(item) for item in (row.get("error"), judge.get("error")) if item
    )))
    result = network_probe() if probe is None else probe()
    internet_down = not _probe_target_reachable(result, INTERNET_PROBE_URL)
    return {
        "class": "network_suspect" if signature or internet_down else "no_network_signal",
        "failed_stage": "agent" if agent_failed else "judge",
        "error_signature": signature,
        "api_reachable": _probe_target_reachable(result, API_HEALTH_URL),
        "probe": result,
    }


def _cli_invocation_totals(counts: dict, resumed_rows: list[dict]) -> dict:
    """Copy this process's counts and add one start per checkpointed row."""
    total = {cli: dict(roles) for cli, roles in counts.items()}
    for row in resumed_rows:
        agent = row["cli"]
        total.setdefault(agent, {"agent": 0, "judge": 0})
        total[agent]["agent"] += 1
        judge = row.get("judge_execution")
        if isinstance(judge, dict) and judge.get("cli"):
            judge_cli = judge["cli"]
            total.setdefault(judge_cli, {"agent": 0, "judge": 0})
            total[judge_cli]["judge"] += 1
    return total


def scenario_report(config, selected, scenarios, output, *, day, dry_run=False, resume=False):
    if resume and dry_run:
        raise ValueError("--resume cannot be combined with --dry-run")
    engine_sha = git_command(tui_harness.ROOT, "rev-parse", "HEAD")
    rows, resumed, recorded, checkpoint = [], 0, {}, None
    if not dry_run:
        checkpoint = _scenario_checkpoint(
            output, selected, scenarios, day, engine_sha, config=config,
        )
        _require_checkpoint_resume_state(checkpoint, resume=resume)
        if checkpoint.exists():
            loaded = _read_checkpoint(checkpoint)
            expected = {(scenario["id"], cli) for scenario in scenarios for cli in selected}
            for row in loaded:
                pair = (row["scenario"], row["cli"])
                if pair not in expected or pair in recorded:
                    raise ValueError(f"Malformed checkpoint line in {checkpoint}")
                recorded[pair] = row
            resumed = len(loaded)
        if resume:
            total = len(scenarios) * len(selected)
            print(
                f"Resuming: {resumed} of {total} rows already recorded in {checkpoint}",
                flush=True,
            )
    needed = list(dict.fromkeys(selected + [tui_harness.judge_for(c, config["judges"]) for c in selected]))
    isolation = {} if dry_run else require_ready(config, needed, output)
    runner = tui_harness.Runner(config, output, isolation)
    for scenario in scenarios:
        for cli in selected:
            saved = recorded.get((scenario["id"], cli))
            if saved is not None:
                rows.append(saved)
                continue
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
            if checkpoint is not None:
                row["network"] = network_tag(row)
                _append_checkpoint(checkpoint, row)
    metadata = {"agents": {AGENT_NAMES[c]: config["clis"][c] for c in selected},
                "judge": {"mode": "single", "routes": config["judges"]},
                "transport": "subscription-cli", "auth": "CLI subscription",
                "source_hashes": agent_harness.source_hashes(),
                "cli_invocations": runner.counts,
                "cli_invocations_total": _cli_invocation_totals(runner.counts, list(recorded.values())),
                "cli_invocations_scope": "final invocation only" if resumed else "whole run",
                "engine_sha": engine_sha,
                "max_runs_per_cli": config["max_runs_per_cli"], "isolation": isolation}
    report = agent_harness.make_report(rows, scenarios, dry_run, Budget(0), day, metadata)
    report["partial"] = any(
        row["status"] == "quiet_hours" or row.get("judge_execution", {}).get("status") == "quiet_hours"
        for row in rows
    )
    note = (
        "Subscription CLI agents and separate cross-family CLI judges over ModelSpec MCP. "
        "API-shaped aggregates and unordered recall scoring are unchanged. Vendor API spend is zero; "
        "reported token-equivalent costs are separate. Unknown latency stays unknown. "
        + ("Dry-run command previews contain no measured results." if dry_run else "Measured subscription run.")
    )
    suspects = sorted(
        [row["scenario"], row["cli"]]
        for row in rows
        if (row.get("network") or {}).get("class") == "network_suspect"
    )
    if resumed:
        note += f" Resumed after an interruption: {resumed} rows came from the checkpoint."
    if suspects:
        note += (
            f" {len(suspects)} failed rows are tagged network_suspect"
            " and can be excluded; see network_suspect."
        )
    report["evidence_note"] = note
    report["resumed"] = resumed
    report["network_suspect"] = suspects
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
    misuse = report.get("isolation_misuse") or []
    pairs = [f"[{scenario}, {cli}]" for scenario, cli, *_rest in misuse]
    shown = ", ".join(pairs[:10])
    more = f" (+{len(pairs) - 10} more)" if len(pairs) > 10 else ""
    lines.append(
        f"Isolation misuse: {len(misuse)} rows" + (f": {shown}{more}" if misuse else ".")
    )
    defects = [f"[{scenario}, {cli}]" for scenario, cli in agent_harness.parse_defect_pairs(report)]
    shown = ", ".join(defects[:10])
    more = f" (+{len(defects) - 10} more)" if len(defects) > 10 else ""
    lines.append(
        f"Parse defects: {len(defects)} rows" + (f": {shown}{more}" if defects else ".")
    )
    if defects:
        lines.append(agent_harness.PARSE_DEFECT_NOTE)
    return "\n".join(lines) + "\n"


def decide_health(report: dict) -> dict:
    """Count decide answers the key could not fund or did not authorise.

    parse_defects counts observed ModelSpec results with no JSON envelope.
    Those rows are measurement defects and do not refuse publication.
    """
    counts = {
        "decide_answers": 0, "credits_exhausted": 0, "partial": 0, "unauthorised": 0,
        "unreadable": 0, "parse_defects": 0,
    }
    for run in report["runs"]:
        for call in run.get("tool_calls") or []:
            ref = call.get("response_ref")
            response = report["tool_responses"].get(ref) if ref else None
            if agent_harness.call_parse_defect(call, response):
                counts["parse_defects"] += 1
            # A call cut off by a timeout or turn cap keeps a null placeholder result.
            if call.get("name") != "decide" or response is None or call.get("result_observed") is False:
                continue
            readable = False
            for block in response.get("content") or []:
                envelope = agent_harness.status_envelope(block)
                if envelope is None:
                    continue
                readable = True
                body = envelope.get("body") if isinstance(envelope.get("body"), dict) else {}
                credits = body.get("credits") if isinstance(body.get("credits"), dict) else {}
                counts["decide_answers"] += 1
                counts["unauthorised"] += envelope.get("status") in (401, 402, 403)
                counts["credits_exhausted"] += credits.get("exhausted") is True
                counts["partial"] += body.get("status") == "partial"
            # A tool-level error in plain text never reached the API.
            counts["unreadable"] += not readable and not response.get("isError")
    return counts


def require_funded_key(report: dict, checkpoint: Path | None = None) -> dict:
    """Refuse publication when a decide was unauthorised, unfunded, or unreadable."""
    health = decide_health(report)
    if health["credits_exhausted"] or health["unauthorised"]:
        message = (
            f"ModelSpec key unusable: {health['credits_exhausted']} credits.exhausted and "
            f"{health['unauthorised']} unauthorised of {health['decide_answers']} decide answers. "
            "Report kept locally, not published; fix the key and rerun."
        )
        if checkpoint is not None:
            message += (
                f" Recorded rows in {checkpoint} will be replayed on --resume."
                " After fixing the key, delete the checkpoint and start over."
            )
        raise ValueError(message)
    if health["decide_answers"] == 0 and health["unreadable"] > 0:
        raise ValueError(
            "No decide answer was readable "
            f"({health['unreadable']} unreadable); key health unknown."
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
    parser.add_argument(
        "--resume", action="store_true",
        help="Skip scenario rows already recorded by an interrupted run "
             "with the same CLIs, scenarios, day, engine and ModelSpec key presence",
    )
    parser.add_argument("--scheduled", action="store_true", help="Always enforces quiet hours")
    parser.add_argument("--quiet-hours", action="store_true")
    parser.add_argument("--cli", choices=CLIS, action="append")
    parser.add_argument("--scenario", action="append", help="Scenario ID glob; repeatable")
    parser.add_argument("--max-runs-per-cli", type=int)
    parser.add_argument("--date", default=datetime.now(timezone.utc).date().isoformat())
    parser.add_argument("--base-url", default="https://modelspec.dev/decide/")
    args = parser.parse_args(argv)
    try:
        if args.resume and args.dry_run:
            raise ValueError("--resume cannot be combined with --dry-run")
        if args.resume and args.job != "scenarios":
            raise ValueError("--resume applies only to the scenarios job")
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
            scenarios = _selected_scenarios(args.scenario) if args.job == "scenarios" else None
            checkpoint = None
            if scenarios is not None and not args.dry_run:
                engine_sha = git_command(tui_harness.ROOT, "rev-parse", "HEAD")
                checkpoint = _scenario_checkpoint(
                    state, selected, scenarios, args.date, engine_sha, config=config,
                )
                _require_checkpoint_resume_state(checkpoint, resume=args.resume)

            def execute(tree):
                output = tree / REPORT_PATHS[args.job]
                output.mkdir(parents=True, exist_ok=True)
                if args.job == "scenarios":
                    report = scenario_report(config, selected, scenarios, state, day=args.date,
                                             dry_run=args.dry_run, resume=args.resume)
                    write_pair(output, args.date, report, agent_harness.markdown(report))
                    if checkpoint is not None and modelspec_key_present(config):
                        health = require_funded_key(report, checkpoint)
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
