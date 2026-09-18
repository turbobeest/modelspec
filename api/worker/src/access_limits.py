"""Two counters, two fixed windows, one documented boundary (MODEL-69).

**The daily window is a UTC calendar day.** It opens at 00:00:00Z and resets at
the next 00:00:00Z, so a caller's quota returns at midnight UTC wherever they
are. UTC was chosen because it is the only boundary that is the same for every
caller, needs no timezone data in the isolate, and cannot move under a caller
twice a year; the cost is that for some of the world the reset lands mid-
afternoon. The boundary is stated in every refusal as an exact `resets_at`, so
nobody has to infer it, and it is configuration-checked: a tier table asking for
another timezone is refused by `access_config` rather than metered in UTC anyway.

**The burst window is a wall-clock minute**, 00–59 seconds of the UTC minute.
Both windows are fixed, not sliding. A fixed window is cheap — one counter, one
name derived from the clock, no stored history — and it admits at most twice the
burst limit across a boundary. For a 5/minute guard over a 10/day quota that is
not worth a sliding window's storage.

Counting and limiting are separate. Every live call is counted, including the
ones no limit will ever refuse, because usage is worth knowing for a key that
pays nothing and for the key that is exempt. A tier is unlimited when its limit
is `None`, and a `None` limit is a comparison that never refuses — not a branch
that skips the meter.

A refused call is not counted. Being told "no" must not cost quota, or a
mis-looping client would never get its window back.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import UTC, datetime, timedelta
from typing import Any

from access_config import TierLimits

DAY = "daily"
MINUTE = "burst"

DAY_SECONDS = 86_400
MINUTE_SECONDS = 60

#: How long a counter outlives its window. The day counter is kept a little
#: past its reset so a late-arriving write cannot resurrect it into the next
#: day; the minute counter takes KV's 60-second floor.
_DAY_TTL = DAY_SECONDS * 2
_MINUTE_TTL = MINUTE_SECONDS


@dataclass(frozen=True)
class WindowState:
    """One window's meter, as the caller is told about it."""

    scope: str
    bucket: str
    limit: int | None
    used: int
    resets_at: datetime
    window: str
    window_seconds: int

    @property
    def remaining(self) -> int | None:
        if self.limit is None:
            return None
        return max(0, self.limit - self.used)

    @property
    def exceeded(self) -> bool:
        return self.limit is not None and self.used >= self.limit

    def retry_after(self, now: datetime) -> int:
        return max(1, int((self.resets_at - now).total_seconds()))

    def to_json(self, now: datetime) -> dict[str, Any]:
        return {
            "scope": self.scope,
            "limit": self.limit,
            "used": self.used,
            "remaining": self.remaining,
            "window": self.window,
            "window_seconds": self.window_seconds,
            "resets_at": _iso(self.resets_at),
            "retry_after_seconds": self.retry_after(now),
        }


@dataclass(frozen=True)
class MeterOutcome:
    """What the meter decided, and everything needed to explain it."""

    allowed: bool
    windows: tuple[WindowState, ...]
    refused_by: WindowState | None = None

    def window(self, scope: str) -> WindowState | None:
        return next((w for w in self.windows if w.scope == scope), None)


def _iso(moment: datetime) -> str:
    return moment.astimezone(UTC).isoformat().replace("+00:00", "Z")


def _utc(now: datetime) -> datetime:
    if now.tzinfo is None:
        raise ValueError("the clock passed to the meter must be timezone-aware")
    return now.astimezone(UTC)


def day_window(now: datetime) -> tuple[str, datetime]:
    """The UTC calendar day `now` falls in, and when it resets."""
    moment = _utc(now)
    start = moment.replace(hour=0, minute=0, second=0, microsecond=0)
    return start.strftime("%Y-%m-%d"), start + timedelta(days=1)


def minute_window(now: datetime) -> tuple[str, datetime]:
    """The UTC minute `now` falls in, and when it resets."""
    moment = _utc(now)
    start = moment.replace(second=0, microsecond=0)
    return start.strftime("%Y-%m-%dT%H:%M"), start + timedelta(minutes=1)


def counter_name(identifier: str, scope: str, bucket: str) -> str:
    """The KV name a counter lives under. Keyed by fingerprint, never by key."""
    return f"count:{identifier}:{scope}:{bucket}"


async def _read(kv: Any, name: str) -> int:
    raw = await kv.get(name)
    if raw is None:
        return 0
    try:
        return max(0, int(str(raw).strip()))
    except ValueError:
        # A corrupt counter must not hand out an unlimited quota. Treat it as
        # spent for this window; it expires on its own.
        return 1 << 30


async def consume(kv: Any, identifier: str, limits: TierLimits,
                  now: datetime) -> MeterOutcome:
    """Meter one live call for `identifier` (a key fingerprint, not a key).

    Reads both windows, refuses if either is spent, and otherwise records the
    call in both. The daily window is reported first when both are spent: it is
    the longer wait and the more useful thing to be told.
    """
    moment = _utc(now)
    day_bucket, day_reset = day_window(moment)
    minute_bucket, minute_reset = minute_window(moment)

    day_name = counter_name(identifier, DAY, day_bucket)
    minute_name = counter_name(identifier, MINUTE, minute_bucket)
    day_used = await _read(kv, day_name)
    minute_used = await _read(kv, minute_name)

    day = WindowState(
        scope=DAY, bucket=day_bucket, limit=limits.daily_limit, used=day_used,
        resets_at=day_reset, window="1 day, fixed, resetting at 00:00:00 UTC",
        window_seconds=DAY_SECONDS,
    )
    minute = WindowState(
        scope=MINUTE, bucket=minute_bucket, limit=limits.burst_limit, used=minute_used,
        resets_at=minute_reset, window="1 minute, fixed, resetting on the UTC minute",
        window_seconds=MINUTE_SECONDS,
    )

    refused = next((w for w in (day, minute) if w.exceeded), None)
    if refused is not None:
        return MeterOutcome(allowed=False, windows=(day, minute), refused_by=refused)

    await kv.put(day_name, str(day_used + 1), expiration_ttl=_DAY_TTL)
    await kv.put(minute_name, str(minute_used + 1), expiration_ttl=_MINUTE_TTL)

    return MeterOutcome(allowed=True, windows=(replace(day, used=day_used + 1),
                                               replace(minute, used=minute_used + 1)))
