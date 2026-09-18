"""MODEL-69 through the Worker's real entry point: `entry.Default.fetch`.

`tests/test_api_access.py` proves the access modules on their own. This file
proves the wiring — that the switch, the key store binding and the tier table
reach `access.gate` the way `wrangler.jsonc` and the deploy set them, and that
what a caller sees is what `docs/api-access.md` says:

* **Enforcement off** (as shipped): no key is served exactly as before; a
  presented key is checked — sandbox, metered live, or refused. A bad key is
  never downgraded to anonymous.
* **Enforcement on**: no key is a 401 naming where to get one.
* **ACCESS bound** (as shipped): a presented live key is checked against the
  store. No key is issued yet (MODEL-73).
* **No ACCESS binding** (fallback): a presented live key is refused
  `access_store_not_configured`; anonymous and `test_` requests are unaffected.
* The ACCESS store is a stub that behaves as Workers KV does under Pyodide: a
  missing key reads as a `jsnull` stand-in, not `None`.

`entry.py` imports the Workers runtime (`js`, `workers`), stubbed here with the
least that lets it import, exactly as `tests/test_policy_store_state.py` does.
"""

from __future__ import annotations

import asyncio
import importlib.util
import json
import sys
import types
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
WORKER_SRC = REPO_ROOT / "api" / "worker" / "src"
TIERS = (REPO_ROOT / "api" / "worker" / "tiers.json").read_text(encoding="utf-8")

EXPORT = {"build": {"commit": "deadbeef", "built_at": "2026-09-17T00:00:00Z",
                    "export_schema_version": "2.0"},
          "candidates": []}
CATALOGUE = {"build": {"commit": "deadbeef"}, "models": [],
             "platform_classes": {"all": [], "unbounded": []}}


class _Response:
    def __init__(self, body, status=200, headers=None):
        self.body, self.status, self.headers = body, status, headers or {}

    def json(self):
        return json.loads(self.body)


class _WorkerEntrypoint:
    pass


