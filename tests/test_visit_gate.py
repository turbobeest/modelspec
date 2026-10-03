"""MODEL-292: real SQLite metering and Worker routing, external verifier stubbed."""
import asyncio
import json
from types import SimpleNamespace
from pathlib import Path

import pytest

from tests.test_human_gate import (Storage, ORIGIN, KEY, IP, PRIMARY, PLOT, INTENT,
                                  human_gate_do, verified)
from tests.test_x402 import entry, _Req, _entry_env, _decision_worker  # noqa: F401
import visit_token
from pipeline.worker_flags import production_vars


def environment(**overrides):
    values = {key: value for key, value in production_vars(Path(__file__).resolve().parents[1]).items() if key.startswith("VISIT_")}
    env = _entry_env(**{**values, "VISIT_GATE_ENABLED": "true", "ACCESS_ENFORCED": "true",
                       "HUMAN_GATE_ENABLED": "true", "VISITOR_HMAC_KEY": KEY,
                       "VISIT_TOKEN_HMAC_KEY": "fixture-visit-signing-secret-0123456789",
                       "TURNSTILE_SECRET": "fixture-secret", **overrides})
    class Namespace:
        objects = {}

        def idFromName(self, name):
            return name

        def get(self, name):
            if name not in self.objects:
                self.objects[name] = human_gate_do.HumanGateObject(SimpleNamespace(storage=Storage()), env)
            return self.objects[name]
    env.HUMAN_GATE = Namespace()
    return env


def request(path="/v1/decide", token=None, key=None, origin=ORIGIN, ip=IP, **headers):
    return _Req(path, PRIMARY, method="GET" if path == "/v1/vocabulary" else "POST", headers={
        "origin": origin, "CF-Connecting-IP": ip, **headers,
        **({visit_token.HEADER: token} if token else {}),
        **({"authorization": f"Bearer {key}"} if key else {}),
    })


def mint(env, now=None):
    identity, origin, secret = visit_token.credential(request(), env, {ORIGIN})
    return visit_token.issue(identity, origin, secret, now)[0]


def test_issue_and_expiry_boundary():
    secret = b"new-signing-secret"
    token, expiry = visit_token.issue("visitor:one", ORIGIN, secret, 1000)
    assert expiry == 2800
    assert visit_token.verify(token, "visitor:one", ORIGIN, secret, 2799) is None
    assert visit_token.verify(token, "visitor:one", ORIGIN, secret, 2800) == "visit_token_expired"
    assert visit_token.verify(token, "visitor:one", ORIGIN, secret, 999) == "visit_token_invalid"


@pytest.mark.parametrize("identity,origin,secret", [
    ("visitor:two", ORIGIN, b"new-signing-secret"),
    ("visitor:one", "https://www.modelspec.dev", b"new-signing-secret"),
    ("visitor:one", ORIGIN, b"different-secret"),
])
def test_binding(identity, origin, secret):
    token, _ = visit_token.issue("visitor:one", ORIGIN, b"new-signing-secret", 1000)
    assert visit_token.verify(token, identity, origin, secret, 1001) == "visit_token_invalid"


@pytest.mark.parametrize("change", [lambda value: value + "x", lambda value: "X" + value[1:],
                                   lambda value: "garbage", lambda value: "", lambda value: "é." + "0" * 64])
def test_tampered_and_malformed_tokens(change):
    token, _ = visit_token.issue("visitor:one", ORIGIN, b"new-signing-secret", 1000)
    assert visit_token.verify(change(token), "visitor:one", ORIGIN, b"new-signing-secret", 1001) == "visit_token_invalid"


@pytest.mark.parametrize("result", [None, {"success": False}, {"success": "true"},
    {"success": True, "hostname": "evil.test", "action": "decide"},
    {"success": True, "hostname": "modelspec.dev", "action": "other"}])
def test_exchange_validates_all_siteverify_claims(result):
    async def verifier(secret, token):
        return result
    out = asyncio.run(visit_token.exchange(request(**{"x-modelspec-turnstile": "single-use"}), environment(), {ORIGIN}, verifier))
    assert out[0] == 403


def test_exchange_and_replay(entry, monkeypatch):
    env = environment()
    worker = _decision_worker(entry, env)
    used = set()
    async def verifier(secret, token):
        if token in used:
            return {"success": False}
        used.add(token)
        return await verified(secret, token)
    monkeypatch.setattr(entry, "_verify_turnstile", verifier)
    req = request("/v1/visit-token", **{"x-modelspec-turnstile": "single-use"})
    first = asyncio.run(worker.fetch(req))
    assert first.status == 200
    assert visit_token.verify(first.json()["token"], *visit_token.credential(req, env, {ORIGIN})) is None
    assert first.headers["cache-control"] == "no-store"
    assert "set-cookie" not in first.headers
    assert asyncio.run(worker.fetch(req)).status == 403
    assert not env.HUMAN_GATE.objects


