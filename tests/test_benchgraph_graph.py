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


def test_read_export_http_sends_user_agent(tmp_path, monkeypatch):
    doc = bg.build_document(pages=FIXTURE_PAGES, evidence=FIXTURE_EVIDENCE)
    bg.write_export(doc, tmp_path)
    seen = []

    class _Resp:
        def __init__(self, data):
            self._data = data

        def read(self):
            return self._data

        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

    def fake_urlopen(req, timeout=None):
        assert isinstance(req, urllib.request.Request)
        seen.append(req)
        return _Resp((tmp_path / req.full_url.rsplit("/", 1)[1]).read_bytes())

    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
    manifest, loaded = bg.read_export("https://graph-exports.example/benchgraph-graph/latest/")
    assert loaded["nodes"] == json.loads(json.dumps(doc["nodes"]))
    assert [r.full_url.rsplit("/", 1)[1] for r in seen] == ["manifest.json", "nodes.json", "edges.json"]
    for req in seen:
        ua = req.get_header("User-agent")
        assert ua and not ua.startswith("Python-urllib")
        assert ua == bg.EXPORT_USER_AGENT


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


def test_redact_diagnostic_drops_host_and_caps_length():
    """The health diagnostic says what failed, never where the export lives."""
    svc = _service_module()
    assert svc.redact_diagnostic(f"HTTP Error 403 for url {SIGNED}") == \
        "HTTP Error 403 for url <url>"
    assert svc.redact_diagnostic("connect to 10.0.0.7:6379 refused") == "connect to <host> refused"
    assert svc.redact_diagnostic("a\n  b") == "a b"
    assert len(svc.redact_diagnostic("x" * 500)) == svc.MAX_DIAGNOSTIC


def test_load_failure_is_not_exposed(capsys):
    svc = _service_module()

    def boom(source):
        raise OSError(f"urlopen error for {SIGNED} at 10.0.0.7:6379")

    svc.load = boom
    svc.STATE.update(manifest=None, graph=None, error=None, status="loading",
                     last_error=None, attempts=0)
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
            # Never on any route: the signed URL, its host, or the FalkorDB address.
            for bad in ("SECRET", "X-Amz", "example", "10.0.0.7", "6379"):
                assert bad not in body, (path, body)
            if path == "/graph/health":
                # health alone carries the redacted loader diagnostic (MODEL-9),
                # so a container that never loads is diagnosable from outside.
                assert json.loads(body) == {
                    "build_commit": None, "format_version": None, "status": "error",
                    "service_commit": None,
                    "error": "export_not_loaded", "attempts": 2,
                    "last_error": {"exception": "OSError",
                                   "message": "urlopen error for <url> at <host>"}}
            else:
                assert "OSError" not in body and "urlopen" not in body
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
    # The container loads the export through the Worker's R2 binding, never the
    # public custom domain (unreachable from the container in production).
    js = (ROOT / "graph-service/worker/src/index.js").read_text()
    export_js = (ROOT / "graph-service/worker/src/export.js").read_text()
    host = re.search(r'EXPORT_HOST = "([^"]+)"', export_js).group(1)
    assert url.scheme == "http" and url.hostname == host and host.endswith(".internal")
    assert url.path == "/benchgraph-graph/latest"
    assert cfg["r2_buckets"] == [{"binding": "EXPORTS", "bucket_name": "benchgraph-graph-exports"}]
    assert "GraphContainer.outboundByHost = { [EXPORT_HOST]: serveExport };" in js
    assert "export { ContainerProxy }" in js
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


def test_worker_export_handler_is_read_only_and_scoped():
    """serveExport answers GET for the three export files only (run under node)."""
    js = (ROOT / "graph-service/worker/src/export.js").read_text()
    assert "import " not in js
    assert ".list(" not in js and ".put(" not in js and ".delete(" not in js
    script = r"""
import { serveExport } from "./src/export.js";
const store = {"benchgraph-graph/latest/manifest.json": "{}"};
const env = { EXPORTS: { get: async (k) => k in store ? object(store[k]) : null } };
// `body` is the R2 stream serveExport must NOT hand back: reading it fails the
// test, which is what pins the buffered response in place.
function object(text) {
  return { arrayBuffer: async () => new TextEncoder().encode(text).buffer,
           get body() { throw new Error("streamed the R2 body"); } };
}
const h = "http://graph-export.internal";
const r = async (p, m="GET") => (await serveExport(new Request(h + p, {method: m}), env)).status;
console.log(JSON.stringify([
  await r("/benchgraph-graph/latest/manifest.json"),
  await r("/benchgraph-graph/latest/nodes.json"),
  await r("/benchgraph-graph/latest/manifest.json", "PUT"),
  await r("/benchgraph-graph/latest/"),
  await r("/benchgraph-graph/abc/manifest.json"),
  await r("/benchgraph-graph/latest/../latest/manifest.json"),
]));
"""
    assert _run_node(script, "_serve_export_check.mjs") == [200, 404, 405, 404, 404, 200]


