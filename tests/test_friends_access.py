"""MODEL-282: invited keys remain keyed, credit-exempt, metered and revocable."""

from __future__ import annotations

import asyncio
import json
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace

import pytest

WORKER_SRC = Path(__file__).resolve().parents[1] / "api" / "worker" / "src"
sys.path.insert(0, str(WORKER_SRC))

import access_config  # noqa: E402
import access_keys  # noqa: E402
import access_limits  # noqa: E402
import credits  # noqa: E402
from access_kv import CloudflareKV  # noqa: E402

from scripts import issue_api_key, revoke_api_key  # noqa: E402
from tests.test_access_wiring import (  # noqa: E402
    TIERS,
    Request,
    WorkersKV,
    _env,
)
from tests.test_access_wiring import entry as entry  # noqa: E402

NOW = datetime(2026, 10, 14, 12, 30, tzinfo=UTC)
SECRET = "live_MODEL_282_friends_fixture"
FRIENDS = {
    "daily_limit": None,
    "burst_limit": 60,
    "live_data": True,
    "paid": True,
    "credits_exempt": True,
    "description": "Friends and family: live access without credit charges.",
}


def _configured_policy(tier="friends"):
    raw = json.loads(TIERS)
    raw["tiers"][tier] = FRIENDS
    return raw


def test_shipped_friends_tier_matches_the_highest_paid_burst():
    policy = access_config.load_policy()
    friends = policy.tier("friends")
    assert friends.daily_limit is None
    assert friends.burst_limit == 60 == policy.tier("paid").burst_limit
    assert friends.live_data is True
    assert friends.paid is True
    assert friends.credits_exempt is True
    assert friends.unlimited is False
    assert policy.tier("paid").credits_exempt is False


def test_credit_exemption_survives_policy_round_trip():
    policy = access_config.policy_from_mapping(_configured_policy())
    reloaded = access_config.policy_from_mapping(policy.to_json())
    assert reloaded.tier("friends").credits_exempt is True


def test_operator_can_issue_a_friends_key(monkeypatch, capsys):
    calls = []
    monkeypatch.setattr(access_keys, "mint", lambda policy: SECRET)

    def run(command, **kwargs):
        calls.append(command)
        return subprocess.CompletedProcess(command, 0)

    monkeypatch.setattr(issue_api_key.subprocess, "run", run)
    result = issue_api_key.main([
        "--owner", "friends-fixture", "--tier", "friends", "--put",
    ])

    output = capsys.readouterr()
    assert result == 0
    assert output.err == ""
    assert output.out.count(SECRET) == 1
    assert len(calls) == 1
    command = calls[0]
    stored = json.loads(command[command.index("--value") + 1])
    assert stored["tier"] == "friends"
    assert stored["active"] is True
    assert SECRET not in " ".join(command)
    assert command[5] == access_keys.storage_name(SECRET)


@pytest.fixture
def friends_worker(entry, monkeypatch):
    def build(*, enabled="false", ledger_bound=True, tier="friends"):
        raw = _configured_policy(tier)
        policy = access_config.policy_from_mapping(raw)
        binding = WorkersKV()
        kv = CloudflareKV(binding)
        asyncio.run(access_keys.issue(
            kv, tier=tier, owner="friends-fixture", now=NOW,
            policy=policy, secret=SECRET,
        ))
        env = _env(enforced="true", access=binding)
        env.TIER_POLICY = json.dumps(raw)
        env.X402_ENABLED = enabled
        env.HUMAN_GATE_ENABLED = "true"
        env.VISIT_GATE_ENABLED = "true"
        ledger = credits.MemoryLedger()
        if ledger_bound:
            env.CREDITS = ledger
        worker = entry.Default()
        worker.env = env
        produced = []

        async def decide(*args, **kwargs):
            produced.append("decide")
            return 200, {"endpoint": "decide", "result": [{"model": "fixture/live"}]}

        worker._decide = decide
        original_gate = entry.access.gate
        outcomes = []

        async def gate(**kwargs):
            outcome = await original_gate(**{**kwargs, "now": NOW})
            outcomes.append(outcome)
            return outcome

        monkeypatch.setattr(entry.access, "gate", gate)

        def call(*, key=SECRET, path="/v1/decide", method="POST"):
            request = Request(path, {"task": "general"}, key=key)
            request.method = method
            return asyncio.run(worker.fetch(request))

        return SimpleNamespace(
            call=call, binding=binding, kv=kv, ledger=ledger, env=env,
            outcomes=outcomes, produced=produced,
        )

    return build


