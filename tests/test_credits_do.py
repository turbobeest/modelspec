"""CreditsObject against the row shapes the Workers Python runtime returns.

Under Pyodide, `ctx.storage.sql.exec(...).one()` hands back a JsProxy of a
JavaScript object, not a Python dict or tuple: `row[0]` raises TypeError. The
first read after any write took the whole Worker down with a 1101 (found in
the MODEL-93 end-to-end test, 2026-09-19).
"""

from __future__ import annotations

import asyncio
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "api" / "worker" / "src"))

import credits  # noqa: E402
import credits_do  # noqa: E402
import x402  # noqa: E402
from tests.test_credits import _cfg, _ok, _boom, ENVELOPE, RESOURCE  # noqa: E402
from x402_facilitator import StubFacilitator  # noqa: E402


class JsObjectProxy:
    """What Pyodide returns for `{v: "..."}`: attribute access and to_py(),
    no integer indexing."""

    def __init__(self, fields: dict[str, str]):
        self._fields = fields

    def __getattr__(self, name: str):
        try:
            return self._fields[name]
        except KeyError:
            raise AttributeError(name) from None

    def to_py(self) -> dict[str, str]:
        return dict(self._fields)


class Cursor:
    def __init__(self, row):
        self._row = row

    def one(self):
        if self._row is None:
            raise RuntimeError("Expected exactly one result from SQL query, but got no results.")
        return self._row


class Sql:
    def __init__(self, row_type):
        self.table: dict[str, str] = {}
        self.row_type = row_type

    def exec(self, query: str, *params):
        if query.startswith("INSERT"):
            self.table[params[0]] = params[1]
            return Cursor(None)
        if query.startswith("SELECT"):
            v = self.table.get(params[0])
            return Cursor(None if v is None else self.row_type(v))
        return Cursor(None)


class Ctx:
    def __init__(self, row_type):
        self.storage = type("Storage", (), {"sql": Sql(row_type)})()
        self._gate = asyncio.Lock()

    async def blockConcurrencyWhile(self, callback):
        async with self._gate:
            return await callback()


def _round_trip(row_type) -> dict:
    obj = credits_do.CreditsObject(Ctx(row_type), env=None)
    asyncio.run(obj.set_monthly("key:abc", 4000, "in_1", "Solo"))
    return asyncio.run(obj.balance("key:abc", ""))


def test_ledger_reads_back_a_js_object_row():
    bal = _round_trip(lambda v: JsObjectProxy({"v": v}))
    assert bal["monthly"] == 4000


def test_ledger_reads_back_dict_and_tuple_rows():
    assert _round_trip(lambda v: {"v": v})["monthly"] == 4000
    assert _round_trip(lambda v: (v,))["monthly"] == 4000


def _ledger(obj):
    def id_from_name(name):
        assert name == "ledger"
        return name

    return credits.DurableLedger(SimpleNamespace(idFromName=id_from_name, get=lambda _id: obj))


def test_a_one_shot_payment_is_credited_and_spent_in_one_step():
    obj = credits_do.CreditsObject(Ctx(lambda v: {"v": v}), env=None)
    ledger = _ledger(obj)

    result = asyncio.run(ledger.spend_paid("payer:0xabc", "x402:n1", 1, "0xtx"))

    assert result.credited is True
    state = credits.LedgerState.from_json(json.loads(obj._get("state")))
    assert len(state.accounts) == 1
    assert state.balance("payer:0xabc").available == 0
    assert state.seen("x402:n1") is True


def test_a_live_ledger_rpc_error_reaches_the_caller():
    async def credit(*_args):
        raise RuntimeError("bad payment id ledger-sealed: live")

    ledger = _ledger(SimpleNamespace(credit=credit))
    with pytest.raises(RuntimeError, match="bad payment id"):
        asyncio.run(ledger.credit("key:a", "x402:ledger-sealed: live", 1, "tx"))


def test_existing_state_survives_with_unused_move_and_lease_rows():
    ctx = Ctx(lambda v: {"v": v})
    state = credits.LedgerState()
    state.credit("key:a", "pack:old", 10, "tx-old", source="pack")
    unused = {"move": '{"role":"live","imported":"old-digest"}',
              "leases": '{"old-lease":9999999999}'}
    ctx.storage.sql.table.update({"state": json.dumps(state.to_json()), **unused})
    original_exec = ctx.storage.sql.exec

    def state_only(query, *params):
        if query.startswith(("SELECT", "INSERT")):
            assert params[0] == "state"
        return original_exec(query, *params)

    ctx.storage.sql.exec = state_only
    ledger = _ledger(credits_do.CreditsObject(ctx, env=None))
    assert asyncio.run(ledger.balance("key:a")).available == 10
    assert not asyncio.run(ledger.credit("key:a", "pack:old", 10, "tx-old", source="pack")).credited
    held = asyncio.run(ledger.reserve("key:a", 3))
    assert held.ok
    assert asyncio.run(ledger.commit("key:a", held.reservation_id)).ok

    restarted = _ledger(credits_do.CreditsObject(ctx, env=None))
    assert asyncio.run(restarted.balance("key:a")).available == 7
    assert {key: ctx.storage.sql.table[key] for key in unused} == unused
    assert set(ctx.storage.sql.table) == {"state", "move", "leases"}


