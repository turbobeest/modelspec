"""Native CLI inventories, separate from each vendor's model event stream."""

from __future__ import annotations

import json
import os
import re
import selectors
import subprocess
from pathlib import Path
from time import monotonic

from qa.tui_docker import popen_cli, run_cli, stop_process
from qa.tui_homes import resolve_executable

MECHANISMS = {
    "claude": "stream init: skills, plugins, mcp_servers, tools; hook events",
    "codex": "app-server skills/list; mcp list --json; plugin list --json; features list; "
    "debug prompt-input",
    "gemini": "mcp list; extensions list --output-format json; skills list; "
    "installed loadSettings().merged for hooks and skill enablement",
    "grok": "inspect --json: skills, plugins, hooks, projectInstructions, mcpServers",
}


def inventory_violation(inventory: dict | None, *, mcp_enabled: bool, allowed_servers=None) -> str | None:
    if not isinstance(inventory, dict):
        return "CLI did not expose its native inventory"
    if inventory.get("error"):
        return inventory["error"]
    for key in ("mcp_servers", "skills", "extensions", "hooks"):
        if not isinstance(inventory.get(key), list):
            return f"Native inventory omitted or malformed {key}"
    checks = inventory.get("checks")
    if (
        not isinstance(inventory.get("mechanism"), str)
        or not isinstance(checks, list)
        or not checks
        or any(
            not isinstance(check, dict)
            or check.get("exit_code") != 0
            or not isinstance(check.get("command"), str)
            for check in checks
        )
    ):
        return "Native inventory omitted its sources"
    for key in ("skills", "extensions", "hooks"):
        if inventory[key]:
            return f"CLI loaded user {key}"
    allowed = sorted(allowed_servers if allowed_servers is not None else ["modelspec"]) if mcp_enabled else []
    if inventory["mcp_servers"] != allowed:
        return "Native inventory did not show exactly the configured ModelSpec MCP servers"
    return None


def _list(value, description: str) -> list:
    if not isinstance(value, list):
        raise ValueError(f"Native inventory omitted or malformed {description}")
    return value


def _names(rows: list, *, enabled_key: str | None = None) -> list[str]:
    names = []
    for row in rows:
        if not isinstance(row, dict) or not isinstance(row.get("name"), str):
            raise ValueError("Native inventory has a malformed entry")
        if enabled_key and type(row.get(enabled_key)) is not bool:
            raise ValueError("Native inventory omitted entry enablement")
        if enabled_key is None or row[enabled_key]:
            names.append(row["name"])
    if len(names) != len(set(names)):
        raise ValueError("Native inventory has duplicate entries")
    return sorted(names)


GEMINI_MCP_NOTICES = frozenset(
    (
        "Registering notification handlers for server 'modelspec'. "
        "Capabilities: { tools: { listChanged: true } }",
        "Server 'modelspec' supports tool updates. Listening for changes...",
        "Scheduling MCP context refresh...",
        "Executing MCP context refresh...",
        "MCP context refresh complete.",
    )
)


# The controls pin /work untrusted, so Codex refuses its .codex config, hooks and exec
# policies and says so, as a configWarning event and on stderr. Doctor plants that
# folder, so this exact warning confirms the refusal.
CODEX_UNTRUSTED_PROJECT_WARNING = (
    "Project-local config, hooks, and exec policies are disabled in the following folders "
    "until the project is trusted, but skills still load.\n"
    "    1. /work/.codex\n"
    "       /work is marked as untrusted in the effective configuration. To load "
    "project-local config, hooks, and exec policies, update its trust setting. If that "
    "setting is managed by your organization, contact your administrator.\n"
)
_CODEX_WARNING_LINES = CODEX_UNTRUSTED_PROJECT_WARNING.splitlines()
CODEX_UNTRUSTED_PROJECT_NOTICE = (
    re.compile(
        r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(\.\d+)?Z ERROR codex_app_server: "
        + re.escape(_CODEX_WARNING_LINES[0])
    ),
    *(re.compile(re.escape(line)) for line in _CODEX_WARNING_LINES[1:]),
)


