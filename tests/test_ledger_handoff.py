"""MODEL-441: the credit ledger moves between Cloudflare accounts by handoff.

Two in-memory "accounts", each with its own CreditsObject, joined by the
bridge over a fake HTTPS hop. The properties under test are the ones the
move must keep: every balance arrives, a payment credited before the move
stays a duplicate after it, and exactly one copy accepts writes at a time.
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
import ledger_bridge  # noqa: E402

SECRET = "bridge-test-secret"
OLD = "https://old.example.workers.dev"
NEW = "https://new.example.workers.dev"


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
    def __init__(self):
        ctx = type("Ctx", (), {})()
        ctx.storage = type("Storage", (), {"sql": Sql()})()
        self.obj = credits_do.CreditsObject(ctx, env=None)

    def idFromName(self, name):
        assert name == "ledger"
        return name

    def get(self, _id):
        return Stub(self.obj)


class Env:
    def __init__(self, secret=SECRET):
        self.CREDITS = Namespace()
        self.LEDGER_BRIDGE_SECRET = secret


class Network:
    """HTTPS between the two Workers. `down` makes a host unreachable."""

    def __init__(self, envs: dict[str, Env]):
        self.envs = envs
        self.down: set[str] = set()

    async def post(self, url, payload, headers):
        origin = url.split("/internal/", 1)[0]
        if origin in self.down:
            raise ConnectionError("unreachable")
        path = "/internal/" + url.split("/internal/", 1)[1]
        return await ledger_bridge.handle(
            self.envs[origin], path, "POST", headers["authorization"],
            json.dumps(payload), post=self.post)


def run(coro):
    return asyncio.run(coro)


def _accounts():
    old, new = Env(), Env()
    net = Network({OLD: old, NEW: new})
    return old, new, net


def _ledger(env, net):
    return credits.DurableLedger(env.CREDITS, SECRET, post=net.post, sleep=_no_sleep)


async def _no_sleep(_seconds):
    return None


def _handoff(env, net, target):
    return run(ledger_bridge.handle(env, "/internal/ledger/handoff", "POST",
                                    "Bearer " + SECRET, json.dumps({"target": target}),
                                    post=net.post))


def _status(env):
    return run(ledger_bridge.handle(env, "/internal/ledger/status", "GET",
                                    "Bearer " + SECRET, ""))[1]


def test_balances_arrive_and_later_calls_on_the_old_worker_land_in_the_new_ledger():
    old, new, net = _accounts()
    run(_ledger(old, net).credit("key:a", "pack:cs_1", 500, "pi_1", source="pack"))
    run(_ledger(old, net).set_monthly("key:b", 4000, "in_1", "Solo"))

    status, body = _handoff(old, net, NEW)

    assert status == 200
    assert body["moved_to"] == NEW
    assert _status(new)["digest"] == body["digest"]
    assert run(_ledger(new, net).balance("key:a")).available == 500
    assert run(_ledger(new, net).balance("key:b")).monthly == 4000

    run(_ledger(old, net).credit("key:a", "pack:cs_2", 250, "pi_2", source="pack"))

    assert run(_ledger(new, net).balance("key:a")).available == 750
    assert run(_ledger(old, net).balance("key:a")).available == 750
    assert json.loads(old.CREDITS.obj._get("state"))["accounts"]["key:a"] != \
        json.loads(new.CREDITS.obj._get("state"))["accounts"]["key:a"]


def test_a_payment_credited_before_the_move_is_a_duplicate_after_it_on_either_worker():
    old, new, net = _accounts()
    run(_ledger(old, net).credit("key:a", "pack:cs_1", 500, "pi_1", source="pack"))
    _handoff(old, net, NEW)

    via_old = run(_ledger(old, net).credit("key:a", "pack:cs_1", 500, "pi_1", source="pack"))
    via_new = run(_ledger(new, net).credit("key:a", "pack:cs_1", 500, "pi_1", source="pack"))

    assert (via_old.credited, via_new.credited) == (False, False)
    assert run(_ledger(new, net).balance("key:a")).available == 500


def test_a_refused_import_unseals_the_old_ledger_and_it_keeps_serving():
    old, new, net = _accounts()
    run(_ledger(old, net).credit("key:a", "pack:cs_1", 500, "pi_1", source="pack"))
    run(_ledger(new, net).credit("key:z", "pack:cs_9", 1, "pi_9", source="pack"))

    status, body = _handoff(old, net, NEW)

    assert (status, body["error"]["code"]) == (409, "import_refused")
    assert _status(old)["moving"] == "" and _status(old)["moved_to"] == ""
    run(_ledger(old, net).credit("key:a", "pack:cs_2", 1, "pi_2", source="pack"))
    assert run(_ledger(old, net).balance("key:a")).available == 501


def test_an_unknown_import_outcome_keeps_the_seal_and_a_rerun_finishes():
    old, new, net = _accounts()
    run(_ledger(old, net).credit("key:a", "pack:cs_1", 500, "pi_1", source="pack"))
    net.down.add(NEW)

    status, body = _handoff(old, net, NEW)

    assert (status, body["error"]["code"]) == (502, "import_unknown")
    assert _status(old)["moving"] == NEW
    try:
        run(_ledger(old, net).balance("key:a"))
    except credits.LedgerUnavailable as exc:
        assert "being moved" in str(exc)
    else:
        raise AssertionError("a sealed, unfinished ledger must refuse")

    net.down.clear()
    status, body = _handoff(old, net, NEW)

    assert (status, body["moved_to"]) == (200, NEW)
    assert run(_ledger(old, net).balance("key:a")).available == 500


def test_handing_the_ledger_back_restores_the_old_account_with_later_writes():
    old, new, net = _accounts()
    run(_ledger(old, net).credit("key:a", "pack:cs_1", 500, "pi_1", source="pack"))
    _handoff(old, net, NEW)
    run(_ledger(new, net).credit("key:a", "pack:cs_2", 100, "pi_2", source="pack"))

    status, body = _handoff(new, net, OLD)

    assert (status, body["moved_to"]) == (200, OLD)
    assert _status(old)["moved_to"] == ""
    assert run(_ledger(old, net).balance("key:a")).available == 600
    assert run(_ledger(new, net).balance("key:a")).available == 600


def test_rerunning_a_finished_handoff_changes_nothing():
    old, new, net = _accounts()
    run(_ledger(old, net).credit("key:a", "pack:cs_1", 500, "pi_1", source="pack"))
    first = _handoff(old, net, NEW)
    run(_ledger(old, net).credit("key:a", "pack:cs_2", 1, "pi_2", source="pack"))

    again = _handoff(old, net, NEW)

    assert again == (200, _status(old))
    assert first[1]["moved_to"] == again[1]["moved_to"] == NEW
    assert run(_ledger(new, net).balance("key:a")).available == 501


def test_the_bridge_refuses_without_the_secret_and_names_only_ledger_methods():
    env = Env()
    no_secret = Env(secret="")

    assert run(ledger_bridge.handle(no_secret, "/internal/ledger/status", "GET", "", ""))[0] == 404
    assert run(ledger_bridge.handle(env, "/internal/ledger/status", "GET", "Bearer wrong", ""))[0] == 401
    bad = run(ledger_bridge.handle(env, "/internal/ledger/call", "POST", "Bearer " + SECRET,
                                   json.dumps({"method": "begin_handoff", "args": [NEW]})))
    assert bad[0] == 400
    assert _status(env)["moving"] == ""
    plain = run(ledger_bridge.handle(env, "/internal/ledger/handoff", "POST", "Bearer " + SECRET,
                                     json.dumps({"target": "http://insecure.example"})))
    assert plain[0] == 400


def test_a_moved_ledger_without_a_bridge_secret_refuses_instead_of_serving_stale_balances():
    old, new, net = _accounts()
    run(_ledger(old, net).credit("key:a", "pack:cs_1", 500, "pi_1", source="pack"))
    _handoff(old, net, NEW)
    unbridged = credits.DurableLedger(old.CREDITS, "", post=net.post, sleep=_no_sleep)

    try:
        run(unbridged.balance("key:a"))
    except credits.StoreNotConfigured as exc:
        assert "no bridge secret" in str(exc)
    else:
        raise AssertionError("a moved ledger must not answer from its stale copy")
