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
    if payload is not None:
        request._body = json.dumps(payload)
    return human_gate.admit(request, environment, {ORIGIN}, verify)


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
    state = json.loads(obj.ctx.storage.sql.exec("SELECT v FROM human_state").toArray()[0]["v"])
    assert state == {"day": 0, "count": 1, "events": [10000]}
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
    environment = _entry_env(**vars(env()))
    worker = _decision_worker(entry, environment)
    response = asyncio.run(worker.fetch(_Req("/v1/human-status", method="GET", headers={"origin": ORIGIN, "CF-Connecting-IP": IP})))
    assert response.status == 200
    assert response.json() == {"enabled": True, "remaining": 20}
    obj = next(iter(environment.HUMAN_GATE.objects.values()))
    assert obj.ctx.storage.sql.exec("SELECT name FROM sqlite_master WHERE type = 'table'").toArray() == []
    assert obj.ctx.storage.alarm_at is None


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


@pytest.mark.parametrize("times", [
    [0, 61, 123, 187, 252, 318],
    [0, 60, 125, 185, 255, 317, 385, 446, 512, 576],
])
def test_irregular_distinct_specs_are_admitted(monkeypatch, times):
    now = [10000]
    monkeypatch.setattr(human_gate_do.time, "time", lambda: now[0])
    e = env()
    for index, offset in enumerate(times):
        now[0] = 10000 + offset
        out = asyncio.run(admit(req(str(index)), e, {"task": str(index)}))
        assert out[0] == 200
        assert out[3][human_gate.REMAINING_HEADER] == str(19 - index)
    # Further distinct edits remain subject to the burst and daily caps.
    for i in range(2):
        assert asyncio.run(admit(req(), e, {"task": f"burst-{i}"}))[0] == 200
    assert asyncio.run(admit(req(), e, {"task": "burst-refused"}))[1] == "human_burst_limit"
    now[0] += 601
    for i in range(20 - len(times) - 2):
        assert asyncio.run(admit(req(), e, {"task": f"later-{i}"}))[0] == 200
        now[0] += 601
    assert asyncio.run(admit(req(), e))[1] == "human_day_limit"


def test_ipv6_same_network_shares_allowance_other_network_does_not(monkeypatch):
    monkeypatch.setattr(human_gate_do.time, "time", lambda: 10000)
    e = env()
    def request(address):
        return _Req("/v1/decide", {"spec_version": 1}, headers={
            "origin": ORIGIN, "CF-Connecting-IP": address, human_gate.TOKEN_HEADER: "token"})
    assert asyncio.run(admit(request("2001:db8:abcd:1234::1"), e))[3][human_gate.REMAINING_HEADER] == "19"
    assert asyncio.run(admit(request("2001:db8:abcd:1234:ffff::2"), e))[3][human_gate.REMAINING_HEADER] == "18"
    assert asyncio.run(admit(request("2001:db8:abcd:1235::1"), e))[3][human_gate.REMAINING_HEADER] == "19"
    assert len(e.HUMAN_GATE.objects) == 2
    # MODEL-241 still distinguishes individual IPv6 addresses.
    assert human_gate.visitor.visitor_id_for(request("2001:db8:abcd:1234::1"), e) != human_gate.visitor.visitor_id_for(request("2001:db8:abcd:1234:ffff::2"), e)
    assert human_gate.identity_for(req(), e) == human_gate.visitor.visitor_id_for(req(), e)


def test_gate_refusal_uses_transport_route_without_decision_error_builder(entry, monkeypatch):
    worker = _decision_worker(entry, _entry_env(**vars(env())))
    decider = entry._decide_service()
    def never(*args, **kwargs):
        pytest.fail("access refusal reached decision-contract error builder")
    monkeypatch.setattr(decider, "error_response", never)
    response = asyncio.run(worker.fetch(req(token="")))
    assert response.status == 403
    assert response.json() == {
        "contract_version": decider.contract.CONTRACT_VERSION,
        "endpoint": "decide", "snapshot": None,
        "error": {"code": "human_challenge_required", "message": "Complete the human verification before each lookup."},
    }


