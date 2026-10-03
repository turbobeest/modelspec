"""All routes negotiate workerd's native compression, including refusals."""

import asyncio
import importlib.util
import json
import sys
from copy import deepcopy
from types import SimpleNamespace

import pytest

from tests.test_rank_worker import _guided_export
from tests.test_x402 import _entry_env, _Req, entry  # noqa: F401


def _import_bundle(entry, monkeypatch, blobs):  # noqa: F811
    bundle = SimpleNamespace(read=blobs.get)
    monkeypatch.setitem(sys.modules, "bundled_data", bundle)
    spec = importlib.util.spec_from_file_location("prepared_entry", entry.__file__)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert module._isolate_served is False
    return module, bundle


@pytest.mark.parametrize("accepted,expected", [
    ("br, gzip", "br"), ("gzip", "gzip"), ("identity", None), ("", None),
    ("br;q=0, gzip;q=.5", "gzip"), ("br;q=.2, gzip;q=.8", "gzip"),
    ("br;q=invalid", None), ("*;q=.5", "br"),
])
def test_encoding_respects_client_preferences(entry, accepted, expected):  # noqa: F811
    assert entry._response_encoding(accepted) == expected


@pytest.mark.parametrize("path,method,body", [
    ("/missing", "GET", None),
    ("/v1/rank", "POST", "invalid JSON"),
    ("/v1/decide", "POST", "invalid JSON"),
    ("/v1/rank", "DELETE", None),
])
def test_refusals_also_negotiate_brotli(entry, path, method, body):  # noqa: F811
    worker = entry.Default()
    worker.env = _entry_env(X402_ENABLED="false")
    response = asyncio.run(worker.fetch(_Req(path, body, method, {"accept-encoding": "br"})))
    assert response.status >= 400
    assert response.headers["content-encoding"] == "br"
    assert "Accept-Encoding" in response.headers["vary"]
    assert isinstance(response.json(), dict)


def test_compression_preserves_cors_and_does_not_recompress(entry):  # noqa: F811
    request = _Req("/v1/decide", headers={"accept-encoding": "br"})
    response = entry.Response("{}", headers={"vary": "Origin", "content-length": "2"})
    encoded = entry._compress_response(request, response)
    assert encoded.headers["vary"] == "Origin, Accept-Encoding"
    assert "content-length" not in encoded.headers
    assert entry._compress_response(request, encoded) is encoded
    assert entry._compress_response(_Req("/v1/health", method="HEAD"), response) is response
    empty = entry.Response("", status=204)
    assert entry._compress_response(request, empty) is empty


def test_bundled_rank_is_prepared_before_first_request(entry, monkeypatch):  # noqa: F811
    export = _guided_export()
    export["candidates"][0]["fits"] = {"test-device": None}
    hardware = {"hardware": [{"id": "test-device", "name": "Test device"}]}
    module, bundle = _import_bundle(entry, monkeypatch, {
        entry.CANDIDATES_PATH: json.dumps(export).encode(),
        entry.HARDWARE_PATH: json.dumps(hardware).encode(),
    })
    assert module._cache["hardware"] == hardware
    assert module._cache["prepared"] is not None

    def read_again(_):
        raise AssertionError("request decompressed or parsed the deployment bundle again")

    monkeypatch.setattr(bundle, "read", read_again)
    worker = module.Default()
    worker.env = _entry_env(X402_ENABLED="false")
    payload = {"use_case": "coding", "limit": 1, "environment": {"hardware": "test-device"}}
    response = asyncio.run(worker.fetch(_Req("/v1/rank", payload)))
    assert response.status == 200
    assert response.json()["result"][0]["model_id"] == "acme/guided"
    warm = asyncio.run(worker.fetch(_Req("/v1/rank", payload)))
    assert warm.status == 200
    assert warm.body.encode() == response.body.encode()
    assert 'isolate;desc="cold"' in response.headers["Server-Timing"]
    assert 'isolate;desc="warm"' in warm.headers["Server-Timing"]


