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
4. The rolling re-read re-reads such a fact. When the page's visible text changes (a hash
   of the normalised text, so byte churn does not count; at most one request per fact per
   7 days), two readers read the page again (``reread_required``, ``reread_due``, ``reread``).
5. A retaining source wins. The gate itself looks up, in the data directory's source
   registry and the subject's card, every source registered for the subject and facet;
   any of them on a host that retains copies makes it refuse. A lookup that fails is a
   refusal.

``cited_change`` is the only gate. It checks every condition in code and either
returns the whole record or refuses with one named reason. It never writes a partial
change. The gate itself fetches the page in memory with redirects off (every hop must be
a cite-only host), calls the reader harness, and logs every attempt; a caller supplies
only the readers (and, in tests, the HTTP transport). No page is persisted. A first
complete attempt that did not agree blocks any later agreement (``prior_attempt_disagreed``).
"""

from __future__ import annotations

import json
import re
import urllib.error
import urllib.request
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, field
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from typing import Any, Literal
from urllib.parse import urljoin

import yaml
from pydantic import JsonValue

from decision.cited_reader import (
    INPUT_FIELDS, Reader, ReaderAnswer, ReaderError, attempts, build_prompt, canonical,
    input_manifest, read_page, sha256, text_sha256,
)
from decision.model import _LINEAGES, _NO_LINEAGE, DETERMINISTIC, model_family
from decision.retention import DATA_DIR_ENV, cite_only_origin_status, cite_only_status

RULE = "two-readers-cited-change@3"
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
#: An entry in that file is honoured only while its ``checked`` date is at most this old.
REDIRECT_MAX_AGE = timedelta(days=7)
MAX_HOPS = 3
USER_AGENT = "ModelSpec-Cite-Read/1.0 (+https://modelspec.dev)"

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
    "prior_attempt_disagreed",
    "reader_failed",
    "page_unreadable",
    "redirect_to_retaining_host",
    "reading_not_found",
    "reading_ambiguous",
    "unknown_benchmark",
)


@dataclass(frozen=True)
class CitedChange:
    """``cited_change`` when the whole rule held; ``refused`` with a named reason otherwise."""

    outcome: Literal["cited_change", "refused", "absence_pending", "not_published"]
    reason: str | None = None
    detail: str = ""
    record: dict[str, JsonValue] | None = None

    @property
    def changed(self) -> bool:
        return self.outcome == "cited_change"

    @property
    def marked(self) -> bool:
        """A reading's absence was seen on two harness reads at least 24 h apart."""
        return self.outcome == "not_published"


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
        block = cited_change_block(self.fact) or {}
        return tuple(dict.fromkeys([*ids, *(self.fact.get("checked_sources") or []),
                                    *(block.get("previous_sources") or [])]))


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
    return canonical(value, facet.id)


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


def _check_identities(items: Sequence[Any]) -> CitedChange | None:
    """Two readers (or answers) with id, family and version, of two distinct known lineages."""
    if len(items) != 2:
        return _refuse("reader_count", f"{len(items)} readers; the rule needs exactly two")
    if not all(all(isinstance(getattr(i, n, None), str) and getattr(i, n).strip()
                   for n in ("reader_id", "family", "version")) for i in items):
        return _refuse("reader_metadata_missing", "a reader id, family or version is missing")
    mapped = [model_family(i.family) for i in items]
    if any(i.family.strip().casefold() in {DETERMINISTIC, *_NO_LINEAGE} for i in items) \
            or any(m not in KNOWN_FAMILIES for m in mapped) or mapped[0] == mapped[1] \
            or items[0].reader_id == items[1].reader_id:
        return _refuse("reader_families_not_distinct",
                       "the readers are not two distinct, known model lineages")
    return None


def _check_readers(answers: Sequence[ReaderAnswer], facet: Any, *, url: str, subject_name: str,
                   page_bytes: bytes) -> CitedChange | None:
    if not all(isinstance(a, ReaderAnswer) for a in answers):
        return _refuse("reader_count", "the answers are not reader answers")
    refusal = _check_identities(answers)
    if refusal is not None:
        return refusal
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


