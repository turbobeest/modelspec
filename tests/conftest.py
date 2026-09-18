"""Isolate pytest workers from leaked process-wide CLI env."""

from __future__ import annotations

import pytest


@pytest.fixture(autouse=True)
def _clear_modelspec_cache_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """A leftover MODELSPEC_CACHE would point another CLI test at the same snapshot."""
    monkeypatch.delenv("MODELSPEC_CACHE", raising=False)
