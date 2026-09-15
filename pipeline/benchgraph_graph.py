"""The benchgraph graph: benchmark pages as FalkorDB nodes and edges (MODEL-9).

`benchmarks/*.md` is canonical. This module never edits Markdown and nothing
edits the graph by hand: the graph is rebuilt from the pages every time.

Pipeline::

    benchmarks/*.md + models/*.md evidence
        -> build_document()            portable nodes/edges (plain JSON)
        -> write_export()              dist/benchgraph-graph/{manifest,nodes,edges}.json
        -> load_document(graph, doc)   the same loader CI and the container use
        -> read_front_matter(graph)    graph -> front-matter dicts (round-trip proof)

The container (graph-service/) runs only the named, read-only queries in
`QUERIES`, through GRAPH.RO_QUERY. See docs/benchgraph-graph.md.

CLI::

    python -m pipeline.benchgraph_graph export --out dist/benchgraph-graph/ [--verify]
    python -m pipeline.benchgraph_graph query benchmarks_still_separating capability=coding
"""

from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import json
import os
import re
import subprocess
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

REPO_ROOT = Path(__file__).resolve().parent.parent
GRAPH_NAME = "benchgraph"
EXPORT_FORMAT = "benchgraph-graph"
#: New artefact under MODEL-59: additive, so it starts at 1.0 and bumps no
#: existing contract (`build.export_schema_version`, CLI `schema_version`).
EXPORT_FORMAT_VERSION = "1.0"
#: The FalkorDB image the loader and queries are tested against (CI service,
#: container base). The export itself is JSON and does not depend on it.
FALKORDB_IMAGE = "falkordb/falkordb:v4.20.1"

# ── field mapping ─────────────────────────────────────────────────────────────
#: Front-matter leaves stored as Benchmark node properties ("a.b" -> "a__b").
NODE_FIELDS: tuple[str, ...] = (
    "id", "name", "aliases", "page_kind", "subcategory", "status", "summary",
    "measures", "task_format",
    "metric.name", "metric.direction", "metric.unit", "metric.max_score",
    "metric.random_baseline", "metric.human_baseline", "metric.baseline_note",
    "dataset.size", "dataset.size_note", "dataset.license", "dataset.languages",
    "dataset.modalities", "dataset.splits", "dataset.public_test_set",
    "paper.title", "paper.arxiv", "paper.url", "paper.year",
    "leaderboard_url", "repo_url", "released", "last_updated",
    "saturation.status", "saturation.top_score", "saturation.as_of", "saturation.note",
    "contamination.risk", "contamination.note",
    "harness.lm_eval", "harness.inspect_evals", "harness.helm",
    "harness.opencompass", "harness.bigbench", "harness.other",
    "tags",
)
#: Front-matter leaves carried by an edge instead of a node property.
#: field -> (edge type, target label, direction, edge-property fields)
EDGE_SCALARS: dict[str, tuple[str, str]] = {
    "category": ("MEASURES", "Capability"),
    "lineage.family": ("BELONGS_TO", "Family"),
    "publisher.org": ("PUBLISHED_BY", "Publisher"),
    "dataset.url": ("USES_DATASET", "Dataset"),
    # (b)-[:SUPERSEDES]->(predecessor)
    "lineage.predecessor": ("SUPERSEDES", "Benchmark"),
}
#: List leaves carried by edges. Each list element is one edge with `pos`.
EDGE_LISTS: dict[str, tuple[str, str, bool]] = {
    # (successor)-[:SUPERSEDES]->(b): reversed direction
    "lineage.successors": ("SUPERSEDES", "Benchmark", True),
    # (variant)-[:VARIANT_OF]->(b): reversed direction
    "lineage.variants": ("VARIANT_OF", "Benchmark", True),
}
#: Leaves stored as properties of the PUBLISHED_BY edge (they describe this
#: page's view of the publisher, not the organisation node).
PUBLISHER_EDGE_FIELDS = ("publisher.authors", "publisher.url")