def _redirect_honoured(entry: Any, found: Lookup, now: datetime) -> bool:
    """A source-redirects entry counts only if ``to`` is a registered cite-only source URL
    and ``checked`` is a date at most ``REDIRECT_MAX_AGE`` old."""
    if not isinstance(entry, Mapping):
        return False
    registered = {row.get("url") for row in found.sources.values()
                  if cite_only_status(row.get("url")) is True}
    try:
        checked = date.fromisoformat(str(entry.get("checked")))
    except ValueError:
        return False
    today = now.astimezone(UTC).date()
    return entry.get("to") in registered and checked <= today \
        and today - checked <= REDIRECT_MAX_AGE


def _check_retaining(found: Lookup, facet: Any, now: datetime) -> CitedChange | None:
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
        if status or _redirect_honoured(found.redirects.get(source_id), found, now):
            continue
        return _refuse("retaining_source_registered",
                       f"registered source {source_id} is on a host that retains copies")
    return None


def _retrieved_at(read_at: datetime) -> str:
    return read_at.astimezone(UTC).replace(microsecond=0).isoformat()


def _record(subject: str, facet_id: str, value: JsonValue, row: Mapping[str, Any], source_id: str,
            read_at: datetime, page_sha: str, page_text_sha: str, answers: Sequence[ReaderAnswer],
            previous: JsonValue, previous_sources: Sequence[str],
            resolved: Sequence[str]) -> dict[str, JsonValue]:
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
            "text_sha256": page_text_sha,
            "url": row["url"],
            "previous_value": previous,
            "previous_sources": list(previous_sources),
            "resolved_urls": list(resolved),
            "readers": [{"reader_id": a.reader_id, "family": a.family, "version": a.version,
                         "value": a.value, "prompt_sha256": a.prompt_sha256,
                         "manifest": a.manifest} for a in answers],
        }},
    }


Request = Callable[[str], "tuple[int, str | None, bytes]"]


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


def _http_once(url: str) -> tuple[int, str | None, bytes]:
    """One request with redirects off: the status, the Location header and the body (in memory)."""
    opener = urllib.request.build_opener(_NoRedirect)
    try:
        with opener.open(urllib.request.Request(url, headers={"User-Agent": USER_AGENT}),
                         timeout=60) as response:
            return response.status, None, response.read(8 * 1024 * 1024 + 1)
    except urllib.error.HTTPError as error:
        return error.code, error.headers.get("Location"), b""


def _fetch(url: str, request: Request) -> tuple[bytes, tuple[str, ...]] | CitedChange:
    """The page bytes, read in memory with redirects off. Every hop is checked by hand and
    must be on a cite-only host; nothing is persisted."""
    resolved: list[str] = []
    current = url
    for _ in range(MAX_HOPS + 1):
        try:
            status, location, body = request(current)
        except Exception as error:  # noqa: BLE001  a transport failure reads no page
            return _refuse("page_unreadable", type(error).__name__)
        if 300 <= status < 400 and location:
            target = urljoin(current, location)
            hop = cite_only_status(target)
            if hop is None:
                return _refuse("host_unreadable", "a redirect target does not parse")
            if not hop:
                return _refuse("redirect_to_retaining_host",
                               "the page redirects to a host that retains copies; not requested")
            resolved.append(target)
            current = target
            continue
        if status != 200 or not body or len(body) > 8 * 1024 * 1024:
            return _refuse("page_unreadable", f"HTTP {status}")
        return body, tuple(resolved)
    return _refuse("page_unreadable", "too many redirects")


