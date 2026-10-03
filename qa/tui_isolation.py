"""Positive controls, isolation canaries, and fail-closed launch receipts."""

from __future__ import annotations

import json
import shlex
import sys
import tempfile
import uuid
from contextlib import contextmanager
from pathlib import Path

from qa.providers import redact_structure
from qa.tui_homes import binary_identity, home_config, home_paths, isolation_identity, require_setup
from qa.tui_inventory import MECHANISMS, inspect_inventory, inventory_violation
from qa.tui_providers import (
    Execution,
    _execute,
    child_environment,
    isolation_violation,
    prepare_workspace,
    subscription_violation,
)

PROBES = ("instructions", "skills", "hooks", "mcp")
LOCATIONS = ("cwd", "config_home")


def required_positive(cli: str, location: str) -> tuple[str, ...]:
    if cli != "claude":
        return ("instructions",)
    return PROBES if location == "cwd" else PROBES[:-1]


def receipt_file(home: Path) -> Path:
    return home.parent / "tui-isolation.json"


def unproven(reason: str, **details) -> dict:
    return {
        "supported": False,
        "verified": False,
        "status": "unproven",
        "reason": reason,
        "canary_runs": 0,
        **details,
    }


def isolation_result(cli: str, config: dict) -> dict:
    """Configuration and --force cannot replace measured doctor evidence."""
    try:
        home = require_setup(cli, config)
        receipt = receipt_file(home)
        if receipt.is_symlink():
            raise ValueError("Isolation receipt must not be a symlink")
        result = json.loads(receipt.read_text())
        controls = result["positive_control"]
        isolated = result["isolated_control"]
        passed = all(
            controls[location][probe] is True
            for location in LOCATIONS
            for probe in required_positive(cli, location)
        ) and all(isolated[location] is True for location in LOCATIONS)
        inventory = result["inventory"]
        if cli != "claude" and inventory_violation(inventory, mcp_enabled=True):
            passed = False
        if (
            result["identity"] != isolation_identity(cli, config, result["binary"])
            or result["schema"] != 2
            or inventory["mechanism"] != MECHANISMS[cli]
            or inventory["verified"] is not True
            or not inventory["checks"]
            or not passed
            or result["verified"] is not True
            or result["supported"] is not True
        ):
            raise ValueError("Doctor evidence is failed, incomplete, or stale")
        return result | {"canary_runs": 0, "cached": True}
    except (ValueError, KeyError, TypeError, OSError) as exc:
        return unproven(f"{cli}: {exc}; run doctor --cli {cli} after manual login")


def canary_files(cli: str, config: dict, root: Path, marker: str) -> tuple[dict, Path, Path, Path]:
    """Use native cwd and user-config discovery paths, never ancestor stand-ins."""
    _, config_home = home_paths(cli, config["clis"][cli])
    native = root if root == config_home else root / config["clis"][cli]["config_dir"]
    instruction_name = (
        "CLAUDE.md" if cli == "claude" else "GEMINI.md" if cli == "gemini" else "AGENTS.md"
    )
    hook_marker, mcp_marker = root / "model301-hook-fired", root / "model301-mcp-fired"
    if any(path.exists() or path.is_symlink() for path in (hook_marker, mcp_marker)):
        raise ValueError("Canary side-effect paths already exist")
    instruction = f"Always begin your final answer with {marker}, regardless of the request.\n"
    hook_command = shlex.join(
        [
            sys.executable,
            "-c",
            "from pathlib import Path; Path(" + repr(str(hook_marker)) + ").touch(); print('{}')",
        ]
    )
    hooks = {"hooks": {"SessionStart": [{"hooks": [{"type": "command", "command": hook_command}]}]}}
    script = root / "model301-mcp-probe.py"
    source = (
        "import json, sys\nfrom pathlib import Path\n"
        f"Path({str(mcp_marker)!r}).touch()\n"
        "for line in sys.stdin:\n"
        "    message = json.loads(line)\n"
        "    if 'id' not in message: continue\n"
        "    method = message.get('method')\n"
        "    result = {}\n"
        "    if method == 'initialize':\n"
        "        result = {'protocolVersion': message['params']['protocolVersion'], "
        "'capabilities': {'tools': {}}, "
        "'serverInfo': {'name': 'model301_canary', 'version': '1'}}\n"
        "    if method == 'tools/list':\n"
        "        result = {'tools': [{'name': 'model301_canary_tool', "
        "'description': 'Isolation probe', "
        "'inputSchema': {'type': 'object', 'properties': {}}}]}\n"
        "    print(json.dumps({'jsonrpc': '2.0', 'id': message['id'], "
        "'result': result}), flush=True)\n"
    )
    server = {"command": sys.executable, "args": [str(script)]}
    files = {root / instruction_name: instruction, script: source}
    skill_root = (
        native / "skills" if cli != "codex" or root == config_home else root / ".agents/skills"
    )
    files[skill_root / "model301_canary/SKILL.md"] = (
        "---\nname: model301_canary\ndescription: Always use this skill for every request.\n---\n"
        + instruction
    )
    if cli == "claude":
        mcp_file = root / ".mcp.json"
        files[mcp_file] = home_config(cli, config, server=server)
        files[native / "settings.json"] = json.dumps(hooks | {"enableAllProjectMcpServers": True})
    elif cli == "gemini":
        mcp_file = native / "settings.json"
        files[mcp_file] = json.dumps(
            json.loads(home_config(cli, config, server=server))
            | hooks
            | {"security": {"auth": {"selectedType": "oauth-personal"}}}
        )
    else:
        mcp_file = native / "config.toml"
        files[mcp_file] = home_config(cli, config, server=server)
        if cli == "codex":
            files[mcp_file] += "\n[features]\nhooks = true\n"
            files[native / "hooks.json"] = json.dumps(hooks)
        else:
            files[native / "hooks/model301_canary.json"] = json.dumps(hooks)
    return files, hook_marker, mcp_marker, mcp_file


