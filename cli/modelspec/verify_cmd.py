"""``modelspec verify``: two-key verification of what is queued (MODEL-140).

Reads the queue in ``verification/queue/events.jsonl``, re-reads each claim from
its retained source copy with the deterministic extractors, appends every
outcome to ``verification/log.jsonl`` and prints a summary. Pass
``--llm-reader claude`` to add the independent Claude Sonnet prose reader after
the deterministic readers.
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import typer

from decision import verify as v
from decision.sources import CopyStore


def verify(
    changed_only: bool = typer.Option(
        False, "--changed-only", help="Only values re-queued by source change detection."),
    root: Path = typer.Option(v.REPO_ROOT, "--root", help="Repository root."),
    llm_reader: str | None = typer.Option(
        None, "--llm-reader", help="Independent prose reader (supported: claude)."),
    as_json: bool = typer.Option(False, "--json", help="Machine-readable output."),
) -> None:
    """Verify queued facts and evidence against their sources (two keys)."""
    directory = root / "verification"
    extractors = v.deterministic_extractors()
    if llm_reader is not None:
        if llm_reader != "claude":
            raise typer.BadParameter("supported reader: claude", param_hint="--llm-reader")
        extractors.append(v.claude_extractor())
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
        detail = "; ".join(f"{d.field}: expected {d.expected}, found {d.found}"
                           for d in r.diffs) or r.reason or ""
        typer.echo(f"  {r.outcome:<11} {v.ref_str(r.target)}  {detail}")
    for t in report.unknown:
        typer.echo(f"  no claim filed for re-queued {v.ref_str(t)}")
