"""A cite-only page may change a value when two readers of different families agree.

Jamie, 2026-11-22 (MODEL-531). The rule, as it is built here:

1. Two readers from different model families each read the page in memory, blind to
   each other and to the filed value, and return the same normalised value. A
   disagreement leaves the fact as filed and flags it.
2. The page is first-party for the facet: the lab's or provider's own page, of a
   kind the facet's ``permitted_source_kinds`` allows.
3. The fact is served as cited, never verified. The record keeps the URL, read date,
   sha256 and both readers' normalised answers with their reader ids, families and
   versions. It keeps no page text and no excerpt, and no ``Verification`` is logged.
4. The rolling re-read re-reads such a fact. When the page's sha256 changes, two
   readers read it again (``reread``).
5. A retaining source wins. When any source registered for the subject and facet sits
   on a host that retains copies, that path is used instead and this one refuses.

``cited_change`` is the only gate. It checks every condition in code and either
returns the whole record or refuses with one named reason. It never writes a partial
change. Nothing here reads a page or calls a model: the readers' answers come in as
data.
"""

from __future__ import annotations

import json
import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from datetime import UTC, date, datetime, time
from typing import Any, Literal

from pydantic import JsonValue

from decision.model import DETERMINISTIC, model_family
from decision.retention import cite_only_origin_status, cite_only_status

RULE = "two-readers-cited-change@1"
DECIDED_BY = "Jamie 2026-11-22 (MODEL-531)"
#: Source kinds that are a lab's or provider's own page. A facet's
#: ``permitted_source_kinds`` must also list the kind.
FIRST_PARTY_KINDS = frozenset({
    "lab_documentation", "lab_announcement", "provider_documentation", "provider_terms",
    "provider_trust_center",
})
#: A string answer longer than this reads as an excerpt, not a normalised value.
MAX_STRING_LENGTH = 120
SHA256 = re.compile(r"[0-9a-f]{64}")

#: Every named refusal reason.
REFUSALS = (
    "unknown_facet",
    "host_not_cite_only",
    "host_unreadable",
    "source_kind_not_permitted",
    "not_first_party",
    "reader_count",
    "reader_metadata_missing",
    "reader_not_blind",
    "reader_families_not_distinct",
    "readers_disagree",
    "no_value",
    "value_invalid",
    "value_unchanged",
    "retaining_source_registered",
    "retaining_source_unreadable",
    "bad_sha256",
    "bad_read_date",
)


@dataclass(frozen=True)
class ReaderAnswer:
    """One reader's normalised answer. ``blind`` attests it read the page without the
    filed value and without the other reader's answer."""

    reader_id: str
    family: str
    version: str
    value: JsonValue
    blind: bool = False

    def metadata_present(self) -> bool:
        return all(isinstance(part, str) and part.strip()
                   for part in (self.reader_id, self.family, self.version))


@dataclass(frozen=True)
class CitedSource:
    """The page that was read: where, what kind, when and the sha256 of the bytes read."""

    source_id: str
    url: str
    kind: str
    read_date: date
    sha256: str
    publisher: str | None = None
    resolved_urls: tuple[str, ...] = ()
    cited_regions: tuple[str, ...] = ("page",)
    #: The instant of the read (timezone-aware), when known; the record keeps it as ``retrieved_at``.
    read_at: datetime | None = None


@dataclass(frozen=True)
class RegisteredSource:
    """A source registered for the subject and facet (the cited one included)."""

    source_id: str
    url: str


@dataclass(frozen=True)
class CitedChange:
    """``cited_change`` when the whole rule held; ``refused`` with a named reason otherwise."""

    outcome: Literal["cited_change", "refused"]
    reason: str | None = None
    detail: str = ""
    record: dict[str, JsonValue] | None = None

    @property
    def changed(self) -> bool:
        return self.outcome == "cited_change"


def _refuse(reason: str, detail: str = "") -> CitedChange:
    assert reason in REFUSALS, reason
    return CitedChange("refused", reason, detail, None)


def _canonical(value: JsonValue, facet: Any) -> str:
    """A value in one spelling: a set facet's members are sorted."""
    if isinstance(value, list) and getattr(facet.value_type, "kind", None) in {"set", "string_set"}:
        value = sorted(value, key=lambda item: json.dumps(item, sort_keys=True))
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def _facet(facet_id: str):
    from decision.registry import default

    try:
        return default().facet(facet_id)
    except KeyError:
        return None


