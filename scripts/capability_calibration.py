"""Audit the calibration of the capability model's 80% intervals (MODEL-206).

The published domain estimate is a projection: each admitted measurement is
standardised within its benchmark and treated as the model's domain
capability plus noise. The noise variance of one fresh, direct measurement is
``_OBSERVATION_VARIANCE``; proxy tags and old evidence carry less precision.

Capability itself is never observed, so the audit checks what the model
predicts about data it has not seen. It holds out one model-benchmark cell at
a time, refits the benchmark's standardisation without it, estimates the
model's domain capability from the model's other measurements, and asks
whether the held-out standardised value falls inside the 80% *predictive*
interval, which adds that measurement's own noise to the estimate's spread.
If the noise variance is right, about 80% land inside at every evidence level.

It also reports the naive reading, how often the held-out value falls inside
the capability interval itself. That share must fall as evidence grows,
because one benchmark carries noise the capability interval does not.

Run: ``PYTHONPATH=$PWD python scripts/capability_calibration.py``. It writes
``docs/research/capability-interval-calibration.md`` and a JSON twin.
"""

from __future__ import annotations

import argparse
import json
import math
from collections import defaultdict
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

from decision import capability
from decision.capability import (
    BenchmarkSpec,
    CapabilityObservation,
    _item_zscores,
    _prepare,
    _projection_loading,
)

ROOT = Path(__file__).resolve().parents[1]
Z80 = 1.2815515655446004
#: A held-out cell needs this many other models on its benchmark, so the
#: benchmark can still be standardised without it.
MIN_TRAINING_MODELS = 3
#: The grids the two noise variances are fitted on.
WELL_GRID = tuple(round(0.25 + 0.05 * step, 2) for step in range(12))
SPARSE_GRID = tuple(round(0.40 + 0.05 * step, 2) for step in range(21))


@dataclass(frozen=True)
class Noise:
    """Noise variance of one measurement, by how many direct measurements the model has."""

    well: float
    sparse: float
    well_measured: int = capability._WELL_MEASURED

    def variance(self, direct: int) -> float:
        return self.well if direct >= self.well_measured else self.sparse

    def label(self) -> str:
        if self.well == self.sparse:
            return f"{self.well} for every model"
        return (f"{self.well} with {self.well_measured}+ direct measurements, "
                f"{self.sparse} with fewer")


UNCALIBRATED = Noise(1.0, 1.0)


def current() -> Noise:
    return Noise(capability._OBSERVATION_VARIANCE, capability._SPARSE_OBSERVATION_VARIANCE)


@dataclass(frozen=True)
class HeldOut:
    """One held-out cell: its standardised value and the rest of the model's evidence."""

    model_id: str
    domain: str
    directness: str
    value: float
    recency: float
    #: (standardised value, recency, directness) of the model's other cells in the domain.
    rest: tuple[tuple[float, float, str], ...]

    @property
    def direct_rest(self) -> int:
        return sum(1 for _, _, directness in self.rest if directness == "direct")

    @property
    def direct_total(self) -> int:
        """Direct measurements the model has in the domain, the held-out cell included."""
        return self.direct_rest + (self.directness == "direct")


def _level(direct: int) -> str:
    return "0" if direct == 0 else "1" if direct == 1 else "2" if direct == 2 \
        else "3-4" if direct <= 4 else "5+"


LEVELS = ("0", "1", "2", "3-4", "5+")


def held_out_cells(
    observations: Sequence[CapabilityObservation],
    specs: Mapping[str, BenchmarkSpec],
    as_of: date,
) -> list[HeldOut]:
    """Every cell that can be held out, with the evidence left to predict it."""
    items, rows = _prepare(observations, specs, as_of)
    by_item: dict[str, list[Any]] = defaultdict(list)
    for row in rows:
        by_item[row.item_id].append(row)
    full = {id(row): z for row, z in _item_zscores(rows)}
    by_model_domain: dict[tuple[str, str], list[Any]] = defaultdict(list)
    for row in rows:
        for domain, _ in items[row.item_id].domains:
            by_model_domain[(row.observation.model_id, domain)].append(row)
    cases = []
    for (model_id, domain), domain_rows in sorted(by_model_domain.items()):
        for held in domain_rows:
            item_rows = by_item[held.item_id]
            if len({row.observation.model_id for row in item_rows}) <= MIN_TRAINING_MODELS:
                continue
            training = [row for row in item_rows if row is not held]
            targets = [row.target for row in training]
            center = sum(targets) / len(targets)
            spread = math.sqrt(
                sum((value - center) ** 2 for value in targets) / max(1, len(targets) - 1)
            ) or 1.0
            retrained = {id(row): z for row, z in _item_zscores(training)}

            def z(row: Any) -> float:
                return retrained[id(row)] if row.item_id == held.item_id else full[id(row)]

            tags = items[held.item_id].domains
            cases.append(HeldOut(
                model_id=model_id,
                domain=domain,
                directness=dict(tags)[domain],
                value=(held.target - center) / spread,
                recency=held.recency_weight,
                rest=tuple(
                    (z(row), row.recency_weight, dict(items[row.item_id].domains)[domain])
                    for row in domain_rows if row is not held
                ),
            ))
    return cases


