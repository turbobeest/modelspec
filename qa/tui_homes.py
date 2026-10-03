"""Harness-owned configuration homes. Only CLI processes handle their logins."""

from __future__ import annotations

import hashlib
import json
import os
import re
import shlex
import shutil
import subprocess
from pathlib import Path

HOME_VARIABLES = {
    "claude": "CLAUDE_CONFIG_DIR",
    "codex": "CODEX_HOME",
    "gemini": "GEMINI_CLI_HOME",
    "grok": "GROK_HOME",
}
APP_CODEX = Path("/Applications/ChatGPT.app/Contents/Resources/codex-cli/bin/codex")


def resolve_executable(cli: str, settings: dict) -> str:
    default = settings["executable"]
    if cli == "codex" and default == "codex" and APP_CODEX.is_file():
        default = str(APP_CODEX)
    name = os.environ.get(f"TUI_{cli.upper()}_BIN", default)
    executable = shutil.which(os.path.expanduser(name))
    if not executable:
        raise ValueError(f"{cli} binary unavailable; set TUI_{cli.upper()}_BIN")
    return str(Path(executable).resolve())


def home_paths(cli: str, settings: dict) -> tuple[Path, Path]:
    name = settings["config_dir"]
    if name != "." + cli:
        raise ValueError(f"{cli} config_dir must be its native directory name")
    requested = Path(settings["harness_home"]).expanduser()
    if not requested.is_absolute():
        raise ValueError("harness_home must be absolute or start with ~/")
    home = requested.resolve()
    real_home = Path.home().resolve()
    if real_home.is_relative_to(home) or any(
        home.is_relative_to(real_home / ("." + family)) for family in HOME_VARIABLES
    ):
        raise ValueError("harness_home must be a dedicated home, outside existing CLI homes")
    if home.is_relative_to(Path(__file__).resolve().parents[1]):
        raise ValueError("harness_home must be outside the public repository")
    config_home = home / name
    if requested.is_symlink() or config_home.is_symlink():
        raise ValueError("Harness homes must not be symlinks")
    return home, config_home


def home_environment(cli: str, settings: dict) -> dict[str, str]:
    home, config_home = home_paths(cli, settings)
    return {
        "HOME": str(home),
        HOME_VARIABLES[cli]: str(home if cli == "gemini" else config_home),
        "XDG_CONFIG_HOME": str(home / ".config"),
        "XDG_DATA_HOME": str(home / ".local/share"),
        "XDG_CACHE_HOME": str(home / ".cache"),
    }


def config_file(cli: str, config_home: Path) -> Path:
    return (
        config_home
        / {
            "claude": "modelspec-mcp.json",
            "codex": "config.toml",
            "gemini": "settings.json",
            "grok": "config.toml",
        }[cli]
    )


def home_config(cli: str, config: dict, *, enabled=True, server=None) -> str:
    """Render native MCP configuration, retaining only an environment reference."""
    servers = {}
    if server is not None:
        servers = {"model301_canary": server}
    elif enabled:
        item = {"url": config["mcp_url"]}
        token = config.get("mcp_token_env")
        if token:
            if cli == "codex":
                item["bearer_token_env_var"] = token
            else:
                item["headers"] = {"Authorization": "Bearer ${" + token + "}"}
        if cli == "claude":
            item["type"] = "http"
        if cli == "gemini":
            item["httpUrl"] = item.pop("url")
        servers = {"modelspec": item}
    if cli in ("claude", "gemini"):
        return json.dumps({"mcpServers": servers})
    lines = []
    for name, item in servers.items():
        lines.append(f"[mcp_servers.{name}]")
        for key, value in item.items():
            if isinstance(value, dict):
                value = (
                    "{ "
                    + ", ".join(json.dumps(k) + " = " + json.dumps(v) for k, v in value.items())
                    + " }"
                )
            else:
                value = json.dumps(value)
            lines.append(f"{key} = {value}")
    return "\n".join(lines) + "\n"


def setup_file(home: Path) -> Path:
    return home.parent / "tui-setup.json"


def require_setup(cli: str, config: dict) -> Path:
    home, config_home = home_paths(cli, config["clis"][cli])
    marker = setup_file(home)
    if marker.is_symlink():
        raise ValueError("Harness setup receipt must not be a symlink")
    try:
        data = json.loads(marker.read_text())
    except (OSError, ValueError) as exc:
        raise ValueError(f"{cli} home is unprepared; run setup --cli {cli}") from exc
    if (
        not isinstance(data, dict)
        or data.get("schema") not in (1, 2)
        or data.get("cli") != cli
        or data.get("home") != str(home)
        or data.get("schema") == 2
        and not isinstance(data.get("binary"), dict)
        or not config_home.is_dir()
    ):
        raise ValueError(f"{cli} setup receipt does not match its dedicated home")
    return home


def setup_home(cli: str, config: dict) -> Path:
    home, config_home = home_paths(cli, config["clis"][cli])
    if setup_file(home).exists():
        require_setup(cli, config)
    else:
        if home.exists() and any(home.iterdir()):
            raise ValueError(
                "Setup requires an empty dedicated home; it never imports existing state"
            )
        home.mkdir(parents=True, mode=0o700, exist_ok=True)
        config_home.mkdir(mode=0o700)
        config_file(cli, config_home).write_text(home_config(cli, config))
        # Record ownership before launching --version so a failed version check
        # can be retried without importing or deleting any CLI-created state.
        with setup_file(home).open("x") as stream:
            json.dump({"schema": 2, "cli": cli, "home": str(home), "binary": {}}, stream)
    binary = binary_identity(cli, config, home)
    with setup_file(home).open("w") as stream:
        json.dump({"schema": 2, "cli": cli, "home": str(home), "binary": binary}, stream, indent=2)
        stream.write("\n")
    return home


