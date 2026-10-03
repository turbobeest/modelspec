"""Offline CLI wire fixtures and guards. No model, MCP, or subscription calls."""

from __future__ import annotations

import builtins
import copy
import io
import json
import os
import re
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

import pytest
import yaml

from qa import tui_harness as harness
from qa import tui_homes as homes
from qa import tui_isolation as isolation
from qa import tui_providers as providers
from qa.agent_harness import load_scenarios


@pytest.fixture(autouse=True)
def deny_credential_access(monkeypatch):
    denied = re.compile(
        r"\.codex[/\\]auth|auth\.json|\.credentials|keychain|\.claude\.json|"
        r"oauth|google_accounts|mcp_credentials|\.netrc|\.aws[/\\]credentials|"
        r"id_rsa|id_ed25519|[/\\]tokens?\.(?:json|db)",
        re.I,
    )

    def check(value):
        if not isinstance(value, (str, bytes, os.PathLike)) and hasattr(value, "name"):
            value = value.name
        if isinstance(value, (str, bytes, os.PathLike)):
            path = os.fsdecode(value)
            assert not denied.search(path), f"Credential access attempted: {path}"
            assert not denied.search(str(Path(path).resolve())), "Credential alias accessed"

    def wrap(original, *, copying=False):
        def guarded(*args, **kwargs):
            for value in args[:2] if copying else args[:1]:
                check(value)
            for key in ("file", "path", "src", "dst", "fsrc", "fdst"):
                if key in kwargs:
                    check(kwargs[key])
            return original(*args, **kwargs)

        return guarded

    for owner, names in (
        (builtins, ("open",)),
        (io, ("open",)),
        (Path, ("open", "read_text", "read_bytes")),
        (os, ("open",)),
    ):
        for name in names:
            monkeypatch.setattr(owner, name, wrap(getattr(owner, name)))
    for name in dir(shutil):
        if name.startswith("copy") and callable(getattr(shutil, name)):
            monkeypatch.setattr(shutil, name, wrap(getattr(shutil, name), copying=True))


def allow_launch(config, clis=providers.CLIS):
    for cli in clis:
        home = homes.require_setup(cli, config)
        receipt = {
            "schema": 1,
            "identity": homes.isolation_identity(cli, config),
            "supported": True,
            "verified": True,
            "status": "verified",
            "reason": None,
            "positive_control": {
                loc: dict.fromkeys(isolation.PROBES, True) for loc in isolation.LOCATIONS
            },
            "isolated_control": dict.fromkeys(isolation.LOCATIONS, True),
            "canary_runs": 4,
        }
        isolation.receipt_file(home).write_text(json.dumps(receipt))


@pytest.fixture
def config(tmp_path):
    value = yaml.safe_load((harness.HERE / "tui_config.yaml").read_text())
    binary = tmp_path / "fake-cli"
    binary.write_text("#!/bin/sh\nexit 99\n")
    binary.chmod(0o700)
    for cli, profile in value["clis"].items():
        profile["harness_home"] = str(tmp_path / cli / "home")
        profile["executable"] = str(binary)
        homes.setup_home(cli, value)
    return value


@pytest.fixture
def streams():
    return json.loads((harness.HERE / "fixtures/tui-streams.json").read_text())["samples"]


def text(events):
    return "\n".join(json.dumps(event) for event in events)


