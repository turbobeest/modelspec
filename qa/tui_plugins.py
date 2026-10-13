"""The opt-in Claude plugin uses native installation and a private per-run cache."""

from __future__ import annotations

import hashlib
import json
import shlex
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NAME = "modelspec"
PLUGIN_ID = "modelspec@modelspec"
SKILL = "modelspec:report-modelspec-answer"
REPOSITORY = Path("/modelspec")
STATE = ".modelspec-claude-plugin"
CONFIG_DIR = Path("/work") / STATE
PLUGIN_CACHE = CONFIG_DIR / "plugins"
ARTIFACTS = (
    ".claude-plugin/marketplace.json",
    "plugins/modelspec/.claude-plugin/plugin.json",
    "plugins/modelspec/skills/report-modelspec-answer/SKILL.md",
)


def plugin_record(config: dict) -> dict | None:
    name = config.get("claude_plugin")
    if name is None:
        return None
    if name != NAME:
        raise ValueError("--claude-plugin must be modelspec")
    manifest = json.loads((ROOT / ARTIFACTS[1]).read_text())
    return {
        "name": NAME,
        "version": manifest["version"],
        "source": "./plugins/modelspec",
        "sha256": plugin_digest(config),
        "git_sha": checkout_sha(),
        "install_commands": [
            ["claude", "plugin", "marketplace", "add", "."],
            ["claude", "plugin", "install", PLUGIN_ID],
        ],
        "skill": SKILL,
        "role": "agent",
    }


def plugin_identity(config: dict) -> dict | None:
    """The record a receipt certifies: content, not the commit it was read from."""
    record = plugin_record(config)
    if record is not None:
        record.pop("git_sha")
    return record


def plugin_digest(config: dict) -> str | None:
    if config.get("claude_plugin") is None:
        return None
    if config["claude_plugin"] != NAME:
        raise ValueError("--claude-plugin must be modelspec")
    digest = hashlib.sha256()
    for name in ARTIFACTS:
        digest.update(name.encode())
        digest.update((ROOT / name).read_bytes())
    return digest.hexdigest()


def checkout_sha() -> str:
    result = subprocess.run(
        ["git", "-C", str(ROOT), "rev-parse", "HEAD"],
        capture_output=True, text=True, check=False,
    )
    return result.stdout.strip() if result.returncode == 0 else "unknown"


def install_commands() -> list[list[str]]:
    prefix = ["env", f"CLAUDE_CONFIG_DIR={CONFIG_DIR}", "claude", "plugin"]
    return [
        prefix + ["marketplace", "add", str(REPOSITORY)],
        prefix + ["install", PLUGIN_ID],
    ]


def prepare_plugin_workspace(workspace: Path) -> None:
    state = workspace / STATE
    plugins = state / "plugins"
    if any(path.is_symlink() for path in (state, plugins)):
        raise ValueError("Claude plugin state must not traverse symlinks")
    plugins.mkdir(parents=True, mode=0o700, exist_ok=True)
    state.chmod(0o700)


def install_plugin(config: dict, workspace: Path, run_cli) -> None:
    from qa.tui_docker import passed_environment

    for command in install_commands():
        result = run_cli(
            "claude", config, workspace, command, passed_environment(config), home=False,
        )
        if result.returncode:
            raise ValueError(
                f"Claude plugin installation failed (exit {result.returncode}): "
                f"{shlex.join(command)}"
            )


def plugin_paths(record: dict) -> set[str]:
    relative = Path("cache/modelspec/modelspec") / record["version"]
    return {
        str(PLUGIN_CACHE / relative),
        str(REPOSITORY / "plugins/modelspec"),
    }


def report_line(record: dict | None, *, dry_run: bool) -> str | None:
    if record is None:
        return None
    commands = " then ".join(f"`{shlex.join(command)}`" for command in record["install_commands"])
    action = "planned" if dry_run else "installed"
    return (
        f"Claude arm: plugin {record['name']} {record['version']} {action} from the checkout via {commands}. "
        "The plugin applies only to the agent role. Judges use the baseline profile."
    )