@pytest.fixture(scope="module")
def entry():
    saved = {name: sys.modules.get(name) for name in ("js", "workers")}
    js = types.ModuleType("js")

    async def _no_fetch(url):  # pragma: no cover - every test stubs the loaders
        raise AssertionError(f"unexpected fetch of {url}")

    js.fetch = _no_fetch
    workers = types.ModuleType("workers")
    workers.Response = _Response
    workers.WorkerEntrypoint = _WorkerEntrypoint
    sys.modules["js"], sys.modules["workers"] = js, workers
    for path in (str(REPO_ROOT), str(WORKER_SRC)):
        if path not in sys.path:
            sys.path.insert(0, path)
    try:
        spec = importlib.util.spec_from_file_location(
            "modelspec_worker_entry_access", WORKER_SRC / "entry.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        yield module
    finally:
        for name, value in saved.items():
            if value is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = value


class DataPath:
    """Counts reads of the published exports, so a test can say none happened."""

    def __init__(self) -> None:
        self.reads = 0


@pytest.fixture
def data(entry, monkeypatch) -> DataPath:
    seen = DataPath()
    entry._store_cache.update({"at": 0.0, "store": None, "error": None,
                               "state": None, "message": None})

    async def export(origin, *, force=False):
        seen.reads += 1
        return EXPORT, None

    async def catalogue(origin):
        seen.reads += 1
        return CATALOGUE

    def rank(payload, candidates, hardware, service_commit, origin):
        # The scorer is proven elsewhere; here a live answer only has to be
        # recognisable as one, and an empty catalogue would make it a 422.
        return 200, {**entry.service._envelope(candidates, service_commit, origin),
                     "live": True, "result": [{"rank": 1}]}

    monkeypatch.setattr(entry, "_load_export", export)
    monkeypatch.setattr(entry, "_load_policy_catalogue", catalogue)
    monkeypatch.setattr(entry.service, "rank", rank)
    return seen


class JsNull:
    """`pyodide.ffi.jsnull`, as Workers KV's `null` reaches Python."""

    def __str__(self):
        return "jsnull"


class WorkersKV:
    """A Workers KV binding: a missing key reads as `jsnull`, not `None`."""

    def __init__(self, missing: Any = None) -> None:
        self.missing = JsNull() if missing is None else missing
        self.values: dict[str, str] = {}
        self.ops: list[tuple[str, str]] = []

    async def get(self, name):
        self.ops.append(("get", name))
        return self.values.get(name, self.missing)

    async def put(self, name, value, options=None):
        self.ops.append(("put", name))
        self.values[name] = value

    async def delete(self, name):
        self.ops.append(("delete", name))
        self.values.pop(name, None)


class ExplodingKV:
    async def get(self, name):
        raise AssertionError(f"the store was read: {name}")

    async def put(self, name, value, options=None):
        raise AssertionError(f"the store was written: {name}")

    async def delete(self, name):
        raise AssertionError(f"the store was written: {name}")


class Request:
    def __init__(self, path: str, body: Any, key: str | None = None,
                 header: str = "authorization") -> None:
        self.url = f"https://api.modelspec.test{path}"
        self.method = "POST"
        self._body = json.dumps(body)
        self._headers = {}
        if key is not None:
            self._headers[header] = f"Bearer {key}" if header == "authorization" else key
        self.headers = types.SimpleNamespace(get=lambda name: self._headers.get(name.lower()))

    async def text(self):
        return self._body


def _env(*, enforced: str | None = "false", access: Any = None, tier_policy: bool = True,
         determinations: Any = None):
    env = types.SimpleNamespace(BUILD_COMMIT="c0ffee", EXPORT_ORIGIN="https://modelspec.test")
    if enforced is not None:
        env.ACCESS_ENFORCED = enforced
    if access is not None:
        env.ACCESS = access
    if tier_policy:
        env.TIER_POLICY = TIERS  # what the deploy passes with --var
    if determinations is not None:
        env.DETERMINATIONS = determinations
    return env


def _call(entry, env, request) -> _Response:
    worker = entry.Default()
    worker.env = env
    return asyncio.run(worker.fetch(request))


RANK = ("/v1/rank", {"use_case": "general"})
POLICY = ("/v1/policy-check", {"policy": {"licence": {"prohibited": ["cc-by-nc-4.0"]}}})


def _issue(entry, binding: WorkersKV, tier: str, secret: str) -> None:
    import access_config
    import access_keys
    import access_kv
    asyncio.run(access_keys.issue(
        access_kv.CloudflareKV(binding), tier=tier, owner="tests@modelspec.dev",
        now=datetime.now(UTC), policy=access_config.policy_from_json(TIERS), secret=secret))
    binding.ops.clear()


# ── enforcement off: anonymous is unchanged ──────────────────────────────────

@pytest.mark.parametrize("endpoint", [RANK, POLICY], ids=["rank", "policy-check"])
def test_off_an_unkeyed_request_is_answered_exactly_as_before(entry, data, endpoint):
    """No store read, no meter, no tier table needed, no access headers."""
    path, body = endpoint
    response = _call(entry, _env(access=ExplodingKV(), tier_policy=False), Request(path, body))
    assert response.status != 401
    answer = response.json()
    assert "error" not in answer or answer["error"]["code"] not in {
        "missing_api_key", "access_not_configured", "access_store_not_configured"}
    assert not {h for h in response.headers if h.startswith(("ratelimit", "x-modelspec-tier"))}
    assert data.reads == 1
    if path == "/v1/policy-check":
        assert answer["determinations"]["entitlement"] == "public_export"


def test_the_shipped_configuration_is_off_and_bound():
    """What this file tests as 'the default' is what `wrangler.jsonc` ships."""
    config = (REPO_ROOT / "api" / "worker" / "wrangler.jsonc").read_text(encoding="utf-8")
    live = "\n".join(l for l in config.splitlines() if not l.lstrip().startswith("//"))
    assert '"ACCESS_ENFORCED": "false"' in live
    assert '"binding": "ACCESS"' in live, "the ACCESS binding is no longer live; update the docs"


def test_the_deploy_hands_the_isolate_the_tier_table():
    workflow = (REPO_ROOT / ".github" / "workflows" / "rank-api.yml").read_text(encoding="utf-8")
    assert '--var "TIER_POLICY:$(jq -c . tiers.json)"' in workflow


# ── enforcement off: a presented key is checked ──────────────────────────────

def test_off_a_sandbox_key_gets_the_sandbox_and_touches_no_data(entry, data):
    response = _call(entry, _env(access=ExplodingKV()), Request(*RANK, key="test_anything"))
    assert response.status == 200
    body = response.json()
    assert body["sandbox"] is True
    assert all(row["model_id"].startswith("sandbox/") for row in body["result"])
    assert data.reads == 0
    assert response.headers["x-modelspec-tier"] == "sandbox"


def test_the_sandbox_refuses_what_the_live_parser_refuses(entry, data):
    response = _call(entry, _env(), Request("/v1/rank", {"use_case": "nope"}, key="test_x"))
    assert response.status == 400
    assert response.json()["error"]["code"] == "unknown_use_case"
    assert data.reads == 0


def test_the_sandbox_does_not_answer_policy_check_and_touches_no_data(entry, data):
    response = _call(entry, _env(access=ExplodingKV()), Request(*POLICY, key="test_x"))
    assert response.status == 400
    assert response.json()["error"]["code"] == "sandbox_not_available"
    assert data.reads == 0


@pytest.mark.parametrize("missing", [JsNull(), "", None], ids=["jsnull", "empty-string", "none"])
@pytest.mark.parametrize("enforced", ["false", "true"], ids=["off", "on"])
def test_an_unknown_key_is_refused_never_served_as_anonymous(entry, data, missing, enforced):
    """The jsnull bug, end to end: a mistyped key is a clean 401, not a crash."""
    binding = WorkersKV()
    binding.missing = missing
    response = _call(entry, _env(enforced=enforced, access=binding),
                     Request(*RANK, key="live_mistyped"))
    assert response.status == 401
    assert response.json()["error"]["code"] == "invalid_api_key"
    assert data.reads == 0
    assert [op for op, _ in binding.ops] == ["get"]


def test_off_a_revoked_key_is_refused(entry, data):
    import access_keys
    import access_kv
    binding = WorkersKV()
    _issue(entry, binding, "free", "live_gone")
    asyncio.run(access_keys.revoke(access_kv.CloudflareKV(binding), "live_gone"))
    response = _call(entry, _env(access=binding), Request(*RANK, key="live_gone"))
    assert response.status == 403
    assert response.json()["error"]["code"] == "key_revoked"
    assert data.reads == 0


def test_off_a_free_key_is_metered_and_the_429_says_when(entry, data):
    binding = WorkersKV()
    _issue(entry, binding, "free", "live_free")
    env = _env(access=binding)
    statuses = [_call(entry, env, Request(*RANK, key="live_free")).status for _ in range(5)]
    assert statuses == [200] * 5
    refused = _call(entry, env, Request(*RANK, key="live_free"))
    assert refused.status == 429
    error = refused.json()["error"]
    assert error["code"] == "rate_limited"
    for field in ("limit", "window", "resets_at", "retry_after_seconds"):
        assert field in error
    assert refused.headers["retry-after"]
    assert refused.headers["ratelimit-limit"]
    # Every value the store holds is a count or a record; none of it is the key.
    assert "live_free" not in json.dumps(binding.values) + "".join(binding.values)
    assert "live_free" not in refused.body + json.dumps(refused.headers)


def test_the_key_is_read_from_x_api_key_too(entry, data):
    binding = WorkersKV()
    _issue(entry, binding, "free", "live_header")
    response = _call(entry, _env(access=binding),
                     Request(*RANK, key="live_header", header="x-api-key"))
    assert response.status == 200
    assert response.headers["x-modelspec-tier"] == "free"


# ── the entitlement follows the tier ─────────────────────────────────────────

def test_a_free_key_gets_the_free_policy_answer(entry, data):
    binding = WorkersKV()
    _issue(entry, binding, "free", "live_free_pc")
    response = _call(entry, _env(access=binding, determinations=ExplodingKV()),
                     Request(*POLICY, key="live_free_pc"))
    assert response.status == 200
    assert response.json()["determinations"]["entitlement"] == "public_export"


@pytest.mark.parametrize("tier", ["paid", "dpf"])
def test_a_paid_or_exempt_key_is_entitled_to_the_determinations(entry, data, tier):
    """Entitled, so it reads the store — and with none loaded it is the 503,
    never the free answer. That the 503 arrives is the proof of entitlement."""
    binding = WorkersKV()
    _issue(entry, binding, tier, f"live_{tier}_pc")
    response = _call(entry, _env(access=binding), Request(*POLICY, key=f"live_{tier}_pc"))
    assert response.status == 503
    assert response.json()["error"]["code"] == "determinations_unavailable"


def test_the_exempt_key_takes_the_paid_keys_path_through_the_entry_point(
        entry, data, monkeypatch):
    """DPF is exempt and on the same handler as a paid key: identical steps,
    both metered, through `Default.fetch` and not only through `serve`."""
    import access
    outcomes = []
    real = access.gate

    async def recording(**kwargs):
        outcome = await real(**kwargs)
        outcomes.append(outcome)
        return outcome

    monkeypatch.setattr(entry.access, "gate", recording)
    binding = WorkersKV()
    _issue(entry, binding, "paid", "live_paying")
    _issue(entry, binding, "dpf", "live_exempt")
    env = _env(access=binding)
    paid = _call(entry, env, Request(*RANK, key="live_paying"))
    exempt = _call(entry, env, Request(*RANK, key="live_exempt"))
    assert paid.status == exempt.status == 200
    assert outcomes[0].trace == outcomes[1].trace == ("key.lookup", "limits.consume",
                                                     "serve.live")
    assert outcomes[0].meter.window("daily").used == outcomes[1].meter.window("daily").used == 1
    assert outcomes[1].meter.window("daily").limit is None


# ── no key store bound (as shipped) ──────────────────────────────────────────

@pytest.mark.parametrize("enforced", ["false", "true"], ids=["off", "on"])
def test_with_no_access_binding_a_live_key_is_refused_clearly(entry, data, enforced):
    response = _call(entry, _env(enforced=enforced), Request(*RANK, key="live_someone"))
    assert response.status == 503
    error = response.json()["error"]
    assert error["code"] == "access_store_not_configured"
    assert "access store not configured" in error["message"]
    assert data.reads == 0


def test_with_no_access_binding_anonymous_and_sandbox_are_unaffected(entry, data):
    assert _call(entry, _env(), Request(*RANK)).status == 200
    sandbox = _call(entry, _env(), Request(*RANK, key="test_x"))
    assert sandbox.status == 200 and sandbox.json()["sandbox"] is True


def test_with_no_tier_table_a_key_is_refused_and_anonymous_is_unaffected(
        entry, data, monkeypatch, tmp_path):
    import access_config
    monkeypatch.setattr(access_config, "DEFAULT_POLICY_PATH", tmp_path / "absent.json")
    env = _env(access=WorkersKV(), tier_policy=False)
    keyed = _call(entry, env, Request(*RANK, key="live_x"))
    assert keyed.status == 500
    assert keyed.json()["error"]["code"] == "access_not_configured"
    assert _call(entry, env, Request(*RANK)).status == 200


# ── enforcement on ───────────────────────────────────────────────────────────

@pytest.mark.parametrize("endpoint", [RANK, POLICY], ids=["rank", "policy-check"])
def test_on_an_unkeyed_request_is_refused_and_told_how_to_get_a_key(entry, data, endpoint):
    response = _call(entry, _env(enforced="true", access=ExplodingKV()), Request(*endpoint))
    assert response.status == 401
    error = response.json()["error"]
    assert error["code"] == "missing_api_key"
    assert error["how_to_get_a_key"].startswith("https://")
    assert response.headers["www-authenticate"].startswith("Bearer")
    assert data.reads == 0


def test_on_a_valid_key_is_served(entry, data):
    binding = WorkersKV()
    _issue(entry, binding, "free", "live_on")
    response = _call(entry, _env(enforced="true", access=binding), Request(*RANK, key="live_on"))
    assert response.status == 200
    assert response.headers["x-modelspec-tier"] == "free"


def test_on_the_sandbox_still_needs_no_store(entry, data):
    response = _call(entry, _env(enforced="true"), Request(*RANK, key="test_on"))
    assert response.status == 200 and response.json()["sandbox"] is True