@pytest.mark.parametrize("timestamps,now,reason", [
    ([10000, 10001, 10002], 10003, "burst"),
    ([10000, 10070, 10140, 10210], 10280, "sweep"),
    ([9399, 10000, 10061], 10124, ""),
])
def test_legacy_events_load_and_write_only_timestamps(monkeypatch, timestamps, now, reason):
    monkeypatch.setattr(human_gate_do.time, "time", lambda: now)
    storage = Storage()
    storage.sql.exec("CREATE TABLE human_state (k TEXT PRIMARY KEY, v TEXT)")
    old_state = {"day": 0, "count": len(timestamps),
                 "events": [[stamp, "legacy-spec-fingerprint"] for stamp in timestamps]}
    storage.sql.exec("INSERT INTO human_state VALUES ('state', ?)", json.dumps(old_state))
    obj = human_gate_do.HumanGateObject(SimpleNamespace(storage=storage), None)
    assert asyncio.run(obj.remaining()) == 20 - len(timestamps)
    outcome = asyncio.run(obj.take())
    assert outcome["reason"] == reason
    state = json.loads(storage.sql.exec("SELECT v FROM human_state").toArray()[0]["v"])
    expected = [stamp for stamp in timestamps if now - stamp < 600]
    if not reason:
        expected.append(now)
    assert state["events"] == expected
    assert state["count"] == len(timestamps) + (not reason)
    assert "legacy-spec-fingerprint" not in json.dumps(state)
    # A new instance must also accept the timestamp-only rows just written.
    recreated = human_gate_do.HumanGateObject(obj.ctx, None)
    assert asyncio.run(recreated.take())["reason"] == reason


INTENT = "AAAAAAAAAAAAAAAAAAAAAA"
PRIMARY = {
    "spec_version": 1, "optimize": {"weights": {"software_engineering": 1}},
    "where": ["model.context_window >= 32000", "model.weights_openness = open_weights"],
    "access": "own_software", "task_tokens": {"input": 1000, "output": 500},
    "explain": "summary", "limit": 20,
}


def intent_req(intent=INTENT, ip=IP, token="token", spec=None):
    return _Req("/v1/decide", PRIMARY if spec is None else spec, headers={
        "origin": ORIGIN, "CF-Connecting-IP": ip,
        human_gate.TOKEN_HEADER: token, human_gate.INTENT_HEADER: intent})


def test_intent_continuations_share_one_verified_admission(monkeypatch):
    now = [10000]
    monkeypatch.setattr(human_gate_do.time, "time", lambda: now[0])
    e = env()
    calls = []
    async def once(secret, token):
        calls.append(token)
        return await verified(secret, token) if len(calls) == 1 else {"success": False}
    async def action():
        first = await admit(intent_req(), e, verify=once)
        rest = []
        for _ in range(30):
            now[0] += .15
            rest.append(await admit(intent_req(token=""), e, verify=once))
        return [first, *rest]
    outcomes = asyncio.run(action())
    assert all(out[0] == 200 for out in outcomes)
    assert all(out[3][human_gate.REMAINING_HEADER] == "19" for out in outcomes)
    assert calls == ["token"]
    obj = next(iter(e.HUMAN_GATE.objects.values()))
    e.HUMAN_GATE.objects[next(iter(e.HUMAN_GATE.objects))] = human_gate_do.HumanGateObject(obj.ctx, None)
    now[0] += .15
    assert asyncio.run(admit(intent_req(token=""), e))[0] == 200
    assert asyncio.run(admit(intent_req(), e))[:2] == (429, "human_intent_limit")


