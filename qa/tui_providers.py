"""CLI commands and streams. Launch requires measured isolation evidence."""

from __future__ import annotations

import json
import os
import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from time import perf_counter

from qa.contracts import TOOL_NAMES
from qa.providers import redact
from qa.tui_auth import authentication_status
from qa.tui_docker import container_path, passed_environment, run_cli
from qa.tui_homes import (
    block_gemini_dotenv,
)

CLIS = ("claude", "codex", "gemini", "grok")
FAMILY = {"claude": "anthropic", "codex": "openai", "gemini": "google", "grok": "xai"}
CLAUDE_SETTINGS = {
    "disableAllHooks": True,
    "autoMemoryEnabled": False,
    "disableClaudeAiConnectors": True,
    "disableCommandPluginSources": True,
    "enabledPlugins": {},
}
# Do not inherit API keys, prompt injection variables, remote-daemon addresses,
# provider endpoints, config homes, plugin paths, or shell startup overrides.
BASE_ENV = ("TERM", "LANG", "MODELSPEC_MCP_URL")


def child_environment(
    cli: str,
    workspace: Path,
    token_env: str | None = None,
    *,
    settings: dict,
    isolated: bool = True,
    mcp_url: str = "https://api.modelspec.dev/mcp",
) -> dict:
    return passed_environment({"mcp_url": mcp_url, "mcp_token_env": token_env}, token=True)


def build_command(
    cli: str,
    settings: dict,
    workspace: Path,
    prompt: str,
    mcp_file: Path,
    turn_cap: int,
    *,
    isolated: bool = True,
) -> list[str]:
    """Build native headless arguments; launch() separately enforces doctor evidence."""
    executable, model = settings["executable"], settings["model"]
    if cli == "claude":
        common = [
            executable,
            "--print",
            "--output-format",
            "stream-json",
            "--verbose",
            "--model",
            model,
            "--effort",
            settings["effort"],
            "--max-turns",
            str(turn_cap),
            "--no-session-persistence",
            "--no-chrome",
        ]
        controls = (
            [
                "--setting-sources",
                "",
                "--settings",
                json.dumps(CLAUDE_SETTINGS),
                "--disable-slash-commands",
                "--strict-mcp-config",
            ]
            if isolated
            else []
        )
        return (
            common
            + controls
            + (["--mcp-config", container_path(workspace, mcp_file)] if isolated else [])
            + [
                "--tools",
                "",
                "--permission-mode",
                "dontAsk",
                "--allowedTools",
                "mcp__modelspec__*" if isolated else "mcp__model301_canary__*",
                "--",
                prompt,
            ]
        )
    if cli == "codex":
        common = [
            executable,
            "--no-daemon",
            "exec",
            "--ephemeral",
            "--skip-git-repo-check",
            "--json",
            "--sandbox",
            "read-only",
            "-m",
            model,
            "--cd",
            "/work",
        ]
        if isolated:
            common += [
                "--ignore-user-config",
                "--ignore-rules",
            ]
            common += codex_config_args(settings, mcp_file)
        else:
            common += [
                "--dangerously-bypass-hook-trust",
                "-c",
                f"model_reasoning_effort={settings['effort']}",
            ]
        return common + ["--", prompt]
    if cli == "gemini":
        common = [
            executable,
            "--model",
            model,
            "--output-format",
            "stream-json",
        ]
        if isolated:
            common += ["--extensions", "none"]
        return common + [
            "--allowed-mcp-server-names",
            "modelspec" if isolated else "model301_canary",
            "--prompt",
            prompt,
        ]
    if cli == "grok":
        return [
            executable,
            "-m",
            model,
            "--reasoning-effort",
            settings["effort"],
            "--cwd",
            "/work",
            "--output-format",
            "streaming-messages-json",
            "--max-turns",
            str(turn_cap),
            "--no-subagents",
            "--disable-web-search",
            "--tools",
            "",
            "--single",
            prompt,
        ]
    raise ValueError(f"Unknown CLI: {cli}")


