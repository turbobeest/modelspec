"""Load data-defined partial decision specs from ``registry/templates.yaml``."""

from __future__ import annotations

import re
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import yaml

from decision.contract import SpecError, parse_spec
from decision.registry import REGISTRY_DIR, RegistryError, default
from decision.resolve import resolve

TEMPLATES_PATH = REGISTRY_DIR / "templates.yaml"
_ID = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def _mapping(value: Any, path: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise RegistryError(f"{path} must be a mapping")
    return value


def _text(value: Any, path: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise RegistryError(f"{path} must be a non-empty string")
    return value


def _expanded(row: Mapping[str, Any], *, registry: Any) -> dict[str, Any]:
    template_id = _text(row.get("id"), "templates[].id")
    if _ID.fullmatch(template_id) is None:
        raise RegistryError(f"template id {template_id!r} must be a lowercase kebab-case id")

    where_rows = row.get("where")
    if not isinstance(where_rows, list):
        raise RegistryError(f"template {template_id}: where must be a list")
    where = []
    for index, raw in enumerate(where_rows):
        item = _mapping(raw, f"template {template_id}.where[{index}]")
        where.append({
            "condition": _text(
                item.get("condition"), f"template {template_id}.where[{index}].condition"
            ),
            "reason": _text(item.get("reason"), f"template {template_id}.where[{index}].reason"),
        })

    weight_rows = _mapping(row.get("weights"), f"template {template_id}.weights")
    weights: dict[str, dict[str, Any]] = {}
    for facet_id, raw in weight_rows.items():
        item = _mapping(raw, f"template {template_id}.weights.{facet_id}")
        weight = item.get("weight")
        if isinstance(weight, bool) or not isinstance(weight, int | float) or weight <= 0:
            raise RegistryError(f"template {template_id}: weight for {facet_id} must be positive")
        weights[str(facet_id)] = {
            "weight": float(weight),
            "reason": _text(
                item.get("reason"), f"template {template_id}.weights.{facet_id}.reason"
            ),
        }

    needs = _mapping(row.get("needs"), f"template {template_id}.needs")
    classes = needs.get("classes")
    domains = needs.get("domains")
    if not isinstance(classes, list) or not all(isinstance(item, str) for item in classes):
        raise RegistryError(f"template {template_id}: needs.classes must be a list of ids")
    if not isinstance(domains, list) or not all(isinstance(item, str) for item in domains):
        raise RegistryError(f"template {template_id}: needs.domains must be a list of ids")
    allowed_classes = registry.allowed_values(registry.facet("model.class")) or frozenset()
    for class_id in classes:
        if class_id not in allowed_classes:
            raise RegistryError(f"template {template_id}: unknown model class {class_id!r}")
    for domain_id in domains:
        registry.domain(domain_id)

    spec: dict[str, Any] = {
        "spec_version": 1,
        "where": [item["condition"] for item in where],
        "optimize": {"weights": {
            facet_id: item["weight"] for facet_id, item in weights.items()
        }},
    }
    if "task_tokens" in row:
        spec["task_tokens"] = row["task_tokens"]
    try:
        resolve(parse_spec(spec, facets=registry.facet), facets=registry.facet)
    except SpecError as exc:
        raise RegistryError(f"template {template_id}: {exc}") from exc

    return {
        "id": template_id,
        "name": _text(row.get("name"), f"template {template_id}.name"),
        "purpose": _text(row.get("purpose"), f"template {template_id}.purpose"),
        "where": where,
        "weights": weights,
        **({"task_tokens": spec["task_tokens"]} if "task_tokens" in spec else {}),
        "needs": {"classes": list(classes), "domains": list(domains)},
        "teaches": _text(row.get("teaches"), f"template {template_id}.teaches"),
        "spec": spec,
    }


def load_templates(path: Path = TEMPLATES_PATH, *, registry: Any = None) -> list[dict[str, Any]]:
    """Return validated templates in registry order."""
    registry = registry or default()
    try:
        document = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise RegistryError(f"cannot load {path}: {exc}") from exc
    root = _mapping(document, str(path))
    if root.get("schema_version") != 1:
        raise RegistryError(f"{path}: schema_version must be 1")
    rows = root.get("templates")
    if not isinstance(rows, list):
        raise RegistryError(f"{path}: templates must be a list")
    templates = [_expanded(_mapping(row, "templates[]"), registry=registry) for row in rows]
    ids = [row["id"] for row in templates]
    if len(ids) != len(set(ids)):
        raise RegistryError(f"{path}: template ids must be unique")
    return templates


def template_by_id(
    template_id: str, templates: list[dict[str, Any]] | None = None
) -> dict[str, Any]:
    """Return one template or raise an error that names every valid id."""
    rows = templates if templates is not None else load_templates()
    for row in rows:
        if row["id"] == template_id:
            return row
    valid = ", ".join(row["id"] for row in rows)
    raise ValueError(f"unknown template {template_id!r}; valid ids: {valid}")
