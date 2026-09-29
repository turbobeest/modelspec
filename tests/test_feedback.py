"""MODEL-221: `POST /v1/feedback` — rules, privacy and the Worker wiring.

The service (`api/worker/src/feedback_service.py`) is driven directly under
CPython with `access_kv.MemoryKV`; the wiring through `entry.Default.fetch` uses
the same runtime stubs as `tests/test_access_wiring.py`.
"""

from __future__ import annotations

import asyncio
import importlib.util
import json
import sys
import types
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import jsonschema
import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
WORKER_SRC = REPO_ROOT / "api" / "worker" / "src"
for _path in (str(REPO_ROOT), str(WORKER_SRC)):
    if _path not in sys.path:
        sys.path.insert(0, _path)

import access_kv  # noqa: E402
import feedback_service as fb  # noqa: E402

SITE = frozenset({"https://modelspec.dev"})
NOW = datetime(2026, 9, 29, 15, 30, tzinfo=UTC)
PEPPER = b"p" * 32
ADDRESS = "203.0.113.7"


@pytest.fixture(autouse=True)
def _fresh_memory():
    fb._memory.clear()
    yield
    fb._memory.clear()


class ExplodingKV:
    async def get(self, name):
        raise AssertionError(f"the store was read: {name}")

    async def put(self, name, value, **kw):
        raise AssertionError(f"the store was written: {name}")

    async def delete(self, name):
        raise AssertionError(f"the store was written: {name}")


def _submit(body: Any, *, store: fb.Store, address: str = ADDRESS,
            origin: str | None = None, now: datetime = NOW) -> fb.Outcome:
    raw = body if isinstance(body, bytes) else json.dumps(body).encode()
    return asyncio.run(fb.submit(raw=raw, address=address, origin=origin,
                                 allowed_origins=SITE, store=store, now=now))


def _on(kv: Any | None = None) -> fb.Store:
    return fb.Store(enabled=True, kv=access_kv.MemoryKV() if kv is None else kv, pepper=PEPPER)


OFF = fb.Store(enabled=False, kv=ExplodingKV(), pepper=b"")
MINIMAL = {"rating": "unreliable", "client": "agent"}


def test_importing_the_service_draws_no_randomness() -> None:
    """The Workers runtime refuses entropy at startup; the module must import without it."""
    import ast
    tree = ast.parse((WORKER_SRC / "feedback_service.py").read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, (ast.Assign, ast.AnnAssign, ast.Expr)):
            calls = [n for n in ast.walk(node) if isinstance(n, ast.Call)]
            for call in calls:
                name = ast.unparse(call.func)
                assert not name.startswith(("secrets.", "os.urandom", "random.")), name


# ── the request ──────────────────────────────────────────────────────────────

def test_a_minimal_body_is_a_rating_and_a_client() -> None:
    parsed = fb.parse(MINIMAL)
    assert parsed == fb.Feedback(rating="unreliable", client="agent")


@pytest.mark.parametrize("body, fragment", [
    ({"client": "agent"}, "missing required field(s) ['rating']"),
    ({"rating": "great", "client": "agent"}, "rating must be one of"),
    ({"rating": "reliable", "client": "robot"}, "client must be one of"),
    ({**MINIMAL, "email": "a@b.test"}, "unknown field(s) ['email']"),
    ({**MINIMAL, "prompt": "hello"}, "unknown field(s) ['prompt']"),
    ({**MINIMAL, "decision_id": "abc"}, "decision_id must look like"),
    ({**MINIMAL, "page": "https://evil.test/x"}, "page must be a site path"),
    ({**MINIMAL, "template": "Coding Agent"}, "template must be a lowercase"),
    ({**MINIMAL, "note": 5}, "note must be a string or null"),
    ({**MINIMAL, "note": "x" * (fb.NOTE_MAX + 1)}, f"at most {fb.NOTE_MAX} characters"),
    ([MINIMAL], "the body must be a JSON object"),
])
def test_a_body_outside_the_schema_is_refused_with_the_reason(body, fragment) -> None:
    outcome = fb.parse(body)
    assert isinstance(outcome, fb.Outcome)
    assert outcome.status == 400
    assert outcome.body["error"]["code"] == "invalid_request"
    assert fragment in outcome.body["error"]["message"]


