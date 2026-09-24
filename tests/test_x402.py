"""MODEL-75: x402 prepaid credits, settled before delivery, billed only on success."""

from __future__ import annotations

import asyncio
import base64
import json
import logging
import sys
import time
import uuid
from pathlib import Path
from typing import Any

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
WORKER_SRC = REPO_ROOT / "api" / "worker" / "src"
sys.path.insert(0, str(WORKER_SRC))
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import cdp_auth  # noqa: E402
import credits  # noqa: E402
import x402  # noqa: E402
from test_cdp_auth import (  # noqa: E402
    decode_unverified,
    generate_ed25519,
    openssl_sign_async,
)
from x402_facilitator import CdpFacilitator, FacilitatorError, StubFacilitator  # noqa: E402

PAY_TO = "0x209693bc6afc0c5328ba36faf03c514ef312287c"
PAYER = "0x857b06519e91e3a54538791bdbb0e22373e36b66"
ENVELOPE = {"schema_version": "1.0", "service_commit": "test"}
RESOURCE = "https://api.modelspec.dev/v1/rank"


def _cfg(**kwargs: Any) -> x402.Config:
    base = dict(
        enabled=True,
        mainnet=False,
        network=x402.NETWORK_BASE_SEPOLIA,
        asset=x402._norm_addr(x402.USDC_BASE_SEPOLIA),
        pay_to=PAY_TO,
        price_atomic=1000,
        facilitator_url="https://api.cdp.coinbase.com/platform",
        resource_origin="https://api.modelspec.dev",
    )
    base.update(kwargs)
    return x402.Config(**base)  # type: ignore[arg-type]


def _payload(*, nonce: str = "0x" + "11" * 32, value: str = "1000",
             to: str = PAY_TO, sig: str = "0x" + "ab" * 65) -> dict[str, Any]:
    return {
        "x402Version": 2,
        "accepted": {
            "scheme": "exact",
            "network": x402.NETWORK_BASE_SEPOLIA,
            "amount": value,
            "asset": x402._norm_addr(x402.USDC_BASE_SEPOLIA),
            "payTo": to,
        },
        "payload": {
            "signature": sig,
            "authorization": {
                "from": PAYER,
                "to": to,
                "value": value,
                "validAfter": "0",
                "validBefore": "9999999999",
                "nonce": nonce,
            },
        },
    }


def _header(payload: dict[str, Any]) -> dict[str, str]:
    raw = json.dumps(payload).encode("utf-8")
    return {x402.PAYMENT_SIGNATURE: base64.b64encode(raw).decode("ascii")}


def _get_header(headers: dict[str, str]):
    lowered = {k.lower(): v for k, v in headers.items()}

    def get(name: str) -> str | None:
        return lowered.get(name.lower())

    return get


async def _ok() -> tuple[int, dict[str, Any]]:
    return 200, {**ENVELOPE, "result": [{"model_id": "example/ok"}]}


async def _empty() -> tuple[int, dict[str, Any]]:
    return 200, {**ENVELOPE, "result": []}


async def _no_match() -> tuple[int, dict[str, Any]]:
    return 422, {**ENVELOPE, "error": {"code": "no_match", "message": "none"}, "result": []}


async def _boom() -> tuple[int, dict[str, Any]]:
    return 500, {**ENVELOPE, "error": {"code": "export_unavailable", "message": "x"}, "result": []}


def _run(coro):
    return asyncio.run(coro)


# ── 402 discovery ────────────────────────────────────────────────────────────

def test_unfunded_request_returns_well_formed_402_naming_price_and_how_to_pay():
    produced = []

    async def produce():
        produced.append(1)
        return await _ok()

    status, body = _run(x402.charge(
        config=_cfg(), ledger=credits.MemoryLedger(), facilitator=StubFacilitator(),
        get_header=_get_header({}), holder=None, resource_url=RESOURCE,
        envelope=ENVELOPE, produce=produce))
    assert status == 402
    assert produced == []
    error = body["error"]
    assert error["code"] == "payment_required"
    assert error["price"]["amount"] == "1000"
    assert error["price"]["placeholder"] is True
    assert error["payTo"] == PAY_TO
    assert error["resource"] == RESOURCE
    assert error["accepts"][0]["network"] == x402.NETWORK_BASE_SEPOLIA
    assert "PAYMENT-SIGNATURE" in error["how_to_pay"]
    headers = x402.http_headers(status, body)
    assert x402.PAYMENT_REQUIRED_HEADER in headers
    decoded = json.loads(base64.b64decode(headers[x402.PAYMENT_REQUIRED_HEADER]))
    assert decoded["x402Version"] == 2
    assert decoded["accepts"][0]["payTo"] == PAY_TO


