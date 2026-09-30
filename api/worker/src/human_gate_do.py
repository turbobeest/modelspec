"""One daily visitor per SQLite Durable Object, with no I/O during admission."""
from __future__ import annotations

import json
import time

from credits_do import DurableObject, _cell, _one_row
from human_gate import BURST_LIMIT, DAY_LIMIT, WINDOW_SECONDS


def take(state, fingerprint, now):
    day = int(now // 86400)
    if state.get("day") != day:
        state.clear()
        state.update(day=day, count=0, events=[])
    events = [row for row in state["events"] if now - row[0] < WINDOW_SECONDS]
    state["events"] = events
    remaining = max(0, DAY_LIMIT - state["count"])
    reason, retry = "", 0
    if not remaining:
        reason, retry = "day", (day + 1) * 86400 - int(now)
    elif state.get("blocked_until", 0) > now:
        reason, retry = "sweep", max(1, int(state["blocked_until"] - now) + 1)
    elif sum(now - row[0] < 60 for row in events) >= BURST_LIMIT:
        reason, retry = "burst", max(1, int(60 - (now - events[-3][0])) + 1)
    else:
        times = [row[0] for row in events[-4:]] + [now]
        gaps = [b - a for a, b in zip(times, times[1:])]
        even = len(gaps) == 4 and min(gaps) >= 1 and max(gaps) - min(gaps) <= max(0.25, sum(gaps) / 4 * 0.05)
        if even:
            reason, retry = "sweep", WINDOW_SECONDS
            state["blocked_until"] = now + WINDOW_SECONDS
    if not reason:
        state["count"] += 1
        state["events"].append([now, fingerprint])
        remaining -= 1
    return {"remaining": remaining, "reason": reason, "retry_after": retry}


class HumanGateObject(DurableObject):
    def __init__(self, ctx, env):
        super().__init__(ctx, env)
        self.ctx = ctx
        self.env = env

    async def take(self, fingerprint):
        now = time.time()
        self.ctx.storage.sql.exec("CREATE TABLE IF NOT EXISTS human_state (k TEXT PRIMARY KEY, v TEXT)")
        row = _one_row(self.ctx.storage.sql.exec("SELECT v FROM human_state WHERE k = 'state'"))
        state = json.loads(str(_cell(row, "v"))) if row is not None else {}
        result = take(state, str(fingerprint), now)
        # No await between load, admission and save: concurrent calls cannot
        # read the same count. SQLite commits these writes atomically.
        self.ctx.storage.sql.exec("INSERT OR REPLACE INTO human_state (k, v) VALUES ('state', ?)", json.dumps(state))
        await self.ctx.storage.setAlarm((int(now // 86400) + 1) * 86400 * 1000)
        return result

    async def remaining(self):
        table = _one_row(self.ctx.storage.sql.exec(
            "SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'human_state'"))
        if table is None:
            return DAY_LIMIT
        row = _one_row(self.ctx.storage.sql.exec("SELECT v FROM human_state WHERE k = 'state'"))
        state = json.loads(str(_cell(row, "v"))) if row is not None else {}
        count = state.get("count", 0) if state.get("day") == int(time.time() // 86400) else 0
        return max(0, DAY_LIMIT - count)

    async def alarm(self):
        await self.ctx.storage.deleteAll()