def test_rotation_transfer_progress_survives_restart():
    async def scenario():
        ctx = Ctx(lambda v: {"v": v})
        first = _ledger(credits_do.CreditsObject(ctx, env=None))
        await first.set_monthly("key:first", 100, "in_rotation", "Solo")
        await first.save_rotation("key:first", {
            "nonce": "fixture-nonce", "stage": "prepared"})
        assert await first.transfer("key:first", "key:second")

        restarted = _ledger(credits_do.CreditsObject(ctx, env=None))
        assert await restarted.rotation_state("key:first") == {
            "nonce": "fixture-nonce", "stage": "transferred"}
        assert await restarted.rotation_state("key:second") is None
        assert (await restarted.balance("key:first")).available == 0
        assert (await restarted.balance("key:second")).available == 100
        assert not await restarted.transfer("key:first", "key:second")
        assert (await restarted.balance("key:second")).available == 100

    asyncio.run(scenario())


def test_independent_clients_rotate_one_key():
    import access_config
    import access_keys
    import billing
    from access_kv import MemoryKV
    from datetime import UTC, datetime

    class YieldingKV(MemoryKV):
        async def get(self, name):
            value = await super().get(name)
            await asyncio.sleep(0)
            return value

        async def put(self, name, value, **kwargs):
            await super().put(name, value, **kwargs)
            await asyncio.sleep(0)

    async def scenario():
        kv = YieldingKV()
        policy = access_config.load_policy()
        now = datetime(2026, 9, 17, tzinfo=UTC)
        key, _ = await access_keys.issue(
            kv, tier="paid", owner="fixture", now=now, policy=policy)
        holder = credits.holder_from_fingerprint(access_keys.fingerprint(key))
        ctx = Ctx(lambda v: {"v": v})
        obj = credits_do.CreditsObject(ctx, SimpleNamespace(ACCESS=kv))
        clients = [_ledger(obj), _ledger(obj)]
        await clients[0].set_monthly(holder, 100, "in_clients", "Solo")

        results = await asyncio.gather(*(
            billing.rotate(api_key=key, kv=kv, policy=policy, now=now,
                           service_commit="test", ledger=client)
            for client in clients))
        assert sorted(result.status for result in results) == [200, 403]
        successes = [result for result in results if result.status == 200]
        assert len(successes) == 1
        new_key = successes[0].body["key"]
        new_holder = credits.holder_from_fingerprint(access_keys.fingerprint(new_key))
        assert (await clients[0].balance(new_holder)).available == 100
        persisted = json.dumps(ctx.storage.sql.table)
        assert key not in persisted and new_key not in persisted

        restarted = _ledger(credits_do.CreditsObject(ctx, SimpleNamespace(ACCESS=kv)))
        replay = await billing.rotate(
            api_key=key, kv=kv, policy=policy, now=now,
            service_commit="test", ledger=restarted)
        assert replay.status == 403

    asyncio.run(scenario())


@pytest.mark.parametrize("after_write", [False, True])
def test_rotation_resumes_after_object_restart(after_write):
    import access_config
    import access_keys
    import billing
    from access_kv import MemoryKV
    from datetime import UTC, datetime

    class InterruptedKV(MemoryKV):
        failed_name = ""

        async def put(self, name, value, **kwargs):
            interrupted = name == self.failed_name
            if interrupted and not after_write:
                raise OSError("fixture write unavailable")
            await super().put(name, value, **kwargs)
            if interrupted:
                raise OSError("fixture write unavailable")

    async def scenario():
        kv = InterruptedKV()
        policy = access_config.load_policy()
        now = datetime(2026, 9, 17, tzinfo=UTC)
        key, _ = await access_keys.issue(
            kv, tier="paid", owner="fixture", now=now, policy=policy)
        holder = credits.holder_from_fingerprint(access_keys.fingerprint(key))
        ctx = Ctx(lambda v: {"v": v})
        env = SimpleNamespace(ACCESS=kv)
        ledger = _ledger(credits_do.CreditsObject(ctx, env))
        await ledger.set_monthly(holder, 100, "in_restart", "Solo")
        kv.failed_name = access_keys.storage_name(key)

        with pytest.raises(OSError, match="fixture write"):
            await billing.rotate(
                api_key=key, kv=kv, policy=policy, now=now,
                service_commit="test", ledger=ledger)

        kv.failed_name = ""
        restarted = _ledger(credits_do.CreditsObject(ctx, env))
        result = await billing.rotate(
            api_key=key, kv=kv, policy=policy, now=now,
            service_commit="test", ledger=restarted)
        assert result.status == 200
        new_holder = credits.holder_from_fingerprint(
            access_keys.fingerprint(result.body["key"]))
        assert (await restarted.balance(holder)).available == 0
        assert (await restarted.balance(new_holder)).available == 100
        assert not (await access_keys.lookup(kv, key)).active
        assert await restarted.rotation_state(holder) == {"stage": "complete"}

    asyncio.run(scenario())


async def _paid_claim(kind, kv):
    import tests.test_billing as billing_tests

    policy = billing_tests.access_config.load_policy()
    ctx = Ctx(lambda value: {"v": value})
    env = SimpleNamespace(ACCESS=kv)
    obj = credits_do.CreditsObject(ctx, env)
    ledger = _ledger(obj)
    checkout = billing_tests.checkout_obj()
    if kind == "pack":
        checkout.update(mode="payment", subscription="", payment_intent="pi_claim_fixture",
                        metadata={"modelspec_price_id": billing_tests.PACK5})
    result = await billing_tests.apply(
        kv, policy, billing_tests.payload("checkout.session.completed", checkout, "evt_claim"),
        ledger=ledger)
    assert result.status == 200
    return billing_tests, policy, ctx, env, obj, ledger