def test_fourth_distinct_intent_is_refused(monkeypatch):
    monkeypatch.setattr(human_gate_do.time, "time", lambda: 10000)
    e = env()
    outcomes = [asyncio.run(admit(intent_req(chr(65 + i) * 21 + "A"), e)) for i in range(4)]
    assert [out[0] for out in outcomes] == [200, 200, 200, 429]
    assert outcomes[-1][1] == "human_burst_limit"
    # Existing admission is free even when new actions are blocked.
    assert asyncio.run(admit(intent_req(), e))[3][human_gate.REMAINING_HEADER] == "17"


def test_twenty_first_distinct_intent_is_refused(monkeypatch):
    now = [10000]
    monkeypatch.setattr(human_gate_do.time, "time", lambda: now[0])
    e = env()
    for i in range(20):
        now[0] += 601
        assert asyncio.run(admit(intent_req(chr(65 + i) * 21 + "A"), e))[0] == 200
    now[0] += 601
    assert asyncio.run(admit(intent_req("Z" * 21 + "A"), e))[:2] == (429, "human_day_limit")


def test_intent_expires_at_sixty_seconds_and_cannot_be_readmitted(monkeypatch):
    now = [10000]
    monkeypatch.setattr(human_gate_do.time, "time", lambda: now[0])
    e = env()
    assert asyncio.run(admit(intent_req(), e))[0] == 200
    now[0] += 59.99
    assert asyncio.run(admit(intent_req(), e))[0] == 200
    now[0] += .01
    assert asyncio.run(admit(intent_req(), e))[:2] == (429, "human_intent_limit")
    now[0] += 601
    assert asyncio.run(admit(intent_req(), e))[:2] == (429, "human_intent_limit")


@pytest.mark.parametrize("intent", ["", "short", "A" * 22 + "=", "!" * 22, "A" * 21 + "B"])
def test_malformed_intent_meters_every_request(monkeypatch, intent):
    monkeypatch.setattr(human_gate_do.time, "time", lambda: 10000)
    e = env()
    assert [asyncio.run(admit(intent_req(intent), e))[0] for _ in range(4)] == [200, 200, 200, 429]


def test_intent_is_scoped_to_visitor_and_requires_verification(monkeypatch):
    monkeypatch.setattr(human_gate_do.time, "time", lambda: 10000)
    e = env()
    assert asyncio.run(admit(intent_req(), e))[0] == 200
    assert asyncio.run(admit(intent_req(ip="203.0.113.10", token=""), e))[0] == 403
    assert asyncio.run(admit(intent_req(ip="203.0.113.10"), e))[3][human_gate.REMAINING_HEADER] == "19"
    assert len(e.HUMAN_GATE.objects) == 2


def test_even_intervals_count_distinct_intents_only(monkeypatch):
    now = [10000]
    monkeypatch.setattr(human_gate_do.time, "time", lambda: now[0])
    e = env()
    for i in range(5):
        now[0] = 10000 + i * 70
        intent = chr(65 + i) * 21 + "A"
        out = asyncio.run(admit(intent_req(intent), e))
        if i < 4:
            assert out[0] == 200
            for _ in range(10):
                now[0] += .15
                assert asyncio.run(admit(intent_req(intent), e))[0] == 200
    assert out[:2] == (429, "human_sweep_limit")


def test_cors_accepts_intent_header(entry):
    worker = _decision_worker(entry, _entry_env(**vars(env())))
    response = asyncio.run(worker.fetch(_Req("/v1/decide", method="OPTIONS", headers={"origin": ORIGIN})))
    assert human_gate.INTENT_HEADER in response.headers["access-control-allow-headers"]


PLOT = {
    **PRIMARY, "where": [], "explain": "full", "limit": 500,
    "optimize": {"weights": {"-offering.cost_per_task": .5, "software_engineering": .5}},
    "capabilities": {"software_engineering": "preferred"},
}


