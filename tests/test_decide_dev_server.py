"""The documented decide dev server builds and serves frozen data offline."""

from __future__ import annotations

import ast
import json
import os
import re
import selectors
import shlex
import socket
import subprocess
import sys
from http.client import HTTPConnection
from pathlib import Path
from time import monotonic

import pytest

REPO = Path(__file__).resolve().parents[1]
WEB = REPO / "web"


def _readme_command() -> tuple[list[str], dict[str, str]]:
    readme = (WEB / "README.md").read_text(encoding="utf-8")
    section = readme.split("## The decide page against real data\n", 1)[1].split("\n## ", 1)[0]
    block = re.search(r"```bash\n(.*?)\n```", section, re.DOTALL)
    assert block is not None
    lines = block.group(1).splitlines()
    assert all("curl" not in line and "snapshot.json.gz" not in line for line in lines)
    command = next(line for line in lines if "decide_dev_server.py" in line)
    argv = shlex.split(command)
    env = {}
    while "=" in argv[0]:
        name, value = argv.pop(0).split("=", 1)
        env[name] = value
    assert env["PYTHONPATH"] == ".."
    assert argv[0] == "python"
    assert all(not arg.startswith("--snapshot") for arg in argv)
    argv[0] = sys.executable
    return argv, env


def _wait_for_ready(process: subprocess.Popen[str], stderr: Path) -> tuple[str, int]:
    assert process.stdout is not None
    deadline = monotonic() + 240
    lines = []
    with selectors.DefaultSelector() as selector:
        selector.register(process.stdout, selectors.EVENT_READ)
        while monotonic() < deadline:
            if not selector.select(timeout=max(0, deadline - monotonic())):
                break
            line = process.stdout.readline()
            if not line:
                break
            lines.append(line)
            ready = re.match(r"^(snap_\S+) on http://127\.0\.0\.1:(\d+) ", line)
            if ready is not None:
                return ready.group(1), int(ready.group(2))
    pytest.fail(
        f"server did not become ready; exit code: {process.poll()}\n"
        f"stdout: {''.join(lines)}\nstderr: {stderr.read_text(encoding='utf-8')}"
    )


def test_readme_dev_server_works_offline(tmp_path: Path) -> None:
    argv, documented_env = _readme_command()
    (tmp_path / "sitecustomize.py").write_text(
        """\
import socket

original_connect = socket.socket.connect
original_create_connection = socket.create_connection
original_getaddrinfo = socket.getaddrinfo

def check_host(host):
    if host not in ("127.0.0.1", "::1", "localhost"):
        raise OSError("network blocked")

def connect(self, address):
    check_host(address[0])
    return original_connect(self, address)

def create_connection(address, *args, **kwargs):
    check_host(address[0])
    return original_create_connection(address, *args, **kwargs)

def getaddrinfo(host, *args, **kwargs):
    check_host(host)
    return original_getaddrinfo(host, *args, **kwargs)

socket.socket.connect = connect
socket.create_connection = create_connection
socket.getaddrinfo = getaddrinfo
""",
        encoding="utf-8",
    )
    env = {**os.environ, **documented_env}
    documented_paths = [str((WEB / path).resolve())
                        for path in documented_env["PYTHONPATH"].split(os.pathsep)]
    env["PYTHONPATH"] = os.pathsep.join([str(tmp_path), *documented_paths])
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        port = listener.getsockname()[1]
    stderr_path = tmp_path / "server.stderr"
    with stderr_path.open("w", encoding="utf-8") as stderr, subprocess.Popen(
        [*argv, "--port", str(port)],
        cwd=WEB,
        env=env,
        stdout=subprocess.PIPE,
        stderr=stderr,
        text=True,
    ) as process:
        try:
            snapshot_id, bound_port = _wait_for_ready(process, stderr_path)
            assert bound_port == port
            connection = HTTPConnection("127.0.0.1", bound_port, timeout=30)
            try:
                bodies = []
                for route in ("/api/decision/vocabulary.json", "/v1/vocabulary"):
                    connection.request("GET", route)
                    response = connection.getresponse()
                    body = response.read()
                    assert response.status == 200, body
                    assert response.getheader("content-type") == "application/json; charset=utf-8"
                    bodies.append(body)
                assert bodies[0] == bodies[1]
                assert json.loads(bodies[0])["snapshot"] == snapshot_id

                payload = {
                    "spec_version": 1,
                    "optimize": {"max": "software_engineering"},
                    "explain": "none",
                    "limit": 1,
                }
                connection.request("POST", "/v1/decide", json.dumps(payload),
                                   {"Content-Type": "application/json"})
                response = connection.getresponse()
                body = response.read()
                assert response.status == 200, body
                decision = json.loads(body)
                assert decision["snapshot"] == snapshot_id
                assert decision["explain"] == "none"

                connection.request("POST", "/v1/decide", b"{invalid json",
                                   {"Content-Type": "application/json"})
                response = connection.getresponse()
                body = response.read()
                assert response.status == 400, body
                error = json.loads(body)
                assert error["error"]["code"] == "invalid_request"
                assert error["endpoint"] == "decide"
                assert error["snapshot"] is None
            finally:
                connection.close()
        finally:
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=10)


def test_docstring_does_not_point_to_removed_public_snapshot() -> None:
    source = (REPO / "scripts" / "decide_dev_server.py").read_text(encoding="utf-8")
    docstring = ast.get_docstring(ast.parse(source))
    assert docstring is not None
    assert "modelspec.dev/api/decision/snapshot.json.gz" not in docstring
