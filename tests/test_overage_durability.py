"""MODEL-372: recover meter usage across lost RPC replies and key rotation.

The real CreditsObject writes to SQLite. Only RPC delivery and Stripe HTTP
are simulated; the tests do not contact a provider.
"""

from __future__ import annotations

import asyncio
import json
import sqlite3
import sys
import urllib.parse
from pathlib import Path
from types import SimpleNamespace

import pytest

WORKER_SRC = Path(__file__).resolve().parents[1] / "api" / "worker" / "src"
if str(WORKER_SRC) not in sys.path:
    sys.path.insert(0, str(WORKER_SRC))

import credits  # noqa: E402
import credits_do  # noqa: E402
import x402  # noqa: E402
from tests.test_pricing_v2 import _overage_spec  # noqa: E402
from tests.test_x402 import (  # noqa: E402
    ENVELOPE,
    RESOURCE,
    StubFacilitator,
    _cfg,
    _ok,
    entry as _x402_entry,
)


def run(coro):
    return asyncio.run(coro)


@pytest.fixture
def entry(monkeypatch):
    return _x402_entry.__wrapped__(monkeypatch)


class _Sql:
    def __init__(self, path):
        self.connection = sqlite3.connect(path, isolation_level=None)
        self.connection.row_factory = sqlite3.Row

    def exec(self, query, *params):
        cursor = self.connection.execute(query, params)

        class Result:
            def one(self):
                row = cursor.fetchone()
                if row is None:
                    raise RuntimeError("no row")
                return dict(row)

        return Result()


class _Namespace:
    def __init__(self, path):
        self.path = path
        self.sql = _Sql(path)
        self.obj = credits_do.CreditsObject(
            SimpleNamespace(storage=SimpleNamespace(sql=self.sql)), env=None)
        self.lose_commit_reply = False
        self.lose_ack_reply = ""

    def idFromName(self, name):  # noqa: N802 - Workers binding API
        assert name == "ledger"
        return name

    def get(self, object_id):
        assert object_id == "ledger"
        return self

    def __getattr__(self, name):
        return getattr(self.obj, name)

    async def commit(self, holder, reservation_id):
        result = await self.obj.commit(holder, reservation_id)
        if self.lose_commit_reply:
            self.lose_commit_reply = False
            raise TimeoutError("committed debit, lost DO reply")
        return result

    async def ack_uncertain(self, holder, identifier):
        loss, self.lose_ack_reply = self.lose_ack_reply, ""
        if loss == "before":
            raise TimeoutError("ack RPC did not reach DO")
        result = await self.obj.ack_uncertain(holder, identifier)
        if loss == "after":
            raise TimeoutError("ack committed, lost DO reply")
        return result

    def restart(self):
        self.sql.connection.close()
        self.sql = _Sql(self.path)
        self.obj = credits_do.CreditsObject(
            SimpleNamespace(storage=SimpleNamespace(sql=self.sql)), env=None)

    def stored(self):
        cursor = self.sql.connection.execute("SELECT v FROM kv WHERE k = 'state'")
        row = cursor.fetchone()
        assert row is not None
        return json.loads(row["v"])


@pytest.fixture
def namespace(tmp_path):
    ns = _Namespace(tmp_path / "ledger.sqlite")
    try:
        yield ns
    finally:
        ns.sql.connection.close()


class _Stripe:
    def __init__(self):
        self.attempts = []
        self.accepted = {}
        self.during_report = None
        self.lose_reply = False
        self.reject_next = False

    async def fetch(self, url, options=None):
        assert url == "https://api.stripe.com/v1/billing/meter_events"
        fields = dict(urllib.parse.parse_qsl((options or {}).get("body", "")))
        self.attempts.append(fields)
        rejected, self.reject_next = self.reject_next, False
        identifier = fields["identifier"]
        duplicate = identifier in self.accepted
        if rejected:
            pass
        elif duplicate:
            assert self.accepted[identifier] == fields
        else:
            self.accepted[identifier] = fields
        if self.during_report is not None:
            action, self.during_report = self.during_report, None
            await action()
        if self.lose_reply:
            self.lose_reply = False
            raise TimeoutError("Stripe accepted usage, lost HTTP reply")

        class Response:
            ok = not duplicate and not rejected
            status = 400 if duplicate or rejected else 200

            async def text(self):
                if duplicate:
                    return json.dumps({"error": {"code": "duplicate_meter_event"}})
                if rejected:
                    return json.dumps({"error": {"code": "resource_missing"}})
                return "{}"

        return Response()

    def units(self):
        return sum(int(row["payload[value]"]) for row in self.accepted.values())


