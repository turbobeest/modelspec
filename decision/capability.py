"""Learn domain capability estimates from verified benchmark evidence.

The fit is a hierarchical bifactor item-response model. Each model has a
general factor and one deviation per observed domain. Each benchmark learns a
positive discrimination and an intercept. Percentage measurements use a
logistic link with the benchmark's registered random baseline. Other numeric
measurements use a standardised linear link.

The module has no benchmark IDs. Benchmark membership and directness come from
the registry tags carried into the snapshot builder. Missing cells add no
likelihood term. Old evidence loses precision, provider self-reports get a
learned offset, and a learned proxy loading keeps proxy tags weaker than direct
tags. The build stores posterior means, intervals, and explanation drivers.
"""

from __future__ import annotations

import hashlib
import math
import random
from collections import defaultdict
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from datetime import date
from typing import Literal

Direction = Literal["higher_is_better", "lower_is_better"]
Directness = Literal["direct", "proxy"]

_INTERVAL_Z = 1.2815515655446004  # central 80 percent interval
_STATIC_HALF_LIFE_DAYS = 365.0
_MIN_RECENCY = 0.25
_RIDGE_GENERAL = 1.0
_RIDGE_DOMAIN = 4.0
_RIDGE_ITEM = 0.25
_MIN_ITEM_MODELS = 3
_DOMAIN_PRIOR_PRECISION = 0.25
_PROJECTION_PROXY_LOADING = 0.35


@dataclass(frozen=True)
class BenchmarkSpec:
    random_baseline: float | None = None
    sample_size: int | None = None
    direction: Direction = "higher_is_better"


@dataclass(frozen=True)
class CapabilityObservation:
    model_id: str
    benchmark_id: str
    value: float
    unit: str | None
    measured_by: str
    date: date
    record_id: str
    version: str | None
    domains: tuple[tuple[str, Directness], ...]


@dataclass(frozen=True)
class CapabilityEstimate:
    value: float
    low: float
    high: float
    sd: float


@dataclass(frozen=True)
class EstimateDriver:
    record_id: str
    benchmark_id: str
    version: str | None
    loading: float
    weight: float
    recency_weight: float


@dataclass(frozen=True)
class DirectnessFit:
    direct_loading: float = 1.0
    proxy_loading: float = 0.35


@dataclass(frozen=True)
class ItemFit:
    id: str
    benchmark_id: str
    version: str | None
    link: Literal["logistic", "linear"]
    direction: Direction
    domains: tuple[tuple[str, Directness], ...]
    discrimination: float
    intercept: float
    residual_sd: float
    random_baseline: float
    center: float
    scale: float
    sample_size: int
    models: int

    def information(self, ability: float) -> float:
        """Fisher information on the raw measurement scale."""
        if self.link == "logistic":
            probability = self.random_baseline + (1 - self.random_baseline) * _sigmoid(
                self.discrimination * ability + self.intercept
            )
            slope = self.discrimination * max(
                1e-9,
                (probability - self.random_baseline)
                * (1 - probability)
                / max(1e-9, 1 - self.random_baseline),
            )
            variance = self.residual_sd**2 + max(
                1e-6, probability * (1 - probability) / self.sample_size
            )
            return slope * slope / variance
        return self.discrimination**2 / max(1e-9, self.residual_sd**2)


@dataclass(frozen=True)
class BacktestResult:
    cells: int
    model_rmse: float
    naive_rmse: float


@dataclass
class _ModelFit:
    model_id: str
    dimensions: tuple[str, ...]
    values: list[float]
    covariance: list[list[float]] = field(default_factory=list)


@dataclass
class _Prepared:
    observation: CapabilityObservation
    item_id: str
    target: float
    base_weight: float
    recency_weight: float


