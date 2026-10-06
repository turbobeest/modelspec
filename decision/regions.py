"""Provider region names and the countries they guarantee.

An offering's identity keeps the provider's region name
(``offering.provider`` / ``offering.region`` / ``offering.tier``).
A residency condition asks which countries that name guarantees.
A name that guarantees none is unknown: never a pass, never a hard fail.
"""

from __future__ import annotations

import re
from collections.abc import Iterable

# The registry's open ISO check (decision.registry.COUNTRY). Duplicated so
# this module does not import the registry.
_ALPHA2 = re.compile(r"^[A-Z]{2}$")

_MEMBERSHIP = frozenset({"contains", "contains_all", "contains_any", "in", "not_in"})

#: ``None`` means the name is known and guarantees no country.
PROVIDER_REGIONS: dict[str, frozenset[str] | None] = {
    "global": None,
    "global-cross-region": None,
    "global-short-context": None,
    "singapore": frozenset({"SG"}),
}


def is_alpha2(value: str) -> bool:
    return _ALPHA2.fullmatch(value) is not None


def is_global_variant(name: str) -> bool:
    """``global`` and ``global-*``. ``globalfoo`` is not a variant."""
    return name == "global" or name.startswith("global-")


def accepted_identity_region(region: str) -> bool:
    return region in PROVIDER_REGIONS or is_global_variant(region) or is_alpha2(region)


def require_identity_region(region: str) -> None:
    if not accepted_identity_region(region):
        raise ValueError(
            f"offering region {region!r} is not a registered region name "
            "or an ISO 3166-1 alpha-2 code"
        )


def identity_region(offering_id: str) -> str:
    """The region segment of ``provider/model/region/tier``.

    Model ids contain a slash, so the region is the second piece from the right.
    """
    parts = offering_id.rsplit("/", 2)
    if len(parts) != 3:
        return offering_id
    return parts[1]


def no_guarantee_reason(name: str) -> str:
    return f"provider region {name!r} does not guarantee where inference runs"


def countries_of(value: object) -> frozenset[str] | None:
    """Countries ``value`` guarantees, or ``None`` when it guarantees none.

    An empty country list is a known empty set, not an unknown.
    """
    if isinstance(value, str):
        if is_global_variant(value):
            return None
        if value in PROVIDER_REGIONS:
            return PROVIDER_REGIONS[value]
        if is_alpha2(value):
            return frozenset({value})
        return None
    if isinstance(value, list | tuple):
        codes: list[str] = []
        for item in value:
            if not isinstance(item, str) or not is_alpha2(item):
                return None
            codes.append(item)
        return frozenset(codes)
    return None


def guarantees_countries(value: object) -> bool:
    return countries_of(value) is not None


def is_membership_op(op: str) -> bool:
    return op in _MEMBERSHIP


def _wanted(arg: object) -> frozenset[str]:
    if isinstance(arg, str):
        return frozenset({arg})
    if isinstance(arg, Iterable):
        return frozenset(str(item) for item in arg)
    return frozenset({str(arg)})


def region_matches(countries: frozenset[str], op: str, arg: object) -> bool:
    """Whether ``countries`` satisfies a residency membership test."""
    if op == "contains":
        return isinstance(arg, str) and arg in countries
    if op in ("contains_any", "in"):
        return bool(countries & _wanted(arg))
    if op == "contains_all":
        return _wanted(arg) <= countries
    if op == "not_in":
        return not (countries & _wanted(arg))
    raise ValueError(f"not a region membership operator: {op!r}")
