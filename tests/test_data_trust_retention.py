"""Retained-source auditing uses synthetic manifests and never reads source bodies."""

from __future__ import annotations

import gzip
import hashlib
import json
import subprocess
from datetime import date
from pathlib import Path

import pytest

from decision import retention, snapshot
from decision.registry import load as load_registry
from scripts.data_trust import invariants
from scripts.data_trust import retention as audit
from scripts.data_trust.catalogue import calibrate, load

TODAY = date(2026, 11, 9)


@pytest.fixture
def root(tmp_path, monkeypatch):
    monkeypatch.setattr(retention, "cite_only_hosts", lambda: ("cite.example",))
    (tmp_path / "models").mkdir()
    (tmp_path / "models/card.md").write_text("---\nmodel_id: example/model\n---\n")
    (tmp_path / "research").mkdir()
    return tmp_path


def body(root, name="page.gz"):
    path = root / "research" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(gzip.compress(b"synthetic response"))
    return path


def manifest(root, rows, name="sources.json"):
    path = root / "research" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(rows))
    return path


def report(root, **kwargs):
    return invariants.run(load(root, **kwargs), load_registry(), TODAY)


def retained(result):
    return [f for f in result["findings"] if f["rule"] == "retained_cite_only_copy"]


def test_audit_reports_retained_copy_from_cite_only_host(root):
    body(root)
    manifest(root, [{"url": "https://cite.example/source", "path": "page.gz",
                     "sha256": hashlib.sha256(b"synthetic response").hexdigest(), "bytes": 18}])
    assert retained(report(root)) == [{"id": "research/page.gz", "field": "source_copy",
                                      "rule": "retained_cite_only_copy", "severity": "error"}]


@pytest.mark.parametrize("path_field", ["path", "file", "copy", "copy_path", "raw_path", "artifact"])
@pytest.mark.parametrize("container", ["list", "pages", "results", "nested"])
def test_retained_copy_manifest_shapes(root, path_field, container):
    body(root)
    rows = [{"requested_url": "https://cite.example/source", path_field: "research/page.gz"}]
    document = rows if container == "list" else {container: rows}
    manifest(root, document)
    assert len(retained(report(root))) == 1


def test_retainable_origin_and_metadata_without_body_pass(root):
    body(root)
    manifest(root, [{"url": "https://retain.example/source", "path": "page.gz"},
                    {"url": "https://cite.example/source", "path": None, "snapshot_ref": "cited"}])
    assert report(root)["errors"] == 0
    assert not retained(report(root))


@pytest.mark.parametrize("redirect", ["final_url", "resolved_urls"])
def test_audit_reports_redirect_to_cite_only_origin(root, redirect):
    body(root)
    value = "https://cite.example/destination"
    manifest(root, [{"url": "https://retain.example/source", "path": "page.gz",
                     redirect: [value] if redirect == "resolved_urls" else value}])
    assert len(retained(report(root))) == 1


def test_audit_deduplicates_copies_across_manifests(root):
    body(root)
    manifest(root, [{"url": "https://cite.example/source", "path": "page.gz", "file": "page.gz"}])
    manifest(root, {"pages": [{"url": "https://retain.example/source", "copy": "research/page.gz"},
                               {"url": "https://cite.example/source", "copy_path": "research/page.gz"}]},
             "other.json")
    assert len(retained(report(root))) == 1


def test_missing_and_unattributed_bodies_are_coverage_limits(root):
    body(root, "unattributed.gz")
    manifest(root, [{"url": "https://cite.example/source", "path": "missing.gz"}])
    result = report(root)
    assert not retained(result)
    assert {(f["rule"], f["severity"]) for f in result["findings"] if f["field"] == "source_copy"} == {
        ("retained_copy_missing", "warning"), ("retained_copy_unattributed", "warning")}


