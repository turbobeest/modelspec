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
from datetime import UTC, datetime
from pathlib import Path
from types import ModuleType, SimpleNamespace
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "api/worker/src"))
sys.path.insert(0, str(ROOT))

from pipeline.worker_flags import production_vars
from tests.replay_human_gate import Namespace

NOW = datetime(2026, 10, 4, 12, tzinfo=UTC).timestamp()


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

    fixtures = ROOT / "web/src/decide/__fixtures__"
    vocabulary = (fixtures / "live-vocabulary.json").read_bytes()
    js, workers, bundle = ModuleType("js"), ModuleType("workers"), ModuleType("bundled_data")
    js.fetch = no_fetch
    workers.Response = Response
    workers.WorkerEntrypoint = type("WorkerEntrypoint", (), {})
    bundle.read = lambda path: vocabulary if path == "/api/decision/vocabulary.json" else None
    with patch.dict(sys.modules, {"js": js, "workers": workers, "bundled_data": bundle}):
        spec = importlib.util.spec_from_file_location(
            "billing_launch_entry", ROOT / "api/worker/src/entry.py")
        entry = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(entry)

    def request_key(payload):
        return json.dumps({key: value for key, value in payload.items() if key != "snapshot"}, sort_keys=True)

    captures = json.loads((fixtures / "live-decision-requests.json").read_text())
    decisions = {request_key(row["spec"]): json.loads((fixtures / row["file"]).read_text())
                 for row in captures}
    fallback = {explain: json.loads((fixtures / f"live-empty-board-{explain}.json").read_text())
                for explain in ("summary", "full")}
    produced = 0

    async def answer(self, payload, origin, expected=None, transport=None):
        nonlocal produced
        produced += 1
        return 200, decisions.get(request_key(payload), fallback["summary" if payload.get("explain") == "summary" else "full"])

    async def rank(self, payload, service_commit, origin):
        nonlocal produced
        produced += 1
        return 200, {"result": []}

    async def compare(self, payload, origin, expected=None):
        nonlocal produced
        produced += 1
        return 200, {"results": []}

    async def policy_answer(self, payload, service_commit, origin, entitlement):
        nonlocal produced
        produced += 1
        return 200, {"result": []}

    async def export(origin, **kwargs):
        return {"build": {"commit": "offline-fixture", "built_at": "2026-10-04T12:00:00Z",
                          "export_schema_version": "2.0"}, "candidates": []}, None

    async def catalogue(origin):
        return {"models": []}

    used_tokens = set()

    async def verify(secret, token):
        success = token.startswith("browser-test-token-") and token not in used_tokens
        used_tokens.add(token)
        return {"success": success, "hostname": "modelspec.dev", "action": "decide"}

    variables = production_vars(ROOT)
    for name, flag in (("ACCESS_ENFORCED", "enforced"), ("VISIT_GATE_ENABLED", "visit_gate"),
                       ("HUMAN_GATE_ENABLED", "human_gate")):
        if flag in data:
            variables[name] = str(data[flag]).lower()
    environment = SimpleNamespace(
        **variables,
        TIER_POLICY=(ROOT / "api/worker/tiers.json").read_text(),
        VISITOR_HMAC_KEY="fixture-visitor-key-0123456789",
        VISIT_TOKEN_HMAC_KEY="fixture-visit-signing-secret-0123456789",
        TURNSTILE_SECRET="fixture-secret",
    )
    environment.HUMAN_GATE = Namespace(environment)
    worker = entry.Default()
    worker.env = environment
    outcomes = []
    with patch.object(entry.Default, "_decide", answer), \
         patch.object(entry.Default, "_rank", rank), \
         patch.object(entry.Default, "_compare", compare), \
         patch.object(entry.Default, "_policy_answer", policy_answer), \
         patch.object(entry, "_verify_turnstile", verify), \
         patch.object(entry, "_load_export", export), \
         patch.object(entry, "_load_policy_catalogue", catalogue):
        for index, call in enumerate(data["calls"]):
            # Deterministic arrival times; each trace preserves the same object.
            moment = call.get("now", NOW + index)

            class Clock(datetime):
                @classmethod
                def now(cls, tz=None):
                    return datetime.fromtimestamp(moment, UTC)

            with patch("human_gate_do.time.time", return_value=moment), patch("visitor.datetime", Clock):
                response = await worker.fetch(Request(call))
            outcomes.append({"status": response.status, "body": response.body,
                             "headers": response.headers, "produced": produced,
                             "visit_objects": len(environment.HUMAN_GATE.objects)})
    return outcomes


if __name__ == "__main__":
    if "--serve" in sys.argv:
        for line in sys.stdin:
            print(json.dumps(asyncio.run(replay(json.loads(line)))), flush=True)
    else:
        print(json.dumps(asyncio.run(replay(json.load(sys.stdin)))))
