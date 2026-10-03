"""Offline CLI wire fixtures and guards. No model, MCP, or subscription calls."""

from __future__ import annotations

import copy
import json
import subprocess
from datetime import datetime
from pathlib import Path

import pytest
import yaml

from qa import tui_harness as harness
from qa import tui_providers as providers
from qa.agent_harness import load_scenarios


@pytest.fixture
def config():
    return yaml.safe_load((harness.HERE / "tui_config.yaml").read_text())


@pytest.fixture
def streams():
    return json.loads((harness.HERE / "fixtures/tui-streams.json").read_text())["samples"]


def text(events):
    return "\n".join(json.dumps(event) for event in events)


def execution(cli="claude", answer="Fixture answer", *, status="completed", limit=None):
    parsed = providers.Transcript(
        final_answer=answer, turns=1, terminal=True, tokens_in=10, tokens_out=4, cost_usd=0.02
    )
    return providers.Execution(parsed, 0, 25.0, status, limit_reason=limit, observed_output=answer)


def isolated():
    return {
        cli: {"supported": True, "verified": True, "reason": None, "canary_runs": 1}
        for cli in providers.CLIS
    }


def scenario(name="budget-approved"):
    return next(row for row in load_scenarios() if row["id"] == name)


@pytest.mark.parametrize(
    "cli,expected",
    [
        ("claude", ["--model", "fable", "--effort", "high", "--output-format", "stream-json"]),
        ("codex", ["-m", "gpt-6.1-sol", "-c", "model_reasoning_effort=max", "--json"]),
        (
            "gemini",
            ["--model", "gemini-3.8-pro", "--output-format", "stream-json", "--extensions", "none"],
        ),
        (
            "grok",
            [
                "-m",
                "grok-4.7",
                "--reasoning-effort",
                "xhigh",
                "--output-format",
                "streaming-messages-json",
            ],
        ),
    ],
)
def test_native_headless_commands(cli, expected, config, tmp_path):
    command = providers.build_command(
        cli,
        config["clis"][cli],
        tmp_path,
        "A prompt with spaces, $HOME and `literal`",
        tmp_path / "mcp.json",
        8,
    )
    assert command[0] == config["clis"][cli]["executable"]
    assert all(value in command for value in expected)
    assert "A prompt with spaces, $HOME and `literal`" in command
    if cli == "codex":
        assert command[0] == "/Applications/ChatGPT.app/Contents/Resources/codex-cli/bin/codex"
        assert all(
            flag in command for flag in ("--ignore-user-config", "--ignore-rules", "--ephemeral")
        )


def test_claude_excludes_instruction_sources_and_builtin_tools(config, tmp_path):
    command = providers.build_command(
        "claude", config["clis"]["claude"], tmp_path, "OK", tmp_path / "mcp.json", 8
    )
    assert command[command.index("--setting-sources") + 1] == ""
    assert command[command.index("--tools") + 1] == ""
    assert command[command.index("--allowedTools") + 1] == "mcp__modelspec__*"
    settings = json.loads(command[command.index("--settings") + 1])
    assert settings["disableAllHooks"] and not settings["autoMemoryEnabled"]
    assert settings["enabledPlugins"] == {}
    assert "--strict-mcp-config" in command and "--disable-slash-commands" in command
    assert "--no-session-persistence" in command
    assert "--safe-mode" not in command  # It also removes explicit HTTP MCP.
    assert "--bare" not in command  # It excludes subscription authentication.


