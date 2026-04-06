"""ModelSpec CLI — explore, search, compare, and rank AI models.

Entry point: ``modelspec`` (registered in pyproject.toml).
All data comes from the FalkorDB graph on localhost:6382.
"""

from __future__ import annotations

import json
import sys
from typing import Any, Optional

import typer
from falkordb import FalkorDB
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.tree import Tree

# ───────────────────────────────────────────────────────────────
# App setup
# ───────────────────────────────────────────────────────────────

app = typer.Typer(
    name="modelspec",
    help="ModelSpec — explore, search, compare, and rank AI models.",
    no_args_is_help=True,
    rich_markup_mode="rich",
)

console = Console()

# ───────────────────────────────────────────────────────────────
# Graph connection helper
# ───────────────────────────────────────────────────────────────

_FALKORDB_HOST = "localhost"
_FALKORDB_PORT = 6382
_GRAPH_NAME = "modelspec"


def _get_graph():
    """Connect to FalkorDB and return the modelspec graph handle."""
    try:
        db = FalkorDB(host=_FALKORDB_HOST, port=_FALKORDB_PORT)
        return db.select_graph(_GRAPH_NAME)
    except Exception as exc:
        console.print(f"[bold red]Error:[/] Could not connect to FalkorDB at {_FALKORDB_HOST}:{_FALKORDB_PORT}")
        console.print(f"  {exc}")
        raise typer.Exit(1)


# ───────────────────────────────────────────────────────────────
# Formatting helpers
# ───────────────────────────────────────────────────────────────

def _fmt_params(n: int | float | None) -> str:
    """Format parameter count to human-readable string."""
    if n is None:
        return "-"
    n = int(n)
    if n >= 1_000_000_000_000:
        return f"{n / 1_000_000_000_000:.1f}T"
    if n >= 1_000_000_000:
        return f"{n / 1_000_000_000:.1f}B"
    if n >= 1_000_000:
        return f"{n / 1_000_000:.0f}M"
    return f"{n:,}"


def _fmt_cost(v: float | None) -> str:
    """Format cost per million tokens."""
    if v is None:
        return "-"
    if v == 0:
        return "[green]free[/]"
    return f"${v:.2f}"


def _fmt_elo(v: float | None) -> str:
    if v is None:
        return "-"
    return f"{v:.0f}"


def _fmt_float(v: float | None, suffix: str = "") -> str:
    if v is None:
        return "-"
    return f"{v:.1f}{suffix}"


def _fmt_int(v: int | None) -> str:
    if v is None:
        return "-"
    return f"{v:,}"


def _status_color(status: str | None) -> str:
    colors = {
        "active": "green",
        "beta": "yellow",
        "alpha": "yellow",
        "preview": "cyan",
        "deprecated": "red",
        "sunset": "dim red",
    }
    if not status:
        return "white"
    return colors.get(status.lower(), "white")


def _tier_style(tier: str | None) -> str:
    if not tier:
        return "-"
    styles = {
        "tier-1": "[bold green]tier-1[/]",
        "tier-2": "[yellow]tier-2[/]",
        "tier-3": "[dim]tier-3[/]",
    }
    return styles.get(tier, tier)


def _bool_icon(v: Any) -> str:
    if v is True:
        return "[green]Y[/]"
    if v is False:
        return "[dim]-[/]"
    return "-"


def _node_props(node) -> dict[str, Any]:
    """Extract properties dict from a FalkorDB node."""
    if hasattr(node, "properties"):
        return node.properties
    return {}


def _edge_props(edge) -> dict[str, Any]:
    """Extract properties dict from a FalkorDB edge."""
    if hasattr(edge, "properties"):
        return edge.properties
    return {}


# ───────────────────────────────────────────────────────────────
# 1. modelspec info <model_id>
# ───────────────────────────────────────────────────────────────

