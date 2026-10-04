import re
"""MODEL-292: real SQLite metering and Worker routing, external verifier stubbed."""
import asyncio
import json
from types import SimpleNamespace
from pathlib import Path

import sys

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


@pytest.fixture
def bundled_entry(monkeypatch):
    """The Worker with a bundled vocabulary, as deployed with DATA_SPLIT_ENABLED.

    entry.py reads the bundle at import, so install it before loading the module
    rather than rely on another test file having left one in sys.modules.
    """
    bundle = SimpleNamespace(read=lambda path: b'{"facets":[]}' if path == "/api/decision/vocabulary.json" else None)
    monkeypatch.setitem(sys.modules, "bundled_data", bundle)
    from tests.test_x402 import entry as entry_fixture
    return entry_fixture.__wrapped__(monkeypatch)


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
def test_spoofed_origin_with_no_token_gets_no_answer(bundled_entry, path):
    env = environment()
    worker = _decision_worker(bundled_entry, env)
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


def test_worker_vocabulary_uses_token_and_never_caches_credentials(bundled_entry):
    env = environment()
    worker = _decision_worker(bundled_entry, env)
    response = asyncio.run(worker.fetch(request("/v1/vocabulary", token=mint(env))))
    assert response.status == 200
    assert response.json() == {"facets": []}
    assert response.headers["cache-control"] == "no-store"
    assert response.headers["x-modelspec-decisions-remaining"] == "59"
    assert visit_token.HEADER in response.headers
    obj = next(iter(env.HUMAN_GATE.objects.values()))
    assert asyncio.run(obj.remaining(True)) == 300


def test_flag_off_disables_the_exchange(entry):
    # Production turned the visit gate on 2026-10-03 (MODEL-292, privacy v1.9);
    # the flag-off path must still remove the route entirely.
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
    import tests.test_legal
    config = production_vars(Path(__file__).resolve().parents[1])
    config["VISIT_GATE_ENABLED"] = "true"
    monkeypatch.setattr(pipeline.worker_flags, "production_vars", lambda root: config)
    # The adopted statement passes; the same flag against a pre-1.9 statement must not.
    test_visit_gate_requires_adopted_v19_privacy_before_enabling()
    monkeypatch.setattr(tests.test_legal, "PRIVACY",
                        re.sub(r"Version `\d+\.\d+`", "Version `1.8`", tests.test_legal.PRIVACY, count=1))
    with pytest.raises(AssertionError, match="requires adopted privacy v1.9"):
        test_visit_gate_requires_adopted_v19_privacy_before_enabling()


# ── security review follow-ups ───────────────────────────────────────────────

def test_renewal_chain_stops_four_hours_after_the_turnstile_exchange():
    secret = b"new-signing-secret"
    start = 100_000
    token, expiry = visit_token.issue("visitor:one", ORIGIN, secret, start)
    assert expiry == start + visit_token.LIFETIME_SECONDS
    moment = start
    while True:
        # Renew as admit does: carry the chain's original issue forward.
        moment = expiry - 1
        code, original = visit_token.check(token, "visitor:one", ORIGIN, secret, moment)
        assert code is None and original == start
        token, expiry = visit_token.issue("visitor:one", ORIGIN, secret, moment, original=original)
        if expiry == start + visit_token.MAX_CHAIN_SECONDS:
            break
        assert expiry < start + visit_token.MAX_CHAIN_SECONDS
    assert visit_token.MAX_CHAIN_SECONDS == 4 * 60 * 60
    assert visit_token.verify(token, "visitor:one", ORIGIN, secret, expiry - 1) is None
    assert visit_token.verify(token, "visitor:one", ORIGIN, secret, expiry) == "visit_token_expired"


