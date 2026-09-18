"""API keys: format, storage, lookup (MODEL-69).

The secret never reaches the store. A key is looked up by the SHA-256 of its
own bytes, so what is written to KV — both the name and the value — is
survivable in a leak: the record carries a tier, an owner and a short
fingerprint, and nothing that can be replayed against the endpoint.

That is also what makes "no key value is ever logged" a property of the design
rather than a rule to remember. There is no field on `KeyRecord` that holds the
secret, so an accidental `repr()` in a log line cannot print one, and
`tests/test_api_access.py` searches every log record, response body, header and
stored value for the secret it issued.

Two key shapes:

* `test_…` — the sandbox. Valid by construction, never looked up, never stored,
  so a sandbox request touches neither the key store nor the live data.
* `live_…` — issued, stored, metered. The prefix is configuration
  (`tiers.json`), not a literal in this module.
"""

from __future__ import annotations

import hashlib
import json
import secrets
from dataclasses import dataclass, replace
from datetime import datetime
from typing import Any

from access_config import AccessPolicy

#: How much of the fingerprint identifies a key in a log line or a support
#: conversation. 12 hex characters of SHA-256; it identifies, it does not
#: authenticate, and it cannot be walked back to the secret.
KEY_ID_LENGTH = 12

#: Bytes of entropy behind a live key.
SECRET_BYTES = 24

_STORE_PREFIX = "key:"


class StoredKeyError(ValueError):
    """Something is wrong with a stored record, not with the caller."""


@dataclass(frozen=True)
class KeyRecord:
    """What is known about a key. Deliberately not the key.

    `owner` is whoever the key was issued to; MODEL-73 writes a billing
    reference there. `tier` names a row in the tier table, and is the only
    thing that decides what this key may do.
    """

    key_id: str
    tier: str
    owner: str
    created_at: str
    active: bool = True
    label: str = ""

    def to_json(self) -> dict[str, Any]:
        return {
            "key_id": self.key_id,
            "tier": self.tier,
            "owner": self.owner,
            "created_at": self.created_at,
            "active": self.active,
            "label": self.label,
        }

    @classmethod
    def from_json(cls, text: str) -> KeyRecord:
        try:
            data = json.loads(text)
        except ValueError as exc:
            raise StoredKeyError(f"stored key record is not valid JSON: {exc}") from None
        if not isinstance(data, dict) or not data.get("tier"):
            raise StoredKeyError("stored key record carries no tier")
        return cls(
            key_id=str(data.get("key_id") or ""),
            tier=str(data["tier"]),
            owner=str(data.get("owner") or ""),
            created_at=str(data.get("created_at") or ""),
            active=bool(data.get("active", True)),
            label=str(data.get("label") or ""),
        )


def normalise(raw: str | None) -> str | None:
    """Trim a presented key, or `None` when there was not one."""
    if raw is None:
        return None
    value = str(raw).strip()
    return value or None


def fingerprint(key: str) -> str:
    """SHA-256 of the key. The only form of a key that is ever written down."""
    return hashlib.sha256(key.encode("utf-8")).hexdigest()


def key_id(key: str) -> str:
    """The short, loggable identifier for a key."""
    return fingerprint(key)[:KEY_ID_LENGTH]


def storage_name_from_fingerprint(fingerprint_hex: str) -> str:
    """The KV name a key's record lives under, given the hash we already stored."""
    return _STORE_PREFIX + fingerprint_hex


def storage_name(key: str) -> str:
    """The KV name a key's record lives under."""
    return storage_name_from_fingerprint(fingerprint(key))


def is_sandbox(key: str, policy: AccessPolicy) -> bool:
    """Is this a sandbox key? Decided by the configured prefix alone."""
    return key.startswith(policy.sandbox_prefix)


def extract(get_header: Any) -> str | None:
    """Read the key off the request headers.

    `Authorization: Bearer <key>` first, `X-API-Key: <key>` second. A key is
    never read from the query string: URLs are logged by everything they pass
    through, and a secret in one is a secret in somebody else's access log.
    """
    authorization = normalise(get_header("authorization"))
    if authorization:
        scheme, _, value = authorization.partition(" ")
        if scheme.lower() == "bearer":
            return normalise(value)
        return None
    return normalise(get_header("x-api-key"))


def mint(policy: AccessPolicy) -> str:
    """A fresh live key. The only place a secret is generated."""
    return f"{policy.live_prefix}{secrets.token_urlsafe(SECRET_BYTES)}"


async def issue(kv: Any, *, tier: str, owner: str, now: datetime,
                policy: AccessPolicy, label: str = "",
                secret: str | None = None) -> tuple[str, KeyRecord]:
    """Create and store a key. Returns `(secret, record)`.

    The secret is returned to the caller once and never again: the store holds
    only its fingerprint. `secret` is injectable so a test can use a known
    value; nothing else should pass it.
    """
    policy.tier(tier)  # refuses here rather than at the caller's first request
    key = secret or mint(policy)
    record = KeyRecord(
        key_id=key_id(key), tier=tier, owner=owner,
        created_at=now.isoformat().replace("+00:00", "Z"), active=True, label=label,
    )
    await kv.put(storage_name(key), json.dumps(record.to_json()))
    return key, record


async def lookup(kv: Any, key: str) -> KeyRecord | None:
    """The record behind a presented key, or `None` if there is not one."""
    stored = await kv.get(storage_name(key))
    if stored is None:
        return None
    return KeyRecord.from_json(stored)


async def revoke(kv: Any, key: str) -> bool:
    """Mark a key inactive, keeping the record so the refusal can say why."""
    record = await lookup(kv, key)
    if record is None:
        return False
    disabled = replace(record, active=False)
    await kv.put(storage_name(key), json.dumps(disabled.to_json()))
    return True


async def lookup_fingerprint(kv: Any, fingerprint_hex: str) -> KeyRecord | None:
    """The record stored under a fingerprint, or `None` if there is not one."""
    stored = await kv.get(storage_name_from_fingerprint(fingerprint_hex))
    if stored is None:
        return None
    return KeyRecord.from_json(stored)


async def set_tier(kv: Any, fingerprint_hex: str, tier: str, *,
                   policy: AccessPolicy) -> KeyRecord | None:
    """Move an issued key onto another row of the tier table.

    Used to downgrade a cancelled or failed subscription to free limits, and to
    restore the mapped tier after a later successful invoice. The key value
    does not change; only the record's `tier` does.
    """
    policy.tier(tier)
    record = await lookup_fingerprint(kv, fingerprint_hex)
    if record is None:
        return None
    updated = replace(record, tier=tier)
    await kv.put(storage_name_from_fingerprint(fingerprint_hex),
                 json.dumps(updated.to_json()))
    return updated
