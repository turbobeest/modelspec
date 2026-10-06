"""CLI commands and streams. Launch requires measured isolation evidence."""

from __future__ import annotations

import json
import os
import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from time import perf_counter, sleep

from qa.contracts import TOOL_NAMES
from qa.docker.entrypoint import refuse_vendor_auth
from qa.providers import redact
from qa.tui_auth import authentication_status
from qa.tui_docker import GROK_USER_CONFIG, container_path, passed_environment, run_cli
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
SEARCH_TOOLS = {
    "claude": {"WebSearch", "WebFetch", "web_search", "web_fetch"},
    "codex": {"web_search"},
    "gemini": {"google_web_search"},
    "grok": {"web_search", "web_fetch", "x_search", "WebSearch", "WebFetch", "XSearch"},
}
# Codex has no switch for these built-ins. Transcripts report server "codex".
CODEX_RESOURCE_TOOLS = frozenset({
    "list_mcp_resources",
    "list_mcp_resource_templates",
    "read_mcp_resource",
})
CODEX_ISOLATED_FEATURES = (
    "shell_tool",
    "unified_exec",
    "view_image",
    "image_generation",
    "browser_use",
    "browser_use_external",
    "computer_use",
    "multi_agent",
    "goals",
    "tool_suggest",
    "skill_search",
    "in_app_browser",
    "in_app_local_automation",
)
PROMPT_MARKER = "<private prompt>"
PROMPT_FILE = "/work/.prompt.txt"


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
    purpose: str = "scenario",
) -> list[str]:
    """Build native headless arguments; launch() separately enforces doctor evidence."""
    executable, model = settings["executable"], settings["model"]
    if purpose not in ("scenario", "judge", "browser", "search"):
        raise ValueError("Unknown subscription tool purpose")
    search = purpose == "search"
    server = "playwright" if purpose == "browser" else "modelspec"
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
                "WebSearch,WebFetch" if search else "",
                "--permission-mode",
                "dontAsk",
                "--allowedTools",
                "WebSearch,WebFetch" if search else f"mcp__{server}__*" if isolated else "mcp__model301_canary__*",
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
            common += ["-c", 'web_search="live"' if search else 'web_search="disabled"']
        else:
            common += [
                "--dangerously-bypass-hook-trust",
                "-c",
                f"model_reasoning_effort={settings['effort']}",
            ]
        return common + ["--", "-"]
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
            ("model309_none" if search else server) if isolated else "model301_canary",
            "--prompt",
            prompt,
        ]
    if cli == "grok":
        command = [
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
            "--tools",
            # An empty list keeps every built-in; these two reach MCP tools and nothing else.
            "web_search,web_fetch,x_search" if search else "search_tool,use_tool",
            "--permission-mode", "dontAsk",
            "--allow",
            "web_search" if search else f"mcp__{server}__*" if isolated else "mcp__model301_canary__*",
            "--prompt-file",
            PROMPT_FILE,
        ]
        if not search:
            command.insert(command.index("--tools"), "--disable-web-search")
        else:
            # Grok permission rules use Claude-style names; "web_fetch" matches nothing,
            # and a denied fetch cancels the turn. Search tools run server-side.
            command[command.index("--prompt-file"):command.index("--prompt-file")] = [
                "--allow", "WebFetch", "--allow", "x_search",
            ]
        return command
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
        # ChatGPT account apps reappear as enabled plugins after login; plugins={}
        # alone does not turn them off.
        "features.apps=false",
        "features.plugins=false",
        "features.remote_plugin=false",
        *[f"features.{name}=false" for name in CODEX_ISOLATED_FEATURES],
        # A manual full-access run persists a trust grant for /work in the login
        # volume, which would load the cwd's .codex config. Pin it untrusted.
        'projects={"/work"={trust_level="untrusted"}}',
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


