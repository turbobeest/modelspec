"""MODEL-292: gate-off bodies and original headers remain equal to before the visit gate.

The expected responses were recorded from origin/main before the visit gate
existed (tests/fixtures/visit_gate_off_main.json). This file imports nothing
the gate added. MODEL-291 adds guide discovery headers to every /v1 response;
those additions are checked separately before comparing the original response.
"""
import asyncio
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from tests.test_human_gate import IP, ORIGIN, PRIMARY
from tests.test_x402 import _Req, _decision_worker, _entry_env, entry  # noqa: F401

MAIN = json.loads((Path(__file__).parent / "fixtures" / "visit_gate_off_main.json").read_text())["responses"]
#: Derived from the clock; it is not behaviour.
VOLATILE = {"server-timing", "date", "content-length", "ratelimit-reset"}

SITE = {"origin": ORIGIN, "CF-Connecting-IP": IP}
REQUESTS = {
    "decide POST": ("/v1/decide", PRIMARY, "POST", SITE),
    "decide OPTIONS": ("/v1/decide", None, "OPTIONS", SITE),
    "vocabulary GET": ("/v1/vocabulary", None, "GET", SITE),
    "vocabulary GET query": ("/v1/vocabulary?section=facets", None, "GET", SITE),
    "vocabulary HEAD": ("/v1/vocabulary", None, "HEAD", SITE),
    "vocabulary OPTIONS": ("/v1/vocabulary", None, "OPTIONS", SITE),
    "unknown GET": ("/v1/nope", None, "GET", SITE),
    "visit-token POST": ("/v1/visit-token", None, "POST", {**SITE, "x-modelspec-turnstile": "t"}),
    "visit-token GET": ("/v1/visit-token", None, "GET", SITE),
    "visit-token OPTIONS": ("/v1/visit-token", None, "OPTIONS", SITE),
    "visit-token POST no origin": ("/v1/visit-token", None, "POST", {}),
    "visit-token OPTIONS no origin": ("/v1/visit-token", None, "OPTIONS", {}),
}


def _snapshot(response):
    try:
        body = response.json()
    except Exception:
        body = response.body.decode() if isinstance(response.body, bytes) else response.body
    headers = {key: value for key, value in sorted(dict(response.headers).items()) if key.lower() not in VOLATILE}
    return {"status": response.status, "headers": headers, "body": body}


@pytest.fixture
def worker(monkeypatch):
    bundle = SimpleNamespace(read=lambda path: b'{"facets":[]}' if path == "/api/decision/vocabulary.json" else None)
    monkeypatch.setitem(sys.modules, "bundled_data", bundle)
    module = entry.__wrapped__(monkeypatch)
    return _decision_worker(module, _entry_env(VISIT_GATE_ENABLED="false", HUMAN_GATE_ENABLED="false"))


def test_the_recording_covers_every_request():
    assert set(MAIN) == set(REQUESTS)


@pytest.mark.parametrize("name", sorted(REQUESTS))
def test_flag_off_response_equals_main(worker, name):
    path, body, method, headers = REQUESTS[name]
    from api.worker.src.agent_guide import GUIDE_VERSION
    actual = _snapshot(asyncio.run(worker.fetch(_Req(path, body, method, headers))))
    discovery = actual["headers"]
    assert discovery.pop("Link") == '<https://modelspec.dev/agents.md>; rel="describedby"'
    assert discovery.pop("x-modelspec-guide-version") == GUIDE_VERSION
    exposed = discovery.pop("access-control-expose-headers")
    added = "Link, x-modelspec-guide-version"
    assert exposed == added or exposed.endswith(", " + added)
    if exposed != added:
        discovery["access-control-expose-headers"] = exposed.removesuffix(", " + added)
    assert actual == MAIN[name]
