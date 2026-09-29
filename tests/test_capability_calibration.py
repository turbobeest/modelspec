"""The capability interval calibration audit (MODEL-206)."""

from __future__ import annotations

import math
import random
import re
from datetime import date
from pathlib import Path

import pytest

from decision import capability
from decision.capability import CapabilityObservation, fit_capabilities
from scripts import capability_calibration as audit

ROOT = Path(__file__).resolve().parents[1]
AS_OF = date(2026, 9, 29)
REPORT = ROOT / "docs" / "research" / "capability-interval-calibration.md"


def _observations(noise_sd: float, *, models: int = 60, benchmarks: int = 6,
                  seed: int = 206) -> list[CapabilityObservation]:
    """Linear scores drawn from the projection's own model: ability plus noise."""
    rng = random.Random(seed)
    rows = []
    for index in range(models):
        ability = rng.gauss(0, 1)
        for benchmark in range(benchmarks):
            rows.append(CapabilityObservation(
                model_id=f"lab/m{index:02d}",
                benchmark_id=f"bench_{benchmark}",
                value=50 + 10 * (ability + rng.gauss(0, noise_sd)),
                unit="points",
                measured_by="independent",
                date=AS_OF,
                record_id=f"r{index}-{benchmark}",
                version=None,
                domains=(("coding", "direct"),),
            ))
    return rows


def test_the_audit_recovers_the_noise_it_was_given() -> None:
    noise_sd = math.sqrt(0.5)
    cases = audit.held_out_cells(_observations(noise_sd), {}, AS_OF)
    # Standardising within a benchmark divides by the spread of ability plus noise.
    standardised = noise_sd**2 / (1 + noise_sd**2)

    fitted = audit.fit_noise(cases, single=True)
    table = audit.coverage(cases, fitted)

    assert fitted.well == pytest.approx(standardised, abs=0.1)
    assert audit.pooled(table, "direct").predictive == pytest.approx(0.8, abs=0.05)


def test_unit_noise_on_well_measured_benchmarks_overcovers() -> None:
    cases = audit.held_out_cells(_observations(math.sqrt(0.5)), {}, AS_OF)

    assert audit.pooled(audit.coverage(cases, audit.UNCALIBRATED), "direct").predictive > 0.9


def test_the_audits_estimate_is_the_published_estimate() -> None:
    # Seven benchmarks: with one held out the model is still well measured.
    observations = _observations(0.7, models=8, benchmarks=7)
    fit = fit_capabilities(observations, {}, as_of=AS_OF)
    case = audit.held_out_cells(observations, {}, AS_OF)[0]
    held = [row for row in observations if row.model_id == case.model_id]
    # Refit without the held-out cell: the audit's estimate is the projection's.
    kept = [row for row in observations if not (
        row.model_id == case.model_id and row.record_id == held[0].record_id)]
    refit = fit_capabilities(kept, {}, as_of=AS_OF).estimate(case.model_id, "coding")
    mean, variance, _ = audit.predict(case, audit.current())

    assert fit.estimate(case.model_id, "coding") is not None
    assert mean == pytest.approx(refit.value, abs=1e-9)
    assert math.sqrt(variance) == pytest.approx(refit.sd, abs=1e-9)


def test_sparse_models_get_the_wider_noise() -> None:
    assert capability.observation_variance(capability._WELL_MEASURED) \
        == capability._OBSERVATION_VARIANCE
    assert capability.observation_variance(capability._WELL_MEASURED - 1) \
        == capability._SPARSE_OBSERVATION_VARIANCE
    assert capability._SPARSE_OBSERVATION_VARIANCE > capability._OBSERVATION_VARIANCE


def test_a_single_fresh_direct_benchmark_has_the_documented_width() -> None:
    sd = math.sqrt(1 / (capability._DOMAIN_PRIOR_PRECISION
                        + 1 / capability._SPARSE_OBSERVATION_VARIANCE))

    assert 2 * capability._INTERVAL_Z * sd == pytest.approx(2.04, abs=0.01)


def test_the_report_states_the_constants_the_code_uses() -> None:
    text = REPORT.read_text(encoding="utf-8")
    used = re.search(r"`decision/capability.py` uses \*\*(.+?)\*\*", text)

    assert used is not None
    assert used.group(1) == audit.current().label()