@app.command()
def info(
    model_id: str = typer.Argument(..., help="Model ID, e.g. qwen/qwen3-30b-a3b"),
    format: Optional[str] = typer.Option(None, "--format", "-f", help="Output format: json"),
) -> None:
    """Show the full model card for a given model ID."""
    graph = _get_graph()

    # Fetch model node
    result = graph.query(
        "MATCH (m:Model {id: $model_id}) RETURN m",
        {"model_id": model_id},
    )
    if not result.result_set:
        console.print(f"[bold red]Model not found:[/] {model_id}")
        raise typer.Exit(1)

    m = _node_props(result.result_set[0][0])

    # Fetch provider
    prov_result = graph.query(
        "MATCH (m:Model {id: $mid})-[:MADE_BY]->(p:Provider) RETURN p",
        {"mid": model_id},
    )
    provider = _node_props(prov_result.result_set[0][0]) if prov_result.result_set else {}

    # Fetch capabilities
    cap_result = graph.query(
        "MATCH (m:Model {id: $mid})-[r:HAS_CAPABILITY]->(c:Capability) "
        "RETURN c.id, c.name, r.tier ORDER BY c.id",
        {"mid": model_id},
    )

    # Fetch benchmarks
    bench_result = graph.query(
        "MATCH (m:Model {id: $mid})-[r:SCORED_ON]->(b:Benchmark) "
        "RETURN b.id, b.name, r.value ORDER BY b.id",
        {"mid": model_id},
    )

    # Fetch hardware fits
    hw_result = graph.query(
        "MATCH (m:Model {id: $mid})-[r:FITS_ON]->(h:Hardware) "
        "RETURN h.id, r",
        {"mid": model_id},
    )

    # Fetch platforms
    plat_result = graph.query(
        "MATCH (m:Model {id: $mid})-[:AVAILABLE_ON]->(p:Platform) "
        "RETURN p.id, p.display_name",
        {"mid": model_id},
    )

    # Fetch license
    lic_result = graph.query(
        "MATCH (m:Model {id: $mid})-[:LICENSED_AS]->(l:License) RETURN l",
        {"mid": model_id},
    )
    license_info = _node_props(lic_result.result_set[0][0]) if lic_result.result_set else {}

    # Fetch tags
    tag_result = graph.query(
        "MATCH (m:Model {id: $mid})-[:TAGGED_WITH]->(t:Tag) RETURN t.id",
        {"mid": model_id},
    )
    tags = [row[0] for row in tag_result.result_set]

    # ── JSON output ────────────────────────────────────────────
    if format == "json":
        data = {
            "model": m,
            "provider": provider,
            "license": license_info,
            "tags": tags,
            "capabilities": [
                {"id": r[0], "name": r[1], "tier": r[2]}
                for r in cap_result.result_set
            ],
            "benchmarks": [
                {"id": r[0], "name": r[1], "value": r[2]}
                for r in bench_result.result_set
            ],
            "hardware": [
                {"id": r[0], **_edge_props(r[1])}
                for r in hw_result.result_set
            ],
            "platforms": [
                {"id": r[0], "name": r[1]}
                for r in plat_result.result_set
            ],
        }
        console.print_json(json.dumps(data, default=str))
        return

    # ── Rich output ────────────────────────────────────────────

    # Identity panel
    status = m.get("status", "")
    status_clr = _status_color(status)
    identity_lines = [
        f"[bold]{m.get('display_name', model_id)}[/]",
        f"  ID:       {m.get('id', model_id)}",
        f"  Provider: {provider.get('display_name', m.get('id', '').split('/')[0])}",
        f"  Type:     {m.get('model_type', '-')}",
        f"  Status:   [{status_clr}]{status}[/]",
        f"  Released: {m.get('release_date', '-')}",
        f"  Family:   {m.get('family', '-')}",
        f"  Country:  {m.get('origin_country', '-')}",
        f"  Open:     {_bool_icon(m.get('open_weights'))}",
    ]
    if tags:
        identity_lines.append(f"  Tags:     {', '.join(tags)}")
    identity_lines.append(f"  Complete: {_fmt_float(m.get('card_completeness'), '%')}")

    console.print(Panel("\n".join(identity_lines), title="Identity", border_style="blue"))

    # Architecture
    arch_lines = []
    if m.get("architecture_type"):
        arch_lines.append(f"  Architecture: {m['architecture_type']}")
    if m.get("total_parameters"):
        active = m.get("active_parameters")
        params_str = _fmt_params(m["total_parameters"])
        if active:
            params_str += f" ({_fmt_params(active)} active)"
        arch_lines.append(f"  Parameters:   {params_str}")
    if m.get("context_window"):
        arch_lines.append(f"  Context:      {_fmt_int(m['context_window'])} tokens")
    if m.get("max_input"):
        arch_lines.append(f"  Max input:    {_fmt_int(m['max_input'])} tokens")
    if m.get("max_output"):
        arch_lines.append(f"  Max output:   {_fmt_int(m['max_output'])} tokens")
    if m.get("embedding_dimensions"):
        arch_lines.append(f"  Embedding:    {_fmt_int(m['embedding_dimensions'])} dims")
    if arch_lines:
        console.print(Panel("\n".join(arch_lines), title="Architecture", border_style="cyan"))

    # Capabilities
    if cap_result.result_set:
        cap_table = Table(title="Capabilities", show_header=True, header_style="bold magenta")
        cap_table.add_column("Capability", style="white", min_width=30)
        cap_table.add_column("Tier", justify="center")
        for row in cap_result.result_set:
            cap_table.add_row(row[1] or row[0], _tier_style(row[2]))
        console.print(cap_table)

    # Benchmarks
    if bench_result.result_set:
        bench_table = Table(title="Benchmarks", show_header=True, header_style="bold yellow")
        bench_table.add_column("Benchmark", style="white", min_width=25)
        bench_table.add_column("Score", justify="right", style="bold")
        for row in bench_result.result_set:
            bench_table.add_row(row[1] or row[0], _fmt_float(row[2]))
        console.print(bench_table)

    # Hardware fit
    if hw_result.result_set:
        hw_table = Table(title="Hardware Fit", show_header=True, header_style="bold green")
        hw_table.add_column("Hardware", style="white", min_width=25)
        hw_table.add_column("Quant", justify="center")
        hw_table.add_column("VRAM/RAM", justify="right")
        hw_table.add_column("tok/s", justify="right")
        hw_table.add_column("TTFT", justify="right")
        hw_table.add_column("Engine", justify="center")
        for row in hw_result.result_set:
            hw_id = row[0]
            ep = _edge_props(row[1])
            hw_table.add_row(
                hw_id.replace("_", " ").title(),
                ep.get("quantization", "-"),
                _fmt_float(ep.get("vram_usage_gb"), " GB"),
                _fmt_float(ep.get("tokens_per_sec"), ""),
                _fmt_float(ep.get("ttft_ms"), " ms"),
                ep.get("inference_engine", "-"),
            )
        console.print(hw_table)

    # Availability
    if plat_result.result_set:
        plat_names = [row[1] or row[0] for row in plat_result.result_set]
        console.print(Panel(
            "  " + " | ".join(plat_names),
            title="Available On",
            border_style="green",
        ))

    # Cost
    cost_lines = []
    if m.get("cost_input") is not None:
        cost_lines.append(f"  Input:  {_fmt_cost(m['cost_input'])}/M tokens")
    if m.get("cost_output") is not None:
        cost_lines.append(f"  Output: {_fmt_cost(m['cost_output'])}/M tokens")
    if cost_lines:
        console.print(Panel("\n".join(cost_lines), title="Cost", border_style="yellow"))

    # License
    if license_info:
        lic_lines = [f"  License: {license_info.get('name', '-')}"]
        if license_info.get("commercial_ok") is not None:
            lic_lines.append(f"  Commercial: {_bool_icon(license_info['commercial_ok'])}")
        console.print(Panel("\n".join(lic_lines), title="License", border_style="dim"))


