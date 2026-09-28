"""Compare two decisions for the same spec, grouped by model."""

from __future__ import annotations

from collections import defaultdict
from typing import Any

from decision.contract import Compare, Decision, InSet, Known, Window, parse_condition


def _offering_key(offering: Any) -> tuple[Any, ...]:
    return (offering.provider, offering.region, offering.tier)


def _ranked(decision: Decision) -> dict[str, dict[str, Any]]:
    grouped: dict[str, dict[str, Any]] = {}
    for row in decision.results:
        model = row.offering.model
        item = grouped.setdefault(model, {"rank": row.rank, "rows": []})
        item["rank"] = min(item["rank"], row.rank)
        item["rows"].append(row)
    return grouped


def _may_qualify(decision: Decision) -> dict[str, list[str]]:
    unknown: dict[str, set[str]] = defaultdict(set)
    for row in decision.may_qualify:
        unknown[row.model].update(row.unknown)
    return {model: sorted(values) for model, values in unknown.items()}


def _values(decision: Decision) -> dict[str, dict[tuple[Any, ...], dict[str, Any]]]:
    values: dict[str, dict[tuple[Any, ...], dict[str, Any]]] = defaultdict(dict)
    facts = {
        (row.offering.model, _offering_key(row.offering)): row.facts
        for row in decision.top
    }
    for row in decision.results:
        model = row.offering.model
        offering = _offering_key(row.offering)
        for contribution in row.contributions:
            facet = contribution.dimension.removeprefix("-")
            if facet != "offering.cost_per_task":
                continue
            values[model][("cost_per_task", offering)] = {
                "kind": "cost_per_task",
                "offering": row.offering.model_dump(mode="json"),
                "value": contribution.raw_value,
                "unit": contribution.unit,
                "records": contribution.records,
            }
        for estimate in row.estimates or []:
            records = sorted({
                item.record_id
                for group in row.evidence
                if group.domain == estimate.domain
                for item in group.items
                if item.record_id is not None
            })
            values[model][("capability", offering, estimate.domain)] = {
                "kind": "capability",
                "domain": estimate.domain,
                "offering": row.offering.model_dump(mode="json"),
                "value": estimate.value,
                "interval": list(estimate.interval),
                "records": records,
            }
        for fact in facts.get((model, offering), []):
            records = [fact.record_id] if fact.record_id else list(fact.records)
            if fact.facet == "offering.cost_per_task":
                values[model][("cost_per_task", offering)] = {
                    "kind": "cost_per_task",
                    "offering": row.offering.model_dump(mode="json"),
                    "value": fact.value,
                    "unit": fact.unit,
                    "records": records,
                }
                continue
            if fact.facet.startswith("offering.price."):
                continue
            values[model][("facet", offering, fact.facet)] = {
                "kind": "facet",
                "facet": fact.facet,
                "offering": row.offering.model_dump(mode="json"),
                "value": fact.value,
                "unit": fact.unit,
                "records": records,
            }
    for row in decision.eliminated.models:
        if row.offering is None or row.value is None and not row.values:
            continue
        facet = _condition_facet(row.condition)
        if facet is None:
            continue
        offering = _offering_key(row.offering)
        values[row.model][("facet", offering, facet)] = {
            "kind": "facet",
            "facet": facet,
            "offering": row.offering.model_dump(mode="json"),
            "value": row.values or row.value,
            "unit": row.unit,
            "records": row.records,
        }
    for row in decision.may_qualify:
        if row.offering is None:
            continue
        offering = _offering_key(row.offering)
        for facet in row.unknown:
            values[row.model].setdefault(("facet", offering, facet), {
                "kind": "facet",
                "facet": facet,
                "offering": row.offering.model_dump(mode="json"),
                "value": None,
                "unit": None,
                "records": [],
            })
    return values


def _condition_facet(condition: str) -> str | None:
    """Return the one facet named by a leaf Must, or null for a compound Must."""
    text = condition.removesuffix(": unverified: may qualify")
    try:
        parsed = parse_condition(text)
    except ValueError:
        return None
    if isinstance(parsed, Known):
        return parsed.known
    if isinstance(parsed, Compare | Window | InSet):
        return parsed.facet
    return None