def test_price_is_configuration_not_code():
    cheap = x402.payment_required_body(_cfg(price_atomic=1000), ENVELOPE, RESOURCE)
    dear = x402.payment_required_body(_cfg(price_atomic=10000), ENVELOPE, RESOURCE)
    assert cheap["error"]["price"]["amount"] == "1000"
    assert dear["error"]["price"]["amount"] == "10000"
    assert dear["error"]["price"]["usd"] == 0.01


def test_disabled_flag_is_a_no_op():
    status, body = _run(x402.charge(
        config=_cfg(enabled=False), ledger=credits.MemoryLedger(),
        facilitator=StubFacilitator(), get_header=_get_header({}), holder=None,
        resource_url=RESOURCE, envelope=ENVELOPE, produce=_ok))
    assert status == 200
    assert body["result"]


# ── settlement credits once; replay does not ─────────────────────────────────

def test_settled_payment_credits_the_balance_exactly_once():
    ledger = credits.MemoryLedger()
    spy = StubFacilitator()
    holder = "key:" + "a" * 64
    payload = _payload(value="3000")  # three units
    status, body = _run(x402.charge(
        config=_cfg(), ledger=ledger, facilitator=spy,
        get_header=_get_header(_header(payload)), holder=holder,
        resource_url=RESOURCE, envelope=ENVELOPE, produce=_ok))
    assert status == 200
    assert [c[0] for c in spy.calls] == ["verify", "settle"]
    bal = _run(ledger.balance(holder))
    # 3 credited, 1 committed for this success
    assert bal.available == 2
    assert bal.reserved == 0

    spy.calls.clear()
    status, body = _run(x402.charge(
        config=_cfg(), ledger=ledger, facilitator=spy,
        get_header=_get_header(_header(payload)), holder=holder,
        resource_url=RESOURCE, envelope=ENVELOPE, produce=_ok))
    assert status == 200
    assert spy.calls == []  # replay must not re-settle
    bal = _run(ledger.balance(holder))
    assert bal.available == 1


def test_replayed_settlement_does_not_credit_twice():
    ledger = credits.MemoryLedger()
    pid = x402.payment_id(_payload())
    first = _run(ledger.credit("key:h", pid, 5, "0xabc"))
    second = _run(ledger.credit("key:h", pid, 5, "0xabc"))
    assert first.credited is True
    assert second.credited is False
    assert second.reason == "replay"
    assert _run(ledger.balance("key:h")).available == 5


# ── verify, settle, then produce ─────────────────────────────────────────────

def test_attack_verification_ordering_settle_before_produce():
    spy = StubFacilitator()
    trace = x402.ChargeTrace()

    async def produce():
        assert [c[0] for c in spy.calls] == ["verify", "settle"], (
            "produce ran before verify and settle; this test fails if the order "
            "in x402.charge is reversed")
        return await _ok()

    status, _ = _run(x402.charge(
        config=_cfg(), ledger=credits.MemoryLedger(), facilitator=spy,
        get_header=_get_header(_header(_payload())), holder=None,
        resource_url=RESOURCE, envelope=ENVELOPE, produce=produce, trace=trace))
    assert status == 200
    assert trace.events.index("verify") < trace.events.index("settle")
    assert trace.events.index("settle") < trace.events.index("produce")


def test_settlement_before_answer_fails_if_the_order_is_reversed():
    """The acceptance criterion: this assertion is false if produce is moved above settle."""
    spy = StubFacilitator()

    async def produce():
        names = [c[0] for c in spy.calls]
        assert "settle" in names and names.index("settle") == len(names) - 1
        return await _ok()

    _run(x402.charge(
        config=_cfg(), ledger=credits.MemoryLedger(), facilitator=spy,
        get_header=_get_header(_header(_payload())), holder="key:" + "b" * 64,
        resource_url=RESOURCE, envelope=ENVELOPE, produce=produce))


