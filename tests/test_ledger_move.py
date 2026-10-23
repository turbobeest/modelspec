"""MODEL-441: the credit ledger moves between Cloudflare accounts across a
short write freeze.

Two in-memory "accounts", each with its own CreditsObject. The operator
exports the old ledger, which seals it, and imports the copy into the new
one, which waits in standby. The properties under test: every balance
arrives, a payment credited before the move is still a duplicate after it,
at most one ledger accepts writes at any moment, and a frozen ledger fails
closed so no caller treats it as unbound.
"""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "api" / "worker" / "src"))

import credits  # noqa: E402
import credits_do  # noqa: E402
import ledger_admin  # noqa: E402

SECRET = "admin-test-secret"


class Sql:
    def __init__(self):
        self.table: dict[str, str] = {}

    def exec(self, query: str, *params):
        if query.startswith("INSERT"):
            self.table[params[0]] = params[1]
            return Cursor(None)
        if query.startswith("SELECT"):
            value = self.table.get(params[0])
            return Cursor(None if value is None else {"v": value})
        return Cursor(None)


class Cursor:
    def __init__(self, row):
        self._row = row

    def one(self):
        if self._row is None:
            raise RuntimeError("Expected exactly one result from SQL query, but got no results.")
        return self._row


class Stub:
    """An RPC stub: an error crosses the boundary as its text only."""

    def __init__(self, obj):
        self._obj = obj

    def __getattr__(self, name):
        method = getattr(self._obj, name)

        async def call(*args):
            try:
                return await method(*args)
            except Exception as exc:
                raise RuntimeError(f"PythonError: Traceback ...\n{type(exc).__name__}: {exc}") from None
        return call


class Namespace:
    def __init__(self, env):
        ctx = type("Ctx", (), {})()
        ctx.storage = type("Storage", (), {"sql": Sql()})()
        self.obj = credits_do.CreditsObject(ctx, env=env)

    def idFromName(self, name):  # noqa: N802 - the Workers API name
        assert name == "ledger"
        return name

    def get(self, _id):
        return Stub(self.obj)


class Env:
    def __init__(self, secret=SECRET, standby=False):
        self.LEDGER_ADMIN_SECRET = secret
        self.LEDGER_STANDBY = "true" if standby else ""
        self.CREDITS = Namespace(self)


def run(coro):
    return asyncio.run(coro)


def _admin(env, action, body=None, method="POST"):
    return run(ledger_admin.handle(env, ledger_admin.PREFIX + action, method,
                                   "Bearer " + SECRET, json.dumps(body or {})))


def _status(env):
    return _admin(env, "status", method="GET")[1]


def _ledger(env):
    return credits.DurableLedger(env.CREDITS)


def _balance(env, holder="key:a"):
    return run(_ledger(env).balance(holder)).available


def _credit(env, payment, units, holder="key:a"):
    return run(_ledger(env).credit(holder, payment, units, "tx-" + payment, source="pack"))


def _frozen(env):
    try:
        _balance(env)
    except credits.LedgerUnavailable:
        return True
    return False


def _copy(exported):
    return {k: exported[k] for k in ("state", "digest", "generation")}


def _move(old, new):
    exported = _admin(old, "export")[1]
    return exported, _admin(new, "import", _copy(exported))


def test_every_balance_arrives_and_the_old_ledger_freezes():
    old, new = Env(), Env(standby=True)
    _credit(old, "pack:cs_1", 500)
    run(_ledger(old).set_monthly("key:b", 4000, "in_1", "Solo"))

    exported, (status, imported) = _move(old, new)

    assert status == 200
    assert (exported["role"], imported["role"]) == ("sealed", "live")
    assert imported["digest"] == exported["digest"]
    assert imported["holders"] == exported["holders"] == 2
    assert _balance(new) == 500
    assert run(_ledger(new).balance("key:b")).monthly == 4000
    assert _frozen(old)


def test_a_payment_credited_before_the_move_is_a_duplicate_after_it():
    old, new = Env(), Env(standby=True)
    _credit(old, "pack:cs_1", 500)
    _move(old, new)

    assert _credit(new, "pack:cs_1", 500).credited is False
    assert _balance(new) == 500


def test_the_receiving_ledger_serves_nothing_before_its_import():
    new = Env(standby=True)

    assert _frozen(new)
    assert _status(new)["role"] == "standby"


def test_export_and_import_can_be_rerun_and_the_copy_only_lands_once():
    old, new = Env(), Env(standby=True)
    _credit(old, "pack:cs_1", 5)
    first, _ = _move(old, new)
    _credit(new, "pack:cs_2", 7)

    again, (status, imported) = _move(old, new)

    assert again["digest"] == first["digest"]
    assert status == 200
    assert _balance(new) == 12


