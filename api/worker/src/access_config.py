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
from decimal import Decimal, InvalidOperation
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
class OverageConfig:
    """Metered credits past a plan's allowance. Off while `placeholder` is set.

    `usd_per_credit` is a decimal string. The cap is per billing period and is
    the current table's cap at spend time, not a number frozen at purchase.
    """

    usd_per_credit: str
    cap_credits: int
    price_id: str
    meter_event: str
    placeholder: bool

    @property
    def active(self) -> bool:
        return not self.placeholder

    def rate(self) -> Decimal:
        return Decimal(self.usd_per_credit)

    def to_json(self) -> dict[str, Any]:
        return {
            "usd_per_credit": self.usd_per_credit,
            "cap_credits": self.cap_credits,
            "price_id": self.price_id,
            "meter_event": self.meter_event,
            "placeholder": self.placeholder,
        }


@dataclass(frozen=True)
class PriceMapping:
    """One Stripe Price id. Configuration, not code.

    `kind` is `plan` (recurring, SET monthly) or `pack` (one-off, ADD with
    expiry). `credits` is the amount that grant moves. `tier` is the access
    row the minted key is stored under. A legacy row still grants on a Stripe
    webhook and is never offered at checkout.
    """

    price_id: str
    kind: str
    name: str
    credits: int
    usd: int
    tier: str
    interval: str
    placeholder: bool
    description: str
    legacy: bool = False
    overage: OverageConfig | None = None

    @property
    def checkout_mode(self) -> str:
        return "subscription" if self.kind == "plan" else "payment"

    @property
    def for_sale(self) -> bool:
        return not self.placeholder and not self.legacy

    def to_json(self) -> dict[str, Any]:
        data = {
            "price_id": self.price_id,
            "kind": self.kind,
            "name": self.name,
            "credits": self.credits,
            "usd": self.usd,
            "tier": self.tier,
            "interval": self.interval,
            "placeholder": self.placeholder,
            "legacy": self.legacy,
            "description": self.description,
        }
        if self.overage is not None:
            data["overage"] = self.overage.to_json()
        return data


@dataclass(frozen=True)
class ReadsConfig:
    """Keyed metadata reads. One credit covers `reads_per_credit` successful reads."""

    reads_per_credit: int
    daily_cap: int
    burst_limit: int

    def to_json(self) -> dict[str, Any]:
        return {
            "reads_per_credit": self.reads_per_credit,
            "daily_cap": self.daily_cap,
            "burst_limit": self.burst_limit,
        }


@dataclass(frozen=True)
class X402ListPrice:
    """Published x402 price for one decision. A decimal string, config only."""

    list_usd_per_decision: str

    def rate(self) -> Decimal:
        return Decimal(self.list_usd_per_decision)

    def to_json(self) -> dict[str, Any]:
        return {"list_usd_per_decision": self.list_usd_per_decision}


@dataclass(frozen=True)
class CreditsConfig:
    """Credit weights, paid burst, and pack expiry. Every number is in `tiers.json`."""

    weights: Mapping[str, int]
    burst_limit: int
    pack_expiry_days: int
    reads: ReadsConfig | None = None

    def weight(self, resource: str) -> int:
        try:
            return int(self.weights[resource])
        except KeyError:
            raise PolicyError(f"credits.weights has no entry for {resource!r}") from None

    def to_json(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "weights": dict(self.weights),
            "burst_limit": self.burst_limit,
            "pack_expiry_days": self.pack_expiry_days,
        }
        if self.reads is not None:
            data["reads"] = self.reads.to_json()
        return data


@dataclass(frozen=True)
class BillingConfig:
    """Stripe Checkout mapping and windows. Every number lives in `tiers.json`."""

    downgrade_tier: str
    terms_url: str
    cancel_url: str
    success_path: str
    signature_tolerance_seconds: int
    event_ttl_seconds: int
    prices: Mapping[str, PriceMapping]

    def to_json(self) -> dict[str, Any]:
        return {
            "downgrade_tier": self.downgrade_tier,
            "terms_url": self.terms_url,
            "cancel_url": self.cancel_url,
            "success_path": self.success_path,
            "signature_tolerance_seconds": self.signature_tolerance_seconds,
            "event_ttl_seconds": self.event_ttl_seconds,
            "prices": {price_id: row.to_json() for price_id, row in self.prices.items()},
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
    billing: BillingConfig
    credits: CreditsConfig
    x402: X402ListPrice | None = None

    def tier(self, name: str) -> TierLimits:
        try:
            return self.tiers[name]
        except KeyError:
            raise PolicyError(f"no tier named {name!r} in the tier table") from None

    def url(self, name: str) -> str:
        return self.urls.get(name, "")

    def price(self, price_id: str) -> PriceMapping:
        row = self.billing.prices.get(price_id)
        if row is None:
            raise PolicyError(f"no Stripe price {price_id!r} in the tier table")
        return row

    def tier_for_price(self, price_id: str) -> str:
        """The access tier a Stripe Price's key is stored under."""
        row = self.price(price_id)
        self.tier(row.tier)
        return row.tier

    def price_ids(self) -> list[str]:
        """Mapped Stripe Price ids, sorted. Checkout names these on a 400."""
        return sorted(self.billing.prices)

    def to_json(self) -> dict[str, Any]:
        return {
            "policy_version": self.version,
            "timezone": self.timezone,
            "sandbox_prefix": self.sandbox_prefix,
            "urls": dict(self.urls),
            "tiers": {name: row.to_json() for name, row in self.tiers.items()},
            "billing": self.billing.to_json(),
            "credits": self.credits.to_json(),
        } | ({"x402": self.x402.to_json()} if self.x402 is not None else {})


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
        billing=_billing(data.get("billing"), tiers),
        credits=_credits(data.get("credits")),
        x402=_x402_list(data.get("x402")) if "x402" in data else None,
    )


