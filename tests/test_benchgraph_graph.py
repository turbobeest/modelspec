"""MODEL-9: benchgraph graph ingest, round trip, named queries, query service.

FalkorDB-backed tests skip when FalkorDB is unreachable, unless
BENCHGRAPH_REQUIRE_FALKORDB=1 (the Benchgraph graph workflow sets it), in which
case they fail. Point them at a server with BENCHGRAPH_FALKORDB_HOST/PORT
(default localhost:6382, the docker-compose mapping).
"""

from __future__ import annotations

import datetime as dt
import importlib.util
import json
import os
import re
import threading
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path

import pytest

from pipeline import benchgraph_graph as bg

ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture
def graph():
    try:
        g = bg.connect(graph=f"benchgraph_test_{os.getpid()}_{threading.get_ident()}")
        g.query("RETURN 1")
    except Exception as exc:  # noqa: BLE001
        if os.environ.get("BENCHGRAPH_REQUIRE_FALKORDB") == "1":
            pytest.fail(f"FalkorDB required but unreachable: {exc}")
        pytest.skip(f"FalkorDB unreachable at {os.environ.get('BENCHGRAPH_FALKORDB_HOST', 'localhost')}:"
                    f"{os.environ.get('BENCHGRAPH_FALKORDB_PORT', '6382')} ({exc}); "
                    "start one with `docker compose up -d`")
    yield g
    try:
        g.delete()
    except Exception:  # noqa: BLE001
        pass


def _page(bid, category="coding", status="active", sat="open", **extra):
    page = {"id": bid, "name": bid.upper(), "page_kind": "benchmark", "category": category,
            "status": status, "summary": "s", "metric": {"direction": "higher_is_better"},
            "saturation": {"status": sat}, "publisher": {"org": "Org\nwith newline", "authors": [],
                                                         "url": ""},
            "dataset": {"url": f"https://d/{bid}"}, "lineage": {"family": "", "predecessor": "",
                                                               "successors": [], "variants": []},
            "sources": [{"url": "https://x"}], "freshness": {"researched": "2026-01-01"}}
    page.update(extra)
    return page


FIXTURE_PAGES = [
    _page("wide", lineage={"family": "fam", "predecessor": "old", "successors": ["wide_v2", "wide_v2"],
                           "variants": ["wide_sub"]},
          released=dt.date(2025, 1, 2), tags=["a", "b"], aliases=[None, "x"]),
    _page("narrow"),
    _page("unscored"),
    _page("watched", sat="watch"),
    _page("retired", status="superseded"),
    _page("lower", metric={"direction": "lower_is_better"}),
    _page("mathy", category="math", publisher={"org": "", "url": "u"},
          dataset={"validation": "stray key", "size": 3}),
]


def _ev(model, bid, score):
    return {"_model_id": model, "benchmark_id": bid, "score": score, "unit": "percent",
            "source_url": "https://s", "source_kind": "independent_evaluator",
            "evidence_date": "2026-09-01", "date_type": "evaluated", "verified_at": "2026-09-01",
            "configuration": "zero-shot"}


FIXTURE_EVIDENCE = (
    [_ev(f"m{i}", "wide", s) for i, s in enumerate([90, 80, 70])]
    + [_ev(f"m{i}", "narrow", s) for i, s in enumerate([71, 70.5, 70])]
    + [_ev("m0", "narrow", 60)]            # a lower second score for m0 must not count twice
    + [_ev(f"m{i}", "lower", s) for i, s in enumerate([10, 30, 50])]
    + [_ev("m0", "no_such_page", 1)]
)


# ── no database ───────────────────────────────────────────────────────────────
def test_mapping_lists_are_disjoint_and_cover_the_schema():
    from schema.benchmark import BenchmarkCard
    mapped = set(bg.MAPPED_FIELDS)
    assert not mapped & set(bg.UNMAPPED_FIELDS)
    for name, field in BenchmarkCard.model_fields.items():
        sub = getattr(field.annotation, "model_fields", None)
        leaves = [f"{name}.{k}" for k in sub] if sub else [name]
        for leaf in leaves:
            assert leaf in mapped or name in bg.UNMAPPED_FIELDS, f"{leaf} is neither mapped nor allowlisted"


