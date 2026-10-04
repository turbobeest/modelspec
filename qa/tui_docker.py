"""Local Docker execution. Authentication volumes are never inspected or copied."""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import tempfile
import uuid
from pathlib import Path

from qa.docker.entrypoint import PASSED_ENV, refuse_vendor_auth

DOCKER_CONTEXT = Path(__file__).with_name("docker")
CONTAINER_HOME = Path("/home/agent")
CONTAINER_WORK = Path("/work")
LOGIN_ARGS = {
    "claude": ["claude", "auth", "login", "--claudeai"],
    "codex": ["codex", "-c", 'cli_auth_credentials_store="file"', "login", "--device-auth"],
    "gemini": ["gemini"],
    "grok": ["grok", "login", "--device-auth"],
}
# Google's notice: github.com/google-gemini/gemini-cli/discussions/27274
GEMINI_RETIRED = (
    "Google stopped serving Gemini CLI for Google AI Pro, AI Ultra and free accounts on "
    "2026-06-18; only paid API keys and Code Assist Standard/Enterprise remain"
)
_CLIENT_ENV: dict | None = None


def docker_executable() -> str:
    executable = shutil.which("docker")
    if not executable:
        raise ValueError("Docker is unavailable; install/start Docker before build-images")
    return executable


def docker_environment(passed: dict | None = None) -> dict:
    # The client needs HOME to find Docker Desktop's socket context. It never
    # forwards HOME or PATH into the container. No vendor variables reach it.
    global _CLIENT_ENV
    if _CLIENT_ENV is None:
        base = {name: os.environ[name] for name in ("HOME", "PATH") if name in os.environ}
        result = subprocess.run(
            [docker_executable(), "context", "inspect", "--format", "{{.Endpoints.docker.Host}}"],
            env=base,
            input="",
            text=True,
            capture_output=True,
            timeout=15,
        )
        host = result.stdout.strip()
        if result.returncode or not host.startswith("unix://"):
            raise ValueError("Harness requires a local Docker engine on a Unix socket")
        # Buildx writes activity files. Keep those in a private temporary client
        # directory, without reading or copying the user's Docker configuration.
        client = tempfile.mkdtemp(prefix="modelspec-tui-docker-client-")
        plugins = Path(docker_executable()).resolve().parent.parent / "cli-plugins"
        if plugins.is_dir():
            Path(client, "config.json").write_text(
                json.dumps({"cliPluginsExtraDirs": [str(plugins)]})
            )
        _CLIENT_ENV = base | {"DOCKER_CONFIG": client, "DOCKER_HOST": host}
    env = dict(_CLIENT_ENV)
    env.update(passed or {})
    return env


def image_name(cli: str, settings: dict) -> str:
    version = settings["version"]
    if (
        cli not in LOGIN_ARGS
        or not isinstance(version, str)
        or not re.fullmatch(r"\d+\.\d+\.\d+", version)
    ):
        raise ValueError("Docker CLI profiles require an exact stable version")
    if settings.get("executable") != cli:
        raise ValueError("CLI executable must be its image-installed native command")
    variant = settings.get("image_variant", "")
    if variant not in ("", "ux"):
        raise ValueError("Unknown Docker image variant")
    return f"modelspec-harness-{cli}{'-ux' if variant else ''}:{version}"


def home_volume(cli: str) -> str:
    if cli not in LOGIN_ARGS:
        raise ValueError("Unknown subscription CLI")
    return f"modelspec-harness-{cli}-home"


def image_identity(cli: str, config: dict) -> dict:
    settings = config["clis"][cli]
    name = image_name(cli, settings)
    result = subprocess.run(
        [docker_executable(), "image", "inspect", name],
        env=docker_environment(),
        input="",
        capture_output=True,
        text=True,
        timeout=30,
    )
    if result.returncode:
        info = subprocess.run(
            [docker_executable(), "info"],
            env=docker_environment(),
            input="",
            capture_output=True,
            text=True,
            timeout=30,
        )
        if info.returncode:
            raise ValueError("Docker Desktop is not running or its engine is unavailable; start Docker Desktop")
    try:
        if result.returncode:
            raise ValueError()
        rows = json.loads(result.stdout)
        if not isinstance(rows, list) or len(rows) != 1:
            raise ValueError()
        row = rows[0]
        labels = row["Config"]["Labels"]
        if (
            not re.fullmatch(r"sha256:[a-f0-9]{64}", row["Id"])
            or labels.get("modelspec.cli") != cli
            or labels.get("modelspec.cli_version") != settings["version"]
            or row.get("Os") != "linux"
            or row["Config"].get("User") != "agent"
            or labels.get("modelspec.agent_uid") != str(os.getuid())
            or row["Config"].get("Entrypoint")
            != ["python3", "/opt/modelspec-harness/entrypoint.py"]
        ):
            raise ValueError()
        refuse_vendor_auth(dict(item.split("=", 1) for item in row["Config"]["Env"]))
        return {
            "image": name,
            "image_id": row["Id"],
            "version": settings["version"],
            "os": "linux",
            "architecture": row["Architecture"],
        }
    except (ValueError, KeyError, TypeError, AttributeError):
        raise ValueError(
            f"{cli}: image is missing or invalid; run build-images --cli {cli}"
        ) from None


