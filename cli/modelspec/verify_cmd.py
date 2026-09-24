"""``modelspec verify``: two-key verification of what is queued (MODEL-140).

Reads the queue in ``verification/queue/events.jsonl``, re-reads each claim from
its retained source copy with the deterministic extractors, appends every
outcome to ``verification/log.jsonl`` and prints a summary. Prose regions need an
LLM extractor, which this command does not configure: they are reported as
skipped and stay quarantined.
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
    as_json: bool = typer.Option(False, "--json", help="Machine-readable output."),
) -> None:
    """Verify queued facts and evidence against their sources (two keys)."""
    directory = root / "verification"
    report = v.run(
        v.Queue(directory),
        v.VerificationLog(directory),
        v.StoredRegions(CopyStore(), v.load_sources(root / "registry" / "sources.yaml")),
        v.deterministic_extractors(),
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
