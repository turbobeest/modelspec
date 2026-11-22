"""A cite-only page may change a value when two readers of different families agree.

Jamie, 2026-11-22 (MODEL-531). The rule, as it is built here:

1. Two readers from different model families each read the page in memory, blind to
   each other and to the filed value, and return the same normalised value. A
   disagreement leaves the fact as filed and flags it. Blindness is proven, not
   declared: ``decision.cited_reader`` builds the one prompt from the URL, the facet
   definition, the subject's name and the page bytes only, and ``cited_change``
   rebuilds that prompt from the page bytes and refuses unless both readers' recorded
   prompt hashes and input manifests match it. Both families must be known lineages.
2. The page is first-party for the facet: the lab's or provider's own page, of a
   kind the facet's ``permitted_source_kinds`` allows, with a recorded publisher that
   is the subject's lab.
3. The fact is served as cited, never verified. The record keeps the URL, read date,
   sha256 and both readers' answers, with their reader ids, families, versions, prompt
   hashes and input manifests. It keeps no page text and no excerpt, and no
   ``Verification`` is logged. The block is ``record["derivation"]["cited_change"]``.
4. The rolling re-read re-reads such a fact. When the page's sha256 changes, two
   readers read the page again (``reread_required``, ``reread``).
5. A retaining source wins. The gate itself looks up, in the data directory's source
   registry and the subject's card, every source registered for the subject and facet;
   any of them on a host that retains copies makes it refuse. A lookup that fails is a
   refusal.

``cited_change`` is the only gate. It checks every condition in code and either
returns the whole record or refuses with one named reason. It never writes a partial
change. It reads no page and calls no model: the page bytes and the readers' answers
come in as data.
"""

from __future__ import annotations

import json
import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import JsonValue

from decision.cited_reader import (
    INPUT_FIELDS, ReaderAnswer, build_prompt, input_manifest, sha256,
)
from decision.model import _LINEAGES, _NO_LINEAGE, DETERMINISTIC, model_family
from decision.retention import DATA_DIR_ENV, cite_only_origin_status, cite_only_status

RULE = "two-readers-cited-change@2"
DECIDED_BY = "Jamie 2026-11-22 (MODEL-531)"
#: Source kinds that are a lab's or provider's own page. A facet's
#: ``permitted_source_kinds`` must also list the kind.
FIRST_PARTY_KINDS = frozenset({
    "lab_documentation", "lab_announcement", "provider_documentation", "provider_terms",
    "provider_trust_center",
})
#: A string answer longer than this reads as an excerpt, not a normalised value.
MAX_STRING_LENGTH = 120
#: The lineages a reader family may name (``decision.model._LINEAGES``, after mapping).
KNOWN_FAMILIES = frozenset(_LINEAGES.values())
#: Data-directory file: ``{source_id: {"to": url}}`` for a retaining-host source that now
#: answers 3xx to another host. It is not a retaining path when the target is cite-only.
REDIRECTS_FILE = "registry/source-redirects.json"

#: Every named refusal reason.
REFUSALS = (
    "registry_lookup_failed",
    "unknown_facet",
    "host_not_cite_only",
    "host_unreadable",
    "source_kind_not_permitted",
    "not_first_party",
    "reader_count",
    "reader_metadata_missing",
    "reader_input_missing",
    "reader_input_not_blind",
    "reader_families_not_distinct",
    "readers_disagree",
    "no_value",
    "value_invalid",
    "value_unchanged",
    "retaining_source_registered",
    "retaining_source_unreadable",
    "bad_read_date",
)


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


# --- the registry lookup -------------------------------------------------------------------------


class LookupFailed(Exception):
    """The data directory, the subject's card or its source registry could not be read."""


@dataclass(frozen=True)
class Lookup:
    """What the registry says about one subject and facet."""

    subject_name: str
    fact: Mapping[str, Any]
    sources: Mapping[str, Mapping[str, Any]]
    redirects: Mapping[str, Any]

    @property
    def registered_ids(self) -> tuple[str, ...]:
        ids = [s.get("source_id") for s in self.fact.get("sources") or []]
        return tuple(dict.fromkeys([*ids, *(self.fact.get("checked_sources") or [])]))


_SUBJECT = re.compile(r"[a-z0-9][a-z0-9._-]*/[a-z0-9][a-z0-9._-]*")


def lookup(subject: str, facet: str, data_dir: str | Path | None = None) -> Lookup:
    """Read the subject's card, the source registry and the redirect list from the data directory."""
    import os

    root = data_dir or os.environ.get(DATA_DIR_ENV, "").strip()
    if not root:
        raise LookupFailed("no data directory is named")
    root = Path(root)
    if not _SUBJECT.fullmatch(subject):
        raise LookupFailed("the subject is not a model id")
    try:
        card = (root / "models" / f"{subject}.md").read_text(encoding="utf-8")
        front = yaml.safe_load(card.split("---", 2)[1])
        facts = {f["facet"]: f for f in front["facts"]}
        sources = {s["id"]: s for s in
                   yaml.safe_load((root / "registry" / "sources.yaml").read_text("utf-8"))["sources"]}
        path = root / REDIRECTS_FILE
        redirects = json.loads(path.read_text("utf-8")) if path.is_file() else {}
        name = front["display_name"]
        fact = facts[facet]
    except (OSError, ValueError, KeyError, TypeError, IndexError, yaml.YAMLError) as error:
        raise LookupFailed(f"{type(error).__name__}") from None
    if not isinstance(redirects, dict) or not isinstance(name, str) or not name:
        raise LookupFailed("malformed registry")
    return Lookup(name, fact, sources, redirects)


