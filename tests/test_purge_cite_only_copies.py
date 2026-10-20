"""MODEL-419: purge pre-#840 cite-only copies, identified by recorded source URL only.

Every store and data file here is synthetic, under ``tmp_path``; the real cache is
never read.
"""

import json
import os
import subprocess
from datetime import UTC, datetime

import pytest
import yaml

from decision.sources import CopyStore
from scripts import purge_cite_only_copies as purge

AT = datetime(2026, 10, 1, tzinfo=UTC)


@pytest.fixture(autouse=True)
def isolated(monkeypatch, tmp_path):
    monkeypatch.setenv("MODELSPEC_SOURCE_CACHE", str(tmp_path / "default-cache-unused"))
    monkeypatch.delenv("MODELSPEC_DATA_DIR", raising=False)


def old_copy(store: CopyStore, body: bytes) -> str:
    """A copy written before #840: bytes on disk, no sidecar."""
    ref = store.put(body, source_url="https://example.test/placeholder", retrieved_at=AT)
    assert store.path(ref).is_file()
    return ref


def write_yaml(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")


def run(capsys, *args):
    code = purge.main([str(a) for a in args])
    out = capsys.readouterr().out
    return code, out


def summary(out):
    last = next(row for row in out.splitlines() if row.startswith("stores="))
    return dict(part.split("=", 1) for part in last.split())


def listed_refs(out):
    return {line.split("\t")[1] for line in out.splitlines() if "\t" in line}


@pytest.fixture
def estate(tmp_path):
    """A store and a data checkout covering each way a source URL is recorded."""
    store = CopyStore(tmp_path / "cache")
    data = tmp_path / "data"
    refs = {name: old_copy(store, f"page {name}".encode()) for name in (
        "registry_upper_dot_port", "registry_subdomain", "manifest_redirect",
        "state_copy_ref", "card", "jsonl", "lookalike_host", "unrestricted",
        "text_mentions_xai", "unrecorded",
    )}
    # Page text naming a cite-only host must not matter: only recorded URLs count.
    text_ref = old_copy(store, b"<a href='https://x.ai/pricing'>see https://docs.x.ai</a>")
    refs["text_mentions_xai"] = text_ref
    write_yaml(data / "registry" / "sources.yaml", {"schema_version": 1, "sources": [
        {"id": "xai-pricing", "url": "https://DOCS.X.AI.:443/docs/pricing"},
        {"id": "pplx-pro", "url": "https://www.perplexity.ai/pro"},
        {"id": "lookalike", "url": "https://x.ai.example/pricing"},
        {"id": "notx", "url": "https://notx.ai/pricing"},
        {"id": "plain", "url": "https://example.test/pricing"},
        {"id": "card-source", "url": "https://x.ai/news/grok"},
    ]})
    write_yaml(data / "offerings" / "a.yaml", {"price": {"sources": [
        {"source_id": "xai-pricing", "snapshot_ref": refs["registry_upper_dot_port"]},
        {"source_id": "pplx-pro", "snapshot_ref": refs["registry_subdomain"]},
        {"source_id": "lookalike", "snapshot_ref": refs["lookalike_host"]},
        {"source_id": "notx", "snapshot_ref": refs["unrestricted"]},
        {"source_id": "plain", "snapshot_ref": refs["text_mentions_xai"]},
    ]}})
    (data / "research").mkdir(parents=True)
    (data / "research" / "sources.json").write_text(json.dumps([
        {"source_id": "unregistered", "url": "https://example.test/old-link",
         "final_url": "https://example.test/old-link",
         "resolved_urls": ["https://example.test/old-link", "https://x.ai/new-home"],
         "snapshot_ref": refs["manifest_redirect"]},
    ]), encoding="utf-8")
    (data / "research" / "states.json").write_text(json.dumps([
        {"source_id": "pplx-pro", "copy_ref": refs["state_copy_ref"]},
    ]), encoding="utf-8")
    (data / "models").mkdir()
    (data / "models" / "grok.md").write_text(
        "---\n" + yaml.safe_dump({"evidence": [{"sources": [
            {"source_id": "card-source", "snapshot_ref": refs["card"]}]}]})
        + "---\n\nBody text: snapshot_ref sha256:" + "0" * 64 + " https://x.ai\n",
        encoding="utf-8")
    (data / "verification").mkdir()
    (data / "verification" / "events.jsonl").write_text(json.dumps({"claim": {"sources": [
        {"source_id": "xai-pricing", "snapshot_ref": refs["jsonl"]}]}}) + "\n",
        encoding="utf-8")
    return store, data, refs


CITE_ONLY = {"registry_upper_dot_port", "registry_subdomain", "manifest_redirect",
             "state_copy_ref", "card", "jsonl"}


def test_dry_run_lists_recorded_cite_only_sources_and_deletes_nothing(capsys, estate):
    store, data, refs = estate
    before = sorted(p for p in store.root.rglob("*") if p.is_file())
    code, out = run(capsys, "--root", store.root, "--data-dir", data)
    assert code == 0
    assert listed_refs(out) == {refs[name] for name in CITE_ONLY}
    assert summary(out) == {"stores": "1", "entries": "11", "identified": "9",
                            "cite_only": str(len(CITE_ONLY)), "mode": "dry-run"}
    assert sorted(p for p in store.root.rglob("*") if p.is_file()) == before
    assert "https://x.ai/new-home" in out


def test_apply_deletes_only_matches_then_dry_run_lists_zero(capsys, estate):
    store, data, refs = estate
    code, out = run(capsys, "--root", store.root, "--data-dir", data, "--apply")
    assert code == 0
    assert f"deleted={len(CITE_ONLY)} remaining_cite_only=0" in out
    for name, ref in refs.items():
        assert store.path(ref).exists() == (name not in CITE_ONLY), name
    code, out = run(capsys, "--root", store.root, "--data-dir", data)
    assert code == 0
    assert summary(out)["cite_only"] == "0"
    assert listed_refs(out) == set()


def test_sidecar_names_the_source_and_survives_apply(capsys, tmp_path):
    store = CopyStore(tmp_path / "cache")
    ref = old_copy(store, b"page before the policy")
    store.record_citation(ref, source_url="https://example.test/start", retrieved_at=AT,
                          resolved_urls=["https://Perplexity.AI./hub"])
    kept = old_copy(store, b"ordinary page")
    code, out = run(capsys, "--root", store.root)
    assert listed_refs(out) == {ref}
    assert out.splitlines()[0].startswith("sidecar\t")
    code, out = run(capsys, "--root", store.root, "--apply")
    assert code == 0
    assert not store.path(ref).exists()
    assert store.citation(ref)["snapshot_ref"] == ref
    assert store.path(kept).is_file()


def test_git_history_names_refs_a_later_commit_removed(capsys, tmp_path):
    store = CopyStore(tmp_path / "cache")
    ref = old_copy(store, b"superseded page")
    repo = tmp_path / "repo"
    record = repo / "offerings" / "a.yaml"
    write_yaml(repo / "registry" / "sources.yaml", {"schema_version": 1, "sources": [
        {"id": "xai", "url": "https://x.ai/api"}]})
    write_yaml(record, {"sources": [{"source_id": "xai", "snapshot_ref": ref}]})
    git = ["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@example.test",
           "-c", "commit.gpgsign=false"]
    subprocess.run(["git", "init", "-q", str(repo)], check=True)
    subprocess.run([*git, "add", "."], check=True)
    subprocess.run([*git, "commit", "-qm", "old"], check=True)
    write_yaml(record, {"sources": []})
    subprocess.run([*git, "commit", "-qam", "new"], check=True)

    _, out = run(capsys, "--root", store.root, "--data-dir", repo)
    assert listed_refs(out) == set()
    _, out = run(capsys, "--root", store.root, "--data-git", repo)
    assert listed_refs(out) == {ref}


def test_discover_finds_scratch_stores_and_skips_data_directories(capsys, tmp_path, estate):
    _, data, refs = estate
    scratch = CopyStore(tmp_path / "tmp" / "ticket-1" / "pytest-0" / "copies")
    inside_data = CopyStore(data / "research" / "copies")
    ref = refs["registry_subdomain"]
    # Copy the cached bytes into both stores so each holds the same cite-only ref.
    body = (tmp_path / "cache" / ref[7:9] / ref[7:]).read_bytes()
    for store in (scratch, inside_data):
        store.path(ref).parent.mkdir(parents=True)
        store.path(ref).write_bytes(body)
    (tmp_path / "tmp" / "ticket-1" / "ab").mkdir()  # a hex-named directory, not a store
    assert purge.discover_roots(tmp_path / "tmp", [], []) == [scratch.root]

    code, out = run(capsys, "--discover", tmp_path / "tmp", "--root", inside_data.root,
                    "--data-dir", data, "--apply")
    assert code == 0
    assert not scratch.path(ref).exists()
    assert inside_data.path(ref).is_file()


def test_default_root_is_the_copy_store_root(capsys, tmp_path):
    store = CopyStore()
    assert store.root == tmp_path / "default-cache-unused"
    ref = old_copy(store, b"default root page")
    store.record_citation(ref, source_url="https://docs.x.ai/x", retrieved_at=AT)
    _, out = run(capsys)
    assert listed_refs(out) == {ref}


# --- fail-safe: every uncertain case skips, never deletes (REV-848) ---------------------------

needs_permissions = pytest.mark.skipif(os.geteuid() == 0, reason="root ignores file modes")


@pytest.fixture
def restore_modes():
    """Paths whose mode a test lowers; restored even when the test fails."""
    changed = []
    yield changed
    for path in changed:
        os.chmod(path, 0o755)


def cite_only_store(path, body):
    store = CopyStore(path)
    ref = old_copy(store, body)
    store.record_citation(ref, source_url="https://docs.x.ai/x", retrieved_at=AT)
    return store, ref


@needs_permissions
def test_unreadable_git_entry_skips_the_store(capsys, tmp_path, restore_modes):
    checkout = tmp_path / "checkout"
    subprocess.run(["git", "init", "-q", str(checkout)], check=True)
    inside, kept = cite_only_store(checkout / "cache", b"page in an unknown checkout")
    plain, gone = cite_only_store(tmp_path / "plain-cache", b"page in a plain cache")
    os.chmod(checkout / ".git", 0)
    restore_modes.append(checkout / ".git")

    code = purge.main(["--root", str(inside.root), "--root", str(plain.root), "--apply"])
    captured = capsys.readouterr()
    assert code == 1
    assert inside.path(kept).is_file()
    assert not plain.path(gone).exists()
    assert ".git exists but git cannot read it" in captured.err
    assert "skipped_for_error=1" in captured.out


@needs_permissions
def test_unreadable_directories_are_reported_and_siblings_still_purged(
        capsys, tmp_path, restore_modes):
    base = tmp_path / "scratch"
    readable, gone = cite_only_store(base / "a" / "copies", b"readable store page")
    partly = CopyStore(base / "b" / "copies")
    ordinary = old_copy(partly, b"ordinary page")
    locked = partly.root / "ff"
    locked.mkdir()
    unreadable_root, kept = cite_only_store(tmp_path / "locked-root", b"page in a locked root")
    for path in (locked, unreadable_root.root):
        os.chmod(path, 0)
        restore_modes.append(path)

    code = purge.main(["--discover", str(base), "--root", str(unreadable_root.root), "--apply"])
    captured = capsys.readouterr()
    assert code == 1
    assert not readable.path(gone).exists()
    assert partly.path(ordinary).is_file()
    assert f"{locked}: skipped, unreadable" in captured.err
    assert f"{unreadable_root.root}: skipped, cannot check for a .git entry" in captured.err
    assert "deleted=1 remaining_cite_only=0" in captured.out
    os.chmod(unreadable_root.root, 0o755)
    assert unreadable_root.path(kept).is_file()


@needs_permissions
def test_failed_unlink_is_reported_and_the_rescan_still_runs(capsys, tmp_path, restore_modes):
    store, ref = cite_only_store(tmp_path / "cache", b"page in a read-only prefix")
    prefix = store.path(ref).parent
    os.chmod(prefix, 0o555)
    restore_modes.append(prefix)

    code = purge.main(["--root", str(store.root), "--apply"])
    captured = capsys.readouterr()
    assert code == 1
    assert store.path(ref).is_file()
    assert "deleted=0 remaining_cite_only=1" in captured.out
    assert "not deleted" in captured.err


def test_discover_stays_on_one_filesystem_and_follows_no_symlink(
        capsys, tmp_path, monkeypatch):
    real = tmp_path / "real"
    store, _ = cite_only_store(real / "copies", b"page behind a symlink")
    elsewhere, _ = cite_only_store(tmp_path / "elsewhere" / "copies", b"page through a child link")
    (real / "child-link").symlink_to(elsewhere.root.parent, target_is_directory=True)
    link = tmp_path / "start-link"
    link.symlink_to(real, target_is_directory=True)

    errors, notes = [], []
    assert purge.discover_roots(link, errors, notes) == [store.root]
    assert errors == []
    assert notes == [f"{link}: a symlink; discovering under {real} instead"]

    lstat = os.lstat

    def other_device(path, *args, **kwargs):
        result = lstat(path, *args, **kwargs)
        if os.fspath(path) == os.fspath(real):
            fields = list(result[:10])
            fields[2] += 1
            return os.stat_result(fields)
        return result

    monkeypatch.setattr(os, "lstat", other_device)
    notes = []
    assert purge.discover_roots(real, [], notes) == []
    assert f"{real / 'copies'}: another filesystem; not searched" in notes


def test_delete_refuses_dot_dot_and_symlinks(capsys, tmp_path):
    store, ref = cite_only_store(tmp_path / "cache", b"page in the store")
    outside = tmp_path / ref[7:]
    outside.write_bytes(b"a file outside the store")
    with pytest.raises(ValueError, match="outside its copy store"):
        purge.delete(purge.Entry(store.root, ref, store.root / ".." / ref[7:], ("x",), "data"))
    assert outside.is_file()

    target = tmp_path / "precious"
    target.write_bytes(b"symlink target")
    other = "sha256:" + "ab" * 32
    link = store.path(other)
    link.parent.mkdir(parents=True)
    link.symlink_to(target)
    with pytest.raises(ValueError, match="non-regular"):
        purge.delete(purge.Entry(store.root, other, link, ("x",), "data"))
    store.record_citation(other, source_url="https://x.ai/y", retrieved_at=AT)

    code = purge.main(["--root", str(store.root), "--apply"])
    captured = capsys.readouterr()
    assert code == 1
    assert link.is_symlink() and target.read_bytes() == b"symlink target"
    assert not store.path(ref).exists()
    assert "not a regular file; skipped" in captured.err