def test_environment_cannot_inherit_vendor_keys_or_agent_customizations(monkeypatch, tmp_path):
    for key in (
        "ANTHROPIC_API_KEY",
        "OPENAI_API_KEY",
        "GEMINI_API_KEY",
        "XAI_API_KEY",
        "ANTHROPIC_AUTH_TOKEN",
        "CODEX_HOME",
        "GROK_HOME",
        "GEMINI_CLI_HOME",
        "CLAUDE_CODE_SIMPLE",
        "NODE_OPTIONS",
        "BASH_ENV",
        "GEMINI_SYSTEM_MD",
    ):
        monkeypatch.setenv(key, "do-not-inherit")
    monkeypatch.setenv("MODELSPEC_API_KEY", "not-a-real-secret")
    env = providers.child_environment("claude", tmp_path, "MODELSPEC_API_KEY")
    assert not any(value == "do-not-inherit" for value in env.values())
    assert env["CLAUDE_CODE_DISABLE_CLAUDE_MDS"] == "1"
    assert env["CLAUDE_CODE_DISABLE_AUTO_MEMORY"] == "1"
    assert env["ENABLE_CLAUDEAI_MCP_SERVERS"] == "false"
    assert env["MODELSPEC_API_KEY"] == "not-a-real-secret"
    assert env["TMPDIR"] == str(tmp_path)
    assert "MODELSPEC_API_KEY" not in providers.child_environment("claude", tmp_path)


def test_connection_secret_is_an_environment_reference_only(monkeypatch):
    monkeypatch.setenv("MODELSPEC_API_KEY", "not-a-real-secret")
    value = providers.mcp_config("https://api.modelspec.dev/mcp", "MODELSPEC_API_KEY", enabled=True)
    assert set(value["mcpServers"]) == {"modelspec"}
    assert value["mcpServers"]["modelspec"]["headers"] == {
        "Authorization": "Bearer ${MODELSPEC_API_KEY}"
    }
    assert "not-a-real-secret" not in json.dumps(value)
    assert providers.mcp_config("https://api.modelspec.dev/mcp", None, enabled=False) == {
        "mcpServers": {}
    }


@pytest.mark.parametrize("cli", ["codex", "gemini", "grok"])
def test_unsupported_never_starts_a_process(cli, config, tmp_path, monkeypatch):
    monkeypatch.setattr(
        providers.subprocess, "run", lambda *a, **k: pytest.fail("Unsafe CLI launched")
    )
    with pytest.raises(ValueError, match="No auth workaround"):
        providers.launch(cli, config, tmp_path, "Do not run", mcp_enabled=True)
    assert not list(tmp_path.iterdir())
    assert harness.verify_isolation(cli, config, tmp_path)["canary_runs"] == 0


@pytest.mark.parametrize(
    "cli,in_tokens,out_tokens,turns",
    [
        ("claude", 60, 7, 3),
        ("codex", 20, 5, 1),
        ("gemini", 30, 9, 3),
        ("grok", 22, 8, 2),
    ],
)
def test_native_streams_capture_order_usage_and_final_answer(
    cli, in_tokens, out_tokens, turns, streams
):
    parsed = providers.parse_transcript(cli, text(streams[cli]))
    assert [call["name"] for call in parsed.tool_calls] == ["vocab", "decide"]
    assert parsed.first_decide_call == 2
    assert parsed.tool_calls[1]["arguments"] == {
        "spec_version": 1,
        "optimize": {"min": "offering.cost_per_task"},
    }
    assert parsed.tool_calls[1]["result_observed"]
    assert not parsed.tool_calls[1]["result"]["isError"]
    assert parsed.final_answer == "Fixture answer"
    assert parsed.turns == turns
    assert parsed.tokens_in == in_tokens and parsed.tokens_out == out_tokens
    assert parsed.terminal and parsed.usage is not None


def test_claude_messages_and_codex_started_completed_are_deduplicated(streams):
    events = copy.deepcopy(streams["claude"])
    events.insert(2, copy.deepcopy(events[1]))
    parsed = providers.parse_transcript("claude", text(events))
    assert len(parsed.tool_calls) == 2
    assert len(providers.parse_transcript("codex", text(streams["codex"])).tool_calls) == 2


def test_single_json_outputs_and_unknown_usage():
    parsed = providers.parse_transcript("claude", '{"type":"result","result":"OK","num_turns":1}')
    assert parsed.terminal and parsed.final_answer == "OK"
    assert parsed.tokens_in is None and parsed.tokens_out is None and parsed.cost_usd is None
    parsed = providers.parse_transcript(
        "gemini",
        '{"response":"OK","stats":{"models":{"x":{"tokens":{"prompt":4,"candidates":2,"thoughts":3},"api":{"totalRequests":1}}}}}',
    )
    assert (parsed.tokens_in, parsed.tokens_out, parsed.turns) == (4, 5, 1)
    assert providers.parse_transcript("codex", "warning\nnot-json").terminal is False