def _loading(directness: str) -> float:
    return _projection_loading((("domain", directness),), "domain")


def predict(case: HeldOut, noise: Noise) -> tuple[float, float, float]:
    """The projection's estimate from ``case.rest``: mean, estimate variance, predictive variance.

    The noise variance follows the model's direct count with the cell included:
    the count the published estimate uses.
    """
    variance = noise.variance(case.direct_total)
    precision = capability._DOMAIN_PRIOR_PRECISION
    weighted = 0.0
    for value, recency, directness in case.rest:
        weight = _loading(directness) ** 2 * recency / variance
        precision += weight
        weighted += weight * value
    mean = weighted / precision
    own = _loading(case.directness) ** 2 * case.recency / variance
    return mean, 1 / precision, 1 / precision + 1 / own


@dataclass(frozen=True)
class Coverage:
    cells: int
    predictive: float
    capability_interval: float


def coverage(cases: Iterable[HeldOut], noise: Noise) -> dict[tuple[str, str], Coverage]:
    """Coverage of the 80% intervals by held-out directness and direct evidence left."""
    counts: dict[tuple[str, str], list[int]] = defaultdict(lambda: [0, 0, 0])
    for case in cases:
        mean, estimate_variance, predictive_variance = predict(case, noise)
        miss = abs(case.value - mean)
        count = counts[(case.directness, _level(case.direct_rest))]
        count[0] += 1
        count[1] += miss <= Z80 * math.sqrt(predictive_variance)
        count[2] += miss <= Z80 * math.sqrt(estimate_variance)
    return {
        key: Coverage(n, inside / n, naive / n)
        for key, (n, inside, naive) in sorted(counts.items())
    }


def pooled(table: Mapping[tuple[str, str], Coverage], directness: str) -> Coverage:
    rows = [row for (kind, _), row in table.items() if kind == directness]
    cells = sum(row.cells for row in rows)
    return Coverage(
        cells,
        sum(row.predictive * row.cells for row in rows) / cells if cells else math.nan,
        sum(row.capability_interval * row.cells for row in rows) / cells if cells else math.nan,
    )


def log_likelihood(cases: Iterable[HeldOut], noise: Noise) -> float:
    """Mean predictive log density of held-out direct cells."""
    total, count = 0.0, 0
    for case in cases:
        if case.directness != "direct":
            continue
        mean, _, predictive_variance = predict(case, noise)
        total += -0.5 * math.log(2 * math.pi * predictive_variance) \
            - 0.5 * (case.value - mean) ** 2 / predictive_variance
        count += 1
    return total / count if count else -math.inf


def fit_noise(cases: Sequence[HeldOut], *, single: bool = False) -> Noise:
    """The noise variances that best predict held-out direct cells.

    Direct cells only: a domain's capability is what its direct benchmarks
    measure, and proxy evidence enters only as an input to the estimate.
    ``single`` fits one variance for every model, for comparison.
    """
    if single:
        candidates = [Noise(value, value) for value in sorted(set(WELL_GRID + SPARSE_GRID))]
    else:
        candidates = [Noise(well, sparse) for well in WELL_GRID for sparse in SPARSE_GRID]
    return max(candidates, key=lambda noise: (
        log_likelihood(cases, noise), -noise.well, -noise.sparse))


def fit_by_model_folds(cases: Sequence[HeldOut], folds: int = 5) -> dict[str, Any]:
    """Refit with each fifth of the models held out, and score those models."""
    models = sorted({case.model_id for case in cases})
    table: dict[tuple[str, str], list[float]] = defaultdict(lambda: [0, 0.0, 0.0])
    fitted = []
    for fold in range(folds):
        held = set(models[fold::folds])
        noise = fit_noise([case for case in cases if case.model_id not in held])
        fitted.append(noise)
        for key, row in coverage([c for c in cases if c.model_id in held], noise).items():
            table[key][0] += row.cells
            table[key][1] += row.predictive * row.cells
            table[key][2] += row.capability_interval * row.cells
    return {
        "fitted": fitted,
        "coverage": {
            key: Coverage(int(n), inside / n, naive / n)
            for key, (n, inside, naive) in sorted(table.items())
        },
    }