async def _claim_purchase(billing_tests, policy, kv, ledger):
    return await billing_tests.billing.claim(
        session_id=billing_tests.SESSION, kv=kv, policy=policy,
        now=billing_tests.T0, service_commit=billing_tests.COMMIT, ledger=ledger)


@pytest.mark.parametrize("kind,units", [("plan", 4000), ("pack", 1250)])
def test_independent_clients_claim_one_funded_key(kind, units):
    from access_kv import MemoryKV
    import access_billing

    class YieldingKV(MemoryKV):
        async def get(self, name):
            result = await super().get(name)
            await asyncio.sleep(0)
            return result

        async def put(self, name, value, **kwargs):
            await super().put(name, value, **kwargs)
            await asyncio.sleep(0)

    async def scenario():
        kv = YieldingKV()
        t, policy, ctx, env, obj, ledger = await _paid_claim(kind, kv)
        results = await asyncio.gather(*(
            _claim_purchase(t, policy, kv, _ledger(obj)) for _ in range(2)))
        assert sorted(result.status for result in results) == [200, 410]
        successes = [result for result in results if result.status == 200]
        assert len(successes) == 1
        key = successes[0].body["key"]
        fingerprint = t.keys.fingerprint(key)
        holder = credits.holder_from_fingerprint(fingerprint)
        assert (await ledger.balance(holder)).available == units
        sub_id = t.SUB if kind == "plan" else f"pack:{t.SESSION}"
        subscription = await access_billing.load_subscription(kv, sub_id)
        assert subscription.key_fingerprint == fingerprint
        assert key not in json.dumps(ctx.storage.sql.table)
        assert key not in json.dumps(kv.data)
        restarted = _ledger(credits_do.CreditsObject(ctx, env))
        assert (await _claim_purchase(t, policy, kv, restarted)).status == 410

    asyncio.run(scenario())


@pytest.mark.parametrize("kind,units", [("plan", 4000), ("pack", 1250)])
def test_claim_resumes_unfunded_selection_after_restart(kind, units):
    from access_kv import MemoryKV
    import access_billing

    class InterruptedKV(MemoryKV):
        fail = False

        async def put(self, name, value, **kwargs):
            if self.fail and name.startswith("keyref:"):
                raise OSError("fixture claim metadata unavailable")
            await super().put(name, value, **kwargs)

    async def scenario():
        kv = InterruptedKV()
        t, policy, ctx, env, obj, ledger = await _paid_claim(kind, kv)
        kv.fail = True
        with pytest.raises(OSError, match="fixture claim metadata"):
            await _claim_purchase(t, policy, kv, ledger)
        kv.fail = False
        restarted = _ledger(credits_do.CreditsObject(ctx, env))
        result = await _claim_purchase(t, policy, kv, restarted)
        assert result.status == 200
        fingerprint = t.keys.fingerprint(result.body["key"])
        holder = credits.holder_from_fingerprint(fingerprint)
        assert (await restarted.balance(holder)).available == units
        sub_id = t.SUB if kind == "plan" else f"pack:{t.SESSION}"
        subscription = await access_billing.load_subscription(kv, sub_id)
        assert subscription.key_fingerprint == fingerprint
        active = [json.loads(value) for name, value in kv.data.items()
                  if name.startswith("key:") and json.loads(value)["active"]]
        assert len(active) == 1

    asyncio.run(scenario())


@pytest.mark.parametrize("kind,units", [("plan", 4000), ("pack", 1250)])
def test_completed_claim_keeps_its_owner_after_restart(kind, units):
    from access_kv import MemoryKV
    import access_billing

    async def scenario():
        kv = MemoryKV()
        t, policy, ctx, env, obj, ledger = await _paid_claim(kind, kv)
        execute = ctx.storage.sql.exec

        def interrupted_save(query, *params):
            result = execute(query, *params)
            if query.startswith("INSERT"):
                state = json.loads(params[1])
                if any(payment.get("claim", {}).get("stage") == "complete"
                       for payment in state["payments"].values()):
                    raise OSError("fixture completion response unavailable")
            return result

        ctx.storage.sql.exec = interrupted_save
        with pytest.raises(OSError, match="fixture completion response"):
            await _claim_purchase(t, policy, kv, ledger)
        ctx.storage.sql.exec = execute
        restarted = _ledger(credits_do.CreditsObject(ctx, env))
        replay = await _claim_purchase(t, policy, kv, restarted)
        sub_id = t.SUB if kind == "plan" else f"pack:{t.SESSION}"
        subscription = await access_billing.load_subscription(kv, sub_id)
        assert replay.status == 200
        assert t.keys.fingerprint(replay.body["key"]) == subscription.key_fingerprint
        holder = credits.holder_from_fingerprint(subscription.key_fingerprint)
        assert (await restarted.balance(holder)).available == units
        assert len([name for name in kv.data if name.startswith("key:")]) == 1
        assert (await _claim_purchase(t, policy, kv, restarted)).status == 410

    asyncio.run(scenario())


