"""Which spec a domain means, for the post and the social cards (design §3.4).

``standings`` is the per-domain default-benchmark ranking the social generator
used; it moved here so the two share one definition of a domain's default.
``domain_spec`` is the spec a breakdown's domain standing reads: the model's
class, ranked by the domain's capability estimate. Only a weighted objective
returns an estimate, bands and P(best); a single-benchmark objective ranks
raw readings and returns none of them.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from decision.contract import Compare, Objective, Spec
from decision.engine import decide
from decision.registry import Domain
from decision.registry import default as default_registry
from decision.snapshot import LoadedSnapshot
from decision.vocabulary import build_vocabulary


def domain_spec(domain_id: str, model_class: str) -> dict[str, Any]:
    """The domain's default decision: one class, ranked by that domain's estimate."""
    return {
        "spec_version": 1,
        "where": [f"model.class = {model_class}"],
        "optimize": {"weights": {domain_id: 1.0}},
        "explain": "full",
        "limit": 500,
    }


@dataclass(frozen=True)
class Standing:
    snapshot: LoadedSnapshot
    domain: Domain
    benchmark: str
    higher_is_better: bool
    ordered_models: tuple[str, ...]
    results: Mapping[str, Any]
    decision: Any

    def rank(self, model_id: str) -> int | None:
        try:
            return self.ordered_models.index(model_id) + 1
        except ValueError:
            return None


def standings(snapshot: LoadedSnapshot, model_class: str) -> list[Standing]:
    """Each domain's ranking on its default benchmark, within ``model_class``."""
    registry = default_registry()
    vocabulary = build_vocabulary(snapshot, registry=registry)
    domain_rows = {row["id"]: row for row in vocabulary["domains"]}
    benchmark_rows = {row["id"]: row for row in vocabulary["benchmarks"]}
    rows: list[Standing] = []
    for domain in registry.domains():
        published = domain_rows.get(domain.id)
        if published is None or not published["benchmarks"]:
            continue
        benchmark = published["default_benchmark"] or published["benchmarks"][0]
        higher_is_better = bool(benchmark_rows[benchmark]["higher_is_better"])
        spec = Spec(
            spec_version=1,
            capabilities={domain.id: "required"},
            where=[Compare(facet="model.class", op="=", value=model_class)],
            optimize=Objective(**({"max": benchmark} if higher_is_better else {"min": benchmark})),
            explain="full",
            limit=500,
        )
        answer = decide(spec, snapshot, facets=registry.facet)
        ordered: list[str] = []
        results: dict[str, Any] = {}
        for result in answer.results:
            model_id = result.offering.model
            if model_id not in results:
                ordered.append(model_id)
                results[model_id] = result
        rows.append(
            Standing(
                snapshot,
                domain,
                benchmark,
                higher_is_better,
                tuple(ordered),
                results,
                answer,
            )
        )
    return rows