def test_document_shape_and_evidence_skips():
    doc = bg.build_document(pages=FIXTURE_PAGES, evidence=FIXTURE_EVIDENCE)
    labels = {n["label"] for n in doc["nodes"]}
    assert labels == {"Benchmark", "Family", "Publisher", "Dataset", "Capability", "Model"}
    assert {e["type"] for e in doc["edges"]} == set(bg.EDGE_TYPES)
    assert doc["skipped_evidence"] == {"benchmark_without_page": 1}
    stubs = {n["id"] for n in doc["nodes"] if n["label"] == "Benchmark" and n["props"]["stub"]}
    assert stubs == {"old", "wide_v2", "wide_sub"}


def test_export_files_and_manifest(tmp_path):
    doc = bg.build_document(pages=FIXTURE_PAGES, evidence=FIXTURE_EVIDENCE)
    manifest = bg.write_export(doc, tmp_path)
    assert manifest["format_version"] == bg.EXPORT_FORMAT_VERSION
    assert manifest["counts"]["benchmark_pages"] == len(FIXTURE_PAGES)
    assert manifest["build"]["commit"]
    again, loaded = bg.read_export(str(tmp_path))
    assert loaded["nodes"] == json.loads(json.dumps(doc["nodes"]))
    (tmp_path / "edges.json").write_text("[]\n")
    with pytest.raises(ValueError, match="sha256"):
        bg.read_export(str(tmp_path))


def test_param_validation():
    ok = bg.validate_params("benchmarks_still_separating", {"capability": "long-context"})
    assert ok["top_n"] == 5 and ok["include_watch"] is False
    for bad in ({}, {"capability": "x' OR 1=1"}, {"capability": "coding", "top_n": "99"},
                {"capability": "coding", "cypher": "MATCH (n) DELETE n"},
                {"capability": "coding", "require_scores": "maybe"}):
        with pytest.raises(ValueError):
            bg.validate_params("benchmarks_still_separating", bad)


def test_worker_allowlist_matches_service():
    js = (ROOT / "graph-service/worker/src/index.js").read_text()
    names = set(re.search(r"ALLOWED = new Set\(\[(.*?)\]\)", js, re.S).group(1).replace('"', "")
                .replace(" ", "").replace("\n", "").strip(",").split(","))
    service = _service_module()
    assert names == set(service.ALLOWED)


# ── against FalkorDB ──────────────────────────────────────────────────────────
def test_fixture_round_trip(graph):
    doc = bg.build_document(pages=FIXTURE_PAGES, evidence=FIXTURE_EVIDENCE)
    bg.load_document(graph, json.loads(json.dumps(doc, default=str)))
    back = bg.read_front_matter(graph)
    assert set(back) == {p["id"] for p in FIXTURE_PAGES}
    for page in FIXTURE_PAGES:
        assert bg.mapped_view(page) == bg.mapped_view(back[page["id"]]), page["id"]
    assert bg.unmapped_paths(FIXTURE_PAGES[-1]) == ["dataset.validation", "sources", "freshness"]


def test_every_benchmark_page_round_trips(graph):
    """No data loss for mapped fields across every benchmarks/*.md page."""
    from pipeline.load import load_benchmarks
    benches = load_benchmarks(ROOT)
    doc = bg.build_document(pages=[b.front for b in benches], evidence=[])
    bg.load_document(graph, json.loads(json.dumps(doc)))
    back = bg.read_front_matter(graph)
    lost = {}
    unmapped = set()
    for b in benches:
        want, got = bg.mapped_view(b.front), bg.mapped_view(back.get(b.benchmark_id, {}))
        diff = [k for k in want if want[k] != got[k]]
        if diff:
            lost[b.benchmark_id] = diff
        for path in bg.unmapped_paths(b.front):
            top = path.split(".")[0]
            if top not in bg.UNMAPPED_FIELDS:
                # Stray key: not a BenchmarkCard field at all.
                assert top in bg.SCHEMA_PARENTS or top not in _schema_fields(), path
                unmapped.add(path)
    assert len(back) == len(benches) > 1000
    assert not lost, f"round trip lost data: {dict(list(lost.items())[:10])}"


def _schema_fields():
    from schema.benchmark import BenchmarkCard
    return set(BenchmarkCard.model_fields)