async def _charge(entry, env, holder, *, units=1, enabled=False):
    async def report(value, identifier):
        await entry._post_overage(
            env, _overage_spec(), "cus_durable", value, identifier, holder=holder)

    return await x402.charge(
        config=_cfg(enabled=enabled), ledger=credits.ledger_from_env(env),
        facilitator=StubFacilitator(), get_header=lambda _name: None,
        holder=holder, resource_url=RESOURCE, envelope=ENVELOPE,
        produce=_ok, units=units, overage_cap=100, on_overage=report)


@pytest.mark.parametrize("enabled", [False, True])
def test_lost_do_reply_after_commit_reports_usage_once_on_a_later_prepaid_request(
        entry, namespace, enabled):
    env = SimpleNamespace(STRIPE_SECRET_KEY="sk_test_fixture", CREDITS=namespace)
    ledger = credits.ledger_from_env(env)
    holder = "key:lost-reply"
    assert run(ledger.set_monthly(holder, 0, "in_lost", "Scale", "cus_durable")).credited
    stripe = _Stripe()
    entry.fetch = stripe.fetch
    namespace.lose_commit_reply = True

    with pytest.raises(TimeoutError, match="committed debit, lost DO reply"):
        run(_charge(entry, env, holder, units=3, enabled=enabled))
    assert run(ledger.balance(holder)).overage_used == 3
    assert stripe.attempts == []

    namespace.restart()
    assert run(ledger.credit(holder, "pack_recovery", 2, "tx_recovery")).credited
    assert run(_charge(entry, env, holder, enabled=enabled))[0] == 200
    assert stripe.units() == 3
    assert len(stripe.attempts) == 1
    assert stripe.attempts[0]["payload[value]"] == "3"
    assert run(_charge(entry, env, holder, enabled=enabled))[0] == 200
    assert len(stripe.attempts) == 1
    assert run(ledger.balance(holder)).overage_used == 3


@pytest.mark.parametrize("lose_reply", [False, True])
def test_key_rotation_during_report_retries_usage_once_without_a_phantom_account(
        entry, namespace, lose_reply):
    env = SimpleNamespace(STRIPE_SECRET_KEY="sk_test_fixture", CREDITS=namespace)
    ledger = credits.ledger_from_env(env)
    src, dst = "key:before-rotation", "key:after-rotation"
    assert run(ledger.set_monthly(src, 0, "in_rotation", "Scale", "cus_durable")).credited
    stripe = _Stripe()
    entry.fetch = stripe.fetch

    async def rotate():
        assert await ledger.transfer(src, dst)

    stripe.during_report = rotate
    stripe.lose_reply = lose_reply
    assert run(_charge(entry, env, src, units=2))[0] == 200
    assert src not in namespace.stored()["accounts"]

    namespace.restart()
    assert run(ledger.credit(dst, "pack_rotated", 2, "tx_rotated")).credited
    assert run(_charge(entry, env, dst))[0] == 200
    assert stripe.units() == 2
    assert len(stripe.attempts) == (2 if lose_reply else 1)
    assert len({row["identifier"] for row in stripe.attempts}) == 1
    assert run(ledger.list_uncertain(dst)) == []
    assert run(_charge(entry, env, dst))[0] == 200
    assert len(stripe.attempts) == (2 if lose_reply else 1)
    assert src not in namespace.stored()["accounts"]


def test_meter_identifier_resolves_the_account_after_rotation_and_restart(namespace):
    ledger = credits.DurableLedger(namespace)
    assert run(ledger.set_monthly("old", 0, "in_identity", "Scale", "cus_durable")).credited
    before = run(ledger.meter_identifier("old", "res", 7))
    assert run(ledger.transfer("old", "middle"))
    assert run(ledger.transfer("middle", "new"))
    namespace.restart()
    assert run(ledger.meter_identifier("old", "res", 7)) == before
    assert run(ledger.meter_identifier("middle", "res", 7)) == before
    assert run(ledger.meter_identifier("new", "res", 7)) == before
    assert set(namespace.stored()["accounts"]) == {"new"}
    assert run(ledger.balance("old")).available == 0