def execution(cli="claude", answer="Fixture answer", *, status="completed", limit=None):
    parsed = providers.Transcript(
        final_answer=answer,
        turns=1,
        terminal=True,
        tokens_in=10,
        tokens_out=4,
        cost_usd=0.02,
        init={"skills": [], "plugins": [], "mcp_servers": [], "tools": [], "apiKeySource": "none"},
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
    (tmp_path / "mcp.json").write_text(homes.home_config(cli, config))
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


def test_environment_cannot_inherit_vendor_keys_or_agent_customizations(
    config, monkeypatch, tmp_path
):
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
    env = providers.child_environment(
        "claude", tmp_path, "MODELSPEC_API_KEY", settings=config["clis"]["claude"]
    )
    assert not any(value == "do-not-inherit" for value in env.values())
    assert env["CLAUDE_CODE_DISABLE_CLAUDE_MDS"] == "1"
    assert env["CLAUDE_CODE_DISABLE_AUTO_MEMORY"] == "1"
    assert env["ENABLE_CLAUDEAI_MCP_SERVERS"] == "false"
    assert env["MODELSPEC_API_KEY"] == "not-a-real-secret"
    assert env["TMPDIR"] == str(tmp_path)
    assert "MODELSPEC_API_KEY" not in providers.child_environment(
        "claude", tmp_path, settings=config["clis"]["claude"]
    )


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


@pytest.mark.parametrize("cli", providers.CLIS)
def test_unsupported_never_starts_a_process(cli, config, tmp_path, monkeypatch):
    monkeypatch.setattr(
        providers.subprocess, "run", lambda *a, **k: pytest.fail("Unsafe CLI launched")
    )
    config["_force"] = True
    config["clis"][cli]["eligible"] = True
    config["clis"][cli]["isolation_supported"] = True
    with pytest.raises(ValueError, match="doctor --cli"):
        providers.launch(cli, config, tmp_path, "Do not run", mcp_enabled=True)
    assert not (tmp_path / "modelspec-mcp.json").exists()
    assert not isolation.isolation_result(cli, config)["supported"]


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


@pytest.mark.parametrize("cli", providers.CLIS)
@pytest.mark.parametrize("location", isolation.LOCATIONS)
def test_canary_uses_native_cwd_and_config_home_paths(cli, location, config, tmp_path):
    _, config_home = homes.home_paths(cli, config["clis"][cli])
    root = tmp_path if location == "cwd" else config_home
    files, hook, mcp, mcp_file = isolation.canary_files(cli, config, root, "TEST_CANARY_MARKER")
    backups = tmp_path / "backups"
    backups.mkdir()
    with isolation.planted_canary(files, backups):
        assert all(path.exists() for path in files)
        assert mcp_file.exists()
        native = root if location == "config_home" else root / config["clis"][cli]["config_dir"]
        if cli == "claude":
            assert (root / "CLAUDE.md").exists()
            assert (native / "skills/model301_canary/SKILL.md").exists()
            assert (native / "settings.json").exists()
            assert (root / ".mcp.json").exists()
        good = execution(answer="OK")
        assert isolation.canary_passed(good, cli, "TEST_CANARY_MARKER", hook, mcp)
        good.observed_output += "\nstderr contains TEST_CANARY_MARKER"
        assert not isolation.canary_passed(good, cli, "TEST_CANARY_MARKER", hook, mcp)
        good.observed_output = "OK"
        hook.touch()
        assert not isolation.canary_passed(good, cli, "TEST_CANARY_MARKER", hook, mcp)
        hook.unlink()
        mcp.touch()
        assert not isolation.canary_passed(good, cli, "TEST_CANARY_MARKER", hook, mcp)
        mcp.unlink()
        assert not isolation.canary_passed(
            execution(answer="OK", status="usage_limit"), cli, "TEST_CANARY_MARKER", hook, mcp
        )


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


@pytest.mark.parametrize("key", ["skills", "plugins", "mcp_servers", "tools"])
@pytest.mark.parametrize("value", ["absent", None, {}, ""])
def test_inventory_missing_or_malformed_fields_fail_closed(key, value):
    parsed = execution().transcript
    if value == "absent":
        del parsed.init[key]
    else:
        parsed.init[key] = value
    assert key in providers.isolation_violation(parsed, mcp_enabled=False)


@pytest.mark.parametrize(
    "event",
    [
        {"type": "system", "subtype": "hook_started", "hook_name": "SessionStart"},
        {"type": "system", "subtype": "hook_response", "output": "{}"},
        {"type": "init", "hooks": [{"event": "SessionStart"}]},
        {"type": "system", "subtype": "init", "diagnostics": {"hookEvents": ["SessionStart"]}},
        {"type": "hook_start", "name": "SessionStart"},
    ],
)
def test_init_and_system_hook_events_are_violations(event):
    parsed = providers.parse_transcript("claude", text([execution().transcript.init, event]))
    assert providers.isolation_violation(parsed, mcp_enabled=False) == "CLI emitted a hook event"


@pytest.mark.parametrize("source", [None, "apiKeyHelper", "user", "ANTHROPIC_API_KEY", "api_key"])
def test_claude_refuses_missing_or_api_key_auth(source, config, tmp_path, monkeypatch, streams):
    allow_launch(config, ("claude",))
    events = copy.deepcopy(streams["claude"])
    if source is None:
        del events[0]["apiKeySource"]
    else:
        events[0]["apiKeySource"] = source
    monkeypatch.setattr(
        providers.subprocess,
        "run",
        lambda command, **kwargs: subprocess.CompletedProcess(command, 0, text(events), ""),
    )
    result = providers.launch("claude", config, tmp_path, "fixture", mcp_enabled=True)
    assert result.status == "isolation_failed" and "subscription" in result.error


def test_hook_events_on_stderr_refuse_launch(config, tmp_path, monkeypatch, streams):
    allow_launch(config, ("claude",))
    monkeypatch.setattr(
        providers.subprocess,
        "run",
        lambda command, **kwargs: subprocess.CompletedProcess(
            command, 0, text(streams["claude"]), '{"type":"system","subtype":"hook_response"}'
        ),
    )
    result = providers.launch("claude", config, tmp_path, "fixture", mcp_enabled=True)
    assert result.status == "isolation_failed" and result.error == "CLI emitted a hook event"


@pytest.mark.parametrize("failure", ["exit", "timeout", "usage_limit"])
@pytest.mark.parametrize("unsafe", ["hooks", "inventory", "authentication"])
def test_unsafe_startup_revokes_eligibility_even_when_cli_fails(
    failure, unsafe, config, tmp_path, monkeypatch, streams
):
    allow_launch(config, ("claude",))
    events = copy.deepcopy(streams["claude"])
    stderr = ""
    if unsafe == "hooks":
        stderr = '{"type":"system","subtype":"hook_response"}'
        expected = "CLI emitted a hook event"
    elif unsafe == "inventory":
        del events[0]["skills"]
        expected = "CLI startup inventory omitted or malformed skills"
    else:
        events[0]["apiKeySource"] = "ANTHROPIC_API_KEY"
        expected = "Claude did not attest subscription authentication in init.apiKeySource"
    if failure == "usage_limit":
        stderr += "\nweekly usage limit reached"

    def fake(command, **kwargs):
        if failure == "timeout":
            raise subprocess.TimeoutExpired(command, 1, text(events).encode(), stderr.encode())
        return subprocess.CompletedProcess(command, 1, text(events), stderr)

    monkeypatch.setattr(providers.subprocess, "run", fake)
    result = providers.launch("claude", config, tmp_path, "fixture", mcp_enabled=True)
    assert result.status == ("usage_limit" if failure == "usage_limit" else "isolation_failed")
    assert result.error == expected
    assert not isolation.isolation_result("claude", config)["verified"]
    monkeypatch.setattr(
        providers.subprocess, "run", lambda *a, **k: pytest.fail("Revoked CLI launched again")
    )
    with pytest.raises(ValueError, match="doctor --cli"):
        providers.launch("claude", config, tmp_path, "fixture", mcp_enabled=True)


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
    allow_launch(config)
    result = providers.launch("claude", config, tmp_path, "fixture prompt", mcp_enabled=True)
    assert result.status == "completed" and result.exit_code == 0
    assert set(json.loads((tmp_path / "modelspec-mcp.json").read_text())["mcpServers"]) == {
        "modelspec"
    }
    assert observed["capture_output"] and observed["timeout"] == 300
    home, config_home = homes.home_paths("claude", config["clis"]["claude"])
    assert observed["env"]["HOME"] == str(home)
    assert observed["env"]["CLAUDE_CONFIG_DIR"] == str(config_home)


@pytest.mark.parametrize("cli", providers.CLIS)
def test_doctor_requires_positive_controls_and_isolated_inventory(
    cli, config, tmp_path, monkeypatch
):
    seen = []

    def fake(name, cfg, workspace, prompt, *, mcp_enabled, isolated=True, probe_mcp=None):
        assert name == cli and not mcp_enabled and prompt == "Reply with exactly OK."
        seen.append((workspace, isolated))
        if isolated:
            return execution(answer="OK")
        root = probe_mcp.parent
        if cli != "claude":
            root = root if root == homes.home_paths(cli, cfg["clis"][cli])[1] else root.parent
        instruction = next(path for path in root.iterdir() if path.name.endswith(".md"))
        marker = re.search(r"MODEL301_CANARY_\w+", instruction.read_text())[0]
        (root / "model301-hook-fired").touch()
        (root / "model301-mcp-fired").touch()
        result = execution(answer=marker)
        result.transcript.init["skills"] = ["model301_canary"]
        return result

    monkeypatch.setattr(isolation, "_execute", fake)
    result = harness.verify_isolation(cli, config, tmp_path)
    assert result["verified"] and result["supported"] and result["canary_runs"] == 4
    assert [mode for _, mode in seen] == [False, True, False, True]
    assert seen[0][0] == seen[1][0] and seen[2][0] == seen[3][0]
    assert seen[0][0] != seen[2][0] and all(not path.exists() for path, _ in seen)
    assert isolation.isolation_result(cli, config)["verified"]
    assert isolation.isolation_result(cli, config)["canary_runs"] == 0

    monkeypatch.setattr(isolation, "_execute", lambda *a, **k: execution(answer="OK"))
    result = harness.verify_isolation(cli, config, tmp_path)
    assert not result["supported"] and result["status"] == "unproven"
    assert not isolation.isolation_result(cli, config)["verified"]


@pytest.mark.parametrize("key", ["skills", "plugins", "mcp_servers", "tools"])
def test_doctor_never_accepts_a_vacuous_control_or_incomplete_inventory(
    key, config, tmp_path, monkeypatch
):
    # Even a control that proves all probe types cannot rescue a missing negative inventory.
    monkeypatch.setattr(
        isolation, "positive_evidence", lambda *args: dict.fromkeys(isolation.PROBES, True)
    )

    def fake(*args, **kwargs):
        result = execution(answer="OK")
        del result.transcript.init[key]
        return result

    monkeypatch.setattr(isolation, "_execute", fake)
    result = harness.verify_isolation("claude", config, tmp_path)
    assert result["status"] == "unproven" and not result["supported"]


def test_doctor_stops_immediately_on_vendor_limit_and_revokes_previous_pass(
    config, tmp_path, monkeypatch
):
    allow_launch(config)
    calls = []

    def fake(*args, **kwargs):
        calls.append(kwargs["isolated"])
        return execution(answer="OK", status="usage_limit", limit="weekly usage limit reached")

    monkeypatch.setattr(isolation, "_execute", fake)
    result = harness.verify_isolation("claude", config, tmp_path)
    assert result["status"] == "usage_limit" and result["canary_runs"] == 1
    assert calls == [False] and not isolation.isolation_result("claude", config)["supported"]
    _, config_home = homes.home_paths("claude", config["clis"]["claude"])
    assert not (config_home / "CLAUDE.md").exists()
    assert not (config_home.parent.parent / "tui-doctor.lock").exists()


def test_bad_startup_evidence_revokes_a_pass_and_stops_further_family_starts(
    config, tmp_path, monkeypatch, streams
):
    allow_launch(config)
    events = copy.deepcopy(streams["claude"])
    del events[0]["plugins"]
    calls = []

    def fake(command, **kwargs):
        calls.append(command)
        return subprocess.CompletedProcess(command, 0, text(events), "")

    monkeypatch.setattr(providers.subprocess, "run", fake)
    runner = harness.Runner(config, tmp_path, isolated())
    result = runner.invoke("claude", "fixture", "agent")
    assert result.status == "isolation_failed"
    assert runner.refusal("claude")[0] == "unsupported"
    assert not isolation.isolation_result("claude", config)["supported"]
    with pytest.raises(ValueError):
        providers.launch("claude", config, tmp_path, "fixture", mcp_enabled=True)
    assert len(calls) == 1


def test_doctor_restores_existing_config_without_reading_it(config, tmp_path, monkeypatch):
    _, config_home = homes.home_paths("gemini", config["clis"]["gemini"])
    settings = config_home / "settings.json"
    settings.write_text('"existing config must never be opened"')
    original = Path.open

    def guarded(path, *args, **kwargs):
        mode = args[0] if args else kwargs.get("mode", "r")
        assert path != settings or mode == "x"
        return original(path, *args, **kwargs)

    with monkeypatch.context() as patch:
        patch.setattr(Path, "open", guarded)
        patch.setattr(isolation, "_execute", lambda *a, **k: execution(answer="OK"))
        assert harness.verify_isolation("gemini", config, tmp_path)["status"] == "unproven"
    assert settings.read_text() == '"existing config must never be opened"'
    assert not (config_home / "skills/model301_canary").exists()


@pytest.mark.parametrize("change", ["binary", "profile", "receipt", "adapter"])
def test_doctor_receipt_is_bound_to_binary_profile_and_adapter(
    change, config, tmp_path, monkeypatch
):
    allow_launch(config)
    assert isolation.isolation_result("claude", config)["verified"]
    if change == "binary":
        Path(config["clis"]["claude"]["executable"]).write_text("new binary build")
    elif change == "profile":
        config["clis"]["claude"]["model"] = "a different model"
    elif change == "adapter":
        monkeypatch.setattr(isolation, "isolation_identity", lambda *a: "new adapter")
    else:
        home = homes.require_setup("claude", config)
        data = json.loads(isolation.receipt_file(home).read_text())
        del data["positive_control"]["cwd"]["hooks"]
        isolation.receipt_file(home).write_text(json.dumps(data))
    assert not isolation.isolation_result("claude", config)["supported"]
    monkeypatch.setattr(providers.subprocess, "run", lambda *a, **k: pytest.fail("gate bypassed"))
    with pytest.raises(ValueError, match="doctor --cli"):
        providers.launch("claude", config, tmp_path, "fixture", mcp_enabled=False)


@pytest.mark.parametrize("cli", providers.CLIS)
def test_native_home_overrides_exclude_real_home(cli, config, tmp_path, monkeypatch):
    real_home = tmp_path / "real-home"
    real_home.mkdir()
    monkeypatch.setenv("HOME", str(real_home))
    env = providers.child_environment(cli, tmp_path, settings=config["clis"][cli])
    home, config_home = homes.home_paths(cli, config["clis"][cli])
    assert env["HOME"] == str(home)
    assert env[homes.HOME_VARIABLES[cli]] == str(home if cli == "gemini" else config_home)
    assert str(real_home) not in env.values()
    assert env["XDG_CONFIG_HOME"].startswith(str(home))


@pytest.mark.parametrize("cli", providers.CLIS)
def test_setup_creates_only_native_modelspectool_config_and_prints_login(
    cli, config, tmp_path, monkeypatch, capsys
):
    config["clis"][cli]["harness_home"] = str(tmp_path / f"new-{cli}" / "home")
    config_path = tmp_path / "setup.yaml"
    config_path.write_text(yaml.safe_dump(config))
    monkeypatch.setattr(providers.subprocess, "run", lambda *a, **k: pytest.fail("login executed"))
    monkeypatch.setattr(harness, "private_output", lambda p: p)
    assert harness.main(["setup", "--cli", cli, "--config", str(config_path)]) == 0
    output = capsys.readouterr().out
    assert homes.login_command(cli, config) in output
    assert "env -i" in output
    home, config_home = homes.home_paths(cli, config["clis"][cli])
    files = [p for p in home.rglob("*") if p.is_file()]
    assert files == [homes.config_file(cli, config_home)]
    assert "modelspec" in files[0].read_text()
    assert not isolation.isolation_result(cli, config)["supported"]
    # A second setup leaves state created by the CLI untouched.
    unknown = home / "opaque-cli-state"
    unknown.write_bytes(b"do not open or overwrite")
    homes.setup_home(cli, config)
    assert unknown.read_bytes() == b"do not open or overwrite"


def test_setup_refuses_populated_or_real_or_public_homes(config, tmp_path):
    profile = config["clis"]["codex"]
    profile["harness_home"] = str(Path.home())
    with pytest.raises(ValueError, match="dedicated"):
        homes.setup_home("codex", config)
    profile["harness_home"] = str(harness.ROOT / "test-home")
    with pytest.raises(ValueError, match="public"):
        homes.setup_home("codex", config)
    populated = tmp_path / "existing-home"
    populated.mkdir()
    (populated / "untouched").write_text("existing")
    profile["harness_home"] = str(populated)
    with pytest.raises(ValueError, match="empty dedicated"):
        homes.setup_home("codex", config)


def test_binary_path_is_resolved_with_environment_override(config, tmp_path, monkeypatch):
    binary = tmp_path / "override-cli"
    binary.write_text("#!/bin/sh\nexit 1\n")
    binary.chmod(0o700)
    monkeypatch.setenv("TUI_CLAUDE_BIN", str(binary))
    assert homes.resolve_executable("claude", config["clis"]["claude"]) == str(binary)


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
    monkeypatch.setenv("MODELSPEC_OTHER_TOKEN", 'test-other-secret\nwith "quotes"')
    monkeypatch.setenv("MODELSPEC_FLAG", "1")
    row = harness.empty_row(scenario(), "claude", config, "cli_error")
    row["final_answer"] = "test-modelspec-secret and Bearer hidden-token"
    row["error"] = 'test-other-secret\nwith "quotes"'
    report = harness.report_for(
        [row],
        [scenario()],
        ["claude"],
        config,
        isolated(),
        {cli: {"agent": 0, "judge": 0} for cli in providers.CLIS},
        {},
    )
    report["diagnostics"] = {"test-modelspec-secret": "private"}
    js, md = harness.write_report(report, tmp_path)
    assert "test-modelspec-secret" not in js.read_text()
    assert "hidden-token" not in js.read_text()
    assert "test-other-secret" not in js.read_text() and "test-other-secret" not in md.read_text()
    assert json.loads(js.read_text())["metadata"]["concurrency_per_cli"] == 1
    assert js.parent == tmp_path and md.parent == tmp_path
    assert not (tmp_path / "stdout.jsonl").exists()


def test_dry_run_makes_no_cli_or_network_calls(config, tmp_path, monkeypatch, capsys):
    allow_launch(config, ("claude",))
    config_path = tmp_path / "config.yaml"
    config_path.write_text(yaml.safe_dump(config))
    monkeypatch.setattr(harness, "launch", lambda *a, **k: pytest.fail("CLI called during dry-run"))
    assert (
        harness.main(
            [
                "--dry-run",
                "--config",
                str(config_path),
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
    report = json.loads(next(tmp_path.glob("*-tui-agent-scenarios.json")).read_text())
    assert report["executed_runs"] == 0


def test_main_runs_scenario_and_cross_family_judge_with_fake_launch(
    config, tmp_path, monkeypatch, capsys
):
    allow_launch(config, ("claude", "codex"))
    cfg = tmp_path / "live.yaml"
    cfg.write_text(yaml.safe_dump(config))
    seen = []
    judgement = {
        "passed": True,
        "rationale": "fixture",
        "top_models": [],
        "answer_kind": "abstain",
        "missing_capabilities": [],
    }

    def fake(cli, cfg, workspace, prompt, *, mcp_enabled):
        seen.append((cli, mcp_enabled, workspace, prompt))
        return execution(cli, "Fixture answer" if mcp_enabled else json.dumps(judgement))

    monkeypatch.setattr(harness, "launch", fake)
    monkeypatch.setattr(isolation, "_execute", lambda *a, **k: pytest.fail("unexpected doctor"))
    result = harness.main(
        [
            "--config",
            str(cfg),
            "--cli",
            "claude",
            "--scenario",
            "budget-approved",
            "--out",
            str(tmp_path),
        ]
    )
    assert result == 0
    assert [(cli, mcp) for cli, mcp, _, _ in seen] == [("claude", True), ("codex", False)]
    assert "Fixture answer" in seen[1][3]
    assert all(not workspace.exists() for _, _, workspace, _ in seen)
    report = json.loads(next(tmp_path.glob("*-tui-agent-scenarios.json")).read_text())
    assert report["executed_runs"] == 1 and report["runs"][0]["status"] == "completed"
    assert report["runs"][0]["judge"]["cli"] == "codex"
    assert report["cli_invocations"]["claude"] == {"agent": 1, "judge": 0}
    assert report["cli_invocations"]["codex"] == {"agent": 0, "judge": 1}
    assert report["isolation"]["claude"]["canary_runs"] == 0
    assert "Scenario invocations: 1" in capsys.readouterr().out


def test_main_doctor_command_reports_unproven_and_cannot_enable_a_cli(
    config, tmp_path, monkeypatch
):
    cfg = tmp_path / "doctor.yaml"
    cfg.write_text(yaml.safe_dump(config))
    monkeypatch.setattr(isolation, "_execute", lambda *a, **k: execution(answer="OK"))
    assert (
        harness.main(
            ["doctor", "--cli", "claude", "--config", str(cfg), "--out", str(tmp_path), "--force"]
        )
        == 2
    )
    report = json.loads(next(tmp_path.glob("*-tui-agent-scenarios.json")).read_text())
    assert report["executed_runs"] == 0 and report["metadata"]["verification_only"]
    assert report["isolation"]["claude"]["status"] == "unproven"
    assert not isolation.isolation_result("claude", config)["supported"]


def test_tui_sources_contain_no_credential_path_literals():
    forbidden = re.compile(
        r"\.codex[/\\]auth|auth\.json|\.credentials|Keychain|\.claude\.json|"
        r"oauth_creds|google_accounts|mcp_credentials|\.netrc|id_rsa|id_ed25519|"
        r"\.aws[/\\]credentials|[/\\]tokens?\.(?:json|db)",
        re.I,
    )
    for source in harness.HERE.glob("tui_*.py"):
        assert not forbidden.search(source.read_text()), source.name


@pytest.mark.parametrize(
    "path", ["auth.json", ".codex/auth/session", ".credentials/session", "Keychain/session"]
)
@pytest.mark.parametrize(
    "reader",
    [
        lambda p: builtins.open(p),
        lambda p: io.open(p),  # noqa: UP020 -- exercise the separate io.open guard
        lambda p: p.open(),
        lambda p: p.read_text(),
        lambda p: p.read_bytes(),
        lambda p: os.open(p, os.O_RDONLY),
        lambda p: shutil.copy(p, str(p) + "-copy"),
        lambda p: shutil.copy2(p, str(p) + "-copy"),
        lambda p: shutil.copyfile(p, str(p) + "-copy"),
        lambda p: shutil.copytree(p, str(p) + "-copy"),
        lambda p: shutil.copyfileobj(type("FakeFile", (), {"name": str(p)})(), io.BytesIO()),
    ],
)
def test_no_auth_guard_covers_every_read_and_copy_entry_point(reader, path, tmp_path):
    with pytest.raises(AssertionError, match="Credential access attempted"):
        reader(tmp_path / path)


def test_smoke_is_refused_before_any_cli_if_every_isolation_is_not_supported(tmp_path, monkeypatch):
    monkeypatch.setattr(
        harness, "launch", lambda *a, **k: pytest.fail("Smoke started despite isolation guard")
    )
    assert harness.main(["--smoke", "--max-runs-per-cli", "1", "--out", str(tmp_path)]) == 2
    report = json.loads(next(tmp_path.glob("*-tui-agent-scenarios.json")).read_text())
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
    allow_launch(config)
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
    allow_launch(config)
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
