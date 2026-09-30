"""MODEL-248: actual SQLite admission, mocked external Turnstile only."""
import asyncio
import hashlib
import json
import sqlite3
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "api/worker/src"))
import human_gate
import human_gate_do
from tests.test_x402 import entry, _entry_env, _Req, _decision_worker  # noqa: F401

ORIGIN = "https://modelspec.dev"
KEY = "fixture-visitor-key-0123456789"
IP = "203.0.113.9"


class Sql:
    def __init__(self):
        self.db = sqlite3.connect(":memory:")
        self.db.row_factory = sqlite3.Row

    def exec(self, query, *params):
        rows = [dict(row) for row in self.db.execute(query, params).fetchall()]
        return SimpleNamespace(toArray=lambda: rows)


class Storage:
    def __init__(self):
        self.sql = Sql()
        self.alarm_at = None

    async def setAlarm(self, at):
        self.alarm_at = at
        await asyncio.sleep(0)

    async def deleteAll(self):
        self.sql.exec("DROP TABLE IF EXISTS human_state")


class Namespace:
    def __init__(self):
        self.objects = {}

    def idFromName(self, name):
        return name

    def get(self, name):
        if name not in self.objects:
            self.objects[name] = human_gate_do.HumanGateObject(SimpleNamespace(storage=Storage()), None)
        return self.objects[name]


def env(**overrides):
    return SimpleNamespace(**{"HUMAN_GATE_ENABLED": "true", "VISITOR_HMAC_KEY": KEY,
                              "TURNSTILE_SECRET": "fixture-secret", "HUMAN_GATE": Namespace(), **overrides})


def req(token="token", origin=ORIGIN):
    return _Req("/v1/decide", {"spec_version": 1}, headers={
        "origin": origin, "CF-Connecting-IP": IP, human_gate.TOKEN_HEADER: token})


async def verified(secret, token):
    return {"success": True, "hostname": "modelspec.dev", "action": "decide"}


def admit(request, environment, payload=None, verify=verified):
    return human_gate.admit(request, environment, payload or {"spec_version": 1}, {ORIGIN}, verify)


def test_scripted_loop_is_refused_on_fourth_request(monkeypatch):
    monkeypatch.setattr(human_gate_do.time, "time", lambda: 10000)
    e = env()
    outcomes = [asyncio.run(admit(req(str(i)), e)) for i in range(6)]
    assert [o[0] for o in outcomes] == [200, 200, 200, 429, 429, 429]
    assert outcomes[3][1] == "human_burst_limit"
    assert outcomes[3][3][human_gate.REMAINING_HEADER] == "17"


def test_concurrent_admission_never_exceeds_three(monkeypatch):
    monkeypatch.setattr(human_gate_do.time, "time", lambda: 10000)
    e = env()
    async def race():
        return await asyncio.gather(*(admit(req(str(i)), e) for i in range(30)))
    outcomes = asyncio.run(race())
    assert sum(o[0] == 200 for o in outcomes) == 3
    assert sum(o[0] == 429 for o in outcomes) == 27
    obj = next(iter(e.HUMAN_GATE.objects.values()))
    assert asyncio.run(obj.remaining()) == 17
    # Recreate the object against the same storage, so this proves persistence.
    recreated = human_gate_do.HumanGateObject(obj.ctx, None)
    assert asyncio.run(recreated.remaining()) == 17


def test_twenty_day_cap_and_utc_reset(monkeypatch):
    now = [10000]
    monkeypatch.setattr(human_gate_do.time, "time", lambda: now[0])
    e = env()
    for i in range(20):
        now[0] = 10000 + i * 601
        assert asyncio.run(admit(req(str(i)), e))[0] == 200
    now[0] += 601
    out = asyncio.run(admit(req("21"), e))
    assert out[:2] == (429, "human_day_limit")
    assert out[3][human_gate.REMAINING_HEADER] == "0"
    now[0] = 86400
    assert asyncio.run(admit(req("next-day"), e))[3][human_gate.REMAINING_HEADER] == "19"


