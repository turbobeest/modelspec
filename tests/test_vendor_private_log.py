"""Private vendor logs keep counts. Identifiers from the data directory stay off the log."""

from __future__ import annotations

import importlib.util
import logging
import subprocess
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
MARKER = "marker-lab-slug-483c"
DETAIL_NAME = "modelspec-private-build-detail.txt"


def _vendor():
    spec = importlib.util.spec_from_file_location(
        "vendor_private_log", ROOT / "api/worker/vendor.py"
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _private_fixture(tmp_path: Path) -> tuple[Path, str]:
    """A private-shaped directory whose lab registry holds the marker slug."""
    data = tmp_path / "private"
    registry = data / "registry"
    registry.mkdir(parents=True)
    (registry / "labs.yaml").write_text(
        "schema_version: 1\n"
        "labs:\n"
        f"  - id: {MARKER}\n"
        "    jurisdiction: {state: gap, value: null}\n",
        encoding="utf-8",
    )
    slug = yaml.safe_load((registry / "labs.yaml").read_text(encoding="utf-8"))["labs"][0]["id"]
    assert slug == MARKER
    return data, slug


def test_public_vendor_stdout_stays_the_file_count(tmp_path, monkeypatch, capsys) -> None:
    vendor = _vendor()
    monkeypatch.delenv("MODELSPEC_REQUIRE_DATA_DIR", raising=False)
    monkeypatch.delenv("MODELSPEC_SNAPSHOT_KEY", raising=False)
    out = tmp_path / "bundle"
    monkeypatch.setattr(sys, "argv", ["vendor.py", "--out", str(out)])

    assert vendor.main() == 0

    captured = capsys.readouterr()
    assert captured.err == ""
    assert captured.out == f"vendored {len(vendor.SOURCES)} files into {out}\n"


def test_private_vendor_stderr_keeps_counts_and_drops_the_marker(
    tmp_path, monkeypatch, capsys,
) -> None:
    vendor = _vendor()
    data, slug = _private_fixture(tmp_path)
    monkeypatch.setenv("RUNNER_TEMP", str(tmp_path / "runner"))
    private_path = data / "models" / f"{slug}.md"
    stderr = (
        f"premier models: known 3, explicit null 1, gap 0; "
        f"gap labs outside premier: {slug}\n"
        f"Worker bundle build failed: path={private_path}; category=ValueError\n"
        "uncited policy rows: 2\n"
        f"modality flag contradicts list: {slug}\n"
    ).encode()

    def fake_run(cmd, **kwargs):
        return subprocess.CompletedProcess(cmd, 1, stdout=b"", stderr=stderr)

    monkeypatch.setattr(vendor.subprocess, "run", fake_run)
    with pytest.raises(RuntimeError, match="private Worker data build failed"):
        vendor.bundle_data(tmp_path / "out", data)

    captured = capsys.readouterr()
    blob = captured.out + captured.err
    assert slug not in blob
    assert str(private_path) not in blob
    assert "known 3" in captured.err
    assert "explicit null 1" in captured.err
    assert "gap 0" in captured.err
    assert "uncited policy rows: 2" in captured.err
    assert "ValueError" in captured.err
    assert DETAIL_NAME in captured.err
    detail = (tmp_path / "runner" / DETAIL_NAME).read_text(encoding="utf-8")
    assert slug in detail
    assert "modality flag contradicts list" not in captured.err


def test_private_coverage_handler_prints_counts_and_the_detail_name(
    tmp_path, monkeypatch, capsys,
) -> None:
    vendor = _vendor()
    _data, slug = _private_fixture(tmp_path)
    monkeypatch.setenv("RUNNER_TEMP", str(tmp_path / "runner"))
    log = logging.getLogger("decision.snapshot")
    handlers = list(log.handlers)
    propagate = log.propagate
    try:
        vendor._show_coverage_log()
        from decision.snapshot import JurisdictionCoverage

        coverage = JurisdictionCoverage(4, 5, 6, (), (slug,))
        log.info("%s", coverage)
        log.warning("%s: mismatch supersession refused: %s", slug, slug)
        captured = capsys.readouterr()
        assert slug not in captured.out + captured.err
        assert "known 4" in captured.err
        assert "explicit null 5" in captured.err
        assert "gap 6" in captured.err
        assert DETAIL_NAME in captured.err
        detail = (tmp_path / "runner" / DETAIL_NAME).read_text(encoding="utf-8")
        assert slug in detail
    finally:
        log.handlers[:] = handlers
        log.propagate = propagate
        vendor._coverage_log_ready = False


def test_a_private_system_exit_prints_the_category_and_not_the_marker(
    tmp_path, monkeypatch, capsys,
) -> None:
    vendor = _vendor()
    data, slug = _private_fixture(tmp_path)
    monkeypatch.setenv("RUNNER_TEMP", str(tmp_path / "runner"))
    monkeypatch.setenv("MODELSPEC_SNAPSHOT_KEY", "fixture-key")

    def explode(*_args, **_kwargs):
        raise SystemExit(f"modality flag contradicts list:\n{slug}")

    monkeypatch.setattr(vendor, "build", explode)
    monkeypatch.setattr(
        sys, "argv", ["vendor.py", "--data-dir", str(data), "--out", str(tmp_path / "out")],
    )

    assert vendor.main() == 1

    captured = capsys.readouterr()
    assert slug not in captured.out + captured.err
    assert "SystemExit" in captured.err
    assert slug in (tmp_path / "runner" / DETAIL_NAME).read_text(encoding="utf-8")
