"""Replay Playwright requests through Default.fetch with production flags.

The Cloudflare runtime, signed-data producer and external Turnstile service
use local fixtures. Access classification and SQLite admission run unchanged.
JSON input/output keeps this offline and requires no live secrets.
"""
from __future__ import annotations

import asyncio
import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "api/worker/src"))

from pipeline.worker_flags import production_vars
from tests.replay_human_gate import Namespace


class Response:
    def __init__(self, body, status=200, headers=None):
        self.body, self.status, self.headers = body, status, headers or {}


class Request:
    def __init__(self, call):
        self.url = "https://api.modelspec.dev" + call["path"]
        self.method = call["method"]
        headers = {name.lower(): value for name, value in call["headers"].items()}
        # The runtime fixture has no native response compressor.
        headers.pop("accept-encoding", None)
        # Cloudflare supplies this address. It is not a browser credential.
        headers["cf-connecting-ip"] = "203.0.113.9"
        self.headers = SimpleNamespace(get=lambda name: headers.get(name.lower()))
        self.body = call["body"]

    async def text(self):
        return self.body or ""


async def replay(data):
    async def no_fetch(*args, **kwargs):
        raise AssertionError("unexpected external request")

    js, workers = ModuleType("js"), ModuleType("workers")
    js.fetch = no_fetch
    workers.Response = Response
    workers.WorkerEntrypoint = type("WorkerEntrypoint", (), {})
    with patch.dict(sys.modules, {"js": js, "workers": workers}):
        spec = importlib.util.spec_from_file_location(
            "billing_launch_entry", ROOT / "api/worker/src/entry.py")
        entry = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(entry)

    fixtures = ROOT / "web/src/decide/__fixtures__"
    vocabulary = (fixtures / "vocabulary.json").read_bytes()
    decision = json.loads((fixtures / "live-empty-board-full.json").read_text())
    produced = 0

    async def answer(self, payload, origin, expected=None, transport=None):
        nonlocal produced
        produced += 1
        return 200, decision

    used_tokens = set()

    async def verify(secret, token):
        success = token == "browser-test-token" and token not in used_tokens
        used_tokens.add(token)
        return {"success": success, "hostname": "modelspec.dev", "action": "decide"}

    variables = production_vars(ROOT)
    if "enforced" in data:
        variables["ACCESS_ENFORCED"] = str(data["enforced"]).lower()
    environment = SimpleNamespace(
        **{**variables, "HUMAN_GATE_ENABLED": str(data["human_gate"]).lower()},
        TIER_POLICY=(ROOT / "api/worker/tiers.json").read_text(),
        VISITOR_HMAC_KEY="fixture-visitor-key-0123456789",
        TURNSTILE_SECRET="fixture-secret", HUMAN_GATE=Namespace(),
    )
    worker = entry.Default()
    worker.env = environment
    outcomes = []
    with patch.object(entry.Default, "_decide", answer), \
         patch.object(entry, "_verify_turnstile", verify), \
         patch.object(entry, "_bundled_read", return_value=(True, vocabulary)):
        for index, call in enumerate(data["calls"]):
            # Deterministic arrival times; each trace preserves the same object.
            with patch("human_gate_do.time.time", return_value=10000 + index * .2):
                response = await worker.fetch(Request(call))
            outcomes.append({"status": response.status, "body": response.body,
                             "headers": response.headers, "produced": produced})
    return outcomes


if __name__ == "__main__":
    print(json.dumps(asyncio.run(replay(json.load(sys.stdin)))))
