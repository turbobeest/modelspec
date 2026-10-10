"""Measure Claude's treatment of ModelSpec abstentions before shipping variants.

QA only. Production is never changed. After PR A and the plugin PR B are merged
in the QA checkout, the exact orchestrator command for the tuning run is:

    op run --env-file=qa/subscription.env.op -- \
      /Users/terbeest/dev/modelspec/.venv/bin/python -m qa.run_with_modelspec_key \
      ablation --arms baseline v1 v2 v3 v4 combined --set tuning \
      --state-dir /private/tmp/claude-501/m339/ablation-state \
      --out /private/tmp/claude-501/m339/ablation-tuning --port 8765

Certify separate receipts for Claude, Grok and Codex first, without the shared
subscription-jobs directory:

    /Users/terbeest/dev/modelspec/.venv/bin/python -m qa.ablation doctor \
      --arms baseline v1 v2 v3 v4 combined \
      --state-dir /private/tmp/claude-501/m339/ablation-state \
      --out /private/tmp/claude-501/m339/ablation-doctor --port 8765

Doctor checks the Claude agent and its default Grok + Codex judge panel for each
arm. Both judges must agree and pass. Doctor runs subscription canaries. A live
run requires the agent's own funded ModelSpec key. Neither command is part of
unit testing. --dry-run uses the recorded public engine responses and scripted
agent/judge fixtures in memory;
it opens no sockets, starts no containers and certifies no doctor receipts.
Its pass rates are scripted checks, never evidence about agent behavior.

TUNING is ten scenarios used to adjust copy. HOLDOUT is four recall scenarios
that must never tune copy and run only on baseline and combined. A missing
--claude-plugin flag refuses v2 and combined, even during a dry run.
"""

from __future__ import annotations

import argparse
import copy
import gzip
import io
import json
import os
import sys
from contextlib import contextmanager, redirect_stdout
from datetime import date
from pathlib import Path

import httpx
import yaml

from decision.bounded import project
from decision.contract import CONTRACT_VERSION, Decision, ResponseOptions, parse_spec, spec_hash
from decision.summary import summarize
from pipeline.agent_copy import copy as agent_copy
from qa import subscription_jobs, tui_harness
from qa.ablation_proxy import (
    DECIDE_WORKED_EXAMPLE,
    LIMITATIONS,
    OLD_SUMMARY_RULE,
    SUMMARY_RULE,
    UPSTREAM,
    Audit,
    Proxy,
    Variants,
    decision_identity,
    metadata,
    packed,
    private_directory,
    proxy_port,
    request_spec,
    running_proxy,
    sse_event,
    upstream_url,
    write_private,
)
from qa.docker.entrypoint import refuse_vendor_auth
from qa.providers import redact
from qa.run_with_modelspec_key import job_environment
from qa.tui_providers import Execution, parse_transcript

# These sets are disjoint. HOLDOUT must never be used to adjust the copy.
TUNING = (
    "budget-approved",
    "hardware-spark",
    "prompt-code",
    "prompt-maths",
    "prompt-policy",
    "recall-q01",
    "recall-q03",
    "recall-q04",
    "recall-q07",
    "recall-q09",
)
HOLDOUT = ("recall-q02", "recall-q05", "recall-q08", "recall-q10")
ARMS = {
    "baseline": Variants(),
    "v1": Variants(next_move=True),
    "v2": Variants(plugin=True),
    "v3": Variants(worked_example=True),
    "v4": Variants(annotations=True),
    "combined": Variants(True, True, True, True),
}


def supports_plugin(module) -> bool:
    output = io.StringIO()
    with redirect_stdout(output):
        try:
            module.main(["--help"])
        except SystemExit as exc:
            if exc.code != 0:
                return False
    return "--claude-plugin" in output.getvalue()


def select(arms, scenario_set: str, scenarios=None) -> tuple[list[str], list[str]]:
    chosen_arms = list(
        dict.fromkeys(arms or (["baseline", "combined"] if scenario_set == "holdout" else ARMS))
    )
    if scenario_set == "holdout" and set(chosen_arms) - {"baseline", "combined"}:
        raise ValueError("HOLDOUT runs only with baseline and combined")
    allowed = HOLDOUT if scenario_set == "holdout" else TUNING
    chosen_scenarios = list(dict.fromkeys(scenarios or allowed))
    if set(chosen_scenarios) - set(allowed):
        raise ValueError("Scenarios must belong to the selected tuning or holdout set")
    if any(ARMS[arm].plugin for arm in chosen_arms):
        if not supports_plugin(tui_harness) or not supports_plugin(subscription_jobs):
            raise ValueError(
                "v2 and combined require PR B's --claude-plugin modelspec in both harnesses"
            )
    return chosen_arms, chosen_scenarios


