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
