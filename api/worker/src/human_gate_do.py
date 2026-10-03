"""One daily visitor per SQLite Durable Object, with no I/O during admission."""
from __future__ import annotations

import json
import time

from credits_do import DurableObject, _cell, _one_row
from human_gate import (BURST_LIMIT, DAY_LIMIT, WINDOW_SECONDS, INTENT_REQUEST_LIMIT,
                        INTENT_WINDOW_SECONDS, CONTINUATION_BURST_LIMIT, CONTINUATION_BURST_SECONDS)
from human_question import derivation, fingerprint, digest
import visit_token


def continue_intent(state, now, intent, question=None, day_limit=DAY_LIMIT, burst_limit=BURST_LIMIT):
    if state.get("day") != int(now // 86400):
        return None
    admission = state.get("intents", {}).get(intent)
    if admission is None:
        return None
    remaining = max(0, day_limit - state["count"])
    refused = {"remaining": remaining, "reason": "intent", "retry_after": 1}
    if admission.get("question") is None or question is None:
        return refused
    kind = derivation(admission["question"], question)
    # The first estate/plot variant fixes that auxiliary for the whole action.
    variant = digest({key: question[key] for key in ("optimize", "capabilities", "estate")})
    if kind is None or (kind in ("estate", "plot") and admission.get(kind, variant) != variant):
        # The visitor already verified this ID. A new question spends another
        # admission atomically, replacing the primary only when admitted.
        return take_primary(state, now, intent, question, day_limit, burst_limit)
    if now - admission["first"] >= INTENT_WINDOW_SECONDS or admission["requests"] >= INTENT_REQUEST_LIMIT:
        return {"remaining": remaining, "reason": "intent",
                "retry_after": max(1, (int(now // 86400) + 1) * 86400 - int(now))}
    events = [stamp for stamp in admission.get("events", [admission["first"]])
              if now - stamp < CONTINUATION_BURST_SECONDS]
    if len(events) >= CONTINUATION_BURST_LIMIT:
        return refused
    if kind in ("estate", "plot"):
        admission[kind] = variant
    admission["events"] = [*events, now]
    admission["requests"] += 1
    return {"remaining": remaining, "reason": "", "retry_after": 0}


def take(state, now, intent=None, question=None, day_limit=DAY_LIMIT, burst_limit=BURST_LIMIT):
    day = int(now // 86400)
    if state.get("day") != day:
        state.clear()
        state.update(day=day, count=0, events=[])
    if intent:
        continued = continue_intent(state, now, intent, question, day_limit, burst_limit)
        if continued is not None:
            return continued
    return take_primary(state, now, intent, question, day_limit, burst_limit)


def take_primary(state, now, intent, question, day_limit=DAY_LIMIT, burst_limit=BURST_LIMIT):
    """Meter a new question, including one sent under an already verified ID."""
    day = int(now // 86400)
    # Deployed objects may still contain [timestamp, fingerprint] pairs.
    times = [row[0] if isinstance(row, list) else row for row in state["events"]]
    events = [stamp for stamp in times if now - stamp < WINDOW_SECONDS]
    state["events"] = events
    remaining = max(0, day_limit - state["count"])
    reason, retry = "", 0
    if not remaining:
        reason, retry = "day", (day + 1) * 86400 - int(now)
    elif state.get("blocked_until", 0) > now:
        reason, retry = "sweep", max(1, int(state["blocked_until"] - now) + 1)
    elif sum(now - stamp < 60 for stamp in events) >= burst_limit:
        reason, retry = "burst", max(1, int(60 - (now - events[-burst_limit])) + 1)
    else:
        times = events[-4:] + [now]
        gaps = [b - a for a, b in zip(times, times[1:])]
        even = len(gaps) == 4 and min(gaps) >= 1 and max(gaps) - min(gaps) <= max(0.25, sum(gaps) / 4 * 0.05)
        if even:
            reason, retry = "sweep", WINDOW_SECONDS
            state["blocked_until"] = now + WINDOW_SECONDS
    if not reason:
        state["count"] += 1
        state["events"].append(now)
        remaining -= 1
        if intent:
            state.setdefault("intents", {})[intent] = {
                "first": now, "requests": 1, "question": question, "events": [now]}
    return {"remaining": remaining, "reason": reason, "retry_after": retry}


class HumanGateObject(DurableObject):
    def __init__(self, ctx, env):
        super().__init__(ctx, env)
        self.ctx = ctx
        self.env = env

    async def take(self, intent=None, spec=None):
        return await self._admit(intent, False, spec)

    async def continue_intent(self, intent, spec=None):
        return await self._admit(intent, True, spec)

    async def take_visit(self, intent=None, spec=None):
        return await self._admit(intent, False, spec, visit=True)

    async def _admit(self, intent, admitted_only, spec, visit=False):
        day_limit, burst_limit = visit_token.limits(self.env, "decide") if visit else (DAY_LIMIT, BURST_LIMIT)
        key = "visit" if visit else "state"
        now = time.time()
        self.ctx.storage.sql.exec("CREATE TABLE IF NOT EXISTS human_state (k TEXT PRIMARY KEY, v TEXT)")
        row = _one_row(self.ctx.storage.sql.exec("SELECT v FROM human_state WHERE k = ?", key))
        state = json.loads(str(_cell(row, "v"))) if row is not None else {}
        question = fingerprint(spec) if intent else None
        result = continue_intent(state, now, intent, question, day_limit, burst_limit) if admitted_only else take(state, now, intent, question, day_limit, burst_limit)
        if result is None:
            return None
        # No await between load, admission and save: concurrent calls cannot
        # read the same count. SQLite commits these writes atomically.
        self.ctx.storage.sql.exec("INSERT OR REPLACE INTO human_state (k, v) VALUES (?, ?)", key, json.dumps(state))
        await self.ctx.storage.setAlarm((int(now // 86400) + 1) * 86400 * 1000)
        return result

    async def remaining(self, visit=False):
        day_limit = visit_token.limits(self.env, "decide")[0] if visit else DAY_LIMIT
        key = "visit" if visit else "state"
        table = _one_row(self.ctx.storage.sql.exec(
            "SELECT name FROM sqlite_master WHERE type = 'table' AND name = 'human_state'"))
        if table is None:
            return day_limit
        row = _one_row(self.ctx.storage.sql.exec("SELECT v FROM human_state WHERE k = ?", key))
        state = json.loads(str(_cell(row, "v"))) if row is not None else {}
        count = state.get("count", 0) if state.get("day") == int(time.time() // 86400) else 0
        return max(0, day_limit - count)

    async def alarm(self):
        await self.ctx.storage.deleteAll()

    async def take_visit_vocabulary(self):
        return await self.take_vocabulary(visit=True)

    async def take_vocabulary(self, visit=False):
        """A separate display budget in the same visitor object."""
        day_limit, burst_limit = visit_token.limits(self.env, "vocabulary") if visit else (60, 10)
        key = "visit_vocabulary" if visit else "vocabulary"
        now = time.time()
        self.ctx.storage.sql.exec("CREATE TABLE IF NOT EXISTS human_state (k TEXT PRIMARY KEY, v TEXT)")
        row = _one_row(self.ctx.storage.sql.exec("SELECT v FROM human_state WHERE k = ?", key))
        state = json.loads(str(_cell(row, "v"))) if row is not None else {}
        day = int(now // 86400)
        if state.get("day") != day:
            state = {"day": day, "count": 0, "events": []}
        events = [stamp for stamp in state["events"] if now - stamp < 60]
        reason = "day" if state["count"] >= day_limit else "burst" if len(events) >= burst_limit else ""
        retry = ((day + 1) * 86400 - int(now)) if reason == "day" else max(1, int(60 - (now - events[0])) + 1) if reason else 0
        if not reason:
            state["count"] += 1
            events.append(now)
        state["events"] = events
        self.ctx.storage.sql.exec("INSERT OR REPLACE INTO human_state (k, v) VALUES (?, ?)", key, json.dumps(state))
        await self.ctx.storage.setAlarm((day + 1) * 86400 * 1000)
        return {"remaining": max(0, day_limit - state["count"]), "reason": reason, "retry_after": retry}