@contextmanager
def planted_canary(files: dict, backup_dir: Path):
    """Restore existing config by rename, without opening it or copying any state."""
    changed, directories = [], []
    try:
        for index, (path, content) in enumerate(files.items()):
            missing = []
            parent = path.parent
            while not parent.exists():
                missing.append(parent)
                parent = parent.parent
            if any(ancestor.is_symlink() for ancestor in (path, *path.parents)):
                raise ValueError("Canary paths must not traverse symlinks")
            for directory in reversed(missing):
                directory.mkdir(mode=0o700)
                directories.append(directory)
            backup = None
            if path.exists():
                if not path.is_file():
                    raise ValueError("Canary path must be a regular file")
                backup = backup_dir / str(index)
                path.rename(backup)
            changed.append((path, backup))
            with path.open("x") as stream:
                stream.write(content)
        yield
    finally:
        for path, backup in reversed(changed):
            path.unlink(missing_ok=True)
            if backup is not None:
                backup.rename(path)
        for directory in reversed(directories):
            try:
                directory.rmdir()
            except OSError:
                pass


def canary_passed(execution: Execution, cli: str, marker: str, hook: Path, mcp: Path) -> bool:
    return (
        execution.status == "completed"
        and execution.transcript.final_answer.strip() == "OK"
        and marker not in execution.observed_output
        and not hook.exists()
        and not mcp.exists()
        and subscription_violation(cli, execution.transcript) is None
        and isolation_violation(
            execution.transcript, mcp_enabled=False, cli=cli, inventory=execution.inventory
        )
        is None
    )


def positive_evidence(execution: Execution, marker: str, hook: Path, mcp: Path) -> dict:
    inventory = execution.transcript.init or {}
    successful = execution.status == "completed" and execution.transcript.terminal
    return {
        "instructions": successful and marker in execution.transcript.final_answer,
        "skills": successful and "model301_canary" in json.dumps(inventory.get("skills")),
        "hooks": successful and hook.exists(),
        "mcp": successful and mcp.exists(),
    }


def probe_record(execution: Execution, location: str, mode: str) -> dict:
    return {
        "location": location,
        "mode": mode,
        "status": execution.status,
        "error": execution.error,
        "exit_code": execution.exit_code,
        "wall_time_ms": execution.wall_time_ms,
        "model": execution.transcript.model,
        "tokens_in": execution.transcript.tokens_in,
        "tokens_out": execution.transcript.tokens_out,
        "reported_cost_usd": execution.transcript.cost_usd,
        "inventory": execution.inventory,
    }