def harness_arguments(
    action: str,
    arm: str,
    root: Path,
    state: Path,
    info: dict,
    scenarios: list[str],
    *,
    dry_run=False,
    cli="claude",
) -> list[str]:
    args = [
        action,
        "--cli",
        cli,
        "--out",
        str(root / "report"),
        "--state-dir",
        str(state / arm),
        "--ablation-proxy",
        info["proxy_url"],
        "--ablation-metadata",
        str(root / "proxy" / "ablation.json"),
        "--max-runs-per-cli",
        str(max(32, len(scenarios) * 2)),
    ]
    if ARMS[arm].plugin and cli == "claude":
        args += ["--claude-plugin", "modelspec"]
    if action == "run":
        for scenario in scenarios:
            args += ["--scenario", scenario]
        if dry_run:
            args.append("--dry-run")
    return args


class FixtureReplay:
    """Replay historical 2.10 engine bodies with current additive defaults.

    The identities are synthesized from the MCP defaults for this fixture call.
    This exercises snapshot-pin verification; it does not migrate live data.
    """

    def __init__(self, proxy: Proxy, fixtures: dict, scenarios: list[dict]):
        self.proxy, self.fixtures, self.scenarios = proxy, fixtures, iter(scenarios)
        self.current = None
        self.complete_body = None
        self.call_number = 0

    def transport(self, request: httpx.Request) -> httpx.Response:
        if (
            request.method != "POST"
            or request.url.path != "/v1/decide"
            or self.complete_body is None
        ):
            raise AssertionError("Offline proxy attempted an unexpected request")
        spec = parse_spec(json.loads(request.content), facets=None)
        body = self.complete_body.model_dump(mode="json")
        digest = spec_hash(spec)
        body.update(spec_hash=digest, decision_id=decision_identity(digest, body["snapshot"]))
        return httpx.Response(200, json=body)

    def response(self, method: str, result: dict, params=None, *, sse=False) -> dict:
        self.call_number += 1
        call = {"jsonrpc": "2.0", "id": self.call_number, "method": method}
        if params is not None:
            call["params"] = params
        raw = packed({"jsonrpc": "2.0", "id": self.call_number, "result": result})
        if sse:
            event = sse_event(self.proxy, b"event: message\ndata: " + raw + b"\n\n", call, None)
            raw = event.split(b"data: ", 1)[1].strip()
        else:
            raw, _row = self.proxy.transform(raw, call, None)
        return json.loads(raw)["result"]

    def agent(self, config: dict) -> Execution:
        scenario = next(self.scenarios)
        self.current = self.fixtures["scenarios"][scenario["id"]]["claude"]
        generated = agent_copy()
        self.response(
            "initialize",
            {"instructions": generated["instructions"].replace(SUMMARY_RULE, OLD_SUMMARY_RULE)},
        )
        description = (
            generated["tools"]["decide"]
            .removesuffix(DECIDE_WORKED_EXAMPLE)
            .replace(SUMMARY_RULE, OLD_SUMMARY_RULE)
        )
        self.response(
            "tools/list", {"tools": [{"name": "decide", "description": description}]}, sse=True
        )
        calls = []
        for turn in self.current["turns"]:
            for call in turn["calls"]:
                record = next(
                    self.fixtures["records"][index]
                    for index in self.current["record_indices"]
                    if self.fixtures["records"][index]["name"] == call["name"]
                    and self.fixtures["records"][index]["arguments"] == call["arguments"]
                )
                envelope = copy.deepcopy(record["envelope"])
                if call["name"] == "decide" and envelope["status"] == 200:
                    raw_spec = request_spec(call["arguments"])
                    spec = parse_spec(raw_spec, facets=None)
                    body = envelope["body"] | {
                        "contract_version": CONTRACT_VERSION,
                        "explain": spec.explain,
                    }
                    digest = spec_hash(spec)
                    body.update(
                        spec_hash=digest, decision_id=decision_identity(digest, body["snapshot"])
                    )
                    self.complete_body = Decision.model_validate(body)
                    bounded = project(
                        self.complete_body,
                        ResponseOptions(fields=["model"]),
                        spec=spec,
                        not_applied=[],
                    )
                    bounded.pop("next_move", None)
                    bounded["bounded_version"] = "1.1"
                    bounded["summary_for_user"], bounded["must_mention"] = summarize(
                        self.complete_body, spec
                    )
                    envelope["body"] = bounded
                result = {
                    "content": [{"type": "text", "text": packed(envelope).decode()}],
                    "isError": envelope["status"] >= 400,
                }
                result = self.response(
                    "tools/call", result, {"name": call["name"], "arguments": call["arguments"]}
                )
                calls.append({**call, "result": result})
        turns = self.current["turns"]
        transcript = fixture_transcript(
            "claude",
            calls,
            turns[-1]["text"],
            config["clis"]["claude"]["model"],
            sum(turn["tokens_in"] for turn in turns),
            sum(turn["tokens_out"] for turn in turns),
        )
        return Execution(transcript, 0, 0, "completed")

    def launch(self, cli, config, workspace, prompt, *, mcp_enabled, **kwargs) -> Execution:
        if mcp_enabled:
            if cli != "claude":
                raise AssertionError("Ablation fixtures only run the Claude arm")
            return self.agent(config)
        if self.current is None or cli not in tui_harness.judges_for("claude", config["judges"]):
            raise AssertionError("Ablation fixtures require a judge from the Claude panel")
        judge = self.current["judge"]
        transcript = fixture_transcript(
            cli,
            [],
            judge["text"],
            config["clis"][cli]["model"],
            judge["tokens_in"],
            judge["tokens_out"],
        )
        return Execution(transcript, 0, 0, "completed")

    def runner(self, config, output, scenarios) -> tui_harness.Runner:
        # Fixture evidence is confined to this object and never written as a receipt.
        isolation = {
            cli: {"supported": True, "verified": True, "reason": None}
            for cli in tui_harness.required_clis(["claude"], config)
        }
        return tui_harness.Runner(
            config, output, isolation, launch_fn=self.launch, audit=self.proxy.audit
        )