@dataclass
class CapabilityFit:
    as_of: date
    items: dict[str, ItemFit]
    models: dict[str, _ModelFit]
    domain_sd: dict[str, float]
    source_offsets: dict[str, float]
    directness: DirectnessFit
    drivers: dict[tuple[str, str], tuple[EstimateDriver, ...]]
    domain_estimates: dict[tuple[str, str], CapabilityEstimate] = field(default_factory=dict)

    def estimate(self, model_id: str, domain: str) -> CapabilityEstimate | None:
        domain_estimate = self.domain_estimates.get((model_id, domain))
        if domain_estimate is not None:
            return domain_estimate
        model = self.models.get(model_id)
        if model is None or not model.covariance or domain not in model.dimensions:
            return None
        weights = [1.0 if dimension == "g" else 1.0 if dimension == domain else 0.0
                   for dimension in model.dimensions]
        mean = sum(weight * value for weight, value in zip(weights, model.values))
        variance = sum(
            weights[i] * model.covariance[i][j] * weights[j]
            for i in range(len(weights))
            for j in range(len(weights))
        )
        sd = math.sqrt(max(variance, 1e-9))
        return CapabilityEstimate(mean, mean - _INTERVAL_Z * sd, mean + _INTERVAL_Z * sd, sd)

    def explain(self, model_id: str, domain: str, *, limit: int = 8) -> tuple[EstimateDriver, ...]:
        return self.drivers.get((model_id, domain), ())[:limit]

    def predict(self, model_id: str, benchmark_id: str, version: str | None = None) -> float | None:
        item = _find_item(self.items, benchmark_id, version)
        model = self.models.get(model_id)
        if item is None or model is None:
            return None
        theta = _theta(model, item.domains, self.directness.proxy_loading)
        linear = item.discrimination * theta + item.intercept
        if item.link == "logistic":
            p = item.random_baseline + (1 - item.random_baseline) * _sigmoid(linear)
            value = 100 * p
        else:
            value = item.center + item.scale * linear
        if item.direction == "lower_is_better":
            return 100 - value if item.link == "logistic" else -value
        return value

    def to_payload(self, model_ids: Iterable[str] | None = None) -> dict[str, object]:
        keep = set(self.models) if model_ids is None else set(model_ids)
        domains = sorted(self.domain_sd)
        estimates: dict[str, dict[str, list[float]]] = {}
        driver_rows: dict[str, dict[str, list[list[object]]]] = {}
        for model_id in sorted(keep & set(self.models)):
            by_domain: dict[str, list[float]] = {}
            by_driver: dict[str, list[list[object]]] = {}
            for domain in domains:
                estimate = self.estimate(model_id, domain)
                if estimate is None:
                    continue
                by_domain[domain] = [_round(estimate.value), _round(estimate.low),
                                     _round(estimate.high), _round(estimate.sd)]
                rows = self.explain(model_id, domain)
                if rows:
                    by_driver[domain] = [
                        [row.record_id, row.benchmark_id, row.version,
                         _round(row.loading), _round(row.weight), _round(row.recency_weight)]
                        for row in rows
                    ]
            if by_domain:
                estimates[model_id] = by_domain
            if by_driver:
                driver_rows[model_id] = by_driver
        return {
            "method": "hierarchical-bifactor-irt",
            "as_of": self.as_of.isoformat(),
            "directness": {
                "direct_loading": _round(self.directness.direct_loading),
                "proxy_loading": _round(self.directness.proxy_loading),
            },
            "source_offsets": {key: _round(value) for key, value in sorted(
                self.source_offsets.items()
            )},
            "domain_sd": {key: _round(value) for key, value in sorted(self.domain_sd.items())},
            "items": {
                key: {
                    "benchmark": item.benchmark_id,
                    "version": item.version,
                    "link": item.link,
                    "direction": item.direction,
                    "domains": [list(tag) for tag in item.domains],
                    "discrimination": _round(item.discrimination),
                    "intercept": _round(item.intercept),
                    "residual_sd": _round(item.residual_sd),
                    "random_baseline": _round(item.random_baseline),
                    "center": _round(item.center),
                    "scale": _round(item.scale),
                    "sample_size": item.sample_size,
                    "models": item.models,
                }
                for key, item in sorted(self.items.items())
            },
            "estimates": estimates,
            "drivers": driver_rows,
        }