# ── 500 / no-match / empty do not decrement ──────────────────────────────────

def test_a_500_does_not_decrement_the_balance():
    ledger = credits.MemoryLedger()
    holder = "key:" + "c" * 64
    _run(ledger.credit(holder, "already", 1, "0x1"))
    status, _ = _run(x402.charge(
        config=_cfg(), ledger=ledger, facilitator=StubFacilitator(),
        get_header=_get_header({}), holder=holder, resource_url=RESOURCE,
        envelope=ENVELOPE, produce=_boom))
    assert status == 500
    assert _run(ledger.balance(holder)).available == 1
    assert _run(ledger.balance(holder)).reserved == 0


def test_a_no_match_does_not_decrement_the_balance():
    ledger = credits.MemoryLedger()
    holder = "key:" + "d" * 64
    _run(ledger.credit(holder, "already", 1, "0x1"))
    status, _ = _run(x402.charge(
        config=_cfg(), ledger=ledger, facilitator=StubFacilitator(),
        get_header=_get_header({}), holder=holder, resource_url=RESOURCE,
        envelope=ENVELOPE, produce=_no_match))
    assert status == 422
    assert _run(ledger.balance(holder)).available == 1


def test_an_empty_result_does_not_decrement_the_balance():
    ledger = credits.MemoryLedger()
    holder = "key:" + "e" * 64
    _run(ledger.credit(holder, "already", 1, "0x1"))
    status, _ = _run(x402.charge(
        config=_cfg(), ledger=ledger, facilitator=StubFacilitator(),
        get_header=_get_header({}), holder=holder, resource_url=RESOURCE,
        envelope=ENVELOPE, produce=_empty))
    assert status == 200
    assert _run(ledger.balance(holder)).available == 1


# ── concurrency ──────────────────────────────────────────────────────────────

def test_concurrent_requests_cannot_drive_the_balance_negative_or_double_spend():
    ledger = credits.MemoryLedger()
    holder = "key:" + "f" * 64
    _run(ledger.credit(holder, "seed", 1, "0x1"))

    async def once():
        return await x402.charge(
            config=_cfg(), ledger=ledger, facilitator=StubFacilitator(),
            get_header=_get_header({}), holder=holder, resource_url=RESOURCE,
            envelope=ENVELOPE, produce=_ok)

    async def both():
        return await asyncio.gather(once(), once())

    results = _run(both())
    statuses = sorted(status for status, _ in results)
    assert statuses == [200, 402]
    bal = _run(ledger.balance(holder))
    assert bal.available == 0
    assert bal.reserved == 0
    assert bal.total == 0


# ── attack classes from docs/agent-commerce-assessment.md §5 ─────────────────

def test_attack_free_riding_unfunded_never_produces():
    async def produce():
        raise AssertionError("free-riding: produce ran with no payment and no balance")

    status, body = _run(x402.charge(
        config=_cfg(), ledger=credits.MemoryLedger(), facilitator=StubFacilitator(),
        get_header=_get_header({}), holder=None, resource_url=RESOURCE,
        envelope=ENVELOPE, produce=produce))
    assert status == 402
    assert body["error"]["code"] == "payment_required"


def test_attack_toctou_reserve_before_produce():
    ledger = credits.MemoryLedger()
    holder = "key:" + "g" * 64
    _run(ledger.credit(holder, "seed", 1, "0x1"))
    reserved_at_produce: list[int] = []

    async def produce():
        reserved_at_produce.append(_run(ledger.balance(holder)).reserved)
        return await _ok()

    # produce is async and we cannot call _run from inside the event loop.
    async def produce_async():
        reserved_at_produce.append((await ledger.balance(holder)).reserved)
        return await _ok()

    _run(x402.charge(
        config=_cfg(), ledger=ledger, facilitator=StubFacilitator(),
        get_header=_get_header({}), holder=holder, resource_url=RESOURCE,
        envelope=ENVELOPE, produce=produce_async))
    assert reserved_at_produce == [1], (
        "produce ran without a reservation; a TOCTOU check-then-act would look like this")
    assert _run(ledger.balance(holder)).available == 0