@pytest.mark.parametrize("key,token_kind,enforced,expected", [
    (None, "valid", "true", 200), (None, "valid", "false", 200),
    (None, "absent", "true", 401), (None, "absent", "false", 200),
    (None, "invalid", "true", 401), (None, "invalid", "false", 200),
    ("unknown-key", "valid", "true", 401), ("unknown-key", "valid", "false", 401),
    ("unknown-key", "invalid", "true", 401), ("test_fixture", "valid", "true", 400),
])
def test_precedence_matrix(entry, key, token_kind, enforced, expected):
    env = environment(ACCESS_ENFORCED=enforced, X402_ENABLED="false")
    worker = _decision_worker(entry, env)
    token = mint(env) if token_kind == "valid" else "tampered" if token_kind == "invalid" else None
    response = asyncio.run(worker.fetch(request(token=token, key=key)))
    assert response.status == expected
    if key == "unknown-key":
        assert response.json()["error"]["code"] == "invalid_api_key"
    if key or token_kind != "valid":
        assert not env.HUMAN_GATE.objects


@pytest.mark.parametrize("path", ["/v1/decide", "/v1/vocabulary", "/v1/rank", "/v1/compare", "/v1/policy-check"])
def test_spoofed_origin_with_no_token_gets_no_answer(entry, monkeypatch, path):
    env = environment()
    worker = _decision_worker(entry, env)
    monkeypatch.setattr(entry, "_bundled_read", lambda url: (True, b"{}"))
    response = asyncio.run(worker.fetch(request(path)))
    assert response.status == 401
    assert response.json()["error"]["code"] == "missing_api_key"
    assert not env.HUMAN_GATE.objects


@pytest.mark.parametrize("ip,origin", [("203.0.113.10", ORIGIN), (IP, "https://www.modelspec.dev"), (IP, "https://evil.test")])
def test_worker_rejects_wrong_visitor_and_origin(entry, ip, origin):
    env = environment()
    worker = _decision_worker(entry, env)
    response = asyncio.run(worker.fetch(request(token=mint(env), ip=ip, origin=origin)))
    assert response.status == 401
    assert not env.HUMAN_GATE.objects


def test_expired_worker_token_does_not_consume(entry, monkeypatch):
    env = environment()
    worker = _decision_worker(entry, env)
    token = mint(env, now=10000)
    monkeypatch.setattr(visit_token.time, "time", lambda: 11800)
    response = asyncio.run(worker.fetch(request(token=token)))
    assert response.status == 401
    assert response.json()["error"]["code"] == "visit_token_expired"
    assert not env.HUMAN_GATE.objects


def test_success_slides_expiry_and_keeps_action_meter(entry, monkeypatch):
    env = environment()
    worker = _decision_worker(entry, env)
    now = [10000]
    monkeypatch.setattr(visit_token.time, "time", lambda: now[0])
    token = mint(env)
    now[0] += 20
    req = request(token=token, **{"x-modelspec-intent": INTENT})
    response = asyncio.run(worker.fetch(req))
    assert response.status == 200
    assert response.headers[visit_token.EXPIRY_HEADER] == "11820"
    assert response.headers["x-modelspec-decisions-remaining"] == "299"
    req._body = json.dumps({**PRIMARY, "explain": "full"})
    assert asyncio.run(worker.fetch(req)).headers["x-modelspec-decisions-remaining"] == "299"
    req._body = json.dumps(PLOT)
    assert asyncio.run(worker.fetch(req)).headers["x-modelspec-decisions-remaining"] == "299"
    req._body = json.dumps({**PRIMARY, "where": []})
    assert asyncio.run(worker.fetch(req)).headers["x-modelspec-decisions-remaining"] == "298"


def test_default_day_allowance_and_reset(monkeypatch):
    env = environment()
    now = [10000]
    monkeypatch.setattr(human_gate_do.time, "time", lambda: now[0])
    obj = env.HUMAN_GATE.get("fixture")
    for _ in range(300):
        # Irregular intervals avoid sweep detection while retaining the daily count.
        now[0] += 601 if _ % 4 == 0 else 61
        assert asyncio.run(obj.take_visit())["reason"] == ""
    assert asyncio.run(obj.take_visit())["reason"] == "day"
    assert asyncio.run(obj.remaining(True)) == 0
    now[0] = 86400
    assert asyncio.run(obj.take_visit())["remaining"] == 299