def test_container_failures_are_visible_in_worker_logs():
    """MODEL-9: the container's own stdout/stderr does not reach `wrangler tail`.

    Container logs go to the dashboard Container logs page (which needs
    `observability` on the Worker); tail only sees Worker-side logs. So the
    lifecycle hooks and the export interception must log from the Worker.
    """
    index_js = (ROOT / "graph-service/worker/src/index.js").read_text()
    export_js = (ROOT / "graph-service/worker/src/export.js").read_text()
    assert "onError(error)" in index_js and "console.error(" in index_js
    assert "onStart()" in index_js and "onStop(" in index_js
    # No log line for a route means the container never asked for the export,
    # which is what distinguishes a broken interception from a broken load. The
    # byte count distinguishes "answered" from "answered with nothing".
    assert "console.log(`export ${request.method} ${url.pathname} -> " \
        "${result.status} ${bytes.byteLength}B`)" in export_js
    assert _jsonc(WRANGLER.read_text())["observability"] == {"enabled": True}


# --- MODEL-9 part 2: the deploy must roll the container -------------------
# A `wrangler deploy` leaves a running container alone, and the deploy's own
# smoke test keeps it awake past `sleepAfter`, so the just-deployed image was
# never exercised (#77, #78 and #79 all shipped that way). BUILD_COMMIT is the
# deployed version: the Durable Object destroys an instance left over from an
# earlier one, and the container reports the value it was started with back as
# `service_commit`.

ROLLOUT_JS = ROOT / "graph-service/worker/src/rollout.js"


def test_service_reports_the_version_it_was_started_for(monkeypatch, tmp_path):
    """`service_commit` identifies the running image; `build_commit` the export."""
    monkeypatch.setenv("BUILD_COMMIT", "deadbeef")
    svc = _service_module()
    assert svc.SERVICE_COMMIT == "deadbeef"
    bg.write_export(bg.build_document(pages=FIXTURE_PAGES, evidence=[]), tmp_path)
    manifest, _ = bg.read_export(str(tmp_path))
    # Loaded: both markers present and independent of each other.
    svc.STATE.update(manifest=manifest, graph=None, error=None, status="ok")
    assert svc.Handler._base(svc.Handler) == {
        "build_commit": manifest["build"]["commit"],
        "format_version": manifest["format_version"],
        "service_commit": "deadbeef"}
    # Not loaded: the image still says which version it is, so "wrong version"
    # and "right version, failed to load" stay apart.
    svc.STATE.update(manifest=None, graph=None, status="error")
    assert svc.Handler._base(svc.Handler)["service_commit"] == "deadbeef"

    monkeypatch.delenv("BUILD_COMMIT")
    assert _service_module().SERVICE_COMMIT is None


def _run_node(script: str, name: str):
    """Run an ES module in graph-service/worker and return its parsed last line."""
    import shutil
    import subprocess

    node = shutil.which("node")
    if not node:
        pytest.skip("node not installed")
    worker = ROOT / "graph-service/worker"
    stub = worker / name
    stub.write_text(script)
    try:
        out = subprocess.run([node, stub.name], cwd=worker, capture_output=True,
                             text=True, timeout=60)
    finally:
        stub.unlink()
    assert out.returncode == 0, out.stderr
    return json.loads(out.stdout.strip().splitlines()[-1])


def test_rollout_module_has_no_imports():
    """Runnable under plain node: the test job never installs the worker deps."""
    assert "import " not in ROLLOUT_JS.read_text()