@pytest.mark.parametrize("kind", ["monthly", "pack"])
def test_selected_claim_holder_is_the_only_funding_owner(kind):
    async def scenario():
        ctx = Ctx(lambda value: {"v": value})
        ledger = _ledger(credits_do.CreditsObject(ctx, env=None))
        payment_id = "claim_selected"
        await ledger.save_claim(payment_id, {
            "holder": "key:selected", "record": {}, "stage": "prepared"},
            kind=kind, units=100, tx="fixture")
        if kind == "monthly":
            rejected = await ledger.set_monthly("key:other", 100, payment_id)
            accepted = await ledger.set_monthly("key:selected", 100, payment_id)
        else:
            rejected = await ledger.credit("key:other", payment_id, 100, "fixture")
            accepted = await ledger.credit("key:selected", payment_id, 100, "fixture")
        assert rejected.credited is False and rejected.reason == "conflict"
        assert accepted.credited is True
        await ledger.save_claim(payment_id, {
            "holder": "key:other", "record": {}, "stage": "prepared"},
            kind=kind, units=100, tx="fixture")
        restarted = _ledger(credits_do.CreditsObject(ctx, env=None))
        assert await restarted.claim_state(payment_id) == {"stage": "complete"}
        assert (await restarted.payment(payment_id))["holder"] == "key:selected"
        assert (await restarted.balance("key:selected")).available == 100
        assert (await restarted.balance("key:other")).available == 0

    asyncio.run(scenario())


@pytest.mark.parametrize("explicit", [False, True])
def test_claim_requires_a_configured_ledger(explicit):
    from access_kv import CloudflareKV, MemoryKV

    async def scenario():
        kv = MemoryKV()
        t, policy, ctx, env, obj, ledger = await _paid_claim("plan", kv)
        result = await t.billing.claim(
            session_id=t.SESSION, kv=kv if explicit else CloudflareKV(kv),
            policy=policy, now=t.T0, service_commit=t.COMMIT,
            ledger=credits.UnboundLedger() if explicit else None)
        assert result.status == 503
        assert not [name for name in kv.data if name.startswith("key:")]

    asyncio.run(scenario())


def test_unbound_watermark_is_not_a_stored_period():
    async def scenario():
        with pytest.raises(credits.StoreNotConfigured):
            await credits.UnboundLedger().invoice_watermark("holder")

    asyncio.run(scenario())


def test_plan_claim_funds_invoice_and_completes_selection_together():
    async def scenario():
        ctx = Ctx(lambda value: {"v": value})
        ledger = _ledger(credits_do.CreditsObject(ctx, env=None))
        await ledger.save_claim("claim:subscription", {
            "holder": "key:selected", "units": 100, "stage": "prepared"},
            kind="monthly", units=100, tx="session")
        refused = await ledger.fund_claim(
            "key:other", "claim:subscription", "in_initial", 100, "Solo")
        assert not refused.credited and refused.reason == "conflict"
        result = await ledger.fund_claim(
            "key:selected", "claim:subscription", "in_initial", 100, "Solo")
        assert result.credited
        restarted = _ledger(credits_do.CreditsObject(ctx, env=None))
        assert await restarted.claim_state("claim:subscription") == {"stage": "complete"}
        assert (await restarted.payment("in_initial"))["holder"] == "key:selected"
        reserved = await restarted.reserve("key:selected", 10)
        assert reserved.ok
        assert (await restarted.commit("key:selected", reserved.reservation_id)).ok
        replay = await restarted.set_monthly("key:selected", 100, "in_initial", "Solo")
        assert not replay.credited
        assert (await restarted.balance("key:selected")).monthly == 90

    asyncio.run(scenario())


def test_claim_completion_survives_earlier_checkout_metadata_reads():
    from access_kv import MemoryKV
    import tests.test_billing as t

    class EarlierKV(MemoryKV):
        def __init__(self):
            super().__init__()
            self.earlier = {}
            self.replay_earlier = False

        async def put(self, name, value, **kwargs):
            if name.startswith(("sub:", "session:")) and name not in self.earlier:
                earlier = json.loads(value)
                earlier.pop("pending_invoice_id", None)
                self.earlier[name] = json.dumps(earlier)
            await super().put(name, value, **kwargs)

        async def get(self, name):
            if self.replay_earlier and name in self.earlier:
                return self.earlier[name]
            return await super().get(name)

    async def scenario():
        kv = EarlierKV()
        ctx = Ctx(lambda value: {"v": value})
        env = SimpleNamespace(ACCESS=kv)
        ledger = _ledger(credits_do.CreditsObject(ctx, env))
        policy = t.access_config.load_policy()
        checkout = t.checkout_obj(invoice="in_initial")
        assert (await t.apply(kv, policy, t.payload(
            "checkout.session.completed", checkout, "evt_initial"), ledger=ledger)).status == 200
        first = await _claim_purchase(t, policy, kv, ledger)
        assert first.status == 200
        kv.replay_earlier = True
        restarted = _ledger(credits_do.CreditsObject(ctx, env))
        second = await _claim_purchase(t, policy, kv, restarted)
        assert second.status == 410
        assert len([name for name in kv.data if name.startswith("key:")]) == 1

    asyncio.run(scenario())

def durable():
    return _ledger(credits_do.CreditsObject(Ctx(lambda v: JsObjectProxy({"v": v})), None))