def test_only_a_standby_ledger_accepts_a_copy():
    old, other = Env(), Env()
    _credit(old, "pack:cs_1", 5)
    _credit(other, "pack:cs_9", 1)
    exported = _admin(old, "export")[1]

    status, body = _admin(other, "import", _copy(exported))
    tampered = _admin(Env(standby=True), "import", {**_copy(exported), "digest": "0" * 64})

    assert (status, body["error"]["code"]) == (409, "import_refused")
    assert (tampered[0], tampered[1]["error"]["code"]) == (409, "import_refused")
    assert _balance(other) == 1


def test_a_restart_between_the_state_and_the_record_leaves_a_ledger_that_imports_again():
    old, new = Env(), Env(standby=True)
    _credit(old, "pack:cs_1", 5)
    exported = _admin(old, "export")[1]
    new.CREDITS.obj._save(credits.LedgerState.from_json(json.loads(exported["state"])))

    assert _status(new)["role"] == "standby"
    assert _admin(new, "import", _copy(exported))[1]["role"] == "live"
    assert _balance(new) == 5


def test_a_rollback_seals_the_new_ledger_and_unseals_the_old_only_with_its_digest():
    old, new = Env(), Env(standby=True)
    _credit(old, "pack:cs_1", 5)
    exported, _ = _move(old, new)

    resealed = _admin(new, "export")[1]
    assert resealed["digest"] == exported["digest"]
    assert _admin(old, "unseal", {"digest": "0" * 64})[0] == 409
    assert _admin(old, "unseal", {"digest": exported["digest"]})[1]["role"] == "live"

    assert _frozen(new)
    assert _balance(old) == 5


def test_the_admin_paths_need_their_secret():
    env = Env()
    no_secret = Env(secret="")

    assert run(ledger_admin.handle(no_secret, ledger_admin.PREFIX + "status", "GET", "", ""))[0] == 404
    assert run(ledger_admin.handle(env, ledger_admin.PREFIX + "export", "POST", "Bearer wrong", ""))[0] == 401
    assert _admin(env, "call", {"method": "credit"})[0] == 404
    assert _status(env)["role"] == "live"


class EchoingStub(Stub):
    """A ledger method whose error message echoes caller input."""

    def __getattr__(self, name):
        if name == "credit":
            async def call(*_args):
                raise RuntimeError("PythonError: ValueError: bad payment id ledger-sealed: live")
            return call
        return super().__getattr__(name)


def test_a_seal_mark_echoed_in_an_error_does_not_pass_for_a_freeze():
    env = Env()
    namespace = env.CREDITS
    namespace.get = lambda _id: EchoingStub(namespace.obj)

    try:
        run(_ledger(env).credit("key:a", "x402:ledger-sealed: live", 1, "tx"))
    except credits.LedgerUnavailable:
        raise AssertionError("a live ledger's own error must surface") from None
    except RuntimeError as exc:
        assert "bad payment id" in str(exc)


def test_a_request_in_flight_at_the_export_is_not_charged_and_strands_nothing():
    old, new = Env(), Env(standby=True)
    _credit(old, "pack:cs_1", 10)
    held = run(_ledger(old).reserve("key:a", 3))
    assert held.ok and _balance(old) == 7

    _move(old, new)

    try:
        run(_ledger(old).commit("key:a", held.reservation_id))
    except credits.LedgerUnavailable:
        pass
    else:
        raise AssertionError("a frozen ledger must refuse the commit")
    assert run(_ledger(new).balance("key:a")).reserved == 0
    assert _balance(new) == 10


# ── Codex review REV-895: the freeze holds on every path ─────────────────────

sys.path.insert(0, str(Path(__file__).resolve().parent))
import access_config  # noqa: E402
import access_keys  # noqa: E402
import billing  # noqa: E402
import test_billing as tb  # noqa: E402
from access_kv import MemoryKV  # noqa: E402


def _webhook(kv, policy, body, ledger):
    return run(tb.apply(kv, policy, body, ledger=ledger))


def test_a_standby_ledger_that_already_holds_balances_refuses_a_copy():
    old, new = Env(), Env()
    _credit(old, "pack:cs_1", 5)
    _credit(new, "pack:cs_9", 777)
    new.LEDGER_STANDBY = "true"
    exported = _admin(old, "export")[1]

    status, body = _admin(new, "import", _copy(exported))

    assert (status, body["error"]["code"]) == (409, "import_refused")
    new.LEDGER_STANDBY = ""
    assert _balance(new) == 777