def _observations(snapshot: Any) -> tuple[list[CapabilityObservation], dict[str, BenchmarkSpec]]:
    """The observations the snapshot build fits, read back from a loaded snapshot."""
    tags = snapshot.benchmark_domain_tags()
    observations = []
    for model_id, row in snapshot.corpus_evidence():
        domains = tuple(tags.get(row.benchmark_id, ()))
        if row.date is None or not domains:
            continue
        observations.append(CapabilityObservation(
            model_id=model_id,
            benchmark_id=row.benchmark_id,
            value=float(row.value),
            unit=row.unit,
            measured_by=str(row.measured_by or ""),
            date=row.date,
            record_id=str(row.record_id or ""),
            version=row.version,
            domains=domains,
        ))
    specs: dict[str, BenchmarkSpec] = {}
    for item in snapshot.capability_items.values():
        specs.setdefault(str(item["benchmark"]), BenchmarkSpec(
            random_baseline=item.get("random_baseline"),
            sample_size=item.get("sample_size"),
            direction=item.get("direction", "higher_is_better"),
        ))
    return observations, specs


def audit(snapshot: Any) -> dict[str, Any]:
    observations, specs = _observations(snapshot)
    cases = held_out_cells(observations, specs, snapshot.as_of)
    single = fit_noise(cases, single=True)
    fitted = fit_noise(cases)
    used = current()
    return {
        "snapshot": snapshot.snapshot_id,
        "as_of": snapshot.as_of.isoformat(),
        "observations": len(observations),
        "cells": len(cases),
        "prior_precision": capability._DOMAIN_PRIOR_PRECISION,
        "proxy_loading": capability._PROJECTION_PROXY_LOADING,
        "log_likelihood": {
            "uncalibrated": log_likelihood(cases, UNCALIBRATED),
            "single": log_likelihood(cases, single),
            "fitted": log_likelihood(cases, fitted),
            "current": log_likelihood(cases, used),
        },
        "single": single,
        "fitted": fitted,
        "current": used,
        "before": coverage(cases, UNCALIBRATED),
        "single_coverage": coverage(cases, single),
        "after": coverage(cases, used),
        "folds": fit_by_model_folds(cases),
    }


def _table(rows: Mapping[tuple[str, str], Coverage]) -> list[str]:
    lines = [
        "| Held-out cell | Direct cells left | Cells | Predictive 80% coverage | "
        "Capability-interval coverage |",
        "|---|---|---:|---:|---:|",
    ]
    for (directness, level), row in rows.items():
        lines.append(
            f"| {directness} | {level} | {row.cells} | {row.predictive:.1%} | "
            f"{row.capability_interval:.1%} |"
        )
    for directness in ("direct", "proxy"):
        total = pooled(rows, directness)
        if total.cells:
            lines.append(
                f"| **{directness}, all** | | **{total.cells}** | **{total.predictive:.1%}** | "
                f"{total.capability_interval:.1%} |"
            )
    return lines