@pytest.mark.parametrize('status', [200, 500])
def test_key_rotation_during_response_finishes_reservation(status):
    async def scenario():
        ledger = durable()
        src, dst = 'key:old', 'key:new'
        assert (await ledger.set_monthly(src, 10, 'in_rotation', 'Solo')).credited
        async def produce():
            assert await ledger.transfer(src, dst)
            return await (_ok() if status == 200 else _boom())
        result = await x402.charge(
            config=_cfg(enabled=False), ledger=ledger, facilitator=StubFacilitator(),
            get_header=lambda _: None, holder=src, resource_url=RESOURCE,
            envelope=ENVELOPE, produce=produce, units=5,
        )
        assert result[0] == status
        actual = await ledger.balance(dst)
        assert actual.reserved == 0, actual.to_json()
        assert actual.available == (5 if status == 200 else 10)
        assert (await ledger.balance(src)).available == 0
    asyncio.run(scenario())

def test_rotated_failed_catalog_read_returns_its_credit():
    async def scenario():
        ledger, src, dst = durable(), 'key:old-read', 'key:new-read'
        assert (await ledger.set_monthly(src, 10, 'in_read_rotation', 'Solo')).credited
        taken = await ledger.take_read(src, 10, 100, 10)
        assert taken.ok and taken.token is not None
        assert await ledger.transfer(src, dst)
        released = await ledger.release_read(src, taken.token)
        actual = await ledger.balance(dst)
        assert actual.available == 10, (released, actual.to_json())
    asyncio.run(scenario())


@pytest.mark.parametrize("kind", ["decision", "catalog"])
@pytest.mark.parametrize("success", [True, False])
def test_transferred_tokens_complete_once_across_merges(kind, success):
    async def scenario():
        ledger = durable()
        holders = ["key:first", "key:second", "key:third"]
        pending = []
        for i, who in enumerate(holders):
            await ledger.set_monthly(who, 10, f"in_merge_{i}", "Solo")
            taken = (await ledger.reserve(who, 2) if kind == "decision"
                     else await ledger.take_read(who, 10, 100, 100))
            assert taken.ok
            token = taken.reservation_id if kind == "decision" else taken.token
            assert token is not None
            pending.append((who, token))
        assert await ledger.transfer(holders[0], holders[1])
        assert await ledger.transfer(holders[1], holders[2])
        for who in holders[:2]:
            assert (await ledger.balance(who)).available == 0
            assert not (await ledger.reserve(who, 1, overage_cap=100)).ok
            assert not (await ledger.take_read(who, 10, 100, 100, overage_cap=100)).ok
        complete = ((ledger.commit if success else ledger.release) if kind == "decision"
                    else (ledger.keep_read if success else ledger.release_read))
        for who, token in pending:
            assert await complete(who, token)
            assert not await complete(who, token)
        actual = await ledger.balance(holders[-1])
        assert actual.reserved == 0
        expected = (24 if kind == "decision" else 27) if success else 30
        assert actual.available == expected
    asyncio.run(scenario())


@pytest.mark.parametrize("enabled", [False, True])
def test_charge_requires_a_confirmed_commit(enabled):
    class UnconfirmedLedger(credits.MemoryLedger):
        async def commit(self, holder, reservation_id):
            return credits.CommitResult(False)

    async def scenario():
        ledger = UnconfirmedLedger()
        await ledger.set_monthly("key:confirmation", 5, "in_confirmation", "Solo")
        with pytest.raises(RuntimeError, match="credit reservation"):
            await x402.charge(
                config=_cfg(enabled=enabled), ledger=ledger, facilitator=StubFacilitator(),
                get_header=lambda _: None, holder="key:confirmation", resource_url=RESOURCE,
                envelope=ENVELOPE, produce=_ok)
        assert (await ledger.balance("key:confirmation")).available == 5
    asyncio.run(scenario())


def test_merged_pending_overage_uses_distinct_meter_identities():
    async def scenario():
        ledger = durable()
        pending = []
        for who in ['key:meter-src', 'key:meter-dst']:
            await ledger.set_monthly(who, 0, 'in_' + who, 'Scale', 'cus_test')
            reservation = await ledger.reserve(who, 1, overage_cap=10)
            assert reservation.ok and reservation.reservation_id is not None
            pending.append((who, reservation.reservation_id))
        assert await ledger.transfer('key:meter-src', 'key:meter-dst')
        for who, token in pending:
            assert await ledger.commit(who, token)
        events = await ledger.open_meter_events('key:meter-dst')
        assert len(events) == 2
        assert len({row[0] for row in events}) == 2
    asyncio.run(scenario())


@pytest.mark.parametrize("funding", ["pack", "monthly"])
def test_pending_completion_retains_routing_during_delayed_funding(funding):
    async def scenario():
        ledger = durable()
        src, dst = "key:pending-source", "key:pending-destination"
        await ledger.set_monthly(src, 0, "in_pending", "Scale", "cus_pending")
        taken = await ledger.reserve(src, 5, overage_cap=10)
        assert taken.ok and taken.reservation_id is not None
        identifier = await ledger.meter_identifier(src, "res", taken.reservation_id)
        assert await ledger.transfer(src, dst)
        if funding == "pack":
            await ledger.credit(src, "pack_delayed", 10, "pi_delayed")
        else:
            await ledger.set_monthly(src, 10, "in_delayed", "Solo")
        assert not (await ledger.reserve(src, 1)).ok
        assert not (await ledger.take_read(src, 10, 100, 10)).ok
        assert await ledger.commit(src, taken.reservation_id)
        assert not await ledger.commit(src, taken.reservation_id)
        events = await ledger.open_meter_events(dst)
        assert len(events) == 1 and events[0][:2] == (identifier, 5)
        actual = await ledger.balance(dst)
        if funding == "pack":
            assert actual.packs == 10
            assert actual.overage_used == 5
        else:
            assert actual.monthly == 10
            assert actual.overage_used == 0
    asyncio.run(scenario())


