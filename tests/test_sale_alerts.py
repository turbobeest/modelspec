"""MODEL-391: one ephemeral Pushover notice per confirmed sale. No network."""

from __future__ import annotations

import asyncio
import base64
import inspect
import json
import logging
import sys
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace
from typing import Any
from urllib.parse import parse_qs

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
WORKER_SRC = REPO_ROOT / "api" / "worker" / "src"
for path in (str(REPO_ROOT), str(WORKER_SRC)):
    if path not in sys.path:
        sys.path.insert(0, path)

import access_config  # noqa: E402
import access_kv  # noqa: E402
import billing  # noqa: E402
import billing_stripe  # noqa: E402
import credits  # noqa: E402
import sale_alerts  # noqa: E402
import x402  # noqa: E402
from x402_facilitator import StubFacilitator  # noqa: E402

T0 = datetime(2026, 9, 17, 14, 30, 0, tzinfo=UTC)
TS = int(T0.timestamp())
WEBHOOK_SECRET = "whsec_test_fixture_not_a_real_secret"
COMMIT = "testsha"
PACK = "price_1UP2AVBPydVRHUBjlyyyEjb1"
TOKEN = "pushover-app-token-test"
USER = "pushover-user-key-test"
EMAIL = "buyer@example.com"
API_KEY = "msk_live_SECRETKEY123"
CARD = "4242424242424242"
WALLET = "0x" + "de" * 20
TX = "0x1a2b" + ("cd" * 30)
PAYER = "0x" + "ab" * 20


def run(coro: Any) -> Any:
    return asyncio.run(coro)


class Ctx:
    def __init__(self) -> None:
        self.pending: list[Any] = []

    def waitUntil(self, task: Any) -> None:  # noqa: N802 — Workers API
        self.pending.append(task)

    async def drain(self) -> None:
        pending, self.pending = self.pending, []
        if pending:
            await asyncio.gather(*pending)


class FetchLog:
    def __init__(self, *, fail: bool = False, status: int = 200) -> None:
        self.calls: list[tuple[str, str]] = []
        self.fail = fail
        self.status = status

    async def __call__(self, url: str, body: str) -> SimpleNamespace:
        self.calls.append((url, body))
        if self.fail:
            raise RuntimeError(f"pushover down {TOKEN} {USER} {body}")
        return SimpleNamespace(status=self.status)


@pytest.fixture
def policy() -> access_config.AccessPolicy:
    return access_config.load_policy()


@pytest.fixture
def pushes(monkeypatch: pytest.MonkeyPatch) -> FetchLog:
    fetch = FetchLog()
    monkeypatch.setattr(sale_alerts, "_fetch", fetch)
    sale_alerts._seen.clear()
    return fetch


def alert_env(**extra: Any) -> SimpleNamespace:
    values = {
        "SALE_ALERTS_ENABLED": "1",
        "PUSHOVER_APP_TOKEN": TOKEN,
        "PUSHOVER_USER_KEY": USER,
    }
    values.update(extra)
    return SimpleNamespace(**values)


def payload(type_: str, obj: dict[str, Any], event_id: str) -> str:
    return json.dumps(
        {"id": event_id, "object": "event", "type": type_, "data": {"object": obj}},
        separators=(",", ":"))


def signed(body: str) -> str:
    return billing_stripe.sign_header(body, WEBHOOK_SECRET, TS)


def pack_obj(**extra: Any) -> dict[str, Any]:
    body = {
        "id": "cs_sale_alert",
        "object": "checkout.session",
        "mode": "payment",
        "payment_status": "paid",
        "customer": "cus_sale",
        "customer_email": EMAIL,
        "customer_details": {"email": EMAIL},
        "payment_intent": "pi_sale_alert",
        "amount_total": 999,
        "metadata": {
            "modelspec_price_id": PACK,
            "api_key": API_KEY,
        },
        "payment_method_details": {"card": {"number": CARD}},
        "client_reference_id": WALLET,
    }
    body.update(extra)
    return body


