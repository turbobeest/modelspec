"""The one visitor-identity helper (MODEL-241).

An opaque id for a request's visitor: HMAC-SHA256(secret, IP | UTC day), from
the Worker secret ``VISITOR_HMAC_KEY``. The key stops enumeration of the IPv4
space; the day rotates the id so it cannot follow a visitor across days. Nothing
raw or unkeyed is stored or logged. With no key, or no address, there is no id:
the caller treats the request as not identifiable, never falls back to a bare
hash. The MODEL-241 keyless meter uses the address as supplied. The human
gate normalises IPv6 to /64 before calling visitor_id.
"""

from __future__ import annotations

import hashlib
import hmac
from datetime import UTC, datetime

KEY_VAR = "VISITOR_HMAC_KEY"
PREFIX = "visitor:"
#: Fewer than this many characters is not a key worth the name.
MIN_KEY_CHARS = 16


def visitor_id(connecting_ip: str | None, secret: str | None,
               now: datetime | None = None) -> str | None:
    ip = str(connecting_ip or "").strip()
    key = str(secret or "")
    if not ip or len(key) < MIN_KEY_CHARS:
        return None
    day = (now or datetime.now(UTC)).astimezone(UTC).date().isoformat()
    message = f"{ip}|{day}".encode("utf-8")
    return PREFIX + hmac.new(key.encode("utf-8"), message, hashlib.sha256).hexdigest()


def visitor_id_for(request, env, now: datetime | None = None) -> str | None:
    """The id for a Workers request, reading the address and the secret."""
    return visitor_id(request.headers.get("CF-Connecting-IP"),
                      getattr(env, KEY_VAR, None), now)