def codex_config_args(settings: dict, mcp_file: Path) -> list[str]:
    import tomllib

    args = []
    for value in (
        f"model_reasoning_effort={settings['effort']}",
        "project_doc_max_bytes=0",
        "skills.include_instructions=false",
        "skills.config=[]",
        "features.hooks=false",
        "plugins={}",
        'cli_auth_credentials_store="file"',
        'forced_login_method="chatgpt"',
        "mcp_servers={}",
    ):
        args += ["-c", value]
    servers = tomllib.loads(mcp_file.read_text()).get("mcp_servers", {})
    for name, server in servers.items():
        for key, value in server.items():
            args += ["-c", f"mcp_servers.{name}.{key}={json.dumps(value)}"]
    return args


def mcp_config(url: str, token_env: str | None, *, enabled: bool) -> dict:
    if not enabled:
        return {"mcpServers": {}}
    server = {"type": "http", "url": url}
    if token_env and os.environ.get(token_env):
        # Claude expands this itself. The harness never puts the secret in argv.
        server["headers"] = {"Authorization": "Bearer ${" + token_env + "}"}
    return {"mcpServers": {"modelspec": server}}


def json_events(output: str) -> list[dict]:
    try:
        document = json.loads(output)
    except ValueError:
        events = []
        for line in output.splitlines():
            try:
                event = json.loads(line)
            except ValueError:
                continue
            if isinstance(event, dict):
                events.append(event)
        return events
    if isinstance(document, dict):
        return [document]
    if isinstance(document, list):
        return [event for event in document if isinstance(event, dict)]
    return []


def _arguments(value):
    if isinstance(value, str):
        try:
            return json.loads(value)
        except ValueError:
            pass
    return value


def _tool_name(name: str, server: str | None = None) -> tuple[str | None, str]:
    if server is not None:
        return server, name
    for prefix in ("mcp__modelspec__", "modelspec__", "modelspec/", "modelspec."):
        if name.startswith(prefix):
            return "modelspec", name[len(prefix) :]
    if name in TOOL_NAMES:
        return "modelspec", name
    if name.startswith("mcp__"):
        parts = name.split("__", 2)
        if len(parts) == 3:
            return parts[1], parts[2]
    return None, name


def _result(value, is_error=False) -> dict:
    if isinstance(value, dict) and "content" in value:
        return value | {"isError": value.get("isError", is_error)}
    return {
        "content": value
        if isinstance(value, list)
        else [{"type": "text", "text": value if isinstance(value, str) else json.dumps(value)}],
        "isError": is_error,
    }


@dataclass
class Transcript:
    final_answer: str = ""
    turns: int | None = None
    turns_basis: str = "unavailable"
    tool_calls: list[dict] = field(default_factory=list)
    other_tool_calls: list[dict] = field(default_factory=list)
    tokens_in: int | None = None
    tokens_out: int | None = None
    cost_usd: float | None = None
    usage: dict | None = None
    init: dict | None = None
    hook_events: list[dict] = field(default_factory=list)
    model: str | None = None
    terminal: bool = False
    errors: list[str] = field(default_factory=list)

    @property
    def first_decide_call(self) -> int | None:
        return next(
            (i for i, call in enumerate(self.tool_calls, 1) if call["name"] == "decide"), None
        )


