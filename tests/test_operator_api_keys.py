"""Operator-issued API keys use the Worker's storage contract (MODEL-166)."""

from __future__ import annotations

import asyncio
import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
WORKER_SRC = REPO_ROOT / "api" / "worker" / "src"
for path in (str(REPO_ROOT), str(WORKER_SRC)):
    if path not in sys.path:
        sys.path.insert(0, path)

import access_config  # noqa: E402
import access_keys  # noqa: E402
from access_kv import MemoryKV  # noqa: E402

from scripts import issue_api_key, revoke_api_key  # noqa: E402


def test_an_operator_key_round_trips_through_the_worker_lookup() -> None:
    issued = issue_api_key.build_key(
        owner="x402-smoke", label="Base Sepolia smoke test", tier="free"
    )
    kv = MemoryKV()
    asyncio.run(kv.put(issued.name, issued.value))

    record = asyncio.run(access_keys.lookup(kv, issued.secret))

    assert issued.secret.startswith("live_")
    assert len(issued.secret.removeprefix("live_")) == 32
    assert issued.name == access_keys.storage_name(issued.secret)
    assert record is not None
    assert record.to_json() == {
        "key_id": access_keys.fingerprint(issued.secret)[:12],
        "tier": "free",
        "owner": "x402-smoke",
        "created_at": issued.created_at,
        "active": True,
        "label": "Base Sepolia smoke test",
    }


def test_issue_prints_the_secret_once_and_nowhere_else(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    secret = "live_OPERATOR_TEST_SECRET"
    monkeypatch.setattr(access_keys, "mint", lambda policy: secret)

    result = issue_api_key.main(["--owner", "x402-smoke"])

    output = capsys.readouterr()
    assert result == 0
    assert output.err == ""
    assert output.out.count(secret) == 1
    assert f"API key: {secret}" in output.out
    assert "Store it in 1Password now." in output.out
    command = next(line for line in output.out.splitlines() if "wrangler kv key put" in line)
    assert secret not in command
    assert "--binding ACCESS" in command
    assert "--remote" in command
    assert "api/worker/wrangler.jsonc" in command
    assert access_keys.storage_name(secret) in command


def test_issue_put_runs_the_printed_wrangler_command_without_the_secret(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    secret = "live_OPERATOR_PUT_TEST_SECRET"
    calls: list[list[str]] = []
    monkeypatch.setattr(access_keys, "mint", lambda policy: secret)

    def run(command: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        calls.append(command)
        return subprocess.CompletedProcess(command, 0, "", "")

    monkeypatch.setattr(issue_api_key.subprocess, "run", run)

    result = issue_api_key.main(["--owner", "x402-smoke", "--put"])

    output = capsys.readouterr()
    assert result == 0
    assert len(calls) == 1
    assert secret not in " ".join(calls[0])
    assert output.out.count(secret) == 1


def test_issue_put_targets_the_named_wrangler_environment(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    secret = "live_OPERATOR_STAGING_TEST_SECRET"
    calls: list[list[str]] = []
    monkeypatch.setattr(access_keys, "mint", lambda policy: secret)

    def run(command: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        calls.append(command)
        return subprocess.CompletedProcess(command, 0, "", "")

    monkeypatch.setattr(issue_api_key.subprocess, "run", run)

    result = issue_api_key.main(
        ["--owner", "x402-smoke", "--env", "staging", "--put"]
    )

    output = capsys.readouterr()
    assert result == 0
    assert len(calls) == 1
    assert calls[0][calls[0].index("--env") + 1] == "staging"
    assert secret not in " ".join(calls[0])
    assert "--env staging" in output.out


def test_issue_refuses_a_tier_that_the_worker_does_not_know(
    capsys: pytest.CaptureFixture[str],
) -> None:
    result = issue_api_key.main(["--owner", "x402-smoke", "--tier", "unknown"])

    output = capsys.readouterr()
    assert result == 2
    assert "no tier named 'unknown'" in output.err
    assert "live_" not in output.out


def test_revoke_marks_the_stored_record_inactive(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    secret = "live_OPERATOR_REVOKE_TEST_SECRET"
    issued = issue_api_key.build_key(owner="x402-smoke", label="smoke", secret=secret)
    fingerprint = access_keys.fingerprint(secret)
    calls: list[list[str]] = []

    def run(command: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        calls.append(command)
        if command[4] == "get":
            return subprocess.CompletedProcess(command, 0, issued.value + "\n", "")
        return subprocess.CompletedProcess(command, 0, "", "")

    monkeypatch.setattr(revoke_api_key.subprocess, "run", run)

    result = revoke_api_key.main([fingerprint, "--put"])

    output = capsys.readouterr()
    assert result == 0
    assert output.err == ""
    assert [command[4] for command in calls] == ["get", "put"]
    stored = json.loads(calls[1][calls[1].index("--value") + 1])
    assert stored == {**json.loads(issued.value), "active": False}
    assert secret not in output.out + output.err + " ".join(sum(calls, []))

    kv = MemoryKV()
    asyncio.run(kv.put(issued.name, json.dumps(stored)))
    record = asyncio.run(access_keys.lookup(kv, secret))
    assert record is not None and record.active is False


@pytest.mark.parametrize("fingerprint", ["short", "g" * 64, "A" * 64])
def test_revoke_refuses_anything_but_a_sha256_fingerprint(
    fingerprint: str, capsys: pytest.CaptureFixture[str]
) -> None:
    result = revoke_api_key.main([fingerprint])

    output = capsys.readouterr()
    assert result == 2
    assert "64 lowercase hexadecimal characters" in output.err


def test_scripts_read_the_access_binding_from_wrangler() -> None:
    assert issue_api_key.access_binding() == "ACCESS"
    assert revoke_api_key.access_binding() == "ACCESS"
    assert access_config.load_policy().live_prefix == "live_"
