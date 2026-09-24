"""``modelspec snapshot build``: compile the decision snapshot (MODEL-138).

Collects cards, offerings, sources and the verification log, keeps only
verified values from registered, non-excluded sources, runs the premier-set
completeness gate, and writes a gzipped snapshot. Signed with
``MODELSPEC_SNAPSHOT_KEY`` when it is set. Exits 1 on any failure, naming the
model, facet and source for each gate gap.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Optional

import typer

from decision import snapshot as snap

EXIT_ERROR = 1
REPO_ROOT = Path(__file__).resolve().parents[2]


def build(
    out: Path = typer.Option(..., "--out", help="Where to write the snapshot (.json.gz)."),
    root: Path = typer.Option(REPO_ROOT, "--root", help="Repository root."),
    premier: Optional[Path] = typer.Option(  # noqa: UP045 - Typer reads the annotation
        None, "--premier", help="Premier list; default premier/slice-1.yaml under --root."),
    as_of: Optional[str] = typer.Option(  # noqa: UP045
        None, "--as-of", help="The snapshot's date, YYYY-MM-DD; default today."),
) -> None:
    """Build the decision snapshot. Fails when a premier model lacks a guaranteed fact."""
    premier = premier or root / "premier" / "slice-1.yaml"
    try:
        when = date.fromisoformat(as_of) if as_of else date.today()
        built = snap.build_from_repo(root, premier=premier, as_of=when,
                                     registry=snap.default_registry())
    except ValueError as exc:  # SnapshotError, CompletenessError, a bad --as-of
        typer.echo(f"error: {exc}", err=True)
        raise typer.Exit(EXIT_ERROR) from exc
    signed = snap.env_key() is not None
    built.write(out)
    lineup = len(built.content["lineup"]["candidates"])
    typer.echo(f"{built.snapshot_id} {built.content_hash}")
    typer.echo(f"{lineup} candidates in the lineup, "
               f"{len(built.content['archive']['candidates'])} in the archive; "
               f"{'signed' if signed else f'unsigned ({snap.KEY_ENV} not set)'}")
    typer.echo(f"written to {out}")