@pytest.mark.parametrize("enabled", ["false", "true"])
@pytest.mark.parametrize("ledger_bound", [False, True])
@pytest.mark.parametrize("tier", ["friends", "invited"])
def test_friends_decide_needs_no_credits_and_records_usage(
    friends_worker, enabled, ledger_bound, tier,
):
    worker = friends_worker(enabled=enabled, ledger_bound=ledger_bound, tier=tier)
    response = worker.call()

    assert response.status == 200
    assert response.json() == {
        "endpoint": "decide", "result": [{"model": "fixture/live"}],
    }
    assert response.headers["x-modelspec-tier"] == tier
    assert worker.produced == ["decide"]
    assert len(worker.outcomes) == 1
    outcome = worker.outcomes[0]
    assert outcome.trace == ("key.lookup", "limits.consume", "serve.live")
    assert outcome.meter.window("daily").used == 1
    assert outcome.meter.window("daily").limit is None
    assert outcome.meter.window("burst").used == 1
    assert outcome.meter.window("burst").limit == 60
    daily = access_limits.counter_name(access_keys.key_id(SECRET), "daily", "2026-10-14")
    assert worker.binding.values[daily] == "1"


def test_friends_has_no_daily_cap_but_enforces_the_paid_burst(friends_worker):
    worker = friends_worker()
    fingerprint = access_keys.key_id(SECRET)
    daily = access_limits.counter_name(fingerprint, "daily", "2026-10-14")
    burst = access_limits.counter_name(fingerprint, "burst", "2026-10-14T12:30")
    worker.binding.values.update({daily: "10000", burst: "59"})

    admitted = worker.call()
    refused = worker.call()

    assert admitted.status == 200
    assert refused.status == 429
    error = refused.json()["error"]
    assert error["code"] == "rate_limited"
    assert error["scope"] == "burst"
    assert error["limit"] == error["used"] == 60
    assert worker.binding.values[daily] == "10001"
    assert worker.binding.values[burst] == "60"
    assert worker.produced == ["decide"]


@pytest.mark.parametrize("method", ["GET", "HEAD"])
def test_friends_catalog_read_is_credit_exempt_and_still_metered(
    entry, friends_worker, monkeypatch, method,
):
    worker = friends_worker()
    monkeypatch.setattr(entry, "bundled_data", object(), raising=False)
    monkeypatch.setattr(entry, "_bundled_vocabulary_text", '{"models":{}}', raising=False)

    response = worker.call(path="/v1/vocabulary", method=method)

    assert response.status == 200
    assert worker.outcomes[0].meter.window("daily").used == 1
    assert worker.outcomes[0].meter.window("burst").limit == 60
    assert response.body == (None if method == "HEAD" else '{"models":{}}')


def test_operator_revoke_refuses_the_friends_key(friends_worker, monkeypatch, capsys):
    worker = friends_worker()
    commands = []

    def run(command, **kwargs):
        commands.append(command)
        name = command[5]
        if command[4] == "get":
            return subprocess.CompletedProcess(command, 0, worker.binding.values[name], "")
        worker.binding.values[name] = command[command.index("--value") + 1]
        return subprocess.CompletedProcess(command, 0, "", "")

    monkeypatch.setattr(revoke_api_key.subprocess, "run", run)
    result = revoke_api_key.main([access_keys.fingerprint(SECRET), "--put"])
    response = worker.call()

    output = capsys.readouterr()
    assert result == 0
    assert response.status == 403
    assert response.json()["error"]["code"] == "key_revoked"
    assert [command[4] for command in commands] == ["get", "put"]
    assert SECRET not in output.out + output.err + " ".join(sum(commands, []))
    assert worker.produced == []
    assert not any(name.startswith("count:") for name in worker.binding.values)


@pytest.mark.parametrize("key", [None, "friends", "live_unknown_friends"])
def test_friends_does_not_open_keyless_or_unknown_key_access(friends_worker, key):
    worker = friends_worker()
    response = worker.call(key=key)

    assert response.status == 401
    expected = "missing_api_key" if key is None else "invalid_api_key"
    assert response.json()["error"]["code"] == expected
    assert worker.produced == []
    assert not any(name.startswith("count:") for name in worker.binding.values)
