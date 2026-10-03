"""Registry-backed examples for invalid decision requests (MODEL-285)."""

from __future__ import annotations

import difflib
import json
from typing import Any, Callable

from pydantic import BaseModel, Field

from decision.contract import Issue, Spec, parse_spec
from decision.registry import Facet, default


class Recovery(BaseModel):
    path: str
    accepted_shape: str
    example: dict[str, Any]
    guidance: str
    nearest_facet_ids: list[str] = Field(default_factory=list)


def minimal_spec() -> dict[str, Any]:
    """Pick an addressable numeric model facet, without maintaining another ID list."""
    numeric = next(f for f in default().facets() if f.addressable
                   and f.subject == "model" and f.parameter is None
                   and f.value_type.kind == "number")
    return {"spec_version": 1, "optimize": {"max": numeric.id}}


def _condition(info: Facet) -> tuple[dict[str, Any], str]:
    kind = info.value_type.kind
    if kind == "number":
        return {"facet": info.id, "op": ">=", "value": 1}, "a JSON number"
    if kind == "boolean":
        return {"facet": info.id, "op": "=", "value": True}, "a JSON boolean, true or false"
    values = default().allowed_values(info)
    if kind in {"enum", "set"} and values:
        value = sorted(values)[0]
        shape = "a registered string value" if kind == "enum" else "an array of registered string values"
        condition = ({"facet": info.id, "op": "=", "value": value} if kind == "enum"
                     else {"facet": info.id, "in": [value]})
        return condition, shape
    # A known condition works even for an open vocabulary or a range facet.
    return {"known": info.id}, f"a {kind} value, or a known condition"


def recovery_hints(issues: list[Issue], *, facets: Callable[[str], Facet],
                   benchmark_ids: tuple[str, ...] = (), payload: Any = None) -> list[dict[str, Any]]:
    """Each hint is a standalone valid spec, never a copy of the rejected request."""
    registry = default()
    known = [f.id for f in registry.facets() if f.addressable and f.parameter is None]
    known.extend(d.id for d in registry.domains())
    known.extend(benchmark_ids)
    hints = []
    for issue in issues:
        example = minimal_spec()
        path = "$" + ("." + issue.path if issue.path else "")
        shape = "a Spec object with spec_version: 1 and exactly one optimize objective"
        guidance = "Use the minimal example, then add structured requirements from vocab section=starter."
        nearest: list[str] = []
        info = None
        if issue.field:
            try:
                info = facets(issue.field.lstrip("-"))
            except KeyError:
                pass
        if issue.reason.startswith("unknown facet ") and issue.field:
            nearest = difflib.get_close_matches(issue.field, sorted(set(known)), n=3, cutoff=0.6)
            if nearest:
                info = facets(nearest[0])
            shape = "a valid facet ID from vocab section=starter"
            guidance = "Look up the suggested IDs in vocab before choosing the facet that matches your requirement."
        if info is not None and info.addressable:
            condition, value_shape = _condition(info)
            example["where"] = [condition]
            if not nearest:
                shape = f"a condition on {info.id} using {value_shape}"
                guidance = "Use a structured condition object. Text sets use {a, b}; [low, high] is a numeric or date window."
            if issue.path.startswith("optimize"):
                kind = info.value_type.kind
                if kind in {"number", "range"}:
                    example.pop("where")
                    example["optimize"] = {"weights": {info.id: 1}}
                    shape = "a numeric weight for a numeric facet"
                elif kind in {"boolean", "enum"} and (kind == "boolean" or info.preference_values):
                    example.pop("where")
                    prefer = True if kind == "boolean" else sorted(info.preference_values)[0]
                    example["optimize"] = {"weights": {info.id: {"prefer": prefer, "weight": 1}}}
                    shape = f"a preference object with prefer as {value_shape} and weight as a positive number"
                else:
                    shape = "a where condition; this facet cannot be used as an ordered objective"
                guidance = "Numeric facets take numeric weights; boolean and enum facets take {prefer, weight}. Musts go in where."
        if issue.path == "optimize.weights" and issue.field and issue.field != issue.path:
            key = issue.field
            objective = payload.get("optimize") if isinstance(payload, dict) else None
            weights = objective.get("weights") if isinstance(objective, dict) else None
            if isinstance(weights, dict) and key not in weights and "-" + key in weights:
                key = "-" + key
            path += "[" + json.dumps(key) + "]"
            if issue.reason == "a boolean preference needs true or false" or issue.reason.startswith("preferred value "):
                path += ".prefer"
        if issue.path == "task":
            shape = "structured facets in where and optimize, with optional task_type and capabilities"
            guidance = ("decide takes structured facets only. Translate the request into facets via "
                        "vocab section=starter, then remove task and retry. It does not evaluate an exact prompt.")
        elif issue.path == "where":
            shape = "an array of condition strings or structured condition objects"
            example["where"] = [{"known": example["optimize"]["max"]}]
        elif issue.path == "optimize" and info is None:
            shape = "an object with exactly one of max, min, weights, lexicographic or pareto"
        elif issue.path == "optimize.weights" and info is None and issue.field == issue.path:
            shape = "an object mapping numeric facet IDs to numeric weights, or boolean/enum facet IDs to {prefer, weight}"
        elif issue.path.startswith("capabilities"):
            domain = sorted(registry.domains(), key=lambda d: d.id)[0].id
            shape = 'an object mapping domain IDs to "required" or "preferred"'
            example["capabilities"] = {domain: "required"}
        elif issue.path.startswith("task_tokens"):
            shape = "an object with nonnegative integer input and output token counts"
            example["task_tokens"] = {"input": 1, "output": 1}
        elif issue.reason == "not a spec field":
            shape = "one of the Spec fields: " + ", ".join(Spec.model_fields)
            guidance = "Remove this field. Translate requirements into facets via vocab section=starter."
        # Guard the public recovery contract against registry changes as well as mistakes here.
        parse_spec(example, facets=facets)
        hints.append(Recovery(path=path, accepted_shape=shape, example=example,
                              guidance=guidance, nearest_facet_ids=nearest).model_dump())
    return hints