def _nonneg_int(row: Mapping[str, Any], field: str, *, where: str) -> int:
    if field not in row:
        raise PolicyError(f"{where} does not set {field}")
    value = row[field]
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise PolicyError(f"{where}: {field} must be a nonnegative integer")
    return value


def _billing(raw: Any, tiers: Mapping[str, TierLimits]) -> BillingConfig:
    """Stripe price mapping and windows. Absent means 'not configured', not defaults."""
    if raw is None:
        return BillingConfig(
            downgrade_tier="free" if "free" in tiers else next(iter(tiers)),
            terms_url="", cancel_url="", success_path="/v1/billing/claim",
            signature_tolerance_seconds=0, event_ttl_seconds=0, prices={},
        )
    if not isinstance(raw, Mapping):
        raise PolicyError("billing must be a JSON object")
    downgrade = str(raw.get("downgrade_tier") or "")
    if not downgrade or downgrade not in tiers:
        raise PolicyError(f"billing.downgrade_tier {downgrade!r} is not a row in the tier table")
    raw_prices = raw.get("prices")
    if not isinstance(raw_prices, Mapping):
        raise PolicyError("billing.prices must be an object (empty is allowed)")
    prices: dict[str, PriceMapping] = {}
    for price_id, row in raw_prices.items():
        if not isinstance(row, Mapping):
            raise PolicyError(f"billing.prices[{price_id!r}] must be an object")
        tier = str(row.get("tier") or "")
        if tier not in tiers:
            raise PolicyError(
                f"billing.prices[{price_id!r}] names tier {tier!r}, which is not in the table")
        kind = str(row.get("kind") or "")
        if kind not in {"plan", "pack"}:
            raise PolicyError(
                f"billing.prices[{price_id!r}].kind must be 'plan' or 'pack'")
        name = str(row.get("name") or "")
        if not name:
            raise PolicyError(f"billing.prices[{price_id!r}] does not set name")
        credits = _nonneg_int(row, "credits", where=f"billing.prices[{price_id!r}]")
        if credits < 1:
            raise PolicyError(f"billing.prices[{price_id!r}].credits must be at least 1")
        usd = 0
        if "usd" in row:
            usd = _nonneg_int(row, "usd", where=f"billing.prices[{price_id!r}]")
        interval = str(row.get("interval") or ("month" if kind == "plan" else "once"))
        prices[str(price_id)] = PriceMapping(
            price_id=str(price_id),
            kind=kind,
            name=name,
            credits=credits,
            usd=usd,
            tier=tier,
            interval=interval,
            placeholder=bool(row.get("placeholder", False)),
            description=str(row.get("description") or ""),
            legacy=bool(row.get("legacy", False)),
            overage=_overage(row.get("overage"), str(price_id), kind),
        )
    _check_overage_rates(prices)
    return BillingConfig(
        downgrade_tier=downgrade,
        terms_url=str(raw.get("terms_url") or ""),
        cancel_url=str(raw.get("cancel_url") or ""),
        success_path=str(raw.get("success_path") or "/v1/billing/claim"),
        signature_tolerance_seconds=_nonneg_int(
            raw, "signature_tolerance_seconds", where="billing"),
        event_ttl_seconds=_nonneg_int(raw, "event_ttl_seconds", where="billing"),
        prices=prices,
    )