MAPPED_FIELDS: tuple[str, ...] = tuple(
    sorted(NODE_FIELDS + tuple(EDGE_SCALARS) + tuple(EDGE_LISTS) + PUBLISHER_EDGE_FIELDS)
)
#: Schema fields intentionally not in the graph. Markdown stays canonical for
#: them; the graph answers structural questions, not citation lookups.
UNMAPPED_FIELDS: dict[str, str] = {
    "sources": "citations; a list of objects, read from the Markdown page",
    "freshness": "research bookkeeping (researched/reviewed by and when)",
    "models_covered": "must never be authored; derived at site build",
    "body": "the Markdown article itself",
}
#: Schema leaves under a mapped parent. Anything under a known parent that is
#: not one of these is a stray YAML key (a parse accident) and is unmapped.
SCHEMA_PARENTS = ("metric", "dataset", "publisher", "paper", "lineage", "saturation",
                  "contamination", "harness")


def _prop(field: str) -> str:
    return field.replace(".", "__")


def _get(front: dict[str, Any], field: str) -> Any:
    cur: Any = front
    for part in field.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return None
        cur = cur[part]
    return cur


# ── value encoding (FalkorDB stores primitives and arrays of primitives) ──────
def _primitive(v: Any) -> bool:
    return isinstance(v, (str, int, float, bool)) and not isinstance(v, (_dt.date,))


def encode(value: Any) -> Any:
    """Return a FalkorDB-storable value that `decode` turns back into `value`.

    Primitives and lists of primitives are stored as they are. Anything else
    (nested objects, dates YAML parsed, lists with nulls) is stored as a tagged
    JSON string so nothing is lost silently.
    """
    if _primitive(value):
        if isinstance(value, str) and value.startswith("@@json:"):
            return "@@json:" + json.dumps(value)
        return value
    if isinstance(value, list) and all(_primitive(v) for v in value):
        return value
    return "@@json:" + json.dumps(value, default=_json_default, sort_keys=True)


def _json_default(v: Any) -> Any:
    if isinstance(v, (_dt.date, _dt.datetime)):
        return {"__date__": v.isoformat()}
    raise TypeError(f"cannot encode {type(v).__name__}")


def _json_hook(obj: dict[str, Any]) -> Any:
    if set(obj) == {"__date__"}:
        s = obj["__date__"]
        return _dt.datetime.fromisoformat(s) if "T" in s else _dt.date.fromisoformat(s)
    return obj


def decode(value: Any) -> Any:
    if isinstance(value, str) and value.startswith("@@json:"):
        return json.loads(value[len("@@json:"):], object_hook=_json_hook)
    return value


# ── document build (no database needed) ───────────────────────────────────────
def _commit(root: Path) -> str:
    env = os.environ.get("GITHUB_SHA")
    if env:
        return env
    try:
        return subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"], check=True,
                              capture_output=True, text=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def _nonempty_id(v: Any) -> bool:
    return isinstance(v, str) and v != ""