def test_a_webhook_during_the_freeze_writes_nothing_and_is_not_remembered():
    policy = access_config.load_policy()
    kv = MemoryKV()
    frozen = Env()
    _admin(frozen, "export")
    body = tb.payload("checkout.session.completed", tb.checkout_obj(), "evt_frozen_1")

    outcome = _webhook(kv, policy, body, _ledger(frozen))

    assert outcome.status == 503
    assert kv.data == {}


def test_a_cancellation_during_the_freeze_keeps_the_key_and_its_subscription():
    policy = access_config.load_policy()
    kv = MemoryKV()
    env = Env()
    _webhook(kv, policy, tb.payload("checkout.session.completed", tb.checkout_obj(), "evt_c1"),
             _ledger(env))
    key = run(billing.claim(session_id=tb.SESSION, kv=kv, policy=policy, now=tb.T0,
                            service_commit=tb.COMMIT, ledger=_ledger(env))).body["key"]
    before = dict(kv.data)
    _admin(env, "export")
    cancel = tb.payload("customer.subscription.deleted",
                        {"id": tb.SUB, "object": "subscription", "customer": tb.CUS,
                         "status": "canceled"}, "evt_c2")

    outcome = _webhook(kv, policy, cancel, _ledger(env))

    assert outcome.status == 503
    assert kv.data == before
    assert tb.serve(key, kv, policy).tier == "paid"


def test_claim_and_rotate_during_the_freeze_write_nothing():
    policy = access_config.load_policy()
    kv = MemoryKV()
    env = Env()
    _webhook(kv, policy, tb.payload("checkout.session.completed", tb.checkout_obj(), "evt_r1"),
             _ledger(env))
    key = run(billing.claim(session_id=tb.SESSION, kv=kv, policy=policy, now=tb.T0,
                            service_commit=tb.COMMIT, ledger=_ledger(env))).body["key"]
    _admin(env, "export")
    before = dict(kv.data)

    rotated = run(billing.rotate(api_key=key, kv=kv, policy=policy, now=tb.T0,
                                 service_commit=tb.COMMIT, ledger=_ledger(env)))
    claimed = run(billing.claim(session_id="cs_other", kv=kv, policy=policy, now=tb.T0,
                                service_commit=tb.COMMIT, ledger=_ledger(env)))

    assert (rotated.status, claimed.status) == (503, 503)
    assert kv.data == before
    assert run(access_keys.lookup(kv, key)).active is True


def test_a_one_shot_payment_is_credited_and_spent_in_one_step():
    env = Env()

    result = run(_ledger(env).spend_paid("payer:0xabc", "x402:n1", 1, "0xtx"))
    _admin(env, "export")

    assert result.credited is True
    assert run(env.CREDITS.obj.move_status())["holders"] == 1
    state = credits.LedgerState.from_json(json.loads(env.CREDITS.obj._get("state")))
    assert state.balance("payer:0xabc").available == 0
    assert state.seen("x402:n1") is True



def test_after_a_rollback_the_move_can_be_tried_again_with_the_later_balances():
    old, new = Env(), Env(standby=True)
    _credit(old, "pack:cs_1", 5)
    first, _ = _move(old, new)
    resealed = _admin(new, "export")[1]
    _admin(old, "unseal", {"digest": first["digest"]})
    assert resealed["digest"] == first["digest"]
    _credit(old, "pack:cs_2", 2)

    again, (status, imported) = _move(old, new)

    assert status == 200 and imported["role"] == "live"
    assert imported["digest"] == again["digest"] != first["digest"]
    assert _balance(new) == 7


def test_a_destination_that_took_writes_after_its_import_never_takes_another_copy():
    old, new = Env(), Env(standby=True)
    _credit(old, "pack:cs_1", 5)
    _move(old, new)
    _credit(new, "pack:cs_9", 1)
    _admin(new, "export")
    other = Env()
    _credit(other, "pack:cs_3", 3)
    exported = _admin(other, "export")[1]

    status, body = _admin(new, "import", _copy(exported))

    assert (status, body["error"]["code"]) == (409, "import_refused")



def test_a_stale_copy_replayed_after_a_rollback_never_makes_a_second_live_ledger():
    old, new = Env(), Env(standby=True)
    _credit(old, "pack:cs_1", 5)
    stale, _ = _move(old, new)
    _admin(new, "export")
    _admin(old, "unseal", {"digest": stale["digest"]})

    status, body = _admin(new, "import", _copy(stale))

    assert (status, body["error"]["code"]) == (409, "import_refused")
    assert _frozen(new)
    assert _balance(old) == 5