def _value_fits(value: JsonValue, facet: Any) -> str | None:
    """Why ``value`` is not a value of the facet, or ``None``."""
    from decision import registry
    from decision.model import _check_value

    if isinstance(value, str) and len(value) > MAX_STRING_LENGTH:
        return "a string answer that long is an excerpt, not a normalised value"
    if isinstance(value, list) and any(isinstance(m, str) and len(m) > MAX_STRING_LENGTH
                                       for m in value):
        return "a set member that long is an excerpt, not a normalised value"
    try:
        _check_value(value, facet, registry)
    except ValueError as error:
        return str(error)
    return None


def _check_source(source: CitedSource, facet: Any, owners: Sequence[str]) -> CitedChange | None:
    if not isinstance(source.sha256, str) or not SHA256.fullmatch(source.sha256):
        return _refuse("bad_sha256", "the sha256 of the bytes read is missing or malformed")
    if not isinstance(source.read_date, date) or source.read_date > datetime.now(UTC).date():
        return _refuse("bad_read_date", "the read date is missing or in the future")
    status = cite_only_origin_status(source.url, source.resolved_urls)
    if status is None:
        return _refuse("host_unreadable", "the source URL or a redirect target does not parse")
    if not status or not all(cite_only_status(u) for u in (source.url, *source.resolved_urls)):
        return _refuse("host_not_cite_only",
                       "the host retains copies, so the verified path applies")
    if source.kind not in facet.permitted_source_kinds:
        return _refuse("source_kind_not_permitted",
                       f"{source.kind} is not a permitted source kind for {facet.id}")
    if source.kind not in FIRST_PARTY_KINDS:
        return _refuse("not_first_party", f"{source.kind} is not a lab's or provider's own page")
    if source.publisher is not None and owners and source.publisher not in owners:
        return _refuse("not_first_party", "the page's publisher is not the subject's lab or provider")
    return None


def _check_readers(answers: Sequence[ReaderAnswer], facet: Any) -> CitedChange | None:
    if len(answers) != 2:
        return _refuse("reader_count", f"{len(answers)} readers; the rule needs exactly two")
    if not all(isinstance(a, ReaderAnswer) and a.metadata_present() for a in answers):
        return _refuse("reader_metadata_missing", "a reader id, family or version is missing")
    if not all(a.blind is True for a in answers):
        return _refuse("reader_not_blind", "a reader was not blind to the filed value or the other reader")
    families = [model_family(a.family) for a in answers]
    if DETERMINISTIC in (a.family for a in answers) or "unknown" in families \
            or families[0] == families[1] or answers[0].reader_id == answers[1].reader_id:
        return _refuse("reader_families_not_distinct",
                       "the readers are not two distinct, known model families")
    if _canonical(answers[0].value, facet) != _canonical(answers[1].value, facet):
        return _refuse("readers_disagree", "the readers returned different values")
    return None


def _check_retaining(registered: Sequence[RegisteredSource]) -> CitedChange | None:
    for source in registered:
        status = cite_only_status(source.url)
        if status is None:
            return _refuse("retaining_source_unreadable",
                           f"registered source {source.source_id} has a URL that does not parse")
        if not status:
            return _refuse("retaining_source_registered",
                           f"registered source {source.source_id} is on a host that retains copies")
    return None


def _retrieved_at(source: CitedSource) -> str:
    """An aware timestamp: the instant of the read, or midnight UTC of the read date."""
    if source.read_at is not None and source.read_at.tzinfo is not None:
        return source.read_at.isoformat()
    return datetime.combine(source.read_date, time(), tzinfo=UTC).isoformat()


def _record(subject: str, facet_id: str, value: JsonValue, source: CitedSource,
            answers: Sequence[ReaderAnswer], previous: JsonValue) -> dict[str, JsonValue]:
    """The record: values, URL, date, sha256 and the readers. No page text."""
    return {
        "subject": subject,
        "facet": facet_id,
        "value": value,
        "state": "known",
        "resolution": "cited",
        "source": {
            "source_id": source.source_id,
            "url": source.url,
            "snapshot_ref": f"sha256:{source.sha256}",
            "retrieved_at": _retrieved_at(source),
            "cited_regions": list(source.cited_regions),
        },
        "cited_change": {
            "rule": RULE,
            "decided_by": DECIDED_BY,
            "read_date": source.read_date.isoformat(),
            "sha256": source.sha256,
            "url": source.url,
            "previous_value": previous,
            "readers": [{"reader_id": a.reader_id, "family": a.family, "version": a.version,
                         "value": a.value} for a in answers],
        },
    }