def test_a_page_keeps_its_path_and_loses_its_query() -> None:
    parsed = fb.parse({**MINIMAL, "client": "page", "page": "/decide/?spec=abc#answer"})
    assert parsed.page == "/decide/"


@pytest.mark.parametrize("text, cleaned, kinds", [
    ("write to jo.bloggs@example.com", "write to [email]", {"email"}),
    ("my key is sk-proj-abcdEFGH1234 oops", "my key is [secret] oops", {"secret"}),
    ("ModelSpec key live_ABCDEFGHIJKLMNOP1234", "ModelSpec key [secret]", {"secret"}),
    ("see https://modelspec.dev/decide/?spec=private", "see https://modelspec.dev/decide/",
     {"url_query"}),
    ("from 198.51.100.4 today", "from [ip] today", {"ip"}),
    ("call +44 20 7946 0958", "call [phone]", {"phone"}),
    ("token a1B2c3D4e5F6g7H8i9J0k1L2m3", "token [secret]", {"secret"}),
    # What must survive: model slugs, dates, token counts, decision IDs.
    ("llama-3-70b-instruct-2026-09-29 at 128000 200000 tokens on 2026-09-29",
     "llama-3-70b-instruct-2026-09-29 at 128000 200000 tokens on 2026-09-29", set()),
    ("about dec_3f9a1c2b7d4e5f6a7b8c9d0e1f", "about dec_3f9a1c2b7d4e5f6a7b8c9d0e1f", set()),
])
def test_free_text_is_scrubbed_of_personal_data_and_credentials(text, cleaned, kinds) -> None:
    assert fb.scrub(text) == (cleaned, kinds)


def test_the_scrub_is_reported_back_so_the_sender_knows() -> None:
    parsed = fb.parse({**MINIMAL, "note": "mail me: a@b.test", "trying_to_decide": "10.0.0.1"})
    assert parsed.note == "mail me: [email]"
    assert parsed.trying_to_decide == "[ip]"
    assert parsed.redacted == ("email", "ip")


# ── storage off, as shipped ──────────────────────────────────────────────────

def test_off_a_valid_body_is_answered_and_nothing_is_touched() -> None:
    outcome = _submit({**MINIMAL, "note": "top pick has no EU region"}, store=OFF)
    assert outcome.status == 200
    assert outcome.body["status"] == "not_recorded"
    assert outcome.body["recorded"] is False
    assert outcome.body["receipt"] is None
    assert "nothing was kept" in outcome.body["message"]


def test_off_an_invalid_body_is_still_refused() -> None:
    outcome = _submit({"rating": "meh", "client": "agent"}, store=OFF)
    assert outcome.status == 400


def test_the_shipped_configuration_is_off() -> None:
    from pipeline.worker_flags import parse_jsonc
    config = parse_jsonc((REPO_ROOT / "api/worker/wrangler.jsonc").read_text(encoding="utf-8"))
    assert config["vars"]["FEEDBACK_ENABLED"] == "false"
    assert config["env"]["staging"]["vars"]["FEEDBACK_ENABLED"] == "false"
    bindings = {kv["binding"] for kv in config["kv_namespaces"]}
    assert "FEEDBACK" not in bindings, "the FEEDBACK store is bound before Jamie signed off"


# ── storage on ───────────────────────────────────────────────────────────────