def test_partial_and_failed_calls_retain_observed_evidence(streams):
    partial = providers.parse_transcript("claude", text(streams["claude"][:2]))
    assert len(partial.tool_calls) == 1 and not partial.terminal
    assert partial.tool_calls[0]["result_observed"] is False
    events = copy.deepcopy(streams["codex"])
    completed = next(
        event
        for event in events
        if event.get("item", {}).get("id") == "d" and event["type"] == "item.completed"
    )
    completed["item"]["error"] = {"message": "MCP request failed"}
    completed["item"].pop("result")
    parsed = providers.parse_transcript("codex", text(events))
    assert parsed.tool_calls[1]["result"]["isError"] is True


@pytest.mark.parametrize(
    "message",
    [
        "You've hit your limit · resets 10pm",
        "Rate limit reached",
        "RESOURCE_EXHAUSTED",
        "Quota has been exhausted",
        "usage_limit_reached",
        "Too many requests",
        "out of credits",
    ],
)
def test_usage_limit_messages(message):
    parsed = providers.Transcript(errors=[message])
    assert providers.usage_limit(parsed, "", 1, []) is not None


def test_usage_limit_exit_codes_are_explicit_and_normal_answers_do_not_stop_cli():
    parsed = providers.Transcript(final_answer="The model has a rate limit and monthly quota.")
    assert providers.usage_limit(parsed, "", 1, []) is None
    assert providers.usage_limit(parsed, "", 42, [42]) == "CLI usage-limit exit code 42"
    assert providers.usage_limit(
        providers.Transcript(final_answer="You've hit your limit"), "", 0, []
    )
    # A ModelSpec tool error is not the subscription's vendor quota.
    parsed = providers.parse_transcript(
        "claude",
        text(
            [
                {
                    "type": "user",
                    "message": {
                        "content": [
                            {
                                "type": "tool_result",
                                "tool_use_id": "x",
                                "content": "ModelSpec API rate limit reached",
                                "is_error": True,
                            }
                        ]
                    },
                },
                {"type": "result", "result": "ModelSpec could not answer; its quota is exhausted"},
            ]
        ),
    )
    assert providers.usage_limit(parsed, "", 0, []) is None


@pytest.mark.parametrize(
    "hour,allowed", [(7, True), (8, False), (15, False), (21, False), (22, True), (23, True)]
)
def test_quiet_hours_local_boundaries(hour, allowed):
    now = datetime(2026, 10, 3, hour)
    if allowed:
        harness.quiet_hours_guard(True, False, now)
    else:
        with pytest.raises(ValueError, match="08:00 and 22:00"):
            harness.quiet_hours_guard(True, False, now)
    harness.quiet_hours_guard(True, True, now)
    harness.quiet_hours_guard(False, False, now)


def test_judge_routes_are_cross_family_and_configurable(config):
    for cli in providers.CLIS:
        assert providers.FAMILY[harness.judge_for(cli, config["judges"])] != providers.FAMILY[cli]
    routes = config["judges"] | {"claude": "grok"}
    assert harness.judge_for("claude", routes) == "grok"
    for value in ("claude", "unknown", None):
        with pytest.raises(ValueError, match="different CLI family"):
            harness.judge_for("claude", {"claude": value})


def test_agent_prompt_excludes_ground_truth_and_judge_reuses_rubric():
    case = scenario("recall-q01")
    prompt = harness.scenario_prompt(case)
    assert case["request"] in json.loads(prompt.split("User request:\n")[1])["request"]
    assert (
        '"expected"' not in prompt and '"rubric"' not in prompt and '"fixture_spec"' not in prompt
    )
    judged = harness.judge_prompt(case, {"final_answer": "submitted", "tool_calls": []})
    data = json.loads(judged.split("Submitted data:\n")[1])
    assert data["scenario"]["expected"] == case["expected"]
    assert data["scenario"]["rubric"] == case["rubric"]