def _gate(*, subject: str, facet: str, source_id: str, readers: Sequence[Reader],
          request: Request | None, allow_unchanged: bool, epoch: str = "initial",
          page: tuple[bytes, tuple[str, ...]] | None = None,
          now: datetime | None = None) -> CitedChange:
    now = now or datetime.now(UTC)
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
    refusal = _check_source(row, facet_def, subject, now) or _check_retaining(found, facet_def, now)
    if refusal is not None:
        return refusal
    refusal = _check_identities(readers)  # before any read: a bad pair is never an attempt
    if refusal is not None:
        return refusal
    # No retry-shopping. Every complete attempt at this subject, facet and epoch, on any page,
    # is counted: any disagreement blocks. An agreement authorises only if it was made through
    # this harness (``harness`` true); an agreement from reads whose blindness was never proven
    # (``harness`` false, seeded) authorises nothing, but a disagreement from them still blocks.
    history = [a for a in attempts(subject, facet, epoch) if a.get("complete")]
    if any(not a.get("agreed") for a in history):
        return _refuse("prior_attempt_disagreed",
                       "an earlier complete attempt at this fact did not agree")
    prior = [a for a in history if a.get("harness") is True]
    if page is None:
        fetched = _fetch(row["url"], request or _http_once)
        if isinstance(fetched, CitedChange):
            return fetched
        page = fetched
    page_bytes, resolved = page
    answers: list[ReaderAnswer] = []
    for _ in range(2):  # an incomplete attempt (a reader failed) may be tried once more
        try:
            answers = read_page(subject=subject, url=row["url"], facet_id=facet,
                                subject_name=found.subject_name, page_bytes=page_bytes,
                                readers=readers, epoch=epoch)
            break
        except ReaderError:
            continue
    if not answers:
        return _refuse("reader_failed", "a reader returned no usable answer")
    refusal = _check_readers(answers, facet_def, url=row["url"], subject_name=found.subject_name,
                             page_bytes=page_bytes)
    if refusal is not None:
        return refusal
    value = answers[0].value
    if value is None:
        return _refuse("no_value", "the readers agree the page states nothing; that is not a change")
    # A prior agreement on another non-null value is a conflict signal, seeded ones too.
    if any(a.get("agreed") and a.get("agreed_value") is not None
           and _canonical(a.get("agreed_value"), facet_def) != _canonical(value, facet_def)
           for a in history):
        return _refuse("prior_attempt_disagreed", "an earlier agreed attempt returned another value")
    problem = _value_fits(value, facet_def)
    if problem is not None:
        return _refuse("value_invalid", problem)
    filed = found.fact.get("value")
    if not allow_unchanged and found.fact.get("state") == "known" \
            and _canonical(value, facet_def) == _canonical(filed, facet_def):
        return _refuse("value_unchanged", "the agreed value is the filed value")
    return CitedChange("cited_change", None, "", _record(
        subject, facet, value, row, source_id, now, sha256(page_bytes), text_sha256(page_bytes),
        answers, filed,
        found.registered_ids, resolved))


def cited_change(*, subject: str, facet: str, source_id: str, readers: Sequence[Reader],
                 request: Request | None = None) -> CitedChange:
    """Fetch the page, have two readers read it, and write their agreed value as ``cited``,
    or refuse with a named reason.

    The filed value, the source row (URL, kind, publisher) and every source registered for
    the subject and facet (and any the fact cited before) are looked up here, in the data
    directory, never supplied. The gate fetches the page itself in memory with redirects off,
    checks every hop's host, and calls the reader harness itself: no answer, hash or manifest
    comes from the caller. ``request`` is the HTTP transport only (tests inject it).
    """
    return _gate(subject=subject, facet=facet, source_id=source_id, readers=readers,
                 request=request, allow_unchanged=False)


# --- a benchmark board reading (Jamie 2026-11-22) -------------------------------------------------
#
# Rule 15 covers a board reading too. The subject is a model, the "facet" is
# ``benchmark:<id>``, and the reading is one evidence row of the card, named by its settings
# (``model_id_as_evaluated``, ``effort``, ``harness``). First party means the board's own
# publisher, not the subject's lab: the source is the benchmark's registered ``benchmark_author``
# page, whose ``publisher`` is a registry id (a lab, provider or subscription vendor) whose
# registry URL host is the source's host and the benchmark page's ``publisher.url`` host.
# Every other condition is the facet rule's, through the same checks.
#
# A model the board no longer lists: both readers agree the page states no value for the row.
# One such read is only logged (``absence_pending``). A second, at least ``ABSENCE_GAP`` after a
# pending one, returns ``not_published`` with the day the absence was first seen, for the
# ``not_published_since`` field of the row. A later read that finds a value ends the pending run.