def test_container_rolls_once_per_deployed_version():
    """Mismatch rolls exactly once; a matching version never rolls."""
    script = r"""
import { rollStaleContainer, staleHealth, ROLLED_KEY } from "./src/rollout.js";

function fake(running) {
  const store = new Map();
  const c = { running, destroys: 0, throws: false,
              async destroy() { this.destroys++; if (this.throws) throw new Error("boom");
                                this.running = false; } };
  return { kv: { get: (k) => store.get(k), put: (k, v) => store.set(k, v) }, container: c,
           store };
}
const roll = (f, want) => rollStaleContainer({ kv: f.kv, container: f.container, want });
const out = {};

// A container left from an earlier version is destroyed once, and the marker
// survives into the next request (and the next DO incarnation).
const stale = fake(true);
out.stale = [await roll(stale, "v2"), await roll(stale, "v2"), await roll(stale, "v2")];
out.staleDestroys = stale.container.destroys;
out.marker = stale.store.get(ROLLED_KEY);

// Already rolled for this version and still running: a container that keeps
// failing to load its export must not be killed on every request.
const current = fake(true);
current.kv.put(ROLLED_KEY, "v2");
out.current = [await roll(current, "v2"), await roll(current, "v2")];
out.currentDestroys = current.container.destroys;

// Nothing running yet (first ever request, or after sleepAfter): nothing to kill.
const cold = fake(false);
out.cold = await roll(cold, "v2");
out.coldDestroys = cold.container.destroys;
out.coldMarker = cold.store.get(ROLLED_KEY);

// No BUILD_COMMIT (local `wrangler dev` without the var): never roll.
const dev = fake(true);
out.dev = await roll(dev, "");
out.devDestroys = dev.container.destroys;
out.devMarker = dev.store.get(ROLLED_KEY) ?? null;

// A destroy that throws is still only attempted once: marker written first.
const broken = fake(true);
broken.container.throws = true;
out.brokenThrew = await roll(broken, "v3").then(() => false, () => true);
out.broken = await roll(broken, "v3");
out.brokenDestroys = broken.container.destroys;

// A newer version rolls again, exactly once.
out.next = [await roll(current, "v3"), await roll(current, "v3")];
out.nextDestroys = current.container.destroys;

// health gating: wrong version vs right version that failed to load.
out.match = staleHealth({ service_commit: "v2", status: "ok" }, "v2");
out.failedLoad = staleHealth({ service_commit: "v2", error: "export_not_loaded" }, "v2");
out.mismatch = staleHealth({ service_commit: "v1", status: "ok" }, "v2");
out.absent = staleHealth({ status: "ok" }, "v2");
out.unparseable = staleHealth(null, "v2");
out.unversioned = staleHealth({ service_commit: "v1" }, "");
console.log(JSON.stringify(out));
"""
    out = _run_node(script, "_rollout_check.mjs")
    # One roll per version, no restart loop.
    assert out["stale"] == ["rolled", "current", "current"] and out["staleDestroys"] == 1
    assert out["marker"] == "v2"
    assert out["current"] == ["current", "current"] and out["currentDestroys"] == 0
    assert out["cold"] == "fresh" and out["coldDestroys"] == 0 and out["coldMarker"] == "v2"
    assert out["dev"] == "unversioned" and out["devDestroys"] == 0 and out["devMarker"] is None
    # The marker is written before destroy(), so a failing destroy cannot loop.
    assert out["brokenThrew"] is True
    assert out["broken"] == "current" and out["brokenDestroys"] == 1
    # The next deployed version rolls again, once.
    assert out["next"] == ["rolled", "current"] and out["nextDestroys"] == 1
    # "right version, failed to load" passes through; "wrong version" does not.
    assert out["match"] is None and out["failedLoad"] is None and out["unversioned"] is None
    for key in ("mismatch", "absent", "unparseable"):
        assert out[key]["error"] == "version_rolling", key
        assert out[key]["expected_service_commit"] == "v2", key
    assert out["mismatch"]["service_commit"] == "v1"
    assert out["absent"]["service_commit"] is None


