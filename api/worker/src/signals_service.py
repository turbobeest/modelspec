"""Authenticated release-signal storage for the Cloudflare Worker (MODEL-113).

Two intakes feed one pending queue. `intake` takes Grok Bot's HMAC-signed
`release-signal` v1. `discovered` takes the primary-source watcher's
`release-discovery` v1 (MODEL-216) under the repository read key. Processing,
acknowledgement and re-checks do not care which intake a row came through.
"""

from __future__ import annotations

import hmac
import json
import re
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from typing import Any
from urllib.parse import urlsplit

from release_signals.contract import SIGNAL_ID, WATCH_PREFIX, ReleaseSignal, SignalError

SCHEMA_VERSION = "1"
#: The pending queue's own version. 2 since MODEL-216: a queued row can now be a
#: `release-discovery` v1, whose `first_seen_url` is not on X. That widens the
#: rows' range, so under MODEL-59 the queue took a major. Its only consumer is
#: this repository's `release-signals.yml`.
PENDING_SCHEMA_VERSION = "2"
PENDING_PREFIX = "release-signals/v1/pending/"
SEEN_PREFIX = "release-signals/v1/seen/"
#: One permanent key per discovery the watcher ever filed. The watcher re-posts
#: every uncatalogued discovery on every run; this is what makes that a no-op
#: after the first, including once the pending row is acknowledged and gone.
DISCOVERED_PREFIX = "release-signals/v1/discovered/"
AUDIT_PREFIX = "release-signals/v1/audit/"
RECHECK_PREFIX = "release-signals/v1/recheck/"
#: One permanent marker per completed re-check row, `<due>/<signal_id>` (MODEL-475).
#: Written before the row is deleted. It makes a retried acknowledgement a no-op
#: success, and it lets a concurrent relink undo a put that landed on a deleted row.
RECHECK_DONE_PREFIX = "release-signals/v1/recheck-done/"
#: A done marker outlives the signal's last re-check by 45 days: 75 days from the
#: first acknowledgement, so KV does not grow without limit (MODEL-475).
RECHECK_DONE_KEEP_AFTER_LAST = timedelta(days=45)
MAX_AGE = timedelta(hours=24)
MAX_FUTURE_SKEW = timedelta(minutes=5)
MAX_BODY_BYTES = 4096
ACKNOWLEDGEMENT_FIELDS = frozenset({
    "signal_id", "result", "pr_url", "recheck_due", "recheck_day",
})
RFC3339_FULL_DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
#: A GitHub pull request, the only URL a later run may move a re-check onto (MODEL-475).
PULL_REQUEST_URL = re.compile(
    r"^https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+/pull/[1-9][0-9]*$"
)
RECHECK_DAYS = (1, 7, 30)


@dataclass(frozen=True)
class Outcome:
    status: int
    body: dict[str, Any]


def enabled(value: object) -> bool:
    return str(value or "").strip().casefold() not in {"", "0", "false", "no", "off"}


def _error(status: int, code: str, message: str) -> Outcome:
    return Outcome(status, {
        "schema_version": SCHEMA_VERSION,
        "endpoint": "signals",
        "error": {"code": code, "message": message},
    })


def _authorised(authorization: str | None, read_key: str | None) -> bool:
    if not read_key or not authorization:
        return False
    scheme, separator, value = authorization.partition(" ")
    return (
        separator == " "
        and scheme.casefold() == "bearer"
        and value.isascii()
        and read_key.isascii()
        and hmac.compare_digest(value.strip(), read_key)
    )


def _valid_uri(value: object) -> bool:
    if (
        not isinstance(value, str)
        or not value
        or any(character.isspace() for character in value)
    ):
        return False
    try:
        parsed = urlsplit(value)
    except ValueError:
        return False
    return bool(parsed.scheme and (parsed.netloc or parsed.path))