BENCHMARK_PREFIX = "benchmark:"
BENCHMARK_AUTHOR = "benchmark_author"
ABSENCE_GAP = timedelta(hours=24)
READING_KEYS = ("model_id_as_evaluated", "effort", "harness")


class _EveryKind:
    """A reading counts every source cited for the benchmark, whatever its kind."""

    def __contains__(self, item: object) -> bool:
        return True


@dataclass(frozen=True)
class _ReadingFacet:
    """The part of a facet the shared checks read."""

    id: str
    permitted_source_kinds: Any = _EveryKind()


@dataclass(frozen=True)
class ReadingLookup:
    subject_name: str
    row: Mapping[str, Any]
    benchmark: Mapping[str, Any]
    sources: Mapping[str, Mapping[str, Any]]
    redirects: Mapping[str, Any]
    publishers: Mapping[str, str]
    cited: tuple[str, ...]

    def as_lookup(self) -> Lookup:
        return Lookup(self.subject_name, {"sources": [{"source_id": i} for i in self.cited],
                                          "checked_sources": []}, self.sources, self.redirects)


def reading_epoch(reading: Mapping[str, Any]) -> str:
    return "reading:" + sha256(canonical({k: reading.get(k) for k in READING_KEYS}, "_"))[:16]


def _front(path: Path) -> dict[str, Any]:
    front = yaml.safe_load(path.read_text(encoding="utf-8").split("---", 2)[1])
    if not isinstance(front, dict):
        raise ValueError("front matter")
    return front


def reading_lookup(subject: str, benchmark_id: str, reading: Mapping[str, Any],
                   data_dir: str | Path | None = None) -> Lookup | ReadingLookup | CitedChange:
    """The card's evidence row for the reading, the benchmark page, the source registry and the
    publisher registry, or a refusal. A reading names ``model_id_as_evaluated``, ``effort`` and
    ``harness``; it must match exactly one evidence row of the benchmark."""
    import os

    root = data_dir or os.environ.get(DATA_DIR_ENV, "").strip()
    if not root:
        return _refuse("registry_lookup_failed", "no data directory is named")
    root = Path(root)
    if not _SUBJECT.fullmatch(subject) or not re.fullmatch(r"[a-z0-9][a-z0-9_.-]*", benchmark_id):
        return _refuse("registry_lookup_failed", "the subject or benchmark is not an id")
    if set(reading) != set(READING_KEYS):
        return _refuse("reading_not_found", f"a reading names exactly {', '.join(READING_KEYS)}")
    try:
        front = _front(root / "models" / f"{subject}.md")
        page = root / "benchmarks" / f"{benchmark_id}.md"
        if not page.is_file():
            return _refuse("unknown_benchmark", benchmark_id)
        benchmark = _front(page)
        sources = {s["id"]: s for s in
                   yaml.safe_load((root / "registry" / "sources.yaml").read_text("utf-8"))["sources"]}
        path = root / REDIRECTS_FILE
        redirects = json.loads(path.read_text("utf-8")) if path.is_file() else {}
        publishers: dict[str, str] = {}
        providers = yaml.safe_load((root / "registry" / "providers.yaml").read_text("utf-8"))
        for group in ("providers", "subscription_vendors"):
            for entry in providers.get(group) or []:
                publishers[entry["id"]] = str(entry.get("url") or "")
        for entry in yaml.safe_load((root / "registry" / "labs.yaml").read_text("utf-8"))["labs"]:
            publishers.setdefault(entry["id"], str(entry.get("url") or ""))
        name = front["display_name"]
        rows = [r for r in front["benchmarks"] if r.get("benchmark_id") == benchmark_id]
    except (OSError, ValueError, KeyError, TypeError, IndexError, AttributeError,
            yaml.YAMLError) as error:
        return _refuse("registry_lookup_failed", type(error).__name__)
    if not isinstance(redirects, dict) or not isinstance(name, str) or not name:
        return _refuse("registry_lookup_failed", "malformed registry")
    hits = [r for r in rows if all(r.get(k) == reading[k] for k in READING_KEYS)]
    if not hits:
        return _refuse("reading_not_found", "no evidence row has these settings")
    if len(hits) > 1:
        return _refuse("reading_ambiguous", "several evidence rows have these settings")
    cited = tuple(dict.fromkeys(s.get("source_id") for r in rows for s in r.get("sources") or []))
    return ReadingLookup(name, hits[0], benchmark, sources, redirects, publishers, cited)


