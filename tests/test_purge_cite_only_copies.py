"""MODEL-419: purge pre-#840 cite-only copies, identified by recorded source URL only.

Every store and data file here is synthetic, under ``tmp_path``; the real cache is
never read.
"""

import json
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
    assert purge.discover_roots(tmp_path / "tmp") == [scratch.root]

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