def _funding_ledger(kind):
    if kind == "memory":
        return credits.MemoryLedger(), None
    obj = credits_do.CreditsObject(Ctx(lambda v: JsObjectProxy({"v": v})), None)
    return _ledger(obj), obj


def _funding_accounts(ledger, obj):
    if obj is None:
        return ledger.state.accounts
    return credits.LedgerState.from_json(json.loads(obj._get("state"))).accounts


@pytest.mark.parametrize("kind", ["memory", "durable"])
@pytest.mark.parametrize("funding", ["pack", "monthly", "clear"])
def test_funding_after_transfer_reaches_the_live_account(kind, funding):
    async def scenario():
        ledger, obj = _funding_ledger(kind)
        src, dst = "key:fund-src", "key:fund-dst"
        if funding == "pack":
            assert (await ledger.set_monthly(src, 0, "in_old", "Scale", "cus_fund")).credited
            opened = await ledger.reserve(src, 5, overage_cap=10)
            assert opened.ok and opened.reservation_id is not None
            assert await ledger.transfer(src, dst)
            assert (await ledger.credit(src, "pack_delayed", 7, "pi_delayed")).credited
            live = await ledger.balance(dst)
            assert live.packs == 7
            assert live.monthly == 0
            assert (await ledger.credit(src, "pack_delayed", 7, "pi_delayed")).reason == "replay"
            assert (await ledger.credit(dst, "pack_delayed", 7, "pi_delayed")).reason == "replay"
            assert (await ledger.commit(src, opened.reservation_id)).ok
            live = await ledger.balance(dst)
            assert live.packs == 7
            assert live.overage_used == 5
            drawn = await ledger.reserve(dst, 7)
            assert drawn.ok
            assert (await ledger.balance(dst)).available == 0
        elif funding == "monthly":
            assert (await ledger.set_monthly(src, 0, "in_old", "Scale", "cus_fund")).credited
            opened = await ledger.reserve(src, 5, overage_cap=10)
            assert opened.ok and opened.reservation_id is not None
            identifier = await ledger.meter_identifier(src, "res", opened.reservation_id)
            assert await ledger.transfer(src, dst)
            assert (await ledger.set_monthly(src, 10, "in_delayed", "Solo")).credited
            assert (await ledger.balance(dst)).monthly == 10
            assert (await ledger.balance(dst)).overage_used == 0
            spent = await ledger.reserve(dst, 10)
            assert spent.ok
            extra = await ledger.reserve(dst, 1, overage_cap=10)
            assert extra.ok and extra.reservation_id is not None
            assert (await ledger.set_monthly(src, 10, "in_delayed", "Solo")).reason == "replay"
            assert (await ledger.set_monthly(dst, 10, "in_delayed", "Solo")).reason == "replay"
            assert (await ledger.commit(dst, extra.reservation_id)).ok
            assert (await ledger.commit(src, opened.reservation_id)).ok
            events = await ledger.open_meter_events(dst)
            assert (identifier, 5) in [row[:2] for row in events]
            live = await ledger.balance(dst)
            assert live.monthly == 0
            assert live.overage_used == 1
        else:
            assert (await ledger.set_monthly(src, 8, "in_old", "Solo")).credited
            held = await ledger.reserve(src, 5)
            assert held.ok and held.reservation_id is not None
            assert await ledger.transfer(src, dst)
            cleared = await ledger.clear_monthly(src)
            assert cleared.credited and cleared.reason == "cleared"
            assert (await ledger.balance(dst)).monthly == 0
            assert await ledger.release(src, held.reservation_id)
            live = await ledger.balance(dst)
            assert live.monthly == 0
            assert live.available == 0
            assert live.reserved == 0
        accounts = _funding_accounts(ledger, obj)
        assert src not in accounts
        assert dst in accounts
        assert (await ledger.balance(src)).available == 0
        assert not (await ledger.reserve(src, 1)).ok
        assert not (await ledger.take_read(src, 10, 100, 10)).ok
    asyncio.run(scenario())


class _Namespace:
    """One CreditsObject, reached the way DurableLedger reaches the binding."""

    def __init__(self) -> None:
        self.obj = credits_do.CreditsObject(Ctx(lambda value: {"v": value}), env=None)

    def idFromName(self, name: str) -> str:  # noqa: N802 - the Workers API name
        return name

    def get(self, _id: str):
        return self.obj


