"""Licence detection and the official remote MCP registry listing (MODEL-261)."""

import hashlib
import importlib.util
import json
import re
import tomllib
from pathlib import Path

import jsonschema
import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "tests/fixtures/mcp_registry/server-2025-12-11.schema.json"


def test_license_is_the_existing_mit_text_only():
    assert hashlib.sha256((ROOT / "LICENSE").read_bytes()).hexdigest() == (
        "11bf2c064d493a1b2dba178c63a6dfefcee76c168e4461497570c2d18e173ce2"
    )
    project = tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]
    assert project["license"] == "MIT"
    assert "LICENSE" in project["license-files"]


def test_licensing_preserves_the_notice_and_its_referenced_mit_text():
    path = ROOT / "LICENSING.md"
    assert path.is_file(), "the existing notice must remain available verbatim"
    assert hashlib.sha256(path.read_bytes()).hexdigest() == (
        "bc906b1ded00661b37b2901f3f43d60a84afc49a3e020ca774e690b20f4cd0f0"
    )
    assert "[LICENSING.md](LICENSING.md)" in (ROOT / "README.md").read_text()
    assert hashlib.sha256((ROOT / "LICENSE-DATA").read_bytes()).hexdigest() == (
        "28a9529c7d0bb4dc51f4bf5c116a3d16ef247a052f7591466768ddf563fd1cf5"
    )


def test_remote_manifest_validates_and_matches_the_deployed_route():
    path = ROOT / "server.json"
    assert path.is_file(), "the remote MCP server needs a registry manifest"
    manifest = json.loads(path.read_text())
    schema = json.loads(SCHEMA.read_text())
    assert hashlib.sha256(SCHEMA.read_bytes()).hexdigest() == (
        "3fba09590c99f61735d234822279f4223fab9e300c0a81e81c91ab62a4114de0"
    )
    assert manifest["$schema"] == schema["$id"]
    jsonschema.validators.validator_for(schema)(schema).validate(manifest)
    assert manifest["name"] == "io.github.turbobeest/modelspec"
    assert manifest["repository"] == {
        "url": "https://github.com/turbobeest/modelspec", "source": "github", "subfolder": "mcp"
    }
    assert manifest["websiteUrl"] == "https://modelspec.dev"
    assert "packages" not in manifest
    remote, = manifest["remotes"]
    assert remote["type"] == "streamable-http"
    assert remote["url"] == "https://api.modelspec.dev/mcp"
    config = (ROOT / "mcp/wrangler.jsonc").read_text()
    assert f'"pattern": "{remote["url"].removeprefix("https://")}*"' in config
    assert '"MCP_REQUIRE_API_KEY": "true"' in config
    header, = remote["headers"]
    assert header["name"] == "Authorization"
    assert header["isRequired"] is True
    assert header["isSecret"] is True
    assert header["value"] == "Bearer {api_key}"
    assert "https://modelspec.dev/pricing/" in header["description"]
    assert header["variables"]["api_key"]["isRequired"] is True
    assert header["variables"]["api_key"]["isSecret"] is True
    assert re.fullmatch(r"[0-9a-f]{40}", manifest["version"])


def test_registry_publishing_is_manual_and_uses_oidc():
    path = ROOT / ".github/workflows/publish-mcp-registry.yml"
    assert path.is_file(), "registry publishing must be available for operator dispatch"
    workflow = yaml.safe_load(path.read_text())
    assert workflow.get("on", workflow.get(True)) == {"workflow_dispatch": None}
    job = workflow["jobs"]["publish"]
    assert job["if"] == "github.ref == 'refs/heads/main'"
    assert job["permissions"] == {"contents": "read", "id-token": "write"}
    commands = "\n".join(step.get("run", "") for step in job["steps"])
    assert "mcp-publisher login github-oidc" in commands
    assert "sha256sum --check" in commands
    assert "/releases/download/v1.8.1/" in commands
    assert "a06c9096dcb9727c13555b6be26c7effa707b01f06a4c561ba7a3635443cf2cc" in commands
    assert "secrets." not in path.read_text()


@pytest.mark.parametrize("sse", [False, True])
def test_publish_manifest_uses_the_verified_worker_commit(sse):
    script = ROOT / "mcp/scripts/registry_manifest.py"
    assert script.is_file(), "publishing must check the deployed Worker's commit"
    spec = importlib.util.spec_from_file_location("registry_manifest", script)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    commit = "a" * 40
    response = json.dumps({"result": {"serverInfo": {"name": "modelspec", "version": commit}}})
    if sse:
        response = f"event: message\ndata: {response}\n\n"
    original = {"version": "b" * 40, "name": "io.github.turbobeest/modelspec"}
    assert module.prepare_manifest(original, response, commit) == {
        "version": commit, "name": "io.github.turbobeest/modelspec"
    }
    assert original["version"] == "b" * 40
    with pytest.raises(ValueError, match="serverInfo.version"):
        module.prepare_manifest(original, response, "c" * 40)
    with pytest.raises(ValueError, match="initialize"):
        module.prepare_manifest(original, '{"error":{"code":-32603}}', commit)
