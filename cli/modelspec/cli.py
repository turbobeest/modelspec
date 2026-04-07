"""ModelSpec CLI — explore, search, compare, and rank AI models.

Entry point: ``modelspec`` (registered in pyproject.toml).
Graph commands use FalkorDB on localhost:6382.
Community commands (gaps, research, contribute, validate) work offline from YAML files.
"""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import date
from pathlib import Path
from typing import Any, Optional

import typer
from falkordb import FalkorDB
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
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
# Offline YAML helpers (used by gaps, research, contribute, validate)
# ───────────────────────────────────────────────────────────────

# Resolve project root relative to this file:
# cli/modelspec/cli.py -> project root is ../../..
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
_MODELS_DIR = _PROJECT_ROOT / "models"

# Lazy import — schema.card lives at project root level
_ModelCard = None  # type: ignore[assignment]


def _get_model_card_class():
    """Import ModelCard lazily so graph-only commands don't need the schema on sys.path."""
    global _ModelCard
    if _ModelCard is not None:
        return _ModelCard
    root = str(_PROJECT_ROOT)
    if root not in sys.path:
        sys.path.insert(0, root)
    from schema.card import ModelCard
    _ModelCard = ModelCard
    return ModelCard


def _discover_card_files(
    provider: str | None = None,
) -> list[Path]:
    """Find all .md model card files, optionally filtered by provider."""
    if provider:
        provider_dir = _MODELS_DIR / provider
        if not provider_dir.is_dir():
            return []
        return sorted(provider_dir.glob("*.md"))
    return sorted(_MODELS_DIR.glob("*/*.md"))


def _load_cards(
    provider: str | None = None,
    model_type: str | None = None,
) -> list[Any]:
    """Load and parse all model cards, with optional filters."""
    ModelCard = _get_model_card_class()
    cards = []
    for path in _discover_card_files(provider=provider):
        try:
            card = ModelCard.from_yaml_file(path)
            if model_type and card.identity.model_type:
                if card.identity.model_type.value != model_type:
                    continue
            elif model_type and not card.identity.model_type:
                continue
            card._source_path = path  # stash for later use
            cards.append(card)
        except Exception:
            # Skip unparseable cards silently in bulk load
            continue
    return cards


# Key benchmark fields that matter most
_KEY_BENCHMARKS = [
    "humaneval", "gpqa_diamond", "mmlu_pro", "arena_elo_overall",
    "swe_bench_verified", "math_500", "aime_2025", "live_code_bench",
    "ifeval", "mmmu", "mteb_overall",
]

# Major providers get a higher importance multiplier
_MAJOR_PROVIDERS = {
    "openai": 3.0, "anthropic": 3.0, "google": 3.0, "meta": 2.5,
    "mistral": 2.0, "deepseek": 2.0, "qwen": 2.0, "xai": 2.0,
    "cohere": 1.5, "microsoft": 1.5, "nvidia": 1.5, "amazon": 1.5,
}


def _compute_gap_info(card: Any) -> dict[str, Any]:
    """Analyze a card for missing data and compute a priority score."""
    missing: list[str] = []

    # Benchmarks
    bench = card.benchmarks
    filled_bench = bench.filled_count()
    if filled_bench == 0:
        missing.append("benchmarks (none)")
    elif filled_bench < 5:
        missing.append(f"benchmarks ({filled_bench} filled)")

    # Cost
    if card.cost.input is None:
        missing.append("cost.input")
    if card.cost.output is None:
        missing.append("cost.output")

    # Architecture
    if card.architecture.total_parameters is None:
        missing.append("total_parameters")

    # Context window (None means missing; 0 is a valid value for non-text models)
    if card.modalities.text.context_window is None:
        missing.append("context_window")

    # Capabilities — check if the key sub-sections have overall tier set
    cap = card.capabilities
    cap_filled = False
    for section_name in ("coding", "reasoning", "tool_use"):
        sub = getattr(cap, section_name)
        if sub.overall is not None:
            cap_filled = True
            break
    # Also check language and creative via their own key fields
    if not cap_filled and card.capabilities.language.multilingual:
        cap_filled = True
    if not cap_filled and card.capabilities.creative.writing is not None:
        cap_filled = True
    if not cap_filled:
        missing.append("capabilities")

    # Platform availability
    platforms = card.availability.platforms_available()
    if len(platforms) == 0:
        missing.append("availability")

    # Model importance heuristic
    provider = card.identity.provider
    importance = _MAJOR_PROVIDERS.get(provider, 1.0)

    # Bump importance for models with community signals
    if card.adoption.huggingface_downloads and card.adoption.huggingface_downloads > 100_000:
        importance *= 1.5
    arena_elo = card.benchmarks.scores.get("arena_elo_overall")
    if arena_elo and arena_elo > 1200:
        importance *= 1.3

    priority = importance * len(missing)

    return {
        "model_id": card.identity.model_id,
        "display_name": card.identity.display_name,
        "completeness": card.card_completeness,
        "missing": missing,
        "missing_count": len(missing),
        "priority": round(priority, 1),
        "provider": provider,
    }


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