class _LedgerSurface:
    """MemoryLedger, the durable ledger, or the credits object, one result shape."""

    def __init__(self, kind: str) -> None:
        self.kind = kind
        if kind == "memory":
            self.ledger = credits.MemoryLedger()
        elif kind == "durable":
            self.ledger = credits.DurableLedger(_Namespace())
        else:
            self.ledger = credits_do.CreditsObject(
                Ctx(lambda value: {"v": value}), env=None)

    def _result(self, value: Any) -> credits.CreditResult:
        if isinstance(value, dict):
            return credits.CreditResult.from_json(value)
        return value

    async def set_monthly(self, holder: str, units: int, invoice_id: str, **fields: Any):
        return self._result(await self.ledger.set_monthly(
            holder, units, invoice_id, fields.get("plan", ""),
            fields.get("customer_id", ""),
            period_end=int(fields.get("period_end") or 0),
            period_start=int(fields.get("period_start") or 0),
            subscription_id=str(fields.get("subscription_id") or "")))

    async def clear_monthly(self, holder: str, *, watermark: int = 0,
                            subscription_id: str = ""):
        return self._result(await self.ledger.clear_monthly(
            holder, watermark=watermark, subscription_id=subscription_id))

    async def save_claim(self, payment_id: str, holder: str) -> None:
        await self.ledger.save_claim(
            payment_id, {"holder": holder, "units": 100, "stage": "prepared"},
            kind="monthly", units=100, tx="session")

    async def fund_claim(self, holder: str, claim_id: str, invoice_id: str, *,
                         subscription_id: str):
        return self._result(await self.ledger.fund_claim(
            holder, claim_id, invoice_id, 100, "Solo", "",
            subscription_id=subscription_id))

    async def transfer(self, src: str, dst: str) -> bool:
        return bool(await self.ledger.transfer(src, dst))


async def _cancellation_id_table(surface: _LedgerSurface) -> None:
    """D5, on one ledger. A different known subscription is not stale."""
    cleared = await surface.clear_monthly("key:diff", watermark=300, subscription_id="sub_x")
    assert cleared.reason == "cleared"
    other = await surface.set_monthly("key:diff", 100, "in_diff_y", subscription_id="sub_y")
    assert other.credited, other
    reopened = await surface.set_monthly("key:diff", 100, "in_diff_x", subscription_id="sub_x")
    assert reopened.credited, reopened

    await surface.clear_monthly("key:before", watermark=300, subscription_id="sub_x")
    before = await surface.set_monthly(
        "key:before", 100, "in_before", period_start=200, period_end=400,
        subscription_id="sub_x")
    assert before.reason == "stale"

    await surface.clear_monthly("key:at", watermark=300, subscription_id="sub_x")
    at_cancel = await surface.set_monthly(
        "key:at", 100, "in_at", period_start=300, period_end=400, subscription_id="sub_x")
    assert at_cancel.credited
    assert (await surface.set_monthly(
        "key:at", 50, "in_at_follow", subscription_id="sub_x")).credited

    await surface.clear_monthly("key:after", watermark=300, subscription_id="sub_x")
    after = await surface.set_monthly(
        "key:after", 100, "in_after", period_start=360, period_end=500,
        subscription_id="sub_x")
    assert after.credited

    await surface.clear_monthly("key:noend", watermark=300, subscription_id="sub_x")
    no_end = await surface.set_monthly(
        "key:noend", 100, "in_noend", period_start=400, subscription_id="sub_x")
    assert no_end.reason == "stale"
    await surface.clear_monthly("key:bare", watermark=300, subscription_id="sub_x")
    assert (await surface.set_monthly(
        "key:bare", 100, "in_bare", subscription_id="sub_x")).reason == "stale"

    await surface.clear_monthly("key:unknown-grant", watermark=300, subscription_id="sub_x")
    assert (await surface.set_monthly(
        "key:unknown-grant", 100, "in_unknown_grant")).reason == "stale"
    await surface.clear_monthly(
        "key:unknown-grant-period", watermark=300, subscription_id="sub_x")
    assert (await surface.set_monthly(
        "key:unknown-grant-period", 100, "in_unknown_grant_period",
        period_start=360, period_end=500)).credited

    await surface.clear_monthly("key:unknown-cancel", watermark=300, subscription_id="")
    assert (await surface.set_monthly(
        "key:unknown-cancel", 100, "in_unknown_cancel", subscription_id="sub_y")).reason == "stale"
    await surface.clear_monthly("key:both", watermark=300, subscription_id="")
    assert (await surface.set_monthly("key:both", 100, "in_both")).reason == "stale"
    await surface.clear_monthly("key:both-period", watermark=300, subscription_id="")
    assert (await surface.set_monthly(
        "key:both-period", 100, "in_both_period", period_start=360, period_end=500)).credited

    await surface.clear_monthly("key:fund", watermark=300, subscription_id="sub_x")
    await surface.save_claim("claim:fund", "key:fund")
    funded = await surface.fund_claim(
        "key:fund", "claim:fund", "in_fund_y", subscription_id="sub_y")
    assert funded.credited, funded

    assert (await surface.set_monthly("key:src", 10, "in_src")).credited
    assert (await surface.clear_monthly(
        "key:src", watermark=300, subscription_id="sub_x")).reason == "cleared"
    assert (await surface.set_monthly("key:dst", 1, "in_dst")).credited
    assert await surface.transfer("key:src", "key:dst")
    moved = await surface.set_monthly("key:dst", 100, "in_moved", subscription_id="sub_y")
    assert moved.credited, moved