def passed_environment(config: dict, *, token: bool = False) -> dict:
    env = {name: os.environ[name] for name in ("TERM", "LANG") if name in os.environ}
    env.setdefault("TERM", "xterm-256color")
    env.setdefault("LANG", "C.UTF-8")
    env["MODELSPEC_MCP_URL"] = config["mcp_url"]
    name = config.get("mcp_token_env")
    if token and name and os.environ.get(name):
        env[name] = os.environ[name]
    return env


def container_path(workspace: Path, path: Path) -> str:
    return str(CONTAINER_WORK / path.relative_to(workspace))


def container_command(
    cli: str,
    config: dict,
    workspace: Path | None,
    command: list[str],
    env: dict,
    *,
    isolated: bool = True,
    interactive: bool = False,
    name: str | None = None,
    image: str | None = None,
    home: bool = True,
    preview: bool = False,
) -> list[str]:
    refuse_vendor_auth(env)
    allowed = PASSED_ENV | ({config["mcp_token_env"]} if config.get("mcp_token_env") else set())
    if set(env) - allowed:
        raise ValueError("Container environment must use the explicit harness allowlist")
    argv = ["docker" if preview else docker_executable(), "run", "--rm", "--init", "--pull=never"]
    if name:
        argv += ["--name", name]
    argv += ["--cap-drop=ALL", "--security-opt=no-new-privileges", "--workdir", "/work"]
    if interactive:
        argv += ["-it"]
    else:
        argv += ["-i"]
    if home:
        argv += ["--mount", f"type=volume,source={home_volume(cli)},target=/home/agent"]
    else:
        argv += ["--tmpfs", f"/home/agent:rw,uid={os.getuid()},gid={os.getgid()},mode=700"]
    if workspace is not None:
        resolved = workspace.resolve()
        root = Path(__file__).resolve().parents[1]
        real_home = Path.home().resolve()
        if (
            not resolved.is_dir()
            or "," in str(resolved)
            or real_home.is_relative_to(resolved)
            or resolved.is_relative_to(root)
            or any(resolved.is_relative_to(real_home / ("." + family)) for family in LOGIN_ARGS)
        ):
            raise ValueError("Only a private per-run workspace may be mounted at /work")
        argv += ["--mount", f"type=bind,source={resolved},target=/work"]
    for key in sorted(env):
        argv += ["--env", key]  # Values, especially the ModelSpec key, never enter argv.
    argv += [
        image or config.get("_image_ids", {}).get(cli) or image_name(cli, config["clis"][cli]),
        cli,
        "login" if interactive else "isolated" if isolated else "positive",
        *command,
    ]
    return argv


def remove_container(name: str) -> None:
    subprocess.run(
        [docker_executable(), "rm", "--force", name],
        env=docker_environment(),
        input="",
        capture_output=True,
        text=True,
        timeout=15,
    )


def run_cli(
    cli: str,
    config: dict,
    workspace: Path,
    command: list[str],
    env: dict,
    *,
    isolated: bool = True,
    home: bool = True,
    input_text: str = "",
) -> subprocess.CompletedProcess:
    name = "modelspec-tui-" + uuid.uuid4().hex
    argv = container_command(
        cli,
        config,
        workspace,
        command,
        env,
        isolated=isolated,
        name=name,
        home=home and not config.get("_anonymous_home", False),
    )
    try:
        return subprocess.run(
            argv,
            cwd=workspace,
            env=docker_environment(env),
            input=input_text,
            text=True,
            capture_output=True,
            timeout=config["timeout_seconds"],
        )
    except BaseException:
        # Killing the Docker client alone can leave a billable container running.
        remove_container(name)
        raise


def popen_cli(cli: str, config: dict, workspace: Path, command: list[str], env: dict):
    name = "modelspec-tui-" + uuid.uuid4().hex
    argv = container_command(
        cli,
        config,
        workspace,
        command,
        env,
        name=name,
        home=not config.get("_anonymous_home", False),
    )
    process = subprocess.Popen(
        argv,
        cwd=workspace,
        env=docker_environment(env),
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    process.tui_container_name = name
    return process


def stop_process(process) -> tuple:
    remove_container(process.tui_container_name)
    try:
        return process.communicate(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()
        return process.communicate()


def build_images(config: dict, selected: list[str]) -> None:
    for cli in selected:
        settings = config["clis"][cli]
        name = image_name(cli, settings)
        result = subprocess.run(
            [
                docker_executable(),
                "build",
                "--target",
                cli + ("-ux" if settings.get("image_variant") == "ux" else ""),
                "--build-arg",
                f"CLI_VERSION={settings['version']}",
                "--build-arg",
                f"AGENT_UID={os.getuid()}",
                "--tag",
                name,
                str(DOCKER_CONTEXT),
            ],
            env=docker_environment(),
            check=False,
        )
        if result.returncode:
            raise ValueError(f"{cli}: local image build failed")
        identity = image_identity(cli, config)
        print(f"Built {name} ({identity['image_id']})")