def _left_reason(decision: Decision, model: str) -> str:
    reasons = [row.condition for row in decision.eliminated.models if row.model == model]
    must = [reason for reason in reasons
            if not reason.startswith(("dominated by ", "outside requested result limit"))]
    return (must or reasons or ["no longer in the lineup"])[0]


def _measured_value(value: dict[str, Any]) -> dict[str, Any]:
    """The underlying value, excluding provenance that may rotate unchanged."""
    return {key: item for key, item in value.items() if key != "records"}


def _dimension(key: tuple[Any, ...]) -> tuple[Any, ...]:
    """A compared value's identity apart from the selected offering."""
    return (key[0], *key[2:])


def _value_change(before: dict[str, Any], after: dict[str, Any]) -> dict[str, Any]:
    offering: Any = after.get("offering")
    if before.get("offering") != offering:
        offering = {"old": before.get("offering"), "new": offering}
    return {
        "kind": after["kind"],
        **{name: after[name] for name in ("facet", "domain") if name in after},
        **({"offering": offering} if offering is not None else {}),
        "old": {k: v for k, v in before.items()
                if k not in {"kind", "facet", "domain", "offering"}},
        "new": {k: v for k, v in after.items()
                if k not in {"kind", "facet", "domain", "offering"}},
    }


def compare(
    old: Decision,
    new: Decision,
    *,
    old_as_of: str | None = None,
    new_as_of: str | None = None,
) -> dict[str, Any]:
    """Return the deterministic model-grained difference between two decisions."""
    old_ranked, new_ranked = _ranked(old), _ranked(new)
    old_may, new_may = _may_qualify(old), _may_qualify(new)
    old_values, new_values = _values(old), _values(new)
    old_eliminated = {row.model for row in old.eliminated.models}
    new_eliminated = {row.model for row in new.eliminated.models}
    models = sorted(
        set(old_ranked) | set(new_ranked) | set(old_may) | set(new_may)
        | old_eliminated | new_eliminated
    )
    changes = []
    for model in models:
        entered = model in new_ranked and model not in old_ranked
        left = model in old_ranked and model not in new_ranked
        old_rank = old_ranked.get(model, {}).get("rank")
        new_rank = new_ranked.get(model, {}).get("rank")
        rank = ({"old": old_rank, "new": new_rank}
                if old_rank is not None and new_rank is not None and old_rank != new_rank else None)
        may = ({"old": old_may.get(model), "new": new_may.get(model)}
               if old_may.get(model) != new_may.get(model) else None)
        value_changes = []
        before_model = old_values.get(model, {})
        after_model = new_values.get(model, {})
        shared = set(before_model) & set(after_model)
        pairs = [(before_model[key], after_model[key]) for key in sorted(shared, key=str)]
        unmatched_before = [key for key in before_model if key not in shared]
        unmatched_after = [key for key in after_model if key not in shared]
        dimensions = (
            {_dimension(key) for key in unmatched_before}
            & {_dimension(key) for key in unmatched_after}
        )
        for dimension in sorted(dimensions, key=str):
            old_keys = [key for key in unmatched_before if _dimension(key) == dimension]
            new_keys = [key for key in unmatched_after if _dimension(key) == dimension]
            if len(old_keys) == len(new_keys) == 1:
                pairs.append((before_model[old_keys[0]], after_model[new_keys[0]]))
        for before, after in pairs:
            if _measured_value(before) != _measured_value(after):
                value_changes.append(_value_change(before, after))
        if entered or left or rank or may or value_changes:
            changes.append({
                "model": model,
                "entered": entered,
                "left": ({"reason": _left_reason(new, model)} if left else None),
                "rank_changed": rank,
                "may_qualify": may,
                "values": value_changes,
            })
    counts = {
        "entered": sum(row["entered"] for row in changes),
        "left": sum(row["left"] is not None for row in changes),
        "rank_changed": sum(row["rank_changed"] is not None for row in changes),
        "may_qualify_changed": sum(row["may_qualify"] is not None for row in changes),
        "models_changed": len(changes),
    }
    return {
        "changed": bool(changes),
        "snapshot": {
            "old": {"id": old.snapshot, "as_of": old_as_of},
            "new": {"id": new.snapshot, "as_of": new_as_of},
        },
        "status": {"old": old.status, "new": new.status},
        "counts": counts,
        "models": changes,
    }
