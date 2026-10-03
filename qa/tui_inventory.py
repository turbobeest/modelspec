"""Native CLI inventories, separate from each vendor's model event stream."""

from __future__ import annotations

import json
import os
import re
import selectors
import subprocess
from pathlib import Path
from time import monotonic

from qa.tui_homes import gemini_runtime, resolve_executable

MECHANISMS = {
    "claude": "stream init: skills, plugins, mcp_servers, tools; hook events",
    "codex": "app-server skills/list; mcp list --json; plugin list --json; features list; "
    "debug prompt-input",
    "gemini": "mcp list; extensions list --output-format json; skills list; "
    "installed loadSettings().merged for hooks and skill enablement",
    "grok": "inspect --json: skills, plugins, hooks, projectInstructions, mcpServers",
}


def inventory_violation(inventory: dict | None, *, mcp_enabled: bool) -> str | None:
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
    allowed = ["modelspec"] if mcp_enabled else []
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


def _gemini_settings_module(bundle: Path) -> Path:
    # Inspect only installed package code, never a user's config or state files.
    matches = []
    for path in bundle.parent.glob("chunk-*.js"):
        module = path.resolve()
        if not module.is_relative_to(bundle.parent):
            raise ValueError("Gemini settings module leaves its installed bundle")
        if re.search(r"export\s*\{[^}]*\bloadSettings\b", module.read_text(), re.S):
            matches.append(module)
    if len(matches) != 1:
        raise ValueError("Gemini package does not expose an unambiguous loadSettings export")
    module = matches[0].resolve()
    if not module.is_relative_to(bundle.parent):
        raise ValueError("Gemini settings module leaves its installed bundle")
    return module


