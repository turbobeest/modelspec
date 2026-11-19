"""A host the private terms register marks forbids is restrictively cite-only (MODEL-510).

The register here is synthetic. With no data directory the public list alone decides.
"""

from __future__ import annotations

import gzip
import json

import pytest

from decision import retention
from scripts.data_trust import retention as audit

LISTED = "listed.example"
FORBIDDEN = "forbidden.example"


@pytest.fixture(autouse=True)
def lists(monkeypatch):
    monkeypatch.setattr(retention, "cite_only_hosts", lambda: (LISTED,))
    retention._register_forbidding.cache_clear()
    yield
    retention._register_forbidding.cache_clear()


@pytest.fixture
def data_dir(tmp_path, monkeypatch):
    (tmp_path / "registry").mkdir()
    (tmp_path / "registry/source-terms.json").write_text(json.dumps({
        FORBIDDEN: "forbids", "unclear.example": "unclear",
        "restricts.example": "restricts", "permits.example": "permits"}))
    monkeypatch.setenv("MODELSPEC_DATA_DIR", str(tmp_path))
    return tmp_path


def test_forbids_host_is_restrictively_cite_only_with_parent_suffix(data_dir):
    assert retention.is_cite_only_restrictive(f"https://{FORBIDDEN}/a")
    assert retention.is_cite_only_restrictive(f"https://docs.{FORBIDDEN}/a")
    assert not retention.is_cite_only_restrictive(f"https://not{FORBIDDEN}/a")
    assert retention.is_cite_only_restrictive(f"https://{LISTED}/a")


@pytest.mark.parametrize("host", ["unclear.example", "restricts.example", "permits.example"])
def test_other_classes_are_unchanged(data_dir, host):
    assert not retention.is_cite_only_restrictive(f"https://{host}/a")


def test_without_a_data_dir_behaviour_is_unchanged(monkeypatch):
    monkeypatch.delenv("MODELSPEC_DATA_DIR", raising=False)
    assert not retention.is_cite_only_restrictive(f"https://{FORBIDDEN}/a")
    assert retention.is_cite_only_restrictive(f"https://{LISTED}/a")


def test_granting_status_is_not_widened(data_dir):
    assert retention.cite_only_status(f"https://{FORBIDDEN}/a") is False
    assert retention.cite_only_origin_status(f"https://{FORBIDDEN}/a") is False
    assert retention.cite_only_status(f"https://{LISTED}/a") is True


def test_unreadable_register_changes_nothing(tmp_path, monkeypatch):
    (tmp_path / "registry").mkdir()
    (tmp_path / "registry/source-terms.json").write_text("{")
    monkeypatch.setenv("MODELSPEC_DATA_DIR", str(tmp_path))
    assert not retention.is_cite_only_restrictive(f"https://{FORBIDDEN}/a")


def test_audit_flags_retained_copy_from_forbids_host_only(data_dir):
    (data_dir / "research").mkdir()
    for name in ("a.gz", "b.gz"):
        (data_dir / "research" / name).write_bytes(gzip.compress(b"synthetic"))
    (data_dir / "research/sources.json").write_text(json.dumps([
        {"url": f"https://{FORBIDDEN}/x", "path": "a.gz", "sha256": "0" * 64},
        {"url": "https://unclear.example/x", "path": "b.gz", "sha256": "0" * 64}]))
    found = [f for f in audit.inventory(data_dir) if f.rule == "retained_cite_only_copy"]
    assert [f.id for f in found] == ["research/a.gz"]