def test_a_token_claiming_a_longer_chain_or_lifetime_is_invalid():
    import base64
    import hashlib
    import hmac
    secret = b"new-signing-secret"

    def signed(claims):
        encoded = base64.urlsafe_b64encode(json.dumps(claims, separators=(",", ":")).encode()).decode().rstrip("=")
        return encoded + "." + hmac.new(secret, encoded.encode(), hashlib.sha256).hexdigest()
    now = 100_000
    four_hours = visit_token.MAX_CHAIN_SECONDS
    for claims in (
        ["visitor:one", ORIGIN, now - four_hours, now - 10, now + 1790],  # renewed past the chain
        ["visitor:one", ORIGIN, now, now, now + visit_token.LIFETIME_SECONDS + 1],  # longer than 30 minutes
        ["visitor:one", ORIGIN, now + 1, now, now + 60],  # original after this issue
        ["visitor:one", ORIGIN, now, now, now + 60, "extra"],
        ["visitor:one", ORIGIN, now, now + 60],  # the pre-chain shape
    ):
        assert visit_token.verify(signed(claims), "visitor:one", ORIGIN, secret, now + 1) == "visit_token_invalid"


def test_worker_renewal_never_extends_past_the_chain(entry, monkeypatch):
    env = environment()
    worker = _decision_worker(entry, env)
    now = [100_000]
    monkeypatch.setattr(visit_token.time, "time", lambda: now[0])
    monkeypatch.setattr(human_gate_do.time, "time", lambda: now[0])
    token = mint(env)
    now[0] += visit_token.MAX_CHAIN_SECONDS - 60
    # Rebind the day: the identity is daily, so stay within one UTC day.
    response = asyncio.run(worker.fetch(request(token=_renewed_until(worker, env, token, now))))
    assert response.status == 200
    assert int(response.headers[visit_token.EXPIRY_HEADER]) == 100_000 + visit_token.MAX_CHAIN_SECONDS
    now[0] = 100_000 + visit_token.MAX_CHAIN_SECONDS
    refused = asyncio.run(worker.fetch(request(token=response.headers[visit_token.HEADER])))
    assert refused.status == 401
    assert refused.json()["error"]["code"] == "visit_token_expired"


def _renewed_until(worker, env, token, now):
    """Slide the token forward every 29 minutes up to `now`, as an active page would."""
    target = now[0]
    now[0] = 100_000
    while now[0] + 29 * 60 < target:
        now[0] += 29 * 60
        response = asyncio.run(worker.fetch(request(token=token, **{"x-modelspec-intent": f"intent-{now[0]}"})))
        assert response.status == 200
        token = response.headers[visit_token.HEADER]
    now[0] = target
    return token


def test_visit_meter_keeps_only_intents_inside_their_window(monkeypatch):
    now = [10_000.0]
    monkeypatch.setattr(human_gate_do.time, "time", lambda: now[0])
    env = environment()
    obj = env.HUMAN_GATE.get("fixture")
    for index in range(300):
        now[0] += 601 if index % 4 == 0 else 61
        assert asyncio.run(obj.take_visit(f"intent-{index}", PRIMARY))["reason"] == ""
    from credits_do import _cell, _one_row
    state = json.loads(str(_cell(_one_row(obj.ctx.storage.sql.exec("SELECT v FROM human_state WHERE k = 'visit'")), "v")))
    assert state["count"] == 300
    assert list(state["intents"]) == ["intent-299"]
    # The window still holds for a live intent; an expired one is metered anew.
    now[0] += 1
    assert asyncio.run(obj.take_visit("intent-299", PRIMARY))["remaining"] == 0
    assert asyncio.run(obj.take_visit("intent-298", PRIMARY))["reason"] == "day"


def test_prune_keeps_live_admissions_untouched():
    state = {"intents": {"old": {"first": 0, "requests": 8}, "live": {"first": 50, "requests": 2}}}
    human_gate_do.prune_intents(state, 100)
    assert state == {"intents": {"live": {"first": 50, "requests": 2}}}