@pytest.mark.parametrize("times,payloads", [
    ([0, 61, 123, 187, 252, 318], [str(i) for i in range(6)]),
    ([0, 70, 140, 210, 280], ["same"] * 5),
])
def test_sweeps_and_even_intervals_trigger_sticky_refusal(monkeypatch, times, payloads):
    now = [10000]
    monkeypatch.setattr(human_gate_do.time, "time", lambda: now[0])
    e = env()
    for offset, payload in zip(times, payloads):
        now[0] = 10000 + offset
        out = asyncio.run(admit(req(), e, {"task": payload}))
    assert out[:2] == (429, "human_sweep_limit")
    now[0] += 23
    assert asyncio.run(admit(req(), e))[1] == "human_sweep_limit"
    now[0] += 601
    assert asyncio.run(admit(req(), e))[0] == 200


@pytest.mark.parametrize("result", [
    {"success": False, "error-codes": ["timeout-or-duplicate"]},
    {"success": True, "hostname": "evil.test", "action": "decide"},
    {"success": True, "hostname": "modelspec.dev", "action": "login"},
    {"success": "true", "hostname": "modelspec.dev", "action": "decide"},
    None,
])
def test_invalid_turnstile_never_consumes_or_produces(result):
    e = env()
    async def verify(secret, token):
        return result
    assert asyncio.run(admit(req(), e, verify=verify))[0] == 403
    assert asyncio.run(next(iter(e.HUMAN_GATE.objects.values())).remaining()) == 20


def test_tokens_are_single_use_by_siteverify():
    used = set()
    async def verify(secret, token):
        if token in used:
            return {"success": False, "error-codes": ["timeout-or-duplicate"]}
        used.add(token)
        return await verified(secret, token)
    e = env()
    assert asyncio.run(admit(req(), e, verify=verify))[0] == 200
    assert asyncio.run(admit(req(), e, verify=verify))[0] == 403


@pytest.mark.parametrize("overrides", [{"TURNSTILE_SECRET": None}, {"VISITOR_HMAC_KEY": None}, {"HUMAN_GATE": None}])
def test_missing_secrets_or_binding_fail_closed(overrides):
    assert asyncio.run(admit(req(), env(**overrides)))[0] == 503


def test_verifier_outage_is_unavailable():
    async def outage(secret, token):
        raise OSError("fixture outage")
    assert asyncio.run(admit(req(), env(), verify=outage))[0] == 503


def test_no_ip_unkeyed_id_token_or_spec_is_stored(monkeypatch):
    monkeypatch.setattr(human_gate_do.time, "time", lambda: 10000)
    e = env()
    assert asyncio.run(admit(req("private-token"), e, {"task": "private-task"}))[0] == 200
    obj = next(iter(e.HUMAN_GATE.objects.values()))
    blob = json.dumps(list(e.HUMAN_GATE.objects)) + json.dumps(obj.ctx.storage.sql.exec("SELECT * FROM human_state").toArray())
    for raw in (IP, hashlib.sha256(IP.encode()).hexdigest(), "private-task", "private-token", KEY):
        assert raw not in blob
    asyncio.run(obj.alarm())
    assert asyncio.run(obj.remaining()) == 20


def test_worker_gate_runs_before_decision_and_bypasses_old_free_meter(entry, monkeypatch):
    monkeypatch.setattr(human_gate_do.time, "time", lambda: 10000)
    environment = _entry_env(**vars(env()))
    worker = _decision_worker(entry, environment)
    monkeypatch.setattr(entry, "_verify_turnstile", verified)
    responses = [asyncio.run(worker.fetch(req(str(i)))) for i in range(4)]
    assert [r.status for r in responses] == [200, 200, 200, 429]
    assert responses[0].headers[human_gate.REMAINING_HEADER] == "19"
    assert "x-modelspec-decisions-remaining" in responses[0].headers["access-control-expose-headers"]
    assert not environment.ACCESS.store.data
    response = asyncio.run(worker.fetch(req(origin="https://evil.test")))
    assert response.status == 402  # existing paid per-call x402 path


