"""ModelSpec REST API — FastAPI backend for the model intelligence graph.

Connects to FalkorDB and exposes model cards, graph data (D3.js format),
search, statistics, hardware compatibility, and ranking endpoints.
"""

from __future__ import annotations

import logging
import time
from contextlib import asynccontextmanager
from typing import Any

from pathlib import Path

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from schema.graph import EdgeType, create_indexes

# ═══════════════════════════════════════════════════════════════
# Logging
# ═══════════════════════════════════════════════════════════════

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("modelspec.api")

# ═══════════════════════════════════════════════════════════════
# FalkorDB connection
# ═══════════════════════════════════════════════════════════════

FALKORDB_HOST = "localhost"
FALKORDB_PORT = 6382
GRAPH_NAME = "modelspec"

_graph = None


def get_graph():
    """Return the cached FalkorDB graph handle."""
    global _graph
    if _graph is None:
        from falkordb import FalkorDB
        db = FalkorDB(host=FALKORDB_HOST, port=FALKORDB_PORT)
        _graph = db.select_graph(GRAPH_NAME)
    return _graph


# ═══════════════════════════════════════════════════════════════
# Response models
# ═══════════════════════════════════════════════════════════════

class ModelSummary(BaseModel):
    """Lightweight model listing entry."""
    id: str
    display_name: str
    model_type: str | None = None
    status: str | None = None
    provider: str | None = None
    total_parameters: int | None = None
    context_window: int | None = None
    open_weights: bool | None = None
    arena_elo_overall: float | None = None
    cost_input: float | None = None
    cost_output: float | None = None
    card_completeness: float | None = None
    release_date: str | None = None


class ModelListResponse(BaseModel):
    models: list[ModelSummary]
    total: int
    page: int
    page_size: int


class EdgeResponse(BaseModel):
    source: str
    target: str
    type: str
    properties: dict[str, Any] = {}


class ModelEdgesResponse(BaseModel):
    model_id: str
    edges: list[EdgeResponse]
    total: int


class GraphNode(BaseModel):
    id: str
    display_name: str | None = None
    label: str  # Node label: Model, Provider, Platform, etc.
    model_type: str | None = None
    total_parameters: int | None = None
    group: str | None = None
    # Extra properties carried through
    properties: dict[str, Any] = {}


class GraphEdge(BaseModel):
    source: str
    target: str
    type: str
    properties: dict[str, Any] = {}


class GraphResponse(BaseModel):
    nodes: list[GraphNode]
    edges: list[GraphEdge]


class SearchResult(BaseModel):
    id: str
    display_name: str | None = None
    label: str
    score: float = 1.0
    properties: dict[str, Any] = {}


class SearchResponse(BaseModel):
    results: list[SearchResult]
    total: int
    query: str


class StatsResponse(BaseModel):
    total_models: int
    total_providers: int
    total_platforms: int
    total_capabilities: int
    total_benchmarks: int
    total_hardware: int
    total_edges: int
    node_counts: dict[str, int]
    edge_counts: dict[str, int]


class HardwareCompatModel(BaseModel):
    model_id: str
    display_name: str | None = None
    quantization: str | None = None
    vram_usage_gb: float | None = None
    tokens_per_sec: float | None = None
    ttft_ms: float | None = None
    max_context_tokens: int | None = None
    inference_engine: str | None = None


class HardwareResponse(BaseModel):
    hardware_id: str
    models: list[HardwareCompatModel]
    total: int


class RankRequest(BaseModel):
    use_case: str | None = None
    hardware: str | None = None
    constraints: dict[str, Any] = {}
    limit: int = 10


class RankedModel(BaseModel):
    rank: int
    model_id: str
    display_name: str | None = None
    model_type: str | None = None
    score: float
    benchmark_score: float = 0.0
    capability_score: float = 0.0
    cost_score: float = 0.0
    context_score: float = 0.0
    type_bonus: float = 0.0
    speed_score: float = 0.0
    estimated_tps: float | None = None
    concurrent_instances: int | None = None
    reasons: list[str] = []
    benchmark_contributions: dict[str, float] = {}
    arena_elo_overall: float | None = None
    total_parameters: int | None = None
    context_window: int | None = None
    cost_input: float | None = None
    cost_output: float | None = None
    open_weights: bool | None = None
    provider: str | None = None
    status: str | None = None