# ═══════════════════════════════════════════════════════════════
# Community contribution commands (offline, YAML-based)
# ═══════════════════════════════════════════════════════════════


# ───────────────────────────────────────────────────────────────
# 7. modelspec gaps — find data gaps
# ───────────────────────────────────────────────────────────────

@app.command()
def gaps(
    type: Optional[str] = typer.Option(None, "--type", "-t", help="Filter by model_type (e.g. llm-chat, vlm)"),
    provider: Optional[str] = typer.Option(None, "--provider", "-p", help="Filter by provider slug"),
    top: int = typer.Option(20, "--top", "-n", help="Show top N models with gaps"),
    field: Optional[str] = typer.Option(None, "--field", help="Show gaps for a specific field (benchmarks, cost, capabilities, context_window, availability, total_parameters)"),
) -> None:
    """Find models with the most missing data, ranked by priority.

    Works offline from YAML model cards in models/.
    """
    cards = _load_cards(provider=provider, model_type=type)
    if not cards:
        console.print("[yellow]No model cards found matching your filters.[/]")
        raise typer.Exit(1)

    gap_rows = []
    for card in cards:
        info = _compute_gap_info(card)
        # If --field is given, only include models missing that field
        if field:
            matches = [m for m in info["missing"] if field.lower() in m.lower()]
            if not matches:
                continue
        if info["missing_count"] == 0:
            continue
        gap_rows.append(info)

    # Sort by priority descending
    gap_rows.sort(key=lambda x: x["priority"], reverse=True)
    gap_rows = gap_rows[:top]

    if not gap_rows:
        console.print("[green]All model cards look complete for the selected criteria.[/]")
        return

    table = Table(
        title=f"Data Gaps (top {len(gap_rows)} of {len(cards)} models)",
        show_header=True,
        header_style="bold cyan",
    )
    table.add_column("#", justify="right", style="dim", width=4)
    table.add_column("Model", style="bold white", min_width=30)
    table.add_column("Provider", style="dim", min_width=10)
    table.add_column("Complete", justify="right", min_width=9)
    table.add_column("Missing Fields", style="yellow", min_width=35)
    table.add_column("Priority", justify="right", style="bold magenta")

    for i, row in enumerate(gap_rows, 1):
        pct = row["completeness"]
        if pct >= 50:
            comp_str = f"[green]{pct:.1f}%[/]"
        elif pct >= 25:
            comp_str = f"[yellow]{pct:.1f}%[/]"
        else:
            comp_str = f"[red]{pct:.1f}%[/]"

        missing_str = ", ".join(row["missing"][:5])
        if len(row["missing"]) > 5:
            missing_str += f" (+{len(row['missing']) - 5} more)"

        table.add_row(
            str(i),
            row["display_name"] or row["model_id"],
            row["provider"],
            comp_str,
            missing_str,
            f"{row['priority']:.1f}",
        )

    console.print(table)

    # Summary
    total_gaps = sum(r["missing_count"] for r in gap_rows)
    console.print(f"\n[dim]Total gap fields across shown models: {total_gaps}[/]")
    console.print("[dim]Run [bold]modelspec research <model_id>[/bold] to auto-fill data from HuggingFace.[/]")


# ───────────────────────────────────────────────────────────────
# 8. modelspec research <model_id> — auto-research a model
# ───────────────────────────────────────────────────────────────

def _find_card_path(model_id: str) -> Path | None:
    """Find the YAML file for a given model_id like 'openai/gpt-4o'."""
    parts = model_id.split("/", 1)
    if len(parts) != 2:
        return None
    provider, slug = parts
    path = _MODELS_DIR / provider / f"{slug}.md"
    if path.exists():
        return path
    # Try case-insensitive match
    provider_dir = _MODELS_DIR / provider
    if provider_dir.is_dir():
        for f in provider_dir.glob("*.md"):
            if f.stem.lower() == slug.lower():
                return f
    return None


