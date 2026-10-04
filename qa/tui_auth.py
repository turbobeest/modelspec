"""Native authentication status. Only booleans and method names leave this module."""

from __future__ import annotations

import json
import os
import re
import selectors
import subprocess
from pathlib import Path
from time import monotonic

from qa.tui_docker import GEMINI_RETIRED, popen_cli, run_cli, stop_process
from qa.tui_homes import resolve_executable


def _rpc(
    cli: str,
    config: dict,
    command: list[str],
    workspace: Path,
    env: dict,
    requests: list,
    timeout: float,
) -> list:
    process = popen_cli(cli, config, workspace, command, env)
    pending, diagnostics, responses = b"", b"", []
    deadline = monotonic() + timeout
    try:
        with selectors.DefaultSelector() as selector:
            selector.register(process.stdout, selectors.EVENT_READ)
            selector.register(process.stderr, selectors.EVENT_READ)
            for identity, (method, params) in enumerate(requests, 1):
                process.stdin.write(
                    (
                        json.dumps(
                            {"jsonrpc": "2.0", "id": identity, "method": method, "params": params}
                        )
                        + "\n"
                    ).encode()
                )
                process.stdin.flush()
                while True:
                    response = None
                    while b"\n" in pending:
                        line, pending = pending.split(b"\n", 1)
                        message = json.loads(line)
                        if message.get("id") == identity:
                            response = message
                            break
                        # ACP startup can announce session state, but a request
                        # for client work is never answered by this status probe.
                        if "id" in message or not isinstance(message.get("method"), str):
                            raise ValueError("Unexpected authentication status RPC event")
                    if response is not None:
                        responses.append(response)
                        break
                    remaining = deadline - monotonic()
                    if remaining <= 0:
                        raise ValueError("Authentication status RPC timed out")
                    for key, _ in selector.select(remaining):
                        data = os.read(key.fileobj.fileno(), 65536)
                        if not data:
                            selector.unregister(key.fileobj)
                            if key.fileobj is process.stdout:
                                raise ValueError(
                                    "Authentication status RPC closed before its response"
                                )
                            continue
                        if key.fileobj is process.stderr:
                            diagnostics += data
                        else:
                            pending += data
                    if len(pending) > 1_000_000 or len(diagnostics) > 100_000:
                        raise ValueError("Authentication status RPC emitted excess output")
    finally:
        _, stderr = stop_process(process)
        diagnostics += stderr
    # Gemini's native authentication success message is written to stderr.
    error = responses[-1].get("error", {}) if responses else {}
    expected_refusal = error.get("code") == -32000 and (
        "Manual authorization is required but the current session is non-interactive."
        in error.get("message", "")
        or "This client is no longer supported for Gemini Code Assist for individuals."
        in error.get("message", "")
    )
    if not expected_refusal and any(
        line != "Loaded cached credentials."
        for line in diagnostics.decode().splitlines()
        if line.strip()
    ):
        raise ValueError("Authentication status RPC emitted diagnostics")
    return responses


