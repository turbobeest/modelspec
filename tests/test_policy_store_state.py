"""The determination store's four states, as `/v1/health` reports them (MODEL-80).

Observed live on 2026-09-17, right after the `DETERMINATIONS` namespace was
bound and before anything was loaded into it: `/v1/health` said
`last_error: "JSONDecodeError: Expecting value: line 1 column 1 (char 0)"`. The
namespace was simply empty. Workers KV answers a missing key with JS `null`,
Pyodide hands that to Python as `pyodide.ffi.jsnull` rather than `None`, the
`is None` test let it through, and its `str()` went to `json.loads`. An empty
store read as a corrupt one.

These tests hold the four states apart:

* **unbound** — no binding; not an error;
* **empty** — bound, no manifest; not an error, whichever way KV says "absent"
  (`None`, Pyodide's `jsnull`, or an empty string);
* **loaded** — manifest present and both blobs match its SHA-256s;
* **broken** — a manifest exists and a blob is missing, mismatched or not JSON;
  this one is an error and says so.

And the rule that must survive all of it: an entitled request that cannot read
the store gets 503 — for an *empty* store too — never the free answer.

`entry.py` imports the Workers runtime (`js`, `workers`), which does not exist
under CPython, so both are stubbed here with the least that lets the module
import. Nothing in the stubs is asserted on.
"""

from __future__ import annotations

import asyncio
import hashlib
import importlib.util
import json
import sys
import types
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
WORKER_SRC = REPO_ROOT / "api" / "worker" / "src"


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
            "modelspec_worker_entry", WORKER_SRC / "entry.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        yield module
    finally:
        for name, value in saved.items():
            if value is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = value


@pytest.fixture(autouse=True)
def fresh_cache(entry, monkeypatch):
    entry._store_cache.update({"at": 0.0, "store": None, "error": None,
                               "state": None, "message": None})

    async def export(origin, *, force=False):
        return {"build": {"commit": "deadbeef"}, "candidates": []}, None

    async def catalogue(origin):
        return {"build": {"commit": "deadbeef"}, "models": [],
                "platform_classes": {"all": [], "unbounded": []}}

    monkeypatch.setattr(entry, "_load_export", export)
    monkeypatch.setattr(entry, "_load_policy_catalogue", catalogue)
    yield


class JsNull:
    """Stands in for `pyodide.ffi.jsnull`: what KV's `null` becomes in Pyodide.

    Its `str()` is deliberately not JSON, which is what made the old code raise
    `JSONDecodeError` on an empty namespace.
    """

    def __str__(self):
        return "jsnull"


class StubKV:
    """A Workers KV namespace. `missing` is what a get of an absent key returns."""

    def __init__(self, values=None, missing=None):
        self.values, self.missing = dict(values or {}), missing
        self.reads: list[str] = []

    async def get(self, key):
        self.reads.append(key)
        return self.values.get(key, self.missing)


def _env(kv=None):
    env = types.SimpleNamespace(BUILD_COMMIT="c0ffee", EXPORT_ORIGIN="https://modelspec.test")
    if kv is not None:
        env.DETERMINATIONS = kv
    return env


def _bundle(entry, *, tamper=None, drop=None):
    """The three KV values `load_determinations.py` would write."""
    cu = json.dumps({"bundle_version": "1", "kind": "commercial_use",
                     "generated_on": "2026-09-17", "count": 0, "commercial_use": {}})
    res = json.dumps({"bundle_version": "1", "kind": "residency",
                      "generated_on": "2026-09-17", "count": 0, "residency": {}})
    blobs = {entry.KV_COMMERCIAL_USE: cu, entry.KV_RESIDENCY: res}
    manifest = {"bundle_version": "1", "generated_on": "2026-09-17",
                "blobs": {k: {"sha256": hashlib.sha256(v.encode()).hexdigest()}
                          for k, v in blobs.items()}}
    values = {**blobs, entry.KV_MANIFEST: json.dumps(manifest)}
    if tamper:
        values.update(tamper)
    if drop:
        values.pop(drop)
    return values


def _health(entry, env) -> dict:
    worker = entry.Default()
    worker.env = env
    return asyncio.run(worker._health("c0ffee", "https://modelspec.test")).json()["determinations"]


# ── the four states ──────────────────────────────────────────────────────────