@pytest.mark.parametrize("spec", [
    {**PRIMARY, "explain": "full", "limit": 500},
    {**PRIMARY, "where": [*PRIMARY["where"], "offering.price.input <= 2"], "explain": "none", "limit": 500},
    {**PRIMARY, "where": PRIMARY["where"][:1]},
    PLOT,
    {**PRIMARY, "estate": {"providers": ["openai"], "plans": ["claude-pro"], "devices": ["apple-m4-max"]}},
    # Defaults, condition syntax/order, access spelling and numeric spelling
    # are canonical, while objective and condition semantics stay fixed.
    {**PRIMARY, "where": ['model.weights_openness = "open_weights"',
                           {"facet": "model.context_window", "op": ">=", "value": 32000.0}],
     "access": {"kind": "own_software"}, "unknowns": "default", "snapshot": "latest"},
])
def test_each_permitted_derivation_is_admitted(monkeypatch, spec):
    monkeypatch.setattr(human_gate_do.time, "time", lambda: 10000)
    e = env()
    assert asyncio.run(admit(intent_req(), e))[0] == 200
    assert asyncio.run(admit(intent_req(token="", spec=spec), e))[0] == 200
    obj = next(iter(e.HUMAN_GATE.objects.values()))
    assert asyncio.run(obj.remaining()) == 19


@pytest.mark.parametrize("spec", [
    {**PRIMARY, "optimize": {"max": "general_reasoning"}},
    {**PRIMARY, "where": ["offering.price.input <= 1"]},
    {**PRIMARY, "where": []},
    {**PRIMARY, "where": [*PRIMARY["where"], "offering.price.input <= 1", "offering.price.output <= 2"]},
    {**PRIMARY, "where": [*PRIMARY["where"], "all(offering.price.input <= 1; offering.price.output <= 2)"]},
    {**PRIMARY, "access": "chat_app"},
    {**PRIMARY, "task_tokens": {"input": 9999, "output": 999}},
    {**PRIMARY, "capabilities": {"general_reasoning": "required"}},
    {**PRIMARY, "exclude_benchmarks": ["swe_bench_pro"]},
    {**PRIMARY, "task_type": "migration"},
    {**PRIMARY, "snapshot": "snap_unrelated"},
    {**PRIMARY, "profile": "profile:other"},
    {**PRIMARY, "save_as": "other"},
    {**PRIMARY, "estate": {"providers": ["openai"], "exhausted": ["openai"]}},
    {**PLOT, "optimize": {"weights": {"-offering.cost_per_task": .2, "software_engineering": .8}}},
    {**PLOT, "capabilities": {"general_reasoning": "preferred"}},
    {**PLOT, "capabilities": {"software_engineering": "required"}},
    {**PLOT, "estate": {"providers": ["openai"]}},
    {"spec_version": 1},
])
def test_unrelated_or_broader_derivations_are_refused_without_siteverify(monkeypatch, spec):
    monkeypatch.setattr(human_gate_do.time, "time", lambda: 10000)
    e = env()
    assert asyncio.run(admit(intent_req(), e))[0] == 200
    async def never(*args):
        pytest.fail("known intent refusal must not fall back to Siteverify")
    assert asyncio.run(admit(intent_req(spec=spec), e, verify=never))[:2] == (429, "human_intent_limit")
    assert asyncio.run(admit(intent_req(token=""), e))[0] == 200


def test_auxiliaries_cannot_chain_or_sweep_plot_and_estate_variants(monkeypatch):
    monkeypatch.setattr(human_gate_do.time, "time", lambda: 10000)
    e = env()
    assert asyncio.run(admit(intent_req(), e))[0] == 200
    first_probe = {**PRIMARY, "where": [*PRIMARY["where"], "offering.price.input <= 1"]}
    assert asyncio.run(admit(intent_req(spec=first_probe), e))[0] == 200
    chained = {**first_probe, "where": [*first_probe["where"], "offering.price.output <= 1"]}
    assert asyncio.run(admit(intent_req(spec=chained), e))[1] == "human_intent_limit"
    assert asyncio.run(admit(intent_req(spec=PLOT), e))[0] == 200
    assert asyncio.run(admit(intent_req(spec={**PLOT, "explain": "full"}), e))[0] == 200
    other_plot = {**PLOT, "optimize": {"weights": {"general_reasoning": 1}}, "capabilities": {"general_reasoning": "preferred"}}
    assert asyncio.run(admit(intent_req(spec=other_plot), e))[1] == "human_intent_limit"
    estate = {**PRIMARY, "estate": {"providers": ["openai", "anthropic"]}}
    assert asyncio.run(admit(intent_req(spec=estate), e))[0] == 200
    assert asyncio.run(admit(intent_req(spec={**estate, "estate": {"providers": ["anthropic", "openai"]}}), e))[0] == 200
    assert asyncio.run(admit(intent_req(spec={**estate, "estate": {"providers": ["google"]}}), e))[1] == "human_intent_limit"