# ───────────────────────────────────────────────────────────────
# 2. modelspec search
# ───────────────────────────────────────────────────────────────

@app.command()
def search(
    type: Optional[str] = typer.Option(None, "--type", "-t", help="Model type, e.g. llm-chat"),
    hardware: Optional[str] = typer.Option(None, "--hardware", "-hw", help="Hardware ID filter (FITS_ON)"),
    license: Optional[str] = typer.Option(None, "--license", "-l", help="License type filter"),
    origin: Optional[str] = typer.Option(None, "--origin", help="Origin country code, e.g. US, CN"),
    open_weights: Optional[bool] = typer.Option(None, "--open-weights/--closed-weights", help="Filter by open weights"),
    min_params: Optional[int] = typer.Option(None, "--min-params", help="Minimum total parameters"),
    max_params: Optional[int] = typer.Option(None, "--max-params", help="Maximum total parameters"),
    query: Optional[str] = typer.Option(None, "--query", "-q", help="Text search on display_name"),
    format: Optional[str] = typer.Option(None, "--format", "-f", help="Output format: json"),
) -> None:
    """Search models with filters."""
    graph = _get_graph()

    # Build dynamic WHERE clauses
    where_clauses: list[str] = []
    params: dict[str, Any] = {}

    match_prefix = "MATCH (m:Model)"
    extra_matches: list[str] = []

    if type:
        where_clauses.append("m.model_type = $model_type")
        params["model_type"] = type

    if origin:
        where_clauses.append("m.origin_country = $origin")
        params["origin"] = origin.upper()

    if open_weights is not None:
        where_clauses.append("m.open_weights = $open_weights")
        params["open_weights"] = open_weights

    if min_params is not None:
        where_clauses.append("m.total_parameters >= $min_params")
        params["min_params"] = min_params

    if max_params is not None:
        where_clauses.append("m.total_parameters <= $max_params")
        params["max_params"] = max_params

    if query:
        where_clauses.append("toLower(m.display_name) CONTAINS toLower($query_text)")
        params["query_text"] = query

    if hardware:
        extra_matches.append(f"MATCH (m)-[:FITS_ON]->(h:Hardware {{id: $hw_id}})")
        params["hw_id"] = hardware

    if license:
        extra_matches.append(f"MATCH (m)-[:LICENSED_AS]->(l:License {{id: $lic_id}})")
        params["lic_id"] = license

    cypher = match_prefix
    if extra_matches:
        cypher += " " + " ".join(extra_matches)
    if where_clauses:
        cypher += " WHERE " + " AND ".join(where_clauses)
    cypher += (
        " RETURN m.id, m.display_name, m.model_type, m.total_parameters, "
        "m.arena_elo_overall, m.cost_input, m.cost_output, m.status, "
        "m.open_weights, m.origin_country "
        "ORDER BY m.arena_elo_overall DESC"
    )

    result = graph.query(cypher, params)

    if format == "json":
        rows = []
        for r in result.result_set:
            rows.append({
                "id": r[0], "name": r[1], "type": r[2],
                "parameters": r[3], "arena_elo": r[4],
                "cost_input": r[5], "cost_output": r[6],
                "status": r[7], "open_weights": r[8],
                "origin": r[9],
            })
        console.print_json(json.dumps(rows, default=str))
        return

    if not result.result_set:
        console.print("[yellow]No models found matching your filters.[/]")
        return

    table = Table(
        title=f"Models ({len(result.result_set)} found)",
        show_header=True,
        header_style="bold cyan",
    )
    table.add_column("Model", style="bold white", min_width=20)
    table.add_column("Type", style="dim")
    table.add_column("Params", justify="right")
    table.add_column("ELO", justify="right")
    table.add_column("$/M in", justify="right")
    table.add_column("$/M out", justify="right")
    table.add_column("Status", justify="center")
    table.add_column("Open", justify="center")
    table.add_column("Origin", justify="center")

    for r in result.result_set:
        status = r[7] or ""
        table.add_row(
            r[1] or r[0],
            r[2] or "-",
            _fmt_params(r[3]),
            _fmt_elo(r[4]),
            _fmt_cost(r[5]),
            _fmt_cost(r[6]),
            f"[{_status_color(status)}]{status}[/]",
            _bool_icon(r[8]),
            r[9] or "-",
        )

    console.print(table)