def _grok_mcp_content(value, is_error=False):
    """Unwrap Grok's use_tool envelopes into MCP content blocks.

    MCP results arrive as JSON text {"type": "MCP", "output": {"OkayOutput"|"Error": text}};
    refusals as [{"type": "content", "content": block}]. Grok joins the server's text
    blocks into that string. A leading JSON object is its own block, and any remainder
    is a second text block.
    """
    try:
        decoded = json.loads(value) if isinstance(value, str) else value
    except ValueError:
        return value, is_error
    if isinstance(decoded, dict) and decoded.get("type") == "MCP":
        output = decoded.get("output")
        if isinstance(output, dict) and len(output) == 1:
            (kind, text), = output.items()
            if kind in ("OkayOutput", "Error"):
                if not isinstance(text, str):
                    text = json.dumps(text)
                blocks = [{"type": "text", "text": text}]
                if text.lstrip().startswith("{"):
                    try:
                        start = len(text) - len(text.lstrip())
                        leading, end = json.JSONDecoder().raw_decode(text, start)
                    except ValueError:
                        leading = None
                    if isinstance(leading, dict):
                        blocks = [{"type": "text", "text": text[:end].strip()}]
                        remainder = text[end:].strip()
                        if remainder:
                            blocks.append({"type": "text", "text": remainder})
                return blocks, is_error or kind == "Error"
        return value, True
    if isinstance(decoded, list) and decoded and all(
        isinstance(block, dict) and block.get("type") == "content" for block in decoded
    ):
        return [block.get("content") for block in decoded], is_error
    return value, is_error


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
                        name, arguments = block["name"], block.get("input", {})
                        if cli == "grok" and name == "use_tool" and isinstance(arguments, dict):
                            # Grok defers MCP tools behind use_tool("<server>__<tool>", input).
                            name = "mcp__" + str(arguments.get("tool_name"))
                            arguments = arguments.get("tool_input", {})
                        call(block["id"], name, arguments)
                    elif block.get("type") in ("web_search_tool_result", "web_fetch_tool_result"):
                        finish(block["tool_use_id"], block.get("content"), isinstance(block.get("content"), dict) and "error_code" in block["content"])
            else:
                for block in message.get("content", []):
                    if block.get("type") == "tool_result":
                        content, is_error = block.get("content"), block.get("is_error", False)
                        if cli == "grok":
                            content, is_error = _grok_mcp_content(content, is_error)
                        finish(block["tool_use_id"], content, is_error)
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
                    record = call(
                        item["id"], item["type"], item.get("action", item.get("command", {}))
                    )
                    if isinstance(item.get("status"), str):
                        record["status"] = item["status"]
                    if kind == "item.completed":
                        finish(item["id"], item, bool(item.get("error")))
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
    retries = {}
    for record in parsed.tool_calls:
        record["retry_of"] = retries.get(record["name"])
        record["turn"] = None  # The native CLI's tool index is not an API model turn.
        for block in record["result"].get("content", []):
            if not isinstance(block, dict) or block.get("type") != "text":
                continue
            try:
                envelope = json.loads(block["text"])
            except (ValueError, KeyError, TypeError):
                continue
            if not isinstance(envelope, dict) or envelope.get("status") not in (400, 422):
                continue
            body = envelope.get("body", {})
            error = body.get("error", {}) if isinstance(body, dict) else {}
            if not isinstance(error, dict):
                continue
            issues = error.get("issues", []) or [error.get("message", error.get("code", body))]
            record["validation_errors"] = issues
            record["api_call"] = envelope.get("origin") is not None
            record["unknown_facets"] = sorted({
                issue.get("field", issue.get("facet")) for issue in issues
                if isinstance(issue, dict) and isinstance(issue.get("field", issue.get("facet")), str)
                and any(word in str(issue.get("reason", issue.get("message", ""))).lower()
                        for word in ("unknown", "not registered", "unregistered"))
            })
        if record["result"].get("isError"):
            retries[record["name"]] = record["id"]
        else:
            retries.pop(record["name"], None)
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


def _allowed_servers(mcp_enabled: bool, allowed_servers) -> set:
    if not mcp_enabled:
        return set()
    if allowed_servers is None:
        return {"modelspec"}
    return set(allowed_servers)


def _native_tools(cli: str, purpose: str) -> set:
    native = set(SEARCH_TOOLS[cli]) if purpose == "search" else set()
    if cli == "grok" and purpose != "search":
        # Grok's deferred-tool lookup. It runs no tool; use_tool calls are checked by server.
        native.add("search_tool")
    return native


def _offending_call(call: dict, *, cli: str, native: set, allowed: set) -> str | None:
    name = call.get("name")
    if not isinstance(name, str) or not name:
        return "unnamed"
    if cli == "codex" and name in CODEX_RESOURCE_TOOLS:
        arguments = call.get("arguments")
        if not isinstance(arguments, dict):
            return name
        server = arguments.get("server")
        if "server" not in arguments or server is None or server in allowed:
            return None
        return name
    if call.get("server") is None:
        return None if name in native else name
    if call.get("server") not in allowed:
        return name
    return None


