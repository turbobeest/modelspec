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
import sys
from datetime import datetime
from pathlib import Path

import pytest
import yaml

from qa import tui_auth as auth
from qa import tui_docker as docker
from qa import tui_harness as harness
from qa import tui_homes as homes
from qa import tui_inventory as inventory
from qa import tui_isolation as isolation
from qa import tui_providers as providers
from qa.agent_harness import load_scenarios
from qa.docker import entrypoint
from qa.subscription_jobs import decide_health, require_funded_key

IMAGE_IDENTITY = docker.image_identity


@pytest.fixture(autouse=True)
def deny_credential_access(monkeypatch):
    for name in tuple(os.environ):
        if entrypoint.VENDOR_ENV.search(name) and not name.startswith("MODELSPEC_"):
            monkeypatch.delenv(name)
    original_open = builtins.open
    denied = re.compile(
        r"\.codex[/\\]auth|auth\.json|\.credentials|keychain|\.claude\.json|"
        r"oauth|google_accounts|mcp_credentials|\.netrc|\.aws[/\\]credentials|"
        r"id_rsa|id_ed25519|[/\\]tokens?\.(?:json|db)|"
        r"[/\\]modelspec-harness-(?:claude|codex|gemini|grok)-home(?:[/\\:]|$)|"
        r"[/\\]home[/\\]agent(?:[/\\]|$)|[/\\]var[/\\]lib[/\\]docker[/\\]volumes",
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
            for key in ("file", "path", "src", "dst", "fsrc", "fdst", "target"):
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
        if (name.startswith("copy") or name == "move") and callable(getattr(shutil, name)):
            monkeypatch.setattr(shutil, name, wrap(getattr(shutil, name), copying=True))
    for owner in (os, Path):
        monkeypatch.setattr(owner, "rename", wrap(getattr(owner, "rename"), copying=True))
    return original_open


def native_inventory(cli, *, mcp_enabled=True):
    return {
        "mechanism": inventory.MECHANISMS[cli],
        "checks": [{"command": "fixture", "exit_code": 0}],
        "mcp_servers": ["modelspec"] if mcp_enabled else [],
        "skills": [],
        "extensions": [],
        "hooks": [],
        "verified": True,
        "error": None,
        **(
            {"skill_config": "skills.config=[]", "workspace_trust": "untrusted"}
            if cli == "codex"
            else {}
        ),
    }


def allow_launch(config, clis=providers.CLIS):
    for cli in clis:
        home = homes.state_directory(cli, config)
        binary = homes.image_identity(cli, config) | {
            "reported_version": config["clis"][cli]["version"]
        }
        receipt = {
            "schema": 4,
            "authentication": {"logged_in": True, "auth_method": "subscription", "verified": True},
            "container_boundary": {"verified": True},
            "identity": homes.isolation_identity(cli, config, binary),
            "binary": binary,
            "inventory": native_inventory(cli),
            "supported": True,
            "verified": True,
            "status": "verified",
            "reason": None,
            "positive_control": {
                loc: dict.fromkeys(isolation.PROBES, True) for loc in isolation.LOCATIONS
            },
            "isolated_control": dict.fromkeys(isolation.LOCATIONS, True),
            "canary_runs": 2,
        }
        isolation.receipt_file(home).write_text(json.dumps(receipt))


@pytest.fixture
def config(tmp_path, monkeypatch):
    value = yaml.safe_load((harness.HERE / "tui_config.yaml").read_text())
    value["_state_dir"] = str(tmp_path / ".tui-state")
    monkeypatch.setattr(docker, "docker_executable", lambda: "/fake/docker")
    monkeypatch.setattr(docker, "_CLIENT_ENV", {"PATH": "/fake", "HOME": str(tmp_path)})

    def identity(cli, cfg):
        return {
            "image": docker.image_name(cli, cfg["clis"][cli]),
            "image_id": "sha256:" + "a" * 64,
            "os": "linux",
            "architecture": "arm64",
            "version": cfg["clis"][cli]["version"],
        }

    monkeypatch.setattr(homes, "image_identity", identity)
    monkeypatch.setattr(docker, "image_identity", identity)
    monkeypatch.setattr(isolation, "image_identity", identity)
    monkeypatch.setattr(homes, "docker_executable", lambda: "/fake/docker")
    def run_native(cli, cfg, workspace, command, env, **kwargs):
        if command == ["printenv", "GROK_MAX_MCP_OUTPUT_BYTES"]:
            return subprocess.CompletedProcess(command, 0, "4000000\n", "")
        return subprocess.CompletedProcess([], 0, cfg["clis"][cli]["version"], "")

    monkeypatch.setattr(homes, "run_cli", run_native)
    monkeypatch.setattr(isolation, "inspect_inventory", lambda cli, *a, **k: native_inventory(cli))

    def subscription(*a):
        return {"logged_in": True, "auth_method": "subscription", "verified": True}

    monkeypatch.setattr(isolation, "authentication_status", subscription)
    monkeypatch.setattr(providers, "authentication_status", subscription)
    monkeypatch.setenv("HOME", str(tmp_path.parent / "real-user"))
    monkeypatch.setattr(docker, "remove_container", lambda *a: None)
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
    return providers.Execution(
        parsed,
        0,
        25.0,
        status,
        limit_reason=limit,
        observed_output=answer,
        inventory=native_inventory(cli, mcp_enabled=False) if cli != "claude" else None,
    )


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


@pytest.mark.parametrize("isolated,allowed", [(True, "mcp__modelspec__*"), (False, "mcp__model301_canary__*")])
def test_grok_allows_only_the_controls_own_mcp_server(isolated, allowed, config, tmp_path):
    # A denied MCP call cancels the whole Grok turn, so the positive control must
    # allow the canary server it planted, and nothing else.
    command = providers.build_command(
        "grok", config["clis"]["grok"], tmp_path, "OK", tmp_path / "mcp.json", 8,
        isolated=isolated,
    )
    assert [command[i + 1] for i, value in enumerate(command) if value == "--allow"] == [allowed]


def test_grok_search_allows_web_fetch_by_its_permission_rule_name(config, tmp_path):
    command = providers.build_command(
        "grok", config["clis"]["grok"], tmp_path, "OK", tmp_path / "mcp.json", 8,
        purpose="search",
    )
    allowed = [command[i + 1] for i, value in enumerate(command) if value == "--allow"]
    assert "WebFetch" in allowed and "web_fetch" not in allowed


def test_grok_isolated_mcp_lives_in_a_user_layer_and_project_layer_stays_empty(config, tmp_path):
    providers.prepare_workspace("grok", config, tmp_path, mcp_enabled=True)
    assert "mcp_servers" not in (tmp_path / ".grok/config.toml").read_text()
    user = (tmp_path / docker.GROK_USER_CONFIG).read_text()
    assert "[mcp_servers.modelspec]" in user and config["mcp_url"] in user


@pytest.mark.parametrize("status,error", [
    ("connected", None), ("pending", None), ("disabled", "ModelSpec MCP did not connect"),
    ("failed", "ModelSpec MCP did not connect"), (None, "ModelSpec MCP did not connect"),
])
def test_grok_scenarios_fail_closed_unless_modelspec_connected(status, error):
    parsed = providers.Transcript(init={"mcp_servers": [{"name": "modelspec", "status": status}] if status else []})
    inventory_ok = native_inventory("grok")
    assert providers.isolation_violation(
        parsed, mcp_enabled=True, cli="grok", inventory=inventory_ok
    ) == error


def test_grok_use_tool_unwraps_to_a_modelspec_call_and_search_tool_is_lookup_only():
    output = "\n".join(json.dumps(e) for e in [
        {"type": "system", "subtype": "init", "mcp_servers": [{"name": "modelspec", "status": "connected"}]},
        {"type": "assistant", "message": {"id": "m0", "content": [
            {"type": "tool_use", "id": "s1", "name": "search_tool", "input": {"query": "decide"}},
            {"type": "tool_use", "id": "u1", "name": "use_tool",
             "input": {"tool_name": "modelspec__decide", "tool_input": {"spec": {"spec_version": 1}}}},
        ]}},
        {"type": "user", "message": {"content": [{"type": "tool_result", "tool_use_id": "u1",
            "content": json.dumps({"type": "MCP", "tool_name": "decide", "server_name": "modelspec",
                                   "output": {"OkayOutput": "{\"status\": 200}"}})}]}},
        {"type": "result", "result": "Done", "num_turns": 2},
    ])
    parsed = providers.parse_transcript("grok", output)
    assert [(c["server"], c["name"], c["arguments"]) for c in parsed.tool_calls] == [
        ("modelspec", "decide", {"spec": {"spec_version": 1}})
    ]
    assert parsed.tool_calls[0]["result"] == {
        "content": [{"type": "text", "text": '{"status": 200}'}], "isError": False}
    failed = providers.parse_transcript("grok", output.replace("OkayOutput", "Error"))
    assert failed.tool_calls[0]["result"]["isError"] is True
    refused = providers.parse_transcript("grok", output.replace(
        json.dumps(json.dumps({"type": "MCP", "tool_name": "decide", "server_name": "modelspec",
                               "output": {"OkayOutput": '{"status": 200}'}})),
        json.dumps(json.dumps([{"type": "content", "content": {"type": "text", "text": "cancelled"}}]))))
    assert refused.tool_calls[0]["result"]["content"] == [{"type": "text", "text": "cancelled"}]
    assert [c["name"] for c in parsed.other_tool_calls] == ["search_tool"]
    assert providers.isolation_violation(
        parsed, mcp_enabled=True, cli="grok", inventory=native_inventory("grok")
    ) is None
    parsed.other_tool_calls.append({"name": "run_terminal_command"})
    assert providers.isolation_violation(
        parsed, mcp_enabled=True, cli="grok", inventory=native_inventory("grok")
    ) == "CLI used a tool outside the configured ModelSpec MCP"
    foreign = providers.parse_transcript("grok", output.replace("modelspec__decide", "other__tool"))
    assert providers.isolation_violation(
        foreign, mcp_enabled=True, cli="grok", inventory=native_inventory("grok")
    ) == "CLI used a tool outside the configured ModelSpec MCP"


def test_grok_use_tool_splits_a_leading_json_object_from_the_summary():
    envelope = (
        '{"origin":"https://api.modelspec.dev/v1/decide","status":200,'
        '"body":{"status":"no_feasible"}}'
    )
    summary = "status: no_feasible; top models: none"
    broken = "{not json"

    def transcript(okay: str) -> str:
        return "\n".join(json.dumps(event) for event in [
            {"type": "assistant", "message": {"id": "m0", "content": [
                {"type": "tool_use", "id": "u1", "name": "use_tool",
                 "input": {"tool_name": "modelspec__decide", "tool_input": {}}},
            ]}},
            {"type": "user", "message": {"content": [{
                "type": "tool_result", "tool_use_id": "u1",
                "content": json.dumps({
                    "type": "MCP", "tool_name": "decide", "server_name": "modelspec",
                    "output": {"OkayOutput": okay},
                }),
            }]}},
        ])

    parsed = providers.parse_transcript("grok", transcript(envelope + "\n" + summary))
    blocks = parsed.tool_calls[0]["result"]["content"]
    assert blocks == [
        {"type": "text", "text": envelope},
        {"type": "text", "text": summary},
    ]
    assert json.loads(blocks[0]["text"])["status"] == 200
    assert parsed.tool_calls[0]["result"]["isError"] is False
    assert providers.parse_transcript("grok", transcript(envelope)).tool_calls[0]["result"][
        "content"
    ] == [{"type": "text", "text": envelope}]
    assert providers.parse_transcript("grok", transcript(summary)).tool_calls[0]["result"][
        "content"
    ] == [{"type": "text", "text": summary}]
    assert providers.parse_transcript("grok", transcript(broken)).tool_calls[0]["result"][
        "content"
    ] == [{"type": "text", "text": broken}]
    padded = providers.parse_transcript("grok", transcript("  " + envelope + "\n" + summary))
    padded_blocks = padded.tool_calls[0]["result"]["content"]
    assert padded_blocks == [
        {"type": "text", "text": envelope},
        {"type": "text", "text": summary},
    ]
    assert json.loads(padded_blocks[0]["text"]) == {
        "origin": "https://api.modelspec.dev/v1/decide",
        "status": 200,
        "body": {"status": "no_feasible"},
    }
    errored = providers.parse_transcript(
        "grok", transcript(envelope + "\n" + summary).replace("OkayOutput", "Error")
    )
    assert errored.tool_calls[0]["result"] == {
        "content": [
            {"type": "text", "text": envelope},
            {"type": "text", "text": summary},
        ],
        "isError": True,
    }
    report = {
        "runs": [{"tool_calls": [{"name": "decide", "response_ref": "r0"}]}],
        "tool_responses": {"r0": parsed.tool_calls[0]["result"]},
    }
    assert decide_health(report) == {
        "decide_answers": 1, "credits_exhausted": 0, "partial": 0,
        "unauthorised": 0, "unreadable": 0,
    }

    def gated(okay: str) -> dict:
        seen = providers.parse_transcript("grok", transcript(okay + "\n" + summary))
        return {
            "runs": [{"tool_calls": [{"name": "decide", "response_ref": "r0"}]}],
            "tool_responses": {"r0": seen.tool_calls[0]["result"]},
        }

    exhausted = (
        '{"origin":"https://api.modelspec.dev/v1/decide","status":200,'
        '"body":{"credits":{"exhausted":true}}}'
    )
    with pytest.raises(ValueError, match="credits.exhausted"):
        require_funded_key(gated(exhausted))
    unauthorised = '{"origin":"https://api.modelspec.dev/v1/decide","status":401,"body":{}}'
    with pytest.raises(ValueError, match="unauthorised"):
        require_funded_key(gated(unauthorised))


def test_grok_judge_may_look_up_tools_but_not_call_use_tool():
    def transcript(block):
        return providers.parse_transcript("grok", text([
            {"type": "assistant", "message": {"id": "m0", "content": [block]}},
            {"type": "result", "result": "Done", "num_turns": 1},
        ]))

    inventory = native_inventory("grok", mcp_enabled=False)
    looked_up = transcript(
        {"type": "tool_use", "id": "s1", "name": "search_tool", "input": {"query": "decide"}}
    )
    assert providers.isolation_violation(
        looked_up, mcp_enabled=False, cli="grok", inventory=inventory, purpose="judge"
    ) is None
    bash = transcript({
        "type": "tool_use",
        "id": "u1",
        "name": "use_tool",
        "input": {"tool_name": "bash", "tool_input": {"command": "ls"}},
    })
    assert providers.isolation_violation(
        bash, mcp_enabled=False, cli="grok", inventory=inventory, purpose="judge"
    ) == "CLI used a tool outside the configured ModelSpec MCP"


def test_grok_user_layer_mount_refuses_symlinks_and_skips_other_modes(config, tmp_path):
    env = docker.passed_environment(config)
    command = ["grok", "--version"]
    target = tmp_path / "elsewhere.toml"
    target.write_text("")
    (tmp_path / docker.GROK_USER_CONFIG).symlink_to(target)
    with pytest.raises(ValueError, match="generated user configuration"):
        docker.container_command("grok", config, tmp_path, command, env)
    # A preview never runs, so it may show the command before the workspace exists.
    assert docker.container_command("grok", config, tmp_path, command, env, preview=True)
    for options in ({"isolated": False}, {"home": False}):
        argv = docker.container_command("grok", config, tmp_path, command, env, **options)
        assert ".grok/config.toml" not in " ".join(argv)


def test_grok_positive_controls_get_an_empty_user_layer(config, tmp_path):
    providers.prepare_workspace("grok", config, tmp_path, mcp_enabled=True, isolated=False)
    assert "mcp_servers" not in (tmp_path / docker.GROK_USER_CONFIG).read_text()
    assert not (tmp_path / ".grok/config.toml").exists()


@pytest.mark.parametrize("init,error", [
    (None, "CLI did not expose its startup inventory"),
    ({"mcp_servers": [{"name": "modelspec", "status": "pending"},
                      {"name": "other", "status": "connected"}]}, "CLI loaded another MCP server"),
    ({"mcp_servers": [{"name": "modelspec", "status": "pending"},
                      {"name": "other", "status": "disabled"}]}, None),
    ({"mcp_servers": [{"name": "modelspec", "status": "pending"}, "other"]},
     "CLI startup inventory omitted or malformed mcp_servers"),
])
def test_grok_init_must_exist_and_list_no_live_foreign_server(init, error):
    parsed = providers.Transcript(init=init)
    assert providers.isolation_violation(
        parsed, mcp_enabled=True, cli="grok", inventory=native_inventory("grok")
    ) == error


@pytest.mark.parametrize("tool_name", [None, "decide", "modelspecx__decide", "mcp__modelspec__decide"])
def test_grok_use_tool_without_a_modelspec_server_prefix_fails_closed(tool_name):
    output = "\n".join(json.dumps(e) for e in [
        {"type": "system", "subtype": "init", "mcp_servers": [{"name": "modelspec", "status": "pending"}]},
        {"type": "assistant", "message": {"id": "m0", "content": [
            {"type": "tool_use", "id": "u1", "name": "use_tool",
             "input": {"tool_name": tool_name, "tool_input": {}}}]}},
        {"type": "result", "result": "Done", "num_turns": 1},
    ])
    parsed = providers.parse_transcript("grok", output)
    assert providers.isolation_violation(
        parsed, mcp_enabled=True, cli="grok", inventory=native_inventory("grok")
    ) == "CLI used a tool outside the configured ModelSpec MCP"


def test_codex_modelspec_server_approves_its_own_tools_only(config):
    text = homes.home_config("codex", config)
    assert 'default_tools_approval_mode = "approve"' in text
    assert "approval" not in homes.home_config("codex", config, server={"command": "x"})


def test_codex_controls_disable_account_apps_and_pin_the_workspace_untrusted(config, tmp_path):
    (tmp_path / "mcp.toml").write_text(homes.home_config("codex", config))
    args = providers.codex_config_args(config["clis"]["codex"], tmp_path / "mcp.toml")
    values = [args[i + 1] for i, value in enumerate(args) if value == "-c"]
    for value in (
        "plugins={}",
        "features.apps=false",
        "features.plugins=false",
        "features.remote_plugin=false",
        'projects={"/work"={trust_level="untrusted"}}',
    ):
        assert value in values


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
    assert (
        entrypoint.runtime_environment("claude", "isolated", env)["CLAUDE_CODE_DISABLE_CLAUDE_MDS"]
        == "1"
    )
    assert (
        entrypoint.runtime_environment("claude", "isolated", env)["CLAUDE_CODE_DISABLE_AUTO_MEMORY"]
        == "1"
    )
    assert (
        entrypoint.runtime_environment("claude", "isolated", env)["ENABLE_CLAUDEAI_MCP_SERVERS"]
        == "false"
    )
    assert env["MODELSPEC_API_KEY"] == "not-a-real-secret"
    assert entrypoint.runtime_environment("claude", "isolated", env)["TMPDIR"] == "/tmp"
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
        good = execution(cli, answer="OK")
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


def test_pre_init_crash_retries_once_then_keeps_a_successful_receipt(
    config, tmp_path, monkeypatch, streams
):
    allow_launch(config, ("claude",))
    calls = []

    def fake(command, **kwargs):
        calls.append(kwargs["cwd"])
        if len(calls) == 1:
            return subprocess.CompletedProcess(command, 255, "", "")
        return subprocess.CompletedProcess(command, 0, text(streams["claude"]), "")

    monkeypatch.setattr(providers.subprocess, "run", fake)
    result = providers.launch("claude", config, tmp_path, "fixture", mcp_enabled=True)
    assert result.status == "completed" and result.exit_code == 0
    assert calls == [tmp_path, tmp_path]
    assert isolation.isolation_result("claude", config)["verified"]


def test_two_pre_init_crashes_are_cli_error_and_keep_the_receipt(config, tmp_path, monkeypatch):
    allow_launch(config, ("claude",))
    seen = []
    original = providers._execute

    def wrapped(*args, **kwargs):
        result = original(*args, **kwargs)
        seen.append((result.status, result.error, result.exit_code))
        return result

    def fake(command, **kwargs):
        return subprocess.CompletedProcess(command, 255, "", "")

    monkeypatch.setattr(providers, "_execute", wrapped)
    monkeypatch.setattr(providers.subprocess, "run", fake)
    result = providers.launch("claude", config, tmp_path, "fixture", mcp_enabled=True)
    assert seen == [
        ("cli_error", "CLI exited before startup (exit 255)", 255),
        ("cli_error", "CLI exited before startup (exit 255)", 255),
    ]
    assert result.status == "cli_error"
    assert result.error == "CLI exited before startup twice (exit 255); not retried further"
    assert isolation.isolation_result("claude", config)["verified"]


def test_exit_zero_without_init_still_revokes_and_is_not_retried(config, tmp_path, monkeypatch):
    allow_launch(config, ("claude",))
    calls = []

    def fake(command, **kwargs):
        calls.append(kwargs["cwd"])
        return subprocess.CompletedProcess(command, 0, "", "")

    monkeypatch.setattr(providers.subprocess, "run", fake)
    result = providers.launch("claude", config, tmp_path, "fixture", mcp_enabled=True)
    assert result.status == "isolation_failed" and "subscription" in result.error
    assert not providers.pre_init_crash(result)
    assert calls == [tmp_path]
    assert not isolation.isolation_result("claude", config)["verified"]


def test_a_tool_call_before_a_crash_is_not_a_pre_init_crash(config, tmp_path, monkeypatch):
    allow_launch(config, ("claude",))
    calls = []
    events = [{
        "type": "assistant",
        "message": {
            "id": "m",
            "content": [
                {"type": "tool_use", "id": "t1", "name": "Bash", "input": {"command": "ls"}}
            ],
        },
    }]

    def fake(command, **kwargs):
        calls.append(kwargs["cwd"])
        return subprocess.CompletedProcess(command, 1, text(events), "")

    monkeypatch.setattr(providers.subprocess, "run", fake)
    result = providers.launch("claude", config, tmp_path, "fixture", mcp_enabled=True)
    assert result.status == "isolation_failed"
    assert not providers.pre_init_crash(result)
    assert calls == [tmp_path]
    assert not isolation.isolation_result("claude", config)["verified"]


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
        observed.update(kwargs, command=command)
        assert kwargs["input"] == ""
        assert kwargs["cwd"] == tmp_path
        assert command[0] == "/fake/docker"
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
    assert "CLAUDE_CONFIG_DIR" not in observed["env"]
    assert (
        "type=volume,source=modelspec-harness-claude-home,target=/home/agent" in observed["command"]
    )


@pytest.mark.parametrize("cli", providers.CLIS)
def test_doctor_requires_positive_controls_and_isolated_inventory(
    cli, config, tmp_path, monkeypatch
):
    seen = []

    def fake(name, cfg, workspace, prompt, *, mcp_enabled, isolated=True, probe_mcp=None):
        assert name == cli and not mcp_enabled and prompt == "Reply with exactly OK."
        seen.append((workspace, isolated))
        if isolated:
            return execution(cli, answer="OK")
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
    assert result["verified"] and result["supported"] and result["canary_runs"] == 2
    if cli == "grok":
        assert result["mcp_output_bytes"] == 4000000
    else:
        assert "mcp_output_bytes" not in result
    assert [mode for _, mode in seen] == [False, True]
    assert seen[0][0] == seen[1][0]
    assert all(not path.exists() for path, _ in seen)
    assert isolation.isolation_result(cli, config)["verified"]
    assert isolation.isolation_result(cli, config)["canary_runs"] == 0

    monkeypatch.setattr(isolation, "_execute", lambda *a, **k: execution(answer="OK"))
    result = harness.verify_isolation(cli, config, tmp_path)
    assert not result["supported"] and result["status"] == "unproven"
    assert not isolation.isolation_result(cli, config)["verified"]


@pytest.mark.parametrize("trust", ["unreported", "trusted", None])
def test_codex_doctor_fails_unless_codex_reports_the_workspace_untrusted(
    trust, config, tmp_path, monkeypatch
):
    def fake(name, cfg, workspace, prompt, *, mcp_enabled, isolated=True, probe_mcp=None):
        if not isolated:
            marker = re.search(
                r"MODEL301_CANARY_\w+", (probe_mcp.parent.parent / "AGENTS.md").read_text()
            )[0]
            return execution("codex", answer=marker)
        result = execution("codex", answer="OK")
        result.inventory["workspace_trust"] = trust
        return result

    monkeypatch.setattr(isolation, "_execute", fake)
    result = harness.verify_isolation("codex", config, tmp_path)
    assert result["positive_control"]["cwd"]["instructions"]
    assert result["isolated_control"] == {"cwd": False}
    assert not result["verified"]


def test_codex_inventory_reports_untrusted_only_when_codex_says_so(config, tmp_path, monkeypatch):
    def skills(binary, controls, workspace, env, timeout, cfg, notices):
        calls.append(None)
        if planted == "both" or planted == "discovery" and len(calls) == 1:
            notices.append("untrusted_project")
        return []

    monkeypatch.setattr(inventory, "_codex_skills", skills)

    def run(argv, **kwargs):
        if argv[-3:] == ["mcp", "list", "--json"]:
            value = []
        elif argv[-3:] == ["plugin", "list", "--json"]:
            value = {"installed": [], "available": []}
        elif argv[-2:] == ["features", "list"]:
            return subprocess.CompletedProcess(argv, 0, "hooks stable false\n", "")
        else:
            value = [{"type": "message", "content": [{"type": "input_text", "text": "context"}]}]
        return subprocess.CompletedProcess(argv, 0, json.dumps(value), "")

    monkeypatch.setattr(docker.subprocess, "run", run)
    mcp = tmp_path / "mcp.toml"
    mcp.write_text(homes.home_config("codex", config, enabled=False))
    for planted, expected in (("both", "untrusted"), ("discovery", "unreported"), (None, "unreported")):
        calls = []
        result = inventory.inspect_inventory(
            "codex", config, tmp_path, docker.passed_environment(config), mcp, mcp_enabled=False
        )
        assert result["workspace_trust"] == expected


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
    assert result["authentication"]["logged_in"] is True
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


@pytest.mark.parametrize("change", ["binary", "profile", "receipt", "adapter"])
def test_doctor_receipt_is_bound_to_binary_profile_and_adapter(
    change, config, tmp_path, monkeypatch
):
    allow_launch(config)
    assert isolation.isolation_result("claude", config)["verified"]
    if change == "binary":
        original = homes.image_identity
        monkeypatch.setattr(
            homes, "image_identity", lambda *a: original(*a) | {"image_id": "sha256:" + "b" * 64}
        )
    elif change == "profile":
        config["clis"]["claude"]["model"] = "a different model"
    elif change == "adapter":
        monkeypatch.setattr(isolation, "isolation_identity", lambda *a: "new adapter")
    else:
        home = homes.state_directory("claude", config)
        data = json.loads(isolation.receipt_file(home).read_text())
        del data["positive_control"]["cwd"]["hooks"]
        isolation.receipt_file(home).write_text(json.dumps(data))
    assert not isolation.isolation_result("claude", config)["supported"]
    monkeypatch.setattr(providers.subprocess, "run", lambda *a, **k: pytest.fail("gate bypassed"))
    with pytest.raises(ValueError, match="doctor --cli"):
        providers.launch("claude", config, tmp_path, "fixture", mcp_enabled=False)


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
    assert all(f'"cli": "{cli}"' in output for cli in providers.CLIS)
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
    "path",
    [
        "auth.json",
        ".codex/auth/session",
        ".credentials/session",
        "Keychain/session",
        "docker-volumes/modelspec-harness-codex-home/_data/opaque-state",
        "docker-volumes/modelspec-harness-gemini-home/_data/opaque-state",
        "docker-volumes/modelspec-harness-grok-home/_data/opaque-state",
        "docker-volumes/modelspec-harness-claude-home/_data/opaque-state",
        "home/agent/native-state",
    ],
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
        lambda p: os.rename(p, str(p) + "-renamed"),
        lambda p: p.rename(str(p) + "-renamed"),
        lambda p: shutil.move(p, str(p) + "-moved"),
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


def doctor_reply(cli, config, workspace, prompt, *, mcp_enabled, isolated=True, probe_mcp=None):
    if isolated:
        result = execution(cli, "OK")
    else:
        _, config_home = homes.home_paths(cli, config["clis"][cli])
        root = probe_mcp.parent
        if cli != "claude" and root != config_home:
            root = root.parent
        instruction = next(path for path in root.iterdir() if path.name.endswith(".md"))
        marker = re.search(r"MODEL301_CANARY_\w+", instruction.read_text())[0]
        (root / "model301-hook-fired").touch()
        (root / "model301-mcp-fired").touch()
        result = execution(cli, marker)
        result.transcript.init["skills"] = ["model301_canary"]
    if cli != "claude":
        result.transcript.init = None
    return result


@pytest.mark.parametrize(
    "stdout,code,accepted",
    [
        ("4000000\n", 0, True),
        ("1000000", 0, True),
        ("999999\n", 0, False),
        ("", 1, False),
        ("nope\n", 0, False),
    ],
)
def test_grok_doctor_requires_a_million_byte_inline_mcp_limit(
    stdout, code, accepted, config, tmp_path, monkeypatch
):
    seen = []

    def run(cli, cfg, workspace, command, env, **kwargs):
        if command == ["printenv", "GROK_MAX_MCP_OUTPUT_BYTES"]:
            seen.append(kwargs)
            return subprocess.CompletedProcess(command, code, stdout, "")
        return subprocess.CompletedProcess([], 0, cfg["clis"][cli]["version"], "")

    monkeypatch.setattr(homes, "run_cli", run)
    if accepted:
        monkeypatch.setattr(isolation, "_execute", doctor_reply)
    else:
        monkeypatch.setattr(isolation, "_execute", lambda *a, **k: pytest.fail("canaries ran"))
    result = harness.verify_isolation("grok", config, tmp_path)
    assert seen == [{"home": False}]
    if accepted:
        measured = int(stdout.strip())
        assert result["verified"] and result["mcp_output_bytes"] == measured
        receipt_path = isolation.receipt_file(homes.state_directory("grok", config))
        receipt = json.loads(receipt_path.read_text())
        assert receipt["mcp_output_bytes"] == measured
    else:
        assert result["status"] == "unproven" and result["canary_runs"] == 0
        assert result["reason"] == (
            "Grok would spill large MCP results to files; "
            "GROK_MAX_MCP_OUTPUT_BYTES is missing or too low"
        )
        assert "mcp_output_bytes" not in result
        assert not isolation.isolation_result("grok", config)["verified"]


@pytest.mark.parametrize("cli", providers.CLIS)
def test_dummy_credentials_survive_setup_doctor_and_launch_without_access(
    cli, config, tmp_path, monkeypatch, streams, deny_credential_access
):
    home = tmp_path / "docker-volumes" / docker.home_volume(cli) / "_data"
    config_home = home / ("." + cli)
    config_home.mkdir(parents=True)
    dummy_files = [config_home / name for name in ("auth.json", ".credentials.json")]
    for path in dummy_files:
        # The only bypass of the guard plants new dummy files inside this test's fake home.
        assert path.is_relative_to(tmp_path) and not path.exists()
        with deny_credential_access(path, "x") as stream:
            stream.write('{"dummy": "not a credential"}')
    before = [(p.stat().st_ino, p.stat().st_size, p.stat().st_mtime_ns) for p in dummy_files]
    config_path = tmp_path / "dummy-home.yaml"
    config_path.write_text(yaml.safe_dump(config))
    monkeypatch.setattr(harness, "private_output", lambda path: path)
    monkeypatch.setattr(isolation, "_execute", doctor_reply)
    monkeypatch.setattr(
        inventory,
        "inspect_inventory",
        lambda name, *a, **k: native_inventory(name, mcp_enabled=k["mcp_enabled"]),
    )
    monkeypatch.setattr(
        providers.subprocess,
        "run",
        lambda command, **kwargs: subprocess.CompletedProcess(command, 0, text(streams[cli]), ""),
    )
    assert (
        harness.main(
            [
                "doctor",
                "--cli",
                cli,
                "--config",
                str(config_path),
                "--out",
                str(tmp_path),
            ]
        )
        == 0
    )
    assert (
        providers.launch(cli, config, tmp_path, "Fixture request", mcp_enabled=True).status
        == "completed"
    )
    assert before == [
        (p.stat().st_ino, p.stat().st_size, p.stat().st_mtime_ns) for p in dummy_files
    ]
    assert home.is_dir()


@pytest.mark.parametrize(
    "field", ["image", "image_id", "version", "reported_version", "os", "architecture"]
)
def test_binary_receipt_binds_every_readable_field(field, config):
    allow_launch(config, ("claude",))
    home = homes.state_directory("claude", config)
    path = isolation.receipt_file(home)
    receipt = json.loads(path.read_text())
    receipt["binary"][field] = (
        "0.161.0" if field == "version" else receipt["binary"][field] + "-changed"
    )
    path.write_text(json.dumps(receipt))
    assert not isolation.isolation_result("claude", config)["verified"]


def test_claude_relaxed_mcp_probe_uses_discovery_and_config_home_does_not_require_mcp(
    config, tmp_path
):
    command = providers.build_command(
        "claude",
        config["clis"]["claude"],
        tmp_path,
        "OK",
        tmp_path / ".mcp.json",
        1,
        isolated=False,
    )
    assert "--mcp-config" not in command
    files, _, _, _ = isolation.canary_files("claude", config, tmp_path, "MARKER")
    assert (
        json.loads(files[tmp_path / ".claude/settings.json"])["enableAllProjectMcpServers"] is True
    )
    assert "mcp" in isolation.required_positive("claude", "cwd")
    assert "mcp" not in isolation.required_positive("claude", "config_home")


def test_existing_doctor_lock_reports_the_exact_clear_command(config, tmp_path, monkeypatch):
    home = homes.state_directory("codex", config)
    lock = home / "tui-doctor.lock"
    lock.mkdir()
    monkeypatch.setattr(
        isolation, "_execute", lambda *a, **k: pytest.fail("locked doctor launched")
    )
    result = harness.verify_isolation("codex", config, tmp_path)
    assert result["status"] == "unproven" and f"rmdir {lock}" in result["reason"]
    assert "If no doctor is running" in result["reason"]
    assert "doctor --cli codex" in result["reason"]


@pytest.mark.parametrize("cli", ["codex", "gemini", "grok"])
def test_native_inventory_and_canary_allow_a_stream_without_init_inventory(
    cli, config, tmp_path, monkeypatch
):
    monkeypatch.setattr(isolation, "_execute", doctor_reply)
    result = harness.verify_isolation(cli, config, tmp_path)
    assert result["verified"] and result["inventory"]["mcp_servers"] == ["modelspec"]
    assert result["inventory"]["mechanism"] == inventory.MECHANISMS[cli]
    assert isolation.isolation_result(cli, config)["verified"]
    # Grok's stream always carries init, and only init shows whether its MCP connected.
    assert providers.isolation_violation(
        providers.Transcript(init=None),
        cli=cli,
        mcp_enabled=True,
        inventory=native_inventory(cli),
    ) == ("CLI did not expose its startup inventory" if cli == "grok" else None)
    monkeypatch.setattr(
        isolation, "inspect_inventory", lambda *a, **k: {"error": "missing inventory"}
    )
    result = harness.verify_isolation(cli, config, tmp_path)
    assert not result["verified"] and result["canary_runs"] == 0
    assert not isolation.isolation_result(cli, config)["verified"]


@pytest.mark.parametrize(
    "cli,stream",
    [("codex", "stdout"), ("gemini", "stdout"), ("gemini", "stderr"), ("grok", "stdout")],
)
def test_native_inventory_reads_cli_reports_under_exact_launch_environment(
    cli, stream, config, tmp_path, monkeypatch
):
    outputs = {
        "mcp list --json": [
            {
                "name": "modelspec",
                "enabled": True,
                "transport": {"type": "streamable_http", "url": config["mcp_url"]},
            }
        ],
        "plugin list --json": {"installed": [], "available": []},
        "features list": "hooks\tunder development\tfalse\n",
        "debug prompt-input": [
            {
                "type": "message",
                "role": "user",
                "content": [{"type": "input_text", "text": "native context"}],
            }
        ],
        "mcp list": "Configured MCP servers:\n\n"
        f"✓ modelspec: {config['mcp_url']} (http) - Connected\n",
        "extensions list --output-format json": [],
        "skills list": "No skills discovered.\n",
        "effective settings": {
            "skillsEnabled": False,
            "hooksEnabled": False,
            "hookEvents": [],
            "userSettingsPath": str(
                homes.home_paths("gemini", config["clis"]["gemini"])[1] / "settings.json"
            ),
            "realHomeSandboxPolicyExists": False,
        },
        "inspect --json": {
            "cwd": "/work",
            "skills": [
                {"name": "builtin-skill", "source": {"type": "builtin"}},
                {"name": "bundled-skill", "source": {"type": "bundled", "path": "/bundle"}},
            ],
            "hooks": [],
            "plugins": [],
            "projectInstructions": [],
            "mcpServers": [{"name": "modelspec", "transport": "http", "target": config["mcp_url"]}],
        },
    }
    env = providers.child_environment(cli, tmp_path, settings=config["clis"][cli])
    calls = []

    def fake(command, **kwargs):
        assert kwargs["env"] == docker.docker_environment(env) and kwargs["cwd"] == tmp_path
        assert kwargs["input"] == ""
        calls.append(command)
        key = next(
            (key for key in outputs if command[-len(key.split()) :] == key.split()),
            "effective settings",
        )
        value = outputs[key]
        listing = value if isinstance(value, str) else json.dumps(value)
        if cli == "gemini" and stream == "stderr" and key != "effective settings":
            return subprocess.CompletedProcess(command, 0, "", listing)
        return subprocess.CompletedProcess(command, 0, listing, "")

    monkeypatch.setattr(providers.subprocess, "run", fake)
    monkeypatch.setattr(inventory, "_codex_skills", lambda *a: [])
    if cli == "grok":
        providers.prepare_workspace(cli, config, tmp_path, mcp_enabled=True)
    mcp_file = tmp_path / "modelspec-mcp.json"
    mcp_file.write_text(homes.home_config(cli, config))
    result = inventory.inspect_inventory(cli, config, tmp_path, env, mcp_file, mcp_enabled=True)
    assert inventory.inventory_violation(result, mcp_enabled=True) is None
    assert result["mechanism"] == inventory.MECHANISMS[cli] and len(calls) >= 1
    # A ModelSpec label alone cannot attest a different service or a local executable.
    outputs["mcp list --json"][0]["transport"]["url"] = "https://foreign.test/mcp"
    outputs["mcp list"] = (
        "Configured MCP servers:\n\n✓ modelspec: https://foreign.test/mcp (http) - Connected\n"
    )
    outputs["inspect --json"]["mcpServers"][0]["target"] = "https://foreign.test/mcp"
    result = inventory.inspect_inventory(cli, config, tmp_path, env, mcp_file, mcp_enabled=True)
    assert inventory.inventory_violation(result, mcp_enabled=True)
    monkeypatch.setattr(
        providers.subprocess,
        "run",
        lambda command, **kw: subprocess.CompletedProcess(command, 0, "", ""),
    )
    result = inventory.inspect_inventory(cli, config, tmp_path, env, mcp_file, mcp_enabled=True)
    assert inventory.inventory_violation(result, mcp_enabled=True)


@pytest.mark.parametrize("cli", ["codex", "gemini", "grok"])
@pytest.mark.parametrize("field", ["mcp_servers", "skills", "extensions", "hooks"])
def test_native_inventory_fails_closed_on_missing_or_extra_customizations(cli, field):
    result = native_inventory(cli)
    result[field] = ["foreign customization"]
    assert inventory.inventory_violation(result, mcp_enabled=True)
    del result[field]
    assert inventory.inventory_violation(result, mcp_enabled=True)


def test_codex_skill_disabling_uses_cli_discovery_and_verifies_effective_state(
    config, tmp_path, monkeypatch
):
    discovered = {
        "name": "user-skill",
        "scope": "user",
        "enabled": True,
        "path": str(tmp_path / "skills/user-skill/SKILL.md"),
    }
    assert inventory._codex_skill_config([discovered]) == (
        "skills.config=[{path=" + json.dumps(discovered["path"]) + ",enabled=false}]"
    )
    with pytest.raises(ValueError, match="unknown entry"):
        inventory._codex_skill_config([discovered | {"scope": "unknown"}])


@pytest.mark.parametrize("move", ["os.rename", "Path.rename", "shutil.move"])
def test_runtime_guard_also_denies_a_credential_destination(move, tmp_path):
    source = tmp_path / "innocent-config"
    source.write_text("config")
    with pytest.raises(AssertionError, match="Credential access attempted"):
        # Resolve the guarded function after the autouse fixture has patched it.
        owner, name = move.split(".")
        guarded = getattr({"os": os, "Path": Path, "shutil": shutil}[owner], name)
        guarded(source, tmp_path / "auth.json")


@pytest.mark.parametrize("malformed", [False, True])
def test_codex_skill_rpc_uses_the_exact_home_and_cwd_without_a_model_turn(
    malformed, config, tmp_path, monkeypatch
):
    fake = tmp_path / "inventory-cli.py"
    fake.write_text(
        f"#!{sys.executable}\n"
        "import json,sys\n"
        "for line in sys.stdin:\n"
        "    request = json.loads(line)\n"
        "    method = request['method']\n"
        "    if method == 'initialized': continue\n"
        "    if method == 'initialize': result = {'userAgent': 'fake-cli'}\n"
        "    elif method == 'skills/list':\n"
        "        assert request['params']['cwds'] == ['/work']\n"
        "        assert request['params']['forceReload'] is True\n"
        "        result = {'data': [{'cwd': '/work', 'skills': []"
        + ("" if malformed else ", 'errors': []")
        + "}]}\n"
        "    else: raise AssertionError('Unexpected RPC or model turn')\n"
        "    print(json.dumps({'id': request['id'], 'result': result}), flush=True)\n"
    )

    def popen(cli, cfg, workspace, command, env):
        assert cli == "codex" and workspace == tmp_path
        assert command == ["codex", "--no-daemon", "app-server", "--listen", "stdio://"]
        # A local fake stands in for the Docker client's stdio transport.
        return subprocess.Popen(
            [sys.executable, str(fake)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    def stop(process):
        process.terminate()
        return process.communicate(timeout=5)

    monkeypatch.setattr(inventory, "popen_cli", popen)
    monkeypatch.setattr(inventory, "stop_process", stop)
    env = providers.child_environment("codex", tmp_path, settings=config["clis"]["codex"])
    if malformed:
        with pytest.raises(ValueError, match="skill discovery errors"):
            inventory._codex_skills("codex", ["--no-daemon"], tmp_path, env, 5, config)
    else:
        assert inventory._codex_skills("codex", ["--no-daemon"], tmp_path, env, 5, config) == []


CODEX_WARNING_EVENT = {
    "method": "configWarning",
    "params": {"summary": inventory.CODEX_UNTRUSTED_PROJECT_WARNING, "details": None},
    "emittedAtMs": 1,
}
CODEX_WARNING_STDERR = (
    "\x1b[2m2026-10-04T12:13:34.529959Z\x1b[0m \x1b[31mERROR\x1b[0m "
    "\x1b[2mcodex_app_server\x1b[0m\x1b[2m:\x1b[0m "
    + inventory.CODEX_UNTRUSTED_PROJECT_WARNING
    + "\n"
)


@pytest.mark.parametrize(
    "event,stderr,error",
    [
        (CODEX_WARNING_EVENT, CODEX_WARNING_STDERR, None),
        (
            CODEX_WARNING_EVENT | {"params": {"summary": "Other warning", "details": None}},
            "",
            "Unexpected Codex inventory RPC event",
        ),
        (None, CODEX_WARNING_STDERR + "WARN codex: unknown\n", "emitted diagnostics"),
        # Unterminated, so only the check after the process stops can see it.
        (None, "WARN codex: unterminated", "emitted diagnostics"),
        (None, CODEX_WARNING_STDERR.replace("/work/.codex", "/home/agent/.codex"), "emitted diagnostics"),
    ],
)
def test_codex_untrusted_project_warning_is_the_only_tolerated_diagnostic(
    event, stderr, error, config, tmp_path, monkeypatch
):
    fake = tmp_path / "inventory-cli.py"
    fake.write_text(
        f"#!{sys.executable}\n"
        "import json,sys\n"
        f"sys.stderr.write({stderr!r}); sys.stderr.flush()\n"
        f"event = {json.dumps(event)!r}\n"
        "for line in sys.stdin:\n"
        "    request = json.loads(line)\n"
        "    if request['method'] == 'initialized': continue\n"
        "    if request['method'] == 'skills/list' and event != 'null':\n"
        "        print(event, flush=True)\n"
        "    result = {'data': [{'cwd': '/work', 'skills': [], 'errors': []}]}\n"
        "    print(json.dumps({'id': request['id'], 'result': result}), flush=True)\n"
    )

    def popen(cli, cfg, workspace, command, env):
        return subprocess.Popen(
            [sys.executable, str(fake)],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    def stop(process):
        process.terminate()
        return process.communicate(timeout=5)

    monkeypatch.setattr(inventory, "popen_cli", popen)
    monkeypatch.setattr(inventory, "stop_process", stop)
    env = providers.child_environment("codex", tmp_path, settings=config["clis"]["codex"])
    if error is None:
        assert inventory._codex_skills("codex", ["--no-daemon"], tmp_path, env, 5, config) == []
    else:
        with pytest.raises(ValueError, match=error):
            inventory._codex_skills("codex", ["--no-daemon"], tmp_path, env, 5, config)


def test_codex_partial_diagnostic_lines_wait_until_complete():
    line = CODEX_WARNING_STDERR.encode()
    assert not inventory.codex_unknown_diagnostics(line[:40], final=False)
    assert not inventory.codex_unknown_diagnostics(line, final=True)
    assert inventory.codex_unknown_diagnostics(line[:40], final=True)


@pytest.mark.parametrize("cli", providers.CLIS)
def test_not_logged_in_stops_doctor_before_version_inventory_or_canaries(
    cli, config, tmp_path, monkeypatch
):
    monkeypatch.setattr(
        isolation,
        "authentication_status",
        lambda *a: {
            "logged_in": False,
            "auth_method": "none",
            "verified": True,
            "reason": None,
        },
    )
    for name in ("binary_identity", "inspect_inventory", "_execute"):
        monkeypatch.setattr(
            isolation, name, lambda *a, **k: pytest.fail("doctor continued without login")
        )
    result = harness.verify_isolation(cli, config, tmp_path)
    assert result["reason"] == f"{cli}: not logged in"
    assert result["authentication"]["auth_method"] == "none"
    assert not result["verified"] and result["canary_runs"] == 0


@pytest.mark.parametrize("logged_in,code", [(True, 0), (False, 1)])
def test_claude_auth_status_discards_account_identifiers(
    logged_in, code, config, tmp_path, monkeypatch
):
    value = {
        "loggedIn": logged_in,
        "authMethod": "claude.ai" if logged_in else "none",
        "email": "private@example.invalid",
        "orgId": "private-org",
        "accountId": "private-account",
    }

    def run(command, **kwargs):
        assert command[-2:] == ["auth", "status"]
        assert "--env" in command and "HOME" not in command
        return subprocess.CompletedProcess(command, code, json.dumps(value), "")

    monkeypatch.setattr(auth.subprocess, "run", run)
    env = providers.child_environment("claude", tmp_path, settings=config["clis"]["claude"])
    result = auth.authentication_status("claude", config, tmp_path, env)
    assert result["logged_in"] is logged_in and result["verified"]
    assert "private" not in json.dumps(result)


@pytest.mark.parametrize(
    "listing,code,verified",
    [
        ("Logged in using ChatGPT", 0, True),
        ("Not logged in", 1, True),
        ("Logged in using ChatGPT\nWARNING: unknown diagnostic", 0, False),
        ("Logged in using an API key - private-key", 0, False),
    ],
)
def test_codex_auth_status_accepts_only_native_status_grammar(
    listing, code, verified, config, tmp_path, monkeypatch
):
    monkeypatch.setattr(
        auth.subprocess,
        "run",
        lambda command, **k: subprocess.CompletedProcess(command, code, "", listing),
    )
    env = providers.child_environment("codex", tmp_path, settings=config["clis"]["codex"])
    result = auth.authentication_status("codex", config, tmp_path, env)
    assert result["verified"] is verified
    assert "private-key" not in json.dumps(result)


def test_gemini_authenticated_service_rejection_is_not_missing_login(config, tmp_path, monkeypatch):
    monkeypatch.setattr(
        auth,
        "run_cli",
        lambda *a, **k: subprocess.CompletedProcess([], 0, '{"selectedType":"oauth-personal"}', ""),
    )
    monkeypatch.setattr(
        auth,
        "_rpc",
        lambda *a: [
            {},
            {
                "error": {
                    "code": -32000,
                    "message": (
                        "This client is no longer supported for Gemini Code Assist for individuals."
                    ),
                }
            },
        ],
    )
    env = providers.child_environment("gemini", tmp_path, settings=config["clis"]["gemini"])
    result = auth.authentication_status("gemini", config, tmp_path, env)
    assert result["verified"] and result["logged_in"] is True
    assert result["auth_method"] == "oauth-personal" and result["service_available"] is False
    assert result["reason"] == docker.GEMINI_RETIRED


@pytest.mark.parametrize("cli", providers.CLIS)
def test_doctor_never_plants_in_real_or_dedicated_home(cli, config):
    home, config_home = homes.home_paths(cli, config["clis"][cli])
    for root in (Path.home(), home, config_home, Path.home() / ("." + cli)):
        with pytest.raises(ValueError, match="must not be planted"):
            isolation.canary_files(cli, config, root, "CANARY")


@pytest.mark.parametrize(
    "listing",
    [
        "Configured MCP servers:\n",
        "Configured MCP servers:\n"
        "✓ modelspec: https://api.modelspec.dev/mcp (http) - Connected\nunknown diagnostic",
        "Configured MCP servers:\n✗ modelspec: https://api.modelspec.dev/mcp (http) - Connected",
        "Configured MCP servers:\n"
        "✓ modelspec: https://api.modelspec.dev/mcp (http) - Connected\n"
        "✓ modelspec: https://api.modelspec.dev/mcp (http) - Connected",
        "ERROR: failed to load MCP configuration\nNo MCP servers configured.",
    ],
)
def test_gemini_stderr_listing_rejects_unknown_lines_and_malformed_grammar(
    listing, config, tmp_path, monkeypatch
):
    monkeypatch.setattr(
        inventory.subprocess,
        "run",
        lambda command, **k: subprocess.CompletedProcess(command, 0, "", listing),
    )
    mcp = tmp_path / "modelspec-mcp.json"
    mcp.write_text(homes.home_config("gemini", config))
    env = providers.child_environment("gemini", tmp_path, settings=config["clis"]["gemini"])
    result = inventory.inspect_inventory("gemini", config, tmp_path, env, mcp, mcp_enabled=True)
    assert result["error"] and result["checks"][0]["exit_code"] == 0


@pytest.mark.parametrize("symlink", [False, True])
def test_gemini_existing_dotenv_refuses_startup_without_read_or_overwrite(
    symlink, config, tmp_path, monkeypatch
):
    target = tmp_path / "existing-env"
    target.write_text("INJECTED=1\n")
    barrier = tmp_path / ".env"
    if symlink:
        barrier.symlink_to(target)
    else:
        target.rename(barrier)
        target = barrier
    original_stat = target.stat()
    original_open = Path.open

    def guarded(path, *args, **kwargs):
        if path in (target, barrier):
            pytest.fail("Existing dotenv was opened")
        return original_open(path, *args, **kwargs)

    monkeypatch.setattr(Path, "open", guarded)
    monkeypatch.setattr(docker.subprocess, "run", lambda *a, **k: pytest.fail("CLI started"))
    with pytest.raises(ValueError, match="empty private cwd .env"):
        providers.prepare_workspace("gemini", config, tmp_path, mcp_enabled=False)
    assert target.stat() == original_stat


@pytest.mark.parametrize("cli", providers.CLIS)
def test_docker_boundary_mounts_login_volume_private_workspace_and_grok_user_layer(cli, config, tmp_path):
    env = docker.passed_environment(config)
    if cli == "grok":
        with pytest.raises(ValueError, match="generated user configuration"):
            docker.container_command(cli, config, tmp_path, [cli, "--version"], env)
        providers.prepare_workspace(cli, config, tmp_path, mcp_enabled=True)
    argv = docker.container_command(cli, config, tmp_path, [cli, "--version"], env)
    mounts = [argv[i + 1] for i, value in enumerate(argv) if value == "--mount"]
    assert mounts == [
        f"type=volume,source=modelspec-harness-{cli}-home,target=/home/agent",
        f"type=bind,source={tmp_path.resolve()},target=/work",
    ] + (
        [f"type=bind,source={tmp_path.resolve() / docker.GROK_USER_CONFIG},"
         f"target={target},readonly"
         for target in ("/home/agent/.grok/config.toml", "/work/" + docker.GROK_USER_CONFIG)]
        if cli == "grok" else []
    )
    passed = [argv[i + 1] for i, value in enumerate(argv) if value == "--env"]
    assert set(passed) == {"TERM", "LANG", "MODELSPEC_MCP_URL"}
    assert "--rm" in argv and "--pull=never" in argv
    assert "--privileged" not in argv and "--network=host" not in argv
    assert argv[-3:] == ["isolated", cli, "--version"]
    assert "HOME" not in passed and "PATH" not in passed
    assert argv[argv.index("--workdir") + 1] == "/work"
    assert str(Path.home()) not in " ".join(argv)


@pytest.mark.parametrize("cli", providers.CLIS)
def test_native_headless_paths_are_linux_paths_without_rewriting_the_prompt(cli, config, tmp_path):
    path = tmp_path / "mcp.json"
    path.write_text(homes.home_config(cli, config))
    prompt = f"literal {tmp_path} $HOME `echo hi`"
    argv = providers.build_command(cli, config["clis"][cli], tmp_path, prompt, path, 8)
    assert argv[-1] == prompt
    assert not any(str(tmp_path) in value for value in argv[:-1])
    if cli == "claude":
        assert argv[argv.index("--mcp-config") + 1] == "/work/mcp.json"
    if cli in ("codex", "grok"):
        assert "/work" in argv


@pytest.mark.parametrize(
    "variable",
    [
        "ANTHROPIC_API_KEY",
        "OPENAI_API_KEY",
        "GEMINI_API_KEY",
        "GOOGLE_API_KEY",
        "XAI_API_KEY",
        "AZURE_OPENAI_API_KEY",
        "ANTHROPIC_AUTH_TOKEN",
        "CLAUDE_CODE_OAUTH_TOKEN",
        "CODEX_ACCESS_TOKEN",
        "GROK_DEPLOYMENT_KEY",
        "GOOGLE_APPLICATION_CREDENTIALS",
        "AWS_ACCESS_KEY_ID",
        "OPENAI_IDENTITY_TOKEN_FILE",
    ],
)
@pytest.mark.parametrize("value", ["", "must-never-be-printed"])
def test_container_refuses_vendor_credential_environment_even_when_empty(
    variable, value, config, tmp_path, monkeypatch, capsys
):
    env = docker.passed_environment(config) | {variable: value}
    monkeypatch.setattr(docker.subprocess, "run", lambda *a, **k: pytest.fail("Docker started"))
    with pytest.raises(ValueError, match="Subscription-only"):
        docker.run_cli("claude", config, tmp_path, ["claude", "--version"], env)
    with pytest.raises(ValueError, match="Subscription-only"):
        entrypoint.runtime_environment("claude", "isolated", env)
    assert "must-never-be-printed" not in repr(capsys.readouterr())


@pytest.mark.parametrize("variable", ["HOME", "PATH", "NODE_OPTIONS", "BASH_ENV", "CODEX_HOME"])
def test_container_rejects_nonallowlisted_environment(variable, config, tmp_path):
    with pytest.raises(ValueError, match="explicit harness allowlist"):
        docker.container_command(
            "codex",
            config,
            tmp_path,
            ["codex", "--help"],
            docker.passed_environment(config) | {variable: "host-value"},
        )


@pytest.mark.parametrize("cli", providers.CLIS)
def test_runtime_uses_fixed_linux_home_and_suppresses_host_customizations(cli):
    env = entrypoint.runtime_environment(
        cli,
        "isolated",
        {
            "TERM": "xterm",
            "LANG": "C.UTF-8",
            "PATH": "/host/bin",
            "HOME": "/host/home",
            "BASH_ENV": "/host/shell",
            "NODE_OPTIONS": "--require=host.js",
            "MODELSPEC_MCP_URL": "https://example.test/mcp",
        },
    )
    assert env["HOME"] == "/home/agent"
    assert env["PATH"] == "/usr/local/bin:/usr/bin:/bin" and env["TMPDIR"] == "/tmp"
    assert "BASH_ENV" not in env and "NODE_OPTIONS" not in env
    if cli == "gemini":
        assert env["NO_BROWSER"] == "true"
        assert env["GEMINI_CLI_SYSTEM_SETTINGS_PATH"].startswith("/opt/modelspec-harness/")
        assert "selectedType" not in Path("qa/docker/gemini-isolated.json").read_text()
    if cli == "grok":
        assert env["GROK_FOLDER_TRUST"] == "1"
        assert env["GROK_MAX_MCP_OUTPUT_BYTES"] == "4000000"
    else:
        assert "GROK_MAX_MCP_OUTPUT_BYTES" not in env


def test_grok_positive_control_does_not_persist_trust_into_login_volume(config, tmp_path):
    env = entrypoint.runtime_environment("grok", "positive", {})
    assert env["GROK_FOLDER_TRUST"] == "0"
    assert "GROK_MAX_MCP_OUTPUT_BYTES" not in env
    login = entrypoint.runtime_environment("grok", "login", {})
    assert "GROK_FOLDER_TRUST" not in login and "GROK_MAX_MCP_OUTPUT_BYTES" not in login
    command = providers.build_command(
        "grok",
        config["clis"]["grok"],
        tmp_path,
        "OK",
        tmp_path / "mcp.json",
        8,
        isolated=False,
    )
    assert "--trust" not in command and "--trust-folder" not in command


def test_doctor_rejects_state_directory_aliases_before_any_docker_call(
    config, tmp_path, monkeypatch
):
    root = Path(config["_state_dir"])
    root.mkdir()
    target = tmp_path / "docker-volumes" / docker.home_volume("codex") / "_data"
    target.mkdir(parents=True)
    (root / "codex").symlink_to(target, target_is_directory=True)
    monkeypatch.setattr(
        isolation, "image_identity", lambda *a: pytest.fail("Docker must not be started")
    )
    result = harness.verify_isolation("codex", config, tmp_path)
    assert not result["verified"] and "must not be symlinks" in result["reason"]
    assert not list(target.iterdir())


def test_gemini_login_refuses_before_docker_because_google_retired_it(config, monkeypatch):
    monkeypatch.setattr(homes.os, "execve", lambda *a: pytest.fail("Docker must not be started"))
    monkeypatch.setattr(
        homes, "image_identity", lambda *a: pytest.fail("Docker must not be queried")
    )
    with pytest.raises(ValueError, match="2026-06-18"):
        homes.login("gemini", config)


def test_build_images_prints_gemini_retirement_not_a_login_command(monkeypatch, capsys):
    monkeypatch.setattr(harness, "build_images", lambda *a: None)
    monkeypatch.setattr(harness, "binary_identity", lambda *a: {"reported_version": "0.62.0"})
    assert harness.main(["build-images", "--cli", "gemini"]) == 0
    out = capsys.readouterr().out
    assert out == f"gemini: 0.62.0. {docker.GEMINI_RETIRED}.\n"


@pytest.mark.parametrize("cli", [cli for cli in providers.CLIS if cli != "gemini"])
def test_login_execs_docker_with_subscription_flow_and_uncaptured_terminal(
    cli, config, monkeypatch, capsys
):
    observed = []
    monkeypatch.setenv("MODELSPEC_API_KEY", "model-secret")
    monkeypatch.setenv("OPENAI_API_KEY", "vendor-secret")
    monkeypatch.setattr(homes.os, "execve", lambda *args: observed.append(args))
    monkeypatch.setattr(docker.subprocess, "run", lambda *a, **k: pytest.fail("login captured"))
    homes.login(cli, config)
    executable, argv, env = observed[0]
    assert executable == "/fake/docker" and argv[:3] == ["/fake/docker", "run", "--rm"]
    assert (
        "-it" in argv
        and "type=volume,source=" + docker.home_volume(cli) + ",target=/home/agent" in argv
    )
    assert not any("type=bind" in value for value in argv)
    assert not any(key.startswith("MODELSPEC") for key in env)
    assert "OPENAI_API_KEY" not in env
    native = argv[argv.index("login", argv.index("sha256:" + "a" * 64)) + 1 :]
    assert native == docker.LOGIN_ARGS[cli]
    assert "--with-api-key" not in native
    if cli in ("codex", "grok"):
        assert "--device-auth" in native
    if cli == "claude":
        assert native == ["claude", "auth", "login", "--claudeai"]
    assert capsys.readouterr().out == ""
    assert homes.login_command(cli) == f"python -m qa.tui_harness login --cli {cli}"


@pytest.mark.parametrize(
    "cli,method",
    [
        ("claude", "api_key"),
        ("codex", "api_key"),
        ("gemini", "gemini-api-key"),
        ("grok", "api_key"),
    ],
)
def test_api_auth_refuses_model_start_and_revokes_doctor(
    cli, method, config, tmp_path, monkeypatch
):
    allow_launch(config, (cli,))
    monkeypatch.setattr(
        providers,
        "authentication_status",
        lambda *a: {
            "logged_in": True,
            "auth_method": method,
            "verified": False,
            "reason": "CLI reports API-key authentication",
        },
    )
    monkeypatch.setattr(providers, "run_cli", lambda *a, **k: pytest.fail("model started"))
    result = providers.launch(cli, config, tmp_path, "Never run this prompt", mcp_enabled=False)
    assert result.status == "isolation_failed" and "API-key" in result.error
    assert not isolation.isolation_result(cli, config)["verified"]


@pytest.mark.parametrize("method", ["gemini-api-key", "vertex-ai", "unknown", "none"])
def test_gemini_checks_native_auth_selection_before_acp(method, config, tmp_path, monkeypatch):
    calls = []

    def status(cli, cfg, workspace, command, env):
        calls.append(command)
        return subprocess.CompletedProcess(command, 0, json.dumps({"selectedType": method}), "")

    monkeypatch.setattr(auth, "run_cli", status)
    monkeypatch.setattr(auth, "_rpc", lambda *a: pytest.fail("non-Google ACP started"))
    result = auth.authentication_status(
        "gemini", config, tmp_path, docker.passed_environment(config)
    )
    assert result["verified"] is (method == "none")
    assert calls == [["node", "/opt/modelspec-harness/gemini-settings.mjs", "auth"]]


def test_claude_status_api_key_source_overrides_subscription_method(config, tmp_path, monkeypatch):
    monkeypatch.setattr(
        auth,
        "run_cli",
        lambda *a: subprocess.CompletedProcess(
            [], 0, '{"loggedIn":true,"authMethod":"claude.ai","apiKeySource":"apiKeyHelper"}', ""
        ),
    )
    result = auth.authentication_status(
        "claude", config, tmp_path, docker.passed_environment(config)
    )
    assert not result["verified"] and result["auth_method"] == "api_key"


def test_modelspec_token_is_forwarded_only_for_agents_and_never_in_docker_argv(
    config, tmp_path, monkeypatch
):
    monkeypatch.setenv("MODELSPEC_API_KEY", "must-stay-out-of-argv")
    for enabled in (False, True):
        env = docker.passed_environment(config, token=enabled)
        argv = docker.container_command("claude", config, tmp_path, ["claude", "--help"], env)
        assert ("MODELSPEC_API_KEY" in env) is enabled
        assert ("MODELSPEC_API_KEY" in argv) is enabled
        assert "must-stay-out-of-argv" not in " ".join(argv)


def test_docker_timeout_removes_the_container_without_retry(config, tmp_path, monkeypatch):
    removed, starts = [], []
    monkeypatch.setattr(docker, "remove_container", removed.append)

    def run(argv, **kwargs):
        starts.append(argv)
        raise subprocess.TimeoutExpired(argv, 1, b"partial transcript", b"diagnostic")

    monkeypatch.setattr(docker.subprocess, "run", run)
    with pytest.raises(subprocess.TimeoutExpired) as caught:
        docker.run_cli(
            "codex", config, tmp_path, ["codex", "--version"], docker.passed_environment(config)
        )
    assert caught.value.stdout == b"partial transcript"
    assert len(starts) == 1 and removed == [starts[0][starts[0].index("--name") + 1]]


def test_build_images_uses_pinned_local_targets_and_only_the_docker_context(
    config, monkeypatch, capsys
):
    commands = []
    monkeypatch.setattr(
        docker.subprocess,
        "run",
        lambda argv, **kw: commands.append(argv) or subprocess.CompletedProcess(argv, 0),
    )
    docker.build_images(config, list(providers.CLIS))
    assert len(commands) == 4
    for cli, argv in zip(providers.CLIS, commands, strict=True):
        assert argv[:2] == ["/fake/docker", "build"]
        assert argv[argv.index("--target") + 1] == cli
        assert f"CLI_VERSION={config['clis'][cli]['version']}" in argv
        assert argv[-1] == str(harness.HERE / "docker")
        assert "push" not in argv and "--push" not in argv
    assert "Built modelspec-harness-codex:0.160.0" in capsys.readouterr().out


@pytest.mark.parametrize("version", ["latest", "0.160", "0.160.0-rc1", "0.159.9"])
def test_invalid_or_old_codex_image_version_is_rejected(version, config):
    config["clis"]["codex"]["version"] = version
    with pytest.raises(ValueError):
        harness.validate_config(config)


def test_version_measurement_has_no_login_volume_and_mismatch_refuses_doctor(
    config, tmp_path, monkeypatch
):
    seen = []

    def run(cli, cfg, workspace, argv, env, **kwargs):
        seen.append((cli, argv, kwargs))
        return subprocess.CompletedProcess(argv, 0, "codex-cli 0.159.9", "")

    monkeypatch.setattr(homes, "run_cli", run)
    with pytest.raises(ValueError, match="pinned image version"):
        homes.binary_identity("codex", config, tmp_path)
    assert seen == [("codex", ["codex", "--version"], {"home": False})]


def test_inventory_action_has_an_ephemeral_home_and_never_certifies_or_authenticates(
    config, tmp_path, monkeypatch, capsys
):
    config_path = tmp_path / "config.yaml"
    config_path.write_text(yaml.safe_dump(config))
    calls = []

    def inspect(cli, cfg, workspace, env, mcp_file, **kwargs):
        assert cfg["_anonymous_home"] is True
        assert workspace.is_relative_to(tmp_path) and "MODELSPEC_API_KEY" not in env
        calls.append(cli)
        return native_inventory(cli)

    monkeypatch.setattr(inventory, "inspect_inventory", inspect)
    monkeypatch.setattr(auth, "authentication_status", lambda *a: pytest.fail("auth was queried"))
    monkeypatch.setattr(providers, "_execute", lambda *a, **k: pytest.fail("model started"))
    assert (
        harness.main(
            ["inventory", "--cli", "codex", "--config", str(config_path), "--out", str(tmp_path)]
        )
        == 0
    )
    assert calls == ["codex"] and '"certified": false' in capsys.readouterr().out
    assert not list(tmp_path.glob(".tui-state/*/tui-isolation.json"))


def test_doctor_runs_the_auth_version_and_paired_controls_through_fake_docker(
    config, tmp_path, monkeypatch
):
    calls = []
    monkeypatch.setattr(homes, "run_cli", docker.run_cli)
    monkeypatch.setattr(isolation, "authentication_status", auth.authentication_status)
    monkeypatch.setattr(providers, "authentication_status", auth.authentication_status)

    def run(argv, **kwargs):
        assert argv[:3] == ["/fake/docker", "run", "--rm"]
        native_at = argv.index("sha256:" + "a" * 64) + 3
        native = argv[native_at:]
        mode = argv[native_at - 1]
        calls.append((native, mode, argv))
        if native == ["claude", "auth", "status"]:
            stdout = '{"loggedIn":true,"authMethod":"claude.ai"}'
        elif native == ["claude", "--version"]:
            stdout = "2.1.289 (Claude Code)"
            assert not any("type=volume" in value for value in argv)
        else:
            assert native[0:2] == ["claude", "--print"]
            marker = "OK"
            if mode == "positive":
                root = kwargs["cwd"]
                marker = re.search(r"MODEL301_CANARY_\w+", (root / "CLAUDE.md").read_text())[0]
                (root / "model301-hook-fired").touch()
                (root / "model301-mcp-fired").touch()
            stdout = text(
                [
                    {
                        "type": "system",
                        "subtype": "init",
                        "apiKeySource": "none",
                        "skills": ["model301_canary"] if mode == "positive" else [],
                        "plugins": [],
                        "mcp_servers": [],
                        "tools": [],
                    },
                    {"type": "result", "result": marker, "num_turns": 1},
                ]
            )
        return subprocess.CompletedProcess(argv, 0, stdout, "")

    monkeypatch.setattr(docker.subprocess, "run", run)
    result = harness.verify_isolation("claude", config, tmp_path)
    assert result["verified"] and result["canary_runs"] == 2
    assert result["schema"] == 4 and isolation.isolation_result("claude", config)["verified"]
    prompts = [(native, mode) for native, mode, _ in calls if "--print" in native]
    assert [mode for _, mode in prompts] == ["positive", "isolated"]
    assert all("MODELSPEC_API_KEY" not in argv for _, _, argv in calls)


@pytest.mark.parametrize("bad", ["missing", "version", "uid", "vendor_env", "entrypoint"])
def test_build_identity_rejects_missing_changed_or_key_bearing_images(
    bad, config, monkeypatch, capsys
):
    row = {
        "Id": "sha256:" + "a" * 64,
        "Os": "linux",
        "Architecture": "arm64",
        "Config": {
            "Labels": {
                "modelspec.cli": "codex",
                "modelspec.cli_version": "0.160.0",
                "modelspec.agent_uid": str(os.getuid()),
            },
            "User": "agent",
            "Entrypoint": ["python3", "/opt/modelspec-harness/entrypoint.py"],
            "Env": ["HOME=/home/agent", "PATH=/usr/local/bin:/usr/bin:/bin"],
        },
    }
    if bad == "version":
        row["Config"]["Labels"]["modelspec.cli_version"] = "0.159.9"
    elif bad == "uid":
        row["Config"]["Labels"]["modelspec.agent_uid"] = "9999"
    elif bad == "vendor_env":
        row["Config"]["Env"].append("OPENAI_API_KEY=never-print-this")
    elif bad == "entrypoint":
        row["Config"]["Entrypoint"] = ["sh", "-c"]

    def inspect(argv, **kwargs):
        if argv[1:] == ["info"]:
            return subprocess.CompletedProcess(argv, 0, "", "")
        assert argv[1:3] == ["image", "inspect"]
        return subprocess.CompletedProcess(
            argv, 1 if bad == "missing" else 0, json.dumps([row]), ""
        )

    monkeypatch.setattr(docker.subprocess, "run", inspect)
    with pytest.raises(ValueError, match="image is missing or invalid"):
        IMAGE_IDENTITY("codex", config)
    assert "never-print-this" not in repr(capsys.readouterr())


@pytest.mark.parametrize("running", [False, True])
def test_missing_image_is_distinguished_from_stopped_docker(config, monkeypatch, running):
    calls = []
    def run(argv, **kwargs):
        calls.append(argv[1:])
        return subprocess.CompletedProcess(argv, int(not running) if argv[1:] == ["info"] else 1,
                                           "", "Cannot connect to the Docker daemon")
    monkeypatch.setattr(docker.subprocess, "run", run)
    message = "image is missing or invalid" if running else "Docker Desktop is not running"
    with pytest.raises(ValueError, match=message):
        IMAGE_IDENTITY("codex", config)
    assert calls == [["image", "inspect", "modelspec-harness-codex:0.160.0"], ["info"]]


def test_codex_account_plugin_listing_is_reported_and_never_assumed_disabled(
    config, tmp_path, monkeypatch
):
    monkeypatch.setattr(inventory, "_codex_skills", lambda *a: [])

    def run(argv, **kwargs):
        if argv[-3:] == ["mcp", "list", "--json"]:
            value = [
                {
                    "name": "modelspec",
                    "enabled": True,
                    "transport": {"type": "streamable_http", "url": config["mcp_url"]},
                }
            ]
        elif argv[-3:] == ["plugin", "list", "--json"]:
            value = {
                "installed": [{"name": "account-app", "enabled": True, "scope": "account"}],
                "available": [],
            }
        elif argv[-2:] == ["features", "list"]:
            return subprocess.CompletedProcess(argv, 0, "hooks stable false\n", "")
        else:
            value = [{"type": "message", "content": [{"type": "input_text", "text": "context"}]}]
        return subprocess.CompletedProcess(argv, 0, json.dumps(value), "")

    monkeypatch.setattr(docker.subprocess, "run", run)
    mcp = tmp_path / "mcp.toml"
    mcp.write_text(homes.home_config("codex", config))
    result = inventory.inspect_inventory(
        "codex", config, tmp_path, docker.passed_environment(config), mcp, mcp_enabled=True
    )
    assert result["plugins"] == [{"name": "account-app", "enabled": True, "scope": "account"}]
    assert result["extensions"] == ["account-app"]
    assert inventory.inventory_violation(result, mcp_enabled=True) == "CLI loaded user extensions"


def test_gemini_lifecycle_notices_are_recognized_but_unknown_diagnostics_remain_failures():
    output = "No skills discovered.\n" + "\n".join(sorted(inventory.GEMINI_MCP_NOTICES))
    assert inventory.gemini_skill_listing(output) == "No skills discovered."
    assert "warning" in inventory.gemini_skill_listing(
        output + "\nwarning: unknown discovery failure"
    )
    assert "foreign" in inventory.gemini_skill_listing(
        "Server 'foreign' supports tool updates. Listening for changes...\nNo skills discovered."
    )