def codex_untrusted_project_warning(message: dict) -> bool:
    return (
        message.get("method") == "configWarning"
        and message.get("params")
        == {"summary": CODEX_UNTRUSTED_PROJECT_WARNING, "details": None}
    )


def codex_unknown_diagnostics(stderr: bytes, *, final: bool) -> bool:
    """Every line except the untrusted-project notice is an unknown diagnostic."""
    text = re.sub(r"\x1b\[[0-9;]*m", "", stderr.decode(errors="replace"))
    lines = text.split("\n")
    if not final:
        lines = lines[:-1]  # Judge a partial line once it is complete.
    return any(
        line.strip()
        and not any(pattern.fullmatch(line) for pattern in CODEX_UNTRUSTED_PROJECT_NOTICE)
        for line in lines
    )


def gemini_skill_listing(output: str, allowed_servers=("modelspec",)) -> str:
    # Keep unknown diagnostics in the listing so its strict grammar rejects them.
    notices = {notice.replace("'modelspec'", f"'{server}'")
               for server in allowed_servers for notice in GEMINI_MCP_NOTICES}
    return "\n".join(line for line in output.splitlines() if line not in notices).strip()


def _codex_skills(
    binary: str,
    controls: list[str],
    workspace: Path,
    env: dict,
    timeout: float,
    config: dict,
    notices: list | None = None,
) -> list[dict]:
    """Query the CLI's local inventory RPC without starting a model turn.

    Codex's untrusted-project warning is appended to notices when it arrives.
    """
    process = popen_cli(
        "codex", config, workspace, [binary, *controls, "app-server", "--listen", "stdio://"], env
    )
    pending, diagnostics = b"", b""
    deadline = monotonic() + timeout
    try:
        with selectors.DefaultSelector() as selector:
            selector.register(process.stdout, selectors.EVENT_READ)
            selector.register(process.stderr, selectors.EVENT_READ)

            def request(identity, method, params):
                nonlocal pending, diagnostics
                process.stdin.write(
                    (
                        json.dumps({"id": identity, "method": method, "params": params}) + "\n"
                    ).encode()
                )
                process.stdin.flush()
                while True:
                    while b"\n" in pending:
                        line, pending = pending.split(b"\n", 1)
                        message = json.loads(line)
                        if message.get("id") == identity:
                            if "error" in message or "result" not in message:
                                raise ValueError("Codex skills inventory RPC failed")
                            return message["result"]
                        if codex_untrusted_project_warning(message):
                            if notices is not None:
                                notices.append("untrusted_project")
                        elif message.get("method") not in (
                            "skills/changed",
                            "remoteControl/status/changed",
                        ):
                            raise ValueError("Unexpected Codex inventory RPC event")
                    remaining = deadline - monotonic()
                    if remaining <= 0:
                        raise ValueError("Codex skills inventory timed out")
                    events = selector.select(remaining)
                    for key, _ in events:
                        chunk = os.read(key.fileobj.fileno(), 65536)
                        if not chunk:
                            raise ValueError("Codex skills inventory closed before its response")
                        if key.fileobj is process.stderr:
                            diagnostics += chunk
                        else:
                            pending += chunk
                    if (
                        codex_unknown_diagnostics(diagnostics, final=False)
                        or len(pending) > 1_000_000
                    ):
                        raise ValueError(
                            "Codex skills inventory emitted diagnostics or excess output"
                        )

            request(
                1, "initialize", {"clientInfo": {"name": "modelspec_tui_inventory", "version": "1"}}
            )
            process.stdin.write(b'{"method":"initialized"}\n')
            process.stdin.flush()
            result = request(2, "skills/list", {"cwds": ["/work"], "forceReload": True})
            data = _list(result.get("data"), "Codex skills/list data")
            if len(data) != 1 or data[0].get("cwd") != "/work":
                raise ValueError("Codex skills inventory omitted or mismatched its cwd")
            errors = _list(data[0].get("errors"), "Codex skill discovery errors")
            if errors:
                raise ValueError("Codex reported skill discovery errors")
            return _list(data[0].get("skills"), "Codex skills")
    finally:
        _, stderr = stop_process(process)
        if codex_unknown_diagnostics(diagnostics + (stderr or b""), final=True):
            raise ValueError("Codex skills inventory emitted diagnostics")