def fixture_transcript(cli, calls, answer, model, tokens_in, tokens_out):
    events = []
    for call in calls:
        events.append(
            {
                "type": "assistant",
                "message": {
                    "id": call["id"],
                    "content": [
                        {
                            "type": "tool_use",
                            "id": call["id"],
                            "name": "mcp__modelspec__" + call["name"],
                            "input": call["arguments"],
                        }
                    ],
                },
            }
        )
        events.append(
            {
                "type": "user",
                "message": {
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": call["id"],
                            "content": call["result"]["content"],
                            "is_error": call["result"]["isError"],
                        }
                    ]
                },
            }
        )
    events.append(
        {
            "type": "result",
            "result": answer,
            "model": model,
            "total_cost_usd": 0.0,
            "usage": {"input_tokens": tokens_in, "output_tokens": tokens_out},
        }
    )
    return parse_transcript(cli, "\n".join(packed(event).decode() for event in events))


@contextmanager
def dry_proxy(variants: Variants, root: Path, info: dict):
    audit = Audit(root, info)
    proxy = Proxy(variants, audit)
    proxy.client.close()
    try:
        yield proxy
    finally:
        proxy.client.close()
        write_private(root / "counters.json", audit.snapshot())


def applied(arm: str, row: dict) -> bool:
    counts = row.get("proxy_rewrites", {})
    variants = ARMS[arm]
    if (
        counts.get("proxy_error")
        or counts.get("budget_passthrough")
        or counts.get("bounded_fallback")
        or counts.get("candidates_truncated")
    ):
        return False
    if not counts.get("responses"):
        return False
    if variants.next_move and not (
        counts.get("instructions") and counts.get("tools.decide.description")
    ):
        return False
    if variants.worked_example and not counts.get("tools.decide.description"):
        return False
    if variants.annotations and not counts.get("content.user_summary"):
        return False
    if variants.plugin and (row.get("claude_plugin") or {}).get("name") != "modelspec":
        return False
    return True