def test_retained_copy_check_never_reads_or_expands_body(root, monkeypatch):
    path = body(root)
    path.write_bytes(b"not a compressed archive")
    manifest(root, [{"url": "https://cite.example/source", "path": "page.gz"}])
    read_bytes = Path.read_bytes
    def guarded_read(self):
        assert self != path, "audit must use manifest metadata without reading a source body"
        return read_bytes(self)
    monkeypatch.setattr(Path, "read_bytes", guarded_read)
    assert len(retained(report(root))) == 1


@pytest.mark.parametrize("external", ["absolute", "traversal", "symlink"])
def test_retention_audit_does_not_follow_external_paths(root, tmp_path_factory, external):
    outside = tmp_path_factory.mktemp("outside") / "page.gz"
    outside.write_bytes(b"external body")
    if external == "absolute":
        path = str(outside)
    elif external == "traversal":
        path = "../../" + outside.parent.name + "/page.gz"
    else:
        (root / "research/page.gz").symlink_to(outside)
        path = "page.gz"
    manifest(root, [{"url": "https://cite.example/source", "path": path}])
    result = report(root)
    assert not retained(result)
    assert any(f["rule"] == "retained_copy_unsafe_path" for f in result["findings"])


def test_malformed_http_origin_does_not_grant_retention(root):
    body(root)
    manifest(root, [{"url": "https://retain.example:bad/source", "path": "page.gz"}])
    assert len(retained(report(root))) == 1


def test_body_without_origin_is_unattributed(root):
    body(root)
    manifest(root, [{"path": "page.gz", "sha256": "synthetic"}])
    result = report(root)
    assert not retained(result)
    assert any(f["rule"] == "retained_copy_unattributed" and f["severity"] == "warning"
               for f in result["findings"])


def test_copy_findings_survive_calibration(root, monkeypatch):
    body(root)
    manifest(root, [{"url": "https://cite.example/source", "path": "page.gz"}])
    c = load(root)
    monkeypatch.setattr(snapshot, "collect_repo", lambda root: snapshot.SnapshotInputs(
        models=[{"id": "example/model", "lifecycle": "active", "facts": []}]))
    registry = load_registry()
    calibrate(c, root, registry, TODAY)
    assert len(retained(invariants.run(c, registry, TODAY))) == 1


def test_explicit_source_root_supports_composed_catalogues(root, tmp_path_factory):
    body(root)
    manifest(root, [{"url": "https://cite.example/source", "path": "page.gz"}])
    overlay = tmp_path_factory.mktemp("composed")
    (overlay / "models").symlink_to(root / "models", target_is_directory=True)
    (overlay / "research").symlink_to(root / "research", target_is_directory=True)
    assert len(retained(report(overlay, source_root=root))) == 1


def test_git_inventory_does_not_attribute_untracked_files(root):
    body(root)
    manifest(root, [{"url": "https://cite.example/source", "path": "page.gz"}])
    subprocess.run(["git", "init", "--quiet", str(root)], check=True)
    subprocess.run(["git", "-C", str(root), "add", "models", "research/sources.json"], check=True)
    assert not retained(report(root))


def test_manifest_size_limit_is_reported_without_reading_large_file(root):
    body(root)
    manifest(root, [{"url": "https://cite.example/source", "path": "page.gz"}])
    large = root / "research/large.json"
    with large.open("wb") as out:
        out.truncate(2 * 1024 * 1024 + 1)
    result = report(root)
    assert len(retained(result)) == 1
    assert any(f["rule"] == "retained_copy_manifest_limit" and f["severity"] == "warning"
               for f in result["findings"])


def test_manifest_relative_parent_path_resolves_inside_root(root):
    body(root)
    manifest(root, [{"url": "https://cite.example/source", "path": "../page.gz"}],
             "nested/sources.json")
    result = report(root)
    assert len(retained(result)) == 1
    assert not any(f["rule"] == "retained_copy_unsafe_path" for f in result["findings"])


@pytest.mark.parametrize("value", ["loop.gz", "invalid\x00.gz"])
def test_malformed_paths_are_coverage_limits(root, value):
    (root / "research/loop.gz").symlink_to("loop.gz")
    manifest(root, [{"url": "https://cite.example/source", "path": value}])
    result = report(root)
    assert not retained(result)
    assert any(f["rule"] == "retained_copy_unsafe_path" for f in result["findings"])


