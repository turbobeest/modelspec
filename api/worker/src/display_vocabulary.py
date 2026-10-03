"""Names and definitions for drawing /decide, without catalogue statistics."""
from __future__ import annotations

import json
import re
from collections import Counter
from copy import deepcopy

try:
    from agent_guide import MINIMAL_SPEC, VOCAB_NEXT
except ImportError:
    from .agent_guide import MINIMAL_SPEC, VOCAB_NEXT

SECTIONS = ("starter", "facets", "benchmarks", "domains", "providers", "models",
            "task_types", "coverage", "templates", "refinements", "estate", "vendors",
            "template_categories", "template_tiers")
PAGE_SIZE = 20

FACET_FIELDS = ("id", "label", "definition", "subject", "value_type", "unit", "unit_definition",
                "operators", "objective", "preference", "better", "risk", "computed_by", "literals")
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


MAX_IDS = 100


def vocabulary_response(selected, section):
    result = {section: selected, "next": VOCAB_NEXT["starter" if section == "starter" else "lookup"]}
    if section == "starter":
        result["spec"] = deepcopy(MINIMAL_SPEC)
    return result


def starter_ids(vocabulary):
    """Count each registered facet once per template spec; break ties by ID."""
    counts = Counter()
    for template in vocabulary.get("templates", []):
        spec = json.dumps(template.get("spec") or {})
        counts.update(row["id"] for row in vocabulary.get("facets", [])
                      if re.search(r"(?<![\w.])" + re.escape(row["id"]) + r"(?![\w.])", spec))
    return sorted(counts, key=lambda fid: (-counts[fid], fid))[:15]


def lookup(vocabulary, *, section="starter", search="", ids=(), detail="compact",
           offset=0, limit=PAGE_SIZE):
    """An opt-in lookup. Full detail stays inside the existing display boundary."""
    if section not in SECTIONS:
        raise ValueError("unknown vocabulary section")
    if detail not in {"compact", "full"}:
        raise ValueError("detail must be compact or full")
    if offset < 0 or not 1 <= limit <= PAGE_SIZE:
        raise ValueError("offset must be nonnegative; limit must be between 1 and 20")
    ids = set(ids)
    if len(ids) > MAX_IDS:
        raise ValueError(f"at most {MAX_IDS} ids per lookup")
    source = vocabulary.get(section, {} if section in {"models", "providers", "vendors", "coverage", "estate"} else [])
    if section == "coverage" and detail == "compact" and not ids:
        return vocabulary_response({}, section)
    if section == "estate" and detail == "compact" and not ids:
        source = {key: vocabulary.get("estate", {}).get(key, []) for key in ("providers", "devices")}
    if section == "starter":
        by_id = {row["id"]: row for row in vocabulary.get("facets", [])}
        source = [by_id[fid] for fid in starter_ids(vocabulary)]
    mapping = isinstance(source, dict)
    if mapping:
        rows = [(key, value) for key, value in source.items()]
    else:
        rows = [(row.get("id", "") if isinstance(row, dict) else row, row) for row in source]

    def matches(key, row):
        label = row.get("label", row.get("name", row.get("display_name", ""))) if isinstance(row, dict) else row
        return (not ids or key in ids) and (not search or search.lower() in str(key).lower()
                                           or search.lower() in str(label if label is not None else "").lower())

    rows = [(key, row) for key, row in rows if matches(key, row)]
    full = detail == "full" or bool(ids)
    if not full:
        rows = rows[offset:offset + limit]

    def compact(row):
        if section in {"facets", "starter"}:
            result = pick(row, ("id", "label", "definition", "value_type", "better", "literals"))
            if isinstance(result.get("definition"), str):
                result["definition"] = re.split(r"\.\s", " ".join(result["definition"].split()))[0].rstrip(".") + "."
            if "allowed_values" in row:
                result["allowed_values"] = row["allowed_values"]
            elif "values" in row:
                result["allowed_values"] = [value["value"] for value in row["values"]]
            return result
        if section == "models":
            return pick(row, ("display_name",))
        if isinstance(row, dict):
            return pick(row, ("id", "name", "label"))
        return row

    selected = [(key, row if full else compact(row)) for key, row in rows]
    return vocabulary_response(dict(selected) if mapping else [row for _, row in selected], section)