async def _grant_monthly_carries_the_id(surface: _LedgerSurface) -> None:
    import access_billing
    import access_config
    import access_keys
    from access_kv import MemoryKV

    kv = MemoryKV()
    policy = access_config.load_policy()
    secret, record = await access_keys.issue(
        kv, tier="paid", owner="fixture", now=datetime(2026, 6, 1, tzinfo=UTC),
        policy=policy)
    fingerprint = access_keys.fingerprint(secret)
    holder = credits.holder_from_fingerprint(fingerprint)
    await access_billing._write_sub(kv, access_billing.SubscriptionRecord(
        subscription_id="sub_y", customer_id="cus", price_id="price",
        tier="paid", status="active", key_fingerprint=fingerprint,
        key_id=record.key_id, created_at="2026-06-01T00:00:00Z",
        pending_monthly=0, plan_name="Solo", plan_credits=100))
    assert (await surface.clear_monthly(
        holder, watermark=300, subscription_id="sub_x")).reason == "cleared"
    granted = await access_billing.grant_monthly(
        kv, "sub_y", ledger=surface.ledger, units=100, invoice_id="in_grant_y",
        plan="Solo")
    assert granted == "granted"


@pytest.mark.parametrize("kind", ["memory", "durable", "object"])
def test_cancellation_subscription_id_on_every_ledger(kind):
    async def scenario():
        surface = _LedgerSurface(kind)
        await _cancellation_id_table(surface)
        if kind != "object":
            await _grant_monthly_carries_the_id(surface)

    asyncio.run(scenario())


def test_a_stored_cancellation_subscription_id_loads():
    named = credits._Account.from_json({
        "canceled_at": 300, "canceled_subscription_id": "sub_x"})
    assert named.canceled_subscription_id == "sub_x"
    assert credits._Account.from_json({"canceled_at": 300}).canceled_subscription_id == ""

    async def scenario():
        ctx = Ctx(lambda value: {"v": value})
        state = credits.LedgerState()
        state.accounts["key:held"] = credits._Account(
            canceled_at=300, canceled_subscription_id="sub_x")
        ctx.storage.sql.table["state"] = json.dumps(state.to_json())
        obj = credits_do.CreditsObject(ctx, env=None)
        loaded = credits.CreditResult.from_json(await obj.set_monthly(
            "key:held", 100, "in_loaded", "Solo", "", 0, 0, "sub_y"))
        assert loaded.credited
        ctx.storage.sql.table["state"] = json.dumps({
            "accounts": {"key:bare": {"canceled_at": 300}}, "payments": {}})
        bare = credits.CreditResult.from_json(await obj.set_monthly(
            "key:bare", 100, "in_bare_load", "Solo", "", 0, 0, "sub_y"))
        assert bare.reason == "stale"

    asyncio.run(scenario())


def test_stored_alias_accepts_later_funding_on_the_live_account():
    state = credits.LedgerState()
    assert state.set_monthly("key:src", 8, "in_old", "Solo").credited
    assert state.transfer("key:src", "key:dst")
    restored = credits.LedgerState.from_json(json.loads(json.dumps(state.to_json())))
    assert restored.set_monthly("key:src", 4, "in_later", "Solo").credited
    assert restored.balance("key:dst").monthly == 4
    assert "key:src" not in restored.accounts
    assert restored.set_monthly("key:src", 4, "in_later", "Solo").reason == "replay"
    assert restored.set_monthly("key:dst", 4, "in_later", "Solo").reason == "replay"
    assert restored.balance("key:dst").monthly == 4
    assert restored.set_monthly("key:src", 8, "in_old", "Solo").reason == "replay"


def test_durable_ledger_notes_and_reads_the_binding():
    """DurableLedger notes a binding and reads that binding back."""

    async def scenario():
        obj = credits_do.CreditsObject(Ctx(lambda value: {"v": value}), env=None)
        ledger = _ledger(obj)
        await ledger.note_key_binding("key:holder", "abc123")
        assert await ledger.key_binding("key:holder") == "abc123"

    asyncio.run(scenario())


def test_account_json_round_trips_the_binding():
    """Stored account JSON carries the binding through a round trip."""
    account = credits._Account(monthly=4, bound_fingerprint="abc123")
    restored = credits._Account.from_json(json.loads(json.dumps(account.to_json())))
    assert restored.bound_fingerprint == "abc123"
    assert restored.monthly == 4


def test_account_json_without_the_binding_field_loads_empty():
    """An account stored without the field loads an empty binding."""
    loaded = credits._Account.from_json({"monthly": 4})
    assert loaded.bound_fingerprint == ""
    assert loaded.monthly == 4


def test_transfer_onto_an_existing_account_keeps_the_binding():
    """A transfer onto an existing account carries the binding."""
    state = credits.LedgerState()
    assert state.set_monthly("key:dst", 1, "in_dst", "Solo").credited
    state.note_key_binding("key:src", "abc123")
    assert state.transfer("key:src", "key:dst")
    assert state.key_binding("key:dst") == "abc123"


def test_unbound_ledger_refuses_the_binding_note_and_read():
    """UnboundLedger refuses the binding note and the binding read."""

    async def scenario():
        ledger = credits.UnboundLedger()
        with pytest.raises(credits.StoreNotConfigured):
            await ledger.note_key_binding("key:holder", "abc123")
        with pytest.raises(credits.StoreNotConfigured):
            await ledger.key_binding("key:holder")

    asyncio.run(scenario())