def login_command(cli: str, config_path: Path | None = None) -> str:
    command = ["python", "-m", "qa.tui_harness", "login", "--cli", cli]
    if config_path is not None and config_path.resolve() != Path(__file__).with_name(
        "tui_config.yaml"
    ):
        command += ["--config", str(config_path.resolve())]
    return shlex.join(command)


def login(cli: str, config: dict) -> None:
    from qa.tui_providers import child_environment

    home = require_setup(cli, config)
    settings = config["clis"][cli]
    recorded = json.loads(setup_file(home).read_text()).get("binary", {})
    if "version" not in recorded:
        raise ValueError(f"Repeat setup --cli {cli} to record the CLI version before login")
    if binary_identity(cli, config, home, versions=recorded) != recorded:
        raise ValueError(f"CLI changed after setup; repeat setup --cli {cli} before login")
    env = child_environment(cli, home, config.get("mcp_token_env"), settings=settings)
    env["TERM"] = os.environ.get("TERM", "xterm-256color")
    executable = resolve_executable(cli, settings)
    command = [
        executable,
        *{
            "claude": ["auth", "login", "--claudeai"],
            "codex": ["login"],
            "gemini": [],
            "grok": ["login"],
        }[cli],
    ]
    os.chdir(home)
    os.execve(executable, command, env)


def version_numbers(value: str) -> tuple[int, int, int]:
    match = re.search(r"(?<![\d.])(\d+)\.(\d+)(?:\.(\d+))?(?![\d.])", value)
    if not match:
        raise ValueError("CLI version must contain a numeric major.minor[.patch] version")
    return tuple(int(part or 0) for part in match.groups())


def read_version(path: str, workspace: Path, env: dict, timeout: float) -> str:
    try:
        result = subprocess.run(
            [path, "--version"],
            cwd=workspace,
            env=env,
            input="",
            text=True,
            capture_output=True,
            timeout=timeout,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ValueError("CLI --version failed; check the native binary override") from exc
    value = result.stdout.strip()
    if result.returncode or not value or len(value) > 500:
        raise ValueError("CLI --version failed; check the native binary override")
    version_numbers(value)
    return value


def gemini_runtime(executable: Path) -> tuple[Path, Path]:
    node = shutil.which("node")
    if executable.suffix != ".js" or not node:
        raise ValueError(
            "Gemini requires its native bundle/gemini.js and Node on PATH; "
            "set TUI_GEMINI_BIN to the native npm entry, not a shell wrapper"
        )
    return Path(node).resolve(), executable


def binary_identity(
    cli: str, config: dict, workspace: Path, *, versions: dict | None = None
) -> dict:
    """Measure versions only at setup/doctor; receipt reuse checks the same paths and stats."""
    from qa.tui_providers import child_environment

    settings = config["clis"][cli]
    env = child_environment(cli, workspace, config.get("mcp_token_env"), settings=settings)

    def record(path, cached=None):
        stat = path.stat()
        version = (
            cached
            if cached is not None
            else read_version(str(path), workspace, env, config["timeout_seconds"])
        )
        return {
            "path": str(path),
            "version": version,
            "size": stat.st_size,
            "mtime": stat.st_mtime_ns,
        }

    executable = Path(resolve_executable(cli, settings))
    identity = record(executable, versions["version"] if versions else None)
    minimum = settings.get("min_version")
    if minimum is not None and (
        version_numbers(identity["version"]) < version_numbers(minimum)
        or re.search(r"\d\.\d+(?:\.\d+)?-(?:alpha|beta|rc|dev)", identity["version"])
        and version_numbers(identity["version"]) == version_numbers(minimum)
    ):
        raise ValueError(f"{cli} {identity['version']} is below min_version {minimum}")
    if cli == "gemini":
        node, bundle = gemini_runtime(executable)
        identity["node"] = record(node, versions["node"]["version"] if versions else None)
        identity["bundle"] = {
            "path": str(bundle),
            "size": bundle.stat().st_size,
            "mtime": bundle.stat().st_mtime_ns,
            "sources": hashlib.sha256(
                json.dumps(
                    [
                        [
                            str(path.relative_to(bundle.parent)),
                            path.stat().st_size,
                            path.stat().st_mtime_ns,
                        ]
                        for path in sorted(bundle.parent.rglob("*.js"))
                    ]
                ).encode()
            ).hexdigest(),
        }
    return identity


def isolation_identity(cli: str, config: dict, binary: dict | None = None) -> str:
    settings = config["clis"][cli]
    home, _ = home_paths(cli, settings)
    if binary is None:
        binary = json.loads(setup_file(home).read_text())["binary"]
    if binary_identity(cli, config, home, versions=binary) != binary:
        raise ValueError("CLI binary, Node or Gemini bundle changed; rerun doctor")
    identity = {
        "binary": binary,
        "home": str(home),
        "profile": settings,
        "mcp_url": config["mcp_url"],
        "mcp_token_env": config.get("mcp_token_env"),
    }
    digest = hashlib.sha256(json.dumps(identity, sort_keys=True).encode())
    for name in (
        "tui_homes.py",
        "tui_providers.py",
        "tui_isolation.py",
        "tui_harness.py",
        "tui_inventory.py",
    ):
        digest.update(Path(__file__).with_name(name).read_bytes())
    return digest.hexdigest()