def cited_change(*, subject: str, facet: str, filed_value: JsonValue, source: CitedSource,
                 answers: Sequence[ReaderAnswer], registered_sources: Sequence[RegisteredSource],
                 owners: Sequence[str] = (), _allow_unchanged: bool = False) -> CitedChange:
    """Write ``answers``' agreed value as ``cited``, or refuse with a named reason.

    ``registered_sources`` lists every source registered for this subject and facet.
    ``owners`` are the ids of the subject's lab and provider, for the publisher check.
    """
    facet_def = _facet(facet)
    if facet_def is None:
        return _refuse("unknown_facet", facet)
    refusal = (_check_source(source, facet_def, owners)
               or _check_readers(answers, facet_def)
               or _check_retaining(registered_sources))
    if refusal is not None:
        return refusal
    value = answers[0].value
    if value is None:
        return _refuse("no_value", "the readers agree the page states nothing; that is not a change")
    problem = _value_fits(value, facet_def)
    if problem is not None:
        return _refuse("value_invalid", problem)
    if not _allow_unchanged and _canonical(value, facet_def) == _canonical(filed_value, facet_def):
        return _refuse("value_unchanged", "the agreed value is the filed value")
    return CitedChange("cited_change", None, "", _record(subject, facet, value, source, answers,
                                                         filed_value))


# --- the re-read ---------------------------------------------------------------------------------


def cited_change_block(fact: Mapping[str, Any]) -> Mapping[str, Any] | None:
    """The ``cited_change`` block of a fact (in its ``derivation``), or ``None``."""
    derivation = fact.get("derivation") if isinstance(fact, Mapping) else None
    block = derivation.get("cited_change") if isinstance(derivation, Mapping) else None
    return block if isinstance(block, Mapping) else None


def reread_required(fact: Mapping[str, Any], current_sha256: str) -> bool:
    """Whether the rolling re-read must have two readers read the page again.

    True for a cited-change fact whose recorded sha256 differs from the page's now (a
    missing or malformed recorded sha256 counts as a difference). False for a fact that
    is not a cited change, and for a page whose sha256 has not changed.
    """
    block = cited_change_block(fact)
    return block is not None and block.get("sha256") != current_sha256


@dataclass(frozen=True)
class Reread:
    """What a re-read of a cited-change fact decided.

    ``current``: the sha256 is unchanged, nothing to do. ``confirmed``: two readers agree
    the recorded value still holds; ``record`` carries the new sha256 and date.
    ``changed``: two readers agree on another value; ``record`` carries it. ``flagged``:
    the readers disagree, are not two, or a condition failed; the fact stays as filed and
    is listed for review. ``reason`` names the refusal.
    """

    outcome: Literal["current", "confirmed", "changed", "flagged"]
    reason: str | None = None
    record: dict[str, JsonValue] | None = None
    detail: str = field(default="")


def reread(fact: Mapping[str, Any], *, source: CitedSource, answers: Sequence[ReaderAnswer],
           registered_sources: Sequence[RegisteredSource], owners: Sequence[str] = ()) -> Reread:
    """Re-read a cited-change fact. A changed sha256 needs two readers; fewer flags it."""
    block = cited_change_block(fact)
    if block is None:
        return Reread("flagged", "not_a_cited_change", None, "the fact carries no cited_change block")
    if not reread_required(fact, source.sha256):
        return Reread("current")
    outcome = cited_change(subject=str(fact.get("subject")), facet=str(fact.get("facet")),
                           filed_value=fact.get("value"), source=source, answers=answers,
                           registered_sources=registered_sources, owners=owners,
                           _allow_unchanged=True)
    if not outcome.changed:
        return Reread("flagged", outcome.reason, None, outcome.detail)
    agreed = outcome.record["value"] if outcome.record else None
    facet_def = _facet(str(fact.get("facet")))
    same = _canonical(agreed, facet_def) == _canonical(fact.get("value"), facet_def)
    return Reread("confirmed" if same else "changed", None, outcome.record)