def _round(value: float) -> float:
    # CPython's summation changed in 3.14; discard noise below the precision
    # the learned fit can justify so snapshot hashes remain runtime-independent.
    return round(float(value), 10)


def _sigmoid(value: float) -> float:
    if value >= 0:
        return 1 / (1 + math.exp(-min(value, 700)))
    exp = math.exp(max(value, -700))
    return exp / (1 + exp)


def _logit(value: float) -> float:
    value = min(max(value, 1e-4), 1 - 1e-4)
    return math.log(value / (1 - value))


def _solve(matrix: list[list[float]], vector: list[float]) -> list[float]:
    """Solve a small positive-definite system with deterministic elimination."""
    size = len(vector)
    augmented = [list(row) + [vector[index]] for index, row in enumerate(matrix)]
    for pivot in range(size):
        row = max(range(pivot, size), key=lambda index: abs(augmented[index][pivot]))
        augmented[pivot], augmented[row] = augmented[row], augmented[pivot]
        divisor = augmented[pivot][pivot]
        if abs(divisor) < 1e-12:
            divisor = 1e-12
        for column in range(pivot, size + 1):
            augmented[pivot][column] /= divisor
        for index in range(size):
            if index == pivot:
                continue
            factor = augmented[index][pivot]
            for column in range(pivot, size + 1):
                augmented[index][column] -= factor * augmented[pivot][column]
    return [augmented[index][-1] for index in range(size)]


def _inverse(matrix: list[list[float]]) -> list[list[float]]:
    size = len(matrix)
    columns = [
        _solve(matrix, [1.0 if row == column else 0.0 for row in range(size)])
        for column in range(size)
    ]
    return [[columns[column][row] for column in range(size)] for row in range(size)]


def _recency(observed: date, as_of: date) -> float:
    age = max(0, (as_of - observed).days)
    return float(max(_MIN_RECENCY, 0.5 ** (age / _STATIC_HALF_LIFE_DAYS)))


def _item_ids(observations: Sequence[CapabilityObservation]) -> dict[int, str]:
    versions: dict[str, set[str | None]] = defaultdict(set)
    for row in observations:
        versions[row.benchmark_id].add(row.version)
    return {
        index: row.benchmark_id
        if len(versions[row.benchmark_id]) == 1
        else f"{row.benchmark_id}@{row.version or 'unversioned'}"
        for index, row in enumerate(observations)
    }


def _loading(tags: Sequence[tuple[str, Directness]], proxy: float) -> dict[str, float]:
    values = {
        domain: 1.0 if directness == "direct" else proxy
        for domain, directness in tags
    }
    total = sum(values.values()) or 1.0
    return {"g": 1.0, **{domain: value / total for domain, value in values.items()}}


def _theta(model: _ModelFit, tags: Sequence[tuple[str, Directness]], proxy: float) -> float:
    coefficients = _loading(tags, proxy)
    by_dimension = dict(zip(model.dimensions, model.values))
    return sum(coefficient * by_dimension.get(dimension, 0.0)
               for dimension, coefficient in coefficients.items())


def _find_item(items: Mapping[str, ItemFit], benchmark: str,
               version: str | None) -> ItemFit | None:
    found = [item for item in items.values()
             if item.benchmark_id == benchmark and (version is None or item.version == version)]
    return found[0] if len(found) == 1 else None