def parse_transcript(cli: str, output: str) -> Transcript:
    """Keep ordered calls and their results, never count streaming deltas twice."""
    parsed = Transcript()
    calls, message_ids = {}, set()
    assistant_turns, codex_turns = 0, 0
    gemini_text = ""

    def call(identity, name, arguments, server=None):
        server, name = _tool_name(name, server)
        identity = str(identity)
        if identity not in calls:
            record = {
                "id": identity,
                "server": server,
                "name": name,
                "arguments": _arguments(arguments),
                "result": _result(None),
                "result_observed": False,
                "latency_ms": None,
                "api_call": True,
                "validation_errors": [],
                "unknown_facets": [],
                "unadvertised_facets": [],
            }
            calls[identity] = record
            (parsed.tool_calls if server is not None else parsed.other_tool_calls).append(record)
        elif arguments:
            calls[identity]["arguments"] = _arguments(arguments)
        return calls[identity]

    def finish(identity, value, is_error=False):
        if str(identity) in calls:
            calls[str(identity)].update(result=_result(value, is_error), result_observed=True)

    for event in json_events(output):
        kind = event.get("type")
        if hook_event(event):
            parsed.hook_events.append(event)
        if kind == "system" and event.get("subtype") == "init" or kind == "init":
            parsed.init = event
            parsed.model = event.get("model")
        if kind in ("error", "turn.failed") or kind is None and event.get("error"):
            parsed.errors.append(json.dumps(event.get("error", event.get("message", event))))
        if kind in ("assistant", "user"):
            message = event.get("message", {})
            if kind == "assistant":
                identity = message.get("id", event.get("uuid"))
                if identity is None or identity not in message_ids:
                    assistant_turns += 1
                    message_ids.add(identity)
                text = "".join(
                    block.get("text", "")
                    for block in message.get("content", [])
                    if block.get("type") == "text"
                )
                if text:
                    parsed.final_answer = text
                for block in message.get("content", []):
                    if block.get("type") in ("tool_use", "server_tool_use"):
                        call(block["id"], block["name"], block.get("input", {}))
            else:
                for block in message.get("content", []):
                    if block.get("type") == "tool_result":
                        finish(
                            block["tool_use_id"], block.get("content"), block.get("is_error", False)
                        )
        if cli == "codex":
            if kind == "turn.started":
                codex_turns += 1
            if kind in ("item.started", "item.completed"):
                item = event.get("item", {})
                if item.get("type") == "mcp_tool_call":
                    record = call(
                        item["id"], item["tool"], item.get("arguments", {}), item["server"]
                    )
                    if kind == "item.completed":
                        finish(
                            item["id"],
                            item.get("result", item.get("error")),
                            bool(item.get("error")),
                        )
                    if "duration_ms" in item:
                        record["latency_ms"] = item["duration_ms"]
                elif item.get("type") == "agent_message" and kind == "item.completed":
                    parsed.final_answer = item.get("text", "")
                elif item.get("type") in ("command_execution", "web_search", "file_change"):
                    call(item["id"], item["type"], item.get("command", {}))
            if kind == "turn.completed":
                parsed.terminal = True
                parsed.usage = event.get("usage")
                parsed.turns, parsed.turns_basis = codex_turns, "CLI turn.started events"
        if cli == "gemini":
            if kind == "message" and event.get("role") == "assistant":
                if event.get("delta"):
                    gemini_text += event.get("content", "")
                else:
                    gemini_text = event.get("content", "")
                    assistant_turns += 1
                parsed.final_answer = gemini_text
            if kind == "tool_use":
                call(event["tool_id"], event["tool_name"], event.get("parameters", {}))
                gemini_text = ""
            if kind == "tool_result":
                finish(event["tool_id"], event.get("output"), event.get("status") == "error")
        if kind in ("result", "end") or kind is None and "response" in event:
            parsed.terminal = True
            parsed.final_answer = event.get("result", event.get("response", parsed.final_answer))
            if not isinstance(parsed.final_answer, str):
                parsed.final_answer = json.dumps(parsed.final_answer)
            if type(event.get("num_turns")) is int:
                parsed.turns, parsed.turns_basis = event["num_turns"], "CLI num_turns"
            if event.get("is_error") or event.get("status") == "error":
                parsed.errors.append(
                    json.dumps(event.get("error", event.get("errors", parsed.final_answer)))
                )
            parsed.usage = event.get("usage", event.get("stats"))
            parsed.cost_usd = event.get("total_cost_usd", event.get("cost_usd"))
            if event.get("model"):
                parsed.model = event["model"]
    if parsed.turns is None and assistant_turns:
        parsed.turns, parsed.turns_basis = assistant_turns, "distinct assistant messages"
    if parsed.usage:
        usage = parsed.usage
        if "input_tokens" in usage:
            parsed.tokens_in = usage["input_tokens"] + usage.get("cache_creation_input_tokens", 0)
            if cli in ("claude", "grok"):
                parsed.tokens_in += usage.get("cache_read_input_tokens", 0)
            parsed.tokens_out = usage.get("output_tokens")
        elif "models" in usage:
            token_rows = [row["tokens"] for row in usage["models"].values() if "tokens" in row]
            if token_rows:
                parsed.tokens_in = sum(row.get("prompt", 0) for row in token_rows)
                parsed.tokens_out = sum(
                    row.get("candidates", 0) + row.get("thoughts", 0) for row in token_rows
                )
                parsed.turns = (
                    sum(
                        row.get("api", {}).get("totalRequests", 0)
                        for row in usage["models"].values()
                    )
                    or parsed.turns
                )
                parsed.turns_basis = "Gemini stats.models API requests"
    return parsed