def _credits(raw: Any) -> CreditsConfig:
    """Credit weights and pack expiry. Absent is a configuration error, not a default."""
    if not isinstance(raw, Mapping):
        raise PolicyError("credits must be a JSON object")
    raw_weights = raw.get("weights")
    if not isinstance(raw_weights, Mapping) or not raw_weights:
        raise PolicyError("credits.weights must be a non-empty object")
    weights: dict[str, int] = {}
    for name, value in raw_weights.items():
        if not isinstance(value, int) or isinstance(value, bool) or value < 1:
            raise PolicyError(
                f"credits.weights[{name!r}] must be a positive integer")
        weights[str(name)] = value
    for required in ("rank", "policy-check", "decide.none", "decide.summary",
                     "decide.full"):
        if required not in weights:
            raise PolicyError(f"credits.weights must set {required!r}")
    expiry = _nonneg_int(raw, "pack_expiry_days", where="credits")
    if expiry < 1:
        raise PolicyError("credits.pack_expiry_days must be at least 1")
    return CreditsConfig(
        weights=weights,
        burst_limit=_nonneg_int(raw, "burst_limit", where="credits"),
        pack_expiry_days=expiry,
        reads=_reads(raw.get("reads")) if "reads" in raw else None,
    )


def _positive_int(row: Mapping[str, Any], field: str, *, where: str) -> int:
    value = _nonneg_int(row, field, where=where)
    if value < 1:
        raise PolicyError(f"{where}: {field} must be at least 1")
    return value


def _decimal_str(value: Any, where: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise PolicyError(f"{where} must be a positive decimal string")
    try:
        parsed = Decimal(value)
    except InvalidOperation:
        raise PolicyError(f"{where} must be a positive decimal string") from None
    if parsed <= 0:
        raise PolicyError(f"{where} must be a positive decimal string")
    return value


def _reads(raw: Any) -> ReadsConfig:
    if not isinstance(raw, Mapping):
        raise PolicyError("credits.reads must be an object")
    return ReadsConfig(
        reads_per_credit=_positive_int(raw, "reads_per_credit", where="credits.reads"),
        daily_cap=_positive_int(raw, "daily_cap", where="credits.reads"),
        burst_limit=_positive_int(raw, "burst_limit", where="credits.reads"),
    )


def _x402_list(raw: Any) -> X402ListPrice:
    if not isinstance(raw, Mapping):
        raise PolicyError("x402 must be an object")
    return X402ListPrice(
        list_usd_per_decision=_decimal_str(
            raw.get("list_usd_per_decision"), "x402.list_usd_per_decision"),
    )


def _overage(raw: Any, price_id: str, kind: str) -> OverageConfig | None:
    if raw is None:
        return None
    where = f"billing.prices[{price_id!r}].overage"
    if kind != "plan":
        raise PolicyError(f"{where} is only valid on a plan")
    if not isinstance(raw, Mapping):
        raise PolicyError(f"{where} must be an object")
    price = str(raw.get("price_id") or "")
    event = str(raw.get("meter_event") or "")
    if not price or not event:
        raise PolicyError(f"{where} must set price_id and meter_event")
    return OverageConfig(
        usd_per_credit=_decimal_str(raw.get("usd_per_credit"), f"{where}.usd_per_credit"),
        cap_credits=_positive_int(raw, "cap_credits", where=where),
        price_id=price,
        meter_event=event,
        placeholder=bool(raw.get("placeholder", False)),
    )


def _check_overage_rates(prices: Mapping[str, PriceMapping]) -> None:
    """Overage sits above this plan's included rate and below every other current plan.

    Legacy plans are not part of the comparison: their rates are the prices
    existing customers already hold, and a new overage rate is not required
    to undercut them.
    """
    current = [row for row in prices.values()
               if row.kind == "plan" and not row.legacy and row.credits > 0 and row.usd > 0]
    for row in prices.values():
        if row.overage is None:
            continue
        rate = row.overage.rate()
        included = Decimal(row.usd) / Decimal(row.credits)
        if rate <= included:
            raise PolicyError(
                f"billing.prices[{row.price_id!r}].overage rate {rate} must be "
                f"above the plan's included rate {included}")
        for other in current:
            if other.price_id == row.price_id:
                continue
            other_rate = Decimal(other.usd) / Decimal(other.credits)
            if rate >= other_rate:
                raise PolicyError(
                    f"billing.prices[{row.price_id!r}].overage rate {rate} must be "
                    f"below {other.name}'s included rate {other_rate}")


def overage_for(policy: AccessPolicy, plan: str,
                customer_id: str | None = None) -> tuple[int, OverageConfig | None]:
    """Cap and overage row for a current plan of this name.

    The cap is 0 while the overage Price is a placeholder, so a Scale key
    stops at zero until that Price is configured. Passing a blank
    `customer_id` also returns 0: overage that cannot be billed is not granted.
    Omit `customer_id` to read the table cap alone. The cap is read from the
    current table, not stored on the account.
    """
    if not plan:
        return 0, None
    for row in policy.billing.prices.values():
        if (row.kind == "plan" and not row.legacy and row.name == plan
                and row.overage is not None):
            if row.overage.placeholder:
                return 0, row.overage
            if customer_id is not None and not str(customer_id).strip():
                return 0, row.overage
            return row.overage.cap_credits, row.overage
    return 0, None


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