def _prepare(
    observations: Sequence[CapabilityObservation],
    specs: Mapping[str, BenchmarkSpec],
    as_of: date,
) -> tuple[dict[str, ItemFit], list[_Prepared]]:
    ordered = sorted(observations, key=lambda row: (
        row.benchmark_id, row.version or "", row.model_id, row.measured_by, row.record_id
    ))
    ids = _item_ids(ordered)
    grouped: dict[str, list[CapabilityObservation]] = defaultdict(list)
    for index, row in enumerate(ordered):
        if row.domains and math.isfinite(row.value):
            grouped[ids[index]].append(row)
    items: dict[str, ItemFit] = {}
    prepared: list[_Prepared] = []
    for item_id, rows in sorted(grouped.items()):
        models = len({row.model_id for row in rows})
        if models < _MIN_ITEM_MODELS:
            continue
        first = rows[0]
        spec = specs.get(first.benchmark_id, BenchmarkSpec())
        percent = (first.unit or "").casefold() in {"percent", "%", "percentage"}
        baseline = 0.0
        if (percent and spec.direction == "higher_is_better"
                and spec.random_baseline is not None):
            registered = spec.random_baseline
            baseline = min(0.5, max(0.0, registered if registered <= 1 else registered / 100))
        sample_size = min(3000, max(100, spec.sample_size or 300))
        raw = [
            (100 - row.value if percent else -row.value)
            if spec.direction == "lower_is_better" else row.value
            for row in rows
        ]
        if percent:
            center, scale = 0.0, 1.0
            targets = [_logit((value / 100 - baseline) / max(1e-9, 1 - baseline))
                       for value in raw]
            link: Literal["logistic", "linear"] = "logistic"
        else:
            center = sum(raw) / len(raw)
            variance = sum((value - center) ** 2 for value in raw) / max(1, len(raw) - 1)
            scale = math.sqrt(variance) or 1.0
            targets = [(value - center) / scale for value in raw]
            link = "linear"
        intercept = sum(targets) / len(targets)
        item = ItemFit(
            id=item_id,
            benchmark_id=first.benchmark_id,
            version=first.version,
            link=link,
            direction=spec.direction,
            domains=tuple(sorted(first.domains)),
            discrimination=1.0,
            intercept=intercept,
            residual_sd=0.35,
            random_baseline=baseline,
            center=center,
            scale=scale,
            sample_size=sample_size,
            models=models,
        )
        items[item_id] = item
        for row, target in zip(rows, targets):
            recency = _recency(row.date, as_of)
            if link == "logistic":
                oriented = 100 - row.value if spec.direction == "lower_is_better" else row.value
                probability = min(max(oriented / 100, 1e-4), 1 - 1e-4)
                slope = max(1e-4, (probability - baseline) * (1 - probability)
                            / max(1e-9, 1 - baseline))
                raw_variance = 0.04**2 + probability * (1 - probability) / sample_size
                base_weight = recency * slope * slope / raw_variance
            else:
                base_weight = recency
            prepared.append(_Prepared(row, item_id, target, base_weight, recency))
    return items, prepared


def _domain_estimates(
    items: Mapping[str, ItemFit],
    rows: Sequence[_Prepared],
) -> tuple[
    dict[tuple[str, str], CapabilityEstimate],
    dict[tuple[str, str], tuple[EstimateDriver, ...]],
]:
    """Project every domain from its own tagged measurements.

    The bifactor fit may use one item for a direct domain and, at a lower
    loading, for a proxy domain. Its other factors must not then order another
    domain. This projection uses only rows tagged to the requested domain.
    Positive within-item scores make it monotone in each observed value, while
    proxy loadings add less precision and therefore leave broader intervals.
    """
    domains = {domain for item in items.values() for domain, _ in item.domains}
    estimates: dict[tuple[str, str], CapabilityEstimate] = {}
    drivers: dict[tuple[str, str], tuple[EstimateDriver, ...]] = {}

    for domain in sorted(domains):
        domain_rows = [
            row
            for row in rows
            if domain in dict(items[row.item_id].domains)
        ]
        by_item: dict[str, list[_Prepared]] = defaultdict(list)
        for row in domain_rows:
            by_item[row.item_id].append(row)

        scores: dict[str, list[tuple[_Prepared, float, float]]] = defaultdict(list)
        for item_id, item_rows in sorted(by_item.items()):
            targets = [row.target for row in item_rows]
            center = sum(targets) / len(targets)
            spread = math.sqrt(
                sum((value - center) ** 2 for value in targets)
                / max(1, len(targets) - 1)
            ) or 1.0
            for row, value in zip(item_rows, targets):
                z_score = (value - center) / spread
                directness_loading = (
                    1.0
                    if dict(items[item_id].domains)[domain] == "direct"
                    else _PROJECTION_PROXY_LOADING
                )
                precision = directness_loading**2 * row.recency_weight
                scores[row.observation.model_id].append((row, z_score, precision))

        for model_id, model_rows in sorted(scores.items()):
            precision = _DOMAIN_PRIOR_PRECISION + sum(
                weight for _, _, weight in model_rows
            )
            mean = sum(weight * value for _, value, weight in model_rows) / precision
            sd = math.sqrt(1 / precision)
            estimates[(model_id, domain)] = CapabilityEstimate(
                mean,
                mean - _INTERVAL_Z * sd,
                mean + _INTERVAL_Z * sd,
                sd,
            )
            total = sum(weight for _, _, weight in model_rows) or 1.0
            driver_rows = [
                EstimateDriver(
                    row.observation.record_id,
                    row.observation.benchmark_id,
                    row.observation.version,
                    1.0
                    if dict(items[row.item_id].domains)[domain] == "direct"
                    else _PROJECTION_PROXY_LOADING,
                    weight / total,
                    row.recency_weight,
                )
                for row, _, weight in model_rows
            ]
            driver_rows.sort(key=lambda driver: (-driver.weight, driver.record_id))
            drivers[(model_id, domain)] = tuple(driver_rows)

    return estimates, drivers