def _host(url: Any) -> str | None:
    from urllib.parse import urlsplit

    try:
        host = (urlsplit(str(url)).hostname or "").lower().rstrip(".")
    except ValueError:
        return None
    return host.removeprefix("www.") or None


def _check_board_source(found: ReadingLookup, source_id: str, now: datetime) -> CitedChange | None:
    """The source is the board's own publisher's page, on a cite-only host."""
    if source_id not in found.cited:
        return _refuse("registry_lookup_failed", "the reading's evidence does not cite this source")
    row = found.sources.get(source_id)
    if row is None or not row.get("url"):
        return _refuse("registry_lookup_failed", "the cited source is not in the source registry")
    status = cite_only_origin_status(row["url"], ())
    if status is None:
        return _refuse("host_unreadable", "the source URL does not parse")
    if not status:
        return _refuse("host_not_cite_only", "the host retains copies, so the verified path applies")
    if row.get("kind") != BENCHMARK_AUTHOR:
        return _refuse("source_kind_not_permitted", f"{row.get('kind')} is not {BENCHMARK_AUTHOR}")
    publisher = row.get("publisher")
    registered = found.publishers.get(publisher) if isinstance(publisher, str) else None
    if not publisher or not registered:
        return _refuse("not_first_party",
                       "the source registry records no publisher, or one the registries do not know")
    host = _host(row["url"])
    owners = {_host(registered), _host((found.benchmark.get("publisher") or {}).get("url"))}
    if host is None or owners != {host}:
        return _refuse("not_first_party",
                       "the source's publisher is not the benchmark's own publisher")
    return None


def reading_definition(benchmark: Mapping[str, Any], reading: Mapping[str, Any]) -> str:
    """What a reader is asked: the row's settings, never a filed value."""
    metric = benchmark.get("metric") or {}
    unit = metric.get("unit") or ""
    parts = [f"the {metric.get('name') or 'score'} the board states for the row labelled "
             f"{reading['model_id_as_evaluated']!r}"]
    if reading.get("effort"):
        parts.append(f"at effort {reading['effort']!r}")
    if reading.get("harness"):
        parts.append(f"in harness {reading['harness']!r}")
    return (f"{' '.join(parts)}. Type: number, a bare number in {unit or 'the board unit'} "
            f"(no units, no sign), exactly as the board prints it. Return null when the board "
            f"lists no such row or prints no score for it.")


def _entry_time(entry: Mapping[str, Any]) -> datetime | None:
    try:
        return datetime.fromisoformat(str(entry.get("at")))
    except ValueError:
        return None


def _is_absent(entry: Mapping[str, Any]) -> bool:
    return bool(entry.get("agreed")) and entry.get("harness") is True \
        and bool(entry.get("readers")) and all(r.get("value") is None for r in entry["readers"])


def pending_absences(history: Sequence[Mapping[str, Any]]) -> list[Mapping[str, Any]]:
    """Harness reads that found the row absent and were not followed by a read that found it."""
    seen = [a for a in history if a.get("agreed") and a.get("agreed_value") is not None
            and a.get("harness") is True and _entry_time(a)]
    out = []
    for a in history:
        t = _entry_time(a)
        if _is_absent(a) and t and not any(_entry_time(b) > t for b in seen):
            out.append(a)
    return sorted(out, key=_entry_time)