def test_isolation_canary_is_planted_outside_workspace_and_checks_all_output(tmp_path):
    marker = "TEST_CANARY_MARKER"
    hook = harness.plant_canary(tmp_path, marker)
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    assert marker in (workspace.parent / "CLAUDE.md").read_text()
    assert marker in (workspace.parent / "AGENTS.md").read_text()
    assert marker in (workspace.parent / ".agents/skills/canary/SKILL.md").read_text()
    good = execution(answer="OK")
    assert harness.canary_passed(good, marker, hook)
    good.observed_output += "\nstderr contains " + marker
    assert not harness.canary_passed(good, marker, hook)
    good.observed_output = "OK"
    hook.touch()
    assert not harness.canary_passed(good, marker, hook)
    hook.unlink()
    assert not harness.canary_passed(execution(answer="", status="cli_error"), marker, hook)
    assert not harness.canary_passed(execution(answer="OK", status="usage_limit"), marker, hook)


@pytest.mark.parametrize(
    "field,value",
    [
        ("skills", ["user-skill"]),
        ("plugins", [{"path": "/user/plugin"}]),
        ("mcp_servers", [{"name": "other", "status": "connected"}]),
        ("tools", ["Bash"]),
    ],
)
def test_startup_inventory_rejects_other_customizations(field, value):
    parsed = providers.Transcript(init={field: value})
    assert providers.isolation_violation(parsed, mcp_enabled=False)
    assert providers.isolation_violation(providers.Transcript(), mcp_enabled=False)
    assert (
        providers.isolation_violation(
            providers.Transcript(
                init={
                    "skills": [],
                    "plugins": [{"path": "builtin"}],
                    "mcp_servers": [],
                    "tools": [],
                }
            ),
            mcp_enabled=False,
        )
        is None
    )


def test_scenario_requires_a_connected_modelspectool_server(streams):
    parsed = providers.parse_transcript("claude", text(streams["claude"]))
    assert providers.isolation_violation(parsed, mcp_enabled=True) is None
    parsed.init["mcp_servers"][0]["status"] = "failed"
    assert (
        providers.isolation_violation(parsed, mcp_enabled=True) == "ModelSpec MCP did not connect"
    )


def test_launch_uses_empty_stdin_and_never_reads_auth(config, tmp_path, monkeypatch, streams):
    observed = {}

    def fake(command, **kwargs):
        observed.update(kwargs)
        assert kwargs["input"] == ""
        assert kwargs["cwd"] == tmp_path
        assert command[0] == config["clis"]["claude"]["executable"]
        return subprocess.CompletedProcess(command, 0, text(streams["claude"]), "")

    monkeypatch.setattr(providers.subprocess, "run", fake)
    original = Path.read_text

    def safe_read(path, *args, **kwargs):
        assert not any(
            name in str(path) for name in ("auth.json", ".claude.json", "accounts", "oauth")
        )
        return original(path, *args, **kwargs)

    monkeypatch.setattr(Path, "read_text", safe_read)
    result = providers.launch("claude", config, tmp_path, "fixture prompt", mcp_enabled=True)
    assert result.status == "completed" and result.exit_code == 0
    assert set(json.loads((tmp_path / "modelspec-mcp.json").read_text())["mcpServers"]) == {
        "modelspec"
    }
    assert observed["capture_output"] and observed["timeout"] == 300


def test_canary_launch_is_non_mcp_and_uses_fresh_workspace(config, tmp_path, monkeypatch):
    seen = []

    def fake(cli, cfg, workspace, prompt, *, mcp_enabled):
        seen.append(workspace)
        assert not mcp_enabled and prompt == "Reply with exactly OK."
        assert not list(workspace.iterdir())
        assert (workspace.parent / "CLAUDE.md").exists()
        return execution(answer="OK")

    monkeypatch.setattr(harness, "launch", fake)
    assert harness.verify_isolation("claude", config, tmp_path)["verified"]
    assert harness.verify_isolation("claude", config, tmp_path)["verified"]
    assert seen[0] != seen[1] and all(not path.exists() for path in seen)


