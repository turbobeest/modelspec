"""Which workflows run on a schedule, and how often (MODEL-421).

The ``workflow-health`` target watches every workflow with a ``schedule:``
trigger. It reads the list and each cadence from the workflow files, so a new
scheduled job is watched the day it lands, with no list to keep by hand.

A workflow's cadence is the longest gap between two consecutive firings of all
its cron lines together: ``17 6 * * 1`` is 168 hours, ``41 */6 * * *`` is 6.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path

import yaml

_NAMES = {
    "month": ["JAN", "FEB", "MAR", "APR", "MAY", "JUN",
              "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"],
    "dow": ["SUN", "MON", "TUE", "WED", "THU", "FRI", "SAT"],
}
_RANGES = {"minute": (0, 59), "hour": (0, 23), "dom": (1, 31), "month": (1, 12),
           "dow": (0, 7)}
# Two years from a fixed day, so every weekday falls on every day of the
# month and a leap day is included. The answer does not depend on today.
_WINDOW_START = date(2027, 1, 1)
_WINDOW_DAYS = 731


class CronError(ValueError):
    """A cron line this parser cannot read."""


def _value(token: str, field: str) -> int:
    names = _NAMES.get(field)
    if names and token.upper() in names:
        return names.index(token.upper()) + (1 if field == "month" else 0)
    if not token.isdigit():
        raise CronError(f"{field} value {token!r} is not a number")
    return int(token)


def _field(text: str, field: str) -> frozenset[int]:
    low, high = _RANGES[field]
    out: set[int] = set()
    for part in text.split(","):
        body, _, step_text = part.partition("/")
        step = int(step_text) if step_text else 1
        if step_text and (not step_text.isdigit() or step == 0):
            raise CronError(f"{field} step {step_text!r} is not a positive number")
        if body == "*":
            start, end = low, high
        elif "-" in body:
            a, b = body.split("-", 1)
            start, end = _value(a, field), _value(b, field)
        else:
            start = _value(body, field)
            end = high if step_text else start
        if not (low <= start <= high and low <= end <= high) or start > end:
            raise CronError(f"{field} {part!r} is outside {low}-{high}")
        out.update(range(start, end + 1, step))
    if field == "dow" and 7 in out:
        out = (out - {7}) | {0}
    return frozenset(out)


@dataclass(frozen=True)
class Cron:
    """One POSIX cron line, as GitHub Actions reads it (UTC)."""

    minutes: frozenset[int]
    hours: frozenset[int]
    days: frozenset[int]
    months: frozenset[int]
    weekdays: frozenset[int]
    any_day: bool
    any_weekday: bool

    @classmethod
    def parse(cls, line: str) -> Cron:
        parts = line.split()
        if len(parts) != 5:
            raise CronError(f"{line!r} does not have five fields")
        minute, hour, dom, month, dow = parts
        return cls(_field(minute, "minute"), _field(hour, "hour"), _field(dom, "dom"),
                   _field(month, "month"), _field(dow, "dow"),
                   any_day=dom.startswith("*"), any_weekday=dow.startswith("*"))

    def runs_on(self, day: date) -> bool:
        if day.month not in self.months:
            return False
        on_day = day.day in self.days
        on_weekday = day.isoweekday() % 7 in self.weekdays
        # POSIX: with both day fields restricted, either one matching is enough.
        if self.any_day or self.any_weekday:
            return on_day and on_weekday
        return on_day or on_weekday

    def firings(self, start: date, days: int) -> Iterable[datetime]:
        for offset in range(days):
            day = start + timedelta(days=offset)
            if self.runs_on(day):
                for hour in sorted(self.hours):
                    for minute in sorted(self.minutes):
                        yield datetime(day.year, day.month, day.day, hour, minute)


def cadence_hours(crons: Sequence[str]) -> float:
    """The longest gap, in hours, between consecutive firings of these cron lines."""
    parsed = [Cron.parse(line) for line in crons]
    times = sorted({t for c in parsed for t in c.firings(_WINDOW_START, _WINDOW_DAYS)})
    if len(times) < 2:
        raise CronError(f"{list(crons)} fires fewer than twice in two years")
    gap = max(b - a for a, b in zip(times, times[1:], strict=False))
    return gap.total_seconds() / 3600


def schedule_of(text: str) -> list[str]:
    """The cron lines of one workflow file; empty when it has no schedule."""
    data = yaml.safe_load(text) or {}
    # PyYAML reads a bare `on:` key as the boolean True.
    triggers = data.get("on", data.get(True)) if isinstance(data, dict) else None
    if not isinstance(triggers, dict):
        return []
    return [str(entry["cron"]) for entry in triggers.get("schedule") or ()
            if isinstance(entry, dict) and entry.get("cron")]


@dataclass(frozen=True)
class Scheduled:
    file: str
    crons: tuple[str, ...]
    cadence_hours: float


def scheduled_in(files: Mapping[str, str]) -> tuple[list[Scheduled], list[str]]:
    """Every workflow file (name -> text) with a schedule, and what could not be read."""
    found, errors = [], []
    for name in sorted(files):
        try:
            crons = schedule_of(files[name])
            if crons:
                found.append(Scheduled(name, tuple(crons), cadence_hours(crons)))
        except CronError as exc:
            errors.append(f"{name}: schedule could not be read: {exc}")
        except yaml.YAMLError:
            errors.append(f"{name}: schedule could not be read")
    return found, errors


def workflow_files(workflow_dir: Path) -> dict[str, str]:
    return {path.name: path.read_text(encoding="utf-8")
            for path in [*workflow_dir.glob("*.yml"), *workflow_dir.glob("*.yaml")]}


def scheduled_workflows(workflow_dir: Path) -> tuple[list[Scheduled], list[str]]:
    """Every workflow in ``workflow_dir`` with a schedule, and what could not be read."""
    return scheduled_in(workflow_files(workflow_dir))
