"""MODEL-441: the credit ledger moves between Cloudflare accounts by a one-way
handoff.

Two in-memory "accounts", each with its Durable Object namespace, joined by
the bridge over a fake HTTPS hop that can drop requests or lose answers. The
properties under test are the ones the move must keep: every balance arrives,
a payment credited before the move stays a duplicate after it, exactly one
ledger accepts writes at a time, and no sequence of re-runs, lost answers,
duplicate deliveries or rollbacks leaves none.
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
    """Objects by name, as `idFromName` gives them."""

    def __init__(self, env):
        self._env = env
        self.objects: dict[str, credits_do.CreditsObject] = {}

    def _object(self, name):
        if name not in self.objects:
            ctx = type("Ctx", (), {})()
            ctx.storage = type("Storage", (), {"sql": Sql()})()
            self.objects[name] = credits_do.CreditsObject(ctx, env=self._env)
        return self.objects[name]

    @property
    def obj(self):
        return self._object(credits.ledger_name(self._env))

    def idFromName(self, name):
        return name

    def get(self, name):
        return Stub(self._object(name))


class Env:
    def __init__(self, secret=SECRET, target="", standby=False):
        self.LEDGER_BRIDGE_SECRET = secret
        self.LEDGER_BRIDGE_TARGET = target
        self.LEDGER_STANDBY = "true" if standby else ""
        self.LEDGER_NAME = ""
        self.CREDITS = Namespace(self)


class Network:
    """HTTPS between the two Workers. `down` makes a host unreachable before
    the request lands; `lose_answer` lets the request land and loses the reply."""

    def __init__(self, envs: dict[str, Env]):
        self.envs = envs
        self.down: set[str] = set()
        self.lose_answer: set[str] = set()
        self.sent: list[tuple[str, dict]] = []

    async def post(self, url, payload, headers):
        origin = url.split("/internal/", 1)[0]
        self.sent.append((url, payload))
        if origin in self.down:
            raise ConnectionError("unreachable")
        path = "/internal/" + url.split("/internal/", 1)[1]
        answer = await ledger_bridge.handle(
            self.envs[origin], path, "POST", headers["authorization"],
            json.dumps(payload), post=self.post)
        if origin in self.lose_answer:
            raise TimeoutError("answer lost")
        return answer


def run(coro):
    return asyncio.run(coro)


def _accounts():
    old, new = Env(target=NEW), Env(target=OLD, standby=True)
    net = Network({OLD: old, NEW: new})
    return old, new, net


def _ledger(env, net):
    return credits.DurableLedger(env.CREDITS, SECRET, post=net.post, sleep=_no_sleep,
                                 bridge_target=env.LEDGER_BRIDGE_TARGET,
                                 name=credits.ledger_name(env))


async def _no_sleep(_seconds):
    return None


def _handoff(env, net, target):
    return run(ledger_bridge.handle(env, "/internal/ledger/handoff", "POST",
                                    "Bearer " + SECRET, json.dumps({"target": target}),
                                    post=net.post))


def _status(env):
    return run(ledger_bridge.handle(env, "/internal/ledger/status", "GET",
                                    "Bearer " + SECRET, ""))[1]


def _balance(env, net, holder="key:a"):
    return run(_ledger(env, net).balance(holder)).available


def _credit(env, net, payment, units, holder="key:a"):
    return run(_ledger(env, net).credit(holder, payment, units, "tx-" + payment, source="pack"))


def _refuses(env, net):
    try:
        _balance(env, net)
    except credits.LedgerUnavailable:
        return True
    return False


def _live_objects(*envs):
    """Every ledger object in every account that would serve a call."""
    return [(i, name) for i, env in enumerate(envs)
            for name, obj in env.CREDITS.objects.items()
            if run(obj.handoff_status())["role"] == "live"]


def _imports(net):
    return [payload for url, payload in net.sent if url.endswith("/import")]


def _roll_back_into_a_fresh_ledger(old):
    old.LEDGER_NAME = "ledger-2"
    old.LEDGER_STANDBY = "true"


def test_balances_arrive_and_later_calls_on_the_old_worker_land_in_the_new_ledger():
    old, new, net = _accounts()
    _credit(old, net, "pack:cs_1", 500)
    run(_ledger(old, net).set_monthly("key:b", 4000, "in_1", "Solo"))

    status, body = _handoff(old, net, NEW)

    assert (status, body["role"], body["target"]) == (200, "moved", NEW)
    assert _status(new)["imported_handoff"] == body["handoff"]
    assert _balance(new, net) == 500
    assert run(_ledger(new, net).balance("key:b")).monthly == 4000
    _credit(old, net, "pack:cs_2", 250)
    assert (_balance(new, net), _balance(old, net)) == (750, 750)
    assert _live_objects(old, new) == [(1, "ledger")]


def test_a_payment_credited_before_the_move_is_a_duplicate_after_it_on_either_worker():
    old, new, net = _accounts()
    _credit(old, net, "pack:cs_1", 500)
    _handoff(old, net, NEW)

    assert (_credit(old, net, "pack:cs_1", 500).credited,
            _credit(new, net, "pack:cs_1", 500).credited) == (False, False)
    assert _balance(new, net) == 500


def test_a_receiving_ledger_serves_nothing_until_it_is_handed_over():
    old, new, net = _accounts()

    assert _refuses(new, net)
    assert (_status(old)["role"], _status(new)["role"]) == ("live", "standby")
    assert _live_objects(old, new) == [(0, "ledger")]


def test_a_refused_import_unseals_the_old_ledger_and_it_keeps_serving():
    old, new, net = _accounts()
    _credit(old, net, "pack:cs_1", 500)
    live_target = Env(target=OLD)
    net.envs[NEW] = live_target
    _credit(live_target, net, "pack:cs_9", 1, holder="key:z")

    status, body = _handoff(old, net, NEW)

    assert (status, body["error"]["code"]) == (409, "import_refused")
    assert _status(old)["role"] == "live"
    _credit(old, net, "pack:cs_2", 1)
    assert _balance(old, net) == 501


def test_an_unreachable_target_keeps_the_seal_and_a_rerun_finishes():
    old, new, net = _accounts()
    _credit(old, net, "pack:cs_1", 500)
    net.down.add(NEW)

    status, body = _handoff(old, net, NEW)

    assert (status, body["error"]["code"]) == (502, "import_unknown")
    assert _status(old)["role"] == "moving"
    assert _refuses(old, net)
    net.down.clear()
    assert _handoff(old, net, NEW)[1]["role"] == "moved"
    assert _balance(old, net) == 500
    assert _live_objects(old, new) == [(1, "ledger")]


def test_a_lost_answer_then_writes_on_the_target_then_a_rerun_leaves_one_live_ledger():
    old, new, net = _accounts()
    _credit(old, net, "pack:cs_1", 10)
    net.lose_answer.add(NEW)
    assert _handoff(old, net, NEW)[0] == 502
    net.lose_answer.clear()
    _credit(new, net, "pack:cs_2", 5)

    status, body = _handoff(old, net, NEW)

    assert (status, body["role"]) == (200, "moved")
    assert _live_objects(old, new) == [(1, "ledger")]
    assert (_balance(old, net), _balance(new, net)) == (15, 15)


def test_a_duplicate_import_delivered_late_never_revives_a_copy():
    old, new, net = _accounts()
    _credit(old, net, "pack:cs_1", 5)
    _handoff(old, net, NEW)
    late = _imports(net)[-1]
    _credit(new, net, "pack:cs_2", 7)
    _roll_back_into_a_fresh_ledger(old)
    _handoff(new, net, OLD)

    replay = run(ledger_bridge.handle(new, "/internal/ledger/import", "POST", "Bearer " + SECRET,
                                      json.dumps(late)))

    assert replay[0] == 200 and replay[1]["role"] == "moved"
    assert _live_objects(old, new) == [(0, "ledger-2")]
    assert _balance(old, net) == 12


def test_a_rollback_receives_the_ledger_into_a_fresh_object_with_every_later_write():
    old, new, net = _accounts()
    _credit(old, net, "pack:cs_1", 500)
    _handoff(old, net, NEW)
    _credit(new, net, "pack:cs_2", 100)
    _roll_back_into_a_fresh_ledger(old)
    assert _refuses(old, net)

    status, body = _handoff(new, net, OLD)

    assert (status, body["role"]) == (200, "moved")
    assert _live_objects(old, new) == [(0, "ledger-2")]
    assert (_balance(old, net), _balance(new, net)) == (600, 600)
    assert _credit(old, net, "pack:cs_1", 500).credited is False


def test_a_rollback_cannot_overwrite_the_moved_original():
    old, new, net = _accounts()
    _credit(old, net, "pack:cs_1", 5)
    _handoff(old, net, NEW)

    status, body = _handoff(new, net, OLD)

    assert (status, body["error"]["code"]) == (409, "import_refused")
    assert _live_objects(old, new) == [(1, "ledger")]


def test_a_target_that_moved_on_before_the_source_heard_back_lets_the_source_finish():
    old, new, net = _accounts()
    _credit(old, net, "pack:cs_1", 5)
    net.lose_answer.add(NEW)
    _handoff(old, net, NEW)
    net.lose_answer.clear()
    run(new.CREDITS.obj.begin_handoff(OLD))

    status, body = _handoff(old, net, NEW)

    assert (status, body["role"]) == (200, "moved")
    assert _status(old)["role"] == "moved"


def test_rerunning_a_finished_handoff_changes_nothing():
    old, new, net = _accounts()
    _credit(old, net, "pack:cs_1", 500)
    first = _handoff(old, net, NEW)
    _credit(old, net, "pack:cs_2", 1)

    again = _handoff(old, net, NEW)

    assert again == (200, _status(old))
    assert first[1]["handoff"] == again[1]["handoff"]
    assert _balance(new, net) == 501


def test_there_is_no_remote_way_to_unseal_a_moving_ledger():
    old, new, net = _accounts()
    _credit(old, net, "pack:cs_1", 5)
    net.down.add(NEW)
    _handoff(old, net, NEW)

    for body in ({}, {"force": True}):
        answer = run(ledger_bridge.handle(old, "/internal/ledger/abort", "POST",
                                          "Bearer " + SECRET, json.dumps(body)))
        assert answer[0] == 404
    assert _status(old)["role"] == "moving"


def test_break_glass_unseals_only_the_named_handoff_and_abandons_its_target():
    old, new, net = _accounts()
    _credit(old, net, "pack:cs_1", 5)
    net.down.add(NEW)
    _handoff(old, net, NEW)
    handoff = _status(old)["handoff"]

    old.LEDGER_UNSEAL_HANDOFF = "0" * 32
    assert _status(old)["role"] == "moving"
    old.LEDGER_UNSEAL_HANDOFF = handoff
    assert _status(old)["role"] == "live"
    assert _balance(old, net) == 5
    net.down.clear()
    status, body = _handoff(old, net, NEW)
    assert (status, body["error"]["code"]) == (409, "handoff_refused")
    assert _status(old)["role"] == "live"


def test_an_import_that_commits_but_loses_its_answer_never_unseals_the_source():
    old, new, net = _accounts()
    _credit(old, net, "pack:cs_1", 10)
    namespace = new.CREDITS
    original = namespace.get
    namespace.get = lambda name: AnswerLostAfterImport(namespace._object(name))

    status, body = _handoff(old, net, NEW)

    assert (status, body["error"]["code"]) == (502, "import_unknown")
    assert _status(old)["role"] == "moving"
    namespace.get = original
    assert _handoff(old, net, NEW)[1]["role"] == "moved"
    assert _live_objects(old, new) == [(1, "ledger")]
    assert _balance(new, net) == 10


def test_a_restart_between_the_state_and_the_record_leaves_a_rerun_that_imports_again():
    old, new, net = _accounts()
    _credit(old, net, "pack:cs_1", 5)
    sealed = run(old.CREDITS.obj.begin_handoff(NEW))
    new.CREDITS.obj._save(credits.LedgerState.from_json(json.loads(sealed["state"])))

    status, body = _handoff(old, net, NEW)

    assert (status, body["role"]) == (200, "moved")
    assert _live_objects(old, new) == [(1, "ledger")]
    assert _balance(new, net) == 5


def test_a_target_without_the_bridge_keeps_the_source_sealed():
    old, new, net = _accounts()
    _credit(old, net, "pack:cs_1", 10)
    net.envs[NEW] = Env(secret="", standby=True)

    status, body = _handoff(old, net, NEW)

    assert (status, body["error"]["code"]) == (502, "import_unknown")
    assert _status(old)["role"] == "moving"


def test_a_reservation_whose_forwarded_answer_was_lost_can_be_found_and_released():
    old, new, net = _accounts()
    _credit(old, net, "pack:cs_1", 10)
    _handoff(old, net, NEW)
    net.lose_answer.add(NEW)
    try:
        run(_ledger(old, net).reserve("key:a", 3))
    except credits.LedgerUnavailable:
        pass
    net.lose_answer.clear()

    holds = run(_ledger(old, net)._call("open_holds", "key:a"))
    assert holds == {"reservations": {"1": 3}, "taken_reads": []}
    assert run(_ledger(old, net).release("key:a", 1)) is True
    assert _balance(new, net) == 10


def test_the_bridge_refuses_without_the_secret_and_names_only_ledger_methods():
    env = Env(target=NEW)
    no_secret = Env(secret="")

    assert run(ledger_bridge.handle(no_secret, "/internal/ledger/status", "GET", "", ""))[0] == 404
    assert run(ledger_bridge.handle(env, "/internal/ledger/status", "GET", "Bearer wrong", ""))[0] == 401
    bad = run(ledger_bridge.handle(env, "/internal/ledger/call", "POST", "Bearer " + SECRET,
                                   json.dumps({"method": "begin_handoff", "args": [NEW]})))
    assert bad[0] == 400
    assert _status(env)["role"] == "live"


def test_a_moved_ledger_without_a_bridge_refuses_instead_of_serving_stale_balances():
    old, new, net = _accounts()
    _credit(old, net, "pack:cs_1", 500)
    _handoff(old, net, NEW)
    unbridged = credits.DurableLedger(old.CREDITS, "", post=net.post, sleep=_no_sleep)

    try:
        run(unbridged.balance("key:a"))
    except credits.LedgerUnavailable as exc:
        assert "no bridge configured" in str(exc)
    else:
        raise AssertionError("a moved ledger must not answer from its stale copy")


class EchoingStub(Stub):
    """A ledger method whose error message echoes caller input."""

    def __init__(self, obj, echoed):
        super().__init__(obj)
        self._echoed = echoed

    def __getattr__(self, name):
        if name == "credit":
            async def call(*_args):
                raise RuntimeError(f"PythonError: ValueError: bad payment id {self._echoed}")
            return call
        return super().__getattr__(name)


def test_a_seal_mark_echoed_in_an_error_never_forwards_a_live_ledgers_call():
    old, new, net = _accounts()
    namespace = old.CREDITS
    namespace.get = lambda name: EchoingStub(namespace._object(name), "ledger-sealed: moved")
    ledger = credits.DurableLedger(namespace, SECRET, post=net.post, sleep=_no_sleep,
                                   bridge_target=NEW)

    try:
        run(ledger.credit("key:a", "x402:ledger-sealed: moved", 1, "tx"))
    except RuntimeError as exc:
        assert "bad payment id" in str(exc)
    else:
        raise AssertionError("the original error must surface")
    assert net.sent == []


def test_a_moved_ledger_forwards_only_to_the_configured_target():
    old, new, net = _accounts()
    _credit(old, net, "pack:cs_1", 500)
    _handoff(old, net, NEW)
    elsewhere = credits.DurableLedger(old.CREDITS, SECRET, post=net.post, sleep=_no_sleep,
                                      bridge_target="https://other.example.workers.dev")

    try:
        run(elsewhere.balance("key:a"))
    except credits.LedgerUnavailable as exc:
        assert "not configured to reach" in str(exc)
    else:
        raise AssertionError("a target other than the configured one must be refused")


def test_a_handoff_goes_only_to_the_configured_target():
    old, new, net = _accounts()

    status, body = _handoff(old, net, "https://attacker.example")

    assert (status, body["error"]["code"]) == (400, "invalid_request")
    assert _status(old)["role"] == "live"


class AnswerLostAfterImport(Stub):
    """The import commits, then the answer back to the Worker is lost."""

    def __getattr__(self, name):
        method = super().__getattr__(name)
        if name != "import_state":
            return method

        async def call(*args):
            await method(*args)
            raise RuntimeError("Network connection lost.")
        return call