def combined_report(
    reports: dict,
    audits: dict,
    scenario_set: str,
    scenarios: list[str],
    *,
    dry_run: bool,
    expected_arms=None,
) -> dict:
    cells = []
    rates = {}
    for arm in expected_arms or reports:
        report = reports.get(arm, {})
        rows = {row["scenario"]: row for row in report.get("runs", [])}
        for scenario in scenarios:
            row = rows.get(scenario, {})
            judgement = row.get("judge")
            proof = applied(arm, row)
            cells.append(
                {
                    "arm": arm,
                    "scenario": scenario,
                    "passed": bool(row.get("success")) and proof,
                    "judge_passed": bool(row.get("success")),
                    "judge": {**judgement, "rationale": judgement["rationale"][:300]}
                    if judgement else None,
                    "judges": [
                        {**judge, "rationale": judge["rationale"][:300]}
                        for judge in row.get("judges", [])
                    ],
                    "judge_executions": row.get("judge_executions", []),
                    "variant_applied": proof,
                    "rationale": (row.get("judge") or {}).get(
                        "rationale", row.get("error") or "No judgment"
                    )[:300],
                    "status": row.get("evaluation_status", row.get("status", "not_run")),
                    "ablation": report.get("metadata", {}).get("ablation"),
                    "proxy_rewrites": row.get("proxy_rewrites", {}),
                }
            )
        passed = sum(cell["passed"] for cell in cells if cell["arm"] == arm)
        rates[arm] = {
            "passed": passed,
            "total": len(scenarios),
            "pass_rate": passed / len(scenarios),
        }
    return {
        "mode": "dry-run" if dry_run else "live",
        "scenario_set": scenario_set,
        "scenario_sets": {"tuning": list(TUNING), "holdout": list(HOLDOUT)},
        "evidence_note": "Scripted fixture results; no agent measurement."
        if dry_run
        else "Claude subscription agents, Grok + Codex subscription judge panels, "
        "QA proxy; no deployment.",
        "limitations": LIMITATIONS,
        "arms": rates,
        "runs": cells,
        "proxy": audits,
        "metadata": {
            "judge": {
                arm: report.get("metadata", {}).get("judge") for arm, report in reports.items()
            },
            "ablation": {
                arm: report.get("metadata", {}).get("ablation") for arm, report in reports.items()
            }
        },
    }


