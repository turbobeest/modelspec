"""The decision vocabulary: what a spec can name, as data (MODEL-153).

The site build writes it to ``/api/decision/vocabulary.json`` beside the
decision snapshot it describes, so a client (the decide page) never carries a
list of facets or benchmarks of its own:

* ``facets``: every registered facet except the parameterised families
  (``evidence.benchmark`` and the like, whose members are the benchmarks
  below), with its label, unit, subject, value type, the condition operators
  that type admits, whether it can be an objective, and how much of the
  snapshot's lineup knows it (``known`` of ``of``), with the values or the
  range it takes there. A facet no lineup candidate knows is listed with
  ``known: 0``; a client should not offer it.
* ``benchmarks``: every benchmark with verified evidence in the snapshot, with
  its name, unit, domains and directness, how many lineup models have a
  verified row (``models``), how many have one not reported by their own lab
  (``independent_models``), and the range of those values. A benchmark with
  none is not listed.
* ``domains``: every registered domain with a listed benchmark, its
  benchmarks ordered direct first, then by how many models they cover.

Operators are the compact condition forms: ``=``, ``!=``, ``<``, ``<=``,
``>``, ``>=``, ``between`` (``facet in [low, high]``), ``in`` and ``not in``
(``facet in {a, b}``), and ``known`` (``known(facet)``).
"""

from __future__ import annotations

import typing
from collections import Counter
from collections.abc import Iterable, Mapping
from typing import Any

from decision.computed import with_computed
from decision.contract import CONTRACT_VERSION, DEFAULT_TASK_TOKENS, TaskType
from decision.filter import _INDEPENDENT as INDEPENDENT_MEASURERS

VOCABULARY_VERSION = 1

_ORDERED = ("=", "!=", "<", "<=", ">", ">=", "between")
OPERATORS: Mapping[str, tuple[str, ...]] = {
    "number": (*_ORDERED, "known"),
    "date": (*_ORDERED, "known"),
    "enum": ("=", "!=", "in", "not in", "known"),
    "boolean": ("=", "!=", "known"),
    "set": ("in", "not in", "known"),
}
_LITERALS = ("unbounded", "not_offered")


def _lineup(snapshot: Any) -> list[str]:
    return [cid for cid in snapshot.candidates() if snapshot.lifecycle(cid) != "retired"]


def _number(value: Any) -> float | None:
    if isinstance(value, bool) or not isinstance(value, int | float):
        return None
    return value


def _facet_row(facet: Any, snapshot: Any, subjects: Iterable[str], unit_definition: str | None,
               ) -> dict[str, Any]:
    kind = facet.value_type.kind
    subjects = list(subjects)
    values: list[Any] = []
    for cid in subjects:
        fact = snapshot.fact(cid, facet.id)
        if fact.state == "known" and fact.value is not None:
            values.append(fact.value)
    row: dict[str, Any] = {
        "id": facet.id,
        "label": facet.label or facet.id,
        "definition": facet.definition,
        "subject": facet.subject,
        "value_type": kind,
        "unit": facet.unit,
        "unit_definition": unit_definition,
        "operators": list(OPERATORS[kind]),
        "objective": kind == "number",
        "risk": facet.risk,
        "computed_by": facet.computed_by,
        "known": len(values),
        "of": len(subjects),
    }
    if kind == "number":
        numbers = [n for n in map(_number, values) if n is not None]
        row["range"] = {"min": min(numbers), "max": max(numbers)} if numbers else None
    elif kind == "date":
        dates = sorted(str(v) for v in values)
        row["range"] = {"min": dates[0], "max": dates[-1]} if dates else None
    if kind == "number":
        literals = sorted({v for v in values if v in _LITERALS})
        if literals:
            row["literals"] = literals
    elif kind in ("enum", "boolean", "set"):
        counts: Counter[Any] = Counter()
        for value in values:
            counts.update(set(value) if isinstance(value, list) else {value})
        row["values"] = [{"value": v, "count": counts[v]}
                         for v in sorted(counts, key=lambda v: (str(type(v)), str(v)))]
    return row


def _benchmark_rows(snapshot: Any, lineup: list[str], pages: Mapping[str, Mapping[str, Any]],
                    ) -> list[dict[str, Any]]:
    tags = snapshot.benchmark_domain_tags()
    rows = []
    for benchmark in snapshot.benchmark_ids():
        models: set[str] = set()
        independent: set[str] = set()
        units: Counter[str] = Counter()
        scores: list[float] = []
        for cid in lineup:
            found = [e for e in snapshot.evidence(cid, benchmark) if e.verified]
            if found:
                models.add(snapshot.model_of(cid))
                units.update(e.unit for e in found if e.unit)
                scores.extend(e.value for e in found)
            if any(e.measured_by in INDEPENDENT_MEASURERS for e in found):
                independent.add(snapshot.model_of(cid))
        if not models:
            continue
        page = pages.get(benchmark) or {}
        metric = page.get("metric") or {}
        unit = sorted(units.items(), key=lambda item: (-item[1], item[0]))[0][0] if units else None
        rows.append({
            "id": benchmark,
            "name": str(page.get("name") or benchmark),
            "unit": unit,
            "higher_is_better": metric.get("direction", "higher_is_better") != "lower_is_better",
            "models": len(models),
            "independent_models": len(independent),
            "range": {"min": min(scores), "max": max(scores)},
            "domains": [{"id": d, "directness": k} for d, k in tags.get(benchmark, ())],
        })
    return rows


def build_vocabulary(snapshot: Any, *, pages: Mapping[str, Mapping[str, Any]] | None = None,
                     registry: Any = None) -> dict[str, Any]:
    """The vocabulary of ``snapshot``. ``pages`` maps benchmark IDs to their page
    front matter (for names and metric direction); ``registry`` defaults to the
    repository's own."""
    if registry is None:
        from decision.registry import default

        registry = default()
    view = with_computed(snapshot, DEFAULT_TASK_TOKENS)
    lineup = _lineup(view)
    by_kind = {kind: [cid for cid in lineup if view.kind(cid) == kind]
               for kind in ("model", "offering")}
    facets = []
    for facet in registry.facets():
        if facet.parameter is not None:
            continue
        unit = registry.unit(facet.unit).definition if facet.unit else None
        facets.append(_facet_row(facet, view, by_kind[facet.subject], unit))
    benchmarks = _benchmark_rows(view, lineup, pages or {})
    covered = {row["id"]: row for row in benchmarks}
    domains = []
    for domain in registry.domains():
        members = [b for b in covered.values()
                   if any(tag["id"] == domain.id for tag in b["domains"])]
        if not members:
            continue

        def order(row: Mapping[str, Any], domain_id: str = domain.id) -> tuple[Any, ...]:
            direct = any(t == {"id": domain_id, "directness": "direct"} for t in row["domains"])
            return (not direct, -row["models"], row["id"])

        domains.append({
            "id": domain.id,
            "name": domain.name,
            "proxy_only": domain.proxy_only,
            "benchmarks": [row["id"] for row in sorted(members, key=order)],
        })
    return {
        "vocabulary_version": VOCABULARY_VERSION,
        "contract_version": CONTRACT_VERSION,
        "snapshot": snapshot.snapshot_id,
        "default_task_tokens": {"input": DEFAULT_TASK_TOKENS.input,
                                "output": DEFAULT_TASK_TOKENS.output},
        "task_types": list(typing.get_args(TaskType)),
        "facets": facets,
        "benchmarks": benchmarks,
        "domains": domains,
    }