class RankResponse(BaseModel):
    ranked: list[RankedModel]
    use_case: str | None = None
    hardware: str | None = None
    total: int
    available_use_cases: list[str] = []


class HealthResponse(BaseModel):
    status: str
    graph: str
    node_count: int


# ═══════════════════════════════════════════════════════════════
# App lifespan
# ═══════════════════════════════════════════════════════════════

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: verify FalkorDB, create indexes. Shutdown: clean up."""
    logger.info("Starting ModelSpec API...")
    try:
        graph = get_graph()
        create_indexes(graph)
        result = graph.query("MATCH (n) RETURN count(n) AS cnt")
        count = result.result_set[0][0] if result.result_set else 0
        logger.info(f"FalkorDB connected. Graph '{GRAPH_NAME}' has {count} nodes.")
    except Exception as exc:
        logger.error(f"FalkorDB connection failed: {exc}")
        raise
    yield
    logger.info("ModelSpec API shutting down.")


# ═══════════════════════════════════════════════════════════════
# FastAPI app
# ═══════════════════════════════════════════════════════════════

app = FastAPI(
    title="ModelSpec API",
    description="REST API for the ModelSpec model intelligence graph",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Request logging middleware ───────────────────────────────

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    elapsed = (time.time() - start) * 1000
    logger.info(f"{request.method} {request.url.path} → {response.status_code} ({elapsed:.1f}ms)")
    return response


# ═══════════════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════════════

def _node_props(node) -> dict[str, Any]:
    """Extract all properties from a FalkorDB node."""
    return dict(node.properties) if node.properties else {}


def _safe_int(val) -> int | None:
    if val is None:
        return None
    try:
        return int(val)
    except (ValueError, TypeError):
        return None


# Edge type groupings for the ?view= parameter
VIEW_EDGE_MAP: dict[str, list[str]] = {
    "provider": ["MADE_BY"],
    "lineage": ["DERIVED_FROM", "MERGED_FROM"],
    "competition": ["COMPETES_WITH", "OUTPERFORMS", "SIMILAR_TO"],
    "platforms": ["AVAILABLE_ON"],
    "benchmarks": ["SCORED_ON"],
    "capabilities": ["HAS_CAPABILITY"],
    "licensing": ["LICENSED_AS"],
    "tags": ["TAGGED_WITH"],
}


# ═══════════════════════════════════════════════════════════════
# Endpoints
# ═══════════════════════════════════════════════════════════════

@app.get("/api/v1/health", response_model=HealthResponse)
async def health():
    """Health check."""
    try:
        graph = get_graph()
        result = graph.query("MATCH (n) RETURN count(n)")
        count = result.result_set[0][0] if result.result_set else 0
        return HealthResponse(status="ok", graph=GRAPH_NAME, node_count=count)
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Database unavailable: {exc}")


# ─── 1. List models ──────────────────────────────────────────

@app.get("/api/v1/models", response_model=ModelListResponse)
async def list_models(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    model_type: str | None = Query(None, description="Filter by model_type"),
    provider: str | None = Query(None, description="Filter by provider slug"),
    status: str | None = Query(None, description="Filter by status"),
    open_weights: bool | None = Query(None, description="Filter by open_weights"),
    min_params: int | None = Query(None, description="Min total_parameters"),
    max_params: int | None = Query(None, description="Max total_parameters"),
    sort_by: str = Query("display_name", description="Sort field"),
    sort_dir: str = Query("asc", description="asc or desc"),
):
    """List models with pagination and filtering."""
    graph = get_graph()

    # Build WHERE clauses
    conditions: list[str] = []
    params: dict[str, Any] = {}

    if model_type:
        conditions.append("m.model_type = $model_type")
        params["model_type"] = model_type
    if provider:
        conditions.append("m.id STARTS WITH $provider_prefix")
        params["provider_prefix"] = f"{provider}/"
    if status:
        conditions.append("m.status = $status")
        params["status"] = status
    if open_weights is not None:
        conditions.append("m.open_weights = $open_weights")
        params["open_weights"] = open_weights
    if min_params is not None:
        conditions.append("m.total_parameters >= $min_params")
        params["min_params"] = min_params
    if max_params is not None:
        conditions.append("m.total_parameters <= $max_params")
        params["max_params"] = max_params

    where = f" WHERE {' AND '.join(conditions)}" if conditions else ""

    # Validate sort
    allowed_sorts = {
        "display_name", "model_type", "status", "total_parameters",
        "arena_elo_overall", "cost_input", "release_date", "card_completeness",
    }
    if sort_by not in allowed_sorts:
        sort_by = "display_name"
    direction = "DESC" if sort_dir.lower() == "desc" else "ASC"

    # Count
    count_q = f"MATCH (m:Model){where} RETURN count(m)"
    count_result = graph.query(count_q, params)
    total = count_result.result_set[0][0] if count_result.result_set else 0

    # Fetch page
    skip = (page - 1) * page_size
    params["skip"] = skip
    params["limit"] = page_size
    fetch_q = (
        f"MATCH (m:Model){where} "
        f"RETURN m "
        f"ORDER BY m.{sort_by} {direction} "
        f"SKIP $skip LIMIT $limit"
    )
    result = graph.query(fetch_q, params)

    models = []
    for row in result.result_set:
        node = row[0]
        p = _node_props(node)
        models.append(ModelSummary(
            id=p.get("id", ""),
            display_name=p.get("display_name", ""),
            model_type=p.get("model_type"),
            status=p.get("status"),
            provider=p.get("id", "").split("/")[0] if "/" in p.get("id", "") else None,
            total_parameters=_safe_int(p.get("total_parameters")),
            context_window=_safe_int(p.get("context_window")),
            open_weights=p.get("open_weights"),
            arena_elo_overall=p.get("arena_elo_overall"),
            cost_input=p.get("cost_input"),
            cost_output=p.get("cost_output"),
            card_completeness=p.get("card_completeness"),
            release_date=p.get("release_date"),
        ))

    return ModelListResponse(models=models, total=total, page=page, page_size=page_size)


# ─── 2. Get single model card ────────────────────────────────

@app.get("/api/v1/models/{model_id:path}/edges", response_model=ModelEdgesResponse)
async def get_model_edges(model_id: str):
    """Get all edges for a specific model."""
    graph = get_graph()

    # Verify model exists
    check = graph.query("MATCH (m:Model {id: $mid}) RETURN m", {"mid": model_id})
    if not check.result_set:
        raise HTTPException(status_code=404, detail=f"Model '{model_id}' not found")

    # Get outgoing edges
    out_q = (
        "MATCH (m:Model {id: $mid})-[e]->(t) "
        "RETURN type(e) AS etype, t.id AS target_id, properties(e) AS eprops"
    )
    out_result = graph.query(out_q, {"mid": model_id})

    # Get incoming edges
    in_q = (
        "MATCH (s)-[e]->(m:Model {id: $mid}) "
        "RETURN type(e) AS etype, s.id AS source_id, properties(e) AS eprops"
    )
    in_result = graph.query(in_q, {"mid": model_id})

    edges: list[EdgeResponse] = []
    for row in out_result.result_set:
        etype, target_id, eprops = row
        edges.append(EdgeResponse(
            source=model_id,
            target=target_id or "",
            type=etype,
            properties=eprops if isinstance(eprops, dict) else {},
        ))
    for row in in_result.result_set:
        etype, source_id, eprops = row
        edges.append(EdgeResponse(
            source=source_id or "",
            target=model_id,
            type=etype,
            properties=eprops if isinstance(eprops, dict) else {},
        ))

    return ModelEdgesResponse(model_id=model_id, edges=edges, total=len(edges))


@app.get("/api/v1/models/{model_id:path}", response_model=dict)
async def get_model(model_id: str):
    """Get full model card as JSON. Returns all node properties plus edges."""
    graph = get_graph()

    result = graph.query("MATCH (m:Model {id: $mid}) RETURN m", {"mid": model_id})
    if not result.result_set:
        raise HTTPException(status_code=404, detail=f"Model '{model_id}' not found")

    node = result.result_set[0][0]
    model_data = _node_props(node)

    # Gather related nodes via edges
    related_q = (
        "MATCH (m:Model {id: $mid})-[e]->(t) "
        "RETURN type(e) AS etype, labels(t) AS tlabels, t.id AS tid, "
        "       t.display_name AS tname, properties(e) AS eprops"
    )
    related = graph.query(related_q, {"mid": model_id})

    relationships: dict[str, list[dict]] = {}
    for row in related.result_set:
        etype, tlabels, tid, tname, eprops = row
        label = tlabels[0] if tlabels else "Unknown"
        entry = {
            "id": tid,
            "display_name": tname,
            "label": label,
        }
        if eprops and isinstance(eprops, dict):
            entry["edge_properties"] = eprops
        relationships.setdefault(etype, []).append(entry)

    # Gather incoming edges too
    incoming_q = (
        "MATCH (s)-[e]->(m:Model {id: $mid}) "
        "RETURN type(e) AS etype, labels(s) AS slabels, s.id AS sid, "
        "       s.display_name AS sname, properties(e) AS eprops"
    )
    incoming = graph.query(incoming_q, {"mid": model_id})
    for row in incoming.result_set:
        etype, slabels, sid, sname, eprops = row
        label = slabels[0] if slabels else "Unknown"
        entry = {
            "id": sid,
            "display_name": sname,
            "label": label,
            "direction": "incoming",
        }
        if eprops and isinstance(eprops, dict):
            entry["edge_properties"] = eprops
        key = f"{etype}_incoming"
        relationships.setdefault(key, []).append(entry)

    model_data["relationships"] = relationships
    return model_data


# ─── 3. Full graph for D3.js ─────────────────────────────────

@app.get("/api/v1/graph", response_model=GraphResponse)
async def get_graph_data(
    view: str = Query("all", description="Graph view filter: all, provider, lineage, competition, hardware, platforms, benchmarks, capabilities, licensing, tags"),
):
    """Return the full graph (or filtered subgraph) in D3.js force-directed format."""
    graph = get_graph()

    # Determine which edge types to include
    if view == "all":
        # Exclude competition edges from "all" view — too dense
        edge_filter = ["MADE_BY", "DERIVED_FROM", "MERGED_FROM", "LICENSED_AS",
                       "HAS_CAPABILITY", "SCORED_ON", "AVAILABLE_ON", "TAGGED_WITH", "FITS_ON"]
    elif view in VIEW_EDGE_MAP:
        edge_filter = VIEW_EDGE_MAP[view]
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown view '{view}'. Valid: all, {', '.join(VIEW_EDGE_MAP.keys())}",
        )

    # Build edge query
    if edge_filter:
        # Filter to specific edge types
        type_checks = " OR ".join(f"type(e) = '{t}'" for t in edge_filter)
        # For competition edges, only show one direction and cap to keep renderer fast
        if view == "competition":
            edge_q = (
                f"MATCH (a)-[e]->(b) WHERE ({type_checks}) "
                "AND e.overlap_score >= 0.9 AND id(a) < id(b) "
                "RETURN a, e, b LIMIT 1500"
            )
        else:
            edge_q = (
                f"MATCH (a)-[e]->(b) WHERE ({type_checks}) "
                "RETURN a, e, b"
            )
    else:
        edge_q = "MATCH (a)-[e]->(b) RETURN a, e, b"

    result = graph.query(edge_q)

    nodes_map: dict[str, GraphNode] = {}
    edges_list: list[GraphEdge] = []

    for row in result.result_set:
        src_node, edge, tgt_node = row

        src_props = _node_props(src_node)
        tgt_props = _node_props(tgt_node)
        src_id = src_props.get("id", "")
        tgt_id = tgt_props.get("id", "")
        src_labels = src_node.labels
        tgt_labels = tgt_node.labels
        src_label = src_labels[0] if src_labels else "Unknown"
        tgt_label = tgt_labels[0] if tgt_labels else "Unknown"

        # Build group for models
        src_group = None
        if src_label == "Model":
            provider_slug = src_id.split("/")[0] if "/" in src_id else src_id
            src_group = f"provider:{provider_slug}"
        elif src_label == "Provider":
            src_group = f"provider:{src_id}"
        else:
            src_group = f"{src_label.lower()}:{src_id}"

        tgt_group = None
        if tgt_label == "Model":
            provider_slug = tgt_id.split("/")[0] if "/" in tgt_id else tgt_id
            tgt_group = f"provider:{provider_slug}"
        elif tgt_label == "Provider":
            tgt_group = f"provider:{tgt_id}"
        else:
            tgt_group = f"{tgt_label.lower()}:{tgt_id}"

        if src_id and src_id not in nodes_map:
            # Collect extra properties for the node, excluding id/display_name
            extra = {k: v for k, v in src_props.items()
                     if k not in ("id", "display_name", "model_type", "total_parameters")}
            nodes_map[src_id] = GraphNode(
                id=src_id,
                display_name=src_props.get("display_name"),
                label=src_label,
                model_type=src_props.get("model_type"),
                total_parameters=_safe_int(src_props.get("total_parameters")),
                group=src_group,
                properties=extra,
            )

        if tgt_id and tgt_id not in nodes_map:
            extra = {k: v for k, v in tgt_props.items()
                     if k not in ("id", "display_name", "model_type", "total_parameters")}
            nodes_map[tgt_id] = GraphNode(
                id=tgt_id,
                display_name=tgt_props.get("display_name"),
                label=tgt_label,
                model_type=tgt_props.get("model_type"),
                total_parameters=_safe_int(tgt_props.get("total_parameters")),
                group=tgt_group,
                properties=extra,
            )

        edge_props = dict(edge.properties) if edge.properties else {}
        edges_list.append(GraphEdge(
            source=src_id,
            target=tgt_id,
            type=edge.relation,
            properties=edge_props,
        ))

    return GraphResponse(nodes=list(nodes_map.values()), edges=edges_list)


# ─── 4. Search ───────────────────────────────────────────────

@app.get("/api/v1/search", response_model=SearchResponse)
async def search(
    q: str = Query(..., min_length=1, description="Search query"),
    type: str | None = Query(None, alias="type", description="Node type filter: Model, Provider, Platform, Capability, etc."),
    limit: int = Query(20, ge=1, le=100),
):
    """Search nodes by name/id. Uses case-insensitive CONTAINS matching."""
    graph = get_graph()

    params: dict[str, Any] = {"query": q, "limit": limit}

    if type:
        # Search specific node type
        match_clause = f"MATCH (n:{type})"
    else:
        match_clause = "MATCH (n)"

    search_q = (
        f"{match_clause} "
        "WHERE toLower(n.id) CONTAINS toLower($query) "
        "   OR toLower(n.display_name) CONTAINS toLower($query) "
        "RETURN n, labels(n) AS nlabels "
        "LIMIT $limit"
    )
    result = graph.query(search_q, params)

    results: list[SearchResult] = []
    for row in result.result_set:
        node, nlabels = row
        props = _node_props(node)
        nid = props.get("id", "")
        name = props.get("display_name", "")
        label = nlabels[0] if nlabels else "Unknown"

        # Simple relevance: exact match > starts with > contains
        q_lower = q.lower()
        nid_lower = nid.lower()
        name_lower = (name or "").lower()
        if nid_lower == q_lower or name_lower == q_lower:
            score = 3.0
        elif nid_lower.startswith(q_lower) or name_lower.startswith(q_lower):
            score = 2.0
        else:
            score = 1.0

        extra = {k: v for k, v in props.items() if k not in ("id", "display_name")}
        results.append(SearchResult(
            id=nid,
            display_name=name,
            label=label,
            score=score,
            properties=extra,
        ))

    # Sort by score descending
    results.sort(key=lambda r: r.score, reverse=True)

    return SearchResponse(results=results, total=len(results), query=q)


# ─── 5. Stats ────────────────────────────────────────────────

@app.get("/api/v1/stats", response_model=StatsResponse)
async def get_stats():
    """Database statistics."""
    graph = get_graph()

    # Node counts by label
    node_q = graph.query("MATCH (n) RETURN labels(n) AS label, count(n) AS cnt")
    node_counts: dict[str, int] = {}
    for row in node_q.result_set:
        label = row[0][0] if row[0] else "Unknown"
        node_counts[label] = row[1]

    # Edge counts by type
    edge_q = graph.query("MATCH ()-[e]->() RETURN type(e) AS etype, count(e) AS cnt")
    edge_counts: dict[str, int] = {}
    for row in edge_q.result_set:
        edge_counts[row[0]] = row[1]

    return StatsResponse(
        total_models=node_counts.get("Model", 0),
        total_providers=node_counts.get("Provider", 0),
        total_platforms=node_counts.get("Platform", 0),
        total_capabilities=node_counts.get("Capability", 0),
        total_benchmarks=node_counts.get("Benchmark", 0),
        total_hardware=node_counts.get("Hardware", 0),
        total_edges=sum(edge_counts.values()),
        node_counts=node_counts,
        edge_counts=edge_counts,
    )


# ─── 6. Hardware compatibility ────────────────────────────────

@app.get("/api/v1/hardware/{hw_id}", response_model=HardwareResponse)
async def get_hardware_models(hw_id: str):
    """List all models that fit on a specific hardware profile."""
    graph = get_graph()

    # Check hardware exists
    check = graph.query("MATCH (h:Hardware {id: $hid}) RETURN h", {"hid": hw_id})
    if not check.result_set:
        raise HTTPException(status_code=404, detail=f"Hardware '{hw_id}' not found")

    q = (
        "MATCH (m:Model)-[e:FITS_ON]->(h:Hardware {id: $hid}) "
        "RETURN m.id AS mid, m.display_name AS mname, "
        "       e.quantization AS quant, e.vram_usage_gb AS vram, "
        "       e.tokens_per_sec AS tps, e.ttft_ms AS ttft, "
        "       e.max_context_tokens AS max_ctx, e.inference_engine AS engine "
        "ORDER BY e.tokens_per_sec DESC"
    )
    result = graph.query(q, {"hid": hw_id})

    models: list[HardwareCompatModel] = []
    for row in result.result_set:
        mid, mname, quant, vram, tps, ttft, max_ctx, engine = row
        models.append(HardwareCompatModel(
            model_id=mid or "",
            display_name=mname,
            quantization=quant,
            vram_usage_gb=vram,
            tokens_per_sec=tps,
            ttft_ms=ttft,
            max_context_tokens=_safe_int(max_ctx),
            inference_engine=engine,
        ))

    return HardwareResponse(hardware_id=hw_id, models=models, total=len(models))


# ─── 7. Ranking endpoint ─────────────────────────────────────

@app.post("/api/v1/rank", response_model=RankResponse)
async def rank_models(req: RankRequest):
    """Rank models using the 4-stage ranking engine.

    Stages:
      1. Filter — eliminate models that fail hard constraints
      2. Score  — weighted composite across benchmarks, capabilities, cost, context
      3. Rank   — sort by score, break ties by Arena ELO then parameter count
      4. Explain — human-readable reasons for each ranking
    """
    from api.ranking import RankingEngine, USE_CASE_PROFILES

    graph = get_graph()

    # Validate hardware exists if specified
    if req.hardware:
        hw_check = graph.query("MATCH (h:Hardware {id: $hid}) RETURN h", {"hid": req.hardware})
        if not hw_check.result_set:
            raise HTTPException(status_code=404, detail=f"Hardware '{req.hardware}' not found")

    engine = RankingEngine(graph)
    scored = engine.rank(
        use_case=req.use_case,
        hardware=req.hardware,
        constraints=req.constraints,
        limit=req.limit,
    )

    ranked: list[RankedModel] = []
    for i, sm in enumerate(scored):
        ranked.append(RankedModel(
            rank=i + 1,
            model_id=sm.model_id,
            display_name=sm.display_name,
            model_type=sm.model_type,
            score=sm.score,
            benchmark_score=sm.benchmark_score,
            capability_score=sm.capability_score,
            cost_score=sm.cost_score,
            context_score=sm.context_score,
            type_bonus=sm.type_bonus,
            speed_score=sm.speed_score,
            estimated_tps=sm.estimated_tps,
            concurrent_instances=sm.concurrent_instances,
            reasons=sm.reasons,
            benchmark_contributions=sm.benchmark_contributions,
            arena_elo_overall=sm.arena_elo_overall,
            total_parameters=sm.total_parameters,
            context_window=sm.context_window,
            cost_input=sm.cost_input,
            cost_output=sm.cost_output,
            open_weights=sm.open_weights,
            provider=sm.provider,
            status=sm.status,
        ))

    return RankResponse(
        ranked=ranked,
        use_case=req.use_case,
        hardware=req.hardware,
        total=len(ranked),
        available_use_cases=sorted(USE_CASE_PROFILES.keys()),
    )


# ─── 8. Views list (for 3D graph UI) ───────────────────────────

@app.get("/api/v1/views")
async def list_views():
    """List available edge views for the graph visualization."""
    return [
        {"id": k, "label": k.replace("_", " ").title()}
        for k in VIEW_EDGE_MAP.keys()
    ] + [{"id": "all", "label": "All Relationships"}]


# ─── 9. Node detail (for 3D graph UI) ──────────────────────────

@app.get("/api/v1/node/{node_id:path}")
async def get_node_detail(node_id: str):
    """Get full details for a specific node and its relationships."""
    graph = get_graph()

    # Try to find node by id property
    result = graph.query(
        "MATCH (n {id: $nid}) RETURN labels(n) AS labels, properties(n) AS props",
        {"nid": node_id},
    )
    if not result.result_set:
        raise HTTPException(status_code=404, detail="Node not found")

    row = result.result_set[0]
    props = row[1] if row[1] else {}
    label = row[0][0] if row[0] else "Unknown"

    # Get all relationships
    rels = graph.query(
        "MATCH (n {id: $nid})-[r]-(m) "
        "RETURN type(r) AS rel, m.id AS peer_id, labels(m) AS peer_labels, "
        "       m.display_name AS peer_name, startNode(r).id = $nid AS outgoing",
        {"nid": node_id},
    )

    relationships = []
    for r in rels.result_set:
        relationships.append({
            "type": r[0],
            "peer_id": r[1],
            "peer_label": r[2][0] if r[2] else "Unknown",
            "peer_name": r[3] or str(r[1]),
            "direction": "outgoing" if r[4] else "incoming",
        })

    return {
        "id": node_id,
        "label": label,
        "properties": props,
        "relationships": relationships,
    }


# ─── 10. Serve 3D frontend ─────────────────────────────────────

GRAPH3D_DIR = Path(__file__).resolve().parent.parent / "web3d"


@app.get("/graph", response_class=HTMLResponse)
async def serve_3d_graph():
    """Serve the 3D knowledge graph visualization."""
    index = GRAPH3D_DIR / "index.html"
    if not index.exists():
        raise HTTPException(404, "3D frontend not found")
    return HTMLResponse(index.read_text())


@app.get("/downselect", response_class=HTMLResponse)
async def serve_downselect():
    """Serve the downselect wizard."""
    page = GRAPH3D_DIR / "downselect.html"
    if not page.exists():
        raise HTTPException(404, "Downselect page not found")
    return HTMLResponse(page.read_text())


@app.get("/contribute", response_class=HTMLResponse)
async def serve_contribute():
    """Serve the contribution/research page."""
    page = GRAPH3D_DIR / "contribute.html"
    if not page.exists():
        raise HTTPException(404, "Contribute page not found")
    return HTMLResponse(page.read_text())