@pytest.mark.parametrize("method,args,expected", [
    ("note_uncertain", (2, "evt_unknown"), False),
    ("note_unreported", (2, "evt_unknown"), False),
    ("meter_identifier", ("res", 1), ""),
])
def test_meter_writes_never_create_an_unknown_account(namespace, method, args, expected):
    ledger = credits.DurableLedger(namespace)
    assert run(getattr(ledger, method)("unknown", *args)) == expected
    assert namespace.stored()["accounts"] == {}


def test_rotation_onto_an_existing_account_preserves_each_naming_identity(namespace):
    ledger = credits.DurableLedger(namespace)
    assert run(ledger.set_monthly("src", 0, "in_src", "Scale", "cus_durable")).credited
    assert run(ledger.set_monthly("dst", 0, "in_dst", "Scale", "cus_durable")).credited
    src_id = run(ledger.meter_identifier("src", "read", 1))
    dst_id = run(ledger.meter_identifier("dst", "read", 1))
    assert src_id != dst_id
    assert run(ledger.transfer("src", "dst"))
    namespace.restart()
    assert run(ledger.meter_identifier("src", "read", 1)) == src_id
    assert run(ledger.meter_identifier("dst", "read", 1)) == dst_id
    assert set(namespace.stored()["accounts"]) == {"dst"}


@pytest.mark.parametrize("lose_ack", ["before", "after"])
def test_lost_meter_acknowledgement_never_reports_usage_twice(entry, namespace, lose_ack):
    env = SimpleNamespace(STRIPE_SECRET_KEY="sk_test_fixture", CREDITS=namespace)
    ledger = credits.ledger_from_env(env)
    holder = "key:ack-loss"
    assert run(ledger.set_monthly(holder, 0, "in_ack", "Scale", "cus_durable")).credited
    stripe = _Stripe()
    entry.fetch = stripe.fetch
    namespace.lose_ack_reply = lose_ack
    assert run(_charge(entry, env, holder, units=2))[0] == 200
    namespace.restart()
    assert run(ledger.credit(holder, "pack_ack", 1, "tx_ack")).credited
    assert run(_charge(entry, env, holder))[0] == 200
    assert stripe.units() == 2
    assert len(stripe.attempts) == (2 if lose_ack == "before" else 1)
    assert run(ledger.list_uncertain(holder)) == []


def test_a_rejected_first_durable_report_keeps_usage_in_the_unreported_backlog(
        entry, namespace):
    env = SimpleNamespace(STRIPE_SECRET_KEY="sk_test_fixture", CREDITS=namespace)
    ledger = credits.ledger_from_env(env)
    holder = "key:rejected"
    assert run(ledger.set_monthly(holder, 0, "in_rejected", "Scale", "cus_durable")).credited
    stripe = _Stripe()
    stripe.reject_next = True
    entry.fetch = stripe.fetch
    assert run(_charge(entry, env, holder, units=2))[0] == 200
    account = namespace.stored()["accounts"][holder]
    assert account["overage_unreported"] == 2
    assert account["overage_uncertain"] == []
    assert account["overage_unreconciled"] == 0
    assert run(ledger.credit(holder, "pack_rejected", 1, "tx_rejected")).credited
    assert run(_charge(entry, env, holder))[0] == 200
    assert stripe.units() == 2
    assert run(ledger.balance(holder)).overage_unreported == 0


