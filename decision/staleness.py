"""Display staleness of a verified fact (MODEL-521). Display and reports only.

A verified fact is shown as stale when its latest verified date is older than a line:
90 days, or 45 for price and subscription facets. Until ``FIRST_QUARTER_END`` a one-time
120-day line replaces the 90-day line only (price and subscription keep 45), so the re-reads can catch up (owner decision, 2026-11-21).
Staleness is never a ranking input: nothing here is read by ``rank_score``, the floors
or the decide verdicts. ``today`` is always passed in by the caller, never read here.
"""

from __future__ import annotations

from datetime import date

STALE_DAYS = 90
STALE_DAYS_FAST = 45
#: Facet prefixes held to the 45-day line: price and subscription facets.
FAST_FACET_PREFIXES = ("offering.price", "offering.subscription")
#: The one-time line for non-price facets, active through this date inclusive; set the end date here only.
FIRST_QUARTER_DAYS = 120
FIRST_QUARTER_END = date(2027, 3, 31)
LABEL_PREFIX = "Last checked"
LABEL_SUFFIX = "may be out of date"


def is_fast_facet(facet: object) -> bool:
    return str(facet or "").startswith(FAST_FACET_PREFIXES)


def age_line(facet: object, today: date, *, fast: bool | None = None) -> int:
    """The age in days beyond which a verified fact is stale on ``today``."""
    fast = is_fast_facet(facet) if fast is None else fast
    if fast:
        return STALE_DAYS_FAST  # re-read weekly: 45 days throughout, override included
    return FIRST_QUARTER_DAYS if today <= FIRST_QUARTER_END else STALE_DAYS


def _day(value: object) -> date | None:
    if isinstance(value, date):
        return value
    try:
        return date.fromisoformat(str(value)[:10])
    except ValueError:
        return None


def is_stale(verified: object, facet: object, today: date, *, fast: bool | None = None) -> bool:
    day = _day(verified)
    return day is not None and (today - day).days > age_line(facet, today, fast=fast)


def label(verified: object) -> str:
    """The exact label text: "Last checked <date>, may be out of date"."""
    return f"{LABEL_PREFIX} {_day(verified).isoformat()}, {LABEL_SUFFIX}"
