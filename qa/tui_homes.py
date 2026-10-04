"""Native MCP rendering and image-bound identity. No host authentication homes."""

from __future__ import annotations

import hashlib
import json
import os
import re
import shlex
from pathlib import Path

from qa.tui_docker import (
    CONTAINER_HOME,
    GEMINI_RETIRED,
    LOGIN_ARGS,
    container_command,
    docker_environment,
    docker_executable,
    home_volume,
    image_identity,
    passed_environment,
    run_cli,
)


def state_directory(cli: str, config: dict) -> Path:
    try:
        root = Path(config.get("_state_dirs", {}).get(cli, config["_state_dir"]))
    except KeyError:
        raise ValueError("A private --out is required for doctor receipts") from None
    path = root / cli
    if any(p.is_symlink() for p in (path, *path.parents)):
        raise ValueError("Doctor state paths must not be symlinks")
    path.mkdir(parents=True, exist_ok=True, mode=0o700)
    return path


def resolve_executable(cli: str, settings: dict) -> str:
    if settings["executable"] != cli:
        raise ValueError("Use the native executable installed in the pinned Docker image")
    return cli


def home_paths(cli: str, settings: dict) -> tuple[Path, Path]:
    if settings["config_dir"] != "." + cli:
        raise ValueError("config_dir must be the native directory name")
    return CONTAINER_HOME, CONTAINER_HOME / settings["config_dir"]


def block_gemini_dotenv(workspace: Path) -> Path | None:
    path = workspace / ".env"
    if path.is_symlink() or path.exists() and (not path.is_file() or path.stat().st_size):
        raise ValueError("Gemini requires an empty private cwd .env to stop ancestor discovery")
    if not path.exists():
        path.open("x").close()
        return path
    return None


def home_config(cli: str, config: dict, *, enabled=True, server=None, with_token=False) -> str:
    """Render native MCP configuration, retaining only an environment reference."""
    servers = {}
    if enabled and "_mcp_servers" in config:
        servers = config["_mcp_servers"]
        if cli == "gemini":
            servers = {name: item | {"trust": True} for name, item in servers.items()}
    elif server is not None:
        servers = {"model301_canary": server}
    elif enabled:
        item = {"url": config["mcp_url"]}
        token = config.get("mcp_token_env")
        if token and with_token:
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


def login_command(cli: str, config_path: Path | None = None) -> str:
    command = ["python", "-m", "qa.tui_harness", "login", "--cli", cli]
    if config_path is not None and config_path.resolve() != Path(__file__).with_name(
        "tui_config.yaml"
    ):
        command += ["--config", str(config_path.resolve())]
    return shlex.join(command)


def version_numbers(value: str) -> tuple[int, int, int]:
    match = re.search(r"(?<![\d.])(\d+)\.(\d+)(?:\.(\d+))?(?![\d.])", value)
    if not match:
        raise ValueError("CLI version must contain a numeric major.minor[.patch] version")
    return tuple(int(part or 0) for part in match.groups())


def login(cli: str, config: dict) -> None:
    if cli == "gemini":
        # Its Google sign-in now ends at the API-key prompt this harness refuses.
        raise ValueError(GEMINI_RETIRED)
    # Inspect image metadata only. Login inherits terminal stdio through exec.
    identity = image_identity(cli, config)
    env = passed_environment(config)
    env.pop("MODELSPEC_MCP_URL")
    command = container_command(
        cli,
        config,
        None,
        LOGIN_ARGS[cli],
        env,
        interactive=True,
        image=identity["image_id"],
    )
    os.execve(docker_executable(), command, docker_environment(env))


def binary_identity(cli: str, config: dict, workspace: Path, *, versions=None) -> dict:
    identity = image_identity(cli, config)
    config.setdefault("_image_ids", {})[cli] = identity["image_id"]
    if versions is not None:
        if identity != {k: versions[k] for k in identity}:
            raise ValueError("Docker image changed; rerun doctor")
        return versions
    result = run_cli(
        cli, config, workspace, [cli, "--version"], passed_environment(config), home=False
    )
    value = result.stdout.strip()
    if (
        result.returncode
        or result.stderr.strip()
        or len(value) > 500
        or version_numbers(value) != version_numbers(identity["version"])
        or re.search(r"\d\.\d+(?:\.\d+)?-(?:alpha|beta|rc|dev)", value)
    ):
        raise ValueError(f"{cli}: native version differs from its pinned image version")
    return identity | {"reported_version": value}


def isolation_identity(cli: str, config: dict, binary: dict) -> str:
    binary_identity(cli, config, Path("/work"), versions=binary)
    identity = {
        "binary": binary,
        "profile": config["clis"][cli],
        "home_volume": home_volume(cli),
        "mcp_url": config["mcp_url"],
        "mcp_token_env": config.get("mcp_token_env"),
    }
    digest = hashlib.sha256(json.dumps(identity, sort_keys=True).encode())
    for path in sorted(Path(__file__).parent.glob("tui_*.py")):
        digest.update(path.read_bytes())
    for name in (
        "Dockerfile",
        ".dockerignore",
        "entrypoint.py",
        "gemini-settings.mjs",
        "gemini-isolated.json",
        "gemini-positive.json",
        "ux-mcp.mjs",
    ):
        digest.update(Path(__file__).with_name("docker").joinpath(name).read_bytes())
    return digest.hexdigest()