LIMIT_MESSAGE = re.compile(
    r"usage[_ -]?limit|rate[_ -]?limit|quota.{0,35}(?:exceed|exhaust)|resource_exhausted|"
    r"too many requests|(?:hit|reached|exceeded).{0,25}(?:usage |rate |weekly |daily )?limit|"
    r"(?:out of|exhausted|insufficient) credits|limit_reached",
    re.I,
)
LIMIT_ANSWER = re.compile(
    r"^\s*(?:you(?:'ve| have) (?:hit|reached)|usage limit|rate limit|"
    r"quota exceeded|resource_exhausted)",
    re.I,
)


def usage_limit(parsed: Transcript, stderr: str, code: int, exit_codes: list[int]) -> str | None:
    if code in exit_codes:
        return f"CLI usage-limit exit code {code}"
    for message in [stderr, *parsed.errors]:
        if LIMIT_MESSAGE.search(message):
            return redact(message.strip())[:500]
    if LIMIT_ANSWER.search(parsed.final_answer) and LIMIT_MESSAGE.search(parsed.final_answer):
        return redact(parsed.final_answer)[:500]
    return None


def hook_event(event: dict) -> bool:
    kind = str(event.get("type", "")).lower()
    if "hook" in kind or "hook" in str(event.get("subtype", "")).lower():
        return True
    if kind not in ("init", "system"):
        return False

    def contains_hook(value):
        if isinstance(value, dict):
            return any(
                (key.lower().startswith("hook") and bool(item)) or contains_hook(item)
                for key, item in value.items()
            )
        if isinstance(value, list):
            return any(contains_hook(item) for item in value)
        return False

    return contains_hook(event)


def subscription_violation(cli: str, parsed: Transcript) -> str | None:
    if cli == "claude" and (
        parsed.init is None
        or parsed.init.get("apiKeySource") not in ("none", "subscription", "oauth")
    ):
        return "Claude did not attest subscription authentication in init.apiKeySource"
    return None


def isolation_violation(
    parsed: Transcript, *, mcp_enabled: bool, cli="claude", inventory: dict | None = None
) -> str | None:
    if parsed.hook_events or parsed.init and hook_event(parsed.init):
        return "CLI emitted a hook event"
    allowed = {"modelspec"} if mcp_enabled else set()
    if parsed.other_tool_calls or any(call["server"] not in allowed for call in parsed.tool_calls):
        return "CLI used a tool outside the configured ModelSpec MCP"
    if cli != "claude":
        from qa.tui_inventory import inventory_violation

        return inventory_violation(inventory, mcp_enabled=mcp_enabled)
    if parsed.init is None:
        return "CLI did not expose its startup inventory"
    for key in ("skills", "plugins", "mcp_servers", "tools"):
        if key not in parsed.init or not isinstance(parsed.init[key], list):
            return f"CLI startup inventory omitted or malformed {key}"
    if parsed.init["skills"]:
        return "CLI loaded skills"
    if any(
        not isinstance(plugin, dict) or plugin.get("path") != "builtin"
        for plugin in parsed.init["plugins"]
    ):
        return "CLI loaded a non-builtin plugin"
    if any(
        not isinstance(server, dict) or server.get("name") not in allowed
        for server in parsed.init["mcp_servers"]
    ):
        return "CLI loaded another MCP server"
    for name in parsed.init["tools"]:
        if not isinstance(name, str) or _tool_name(name)[0] not in allowed:
            return "CLI exposed an unapproved tool"
    if mcp_enabled and not any(
        server.get("name") == "modelspec" and server.get("status") == "connected"
        for server in parsed.init["mcp_servers"]
    ):
        return "ModelSpec MCP did not connect"
    return None