def test_a_token_from_yesterday_is_refused_after_the_daily_identity_rotates(entry, monkeypatch):
    from datetime import UTC, datetime
    import visitor
    moment = [datetime(2026, 10, 2, 23, 59, 30, tzinfo=UTC)]

    class Clock(datetime):
        @classmethod
        def now(cls, tz=None):
            return moment[0]
    monkeypatch.setattr(visitor, "datetime", Clock)
    monkeypatch.setattr(visit_token.time, "time", lambda: moment[0].timestamp())
    env = environment()
    worker = _decision_worker(entry, env)
    token = mint(env)
    moment[0] = datetime(2026, 10, 3, 0, 0, 30, tzinfo=UTC)
    response = asyncio.run(worker.fetch(request(token=token)))
    assert response.status == 401
    assert response.json()["error"]["code"] == "visit_token_invalid"
    assert not env.HUMAN_GATE.objects


def test_missing_connecting_ip_fails_closed_on_exchange_and_admit(entry, capsys):
    env = environment()
    token = mint(env)
    exchange = asyncio.run(visit_token.exchange(request(ip="", **{"x-modelspec-turnstile": "single-use"}), env, {ORIGIN}, verified))
    assert exchange[0] == 503
    worker = _decision_worker(entry, env)
    for path in ("/v1/decide", "/v1/vocabulary"):
        admitted = asyncio.run(visit_token.admit(request(path, token=token, ip=""), env, {ORIGIN}, path.rsplit("/", 1)[-1], PRIMARY))
        assert admitted[:2] == (503, "human_gate_unavailable")
    response = asyncio.run(worker.fetch(request(token=token, ip="")))
    assert response.status == 503
    assert response.json()["error"]["code"] == "human_gate_unavailable"
    assert not env.HUMAN_GATE.objects
    logged = capsys.readouterr().out
    assert "human_gate_unavailable where=visit_exchange type=ValueError" in logged
    assert "human_gate_unavailable where=visit_admit type=ValueError" in logged


def test_failure_logs_name_the_cause_but_never_a_credential(capsys):
    env = environment(VISIT_TOKEN_HMAC_KEY=None)
    secret = "fixture-visit-signing-secret-0123456789"
    turnstile = "single-use-turnstile-value"
    assert asyncio.run(visit_token.exchange(request(**{"x-modelspec-turnstile": turnstile}), env, {ORIGIN}, verified))[0] == 503
    token = mint(environment())
    assert asyncio.run(visit_token.admit(request(token=token), env, {ORIGIN}, "decide", PRIMARY))[0] == 503
    logged = capsys.readouterr().out
    assert logged.count("visit signing secret unavailable") == 2
    for value in (secret, turnstile, token, KEY, IP):
        assert value not in logged


@pytest.mark.parametrize("path", ["/v1/rank", "/v1/compare", "/v1/policy-check"])
def test_a_valid_visit_token_admits_nothing_but_decide_and_vocabulary(entry, path):
    env = environment()
    worker = _decision_worker(entry, env)
    response = asyncio.run(worker.fetch(request(path, token=mint(env))))
    assert response.status == 401
    assert response.json()["error"]["code"] == "missing_api_key"
    assert visit_token.HEADER not in response.headers
    assert not env.HUMAN_GATE.objects


@pytest.mark.parametrize("method,query", [("HEAD", ""), ("GET", "?section=facets"), ("HEAD", "?section=facets&limit=5")])
def test_vocabulary_head_and_query_variants_take_the_same_visit_gate(bundled_entry, method, query):
    env = environment()
    worker = _decision_worker(bundled_entry, env)

    def fetch(token):
        req = request("/v1/vocabulary" + query, token=token)
        req.method = method
        return asyncio.run(worker.fetch(req))
    refused = fetch(None)
    assert refused.status == 401
    assert not env.HUMAN_GATE.objects
    response = fetch(mint(env))
    assert response.status == 200
    assert response.headers["cache-control"] == "no-store"
    assert response.headers["x-modelspec-decisions-remaining"] == "59"
    assert visit_token.HEADER in response.headers
    if method == "HEAD":
        assert not response.body
    else:
        assert "facets" in response.json()