def test_attack_front_running_wrong_payto_never_settles():
    spy = StubFacilitator()
    other = "0x0000000000000000000000000000000000000001"
    status, body = _run(x402.charge(
        config=_cfg(), ledger=credits.MemoryLedger(), facilitator=spy,
        get_header=_get_header(_header(_payload(to=other))), holder=None,
        resource_url=RESOURCE, envelope=ENVELOPE, produce=_ok))
    assert status == 400
    assert body["error"]["code"] == "invalid_payment"
    assert spy.calls == []


# ── per-call fallback; balance query ─────────────────────────────────────────

def test_per_call_402_fallback_works_with_no_stored_balance():
    spy = StubFacilitator()
    status, body = _run(x402.charge(
        config=_cfg(), ledger=credits.MemoryLedger(), facilitator=spy,
        get_header=_get_header(_header(_payload())), holder=None,
        resource_url=RESOURCE, envelope=ENVELOPE, produce=_ok))
    assert status == 200
    assert body["result"]
    assert [c[0] for c in spy.calls] == ["verify", "settle"]


def test_drive_by_replay_does_not_get_a_second_result():
    ledger = credits.MemoryLedger()
    headers = _header(_payload(nonce="0x" + "cd" * 32))
    first = _run(x402.charge(
        config=_cfg(), ledger=ledger, facilitator=StubFacilitator(),
        get_header=_get_header(headers), holder=None, resource_url=RESOURCE,
        envelope=ENVELOPE, produce=_ok))
    assert first[0] == 200
    second = _run(x402.charge(
        config=_cfg(), ledger=ledger, facilitator=StubFacilitator(),
        get_header=_get_header(headers), holder=None, resource_url=RESOURCE,
        envelope=ENVELOPE, produce=_ok))
    assert second[0] == 402


def test_balance_is_queryable_by_the_holder():
    ledger = credits.MemoryLedger()
    key = "live_secret_example"
    holder = x402.holder_from_key(key)
    _run(ledger.credit(holder, "p", 4, "0x"))
    status, body = _run(x402.balance_query(
        config=_cfg(), ledger=ledger, api_key=key, envelope=ENVELOPE))
    assert status == 200
    assert body["available"] == 4
    assert body["holder"] == holder
    assert body["endpoint"] == "credits"


def test_balance_query_without_a_key_is_401():
    status, body = _run(x402.balance_query(
        config=_cfg(), ledger=credits.MemoryLedger(), api_key=None, envelope=ENVELOPE))
    assert status == 401
    assert body["error"]["code"] == "missing_holder"


def test_failed_verify_never_produces():
    spy = StubFacilitator(valid=False)

    async def produce():
        raise AssertionError("produce after failed verify")

    status, body = _run(x402.charge(
        config=_cfg(), ledger=credits.MemoryLedger(), facilitator=spy,
        get_header=_get_header(_header(_payload())), holder=None,
        resource_url=RESOURCE, envelope=ENVELOPE, produce=produce))
    assert status == 402
    assert body["error"]["code"] == "payment_failed"
    assert [c[0] for c in spy.calls] == ["verify"]


def test_mainnet_is_off_by_default_and_refuses_a_mainnet_network_var():
    cfg = _cfg(mainnet=False, network=x402.NETWORK_BASE)
    assert cfg.mainnet is False
    status, body = _run(x402.charge(
        config=cfg, ledger=credits.MemoryLedger(), facilitator=StubFacilitator(),
        get_header=_get_header(_header(_payload())), holder=None,
        resource_url=RESOURCE, envelope=ENVELOPE, produce=_ok))
    assert status == 400


# ── facilitator client; no network ───────────────────────────────────────────

