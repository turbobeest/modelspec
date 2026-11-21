"""Isolate pytest workers from leaked process-wide CLI env."""

from __future__ import annotations

import os
from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def _clear_modelspec_cache_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """A leftover MODELSPEC_CACHE would point another CLI test at the same snapshot.

    A leftover MODELSPEC_ARENA_REVISION would switch an unrelated refresh to
    latest. Tests that need the variable set it themselves.
    """
    monkeypatch.delenv("MODELSPEC_CACHE", raising=False)
    monkeypatch.delenv("MODELSPEC_ARENA_REVISION", raising=False)


@pytest.fixture(autouse=True)
def _clear_modelspec_data_dir_env(monkeypatch: pytest.MonkeyPatch):
    """A leaked MODELSPEC_DATA_DIR flips later tests into private mode (MODEL-510).

    Entry points that take a data directory set it for the length of the call;
    tests that need it set it themselves.
    """
    monkeypatch.delenv("MODELSPEC_DATA_DIR", raising=False)
    yield
    os.environ.pop("MODELSPEC_DATA_DIR", None)


@pytest.fixture(autouse=True)
def _no_live_cite_only_reads(monkeypatch: pytest.MonkeyPatch) -> None:
    """The refresh reads a cite-only board in memory (MODEL-482); a test never reaches the net.

    A test that serves a page replaces ``request_once`` itself.
    """
    from scripts import evidence_reread

    def offline(url: str):
        raise ConnectionError("the network is off in tests")

    monkeypatch.setattr(evidence_reread, "request_once", offline)


@pytest.fixture
def subscription_repository() -> Path:
    return Path(__file__).resolve().parents[1]


@pytest.fixture(scope="session")
def generated_pin_bytes():
    from pipeline.agent_copy import cli_bundle, render
    from qa.contracts import capture_tools

    return {
        "cli/modelspec/agent-bundle.json": render(cli_bundle()).encode(),
        "qa/fixtures/mcp-tools.json": render(capture_tools()).encode(),
    }


def pytest_configure(config):
    # Timing assertions. CI runs them in their own serial step (no xdist), so
    # the bound measures the code, not four workers fighting for the runner.
    config.addinivalue_line("markers", "perf: wall-clock bound; CI runs these serially")