def test_unbound_is_a_state_not_an_error(entry):
    health = _health(entry, _env())
    assert health["bound"] is False
    assert health["state"] == "unbound"
    assert health["loaded"] is False
    assert health["last_error"] is None


@pytest.mark.parametrize("missing", [None, JsNull(), ""], ids=["none", "jsnull", "empty-string"])
def test_a_bound_empty_namespace_is_empty_not_corrupt(entry, missing):
    kv = StubKV(missing=missing)
    health = _health(entry, _env(kv))
    assert health == {
        "bound": True, "state": "empty", "loaded": False,
        "bundle_version": None, "generated_on": None,
        "message": entry.STORE_MESSAGES["empty"], "last_error": None,
    }
    # With no manifest there is nothing to verify a blob against; do not read one.
    assert kv.reads == [entry.KV_MANIFEST]


def test_a_verified_bundle_is_loaded(entry):
    health = _health(entry, _env(StubKV(_bundle(entry))))
    assert health["state"] == "loaded"
    assert health["loaded"] is True
    assert health["bundle_version"] == "1"
    assert health["generated_on"] == "2026-09-17"
    assert health["last_error"] is None


@pytest.mark.parametrize("missing", [None, JsNull(), ""], ids=["none", "jsnull", "empty-string"])
def test_a_manifest_naming_a_missing_blob_is_broken(entry, missing):
    kv = StubKV(_bundle(entry, drop="determinations/residency"), missing=missing)
    health = _health(entry, _env(kv))
    assert health["state"] == "broken"
    assert health["loaded"] is False
    assert "determinations/residency is named by the manifest" in health["last_error"]


def test_a_blob_that_fails_its_checksum_is_broken(entry):
    kv = StubKV(_bundle(entry, tamper={"determinations/commercial_use": '{"x": 1}'}))
    health = _health(entry, _env(kv))
    assert health["state"] == "broken"
    assert "does not match the manifest" in health["last_error"]


def test_a_manifest_that_is_not_json_is_broken(entry):
    kv = StubKV(_bundle(entry, tamper={"determinations/manifest": "{not json"}))
    health = _health(entry, _env(kv))
    assert health["state"] == "broken"
    assert health["last_error"].startswith("JSONDecodeError")


# ── the MODEL-80 rule: an entitled request never gets the free answer ────────

def _entitled_check(entry, monkeypatch, env):
    policy_service = sys.modules["policy_service"]
    monkeypatch.setattr(entry, "_entitlement",
                        lambda request, env: policy_service.ENTITLEMENT_DETERMINATIONS)
    worker = entry.Default()
    worker.env = env
    payload = {"policy": {"licence": {"prohibited": ["cc-by-nc-4.0"]}}}
    response = asyncio.run(worker._policy_check(payload, "c0ffee", "https://modelspec.test"))
    return response.status, response.json()


@pytest.mark.parametrize("missing", [None, JsNull(), ""], ids=["none", "jsnull", "empty-string"])
def test_an_entitled_request_against_an_empty_store_is_refused_with_503(
        entry, monkeypatch, missing):
    status, body = _entitled_check(entry, monkeypatch, _env(StubKV(missing=missing)))
    assert status == 503
    assert body["error"]["code"] == "determinations_unavailable"
    assert body["error"]["store_state"] == "empty"
    assert body["error"]["last_error"] is None
    assert body["result"] == []


def test_an_entitled_request_with_no_binding_is_refused_with_503(entry, monkeypatch):
    status, body = _entitled_check(entry, monkeypatch, _env())
    assert status == 503
    assert body["error"]["store_state"] == "unbound"


def test_an_entitled_request_against_a_broken_store_is_refused_with_503(entry, monkeypatch):
    kv = StubKV(_bundle(entry, tamper={"determinations/residency": "[]"}))
    status, body = _entitled_check(entry, monkeypatch, _env(kv))
    assert status == 503
    assert body["error"]["store_state"] == "broken"
    assert "does not match the manifest" in body["error"]["last_error"]


def test_an_entitled_request_against_a_loaded_store_is_answered(entry, monkeypatch):
    status, body = _entitled_check(entry, monkeypatch, _env(StubKV(_bundle(entry))))
    assert status == 200
    assert body["determinations"]["included"] is True