def _acknowledgement_error(payload: object) -> str | None:
    if not isinstance(payload, dict):
        return "the body must be a JSON object"
    unknown = set(payload) - ACKNOWLEDGEMENT_FIELDS
    missing = {"signal_id", "result"} - set(payload)
    if unknown or missing:
        detail = []
        if missing:
            detail.append(f"missing {sorted(missing)}")
        if unknown:
            detail.append(f"unknown {sorted(unknown)}")
        return "; ".join(detail)
    signal_id = payload["signal_id"]
    if not isinstance(signal_id, str) or SIGNAL_ID.fullmatch(signal_id) is None:
        return "signal_id contains unsupported characters"
    if payload["result"] is not None and not isinstance(payload["result"], str):
        return "result must be a string or null"
    pr_url = payload.get("pr_url")
    if pr_url is not None and not _valid_uri(pr_url):
        return "pr_url must be a URI or null"
    if "recheck_due" in payload:
        recheck_due = payload["recheck_due"]
        if not isinstance(recheck_due, str) or RFC3339_FULL_DATE.fullmatch(recheck_due) is None:
            return "recheck_due must be an RFC 3339 full-date"
        try:
            date.fromisoformat(recheck_due)
        except ValueError:
            return "recheck_due must be an RFC 3339 full-date"
    if "recheck_day" in payload:
        recheck_day = payload["recheck_day"]
        if (
            isinstance(recheck_day, bool)
            or not isinstance(recheck_day, int)
            or recheck_day not in (1, 7, 30)
        ):
            return "recheck_day must be 1, 7, or 30"
    return None


async def intake(
    *,
    raw: bytes,
    signature: str | None,
    secret: bytes,
    enabled: bool,
    kv: Any,
    now: datetime | None = None,
) -> Outcome:
    if not enabled:
        return _error(404, "not_found", "release-signal intake is disabled")
    if kv is None:
        return _error(503, "store_unavailable", "the release-signal store is not bound")
    if not secret:
        return _error(503, "secret_unavailable", "the release-signal secret is not configured")
    if len(raw) > MAX_BODY_BYTES:
        return _error(413, "payload_too_large", f"the body must be at most {MAX_BODY_BYTES} bytes")
    try:
        signal = ReleaseSignal.from_signed_body(raw, signature, secret)
    except SignalError as exc:
        return _error(401 if "signature" in str(exc) else 400, "invalid_signal", str(exc))
    observed = (now or datetime.now(UTC)).astimezone(UTC)
    if observed - signal.instant > MAX_AGE or signal.instant - observed > MAX_FUTURE_SKEW:
        return _error(400, "stale_signal", "timestamp is outside the accepted intake window")

    key = PENDING_PREFIX + signal.signal_id
    marker = SEEN_PREFIX + signal.signal_id
    serialised = json.dumps(signal.to_dict(), separators=(",", ":"), sort_keys=True)
    existing = await kv.get(marker)
    if existing is None:
        existing = await kv.get(key)
    if existing is not None:
        if str(existing) != serialised:
            return _error(409, "signal_id_conflict", "signal_id already names another payload")
        return Outcome(200, {
            "schema_version": SCHEMA_VERSION,
            "endpoint": "signals",
            "status": "duplicate",
            "signal_id": signal.signal_id,
        })
    await kv.put(key, serialised)
    await kv.put(marker, serialised)
    return Outcome(202, {
        "schema_version": SCHEMA_VERSION,
        "endpoint": "signals",
        "status": "accepted",
        "signal_id": signal.signal_id,
    })


async def discovered(
    *,
    raw: bytes,
    authorization: str | None,
    read_key: str | None,
    kv: Any,
    now: datetime | None = None,
) -> Outcome:
    """Queue one watcher discovery, once, as the same pending work Grok Bot's are."""
    if not _authorised(authorization, read_key):
        return _error(401, "unauthorised", "a valid signals read key is required")
    if kv is None:
        return _error(503, "store_unavailable", "the release-signal store is not bound")
    if len(raw) > MAX_BODY_BYTES:
        return _error(413, "payload_too_large", f"the body must be at most {MAX_BODY_BYTES} bytes")
    try:
        payload = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError, RecursionError) as exc:
        return _error(400, "invalid_signal", f"the body is not valid JSON: {exc}")
    try:
        signal = ReleaseSignal.parse(payload, discovered=True)
    except SignalError as exc:
        return _error(400, "invalid_signal", str(exc))
    observed = (now or datetime.now(UTC)).astimezone(UTC)
    if observed - signal.instant > MAX_AGE or signal.instant - observed > MAX_FUTURE_SKEW:
        return _error(400, "stale_signal", "timestamp is outside the accepted intake window")

    marker = DISCOVERED_PREFIX + signal.signal_id
    if await kv.get(marker) is not None:
        return Outcome(200, {
            "schema_version": SCHEMA_VERSION,
            "endpoint": "signals.discovered",
            "status": "duplicate",
            "signal_id": signal.signal_id,
        })
    await kv.put(
        PENDING_PREFIX + signal.signal_id,
        json.dumps(signal.to_dict(), separators=(",", ":"), sort_keys=True),
    )
    await kv.put(marker, signal.timestamp)
    return Outcome(202, {
        "schema_version": SCHEMA_VERSION,
        "endpoint": "signals.discovered",
        "status": "accepted",
        "signal_id": signal.signal_id,
    })