def test_on_a_record_holds_exactly_the_stored_fields_and_no_caller() -> None:
    kv = access_kv.MemoryKV()
    body = {"rating": "confusing", "client": "page", "decision_id": "dec_3f9a1c2b7d4e",
            "page": "/decide/", "template": "coding", "note": "which band is best?",
            "trying_to_decide": "a coding model under $1"}
    outcome = _submit(body, store=_on(kv), origin="https://modelspec.dev")

    assert outcome.status == 202
    assert outcome.body["status"] == "recorded"
    assert outcome.body["retention_days"] == fb.RETENTION_DAYS
    receipt = outcome.body["receipt"]
    assert fb.RECEIPT.fullmatch(receipt)

    records = {k: v for k, v in kv.data.items() if k.startswith(fb.RECORD_PREFIX)}
    assert len(records) == 1
    (name, value), = records.items()
    stored = json.loads(value)
    assert tuple(stored) == fb.STORED_FIELDS
    assert stored == {"received_on": "2026-09-29", **body, "redacted": []}
    assert kv.ttl[name] == fb.RETENTION_DAYS * 86_400
    # The receipt is the deletion handle and is never stored, nor is the caller.
    everything = json.dumps(kv.data)
    assert receipt not in everything
    for leak in (ADDRESS, "203.0.113", "modelspec.dev\"", "15:30"):
        assert leak not in everything, leak


def test_on_the_limit_counters_expire_and_are_named_by_an_hmac() -> None:
    kv = access_kv.MemoryKV()
    _submit(MINIMAL, store=_on(kv))
    counters = [k for k in kv.data if k.startswith(fb.LIMIT_PREFIX)]
    assert sorted(counters)[0] == f"{fb.LIMIT_PREFIX}day/2026-09-29/" + fb._mac(
        PEPPER, "2026-09-29", ADDRESS)
    assert all(kv.ttl[k] == 2 * 86_400 for k in counters)
    assert all(ADDRESS not in k for k in counters)
    # The same address tomorrow is a different, unlinkable name.
    assert fb._mac(PEPPER, "2026-09-30", ADDRESS) != fb._mac(PEPPER, "2026-09-29", ADDRESS)


@pytest.mark.parametrize("store", [
    fb.Store(enabled=True, kv=None, pepper=PEPPER),
    fb.Store(enabled=True, kv=access_kv.MemoryKV(), pepper=b""),
], ids=["no-namespace", "no-pepper"])
def test_on_without_a_store_or_a_pepper_refuses_rather_than_store_unkeyed(store) -> None:
    outcome = _submit(MINIMAL, store=store)
    assert outcome.status == 503
    assert outcome.body["error"]["code"] == "feedback_store_unavailable"


def test_a_burst_from_one_address_is_limited_in_memory_only() -> None:
    for _ in range(fb.BURST_LIMIT):
        assert _submit(MINIMAL, store=OFF).status == 200
    refused = _submit(MINIMAL, store=OFF)
    assert refused.status == 429
    assert refused.headers["retry-after"] == "60"
    assert refused.body["error"]["retry_after"] == 60
    assert all(ADDRESS not in name for name in fb._memory)
    # Another address, and the next minute, are unaffected.
    assert _submit(MINIMAL, store=OFF, address="198.51.100.9").status == 200
    assert _submit(MINIMAL, store=OFF, now=NOW + timedelta(minutes=1)).status == 200


def test_the_daily_limit_per_address_and_the_global_cap() -> None:
    kv = access_kv.MemoryKV()
    store = _on(kv)
    for i in range(fb.DAILY_LIMIT):
        assert _submit(MINIMAL, store=store, now=NOW + timedelta(minutes=i)).status == 202
    refused = _submit(MINIMAL, store=store, now=NOW + timedelta(hours=1))
    assert refused.status == 429
    assert "a day from one address" in refused.body["error"]["message"]

    kv.data[f"{fb.LIMIT_PREFIX}global/2026-09-29"] = str(fb.GLOBAL_DAILY_CAP)
    capped = _submit(MINIMAL, store=store, address="198.51.100.9")
    assert capped.status == 429
    assert "all the feedback it can for today" in capped.body["error"]["message"]


def test_a_receipt_deletes_its_record_and_nothing_else() -> None:
    kv = access_kv.MemoryKV()
    store = _on(kv)
    first = _submit(MINIMAL, store=store).body["receipt"]
    _submit({**MINIMAL, "rating": "reliable"}, store=store, now=NOW + timedelta(minutes=1))

    def withdraw(body: Any) -> fb.Outcome:
        return asyncio.run(fb.withdraw(raw=json.dumps(body).encode(), address=ADDRESS,
                                       origin=None, allowed_origins=SITE, store=store,
                                       now=NOW + timedelta(minutes=2)))

    assert withdraw({"receipt": first}).status == 200
    left = [json.loads(v)["rating"] for k, v in kv.data.items() if k.startswith(fb.RECORD_PREFIX)]
    assert left == ["reliable"]
    assert withdraw({"receipt": first}).body["error"]["code"] == "receipt_not_found"
    assert withdraw({"receipt": "dec_x"}).status == 400
    assert withdraw({"receipt": first, "extra": 1}).status == 400


