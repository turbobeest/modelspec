"""Deployment smokes exercise enforcement offline, including the optional dpf key."""
from __future__ import annotations

import asyncio
import importlib.util
import io
import json
from pathlib import Path
from types import SimpleNamespace
import urllib.error
from urllib.parse import urlparse

import pytest
import yaml

from api.worker import openapi
from pipeline.worker_flags import production_vars
from tests.corpus import __main__ as corpus
from tests.corpus.corpus import Case, Expect
from tests.replay_billing_launch import replay

ROOT = Path(__file__).resolve().parents[1]
module_spec = importlib.util.spec_from_file_location(
    "private_rank_smoke", ROOT / ".github/scripts/check_private_rank.py")
private_rank = importlib.util.module_from_spec(module_spec)
module_spec.loader.exec_module(private_rank)
MISSING = {"error": {
    "code": "missing_api_key",
    "message": "This endpoint requires an API key. Get one at https://modelspec.dev/pricing.",
    "how_to_get_a_key": "https://modelspec.dev/pricing",
}}
KEY = "offline-smoke-key"


class Response(io.BytesIO):
    def __init__(self, status, body):
        super().__init__(json.dumps(body).encode())
        self.status = status


@pytest.fixture
def flags(tmp_path, monkeypatch):
    config = tmp_path / "api/worker/wrangler.jsonc"
    config.parent.mkdir(parents=True)

    def configure(enforced):
        config.write_text(json.dumps({
            "vars": {"ACCESS_ENFORCED": str(enforced).lower()},
            "env": {"staging": {"vars": {"ACCESS_ENFORCED": str(not enforced).lower()}}},
        }))
        assert production_vars(tmp_path)["ACCESS_ENFORCED"] == str(enforced).lower()

    monkeypatch.setattr(openapi, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(private_rank, "ROOT", tmp_path)
    monkeypatch.setattr(corpus, "production_vars", lambda _: production_vars(tmp_path))
    monkeypatch.delenv("MODELSPEC_SMOKE_API_KEY", raising=False)
    return configure


def fake_http(monkeypatch, *, enforced, leak=False, pointer=True):
    calls = []

    def request(req, timeout):
        path = urlparse(req.full_url).path
        key = req.get_header("Authorization")
        calls.append((path, key))
        if path == "/v1/health":
            return Response(200, {"service_commit": "deployed-sha", "export_loaded": True})
        if enforced and not key and not leak:
            body = json.loads(json.dumps(MISSING))
            if not pointer:
                del body["error"]["how_to_get_a_key"]
            raise urllib.error.HTTPError(req.full_url, 401, "Unauthorized", {}, Response(401, body))
        return Response(200, {"facets": [], "domains": [], "models": {}, "templates": [],
                              "estate": {}, "credits": {"exhausted": True}})

    monkeypatch.setattr(private_rank.urllib.request, "urlopen", request)
    return calls


@pytest.mark.parametrize("enforced,keyed", [(True, False), (True, True), (False, False)])
def test_private_smoke_checks_the_boundary_and_only_uses_an_optional_key(
        flags, monkeypatch, capsys, enforced, keyed):
    flags(enforced)
    if keyed:
        monkeypatch.setenv("MODELSPEC_SMOKE_API_KEY", KEY)
    calls = fake_http(monkeypatch, enforced=enforced)
    private_rank.main(["--host", "offline.example", "--commit", "deployed-sha"])
    assert calls[0] == ("/v1/health", None)
    if enforced:
        assert {(path, key) for path, key in calls if key is None} == {
            (path, None) for path in (
                "/v1/health", "/v1/rank", "/v1/policy-check", "/v1/decide",
                "/v1/compare", "/v1/vocabulary")
        }
    if keyed:
        assert {path for path, key in calls if key == f"Bearer {KEY}"} == {
            "/v1/rank", "/v1/policy-check", "/v1/decide", "/v1/vocabulary",
        }
    else:
        assert all(key is None for _, key in calls)
        if enforced:
            assert "::notice::" in capsys.readouterr().out


@pytest.mark.parametrize("leak,pointer", [(True, True), (False, False)])
def test_private_smoke_fails_on_a_free_machine_path_or_a_missing_pointer(
        flags, monkeypatch, leak, pointer):
    flags(True)
    fake_http(monkeypatch, enforced=True, leak=leak, pointer=pointer)
    with pytest.raises(SystemExit, match="Worker access check failed"):
        private_rank.main(["--host", "offline.example", "--commit", "deployed-sha"])


def probe_spec():
    response = lambda schema: {"content": {"application/json": {"schema": schema}}}
    operation = {
        "requestBody": {"content": {"application/json": {"example": {"spec_version": 1},
                                                          "schema": {"type": "object"}}}},
        "responses": {
            "200": response({"type": "object", "required": ["credits"], "properties": {
                "credits": {"type": "object", "required": ["exhausted"], "properties": {
                    "exhausted": {"type": "boolean"},
                }},
            }}),
            "401": response({"type": "object", "required": ["error"]}),
        },
    }
    return {"security": [{"bearer": []}], "paths": {
        **{path: {"post": operation} for path in (
            "/v1/rank", "/v1/policy-check", "/v1/decide", "/v1/compare")},
        "/v1/vocabulary": {"get": {"responses": operation["responses"]}},
        "/v1/health": {"get": {"security": [], "responses": {
            "200": response({"type": "object", "required": ["export_loaded"]}),
        }}},
    }}


@pytest.mark.parametrize("enforced,keyed", [(True, False), (True, True), (False, False)])
def test_openapi_probe_proves_the_keyless_boundary_and_accepts_exhausted_dpf_answers(
        flags, monkeypatch, capsys, enforced, keyed):
    flags(enforced)
    if keyed:
        monkeypatch.setenv("MODELSPEC_SMOKE_API_KEY", KEY)
    calls = fake_http(monkeypatch, enforced=enforced)
    assert openapi.probe("https://offline.example", probe_spec()) == 0
    assert ("/v1/health", None) in calls
    assert not any(path == "/v1/health" and key for path, key in calls)
    assert len(calls) == (11 if keyed else 6)
    if keyed:
        assert sum(key == f"Bearer {KEY}" for _, key in calls) == 5
    elif enforced:
        assert "::notice::" in capsys.readouterr().out


@pytest.mark.parametrize("leak,pointer", [(True, True), (False, False)])
def test_openapi_probe_rejects_keyless_data_or_an_unhelpful_refusal(
        flags, monkeypatch, leak, pointer):
    flags(True)
    fake_http(monkeypatch, enforced=True, leak=leak, pointer=pointer)
    assert openapi.probe("https://offline.example", probe_spec()) == 1


def test_generated_split_openapi_probe_matches_real_worker_keyless_responses(monkeypatch):
    monkeypatch.delenv("MODELSPEC_SMOKE_API_KEY", raising=False)
    monkeypatch.setenv("DATA_SPLIT_ENABLED", "true")
    paths = []

    def request(req, timeout):
        path = urlparse(req.full_url).path
        paths.append(path)
        assert req.get_header("Authorization") is None
        response, = asyncio.run(replay({"calls": [{
            "path": path, "method": req.get_method(),
            "headers": dict(req.header_items()),
            "body": req.data.decode() if req.data is not None else None,
        }]}))
        return Response(response["status"], json.loads(response["body"]))

    monkeypatch.setattr(openapi.urllib.request, "urlopen", request)
    assert openapi.probe("https://offline.example", yaml.safe_load(openapi.render())) == 0
    assert set(paths) >= {
        "/v1/rank", "/v1/policy-check", "/v1/decide", "/v1/compare",
        "/v1/vocabulary", "/v1/health",
    }


@pytest.mark.parametrize("enforced,keyed", [(True, False), (True, True), (False, False)])
def test_live_corpus_checks_keyless_refusals_and_optional_keyed_answers(
        tmp_path, flags, monkeypatch, capsys, enforced, keyed):
    flags(enforced)
    if keyed:
        monkeypatch.setenv("MODELSPEC_SMOKE_API_KEY", KEY)
    case = Case("lookup", "machine lookup", "live",
                {"spec_version": 1, "optimize": {"min": "offering.cost_per_task"}},
                Expect(200, status=("answered",)), live=True)
    monkeypatch.setattr(corpus, "load_cases", lambda: [case])
    calls = []

    def request(req, timeout):
        key = req.get_header("Authorization")
        calls.append(key)
        if req.data == b"{not json":
            return Response(400, {"error": {"code": "invalid_request"}})
        if len(req.data) > 64 * 1024:
            return Response(413, {"error": {"code": "payload_too_large"}})
        if enforced and not key:
            return Response(401, MISSING)
        return Response(200, {"status": "answered", "credits": {"exhausted": True}})

    monkeypatch.setattr(corpus.urllib.request, "urlopen", request)
    assert corpus._live(SimpleNamespace(out=tmp_path / "corpus", origin="https://offline.example",
                                       attempts=1)) == 0
    assert calls == ([None, f"Bearer {KEY}", None, None] if keyed else [None, None, None])
    rows = json.loads((tmp_path / "corpus/index.json").read_text())["cases"]
    assert [row["http"] for row in rows] == ([401, 200] if keyed else [401] if enforced else [200])
    if enforced and not keyed:
        assert "::notice::" in capsys.readouterr().out