def build_document(root: Path | None = None, *, pages: list[dict[str, Any]] | None = None,
                   evidence: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    """Build the portable graph document from front matter.

    `pages` and `evidence` override reading the repository (used by tests).
    """
    root = root or REPO_ROOT
    if pages is None:
        from pipeline.load import load_benchmarks, load_models
        pages = [b.front for b in load_benchmarks(root)]
        evidence = []
        for m in load_models(root):
            bench = m.front.get("benchmarks")
            recs = bench.get("evidence") if isinstance(bench, dict) else None
            for rec in recs or []:
                if isinstance(rec, dict):
                    evidence.append({**rec, "_model_id": m.model_id})
    evidence = evidence or []

    nodes: dict[tuple[str, str], dict[str, Any]] = {}
    edges: list[dict[str, Any]] = []

    def node(label: str, key: str, props: dict[str, Any] | None = None) -> None:
        cur = nodes.setdefault((label, key), {"label": label, "id": key, "props": {}})
        if props:
            cur["props"].update(props)

    page_ids = {str(p["id"]) for p in pages}
    for page in pages:
        bid = str(page["id"])
        props: dict[str, Any] = {}
        for field in NODE_FIELDS:
            v = _get(page, field)
            if v is not None and field != "id":
                props[_prop(field)] = encode(v)
        node("Benchmark", bid, {**props, "stub": False})

        for field, (etype, label) in EDGE_SCALARS.items():
            v = _get(page, field)
            if _nonempty_id(v):
                node(label, v)
                eprops: dict[str, Any] = {"declared_in": bid, "field": field}
                if field == "publisher.org":
                    for pf in PUBLISHER_EDGE_FIELDS:
                        pv = _get(page, pf)
                        if pv is not None:
                            eprops[pf.split(".")[1]] = encode(pv)
                edges.append({"type": etype, "from": ["Benchmark", bid], "to": [label, v],
                              "props": eprops})
            elif v is not None:
                # "" or an odd type: keep the raw value on the node.
                nodes[("Benchmark", bid)]["props"][_prop(field) + "__raw"] = encode(v)
            if field == "publisher.org" and not _nonempty_id(v):
                for pf in PUBLISHER_EDGE_FIELDS:
                    pv = _get(page, pf)
                    if pv is not None:
                        nodes[("Benchmark", bid)]["props"][_prop(pf) + "__raw"] = encode(pv)

        for field, (etype, label, reverse) in EDGE_LISTS.items():
            v = _get(page, field)
            if isinstance(v, list) and all(_nonempty_id(x) for x in v):
                nodes[("Benchmark", bid)]["props"][_prop(field) + "__len"] = len(v)
                for pos, target in enumerate(v):
                    node(label, target)
                    ends = (["Benchmark", target], ["Benchmark", bid]) if reverse else \
                           (["Benchmark", bid], ["Benchmark", target])
                    edges.append({"type": etype, "from": ends[0], "to": ends[1],
                                  "props": {"declared_in": bid, "field": field, "pos": pos}})
            elif v is not None:
                nodes[("Benchmark", bid)]["props"][_prop(field) + "__raw"] = encode(v)

    # Lineage targets without a page become stubs.
    for (label, key), n in nodes.items():
        if label == "Benchmark" and key not in page_ids:
            n["props"].setdefault("stub", True)

    skipped = Counter()
    for rec in evidence:
        bid = rec.get("benchmark_id")
        if bid not in page_ids:
            skipped["benchmark_without_page"] += 1
            continue
        score = rec.get("score")
        if not isinstance(score, (int, float)) or isinstance(score, bool):
            skipped["non_numeric_score"] += 1
            continue
        mid = str(rec["_model_id"])
        node("Model", mid)
        eprops = {
            "value": float(score),
            "unit": rec.get("unit"),
            "date": str(rec.get("evidence_date") or ""),
            "date_type": rec.get("date_type"),
            "source": rec.get("source_url"),
            "source_kind": rec.get("source_kind"),
            "protocol": rec.get("configuration"),
            "benchmark_version": rec.get("benchmark_version"),
            "model_id_as_evaluated": rec.get("model_id_as_evaluated"),
            "verified_at": str(rec.get("verified_at") or ""),
        }
        edges.append({"type": "SCORED_ON", "from": ["Model", mid], "to": ["Benchmark", bid],
                      "props": {k: v for k, v in eprops.items() if v is not None}})

    node_list = sorted(nodes.values(), key=lambda n: (n["label"], n["id"]))
    edges.sort(key=lambda e: (e["type"], e["from"], e["to"], json.dumps(e["props"], sort_keys=True)))
    return {"nodes": node_list, "edges": edges, "skipped_evidence": dict(skipped),
            "benchmark_pages": len(pages)}


# ── export files ──────────────────────────────────────────────────────────────
def _dump(obj: Any) -> bytes:
    return (json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode()


def write_export(doc: dict[str, Any], out: Path, root: Path | None = None) -> dict[str, Any]:
    out.mkdir(parents=True, exist_ok=True)
    files: dict[str, dict[str, Any]] = {}
    for name, payload in (("nodes.json", doc["nodes"]), ("edges.json", doc["edges"])):
        data = _dump(payload)
        (out / name).write_bytes(data)
        files[name] = {"sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)}
    manifest = {
        "format": EXPORT_FORMAT,
        "format_version": EXPORT_FORMAT_VERSION,
        "graph_name": GRAPH_NAME,
        "build": {"commit": _commit(root or REPO_ROOT),
                  "generated_at": _dt.datetime.now(_dt.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")},
        "falkordb_tested": FALKORDB_IMAGE,
        "counts": {
            "benchmark_pages": doc["benchmark_pages"],
            "nodes": dict(sorted(Counter(n["label"] for n in doc["nodes"]).items())),
            "edges": dict(sorted(Counter(e["type"] for e in doc["edges"]).items())),
            "stub_benchmarks": sum(1 for n in doc["nodes"]
                                   if n["label"] == "Benchmark" and n["props"].get("stub")),
            "skipped_evidence": doc["skipped_evidence"],
        },
        "files": files,
        "mapped_fields": list(MAPPED_FIELDS),
        "unmapped_fields": UNMAPPED_FIELDS,
        "queries": sorted(QUERIES),
    }
    (out / "manifest.json").write_bytes(json.dumps(manifest, indent=2, sort_keys=True).encode() + b"\n")
    return manifest


EXPORT_USER_AGENT = "modelspec-graph-service/1.0 (+https://benchgraph.dev)"


def read_export(source: str) -> tuple[dict[str, Any], dict[str, Any]]:
    """Read an export from a directory path, file:// URL or http(s):// base URL.

    Verifies each file against the manifest's sha256.
    """
    def fetch(name: str) -> bytes:
        if source.startswith(("http://", "https://")):
            import urllib.request
            url = source.rstrip("/") + "/" + name
            # Cloudflare answers the default Python-urllib User-Agent with 403.
            req = urllib.request.Request(url, headers={"User-Agent": EXPORT_USER_AGENT})
            with urllib.request.urlopen(req, timeout=60) as r:  # noqa: S310 - scheme checked
                return r.read()
        path = source[len("file://"):] if source.startswith("file://") else source
        return (Path(path) / name).read_bytes()

    manifest = json.loads(fetch("manifest.json"))
    if manifest.get("format") != EXPORT_FORMAT:
        raise ValueError(f"not a {EXPORT_FORMAT} export")
    if str(manifest.get("format_version", "")).split(".")[0] != EXPORT_FORMAT_VERSION.split(".")[0]:
        raise ValueError(f"export format {manifest.get('format_version')} is not {EXPORT_FORMAT_VERSION}")
    parts = {}
    for name in ("nodes.json", "edges.json"):
        data = fetch(name)
        want = manifest["files"][name]["sha256"]
        if hashlib.sha256(data).hexdigest() != want:
            raise ValueError(f"{name} does not match the manifest sha256")
        parts[name] = json.loads(data)
    return manifest, {"nodes": parts["nodes.json"], "edges": parts["edges.json"]}


# ── FalkorDB ──────────────────────────────────────────────────────────────────
def connect(host: str | None = None, port: int | None = None, graph: str = GRAPH_NAME):
    from falkordb import FalkorDB
    db = FalkorDB(host=host or os.environ.get("BENCHGRAPH_FALKORDB_HOST", "localhost"),
                  port=int(port or os.environ.get("BENCHGRAPH_FALKORDB_PORT", "6382")))
    return db.select_graph(graph)


LABELS = ("Benchmark", "Family", "Publisher", "Dataset", "Capability", "Model")
_BATCH = 500


def _key(node_id: str) -> str:
    """Match key. Free-text ids (publisher names) can hold newlines, which the
    client's parameter encoding does not match reliably, so edges join on hex."""
    return hashlib.sha1(node_id.encode()).hexdigest()


def load_document(graph, doc: dict[str, Any]) -> None:
    """Replace the graph's contents with `doc`. The only write path."""
    try:
        graph.delete()
    except Exception:  # noqa: BLE001 - graph did not exist yet
        pass
    for label in LABELS:
        graph.query(f"CREATE INDEX FOR (n:{label}) ON (n.id)")
        graph.query(f"CREATE INDEX FOR (n:{label}) ON (n._key)")
    by_label: dict[str, list[dict[str, Any]]] = {}
    for n in doc["nodes"]:
        by_label.setdefault(n["label"], []).append(
            {"id": n["id"], "key": _key(n["id"]), "props": n["props"]})
    for label, rows in by_label.items():
        if label not in LABELS:
            raise ValueError(f"unknown label {label!r}")
        for i in range(0, len(rows), _BATCH):
            graph.query(f"UNWIND $rows AS r CREATE (n:{label}) SET n = r.props, n.id = r.id, n._key = r.key",
                        {"rows": rows[i:i + _BATCH]})
    groups: dict[tuple[str, str, str], list[dict[str, Any]]] = {}
    for e in doc["edges"]:
        if e["type"] not in EDGE_TYPES or e["from"][0] not in LABELS or e["to"][0] not in LABELS:
            raise ValueError(f"unknown edge {e['type']} {e['from'][0]}->{e['to'][0]}")
        groups.setdefault((e["type"], e["from"][0], e["to"][0]), []).append(
            {"a": _key(e["from"][1]), "b": _key(e["to"][1]), "props": e["props"]})
    for (etype, la, lb), rows in groups.items():
        for i in range(0, len(rows), _BATCH):
            graph.query(f"UNWIND $rows AS r MATCH (a:{la} {{_key: r.a}}), (b:{lb} {{_key: r.b}}) "
                        f"CREATE (a)-[e:{etype}]->(b) SET e = r.props", {"rows": rows[i:i + _BATCH]})


EDGE_TYPES = ("BELONGS_TO", "SUPERSEDES", "VARIANT_OF", "MEASURES", "PUBLISHED_BY",
              "USES_DATASET", "SCORED_ON")


def _set(front: dict[str, Any], field: str, value: Any) -> None:
    parts = field.split(".")
    cur = front
    for p in parts[:-1]:
        cur = cur.setdefault(p, {})
    cur[parts[-1]] = value


def read_front_matter(graph) -> dict[str, dict[str, Any]]:
    """Export the graph back to front-matter dicts (mapped fields only)."""
    out: dict[str, dict[str, Any]] = {}
    res = graph.ro_query("MATCH (b:Benchmark) WHERE b.stub = false RETURN b.id, properties(b)")
    for bid, props in res.result_set:
        front: dict[str, Any] = {"id": bid}
        for field in NODE_FIELDS:
            if field != "id" and _prop(field) in props:
                _set(front, field, decode(props[_prop(field)]))
        for field in list(EDGE_SCALARS) + list(EDGE_LISTS) + list(PUBLISHER_EDGE_FIELDS):
            raw = _prop(field) + "__raw"
            if raw in props:
                _set(front, field, decode(props[raw]))
        for field in EDGE_LISTS:
            if _prop(field) + "__len" in props:
                _set(front, field, [None] * props[_prop(field) + "__len"])
        out[bid] = front

    res = graph.ro_query(
        "MATCH (a)-[e]->(b) WHERE e.declared_in IS NOT NULL "
        "RETURN e.declared_in, e.field, e.pos, a.id, b.id, properties(e)")
    for declared_in, field, pos, a, b, eprops in res.result_set:
        front = out[declared_in]
        if field in EDGE_LISTS:
            reverse = EDGE_LISTS[field][2]
            _get(front, field)[pos] = a if reverse else b
        else:
            _set(front, field, b)
            if field == "publisher.org":
                for pf in PUBLISHER_EDGE_FIELDS:
                    key = pf.split(".")[1]
                    if key in eprops:
                        _set(front, pf, decode(eprops[key]))
    return out


def mapped_view(front: dict[str, Any]) -> dict[str, Any]:
    """The mapped leaves of a page, with absent and null treated alike."""
    return {f: _get(front, f) for f in MAPPED_FIELDS}


def unmapped_paths(front: dict[str, Any]) -> list[str]:
    """Every leaf path on a page that the graph does not carry."""
    mapped = set(MAPPED_FIELDS)
    out = []
    for k, v in front.items():
        if k in SCHEMA_PARENTS and isinstance(v, dict):
            out += [f"{k}.{kk}" for kk in v if f"{k}.{kk}" not in mapped]
        elif k not in mapped:
            out.append(k)
    return out


# ── named read-only queries ───────────────────────────────────────────────────
@dataclass(frozen=True)
class Param:
    kind: Callable[[str], Any]
    default: Any
    doc: str
    required: bool = False


def _capability(s: str) -> str:
    if not re.fullmatch(r"[a-z][a-z-]{1,40}", s):
        raise ValueError("capability must be a category id such as 'coding' or 'long-context'")
    return s


def _int_range(lo: int, hi: int) -> Callable[[str], int]:
    def parse(s: str) -> int:
        v = int(s)
        if not lo <= v <= hi:
            raise ValueError(f"must be between {lo} and {hi}")
        return v
    return parse


def _float_range(lo: float, hi: float) -> Callable[[str], float]:
    def parse(s: str) -> float:
        v = float(s)
        if not lo <= v <= hi:
            raise ValueError(f"must be between {lo} and {hi}")
        return v
    return parse


def _bool(s: str) -> bool:
    if s.lower() in ("1", "true", "yes"):
        return True
    if s.lower() in ("0", "false", "no"):
        return False
    raise ValueError("must be true or false")


@dataclass(frozen=True)
class NamedQuery:
    cypher: str
    params: dict[str, Param]
    doc: str


# "Still separates top models", from existing fields only:
#   1. the page measures the capability (category -> MEASURES edge);
#   2. saturation.status is `open` (plus `watch` when include_watch=true);
#      AUTHORING.md defines `watch` as "the spread among top models has
#      collapsed or a harder successor exists", so it is excluded by default;
#   3. page status is not deprecated, superseded or saturated;
#   4. when at least `top_n` models have SCORED_ON evidence, the spread between
#      the best and the top_n-th best model (best score per model, respecting
#      metric.direction) is >= min_spread. With fewer scored models the page is
#      kept on its saturation label alone and `spread` is null, unless
#      require_scores=true.
# Limits: the saturation label is an author's judgement at `saturation.as_of`;
# evidence covers few benchmarks; spread is in the evidence's own units, which
# can differ between records for one benchmark (percent vs fraction, Elo).
STILL_SEPARATING = """
MATCH (b:Benchmark)-[:MEASURES]->(:Capability {id: $capability})
WHERE b.stub = false
  AND b.saturation__status IN $saturation_statuses
  AND NOT coalesce(b.status, 'unknown') IN ['deprecated', 'superseded', 'saturated']
OPTIONAL MATCH (m:Model)-[s:SCORED_ON]->(b)
WITH b, m, max(CASE WHEN b.metric__direction = 'lower_is_better' THEN -s.value ELSE s.value END) AS k
ORDER BY k DESC
WITH b, collect(k) AS ks
WITH b, ks[0..$top_n] AS top, size(ks) AS scored
WITH b, top, scored,
     CASE WHEN size(top) >= $top_n AND $top_n >= 2 THEN abs(top[0] - top[size(top) - 1]) ELSE null END AS spread
WHERE (spread IS NULL AND NOT $require_scores) OR spread >= $min_spread
RETURN b.id AS id, b.name AS name, b.status AS status,
       b.saturation__status AS saturation_status, b.saturation__top_score AS saturation_top_score,
       b.saturation__as_of AS saturation_as_of, b.metric__direction AS metric_direction,
       scored AS scored_models, spread
ORDER BY coalesce(spread, -1.0) DESC, id
LIMIT $limit
"""

QUERIES: dict[str, NamedQuery] = {
    "benchmarks_still_separating": NamedQuery(
        cypher=STILL_SEPARATING,
        doc="Benchmarks that measure a capability and still separate top models.",
        params={
            "capability": Param(_capability, None, "category id, e.g. coding", required=True),
            "include_watch": Param(_bool, False, "also accept saturation.status=watch"),
            "top_n": Param(_int_range(2, 20), 5, "models compared for the spread"),
            "min_spread": Param(_float_range(0, 10000), 5.0, "minimum best-to-top_n spread"),
            "require_scores": Param(_bool, False, "drop pages without top_n scored models"),
            "limit": Param(_int_range(1, 500), 100, "maximum rows"),
        },
    ),
}


def validate_params(name: str, raw: dict[str, str]) -> dict[str, Any]:
    """Validate request parameters for a named query. Raises KeyError/ValueError."""
    spec = QUERIES[name]
    unknown = set(raw) - set(spec.params)
    if unknown:
        raise ValueError(f"unknown parameter(s): {', '.join(sorted(unknown))}")
    out: dict[str, Any] = {}
    for key, p in spec.params.items():
        if key in raw:
            try:
                out[key] = p.kind(raw[key])
            except ValueError as exc:
                raise ValueError(f"{key}: {exc}") from exc
        elif p.required:
            raise ValueError(f"missing required parameter: {key}")
        else:
            out[key] = p.default
    return out


def run_query(graph, name: str, raw: dict[str, str]) -> list[dict[str, Any]]:
    params = validate_params(name, raw)
    cypher_params = dict(params)
    if name == "benchmarks_still_separating":
        cypher_params["saturation_statuses"] = ["open", "watch"] if params["include_watch"] else ["open"]
        del cypher_params["include_watch"]
    res = graph.ro_query(QUERIES[name].cypher, cypher_params)
    cols = [h[1] if isinstance(h, (list, tuple)) else h for h in res.header]
    return [dict(zip(cols, row)) for row in res.result_set]


# ── CLI ───────────────────────────────────────────────────────────────────────
def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="python -m pipeline.benchgraph_graph")
    sub = ap.add_subparsers(dest="cmd", required=True)
    ex = sub.add_parser("export", help="build the portable graph export from Markdown")
    ex.add_argument("--out", type=Path, default=Path("dist/benchgraph-graph"))
    ex.add_argument("--verify", action="store_true",
                    help="load into FalkorDB and prove the mapped fields round-trip")
    ld = sub.add_parser("load", help="load an export into FalkorDB")
    ld.add_argument("source")
    q = sub.add_parser("query", help="run a named read-only query")
    q.add_argument("name", choices=sorted(QUERIES))
    q.add_argument("params", nargs="*", help="key=value")
    args = ap.parse_args(argv)

    if args.cmd == "export":
        doc = build_document()
        manifest = write_export(doc, args.out)
        if args.verify:
            _, loaded = read_export(str(args.out))
            g = connect()
            load_document(g, loaded)
            from pipeline.load import load_benchmarks
            back = read_front_matter(g)
            lost = [b.benchmark_id for b in load_benchmarks()
                    if mapped_view(b.front) != mapped_view(back.get(b.benchmark_id, {}))]
            if lost:
                print(f"round trip lost data on {len(lost)} page(s): {lost[:10]}", file=sys.stderr)
                return 1
        print(json.dumps({"out": str(args.out), "build": manifest["build"],
                          "counts": manifest["counts"], "files": manifest["files"]}, indent=2))
        return 0
    if args.cmd == "load":
        _, doc = read_export(args.source)
        load_document(connect(), doc)
        return 0
    raw = dict(p.split("=", 1) for p in args.params)
    print(json.dumps(run_query(connect(), args.name, raw), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