def test_a_browser_on_another_origin_is_refused() -> None:
    assert _submit(MINIMAL, store=OFF, origin="https://evil.test").status == 403
    assert _submit(MINIMAL, store=OFF, origin="https://modelspec.dev").status == 200
    assert _submit(MINIMAL, store=OFF, origin=None).status == 200


def test_an_oversized_or_malformed_body_is_refused_before_parsing() -> None:
    assert _submit(b"{" + b" " * fb.MAX_BODY_BYTES + b"}", store=OFF).status == 413
    assert _submit(b"{not json", store=OFF).status == 400


# ── what is published ────────────────────────────────────────────────────────

def test_the_published_schema_is_generated_from_the_validator() -> None:
    committed = json.loads((REPO_ROOT / "schemas/feedback-v1.schema.json").read_text("utf-8"))
    assert committed == fb.request_schema(), (
        "schemas/feedback-v1.schema.json drifted; regenerate it with "
        "`python -m tests.test_feedback`")


@pytest.mark.parametrize("body", [
    MINIMAL,
    {"rating": "trustworthy", "client": "cli", "decision_id": "dec_3f9a1c2b7d4e",
     "note": None, "trying_to_decide": "cheapest local coder"},
    *fb.request_schema()["examples"],
])
def test_the_schema_and_the_validator_accept_the_same_bodies(body) -> None:
    jsonschema.validate(body, fb.request_schema())
    assert isinstance(fb.parse(body), fb.Feedback)


@pytest.mark.parametrize("body", [
    {"rating": "reliable"},
    {**MINIMAL, "extra": True},
    {**MINIMAL, "rating": "ok"},
    {**MINIMAL, "decision_id": "nope"},
])
def test_the_schema_and_the_validator_refuse_the_same_bodies(body) -> None:
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(body, fb.request_schema())
    assert isinstance(fb.parse(body), fb.Outcome)


def test_every_refusal_has_a_documented_fix() -> None:
    doc = (REPO_ROOT / "docs/feedback-api.md").read_text(encoding="utf-8")
    for code, (status, fix) in fb.ERRORS.items():
        assert f"| `{code}` | {status} | {fix} |" in doc, code


# ── the Worker's entry point ─────────────────────────────────────────────────

class _Response:
    def __init__(self, body, status=200, headers=None):
        self.body, self.status, self.headers = body, status, headers or {}

    def json(self):
        return json.loads(self.body)