# --- the checks ----------------------------------------------------------------------------------


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


def _check_source(row: Mapping[str, Any], facet: Any, subject: str,
                  read_at: datetime) -> CitedChange | None:
    if not isinstance(read_at, datetime) or read_at.tzinfo is None \
            or read_at > datetime.now(UTC):
        return _refuse("bad_read_date", "the read time is missing, naive or in the future")
    url = row.get("url")
    status = cite_only_origin_status(url, ())
    if status is None:
        return _refuse("host_unreadable", "the source URL does not parse")
    if not status:
        return _refuse("host_not_cite_only",
                       "the host retains copies, so the verified path applies")
    kind = row.get("kind")
    if kind not in facet.permitted_source_kinds:
        return _refuse("source_kind_not_permitted",
                       f"{kind} is not a permitted source kind for {facet.id}")
    owner = subject.split("/", 1)[0]
    if kind not in FIRST_PARTY_KINDS:
        return _refuse("not_first_party", f"{kind} is not a lab's or provider's own page")
    if not row.get("publisher") or row.get("publisher") != owner:
        return _refuse("not_first_party",
                       "the source registry records no publisher, or not the subject's lab")
    return None


def _check_readers(answers: Sequence[ReaderAnswer], facet: Any, *, url: str, subject_name: str,
                   page_bytes: bytes) -> CitedChange | None:
    if len(answers) != 2 or not all(isinstance(a, ReaderAnswer) for a in answers):
        return _refuse("reader_count", f"{len(answers)} readers; the rule needs exactly two")
    if not all(a.metadata_present() for a in answers):
        return _refuse("reader_metadata_missing", "a reader id, family or version is missing")
    mapped = [model_family(a.family) for a in answers]
    if any(a.family.strip().casefold() in {DETERMINISTIC, *_NO_LINEAGE} for a in answers) \
            or any(m not in KNOWN_FAMILIES for m in mapped) or mapped[0] == mapped[1] \
            or answers[0].reader_id == answers[1].reader_id:
        return _refuse("reader_families_not_distinct",
                       "the readers are not two distinct, known model lineages")
    prompt_hash = sha256(build_prompt(url=url, facet_id=facet.id, subject_name=subject_name,
                                      page_bytes=page_bytes))
    manifest = input_manifest(url=url, facet_id=facet.id, subject_name=subject_name,
                              page_bytes=page_bytes)
    if not all(isinstance(a.manifest, dict) and a.manifest and a.prompt_sha256 for a in answers):
        return _refuse("reader_input_missing", "a reader's prompt hash or input manifest is missing")
    if any(a.manifest != manifest or a.prompt_sha256 != prompt_hash
           or list(a.manifest.get("fields", ())) != list(INPUT_FIELDS) for a in answers):
        return _refuse("reader_input_not_blind",
                       "a reader's input is not the prompt built from the URL, facet "
                       "definition, subject name and page bytes alone")
    if _canonical(answers[0].value, facet) != _canonical(answers[1].value, facet):
        return _refuse("readers_disagree", "the readers returned different values")
    return None


def _check_retaining(found: Lookup, facet: Any) -> CitedChange | None:
    for source_id in found.registered_ids:
        row = found.sources.get(source_id)
        if row is None:
            return _refuse("registry_lookup_failed",
                           f"registered source {source_id} is not in the source registry")
        if row.get("kind") not in facet.permitted_source_kinds:
            continue
        status = cite_only_status(row.get("url"))
        if status is None:
            return _refuse("retaining_source_unreadable",
                           f"registered source {source_id} has a URL that does not parse")
        if status:
            continue
        moved = found.redirects.get(source_id)
        if isinstance(moved, Mapping) and cite_only_status(moved.get("to")) is True:
            continue
        return _refuse("retaining_source_registered",
                       f"registered source {source_id} is on a host that retains copies")
    return None


def _retrieved_at(read_at: datetime) -> str:
    return read_at.astimezone(UTC).replace(microsecond=0).isoformat()