# ───────────────────────────────────────────────────────────────
# 3. modelspec compare <model_ids>
# ───────────────────────────────────────────────────────────────

@app.command()
def compare(
    model_ids: list[str] = typer.Argument(..., help="2-4 model IDs to compare"),
    format: Optional[str] = typer.Option(None, "--format", "-f", help="Output format: json"),
) -> None:
    """Side-by-side comparison of 2-4 models."""
    if len(model_ids) < 2 or len(model_ids) > 4:
        console.print("[bold red]Error:[/] Provide 2 to 4 model IDs.")
        raise typer.Exit(1)

    graph = _get_graph()

    models: list[dict[str, Any]] = []
    all_benchmarks: dict[str, dict[str, float | None]] = {}  # bench_id -> {model_id: value}
    all_caps: dict[str, dict[str, str | None]] = {}  # cap_id -> {model_id: tier}
    all_hw: dict[str, dict[str, dict]] = {}  # hw_id -> {model_id: props}

    for mid in model_ids:
        # Model node
        result = graph.query("MATCH (m:Model {id: $mid}) RETURN m", {"mid": mid})
        if not result.result_set:
            console.print(f"[bold red]Model not found:[/] {mid}")
            raise typer.Exit(1)
        m = _node_props(result.result_set[0][0])
        models.append(m)

        # Benchmarks
        bench_r = graph.query(
            "MATCH (m:Model {id: $mid})-[r:SCORED_ON]->(b:Benchmark) "
            "RETURN b.id, b.name, r.value",
            {"mid": mid},
        )
        for row in bench_r.result_set:
            bid = row[0]
            if bid not in all_benchmarks:
                all_benchmarks[bid] = {"_name": row[1]}
            all_benchmarks[bid][mid] = row[2]

        # Capabilities (section-level only: coding, reasoning, tool_use, etc.)
        cap_r = graph.query(
            "MATCH (m:Model {id: $mid})-[r:HAS_CAPABILITY]->(c:Capability) "
            "WHERE NOT c.id CONTAINS ':' "
            "RETURN c.id, c.name, r.tier",
            {"mid": mid},
        )
        for row in cap_r.result_set:
            cid = row[0]
            if cid not in all_caps:
                all_caps[cid] = {"_name": row[1]}
            all_caps[cid][mid] = row[2]

        # Hardware
        hw_r = graph.query(
            "MATCH (m:Model {id: $mid})-[r:FITS_ON]->(h:Hardware) RETURN h.id, r",
            {"mid": mid},
        )
        for row in hw_r.result_set:
            hid = row[0]
            if hid not in all_hw:
                all_hw[hid] = {}
            all_hw[hid][mid] = _edge_props(row[1])

    if format == "json":
        data = {
            "models": [{
                "id": m.get("id"),
                "display_name": m.get("display_name"),
                "model_type": m.get("model_type"),
                "total_parameters": m.get("total_parameters"),
                "arena_elo_overall": m.get("arena_elo_overall"),
                "cost_input": m.get("cost_input"),
                "cost_output": m.get("cost_output"),
            } for m in models],
            "benchmarks": all_benchmarks,
            "capabilities": all_caps,
            "hardware": all_hw,
        }
        console.print_json(json.dumps(data, default=str))
        return

    names = [m.get("display_name", m.get("id", "?")) for m in models]

    # ── Overview table ──────────────────────────────────────
    overview = Table(title="Model Comparison", show_header=True, header_style="bold cyan")
    overview.add_column("Attribute", style="bold", min_width=18)
    for name in names:
        overview.add_column(name, justify="center", min_width=16)

    attrs = [
        ("Type", "model_type"),
        ("Parameters", None),
        ("Context", "context_window"),
        ("Arena ELO", "arena_elo_overall"),
        ("Cost (in)", "cost_input"),
        ("Cost (out)", "cost_output"),
        ("Open Weights", "open_weights"),
        ("Origin", "origin_country"),
        ("Status", "status"),
    ]

    for label, key in attrs:
        cells: list[str] = []
        for m in models:
            if label == "Parameters":
                active = m.get("active_parameters")
                total = m.get("total_parameters")
                s = _fmt_params(total)
                if active:
                    s += f"\n({_fmt_params(active)} active)"
                cells.append(s)
            elif key == "arena_elo_overall":
                cells.append(_fmt_elo(m.get(key)))
            elif key in ("cost_input", "cost_output"):
                cells.append(_fmt_cost(m.get(key)))
            elif key == "context_window":
                cells.append(_fmt_int(m.get(key)))
            elif key == "open_weights":
                cells.append(_bool_icon(m.get(key)))
            elif key == "status":
                v = m.get(key, "")
                cells.append(f"[{_status_color(v)}]{v}[/]")
            else:
                cells.append(str(m.get(key, "-") or "-"))
        overview.add_row(label, *cells)

    console.print(overview)

    # ── Capabilities comparison ─────────────────────────────
    if all_caps:
        cap_table = Table(title="Capabilities", show_header=True, header_style="bold magenta")
        cap_table.add_column("Capability", style="bold", min_width=18)
        for name in names:
            cap_table.add_column(name, justify="center", min_width=16)
        for cid in sorted(all_caps.keys()):
            row_data = all_caps[cid]
            cap_table.add_row(
                row_data.get("_name", cid),
                *[_tier_style(row_data.get(mid)) for mid in model_ids],
            )
        console.print(cap_table)

    # ── Benchmark comparison (highlight winner) ─────────────
    if all_benchmarks:
        bench_table = Table(title="Benchmarks", show_header=True, header_style="bold yellow")
        bench_table.add_column("Benchmark", style="bold", min_width=22)
        for name in names:
            bench_table.add_column(name, justify="right", min_width=16)

        for bid in sorted(all_benchmarks.keys()):
            row_data = all_benchmarks[bid]
            values = {mid: row_data.get(mid) for mid in model_ids}
            numeric_vals = [v for v in values.values() if v is not None]
            # Lower is better for some benchmarks (like FID), but most are higher-is-better
            lower_is_better = bid in ("fid", "wer_librispeech", "api_latency_p50_ms", "api_latency_p99_ms", "api_ttft_ms")
            if numeric_vals:
                best = min(numeric_vals) if lower_is_better else max(numeric_vals)
            else:
                best = None

            cells: list[str] = []
            for mid in model_ids:
                v = values.get(mid)
                if v is None:
                    cells.append("-")
                elif v == best and len(numeric_vals) > 1:
                    cells.append(f"[bold green]{v:.1f}[/]")
                else:
                    cells.append(f"{v:.1f}")

            bench_table.add_row(row_data.get("_name", bid), *cells)

        console.print(bench_table)

    # ── Hardware fit comparison ──────────────────────────────
    if all_hw:
        hw_table = Table(title="Hardware Fit", show_header=True, header_style="bold green")
        hw_table.add_column("Hardware", style="bold", min_width=22)
        for name in names:
            hw_table.add_column(name, justify="center", min_width=16)

        for hid in sorted(all_hw.keys()):
            hw_data = all_hw[hid]
            cells: list[str] = []
            for mid in model_ids:
                props = hw_data.get(mid)
                if props:
                    tps = props.get("tokens_per_sec")
                    quant = props.get("quantization", "?")
                    s = f"[green]Y[/] {quant}"
                    if tps:
                        s += f"\n{tps:.0f} tok/s"
                    cells.append(s)
                else:
                    cells.append("[dim]-[/]")
            hw_table.add_row(hid.replace("_", " ").title(), *cells)

        console.print(hw_table)


