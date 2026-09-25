"""``modelspec verify``: verification and decision-engine accuracy.

Reads the queue in ``verification/queue/events.jsonl``, re-reads each claim from
its retained source copy with the deterministic extractors, appends every
outcome to ``verification/log.jsonl`` and prints a summary. Pass
``--llm-reader claude`` (Claude Sonnet) or ``--llm-reader mistral`` (Mistral
Large on the local ollama host) to add a prose reader after the deterministic
readers. A reader is only asked about values collected by another model family.
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import typer

from decision import verify as v
from decision.sources import CopyStore

#: ``--llm-reader`` name -> the ``decision.verify`` factory that builds it.
READERS = {"claude": "claude_extractor", "mistral": "mistral_extractor"}

app = typer.Typer(
    help="Verify queued values or run decision-engine accuracy checks.",
    invoke_without_command=True,
    no_args_is_help=False,
)


@app.callback()
def verify(
    ctx: typer.Context,
    changed_only: bool = typer.Option(
        False, "--changed-only", help="Only values re-queued by source change detection."
    ),
    root: Path = typer.Option(v.REPO_ROOT, "--root", help="Repository root."),
    llm_reader: str | None = typer.Option(
        None, "--llm-reader", help="Independent prose reader: claude or mistral."
    ),
    as_json: bool = typer.Option(False, "--json", help="Machine-readable output."),
) -> None:
    """Verify queued facts and evidence against their sources (two keys)."""
    if ctx.invoked_subcommand is not None:
        return
    directory = root / "verification"
    extractors = v.deterministic_extractors()
    if llm_reader is not None:
        if llm_reader not in READERS:
            raise typer.BadParameter(
                f"supported readers: {', '.join(READERS)}", param_hint="--llm-reader"
            )
        extractors.append(getattr(v, READERS[llm_reader])())
    report = v.run(
        v.Queue(directory),
        v.VerificationLog(directory),
        v.StoredRegions(CopyStore(), v.load_sources(root / "registry" / "sources.yaml")),
        extractors,
        today=date.today(),
        changed_only=changed_only,
    )
    if as_json:
        typer.echo(json.dumps({"command": "verify", **report.to_dict()}, indent=2))
        return
    scope = "re-queued by change detection" if changed_only else "queued"
    typer.echo(f"Verified what was {scope}: {len(report.results)} value(s).")
    for outcome, n in report.counts.items():
        typer.echo(f"  {outcome}: {n}")
    for r in report.results:
        if r.outcome == "verified":
            continue
        detail = (
            "; ".join(f"{d.field}: expected {d.expected}, found {d.found}" for d in r.diffs)
            or r.reason
            or ""
        )
        typer.echo(f"  {r.outcome:<11} {v.ref_str(r.target)}  {detail}")
    for t in report.unknown:
        typer.echo(f"  no claim filed for re-queued {v.ref_str(t)}")


@app.command("accuracy")
def accuracy(
    profile: str = typer.Option("pr", "--profile", help="pr or nightly."),
    output_dir: Path = typer.Option(Path("accuracy-report"), "--output-dir"),
    root: Path = typer.Option(v.REPO_ROOT, "--root", help="Repository root."),
    config: Path | None = typer.Option(None, "--config", help="Accuracy config YAML."),
    snapshot_file: Path | None = typer.Option(None, "--snapshot-file"),
    report_date: str | None = typer.Option(None, "--date", help="Report date, YYYY-MM-DD."),
    llm_reader: str | None = typer.Option(None, "--llm-reader"),
    sample_size: int | None = typer.Option(None, "--sample-size"),
    seed: str | None = typer.Option(None, "--seed"),
) -> None:
    """Run the decision-engine accuracy harness and print its Markdown report."""
    from scripts import accuracy as harness

    if profile not in harness.PROFILES:
        raise typer.BadParameter("supported profiles: pr, nightly", param_hint="--profile")
    try:
        day = date.fromisoformat(report_date) if report_date else date.today()
    except ValueError as exc:
        raise typer.BadParameter("expected YYYY-MM-DD", param_hint="--date") from exc
    report = harness.run_profile(
        root=root,
        config_path=config or root / "accuracy.yaml",
        profile=profile,
        output_dir=output_dir,
        snapshot_file=snapshot_file,
        as_of=day,
        llm_reader=llm_reader,
        sample_size=sample_size,
        random_seed=seed,
    )
    markdown, payload = harness.write_report(report, output_dir)
    typer.echo(markdown.read_text(encoding="utf-8"), nl=False)
    typer.echo(f"JSON: {payload}")
    if report.status == "fail":
        raise typer.Exit(1)