def cited_reading(*, subject: str, benchmark_id: str, reading: Mapping[str, Any], source_id: str,
                  readers: Sequence[Reader], request: Request | None = None,
                  now: datetime | None = None) -> CitedChange:
    """The gate for one board reading: fetch the board in memory, have two readers read the one
    row, and return their agreed score as ``cited``, an absence (pending or, on the second read
    at least 24 h later, marked), or a named refusal. Everything but the readers and the
    transport is looked up here."""
    now = now or datetime.now(UTC)
    found = reading_lookup(subject, benchmark_id, reading)
    if isinstance(found, CitedChange):
        return found
    refusal = _check_board_source(found, source_id, now) \
        or _check_retaining(found.as_lookup(), _ReadingFacet(BENCHMARK_PREFIX + benchmark_id), now)
    if refusal is None:
        refusal = _check_identities(readers)
    if refusal is not None:
        return refusal
    facet_id, epoch = BENCHMARK_PREFIX + benchmark_id, reading_epoch(reading)
    history = [a for a in attempts(subject, facet_id, epoch) if a.get("complete")]
    if any(not a.get("agreed") for a in history):
        return _refuse("prior_attempt_disagreed",
                       "an earlier complete attempt at this reading did not agree")
    url = found.sources[source_id]["url"]
    fetched = _fetch(url, request or _http_once)
    if isinstance(fetched, CitedChange):
        return fetched
    page_bytes, resolved = fetched
    definition = reading_definition(found.benchmark, reading)
    answers: list[ReaderAnswer] = []
    for _ in range(2):
        try:
            answers = read_page(subject=subject, url=url, facet_id=facet_id,
                                subject_name=found.subject_name, page_bytes=page_bytes,
                                readers=readers, epoch=epoch, definition=definition)
            break
        except ReaderError:
            continue
    if not answers:
        return _refuse("reader_failed", "a reader returned no usable answer")
    facet = _ReadingFacet(facet_id)
    prompt_hash = sha256(build_prompt(url=url, facet_id=facet_id, subject_name=found.subject_name,
                                      page_bytes=page_bytes, definition=definition))
    manifest = input_manifest(url=url, facet_id=facet_id, subject_name=found.subject_name,
                              page_bytes=page_bytes, definition=definition)
    if not all(isinstance(a.manifest, dict) and a.manifest and a.prompt_sha256 for a in answers):
        return _refuse("reader_input_missing", "a reader's prompt hash or input manifest is missing")
    if any(a.manifest != manifest or a.prompt_sha256 != prompt_hash for a in answers):
        return _refuse("reader_input_not_blind", "a reader's input is not the rebuilt blind prompt")
    if canonical(answers[0].value, facet.id) != canonical(answers[1].value, facet.id):
        return _refuse("readers_disagree", "the readers returned different values")
    value = answers[0].value
    mark = {"subject": subject, "benchmark_id": benchmark_id,
            "reading": {k: reading[k] for k in READING_KEYS}}
    if value is None:
        pending = pending_absences(history)
        first = _entry_time(pending[0]) if pending else None
        if first is None or now - first < ABSENCE_GAP:
            return CitedChange("absence_pending", None,
                               "the board lists no such row on this read; a second read at least "
                               "24 h after the first marks it", {**mark, "reads": len(pending) + 1})
        return CitedChange("not_published", None, "", {
            **mark, "not_published_since": first.astimezone(UTC).date().isoformat(),
            "reads": len(pending) + 1, "state": "known", "resolution": "cited"})
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return _refuse("value_invalid", "a board score is a number")
    benchmark_max = (found.benchmark.get("metric") or {}).get("max_score")
    if value < 0 or (isinstance(benchmark_max, (int, float)) and value > benchmark_max):
        return _refuse("value_invalid", "the score is outside the board's range")
    filed = found.row.get("score")
    if canonical(value, facet.id) == canonical(filed, facet.id):
        return _refuse("value_unchanged", "the agreed value is the filed value")
    record = _record(subject, facet_id, value, found.sources[source_id], source_id, now,
                     sha256(page_bytes), text_sha256(page_bytes), answers, filed, found.cited, resolved)
    record["benchmark_id"] = benchmark_id
    record["reading"] = mark["reading"]
    record["clears_not_published_since"] = found.row.get("not_published_since") not in (None, "")
    del record["facet"]
    return CitedChange("cited_change", None, "", record)


