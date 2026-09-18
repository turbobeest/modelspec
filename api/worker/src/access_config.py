"""Tier limits, as configuration (MODEL-69).

Every number a caller can be refused by lives in `api/worker/tiers.json`. There
is no limit written in Python anywhere in this package, and
`tests/test_api_access.py` asserts that by changing a limit in a JSON document
and watching the behaviour change with no code edit. MODEL-73 provisions paid
plans by adding rows to that table, not by editing a handler.

Resolution order, most to least specific:

1. `TIER_POLICY` on the Worker's `env` — a JSON string. An operator can change
   a limit with a variable update and no code change at all.
2. The JSON text the caller passes in (this is how the deploy injects
   `tiers.json` without the isolate needing a filesystem).
3. `api/worker/tiers.json` read from disk. That is the path the repository's
   own tests and the CLI take; the Worker is not expected to reach it.

A policy that resolves to none of the three raises rather than falling back to
a limit invented in code. A missing configuration is an outage, and an outage
that announces itself beats a Worker quietly serving somebody else's numbers.
"""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

#: The committed tier table. `Path` is used by the tests and the build step;
#: the Worker gets the same bytes through `TIER_POLICY`.
try:
    DEFAULT_POLICY_PATH = Path(__file__).resolve().parents[1] / "tiers.json"
except (IndexError, NameError):  # pragma: no cover - an isolate laid out flat
    # Imported by the Worker at startup, so this must never raise. The isolate
    # reads the table from `TIER_POLICY`; a path that does not exist only means
    # the fallback refuses, as it should.
    DEFAULT_POLICY_PATH = Path("tiers.json")

#: The `env` variable the Worker reads the table from.
POLICY_ENV_VAR = "TIER_POLICY"

#: The only reset boundary this package implements. A table that asks for
#: another timezone is refused rather than silently metered in UTC — see
#: `access_limits`.
SUPPORTED_TIMEZONE = "UTC"


class PolicyError(ValueError):
    """The tier table is missing, unreadable, or does not say what it must."""


@dataclass(frozen=True)
class TierLimits:
    """One row of the tier table.

    `None` means unlimited, which is how the sandbox and DPF are expressed. It
    is not a flag the code branches on: `access_limits` compares a count with a
    limit, and a limit of `None` is a comparison that never refuses.
    """

    name: str
    daily_limit: int | None
    burst_limit: int | None
    live_data: bool
    paid: bool
    description: str

    @property
    def unlimited(self) -> bool:
        return self.daily_limit is None and self.burst_limit is None

    def to_json(self) -> dict[str, Any]:
        return {
            "tier": self.name,
            "daily_limit": self.daily_limit,
            "burst_limit": self.burst_limit,
            "live_data": self.live_data,
            "paid": self.paid,
            "description": self.description,
        }


@dataclass(frozen=True)
class AccessPolicy:
    """The whole table, plus the two strings that classify a key."""

    version: str
    timezone: str
    sandbox_prefix: str
    sandbox_tier: str
    live_prefix: str
    urls: Mapping[str, str]
    tiers: Mapping[str, TierLimits]

    def tier(self, name: str) -> TierLimits:
        try:
            return self.tiers[name]
        except KeyError:
            raise PolicyError(f"no tier named {name!r} in the tier table") from None

    def url(self, name: str) -> str:
        return self.urls.get(name, "")

    def to_json(self) -> dict[str, Any]:
        return {
            "policy_version": self.version,
            "timezone": self.timezone,
            "sandbox_prefix": self.sandbox_prefix,
            "urls": dict(self.urls),
            "tiers": {name: row.to_json() for name, row in self.tiers.items()},
        }


def _limit(row: Mapping[str, Any], field: str, tier: str) -> int | None:
    if field not in row:
        raise PolicyError(f"tier {tier!r} does not set {field}")
    value = row[field]
    if value is None:
        return None
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise PolicyError(f"tier {tier!r}: {field} must be a nonnegative integer or null")
    return value


def policy_from_mapping(data: Mapping[str, Any]) -> AccessPolicy:
    """Validate a decoded tier table. Every complaint names the field."""
    if not isinstance(data, Mapping):
        raise PolicyError("the tier table must be a JSON object")

    timezone = str(data.get("timezone") or "")
    if timezone != SUPPORTED_TIMEZONE:
        raise PolicyError(
            f"timezone must be {SUPPORTED_TIMEZONE!r}; {timezone!r} would need a "
            "reset boundary this package does not implement")

    raw_tiers = data.get("tiers")
    if not isinstance(raw_tiers, Mapping) or not raw_tiers:
        raise PolicyError("the tier table must carry a non-empty 'tiers' object")

    tiers: dict[str, TierLimits] = {}
    for name, row in raw_tiers.items():
        if not isinstance(row, Mapping):
            raise PolicyError(f"tier {name!r} must be an object")
        tiers[str(name)] = TierLimits(
            name=str(name),
            daily_limit=_limit(row, "daily_limit", str(name)),
            burst_limit=_limit(row, "burst_limit", str(name)),
            live_data=bool(row.get("live_data", True)),
            paid=bool(row.get("paid", False)),
            description=str(row.get("description") or ""),
        )

    sandbox_prefix = str(data.get("sandbox_prefix") or "")
    if not sandbox_prefix:
        raise PolicyError("the tier table must set 'sandbox_prefix'")
    sandbox_tier = str(data.get("sandbox_tier") or "sandbox")
    if sandbox_tier not in tiers:
        raise PolicyError(f"sandbox_tier {sandbox_tier!r} is not a row in the tier table")
    if tiers[sandbox_tier].live_data:
        raise PolicyError(f"tier {sandbox_tier!r} is the sandbox and must set live_data false")

    urls = data.get("urls") or {}
    if not isinstance(urls, Mapping) or not urls.get("get_a_key"):
        raise PolicyError("the tier table must carry urls.get_a_key, named in every refusal")

    return AccessPolicy(
        version=str(data.get("policy_version") or "unversioned"),
        timezone=timezone,
        sandbox_prefix=sandbox_prefix,
        sandbox_tier=sandbox_tier,
        live_prefix=str(data.get("live_prefix") or ""),
        urls={str(k): str(v) for k, v in urls.items()},
        tiers=tiers,
    )


def policy_from_json(text: str) -> AccessPolicy:
    try:
        data = json.loads(text)
    except ValueError as exc:
        raise PolicyError(f"the tier table is not valid JSON: {exc}") from None
    return policy_from_mapping(data)


def load_policy(env: Any = None, *, text: str | None = None,
                path: Path | None = None) -> AccessPolicy:
    """Resolve the tier table. See the module docstring for the order."""
    from_env = getattr(env, POLICY_ENV_VAR, None) if env is not None else None
    if from_env:
        return policy_from_json(str(from_env))
    if text:
        return policy_from_json(text)
    source = path or DEFAULT_POLICY_PATH
    try:
        return policy_from_json(source.read_text(encoding="utf-8"))
    except OSError as exc:
        raise PolicyError(
            f"no tier table: {POLICY_ENV_VAR} is unset and {source} could not be read ({exc})"
        ) from None
