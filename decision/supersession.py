"""Supersede a stale mismatch with a newer cite-only read (MODEL-415).

A cite-only fact gets no new verification rows, so a mismatch logged against a
region the fact no longer cites would quarantine it forever. A supersession
record, appended to ``verification/supersessions.jsonl`` in the private data
repository, retires that mismatch for admission only. The fact stays cited,
never verified, and the mismatch stays in its provenance.
See ``docs/design/cite-only-supersession.md``.
"""

from __future__ import annotations

import datetime
import hashlib
import json
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from typing import Any, Literal, Self

from pydantic import AwareDatetime, ValidationError, field_validator, model_validator

from decision.model import ContentRef, Record, Text, VerificationTarget
from decision.retention import is_cite_only, metadata_origins, require_source_url

class _Located(Record):
    source_id: Text
    url: Text
    region: Text

    @field_validator("url")
    @classmethod
    def _http(cls, value: str) -> str:
        return require_source_url(value)


class SupersededMismatch(_Located):
    """The logged mismatch: its log coordinates and the region it read."""

    date: datetime.date
    method: Text
    snapshot_ref: ContentRef | None = None


class CitedRead(_Located):
    """The newer transient read of the region the fact now cites."""

    retrieved_at: AwareDatetime
    snapshot_ref: ContentRef


class MismatchSupersession(Record):
    schema_version: Literal[1]
    target: VerificationTarget
    mismatch: SupersededMismatch
    read: CitedRead
    recorded_at: AwareDatetime
    recorded_by: Text
    reason: Text

    @model_validator(mode="after")
    def _ordered(self) -> Self:
        if self.target.kind != "fact":
            raise ValueError("only a fact's mismatch can be superseded")
        if self.recorded_at < self.read.retrieved_at:
            raise ValueError("a supersession cannot be recorded before its read")
        return self


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False).encode("utf-8")