def _codex_skills(
    binary: str, controls: list[str], workspace: Path, env: dict, timeout: float
) -> list[dict]:
    """Query the CLI's local inventory RPC without starting a model turn."""
    process = subprocess.Popen(
        [binary, *controls, "app-server", "--listen", "stdio://"],
        cwd=workspace,
        env=env,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
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
                        if message.get("method") != "skills/changed":
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
                    if diagnostics.strip() or len(pending) > 1_000_000:
                        raise ValueError(
                            "Codex skills inventory emitted diagnostics or excess output"
                        )

            request(
                1, "initialize", {"clientInfo": {"name": "modelspec_tui_inventory", "version": "1"}}
            )
            process.stdin.write(b'{"method":"initialized"}\n')
            process.stdin.flush()
            result = request(2, "skills/list", {"cwds": [str(workspace)], "forceReload": True})
            data = _list(result.get("data"), "Codex skills/list data")
            if len(data) != 1 or data[0].get("cwd") != str(workspace):
                raise ValueError("Codex skills inventory omitted or mismatched its cwd")
            errors = _list(data[0].get("errors"), "Codex skill discovery errors")
            if errors:
                raise ValueError("Codex reported skill discovery errors")
            return _list(data[0].get("skills"), "Codex skills")
    finally:
        process.terminate()
        try:
            _, stderr = process.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            _, stderr = process.communicate()
        if stderr.strip():
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

    def run(args: list[str], *, executable=binary, label=None) -> str:
        result = subprocess.run(
            [executable, *args],
            cwd=workspace,
            env=env,
            input="",
            text=True,
            capture_output=True,
            timeout=config["timeout_seconds"],
        )
        checks.append({"command": label or " ".join(args), "exit_code": result.returncode})
        if result.returncode:
            raise ValueError("Native inventory command failed: " + (label or " ".join(args)))
        # Listing stderr can carry discovery failures. Never treat them as an empty inventory.
        if result.stderr.strip():
            raise ValueError("Native inventory command emitted diagnostics")
        return re.sub(r"\x1b\[[0-9;]*m", "", result.stdout).strip()

    try:
        if cli == "codex":
            controls = ["--no-daemon", *codex_config_args(config["clis"][cli], mcp_file)]
            rows = _codex_skills(binary, controls, workspace, env, config["timeout_seconds"])
            skill_config = _codex_skill_config(rows)
            controls += ["-c", skill_config]
            effective_skills = _codex_skills(
                binary, controls, workspace, env, config["timeout_seconds"]
            )
            _codex_skill_config(effective_skills)
            skills = [
                row["name"]
                for row in effective_skills
                if row["enabled"] and row["scope"] != "system"
            ]
            checks.extend(
                {"command": "codex app-server skills/list", "phase": phase, "exit_code": 0}
                for phase in ("discovery", "effective")
            )
            evidence["skill_config"] = skill_config

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
            listing = run(["mcp", "list"])
            servers = []
            if listing != "No MCP servers configured.":
                lines = listing.splitlines()
                if not lines or lines[0] != "Configured MCP servers:":
                    raise ValueError("Unknown Gemini MCP inventory format")
                for line in filter(None, lines[1:]):
                    match = re.fullmatch(
                        r"[✓✗○⛔…] ([\w-]+): .+ - "
                        r"(Connected|Disconnected|Disabled|Blocked|Connecting)",
                        line,
                    )
                    if not match:
                        raise ValueError("Unknown Gemini MCP inventory entry")
                    if match[2] in ("Connected", "Disconnected", "Connecting"):
                        if match[1] == "modelspec" and not line.startswith(
                            line[0] + " modelspec: " + config["mcp_url"] + " (http) - "
                        ):
                            raise ValueError(
                                "Gemini ModelSpec inventory reports a different endpoint"
                            )
                        servers.append(match[1])
            # Names only: extension rows can carry MCP env, headers and settings.
            extensions = _names(_list(
                json.loads(run(["extensions", "list", "--output-format", "json"])),
                "Gemini extensions",
            ))
            skills_output = run(["skills", "list"])
            node, bundle = gemini_runtime(Path(binary))
            module = _gemini_settings_module(bundle)
            script = (
                "const {loadSettings} = await import(process.argv[1]);"
                "const s = loadSettings(process.cwd());"
                "if (!Array.isArray(s.errors) || s.errors.length) process.exit(2);"
                "console.log(JSON.stringify({skillsEnabled:s.merged.skills?.enabled,"
                "hooksEnabled:s.merged.hooksConfig?.enabled,"
                "hookEvents:Object.keys(s.merged.hooks || {})}));"
            )
            effective = json.loads(
                run(
                    ["--input-type=module", "-e", script, module.as_uri()],
                    executable=str(node),
                    label="Gemini loadSettings().merged",
                )
            )
            if (
                effective.get("skillsEnabled") is not False
                or effective.get("hooksEnabled") is not False
            ):
                raise ValueError("Gemini effective settings did not disable skills and hooks")
            _list(effective.get("hookEvents"), "Gemini hook events")
            if skills_output != "No skills discovered." and not skills_output.startswith(
                "Discovered Agent Skills:\n"
            ):
                raise ValueError("Unknown Gemini skills inventory format")
            discovered = []
            if skills_output != "No skills discovered.":
                for entry in (
                    skills_output.removeprefix("Discovered Agent Skills:\n").strip().split("\n\n")
                ):
                    lines = entry.splitlines()
                    match = re.fullmatch(r"([\w.:-]+) \[(Enabled|Disabled)\]", lines[0])
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
            if report.get("cwd") != str(workspace):
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
            _list(report.get("projectInstructions"), "Grok instructions")
            evidence.update(names)
        else:
            raise ValueError("This CLI uses stream inventory")
        evidence["error"] = inventory_violation(evidence, mcp_enabled=mcp_enabled)
    except (ValueError, KeyError, TypeError, AttributeError, OSError, subprocess.TimeoutExpired):
        evidence["error"] = "Native inventory failed, is incomplete, or has an unknown format"
    return evidence
