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


def _capture(monkeypatch, target, name, seen):
    def fake(*args, **kwargs):
        seen.append(retention.forbidding_hosts())
        return 0
    monkeypatch.setattr(target, name, fake)


def test_vendor_data_dir_applies_the_forbids_class(data_dir, monkeypatch):
    import sys
    from tests.test_private_serving import _vendor
    vendor = _vendor()
    monkeypatch.setenv("MODELSPEC_DATA_DIR", "")  # restored after the test
    monkeypatch.setenv("MODELSPEC_SNAPSHOT_KEY", "fixture-key")
    seen = []
    for name in ("build", "export_data"):
        _capture(monkeypatch, vendor, name, seen)
    monkeypatch.setattr(vendor, "build", lambda *a, **k: (seen.append(retention.forbidding_hosts()),
                                                        data_dir)[1])
    monkeypatch.setattr(sys, "argv", ["vendor.py", "--data-dir", str(data_dir)])
    vendor.main()
    monkeypatch.setattr(sys, "argv", ["vendor.py", "--data-dir", str(data_dir),
                                      "--export-data", str(data_dir / "out")])
    assert vendor.main() == 0
    assert seen and all(hosts == (FORBIDDEN,) for hosts in seen)


def test_vendor_bundle_subprocess_inherits_the_data_dir(data_dir, monkeypatch):
    from tests.test_private_serving import _vendor
    vendor = _vendor()
    envs = []

    class Done:
        returncode = 0
        stderr = b""

    monkeypatch.setattr(vendor.subprocess, "run", lambda *a, **k: (envs.append(k["env"]), Done())[1])
    try:
        vendor.bundle_data(data_dir / "out", data_dir)
    except Exception:
        pass  # only the environment handed to the export subprocess matters here
    assert envs and envs[0]["MODELSPEC_DATA_DIR"] == str(data_dir.resolve())


def test_build_data_dir_applies_the_forbids_class(data_dir, monkeypatch):
    from pipeline import build
    monkeypatch.setenv("MODELSPEC_DATA_DIR", "")  # restored after the test
    monkeypatch.delenv("DATA_SPLIT_ENABLED", raising=False)
    monkeypatch.delenv("MODELSPEC_REQUIRE_DATA_DIR", raising=False)
    seen = []
    monkeypatch.setattr(build.data_source, "overlay", lambda public, private, out: data_dir)
    monkeypatch.setattr(build.decision_registry, "use_root", lambda root: None)
    _capture(monkeypatch, build, "build_site", seen)
    assert build.main(["--out", str(data_dir / "out"), "--data-dir", str(data_dir)]) == 0
    assert seen == [(FORBIDDEN,)]


def test_copy_store_withholds_bytes_for_a_forbids_host(data_dir, tmp_path):
    from decision.sources import CopyStore, fingerprint_bytes
    store = CopyStore(tmp_path / "store")
    body = b"synthetic page"
    ref = store.put(body, source_url=f"https://{FORBIDDEN}/page")
    assert ref == fingerprint_bytes(body)
    assert not store.has(ref)
    assert store.citation(ref)["url"] == f"https://{FORBIDDEN}/page"
    other = store.put(b"open page", source_url="https://permits.example/page")
    assert store.has(other)


def test_copy_store_keeps_bytes_without_a_data_dir(tmp_path, monkeypatch):
    from decision.sources import CopyStore
    monkeypatch.delenv("MODELSPEC_DATA_DIR", raising=False)
    store = CopyStore(tmp_path / "store")
    assert store.has(store.put(b"page", source_url=f"https://{FORBIDDEN}/page"))