def misuse_calls(
    parsed: Transcript, *, mcp_enabled: bool, cli="claude", allowed_servers=None, purpose="scenario",
) -> list[tuple[str, dict]]:
    """Disallowed calls in transcript order, classified the same way as tool_misuse."""
    allowed = _allowed_servers(mcp_enabled, allowed_servers)
    native = _native_tools(cli, purpose)
    found = []
    for call in [*parsed.other_tool_calls, *parsed.tool_calls]:
        name = _offending_call(call, cli=cli, native=native, allowed=allowed)
        if name:
            found.append((name, call))
    return found


def tool_misuse(
    parsed: Transcript, *, mcp_enabled: bool, cli="claude", allowed_servers=None, purpose="scenario",
) -> list[str]:
    """Tool names this transcript called outside the run's allowlist.

    Codex resource tools are lookups. They are allowed when their server argument
    is absent or names an allowed MCP server. Any other server is misuse.
    """
    found, seen = [], set()
    for name, _call in misuse_calls(
        parsed, mcp_enabled=mcp_enabled, cli=cli, allowed_servers=allowed_servers, purpose=purpose,
    ):
        if name not in seen:
            seen.add(name)
            found.append(name)
    return found


def _result_text(result: dict) -> str:
    content = result.get("content")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict) and isinstance(block.get("text"), str):
                parts.append(block["text"])
        return "\n".join(parts)
    return ""


def _codex_item_status(call: dict, result: dict, blob: str) -> str | None:
    for source in (call.get("status"), result.get("status")):
        if isinstance(source, str):
            return source.lower()
    try:
        payload = json.loads(blob)
    except ValueError:
        return None
    if isinstance(payload, dict) and isinstance(payload.get("status"), str):
        return payload["status"].lower()
    return None


def disallowed_call_refused(cli: str, call: dict) -> bool:
    """A disallowed call that was not observed, errored, cancelled, or declined.

    Grok reports a permission refusal as use_tool text beginning with "User cancelled".
    Codex reports command_execution and the other built-in items with status failed
    or declined, including when the item has no error field.
    """
    if call.get("result_observed") is False:
        return True
    result = call.get("result") if isinstance(call.get("result"), dict) else {}
    if result.get("isError") is True:
        return True
    blob = _result_text(result)
    if cli == "grok" and "User cancelled" in blob:
        return True
    if cli == "codex" and _codex_item_status(call, result, blob) in ("failed", "declined"):
        return True
    return False


def misuse_error(names: list[str]) -> str:
    return "CLI used a tool outside the configured ModelSpec MCP: " + ", ".join(names)


def guard_result(
    cli: str, parsed: Transcript, *, mcp_enabled: bool, inventory: dict | None,
    allowed_servers, purpose: str, isolated: bool,
) -> tuple[str | None, list[str]]:
    """Revocation reason, then tool-misuse names. A revocation hides misuse."""
    violation = subscription_violation(cli, parsed)
    if isolated:
        violation = violation or isolation_violation(
            parsed, mcp_enabled=mcp_enabled, cli=cli, inventory=inventory,
            allowed_servers=allowed_servers, purpose=purpose,
        )
    if violation or not isolated:
        return violation, []
    return None, tool_misuse(
        parsed, mcp_enabled=mcp_enabled, cli=cli, allowed_servers=allowed_servers, purpose=purpose,
    )


def isolation_violation(
    parsed: Transcript, *, mcp_enabled: bool, cli="claude", inventory: dict | None = None,
    allowed_servers=None, purpose="scenario",
) -> str | None:
    if parsed.hook_events or parsed.init and hook_event(parsed.init):
        return "CLI emitted a hook event"
    allowed = _allowed_servers(mcp_enabled, allowed_servers)
    native = _native_tools(cli, purpose)
    if cli == "grok" and mcp_enabled:
        if parsed.init is None:
            return "CLI did not expose its startup inventory"
        servers = parsed.init.get("mcp_servers") or []
        if not isinstance(servers, list) or not all(isinstance(s, dict) for s in servers):
            return "CLI startup inventory omitted or malformed mcp_servers"
        status = {s.get("name"): s.get("status") for s in servers}
        # Grok connects lazily: init reports "pending" for a server it will use.
        if any(status.get(name) not in ("connected", "pending") for name in allowed):
            return "ModelSpec MCP did not connect"
        if any(state != "disabled" for name, state in status.items() if name not in allowed):
            return "CLI loaded another MCP server"
    if cli != "claude":
        from qa.tui_inventory import inventory_violation

        return inventory_violation(inventory, mcp_enabled=mcp_enabled, allowed_servers=allowed)
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
        if not isinstance(name, str) or name not in native and _tool_name(name)[0] not in allowed:
            return "CLI exposed an unapproved tool"
    if mcp_enabled and not all(any(
        server.get("name") == name and server.get("status") == "connected"
        for server in parsed.init["mcp_servers"]
    ) for name in allowed):
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
    activity: bool = False
    attempts: int = 1
    misuse: list[str] = field(default_factory=list)


