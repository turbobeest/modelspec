"""Commands that answer from the local snapshot, with no database and no network.

This is the interface dpf's ticket author calls, so it is a contract rather than
a convenience:

* `--json` emits a versioned envelope. `schema_version` changes only when the
  shape changes incompatibly.
* Every answer carries the freshness of the data behind it. A caller can record
  which snapshot informed a decision, which is the honest-broker requirement.
* Exit codes distinguish the cases a caller must tell apart:

      0  an answer
      1  a usage or runtime error
      2  no result matched the constraints, which is a real answer
      3  no snapshot; run `modelspec snapshot fetch`
      4  the snapshot is stale and --require-fresh was given

  The pre-existing graph commands exit 0 when FalkorDB is unreachable, so a
  script cannot tell an answer from a failure. Nothing here does that.
"""

from __future__ import annotations

import json
import sys
from typing import Any

import typer

from . import snapshot as snap

#: Bumped only for an incompatible change to the JSON envelope.
SCHEMA_VERSION = "1.0"

EXIT_OK = 0
EXIT_ERROR = 1
EXIT_NO_MATCH = 2
EXIT_NO_SNAPSHOT = 3
EXIT_STALE = 4

app = typer.Typer(help="Answer from the local snapshot. No database, no network, no credential.")
snapshot_app = typer.Typer(help="Manage the local snapshot.")
app.add_typer(snapshot_app, name="snapshot")


def _emit(payload: dict[str, Any], as_json: bool) -> None:
    if as_json:
        typer.echo(json.dumps(payload, indent=2, default=str))


def _envelope(command: str, snapshot: snap.Snapshot, result: Any) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "command": command,
        "freshness": snapshot.freshness(),
        "result": result,
    }


def _load_or_exit(require_fresh: bool) -> snap.Snapshot:
    try:
        snapshot = snap.load()
    except snap.SnapshotMissing as exc:
        typer.echo(f"error: {exc}", err=True)
        raise typer.Exit(EXIT_NO_SNAPSHOT) from exc
    if require_fresh and snapshot.is_stale:
        typer.echo(
            f"error: snapshot is {snapshot.age_days:.0f} days old and --require-fresh was given. "
            "Run `modelspec snapshot fetch`.", err=True)
        raise typer.Exit(EXIT_STALE)
    if snapshot.is_stale:
        typer.echo(
            f"warning: snapshot is {snapshot.age_days:.0f} days old "
            f"(stale after {snap.STALE_AFTER_DAYS}). Answers may be out of date.", err=True)
    return snapshot


def _candidates(snapshot: snap.Snapshot) -> list[Any]:
    """Rebuild ranking records from the snapshot, reusing the tested scorer."""
    sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[2]))
    from pipeline.ranking import Candidate

    return [
        Candidate(
            model_id=c["model_id"], display_name=c["display_name"], provider=c["provider"],
            model_type=c.get("model_type"), model_subtypes=c.get("model_subtypes") or [],
            benchmark_scores=c.get("benchmark_scores") or {},
            capability_tiers=c.get("capability_tiers") or {},
            cost_input=c.get("cost_input"), context_window=c.get("context_window"),
            open_weights=bool(c.get("open_weights")), scores_as_of=c.get("scores_as_of"),
            fits=c.get("fits") or {},
        )
        for c in snapshot.data["candidates"]["candidates"]
    ]


@snapshot_app.command("fetch")
def snapshot_fetch(
    origin: str = typer.Option(snap.DEFAULT_ORIGIN, help="Where to fetch from."),
) -> None:
    """Download the published export. The only command that needs the network."""
    try:
        result = snap.fetch(origin)
    except Exception as exc:  # noqa: BLE001 - surfaced to the user, not swallowed
        typer.echo(f"error: could not fetch the snapshot: {exc}", err=True)
        raise typer.Exit(EXIT_ERROR) from exc
    typer.echo(f"fetched {len(result.data['candidates']['candidates'])} models "
               f"from {origin} (build {result.build_commit[:12]})")
    typer.echo(f"cached at {result.path}")


@snapshot_app.command("status")
def snapshot_status(as_json: bool = typer.Option(False, "--json")) -> None:
    """Show what snapshot is cached and how old it is."""
    info = snap.status()
    if as_json:
        typer.echo(json.dumps({"schema_version": SCHEMA_VERSION, "result": info}, indent=2))
    elif not info["present"]:
        typer.echo(info["message"])
    else:
        typer.echo(f"snapshot   {info['path']}")
        typer.echo(f"fetched    {info['fetched_at']} ({info['age_days']:.1f} days ago)")
        typer.echo(f"build      {info['build_commit'][:12]} from {info['origin']}")
        typer.echo(f"stale      {info['stale']}")
    if not info["present"]:
        raise typer.Exit(EXIT_NO_SNAPSHOT)