def test_worker_missing_secret_never_calls_producer(entry):
    worker = _decision_worker(entry, _entry_env(**vars(env(TURNSTILE_SECRET=None))))
    async def never(*args):
        pytest.fail("refused request reached decision producer")
    worker._decide = never
    response = asyncio.run(worker.fetch(req()))
    assert response.status == 503
    assert "temporarily unavailable" in response.json()["error"]["message"]


def test_worker_siteverify_posts_only_secret_and_token(entry, monkeypatch):
    calls = []
    async def http(url, **options):
        calls.append((url, options))
        async def text():
            return json.dumps(await verified("", ""))
        return SimpleNamespace(status=200, text=text)
    monkeypatch.setattr(entry, "_stripe_http", http)
    assert asyncio.run(entry._verify_turnstile("fixture-secret", "fixture-token"))["success"] is True
    assert calls[0][0] == human_gate.SITEVERIFY
    assert json.loads(calls[0][1]["body"]) == {"secret": "fixture-secret", "response": "fixture-token"}


def test_status_reads_current_allowance_without_consuming(entry):
    worker = _decision_worker(entry, _entry_env(**vars(env())))
    response = asyncio.run(worker.fetch(_Req("/v1/human-status", method="GET", headers={"origin": ORIGIN, "CF-Connecting-IP": IP})))
    assert response.status == 200
    assert response.json() == {"enabled": True, "remaining": 20}


def test_rolling_burst_recovers_at_sixty_seconds(monkeypatch):
    now = [10000]
    monkeypatch.setattr(human_gate_do.time, "time", lambda: now[0])
    e = env()
    for i in range(3):
        assert asyncio.run(admit(req(str(i)), e))[0] == 200
    now[0] += 59
    assert asyncio.run(admit(req("refused"), e))[1] == "human_burst_limit"
    now[0] += 1
    assert asyncio.run(admit(req("fresh"), e))[0] == 200


def test_missing_challenge_and_other_origins_cannot_use_free_producer(entry):
    worker = _decision_worker(entry, _entry_env(X402_ENABLED="false", **vars(env())))
    async def never(*args):
        pytest.fail("machine or unverified request reached free producer")
    worker._decide = never
    assert asyncio.run(worker.fetch(req(token=""))).status == 403
    assert asyncio.run(worker.fetch(req(origin="https://evil.test"))).status == 401
    assert asyncio.run(worker.fetch(req(origin=""))).status == 401


@pytest.mark.parametrize("funded", [False, True])
def test_keyed_decisions_need_paid_credits_and_do_not_need_human_secrets(entry, funded):
    from datetime import UTC, datetime
    import access_config
    import access_keys
    import x402

    key = "live_human_gate_test"
    environment = _entry_env(X402_ENABLED="false", **vars(env(TURNSTILE_SECRET=None)))
    asyncio.run(access_keys.issue(environment.ACCESS, tier="free", owner="fixture",
                                 now=datetime.now(UTC), policy=access_config.load_policy(environment),
                                 secret=key))
    holder = x402.holder_from_key(key)
    if funded:
        asyncio.run(environment.CREDITS.set_monthly(holder, 5, "invoice-fixture", "fixture"))
    request = _Req("/v1/decide", {"spec_version": 1}, headers={
        "origin": ORIGIN, "authorization": f"Bearer {key}", "CF-Connecting-IP": IP})
    worker = _decision_worker(entry, environment)
    if not funded:
        async def never(*args):
            pytest.fail("unfunded key bypassed the human gate")
        worker._decide = never
    response = asyncio.run(worker.fetch(request))
    assert response.status == (200 if funded else 402)
    assert not environment.HUMAN_GATE.objects
    if funded:
        assert asyncio.run(environment.CREDITS.balance(holder)).available == 4
    else:
        assert response.json()["error"]["code"] == "payment_required"
