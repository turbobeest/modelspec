"""MODEL-247 S: private data cannot reach any public serving composition."""
from __future__ import annotations

import gzip
import importlib.util
import shutil
from pathlib import Path

import pytest
import yaml

from pipeline import build, holding, live
from pipeline.data_source import DATA_PATHS
from pipeline.public_data import KEEP_API
from schema.card import Identity, ModelCard

ROOT = Path(__file__).resolve().parents[1]
SENTINEL = "model247-private-sentinel-8675309"


def _vendor():
    spec = importlib.util.spec_from_file_location("private_serving_vendor", ROOT / "api/worker/vendor.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def private(tmp_path_factory):
    tree = tmp_path_factory.mktemp("private-data")
    for rel in DATA_PATHS:
        source, target = ROOT / rel, tree / rel
        if source.is_dir():
            shutil.copytree(source, target)
        elif source.is_file():
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
    card = ModelCard(identity=Identity(model_id="lab/" + SENTINEL,
                                     display_name=SENTINEL, provider="lab"))
    (tree / "models" / (SENTINEL + ".md")).write_text(
        card.to_yaml().replace("---\n", "---\nlifecycle: retired\n", 1))
    return tree


def test_private_model_is_absent_from_every_public_file(private, tmp_path, monkeypatch):
    monkeypatch.setenv("DATA_SPLIT_ENABLED", "true")
    monkeypatch.setenv("MODELSPEC_REQUIRE_DATA_DIR", "1")
    out = tmp_path / "public"
    assert build.main(["--out", str(out), "--data-dir", str(private)]) == 0
    # Full, holding and live compositions all receive only the frozen image.
    holding.build(out, tmp_path / "holding")
    web = tmp_path / "web"
    (web / "assets").mkdir(parents=True)
    (web / "decide.html").write_text('<html><body>API decision client</body></html>')
    live.build(out, web, tmp_path / "live")
    for tree in (out, tmp_path / "holding", tmp_path / "live"):
        for path in tree.rglob("*"):
            if path.is_file():
                raw = path.read_bytes()
                if path.suffix == ".gz":
                    raw = gzip.decompress(raw)
                assert SENTINEL.encode() not in raw, path.relative_to(tree)
    api = out / "modelspec/api"
    assert {p.relative_to(api).as_posix() for p in api.rglob("*") if p.is_file()} == KEEP_API
    assert (out / "modelspec/graph/data/views.json").is_file()
    assert live.dead_links(tmp_path / "live/modelspec") == []


def test_private_bundle_contains_the_model_and_private_registry(private, tmp_path, monkeypatch):
    monkeypatch.setenv("MODELSPEC_SNAPSHOT_KEY", "model247-test-key")
    # A distinct private-only device proves file enumeration uses private data.
    shutil.copy2(next((private / "hardware").glob("*.yaml")), private / "hardware/private-device.yaml")
    vendor = _vendor()
    bundle = vendor.build(tmp_path / "bundle", data_dir=private)
    assert (bundle / "hardware/private-device.yaml").read_bytes() == (private / "hardware/private-device.yaml").read_bytes()
    for name in ("harnesses", "providers", "sources"):
        assert (bundle / f"registry/{name}.yaml").read_bytes() == (private / f"registry/{name}.yaml").read_bytes()
    spec = importlib.util.spec_from_file_location("private_bundled_data", bundle / "bundled_data.py")
    data = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(data)
    assert SENTINEL.encode() in data.read("/api/rank/candidates.json")
    assert SENTINEL.encode() in gzip.decompress(data.read("/api/decision/snapshot.json.gz"))
    assert SENTINEL.encode() in data.read("/api/decision/vocabulary.json")
    assert data.read("/api/decision/snapshots/missing.json.gz") is None


def test_private_workflow_jobs_have_main_event_gates_and_no_artifacts():
    for filename in ("deploy-sites.yml", "rank-api.yml"):
        jobs = yaml.safe_load((ROOT / ".github/workflows" / filename).read_text())["jobs"]
        for job in jobs.values():
            steps = job.get("steps", [])
            checkouts = [s for s in steps if s.get("with", {}).get("repository") == "turbobeest/modelspec-data"]
            if not checkouts:
                continue
            assert not any("upload-artifact" in s.get("uses", "") for s in steps)
            for checkout in checkouts:
                gate = job.get("if", "") + checkout.get("if", "")
                assert "refs/heads/main" in gate
                assert "DATA_SPLIT_ENABLED" in gate
                assert "push" in gate and "workflow_dispatch" in gate
                assert checkout["with"]["persist-credentials"] is False


def test_worker_reads_bundled_bytes_without_any_public_fetch(monkeypatch):
    import asyncio
    import sys
    import types
    from tests.test_feedback import entry as entry_fixture, Request

    # Use the same Cloudflare transport stub as the endpoint suites.
    context = entry_fixture.__wrapped__()
    entry = next(context)
    raw = b'{"models":{"lab/private":{"display_name":"Private"}}}'
    blobs = {"/api/decision/vocabulary.json": raw,
             "/api/rank/candidates.json": b'{"candidates":[]}',
             "/api/decision/snapshot.json.gz": b"snapshot-bytes"}
    monkeypatch.setitem(sys.modules, "bundled_data", types.SimpleNamespace(read=blobs.get))

    async def exercise():
        assert await entry._get_json("https://modelspec.dev/api/rank/candidates.json") == {"candidates": []}
        fetch = entry._snapshot_fetcher("https://modelspec.dev/api/decision/snapshot.json.gz")
        first = await fetch(None)
        assert first.status == 200 and first.body == b"snapshot-bytes"
        assert (await fetch(first.etag)).status == 304
        missing = await entry._snapshot_fetcher("https://modelspec.dev/api/decision/snapshots/missing.json.gz")(None)
        assert missing.status == 404
        worker = entry.Default()
        worker.env = types.SimpleNamespace()
        request = Request("GET", headers={"Origin": "https://modelspec.dev"})
        request.url = "https://api.modelspec.dev/v1/vocabulary"
        response = await worker.fetch(request)
        assert response.status == 200
        assert response.json()["models"]["lab/private"]["display_name"] == "Private"
        assert response.headers["access-control-allow-origin"] == "https://modelspec.dev"

    try:
        asyncio.run(exercise())
    finally:
        context.close()