@pytest.mark.parametrize("path,raw,error", [
    ("/api/decision/vocabulary.json", b"\xff", UnicodeDecodeError),
    ("/api/decision/vocabulary.json", b"{bad", json.JSONDecodeError),
    ("/api/rank/candidates.json", b"{bad", json.JSONDecodeError),
])
def test_malformed_required_bundle_fails_import(entry, monkeypatch, path, raw, error):  # noqa: F811
    with pytest.raises(error):
        _import_bundle(entry, monkeypatch, {path: raw})


@pytest.mark.parametrize("raw", [b"{bad", b"\xff", None])
def test_optional_bundled_hardware_failure_still_serves_rank(entry, monkeypatch, raw):  # noqa: F811
    module, _ = _import_bundle(entry, monkeypatch, {
        entry.CANDIDATES_PATH: json.dumps(_guided_export()).encode(),
        entry.HARDWARE_PATH: raw,
    })
    assert module._cache["hardware"] is None
    worker = module.Default()
    worker.env = _entry_env(X402_ENABLED="false")
    response = asyncio.run(worker.fetch(_Req("/v1/rank", {"use_case": "coding"})))
    assert response.status == 200
    refused = asyncio.run(worker.fetch(_Req("/v1/rank", {
        "use_case": "coding", "environment": {"hardware": "test-device"},
    })))
    assert refused.json()["error"]["code"] == "unknown_hardware"


def test_concurrent_real_requests_claim_only_one_cold_marker(entry, monkeypatch):  # noqa: F811
    module, _ = _import_bundle(entry, monkeypatch, {})
    export = _guided_export()

    async def both():
        arrivals = 0
        ready = asyncio.Event()

        async def get_json(url):
            nonlocal arrivals
            if url.endswith(module.CANDIDATES_PATH):
                arrivals += 1
                if arrivals == 2:
                    ready.set()
                await ready.wait()
                return export
            return None

        monkeypatch.setattr(module, "_get_json", get_json)
        first, second = module.Default(), module.Default()
        first.env = second.env = _entry_env(X402_ENABLED="false")
        return await asyncio.gather(
            first.fetch(_Req("/v1/rank", {"use_case": "coding"})),
            second.fetch(_Req("/v1/rank", {"use_case": "coding"})),
        )

    async def bounded():
        return await asyncio.wait_for(both(), timeout=5)

    responses = asyncio.run(bounded())
    assert all(response.status == 200 for response in responses)
    assert responses[0].body == responses[1].body
    timings = [response.headers["Server-Timing"] for response in responses]
    assert sum('isolate;desc="cold"' in timing for timing in timings) == 1
    assert sum('isolate;desc="warm"' in timing for timing in timings) == 1


@pytest.mark.parametrize("path,status", [("/v1/health", 200), ("/missing", 404)])
def test_health_and_refusals_consume_cold_marker(entry, monkeypatch, path, status):  # noqa: F811
    module, _ = _import_bundle(entry, monkeypatch, {
        entry.CANDIDATES_PATH: json.dumps(_guided_export()).encode(),
        entry.POLICY_PATH: b'{"models": []}',
    })
    worker = module.Default()
    worker.env = _entry_env(X402_ENABLED="false")
    cold = asyncio.run(worker.fetch(_Req(path, method="GET")))
    warm = asyncio.run(worker.fetch(_Req("/missing", method="GET")))
    assert cold.status == status
    assert 'isolate;desc="cold"' in cold.headers["Server-Timing"]
    assert 'isolate;desc="warm"' in warm.headers["Server-Timing"]


