"""``modelspec outcome``: opt-in, local outcome records (MODEL-211).

Off until a person runs ``modelspec outcome enable`` and agrees to the text it
prints. ``record`` writes one strict record to ``~/.modelspec/outcomes.jsonl``;
``show`` and ``export`` read it back; ``disable`` stops it. No command here
touches the network.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any, NoReturn, Optional

import typer
from pydantic import ValidationError

from . import outcome
from .vocabulary_cache import VocabularyInvalidError, VocabularyMissingError, load_cached_vocabulary

EXIT_ERROR = 1

app = typer.Typer(
    help="Opt-in, local records of whether a decision was adopted and the task succeeded.",
    no_args_is_help=True,
)


def _fail(command: str, code: str, message: str, as_json: bool) -> NoReturn:
    if as_json:
        typer.echo(json.dumps({"command": f"outcome {command}",
                               "error": {"code": code, "message": message}}, indent=2), err=True)
    else:
        typer.echo(f"error: {message}", err=True)
    raise typer.Exit(EXIT_ERROR)


def _validation_message(exc: ValidationError, field: str = "record") -> str:
    # The field and the reason, never the rejected value: it may be the very
    # text the schema exists to keep out.
    return "; ".join(
        f"{'.'.join(str(part) for part in error['loc']) or field}: {error['msg']}"
        for error in exc.errors(include_input=False)
    )


@app.command()
def enable(
    yes: bool = typer.Option(
        False, "--yes", help="Agree without a prompt, after reading the text."
    ),
) -> None:
    """Show exactly what is recorded, and turn recording on if you agree."""
    typer.echo(outcome.consent_text())
    if outcome.enabled():
        typer.echo("Outcome recording is already on.")
        return
    if not yes:
        if not sys.stdin.isatty():
            typer.echo("error: not a terminal; after reading the text above, "
                       "run `modelspec outcome enable --yes` to agree", err=True)
            raise typer.Exit(EXIT_ERROR)
        if not typer.confirm("Turn outcome recording on?", default=False):
            typer.echo("Outcome recording stays off. Nothing was written.")
            return
    try:
        outcome.enable()
    except OSError as exc:
        typer.echo(f"error: cannot write {outcome.consent_path()}: {exc.strerror or exc}",
                   err=True)
        raise typer.Exit(EXIT_ERROR) from None
    typer.echo(f"Outcome recording is on. Records go to {outcome.outcomes_path()}.")


@app.command()
def disable(
    delete: bool = typer.Option(False, "--delete", help="Also delete every record."),
) -> None:
    """Turn recording off. With --delete, also delete every record."""
    try:
        remaining = outcome.disable(delete=delete)
    except OSError as exc:
        typer.echo(f"error: recording is off, but a file could not be deleted: "
                   f"{exc.strerror or exc}", err=True)
        raise typer.Exit(EXIT_ERROR) from None
    typer.echo("Outcome recording is off. The decision stubs this CLI wrote were deleted.")
    if delete:
        typer.echo(f"Every record was deleted from {outcome.outcomes_path()}.")
    elif remaining:
        typer.echo(f"{remaining} record{'' if remaining == 1 else 's'} stay in "
                   f"{outcome.outcomes_path()}; `modelspec outcome disable --delete` "
                   "removes them.")


def _catalogue() -> tuple[set[str], set[str]] | None:
    try:
        vocabulary = load_cached_vocabulary()
    except (VocabularyMissingError, VocabularyInvalidError):
        return None
    models = vocabulary.get("models")
    providers = vocabulary.get("providers")
    return (set(models) if isinstance(models, dict) else set(),
            set(providers) if isinstance(providers, dict) else set())


def _stub_from_file(path: Path, decision_id: str, as_json: bool) -> outcome.DecisionStub:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(value, dict):
            raise ValueError("not a JSON object")
        stub = outcome.stub_from_decision(value)
    except OSError as exc:
        _fail("record", "unreadable", f"cannot read {path}: {exc.strerror or exc}", as_json)
    except ValidationError as exc:
        _fail("record", "invalid_decision",
              f"{path} is not a decision: {_validation_message(exc)}", as_json)
    except (ValueError, KeyError, TypeError, AttributeError) as exc:
        detail = f"missing {exc}" if isinstance(exc, KeyError) else "unexpected shape"
        _fail("record", "invalid_decision", f"{path} is not a decision: {detail}", as_json)
    if stub.decision_id != decision_id:
        _fail("record", "invalid_decision",
              f"{path} is a different decision from the one named", as_json)
    return stub


def _adopted(value: str, as_json: bool) -> tuple[str, str | None]:
    """Parse --adopted and check it against the cached vocabulary.

    The vocabulary is the only catalogue. A decision, a stub or a file never
    vouches for a model: ``decide --snapshot-file`` accepts a private snapshot,
    and a stub made from one could carry a private model's name past the check.
    """
    parts = value.split("/")
    if parts[0] == outcome.OTHER and len(parts) <= 2:
        model, provider = outcome.OTHER, (parts[1] if len(parts) == 2 else None)
    elif len(parts) in (2, 3):
        model, provider = "/".join(parts[:2]), (parts[2] if len(parts) == 3 else None)
    else:
        _fail("record", "invalid_adopted",
              "--adopted is lab/model, lab/model/provider, other or other/provider", as_json)
    catalogue = _catalogue()
    if model != outcome.OTHER and (catalogue is None or model not in catalogue[0]):
        hint = "" if catalogue is not None else " Run `modelspec snapshot fetch` first."
        _fail("record", "unknown_model",
              "--adopted names a model that is not in the ModelSpec catalogue; for a "
              f"model ModelSpec does not list, pass --adopted other.{hint}", as_json)
    if provider is not None and (catalogue is None or provider not in catalogue[1]):
        hint = "" if catalogue is not None else " Run `modelspec snapshot fetch` first."
        _fail("record", "unknown_provider",
              "--adopted names a provider that is not in the ModelSpec catalogue; "
              f"leave the provider off.{hint}", as_json)
    return model, provider


@app.command()
def record(
    decision_id: str = typer.Argument(..., help="The decision you acted on (dec_...)."),
    adopted: str = typer.Option(
        ..., "--adopted", metavar="MODEL[/PROVIDER]",
        help="The model you used, optionally with its provider; `other` if not catalogued.",
    ),
    result: str = typer.Option(..., "--result", help="success, partial or failure."),
    task_kind: Optional[str] = typer.Option(  # noqa: UP045 - Typer reads the annotation
        None, "--task-kind", metavar="KIND", help="One of the fixed task types, e.g. bug_fix.",
    ),
    latency_ms: Optional[int] = typer.Option(  # noqa: UP045 - Typer reads the annotation
        None, "--latency-ms", help="Whole milliseconds."
    ),
    cost_usd: Optional[float] = typer.Option(  # noqa: UP045 - Typer reads the annotation
        None, "--cost-usd", help="US dollars."
    ),
    decision_file: Optional[Path] = typer.Option(  # noqa: UP045 - Typer reads the annotation
        None, "--decision", metavar="FILE",
        help="The decision's JSON, when `decide` did not run here (e.g. the Worker's answer).",
    ),
    as_json: bool = typer.Option(False, "--json", help="Machine-readable output."),
) -> None:
    """Record whether a decision was adopted and how the task went. Off unless enabled."""
    if not outcome.enabled():
        # Nothing is read, validated or written while recording is off.
        if as_json:
            typer.echo(json.dumps({"command": "outcome record", "recorded": False,
                                   "reason": "disabled"}))
        typer.echo("not recorded: outcome recording is off "
                   "(`modelspec outcome enable` turns it on)", err=True)
        return
    try:
        outcome.check_decision_id(decision_id)
    except ValidationError as exc:
        _fail("record", "invalid_record", _validation_message(exc, "decision_id"), as_json)
    stub = (_stub_from_file(decision_file, decision_id, as_json)
            if decision_file is not None else outcome.load_stub(decision_id))
    model, provider = _adopted(adopted, as_json)
    try:
        entry = outcome.build_record(
            decision_id=decision_id, stub=stub, adopted_model=model,
            adopted_offering=provider, result=result, task_kind=task_kind,
            latency_ms=latency_ms, cost_usd=cost_usd,
        )
        outcome.append(entry)
    except ValidationError as exc:
        _fail("record", "invalid_record", _validation_message(exc), as_json)
    except OSError as exc:
        _fail("record", "unwritable",
              f"cannot write {outcome.outcomes_path()}: {exc.strerror or exc}", as_json)
    if as_json:
        typer.echo(json.dumps({"command": "outcome record", "recorded": True,
                               "record": entry.model_dump(mode="json")}))
        return
    known = "" if stub is not None else " (decision not cached: leader and band unknown)"
    typer.echo(f"recorded {entry.result} for {entry.decision_id}{known}")


def _row(entry: outcome.OutcomeRecord) -> str:
    def flag(value: bool | None) -> str:
        return "?" if value is None else ("yes" if value else "no")

    model = entry.adopted_model + (f"/{entry.adopted_offering}" if entry.adopted_offering else "")
    return (f"{entry.recorded_at}  {entry.decision_id}  {model}  {entry.result}  "
            f"leader:{flag(entry.was_leader)} best:{flag(entry.in_best_band)}"
            + (f"  {entry.task_kind}" if entry.task_kind else ""))


@app.command()
def show(
    limit: int = typer.Option(20, "--limit", "-n", help="The most recent N records."),
    as_json: bool = typer.Option(False, "--json", help="Machine-readable output."),
) -> None:
    """Say whether recording is on, where the records are, and list the latest."""
    records, refused = outcome.read()
    shown = records[-limit:] if limit > 0 else []
    if as_json:
        payload: dict[str, Any] = {
            "command": "outcome show", "enabled": outcome.enabled(),
            "path": str(outcome.outcomes_path()), "count": len(records),
            "refused_lines": refused,
            "records": [entry.model_dump(mode="json") for entry in shown],
        }
        typer.echo(json.dumps(payload, indent=2))
        return
    typer.echo(f"outcome recording: {'on' if outcome.enabled() else 'off'}")
    typer.echo(f"records: {len(records)} in {outcome.outcomes_path()}")
    if refused:
        typer.echo(f"warning: {refused} line{'' if refused == 1 else 's'} did not match "
                   "the record schema and were skipped", err=True)
    for entry in shown:
        typer.echo(_row(entry))


@app.command()
def export(
    out: Optional[Path] = typer.Option(  # noqa: UP045 - Typer reads the annotation
        None, "--out", help="Write JSON Lines here instead of stdout."
    ),
) -> None:
    """Print every record as JSON Lines, re-checked against the schema."""
    records, refused = outcome.read()
    text = "".join(entry.model_dump_json() + "\n" for entry in records)
    if refused:
        typer.echo(f"warning: {refused} line{'' if refused == 1 else 's'} did not match "
                   "the record schema and were left out", err=True)
    if out is None:
        typer.echo(text, nl=False)
        return
    try:
        descriptor = outcome.open_private(out, os.O_WRONLY | os.O_TRUNC)
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            handle.write(text)
    except OSError as exc:
        _fail("export", "unwritable", f"cannot write {out}: {exc.strerror or exc}", False)
    typer.echo(f"wrote {len(records)} record{'' if len(records) == 1 else 's'} to {out}",
               err=True)