# ───────────────────────────────────────────────────────────────
# 4. modelspec rank --use-case <USE_CASE>
# ───────────────────────────────────────────────────────────────

# Benchmark weights per use case
_USE_CASE_WEIGHTS: dict[str, dict[str, float]] = {
    "coding": {
        "humaneval": 2.0, "swe_bench_verified": 3.0, "live_code_bench": 2.0,
        "aider_polyglot": 2.0, "arena_elo_coding": 2.0, "arena_elo_overall": 1.0,
    },
    "reasoning": {
        "gpqa_diamond": 2.0, "math_500": 2.0, "aime_2025": 2.0,
        "bbh": 1.5, "arena_elo_overall": 1.0, "arena_elo_math": 1.5,
    },
    "chat": {
        "arena_elo_overall": 3.0, "arena_elo_style_control": 1.5,
        "mt_bench": 1.5, "alpaca_eval": 1.0, "ifeval": 1.5,
    },
    "embedding": {
        "mteb_overall": 3.0, "mteb_retrieval": 2.0, "mteb_classification": 1.5,
        "beir": 1.5,
    },
    "agentic": {
        "swe_bench_verified": 2.0, "swe_bench_agent": 3.0, "tau_bench": 2.0,
        "web_arena": 2.0, "arena_elo_overall": 1.0,
    },
    "general": {
        "arena_elo_overall": 2.0, "gpqa_diamond": 1.0, "humaneval": 1.0,
        "math_500": 1.0, "swe_bench_verified": 1.0, "mmlu_pro": 1.0,
    },
}