def test_worker_rolls_the_container_and_gates_health():
    """The Durable Object rolls before proxying, and health is version-gated.

    index.js imports @cloudflare/containers, which the test job does not
    install, so this asserts the wiring in the source.
    """
    js = (ROOT / "graph-service/worker/src/index.js").read_text()
    assert 'import { rollStaleContainer, staleHealth } from "./rollout.js"' in js
    # The container is started with the deployed version, so it can report it.
    assert 'BUILD_COMMIT: env.BUILD_COMMIT ?? ""' in js
    assert "GRAPH_EXPORT_URL: env.GRAPH_EXPORT_URL" in js
    # The roll runs inside the Durable Object's fetch, before super.fetch, so
    # every route gets a fresh instance and not just /graph/health.
    roll = re.search(r"async fetch\(request\) \{(.*?)\n  \}", js, re.S).group(1)
    assert "rollStaleContainer({" in roll
    assert "kv: this.ctx.storage.kv" in roll and "container: this.ctx.container" in roll
    assert "want: this.env.BUILD_COMMIT" in roll
    assert roll.index("rollStaleContainer") < roll.index("super.fetch(request)")
    # The gate turns a stale answer into a loud 503 instead of a 200.
    gate = re.search(r"async function gateHealth\(.*?\n\}", js, re.S).group(0)
    assert "staleHealth(body, want)" in gate and "503" in gate
    assert "gateHealth(response, env.BUILD_COMMIT" in js
    # Public surface unchanged: still GET/HEAD only, still the same allowlist.
    assert 'request.method !== "GET" && request.method !== "HEAD"' in js
    assert ".put(" not in js and ".delete(" not in js and ".list(" not in js


def test_deploy_injects_the_version_and_smoke_asserts_a_fresh_instance():
    _, job = _deploy_job()
    steps = {s.get("name", ""): s.get("run", "") for s in job["steps"]}
    deploy = steps["Deploy Worker and Container"]
    assert 'wrangler deploy --var "BUILD_COMMIT:${GITHUB_SHA}"' in deploy
    smoke = steps["Smoke-test graph.benchgraph.dev"]
    # Both markers, and the loop only breaks when both equal the pushed sha.
    assert "service=$(field service_commit)" in smoke
    assert "commit=$(field build_commit)" in smoke
    assert '[ "$service" = "${GITHUB_SHA}" ] && [ "$commit" = "${GITHUB_SHA}" ]' in smoke
    # A version that never rolls fails loudly, and says so specifically.
    assert '::error::the container never rolled onto ${GITHUB_SHA}' in smoke
    assert 'if [ "$service" != "${GITHUB_SHA}" ]; then' in smoke
    assert smoke.count("exit 1") == 3
    # The PR-reachable container smoke proves the image echoes BUILD_COMMIT back.
    ci = next(s["run"] for s in _deploy_job()[0]["jobs"]["graph"]["steps"]
              if s.get("name") == "Smoke-test the query container")
    assert '-e "BUILD_COMMIT=${GITHUB_SHA}"' in ci and "service_commit" in ci
    # Local dev still has a value, so a `wrangler dev` container is not rolled
    # on every request.
    assert _jsonc(WRANGLER.read_text())["vars"]["BUILD_COMMIT"] == "dev"


# --- MODEL-9 part 2: the intercepted export fetch must deliver bytes ------
# A fresh container on post-#79 code logged Worker events with outcome Ok for
# every intercepted GET, while the loader saw `HTTPError: HTTP Error 530:` with
# an empty body on all 21 attempts. Both surviving explanations end here: the
# response is buffered with a content-length instead of handing back an R2
# stream the handler has already returned from, and a request that matches no
# handler is refused and named instead of falling through to a public fetch of a
# hostname that does not resolve (which the runtime answers with an empty 530
# while the Worker event still reads Ok).


def test_intercepted_export_delivers_buffered_bytes():
    script = r"""
import { serveExport, blockOutbound } from "./src/export.js";
const payload = JSON.stringify({ format: "benchgraph-export", n: "x".repeat(4096) });
const env = { EXPORTS: { get: async (k) =>
  k === "benchgraph-graph/latest/manifest.json"
    ? { arrayBuffer: async () => new TextEncoder().encode(payload).buffer,
        get body() { throw new Error("streamed the R2 body"); } }
    : k === "benchgraph-graph/latest/nodes.json"
      ? { arrayBuffer: async () => { throw new Error("r2 exploded"); } }
      : null } };
const h = "http://graph-export.internal";
const get = (p) => serveExport(new Request(h + p, { method: "GET" }), env);
const out = {};

const ok = await get("/benchgraph-graph/latest/manifest.json");
out.status = ok.status;
out.length = ok.headers.get("content-length");
out.type = ok.headers.get("content-type");
out.text = await ok.text();
out.delivered = out.text.length === payload.length && out.text === payload;

// A throw inside the handler becomes a readable 502, not an opaque failure.
const boom = await get("/benchgraph-graph/latest/nodes.json");
out.boom = [boom.status, await boom.text()];

// Any other host is refused and logged, never fetched.
const blocked = await blockOutbound(new Request("http://example.com/x", { method: "GET" }));
out.blocked = [blocked.status, await blocked.text()];
console.log(JSON.stringify(out));
"""
    out = _run_node(script, "_export_delivery_check.mjs")
    # Buffered: reading the R2 stream would have thrown, and the bytes arrive.
    assert out["status"] == 200 and out["delivered"] is True
    assert out["length"] == str(len(out["text"].encode())) and out["length"] != "0"
    assert out["type"] == "application/json"
    assert out["boom"][0] == 502 and "unavailable" in out["boom"][1]
    assert out["blocked"][0] == 502