def _record(subject: str, facet_id: str, value: JsonValue, row: Mapping[str, Any], source_id: str,
            read_at: datetime, page_sha: str, answers: Sequence[ReaderAnswer],
            previous: JsonValue) -> dict[str, JsonValue]:
    """The record: values, URL, date, sha256 and the readers. No page text."""
    return {
        "subject": subject,
        "facet": facet_id,
        "value": value,
        "state": "known",
        "resolution": "cited",
        "source": {
            "source_id": source_id,
            "snapshot_ref": f"sha256:{page_sha}",
            "retrieved_at": _retrieved_at(read_at),
            "cited_regions": [r["id"] for r in row.get("cited_regions") or []] or ["page"],
        },
        "derivation": {"cited_change": {
            "rule": RULE,
            "decided_by": DECIDED_BY,
            "read_date": read_at.astimezone(UTC).date().isoformat(),
            "sha256": page_sha,
            "url": row["url"],
            "previous_value": previous,
            "readers": [{"reader_id": a.reader_id, "family": a.family, "version": a.version,
                         "value": a.value, "prompt_sha256": a.prompt_sha256,
                         "manifest": a.manifest} for a in answers],
        }},
    }


def _gate(*, subject: str, facet: str, source_id: str, read_at: datetime, page_bytes: bytes,
          answers: Sequence[ReaderAnswer], allow_unchanged: bool) -> CitedChange:
    facet_def = _facet(facet)
    if facet_def is None:
        return _refuse("unknown_facet", facet)
    try:
        found = lookup(subject, facet)
    except LookupFailed as error:
        return _refuse("registry_lookup_failed", str(error))
    row = found.sources.get(source_id)
    if row is None or not row.get("url"):
        return _refuse("registry_lookup_failed", "the cited source is not in the source registry")
    refusal = (_check_source(row, facet_def, subject, read_at)
               or _check_readers(answers, facet_def, url=row["url"],
                                 subject_name=found.subject_name, page_bytes=page_bytes)
               or _check_retaining(found, facet_def))
    if refusal is not None:
        return refusal
    value = answers[0].value
    if value is None:
        return _refuse("no_value", "the readers agree the page states nothing; that is not a change")
    problem = _value_fits(value, facet_def)
    if problem is not None:
        return _refuse("value_invalid", problem)
    filed = found.fact.get("value")
    if not allow_unchanged and found.fact.get("state") == "known" \
            and _canonical(value, facet_def) == _canonical(filed, facet_def):
        return _refuse("value_unchanged", "the agreed value is the filed value")
    return CitedChange("cited_change", None, "", _record(
        subject, facet, value, row, source_id, read_at, sha256(page_bytes), answers, filed))


def cited_change(*, subject: str, facet: str, source_id: str, read_at: datetime,
                 page_bytes: bytes, answers: Sequence[ReaderAnswer]) -> CitedChange:
    """Write ``answers``' agreed value as ``cited``, or refuse with a named reason.

    The filed value, the source row (URL, kind, publisher) and every source registered
    for the subject and facet are looked up here, in the data directory, never supplied.
    ``page_bytes`` are the bytes the readers read; the gate hashes them and rebuilds the
    readers' prompt from them. They are not stored.
    """
    return _gate(subject=subject, facet=facet, source_id=source_id, read_at=read_at,
                 page_bytes=page_bytes, answers=answers, allow_unchanged=False)


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


def cited_change_facts(data_dir: str | Path) -> list[dict[str, Any]]:
    """Every fact in the data directory's cards that carries a ``cited_change`` block.

    Each entry has ``subject``, ``facet``, ``value``, ``derivation`` and ``source_id``.
    """
    out: list[dict[str, Any]] = []
    for path in sorted((Path(data_dir) / "models").glob("*/*.md")):
        try:
            front = yaml.safe_load(path.read_text("utf-8").split("---", 2)[1])
            facts = front.get("facts") or []
        except (OSError, IndexError, AttributeError, yaml.YAMLError):
            continue
        for fact in facts:
            if isinstance(fact, dict) and cited_change_block(fact) is not None:
                sources = fact.get("sources") or [{}]
                out.append({"subject": f"{path.parent.name}/{path.stem}", "facet": fact.get("facet"),
                            "value": fact.get("value"), "derivation": fact.get("derivation"),
                            "source_id": sources[0].get("source_id")})
    return out


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


def reread(fact: Mapping[str, Any], *, source_id: str, read_at: datetime, page_bytes: bytes,
           answers: Sequence[ReaderAnswer]) -> Reread:
    """Re-read a cited-change fact. A changed sha256 needs two readers; fewer flags it."""
    block = cited_change_block(fact)
    if block is None:
        return Reread("flagged", "not_a_cited_change", None, "the fact carries no cited_change block")
    if not reread_required(fact, sha256(page_bytes)):
        return Reread("current")
    outcome = _gate(subject=str(fact.get("subject")), facet=str(fact.get("facet")),
                    source_id=source_id, read_at=read_at, page_bytes=page_bytes, answers=answers,
                    allow_unchanged=True)
    if not outcome.changed:
        return Reread("flagged", outcome.reason, None, outcome.detail)
    facet_def = _facet(str(fact.get("facet")))
    agreed = outcome.record["value"] if outcome.record else None
    same = _canonical(agreed, facet_def) == _canonical(fact.get("value"), facet_def)
    return Reread("confirmed" if same else "changed", None, outcome.record)
