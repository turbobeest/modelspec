"""Fingerprint and compare continuations against the immutable primary Spec."""
from __future__ import annotations

import hashlib
import json

from decision import contract, registry


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                     ensure_ascii=False).encode()).hexdigest()


def fingerprint(raw):
    try:
        spec = contract.parse_spec(json.loads(raw), facets=None)
    except (ValueError, TypeError):
        # A malformed primary still spends admission, but buys no auxiliaries.
        return None
    data = json.loads(contract.canonical_json(spec))
    where = data.pop("where")
    objective = data.pop("optimize")
    capabilities = data.pop("capabilities", None)
    estate = data.pop("estate", None)
    data.pop("explain")
    data.pop("limit")
    conditions = [digest(condition) for condition in where]
    return {
        "fixed": digest(data), "where": sorted(conditions),
        "optimize": digest(objective), "capabilities": digest(capabilities),
        "estate": digest(estate), "no_estate": estate is None,
        "estate_allowed": spec.estate is not None and not spec.estate.exhausted,
        "plot": is_plot(spec),
    }


def is_plot(spec):
    """The exact canvasPlotSpec transformation: at most two numeric axes."""
    if spec.where or spec.explain != "full" or spec.limit != 500:
        return False
    weights = spec.optimize.weights
    if not weights or len(weights) > 2 or spec.optimize.qualifiers:
        return False
    for key, weight in weights.items():
        if weight != 1 / len(weights):
            return False
        try:
            registry.domain(key)
        except registry.UnknownIdError:
            try:
                if registry.facet(key.removeprefix("-")).value_type.kind != "number":
                    return False
            except registry.UnknownIdError:
                return False
    capabilities = spec.capabilities or {}
    return len(capabilities) <= 2 and all(
        level == "preferred" and domain in weights
        for domain, level in capabilities.items())


def derivation(primary, next_spec):
    if primary is None or next_spec is None or primary["fixed"] != next_spec["fixed"]:
        return None
    same_objective = all(primary[key] == next_spec[key]
                         for key in ("optimize", "capabilities"))
    same_where = primary["where"] == next_spec["where"]
    same_estate = primary["estate"] == next_spec["estate"]
    if same_objective and same_estate and same_where:
        return "same"
    if same_objective and same_where and primary["no_estate"] and next_spec["estate_allowed"]:
        return "estate"
    if same_estate and next_spec["plot"]:
        return "plot"
    return None
