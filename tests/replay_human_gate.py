"""Replay a browser request trace through the real SQLite gate for Vitest.

Only external Turnstile validation is replaced, as in test_human_gate.py.
Run from the repository root, with a JSON trace on stdin.
"""
import asyncio
import json
import sqlite3
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "api/worker/src"))
import human_gate
import human_gate_do


class Storage:
    def __init__(self):
        self.db = sqlite3.connect(":memory:")
        self.db.row_factory = sqlite3.Row
        self.sql = self

    def exec(self, query, *params):
        rows = [dict(row) for row in self.db.execute(query, params).fetchall()]
        return SimpleNamespace(toArray=lambda: rows)

    async def setAlarm(self, at):
        pass


class Namespace:
    def __init__(self):
        self.objects = {}

    def idFromName(self, name):
        return name

    def get(self, name):
        if name not in self.objects:
            self.objects[name] = human_gate_do.HumanGateObject(SimpleNamespace(storage=Storage()), None)
        return self.objects[name]


async def verified(secret, token):
    return {"success": True, "hostname": "modelspec.dev", "action": "decide"}


async def replay(trace):
    environment = SimpleNamespace(HUMAN_GATE=Namespace(), TURNSTILE_SECRET="fixture-secret",
                                  VISITOR_HMAC_KEY="fixture-visitor-key-0123456789")
    outcomes = []
    for call in trace:
        headers = {"origin": "https://modelspec.dev", "cf-connecting-ip": "203.0.113.9",
                   human_gate.INTENT_HEADER: call["intent"], human_gate.TOKEN_HEADER: call["token"]}
        request = SimpleNamespace(headers=SimpleNamespace(get=lambda name: headers.get(name.lower())))
        with patch.object(human_gate_do.time, "time", return_value=call["now"]):
            outcomes.append(await human_gate.admit(request, environment, {"https://modelspec.dev"},
                                                   verified, call["spec"]))
    return outcomes


if __name__ == "__main__":
    print(json.dumps(asyncio.run(replay(json.load(sys.stdin)))))