def test_default_burst_is_atomic_and_allowances_are_configurable(monkeypatch):
    monkeypatch.setattr(human_gate_do.time, "time", lambda: 10000)
    obj = environment().HUMAN_GATE.get("fixture")
    async def race():
        return await asyncio.gather(*(obj.take_visit() for _ in range(40)))
    out = asyncio.run(race())
    assert sum(row["reason"] == "" for row in out) == 30
    assert out[-1] == {"remaining": 270, "reason": "burst", "retry_after": 61}
    tuned = environment(VISIT_DECIDE_DAY_LIMIT="2", VISIT_DECIDE_BURST_LIMIT="1").HUMAN_GATE.get("fixture")
    assert asyncio.run(tuned.take_visit())["remaining"] == 1
    assert asyncio.run(tuned.take_visit())["reason"] == "burst"


def test_sweep_is_retained_and_vocabulary_has_its_own_allowance(monkeypatch):
    now = [10000]
    monkeypatch.setattr(human_gate_do.time, "time", lambda: now[0])
    obj = environment(VISIT_VOCABULARY_DAY_LIMIT="2", VISIT_VOCABULARY_BURST_LIMIT="1").HUMAN_GATE.get("fixture")
    for _ in range(5):
        out = asyncio.run(obj.take_visit())
        now[0] += 70
    assert out["reason"] == "sweep"
    assert asyncio.run(obj.take_visit_vocabulary())["remaining"] == 1
    assert asyncio.run(obj.take_visit_vocabulary())["reason"] == "burst"
    now[0] += 61
    assert asyncio.run(obj.take_visit_vocabulary())["remaining"] == 0
    now[0] += 61
    assert asyncio.run(obj.take_visit_vocabulary())["reason"] == "day"
    assert asyncio.run(obj.take_visit())["reason"] == "sweep"


def test_worker_vocabulary_uses_token_and_never_caches_credentials(entry, monkeypatch):
    env = environment()
    worker = _decision_worker(entry, env)
    monkeypatch.setattr(entry, "_bundled_read", lambda url: (True, b'{"facets":[]}'))
    response = asyncio.run(worker.fetch(request("/v1/vocabulary", token=mint(env))))
    assert response.status == 200
    assert response.json() == {"facets": []}
    assert response.headers["cache-control"] == "no-store"
    assert response.headers["x-modelspec-decisions-remaining"] == "59"
    assert visit_token.HEADER in response.headers
    obj = next(iter(env.HUMAN_GATE.objects.values()))
    assert asyncio.run(obj.remaining(True)) == 300


def test_flags_ship_off_and_exchange_is_disabled(entry):
    values = production_vars(Path(__file__).resolve().parents[1])
    assert values["VISIT_GATE_ENABLED"] == "false"
    worker = _decision_worker(entry, environment(VISIT_GATE_ENABLED="false"))
    assert asyncio.run(worker.fetch(request("/v1/visit-token"))).status == 404


def test_live_key_wins_even_with_a_tampered_visit_token(entry):
    from datetime import UTC, datetime
    import access_config
    import access_keys
    import x402
    env = environment(X402_ENABLED="false", TURNSTILE_SECRET=None, VISIT_TOKEN_HMAC_KEY=None)
    key = "live_visit_fixture"
    asyncio.run(access_keys.issue(env.ACCESS, tier="free", owner="fixture", now=datetime.now(UTC),
                                 policy=access_config.load_policy(env), secret=key))
    asyncio.run(env.CREDITS.set_monthly(x402.holder_from_key(key), 5, "fixture-invoice", "fixture"))
    worker = _decision_worker(entry, env)
    response = asyncio.run(worker.fetch(request(key=key, token="tampered")))
    assert response.status == 200
    assert "x-modelspec-key-id" in response.headers
    assert visit_token.HEADER not in response.headers
    assert not env.HUMAN_GATE.objects


@pytest.mark.parametrize("overrides", [
    {"VISIT_TOKEN_HMAC_KEY": None}, {"VISITOR_HMAC_KEY": None},
    {"TURNSTILE_SECRET": None}, {"VISIT_DECIDE_DAY_LIMIT": "0"},
])
def test_unconfigured_exchange_fails_closed(overrides):
    env = environment(**overrides)
    response = asyncio.run(visit_token.exchange(request(**{"x-modelspec-turnstile": "token"}), env, {ORIGIN}, verified))
    assert response[0] == 503
    assert not env.HUMAN_GATE.objects


def test_privacy_guard_rejects_switching_on_before_adoption(monkeypatch):
    from tests.test_legal import test_visit_gate_requires_adopted_v19_privacy_before_enabling
    import pipeline.worker_flags
    config = production_vars(Path(__file__).resolve().parents[1])
    config["VISIT_GATE_ENABLED"] = "true"
    monkeypatch.setattr(pipeline.worker_flags, "production_vars", lambda root: config)
    with pytest.raises(AssertionError, match="requires adopted privacy v1.9"):
        test_visit_gate_requires_adopted_v19_privacy_before_enabling()