def fit_capabilities(
    observations: Iterable[CapabilityObservation],
    benchmark_specs: Mapping[str, BenchmarkSpec],
    *,
    as_of: date,
    sweeps: int = 60,
) -> CapabilityFit:
    """Fit all admitted evidence. Input order does not change the result."""
    rows_in = tuple(observations)
    items, rows = _prepare(rows_in, benchmark_specs, as_of)
    by_model: dict[str, list[_Prepared]] = defaultdict(list)
    by_item: dict[str, list[_Prepared]] = defaultdict(list)
    domains = sorted({domain for row in rows for domain, _ in row.observation.domains})
    for row in rows:
        by_model[row.observation.model_id].append(row)
        by_item[row.item_id].append(row)
    models = {
        model_id: _ModelFit(
            model_id,
            ("g", *sorted({domain for row in model_rows
                            for domain, _ in row.observation.domains})),
            [0.0] * (1 + len({domain for row in model_rows
                              for domain, _ in row.observation.domains})),
        )
        for model_id, model_rows in sorted(by_model.items())
    }
    source_offsets = {kind: 0.0 for kind in sorted({row.observation.measured_by for row in rows})}
    proxy = 0.35

    for _ in range(sweeps):
        before = {model_id: tuple(model.values) for model_id, model in models.items()}
        for model_id, model in models.items():
            index = {dimension: position for position, dimension in enumerate(model.dimensions)}
            size = len(index)
            matrix = [[0.0] * size for _ in range(size)]
            vector = [0.0] * size
            for position, dimension in enumerate(model.dimensions):
                matrix[position][position] = (_RIDGE_GENERAL if dimension == "g"
                                               else _RIDGE_DOMAIN)
            for row in by_model[model_id]:
                item = items[row.item_id]
                coefficients = _loading(item.domains, proxy)
                design = [item.discrimination * coefficients.get(dimension, 0.0)
                          for dimension in model.dimensions]
                target = (row.target - item.intercept
                          - source_offsets.get(row.observation.measured_by, 0.0))
                weight = row.base_weight / max(0.02, item.residual_sd**2)
                for i in range(size):
                    vector[i] += weight * design[i] * target
                    for j in range(size):
                        matrix[i][j] += weight * design[i] * design[j]
            model.values = _solve(matrix, vector)

        next_items = {}
        for item_id, item in items.items():
            item_rows = by_item[item_id]
            xs = [_theta(models[row.observation.model_id], item.domains, proxy)
                  for row in item_rows]
            ys = [row.target - source_offsets.get(row.observation.measured_by, 0.0)
                  for row in item_rows]
            weights = [row.base_weight for row in item_rows]
            sw = sum(weights) + _RIDGE_ITEM
            sx = sum(weight * x for weight, x in zip(weights, xs))
            sy = sum(weight * y for weight, y in zip(weights, ys))
            sxx = sum(weight * x * x for weight, x in zip(weights, xs)) + _RIDGE_ITEM
            sxy = sum(weight * x * y for weight, x, y in zip(weights, xs, ys)) + _RIDGE_ITEM
            determinant = sw * sxx - sx * sx
            if determinant > 1e-9:
                discrimination = max(0.05, min(6.0, (sw * sxy - sx * sy) / determinant))
                intercept = (sy - discrimination * sx) / sw
            else:
                discrimination, intercept = item.discrimination, item.intercept
            residuals = [y - (intercept + discrimination * x) for x, y in zip(xs, ys)]
            residual_sd = math.sqrt(
                (sum(weight * residual * residual for weight, residual in zip(weights, residuals))
                 + 10 * 0.35**2)
                / (sum(weights) + 10)
            )
            next_items[item_id] = ItemFit(
                **{**item.__dict__, "discrimination": discrimination,
                   "intercept": intercept, "residual_sd": max(0.05, residual_sd)}
            )
        items = next_items

        for kind in source_offsets:
            if kind in {"independent", "independent_evaluator", "benchmark_author", "modelspec",
                        "outcome_protocol"}:
                source_offsets[kind] = 0.0
                continue
            kind_rows = [row for row in rows if row.observation.measured_by == kind]
            residuals = []
            weights = []
            for row in kind_rows:
                item = items[row.item_id]
                predicted = item.intercept + item.discrimination * _theta(
                    models[row.observation.model_id], item.domains, proxy
                )
                residuals.append(row.target - predicted)
                weights.append(row.base_weight)
            source_offsets[kind] = (
                sum(weight * residual for weight, residual in zip(weights, residuals))
                / (sum(weights) + 4.0)
            ) if residuals else 0.0

        proxy_rows = [row for row in rows
                      if any(directness == "proxy" for _, directness in row.observation.domains)]
        if proxy_rows:
            candidates = [0.1 + 0.05 * index for index in range(17)]
            proxy = min(candidates, key=lambda candidate: sum(
                row.base_weight * (
                    row.target
                    - items[row.item_id].intercept
                    - source_offsets.get(row.observation.measured_by, 0.0)
                    - items[row.item_id].discrimination * _theta(
                        models[row.observation.model_id], items[row.item_id].domains, candidate
                    )
                ) ** 2
                for row in proxy_rows
            ) + 0.2 * (candidate - 0.35) ** 2)
        moved = max((abs(value - prior[position])
                     for model_id, model in models.items()
                     for position, value in enumerate(model.values)
                     for prior in [before[model_id]]), default=0.0)
        if moved < 1e-7:
            break

    general = [model.values[0] for model in models.values() if len(by_model[model.model_id]) >= 2]
    mean = sum(general) / len(general) if general else 0.0
    sd = math.sqrt(sum((value - mean) ** 2 for value in general) / len(general)) if general else 1.0
    sd = sd or 1.0
    for model in models.values():
        model.values = [(value - mean if index == 0 else value) / sd
                        for index, value in enumerate(model.values)]
    items = {
        key: ItemFit(**{**item.__dict__,
                        "discrimination": item.discrimination * sd,
                        "intercept": item.intercept + item.discrimination * mean})
        for key, item in items.items()
    }

    domain_sd = {}
    for domain in domains:
        values = [model.values[model.dimensions.index(domain)]
                  for model in models.values() if domain in model.dimensions]
        spread = math.sqrt(sum(value * value for value in values) / len(values)) if values else 0.5
        domain_sd[domain] = min(1.2, max(0.2, spread))

    for model_id, model in models.items():
        index = {dimension: position for position, dimension in enumerate(model.dimensions)}
        size = len(index)
        matrix = [[0.0] * size for _ in range(size)]
        for position, dimension in enumerate(model.dimensions):
            matrix[position][position] = (_RIDGE_GENERAL if dimension == "g"
                                           else 1 / domain_sd.get(dimension, 0.5) ** 2)
        for row in by_model[model_id]:
            item = items[row.item_id]
            coefficients = _loading(item.domains, proxy)
            design = [item.discrimination * coefficients.get(dimension, 0.0)
                      for dimension in model.dimensions]
            weight = row.base_weight / max(0.02, item.residual_sd**2)
            for i in range(size):
                for j in range(size):
                    matrix[i][j] += weight * design[i] * design[j]
        model.covariance = _inverse(matrix)

    drivers: dict[tuple[str, str], tuple[EstimateDriver, ...]] = {}
    for model_id, model_rows in by_model.items():
        for domain in domains:
            driver_candidates: list[EstimateDriver] = []
            for row in model_rows:
                item = items[row.item_id]
                coefficients = _loading(item.domains, proxy)
                domain_loading = coefficients.get(domain, 0.0)
                loading = item.discrimination * domain_loading
                if loading <= 0:
                    continue
                weight = row.base_weight * loading * loading / max(0.02, item.residual_sd**2)
                driver_candidates.append(EstimateDriver(
                    row.observation.record_id,
                    row.observation.benchmark_id,
                    row.observation.version,
                    loading,
                    weight,
                    row.recency_weight,
                ))
            total = sum(driver.weight for driver in driver_candidates) or 1.0
            normalised = [EstimateDriver(
                driver.record_id, driver.benchmark_id, driver.version, driver.loading,
                driver.weight / total, driver.recency_weight,
            ) for driver in driver_candidates]
            normalised.sort(key=lambda driver: (-driver.weight, driver.record_id))
            drivers[(model_id, domain)] = tuple(normalised)

    domain_estimates, domain_drivers = _domain_estimates(items, rows)
    drivers.update(domain_drivers)

    return CapabilityFit(
        as_of=as_of,
        items=items,
        models=models,
        domain_sd=domain_sd,
        source_offsets=source_offsets,
        directness=DirectnessFit(proxy_loading=proxy),
        drivers=drivers,
        domain_estimates=domain_estimates,
    )