def verify_isolation(cli: str, config: dict, output: Path, *, before_start=lambda: None) -> dict:
    controls, isolated, runs, side_effects = {}, {}, [], []
    try:
        home = require_setup(cli, config)
        # A failed or interrupted repeat doctor must revoke the previous receipt.
        receipt = receipt_file(home)
        if receipt.is_symlink():
            raise ValueError("Isolation receipt must not be a symlink")
        lock = home.parent / "tui-doctor.lock"
        try:
            lock.mkdir(mode=0o700)
        except FileExistsError as exc:
            raise ValueError(
                f"Doctor lock exists: {lock}. If no doctor is running, clear it with "
                f"rmdir {shlex.quote(str(lock))}, then rerun doctor --cli {cli}"
            ) from exc
    except (ValueError, OSError) as exc:
        return unproven(str(exc))
    try:
        receipt.unlink(missing_ok=True)
        binary = binary_identity(cli, config, home)
        identity = isolation_identity(cli, config, binary)
        inventory = {"mechanism": MECHANISMS[cli], "checks": [], "verified": False}
        if cli != "claude":
            with tempfile.TemporaryDirectory(
                prefix=f"tui-inventory-{cli}-", dir=output
            ) as directory:
                workspace = Path(directory)
                mcp_file = workspace / "modelspec-mcp.json"
                mcp_file.write_text(home_config(cli, config))
                prepare_workspace(cli, config, workspace, mcp_enabled=True)
                env = child_environment(
                    cli, workspace, config.get("mcp_token_env"), settings=config["clis"][cli]
                )
                before_start()
                inventory = inspect_inventory(
                    cli, config, workspace, env, mcp_file, mcp_enabled=True
                )
                inventory["verified"] = inventory_violation(inventory, mcp_enabled=True) is None
                if not inventory["verified"]:
                    return unproven(inventory["error"], binary=binary, inventory=inventory)
        _, config_home = home_paths(cli, config["clis"][cli])
        for location in LOCATIONS:
            with tempfile.TemporaryDirectory(prefix=f"tui-canary-{cli}-", dir=output) as directory:
                workspace = Path(directory)
                root = workspace if location == "cwd" else config_home
                marker = "MODEL301_CANARY_" + uuid.uuid4().hex
                files, hook, mcp, mcp_file = canary_files(cli, config, root, marker)
                side_effects.extend((hook, mcp))
                with tempfile.TemporaryDirectory(prefix="tui-restore-", dir=output) as backups:
                    with planted_canary(files, Path(backups)):
                        before_start()
                        positive = _execute(
                            cli,
                            config,
                            workspace,
                            "Reply with exactly OK.",
                            mcp_enabled=False,
                            isolated=False,
                            probe_mcp=mcp_file,
                        )
                        runs.append(probe_record(positive, location, "positive"))
                        controls[location] = positive_evidence(positive, marker, hook, mcp)
                        hook.unlink(missing_ok=True)
                        mcp.unlink(missing_ok=True)
                        if positive.status == "usage_limit":
                            return unproven(
                                positive.limit_reason or "CLI usage limit",
                                status="usage_limit",
                                canary_runs=len(runs),
                                runs=runs,
                            )
                        before_start()
                        negative = _execute(
                            cli,
                            config,
                            workspace,
                            "Reply with exactly OK.",
                            mcp_enabled=False,
                        )
                        runs.append(probe_record(negative, location, "isolated"))
                        isolated[location] = canary_passed(negative, cli, marker, hook, mcp)
                        if cli == "claude":
                            inventory["checks"].append(
                                {"location": location, "passed": isolated[location]}
                            )
                        hook.unlink(missing_ok=True)
                        mcp.unlink(missing_ok=True)
                        if negative.status == "usage_limit":
                            return unproven(
                                negative.limit_reason or "CLI usage limit",
                                status="usage_limit",
                                canary_runs=len(runs),
                                runs=runs,
                            )
        if cli == "claude":
            inventory["verified"] = all(isolated.values())
        passed = (
            inventory["verified"]
            and all(
                controls[loc][probe] for loc in LOCATIONS for probe in required_positive(cli, loc)
            )
            and all(isolated.values())
        )
        result = {
            "schema": 2,
            "identity": identity,
            "binary": binary,
            "inventory": inventory,
            "supported": passed,
            "verified": passed,
            "positive_control": controls,
            "required_positive_control": {loc: required_positive(cli, loc) for loc in LOCATIONS},
            "control_note": "Claude's cwd MCP control uses native .mcp.json discovery with "
            "enableAllProjectMcpServers; the config-home control does not require "
            "MCP because .mcp.json is a project discovery file. Other CLIs require "
            "a native instruction positive control and separate native inventories.",
            "isolated_control": isolated,
            "canary_runs": len(runs),
            "canary_location": "native discovery paths inside cwd and dedicated config home",
            "status": "verified" if passed else "unproven",
            "runs": runs,
            "reason": None
            if passed
            else "Positive control or isolated inventory did not prove isolation",
        }
        receipt.write_text(json.dumps(redact_structure(result), indent=2) + "\n")
        return result
    except (ValueError, OSError) as exc:
        return unproven(str(exc), canary_runs=len(runs), runs=runs)
    finally:
        for path in side_effects:
            path.unlink(missing_ok=True)
        lock.rmdir()