def _rows(graph, **raw):
    return {r["id"]: r for r in bg.run_query(graph, "benchmarks_still_separating",
                                             {k: str(v) for k, v in raw.items()})}


def test_still_separating_query(graph):
    bg.load_document(graph, bg.build_document(pages=FIXTURE_PAGES, evidence=FIXTURE_EVIDENCE))
    rows = _rows(graph, capability="coding", top_n=3, min_spread=5)
    # narrow: spread 1 < 5 -> out; retired: superseded -> out; watched: watch -> out
    assert set(rows) == {"wide", "lower", "unscored"}
    assert rows["wide"]["spread"] == 20 and rows["wide"]["scored_models"] == 3
    assert rows["lower"]["spread"] == 40
    assert rows["unscored"]["spread"] is None
    assert set(_rows(graph, capability="coding", top_n=3, min_spread=5, require_scores="true")) == {"wide", "lower"}
    assert "watched" in _rows(graph, capability="coding", include_watch="true")
    assert set(_rows(graph, capability="coding", top_n=3, min_spread=0.5)) >= {"narrow"}
    assert set(_rows(graph, capability="math")) == {"mathy"}


def test_queries_are_read_only(graph):
    bg.load_document(graph, bg.build_document(pages=FIXTURE_PAGES, evidence=[]))
    with pytest.raises(Exception):
        graph.ro_query("MATCH (n) DELETE n")
    for q in bg.QUERIES.values():
        assert not re.search(r"\b(CREATE|MERGE|DELETE|SET|REMOVE|DROP|CALL)\b", q.cypher, re.I)