def _heldout_cells(
    observations: Sequence[CapabilityObservation], holdout: float, seed: int,
) -> tuple[list[CapabilityObservation], list[CapabilityObservation]]:
    cells: dict[tuple[str, str, str | None], list[CapabilityObservation]] = defaultdict(list)
    for row in observations:
        cells[(row.model_id, row.benchmark_id, row.version)].append(row)
    keys = sorted(cells)
    random.Random(seed).shuffle(keys)
    per_model: dict[str, int] = defaultdict(int)
    per_item: dict[tuple[str, str | None], int] = defaultdict(int)
    for model_id, benchmark, version in keys:
        per_model[model_id] += 1
        per_item[(benchmark, version)] += 1
    selected: set[tuple[str, str, str | None]] = set()
    for key in keys:
        if len(selected) >= int(len(keys) * holdout):
            break
        model_id, benchmark, version = key
        if per_model[model_id] <= 2 or per_item[(benchmark, version)] <= 4:
            continue
        selected.add(key)
        per_model[model_id] -= 1
        per_item[(benchmark, version)] -= 1
    train = [row for key, values in cells.items() if key not in selected for row in values]
    held = [row for key, values in cells.items() if key in selected for row in values]
    return train, held


def backtest_capabilities(
    observations: Sequence[CapabilityObservation],
    benchmark_specs: Mapping[str, BenchmarkSpec],
    *,
    as_of: date,
    seeds: Sequence[int] = (7, 19, 37, 53, 71),
    holdout: float = 0.15,
) -> BacktestResult:
    """Hold out model-benchmark cells and compare with the benchmark mean."""
    model_errors: list[float] = []
    naive_errors: list[float] = []
    for seed in seeds:
        train, held = _heldout_cells(observations, holdout, seed)
        fitted, naive = _prediction_errors(train, held, benchmark_specs, as_of)
        model_errors.extend(fitted)
        naive_errors.extend(naive)
    if not model_errors:
        return BacktestResult(0, math.inf, math.inf)
    return BacktestResult(
        len(model_errors),
        math.sqrt(sum(model_errors) / len(model_errors)),
        math.sqrt(sum(naive_errors) / len(naive_errors)),
    )