def _fetch_huggingface_data(model_id: str) -> dict[str, Any]:
    """Fetch model metadata from HuggingFace Hub API."""
    import httpx

    url = f"https://huggingface.co/api/models/{model_id}"
    try:
        resp = httpx.get(url, timeout=15.0, follow_redirects=True)
        if resp.status_code == 200:
            return resp.json()
        return {}
    except Exception:
        return {}


def _apply_hf_updates(card: Any, hf_data: dict[str, Any]) -> dict[str, tuple[Any, Any]]:
    """Apply HuggingFace data to a card, only filling None/empty fields.

    Returns a dict of {field_path: (old_value, new_value)} for changes made.
    """
    changes: dict[str, tuple[Any, Any]] = {}

    # Downloads
    downloads = hf_data.get("downloads")
    if downloads and not card.adoption.huggingface_downloads:
        old = card.adoption.huggingface_downloads
        card.adoption.huggingface_downloads = downloads
        changes["adoption.huggingface_downloads"] = (old, downloads)

    # Likes
    likes = hf_data.get("likes")
    if likes and not card.adoption.huggingface_likes:
        old = card.adoption.huggingface_likes
        card.adoption.huggingface_likes = likes
        changes["adoption.huggingface_likes"] = (old, likes)

    # Tags -> identity.tags (only if empty)
    hf_tags = hf_data.get("tags", [])
    if hf_tags and not card.identity.tags:
        card.identity.tags = hf_tags[:20]  # cap at 20 tags
        changes["identity.tags"] = ([], hf_tags[:20])

    # Pipeline tag
    pipeline_tag = hf_data.get("pipeline_tag")
    if pipeline_tag and not card.identity.pipeline_tag:
        old = card.identity.pipeline_tag
        card.identity.pipeline_tag = pipeline_tag
        changes["identity.pipeline_tag"] = (old, pipeline_tag)

    # License
    license_str = hf_data.get("cardData", {}).get("license") if isinstance(hf_data.get("cardData"), dict) else None
    if not license_str:
        # Try top-level tags for license
        for tag in hf_tags:
            if tag.startswith("license:"):
                license_str = tag.split(":", 1)[1]
                break

    # Parameter count from safetensors
    safetensors = hf_data.get("safetensors")
    if isinstance(safetensors, dict):
        total = safetensors.get("total")
        if total and card.architecture.total_parameters is None:
            card.architecture.total_parameters = total
            changes["architecture.total_parameters"] = (None, total)

    # Base model from tags
    for tag in hf_tags:
        if tag.startswith("base_model:"):
            base = tag.split(":", 1)[1]
            if not card.lineage.base_model:
                card.lineage.base_model = base
                changes["lineage.base_model"] = ("", base)
            break

    # Library name
    library = hf_data.get("library_name")
    if library and not card.lineage.library_name:
        card.lineage.library_name = library
        changes["lineage.library_name"] = ("", library)

    # HuggingFace URL in sources
    hf_id = hf_data.get("id") or hf_data.get("modelId")
    if hf_id and not card.sources.huggingface_url:
        url = f"https://huggingface.co/{hf_id}"
        card.sources.huggingface_url = url
        changes["sources.huggingface_url"] = ("", url)

    # HuggingFace platform availability
    if hf_id and not card.availability.huggingface.available:
        card.availability.huggingface.available = True
        card.availability.huggingface.model_id = hf_id
        changes["availability.huggingface.available"] = (False, True)

    # Update last_scraped timestamp
    card.sources.last_scraped_huggingface = str(date.today())

    return changes


