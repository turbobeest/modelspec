"""Names and definitions for drawing /decide, without catalogue statistics."""
from __future__ import annotations

FACET_FIELDS = ("id", "label", "definition", "subject", "value_type", "unit", "unit_definition",
                "operators", "objective", "preference", "risk", "computed_by", "literals")
BENCHMARK_FIELDS = ("id", "name", "unit", "higher_is_better", "domains")
DOMAIN_FIELDS = ("id", "name", "proxy_only", "default_basis", "default_benchmark", "benchmarks")
TEMPLATE_FIELDS = ("id", "category", "tier", "tradeoff", "canvas", "name", "purpose", "where",
                   "weights", "task_tokens", "needs", "teaches", "spec", "available")


def pick(row, fields):
    return {key: row[key] for key in fields if key in row}


def trim(vocabulary, *, model_ids, facet_values):
    """Project explicit display fields. Only approved aggregates cross this boundary."""
    result = pick(vocabulary, ("vocabulary_version", "contract_version", "snapshot", "default_task_tokens",
                               "task_types", "providers", "vendors", "template_categories", "template_tiers"))
    result["facets"] = [pick(row, FACET_FIELDS) for row in vocabulary.get("facets", [])]
    for row, source in zip(result["facets"], vocabulary.get("facets", [])):
        row["has_data"] = source.get("known", 0) > 0
        observed = {item["value"]: item for item in source.get("values", [])}
        values = facet_values.get(row["id"], list(observed)) if source.get("value_type") in {"enum", "boolean", "set", "string"} else []
        if values:
            row["values"] = [dict(pick(observed.get(value, {"value": value}), ("value", "label")),
                                  has_data=observed.get(value, {}).get("count", 0) > 0)
                             for value in values]
    result["benchmarks"] = [pick(row, BENCHMARK_FIELDS + (("range",) if row.get("models", 0) >= 3 else ()))
                            for row in vocabulary.get("benchmarks", [])]
    result["refinements"] = [dict(pick(row, ("id", "name", "parent_domain", "kind", "definition", "benchmarks", "weight_key")),
                                  thin=row.get("evidence_state") == "thin")
                             for row in vocabulary.get("refinements", [])]
    result["domains"] = [pick(row, DOMAIN_FIELDS) for row in vocabulary.get("domains", [])]
    result["models"] = {mid: {"display_name": row.get("display_name")} for mid, row in
                        vocabulary.get("models", {}).items() if mid in model_ids}
    estate = vocabulary.get("estate", {})
    result["estate"] = {"providers": estate.get("providers", []), "devices": estate.get("devices", []),
                        "plans": [pick(row, ("id", "provider", "name")) for row in estate.get("plans", [])]}
    result["templates"] = [pick(row, TEMPLATE_FIELDS) for row in vocabulary.get("templates", [])]
    return result