def test_an_unchanged_ledger_exported_again_after_a_rollback_still_moves():
    old, new = Env(), Env(standby=True)
    _credit(old, "pack:cs_1", 5)
    first, _ = _move(old, new)
    _admin(new, "export")
    _admin(old, "unseal", {"digest": first["digest"]})

    again, (status, imported) = _move(old, new)

    assert again["digest"] == first["digest"] and again["generation"] != first["generation"]
    assert (status, imported["role"]) == (200, "live")
    assert _balance(new) == 5


# ── Codex review REV-895-r2 ──────────────────────────────────────────────────

def test_an_archived_export_never_revives_a_destination_rolled_back_twice():
    old, new = Env(), Env(standby=True)
    _credit(old, "pack:cs_1", 5)
    first, _ = _move(old, new)
    _admin(new, "export")
    _admin(old, "unseal", {"digest": first["digest"]})
    _credit(old, "pack:cs_2", 2)
    second, _ = _move(old, new)
    resealed = _admin(new, "export")[1]
    _admin(old, "unseal", {"digest": resealed["digest"]})

    replay = _admin(new, "import", _copy(first))
    unnumbered = _admin(new, "import", {"state": first["state"], "digest": first["digest"]})

    assert (replay[0], unnumbered[0]) == (409, 409)
    assert _frozen(new)
    assert _balance(old) == 7


class PausingKV(MemoryKV):
    """KV whose first read waits for the test to let it continue."""

    def __init__(self):
        super().__init__()
        self.reading = asyncio.Event()
        self.go_on = asyncio.Event()

    async def get(self, name):
        if not self.reading.is_set():
            self.reading.set()
            await self.go_on.wait()
        return await super().get(name)


def test_export_waits_for_a_webhook_already_admitted_so_its_writes_are_in_the_copy():
    policy = access_config.load_policy()
    env = Env()
    kv = PausingKV()
    body = tb.payload("checkout.session.completed", tb.checkout_obj(), "evt_inflight")

    async def scenario():
        hook = asyncio.ensure_future(tb.apply(kv, policy, body, ledger=_ledger(env)))
        await kv.reading.wait()
        early = await ledger_admin.handle(env, ledger_admin.PREFIX + "export", "POST",
                                          "Bearer " + SECRET, "{}")
        kv.go_on.set()
        outcome = await hook
        late = await ledger_admin.handle(env, ledger_admin.PREFIX + "export", "POST",
                                         "Bearer " + SECRET, "{}")
        return early, outcome, late

    early, outcome, late = run(scenario())

    assert (early[0], early[1]["error"]["code"]) == (409, "export_refused")
    assert outcome.status == 200
    assert late[1]["role"] == "sealed"
    assert "event:evt_inflight" in kv.data


def test_a_rotation_that_outlives_its_lease_cannot_revoke_after_the_copy(monkeypatch):
    policy = access_config.load_policy()
    env = Env()
    kv = MemoryKV()
    tb.run(tb.apply(kv, policy, tb.payload("checkout.session.completed", tb.checkout_obj(),
                                           "evt_rot"), ledger=_ledger(env)))
    key = run(billing.claim(session_id=tb.SESSION, kv=kv, policy=policy, now=tb.T0,
                            service_commit=tb.COMMIT, ledger=_ledger(env))).body["key"]
    clock = [1_000_000.0]
    monkeypatch.setattr(credits_do, "_clock", lambda: clock[0])
    ledger = _ledger(env)
    real_transfer = ledger.transfer

    async def slow_transfer(src, dst):
        moved = await real_transfer(src, dst)
        clock[0] += credits_do.LEASE_SECONDS + 1
        await ledger_admin.handle(env, ledger_admin.PREFIX + "export", "POST",
                                  "Bearer " + SECRET, "{}")
        return moved

    ledger.transfer = slow_transfer

    outcome = run(billing.rotate(api_key=key, kv=kv, policy=policy, now=tb.T0,
                                 service_commit=tb.COMMIT, ledger=ledger))

    assert outcome.status == 503
    assert _status(env)["role"] == "sealed"
    assert run(access_keys.lookup(kv, key)).active is True



def test_the_admin_transfer_moves_a_stranded_balance_on_a_live_ledger_only():
    env = Env()
    _credit(env, "pack:cs_1", 5, holder="key:unseen")

    moved = _admin(env, "transfer", {"src": "key:unseen", "dst": "key:old"})
    _admin(env, "export")
    frozen = _admin(env, "transfer", {"src": "key:old", "dst": "key:unseen"})

    assert moved == (200, {"moved": True})
    assert frozen[0] == 409
    state = credits.LedgerState.from_json(json.loads(env.CREDITS.obj._get("state")))
    assert state.balance("key:old").available == 5
