"""Isolate pytest workers from leaked process-wide CLI env."""

from __future__ import annotations

import pytest


@pytest.fixture(autouse=True)
def _clear_modelspec_cache_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """A leftover MODELSPEC_CACHE would point another CLI test at the same snapshot."""
    monkeypatch.delenv("MODELSPEC_CACHE", raising=False)


def pytest_configure(config):
    # Timing assertions. CI runs them in their own serial step (no xdist), so
    # the bound measures the code, not four workers fighting for the runner.
    config.addinivalue_line("markers", "perf: wall-clock bound; CI runs these serially")