def test_continuation_burst_is_atomic_persistent_and_recovers(monkeypatch):
    now = [10000]
    monkeypatch.setattr(human_gate_do.time, "time", lambda: now[0])
    e = env()
    assert asyncio.run(admit(intent_req(), e))[0] == 200
    async def race():
        return await asyncio.gather(*(admit(intent_req(token=""), e) for _ in range(31)))
    outcomes = asyncio.run(race())
    assert sum(out[0] == 200 for out in outcomes) == 7
    assert sum(out[1] == "human_intent_limit" for out in outcomes) == 24
    identity, obj = next(iter(e.HUMAN_GATE.objects.items()))
    e.HUMAN_GATE.objects[identity] = human_gate_do.HumanGateObject(obj.ctx, None)
    now[0] += .999
    assert asyncio.run(admit(intent_req(token=""), e))[1] == "human_intent_limit"
    now[0] += .001
    assert asyncio.run(admit(intent_req(token=""), e))[0] == 200


def test_legacy_unbound_intent_fails_closed(monkeypatch):
    monkeypatch.setattr(human_gate_do.time, "time", lambda: 10000)
    e = env()
    assert asyncio.run(admit(intent_req(), e))[0] == 200
    obj = next(iter(e.HUMAN_GATE.objects.values()))
    state = {"day": 0, "count": 1, "events": [10000],
             "intents": {INTENT: {"first": 10000, "requests": 1}}}
    obj.ctx.storage.sql.exec("INSERT OR REPLACE INTO human_state VALUES ('state', ?)", json.dumps(state))
    assert asyncio.run(admit(intent_req(), e))[:2] == (429, "human_intent_limit")


@pytest.mark.parametrize("offsets,expected", [
    ([0, 1, 2, 3], "human_burst_limit"),
    ([0, 70, 140, 210, 280], "human_sweep_limit"),
    ([i * 601 for i in range(21)], "human_day_limit"),
])
def test_sweeper_cannot_vary_questions_under_one_intent_to_bypass_meter(monkeypatch, offsets, expected):
    now = [10000]
    monkeypatch.setattr(human_gate_do.time, "time", lambda: now[0])
    e = env()
    for i, offset in enumerate(offsets):
        now[0] = 10000 + offset
        spec = {**PRIMARY, "task_tokens": {"input": 1000 + i, "output": 500}}
        if i:
            assert asyncio.run(admit(intent_req(token="", spec=spec), e))[1] == "human_intent_limit"
        out = asyncio.run(admit(intent_req(chr(65 + i) * 21 + "A", spec=spec), e))
    assert out[:2] == (429, expected)


def test_worker_uses_same_payload_for_gate_and_producer(entry, monkeypatch):
    monkeypatch.setattr(human_gate_do.time, "time", lambda: 10000)
    monkeypatch.setattr(entry, "_verify_turnstile", verified)
    worker = _decision_worker(entry, _entry_env(**vars(env())))
    assert asyncio.run(worker.fetch(intent_req())).status == 200
    async def never(*args):
        pytest.fail("unrelated continuation reached producer")
    worker._decide = never
    response = asyncio.run(worker.fetch(intent_req(spec={**PRIMARY, "access": "chat_app"})))
    assert response.status == 429
    assert response.json()["error"]["code"] == "human_intent_limit"