def test_limit_stops_only_the_affected_cli_and_counts_judges(config, tmp_path, monkeypatch):
    calls = []

    def fake(cli, cfg, workspace, prompt, *, mcp_enabled):
        calls.append((cli, mcp_enabled, workspace))
        if cli == "claude":
            return execution(status="usage_limit", limit="weekly usage limit reached")
        return execution(
            answer=json.dumps(
                {
                    "passed": True,
                    "rationale": "fixture",
                    "top_models": [],
                    "answer_kind": "abstain",
                    "missing_capabilities": [],
                }
            )
        )

    config["judges"] = {"claude": "codex", "codex": "gemini", "gemini": "codex", "grok": "codex"}
    monkeypatch.setattr(harness, "launch", fake)
    runner = harness.Runner(config, tmp_path, isolated())
    assert runner.scenario(scenario(), "claude")["status"] == "usage_limit"
    assert runner.scenario(scenario(), "claude")["status"] == "usage_limit_skipped"
    assert runner.scenario(scenario(), "grok")["success"]
    assert [(cli, role) for cli, role, _ in calls] == [
        ("claude", True),
        ("grok", True),
        ("codex", False),
    ]
    assert runner.counts["codex"] == {"agent": 0, "judge": 1}
    assert len({path for _, _, path in calls}) == len(calls)


def test_shared_judge_limit_prevents_further_judging_and_wastes_no_scenario_calls(
    config, tmp_path, monkeypatch
):
    config["max_runs_per_cli"] = 1
    runner = harness.Runner(config, tmp_path, isolated())
    monkeypatch.setattr(
        harness, "launch", lambda *a, **k: execution(status="usage_limit", limit="usage limit")
    )
    runner.invoke("claude", "judge", "judge")
    row = runner.scenario(scenario(), "grok")
    assert row["status"] == "judge_unavailable"
    assert runner.counts["grok"]["agent"] == 0
    runner = harness.Runner(config, tmp_path, isolated())
    monkeypatch.setattr(harness, "launch", lambda *a, **k: execution())
    runner.invoke("claude", "judge", "judge")
    assert runner.refusal("claude")[0] == "max_runs"


def test_judge_preserves_recall_rules_and_failed_evaluations(config, tmp_path, monkeypatch):
    case = scenario("recall-q01")
    replies = iter(
        [
            execution(),
            execution(
                answer=json.dumps(
                    {
                        "passed": True,
                        "rationale": "fixture",
                        "top_models": ["invented/winner"],
                        "answer_kind": "single",
                        "missing_capabilities": [],
                    }
                )
            ),
        ]
    )
    monkeypatch.setattr(harness, "launch", lambda *a, **k: next(replies))
    runner = harness.Runner(config, tmp_path, isolated())
    row = runner.scenario(case, "claude")
    assert row["judge"]["passed"] and row["expected_match"] is False and not row["success"]
    assert row["judge"]["family"] == "openai"
    replies = iter([execution(), execution(answer="not valid judge JSON")])
    row = runner.scenario(case, "claude")
    assert row["evaluation_status"] == "evaluation_error" and not row["success"]