def test_facilitator_client_posts_to_the_documented_paths():
    seen: list[str] = []

    async def post(url: str, payload: dict[str, Any], headers: dict[str, str]):
        seen.append(url)
        if url.endswith("/verify"):
            return 200, {"isValid": True, "payer": PAYER}
        return 200, {"success": True, "transaction": "0x1", "payer": PAYER,
                     "network": x402.NETWORK_BASE_SEPOLIA}

    client = CdpFacilitator("https://api.cdp.coinbase.com/platform", post=post)
    _run(client.verify(_payload(), {}))
    _run(client.settle(_payload(), {}))
    assert seen == [
        "https://api.cdp.coinbase.com/platform/v2/x402/verify",
        "https://api.cdp.coinbase.com/platform/v2/x402/settle",
    ]


def _minting_env(*, mainnet: bool = False, static: str = "",
                 key_id: str = "", secret: str = "") -> Any:
    env = type("E", (), {})()
    env.CDP_API_KEY_ID = key_id
    env.CDP_API_KEY_SECRET = secret
    env.CDP_JWT = static
    env.CDP_SIGN = openssl_sign_async
    env.X402_MAINNET = "true" if mainnet else "false"
    return env


def _bearer(headers: dict[str, str]) -> str:
    value = headers.get("Authorization") or headers.get("authorization") or ""
    assert value.startswith("Bearer ")
    return value.split(" ", 1)[1]


def test_each_facilitator_request_carries_a_fresh_unexpired_jwt_for_that_path():
    secret, _der, _pub = generate_ed25519()
    key_id = str(uuid.uuid4())
    seen: list[tuple[str, str]] = []

    async def post(url: str, payload: dict[str, Any], headers: dict[str, str]):
        seen.append((url, _bearer(headers)))
        if url.endswith("/verify"):
            return 200, {"isValid": True, "payer": PAYER}
        return 200, {"success": True, "transaction": "0x1", "payer": PAYER,
                     "network": x402.NETWORK_BASE_SEPOLIA}

    auth = cdp_auth.auth_from_env(
        _minting_env(key_id=key_id, secret=secret),
        mainnet=False, sign=openssl_sign_async,
    )
    client = CdpFacilitator("https://api.cdp.coinbase.com/platform", post=post, auth=auth)
    now = int(time.time())
    _run(client.verify(_payload(), {}))
    _run(client.settle(_payload(), {}))
    assert len(seen) == 2
    nonces = []
    for url, token in seen:
        header, claims, _sig = decode_unverified(token)
        path = url.split("coinbase.com", 1)[1]
        assert claims["uri"] == f"POST api.cdp.coinbase.com{path}"
        assert claims["nbf"] <= now + 1
        assert claims["exp"] > now
        assert claims["exp"] - claims["nbf"] == 120
        assert header["kid"] == key_id
        nonces.append(header["nonce"])
    assert seen[0][1] != seen[1][1]
    assert nonces[0] != nonces[1]
    assert seen[0][0].endswith("/v2/x402/verify")
    assert seen[1][0].endswith("/v2/x402/settle")


def test_static_cdp_jwt_is_refused_when_mainnet_is_on():
    auth = cdp_auth.auth_from_env(
        _minting_env(mainnet=True, static="header.payload.sig"),
        mainnet=True,
    )
    async def post(url: str, payload: dict[str, Any], headers: dict[str, str]):
        raise AssertionError("must not post")

    client = CdpFacilitator(
        "https://api.cdp.coinbase.com/platform", post=post, auth=auth,
    )
    with pytest.raises(FacilitatorError, match="local-testing override"):
        _run(client.verify(_payload(), {}))


def test_static_cdp_jwt_is_a_sepolia_testing_override_only():
    seen: list[str] = []

    async def post(url: str, payload: dict[str, Any], headers: dict[str, str]):
        seen.append(_bearer(headers))
        return 200, {"isValid": True, "payer": PAYER}

    auth = cdp_auth.auth_from_env(
        _minting_env(static="static.local.test"),
        mainnet=False,
    )
    client = CdpFacilitator("https://api.cdp.coinbase.com/platform", post=post, auth=auth)
    _run(client.verify(_payload(), {}))
    assert seen == ["static.local.test"]


