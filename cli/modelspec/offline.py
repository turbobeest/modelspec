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
      5  a keyed origin refused the credential (MODEL-71)
      6  a keyed origin rate-limited the credential (MODEL-71)

  The pre-existing graph commands exit 0 when FalkorDB is unreachable, so a
  script cannot tell an answer from a failure. Nothing here does that.

  5 and 6 belong to `snapshot fetch` against an origin that keys its export.
  No unkeyed origin produces them, so no existing call can start seeing one:
  the free path against `https://modelspec.dev` still exits only 0 or 1.
"""

from __future__ import annotations

import json
import sys
from typing import Any, NoReturn

import click
import typer
from typer.core import TyperCommand, TyperGroup

from . import snapshot as snap

#: Bumped only for an incompatible change to the JSON envelope.
SCHEMA_VERSION = "1.0"

EXIT_OK = 0
EXIT_ERROR = 1
EXIT_NO_MATCH = 2
EXIT_NO_SNAPSHOT = 3
EXIT_STALE = 4
#: Only reachable from `snapshot fetch` against a keyed origin. A rejected key
#: and a spent quota are different problems — one is fixed by a new key, the
#: other by waiting — so a script must be able to tell them apart without
#: reading prose off stderr.
EXIT_KEY_REFUSED = 5
EXIT_RATE_LIMITED = 6


class ContractCommand(TyperCommand):
    """Make Click's syntax/option failures use the CLI's documented code 1."""

    def parse_args(self, ctx: click.Context, args: list[str]) -> list[str]:
        try:
            return super().parse_args(ctx, args)
        except Exception as exc:  # noqa: BLE001 - Typer wraps Click usage errors
            if getattr(exc, "exit_code", None) == 2:
                exc.exit_code = EXIT_ERROR
            raise


class ContractGroup(TyperGroup):
    """Apply the same usage-error exit code while resolving subcommands."""

    def parse_args(self, ctx: click.Context, args: list[str]) -> list[str]:
        try:
            return super().parse_args(ctx, args)
        except Exception as exc:  # noqa: BLE001 - Typer wraps Click usage errors
            if getattr(exc, "exit_code", None) == 2:
                exc.exit_code = EXIT_ERROR
            raise

    def resolve_command(self, ctx: click.Context, args: list[str]) -> Any:
        try:
            return super().resolve_command(ctx, args)
        except Exception as exc:  # noqa: BLE001 - Typer wraps Click usage errors
            if getattr(exc, "exit_code", None) == 2:
                exc.exit_code = EXIT_ERROR
            raise


app = typer.Typer(
    cls=ContractGroup,
    help="Answer from the local snapshot. No database, no network, no credential.",
)
snapshot_app = typer.Typer(cls=ContractGroup, help="Manage the local snapshot.")
app.add_typer(snapshot_app, name="snapshot")


def _emit(payload: dict[str, Any], as_json: bool) -> None:
    if as_json:
        typer.echo(json.dumps(payload, indent=2, default=str))


def _envelope(command: str, snapshot: snap.Snapshot, result: Any,
              **metadata: Any) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "command": command,
        "freshness": snapshot.freshness(),
        "result": result,
        **metadata,
    }


def _emit_error(command: str, message: str, as_json: bool) -> None:
    if as_json:
        typer.echo(json.dumps({
            "schema_version": SCHEMA_VERSION,
            "command": command,
            "error": {"message": message},
        }, indent=2), err=True)
    else:
        typer.echo(f"error: {message}", err=True)


def _load_or_exit(require_fresh: bool, *, command: str, as_json: bool = False) -> snap.Snapshot:
    try:
        snapshot = snap.load()
    except snap.SnapshotMissing as exc:
        _emit_error(command, str(exc), as_json)
        raise typer.Exit(EXIT_NO_SNAPSHOT) from exc
    except snap.SnapshotInvalid as exc:
        _emit_error(command, str(exc), as_json)
        raise typer.Exit(EXIT_ERROR) from exc
    if require_fresh and snapshot.is_stale:
        _emit_error(
            command,
            f"snapshot is {snapshot.age_days:.0f} days old and --require-fresh was given. "
            "Run `modelspec snapshot fetch`.",
            as_json,
        )
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
            verified_benchmarks=set(c.get("verified_benchmarks") or []),
            rehost_of=c.get("rehost_of"), release_date=c.get("release_date"),
        )
        for c in snapshot.data["candidates"]["candidates"]
    ]


def _not_ranked_yet(block: dict[str, Any]) -> str | None:
    """One line under the rank table naming what the ranking could not order (MODEL-110)."""
    count = block["count"]
    if not count:
        return None
    named = [m["model_id"] for m in block["models"]]
    rest = count - len(named)
    head = (f"{count} model is not ranked yet" if count == 1
            else f"{count} models are not ranked yet")
    tail = f", and {rest} more." if rest else "."
    return (f"{head} (not enough benchmark evidence), newest first: "
            f"{', '.join(named)}{tail}")


@snapshot_app.command("fetch", cls=ContractCommand)
def snapshot_fetch(
    origin: str = typer.Option(snap.DEFAULT_ORIGIN, help="Where to fetch from."),
    api_key: str = typer.Option(
        None, "--api-key",
        help=f"Credential for an origin that keys its export. Prefer the "
             f"{snap.API_KEY_ENV} environment variable: a key in argv is visible "
             f"in shell history and in `ps`."),
) -> None:
    """Download the published export. The only command that needs the network.

    Unkeyed by default. With a credential — `MODELSPEC_API_KEY`, or `--api-key`
    — the same command fetches from an origin that keys its export, and the
    snapshot it writes is current rather than 90 days delayed. Nothing about
    the snapshot, the envelope or any other command changes; only `fetched_at`.
    """
    credential = snap.resolve_credential(api_key)

    def fail(message: str, code: int) -> NoReturn:
        # The backstop, not the plan: no message built above interpolates a key.
        typer.echo(f"error: {credential.redact(message) if credential else message}",
                   err=True)
        raise typer.Exit(code)

    if credential is not None and credential.source == "flag":
        typer.echo(
            f"warning: --api-key is visible in shell history and in process "
            f"listings. Prefer {snap.API_KEY_ENV} in the environment.", err=True)
    try:
        result = snap.fetch(origin, credential=credential)
    except snap.KeyRequiredError as exc:
        fail(str(exc), EXIT_KEY_REFUSED)
    except snap.KeyRejectedError as exc:
        fail(str(exc), EXIT_KEY_REFUSED)
    except snap.RateLimitedError as exc:
        fail(str(exc), EXIT_RATE_LIMITED)
    except Exception as exc:  # noqa: BLE001 - surfaced to the user, not swallowed
        # Unchanged for every failure that is not a credential one, including an
        # unreachable origin: same sentence, same exit code as before MODEL-71.
        fail(f"could not fetch the snapshot: {exc}", EXIT_ERROR)
    typer.echo(f"fetched {len(result.data['candidates']['candidates'])} models "
               f"from {origin} (build {result.build_commit[:12]})")
    typer.echo(f"cached at {result.path}")


@snapshot_app.command("status", cls=ContractCommand)
def snapshot_status(as_json: bool = typer.Option(False, "--json")) -> None:
    """Show what snapshot is cached and how old it is."""
    try:
        info = snap.status()
    except snap.SnapshotInvalid as exc:
        _emit_error("status", str(exc), as_json)
        raise typer.Exit(EXIT_ERROR) from exc
    if as_json:
        freshness_keys = ("fetched_at", "age_days", "stale", "stale_after_days",
                          "origin", "build_commit", "built_at")
        freshness = {key: info[key] for key in freshness_keys if key in info} or None
        result = {key: value for key, value in info.items() if key not in freshness_keys}
        typer.echo(json.dumps({
            "schema_version": SCHEMA_VERSION,
            "command": "status",
            "freshness": freshness,
            "result": result,
        }, indent=2))
    elif not info["present"]:
        typer.echo(info["message"])
    else:
        typer.echo(f"snapshot   {info['path']}")
        typer.echo(f"fetched    {info['fetched_at']} ({info['age_days']:.1f} days ago)")
        typer.echo(f"build      {info['build_commit'][:12]} from {info['origin']}")
        typer.echo(f"stale      {info['stale']}")
    if not info["present"]:
        raise typer.Exit(EXIT_NO_SNAPSHOT)


@app.command("rank", cls=ContractCommand)
def rank_offline(
    use_case: str = typer.Argument(..., help="Use-case profile, e.g. coding."),
    limit: int = typer.Option(10, "--limit", "-n"),
    open_weights: bool = typer.Option(
        False, "--open-weights", help="Only models you can download."
    ),
    fits: str = typer.Option(None, "--fits", help="Hardware id the model must fit on."),
    max_cost: float = typer.Option(None, "--max-cost", help="Maximum $ per million input tokens."),
    price_sensitivity: float = typer.Option(
        0.0, "--price-sensitivity",
        help="0 ignores price; 0.25 weighs it heavily. Profiles ignore price by default."),
    as_json: bool = typer.Option(False, "--json", help="Machine-readable output."),
    require_fresh: bool = typer.Option(False, "--require-fresh", help="Fail on a stale snapshot."),
    include_rehosts: bool = typer.Option(
        False, "--include-rehosts", help="Keep repackaged copies of another model's weights."),
) -> None:
    """Rank models for a use case, entirely offline."""
    if limit < 0:
        _emit_error("rank", "--limit must be nonnegative", as_json)
        raise typer.Exit(EXIT_ERROR)
    if not 0.0 <= price_sensitivity <= 1.0:
        _emit_error("rank", "--price-sensitivity must be between 0 and 1", as_json)
        raise typer.Exit(EXIT_ERROR)
    snapshot = _load_or_exit(require_fresh, command="rank", as_json=as_json)
    sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[2]))
    from pipeline.ranking import rank_report

    profiles = snapshot.data["profiles"]["profiles"]
    if use_case not in profiles:
        featured = ", ".join(snapshot.data["profiles"].get("featured") or [])
        _emit_error("rank", f"unknown use case {use_case!r}. Try one of: {featured}", as_json)
        raise typer.Exit(EXIT_ERROR)

    if fits:
        # A typo'd device id must not read as "nothing fits your GPU". That is a
        # different answer, and a caller would act on it.
        known = {n["id"] for n in snapshot.data["hardware"].get("nodes", [])
                 if n.get("label") == "Hardware"}
        if fits not in known:
            _emit_error("rank", f"unknown device {fits!r}. Run `modelspec offline fit` "
                        "with no argument to list them.", as_json)
            raise typer.Exit(EXIT_ERROR)

    try:
        pool = _candidates(snapshot)
        if max_cost is not None:
            pool = [c for c in pool if c.cost_input is not None and c.cost_input <= max_cost]

        report = rank_report(pool, use_case, limit=limit, open_weights_only=open_weights,
                             hardware_id=fits, cost_weight=price_sensitivity or None,
                             include_rehosts=include_rehosts)
    except Exception as exc:  # noqa: BLE001 - CLI must not leak a traceback to callers
        _emit_error("rank", f"could not rank the snapshot: {exc}", as_json)
        raise typer.Exit(EXIT_ERROR) from exc
    results = report["ranked"]
    ranking_status = report["ranking_status"]
    ranked_count = report["ranked_count"]
    unranked_count = report["unranked_count"]

    if as_json:
        typer.echo(json.dumps(_envelope(
            "rank", snapshot, results,
            ranking_status=ranking_status,
            ranked_count=ranked_count,
            unranked_count=unranked_count,
            # MODEL-110. A new envelope field, always present; additive under 1.0.
            unranked_candidates=report["unranked_candidates"],
        ), indent=2, default=str))
    else:
        typer.echo(f"{use_case}: {ranking_status} ordering; "
                   f"{ranked_count} ranked, {unranked_count} unranked.")
        for i, r in enumerate(results, 1):
            typer.echo(f"{i:>3}. {r['score']:>6.2f}  {r['display_name']}  ({r['provider']})")
        if ranking_status == "empty":
            typer.echo("No model matches those constraints.")
        elif ranking_status == "unavailable":
            typer.echo("No model has enough evidence to be ranked.")
        withheld = _not_ranked_yet(report["unranked_candidates"])
        if withheld:
            typer.echo(f"\n{withheld}")
        typer.echo(f"\nfrom a snapshot {snapshot.age_days:.0f} days old, "
                   f"build {snapshot.build_commit[:12]}")

    if ranking_status in {"empty", "unavailable"}:
        raise typer.Exit(EXIT_NO_MATCH)


@app.command("class-fit", cls=ContractCommand)
def class_fit_offline(
    task: str = typer.Argument(
        None, help="What the system has to do, in prose. Matched against the "
                   "published terms and discarded; never sent anywhere."),
    emits: str = typer.Option(
        None, "--emits", help="What the model must produce, e.g. choice, open_text."),
    consumes: str = typer.Option(
        None, "--consumes", help="Comma-separated input kinds, e.g. structured_state,text."),
    decides: str = typer.Option(
        None, "--decides", help="The decision it must make. Strict: no adaptation."),
    as_json: bool = typer.Option(False, "--json", help="Machine-readable output."),
    require_fresh: bool = typer.Option(False, "--require-fresh"),
) -> None:
    """Which *class* of model a task needs, before ranking within one.

    Ranking answers "which model?" once you have decided you want an LLM. This
    answers the question before that one, and it refuses rather than guessing:
    when two classes both survive, it says so and hands back the question you
    have to settle, because ModelSpec holds no measurement that orders one
    class against another.
    """
    snapshot = _load_or_exit(require_fresh, command="class-fit", as_json=as_json)
    sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[2]))
    from api.class_fit import CatalogueEvidence, class_fit
    from pipeline.class_export import counts_from_snapshot_candidates

    counts, examples = counts_from_snapshot_candidates(
        snapshot.data["candidates"]["candidates"])
    answer = class_fit(
        task=task,
        emits=emits,
        consumes=[c.strip() for c in consumes.split(",") if c.strip()] if consumes else None,
        decides=decides,
        evidence=CatalogueEvidence(card_counts=counts, examples=examples),
    )

    if as_json:
        typer.echo(json.dumps(_envelope("class-fit", snapshot, answer,
                                        fit_status=answer["fit_status"]),
                              indent=2, default=str))
    else:
        status = answer["fit_status"]
        if status == "refused":
            typer.echo(f"refused: {answer['refusal']['code']} — "
                       f"{answer['refusal']['message']}")
        else:
            typer.echo(f"{status}: {len(answer['candidates'])} candidate class(es). "
                       "No score orders them.")
        for row in answer["candidates"]:
            catalogue = row["catalogue"]
            count = catalogue.get("card_count")
            held = "evidence not supplied" if count is None else f"{count} card(s)"
            typer.echo(f"\n  {row['class']}  — consumes {', '.join(row['consumes'])}; "
                       f"emits {row['emits']}; decides {row['decides']}  [{held}]")
            typer.echo(f"      {row['because']}")
            if row["emits_adapted"]:
                typer.echo(f"      only via an adaptation: {row['emits_adapted']['how']}")
            typer.echo(f"      next: {row['next']}")
        for question in answer["distinguishing_questions"]:
            typer.echo(f"\n  you must settle: {question['ask']}")
        for chain in answer["composition"]:
            typer.echo(f"\n  they compose: {' then '.join(chain['sequence'])} "
                       f"(evidence: {chain['evidence']} — {chain['see']})")
        if status == "unavailable":
            typer.echo("\nNo class in the published taxonomy produces that. "
                       "See the `emits` vocabulary in /api/rank/class-fit.json.")
        typer.echo(f"\nfrom a snapshot {snapshot.age_days:.0f} days old, "
                   f"build {snapshot.build_commit[:12]}")

    if answer["fit_status"] == "refused":
        raise typer.Exit(EXIT_ERROR)
    if answer["fit_status"] == "unavailable":
        raise typer.Exit(EXIT_NO_MATCH)


@app.command("fit", cls=ContractCommand)
def fit_offline(
    hardware: str = typer.Argument(None, help="Hardware id. Omit to list the devices."),
    limit: int = typer.Option(20, "--limit", "-n"),
    as_json: bool = typer.Option(False, "--json"),
    require_fresh: bool = typer.Option(False, "--require-fresh"),
    include_rehosts: bool = typer.Option(
        False, "--include-rehosts", help="Keep repackaged copies of another model's weights."),
    host: str = typer.Option(
        None, "--host", help="Host profile id (hosts.json). Adds fit_state to every row."),
    host_ram: float = typer.Option(
        None, "--host-ram",
        help="GB of RAM on this machine, before the fixed 8 GB OS reserve. Needs --host."),
    include_offload: bool = typer.Option(
        False, "--include-offload",
        help="Append a separate offload tier: models that fit only by spilling to host RAM. "
             "Needs --host."),
) -> None:
    """What can this machine actually run?"""
    if limit < 0:
        _emit_error("fit", "--limit must be nonnegative", as_json)
        raise typer.Exit(EXIT_ERROR)
    if include_offload and not host:
        _emit_error("fit", "--include-offload requires --host", as_json)
        raise typer.Exit(EXIT_ERROR)
    if host_ram is not None and not host:
        _emit_error("fit", "--host-ram requires --host", as_json)
        raise typer.Exit(EXIT_ERROR)
    if host_ram is not None and host_ram <= 0:
        _emit_error("fit", "--host-ram must be positive", as_json)
        raise typer.Exit(EXIT_ERROR)
    snapshot = _load_or_exit(require_fresh, command="fit", as_json=as_json)
    devices = [
        n for n in snapshot.data["hardware"].get("nodes", []) if n.get("label") == "Hardware"
    ]

    if not hardware:
        rows = sorted(devices, key=lambda d: -(d.get("memory_bandwidth_gb_s") or 0))
        if as_json:
            typer.echo(json.dumps(_envelope("fit", snapshot, rows), indent=2, default=str))
        else:
            for d in rows:
                typer.echo(
                    f"  {d['id']:<28} {d.get('memory_gb', '?'):>6} GB  "
                    f"{d.get('memory_bandwidth_gb_s', '?'):>6} GB/s  {d.get('display_name', '')}"
                )
        return

    known = {d["id"] for d in devices}
    if hardware not in known:
        _emit_error("fit", f"unknown device {hardware!r}. Run `modelspec offline fit` "
                    "with no argument to list them.", as_json)
        raise typer.Exit(EXIT_ERROR)

    host_profile = None
    if host:
        sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[2]))
        from pipeline import hosts as host_layer

        profiles = {h.get("id"): h for h in (snapshot.data.get("hosts") or {}).get("hosts") or []}
        if not profiles:
            _emit_error("fit", "this snapshot has no host profiles (an export older than "
                        "MODEL-26 phase B). Run `modelspec snapshot fetch`.", as_json)
            raise typer.Exit(EXIT_ERROR)
        if host not in profiles:
            _emit_error("fit", f"unknown host {host!r}. Known hosts: "
                        f"{', '.join(sorted(profiles))}", as_json)
            raise typer.Exit(EXIT_ERROR)
        try:
            host_profile = host_layer.host_from_raw(profiles[host])
        except Exception as exc:  # noqa: BLE001 - CLI must not leak a traceback to callers
            _emit_error("fit", f"host profile {host!r} is unreadable: {exc}", as_json)
            raise typer.Exit(EXIT_ERROR) from exc

    try:
        pool = [c for c in _candidates(snapshot) if hardware in c.fits
                and (include_rehosts or not c.rehost_of)]
    except Exception as exc:  # noqa: BLE001 - CLI must not leak a traceback to callers
        _emit_error("fit", f"could not read the snapshot: {exc}", as_json)
        raise typer.Exit(EXIT_ERROR) from exc
    # A non-token model (or, rarely, a token model missing KV geometry) fits
    # in memory but has no decode-speed prediction. It must not crash the
    # sort (None has no ordering against a float) and must not lead the list
    # by an absent rate: real rates first, fastest first; null-decode rows
    # follow, alphabetically (MODEL-53).
    pool.sort(key=lambda c: (
        c.fits[hardware] is None,
        -c.fits[hardware] if c.fits[hardware] is not None else 0.0,
        c.display_name.lower(),
    ))
    results = [{"model_id": c.model_id, "display_name": c.display_name,
                "predicted_decode_tps": c.fits[hardware],
                "prediction_basis": "computed, not measured"}
               for c in pool[:limit]]

    # Without --host nothing below runs, so the output is byte-identical to the
    # pre-host CLI (MODEL-26 decision 1).
    offload: list[dict[str, Any]] = []
    if host_profile is not None:
        for r in results:
            r.update({
                "fit_state": "accelerator", "offload_fraction": 0.0, "host_id": host,
                "predicted_decode_tps_basis": (
                    "accelerator-roofline" if r["predicted_decode_tps"] is not None else None),
            })
        if include_offload and not host_profile.unified:
            offload = _offload_tier(snapshot, hardware, host_profile, host_ram,
                                    include_rehosts, limit)

    if as_json:
        typer.echo(json.dumps(_envelope("fit", snapshot, results + offload),
                              indent=2, default=str))
    elif not results and not offload:
        typer.echo(f"Nothing in the catalogue fits {hardware}.")
    else:
        for r in results:
            tps = r["predicted_decode_tps"]
            rate = f"~{tps:>7.1f}" if tps is not None else f"{'n/a':>8}"
            typer.echo(f"  {rate} tok/s  {r['display_name']}")
        if offload:
            typer.echo(f"\noffload tier on {host} (spills to host RAM; "
                       "not ranked with the rows above):")
            for r in offload:
                tps = r["predicted_decode_tps"]
                rate = f"~{tps:>7.1f}" if tps is not None else f"{'n/a':>8}"
                typer.echo(f"  {rate} tok/s  {r['display_name']}  "
                           f"({r['offload_fraction']:.0%} offloaded, {r['quantization']})")
        typer.echo("\npredicted from memory bandwidth, not measured; "
                   "n/a means the weights fit but the model does not decode tokens")

    if not results and not offload:
        raise typer.Exit(EXIT_NO_MATCH)


def _offload_tier(snapshot: snap.Snapshot, hardware: str, host: Any,
                  host_ram: float | None, include_rehosts: bool,
                  limit: int) -> list[dict[str, Any]]:
    """Models that fit `hardware` only by spilling to `host` RAM, fastest first.

    A separate tier, never interleaved with accelerator rows (decision 2).
    """
    from pipeline import hosts as host_layer

    device = next(n for n in snapshot.data["hardware"]["nodes"]
                  if n.get("label") == "Hardware" and n.get("id") == hardware)
    capacity = device.get("memory_gb")
    bandwidth = device.get("memory_bandwidth_gb_s")
    raw = snapshot.data["candidates"]["candidates"]
    # A device that answers no single-device fit at all (single_device_fit:
    # false) must not grow an offload tier either.
    if not capacity or not bandwidth or not any(hardware in (c.get("fits") or {}) for c in raw):
        return []
    rows = []
    for c in raw:
        if not c.get("open_weights") or hardware in (c.get("fits") or {}):
            continue
        if c.get("rehost_of") and not include_rehosts:
            continue
        if not c.get("total_parameters"):
            continue
        a = host_layer.assess(
            total_params=float(c["total_parameters"]),
            active_params=float(c["active_parameters"]) if c.get("active_parameters") else None,
            model_type=c.get("model_type"), accelerator_gb=float(capacity),
            accelerator_bandwidth=float(bandwidth), host=host, host_ram_gb=host_ram)
        if a["fit_state"] != host_layer.FIT_OFFLOAD:
            continue
        rows.append({"model_id": c["model_id"], "display_name": c["display_name"],
                     "predicted_decode_tps": a["predicted_decode_tps"],
                     "prediction_basis": "computed, not measured",
                     "fit_state": a["fit_state"], "offload_fraction": a["offload_fraction"],
                     "host_id": host.id,
                     "predicted_decode_tps_basis": a["predicted_decode_tps_basis"],
                     "quantization": a["quantization"]})
    rows.sort(key=lambda r: (r["predicted_decode_tps"] is None,
                             -(r["predicted_decode_tps"] or 0.0), r["display_name"].lower()))
    return rows[:limit]
