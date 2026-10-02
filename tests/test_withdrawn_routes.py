"""MODEL-273: withdrawn exports must never pass the production smoke as data."""
import gzip
import json
from pathlib import Path

import pytest
import yaml

from pipeline import public_data

ROOT = Path(__file__).resolve().parents[1]
BODY = json.dumps(public_data.TOMBSTONE).encode()


def test_restrict_replaces_old_exports_and_covers_unknown_family_members(tmp_path):
    api = tmp_path / "api"
    for route in (*public_data.REMOVED, "/api/models/lab/model.json",
                  "/api/benchmarks/benchmark.json", "/api/graph/nodes.json",
                  "/api/future-bulk.json", "/api/build.json"):
        path = tmp_path / route.lstrip("/")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b'{"private-sentinel":true}')
    source_headers = (ROOT / "site/holding/_headers").read_text()
    (tmp_path / "_headers").write_text(source_headers)
    (tmp_path / "_redirects").write_text("/legacy  /  301\n")
    public_data.restrict(tmp_path)
    for route in (*public_data.REMOVED, public_data.TOMBSTONE_PATH):
        raw = (tmp_path / route.lstrip("/")).read_bytes()
        if route.endswith(".gz"):
            raw = gzip.decompress(raw)
        assert json.loads(raw) == public_data.TOMBSTONE
    assert (api / "build.json").read_bytes() == b'{"private-sentinel":true}'
    for path in api.rglob("*"):
        if path.is_file() and path.name != "build.json":
            assert b"private-sentinel" not in path.read_bytes()
    assert (tmp_path / "_redirects").read_text() == (
        "/api/models/*  /api/removed.json  200\n"
        "/api/benchmarks/*  /api/removed.json  200\n"
        "/api/graph/*  /api/removed.json  200\n"
        "/legacy  /  301\n"
    )
    headers = (tmp_path / "_headers").read_text()
    assert "/api/*\n  Cache-Control: no-store\n  Access-Control-Allow-Origin: *\n" in headers
    assert "max-age=604800" not in headers
    assert "max-age=300" in headers
    assert "Content-Type: application/json\n  Content-Encoding: gzip" in headers
    before = {p.relative_to(tmp_path): p.read_bytes() for p in tmp_path.rglob("*") if p.is_file()}
    public_data.restrict(tmp_path)
    assert {p.relative_to(tmp_path): p.read_bytes() for p in tmp_path.rglob("*") if p.is_file()} == before


def test_live_headers_keep_long_caching_only_for_hashed_assets():
    from pipeline import live
    source = (ROOT / "site/holding/_headers").read_text()
    result = public_data.cache_headers(public_data.cache_headers(source) + live.HEADERS)
    assert result.count("/api/*\n") == 1
    assert "/assets/*\n  Cache-Control: public, max-age=31536000, immutable\n" in result
    assert "s-maxage=604800" not in result
    assert "max-age=604800" not in result


def test_live_structured_data_reads_a_tombstone_as_a_withdrawn_catalogue(tmp_path):
    from pipeline import structured_data
    api = tmp_path / "api"
    api.mkdir()
    (api / "build.json").write_text(json.dumps({
        "export_schema_version": "3.0", "built_at": "2026-10-02T00:20:00Z",
    }))
    (api / "index.json").write_bytes(BODY)
    dataset = structured_data.dataset(tmp_path)
    assert dataset["description"].startswith("The frozen public image")
    assert "distribution" not in dataset


@pytest.mark.parametrize("status,headers,body", [
    (404, {}, b"not found"),
    (410, {}, b"gone"),
    (200, {"Cache-Control": "no-store"}, BODY),
    (200, {"cache-control": "no-store"}, gzip.compress(BODY)),
])
def test_smoke_accepts_only_absence_or_uncached_tombstones(status, headers, body):
    seen = []

    def fetch(url):
        seen.append(url)
        return status, headers, body

    assert public_data.smoke("https://modelspec.dev/", fetch) == []
    assert seen == ["https://modelspec.dev" + path for path in public_data.PROBES]
    assert all("?" not in url for url in seen)


@pytest.mark.parametrize("status,headers,body", [
    (200, {"cache-control": "public, s-maxage=604800"}, b'{"models":[{"id":"old"}]}'),
    (200, {"cache-control": "no-store"}, b'{"models":[]}'),
    (200, {"cache-control": "no-store"}, gzip.compress(b'{"snapshot":"old"}')),
    (200, {"cache-control": "no-store"}, b'<html>decide app</html>'),
    (200, {"cache-control": "no-store"}, b"\x1f\x8btruncated"),
    (200, {}, BODY),
    (200, {"cache-control": "public, s-maxage=604800"}, BODY),
    (503, {}, b"unavailable"),
    (302, {}, b"redirect"),
])
def test_smoke_rejects_stale_json_even_if_it_claims_no_store(status, headers, body):
    failed = public_data.smoke("https://modelspec.dev", lambda _: (status, headers, body))
    assert len(failed) == len(public_data.PROBES)
    assert all(path in line for path, line in zip(public_data.PROBES, failed))
    assert all("old" not in line for line in failed)


def test_smoke_aggregates_network_failures_and_exits_nonzero(monkeypatch, capsys):
    def fail(_):
        raise OSError("secret response detail")

    failed = public_data.smoke("https://modelspec.dev", fail)
    assert len(failed) == len(public_data.PROBES)
    monkeypatch.setattr(public_data, "smoke", lambda _: failed)
    assert public_data.main(["smoke", "--origin", "https://modelspec.dev"]) == 1
    assert "secret response detail" not in capsys.readouterr().err


def test_production_workflow_smokes_bare_custom_domain_after_every_enabled_deploy():
    workflow = yaml.safe_load((ROOT / ".github/workflows/deploy-sites.yml").read_text())
    smoke = workflow["jobs"]["smoke"]
    assert "deploy" in smoke["needs"]
    assert "needs.deploy.outputs.deployed == 'true'" in smoke["if"]
    step = next(step for step in smoke["steps"] if "withdrawn bulk routes" in step.get("name", ""))
    assert step["if"] == "${{ !cancelled() && vars.DATA_SPLIT_ENABLED == 'true' }}"
    assert step["run"] == "python -m pipeline.public_data smoke --origin https://modelspec.dev"
    assert "mode" not in step["if"]