def test_container_egress_has_no_silent_fallthrough():
    """An unmatched host must be named and refused, not fetched from the Worker."""
    index_js = (ROOT / "graph-service/worker/src/index.js").read_text()
    export_js = (ROOT / "graph-service/worker/src/export.js").read_text()
    code = re.sub(r"^\s*//.*$", "", export_js, flags=re.M)
    # The catch-all is what promotes the library out of per-host mode, where an
    # unmatched host reaches `fetch(request)`.
    assert "GraphContainer.outbound = blockOutbound;" in index_js
    assert "fetch(" not in code
    assert "console.error(`outbound blocked:" in code
    # enableInternet stays default: 0.3.7 still notes DNS does not work with it off.
    assert "enableInternet" not in re.sub(r"^\s*//.*$", "", index_js, flags=re.M)
    # Every intercepted answer is buffered and framed.
    assert "await object.arrayBuffer()" in code
    assert '"content-length": String(bytes.byteLength)' in code
    assert "object.body" not in code


CONTAINERS_LIB = (ROOT / "graph-service/worker/node_modules/@cloudflare/containers"
                  / "dist/lib/container.js")


def test_outbound_handlers_are_assigned_not_declared_as_static_fields():
    """The proven cause of the container's 530 (cloudflare/containers#247).

    `Container` declares `outboundByHost` and `outbound` as static *accessor
    pairs* whose setters are the only writers of the registries `ContainerProxy`
    reads. A native `static` field defines an own property on the subclass
    instead of invoking the inherited setter, so the registry stays empty while
    the class still reads back the shadowing object: interception is armed (the
    host is registered from `ctor.outboundByHost`), `ContainerProxy` finds no
    handler, and falls through to `return fetch(request)` — a real subrequest for
    a hostname that does not resolve, which answers 530 with an empty body while
    the Worker event's outcome is still Ok. Assignment invokes the setter.
    """
    index_js = (ROOT / "graph-service/worker/src/index.js").read_text()
    body = index_js[index_js.index("export class GraphContainer"):]
    body = body[:body.index("\n}\n")]
    assert "static outboundByHost" not in body and "static outbound" not in body
    assert "GraphContainer.outboundByHost = " in index_js
    assert "GraphContainer.outbound = " in index_js

    if CONTAINERS_LIB.exists():
        # The premise: still accessor pairs backed by module-level registries.
        lib = CONTAINERS_LIB.read_text()
        for name in ("outboundByHost", "outbound"):
            assert f"static get {name}()" in lib and f"static set {name}(" in lib
        assert "const outboundByHostRegistry = new Map();" in lib
        # And the fall-through that turns a registry miss into a public fetch.
        assert "if (allowedHosts || enableInternet) {\n                return fetch(request);" in lib

    # And the semantics themselves, against the same accessor-pair shape.
    script = r"""
const registry = new Map();
class Base {
  static get outboundByHost() { return registry.get(this.name); }
  static set outboundByHost(h) { registry.set(this.name, h); }
}
class Field extends Base { static outboundByHost = { host: "handler" }; }
class Assigned extends Base {}
Assigned.outboundByHost = { host: "handler" };
console.log(JSON.stringify({
  // The shape the Worker used to have: reads back fine, registers nothing.
  fieldRegistered: registry.has("Field"),
  fieldReadsBack: Field.outboundByHost !== undefined,
  assignedRegistered: registry.has("Assigned"),
  assignedHandler: registry.get("Assigned")?.host ?? null,
}));
"""
    out = _run_node(script, "_static_field_shadowing_check.mjs")
    assert out == {"fieldRegistered": False, "fieldReadsBack": True,
                   "assignedRegistered": True, "assignedHandler": "handler"}