@dataclass
class Execution:
    transcript: Transcript
    exit_code: int | None
    wall_time_ms: float
    status: str
    error: str | None = None
    limit_reason: str | None = None
    observed_output: str = field(default="", repr=False)
    inventory: dict | None = None


def launch(cli: str, config: dict, workspace: Path, prompt: str, *, mcp_enabled: bool) -> Execution:
    from qa.tui_isolation import isolation_result

    result = isolation_result(cli, config)
    if not result["verified"]:
        raise ValueError(result["reason"])
    execution = _execute(cli, config, workspace, prompt, mcp_enabled=mcp_enabled)
    violation = subscription_violation(cli, execution.transcript) or isolation_violation(
        execution.transcript, mcp_enabled=mcp_enabled, cli=cli, inventory=execution.inventory
    )
    if execution.status in ("isolation_failed", "transcript_error") or violation:
        from qa.tui_homes import state_directory
        from qa.tui_isolation import receipt_file

        receipt_file(state_directory(cli, config)).unlink(missing_ok=True)
    return execution


def _execute(
    cli: str,
    config: dict,
    workspace: Path,
    prompt: str,
    *,
    mcp_enabled: bool,
    isolated: bool = True,
    probe_mcp: Path | None = None,
) -> Execution:
    from qa.tui_homes import home_config

    settings = config["clis"][cli]
    with_token = mcp_enabled and bool(os.environ.get(config.get("mcp_token_env") or ""))
    mcp_file = probe_mcp or workspace / "modelspec-mcp.json"
    if probe_mcp is None:
        mcp_file.write_text(home_config(cli, config, enabled=mcp_enabled, with_token=with_token))
    prepare_workspace(
        cli, config, workspace, mcp_enabled=mcp_enabled, isolated=isolated, with_token=with_token
    )
    command = build_command(
        cli,
        settings,
        workspace,
        prompt,
        mcp_file,
        config["turn_cap"],
        isolated=isolated,
    )
    env = child_environment(
        cli,
        workspace,
        config.get("mcp_token_env") if mcp_enabled else None,
        settings=settings,
        isolated=isolated,
        mcp_url=config["mcp_url"],
    )
    started = perf_counter()
    authentication = authentication_status(cli, config, workspace, env)
    if not authentication["verified"] or authentication["logged_in"] is not True:
        return Execution(
            Transcript(),
            None,
            (perf_counter() - started) * 1000,
            "isolation_failed",
            authentication.get("reason") or "Native CLI does not report subscription login",
        )
    inventory = None
    if isolated and cli != "claude":
        from qa.tui_inventory import inspect_inventory, inventory_violation

        inventory = inspect_inventory(
            cli, config, workspace, env, mcp_file, mcp_enabled=mcp_enabled
        )
        if violation := inventory_violation(inventory, mcp_enabled=mcp_enabled):
            return Execution(
                Transcript(),
                None,
                (perf_counter() - started) * 1000,
                "isolation_failed",
                violation,
                inventory=inventory,
            )
        if cli == "codex":
            command[command.index("--") : command.index("--")] = ["-c", inventory["skill_config"]]
    try:
        # Empty piped stdin is essential: a launching shell's heredoc must never
        # become extra user context in a CLI that appends stdin to its prompt.
        process = run_cli(cli, config, workspace, command, env, isolated=isolated)
    except subprocess.TimeoutExpired as exc:
        output = exc.stdout or b""
        output = output.decode(errors="replace") if isinstance(output, bytes) else output
        stderr = exc.stderr or b""
        stderr = stderr.decode(errors="replace") if isinstance(stderr, bytes) else stderr
        try:
            parsed = parse_transcript(cli, output)
        except (ValueError, KeyError, TypeError, AttributeError):
            parsed = Transcript()
        parsed.hook_events.extend(event for event in json_events(stderr) if hook_event(event))
        violation = subscription_violation(cli, parsed)
        if isolated:
            violation = violation or isolation_violation(
                parsed, mcp_enabled=mcp_enabled, cli=cli, inventory=inventory
            )
        limit = usage_limit(parsed, stderr, -1, [])
        return Execution(
            parsed,
            None,
            (perf_counter() - started) * 1000,
            "usage_limit" if limit else "isolation_failed" if violation else "timeout",
            violation or "CLI timed out",
            limit,
            output + stderr,
            inventory,
        )
    except OSError as exc:
        return Execution(
            Transcript(),
            None,
            (perf_counter() - started) * 1000,
            "cli_error",
            f"Cannot start CLI ({type(exc).__name__})",
            inventory=inventory,
        )
    try:
        parsed = parse_transcript(cli, process.stdout)
        parsed.hook_events.extend(
            event for event in json_events(process.stderr) if hook_event(event)
        )
        violation = subscription_violation(cli, parsed)
        if isolated:
            violation = violation or isolation_violation(
                parsed, mcp_enabled=mcp_enabled, cli=cli, inventory=inventory
            )
    except (ValueError, KeyError, TypeError, AttributeError):
        return Execution(
            Transcript(),
            process.returncode,
            (perf_counter() - started) * 1000,
            "transcript_error",
            "CLI emitted an invalid structured transcript",
            observed_output=process.stdout + process.stderr,
            inventory=inventory,
        )
    limit = usage_limit(
        parsed, process.stderr, process.returncode, settings["usage_limit_exit_codes"]
    )
    if limit:
        status = "usage_limit"
    elif violation:
        status = "isolation_failed"
    elif process.returncode or parsed.errors:
        status = "cli_error"
    elif not parsed.terminal:
        status = "transcript_error"
    elif not parsed.final_answer.strip():
        status = "empty_answer"
    else:
        status = "completed"
    error = (
        violation
        if violation
        else (
            redact("; ".join(parsed.errors) or process.stderr)[:500]
            if status == "cli_error"
            else None
        )
    )
    return Execution(
        parsed,
        process.returncode,
        (perf_counter() - started) * 1000,
        status,
        error,
        limit,
        process.stdout + process.stderr,
        inventory,
    )


