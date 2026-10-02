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