@app.command()
def rank(
    use_case: str = typer.Option(..., "--use-case", "-u", help="Use case: coding, reasoning, chat, embedding, agentic, general"),
    hardware: Optional[str] = typer.Option(None, "--hardware", "-hw", help="Restrict to models fitting this hardware"),
    license: Optional[str] = typer.Option(None, "--license", "-l", help="Restrict to this license type"),
    top: int = typer.Option(20, "--top", "-n", help="Show top N models"),
    format: Optional[str] = typer.Option(None, "--format", "-f", help="Output format: json"),
) -> None:
    """Rank models by use case, scored on relevant benchmarks."""
    graph = _get_graph()

    weights = _USE_CASE_WEIGHTS.get(use_case.lower())
    if not weights:
        valid = ", ".join(_USE_CASE_WEIGHTS.keys())
        console.print(f"[bold red]Unknown use case:[/] {use_case}")
        console.print(f"  Valid options: {valid}")
        raise typer.Exit(1)

    # Build match
    cypher = "MATCH (m:Model)"
    extra: list[str] = []
    params: dict[str, Any] = {}

    if hardware:
        extra.append("MATCH (m)-[:FITS_ON]->(h:Hardware {id: $hw_id})")
        params["hw_id"] = hardware
    if license:
        extra.append("MATCH (m)-[:LICENSED_AS]->(l:License {id: $lic_id})")
        params["lic_id"] = license

    if extra:
        cypher += " " + " ".join(extra)

    cypher += (
        " OPTIONAL MATCH (m)-[r:SCORED_ON]->(b:Benchmark) "
        "RETURN m.id, m.display_name, m.model_type, m.arena_elo_overall, "
        "m.cost_input, m.total_parameters, collect([b.id, r.value])"
    )

    result = graph.query(cypher, params)

    # Score each model
    scored: list[dict[str, Any]] = []
    for row in result.result_set:
        mid, name, mtype, elo, cost_in, params_val, bench_pairs = row
        bench_map: dict[str, float] = {}
        for pair in bench_pairs:
            if pair[0] and pair[1] is not None:
                bench_map[pair[0]] = pair[1]

        total_score = 0.0
        total_weight = 0.0
        score_parts: dict[str, float] = {}
        for bench_id, weight in weights.items():
            val = bench_map.get(bench_id)
            if val is not None:
                # Normalize: most benchmarks 0-100, ELO ~1000-1400
                if "elo" in bench_id:
                    normalized = (val - 1000) / 400 * 100  # map 1000-1400 to 0-100
                else:
                    normalized = val
                total_score += normalized * weight
                total_weight += weight
                score_parts[bench_id] = val

        final_score = (total_score / total_weight) if total_weight > 0 else 0.0

        scored.append({
            "id": mid,
            "name": name,
            "type": mtype,
            "score": round(final_score, 1),
            "elo": elo,
            "cost_input": cost_in,
            "params": params_val,
            "benchmarks_matched": len(score_parts),
            "score_parts": score_parts,
        })

    scored.sort(key=lambda x: x["score"], reverse=True)
    scored = scored[:top]

    if format == "json":
        console.print_json(json.dumps(scored, default=str))
        return

    if not scored:
        console.print("[yellow]No models found.[/]")
        return

    table = Table(
        title=f"Rankings: {use_case} (top {top})",
        show_header=True,
        header_style="bold cyan",
    )
    table.add_column("#", justify="right", style="dim", width=4)
    table.add_column("Model", style="bold white", min_width=25)
    table.add_column("Type", style="dim")
    table.add_column("Score", justify="right", style="bold yellow")
    table.add_column("ELO", justify="right")
    table.add_column("$/M in", justify="right")
    table.add_column("Params", justify="right")
    table.add_column("Benchmarks", justify="center")

    for i, entry in enumerate(scored, 1):
        rank_str = str(i)
        if i == 1:
            rank_str = f"[bold green]{i}[/]"
        elif i <= 3:
            rank_str = f"[yellow]{i}[/]"

        table.add_row(
            rank_str,
            entry["name"] or entry["id"],
            entry["type"] or "-",
            f"{entry['score']:.1f}",
            _fmt_elo(entry["elo"]),
            _fmt_cost(entry["cost_input"]),
            _fmt_params(entry["params"]),
            f"{entry['benchmarks_matched']}/{len(weights)}",
        )

    console.print(table)

    # Show which benchmarks contributed
    bench_names = ", ".join(weights.keys())
    console.print(f"\n[dim]Scoring benchmarks: {bench_names}[/]")