def test_lost_commit_replies_keep_a_bounded_queue_and_report_all_overflow_once(
        entry, namespace):
    env = SimpleNamespace(STRIPE_SECRET_KEY="sk_test_fixture", CREDITS=namespace)
    ledger = credits.ledger_from_env(env)
    holder = "key:overflow"
    assert run(ledger.set_monthly(holder, 0, "in_overflow", "Scale", "cus_durable")).credited
    stripe = _Stripe()
    entry.fetch = stripe.fetch
    for _ in range(25):
        namespace.lose_commit_reply = True
        with pytest.raises(TimeoutError, match="committed debit, lost DO reply"):
            run(_charge(entry, env, holder))
    account = namespace.stored()["accounts"][holder]
    assert len(account["overage_pending"]) == credits.PENDING_METER_CAP
    assert account["overage_unreported"] == 5
    assert stripe.attempts == []
    namespace.restart()
    assert run(ledger.credit(holder, "pack_overflow", 8, "tx_overflow")).credited
    for _ in range(8):
        before = len(stripe.attempts)
        assert run(_charge(entry, env, holder))[0] == 200
        assert len(stripe.attempts) - before <= credits.UNCERTAIN_RETRIES_PER_REQUEST + 1
    assert stripe.units() == 25
    assert len(stripe.attempts) == 21
    assert run(ledger.balance(holder)).overage_used == 25
    assert run(ledger.balance(holder)).overage_unreported == 0
    assert run(ledger.list_uncertain(holder)) == []
    assert namespace.stored()["accounts"][holder]["overage_pending"] == []


def test_key_rotation_during_catalog_meter_timeout_retries_the_original_usage_once(
        entry, namespace):
    env = SimpleNamespace(STRIPE_SECRET_KEY="sk_test_fixture", CREDITS=namespace)
    ledger = credits.ledger_from_env(env)
    src, dst = "key:catalog-old", "key:catalog-new"
    assert run(ledger.set_monthly(src, 0, "in_catalog", "Scale", "cus_durable")).credited
    identifier = run(ledger.meter_identifier(src, "read", 1))
    stripe = _Stripe()
    entry.fetch = stripe.fetch

    async def rotate():
        assert await ledger.transfer(src, dst)

    stripe.during_report = rotate
    stripe.lose_reply = True
    run(entry._post_overage(
        env, _overage_spec(), "cus_durable", 2, identifier, holder=src))
    assert src not in namespace.stored()["accounts"]
    assert [(ident, value) for ident, value, _at in run(ledger.list_uncertain(dst))] == [
        (identifier, 2)]
    namespace.restart()
    assert run(ledger.credit(dst, "pack_catalog", 1, "tx_catalog")).credited
    assert run(_charge(entry, env, dst))[0] == 200
    assert stripe.units() == 2
    assert [row["identifier"] for row in stripe.attempts] == [identifier, identifier]
    assert run(ledger.list_uncertain(dst)) == []
    assert src not in namespace.stored()["accounts"]


def test_rotation_during_backlog_report_acknowledges_only_the_source_snapshot(
        entry, namespace):
    env = SimpleNamespace(STRIPE_SECRET_KEY="sk_test_fixture", CREDITS=namespace)
    ledger = credits.ledger_from_env(env)
    src, dst = "key:backlog-old", "key:backlog-new"
    assert run(ledger.set_monthly(src, 0, "in_backlog_old", "Scale", "cus_durable")).credited
    assert run(ledger.set_monthly(dst, 0, "in_backlog_new", "Scale", "cus_durable")).credited
    assert run(ledger.note_unreported(src, 2, "evt_old"))
    assert run(ledger.note_unreported(dst, 3, "evt_new"))
    src_backlog = run(ledger.open_backlog(src))
    dst_backlog = run(ledger.open_backlog(dst))
    stripe = _Stripe()
    entry.fetch = stripe.fetch

    async def rotate():
        assert await ledger.transfer(src, dst)

    stripe.during_report = rotate
    run(entry._post_overage(env, _overage_spec(), "cus_durable", 0, "", holder=src))
    assert run(ledger.list_uncertain(dst)) == []
    assert run(ledger.open_backlog(dst)) == dst_backlog
    namespace.restart()
    assert run(ledger.credit(dst, "pack_backlog", 1, "tx_backlog")).credited
    assert run(_charge(entry, env, dst))[0] == 200
    assert stripe.units() == 5
    assert [row["identifier"] for row in stripe.attempts] == [
        src_backlog[2], dst_backlog[2]]
    assert run(ledger.balance(dst)).overage_unreported == 0
    assert src not in namespace.stored()["accounts"]
