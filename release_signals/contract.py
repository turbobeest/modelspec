"""Version 1 of the Grok Bot release-signal contract."""

from __future__ import annotations

import hashlib
import hmac
import json
import re
from collections.abc import Mapping
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from typing import Any
from urllib.parse import urlsplit

FIELDS = (
    "model_name",
    "provider",
    "first_seen_url",
    "timestamp",
    "confidence",
    "signal_id",
)
SIGNAL_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{0,127}$")
RFC3339_DATE_TIME = re.compile(
    r"^\d{4}-\d{2}-\d{2}[Tt]\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:[Zz]|[+-]\d{2}:\d{2})$"
)
X_HOSTS = frozenset({"x.com", "www.x.com", "twitter.com", "www.twitter.com"})


class SignalError(ValueError):
    """A release signal is unauthenticated or outside contract version 1."""


def sign(secret: bytes, body: bytes) -> str:
    """Return the v1 signature header for the exact request body."""
    if not secret:
        raise SignalError("the signing secret is empty")
    return "sha256=" + hmac.new(secret, body, hashlib.sha256).hexdigest()


@dataclass(frozen=True)
class ReleaseSignal:
    model_name: str
    provider: str
    first_seen_url: str
    timestamp: str
    confidence: float
    signal_id: str

    @classmethod
    def parse(cls, value: Mapping[str, Any]) -> ReleaseSignal:
        if not isinstance(value, Mapping):
            raise SignalError("the signal must be a JSON object")
        unknown = set(value) - set(FIELDS)
        missing = set(FIELDS) - set(value)
        if unknown or missing:
            detail = []
            if missing:
                detail.append(f"missing {sorted(missing)}")
            if unknown:
                detail.append(f"unknown {sorted(unknown)}")
            raise SignalError("; ".join(detail))

        model_name = _text(value["model_name"], "model_name")
        provider = _text(value["provider"], "provider")
        first_seen_url = _text(value["first_seen_url"], "first_seen_url")
        parsed_url = urlsplit(first_seen_url)
        if (
            parsed_url.scheme != "https"
            or parsed_url.netloc not in X_HOSTS
            or not parsed_url.path.startswith("/")
        ):
            raise SignalError("first_seen_url must be an https URL on x.com or twitter.com")

        timestamp = _text(value["timestamp"], "timestamp")
        if timestamp != value["timestamp"] or not RFC3339_DATE_TIME.fullmatch(timestamp):
            raise SignalError("timestamp must be an RFC 3339 date-time")
        try:
            instant = datetime.fromisoformat(_normalise_utc_designator(timestamp))
        except ValueError as exc:
            raise SignalError("timestamp must be an RFC 3339 date-time") from exc
        if instant.tzinfo is None:
            raise SignalError("timestamp must include a UTC offset")

        confidence = value["confidence"]
        if isinstance(confidence, bool) or not isinstance(confidence, (int, float)):
            raise SignalError("confidence must be a number from 0 through 1")
        if not 0 <= float(confidence) <= 1:
            raise SignalError("confidence must be a number from 0 through 1")

        signal_id = _text(value["signal_id"], "signal_id")
        if not SIGNAL_ID.fullmatch(signal_id):
            raise SignalError("signal_id contains unsupported characters")
        return cls(
            model_name=model_name,
            provider=provider,
            first_seen_url=first_seen_url,
            timestamp=timestamp,
            confidence=float(confidence),
            signal_id=signal_id,
        )

    @classmethod
    def from_signed_body(
        cls, body: bytes, signature: str | None, secret: bytes
    ) -> ReleaseSignal:
        expected = sign(secret, body)
        if not signature or not hmac.compare_digest(signature.strip(), expected):
            raise SignalError("the signal signature is invalid")
        try:
            payload = json.loads(body)
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise SignalError(f"the body is not valid JSON: {exc}") from exc
        return cls.parse(payload)

    @property
    def instant(self) -> datetime:
        return datetime.fromisoformat(_normalise_utc_designator(self.timestamp)).astimezone(UTC)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _text(value: Any, field: str) -> str:
    if (
        not isinstance(value, str)
        or not value
        or value != value.strip()
        or len(value) > 300
    ):
        raise SignalError(f"{field} must be a non-empty string of at most 300 characters")
    return value


def _normalise_utc_designator(value: str) -> str:
    return value[:-1] + "+00:00" if value.endswith(("Z", "z")) else value
