"""Test the public scenario catalogue through isolated, subscription-backed CLIs.

Reports require a private --out directory. Unsupported CLIs are recorded without
launching them. --dry-run prints commands and makes no CLI or network calls.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import re
import shlex
import subprocess
import tempfile
from datetime import date, datetime
from pathlib import Path

import yaml

from qa.agent_harness import (
    HERE,
    JUDGE_NOTE,
    ROOT,
    agent_context,
    agent_request,
    expected_match,
    load_scenarios,
    make_report,
    parse_judgement,
    percentile,
)
from qa.contracts import source_hashes
from qa.docker.entrypoint import refuse_vendor_auth
from qa.providers import Budget, redact, redact_structure
from qa.tui_docker import (
    GEMINI_RETIRED,
    build_images,
    container_command,
    image_name,
    passed_environment,
)
from qa.tui_homes import (
    binary_identity,
    home_config,
    home_paths,
    login,
    login_command,
    version_numbers,
)
from qa.tui_isolation import isolation_result
from qa.tui_isolation import verify_isolation as doctor_isolation
from qa.tui_providers import (
    BASE_ENV,
    CLIS,
    FAMILY,
    Execution,
    build_command,
    launch,
    mcp_config,
)


def private_output(path: Path) -> Path:
    """Reject this public repository, its other worktrees, and symlink aliases."""
    resolved = path.expanduser().resolve()
    if resolved.is_relative_to(ROOT.resolve()):
        raise ValueError("--out must be outside the public ModelSpec repository")
    ancestor = resolved
    while not ancestor.exists():
        ancestor = ancestor.parent
    if ancestor.is_file():
        raise ValueError("--out must name a directory")

    def common_dir(directory):
        result = subprocess.run(
            ["git", "-C", str(directory), "rev-parse", "--git-common-dir"],
            capture_output=True,
            text=True,
            input="",
            check=False,
        )
        return (directory / result.stdout.strip()).resolve() if result.returncode == 0 else None

    public_common = common_dir(ROOT)
    if public_common and common_dir(ancestor) == public_common:
        raise ValueError("--out must not be in any public ModelSpec worktree")
    return resolved


def quiet_hours_guard(enabled: bool, force: bool, now: datetime | None = None) -> None:
    local = now if now is not None else datetime.now().astimezone()
    if enabled and not force and 8 <= local.hour < 22:
        raise ValueError("Quiet hours refuse CLI starts between 08:00 and 22:00 local; use --force")


def judge_for(cli: str, routes: dict) -> str:
    judge = routes.get(cli)
    if judge not in FAMILY or FAMILY[judge] == FAMILY[cli]:
        raise ValueError(f"{cli} needs a judge from a different CLI family")
    return judge


def validate_config(config: dict) -> None:
    if set(config["clis"]) != set(CLIS):
        raise ValueError("Configure claude, codex, gemini and grok")
    if config["concurrency_per_cli"] != 1:
        raise ValueError("This serial runner supports concurrency_per_cli=1")
    for key in ("turn_cap", "max_runs_per_cli"):
        if type(config[key]) is not int or config[key] < 1:
            raise ValueError(f"{key} must be a positive integer")
    seconds = config["timeout_seconds"]
    if not isinstance(seconds, (int, float)) or not math.isfinite(seconds) or seconds <= 0:
        raise ValueError("timeout_seconds must be finite and positive")
    from urllib.parse import urlsplit

    url = urlsplit(config["mcp_url"])
    if (
        url.scheme != "https"
        or not url.hostname
        or url.username
        or url.password
        or url.query
        or url.fragment
    ):
        raise ValueError("mcp_url must be a remote HTTPS URL without embedded credentials or query")
    token_env = config.get("mcp_token_env")
    if token_env is not None and not re.fullmatch(r"MODELSPEC_[A-Z0-9_]+", token_env):
        raise ValueError("mcp_token_env must be null or a MODELSPEC_ environment variable")
    for cli, profile in config["clis"].items():
        image_name(cli, profile)
        if any(name in profile for name in ("harness_home", "node_executable", "environment")):
            raise ValueError("Native host homes and environment overrides have been retired")
        if any(
            not isinstance(profile[key], str) or not profile[key].strip()
            for key in ("executable", "model")
        ):
            raise ValueError(f"{cli} needs an executable and a model")
        home_paths(cli, profile)
        if cli == "codex" and version_numbers(profile["version"]) < (0, 160, 0):
            raise ValueError("Codex images require version >=0.160.0")
        minimum = profile.get("min_version")
        if minimum is not None:
            if not isinstance(minimum, str) or not re.fullmatch(r"\d+\.\d+(?:\.\d+)?", minimum):
                raise ValueError(f"{cli} min_version must be a numeric major.minor[.patch] string")
            version_numbers(minimum)
        codes = profile["usage_limit_exit_codes"]
        if not isinstance(codes, list) or any(
            type(code) is not int or not 1 <= code <= 255 for code in codes
        ):
            raise ValueError("Usage-limit exit codes must be explicit nonzero exit statuses")
        if cli != "gemini" and profile.get("effort") not in {
            "low",
            "medium",
            "high",
            "xhigh",
            "max",
        }:
            raise ValueError(f"Invalid effort for {cli}")
        judge_for(cli, config["judges"])


def scenario_prompt(scenario: dict) -> str:
    return agent_context() + "\nUser request:\n" + agent_request(scenario)


def judge_prompt(scenario: dict, row: dict) -> str:
    # Same rubric, independent recall expectations and parsing as the API harness.
    data = {
        "scenario": scenario,
        "final_answer": row["final_answer"],
        "tool_calls": row["tool_calls"],
    }
    return JUDGE_NOTE + "\nSubmitted data:\n" + json.dumps(data, ensure_ascii=False)


def verify_isolation(cli: str, config: dict, output: Path) -> dict:
    return doctor_isolation(
        cli,
        config,
        output,
        before_start=lambda: quiet_hours_guard(
            config.get("_quiet_hours", False), config.get("_force", False)
        ),
    )


def empty_row(
    scenario: dict, cli: str, config: dict, status: str, error: str | None = None
) -> dict:
    return {
        "scenario": scenario["id"],
        "family": scenario["family"],
        "agent": cli,
        "model": config["clis"][cli]["model"],
        "tool_calls": [],
        "model_calls": [],
        "tokens_in": None,
        "tokens_out": None,
        "final_answer": "",
        "status": status,
        "judge": None,
        "expected_match": None,
        "success": False,
        "error": error,
        "turns": None,
        "first_decide_call": None,
        "wall_time_ms": None,
        "exit_code": None,
        "reported_cost_usd": None,
    }


def execution_row(scenario: dict, cli: str, config: dict, execution: Execution) -> dict:
    parsed = execution.transcript
    row = empty_row(scenario, cli, config, execution.status, execution.error)
    row.update(
        model=parsed.model or row["model"],
        tool_calls=parsed.tool_calls,
        other_tool_calls=parsed.other_tool_calls,
        tokens_in=parsed.tokens_in,
        tokens_out=parsed.tokens_out,
        final_answer=parsed.final_answer,
        turns=parsed.turns,
        turns_basis=parsed.turns_basis,
        first_decide_call=parsed.first_decide_call,
        wall_time_ms=execution.wall_time_ms,
        exit_code=execution.exit_code,
        reported_cost_usd=parsed.cost_usd,
        usage=parsed.usage,
        usage_limit=execution.limit_reason,
        total_tool_calls=len(parsed.tool_calls) + len(parsed.other_tool_calls),
    )
    row["model_calls"] = [
        {
            "role": "agent",
            "family": FAMILY[cli],
            "model": row["model"],
            "tokens_in": parsed.tokens_in,
            "tokens_out": parsed.tokens_out,
            "cost_usd": parsed.cost_usd,
        }
    ]
    return row


class StartRefusedError(ValueError):
    def __init__(self, status: str, reason: str):
        super().__init__(reason)
        self.status = status


class Runner:
    """One serial owner of scenario and judge quotas, including shared judges."""

    def __init__(self, config: dict, output: Path, isolation: dict):
        self.config, self.output, self.isolation = config, output, isolation
        self.counts = {cli: {"agent": 0, "judge": 0} for cli in CLIS}
        self.stopped = {
            cli: info["reason"]
            for cli, info in isolation.items()
            if info.get("status") == "usage_limit"
        }

    def refusal(self, cli: str) -> tuple[str, str] | None:
        if cli in self.stopped:
            return "usage_limit_skipped", self.stopped[cli]
        info = self.isolation[cli]
        if not info["supported"]:
            return "unsupported", info["reason"]
        if not info["verified"]:
            return "isolation_failed", info["reason"]
        try:
            quiet_hours_guard(
                self.config.get("_quiet_hours", False), self.config.get("_force", False)
            )
        except ValueError as exc:
            return "quiet_hours", str(exc)
        if sum(self.counts[cli].values()) >= self.config["max_runs_per_cli"]:
            return "max_runs", "CLI invocation quota reached (includes judges)"
        return None

    def invoke(self, cli: str, prompt: str, role: str, *, workspace=None, purpose=None, images=()) -> Execution:
        refuse_vendor_auth(os.environ)
        if refusal := self.refusal(cli):
            raise StartRefusedError(*refusal)
        self.counts[cli][role] += 1
        def execute(directory):
            run_config = self.config | ({"_judge_images": images} if images else {})
            try:
                execution = launch(
                    cli, run_config, Path(directory), prompt, mcp_enabled=role == "agent",
                    **({"purpose": purpose} if purpose else {}),
                )
            except ValueError as exc:
                raise StartRefusedError("unsupported", str(exc)) from exc
            return execution
        if workspace is not None:
            execution = execute(workspace)
        else:
            with tempfile.TemporaryDirectory(prefix=f"tui-{cli}-{role}-", dir=self.output) as directory:
                execution = execute(directory)
        if execution.status == "usage_limit":
            self.stopped[cli] = execution.limit_reason or "CLI usage limit"
        elif execution.status in ("isolation_failed", "transcript_error"):
            self.isolation[cli] = {
                **self.isolation[cli],
                "supported": False,
                "verified": False,
                "reason": execution.error or "CLI isolation evidence became invalid",
            }
        return execution

    def scenario(self, scenario: dict, cli: str) -> dict:
        if refusal := self.refusal(cli):
            return empty_row(scenario, cli, self.config, *refusal)
        judge = judge_for(cli, self.config["judges"])
        if refusal := self.refusal(judge):
            return empty_row(
                scenario,
                cli,
                self.config,
                "quiet_hours" if refusal[0] == "quiet_hours" else "judge_unavailable",
                f"{judge}: {refusal[0]}. {refusal[1]}",
            )
        try:
            execution = self.invoke(cli, scenario_prompt(scenario), "agent")
        except StartRefusedError as exc:
            return empty_row(scenario, cli, self.config, exc.status, str(exc))
        row = execution_row(scenario, cli, self.config, execution)
        if execution.status != "completed":
            return row
        try:
            judged = self.invoke(judge, judge_prompt(scenario, row), "judge")
        except StartRefusedError as exc:
            row["evaluation_status"] = "judge_unavailable"
            row["judge_execution"] = {
                "cli": judge,
                "status": exc.status,
                "exit_code": None,
                "wall_time_ms": None,
                "usage_limit": None,
                "error": str(exc),
            }
            return row
        parsed = judged.transcript
        row["judge_execution"] = {
            "cli": judge,
            "status": judged.status,
            "exit_code": judged.exit_code,
            "wall_time_ms": judged.wall_time_ms,
            "usage_limit": judged.limit_reason,
            "error": judged.error,
        }
        row["model_calls"].append(
            {
                "role": "judge",
                "family": FAMILY[judge],
                "model": parsed.model or self.config["clis"][judge]["model"],
                "tokens_in": parsed.tokens_in,
                "tokens_out": parsed.tokens_out,
                "cost_usd": parsed.cost_usd,
            }
        )
        if judged.status != "completed":
            row["evaluation_status"] = "judge_" + judged.status
            return row
        try:
            row["judge"] = {
                "family": FAMILY[judge],
                "cli": judge,
                "model": parsed.model or self.config["clis"][judge]["model"],
                **parse_judgement(parsed.final_answer),
            }
        except (ValueError, TypeError):
            row["evaluation_status"] = "evaluation_error"
            return row
        row["expected_match"] = expected_match(scenario["expected"], row["judge"])
        row["success"] = row["judge"]["passed"] and row["expected_match"] is not False
        row["evaluation_status"] = "judged"
        return row


def report_for(
    rows: list[dict],
    scenarios: list[dict],
    selected: list[str],
    config: dict,
    isolation: dict,
    counts: dict,
    stopped: dict,
    *,
    dry_run=False,
    blocked=None,
) -> dict:
    metadata = {
        "agents": {cli: config["clis"][cli] for cli in selected},
        "judges": config["judges"],
        "transport": "remote-mcp",
        "mcp_url": config["mcp_url"],
        "auth": "CLI subscription",
        "concurrency_per_cli": 1,
        "max_runs_per_cli": config["max_runs_per_cli"],
        "guide_version": re.search(r"Guide version: (\S+)", (ROOT / "docs/agents.md").read_text())[
            1
        ],
        "source_hashes": source_hashes(),
        "blocked_reason": blocked,
    }
    report = make_report(rows, scenarios, dry_run, Budget(0), date.today().isoformat(), metadata)
    report["evidence_note"] = (
        "Subscription CLI transcripts over remote MCP. Unsupported and skipped rows are explicit. "
        "No scenario runs occur in dry-run or isolation verification. Tool latency is unavailable "
        "unless the CLI reports it; wall time measures the agent subprocess, excluding its judge. "
        "CLI turn counters have different meanings; turns_basis records the source. "
        "A reported token-equivalent cost is not the subscription invoice."
    )
    all_costs = [call["cost_usd"] for row in rows for call in row["model_calls"]]
    report["budget"] = {
        "cap_usd": None,
        "estimated_spend_usd": None,
        "real_spend_usd": None,
        "reported_cost_usd": sum(all_costs) if all_costs and None not in all_costs else None,
        "reservations": [],
        "max_runs_per_cli": config["max_runs_per_cli"],
        "quota_includes": ["agent", "judge"],
        "canary_runs_are_separate": True,
    }
    report["isolation"] = isolation
    report["cli_invocations"] = counts
    report["stopped_clis"] = stopped
    report["executed_runs"] = sum(counts[cli]["agent"] for cli in selected)
    report["per_cli"] = {}
    for cli in selected:
        attempted = [row for row in rows if row["agent"] == cli and row["wall_time_ms"] is not None]
        timings = [row["wall_time_ms"] for row in attempted]
        turns = [row["turns"] for row in attempted if row["turns"] is not None]
        decide = [
            row["first_decide_call"] for row in attempted if row["first_decide_call"] is not None
        ]
        report["per_cli"][cli] = {
            **report["per_agent"][cli],
            **isolation[cli],
            "invocations": counts[cli],
            "attempted_scenarios": len(attempted),
            "wall_time_p50_ms": percentile(timings, 0.5),
            "wall_time_p95_ms": percentile(timings, 0.95),
            "mean_turns": sum(turns) / len(turns) if turns else None,
            "mean_first_decide_call": sum(decide) / len(decide) if decide else None,
        }
    return report


def markdown(report: dict) -> str:
    def number(value):
        return "n/a" if value is None else f"{value:.2f}"

    lines = [
        f"# TUI agent scenarios, {report['report_date']}",
        "",
        report["evidence_note"],
        "",
        f"Mode: {report['mode']}. Executed scenarios: {report['executed_runs']}. "
        f"Scheduled rows: {report['scheduled_runs']}. "
        "Quota includes scenario and judge invocations. "
        "Doctor controls are separate from scenario and judge quotas.",
    ]
    if report["metadata"]["blocked_reason"]:
        lines += ["", "Start refused: " + report["metadata"]["blocked_reason"]]
    lines += [
        "",
        "| CLI | Isolation | Attempts | Success | Mean tools | Mean turns | First decide "
        "| Wall p50 ms | Wall p95 ms |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for cli, values in report["per_cli"].items():
        state = (
            "verified"
            if values["verified"]
            else "unverified"
            if values["supported"]
            else "unsupported"
        )
        rate = f"{values['success_rate'] * 100:.1f}%" if values["attempted_scenarios"] else "n/a"
        lines.append(
            f"| {cli} | {state} | {values['attempted_scenarios']} | {rate} | "
            f"{number(values['mean_tool_calls'])} | {number(values['mean_turns'])} | "
            f"{number(values['mean_first_decide_call'])} | {number(values['wall_time_p50_ms'])} | "
            f"{number(values['wall_time_p95_ms'])} |"
        )
    for cli, info in report["isolation"].items():
        authentication = info.get("authentication", {})
        if authentication:
            state = {True: "logged in", False: "not logged in", None: "unknown"}[
                authentication.get("logged_in")
            ]
            lines += [
                "",
                f"{cli} authentication: {state}; method "
                f"{authentication.get('auth_method') or 'unknown'}.",
            ]
        if info.get("reason"):
            lines += ["", f"{cli}: {info['reason']}"]
    lines += [
        "",
        "Success uses the API harness rubric and approved, unordered recall expectations. "
        "Missing judgements and failed, capped or skipped rows remain failures in the API-shaped "
        "aggregates. The JSON contains ordered MCP calls, their response references, "
        "final answers, "
        "usage, exit statuses, judge results, family comparisons, misuse counts and sourced gaps.",
        "",
        "## Scenario outcomes",
        "",
        "| Scenario | CLI | Status | Evaluation | Exit |",
        "| --- | --- | --- | --- | ---: |",
    ]
    for row in report["runs"]:
        lines.append(
            f"| {row['scenario']} | {row['agent']} | {row['status']} | "
            f"{row.get('evaluation_status', 'not judged')} | {row['exit_code']} |"
        )
    return "\n".join(lines) + "\n"


def write_report(report: dict, output: Path) -> tuple[Path, Path]:
    output = private_output(output)
    output.mkdir(parents=True, exist_ok=True)
    stem = output / f"{report['report_date']}-tui-agent-scenarios"
    js, md = stem.with_suffix(".json"), stem.with_suffix(".md")
    if js.is_symlink() or md.is_symlink():
        raise ValueError("Report files must not be symlinks")
    js.write_text(json.dumps(redact_structure(report), indent=2, ensure_ascii=False) + "\n")
    md.write_text(redact(markdown(report)))
    return js, md


def dry_commands(scenarios: list[dict], selected: list[str], config: dict, output: Path) -> None:
    for cli in selected:
        for scenario in scenarios[: config["max_runs_per_cli"]]:
            with tempfile.TemporaryDirectory(prefix=f"tui-dry-{cli}-", dir=output) as directory:
                workspace = Path(directory)
                mcp_file = workspace / "modelspec-mcp.json"
                payload = mcp_config(config["mcp_url"], config.get("mcp_token_env"), enabled=True)
                mcp_file.write_text(home_config(cli, config))
                command = build_command(
                    cli,
                    config["clis"][cli],
                    workspace,
                    scenario_prompt(scenario),
                    mcp_file,
                    config["turn_cap"],
                )
                command = container_command(
                    cli, config, workspace, command, passed_environment(config, token=True)
                )
                print(
                    json.dumps(
                        redact_structure(
                            {
                                "cli": cli,
                                "scenario": scenario["id"],
                                "cwd": str(workspace),
                                "command": shlex.join(command),
                                "stdin": "",
                                "environment_inherit_only": list(BASE_ENV),
                                "eligibility": "Doctor receipt required before execution",
                                "mcp_config": payload,
                                "judge_cli": judge_for(cli, config["judges"]),
                            }
                        ),
                        ensure_ascii=False,
                    )
                )


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=HERE / "tui_config.yaml")
    parser.add_argument(
        "action",
        nargs="?",
        choices=("run", "build-images", "login", "doctor", "inventory"),
        default="run",
    )
    parser.add_argument(
        "--out", type=Path, help="Private report directory, required except for build-images/login"
    )
    parser.add_argument("--cli", choices=CLIS, action="append")
    parser.add_argument("--ux-image", action="store_true", help="Build/certify the Playwright image variant")
    parser.add_argument("--scenario", action="append")
    parser.add_argument(
        "--judge", action="append", metavar="CLI=JUDGE", help="Override a judge route"
    )
    parser.add_argument("--max-runs-per-cli", type=int)
    parser.add_argument("--quiet-hours", action="store_true")
    parser.add_argument("--force", action="store_true", help="Override quiet hours only")
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--dry-run", action="store_true")
    modes.add_argument(
        "--verify-isolation", action="store_true", help="Only non-MCP canaries, no scenarios"
    )
    modes.add_argument(
        "--smoke", action="store_true", help="All isolation must pass; budget-approved only"
    )
    args = parser.parse_args(argv)
    try:
        refuse_vendor_auth(os.environ)
        config = yaml.safe_load(args.config.read_text())
        if args.ux_image:
            for cli in args.cli or CLIS:
                config["clis"][cli]["image_variant"] = "ux"
        if args.max_runs_per_cli is not None:
            config["max_runs_per_cli"] = args.max_runs_per_cli
        for override in args.judge or []:
            cli, judge = override.split("=", 1)
            if cli not in CLIS:
                raise ValueError("Unknown CLI in judge route")
            config["judges"][cli] = judge
        validate_config(config)
        config["_quiet_hours"], config["_force"] = args.quiet_hours, args.force
        if args.action in ("login", "doctor") and len(args.cli or []) != 1:
            raise ValueError("login and doctor require exactly one --cli")
        if args.action == "build-images":
            if args.dry_run or args.smoke or args.verify_isolation:
                raise ValueError("build-images cannot be combined with run modes")
            selected = list(dict.fromkeys(args.cli or CLIS))
            build_images(config, selected)
            for cli in selected:
                with tempfile.TemporaryDirectory(prefix="tui-version-") as directory:
                    identity = binary_identity(cli, config, Path(directory))
                if cli == "gemini":
                    print(f"{cli}: {identity['reported_version']}. {GEMINI_RETIRED}.")
                    continue
                print(f"{cli}: {identity['reported_version']}. Login yourself with:")
                print(login_command(cli, args.config))
            return 0
        if args.action == "login":
            if args.dry_run or args.smoke or args.verify_isolation:
                raise ValueError("login cannot be combined with run modes")
            cli = args.cli[0]
            login(cli, config)
            return 0
        if args.out is None:
            raise ValueError("--out is required for private doctor and run reports")
        if args.action == "doctor":
            if args.dry_run or args.smoke:
                raise ValueError("doctor cannot be combined with run modes")
            args.verify_isolation = True
        output = private_output(args.out)
        config["_state_dir"] = str(output / (".tui-state-ux" if args.ux_image else ".tui-state"))
        if args.action == "inventory":
            if args.dry_run or args.smoke or args.verify_isolation:
                raise ValueError("inventory cannot be combined with run modes")
            from qa.tui_inventory import inspect_inventory
            from qa.tui_providers import prepare_workspace

            output.mkdir(parents=True, exist_ok=True)
            config["_anonymous_home"] = True
            for cli in dict.fromkeys(args.cli or CLIS):
                with tempfile.TemporaryDirectory(prefix=f"tui-inventory-{cli}-", dir=output) as d:
                    workspace = Path(d)
                    binary_identity(cli, config, workspace)
                    mcp_file = workspace / "modelspec-mcp.json"
                    mcp_file.write_text(home_config(cli, config))
                    prepare_workspace(cli, config, workspace, mcp_enabled=True)
                    info = inspect_inventory(
                        cli,
                        config,
                        workspace,
                        passed_environment(config),
                        mcp_file,
                        mcp_enabled=True,
                    )
                    print(
                        json.dumps(
                            redact_structure({"cli": cli, "inventory": info, "certified": False})
                        )
                    )
            return 0
        if not args.dry_run:
            quiet_hours_guard(args.quiet_hours, args.force)
        scenarios = load_scenarios()
        if args.smoke:
            if args.scenario and args.scenario != ["budget-approved"]:
                raise ValueError("Smoke runs only budget-approved")
            if args.max_runs_per_cli not in (None, 1):
                raise ValueError("Smoke runs require max-runs-per-cli=1")
            config["max_runs_per_cli"] = 1
            args.scenario = ["budget-approved"]
        if args.scenario:
            unknown = set(args.scenario) - {scenario["id"] for scenario in scenarios}
            if unknown:
                raise ValueError("Unknown scenario ids: " + ", ".join(sorted(unknown)))
            scenarios = [scenario for scenario in scenarios if scenario["id"] in args.scenario]
    except (ValueError, KeyError, TypeError, OSError) as exc:
        parser.error(str(exc))
    selected = list(dict.fromkeys(args.cli or CLIS))
    output.mkdir(parents=True, exist_ok=True)
    needed = (
        selected
        if args.verify_isolation
        else list(dict.fromkeys(selected + [judge_for(cli, config["judges"]) for cli in selected]))
    )
    isolation = {
        cli: {
            "supported": False,
            "verified": False,
            "status": "unproven",
            "reason": "Dry-run does not certify isolation",
            "canary_runs": 0,
        }
        if args.dry_run
        else isolation_result(cli, config)
        for cli in needed
    }
    counts = {cli: {"agent": 0, "judge": 0} for cli in CLIS}
    blocked, rows, stopped = None, [], {}
    if args.dry_run:
        dry_commands(scenarios, selected, config, output)
    elif args.smoke and any(not info["supported"] for info in isolation.values()):
        blocked = (
            "Smoke requires verified isolation for every selected CLI and every judge; "
            "unsupported CLIs remain."
        )
    else:
        if args.verify_isolation:
            for cli in needed:
                isolation[cli] = verify_isolation(cli, config, output)
        runner = Runner(config, output, isolation)
        if args.smoke and any(not info["verified"] for info in isolation.values()):
            blocked = "Isolation verification failed; smoke did not start."
        elif not args.verify_isolation:
            for scenario in scenarios:
                for cli in selected:
                    rows.append(runner.scenario(scenario, cli))
        counts, stopped = runner.counts, runner.stopped
    if blocked:
        rows = [
            empty_row(
                scenario,
                cli,
                config,
                "unsupported" if not isolation[cli]["supported"] else "smoke_not_started",
                isolation[cli]["reason"] or blocked,
            )
            for scenario in scenarios
            for cli in selected
        ]
    report = report_for(
        rows,
        scenarios,
        selected,
        config,
        isolation,
        counts,
        stopped,
        dry_run=args.dry_run,
        blocked=blocked,
    )
    report["metadata"].update(smoke=args.smoke, verification_only=args.verify_isolation)
    js, md = write_report(report, output)
    print(f"Reports: {js} and {md}. Scenario invocations: {report['executed_runs']}.")
    failed_verification = args.verify_isolation and any(
        not info["verified"] for info in isolation.values()
    )
    return 2 if blocked or failed_verification else 0


if __name__ == "__main__":
    raise SystemExit(main())