# --- the re-read ---------------------------------------------------------------------------------


def cited_change_block(fact: Mapping[str, Any]) -> Mapping[str, Any] | None:
    """The ``cited_change`` block of a fact (in its ``derivation``), or ``None``."""
    derivation = fact.get("derivation") if isinstance(fact, Mapping) else None
    block = derivation.get("cited_change") if isinstance(derivation, Mapping) else None
    return block if isinstance(block, Mapping) else None


REREAD_INTERVAL = timedelta(days=7)


def reread_required(fact: Mapping[str, Any], page_bytes: bytes) -> bool:
    """Whether the page's visible text differs from the text the readers read.

    The test hashes the normalised visible text in memory, so byte churn between two
    fetches (embedded timestamps, script bodies) does not count. True for a cited-change
    fact whose recorded ``text_sha256`` differs from the page's now (a missing one counts
    as a difference). False for a fact that is not a cited change.
    """
    block = cited_change_block(fact)
    return block is not None and block.get("text_sha256") != text_sha256(page_bytes)


def reread_due(fact: Mapping[str, Any], page_bytes: bytes, *, now: datetime,
               last_request: datetime | None = None) -> bool:
    """A re-read is requested only when the text changed AND at least ``REREAD_INTERVAL``
    has passed since the fact was read and since the last re-read request for it."""
    if not reread_required(fact, page_bytes):
        return False
    block = cited_change_block(fact) or {}
    marks = [last_request]
    try:
        marks.append(datetime.fromisoformat(str(block["read_date"])).replace(tzinfo=UTC))
    except (KeyError, ValueError):
        pass
    return all(m is None or now - m >= REREAD_INTERVAL for m in marks)


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


def reread(fact: Mapping[str, Any], *, source_id: str, readers: Sequence[Reader],
           request: Request | None = None) -> Reread:
    """Re-read a cited-change fact. The gate fetches the page; a changed sha256 needs two
    readers; fewer flags the fact. Each recorded sha256 is its own attempt-log epoch."""
    block = cited_change_block(fact)
    if block is None:
        return Reread("flagged", "not_a_cited_change", None, "the fact carries no cited_change block")
    subject, facet = str(fact.get("subject")), str(fact.get("facet"))
    try:
        found = lookup(subject, facet)
    except LookupFailed as error:
        return Reread("flagged", "registry_lookup_failed", None, str(error))
    row = found.sources.get(source_id)
    if row is None or not row.get("url"):
        return Reread("flagged", "registry_lookup_failed", None, "the cited source is not registered")
    fetched = _fetch(row["url"], request or _http_once)
    if isinstance(fetched, CitedChange):
        return Reread("flagged", fetched.reason, None, fetched.detail)
    if not reread_required(fact, fetched[0]):
        return Reread("current")
    outcome = _gate(subject=subject, facet=facet, source_id=source_id, readers=readers,
                    request=request, allow_unchanged=True, page=fetched,
                    epoch=f"reread:{block.get('text_sha256') or block.get('sha256')}")
    if not outcome.changed:
        return Reread("flagged", outcome.reason, None, outcome.detail)
    facet_def = _facet(facet)
    agreed = outcome.record["value"] if outcome.record else None
    same = _canonical(agreed, facet_def) == _canonical(fact.get("value"), facet_def)
    return Reread("confirmed" if same else "changed", None, outcome.record)