def table(report: dict) -> str:
    def cell(text):
        return str(text).replace("|", "\\|").replace("\n", " ").replace("\r", " ")

    lines = [
        "# ModelSpec abstention ablation",
        "",
        report["evidence_note"],
        "",
        f"Scenario set: {report['scenario_set']}. HOLDOUT never tunes copy.",
        "",
        "| Arm | Passed / scenarios | Pass rate |",
        "| --- | ---: | ---: |",
    ]
    for arm, rate in report["arms"].items():
        lines.append(f"| {arm} | {rate['passed']} / {rate['total']} | {rate['pass_rate']:.1%} |")
    lines += [
        "",
        "| Arm | Scenario | Result | Variant applied | Judge verdicts | Aggregate judge pass | "
        "Judge rationale | Proxy rewrites |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for row in report["runs"]:
        counts = ", ".join(f"{key}={value}" for key, value in sorted(row["proxy_rewrites"].items()))
        verdicts = "; ".join(
            f"{judge['cli']}: {'pass' if judge['passed'] else 'fail'}" for judge in row["judges"]
        ) or "No judgment"
        lines.append(
            f"| {row['arm']} | {row['scenario']} | {'pass' if row['passed'] else 'fail'} | "
            f"{row['variant_applied']} | {cell(verdicts)} | {row['judge_passed']} | "
            f"{cell(row['rationale'])} | {cell(counts)} |"
        )
    lines += ["", "Pass requires unanimous judge approval and proven proxy/plugin exposure.", ""]
    lines.extend("- " + text for text in report["limitations"])
    return "\n".join(lines) + "\n"


def write_table(path: Path, report: dict) -> None:
    if path.is_symlink():
        raise ValueError("Ablation table must not be a symlink")
    with path.open("w", encoding="utf-8") as handle:
        path.chmod(0o600)
        handle.write(table(report))


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", nargs="?", choices=("run", "doctor"), default="run")
    parser.add_argument("--arms", nargs="+", choices=ARMS)
    parser.add_argument("--set", choices=("tuning", "holdout"), default="tuning")
    parser.add_argument("--scenario", action="append")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--state-dir", type=Path, required=True)
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--upstream", default=UPSTREAM)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)
    reports, audits = {}, {}
    try:
        refuse_vendor_auth(dict(os.environ))
        arms, scenarios = select(args.arms, args.set, args.scenario)
        proxy_port(f"http://host.docker.internal:{args.port}/mcp")
        upstream_url(args.upstream)
        state = tui_harness.private_output(args.state_dir)
        ordinary = subscription_jobs.DEFAULT_STATE.resolve()
        if state.is_relative_to(ordinary):
            raise ValueError(
                "Ablation must never use the ordinary subscription-jobs state directory"
            )
        if args.action == "doctor" and args.dry_run:
            raise ValueError("Dry runs cannot certify doctor receipts")
        if args.action == "run" and not args.dry_run:
            job_environment(dict(os.environ))
        if not args.dry_run:
            state = private_directory(state)
        output = private_directory(args.out)
        fixtures = (
            json.loads(gzip.decompress((tui_harness.HERE / "fixtures/replay.json.gz").read_bytes()))
            if args.dry_run
            else None
        )
        for arm in arms:
            root = private_directory(output / arm)
            variants = ARMS[arm]
            info = metadata(variants, f"http://host.docker.internal:{args.port}/mcp", args.upstream)
            context = (
                dry_proxy(variants, root / "proxy", info)
                if args.dry_run
                else running_proxy(variants, root / "proxy", port=args.port, upstream=args.upstream)
            )
            mode = "fixtures" if args.dry_run else "subscription"
            print(f"Ablation arm {arm}: {args.action}, {mode}.", flush=True)
            with context as proxy:
                if args.action == "doctor":
                    config = yaml.safe_load((tui_harness.HERE / "tui_config.yaml").read_text())
                    for cli in tui_harness.required_clis(["claude"], config):
                        code = tui_harness.main(
                            harness_arguments("doctor", arm, root, state, info, scenarios, cli=cli)
                        )
                        if code:
                            raise ValueError(f"{arm}: {cli} doctor failed; receipts remain private")
                    continue
                extra = {"ablation_audit": proxy.audit}
                if args.dry_run:
                    catalogue = tui_harness.load_scenarios()
                    selected = [scenario for scenario in catalogue if scenario["id"] in scenarios]
                    replay = FixtureReplay(proxy, fixtures, selected)
                    proxy.client = httpx.Client(
                        transport=httpx.MockTransport(replay.transport), trust_env=False
                    )
                    extra["fixture_runner_factory"] = replay.runner
                code = tui_harness.main(
                    harness_arguments(
                        "run", arm, root, state, info, scenarios, dry_run=args.dry_run
                    ),
                    **extra,
                )
                report_path = (
                    root / "report" / f"{date.today().isoformat()}-tui-agent-scenarios.json"
                )
                reports[arm] = json.loads(report_path.read_text())
                audits[arm] = proxy.audit.snapshot()
                if code or audits[arm]["counters"].get("proxy_error"):
                    raise ValueError(
                        f"{arm}: harness or proxy failed; inspect the private report and counters"
                    )
        if args.action == "doctor":
            print(f"Ablation doctor receipts: {state}")
            return 0
        report = combined_report(
            reports, audits, args.set, scenarios, dry_run=args.dry_run, expected_arms=arms
        )
        write_private(output / "ablation.json", report)
        markdown = output / "ablation.md"
        write_table(markdown, report)
        print(f"Combined ablation report: {output / 'ablation.json'} and {markdown}")
        return 0
    except (ValueError, OSError, AssertionError, httpx.HTTPError, SystemExit) as exc:
        if reports:
            report = combined_report(
                reports, audits, args.set, scenarios, dry_run=args.dry_run, expected_arms=arms
            )
            report["incomplete"] = True
            write_private(output / "ablation.json", report)
            write_table(output / "ablation.md", report)
        reason = (
            "Harness arguments or configuration were refused"
            if isinstance(exc, SystemExit)
            else str(exc)
        )
        print("Ablation refused/failed: " + redact(reason), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