def _prediction_errors(
    train: Sequence[CapabilityObservation],
    held: Sequence[CapabilityObservation],
    benchmark_specs: Mapping[str, BenchmarkSpec],
    as_of: date,
) -> tuple[list[float], list[float]]:
    fit = fit_capabilities(train, benchmark_specs, as_of=as_of)
    means: dict[tuple[str, str | None], float] = {}
    for benchmark, version in sorted({(row.benchmark_id, row.version) for row in train}):
        values = [
            row.value
            for row in train
            if row.benchmark_id == benchmark and row.version == version
        ]
        means[(benchmark, version)] = sum(values) / len(values)
    model_errors: list[float] = []
    naive_errors: list[float] = []
    for row in held:
        predicted = fit.predict(row.model_id, row.benchmark_id, row.version)
        key = (row.benchmark_id, row.version)
        if predicted is None or key not in means:
            continue
        peers = [
            other.value
            for other in train
            if other.benchmark_id == row.benchmark_id and other.version == row.version
        ]
        scale = max(
            5.0,
            math.sqrt(
                sum((value - means[key]) ** 2 for value in peers) / max(1, len(peers) - 1)
            ),
        )
        model_errors.append(((predicted - row.value) / scale) ** 2)
        naive_errors.append(((means[key] - row.value) / scale) ** 2)
    return model_errors, naive_errors


