"""Harness-owned configuration homes. Only CLI processes handle their logins."""

from __future__ import annotations

import hashlib
import json
import os
import shlex
import shutil
from pathlib import Path

HOME_VARIABLES = {
    "claude": "CLAUDE_CONFIG_DIR",
    "codex": "CODEX_HOME",
    "gemini": "GEMINI_CLI_HOME",
    "grok": "GROK_HOME",
}


def resolve_executable(cli: str, settings: dict) -> str:
    name = os.environ.get(f"TUI_{cli.upper()}_BIN", settings["executable"])
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
    if data != {"schema": 1, "cli": cli, "home": str(home)} or not config_home.is_dir():
        raise ValueError(f"{cli} setup receipt does not match its dedicated home")
    return home


def setup_home(cli: str, config: dict) -> Path:
    home, config_home = home_paths(cli, config["clis"][cli])
    if setup_file(home).exists():
        return require_setup(cli, config)
    if home.exists() and any(home.iterdir()):
        raise ValueError("Setup requires an empty dedicated home; it never imports existing state")
    home.mkdir(parents=True, mode=0o700, exist_ok=True)
    config_home.mkdir(mode=0o700)
    config_file(cli, config_home).write_text(home_config(cli, config))
    with setup_file(home).open("x") as stream:
        json.dump({"schema": 1, "cli": cli, "home": str(home)}, stream)
    return home


def login_command(cli: str, config: dict) -> str:
    from qa.tui_providers import BASE_ENV

    settings = config["clis"][cli]
    home, _ = home_paths(cli, settings)
    # Changing cwd also excludes this repository's instructions during login.
    env = {key: os.environ[key] for key in BASE_ENV if key in os.environ}
    env.update(home_environment(cli, settings))
    command = ["env", "-i", *(f"{key}={value}" for key, value in env.items())]
    command.append(resolve_executable(cli, settings))
    command += {
        "claude": ["auth", "login", "--claudeai"],
        "codex": ["login"],
        "gemini": [],
        "grok": ["login"],
    }[cli]
    return f"cd {shlex.quote(str(home))} && {shlex.join(command)}"


def isolation_identity(cli: str, config: dict) -> str:
    settings = config["clis"][cli]
    executable = Path(resolve_executable(cli, settings))
    stat = executable.stat()
    home, _ = home_paths(cli, settings)
    identity = {
        "executable": str(executable),
        "build": [stat.st_size, stat.st_mtime_ns, stat.st_ino],
        "home": str(home),
        "profile": settings,
        "mcp_url": config["mcp_url"],
        "mcp_token_env": config.get("mcp_token_env"),
    }
    digest = hashlib.sha256(json.dumps(identity, sort_keys=True).encode())
    for name in ("tui_homes.py", "tui_providers.py", "tui_isolation.py", "tui_harness.py"):
        digest.update(Path(__file__).with_name(name).read_bytes())
    return digest.hexdigest()