def _sha256(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


class StoreError(ValueError):
    """A malformed supersession row. The message names fields and lines, never values."""

    #: ``schema.private_errors`` passes a value-free message through unredacted.
    _modelspec_redacted = True


@dataclass(frozen=True)
class Candidate:
    """One stored row for a target, as stored and as parsed."""

    raw: Mapping[str, Any]
    record: MismatchSupersession

    @property
    def hash(self) -> str:
        return _sha256(_canonical(self.raw))


def _fields(exc: ValidationError) -> str:
    """Where each schema error is, without the input value."""
    parts = []
    for error in exc.errors(include_input=False, include_context=False, include_url=False):
        where = ".".join(str(part) for part in error["loc"])
        # A whole-record check is one of this module's own value-free messages.
        parts.append(f"{where}: {error['type']}" if where else str(error["msg"]))
    return "; ".join(parts)


def parse(row: Any, where: str) -> Candidate:
    """One stored row, validated, or a ``StoreError`` naming ``where`` and why."""
    if isinstance(row, MismatchSupersession):
        row = row.model_dump(mode="json")
    if not isinstance(row, Mapping):
        raise StoreError(f"{where}: a supersession record must be a JSON object")
    raw = dict(row)
    target = raw.get("target")
    if (not isinstance(target, Mapping) or not isinstance(target.get("id"), str)
            or not target["id"].strip()):
        raise StoreError(f"{where}: a supersession record must name its target fact id")
    try:
        record = MismatchSupersession.model_validate(raw)
    except ValidationError as exc:
        raise StoreError(f"{where}: invalid supersession record ({_fields(exc)})") from None
    return Candidate(raw, record)


def index(rows: Iterable[Any]) -> dict[tuple[str, str], list[Candidate]]:
    """Every row validated, grouped by ``(fact id, value hash)``.

    A malformed row raises ``StoreError`` naming its row number, whether or not
    any fact needs it. A valid record for a fact that no longer exists is kept
    and stays inert.
    """
    grouped: dict[tuple[str, str], list[Candidate]] = {}
    for number, row in enumerate(rows, 1):
        candidate = parse(row, f"supersession row {number}")
        key = (candidate.record.target.id, candidate.record.target.value_hash)
        grouped.setdefault(key, []).append(candidate)
    for candidates in grouped.values():
        candidates.sort(key=lambda c: c.hash)
    return grouped


def _instant(value: Any) -> datetime.datetime | None:
    if value is None:
        return None
    parsed = value if isinstance(value, datetime.datetime) else \
        datetime.datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    return parsed if parsed.tzinfo is not None else None


def _refusal(record: MismatchSupersession, winner: Mapping[str, Any], value_hash: str,
             refs: Sequence[Mapping[str, Any]], sources: Mapping[str, str]) -> str | None:
    m, read = record.mismatch, record.read
    target = winner.get("target") or {}
    if (winner.get("outcome") != "mismatch" or str(winner.get("date")) != m.date.isoformat()
            or winner.get("method") != m.method
            or target.get("value_hash") != value_hash
            or target.get("id") != record.target.id):
        return "names another mismatch"
    if sources.get(m.source_id) != m.url:
        return "mismatch source unresolved"
    if sources.get(read.source_id) != read.url:
        return "read source unresolved"
    # Cite-only status comes from the registered URL alone, never a card's redirects.
    if not is_cite_only(read.url):
        return "read is not cite-only"
    cited = {(sources.get(str(ref.get("source_id"))), str(region))
             for ref in refs for region in ref.get("cited_regions") or ()}
    # A redirect alias is the same page: the mismatch region must not be cited
    # under the registered URL or any URL the citation was resolved through.
    try:
        aliases = {(origin, str(region)) for ref in refs
                   for origin in _origins(ref, sources)
                   for region in ref.get("cited_regions") or ()}
    except ValueError:
        return "citation redirect metadata invalid"
    if (m.url, m.region) in aliases:
        return "same region"
    if (read.url, read.region) not in cited:
        return "read region not cited"
    matching = [ref for ref in refs
                if sources.get(str(ref.get("source_id"))) == read.url
                and read.region in (ref.get("cited_regions") or ())
                and ref.get("snapshot_ref") == read.snapshot_ref]
    if not matching:
        return "read hash differs from citation"
    if not any(ref.get("retrieved_at") is None
               or _instant(ref.get("retrieved_at")) == read.retrieved_at for ref in matching):
        return "read time differs from citation"
    if read.retrieved_at.astimezone(datetime.UTC).date() <= m.date:
        return "read is not newer than mismatch"
    return None


def _origins(ref: Mapping[str, Any], sources: Mapping[str, str]) -> tuple[str, ...]:
    """The URLs that name the page a ref cites: registered, then each redirect hop."""
    resolved = ref.get("resolved_urls") or ()
    if isinstance(resolved, (list, tuple)):
        resolved = [str(url) for url in resolved]
    registered = sources.get(str(ref.get("source_id")))
    return tuple(url for url in (registered, *metadata_origins({"resolved_urls": resolved}))
                 if url)


def supersede(candidates: Sequence[Candidate], winner: Mapping[str, Any] | None,
              value_hash: str, refs: Sequence[Mapping[str, Any]],
              sources: Mapping[str, str]) -> tuple[dict[str, Any] | None, str | None]:
    """The provenance entry of the first record that supersedes ``winner``, or why none did.

    Returns ``(entry, None)`` when one applies, ``(None, reason)`` when records
    targeted the mismatch but each was refused, and ``(None, None)`` when there
    were none. The caller must only ask for a cited fact.
    """
    if winner is None or winner.get("outcome") != "mismatch" or not candidates:
        return None, None
    reasons = []
    for candidate in candidates:
        why = _refusal(candidate.record, winner, value_hash, refs, sources)
        if why is None:
            return provenance(winner, candidate), None
        reasons.append(why)
    return None, "; ".join(dict.fromkeys(reasons))


def provenance(winner: Mapping[str, Any], candidate: Candidate) -> dict[str, Any]:
    """The retained trace: the mismatch (its diff hashed, not copied) and the record."""
    mismatch = {key: winner[key] for key in
                ("target", "collector", "verifier", "method", "outcome", "date")
                if key in winner}
    mismatch["date"] = str(mismatch.get("date"))
    if winner.get("diff") is not None:
        mismatch["diff_sha256"] = _sha256(str(winner["diff"]).encode("utf-8"))
    return {
        "verification": mismatch,
        "supersession": json.loads(_canonical(candidate.raw)),
        "supersession_hash": candidate.hash,
    }


def _lines(text: str) -> list[str]:
    """Lines split on ``\\n`` only: U+2028 or U+0085 inside a JSON string is not a break."""
    lines = text.split("\n")
    return lines[:-1] if lines and lines[-1] == "" else lines


def read_store(path) -> list[dict[str, Any]]:
    """The stored records, one JSON object per non-blank line, each validated.

    A line that is not JSON, not an object, names no target or fails the schema
    raises with the file and line number.
    """
    from schema import private_errors

    rows = []
    for number, line in enumerate(_lines(path.read_text(encoding="utf-8")), 1):
        if line.strip():
            with private_errors(path, line=number):
                rows.append(dict(parse(json.loads(line), f"{path}: line {number}").raw))
    return rows


def append_only_violation(base: str, head: str) -> str | None:
    """The first line of ``base`` that ``head`` changed or dropped, or ``None``.

    The store is append-only: ``head`` keeps every line of ``base`` in place.
    """
    old, new = _lines(base), _lines(head)
    for number, line in enumerate(old, 1):
        if number > len(new):
            return f"line {number} was removed"
        if new[number - 1] != line:
            return f"line {number} was changed"
    return None