async def apply(kv: Any, policy: Any, body: str, *, env: Any, ctx: Ctx,
                ledger: Any = None) -> Any:
    return await billing.webhook(
        payload=body, signature=signed(body), secret=WEBHOOK_SECRET,
        kv=kv, policy=policy, now=T0, service_commit=COMMIT, ledger=ledger,
        env=env, alert_ctx=ctx)


def fields(body: str) -> dict[str, list[str]]:
    return parse_qs(body, keep_blank_values=True)


def test_a_stripe_pack_sale_pushes_once_with_ttl_5(policy, pushes):
    kv = access_kv.MemoryKV()
    ctx = Ctx()
    env = alert_env()
    body = payload("checkout.session.completed", pack_obj(), "evt_sale_1")

    async def once():
        outcome = await apply(kv, policy, body, env=env, ctx=ctx)
        assert outcome.status == 200, outcome.body
        assert outcome.body["action"] == "entitled"
        assert pushes.calls == []
        await ctx.drain()
        return outcome

    outcome = run(once())
    assert outcome.body["duplicate"] is False
    assert len(pushes.calls) == 1
    url, raw = pushes.calls[0]
    assert url == "https://api.pushover.net/1/messages.json"
    form = fields(raw)
    assert form["token"] == [TOKEN]
    assert form["user"] == [USER]
    assert form["title"] == ["ModelSpec sale"]
    assert form["priority"] == ["0"]
    assert form["ttl"] == ["5"]
    assert form["message"] == ["$5.00 · 250-credit pack · card"]
    assert EMAIL not in raw
    assert API_KEY not in raw
    assert CARD not in raw
    assert WALLET not in raw
    assert "evt_sale_1" not in raw


def test_a_webhook_retry_pushes_once(policy, pushes):
    kv = access_kv.MemoryKV()
    ctx = Ctx()
    env = alert_env()
    body = payload("checkout.session.completed", pack_obj(), "evt_sale_retry")

    async def twice():
        first = await apply(kv, policy, body, env=env, ctx=ctx)
        await ctx.drain()
        second = await apply(kv, policy, body, env=env, ctx=ctx)
        await ctx.drain()
        return first, second

    first, second = run(twice())
    assert first.body["duplicate"] is False
    assert second.body["duplicate"] is True
    assert len(pushes.calls) == 1


def test_an_unpaid_session_and_a_refund_do_not_push(policy, pushes):
    kv = access_kv.MemoryKV()
    ctx = Ctx()
    env = alert_env()
    unpaid = payload(
        "checkout.session.completed",
        pack_obj(payment_status="unpaid"), "evt_unpaid")
    refund = payload("charge.refunded", {
        "id": "ch_sale", "object": "charge", "amount": 500,
        "amount_captured": 500, "amount_refunded": 500, "refunded": True,
        "currency": "usd", "customer": EMAIL, "payment_intent": "pi_sale_alert",
        "receipt_email": EMAIL,
    }, "evt_refund")

    async def both():
        skipped = await apply(kv, policy, unpaid, env=env, ctx=ctx)
        reversed_ = await apply(kv, policy, refund, env=env, ctx=ctx,
                                ledger=credits.MemoryLedger())
        await ctx.drain()
        return skipped, reversed_

    skipped, reversed_ = run(both())
    assert skipped.body["action"] == "ignored"
    assert reversed_.body["action"] == "unmatched"
    assert pushes.calls == []


