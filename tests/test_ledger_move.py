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


def _move(old, new):
    exported = _admin(old, "export")[1]
    return exported, _admin(new, "import", {"state": exported["state"],
                                             "digest": exported["digest"]})


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

    status, body = _admin(other, "import", {"state": exported["state"],
                                            "digest": exported["digest"]})
    tampered = _admin(Env(standby=True), "import", {"state": exported["state"], "digest": "0" * 64})

    assert (status, body["error"]["code"]) == (409, "import_refused")
    assert (tampered[0], tampered[1]["error"]["code"]) == (409, "import_refused")
    assert _balance(other) == 1


def test_a_restart_between_the_state_and_the_record_leaves_a_ledger_that_imports_again():
    old, new = Env(), Env(standby=True)
    _credit(old, "pack:cs_1", 5)
    exported = _admin(old, "export")[1]
    new.CREDITS.obj._save(credits.LedgerState.from_json(json.loads(exported["state"])))

    assert _status(new)["role"] == "standby"
    assert _admin(new, "import", {"state": exported["state"],
                                  "digest": exported["digest"]})[1]["role"] == "live"
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