def test_attributed_json_body_is_not_parsed_as_a_manifest(root, monkeypatch):
    target = root / "research/response.json"
    target.write_text('{"response": "synthetic"}')
    manifest(root, [{"url": "https://cite.example/source", "path": "response.json"}])
    original = Path.open
    def guarded_open(self, *args, **kwargs):
        assert self != target, "an attributed JSON source body is not a manifest"
        return original(self, *args, **kwargs)
    monkeypatch.setattr(Path, "open", guarded_open)
    assert len(retained(report(root))) == 1


# MODEL-510: a host the private terms register marks forbids is restrictively cite-only.
# The register here is synthetic. With no data directory the public list alone decides.
LISTED = "listed.example"
FORBIDDEN = "forbidden.example"


@pytest.fixture
def lists(monkeypatch):
    monkeypatch.setattr(retention, "_public_cite_only_hosts", lambda: (LISTED,))
    retention._register_forbidding.cache_clear()
    yield
    retention._register_forbidding.cache_clear()


@pytest.fixture
def forbids_data_dir(tmp_path, monkeypatch):
    (tmp_path / "registry").mkdir()
    (tmp_path / "registry/source-terms.json").write_text(json.dumps({
        FORBIDDEN: "forbids", "unclear.example": "unclear",
        "restricts.example": "restricts", "permits.example": "permits"}))
    monkeypatch.setenv("MODELSPEC_DATA_DIR", str(tmp_path))
    return tmp_path


def test_forbids_host_is_restrictively_cite_only_with_parent_suffix(lists, forbids_data_dir):
    assert retention.is_cite_only_restrictive(f"https://{FORBIDDEN}/a")
    assert retention.is_cite_only_restrictive(f"https://docs.{FORBIDDEN}/a")
    assert not retention.is_cite_only_restrictive(f"https://not{FORBIDDEN}/a")
    assert retention.is_cite_only_restrictive(f"https://{LISTED}/a")


@pytest.mark.parametrize("host", ["unclear.example", "restricts.example", "permits.example"])
def test_other_classes_are_unchanged(lists, forbids_data_dir, host):
    assert not retention.is_cite_only_restrictive(f"https://{host}/a")


def test_without_a_forbids_data_dir_behaviour_is_unchanged(lists, monkeypatch):
    monkeypatch.delenv("MODELSPEC_DATA_DIR", raising=False)
    assert not retention.is_cite_only_restrictive(f"https://{FORBIDDEN}/a")
    assert retention.is_cite_only_restrictive(f"https://{LISTED}/a")


def test_granting_status_is_symmetric_with_the_public_list(lists, forbids_data_dir):
    for host in (FORBIDDEN, f"docs.{FORBIDDEN}", LISTED):
        assert retention.cite_only_status(f"https://{host}/a") is True
        assert retention.cite_only_origin_status(f"https://{host}/a") is True
        assert retention.record_origin_status({"url": f"https://{host}/a"}) is True
    for host in ("unclear.example", "restricts.example", "permits.example", f"not{FORBIDDEN}"):
        assert retention.cite_only_status(f"https://{host}/a") is False
        assert retention.record_origin_status({"url": f"https://{host}/a"}) is False


class _Store:
    def __init__(self, records=None):
        self.records = records or {}

    def citation(self, ref):
        return self.records.get(ref)


HASH = "sha256:" + "a" * 64


def _fact(host):
    return {"sources": [{"source_id": "s", "snapshot_ref": HASH, "cited_regions": ["r"],
                         "retrieved_at": "2026-11-19T00:00:00+00:00"}]}, {"s": f"https://{host}/page"}