async def _keys(kv: Any, prefix: str) -> list[str]:
    names = []
    options = {"prefix": prefix}
    seen_cursors: set[str] = set()
    while True:
        listed = await kv.list(options)
        rows = listed.get("keys", []) if isinstance(listed, dict) else getattr(
            listed, "keys", []
        )
        for row in rows:
            name = row.get("name") if isinstance(row, dict) else getattr(row, "name", None)
            if name:
                names.append(str(name))
        complete = listed.get("list_complete", True) if isinstance(
            listed, dict
        ) else getattr(listed, "list_complete", True)
        if complete:
            break
        cursor_value = listed.get("cursor") if isinstance(listed, dict) else getattr(
            listed, "cursor", None
        )
        cursor = str(cursor_value or "")
        if not cursor or cursor in seen_cursors:
            raise RuntimeError("Workers KV returned an incomplete page without a new cursor")
        seen_cursors.add(cursor)
        options = {"prefix": prefix, "cursor": cursor}
    return sorted(names)


async def pending(
    *, authorization: str | None, read_key: str | None, kv: Any, today: date
) -> Outcome:
    if not _authorised(authorization, read_key):
        return _error(401, "unauthorised", "a valid signals read key is required")
    if kv is None:
        return _error(503, "store_unavailable", "the release-signal store is not bound")
    signals = []
    for key in await _keys(kv, PENDING_PREFIX):
        raw = await kv.get(key)
        if raw:
            signals.append(json.loads(str(raw)))
    rechecks = []
    for key in await _keys(kv, RECHECK_PREFIX):
        parts = key.removeprefix(RECHECK_PREFIX).split("/", 1)
        if len(parts) != 2 or parts[0] > today.isoformat():
            continue
        raw = await kv.get(key)
        if raw:
            rechecks.append(json.loads(str(raw)))
    return Outcome(200, {
        "schema_version": PENDING_SCHEMA_VERSION,
        "endpoint": "signals.pending",
        "signals": sorted(signals, key=lambda row: (row["timestamp"], row["signal_id"])),
        "rechecks": rechecks,
    })


def _done_marker_ttl(row: dict[str, Any], recheck_due: str, today: date) -> int:
    """Seconds until 45 days after the signal's day-30 re-check, never less than 45 days."""
    day, due = row.get("day"), row.get("due") or recheck_due
    try:
        first = date.fromisoformat(str(due)) - timedelta(
            days=day if not isinstance(day, bool) and day in RECHECK_DAYS else 0
        )
    except ValueError:
        first = today
    expires = first + timedelta(days=RECHECK_DAYS[-1]) + RECHECK_DONE_KEEP_AFTER_LAST
    return int(max(expires - today, RECHECK_DONE_KEEP_AFTER_LAST).total_seconds())


async def _relink_rechecks(
    kv: Any, signal_id: str, pr_url: object, *, acknowledged_key: str,
) -> None:
    """Point a signal's remaining re-checks at the pull request a re-check reported.

    The first acknowledgement can carry an identity-review issue or no URL. A
    re-check that later opens a card pull request must move the other re-checks
    onto it, or the workflow finds no open pull request there and drafts the
    same model again (MODEL-475). A report without a pull request keeps what is
    stored.

    Every re-check row of the signal is found by listing, so a second schedule
    left by a retried partial first acknowledgement (another base date) is
    relinked too. Only `pr_url` changes. KV has no transactions, so each write
    is conditional: the row is re-read just before the put and skipped if it is
    gone or no longer the row that was read, and a put that raced the row's own
    completion is undone once its done marker is seen.
    """
    if not isinstance(pr_url, str) or PULL_REQUEST_URL.fullmatch(pr_url) is None:
        return
    # The acknowledged row first: if a later write fails, the row is still due and
    # its retry already carries the pull request, so it updates it, never re-drafts.
    listed = [key for key in await _keys(kv, RECHECK_PREFIX) if key != acknowledged_key]
    for key in [acknowledged_key, *listed]:
        due, separator, owner = key.removeprefix(RECHECK_PREFIX).partition("/")
        if not separator or owner != signal_id:
            continue
        raw = await kv.get(key)
        if not raw:
            continue
        row = json.loads(str(raw))
        if (
            row.get("signal_id") != signal_id
            or row.get("due") != due
            or isinstance(row.get("day"), bool)
            or row.get("day") not in RECHECK_DAYS
            or row.get("pr_url") == pr_url
        ):
            continue
        done = RECHECK_DONE_PREFIX + key.removeprefix(RECHECK_PREFIX)
        if await kv.get(done) is not None or await kv.get(key) != raw:
            continue
        row["pr_url"] = pr_url
        await kv.put(key, json.dumps(row, separators=(",", ":")))
        if await kv.get(done) is not None:
            # The row was completed between the re-read and the put: never resurrect it.
            await kv.delete(key)