# ───────────────────────────────────────────────────────────────
# 5. modelspec stats
# ───────────────────────────────────────────────────────────────

@app.command()
def stats(
    format: Optional[str] = typer.Option(None, "--format", "-f", help="Output format: json"),
) -> None:
    """Show database overview: node counts, edge counts, coverage."""
    graph = _get_graph()

    # Node counts by label
    labels_result = graph.query("CALL db.labels()")
    node_counts: dict[str, int] = {}
    for row in labels_result.result_set:
        label = row[0]
        count_r = graph.query(f"MATCH (n:{label}) RETURN count(n)")
        node_counts[label] = count_r.result_set[0][0]

    # Edge counts by type
    rel_result = graph.query("CALL db.relationshipTypes()")
    edge_counts: dict[str, int] = {}
    for row in rel_result.result_set:
        rtype = row[0]
        count_r = graph.query(f"MATCH ()-[r:{rtype}]->() RETURN count(r)")
        edge_counts[rtype] = count_r.result_set[0][0]

    # Model completeness
    comp_result = graph.query(
        "MATCH (m:Model) "
        "RETURN m.id, m.display_name, m.model_type, m.card_completeness "
        "ORDER BY m.card_completeness DESC"
    )

    # Type breakdown
    type_result = graph.query(
        "MATCH (m:Model) "
        "RETURN m.model_type, count(m) "
        "ORDER BY count(m) DESC"
    )

    if format == "json":
        data = {
            "node_counts": node_counts,
            "edge_counts": edge_counts,
            "models": [
                {"id": r[0], "name": r[1], "type": r[2], "completeness": r[3]}
                for r in comp_result.result_set
            ],
            "type_breakdown": [
                {"type": r[0], "count": r[1]}
                for r in type_result.result_set
            ],
        }
        console.print_json(json.dumps(data, default=str))
        return

    total_nodes = sum(node_counts.values())
    total_edges = sum(edge_counts.values())

    # Header
    console.print(Panel(
        f"[bold]{total_nodes}[/] nodes | [bold]{total_edges}[/] edges | "
        f"[bold]{node_counts.get('Model', 0)}[/] models",
        title="ModelSpec Database",
        border_style="blue",
    ))

    # Node counts
    node_table = Table(title="Nodes by Label", show_header=True, header_style="bold cyan")
    node_table.add_column("Label", style="bold", min_width=15)
    node_table.add_column("Count", justify="right")
    for label, count in sorted(node_counts.items(), key=lambda x: -x[1]):
        node_table.add_row(label, str(count))
    console.print(node_table)

    # Edge counts
    edge_table = Table(title="Edges by Type", show_header=True, header_style="bold magenta")
    edge_table.add_column("Relationship", style="bold", min_width=20)
    edge_table.add_column("Count", justify="right")
    for rtype, count in sorted(edge_counts.items(), key=lambda x: -x[1]):
        edge_table.add_row(rtype, str(count))
    console.print(edge_table)

    # Model type breakdown
    if type_result.result_set:
        type_table = Table(title="Models by Type", show_header=True, header_style="bold green")
        type_table.add_column("Type", style="bold", min_width=20)
        type_table.add_column("Count", justify="right")
        for row in type_result.result_set:
            type_table.add_row(row[0] or "(untyped)", str(row[1]))
        console.print(type_table)

    # Completeness
    if comp_result.result_set:
        comp_table = Table(title="Card Completeness", show_header=True, header_style="bold yellow")
        comp_table.add_column("Model", style="bold", min_width=30)
        comp_table.add_column("Type", style="dim")
        comp_table.add_column("Completeness", justify="right")
        for row in comp_result.result_set:
            pct = row[3]
            if pct is not None:
                if pct >= 50:
                    clr = "green"
                elif pct >= 25:
                    clr = "yellow"
                else:
                    clr = "red"
                comp_str = f"[{clr}]{pct:.1f}%[/]"
            else:
                comp_str = "-"
            comp_table.add_row(row[1] or row[0], row[2] or "-", comp_str)
        console.print(comp_table)