def authentication_status(cli: str, config: dict, workspace: Path, env: dict) -> dict:
    env = {k: v for k, v in env.items() if k != config.get("mcp_token_env")}
    binary = resolve_executable(cli, config["clis"][cli])
    result = {"logged_in": None, "auth_method": None, "verified": False, "checks": []}
    timeout = config["timeout_seconds"]

    def run(args):
        completed = run_cli(cli, config, workspace, [binary, *args], env)
        result["checks"].append({"command": " ".join(args), "exit_code": completed.returncode})
        return completed

    initialize = (
        "initialize",
        {
            "protocolVersion": 1,
            "clientCapabilities": {},
            "clientInfo": {"name": "modelspec_doctor", "version": "1"},
        },
    )
    try:
        if cli == "claude":
            completed = run(["auth", "status"])
            value = json.loads(completed.stdout)
            methods = {
                "none",
                "claude.ai",
                "oauth_token",
                "api_key",
                "apiKey",
                "api_key_helper",
                "third_party",
            }
            if (
                type(value.get("loggedIn")) is not bool
                or value.get("authMethod") not in methods
                or completed.stderr.strip()
                or completed.returncode not in (0, 1)
            ):
                raise ValueError("Unknown Claude authentication status format")
            method = value["authMethod"]
            if value.get("apiKeySource") not in (None, "none", "subscription", "oauth"):
                method = "api_key"
            result.update(logged_in=value["loggedIn"], auth_method=method)
        elif cli == "codex":
            completed = run(["login", "status"])
            listing = (completed.stdout + completed.stderr).strip()
            if completed.returncode == 0 and listing == "Logged in using ChatGPT":
                result.update(logged_in=True, auth_method="chatgpt")
            elif completed.returncode == 1 and listing == "Not logged in":
                result.update(logged_in=False, auth_method="none")
            elif listing.startswith("Logged in using an API key"):
                result.update(logged_in=True, auth_method="api_key")
            else:
                raise ValueError("Unknown Codex authentication status format")
        elif cli == "gemini":
            completed = run_cli(
                cli,
                config,
                workspace,
                ["node", "/opt/modelspec-harness/gemini-settings.mjs", "auth"],
                env,
            )
            result["checks"].append(
                {"command": "Gemini native selectedType", "exit_code": completed.returncode}
            )
            method = json.loads(completed.stdout).get("selectedType")
            if completed.returncode or completed.stderr.strip():
                raise ValueError("Gemini native auth selection failed")
            if method == "none":
                result.update(logged_in=False, auth_method="none", verified=True, reason=None)
                return result
            if method != "oauth-personal":
                result.update(
                    auth_method=method if method in ("gemini-api-key", "vertex-ai") else "unknown",
                    reason="Gemini selectedType is not Google login",
                )
                return result
            command = [
                binary,
                "--acp",
                "--extensions",
                "none",
                "--allowed-mcp-server-names",
                "model301_none",
            ]
            responses = _rpc(
                cli,
                config,
                command,
                workspace,
                env,
                [initialize, ("session/new", {"cwd": "/work", "mcpServers": []})],
                timeout,
            )
            result["checks"].append(
                {"command": "Gemini ACP initialize; session/new (no model turn)", "exit_code": 0}
            )
            response = responses[-1]
            if isinstance(response.get("result", {}).get("sessionId"), str):
                result.update(logged_in=True, auth_method="oauth-personal")
            elif (
                response.get("error", {}).get("code") == -32000
                and "This client is no longer supported for Gemini Code Assist for individuals."
                in response["error"].get("message", "")
            ):
                # This response follows native cached OAuth validation and the
                # authenticated Code Assist setup call. It is not a login failure.
                result.update(
                    logged_in=True,
                    auth_method="oauth-personal",
                    service_available=False,
                    reason=GEMINI_RETIRED,
                )
            elif (
                response.get("error", {}).get("code") == -32000
                and "Manual authorization is required but the current session is non-interactive."
                in response["error"].get("message", "")
            ):
                result.update(logged_in=False, auth_method="none")
            else:
                raise ValueError("Unknown Gemini authentication status format")
        elif cli == "grok":
            responses = _rpc(
                cli,
                config,
                [binary, "agent", "--no-leader", "stdio"],
                workspace,
                env,
                [initialize],
                timeout,
            )
            method = responses[0].get("result", {}).get("_meta", {}).get("defaultAuthMethodId")
            if method in ("api_key", "api-key", "xai-api-key", "deployment_key"):
                result.update(auth_method="api_key", reason="Grok reports API-key authentication")
                return result
            completed = run(["models"])
            if (
                completed.returncode == 0
                and not completed.stderr.strip()
                and re.search(r"grok-[\w.-]+", completed.stdout)
            ):
                if method not in ("cached_token", "grok.com"):
                    raise ValueError("Unknown Grok authentication method")
                result.update(logged_in=True, auth_method=method)
            elif re.search(r"Not logged in|Run `grok login`", completed.stderr):
                result.update(logged_in=False, auth_method="none")
            else:
                raise ValueError("Grok authenticated model listing failed")
            result["checks"].insert(
                0, {"command": "Grok ACP initialize (auth method)", "exit_code": 0}
            )
        result["verified"] = (
            result["auth_method"]
            in {
                "claude": {"claude.ai", "none"},
                "codex": {"chatgpt", "none"},
                "gemini": {"oauth-personal", "none"},
                "grok": {"cached_token", "grok.com", "none"},
            }[cli]
        )
        result.setdefault(
            "reason",
            None if result["verified"] else "CLI does not report subscription authentication",
        )
    except (ValueError, KeyError, TypeError, AttributeError, OSError, subprocess.TimeoutExpired):
        # Status output can contain identities. Never retain raw output or error text.
        result["reason"] = "Native authentication status failed or has an unknown format"
    return result