async def acknowledge(
    *, authorization: str | None, read_key: str | None, kv: Any,
    payload: dict[str, Any], today: date,
) -> Outcome:
    if not _authorised(authorization, read_key):
        return _error(401, "unauthorised", "a valid signals read key is required")
    invalid = _acknowledgement_error(payload)
    if invalid is not None:
        return _error(400, "invalid_request", invalid)
    if kv is None:
        return _error(503, "store_unavailable", "the release-signal store is not bound")
    signal_id = payload["signal_id"]
    recheck_due = payload.get("recheck_due") or ""
    recheck_day = payload.get("recheck_day")
    pending_key = PENDING_PREFIX + signal_id
    source = await kv.get(pending_key)
    recheck_key = f"{RECHECK_PREFIX}{recheck_due}/{signal_id}" if recheck_due else ""
    recheck = await kv.get(recheck_key) if source is None and recheck_key else None
    if source is None and recheck is not None:
        source = json.dumps(json.loads(str(recheck))["signal"])
    if source is None and recheck_key and await kv.get(
        RECHECK_DONE_PREFIX + recheck_key.removeprefix(RECHECK_PREFIX)
    ) is not None:
        # A retry of a completed re-check: finish any relink it left, change nothing else.
        await _relink_rechecks(kv, signal_id, payload.get("pr_url"), acknowledged_key=recheck_key)
        return Outcome(200, {
            "schema_version": SCHEMA_VERSION,
            "endpoint": "signals.ack",
            "status": "acknowledged",
            "signal_id": signal_id,
            "recheck_days": [],
        })
    if not signal_id or source is None:
        return _error(404, "signal_not_found", "the pending signal does not exist")
    audit = {
        "signal": json.loads(str(source)),
        "processed_at": today.isoformat(),
        "result": payload.get("result"),
        "pr_url": payload.get("pr_url"),
    }
    audit_key = f"{AUDIT_PREFIX}{signal_id}/{today.isoformat()}/{recheck_day or 'initial'}"
    if recheck is None and not signal_id.startswith(WATCH_PREFIX):
        await kv.put(
            SEEN_PREFIX + signal_id,
            json.dumps(audit["signal"], separators=(",", ":"), sort_keys=True),
        )
    await kv.put(audit_key, json.dumps(audit, separators=(",", ":")))
    if recheck is None:
        for days in RECHECK_DAYS:
            due = (today + timedelta(days=days)).isoformat()
            row = {
                "signal_id": signal_id,
                "due": due,
                "day": days,
                "pr_url": payload.get("pr_url"),
                "signal": audit["signal"],
            }
            await kv.put(
                f"{RECHECK_PREFIX}{due}/{signal_id}",
                json.dumps(row, separators=(",", ":")),
            )
        await kv.delete(pending_key)
    else:
        # Siblings first, then the marker, then the row: a failed write leaves the
        # row in place, so a retry redoes the whole acknowledgement.
        await _relink_rechecks(kv, signal_id, payload.get("pr_url"), acknowledged_key=recheck_key)
        await kv.put(
            RECHECK_DONE_PREFIX + recheck_key.removeprefix(RECHECK_PREFIX), today.isoformat(),
            expiration_ttl=_done_marker_ttl(json.loads(str(recheck)), recheck_due, today),
        )
        await kv.delete(recheck_key)
    return Outcome(200, {
        "schema_version": SCHEMA_VERSION,
        "endpoint": "signals.ack",
        "status": "acknowledged",
        "signal_id": signal_id,
        "recheck_days": [] if recheck is not None else [1, 7, 30],
    })