@app.command("rank")
def rank_offline(
    use_case: str = typer.Argument(..., help="Use-case profile, e.g. coding."),
    limit: int = typer.Option(10, "--limit", "-n"),
    open_weights: bool = typer.Option(False, "--open-weights", help="Only models you can download."),
    fits: str = typer.Option(None, "--fits", help="Hardware id the model must fit on."),
    max_cost: float = typer.Option(None, "--max-cost", help="Maximum $ per million input tokens."),
    price_sensitivity: float = typer.Option(
        0.0, "--price-sensitivity",
        help="0 ignores price; 0.25 weighs it heavily. Profiles ignore price by default."),
    as_json: bool = typer.Option(False, "--json", help="Machine-readable output."),
    require_fresh: bool = typer.Option(False, "--require-fresh", help="Fail on a stale snapshot."),
) -> None:
    """Rank models for a use case, entirely offline."""
    snapshot = _load_or_exit(require_fresh)
    sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[2]))
    from pipeline.ranking import rank as rank_fn

    profiles = snapshot.data["profiles"]["profiles"]
    if use_case not in profiles:
        featured = ", ".join(snapshot.data["profiles"].get("featured") or [])
        typer.echo(f"error: unknown use case {use_case!r}. Try one of: {featured}", err=True)
        raise typer.Exit(EXIT_ERROR)

    if fits:
        # A typo'd device id must not read as "nothing fits your GPU". That is a
        # different answer, and a caller would act on it.
        known = {n["id"] for n in snapshot.data["hardware"].get("nodes", [])
                 if n.get("label") == "Hardware"}
        if fits not in known:
            typer.echo(f"error: unknown device {fits!r}. Run `modelspec offline fit` "
                       "with no argument to list them.", err=True)
            raise typer.Exit(EXIT_ERROR)

    pool = _candidates(snapshot)
    if max_cost is not None:
        pool = [c for c in pool if c.cost_input is not None and c.cost_input <= max_cost]

    results = rank_fn(pool, use_case, limit=limit, open_weights_only=open_weights,
                      hardware_id=fits, cost_weight=price_sensitivity or None)

    if as_json:
        typer.echo(json.dumps(_envelope("rank", snapshot, results), indent=2, default=str))
    elif not results:
        typer.echo("No model matches those constraints.")
    else:
        for i, r in enumerate(results, 1):
            typer.echo(f"{i:>3}. {r['score']:>6.2f}  {r['display_name']}  ({r['provider']})")
        typer.echo(f"\nfrom a snapshot {snapshot.age_days:.0f} days old, "
                   f"build {snapshot.build_commit[:12]}")

    if not results:
        raise typer.Exit(EXIT_NO_MATCH)


@app.command("fit")
def fit_offline(
    hardware: str = typer.Argument(None, help="Hardware id. Omit to list the devices."),
    limit: int = typer.Option(20, "--limit", "-n"),
    as_json: bool = typer.Option(False, "--json"),
    require_fresh: bool = typer.Option(False, "--require-fresh"),
) -> None:
    """What can this machine actually run?"""
    snapshot = _load_or_exit(require_fresh)
    devices = [n for n in snapshot.data["hardware"].get("nodes", []) if n.get("label") == "Hardware"]

    if not hardware:
        rows = sorted(devices, key=lambda d: -(d.get("memory_bandwidth_gb_s") or 0))
        if as_json:
            typer.echo(json.dumps(_envelope("fit", snapshot, rows), indent=2, default=str))
        else:
            for d in rows:
                typer.echo(f"  {d['id']:<28} {d.get('memory_gb', '?'):>6} GB  "
                           f"{d.get('memory_bandwidth_gb_s', '?'):>6} GB/s  {d.get('display_name', '')}")
        return

    known = {d["id"] for d in devices}
    if hardware not in known:
        typer.echo(f"error: unknown device {hardware!r}. Run `modelspec offline fit` "
                   "with no argument to list them.", err=True)
        raise typer.Exit(EXIT_ERROR)

    pool = [c for c in _candidates(snapshot) if hardware in c.fits]
    pool.sort(key=lambda c: -c.fits[hardware])
    results = [{"model_id": c.model_id, "display_name": c.display_name,
                "predicted_decode_tps": c.fits[hardware],
                "prediction_basis": "computed, not measured"}
               for c in pool[:limit]]

    if as_json:
        typer.echo(json.dumps(_envelope("fit", snapshot, results), indent=2, default=str))
    elif not results:
        typer.echo(f"Nothing in the catalogue fits {hardware}.")
    else:
        for r in results:
            typer.echo(f"  ~{r['predicted_decode_tps']:>7.1f} tok/s  {r['display_name']}")
        typer.echo("\npredicted from memory bandwidth, not measured")

    if not results:
        raise typer.Exit(EXIT_NO_MATCH)
