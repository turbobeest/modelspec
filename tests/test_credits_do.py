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
from pathlib import Path
from types import SimpleNamespace

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "api" / "worker" / "src"))

import credits  # noqa: E402
import credits_do  # noqa: E402


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
        assert replay.status == 410
        sub_id = t.SUB if kind == "plan" else f"pack:{t.SESSION}"
        subscription = await access_billing.load_subscription(kv, sub_id)
        holder = credits.holder_from_fingerprint(subscription.key_fingerprint)
        assert (await restarted.balance(holder)).available == units
        assert len([name for name in kv.data if name.startswith("key:")]) == 1

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