def test_api_key_minting_wins_over_static_jwt():
    secret, _der, _pub = generate_ed25519()
    seen: list[str] = []

    async def post(url: str, payload: dict[str, Any], headers: dict[str, str]):
        seen.append(_bearer(headers))
        return 200, {"isValid": True, "payer": PAYER}

    auth = cdp_auth.auth_from_env(
        _minting_env(key_id="kid", secret=secret, static="static.must.not.be.used"),
        mainnet=False, sign=openssl_sign_async,
    )
    client = CdpFacilitator("https://api.cdp.coinbase.com/platform", post=post, auth=auth)
    _run(client.verify(_payload(), {}))
    assert seen[0] != "static.must.not.be.used"
    _header, claims, _sig = decode_unverified(seen[0])
    assert claims["uri"].endswith("/v2/x402/verify")


def test_secret_and_jwt_do_not_appear_in_facilitator_logs(caplog, capsys):
    secret, _der, _pub = generate_ed25519()
    tokens: list[str] = []
    caplog.set_level(logging.DEBUG)

    async def post(url: str, payload: dict[str, Any], headers: dict[str, str]):
        tokens.append(_bearer(headers))
        return 200, {"isValid": True, "payer": PAYER}

    auth = cdp_auth.auth_from_env(
        _minting_env(key_id="kid", secret=secret),
        mainnet=False, sign=openssl_sign_async,
    )
    client = CdpFacilitator("https://api.cdp.coinbase.com/platform", post=post, auth=auth)
    _run(client.verify(_payload(), {}))
    captured = capsys.readouterr()
    haystack = "\n".join([caplog.text, captured.out, captured.err])
    assert secret not in haystack
    assert tokens[0] not in haystack
    assert "Bearer " not in haystack


def test_no_test_calls_the_network():
    """The production post adapter is worker_post (js.fetch). Tests inject `post`."""
    import inspect
    from x402_facilitator import worker_post
    source = inspect.getsource(test_facilitator_client_posts_to_the_documented_paths)
    assert "worker_post" not in source
    assert worker_post.__name__ == "worker_post"


def test_wrangler_ships_the_flag_off_and_sepolia():
    text = (REPO_ROOT / "api" / "worker" / "wrangler.jsonc").read_text(encoding="utf-8")
    live = "\n".join(l for l in text.splitlines() if not l.lstrip().startswith("//"))
    assert '"X402_ENABLED": "false"' in live
    assert '"X402_MAINNET": "false"' in live
    assert '"X402_NETWORK": "eip155:84532"' in live
    assert '"class_name": "CreditsObject"' in live
    assert '"X402_PAY_TO": ""' in live
    assert "CDP_API_KEY" not in live
    assert "CDP_JWT" not in live


def test_credits_modules_do_not_use_workers_kv():
    for name in ("credits.py", "credits_do.py"):
        source = (WORKER_SRC / name).read_text(encoding="utf-8")
        assert "CloudflareKV" not in source
        assert "kv_namespaces" not in source


# ── Worker wiring ────────────────────────────────────────────────────────────