def test_a_push_failure_leaves_the_sale(policy, monkeypatch, caplog):
    fetch = FetchLog(fail=True)
    monkeypatch.setattr(sale_alerts, "_fetch", fetch)
    sale_alerts._seen.clear()
    kv = access_kv.MemoryKV()
    ctx = Ctx()
    body = payload("checkout.session.completed", pack_obj(), "evt_sale_fail")

    async def once():
        with caplog.at_level(logging.ERROR):
            outcome = await apply(kv, policy, body, env=alert_env(), ctx=ctx)
            await ctx.drain()
        return outcome

    outcome = run(once())
    assert outcome.status == 200
    assert outcome.body["action"] == "entitled"
    assert outcome.body["duplicate"] is False
    assert len(fetch.calls) == 1
    assert "sale_alert_post" in caplog.text
    assert TOKEN not in caplog.text
    assert USER not in caplog.text
    assert EMAIL not in caplog.text
    stored = run(kv.get("session:cs_sale_alert"))
    assert stored is not None


def test_off_or_missing_secrets_do_not_fetch(policy, pushes):
    cases = [
        ("evt_off", "cs_off", alert_env(SALE_ALERTS_ENABLED="0")),
        ("evt_notoken", "cs_notoken", SimpleNamespace(
            SALE_ALERTS_ENABLED="1", PUSHOVER_APP_TOKEN="  ", PUSHOVER_USER_KEY=USER)),
        ("evt_absent", "cs_absent", SimpleNamespace(
            PUSHOVER_APP_TOKEN=TOKEN, PUSHOVER_USER_KEY=USER)),
    ]

    async def each():
        outcomes = []
        for event_id, session_id, env in cases:
            kv = access_kv.MemoryKV()
            ctx = Ctx()
            body = payload(
                "checkout.session.completed",
                pack_obj(id=session_id, payment_intent=f"pi_{session_id}"),
                event_id)
            outcome = await apply(kv, policy, body, env=env, ctx=ctx)
            await ctx.drain()
            outcomes.append(outcome)
        return outcomes

    outcomes = run(each())
    assert [item.status for item in outcomes] == [200, 200, 200]
    assert [item.body["action"] for item in outcomes] == ["entitled", "entitled", "entitled"]
    assert pushes.calls == []


@pytest.mark.parametrize("raw,ttl", [
    (None, "5"),
    ("", "5"),
    ("nope", "5"),
    ("5", "5"),
    ("0", "1"),
    ("1", "1"),
    ("86400", "86400"),
    ("86401", "86400"),
])
def test_ttl_clamps(pushes, raw, ttl):
    ctx = Ctx()
    extra = {} if raw is None else {"SALE_ALERT_TTL_SECONDS": raw}
    sale_alerts.notify_sale(
        alert_env(**extra), ctx, channel="card", product="Solo monthly",
        amount_usd=29, ref=f"evt-ttl-{raw}")
    run(ctx.drain())
    assert len(pushes.calls) == 1
    assert fields(pushes.calls[0][1])["ttl"] == [ttl]
    assert fields(pushes.calls[0][1])["message"] == ["$29.00 · Solo monthly · card"]