@pytest.mark.parametrize("path,method,status", [
    ("/v1/decide", "OPTIONS", 204),
    ("/v1/vocabulary", "HEAD", 200),
    ("/v1/health", "HEAD", 200),
])
def test_timing_preserves_bodyless_responses(entry, monkeypatch, path, method, status):  # noqa: F811
    module, _ = _import_bundle(entry, monkeypatch, {
        entry.CANDIDATES_PATH: json.dumps(_guided_export()).encode(),
        entry.POLICY_PATH: b'{"models": []}',
        "/api/decision/vocabulary.json": b"{}",
    })
    response_type = module.Response

    class StrictResponse(response_type):
        def __init__(self, body, status=200, headers=None):
            # The original preflight returns an empty string. Model workerd's
            # non-null stream when the timing wrapper tries to reconstruct it.
            if status in (204, 304) and body not in (None, ""):
                raise TypeError("bodyless status cannot have a body")
            super().__init__(body, status, headers)
            if body == "" and status in (204, 304):
                self.body = object()

    monkeypatch.setattr(module, "Response", StrictResponse)
    worker = module.Default()
    worker.env = _entry_env(X402_ENABLED="false")
    response = asyncio.run(worker.fetch(_Req(path, method=method, headers={
        "origin": "https://modelspec.dev", "accept-encoding": "br",
    })))
    assert response.status == status
    assert response.body is None
    assert "content-encoding" not in response.headers
    assert 'isolate;desc="cold"' in response.headers["Server-Timing"]
    if method == "OPTIONS":
        assert response.headers["access-control-allow-origin"] == "https://modelspec.dev"


def test_timing_preserves_not_modified_without_a_body(entry):  # noqa: F811
    async def not_modified(request):
        return entry.Response(object(), status=304, headers={"etag": '"same"'})

    worker = entry.Default()
    worker._fetch = not_modified
    response = asyncio.run(worker.fetch(_Req("/v1/vocabulary", method="GET")))
    assert response.status == 304
    assert response.body is None
    assert response.headers["etag"] == '"same"'
    assert 'isolate;desc="cold"' in response.headers["Server-Timing"]


def test_isolate_state_is_shared_and_preserves_existing_timing(entry):  # noqa: F811
    async def fetch(_request):
        return entry.Response('{"unchanged":true}', status=422,
                              headers={"server-timing": "snapshot;dur=12.3"})

    first, second = entry.Default(), entry.Default()
    first._fetch = second._fetch = fetch
    cold = asyncio.run(first.fetch(_Req("/v1/decide")))
    warm = asyncio.run(second.fetch(_Req("/v1/decide")))
    assert cold.body == warm.body == '{"unchanged":true}'
    assert cold.status == warm.status == 422
    assert cold.headers["Server-Timing"] == (
        'snapshot;dur=12.3, isolate;desc="cold", '
        'startup;desc="runtime restore unobservable from Python"')
    assert warm.headers["Server-Timing"] == 'snapshot;dur=12.3, isolate;desc="warm"'


def test_vocabulary_preparation_preserves_bytes_and_lookups(entry, monkeypatch):  # noqa: F811
    raw = ('{ "models": {"acme/a": {"display_name": "Café"}}, "facets": ['
           '{"id": "model.type", "label": "Type", "definition": "First sentence. More detail.", '
           '"values": [{"value": "llm-chat", "label": "Chat"}]}] }')
    module, bundle = _import_bundle(entry, monkeypatch, {
        "/api/decision/vocabulary.json": raw.encode(),
    })
    before = deepcopy(module._bundled_vocabulary)

    def read_again(_):
        raise AssertionError("request decompressed the vocabulary again")

    monkeypatch.setattr(bundle, "read", read_again)
    worker = module.Default()
    worker.env = _entry_env(X402_ENABLED="false")
    full = asyncio.run(worker.fetch(_Req("/v1/vocabulary", method="GET")))
    assert full.body.encode() == raw.encode()
    lookup = asyncio.run(worker.fetch(_Req("/v1/vocabulary?section=models", method="GET")))
    expected = {"facets": [], "domains": [], "templates": [], "models": {
        "acme/a": {"display_name": "Café"}}, "estate": {}}
    assert lookup.body == json.dumps(expected, ensure_ascii=False)
    for query in ("section=models&search=Caf", "section=models&id=acme/a&detail=full",
                  "section=models&offset=1", "section=facets", "section=estate"):
        response = asyncio.run(worker.fetch(_Req("/v1/vocabulary?" + query, method="GET")))
        assert response.status == 200
        assert module._bundled_vocabulary == before
    head = asyncio.run(worker.fetch(_Req("/v1/vocabulary", method="HEAD")))
    assert head.body is None