def markdown(result: Mapping[str, Any]) -> str:
    folds = result["folds"]
    likelihood = result["log_likelihood"]
    used, fitted, single = result["current"], result["fitted"], result["single"]
    lines = [
        "# Capability interval calibration",
        "",
        f"MODEL-206. Snapshot `{result['snapshot']}`, as of {result['as_of']}: "
        f"{result['observations']} admitted observations, {result['cells']} held-out cells.",
        "Generated by `scripts/capability_calibration.py`; do not edit by hand.",
        "",
        "## What was checked",
        "",
        "The domain estimates in `decision/capability.py` are a projection. Each admitted",
        "measurement is standardised within its benchmark and read as the model's domain",
        "capability plus noise. A proxy tag multiplies a measurement's precision by "
        f"{result['proxy_loading']}²,",
        "and age discounts it. The prior on capability has precision "
        f"{result['prior_precision']} (standard deviation 2).",
        "",
        "Capability is never observed, so an interval on it cannot be checked directly.",
        "The audit checks the same model's predictions instead. It holds out one",
        "model-benchmark cell, re-standardises that benchmark without it, estimates the",
        "model's capability from its remaining cells in the domain, and asks whether the",
        "held-out value lies inside the 80% predictive interval: the estimate's spread plus",
        "the held-out measurement's own noise. If the noise model is right, about 80% lie",
        "inside at every evidence level. A cell is held out only when at least",
        f"{MIN_TRAINING_MODELS} other models are measured on its benchmark.",
        "",
        "The last column of each table is the naive reading: the held-out value against",
        "the capability interval alone. It must fall as evidence grows, because one",
        "benchmark carries noise that the capability interval does not. It is reported,",
        "not targeted.",
        "",
        "## Before: noise variance 1",
        "",
        "Before MODEL-206 every measurement had unit noise variance.",
        "",
        *_table(result["before"]),
        "",
        "Coverage was well above 80%: the intervals were too wide. Wide intervals",
        "overlap, and the old answer called any model whose interval overlapped the",
        "leader's a tie.",
        "",
        "## Recalibration",
        "",
        "Only the noise variance was refitted. The prior precision and the proxy loading",
        "are MODEL-129 design values and were left alone; the likelihood was flat around",
        "them. The criterion is the mean predictive log density of held-out *direct*",
        "cells, because a domain's capability is what its direct benchmarks measure.",
        "",
        f"A single variance for every model fits best at **{single.well}**. It leaves",
        "coverage uneven by evidence level:",
        "",
        *_table(result["single_coverage"]),
        "",
        "Models measured directly on few benchmarks miss more often. Their held-out",
        "errors are larger than one variance allows, so one variance makes their",
        "intervals overconfident. The noise variance was therefore fitted separately",
        f"for models with {used.well_measured} or more direct measurements in the domain",
        "and for models with fewer. The split point is where the likelihood stops",
        "improving; the data cannot place it more precisely. Fitted: "
        f"**{fitted.label()}**.",
        "",
        "| Noise model | Mean predictive log density (direct cells) |",
        "|---|---:|",
        f"| 1 for every model (before) | {likelihood['uncalibrated']:.4f} |",
        f"| {single.label()} | {likelihood['single']:.4f} |",
        f"| {fitted.label()} | {likelihood['fitted']:.4f} |",
        "",
        f"`decision/capability.py` uses **{used.label()}** "
        "(`_OBSERVATION_VARIANCE`, `_SPARSE_OBSERVATION_VARIANCE`, `_WELL_MEASURED`).",
        "The refinement projection (MODEL-190) uses the same rule.",
        "",
        "## After",
        "",
        *_table(result["after"]),
        "",
        "## Out of sample",
        "",
        "The fit above scores the cells it was fitted on. The models were also split",
        "into five folds: the variances were refitted on four folds and scored on the",
        "fifth. Fitted per fold: "
        + "; ".join(noise.label() for noise in folds["fitted"]) + ".",
        "",
        *_table(folds["coverage"]),
        "",
        "## Reading",
        "",
        "- Direct cells are now close to 80% at every evidence level with enough cells",
        "  to read. The 3-4 level has too few cells to judge.",
        "- A likely cause of the larger errors at low evidence is the projection's",
        "  standardisation. A benchmark is standardised over the models it measures, and",
        "  sparsely measured models tend to sit on benchmarks with different populations.",
        "  The bifactor fit learns benchmark intercepts; the projection does not. This is",
        "  recorded here, not fixed.",
        "- Proxy cells are still above 80%. The proxy loading keeps proxy evidence",
        "  deliberately weak as an input, and a proxy value is not the quantity a domain",
        "  estimate is about.",
        "- Intervals narrow. A fresh direct measurement now has standard deviation "
        f"{math.sqrt(used.well):.2f}",
        f"  (well-measured) or {math.sqrt(used.sparse):.2f} (sparse), where it was 1.",
        "- Thin-evidence models keep wide intervals. The decision keeps them out of the",
        "  leader's band instead of calling them a tie (`docs/decision-contract.md`, 2.7).",
        "",
    ]
    return "\n".join(lines)


def _json(value: Any) -> Any:
    if isinstance(value, Coverage | Noise):
        return value.__dict__
    if isinstance(value, Mapping):
        return {
            ("/".join(key) if isinstance(key, tuple) else str(key)): _json(item)
            for key, item in value.items()
        }
    if isinstance(value, list | tuple):
        return [_json(item) for item in value]
    return value


def main() -> int:
    from decision.snapshot import build_from_repo, load_built_snapshot

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--date", type=date.fromisoformat, default=date.today())
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    built = build_from_repo(root, premier=root / "premier" / "slice-1.yaml", as_of=args.date,
                            gate=False)
    result = audit(load_built_snapshot(built, source="calibration audit build"))
    output = args.output or root / "docs" / "research" / "capability-interval-calibration.md"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(markdown(result), encoding="utf-8")
    output.with_suffix(".json").write_text(
        json.dumps(_json(result), indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