def test_x402_settle_pushes_once_and_a_replay_does_not(pushes):
    ledger = credits.MemoryLedger()
    policy = access_config.load_policy()
    facilitator = StubFacilitator()
    facilitator.transaction = TX
    facilitator.payer = WALLET
    cfg = x402.Config(
        enabled=True, mainnet=False, network=x402.NETWORK_BASE_SEPOLIA,
        asset=x402._norm_addr(x402.USDC_BASE_SEPOLIA),
        pay_to="0x209693bc6afc0c5328ba36faf03c514ef312287c",
        price_atomic=4_000,
        facilitator_url="https://api.cdp.coinbase.com/platform",
        resource_origin="https://api.modelspec.dev",
        packs=x402.packs_from_policy(policy),
    )
    payload_body = {
        "x402Version": 2,
        "accepted": {
            "scheme": "exact",
            "network": x402.NETWORK_BASE_SEPOLIA,
            "amount": "5000000",
            "asset": x402._norm_addr(x402.USDC_BASE_SEPOLIA),
            "payTo": "0x209693bc6afc0c5328ba36faf03c514ef312287c",
        },
        "payload": {
            "signature": "0x" + "11" * 65,
            "authorization": {
                "from": PAYER,
                "to": "0x209693bc6afc0c5328ba36faf03c514ef312287c",
                "value": "5000000",
                "validAfter": "0",
                "validBefore": "9999999999",
                "nonce": "0x" + "22" * 32,
            },
        },
    }
    raw = base64.b64encode(json.dumps(payload_body).encode("utf-8")).decode("ascii")
    holder = "key:" + "9" * 64
    env = alert_env()
    ctx = Ctx()

    async def buy():
        return await x402.charge(
            config=cfg, ledger=ledger, facilitator=facilitator,
            get_header=lambda name: {x402.PAYMENT_SIGNATURE.lower(): raw}.get(name.lower()),
            holder=holder, resource_url="https://api.modelspec.dev/v1/rank",
            envelope={"schema_version": "1.0", "service_commit": "test"},
            produce=_ok, env=env, alert_ctx=ctx)

    async def twice():
        first = await buy()
        await ctx.drain()
        after_sale = await ledger.balance(holder)
        second = await buy()
        await ctx.drain()
        return first, second, after_sale

    (status, _), _, balance = run(twice())
    assert status == 200
    assert balance.packs == 249
    assert len(pushes.calls) == 1
    form = fields(pushes.calls[0][1])
    assert form["message"] == ["$5.00 · 250-credit pack · x402 · tx 0x1a2b…"]
    assert form["ttl"] == ["5"]
    raw_body = pushes.calls[0][1]
    assert TX not in raw_body
    assert PAYER not in raw_body
    assert WALLET not in raw_body
    assert API_KEY not in raw_body
    assert EMAIL not in raw_body


def test_a_failed_x402_settle_does_not_push_or_credit(pushes):
    ledger = credits.MemoryLedger()
    facilitator = StubFacilitator()
    facilitator.settle_ok = False
    facilitator.transaction = TX
    cfg = x402.Config(
        enabled=True, mainnet=False, network=x402.NETWORK_BASE_SEPOLIA,
        asset=x402._norm_addr(x402.USDC_BASE_SEPOLIA),
        pay_to="0x209693bc6afc0c5328ba36faf03c514ef312287c",
        price_atomic=1000,
        facilitator_url="https://api.cdp.coinbase.com/platform",
        resource_origin="https://api.modelspec.dev",
    )
    payload_body = {
        "x402Version": 2,
        "payload": {
            "signature": "0x" + "33" * 65,
            "authorization": {
                "from": PAYER, "to": cfg.pay_to, "value": "1000",
                "validAfter": "0", "validBefore": "9999999999",
                "nonce": "0x" + "44" * 32,
            },
        },
    }
    raw = base64.b64encode(json.dumps(payload_body).encode("utf-8")).decode("ascii")
    holder = "key:" + "8" * 64
    ctx = Ctx()

    async def once():
        status, body = await x402.charge(
            config=cfg, ledger=ledger, facilitator=facilitator,
            get_header=lambda name: {x402.PAYMENT_SIGNATURE.lower(): raw}.get(name.lower()),
            holder=holder, resource_url="https://api.modelspec.dev/v1/rank",
            envelope={"schema_version": "1.0"}, produce=_ok,
            env=alert_env(), alert_ctx=ctx)
        await ctx.drain()
        return status, body

    status, body = run(once())
    assert status == 402
    assert run(ledger.balance(holder)).total == 0
    assert pushes.calls == []
    assert TX not in json.dumps(body)