def test_report_uses_api_shape_deduplicates_evidence_and_has_cli_comparison(config, streams):
    parsed = providers.parse_transcript("claude", text(streams["claude"]))
    case = scenario()
    row = harness.execution_row(
        case, "claude", config, providers.Execution(parsed, 0, 50, "completed")
    )
    counts = {cli: {"agent": 0, "judge": 0} for cli in providers.CLIS}
    counts["claude"]["agent"] = 1
    report = harness.report_for([row], [case], ["claude"], config, isolated(), counts, {})
    assert {
        "metadata",
        "budget",
        "overall",
        "per_family",
        "per_agent",
        "per_family_agent",
        "misuse_patterns",
        "gap_list",
        "tool_responses",
        "runs",
        "per_cli",
    } <= report.keys()
    assert report["per_cli"]["claude"]["mean_first_decide_call"] == 2
    assert report["per_cli"]["claude"]["wall_time_p50_ms"] == 50
    assert report["overall"]["success_rate"] == 0  # No judgement is a failure.
    assert report["budget"]["real_spend_usd"] is None
    assert report["budget"]["reported_cost_usd"] == 0.1
    for call in report["runs"][0]["tool_calls"]:
        assert "result" not in call and call["response_ref"] in report["tool_responses"]
    md = harness.markdown(report)
    assert "| CLI | Isolation |" in md and "| claude | verified |" in md
    assert "Fixture answer" not in md


def test_private_output_rejects_repo_symlinks_and_other_worktrees(tmp_path):
    with pytest.raises(ValueError, match="public ModelSpec"):
        harness.private_output(harness.ROOT / "qa/reports/tui")
    link = tmp_path / "public-link"
    link.symlink_to(harness.ROOT, target_is_directory=True)
    with pytest.raises(ValueError, match="public ModelSpec"):
        harness.private_output(link / "qa/new")
    common = subprocess.run(
        ["git", "rev-parse", "--git-common-dir"], capture_output=True, text=True, check=True
    ).stdout.strip()
    if Path(common).is_absolute():
        with pytest.raises(ValueError, match="public ModelSpec worktree"):
            harness.private_output(Path(common).parent / "qa/private-pretender")
    assert harness.private_output(tmp_path / "private-report") == tmp_path / "private-report"


def test_live_report_is_redacted_and_written_only_to_out(config, tmp_path, monkeypatch):
    monkeypatch.setenv("MODELSPEC_API_KEY", "test-modelspec-secret")
    row = harness.empty_row(scenario(), "claude", config, "cli_error")
    row["final_answer"] = "test-modelspec-secret and Bearer hidden-token"
    report = harness.report_for(
        [row],
        [scenario()],
        ["claude"],
        config,
        isolated(),
        {cli: {"agent": 0, "judge": 0} for cli in providers.CLIS},
        {},
    )
    js, md = harness.write_report(report, tmp_path)
    assert "test-modelspec-secret" not in js.read_text()
    assert "hidden-token" not in js.read_text()
    assert js.parent == tmp_path and md.parent == tmp_path
    assert not (tmp_path / "stdout.jsonl").exists()