def prepare_workspace(
    cli: str,
    config: dict,
    workspace: Path,
    *,
    mcp_enabled: bool,
    isolated: bool = True,
    with_token: bool = False,
) -> None:
    from qa.tui_homes import home_config

    if cli == "gemini":
        data = (
            json.loads(home_config(cli, config, enabled=mcp_enabled, with_token=with_token))
            if isolated
            else {}
        )
        if isolated:
            data.update(
                skills={"enabled": False},
                hooksConfig={"enabled": False},
                context={"fileName": []},
                mcp={"allowed": ["modelspec"] if mcp_enabled else ["model301_none"]},
            )
        # Only these private temporary workspaces are trusted, including the
        # relaxed control so project discovery really runs there.
        data["security"] = {"folderTrust": {"enabled": False}}
        # Project MCP controls coexist with planted cwd hooks and skills. The
        # user layer disables hooks/skills without replacing a cwd canary file.
        native = workspace / ".gemini"
        native.mkdir(mode=0o700, exist_ok=True)
        path = native / "settings.json"
        if not path.exists():
            path.write_text(json.dumps(data))
        # Stop native .env discovery here, before it can walk into the real HOME.
        block_gemini_dotenv(workspace)
    if cli == "grok" and isolated:
        native = workspace / ".grok"
        native.mkdir(mode=0o700, exist_ok=True)
        (native / "config.toml").write_text(
            home_config(cli, config, enabled=mcp_enabled, with_token=with_token)
        )
        (workspace / ".gitignore").write_text(
            "AGENTS.md\nAgents.md\nAGENT.md\nClaude.md\nCLAUDE.md\nCLAUDE.local.md\n"
            ".agents/\n.claude/\n.cursor/\n.grok/skills/\n.grok/hooks/\n.grok/rules/\n"
            ".grok/agents/\n.grok/plugins/\n"
        )