def test_x402_push_failure_leaves_the_credit(monkeypatch):
    fetch = FetchLog(fail=True)
    monkeypatch.setattr(sale_alerts, "_fetch", fetch)
    sale_alerts._seen.clear()
    ledger = credits.MemoryLedger()
    facilitator = StubFacilitator()
    facilitator.transaction = "0x" + "ef" * 32
    cfg = x402.Config(
        enabled=True, mainnet=False, network=x402.NETWORK_BASE_SEPOLIA,
        asset=x402._norm_addr(x402.USDC_BASE_SEPOLIA),
        pay_to="0x209693bc6afc0c5328ba36faf03c514ef312287c",
        price_atomic=1000,
        facilitator_url="https://api.cdp.coinbase.com/platform",
        resource_origin="https://api.modelspec.dev",
    )
    payload_body = {
        "x402Version": 2,
        "payload": {
            "signature": "0x" + "55" * 65,
            "authorization": {
                "from": PAYER, "to": cfg.pay_to, "value": "3000",
                "validAfter": "0", "validBefore": "9999999999",
                "nonce": "0x" + "66" * 32,
            },
        },
    }
    raw = base64.b64encode(json.dumps(payload_body).encode("utf-8")).decode("ascii")
    holder = "key:" + "7" * 64
    ctx = Ctx()

    async def once():
        status, _ = await x402.charge(
            config=cfg, ledger=ledger, facilitator=facilitator,
            get_header=lambda name: {x402.PAYMENT_SIGNATURE.lower(): raw}.get(name.lower()),
            holder=holder, resource_url="https://api.modelspec.dev/v1/rank",
            envelope={"schema_version": "1.0"}, produce=_ok,
            env=alert_env(), alert_ctx=ctx)
        before = (await ledger.balance(holder)).available
        await ctx.drain()
        after = (await ledger.balance(holder)).available
        return status, before, after

    status, before, after = run(once())
    assert status == 200
    assert before == 2
    assert after == before
    assert len(fetch.calls) == 1


def test_worker_fetch_posts_form_with_a_short_timeout(monkeypatch):
    seen: dict[str, Any] = {}
    js = sys.modules.get("js")
    created = js is None
    if created:
        js = __import__("types").ModuleType("js")
        monkeypatch.setitem(sys.modules, "js", js)

    class _Signal:
        @staticmethod
        def timeout(ms: int) -> dict[str, int]:
            seen["timeout"] = ms
            return {"ms": ms}

    class _Object:
        @staticmethod
        def fromEntries(pairs: Any) -> dict[str, Any]:
            return dict(pairs)

    async def fetch(url: str, options: dict[str, Any]) -> SimpleNamespace:
        seen["url"] = url
        seen["options"] = options
        return SimpleNamespace(status=200)

    monkeypatch.setattr(js, "AbortSignal", _Signal, raising=False)
    monkeypatch.setattr(js, "Object", _Object, raising=False)
    monkeypatch.setattr(js, "fetch", fetch, raising=False)
    ffi = __import__("types").ModuleType("pyodide.ffi")

    def to_js(value: Any, dict_converter: Any = None) -> Any:
        if dict_converter is not None and isinstance(value, dict):
            return dict_converter(list(value.items()))
        return value

    ffi.to_js = to_js
    pyodide = __import__("types").ModuleType("pyodide")
    pyodide.__path__ = []
    pyodide.ffi = ffi
    monkeypatch.setitem(sys.modules, "pyodide", pyodide)
    monkeypatch.setitem(sys.modules, "pyodide.ffi", ffi)
    sale_alerts._seen.clear()
    ctx = Ctx()
    sale_alerts.notify_sale(
        alert_env(), ctx, channel="card", product="250-credit pack",
        amount_usd=5, ref="evt_real_fetch")
    run(ctx.drain())
    assert seen["timeout"] == 5000
    assert seen["url"] == "https://api.pushover.net/1/messages.json"
    assert seen["options"]["method"] == "POST"
    assert seen["options"]["headers"]["content-type"] == "application/x-www-form-urlencoded"
    assert fields(seen["options"]["body"])["message"] == ["$5.00 · 250-credit pack · card"]
    assert "AbortSignal.timeout" in inspect.getsource(sale_alerts._fetch)