def _codex_skill_config(rows: list[dict]) -> str:
    disabled = []
    for row in rows:
        if (
            not isinstance(row, dict)
            or not isinstance(row.get("name"), str)
            or row.get("scope") not in ("user", "repo", "admin", "system")
            or type(row.get("enabled")) is not bool
            or not isinstance(row.get("path"), str)
            or not Path(row["path"]).is_absolute()
        ):
            raise ValueError("Codex skill inventory has an unknown entry")
        if row["scope"] != "system":
            disabled.append("{path=" + json.dumps(row["path"]) + ",enabled=false}")
    return "skills.config=[" + ",".join(disabled) + "]"


def inspect_inventory(
    cli: str, config: dict, workspace: Path, env: dict, mcp_file: Path, *, mcp_enabled: bool
) -> dict:
    """Use the launch's exact environment, home, cwd and effective controls.

    Raw command output stays in memory. Receipts retain only names, disabled
    states and command labels, never the CLI's config values or prompt preview.
    """
    from qa.tui_providers import codex_config_args

    binary = resolve_executable(cli, config["clis"][cli])
    checks = []
    evidence = {"mechanism": MECHANISMS[cli], "checks": checks}

    def run(args: list[str], *, executable=binary, label=None, listing=False) -> str:
        result = run_cli(cli, config, workspace, [executable, *args], env)
        checks.append({"command": label or " ".join(args), "exit_code": result.returncode})
        if result.returncode:
            raise ValueError("Native inventory command failed: " + (label or " ".join(args)))
        # Listing stderr can carry discovery failures. Never treat them as an empty inventory.
        if result.stderr.strip() and not listing:
            raise ValueError("Native inventory command emitted diagnostics")
        output = result.stdout + ("\n" + result.stderr if listing else "")
        return re.sub(r"\x1b\[[0-9;]*m", "", output).strip()

    try:
        if cli == "codex":
            controls = ["--no-daemon", *codex_config_args(config["clis"][cli], mcp_file)]
            discovery = {
                "command": "codex app-server skills/list",
                "phase": "discovery",
                "exit_code": None,
            }
            checks.append(discovery)
            notices = []
            rows = _codex_skills(
                binary, controls, workspace, env, config["timeout_seconds"], config, notices
            )
            discovery["exit_code"] = 0
            skill_config = _codex_skill_config(rows)
            controls += ["-c", skill_config]
            effective_check = {
                "command": "codex app-server skills/list",
                "phase": "effective",
                "exit_code": None,
            }
            checks.append(effective_check)
            effective_skills = _codex_skills(
                binary, controls, workspace, env, config["timeout_seconds"], config, notices
            )
            effective_check["exit_code"] = 0
            _codex_skill_config(effective_skills)
            skills = [
                row["name"]
                for row in effective_skills
                if row["enabled"] and row["scope"] != "system"
            ]
            evidence["skill_config"] = skill_config
            # Codex states the effective trust only when the cwd has a .codex folder.
            evidence["workspace_trust"] = "untrusted" if notices else "unreported"
            evidence["discovered_skills"] = [
                {"name": row["name"], "scope": row["scope"], "enabled": row["enabled"]}
                for row in rows
            ]

            def codex(command):
                return run(controls + command, label="codex " + " ".join(command))

            server_rows = _list(json.loads(codex(["mcp", "list", "--json"])), "MCP servers")
            servers = _names(server_rows, enabled_key="enabled")
            for row in server_rows:
                if row["enabled"] and row["name"] == "modelspec":
                    transport = row.get("transport", {})
                    if (
                        transport.get("type") != "streamable_http"
                        or transport.get("url") != config["mcp_url"]
                    ):
                        raise ValueError("Codex ModelSpec inventory reports a different endpoint")
            plugins = json.loads(codex(["plugin", "list", "--json"]))
            evidence["plugins"] = [
                {
                    "name": row["name"],
                    "enabled": row["enabled"],
                    "scope": row.get("scope")
                    if row.get("scope") in ("account", "user", "workspace", "system")
                    else "unreported",
                }
                for row in _list(plugins["installed"], "installed plugins")
            ]
            extensions = _names(
                _list(plugins["installed"], "installed plugins"), enabled_key="enabled"
            )
            _list(plugins["available"], "available plugins")
            features = codex(["features", "list"])
            hooks = [line for line in features.splitlines() if re.match(r"^hooks\s", line)]
            if len(hooks) != 1 or not re.fullmatch(r"hooks\s+.+\s+false", hooks[0]):
                raise ValueError("Codex effective hooks feature is missing or enabled")
            prompt = _list(json.loads(codex(["debug", "prompt-input"])), "prompt input")
            if not prompt:
                raise ValueError("Codex prompt preview is empty")
            texts = []
            for message in prompt:
                if not isinstance(message, dict) or message.get("type") != "message":
                    raise ValueError("Unknown Codex prompt preview item")
                for content in _list(message.get("content"), "prompt content"):
                    if content.get("type") != "input_text" or not isinstance(
                        content.get("text"), str
                    ):
                        raise ValueError("Unknown Codex prompt preview content")
                    texts.append(content["text"])
            if any("<skills_instructions>" in t for t in texts):
                # Built-in skill instructions are disabled by the same shared override.
                raise ValueError("Codex still exposed skill instructions in its effective prompt")
            evidence.update(mcp_servers=servers, skills=skills, extensions=extensions, hooks=[])
        elif cli == "gemini":
            listing = run(["mcp", "list"], listing=True)
            servers = []
            if listing != "No MCP servers configured.":
                lines = listing.splitlines()
                if not lines or lines[0] != "Configured MCP servers:":
                    raise ValueError("Unknown Gemini MCP inventory format")
                entries = list(filter(None, lines[1:]))
                if not entries:
                    raise ValueError("Gemini MCP inventory header has no entries")
                seen = set()
                indicators = {
                    "Connected": "✓",
                    "Disconnected": "✗",
                    "Disabled": "○",
                    "Blocked": "⛔",
                    "Connecting": "…",
                }
                for line in entries:
                    match = re.fullmatch(
                        r"[✓✗○⛔…] ([\w-]+): .+ - "
                        r"(Connected|Disconnected|Disabled|Blocked|Connecting)",
                        line,
                    )
                    if not match or line[0] != indicators[match[2]] or match[1] in seen:
                        raise ValueError("Unknown Gemini MCP inventory entry")
                    seen.add(match[1])
                    if match[2] in ("Connected", "Disconnected", "Connecting"):
                        if match[1] == "modelspec" and not line.startswith(
                            line[0] + " modelspec: " + config["mcp_url"] + " (http) - "
                        ):
                            raise ValueError(
                                "Gemini ModelSpec inventory reports a different endpoint"
                            )
                        servers.append(match[1])
            # Names only: extension rows can carry MCP env, headers and settings.
            extensions = _names(
                _list(
                    json.loads(
                        run(["extensions", "list", "--output-format", "json"], listing=True)
                    ),
                    "Gemini extensions",
                )
            )
            skills_output = gemini_skill_listing(
                run(["skills", "list"], listing=True),
                config.get("_mcp_servers", {"modelspec": {}}) if mcp_enabled else (),
            )
            effective = json.loads(
                run(
                    ["/opt/modelspec-harness/gemini-settings.mjs", "inventory"],
                    executable="node",
                    label="Gemini loadSettings().merged",
                )
            )
            if (
                effective.get("skillsEnabled") is not False
                or effective.get("hooksEnabled") is not False
            ):
                raise ValueError("Gemini effective settings did not disable skills and hooks")
            _list(effective.get("hookEvents"), "Gemini hook events")
            from qa.tui_homes import home_paths

            _, config_home = home_paths(cli, config["clis"][cli])
            if effective.get("userSettingsPath") != str(config_home / "settings.json"):
                raise ValueError("Gemini settings probe did not attest the dedicated config path")
            if skills_output != "No skills discovered." and not skills_output.startswith(
                "Discovered Agent Skills:\n"
            ):
                raise ValueError("Gemini skills inventory contains unknown or non-listing output")
            discovered = []
            if skills_output != "No skills discovered.":
                for entry in (
                    skills_output.removeprefix("Discovered Agent Skills:\n").strip().split("\n\n")
                ):
                    lines = entry.splitlines()
                    match = re.fullmatch(
                        r"([\w.:-]+) \[(Enabled|Disabled)\](?: \[Built-in\])?", lines[0]
                    )
                    if (
                        not match
                        or len(lines) != 3
                        or not lines[1].startswith("  Description: ")
                        or not lines[2].startswith("  Location:    ")
                    ):
                        raise ValueError("Unknown Gemini skills inventory entry")
                    discovered.append({"name": match[1], "listed_enabled": match[2] == "Enabled"})
            evidence.update(
                mcp_servers=sorted(servers),
                skills=[],
                extensions=extensions,
                hooks=[],
                skills_disabled=True,
                hooks_disabled=True,
                discovered_skills=discovered,
            )
        elif cli == "grok":
            report = json.loads(run(["inspect", "--json"]))
            if report.get("cwd") != "/work":
                raise ValueError("Grok inventory reports a different cwd")
            if report.get("configWarnings") or report.get("mcpConfigProblems"):
                raise ValueError("Grok reported ambiguous configuration")
            names = {}
            for native, key in (
                ("mcpServers", "mcp_servers"),
                ("skills", "skills"),
                ("hooks", "hooks"),
                ("plugins", "extensions"),
            ):
                rows = _list(report.get(native), "Grok " + native)
                active = []
                for row in rows:
                    if not isinstance(row, dict):
                        raise ValueError("Malformed Grok inventory entry")
                    if "disabled" in row and type(row["disabled"]) is not bool:
                        raise ValueError("Malformed Grok disabled state")
                    if key == "extensions" and type(row.get("enabled")) is not bool:
                        raise ValueError("Grok plugin omitted enabled state")
                    if row.get("disabled") is True or key == "extensions" and not row["enabled"]:
                        continue
                    if key == "skills":
                        source = row.get("source")
                        if not isinstance(source, dict) or source.get("type") not in (
                            "builtin",
                            "bundled",
                            "server",
                            "project",
                            "user",
                            "plugin",
                            "configToml",
                            "claudeJson",
                            "mcpJson",
                            "cli",
                            "managed",
                        ):
                            raise ValueError("Unknown Grok skill source")
                        if source["type"] in ("builtin", "bundled"):
                            continue
                    if (
                        key == "mcp_servers"
                        and row.get("name") == "modelspec"
                        and (
                            row.get("target") != config["mcp_url"] or row.get("transport") != "http"
                        )
                    ):
                        raise ValueError("Grok ModelSpec inventory reports a different endpoint")
                    name = row.get("name", row.get("event") if key == "hooks" else None)
                    if not isinstance(name, str):
                        raise ValueError("Grok inventory entry omitted its name")
                    active.append(name)
                names[key] = sorted(active)
            instructions = []
            for row in _list(report.get("projectInstructions"), "Grok instructions"):
                if not isinstance(row, dict) or not isinstance(row.get("path"), str):
                    raise ValueError("Malformed Grok instruction inventory entry")
                if "disabled" in row and type(row["disabled"]) is not bool:
                    raise ValueError("Malformed Grok instruction disabled state")
                if row.get("disabled") is not True:
                    instructions.append(row["path"])
            evidence["instructions"] = instructions
            evidence.update(names)
            if instructions:
                raise ValueError("Grok native inventory reports active instruction files")
        elif cli == "claude":
            plugins = _list(json.loads(run(["plugin", "list", "--json"])), "Claude plugins")
            evidence["extensions"] = _names(plugins, enabled_key="enabled")
            raise ValueError(
                "Claude native plugin list is preliminary; doctor also needs stream init"
            )
        else:
            raise ValueError("Unknown CLI")
        evidence["error"] = inventory_violation(
            evidence, mcp_enabled=mcp_enabled, allowed_servers=config.get("_mcp_servers")
        )
    except ValueError as exc:
        evidence["error"] = str(exc)
    except (KeyError, TypeError, AttributeError, OSError, subprocess.TimeoutExpired):
        evidence["error"] = "Native inventory failed, is incomplete, or has an unknown format"
    return evidence