@pytest.fixture
def entry(monkeypatch):
    import importlib.util
    import types

    js = types.ModuleType("js")

    async def _no_fetch(url):
        raise AssertionError(f"unexpected fetch of {url}")

    js.fetch = _no_fetch
    workers = types.ModuleType("workers")

    class _Response:
        def __init__(self, body, status=200, headers=None):
            self.body, self.status, self.headers = body, status, headers or {}

        def json(self):
            return json.loads(self.body)

    workers.Response = _Response
    workers.WorkerEntrypoint = type("WorkerEntrypoint", (), {})
    workers.DurableObject = type("DurableObject", (), {})
    monkeypatch.setitem(sys.modules, "js", js)
    monkeypatch.setitem(sys.modules, "workers", workers)
    for path in (str(REPO_ROOT), str(WORKER_SRC)):
        if path not in sys.path:
            sys.path.insert(0, path)
    spec = importlib.util.spec_from_file_location(
        "modelspec_worker_entry_x402", WORKER_SRC / "entry.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    async def load_export(origin, force=False):
        return {"build": {"commit": "deadbeef", "built_at": "t",
                          "export_schema_version": "2.0"},
                "candidates": [{"id": "example/ok", "name": "ok"}]}, None

    module._load_export = load_export
    return module


class _Req:
    def __init__(self, path, body=None, method="POST", headers=None):
        self.url = f"https://api.modelspec.test{path}"
        self.method = method
        self._body = json.dumps(body) if not isinstance(body, str) else body
        self._headers = {k.lower(): v for k, v in (headers or {}).items()}
        self.headers = type("H", (), {"get": lambda _s, n: self._headers.get(n.lower())})()

    async def text(self):
        return self._body or ""


def test_entry_unfunded_with_flag_on_is_402_and_does_not_fetch(entry):
    env = type("E", (), {})()
    env.BUILD_COMMIT = "c0ffee"
    env.EXPORT_ORIGIN = "https://modelspec.test"
    env.ACCESS_ENFORCED = "false"
    env.X402_ENABLED = "true"
    env.X402_PAY_TO = PAY_TO
    env.X402_PRICE_ATOMIC = "1000"
    env.X402_NETWORK = x402.NETWORK_BASE_SEPOLIA
    env.X402_ASSET = x402.USDC_BASE_SEPOLIA
    env.CREDITS = credits.MemoryLedger()
    env.X402_FACILITATOR = StubFacilitator()
    worker = entry.Default()
    worker.env = env
    response = asyncio.run(worker.fetch(_Req("/v1/rank", {"use_case": "coding"})))
    assert response.status == 402
    body = response.json()
    assert body["error"]["code"] == "payment_required"
    assert x402.PAYMENT_REQUIRED_HEADER in response.headers


def test_entry_credits_query(entry):
    env = type("E", (), {})()
    env.BUILD_COMMIT = "c0ffee"
    env.EXPORT_ORIGIN = "https://modelspec.test"
    env.X402_ENABLED = "false"
    ledger = credits.MemoryLedger()
    key = "live_abc"
    asyncio.run(ledger.credit(x402.holder_from_key(key), "p", 7, "0x"))
    env.CREDITS = ledger
    worker = entry.Default()
    worker.env = env
    response = asyncio.run(worker.fetch(_Req(
        "/v1/credits", method="GET", headers={"authorization": f"Bearer {key}"}, body="")))
    assert response.status == 200
    assert response.json()["available"] == 7


def test_entry_billing_paths_are_not_x402_paid_resources(entry):
    """Stripe's /v1/billing/* endpoints are not prepaid resources.

    Even with X402_ENABLED on, checkout, webhook, claim and rotate must be
    answered by the billing handlers, never wrapped into a 402.
    """
    assert all(not path.startswith("/v1/billing") for path in entry.POST_ENDPOINTS)
    env = type("E", (), {})()
    env.BUILD_COMMIT = "c0ffee"
    env.EXPORT_ORIGIN = "https://modelspec.test"
    env.ACCESS_ENFORCED = "false"
    env.BILLING_ENABLED = "false"
    env.TIER_POLICY = (REPO_ROOT / "api" / "worker" / "tiers.json").read_text(
        encoding="utf-8")
    env.X402_ENABLED = "true"
    env.X402_PAY_TO = PAY_TO
    env.X402_PRICE_ATOMIC = "1000"
    env.X402_NETWORK = x402.NETWORK_BASE_SEPOLIA
    env.X402_ASSET = x402.USDC_BASE_SEPOLIA
    env.CREDITS = credits.MemoryLedger()
    env.X402_FACILITATOR = StubFacilitator()
    worker = entry.Default()
    worker.env = env
    for path in (
        "/v1/billing/checkout",
        "/v1/billing/stripe-webhook",
        "/v1/billing/claim",
        "/v1/billing/rotate",
    ):
        response = asyncio.run(worker.fetch(_Req(path, body="{}")))
        body = response.json()
        code = (body.get("error") or {}).get("code")
        assert response.status != 402, path
        assert code != "payment_required", path
        assert code != "not_found", path
        assert x402.PAYMENT_REQUIRED_HEADER not in (response.headers or {})
        assert code in {
            "billing_not_enabled", "billing_not_configured",
            "invalid_webhook_signature", "invalid_request",
            "access_store_not_configured",
        }, (path, response.status, code)
