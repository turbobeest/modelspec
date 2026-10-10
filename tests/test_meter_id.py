"""MODEL-357: Stripe meter-event identifiers use a random account id.

The holder is `key:` plus the SHA-256 of the API key. A meter event must not
carry that hash, the holder, or the key. Tests inject HTTP and do not call Stripe.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
WORKER_SRC = REPO_ROOT / "api" / "worker" / "src"
for path in (str(REPO_ROOT), str(WORKER_SRC)):
    if path not in sys.path:
        sys.path.insert(0, path)

import credits  # noqa: E402
import x402  # noqa: E402
from tests.test_pricing_v2 import (  # noqa: E402
    _decision_request,
    _decision_worker,
    _issue,
    _meter_script,
    _overage_spec,
    _scale_configured_text,
    _vocab,
    run,
)
from tests.test_visit_gate import environment  # noqa: E402
from tests.test_x402 import entry as _x402_entry  # noqa: E402

METER_ID = re.compile(r"^m_[0-9a-f]{32}$")


@pytest.fixture
def entry(monkeypatch):
    return _x402_entry.__wrapped__(monkeypatch)


@pytest.fixture
def bundled_entry(monkeypatch):
    bundle = SimpleNamespace(
        read=lambda path: (
            b'{"facets":[]}' if path == "/api/decision/vocabulary.json" else None))
    monkeypatch.setitem(sys.modules, "bundled_data", bundle)
    return _x402_entry.__wrapped__(monkeypatch)


def _bodies(calls: list[dict]) -> str:
    return json.dumps(calls)


def test_stripe_meter_events_use_the_account_meter_id(bundled_entry):
    """Catalog read, uncertain retry, backlog drain, and decide settle."""
    secret = "live_meter_paths"
    calls, fetch = _meter_script(["timeout", 200, 400, 200, 200, 200])
    bundled_entry.fetch = fetch
    env = environment(
        HUMAN_GATE_ENABLED="false",
        X402_ENABLED="false",
        STRIPE_SECRET_KEY="sk_test_fixture",
        TIER_POLICY=_scale_configured_text(cap=10),
    )
    key = run(_issue(env, "paid", secret))
    holder = x402.holder_from_key(key)
    digest = hashlib.sha256(secret.encode("utf-8")).hexdigest()
    assert holder == "key:" + digest
    assert run(env.CREDITS.set_monthly(
        holder, 0, "in_meter_paths", "Scale", "cus_meter_paths")).credited
    worker = _decision_worker(bundled_entry, env)

    for _ in range(30):
        assert run(worker.fetch(_vocab(key))).status == 200
    account = env.CREDITS.state.accounts[holder]
    meter = account.meter_id
    assert METER_ID.fullmatch(meter)
    assert account.next_res == 4
    assert account.overage_used == 3
    assert account.overage_unreported == 0
    assert account.overage_uncertain == []

    decided = run(worker.fetch(_decision_request(key=key)))
    assert decided.status == 200
    assert account.overage_used == 4
    assert [row["identifier"] for row in calls] == [
        f"{meter}:read:1",
        f"{meter}:read:1",
        f"{meter}:read:11",
        f"{meter}:backlog:0",
        f"{meter}:read:21",
        f"{meter}:res:4",
    ]
    assert calls[3]["payload[value]"] == "1"
    assert calls[5]["payload[value]"] == "1"
    assert {row["event_name"] for row in calls} == {"modelspec_scale_overage"}
    assert {row["payload[stripe_customer_id]"] for row in calls} == {"cus_meter_paths"}
    sent = _bodies(calls)
    assert holder not in sent
    assert digest not in sent
    assert secret not in sent
    for row in calls:
        assert row["identifier"].startswith(meter + ":")


def test_meter_id_is_generated_once_and_differs_per_account():
    ledger = credits.MemoryLedger()
    assert run(ledger.set_monthly("alpha", 0, "in_a", "Scale", "cus_alpha")).credited
    assert run(ledger.set_monthly("beta", 0, "in_b", "Scale", "cus_beta")).credited
    assert ledger.state.accounts["alpha"].meter_id == ""
    assert ledger.state.accounts["beta"].meter_id == ""

    first = run(ledger.meter_identifier("alpha", "read", 1))
    again = run(ledger.meter_identifier("alpha", "read", 1))
    other_kind = run(ledger.meter_identifier("alpha", "res", 2))
    beta = run(ledger.meter_identifier("beta", "read", 1))
    meter_a = ledger.state.accounts["alpha"].meter_id
    meter_b = ledger.state.accounts["beta"].meter_id

    assert first == again == f"{meter_a}:read:1"
    assert other_kind == f"{meter_a}:res:2"
    assert beta == f"{meter_b}:read:1"
    assert meter_a != meter_b
    assert METER_ID.fullmatch(meter_a)
    assert METER_ID.fullmatch(meter_b)
    assert "cus_alpha" not in meter_a
    assert "meter_id" not in run(ledger.balance("alpha")).to_json()

    stored = credits.LedgerState.from_json({"accounts": {"kept": {
        "meter_id": "already-stored",
    }}})
    kept = credits.MemoryLedger(stored)
    assert run(kept.meter_identifier("kept", "read", 7)) == "already-stored:read:7"
    assert kept.state.accounts["kept"].meter_id == "already-stored"


def test_a_stored_account_without_meter_id_gets_one_on_first_use():
    loaded = credits.LedgerState.from_json({"accounts": {"old": {
        "plan": "Scale",
        "stripe_customer_id": "cus_old",
        "overage_unreported": 2,
    }}})
    assert loaded.accounts["old"].meter_id == ""
    ledger = credits.MemoryLedger(loaded)
    opened = run(ledger.open_backlog("old"))
    meter = ledger.state.accounts["old"].meter_id
    assert METER_ID.fullmatch(meter)
    assert opened == (2, 0, f"{meter}:backlog:0")
    reloaded = credits.MemoryLedger(credits.LedgerState.from_json(
        json.loads(json.dumps(ledger.state.to_json()))))
    assert run(reloaded.open_backlog("old")) == (2, 0, f"{meter}:backlog:0")
    assert reloaded.state.accounts["old"].meter_id == meter


def test_durable_object_loads_a_record_without_meter_id_and_keeps_it():
    import credits_do
    from tests.test_credits_do import Ctx, JsObjectProxy

    ctx = Ctx(lambda value: JsObjectProxy({"v": value}))
    raw = json.dumps({"accounts": {"legacy": {
        "plan": "Scale",
        "stripe_customer_id": "cus_do",
        "overage_unreported": 4,
    }}})
    assert "meter_id" not in raw
    ctx.storage.sql.exec(
        "INSERT OR REPLACE INTO kv (k, v) VALUES (?, ?)", "state", raw)
    obj = credits_do.CreditsObject(ctx, env=None)
    units, seq, ident = run(obj.open_backlog("legacy"))
    stored = json.loads(ctx.storage.sql.table["state"])
    meter = stored["accounts"]["legacy"]["meter_id"]
    assert METER_ID.fullmatch(meter)
    assert (units, seq, ident) == (4, 0, f"{meter}:backlog:0")

    reloaded = credits_do.CreditsObject(ctx, env=None)
    assert run(reloaded.meter_identifier("legacy", "read", "3")) == f"{meter}:read:3"
    again = json.loads(ctx.storage.sql.table["state"])
    assert again["accounts"]["legacy"]["meter_id"] == meter

    run(reloaded.set_monthly("src", 0, "in_src", "Scale", "cus_src"))
    run(reloaded.set_monthly("dst", 1, "in_dst", "Scale", "cus_dst"))
    src = run(reloaded.meter_identifier("src", "read", "1")).split(":")[0]
    dst = run(reloaded.meter_identifier("dst", "read", "1")).split(":")[0]
    assert src != dst
    assert run(reloaded.transfer("src", "dst")) is True
    moved = credits_do.CreditsObject(ctx, env=None)
    assert run(moved.meter_identifier("dst", "res", "8")) == f"{dst}:res:8"
    after = json.loads(ctx.storage.sql.table["state"])
    assert after["accounts"]["dst"]["meter_id"] == dst
    assert "src" not in after["accounts"]

    run(moved.set_monthly("bare", 2, "in_bare", "Scale"))
    give = run(moved.meter_identifier("give", "read", "1")).split(":")[0]
    assert run(moved.transfer("give", "bare")) is True
    inherited = json.loads(ctx.storage.sql.table["state"])
    assert inherited["accounts"]["bare"]["meter_id"] == give

    whole = run(moved.meter_identifier("whole", "read", "1")).split(":")[0]
    assert run(moved.transfer("whole", "moved")) is True
    wholesale = json.loads(ctx.storage.sql.table["state"])
    assert wholesale["accounts"]["moved"]["meter_id"] == whole


def test_transfer_keeps_or_inherits_meter_id_and_stored_identifiers():
    ledger = credits.MemoryLedger()
    whole = run(ledger.meter_identifier("key:src", "read", 1)).split(":")[0]
    assert run(ledger.transfer("key:src", "key:moved"))
    assert ledger.state.accounts["key:moved"].meter_id == whole
    assert run(ledger.meter_identifier("key:moved", "read", 2)) == f"{whole}:read:2"

    assert run(ledger.set_monthly("key:dest", 1, "in_dest", "Scale", "cus_d")).credited
    dest = run(ledger.meter_identifier("key:dest", "read", 1)).split(":")[0]
    src = run(ledger.meter_identifier("key:other", "read", 1)).split(":")[0]
    assert dest != src
    assert run(ledger.note_unreported("key:other", 3, "evt-src"))
    opened = run(ledger.open_backlog("key:other"))
    assert opened == (3, 0, f"{src}:backlog:0")
    assert run(ledger.note_uncertain("key:other", 2, "key:other:read:1"))
    assert run(ledger.transfer("key:other", "key:dest"))
    merged = ledger.state.accounts["key:dest"]
    assert merged.meter_id == dest
    assert merged.overage_backlog_open == 3
    assert merged.overage_backlog_id == f"{src}:backlog:0"
    assert ("key:other:read:1", 2) in [
        (row[0], row[1]) for row in merged.overage_uncertain]

    inherited_id = "m_" + "cd" * 16
    bare = credits.LedgerState.from_json({"accounts": {
        "key:bare": {"monthly": 1, "plan": "Scale"},
        "key:give": {
            "monthly": 0,
            "plan": "Scale",
            "meter_id": inherited_id,
            "overage_unreported": 1,
        },
    }})
    give = credits.MemoryLedger(bare)
    assert give.state.accounts["key:bare"].meter_id == ""
    assert run(give.transfer("key:give", "key:bare"))
    account = give.state.accounts["key:bare"]
    assert account.meter_id == inherited_id
    assert run(give.open_backlog("key:bare")) == (1, 0, f"{inherited_id}:backlog:0")


def test_a_legacy_uncertain_identifier_is_retried_verbatim(entry):
    env = SimpleNamespace(
        STRIPE_SECRET_KEY="sk_test_fixture", CREDITS=credits.MemoryLedger())
    holder = "key:" + "ab" * 32
    legacy = f"{holder}:read:1"
    assert run(env.CREDITS.note_uncertain(holder, 2, legacy))
    fresh = run(env.CREDITS.meter_identifier(holder, "read", 9))
    meter = env.CREDITS.state.accounts[holder].meter_id
    assert fresh == f"{meter}:read:9"
    calls, fetch = _meter_script([200, 200])
    entry.fetch = fetch
    run(entry._post_overage(
        env, _overage_spec(), "cus_legacy", 1, fresh, holder=holder))
    assert [row["identifier"] for row in calls] == [legacy, fresh]
    assert calls[0]["payload[value]"] == "2"
    assert calls[1]["payload[value]"] == "1"
    assert env.CREDITS.state.accounts[holder].overage_uncertain == []


def test_a_missing_backlog_identifier_is_not_composed_from_the_holder(entry):
    class BlankBacklog(credits.MemoryLedger):
        async def open_backlog(self, holder):
            units, seq, _ident = await super().open_backlog(holder)
            if units:
                self.state.accounts[holder].overage_backlog_id = ""
                return units, seq, ""
            return units, seq, _ident

    env = SimpleNamespace(
        STRIPE_SECRET_KEY="sk_test_fixture", CREDITS=BlankBacklog())
    holder = "key:" + "11" * 32
    assert run(env.CREDITS.note_unreported(
        holder, 2, "evt-old", "cus_blank", "modelspec_scale_overage"))
    fresh = run(env.CREDITS.meter_identifier(holder, "read", 4))
    calls, fetch = _meter_script([200, 200])
    entry.fetch = fetch
    run(entry._post_overage(
        env, _overage_spec(), "cus_blank", 1, fresh, holder=holder))
    assert calls == []
    account = env.CREDITS.state.accounts[holder]
    assert account.overage_uncertain[0][0] == fresh
    assert account.overage_uncertain[0][1] == 1
    assert holder not in _bodies(calls)

    blank = SimpleNamespace(
        STRIPE_SECRET_KEY="sk_test_fixture", CREDITS=credits.MemoryLedger())
    quiet, fetch = _meter_script([200])
    entry.fetch = fetch
    run(entry._post_overage(
        blank, _overage_spec(), "cus_blank", 3, "", holder="plain"))
    assert quiet == []
    parked = blank.CREDITS.state.accounts["plain"]
    assert parked.overage_unreported == 3
    assert parked.meter_id == ""


def test_an_unnamed_event_survives_a_failed_retry_as_unreported(entry):
    """The ledger could not name the new event, and the older retry times out."""
    env = SimpleNamespace(
        STRIPE_SECRET_KEY="sk_test_fixture", CREDITS=credits.MemoryLedger())
    holder = "key:" + "cd" * 32
    older = run(env.CREDITS.meter_identifier(holder, "res", 1))
    assert run(env.CREDITS.note_uncertain(holder, 2, older))
    calls, fetch = _meter_script(["timeout"])
    entry.fetch = fetch
    run(entry._post_overage(
        env, _overage_spec(), "cus_unnamed", 3, "", holder=holder))
    assert [row["identifier"] for row in calls] == [older]
    account = env.CREDITS.state.accounts[holder]
    assert [(ident, units) for ident, units, _at in account.overage_uncertain] == [(older, 2)]
    assert account.overage_unreported == 3