def test_forbids_host_fact_with_a_citation_record_is_admitted_as_cited(lists, forbids_data_dir):
    from decision import citation
    record, sources = _fact(FORBIDDEN)
    store = _Store({HASH: {"url": sources["s"], "snapshot_ref": HASH, "retrieved_at": None,
                           "resolved_urls": []}})
    assert citation.ref_states(record, sources, store) == ("cited",)
    admitted = citation.fact_citation(record, sources, store)
    assert admitted["status"] == "cited" and admitted["sources"][0]["url"] == sources["s"]
    # exactly what a public-list host gets
    pub_record, pub_sources = _fact(LISTED)
    assert citation.ref_states(pub_record, pub_sources, _Store()) == ("cited",)


def test_a_fact_without_a_valid_citation_is_not_admitted(lists, forbids_data_dir):
    from decision import citation
    record, sources = _fact(FORBIDDEN)
    record["sources"][0]["snapshot_ref"] = "not-a-hash"
    with pytest.raises(ValueError):
        citation.fact_citation(record, sources, _Store())
    record["sources"][0]["snapshot_ref"] = HASH
    record["sources"][0]["cited_regions"] = []
    with pytest.raises(ValueError):
        citation.fact_citation(record, sources, _Store())


def test_unclear_host_fact_is_not_cited(lists, forbids_data_dir):
    from decision import citation
    record, sources = _fact("unclear.example")
    assert citation.ref_states(record, sources, _Store()) == ("open",)
    assert citation.fact_citation(record, sources, _Store()) is None


def test_no_data_dir_leaves_a_forbids_host_open(lists, monkeypatch):
    from decision import citation
    monkeypatch.delenv("MODELSPEC_DATA_DIR", raising=False)
    record, sources = _fact(FORBIDDEN)
    assert citation.ref_states(record, sources, _Store()) == ("open",)


def test_data_trust_main_restores_the_data_dir_env(lists, forbids_data_dir, monkeypatch):
    import os
    from scripts.data_trust import __main__ as command
    monkeypatch.delenv("MODELSPEC_DATA_DIR", raising=False)
    seen = []
    monkeypatch.setattr(command, "_audit", lambda args, seed: (
        seen.append(os.environ.get("MODELSPEC_DATA_DIR")), 0)[1])
    assert command.main(["data", "--data-dir", str(forbids_data_dir)]) == 0
    assert seen == [str(forbids_data_dir)]
    assert "MODELSPEC_DATA_DIR" not in os.environ


def test_accuracy_private_run_applies_the_forbids_class_and_restores(lists, forbids_data_dir, monkeypatch):
    import os
    from scripts import accuracy
    monkeypatch.delenv("MODELSPEC_DATA_DIR", raising=False)
    seen = []
    monkeypatch.setattr(accuracy, "_publish_profile", lambda args: (
        seen.append(retention.forbidding_hosts()), 0)[1])
    assert accuracy.main(["--private-data-root", str(forbids_data_dir)]) == 0
    assert seen == [(FORBIDDEN,)]
    assert "MODELSPEC_DATA_DIR" not in os.environ


def test_env_leak_probe_sets_the_variable_directly():
    import os
    os.environ["MODELSPEC_DATA_DIR"] = "/leaked/by/a/test"


def test_env_leak_probe_next_test_sees_no_leak():
    import os
    assert "MODELSPEC_DATA_DIR" not in os.environ


def test_unreadable_register_changes_nothing(lists, tmp_path, monkeypatch):
    (tmp_path / "registry").mkdir()
    (tmp_path / "registry/source-terms.json").write_text("{")
    monkeypatch.setenv("MODELSPEC_DATA_DIR", str(tmp_path))
    assert not retention.is_cite_only_restrictive(f"https://{FORBIDDEN}/a")


def test_audit_flags_retained_copy_from_forbids_host_only(lists, forbids_data_dir):
    (forbids_data_dir / "research").mkdir()
    for name in ("a.gz", "b.gz"):
        (forbids_data_dir / "research" / name).write_bytes(gzip.compress(b"synthetic"))
    (forbids_data_dir / "research/sources.json").write_text(json.dumps([
        {"url": f"https://{FORBIDDEN}/x", "path": "a.gz", "sha256": "0" * 64},
        {"url": "https://unclear.example/x", "path": "b.gz", "sha256": "0" * 64}]))
    found = [f for f in audit.inventory(forbids_data_dir) if f.rule == "retained_cite_only_copy"]
    assert [f.id for f in found] == ["research/a.gz"]


