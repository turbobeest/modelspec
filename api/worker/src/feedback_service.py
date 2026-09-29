"""`POST /v1/feedback`: what a person or an agent thought of an answer (MODEL-221).

One rating from a fixed set, optionally tied to a `decision_id`, with optional
free text. No key is required and none is read: the caller's `Authorization`
header never reaches this module.

**Storage ships off.** `FEEDBACK_ENABLED` in `wrangler.jsonc` is `"false"`, and
while it is off a valid body is answered `200 not_recorded` and nothing is
written anywhere. Turning it on is Jamie's call, after the privacy statement
covers it (`docs/design/feedback-privacy.md`). When it is on, a record goes to
its own Workers KV namespace (`FEEDBACK`), never to `ACCESS` or
`DETERMINATIONS`, and expires on its own after `RETENTION_DAYS`.

What a record holds is `STORED_FIELDS` and nothing else. No IP address, no key,
no user agent, no time finer than the day. Free text is scrubbed of what looks
like an email address, a URL's query, a phone number, an IP address or a
credential before it is stored (`scrub`).

Abuse limits need *something* per caller. The address is only ever used as the
input to an HMAC with a Worker secret (`FEEDBACK_LIMIT_PEPPER`) and the current
window, so the stored counter name changes every window and cannot be reversed
to the address by anyone who reads the namespace. The per-day counter expires
after two days; the per-minute counter lives in isolate memory only.

Nothing here imports the Workers runtime; `tests/test_feedback.py` drives it
under CPython with `access_kv.MemoryKV`.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import re
import secrets
import unicodedata
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

SCHEMA_VERSION = "1.0"
ENDPOINT_URL = "https://api.modelspec.dev/v1/feedback"
SCHEMA_URL = "https://modelspec.dev/api/feedback/v1.schema.json"
DOCS_URL = "https://github.com/turbobeest/modelspec/blob/main/docs/feedback-api.md"
PRIVACY_URL = "https://modelspec.dev/legal/privacy/"

#: The fixed choices. Order is the order a person sees them in.
RATINGS = ("reliable", "unreliable", "trustworthy", "untrustworthy", "confusing")
#: The ratings the weekly digest turns into issue drafts.
NEGATIVE_RATINGS = ("unreliable", "untrustworthy", "confusing")
#: Who sent it, as the caller says. Unverifiable, and used only to group.
CLIENTS = ("agent", "cli", "mcp", "page")

FIELDS = ("rating", "client", "decision_id", "note", "trying_to_decide", "page", "template")
REQUIRED = ("rating", "client")
#: What a stored record holds. The draft privacy wording lists exactly these,
#: and `tests/test_feedback.py` holds the two together.
STORED_FIELDS = (
    "received_on", "rating", "client", "decision_id", "page", "template",
    "note", "trying_to_decide", "redacted",
)

MAX_BODY_BYTES = 4096
NOTE_MAX = 1000
TRYING_TO_DECIDE_MAX = 300
PAGE_MAX = 200

DECISION_ID = re.compile(r"^dec_[0-9A-Za-z]{8,64}$")
TEMPLATE = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}$")
#: A site path only: no scheme, host, query or fragment ever reaches the store.
PAGE = re.compile(r"^/[A-Za-z0-9._~/-]{0,199}$")
RECEIPT = re.compile(r"^fbr_(\d{8})_([0-9a-f]{32})$")

#: Raw records are deleted by Workers KV itself after this many days. Jamie
#: decides the number before storage is turned on.
RETENTION_DAYS = 180
#: Per address. The minute window is isolate memory only; the day window is a
#: KV counter under an HMAC name that expires after two days.
BURST_LIMIT = 5
DAILY_LIMIT = 20
#: Across every caller, per UTC day. Bounds KV writes and a flood from many
#: addresses at once.
GLOBAL_DAILY_CAP = 1000

RECORD_PREFIX = "feedback/v1/record/"
LIMIT_PREFIX = "feedback/v1/limit/"
_DAY_COUNTER_TTL = 2 * 86_400

HTTP_OK = 200
HTTP_ACCEPTED = 202
HTTP_BAD_REQUEST = 400
HTTP_FORBIDDEN = 403
HTTP_NOT_FOUND = 404
HTTP_PAYLOAD_TOO_LARGE = 413
HTTP_TOO_MANY_REQUESTS = 429
HTTP_SERVICE_UNAVAILABLE = 503

#: Every refusal, with its status and what the caller should do about it.
#: `docs/feedback-api.md` repeats the fixes and the tests hold the two equal.
ERRORS: dict[str, tuple[int, str]] = {
    "invalid_request": (HTTP_BAD_REQUEST,
                        "Fix the body against the published schema and send it again."),
    "origin_not_allowed": (HTTP_FORBIDDEN,
                           "Send it from modelspec.dev, or from a client with no Origin header."),
    "receipt_not_found": (HTTP_NOT_FOUND,
                          "Nothing is stored under that receipt; it was deleted or never kept."),
    "payload_too_large": (HTTP_PAYLOAD_TOO_LARGE,
                          f"Keep the body under {MAX_BODY_BYTES} bytes; shorten the note."),
    "rate_limited": (HTTP_TOO_MANY_REQUESTS,
                     "Wait retry_after seconds, then send it once."),
    "feedback_store_unavailable": (HTTP_SERVICE_UNAVAILABLE,
                                   "Storage is on but not configured; retry later."),
}


@dataclass(frozen=True)
class Outcome:
    status: int
    body: dict[str, Any]
    headers: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class Feedback:
    """A validated request, before anything is stored."""

    rating: str
    client: str
    decision_id: str | None = None
    note: str | None = None
    trying_to_decide: str | None = None
    page: str | None = None
    template: str | None = None
    redacted: tuple[str, ...] = ()


def enabled(value: object) -> bool:
    return str(value or "").strip().casefold() not in {"", "0", "false", "no", "off"}


def _envelope(**body: Any) -> dict[str, Any]:
    return {"schema_version": SCHEMA_VERSION, "endpoint": "feedback", **body}


def error(code: str, message: str, **extra: Any) -> Outcome:
    status = ERRORS[code][0]
    headers = {}
    if "retry_after" in extra:
        headers["retry-after"] = str(extra["retry_after"])
    return Outcome(status, _envelope(error={"code": code, "message": message, **extra}), headers)


# ── free text ────────────────────────────────────────────────────────────────

_EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
#: A URL's query and fragment go; its scheme, host and path stay.
_URL_TAIL = re.compile(r"(\bhttps?://[^\s?#]+)[?#]\S*", re.I)
_IPV4 = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
_IPV6 = re.compile(r"\b(?:[0-9a-f]{1,4}:){2,7}[0-9a-f]{1,4}\b", re.I)
#: Credential shapes: a known vendor prefix, a bearer header, a ModelSpec key.
_SECRET_PREFIXED = re.compile(
    r"\b(?:sk|rk|ghp|gho|ghs|github_pat|xox[abpr]|hf|glpat|AIza)[-_][A-Za-z0-9_-]{8,}"
    r"|\b(?:live|test)_[A-Za-z0-9]{16,}"
    r"|\bAKIA[0-9A-Z]{12,}\b"
    r"|\bBearer\s+\S+", re.I)
#: A long unbroken run that mixes letters and digits, as keys do and model
#: slugs (hyphenated) and words do not. Decision and snapshot IDs are kept.
_LONG_TOKEN = re.compile(r"\b[A-Za-z0-9_]{24,}\b|[A-Za-z0-9+/]{40,}={0,2}")
_KEPT_IDS = ("dec_", "snap_", "sha256")
#: An international number, or a North American one in its usual shape.
_PHONE = re.compile(r"\+\d[\d ().-]{7,}\d|\(?\b\d{3}\)?[ .-]\d{3}[ .-]\d{4}\b")


def _is_secret_like(token: str) -> bool:
    return (not token.startswith(_KEPT_IDS)
            and any(c.isdigit() for c in token) and any(c.isalpha() for c in token))


def scrub(text: str) -> tuple[str, set[str]]:
    """Free text with what looks like personal data or a credential replaced.

    Best effort, and stated as such: it catches the shapes, not the meaning.
    The field is labelled optional and asks for none of these things.
    """
    found: set[str] = set()

    def swap(kind: str, pattern: re.Pattern[str], value: str, keep=None) -> str:
        def replace(match: re.Match[str]) -> str:
            if keep is not None and not keep(match.group(0)):
                return match.group(0)
            found.add(kind)
            return f"[{kind}]"
        return pattern.sub(replace, value)

    def drop_query(match: re.Match[str]) -> str:
        found.add("url_query")
        return match.group(1)

    text = unicodedata.normalize("NFC", text)
    text = "".join(c if (c.isprintable() or c == "\n") else " " for c in text)
    text = swap("secret", _SECRET_PREFIXED, text)
    text = swap("email", _EMAIL, text)
    text = _URL_TAIL.sub(drop_query, text)
    text = swap("ip", _IPV4, text)
    text = swap("ip", _IPV6, text)
    text = swap("secret", _LONG_TOKEN, text, _is_secret_like)
    text = swap("phone", _PHONE, text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    return text, found


# ── the request ──────────────────────────────────────────────────────────────

def parse(payload: Any) -> Feedback | Outcome:
    """A `Feedback`, or the refusal that says exactly what was wrong."""
    if not isinstance(payload, dict):
        return error("invalid_request", "the body must be a JSON object")
    unknown = sorted(set(payload) - set(FIELDS))
    if unknown:
        return error("invalid_request",
                     f"unknown field(s) {unknown}; accepted: {list(FIELDS)}")
    missing = [name for name in REQUIRED if name not in payload]
    if missing:
        return error("invalid_request", f"missing required field(s) {missing}")

    rating, client = payload["rating"], payload["client"]
    if rating not in RATINGS:
        return error("invalid_request", f"rating must be one of {list(RATINGS)}")
    if client not in CLIENTS:
        return error("invalid_request", f"client must be one of {list(CLIENTS)}")

    def optional(name: str) -> str | None | Outcome:
        value = payload.get(name)
        if value is None:
            return None
        if not isinstance(value, str):
            return error("invalid_request", f"{name} must be a string or null")
        return value.strip() or None

    values: dict[str, str | None] = {}
    for name in ("decision_id", "note", "trying_to_decide", "page", "template"):
        value = optional(name)
        if isinstance(value, Outcome):
            return value
        values[name] = value

    if values["decision_id"] is not None and not DECISION_ID.fullmatch(values["decision_id"]):
        return error("invalid_request", "decision_id must look like dec_<8-64 letters or digits>")
    if values["template"] is not None and not TEMPLATE.fullmatch(values["template"]):
        return error("invalid_request", "template must be a lowercase template id")
    if values["page"] is not None:
        page = values["page"].split("?", 1)[0].split("#", 1)[0]
        if not PAGE.fullmatch(page):
            return error("invalid_request",
                         f"page must be a site path such as /decide/, at most {PAGE_MAX} characters")
        values["page"] = page

    redacted: set[str] = set()
    for name, cap in (("note", NOTE_MAX), ("trying_to_decide", TRYING_TO_DECIDE_MAX)):
        if values[name] is None:
            continue
        if len(values[name]) > cap:
            return error("invalid_request", f"{name} must be at most {cap} characters")
        text, kinds = scrub(values[name])
        redacted |= kinds
        values[name] = text or None

    return Feedback(rating=rating, client=client, redacted=tuple(sorted(redacted)), **values)


def record(feedback: Feedback, received_on: str) -> dict[str, Any]:
    """The stored form: `STORED_FIELDS`, in that order, nothing else."""
    body = {
        "received_on": received_on,
        "rating": feedback.rating,
        "client": feedback.client,
        "decision_id": feedback.decision_id,
        "page": feedback.page,
        "template": feedback.template,
        "note": feedback.note,
        "trying_to_decide": feedback.trying_to_decide,
        "redacted": list(feedback.redacted),
    }
    assert tuple(body) == STORED_FIELDS
    return body


# ── limits ───────────────────────────────────────────────────────────────────

#: Per isolate, never persisted. Replaced at cold start, so nothing in it
#: outlives the isolate, and its key is a random salt nobody else holds. The
#: salt is drawn on first use, not at import: the Workers runtime refuses
#: randomness while an isolate starts, because a startup value would be
#: repeated in every isolate restored from the same snapshot.
_salt: list[bytes] = []
_memory: dict[str, int] = {}
_MEMORY_MAX_KEYS = 10_000


def _memory_salt() -> bytes:
    if not _salt:
        _salt.append(secrets.token_bytes(32))
    return _salt[0]


def _mac(key: bytes, window: str, address: str) -> str:
    return hmac.new(key, f"{window}|{address}".encode(), hashlib.sha256).hexdigest()[:32]


def _burst_allowed(address: str, now: datetime) -> bool:
    minute = now.strftime("%Y%m%d%H%M")
    if len(_memory) > _MEMORY_MAX_KEYS:
        stale = [name for name in _memory if not name.startswith(minute)]
        for name in stale:
            _memory.pop(name, None)
        if len(_memory) > _MEMORY_MAX_KEYS:
            _memory.clear()
    name = f"{minute}:{_mac(_memory_salt(), minute, address)}"
    count = _memory.get(name, 0)
    if count >= BURST_LIMIT:
        return False
    _memory[name] = count + 1
    return True


async def _counter(kv: Any, name: str) -> int:
    raw = await kv.get(name)
    try:
        return int(str(raw)) if raw is not None else 0
    except ValueError:
        return 0


# ── the endpoint ─────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class Store:
    """What `submit` and `withdraw` need from the Worker, as plain values."""

    enabled: bool
    kv: Any | None
    pepper: bytes

    @property
    def ready(self) -> bool:
        return self.kv is not None and len(self.pepper) >= 16


def _not_recorded(feedback: Feedback) -> Outcome:
    return Outcome(HTTP_OK, _envelope(
        status="not_recorded",
        recorded=False,
        receipt=None,
        retention_days=None,
        redacted=list(feedback.redacted),
        message=("Thank you. Feedback storage is switched off until the privacy statement "
                 "covers it, so nothing was kept."),
        privacy=PRIVACY_URL,
    ))


def origin_allowed(origin: str | None, allowed: frozenset[str]) -> bool:
    """A browser must be on a ModelSpec origin. A client with no Origin is not a browser."""
    return not origin or origin in allowed


async def submit(
    *,
    raw: bytes,
    address: str,
    origin: str | None,
    allowed_origins: frozenset[str],
    store: Store,
    now: datetime | None = None,
) -> Outcome:
    """Validate, limit and — only when storage is on — keep one piece of feedback."""
    now = (now or datetime.now(UTC)).astimezone(UTC)
    if not origin_allowed(origin, allowed_origins):
        return error("origin_not_allowed", "this origin may not send feedback")
    if len(raw) > MAX_BODY_BYTES:
        return error("payload_too_large", f"the body must be at most {MAX_BODY_BYTES} bytes")
    try:
        payload = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, ValueError) as exc:
        return error("invalid_request", f"the body is not valid JSON: {type(exc).__name__}")
    parsed = parse(payload)
    if isinstance(parsed, Outcome):
        return parsed
    if not _burst_allowed(address, now):
        return error("rate_limited", f"at most {BURST_LIMIT} a minute", retry_after=60)
    if not store.enabled:
        return _not_recorded(parsed)
    if not store.ready:
        return error("feedback_store_unavailable",
                     "feedback storage is switched on but has no store or limit secret")

    day = now.date().isoformat()
    seconds_left = 86_400 - (now.hour * 3600 + now.minute * 60 + now.second)
    global_name = f"{LIMIT_PREFIX}global/{day}"
    address_name = f"{LIMIT_PREFIX}day/{day}/{_mac(store.pepper, day, address)}"
    total, mine = await _counter(store.kv, global_name), await _counter(store.kv, address_name)
    if total >= GLOBAL_DAILY_CAP:
        return error("rate_limited", "the service has taken all the feedback it can for today",
                     retry_after=seconds_left)
    if mine >= DAILY_LIMIT:
        return error("rate_limited", f"at most {DAILY_LIMIT} a day from one address",
                     retry_after=seconds_left)

    receipt = f"fbr_{now.strftime('%Y%m%d')}_{secrets.token_hex(16)}"
    await store.kv.put(_record_name(receipt), json.dumps(record(parsed, day),
                                                         separators=(",", ":")),
                       expiration_ttl=RETENTION_DAYS * 86_400)
    await store.kv.put(address_name, str(mine + 1), expiration_ttl=_DAY_COUNTER_TTL)
    await store.kv.put(global_name, str(total + 1), expiration_ttl=_DAY_COUNTER_TTL)
    return Outcome(HTTP_ACCEPTED, _envelope(
        status="recorded",
        recorded=True,
        receipt=receipt,
        retention_days=RETENTION_DAYS,
        redacted=list(parsed.redacted),
        message=("Thank you. Keep the receipt if you may want this deleted: "
                 "DELETE /v1/feedback with {\"receipt\": …}."),
        privacy=PRIVACY_URL,
    ))


def _record_name(receipt: str) -> str:
    """The KV name for a receipt. The receipt itself is never stored."""
    match = RECEIPT.fullmatch(receipt)
    assert match is not None
    day = f"{match.group(1)[:4]}-{match.group(1)[4:6]}-{match.group(1)[6:]}"
    return f"{RECORD_PREFIX}{day}/{hashlib.sha256(receipt.encode()).hexdigest()}"


async def withdraw(
    *,
    raw: bytes,
    address: str,
    origin: str | None,
    allowed_origins: frozenset[str],
    store: Store,
    now: datetime | None = None,
) -> Outcome:
    """`DELETE /v1/feedback`: remove one record by the receipt it was given."""
    now = (now or datetime.now(UTC)).astimezone(UTC)
    if not origin_allowed(origin, allowed_origins):
        return error("origin_not_allowed", "this origin may not delete feedback")
    if len(raw) > MAX_BODY_BYTES:
        return error("payload_too_large", f"the body must be at most {MAX_BODY_BYTES} bytes")
    try:
        payload = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, ValueError) as exc:
        return error("invalid_request", f"the body is not valid JSON: {type(exc).__name__}")
    if not isinstance(payload, dict) or set(payload) != {"receipt"} \
            or not isinstance(payload["receipt"], str) \
            or not RECEIPT.fullmatch(payload["receipt"]):
        return error("invalid_request", 'the body must be {"receipt": "fbr_<date>_<32 hex>"}')
    if not _burst_allowed(address, now):
        return error("rate_limited", f"at most {BURST_LIMIT} a minute", retry_after=60)
    if not store.enabled or not store.ready:
        return error("receipt_not_found", "no feedback is stored under that receipt")
    name = _record_name(payload["receipt"])
    if await store.kv.get(name) is None:
        return error("receipt_not_found", "no feedback is stored under that receipt")
    await store.kv.delete(name)
    return Outcome(HTTP_OK, _envelope(status="deleted", recorded=False))


# ── the published request schema ─────────────────────────────────────────────

def request_schema() -> dict[str, Any]:
    """JSON Schema for the request body, published at `SCHEMA_URL`.

    Generated from the constants above so the schema, the OpenAPI document and
    the validator cannot disagree. `schemas/feedback-v1.schema.json` is this,
    written out; `tests/test_feedback.py` fails if it drifts.
    """
    def text(description: str, cap: int) -> dict[str, Any]:
        return {"type": ["string", "null"], "maxLength": cap, "description": description}

    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": SCHEMA_URL,
        "title": "ModelSpec feedback",
        "description": (
            f"POST this to {ENDPOINT_URL}. No key. One rating from a fixed set, "
            "optionally tied to the decision_id of a ModelSpec answer. Never include a "
            "prompt, a key, or anything that identifies a person. "
            f"Reference: {DOCS_URL}"
        ),
        "type": "object",
        "additionalProperties": False,
        "required": list(REQUIRED),
        "properties": {
            "rating": {"enum": list(RATINGS),
                       "description": "What you thought of the answer or the page."},
            "client": {"enum": list(CLIENTS),
                       "description": "What is sending it: an agent, the CLI, the MCP "
                                      "server, or the website."},
            "decision_id": {"type": ["string", "null"], "pattern": DECISION_ID.pattern,
                            "description": "The decision_id of the answer this is about."},
            "note": text("Optional. What was wrong or right, in your words.", NOTE_MAX),
            "trying_to_decide": text("Optional. What you were trying to decide.",
                                     TRYING_TO_DECIDE_MAX),
            "page": {"type": ["string", "null"], "pattern": PAGE.pattern,
                     "description": "Optional. The site path, such as /decide/."},
            "template": {"type": ["string", "null"], "pattern": TEMPLATE.pattern,
                         "description": "Optional. The decision template in use."},
        },
        "examples": [
            {"rating": "unreliable", "client": "agent", "decision_id": "dec_3f9a1c2b7d4e",
             "note": "The top pick has no pricing for my region."},
        ],
    }