def test_dry_run_makes_no_cli_or_network_calls(config, tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(harness, "launch", lambda *a, **k: pytest.fail("CLI called during dry-run"))
    assert (
        harness.main(
            [
                "--dry-run",
                "--scenario",
                "budget-approved",
                "--max-runs-per-cli",
                "1",
                "--out",
                str(tmp_path),
            ]
        )
        == 0
    )
    output = capsys.readouterr().out
    line = next(line for line in output.splitlines() if line.startswith('{"cli"'))
    planned = json.loads(line)
    assert planned["cli"] == "claude" and "--strict-mcp-config" in planned["command"]
    assert planned["stdin"] == ""
    assert all(f"{cli}: unsupported" in output for cli in ("codex", "gemini", "grok"))
    report = json.loads(next(tmp_path.glob("*.json")).read_text())
    assert report["executed_runs"] == 0


def test_smoke_is_refused_before_any_cli_if_every_isolation_is_not_supported(tmp_path, monkeypatch):
    monkeypatch.setattr(
        harness, "launch", lambda *a, **k: pytest.fail("Smoke started despite isolation guard")
    )
    assert harness.main(["--smoke", "--max-runs-per-cli", "1", "--out", str(tmp_path)]) == 2
    report = json.loads(next(tmp_path.glob("*.json")).read_text())
    assert report["executed_runs"] == 0 and report["metadata"]["blocked_reason"]
    assert {row["scenario"] for row in report["runs"]} == {"budget-approved"}
    assert sum(info["canary_runs"] for info in report["isolation"].values()) == 0


@pytest.mark.parametrize(
    "updates",
    [
        {"max_runs_per_cli": 0},
        {"concurrency_per_cli": 2},
        {"timeout_seconds": float("inf")},
        {"mcp_url": "https://secret@api.modelspec.dev/mcp"},
        {"mcp_token_env": "OPENAI_API_KEY"},
    ],
)
def test_invalid_or_auth_mixing_config_is_rejected(config, updates):
    config.update(updates)
    with pytest.raises(ValueError):
        harness.validate_config(config)


def test_timeout_keeps_partial_calls_and_stops_on_observed_limit(
    config, tmp_path, monkeypatch, streams
):
    def fake(command, **kwargs):
        raise subprocess.TimeoutExpired(
            command, 1, text(streams["claude"][:2]).encode(), b"weekly usage limit reached"
        )

    monkeypatch.setattr(providers.subprocess, "run", fake)
    result = providers.launch("claude", config, tmp_path, "fixture", mcp_enabled=True)
    assert result.status == "usage_limit" and result.exit_code is None
    assert len(result.transcript.tool_calls) == 1
    assert result.transcript.tool_calls[0]["result_observed"] is False
    assert result.limit_reason == "weekly usage limit reached"


def test_malformed_transcript_is_a_failed_run(config, tmp_path, monkeypatch):
    monkeypatch.setattr(
        providers.subprocess,
        "run",
        lambda command, **kwargs: subprocess.CompletedProcess(
            command, 0, '{"type":"assistant","message":null}', ""
        ),
    )
    result = providers.launch("claude", config, tmp_path, "fixture", mcp_enabled=True)
    assert result.status == "transcript_error" and result.exit_code == 0


def test_quiet_hours_are_checked_for_each_start(config, tmp_path, monkeypatch):
    config["_quiet_hours"] = True
    runner = harness.Runner(config, tmp_path, isolated())

    def blocked(*args, **kwargs):
        raise ValueError("Quiet hours refuse this start")

    monkeypatch.setattr(harness, "quiet_hours_guard", blocked)
    assert runner.refusal("claude") == ("quiet_hours", "Quiet hours refuse this start")
    assert runner.counts["claude"] == {"agent": 0, "judge": 0}


@pytest.mark.parametrize("blocked_start", [3, 4])
def test_entering_quiet_hours_preserves_the_run_report(
    blocked_start, config, tmp_path, monkeypatch
):
    checks, launched = [], []

    def clock_guard(*args):
        checks.append(None)
        if len(checks) >= blocked_start:
            raise ValueError("Quiet hours refuse this start")

    def fake(cli, *args, **kwargs):
        launched.append(cli)
        return execution()

    monkeypatch.setattr(harness, "quiet_hours_guard", clock_guard)
    monkeypatch.setattr(harness, "launch", fake)
    runner = harness.Runner(config, tmp_path, isolated())
    row = runner.scenario(scenario(), "claude")
    assert runner.counts["codex"] == {"agent": 0, "judge": 0}
    assert not row["success"]
    if blocked_start == 3:
        assert row["status"] == "quiet_hours" and launched == []
    else:
        assert row["status"] == "completed" and launched == ["claude"]
        assert row["final_answer"] == "Fixture answer"
        assert row["evaluation_status"] == "judge_unavailable"
        assert row["judge_execution"]["status"] == "quiet_hours"
        assert row["judge_execution"]["wall_time_ms"] is None


def test_report_cannot_follow_a_preexisting_file_symlink(config, tmp_path):
    case = scenario()
    report = harness.report_for(
        [],
        [case],
        ["claude"],
        config,
        isolated(),
        {cli: {"agent": 0, "judge": 0} for cli in providers.CLIS},
        {},
    )
    destination = tmp_path / "other-report"
    destination.write_text("untouched")
    (tmp_path / f"{report['report_date']}-tui-agent-scenarios.json").symlink_to(destination)
    with pytest.raises(ValueError, match="must not be symlinks"):
        harness.write_report(report, tmp_path)
    assert destination.read_text() == "untouched"
