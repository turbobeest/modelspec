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
from schema.card import Identity, ModelCard, Cost, Benchmarks

ROOT = Path(__file__).resolve().parents[1]
SENTINEL = "model247-private-sentinel-8675309"
PRICE = 8675.309123
SCORE = 50.1234567


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
                                     display_name=SENTINEL, provider="lab", model_type="llm-reasoning"),
                     cost=Cost(input=PRICE), benchmarks=Benchmarks(scores={"gpqa_diamond": SCORE}))
    # Clone the first complete premier model's admitted facts and log records.
    # The synthetic active model must pass the same completeness gate as real data.
    from pipeline.load import load_models
    base_id = yaml.safe_load((tree / "premier/slice-1.yaml").read_text())["models"][0]["model_id"]
    base = next(row for row in load_models(tree) if row.model_id == base_id)
    text = card.to_yaml()
    parts = text.split("---", 2)
    front = yaml.safe_load(parts[1])
    front["facts"] = yaml.safe_load(yaml.safe_dump(base.front["facts"]).replace(base_id, "lab/" + SENTINEL))
    (tree / "models" / (SENTINEL + ".md")).write_text(
        "---\n" + yaml.safe_dump(front) + "---" + parts[2])
    log = tree / "verification/log.jsonl"
    copied = [line.replace(base_id, "lab/" + SENTINEL)
              for line in log.read_text().splitlines() if base_id in line]
    with log.open("a") as stream:
        stream.write("\n" + "\n".join(copied) + "\n")
    premier = tree / "premier/slice-1.yaml"
    content = yaml.safe_load(premier.read_text())
    content["models"].append({"model_id": "lab/" + SENTINEL})
    premier.write_text(yaml.safe_dump(content))
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
                for value in (SENTINEL, str(PRICE), str(SCORE)):
                    assert value.encode() not in raw, path.relative_to(tree)
    api = out / "modelspec/api"
    assert {p.relative_to(api).as_posix() for p in api.rglob("*") if p.is_file()} == KEEP_API
    assert not (out / "modelspec/graph").exists()
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
    import json
    signed = json.loads(gzip.decompress(data.read("/api/decision/snapshot.json.gz")))
    assert "lab/" + SENTINEL in {row["id"] for row in signed["content"]["lineup"]["candidates"]}
    assert "lab/" + SENTINEL not in {row["id"] for row in signed["content"]["archive"]["candidates"]}
    import json
    vocabulary = json.loads(data.read("/api/decision/vocabulary.json"))
    assert vocabulary["models"]["lab/" + SENTINEL] == {"display_name": SENTINEL}
    for value in (str(PRICE), str(SCORE)):
        assert value.encode() not in data.read("/api/decision/vocabulary.json")
    assert str(PRICE).encode() in data.read("/api/rank/candidates.json")
    assert str(SCORE).encode() in data.read("/api/rank/candidates.json")
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


def test_vocabulary_has_no_fact_fields():
    from api.worker.src.display_vocabulary import trim
    source = {
        "facets": [{"id": "offering.price.input", "known": 19, "of": 21, "range": {"min": PRICE, "max": PRICE}, "values": [{"value": PRICE, "count": 19}]}],
        "benchmarks": [{"id": "gpqa_diamond", "range": {"min": SCORE, "max": SCORE}, "models": 19}],
        "domains": [{"id": "reasoning", "name": "Reasoning", "estimate_models": 19}],
        "models": {"lab/" + SENTINEL: {"display_name": SENTINEL}},
        "estate": {"plans": [{"id": "plan", "name": "Plan", "price": {"amount": PRICE}, "allowances": {"score": SCORE}}]},
        "templates": [],
        "refinements": [{"id": "python", "name": "Python", "evidence_state": "thin", "measured_models": 2}],
    }
    response = trim(source, model_ids=set(), facet_values={})
    import json
    encoded = json.dumps(response)
    for value in (SENTINEL, str(PRICE), '"price"', '"known"', '"count"', '"allowances"'):
        assert value not in encoded
    assert response["estate"]["plans"] == [{"id": "plan", "name": "Plan"}]
    assert response["benchmarks"] == [{"id": "gpqa_diamond", "range": {"min": SCORE, "max": SCORE}}]
    assert response["facets"] == [{"id": "offering.price.input", "has_data": True}]
    assert response["refinements"] == [{"id": "python", "name": "Python", "thin": True}]


@pytest.mark.parametrize("models", [1, 2, 3])
def test_benchmark_range_requires_three_scored_models(models):
    import json
    from api.worker.src.display_vocabulary import trim
    # The value-bearing sentinel is an endpoint: an unsuppressed sparse range
    # would expose its individual score even without a model row.
    source = {"benchmarks": [{"id": "sentinel_benchmark", "models": models,
                              "range": {"min": SCORE, "max": SCORE + 1}}]}
    assert str(SCORE) in json.dumps(source)
    public = trim(source, model_ids=set(), facet_values={})
    if models < 3:
        assert public["benchmarks"] == [{"id": "sentinel_benchmark"}]
        assert str(SCORE) not in json.dumps(public)
    else:
        assert public["benchmarks"] == [{"id": "sentinel_benchmark", "range": {"min": SCORE, "max": SCORE + 1}}]