# A transient OAuth refresh can exit before the CLI prints anything. Wait, then try once.
PRE_INIT_RETRY_DELAY_S = 5.0


def _error_only_event(event: dict) -> bool:
    kind = event.get("type")
    if kind in ("error", "turn.failed"):
        return True
    return kind is None and set(event) <= {"type", "error"} and "error" in event


def _stdout_activity(stdout: str) -> bool:
    return any(not _error_only_event(event) for event in json_events(stdout))


def _pre_init_error(code: int, stderr: str) -> str:
    message = f"CLI exited before startup (exit {code})"
    tail = redact(stderr or "").strip()[-200:]
    if not tail:
        return message
    return f"{message}: {tail}"


def pre_init_crash(execution: Execution) -> bool:
    """Non-zero exit before any model activity, usage limit, or timeout."""
    parsed, code = execution.transcript, execution.exit_code
    return (
        execution.status == "cli_error"
        and not execution.limit_reason
        and type(code) is int
        and code != 0
        and parsed.init is None
        and not parsed.final_answer
        and parsed.model is None
        and parsed.usage is None
        and parsed.tokens_in is None
        and not execution.activity
        and not parsed.tool_calls
        and not parsed.other_tool_calls
        and not parsed.hook_events
        and not parsed.terminal
    )