# ───────────────────────────────────────────────────────────────
# 6. modelspec hardware <hardware_id>
# ───────────────────────────────────────────────────────────────

@app.command()
def hardware(
    hardware_id: str = typer.Argument(..., help="Hardware ID, e.g. macbook_air_m4_24gb"),
    format: Optional[str] = typer.Option(None, "--format", "-f", help="Output format: json"),
) -> None:
    """Show models that fit on a specific hardware device."""
    graph = _get_graph()

    result = graph.query(
        "MATCH (m:Model)-[r:FITS_ON]->(h:Hardware {id: $hw_id}) "
        "RETURN m.id, m.display_name, m.model_type, m.arena_elo_overall, "
        "m.total_parameters, m.cost_input, r "
        "ORDER BY m.arena_elo_overall DESC",
        {"hw_id": hardware_id},
    )

    if not result.result_set:
        # Check if the hardware exists at all
        hw_check = graph.query(
            "MATCH (h:Hardware {id: $hw_id}) RETURN h.id", {"hw_id": hardware_id}
        )
        if not hw_check.result_set:
            # List available hardware
            all_hw = graph.query("MATCH (h:Hardware) RETURN h.id ORDER BY h.id")
            if all_hw.result_set:
                hw_list = ", ".join(r[0] for r in all_hw.result_set)
                console.print(f"[bold red]Hardware not found:[/] {hardware_id}")
                console.print(f"  Available: {hw_list}")
            else:
                console.print(f"[bold red]No hardware profiles in the database.[/]")
        else:
            console.print(f"[yellow]No models fit on {hardware_id}.[/]")
        return

    if format == "json":
        rows = []
        for r in result.result_set:
            ep = _edge_props(r[6])
            rows.append({
                "id": r[0], "name": r[1], "type": r[2],
                "arena_elo": r[3], "parameters": r[4], "cost_input": r[5],
                **ep,
            })
        console.print_json(json.dumps(rows, default=str))
        return

    table = Table(
        title=f"Models for {hardware_id.replace('_', ' ').title()}",
        show_header=True,
        header_style="bold green",
    )
    table.add_column("Model", style="bold white", min_width=25)
    table.add_column("Type", style="dim")
    table.add_column("ELO", justify="right")
    table.add_column("Params", justify="right")
    table.add_column("Quant", justify="center")
    table.add_column("VRAM/RAM", justify="right")
    table.add_column("tok/s", justify="right")
    table.add_column("TTFT", justify="right")
    table.add_column("Engine", justify="center")

    for r in result.result_set:
        ep = _edge_props(r[6])
        table.add_row(
            r[1] or r[0],
            r[2] or "-",
            _fmt_elo(r[3]),
            _fmt_params(r[4]),
            ep.get("quantization", "-"),
            _fmt_float(ep.get("vram_usage_gb"), " GB"),
            _fmt_float(ep.get("tokens_per_sec"), ""),
            _fmt_float(ep.get("ttft_ms"), " ms"),
            ep.get("inference_engine", "-"),
        )

    console.print(table)


# ───────────────────────────────────────────────────────────────
# Entry point (for Typer)
# ───────────────────────────────────────────────────────────────

def main() -> None:
    app()


if __name__ == "__main__":
    main()