def _capture(monkeypatch, target, name, seen):
    def fake(*args, **kwargs):
        seen.append(retention.forbidding_hosts())
        return 0
    monkeypatch.setattr(target, name, fake)


def test_vendor_forbids_data_dir_applies_the_forbids_class(lists, forbids_data_dir, monkeypatch):
    import sys
    from tests.test_private_serving import _vendor
    vendor = _vendor()
    monkeypatch.setenv("MODELSPEC_DATA_DIR", "")  # restored after the test
    monkeypatch.setenv("MODELSPEC_SNAPSHOT_KEY", "fixture-key")
    seen = []
    for name in ("build", "export_data"):
        _capture(monkeypatch, vendor, name, seen)
    monkeypatch.setattr(vendor, "build", lambda *a, **k: (seen.append(retention.forbidding_hosts()),
                                                        forbids_data_dir)[1])
    monkeypatch.setattr(sys, "argv", ["vendor.py", "--data-dir", str(forbids_data_dir)])
    vendor.main()
    monkeypatch.setattr(sys, "argv", ["vendor.py", "--data-dir", str(forbids_data_dir),
                                      "--export-data", str(forbids_data_dir / "out")])
    assert vendor.main() == 0
    assert seen and all(hosts == (FORBIDDEN,) for hosts in seen)


def test_vendor_bundle_subprocess_inherits_the_forbids_data_dir(lists, forbids_data_dir, monkeypatch):
    from tests.test_private_serving import _vendor
    vendor = _vendor()
    envs = []

    class Done:
        returncode = 0
        stderr = b""

    monkeypatch.setattr(vendor.subprocess, "run", lambda *a, **k: (envs.append(k["env"]), Done())[1])
    try:
        vendor.bundle_data(forbids_data_dir / "out", forbids_data_dir)
    except Exception:
        pass  # only the environment handed to the export subprocess matters here
    assert envs and envs[0]["MODELSPEC_DATA_DIR"] == str(forbids_data_dir.resolve())


def test_build_forbids_data_dir_applies_the_forbids_class(lists, forbids_data_dir, monkeypatch):
    from pipeline import build
    monkeypatch.setenv("MODELSPEC_DATA_DIR", "")  # restored after the test
    monkeypatch.delenv("DATA_SPLIT_ENABLED", raising=False)
    monkeypatch.delenv("MODELSPEC_REQUIRE_DATA_DIR", raising=False)
    seen = []
    monkeypatch.setattr(build.data_source, "overlay", lambda public, private, out: forbids_data_dir)
    monkeypatch.setattr(build.decision_registry, "use_root", lambda root: None)
    _capture(monkeypatch, build, "build_site", seen)
    assert build.main(["--out", str(forbids_data_dir / "out"), "--data-dir", str(forbids_data_dir)]) == 0
    assert seen == [(FORBIDDEN,)]


def test_copy_store_withholds_bytes_for_a_forbids_host(lists, forbids_data_dir, tmp_path):
    from decision.sources import CopyStore, fingerprint_bytes
    store = CopyStore(tmp_path / "store")
    body = b"synthetic page"
    ref = store.put(body, source_url=f"https://{FORBIDDEN}/page")
    assert ref == fingerprint_bytes(body)
    assert not store.has(ref)
    assert store.citation(ref)["url"] == f"https://{FORBIDDEN}/page"
    other = store.put(b"open page", source_url="https://permits.example/page")
    assert store.has(other)


def test_copy_store_keeps_bytes_without_a_forbids_data_dir(lists, tmp_path, monkeypatch):
    from decision.sources import CopyStore
    monkeypatch.delenv("MODELSPEC_DATA_DIR", raising=False)
    store = CopyStore(tmp_path / "store")
    assert store.has(store.put(b"page", source_url=f"https://{FORBIDDEN}/page"))
