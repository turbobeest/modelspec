"""The MCP Worker deploy gate can fail, and a 522 cannot abort it."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "mcp.yml"
CHECKER = REPO_ROOT / "mcp" / "scripts" / "check_response.py"


def _checker():
    spec = importlib.util.spec_from_file_location("check_mcp_response", CHECKER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_the_mcp_worker_deploys_only_from_main() -> None:
    workflow = WORKFLOW.read_text(encoding="utf-8")
    assert "    name: Deploy the MCP Worker\n" in workflow
    assert ("if: github.event_name == 'push' && github.ref == 'refs/heads/main'"
            in workflow)


def test_deploy_secrets_are_not_in_scope_on_a_pull_request() -> None:
    workflow = yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))
    test_job = workflow["jobs"]["test"]
    assert "secrets." not in yaml.safe_dump(test_job)
    deploy_env = workflow["jobs"]["deploy"]["env"]
    assert deploy_env["CLOUDFLARE_API_TOKEN"] == \
        "${{ secrets.CLOUDFLARE_API_MODELSPEC_TOKEN }}"


def test_the_bundle_is_proven_to_build_on_every_pull_request() -> None:
    workflow = WORKFLOW.read_text(encoding="utf-8")
    assert "deploy --dry-run" in workflow
    assert "npm test" in workflow
    assert "npm run typecheck" in workflow


def test_the_smoke_test_asserts_the_deployed_version_is_the_one_answering() -> None:
    workflow = WORKFLOW.read_text(encoding="utf-8")
    assert "BUILD_COMMIT:${GITHUB_SHA}" in workflow
    assert "tools/list" in workflow
    assert "https://api.modelspec.dev/mcp" in workflow
    assert "::error::" in workflow
    assert "continue-on-error" not in workflow


def test_no_mcp_response_body_can_make_the_smoke_test_raise(tmp_path: Path) -> None:
    checker = _checker()
    path = tmp_path / "body.json"
    path.write_bytes(b"error code: 522")
    parsed, raw, problem = checker.read_body(str(path))
    assert parsed is None
    assert raw == b"error code: 522"
    assert problem
    line = checker.describe("/mcp", "522", raw, problem)
    assert "\n" not in line
    assert "HTTP 522" in line


def test_tools_list_check_requires_the_four_tools() -> None:
    checker = _checker()
    payload = {
        "jsonrpc": "2.0",
        "id": 2,
        "result": {
            "tools": [
                {"name": "rank", "inputSchema": {"type": "object"}},
                {"name": "model_info", "inputSchema": {"type": "object"}},
                {"name": "list_use_cases", "inputSchema": {"type": "object"}},
                {"name": "policy_check", "inputSchema": {"type": "object"}},
            ]
        },
    }
    assert checker.check_tools_list(payload) == []
    assert checker.check_tools_list({"result": {"tools": []}})


@pytest.mark.parametrize("body", [
    b"error code: 522",
    b"",
    b"<!DOCTYPE html>",
    b'{"jsonrpc":"2.0"',
])
def test_field_version_exits_zero_on_unreadable_bodies(
        body: bytes, tmp_path: Path) -> None:
    import subprocess
    import sys

    path = tmp_path / "body.json"
    path.write_bytes(body)
    done = subprocess.run(
        [sys.executable, str(CHECKER), "field", "version", str(path)],
        capture_output=True, text=True, check=False)
    assert done.returncode == 0