def launch(cli: str, config: dict, workspace: Path, prompt: str, *, mcp_enabled: bool, purpose="scenario") -> Execution:
    from qa.tui_isolation import isolation_result

    refuse_vendor_auth(os.environ)
    result = isolation_result(cli, config)
    if not result["verified"]:
        raise ValueError(result["reason"])
    execution = _execute(cli, config, workspace, prompt, mcp_enabled=mcp_enabled, purpose=purpose)
    if pre_init_crash(execution):
        sleep(PRE_INIT_RETRY_DELAY_S)
        execution = _execute(
            cli, config, workspace, prompt, mcp_enabled=mcp_enabled, purpose=purpose
        )
        execution.attempts = 2
        if pre_init_crash(execution):
            single = f"CLI exited before startup (exit {execution.exit_code})"
            twice = (
                f"CLI exited before startup twice (exit {execution.exit_code}); "
                "not retried further"
            )
            detail = execution.error or ""
            execution.error = twice + detail[len(single) :] if detail.startswith(single) else twice
            return execution
    violation, _misuse = guard_result(
        cli, execution.transcript, mcp_enabled=mcp_enabled, inventory=execution.inventory,
        allowed_servers=config.get("_mcp_servers"), purpose=purpose, isolated=True,
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
    purpose="scenario",
) -> Execution:
    from qa.tui_homes import home_config

    settings = config["clis"][cli]
    mcp_enabled = mcp_enabled and purpose != "search"
    with_token = mcp_enabled and purpose != "browser" and bool(os.environ.get(config.get("mcp_token_env") or ""))
    mcp_file = probe_mcp or workspace / "modelspec-mcp.json"
    if probe_mcp is None:
        mcp_file.write_text(home_config(cli, config, enabled=mcp_enabled, with_token=with_token))
    prepare_workspace(
        cli, config, workspace, mcp_enabled=mcp_enabled, isolated=isolated, with_token=with_token,
        purpose=purpose,
    )
    command = build_command(
        cli,
        settings,
        workspace,
        prompt,
        mcp_file,
        config["turn_cap"],
        isolated=isolated,
        purpose=purpose,
    )
    prompt_stdin = ""
    images = config.get("_judge_images", ())
    if images:
        if mcp_enabled or cli not in ("claude", "codex"):
            raise ValueError("UX image judges require Claude or Codex without MCP")
        if cli == "codex":
            command[command.index("--"):command.index("--")] = [
                "--image", ",".join(container_path(workspace, p) for p in images)
            ]
            prompt_stdin = prompt
        else:
            import base64
            command += ["--input-format", "stream-json"]
            content = [{"type": "text", "text": prompt}] + [
                {"type": "image", "source": {"type": "base64", "media_type": "image/png",
                 "data": base64.b64encode(p.read_bytes()).decode()}} for p in images
            ]
            prompt_stdin = json.dumps({"type": "user", "message": {
                "role": "user", "content": content}}) + "\n"
    elif cli in ("claude", "codex"):
        prompt_stdin = prompt
    elif cli == "grok":
        prompt_path = workspace / ".prompt.txt"
        prompt_path.write_text(prompt)
        prompt_path.chmod(0o600)
    env = child_environment(
        cli,
        workspace,
        config.get("mcp_token_env") if with_token else None,
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
        if violation := inventory_violation(inventory, mcp_enabled=mcp_enabled, allowed_servers=config.get("_mcp_servers")):
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
        # Claude and Codex read the prompt from stdin. Grok reads the private file.
        # Pass an empty stdin for the others so a shell heredoc cannot become context.
        process = run_cli(cli, config, workspace, command, env, isolated=isolated,
                          **({"input_text": prompt_stdin} if prompt_stdin else {}))
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
        violation, misuse = guard_result(
            cli, parsed, mcp_enabled=mcp_enabled, inventory=inventory,
            allowed_servers=config.get("_mcp_servers"), purpose=purpose, isolated=isolated,
        )
        limit = usage_limit(parsed, stderr, -1, [])
        if limit:
            status = "usage_limit"
        elif violation:
            status = "isolation_failed"
        elif misuse:
            status = "isolation_misuse"
        else:
            status = "timeout"
        return Execution(
            parsed,
            None,
            (perf_counter() - started) * 1000,
            status,
            violation
            if violation
            else misuse_error(misuse)
            if status == "isolation_misuse"
            else "CLI timed out",
            limit,
            output + stderr,
            inventory,
            misuse=misuse if status == "isolation_misuse" else [],
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
        violation, misuse = guard_result(
            cli, parsed, mcp_enabled=mcp_enabled, inventory=inventory,
            allowed_servers=config.get("_mcp_servers"), purpose=purpose, isolated=isolated,
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
    activity = _stdout_activity(process.stdout)
    if pre_init_crash(
        Execution(
            parsed, process.returncode, 0.0, "cli_error", limit_reason=limit, activity=activity
        )
    ):
        return Execution(
            parsed,
            process.returncode,
            (perf_counter() - started) * 1000,
            "cli_error",
            _pre_init_error(process.returncode, process.stderr),
            observed_output=process.stdout + process.stderr,
            inventory=inventory,
            activity=activity,
        )
    if limit:
        status = "usage_limit"
    elif violation:
        status = "isolation_failed"
    elif misuse:
        status = "isolation_misuse"
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
        else misuse_error(misuse)
        if status == "isolation_misuse"
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
        activity=activity,
        misuse=misuse if status == "isolation_misuse" else [],
    )


def prepare_workspace(
    cli: str,
    config: dict,
    workspace: Path,
    *,
    mcp_enabled: bool,
    isolated: bool = True,
    with_token: bool = False,
    purpose="scenario",
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
                mcp={"allowed": list(config.get("_mcp_servers", {"modelspec": {}})) if mcp_enabled else ["model301_none"]},
                tools={"core": ["google_web_search"] if purpose == "search" else []},
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
    if cli == "grok":
        # The trust gate disables project MCP servers at run time, although inspect
        # still lists them. The project layer stays empty; the servers go in a user
        # layer that container_command mounts read-only over the volume's config for
        # every isolated-mode command, including status checks in a positive control.
        (workspace / GROK_USER_CONFIG).write_text(
            home_config(cli, config, enabled=mcp_enabled and isolated, with_token=with_token)
        )
    if cli == "grok" and isolated:
        native = workspace / ".grok"
        native.mkdir(mode=0o700, exist_ok=True)
        (native / "config.toml").write_text(home_config(cli, config, enabled=False))
        (workspace / ".gitignore").write_text(
            "AGENTS.md\nAgents.md\nAGENT.md\nClaude.md\nCLAUDE.md\nCLAUDE.local.md\n"
            ".agents/\n.claude/\n.cursor/\n.grok/skills/\n.grok/hooks/\n.grok/rules/\n"
            ".grok/agents/\n.grok/plugins/\n"
        )