def backtest_newest_capabilities(
    observations: Sequence[CapabilityObservation],
    benchmark_specs: Mapping[str, BenchmarkSpec],
    *,
    as_of: date,
) -> BacktestResult:
    """Hold out each model's newest eligible score and compare with an item mean."""
    cells: dict[tuple[str, str, str | None], list[CapabilityObservation]] = defaultdict(list)
    for row in observations:
        cells[(row.model_id, row.benchmark_id, row.version)].append(row)
    item_counts: dict[tuple[str, str | None], int] = defaultdict(int)
    model_cells: dict[str, list[tuple[str, str, str | None]]] = defaultdict(list)
    for key in sorted(cells):
        model_cells[key[0]].append(key)
        item_counts[(key[1], key[2])] += 1
    selected: set[tuple[str, str, str | None]] = set()
    for model_id, keys in sorted(model_cells.items()):
        if len(keys) <= 2:
            continue
        newest = sorted(
            keys,
            key=lambda key: (
                max(row.date for row in cells[key]),
                key[1],
                key[2] or "",
            ),
            reverse=True,
        )
        for key in newest:
            item = (key[1], key[2])
            if item_counts[item] > 4:
                selected.add(key)
                item_counts[item] -= 1
                break
    train = [row for key, values in cells.items() if key not in selected for row in values]
    held = [row for key, values in cells.items() if key in selected for row in values]
    model_errors, naive_errors = _prediction_errors(train, held, benchmark_specs, as_of)
    if not model_errors:
        return BacktestResult(0, math.inf, math.inf)
    return BacktestResult(
        len(model_errors),
        math.sqrt(sum(model_errors) / len(model_errors)),
        math.sqrt(sum(naive_errors) / len(naive_errors)),
    )


def deterministic_probabilities(
    estimates: Mapping[str, CapabilityEstimate],
    *,
    seed_material: str,
    samples: int = 2048,
) -> dict[str, tuple[float, float]]:
    """Return P(best) and top-three stability with a snapshot-derived seed."""
    ordered = sorted(estimates)
    if not ordered:
        return {}
    seed = int.from_bytes(hashlib.sha256(seed_material.encode()).digest()[:8], "big")
    rng = random.Random(seed)
    best = {model_id: 0 for model_id in ordered}
    top3 = {model_id: 0 for model_id in ordered}
    for _ in range(samples):
        drawn = sorted(
            ((rng.gauss(estimates[model_id].value, estimates[model_id].sd), model_id)
             for model_id in ordered),
            key=lambda pair: (-pair[0], pair[1]),
        )
        best[drawn[0][1]] += 1
        for _, model_id in drawn[:3]:
            top3[model_id] += 1
    return {model_id: (best[model_id] / samples, top3[model_id] / samples)
            for model_id in ordered}