def test_sale_alerts_ship_off():
    text = (REPO_ROOT / "api" / "worker" / "wrangler.jsonc").read_text(encoding="utf-8")
    live = "\n".join(line for line in text.splitlines() if not line.lstrip().startswith("//"))
    config = json.loads(live)
    assert config["vars"]["SALE_ALERTS_ENABLED"] == "0"
    assert config["vars"]["SALE_ALERT_TTL_SECONDS"] == "5"
    assert config["env"]["staging"]["vars"]["SALE_ALERTS_ENABLED"] == "0"
    assert config["env"]["staging"]["vars"]["SALE_ALERT_TTL_SECONDS"] == "5"
    assert "PUSHOVER_APP_TOKEN" not in live
    assert "PUSHOVER_USER_KEY" not in live


class _Bind:
    def __init__(self) -> None:
        self.values: dict[str, str] = {}

    async def get(self, name: str) -> str | None:
        return self.values.get(name)

    async def put(self, name: str, value: str, options: Any = None) -> None:
        self.values[name] = value

    async def delete(self, name: str) -> None:
        self.values.pop(name, None)


def test_entry_passes_env_and_ctx_into_the_stripe_webhook(monkeypatch):
    import importlib.util
    import types

    fetch = FetchLog()
    monkeypatch.setattr(sale_alerts, "_fetch", fetch)
    sale_alerts._seen.clear()
    saved = {name: sys.modules.get(name) for name in ("js", "workers")}
    js = types.ModuleType("js")

    async def _no_fetch(url, options=None):
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
    sys.modules["js"] = js
    sys.modules["workers"] = workers
    spec = importlib.util.spec_from_file_location(
        "modelspec_worker_entry_sale_alerts", WORKER_SRC / "entry.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    try:
        assert spec.loader is not None
        spec.loader.exec_module(module)
        env = SimpleNamespace(
            BUILD_COMMIT=COMMIT, EXPORT_ORIGIN="https://modelspec.test",
            ACCESS_ENFORCED="false", BILLING_ENABLED="true",
            STRIPE_WEBHOOK_SECRET=WEBHOOK_SECRET,
            STRIPE_SECRET_KEY="sk_test_fixture",
            TIER_POLICY=(REPO_ROOT / "api" / "worker" / "tiers.json").read_text(
                encoding="utf-8"),
            CREDITS=credits.MemoryLedger(),
            ACCESS=_Bind(),
            SALE_ALERTS_ENABLED="1",
            PUSHOVER_APP_TOKEN=TOKEN,
            PUSHOVER_USER_KEY=USER,
        )
        worker = module.Default()
        worker.env = env
        ctx = Ctx()
        worker.ctx = ctx
        body = payload(
            "checkout.session.completed",
            pack_obj(id="cs_entry_sale", payment_intent="pi_entry_sale"),
            "evt_entry_sale")
        header = billing_stripe.sign_header(
            body, WEBHOOK_SECRET, int(datetime.now(UTC).timestamp()))

        class _Req:
            def __init__(self, path: str, method: str, raw: str,
                         headers: dict[str, str]) -> None:
                self.url = f"https://api.modelspec.test{path}"
                self.method = method
                self._body = raw
                lowered = {key.lower(): value for key, value in headers.items()}
                self.headers = SimpleNamespace(
                    get=lambda name: lowered.get(name.lower()))

            async def text(self) -> str:
                return self._body

        async def once():
            response = await worker.fetch(_Req(
                "/v1/billing/stripe-webhook", "POST", body,
                {"stripe-signature": header}))
            assert fetch.calls == []
            await ctx.drain()
            return response

        response = run(once())
    finally:
        sys.modules.pop(spec.name, None)
        for name, value in saved.items():
            if value is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = value

    assert response.status == 200
    assert response.json()["action"] == "entitled"
    assert len(fetch.calls) == 1
    assert fields(fetch.calls[0][1])["message"] == ["$5.00 · 250-credit pack · card"]
    assert EMAIL not in fetch.calls[0][1]


async def _ok() -> tuple[int, dict[str, Any]]:
    return 200, {"schema_version": "1.0", "result": [{"model_id": "example/ok"}]}