@pytest.fixture(scope="module")
def entry():
    saved = {name: sys.modules.get(name) for name in ("js", "workers")}
    js = types.ModuleType("js")

    async def _no_fetch(url):  # pragma: no cover
        raise AssertionError(f"unexpected fetch of {url}")

    js.fetch = _no_fetch
    workers = types.ModuleType("workers")
    workers.Response = _Response
    workers.WorkerEntrypoint = type("WorkerEntrypoint", (), {})
    sys.modules["js"], sys.modules["workers"] = js, workers
    try:
        spec = importlib.util.spec_from_file_location(
            "modelspec_worker_entry_feedback", WORKER_SRC / "entry.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        yield module
    finally:
        for name, value in saved.items():
            if value is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = value


class Request:
    def __init__(self, method: str, body: Any = None, headers: dict[str, str] | None = None):
        self.url = "https://api.modelspec.test/v1/feedback"
        self.method = method
        self._body = "" if body is None else json.dumps(body)
        self._headers = {k.lower(): v for k, v in (headers or {}).items()}
        self.headers = types.SimpleNamespace(get=lambda name: self._headers.get(name.lower()))

    async def text(self):
        return self._body


class WorkersKV:
    """A KV binding as Pyodide sees it: `put` takes an options object."""

    def __init__(self):
        self.values: dict[str, str] = {}

    async def get(self, name):
        return self.values.get(name)

    async def put(self, name, value, options=None):
        self.values[name] = value

    async def delete(self, name):
        self.values.pop(name, None)


def _call(entry, request, **env: Any) -> _Response:
    worker = entry.Default()
    worker.env = types.SimpleNamespace(BUILD_COMMIT="c0ffee",
                                       EXPORT_ORIGIN="https://modelspec.test", **env)
    return asyncio.run(worker.fetch(request))


def test_the_worker_answers_not_recorded_as_shipped(entry) -> None:
    response = _call(entry, Request("POST", MINIMAL, {"CF-Connecting-IP": ADDRESS,
                                                       "authorization": "Bearer live_x"}),
                     FEEDBACK_ENABLED="false")
    assert response.status == 200
    assert response.json()["status"] == "not_recorded"
    assert response.json()["service_commit"] == "c0ffee"


def test_the_worker_stores_when_switched_on_and_bound(entry) -> None:
    kv = WorkersKV()
    response = _call(entry, Request("POST", {**MINIMAL, "client": "page", "page": "/"},
                                    {"CF-Connecting-IP": ADDRESS,
                                     "origin": "https://modelspec.dev"}),
                     FEEDBACK_ENABLED="true", FEEDBACK=kv, FEEDBACK_LIMIT_PEPPER="x" * 32)
    assert response.status == 202
    assert response.headers["access-control-allow-origin"] == "https://modelspec.dev"
    assert sum(k.startswith(fb.RECORD_PREFIX) for k in kv.values) == 1

    receipt = response.json()["receipt"]
    deleted = _call(entry, Request("DELETE", {"receipt": receipt}, {"CF-Connecting-IP": ADDRESS}),
                    FEEDBACK_ENABLED="true", FEEDBACK=kv, FEEDBACK_LIMIT_PEPPER="x" * 32)
    assert deleted.json()["status"] == "deleted"
    assert not any(k.startswith(fb.RECORD_PREFIX) for k in kv.values)


def test_the_worker_answers_a_site_preflight_and_refuses_another(entry) -> None:
    ok = _call(entry, Request("OPTIONS", headers={"origin": "https://modelspec.dev"}))
    assert ok.status == 204
    assert "DELETE" in ok.headers["access-control-allow-methods"]
    assert _call(entry, Request("OPTIONS", headers={"origin": "https://evil.test"})).status == 403
    dev = _call(entry, Request("OPTIONS", headers={"origin": "http://localhost:8000"}),
                FEEDBACK_DEV_ORIGINS="http://localhost:8000")
    assert dev.status == 204


def test_the_worker_refuses_other_verbs_and_names_the_endpoint(entry) -> None:
    assert _call(entry, Request("GET")).status == 405
    assert {"POST /v1/feedback", "DELETE /v1/feedback"} <= set(entry.ACCEPTED_ENDPOINTS)


def test_the_mcp_workers_forwarded_address_is_used_only_without_cloudflares(entry) -> None:
    headers = {"x-modelspec-client-ip": "198.51.100.9"}
    for _ in range(fb.BURST_LIMIT):
        assert _call(entry, Request("POST", MINIMAL, headers)).status == 200
    assert _call(entry, Request("POST", MINIMAL, headers)).status == 429
    # A caller on the public route cannot pick its own bucket: Cloudflare's wins.
    spoofed = {"CF-Connecting-IP": ADDRESS, "x-modelspec-client-ip": "198.51.100.9"}
    assert _call(entry, Request("POST", MINIMAL, spoofed)).status == 200


def test_the_feedback_path_reads_no_key_and_no_header_but_origin_and_address() -> None:
    import re
    service = (WORKER_SRC / "feedback_service.py").read_text(encoding="utf-8")
    # The service is handed an address and an origin, never the request.
    assert "request.headers" not in service and not re.search(r"^from js |^import js$", service, re.M)
    entry_source = (WORKER_SRC / "entry.py").read_text(encoding="utf-8")
    handler = entry_source[entry_source.index("async def _feedback"):
                           entry_source.index("def _x402_wrap")]
    read = set(re.findall(r'request\.headers\.get\("([^"]+)"\)', handler))
    assert read == {"origin", "CF-Connecting-IP", "x-modelspec-client-ip"}
    assert "access.gate" not in handler and "api_key" not in handler


if __name__ == "__main__":
    (REPO_ROOT / "schemas/feedback-v1.schema.json").write_text(
        json.dumps(fb.request_schema(), indent=2) + "\n", encoding="utf-8")


# ── an agent that has only llms.txt or only openapi.yaml ─────────────────────

def _worker_post(entry, url: str, body: Any, **env: Any) -> _Response:
    """POST to the Worker's entry point at the path an agent discovered."""
    from urllib.parse import urlparse

    request = Request("POST", body, {"CF-Connecting-IP": ADDRESS, "user-agent": "some-agent/1"})
    request.url = "https://api.modelspec.test" + urlparse(url).path
    return _call(entry, request, **env)


def _published(url: str) -> dict[str, Any]:
    """Fetch a modelspec.dev URL from what the site build publishes."""
    from pipeline import feedback_page

    assert url == f"https://modelspec.dev/{feedback_page.SCHEMA_PATH.as_posix()}", url
    return json.loads((REPO_ROOT / "schemas/feedback-v1.schema.json").read_text(encoding="utf-8"))


def _body_from_schema(schema: dict[str, Any]) -> dict[str, Any]:
    """What an agent writes from a schema alone: every required field, a valid value."""
    body = {}
    for name in schema["required"]:
        options = schema["properties"][name]["enum"]
        body[name] = "agent" if "agent" in options else "unreliable" if "unreliable" in options \
            else options[0]
    return body


def test_an_agent_with_only_llms_txt_finds_and_uses_the_endpoint(entry) -> None:
    import re
    from pipeline.build import llms_txt
    from pipeline.export import Build

    text = llms_txt(site="ModelSpec", base="https://modelspec.dev",
                    build=Build(commit="abcdef1234567890", built_at="2026-09-29T00:00:00+00:00",
                                as_of=datetime(2026, 9, 29).date()))
    line = next(line for line in text.splitlines() if "feedback" in line.lower())
    endpoint = re.search(r"POST (https://\S+)", line).group(1)
    schema = _published(re.search(r"Schema: (https://\S+\.json)", line).group(1))
    body = _body_from_schema(schema)
    jsonschema.validate(body, schema)

    off = _worker_post(entry, endpoint, body)
    assert off.status == 200 and off.json()["status"] == "not_recorded"
    kv = WorkersKV()
    on = _worker_post(entry, endpoint, {**body, "decision_id": "dec_3f9a1c2b7d4e"},
                      FEEDBACK_ENABLED="true", FEEDBACK=kv, FEEDBACK_LIMIT_PEPPER="x" * 32)
    assert on.status == 202 and on.json()["status"] == "recorded"
    stored = [json.loads(v) for k, v in kv.values.items() if k.startswith(fb.RECORD_PREFIX)]
    assert stored[0]["rating"] == "unreliable" and stored[0]["client"] == "agent"


def test_an_agent_with_only_openapi_finds_and_uses_the_endpoint(entry) -> None:
    import yaml
    worker = str(REPO_ROOT / "api" / "worker")
    sys.path.insert(0, worker)
    try:
        import openapi as generator
    finally:
        sys.path.remove(worker)
    spec = yaml.safe_load((REPO_ROOT / "api/worker/openapi.yaml").read_text(encoding="utf-8"))
    assert "/v1/feedback" in spec["info"]["description"]
    path, operation = next((path, ops["post"]) for path, ops in spec["paths"].items()
                           if "post" in ops and "feedback" in ops["post"].get("operationId", ""))
    assert operation.get("security") == [{}], "an agent must see that no key is needed"
    content = operation["requestBody"]["content"]["application/json"]
    for body in (content["example"], generator._example_from_schema(content["schema"], spec)):
        response = _worker_post(entry, spec["servers"][0]["url"] + path, body)
        assert str(response.status) in operation["responses"]
        schema = operation["responses"][str(response.status)]["content"]["application/json"]
        assert generator._validate(response.json(), schema["schema"], spec) == []
        assert response.json()["status"] == "not_recorded"


# ── the CLI ──────────────────────────────────────────────────────────────────

@pytest.fixture
def cli_against_worker(entry, monkeypatch):
    """`modelspec feedback` wired to the Worker's entry point instead of the network."""
    import httpx
    from cli.modelspec import feedback_cmd

    seen: list[httpx.Request] = []
    env: dict[str, Any] = {}

    def handle(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        headers = {k: v for k, v in request.headers.items()}
        worker_request = Request(request.method, json.loads(request.content), headers)
        worker_request.url = str(request.url)
        response = _call(entry, worker_request, **env)
        return httpx.Response(response.status, content=response.body.encode(),
                              headers={"content-type": "application/json"})

    monkeypatch.setattr(feedback_cmd, "_transport", httpx.MockTransport(handle))
    monkeypatch.setenv("MODELSPEC_API_KEY", "live_ABCDEFGHIJKLMNOP1234")
    return types.SimpleNamespace(seen=seen, env=env)


def _cli(*args: str):
    from typer.testing import CliRunner
    from cli.modelspec import cli as cli_mod
    return CliRunner().invoke(cli_mod.app, ["feedback", *args])


def test_the_cli_dry_run_prints_the_body_and_sends_nothing(cli_against_worker) -> None:
    result = _cli("dec_3f9a1c2b7d4e", "--rating", "confusing", "--note", "bands?", "--dry-run")
    assert result.exit_code == 0
    assert json.loads(result.stdout)["body"] == {
        "rating": "confusing", "client": "cli", "decision_id": "dec_3f9a1c2b7d4e", "note": "bands?"}
    assert cli_against_worker.seen == []


def test_the_cli_sends_no_key_and_reports_not_recorded(cli_against_worker) -> None:
    result = _cli("dec_3f9a1c2b7d4e", "--rating", "unreliable", "--json")
    assert result.exit_code == 0, result.output
    assert json.loads(result.stdout)["result"]["status"] == "not_recorded"
    (request,) = cli_against_worker.seen
    assert "authorization" not in request.headers and "x-api-key" not in request.headers
    assert request.headers["user-agent"].startswith("modelspec-cli/")
    assert json.loads(request.content) == {"rating": "unreliable", "client": "cli",
                                           "decision_id": "dec_3f9a1c2b7d4e"}


def test_the_cli_prints_the_receipt_when_recorded(cli_against_worker) -> None:
    cli_against_worker.env.update(FEEDBACK_ENABLED="true", FEEDBACK=WorkersKV(),
                                  FEEDBACK_LIMIT_PEPPER="x" * 32)
    result = _cli("--rating", "reliable", "--note", "worked, mail a@b.test")
    assert result.exit_code == 0, result.output
    assert "Your feedback was recorded" in result.stdout
    assert "Receipt (keep it to delete this later): fbr_" in result.stdout
    assert "Removed before storage: email" in result.stdout


def test_the_cli_refuses_a_bad_rating_before_the_network(cli_against_worker) -> None:
    result = _cli("--rating", "meh", "--json")
    assert result.exit_code == 1
    assert json.loads(result.stderr)["error"]["code"] == "invalid_request"
    assert cli_against_worker.seen == []


def test_the_cli_passes_the_workers_refusal_through(cli_against_worker) -> None:
    for _ in range(fb.BURST_LIMIT):
        assert _cli("--rating", "reliable").exit_code == 0
    result = _cli("--rating", "reliable", "--json")
    assert result.exit_code == 1
    assert json.loads(result.stderr)["error"]["code"] == "rate_limited"


def test_the_root_help_tells_an_agent_about_feedback() -> None:
    from typer.testing import CliRunner
    from cli.modelspec import cli as cli_mod
    help_text = CliRunner().invoke(cli_mod.app, ["--help"]).stdout
    assert "modelspec feedback <decision_id> --rating" in help_text
    assert "feedback" in help_text.split("Decision commands", 1)[1]