def test_openapi_off_matches_main_and_on_documents_vocabulary():
    from api.worker import openapi
    import os
    previous = os.environ.pop("DATA_SPLIT_ENABLED", None)
    try:
        expected = (ROOT / "api/worker/openapi.yaml").read_text()
        assert openapi.render() == expected
        os.environ["DATA_SPLIT_ENABLED"] = "true"
        assert "/v1/vocabulary:" in openapi.render()
    finally:
        if previous is None:
            os.environ.pop("DATA_SPLIT_ENABLED", None)
        else:
            os.environ["DATA_SPLIT_ENABLED"] = previous


def test_vocabulary_cap_uses_persistent_visitor_identity(monkeypatch):
    import asyncio
    import sys
    from types import SimpleNamespace
    from tests.test_feedback import entry as entry_fixture, Request
    from tests.test_human_gate import env
    import human_gate_do
    now = [10000]
    monkeypatch.setattr(human_gate_do.time, "time", lambda: now[0])
    blobs = {"/api/decision/vocabulary.json": b'{"models":{}}'}
    monkeypatch.setitem(sys.modules, "bundled_data", SimpleNamespace(read=blobs.get))
    context = entry_fixture.__wrapped__()
    module = next(context)
    worker = module.Default()
    worker.env = env()
    request = Request("GET", headers={"Origin": "https://modelspec.dev", "CF-Connecting-IP": "203.0.113.9"})
    request.url = "https://api.modelspec.dev/v1/vocabulary"
    try:
        responses = [asyncio.run(worker.fetch(request)) for _ in range(11)]
        assert [r.status for r in responses] == [200] * 10 + [429]
        assert responses[0].headers["cache-control"] == "private, max-age=3600"
        # Vocabulary never spends the decision allowance in the same object.
        obj = next(iter(worker.env.HUMAN_GATE.objects.values()))
        assert asyncio.run(obj.remaining()) == 20
        for _ in range(50):
            now[0] += 61
            assert asyncio.run(worker.fetch(request)).status == 200
        now[0] += 61
        assert asyncio.run(worker.fetch(request)).status == 429
        now[0] = 86400
        assert asyncio.run(worker.fetch(request)).status == 200
    finally:
        context.close()


def test_policy_bytes_and_neutrality_survive_enabled_build(tmp_path, monkeypatch):
    from pipeline import export
    from pipeline.load import load_catalogue
    from api.ranking.engine import neutrality_commitment
    identity = export.make_build(load_catalogue(ROOT), ROOT)
    monkeypatch.setattr(build.exporter, "make_build", lambda *_: identity)
    off, on = tmp_path / "off", tmp_path / "on"
    monkeypatch.setenv("DATA_SPLIT_ENABLED", "false")
    assert build.main(["--out", str(off)]) == 0
    monkeypatch.setenv("DATA_SPLIT_ENABLED", "true")
    assert build.main(["--out", str(on)]) == 0
    for route in ("api/rank/profiles.json", "api/rank/class-fit.json"):
        assert (off / "modelspec" / route).read_bytes() == (on / "modelspec" / route).read_bytes()
    before = (off / "modelspec/method/index.html").read_text()
    after = (on / "modelspec/method/index.html").read_text()
    commitment = neutrality_commitment()
    # Compare the adopted policy's exact strings and method_source, including punctuation.
    import html
    assert html.escape(commitment["pledge"]) in before
    assert html.escape(commitment["pledge"]) in after
    def neutrality_section(page):
        start = page.index('id="neutrality"')
        return page[start:page.index('</section>', start)]
    assert neutrality_section(before) == neutrality_section(after)
    assert "https://modelspec.dev/api/rank/profiles.json" in after


def test_private_policy_guard_reports_only_the_count(tmp_path, capsys):
    import json
    path = tmp_path / "catalogue.json"
    path.write_text(json.dumps({"models": [{"model_id": SENTINEL, "primary_provider": {
        "data_residency_disclosure": "published", "data_residency_source": {"read_on": None}}}]}))
    with pytest.raises(ValueError):
        _vendor().require_cited_policy(path)
    assert capsys.readouterr().err == "uncited policy rows: 1\n"


def test_vendor_diagnostics_keep_public_tracebacks_but_hide_private_values(tmp_path, monkeypatch, capsys):
    import sys
    vendor = _vendor()
    def fail(*args, **kwargs):
        raise ValueError(SENTINEL)
    monkeypatch.setattr(vendor, "build", fail)
    monkeypatch.delenv("MODELSPEC_REQUIRE_DATA_DIR", raising=False)
    monkeypatch.setattr(sys, "argv", ["vendor.py"])
    assert vendor.main() == 2
    public = capsys.readouterr().err
    assert "Traceback" in public and SENTINEL in public
    monkeypatch.setenv("MODELSPEC_SNAPSHOT_KEY", "fixture-key")
    monkeypatch.setattr(sys, "argv", ["vendor.py", "--data-dir", str(tmp_path)])
    assert vendor.main() == 2
    private = capsys.readouterr().err
    assert str(tmp_path) in private and "ValueError" in private
    assert SENTINEL not in private and "Traceback" not in private
