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
* ``models``: every lineup and archive model, by ID, with the ``display_name``
  and lab (``lab``, ``lab_name``) its card gives. A name the card does not
  give is ``null``; a client shows the ID, never a name made from the slug.
* ``providers``: every registered provider's display name, by ID.
* ``coverage``: what the lineup holds, so a client can say what an empty
  answer was measured against without writing it per question. ``models`` is
  the lineup size and ``verified`` how many of those have at least one verified
  evidence row; ``as_of`` is the snapshot date. ``classes`` lists every
  registered model class (zeros included) with the same two counts and, per
  domain, how many of its models have verified evidence there. ``domains``
  lists every registered domain with how many lineup models have verified
  evidence on any benchmark tagged to it (``verified``) and on a direct one
  (``direct``).

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
        row["values"] = [
            {"value": v, "count": counts[v],
             **({"label": label} if isinstance(v, str) and (label := facet.value_label(v))
                else {})}
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


def _model_rows(snapshot: Any, cards: Mapping[str, Mapping[str, Any]],
                ) -> dict[str, dict[str, Any]]:
    rows = {}
    for mid in sorted({snapshot.model_of(cid) for cid in snapshot.candidates()}):
        card = cards.get(mid) or {}
        rows[mid] = {
            "display_name": card.get("display_name") or None,
            "lab": card.get("provider") or mid.split("/", 1)[0],
            "lab_name": card.get("provider_display") or None,
        }
    return rows


def _coverage(snapshot: Any, lineup: list[str], registry: Any) -> dict[str, Any]:
    tags = snapshot.benchmark_domain_tags()
    class_of: dict[str, Any] = {}
    for cid in lineup:
        if snapshot.kind(cid) == "model":
            class_of[snapshot.model_of(cid)] = snapshot.fact(cid, "model.class").value
    verified: dict[str, set[str]] = {}  # model -> benchmarks with a verified row
    for cid in lineup:
        for benchmark in snapshot.benchmark_ids():
            if any(e.verified for e in snapshot.evidence(cid, benchmark)):
                verified.setdefault(snapshot.model_of(cid), set()).add(benchmark)

    def in_domain(mid: str, domain: str, *, direct: bool = False) -> bool:
        return any(d == domain and (not direct or k == "direct")
                   for b in verified.get(mid, ()) for d, k in tags.get(b, ()))

    domains = registry.domains()
    classes = []
    for class_id in sorted(registry.allowed_values(registry.facet("model.class")) or ()):
        members = [mid for mid, cls in class_of.items() if cls == class_id]
        per_domain = [{"id": d.id, "verified": n} for d in domains
                      if (n := sum(in_domain(mid, d.id) for mid in members))]
        classes.append({
            "id": class_id,
            "models": len(members),
            "verified": sum(mid in verified for mid in members),
            "domains": sorted(per_domain, key=lambda row: (-row["verified"], row["id"])),
        })
    return {
        "as_of": snapshot.as_of.isoformat() if snapshot.as_of else None,
        "models": len(class_of),
        "verified": sum(mid in verified for mid in class_of),
        "classes": classes,
        "domains": [{
            "id": d.id,
            "name": d.name,
            "verified": sum(in_domain(mid, d.id) for mid in class_of),
            "direct": sum(in_domain(mid, d.id, direct=True) for mid in class_of),
        } for d in domains],
    }


def build_vocabulary(snapshot: Any, *, pages: Mapping[str, Mapping[str, Any]] | None = None,
                     registry: Any = None, cards: Mapping[str, Mapping[str, Any]] | None = None,
                     ) -> dict[str, Any]:
    """The vocabulary of ``snapshot``. ``pages`` maps benchmark IDs to their page
    front matter (for names and metric direction); ``cards`` maps model IDs to
    their card front matter (for display and lab names); ``registry`` defaults
    to the repository's own. Load ``snapshot`` with its archive to name
    archived models too."""
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
        "models": _model_rows(snapshot, cards or {}),
        "providers": {p.id: p.name for p in registry.providers()},
        "coverage": _coverage(view, lineup, registry),
    }
