"""All routes negotiate workerd's native compression, including refusals."""

import asyncio
import importlib.util
import json
from types import SimpleNamespace

import pytest

from tests.test_rank_worker import _guided_export
from tests.test_x402 import _Req, _entry_env, entry  # noqa: F401


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
    bundle = SimpleNamespace(read=lambda path: json.dumps(export).encode()
                             if path == entry.CANDIDATES_PATH else None)
    import sys

    monkeypatch.setitem(sys.modules, "bundled_data", bundle)
    spec = importlib.util.spec_from_file_location("latency_prepared_entry", entry.__file__)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    def read_again(_):
        raise AssertionError("request decompressed or parsed the deployment bundle again")

    monkeypatch.setattr(bundle, "read", read_again)
    worker = module.Default()
    worker.env = _entry_env(X402_ENABLED="false")
    response = asyncio.run(worker.fetch(_Req("/v1/rank", {"use_case": "coding", "limit": 1})))
    assert response.status == 200
    assert response.json()["result"][0]["model_id"] == "acme/guided"


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
    import sys

    raw = '{ "models": {"acme/a": {"display_name": "Café"}}, "facets": [] }'
    bundle = SimpleNamespace(read=lambda path: raw.encode()
                             if path == "/api/decision/vocabulary.json" else None)
    monkeypatch.setitem(sys.modules, "bundled_data", bundle)
    spec = importlib.util.spec_from_file_location("prepared_vocabulary_entry", entry.__file__)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

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
    head = asyncio.run(worker.fetch(_Req("/v1/vocabulary", method="HEAD")))
    assert head.body == ""