@app.command()
def research(
    model_id: str = typer.Argument(..., help="Model ID, e.g. meta/llama-3.1-8b-instruct"),
    source: str = typer.Option("all", "--source", "-s", help="Data source: huggingface, all"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would change without writing"),
) -> None:
    """Auto-research a model: fetch data from HuggingFace and update its card.

    Only fills empty/None fields — never overwrites existing data.
    """
    ModelCard = _get_model_card_class()

    card_path = _find_card_path(model_id)
    if not card_path:
        console.print(f"[bold red]Card not found:[/] {model_id}")
        console.print(f"  Expected at: models/{model_id.replace('/', '/')}.md")
        raise typer.Exit(1)

    card = ModelCard.from_yaml_file(card_path)
    all_changes: dict[str, tuple[Any, Any]] = {}

    # HuggingFace
    if source in ("huggingface", "all"):
        # For open-weights models, use model_id directly;
        # for proprietary, try the HF URL from sources
        hf_id = model_id
        if card.sources.huggingface_url:
            # Extract id from URL like https://huggingface.co/meta-llama/...
            url_parts = card.sources.huggingface_url.rstrip("/").split("huggingface.co/")
            if len(url_parts) == 2:
                hf_id = url_parts[1]

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            progress.add_task(f"Fetching HuggingFace data for {hf_id}...", total=None)
            hf_data = _fetch_huggingface_data(hf_id)

        if hf_data:
            hf_changes = _apply_hf_updates(card, hf_data)
            all_changes.update(hf_changes)
            if not hf_changes:
                console.print(f"[dim]HuggingFace: no new data to fill (existing fields already populated).[/]")
        else:
            console.print(f"[yellow]HuggingFace: no data found for {hf_id}[/]")

    if not all_changes:
        console.print(f"\n[yellow]No changes to make for {model_id}.[/]")
        return

    # Show diff
    diff_lines = []
    for field_path, (old_val, new_val) in sorted(all_changes.items()):
        old_display = repr(old_val) if old_val not in (None, "", [], False) else "[dim]empty[/]"
        new_display = repr(new_val)
        # Truncate long values
        if len(str(new_display)) > 60:
            new_display = str(new_display)[:57] + "..."
        diff_lines.append(f"  [red]- {field_path}: {old_display}[/]")
        diff_lines.append(f"  [green]+ {field_path}: {new_display}[/]")

    console.print(Panel(
        "\n".join(diff_lines),
        title=f"Changes for {model_id} ({len(all_changes)} fields)",
        border_style="cyan",
    ))

    if dry_run:
        console.print(f"\n[yellow]Dry run — no files modified.[/]")
        console.print(f"  Run without --dry-run to write changes to {card_path.relative_to(_PROJECT_ROOT)}")
        return

    # Write updated card
    yaml_content = card.to_yaml()
    card_path.write_text(yaml_content, encoding="utf-8")
    console.print(f"\n[green]Updated {len(all_changes)} fields in {card_path.relative_to(_PROJECT_ROOT)}[/]")


# ───────────────────────────────────────────────────────────────
# 9. modelspec contribute — submit a PR
# ───────────────────────────────────────────────────────────────

def _run_cmd(cmd: list[str], check: bool = True, capture: bool = True) -> subprocess.CompletedProcess:
    """Run a subprocess command, returning the result."""
    return subprocess.run(
        cmd,
        cwd=str(_PROJECT_ROOT),
        capture_output=capture,
        text=True,
        check=check,
    )


@app.command()
def contribute(
    message: Optional[str] = typer.Option(None, "--message", "-m", help="Commit/PR message describing your changes"),
) -> None:
    """Submit your model card changes as a pull request to turbobeest/modelspec.

    Requires the GitHub CLI (gh) to be installed and authenticated.
    """
    # 1. Check gh CLI
    try:
        _run_cmd(["gh", "auth", "status"])
    except (FileNotFoundError, subprocess.CalledProcessError):
        console.print("[bold red]Error:[/] GitHub CLI (gh) is not installed or not authenticated.")
        console.print("  Install: https://cli.github.com/")
        console.print("  Auth:    gh auth login")
        raise typer.Exit(1)

    # 2. Check for changes
    diff_result = _run_cmd(["git", "diff", "--name-only"], check=False)
    staged_result = _run_cmd(["git", "diff", "--name-only", "--cached"], check=False)
    untracked_result = _run_cmd(["git", "ls-files", "--others", "--exclude-standard", "models/"], check=False)

    changed_files = set()
    for output in (diff_result.stdout, staged_result.stdout, untracked_result.stdout):
        for line in output.strip().splitlines():
            line = line.strip()
            if line and line.startswith("models/") and line.endswith(".md"):
                changed_files.add(line)

    if not changed_files:
        console.print("[yellow]No modified or new model cards found.[/]")
        console.print("  Run [bold]modelspec research <model_id>[/] first to enrich a model card.")
        raise typer.Exit(0)

    console.print(f"[bold]Found {len(changed_files)} changed model card(s):[/]")
    for f in sorted(changed_files):
        console.print(f"  [green]+[/] {f}")

    # 3. Determine upstream vs fork
    remote_result = _run_cmd(["git", "remote", "-v"], check=False)
    is_fork = "turbobeest/modelspec" not in remote_result.stdout

    # 4. Get username
    user_result = _run_cmd(["gh", "api", "user", "--jq", ".login"], check=False)
    username = user_result.stdout.strip() or "contributor"

    # 5. Build branch name and message
    today = date.today().strftime("%Y%m%d")
    model_names = []
    for f in sorted(changed_files):
        parts = Path(f).stem
        model_names.append(parts)

    summary = "-".join(model_names[:3])
    if len(model_names) > 3:
        summary += f"-and-{len(model_names) - 3}-more"
    branch_name = f"contrib/{username}/{today}-{summary}"

    if not message:
        message = f"Data enrichment: {', '.join(model_names[:5])}"
        if len(model_names) > 5:
            message += f" and {len(model_names) - 5} more"

    # 6. Load before/after completeness for PR body
    ModelCard = _get_model_card_class()
    pr_body_lines = ["## Summary", "", f"Updated {len(changed_files)} model card(s):", ""]
    for f in sorted(changed_files):
        card_path = _PROJECT_ROOT / f
        try:
            card = ModelCard.from_yaml_file(card_path)
            pr_body_lines.append(f"- **{card.identity.display_name}** (`{card.identity.model_id}`): {card.card_completeness:.1f}% complete")
        except Exception:
            pr_body_lines.append(f"- `{f}`")

    pr_body_lines.extend([
        "",
        "## Details",
        "",
        f"Fields enriched via `modelspec research`.",
        "",
        "## Test plan",
        "",
        "- [ ] `modelspec validate` passes",
        "- [ ] Spot-check updated fields against source",
    ])

    pr_body = "\n".join(pr_body_lines)

    # 7. Create branch, commit, push, open PR
    try:
        _run_cmd(["git", "checkout", "-b", branch_name])
        console.print(f"  Created branch: [bold]{branch_name}[/]")
    except subprocess.CalledProcessError:
        console.print(f"[bold red]Error:[/] Could not create branch {branch_name}")
        raise typer.Exit(1)

    try:
        for f in sorted(changed_files):
            _run_cmd(["git", "add", f])
        _run_cmd(["git", "commit", "-m", message])
        console.print(f"  Committed: {message}")
    except subprocess.CalledProcessError as exc:
        console.print(f"[bold red]Error committing:[/] {exc.stderr}")
        raise typer.Exit(1)

    try:
        if is_fork:
            _run_cmd(["git", "push", "-u", "origin", branch_name])
        else:
            _run_cmd(["git", "push", "-u", "origin", branch_name])
        console.print("  Pushed to origin.")
    except subprocess.CalledProcessError as exc:
        console.print(f"[bold red]Error pushing:[/] {exc.stderr}")
        raise typer.Exit(1)

    # Open PR
    try:
        pr_result = _run_cmd([
            "gh", "pr", "create",
            "--repo", "turbobeest/modelspec",
            "--title", f"Data enrichment: {summary}",
            "--body", pr_body,
        ])
        pr_url = pr_result.stdout.strip()
        console.print(f"\n[bold green]Pull request created![/]")
        console.print(f"  {pr_url}")
    except subprocess.CalledProcessError as exc:
        console.print(f"[bold red]Error creating PR:[/] {exc.stderr}")
        raise typer.Exit(1)


# ───────────────────────────────────────────────────────────────
# 10. modelspec validate — validate all cards
# ───────────────────────────────────────────────────────────────

@app.command()
def validate(
    fix: bool = typer.Option(False, "--fix", help="Attempt to fix common issues"),
) -> None:
    """Validate all model cards against the schema and report issues.

    Works offline from YAML model cards in models/.
    """
    ModelCard = _get_model_card_class()

    card_files = _discover_card_files()
    if not card_files:
        console.print("[yellow]No model cards found in models/.[/]")
        raise typer.Exit(1)

    valid_cards = []
    errors: list[tuple[Path, str]] = []
    fixed: list[tuple[Path, str]] = []

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task(f"Validating {len(card_files)} cards...", total=len(card_files))

        for path in card_files:
            try:
                card = ModelCard.from_yaml_file(path)
                valid_cards.append(card)

                # Check for common issues even on parseable cards
                issues = []

                # Missing required identity fields
                if not card.identity.display_name:
                    issues.append("missing display_name")
                if not card.identity.provider:
                    issues.append("missing provider")

                # Enum mismatches (already caught by Pydantic, but double check)
                if card.identity.model_type is None:
                    issues.append("no model_type set")

                if issues and fix:
                    changed = False
                    if not card.identity.display_name:
                        # Derive from model_id
                        card.identity.display_name = card.identity.model_id.split("/")[-1].replace("-", " ").title()
                        changed = True
                    if changed:
                        yaml_content = card.to_yaml()
                        path.write_text(yaml_content, encoding="utf-8")
                        fixed.append((path, "; ".join(issues)))

                if issues and not fix:
                    for issue in issues:
                        errors.append((path, f"warning: {issue}"))

            except Exception as exc:
                err_msg = str(exc)
                # Truncate long error messages
                if len(err_msg) > 120:
                    err_msg = err_msg[:117] + "..."
                errors.append((path, err_msg))

                if fix:
                    # Try to fix by re-loading raw YAML and patching
                    try:
                        import yaml
                        content = path.read_text(encoding="utf-8")
                        parts = content.split("---", 2)
                        if len(parts) >= 3:
                            data = yaml.safe_load(parts[1]) or {}
                            # Common fix: remove invalid enum values
                            if "status" in data and data["status"] not in (
                                "active", "beta", "alpha", "deprecated", "sunset", "preview"
                            ):
                                data["status"] = "active"
                            yaml_str = yaml.dump(data, default_flow_style=False, sort_keys=False, allow_unicode=True)
                            new_content = f"---\n{yaml_str}---\n\n{parts[2].strip()}"
                            path.write_text(new_content, encoding="utf-8")
                            # Try parsing again
                            card = ModelCard.from_yaml_file(path)
                            valid_cards.append(card)
                            fixed.append((path, "re-serialized with fixes"))
                    except Exception:
                        pass

            progress.advance(task)

    # Report errors
    if errors:
        err_table = Table(
            title=f"Validation Issues ({len(errors)})",
            show_header=True,
            header_style="bold red",
        )
        err_table.add_column("File", style="dim", min_width=40)
        err_table.add_column("Issue", style="yellow")
        for path, msg in errors[:50]:
            rel_path = str(path.relative_to(_PROJECT_ROOT))
            err_table.add_row(rel_path, msg)
        if len(errors) > 50:
            console.print(f"[dim]... and {len(errors) - 50} more issues[/]")
        console.print(err_table)

    if fixed:
        fix_table = Table(
            title=f"Fixed ({len(fixed)})",
            show_header=True,
            header_style="bold green",
        )
        fix_table.add_column("File", style="dim", min_width=40)
        fix_table.add_column("Fix Applied", style="green")
        for path, msg in fixed:
            rel_path = str(path.relative_to(_PROJECT_ROOT))
            fix_table.add_row(rel_path, msg)
        console.print(fix_table)

    # Completeness distribution
    if valid_cards:
        completeness_values = [c.card_completeness for c in valid_cards]
        avg = sum(completeness_values) / len(completeness_values)
        high = len([v for v in completeness_values if v >= 50])
        mid = len([v for v in completeness_values if 25 <= v < 50])
        low = len([v for v in completeness_values if v < 25])

        dist_table = Table(
            title="Completeness Distribution",
            show_header=True,
            header_style="bold cyan",
        )
        dist_table.add_column("Range", style="bold", min_width=15)
        dist_table.add_column("Count", justify="right")
        dist_table.add_column("Bar", min_width=30)

        max_count = max(high, mid, low, 1)
        bar_width = 30

        dist_table.add_row(
            "[green]>= 50%[/]",
            str(high),
            "[green]" + "#" * int(high / max_count * bar_width) + "[/]",
        )
        dist_table.add_row(
            "[yellow]25-49%[/]",
            str(mid),
            "[yellow]" + "#" * int(mid / max_count * bar_width) + "[/]",
        )
        dist_table.add_row(
            "[red]< 25%[/]",
            str(low),
            "[red]" + "#" * int(low / max_count * bar_width) + "[/]",
        )
        console.print(dist_table)

        console.print(
            f"\n[bold]Summary:[/] {len(valid_cards)} valid / {len(card_files)} total cards | "
            f"Average completeness: [bold]{avg:.1f}%[/]"
        )

    if errors and not fix:
        console.print("\n[dim]Run with --fix to attempt automatic fixes.[/]")


# ───────────────────────────────────────────────────────────────
# Entry point (for Typer)
# ───────────────────────────────────────────────────────────────

def main() -> None:
    app()


if __name__ == "__main__":
    main()