# ── query service (no container) ──────────────────────────────────────────────
def _service_module():
    spec = importlib.util.spec_from_file_location("graph_service", ROOT / "graph-service/service.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_query_service_http(graph, tmp_path):
    svc = _service_module()
    bg.write_export(bg.build_document(pages=FIXTURE_PAGES, evidence=FIXTURE_EVIDENCE), tmp_path)
    manifest, doc = bg.read_export(str(tmp_path))
    bg.load_document(graph, doc)
    svc.STATE.update(manifest=manifest, graph=graph, error=None)
    server = ThreadingHTTPServer(("127.0.0.1", 0), svc.Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{server.server_address[1]}"

    def get(path, method="GET"):
        req = urllib.request.Request(base + path, method=method)
        try:
            with urllib.request.urlopen(req) as r:
                return r.status, json.loads(r.read())
        except urllib.error.HTTPError as e:
            return e.code, json.loads(e.read())

    try:
        status, body = get("/graph/health")
        assert status == 200 and body["build_commit"] == manifest["build"]["commit"]
        status, body = get("/graph/benchmarks_still_separating?capability=coding&top_n=3&min_spread=5")
        assert status == 200 and {r["id"] for r in body["rows"]} == {"wide", "lower", "unscored"}
        assert body["build_commit"] == manifest["build"]["commit"]
        assert get("/graph/benchmarks_still_separating?capability=coding&q=MATCH")[0] == 400
        assert get("/graph/benchmarks_still_separating")[0] == 400
        assert get("/graph/benchmarks_still_separating?capability=coding&capability=math")[0] == 400
        assert get("/graph/cypher?q=MATCH%20(n)%20RETURN%20n")[0] == 404
        assert get("/graph/health/../manifest")[0] == 404
        assert get("/graph/manifest", method="POST")[0] == 405
        assert get("/graph/manifest")[1]["manifest"]["format"] == bg.EXPORT_FORMAT
    finally:
        server.shutdown()


# ── service never exposes load errors or the export URL ───────────────────────
SIGNED = "https://bucket.example/benchgraph-graph/latest/manifest.json?X-Amz-Signature=SECRET"


def test_redact_url():
    svc = _service_module()
    assert svc.redact_url("https://user:pw@bucket.example:8443/a/b?X-Amz-Signature=SECRET#frag") == \
        "https://bucket.example:8443/a/b"
    assert svc.redact_url("/export") == "/export"
    assert svc.redact_url("relative/dir") == "relative/dir"
    assert "SECRET" not in svc.redact_message(f"HTTP Error 403 for url {SIGNED}")


def test_load_failure_is_not_exposed(capsys):
    svc = _service_module()

    def boom(source):
        raise OSError(f"urlopen error for {SIGNED} at 10.0.0.7:6379")

    svc.load = boom
    svc.STATE.update(manifest=None, graph=None, error=None, status="loading")
    svc._loader(SIGNED.rsplit("/", 1)[0] + "?X-Amz-Signature=SECRET", attempts=2, sleep=lambda s: None)
    logs = capsys.readouterr()
    assert "SECRET" not in logs.out + logs.err and "X-Amz" not in logs.out + logs.err
    assert "OSError" in logs.err

    server = ThreadingHTTPServer(("127.0.0.1", 0), svc.Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{server.server_address[1]}"
    try:
        for path in ("/graph/health", "/graph/benchmarks_still_separating?capability=coding",
                     "/graph/manifest"):
            try:
                urllib.request.urlopen(base + path)
                raise AssertionError("expected 503")
            except urllib.error.HTTPError as e:
                assert e.code == 503
                body = e.read().decode()
            for bad in ("SECRET", "X-Amz", "example", "urlopen", "OSError", "10.0.0.7"):
                assert bad not in body, (path, body)
            if path == "/graph/health":
                assert json.loads(body) == {"build_commit": None, "format_version": None,
                                            "status": "error", "error": "export_not_loaded"}
            else:
                assert json.loads(body) == {"error": "graph not loaded"}
    finally:
        server.shutdown()


# --- MODEL-9 part 2b: Cloudflare deploy wiring ----------------------------

WRANGLER = ROOT / "graph-service" / "worker" / "wrangler.jsonc"
WORKFLOW = ROOT / ".github" / "workflows" / "benchgraph-graph.yml"


def _jsonc(text: str) -> dict:
    return json.loads(re.sub(r"^\s*//.*$", "", text, flags=re.M))


def _deploy_job() -> tuple[dict, dict]:
    import yaml

    wf = yaml.safe_load(WORKFLOW.read_text())
    return wf, wf["jobs"]["deploy"]


def test_wrangler_config_is_filled_in():
    text = WRANGLER.read_text()
    assert not re.search(r"<[A-Z_]+>", text)
    cfg = _jsonc(text)
    assert cfg["account_id"] == "43840d11c8c4586acdba8b048414900a"
    from urllib.parse import urlparse

    url = urlparse(cfg["vars"]["GRAPH_EXPORT_URL"])
    assert url.scheme == "https" and url.hostname == "graph-exports.benchgraph.dev"
    assert url.path == "/benchgraph-graph/latest"
    assert cfg["routes"] == [
        {"pattern": "graph.benchgraph.dev/graph/*", "zone_name": "benchgraph.dev"}
    ]


def test_deploy_job_only_on_push_to_main_with_graph_token():
    wf, job = _deploy_job()
    assert job["needs"] == "graph"
    cond = job["if"].replace(" ", "")
    assert "github.event_name=='push'" in cond and "github.ref=='refs/heads/main'" in cond
    assert "&&" in cond and "||" not in cond
    assert job["permissions"] == {"contents": "read"}
    assert job["concurrency"]["cancel-in-progress"] is False
    assert job["env"]["CLOUDFLARE_API_TOKEN"] == "${{ secrets.CLOUDFLARE_GRAPH_API_TOKEN }}"
    text = WORKFLOW.read_text()
    assert "secrets.CLOUDFLARE_API_TOKEN" not in text
    # Secrets live on the deploy job only, never on the PR-reachable export job.
    assert "secrets." not in json.dumps(wf["jobs"]["graph"])
    assert "secrets." not in json.dumps({k: v for k, v in wf.items() if k != "jobs"})


def test_deploy_uploads_manifest_last():
    _, job = _deploy_job()
    upload = next(s["run"] for s in job["steps"] if "R2" in s.get("name", ""))
    order = re.search(r"for f in ([^;]+);", upload).group(1).split()
    assert order[-1] == "manifest.json" and set(order[:-1]) == {"nodes.json", "edges.json"}
    assert "benchgraph-graph/${GITHUB_SHA}" in upload and "benchgraph-graph/latest" in upload
    assert "--remote" in upload
    steps = [s.get("name", "") for s in job["steps"]]
    assert steps.index("Deploy Worker and Container") > steps.index(
        "Upload the export to R2 (manifest last)")
