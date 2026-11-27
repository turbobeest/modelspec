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

Offering facts too (MODEL-544). The subject may be an offering
(``<provider>/<lab>/<model>/<region>/<tier>`` in ``offerings/<provider>/<lab>/<model>.yaml``,
or ``<provider>/subscription/<plan>`` in ``offerings/subscriptions/<provider>.yaml``). Every
condition holds unchanged; first party is the offering's provider, and the readers' facet
definition says the subject is an offering. ``scripts/cited_offering.py`` writes the record
into the offering file and files its claim from the one source reference, so the offering
reference and the claim name the same copy.

``not_disclosed`` (MODEL-544). Two readers agreeing that the page states nothing is a change
only when the caller asks for one (``accept_not_disclosed``) and the page can show silence:
the readers saw all of its visible text, there is enough of it, and the fact cites no other
page of a permitted kind. Each reader's finding (``not_stated``) is recorded. Any
disagreement, and any earlier agreed attempt on a value, files nothing. A mismatch or
unreachable verdict binds the value it was logged for, so a new value would enter the build as
cited while the old verdict stayed logged: the gate refuses up front (``quarantined``) any fact,
card or offering, whose verification log or inline verification holds an unresolved mismatch or
unreachable verdict for any value (MODEL-544 review). The one exception (MODEL-552, Jamie
2026-11-25): when the caller asks (``clear_quarantine``), a fresh two-reader agreement may clear
one held mismatch within the limits in ``decision.quarantine_clearing``, and the record then
carries the clearing line the build admits the value through. An unreachable verdict, more than
one held verdict, and a fact that carries an owner's ruling stay refused. A verdict that line
released no longer holds the record in the epochs after the clearing epoch (MODEL-566,
``_unreleased``), so the rolling re-read reads a changed page with two readers again.

A retaining page may also correct a served value (MODEL-573): ``retained_agreement(correct=True)``
files an agreed other value within the limits in ``decision.retained_correction``, whose test the
build and the site loader ask of the filed record too.

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
import unicodedata
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
from schema.yaml_loader import load_yaml_unique

from decision.cited_reader import (
    INPUT_FIELDS, MAX_PAGE_CHARS, Reader, ReaderAnswer, ReaderError, attempts, build_prompt,
    canonical, facet_definition, input_manifest, normalised_text, read_page, sha256, text_sha256,
)
from decision.model import _LINEAGES, _NO_LINEAGE, DETERMINISTIC, model_family
from decision.retention import (
    DATA_DIR_ENV, TermsRegisterUnreadable, canonical_host, cite_only_origin_status,
    cite_only_status, classified_hosts, is_classified,
)

RULE = "two-readers-cited-change@3"
DECIDED_BY = "Jamie 2026-11-22 (MODEL-531)"
#: The same two-reader agreement on a page whose host retains copies (MODEL-558): it confirms
#: a filed value that no engine reader can read, and changes nothing (``retained_agreement``).
RETAINED_RULE = "two-readers-retained-agreement@1"
RETAINED_DECIDED_BY = "Jamie 2026-11-25 (MODEL-558)"
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
    "page_truncated",
    "page_too_short",
    "other_source_unread",
    "quarantined",
    "host_cite_only",
    "host_unclassed",
    "redirect_to_cite_only_host",
    "redirect_to_unclassed_host",
    "engine_reader_reads",
    "value_differs",
    "attempts_exhausted",
    "epoch_not_current",
    "clearing_not_later",
    "correction_not_admitted",
)
#: The most attempts, complete or not, at one subject, facet and epoch (MODEL-558 review): a
#: re-run cannot reset the retry budget to read again until two readers happen to agree.
MAX_ATTEMPTS = 3
#: The verification log, under the data directory, as ``decision.snapshot.collect_repo`` reads it.
VERIFICATION_LOG = "verification/log.jsonl"
#: A page the readers find silent must show at least this much visible text: a script shell
#: or a bot wall reads as silence, and silence there proves nothing.
MIN_SILENT_TEXT = 400
#: What the readers were told about an offering subject (MODEL-544). It names no value.
OFFERING_CLAUSE = (
    " The subject is an offering: the model as this provider serves it, or a subscription plan."
    " A statement the page makes for the provider's service or plan that the subject is applies"
    " to it even when it does not name the model; a statement only about another of the"
    " provider's services or products does not.")


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
    #: ``model`` (a card fact) or ``offering`` (a fact in ``offerings/``).
    kind: str = "model"
    #: The file the fact is in.
    path: Path | None = None
    #: The readers' facet definition, when it is not the registry's own (an offering's).
    definition: str | None = None
    #: The subject's published names, for the claim: the model's, or the plan's.
    names: tuple[str, ...] = ()
    #: Every identity the fact may carry in the verification log: the one its location makes
    #: (the card's ``model_id``, the offering row's own provider, model, region and tier), the
    #: one the build keys it by (its stored ``id`` wins there) and the one the gate was asked for.
    fact_ids: tuple[str, ...] = ()

    @property
    def registered_ids(self) -> tuple[str, ...]:
        ids = [s.get("source_id") for s in self.fact.get("sources") or []]
        block = cited_change_block(self.fact) or {}
        return tuple(dict.fromkeys([*ids, *(self.fact.get("checked_sources") or []),
                                    *(block.get("previous_sources") or [])]))


_SUBJECT = re.compile(r"[a-z0-9][a-z0-9._-]*/[a-z0-9][a-z0-9._-]*")
_PART = r"[a-zA-Z0-9][a-zA-Z0-9._-]*"
#: ``<provider>/<lab>/<model>/<region>/<tier>``, as ``decision.model.Offering.id``.
_OFFERING = re.compile(rf"({_PART})/([a-z0-9][a-z0-9._-]*)/([a-z0-9][a-z0-9._-]*)/({_PART})/({_PART})")
#: ``<provider>/subscription/<plan>``, as ``decision.model.SubscriptionOffering.id``.
_SUBSCRIPTION = re.compile(rf"({_PART})/subscription/({_PART})")


def subject_kind(subject: str) -> str | None:
    """``model``, ``offering`` or ``None`` for a subject id that is neither."""
    if _SUBJECT.fullmatch(subject):
        return "model"
    if _OFFERING.fullmatch(subject) or _SUBSCRIPTION.fullmatch(subject):
        return "offering"
    return None


def _registry(root: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    sources = {s["id"]: s for s in
               yaml.safe_load((root / "registry" / "sources.yaml").read_text("utf-8"))["sources"]}
    path = root / REDIRECTS_FILE
    redirects = json.loads(path.read_text("utf-8")) if path.is_file() else {}
    return sources, redirects


def _provider_name(root: Path, provider: str) -> str:
    providers = yaml.safe_load((root / "registry" / "providers.yaml").read_text("utf-8"))
    for group in ("providers", "subscription_vendors"):
        for entry in providers.get(group) or []:
            if entry.get("id") == provider and isinstance(entry.get("name"), str):
                return entry["name"]
    raise KeyError("provider")


def _offering_lookup(root: Path, subject: str, facet: str) -> Lookup:
    """The offering fact, from the one file the loader allows it in."""
    if match := _SUBSCRIPTION.fullmatch(subject):
        provider = match.group(1)
        path = root / "offerings" / "subscriptions" / f"{provider}.yaml"
    else:
        match = _OFFERING.fullmatch(subject)
        provider, lab, model = match.group(1), match.group(2), match.group(3)
        path = root / "offerings" / provider / lab / f"{model}.yaml"
    rows = load_yaml_unique(path.read_text(encoding="utf-8"))
    # The row is found by its own identity, as the build makes it, never by a stored id.
    hits = [(row, f) for row in rows if _row_id(row) == subject
            for f in row.get("facts") or [] if f.get("facet") == facet]
    if len(hits) != 1:
        raise KeyError("offering fact")
    row, fact = hits[0]
    stored_subject = (fact.get("subject") or {}).get("id")
    ids = (f"{subject}#{facet}", fact.get("id"), f"{stored_subject}#{facet}")
    provider_name = _provider_name(root, provider)
    if row.get("kind") == "subscription":
        names = (row["name"],)
        name = f"{row['name']}, a {provider_name} subscription plan"
    else:
        card = (root / "models" / f"{row['model']}.md").read_text(encoding="utf-8")
        names = (load_yaml_unique(card.split("---", 2)[1])["display_name"],)
        name = f"{names[0]}, as {provider_name} serves it"
    sources, redirects = _registry(root)
    if not all(isinstance(n, str) and n for n in names):
        raise TypeError("name")
    return Lookup(name, fact, sources, redirects, "offering", path,
                  facet_definition(facet) + OFFERING_CLAUSE, names, _ids(ids))


def _row_id(row: Mapping[str, Any]) -> str | None:
    """An offering row's id from its own fields, as ``decision.snapshot.collect_repo`` makes it."""
    try:
        if row.get("kind") == "subscription":
            return f"{row['provider']}/subscription/{row['plan']}"
        return f"{row['provider']}/{row['model']}/{row['region']}/{row['tier']}"
    except (KeyError, TypeError):
        return None


def _ids(ids: Sequence[Any]) -> tuple[str, ...]:
    return tuple(dict.fromkeys(i for i in ids if isinstance(i, str) and i))


def lookup(subject: str, facet: str, data_dir: str | Path | None = None) -> Lookup:
    """Read the subject's card (or offering file), the source registry and the redirect list
    from the data directory."""
    import os

    root = data_dir or os.environ.get(DATA_DIR_ENV, "").strip()
    if not root:
        raise LookupFailed("no data directory is named")
    root = Path(root)
    kind = subject_kind(subject)
    if kind is None:
        raise LookupFailed("the subject is not a model or offering id")
    try:
        if kind == "offering":
            found = _offering_lookup(root, subject, facet)
        else:
            path = root / "models" / f"{subject}.md"
            front = load_yaml_unique(path.read_text(encoding="utf-8").split("---", 2)[1])
            facts = [f for f in front["facts"] if f.get("facet") == facet]
            if len(facts) != 1:
                raise KeyError("card fact")
            sources, redirects = _registry(root)
            name = front["display_name"]
            # The build keys a card fact by the card's ``model_id`` (and a stored id over it).
            ids = (f"{subject}#{facet}", f"{front.get('model_id') or subject}#{facet}",
                   facts[0].get("id"))
            found = Lookup(name, facts[0], sources, redirects, "model", path, None, (name,),
                           _ids(ids))
    except (OSError, ValueError, KeyError, TypeError, IndexError, AttributeError,
            yaml.YAMLError) as error:
        raise LookupFailed(f"{type(error).__name__}") from None
    if not isinstance(found.redirects, dict) or not isinstance(found.subject_name, str) \
            or not found.subject_name:
        raise LookupFailed("malformed registry")
    return found


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


def _classed_retaining(url: Any) -> bool | None:
    """Whether ``url`` is on a host the terms register classes and that retains copies.

    ``None`` when the register cannot be read: a caller refuses."""
    try:
        classes = classified_hosts()
    except TermsRegisterUnreadable:
        return None
    if classes is None:
        return None
    try:
        host = canonical_host(url)
    except ValueError:
        return None
    return is_classified(host, classes) and cite_only_status(url) is False


def _check_source(row: Mapping[str, Any], facet: Any, subject: str,
                  read_at: datetime, *, retaining: bool = False) -> CitedChange | None:
    """The page is on a cite-only host (a classed retaining host when ``retaining``) and first
    party: of a first-party kind the facet permits, published by the subject's owner (a card's
    lab, an offering's provider: the subject id's first part either way)."""
    if not isinstance(read_at, datetime) or read_at.tzinfo is None \
            or read_at > datetime.now(UTC):
        return _refuse("bad_read_date", "the read time is missing, naive or in the future")
    url = row.get("url")
    status = cite_only_origin_status(url, ())
    if status is None:
        return _refuse("host_unreadable", "the source URL does not parse")
    if retaining and status:
        return _refuse("host_cite_only", "the host is cite-only, so cited_change applies")
    if retaining and not _classed_retaining(url):
        return _refuse("host_unclassed",
                       "the host has no class in the terms register; it is not requested")
    if not retaining and not status:
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
                   page_bytes: bytes, definition: str | None = None) -> CitedChange | None:
    if not all(isinstance(a, ReaderAnswer) for a in answers):
        return _refuse("reader_count", "the answers are not reader answers")
    refusal = _check_identities(answers)
    if refusal is not None:
        return refusal
    prompt_hash = sha256(build_prompt(url=url, facet_id=facet.id, subject_name=subject_name,
                                      page_bytes=page_bytes, definition=definition))
    manifest = input_manifest(url=url, facet_id=facet.id, subject_name=subject_name,
                              page_bytes=page_bytes, definition=definition)
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
            resolved: Sequence[str], *, retaining: bool = False) -> dict[str, JsonValue]:
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
            "rule": RETAINED_RULE if retaining else RULE,
            "decided_by": RETAINED_DECIDED_BY if retaining else DECIDED_BY,
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


def _fetch(url: str, request: Request, *,
           retaining: bool = False) -> tuple[bytes, tuple[str, ...]] | CitedChange:
    """The page bytes, read in memory with redirects off. Every hop is checked by hand and
    must be on a cite-only host (with ``retaining``, on a classed host that retains copies);
    nothing is persisted. The origin's current class is checked before it is requested."""
    origin = cite_only_status(url)
    if origin is None:
        return _refuse("host_unreadable", "the source URL does not parse")
    if retaining and origin:
        return _refuse("host_cite_only", "the host is cite-only; not read on the retaining path")
    if retaining and not _classed_retaining(url):
        return _refuse("host_unclassed",
                       "the host has no class in the terms register; it is not requested")
    if not retaining and not origin:
        return _refuse("host_not_cite_only",
                       "the host retains copies, so the verified path applies; not requested")
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
            if retaining and hop:
                return _refuse("redirect_to_cite_only_host",
                               "the page redirects to a cite-only host; not requested")
            if retaining and not _classed_retaining(target):
                return _refuse("redirect_to_unclassed_host",
                               "the page redirects to a host with no class; not requested")
            if not retaining and not hop:
                return _refuse("redirect_to_retaining_host",
                               "the page redirects to a host that retains copies; not requested")
            resolved.append(target)
            current = target
            continue
        if status != 200 or not body or len(body) > 8 * 1024 * 1024:
            return _refuse("page_unreadable", f"HTTP {status}")
        return body, tuple(resolved)
    return _refuse("page_unreadable", "too many redirects")


def quarantine_verdicts(fact_ids: Sequence[str], fact: Mapping[str, Any],
                        data_dir: str | Path | None = None, *, kind: str = "fact",
                        owns: Callable[[str], bool] | None = None) -> list[tuple[str, str]]:
    """``(id, value hash)`` of each value whose latest counting verdict is not ``verified``.

    ``kind`` is the verification target kind: ``fact`` (a card or offering fact) or
    ``evidence`` (a board reading, MODEL-547). ``owns`` claims further logged ids for the
    record: a reading's id changes with its score and date, so its earlier ids are found by
    what they belong to, not by a list.

    The log is parsed as the build parses it (``decision.snapshot.collect_repo``: every line
    through ``decision.owner_ruling.read_json_lines``, which refuses a repeated key; no text
    match) and ranked by the build's own rule
    (``_Compiler._verification_log``: latest ``date``, a later line on a tie, a same-family
    ``verified`` does not count). The fact's inline verification counts too, ranked before the
    log's lines, as the build ranks it. Every identity in ``fact_ids`` is checked, and any
    value, not only the filed one: a verdict binds its own value, so a change to another value
    would step around it. Raises ``LookupFailed`` when the log cannot be read.
    """
    return [key[1:] for key, _ in quarantine_rows(fact_ids, fact, data_dir, kind=kind, owns=owns)]


def quarantine_rows(fact_ids: Sequence[str], fact: Mapping[str, Any],
                    data_dir: str | Path | None = None, *, kind: str = "fact",
                    owns: Callable[[str], bool] | None = None
                    ) -> list[tuple[tuple[str, str, str], dict[str, Any]]]:
    """``quarantine_verdicts`` with each held verdict's key and winning row (MODEL-552: a
    clearing names the row it clears). Raises ``LookupFailed`` when the log cannot be read."""
    import os

    from decision.snapshot import _Compiler

    root = data_dir or os.environ.get(DATA_DIR_ENV, "").strip()
    if not root:
        raise LookupFailed("no data directory is named")
    from decision.owner_ruling import read_json_lines

    path = Path(root) / VERIFICATION_LOG
    try:
        rows = read_json_lines(path)
        return held_rows(_Compiler._verification_log(rows), fact_ids, fact, kind=kind, owns=owns)
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as error:
        raise LookupFailed(f"verification log: {type(error).__name__}") from None


def held_verdicts(latest: Mapping[tuple[str, str, str], Any], fact_ids: Sequence[str],
                  fact: Mapping[str, Any], *, kind: str = "fact",
                  owns: Callable[[str], bool] | None = None) -> list[tuple[str, str]]:
    """``quarantine_verdicts`` over a log already ranked by ``_Compiler._verification_log``
    (the build's own index): the fact's inline verification is ranked in, and every value of
    every identity counts. Raises ``KeyError``/``TypeError`` on a malformed inline record."""
    return [key[1:] for key, _ in held_rows(latest, fact_ids, fact, kind=kind, owns=owns)]


def held_rows(latest: Mapping[tuple[str, str, str], Any], fact_ids: Sequence[str],
              fact: Mapping[str, Any], *, kind: str = "fact",
              owns: Callable[[str], bool] | None = None
              ) -> list[tuple[tuple[str, str, str], dict[str, Any]]]:
    """``held_verdicts`` with each held verdict's ``(kind, id, value hash)`` and winning row."""
    from decision.snapshot import _counts

    ids = set(fact_ids)
    latest = dict(latest)
    inline = fact.get("verification")
    if isinstance(inline, Mapping) and isinstance(inline.get("target"), Mapping) \
            and _counts(inline):
        target = inline["target"]
        key = (target["kind"], target["id"], str(target.get("value_hash") or ""))
        entry = (str(inline["date"]), 0, dict(inline))
        if key not in latest or entry[:2] >= latest[key][:2]:
            latest[key] = entry
    return sorted(((key, dict(row)) for key, (_, _, row) in latest.items()
                   if key[0] == kind and (key[1] in ids or (owns is not None and owns(key[1])))
                   and row.get("outcome") != "verified"), key=lambda item: item[0])


def _check_silence(found: Lookup, facet: Any, source_id: str, page_bytes: bytes,
                   history: Sequence[Mapping[str, Any]]) -> CitedChange | None:
    """Both readers found the page silent. That is ``not_disclosed`` only when the page can
    show it: the readers saw all of its visible text, there is enough of it, the fact cites
    no other page of a permitted kind, and no earlier attempt agreed on a value."""
    text = normalised_text(page_bytes)
    if len(text) > MAX_PAGE_CHARS:
        return _refuse("page_truncated",
                       "the readers saw part of the page; silence there is not the page's")
    if len(text) < MIN_SILENT_TEXT:
        return _refuse("page_too_short",
                       "too little visible text to show the page is silent")
    others = [i for i in found.registered_ids if i != source_id
              and (found.sources.get(i) or {}).get("kind") in facet.permitted_source_kinds]
    if others:
        return _refuse("other_source_unread",
                       f"the fact also cites {others[0]}, which this read did not cover")
    if any(a.get("agreed") and a.get("agreed_value") is not None for a in history):
        return _refuse("prior_attempt_disagreed", "an earlier agreed attempt returned a value")
    return None


def _engine_reads(found: Lookup, subject: str, facet: Any, pages: Mapping[str, bytes]
                  ) -> str | None:
    """The method of a deterministic engine reader that reads the fact from a cited page, if any.

    On a host that retains copies the verified path wins (MODEL-558). ``pages`` holds the bytes
    of every retaining source the fact cites. Each page is put in a temporary copy store and read
    through ``StoredRegions`` (so a PDF takes ``decision.pdf_templates`` as in ``verify``), in
    the context of the full cited set, by the deterministic extractors together and then each
    alone, nothing logged. A reader
    that confirms the value, or finds another one, on any page reads the fact, and the two-reader
    path does not apply. Only when every engine reader finds no value on every page (no reading,
    or a reading of ``None``) are the pages left to the two readers. A check that cannot run
    refuses.
    """
    import os
    import tempfile

    from decision.model import SourceRef, TargetRef, VerificationActor
    from decision.sources import CopyStore, load_sources
    from decision.verify import Claim, StoredRegions, deterministic_extractors, verify

    root = Path(os.environ.get(DATA_DIR_ENV, "").strip() or ".")
    names = tuple(dict.fromkeys([*found.names, subject.split("/")[-1]]))
    target = (found.fact_ids or (f"{subject}#{facet.id}",))[0]
    today = datetime.now(UTC).date()
    try:
        registry = load_sources(root / "registry" / "sources.yaml")
    except Exception as error:  # noqa: BLE001  fail closed
        return f"unrun ({type(error).__name__})"
    with tempfile.TemporaryDirectory() as scratch:
        store = CopyStore(scratch)
        regions = StoredRegions(store, registry)
        refs: list[SourceRef] = []
        for source_id, page_bytes in pages.items():
            source = registry.get(source_id)
            if source is None:
                return f"unrun ({source_id} is not registered)"
            try:
                ref = store.put(page_bytes, source_url=str(source.url))
            except Exception as error:  # noqa: BLE001
                return f"unrun ({type(error).__name__})"
            cited = next((s.get("cited_regions") for s in found.fact.get("sources") or []
                          if s.get("source_id") == source_id), None)
            refs.append(SourceRef(source_id=source_id, snapshot_ref=ref, cited_regions=list(
                cited or [r.id for r in source.cited_regions] or ["page"])))
        # Each source is read in the context of the fact's full cited set (MODEL-558 review): a
        # reader that needs another source (the config reader needs the README) sees it. The
        # source under test goes first, so its own first mismatch is the one ``verify`` reports.
        extractors = deterministic_extractors()
        for n, first in enumerate(refs):
            ordered = (first, *refs[:n], *refs[n + 1:])
            claim = Claim(
                target=TargetRef(kind="fact", id=target), subject=subject, names=names,
                field=facet.id, value=found.fact.get("value"),
                collector=VerificationActor(agent="cited-change-gate", model_family="unrecorded",
                                            method=RETAINED_RULE),
                sources=ordered, unit=facet.unit, label=facet.label,
                state=found.fact.get("state"))
            # All readers together (the PDF route), then one at a time: ``verify`` reports only
            # its first mismatch, and a ``None`` reading must not hide a later reader's value.
            for chosen in [extractors, *([e] for e in extractors)]:
                try:
                    result = verify(claim, regions, chosen, today=today)
                except Exception as error:  # noqa: BLE001  an unrun check is no abstention
                    return f"unrun ({type(error).__name__})"
                if result.verification is None:
                    continue
                if result.outcome == "verified" or (result.outcome == "mismatch" and any(
                        d.field in {"value", "unit"} and d.found is not None
                        for d in result.diffs)):
                    return f"{result.verification.verifier.method} on {first.source_id}"
    return None


def _incomplete_values(entries: Sequence[Mapping[str, Any]]) -> list[JsonValue]:
    """Every answer recorded inside an incomplete attempt (MODEL-558 review): it counts too."""
    return [r.get("value") for a in entries if not a.get("complete")
            for r in a.get("readers") or [] if "value" in r]


QUARANTINED = "lifting it is the owner's call"


def _epoch_at_verdict(verdict: Mapping[str, Any], *, subject: str, facet: str, first: str,
                      base: str, settings: Any = None) -> CitedChange | None:
    """Refuse unless the subject's epoch now (``base``) is the one rule 15 derives for the record
    as filed when the verdict was made (``quarantine_clearing.verdict_epoch``, from the queue)."""
    import os

    from decision.cited_reader import ATTEMPTS_FILE
    from decision.quarantine_clearing import (
        CLEARINGS_FILE,
        QUEUE_FILE,
        AttemptLog,
        queue_history,
        read_clearings,
        verdict_epoch,
    )

    root = Path(os.environ.get(DATA_DIR_ENV, "").strip() or ".")
    target = str((verdict.get("target") or {}).get("id"))
    try:
        history = queue_history(root / QUEUE_FILE, {target}).get(target, [])
        log = AttemptLog.read(root / ATTEMPTS_FILE)
        clearings = read_clearings(root / CLEARINGS_FILE)
    except (OSError, ValueError) as error:
        return _refuse("registry_lookup_failed", f"queue or attempt log: {type(error).__name__}")
    derived = verdict_epoch(verdict, history=history, log=log, subject=subject, facet=facet,
                            first=first, settings=settings, clearings=clearings)
    if derived is None:
        return _refuse("quarantined", "the record's epoch when the verdict was made cannot be "
                       f"shown; {QUARANTINED}")
    # A board row filed in its settings epoch is in a board epoch of it once the gate names one
    # (MODEL-555): the board moved since, and the clearing extends the epoch the row is in now.
    if derived != base and not (derived == first and is_board_epoch(base, first)):
        return _refuse("epoch_not_current",
                       "the record's epoch now is not its epoch when the verdict was made")
    return None


Held = list[tuple[tuple[str, str, str], dict[str, Any]]]


def _unreleased(held: Held, record: Mapping[str, Any], subject: str, *, now: datetime,
                sources: Mapping[str, Mapping[str, Any]],
                owns: Callable[[str], bool] | None = None
                ) -> tuple[Held, list[list[Mapping[str, Any]]]] | CitedChange:
    """``(held, chains)``: the held verdicts that no valid clearing line has released for this
    record, and the chain that releases each one that was (MODEL-566). The test is the build's
    own (``quarantine_clearing.fact_chain``, or ``reading_chain`` when ``owns`` is given): the
    line is checked as #1169 checks it, and the record carries the block that clearing made or one
    a later agreement made in an epoch after the clearing epoch. A verdict newer than the clearing
    is not the one a line names, so it still holds. A read that fails refuses."""
    import os

    from decision.cited_reader import ATTEMPTS_FILE
    from decision.quarantine_clearing import (
        CLEARINGS_FILE,
        QUEUE_FILE,
        AttemptLog,
        fact_chain,
        queue_history,
        read_clearings,
        reading_chain,
    )

    root = Path(os.environ.get(DATA_DIR_ENV, "").strip() or ".")
    mismatches = [h for h in held if h[1].get("outcome") == "mismatch"]
    if not mismatches or not (root / CLEARINGS_FILE).is_file():
        return list(held), []
    try:
        clearings = read_clearings(root / CLEARINGS_FILE)
        targets = {str((row.get("target") or {}).get("id")) for _, row in mismatches}
        history = queue_history(root / QUEUE_FILE, targets)
        log = AttemptLog.read(root / ATTEMPTS_FILE)
    except (OSError, ValueError) as error:
        return _refuse("registry_lookup_failed",
                       f"clearing, queue or attempt log: {type(error).__name__}")
    urls = {str(k): str(v.get("url")) for k, v in sources.items()
            if isinstance(v, Mapping) and v.get("url")}
    common = dict(clearings=clearings, log=log, sources=urls, history=history,
                  cutoff=now.astimezone(UTC).date(), held=[row for _, row in held])
    try:
        chains = [(h, reading_chain(record, subject, verdict=h[1], owns=owns, **common)
                   if owns is not None else fact_chain(record, subject, verdict=h[1], **common))
                  for h in mismatches]
    except (KeyError, TypeError, ValueError, AttributeError) as error:
        return _refuse("registry_lookup_failed", f"clearing check: {type(error).__name__}")
    released = [h for h, chain in chains if chain is not None]
    return [h for h in held if h not in released], [c for _, c in chains if c is not None]


def _relitigates(chains: Sequence[Sequence[Any]], page_bytes: bytes, *,
                 own_fetch: bool, first: str, epoch: str, now: datetime,
                 region: str | None = None) -> CitedChange | None:
    """Refuse a read, after a verdict was released (MODEL-566), unless the gate fetched the page
    itself with its own transport (bytes or a transport a caller supplies never re-read a
    released fact, as MODEL-562 requires) and, for every released verdict, the page is another
    than one of the agreements that opened the epoch in the chain that releases it: its visible
    text hash differs, and so does its cited-region hash when both are logged
    (``quarantine_clearing.openers`` and ``_moved``, the build's own). A clearing, and each read
    after it, is not re-litigated in its own epoch. A clearing of a newer verdict is read in
    that verdict's own clearing epoch, and is not held to this."""
    from decision.quarantine_clearing import _moved, openers, openers_before

    if not own_fetch:
        return _refuse("quarantined", "a released verdict is re-read only on a page the gate "
                       f"fetched itself; {QUARANTINED}")
    read = {"text_sha256": text_sha256(page_bytes), "region_sha256": region,
            "at": now.astimezone(UTC).replace(microsecond=0).isoformat()}
    ready = [openers_before(openers(chain, first, epoch), read, lambda _: True)
             for chain in chains]
    if not all(ready):
        return _refuse("quarantined", "the read would come before the clearing or read that "
                       f"opened the epoch; {QUARANTINED}")
    if not all(any(_moved(o, read) for o in before) for before in ready):
        return _refuse("quarantined", "the page is the one the record's read after its clearing "
                       f"rests on; a released verdict is not re-litigated there; {QUARANTINED}")
    return None


def _not_a_link(chains: Sequence[Sequence[Any]], *, subject: str, facet: str,
                first: str, epoch: str) -> CitedChange | None:
    """After the read is logged (MODEL-566): refuse unless it is a link of every chain that
    releases a verdict on the record, by the build's own test
    (``quarantine_clearing.link_problem`` over every attempt logged in the epoch: an agreement on
    silence or absence there and a later value disagree, and so does an incomplete answer)."""
    from decision.quarantine_clearing import link_problem, openers

    logged = attempts(subject, facet, epoch)
    for chain in chains:
        problem = link_problem(logged, logged[-1], openers(chain, first, epoch), facet) \
            if logged else "the read is not logged"
        if problem is not None:
            return _refuse("prior_attempt_disagreed", problem)
    return None


def _clearing_target(held: Sequence[tuple[tuple[str, str, str], Mapping[str, Any]]],
                     subject_record: Mapping[str, Any], now: datetime, *, allowed: bool,
                     kind: str = "fact"
                     ) -> tuple[CitedChange | None, tuple[tuple[str, str, str], dict] | None]:
    """``(refusal, None)`` unless the one held verdict may be cleared (MODEL-552), then
    ``(None, (key, row))``. Only when the caller asks (``allowed``), never for a fact that carries
    an owner's ruling, only one verdict, only a mismatch, and only on a later day than it."""
    from decision.owner_ruling import has_ruling
    from decision.quarantine_clearing import clearable, later_than

    what = "fact" if kind == "fact" else "reading"
    if not allowed:
        return _refuse("quarantined", f"{len(held)} value(s) of this {what} hold an unresolved "
                       f"mismatch or unreachable verdict; {QUARANTINED}"), None
    if has_ruling(subject_record):  # a fact's (MODEL-551) or a board row's (MODEL-569)
        return _refuse("quarantined", f"the {what} carries an owner's ruling; a ruling never "
                       f"lifts a quarantine, and a clearing does not apply to a ruled {what}"), None
    problem = clearable(held)
    if problem is not None:
        return _refuse("quarantined", f"{problem}; {QUARANTINED}"), None
    key, row = held[0]
    if not later_than(row, now):
        return _refuse("clearing_not_later",
                       "the agreement would not be on a later day than the verdict"), None
    return None, (key, dict(row))


def _with_clearing(outcome: CitedChange, clearing: tuple[tuple[str, str, str], dict], *,
                   subject: str, facet: str, epoch: str, base: str,
                   answers: Sequence[ReaderAnswer], now: datetime) -> CitedChange:
    """The outcome with ``record["clearings"]``: the one line that clears the verdict, naming the
    agreement just logged. The line is checked as the build checks it; a failure refuses."""
    from decision.quarantine_clearing import (
        agreement_problem,
        base_epoch,
        epoch_problem,
        later_than,
        line,
        verdict_sha256,
    )

    key, verdict = clearing
    if base_epoch(epoch, verdict_sha256(verdict)) != base:
        return _refuse("epoch_not_current", "the read was not in the verdict's clearing epoch")
    import copy

    from decision.cited_reader import _attempts_path
    from decision.owner_ruling import loads

    record = copy.deepcopy(dict(outcome.record or {}))
    value = record.get("value")
    logged = attempts(subject, facet, epoch)
    entry = logged[-1] if logged else {}
    # The clearing names the agreement by its exact line: the attempt log's last line, which
    # ``read_page`` has just appended.
    raws = [raw for raw in _attempts_path(None).read_text(encoding="utf-8").split("\n")
            if raw.strip()]
    if not raws or loads(raws[-1]) != entry \
            or entry.get("prompt_sha256") != (answers[0].prompt_sha256 if answers else None) \
            or agreement_problem(entry, value, facet) is not None:
        return _refuse("registry_lookup_failed",
                       "the agreement just logged is not the attempt log's last line")
    for counted in (logged, attempts(subject, facet, base)):
        problem = epoch_problem(counted, value, facet)
        if problem is not None:
            return _refuse("prior_attempt_disagreed", problem)
    at = datetime.fromisoformat(str(entry["at"]))
    if not later_than(verdict, at):
        return _refuse("clearing_not_later", "the agreement is not on a later day than the verdict")
    # The block names the epoch it was read in and the rule-15 epoch that one extends, so the
    # build can derive the base and refuse a fabricated one (``quarantine_clearing.base_problem``).
    block = record["derivation"]["cited_change"]
    block["previous_epoch"], block["clearing_epoch"] = base, epoch
    record["clearings"] = [line(key=key, verdict=verdict, subject=subject, facet=facet,
                                epoch=epoch, attempt_line=raws[-1], value=value,
                                at=max(now, at))]
    return CitedChange(outcome.outcome, outcome.reason, outcome.detail, record)


def _region_sha256(row: Mapping[str, Any], page_bytes: bytes) -> str | None:
    """The hash of the source's cited regions on the page read (MODEL-562): logged with the
    attempt, so a ruling on it names the region it settled. ``None`` when they cannot be read."""
    from decision.ruling_reread import region_sha256

    return region_sha256(row, page_bytes)


def _ruled_epoch(found: Lookup, subject: str, source_id: str, page_bytes: bytes,
                 own_fetch: bool) -> str:
    """The epoch a ruled fact is read in, from the page just fetched (MODEL-562). Only a page
    the gate fetched itself, with its own transport, can name a reopened epoch."""
    import os

    from decision.ruling_reread import gate_epoch

    return gate_epoch(found.fact, subject, source_id=source_id, rows=found.sources,
                      page_bytes=page_bytes, own_fetch=own_fetch,
                      data_dir=os.environ.get(DATA_DIR_ENV, "").strip() or ".")


def _gate(*, subject: str, facet: str, source_id: str, readers: Sequence[Reader],
          request: Request | None, allow_unchanged: bool,
          page: tuple[bytes, tuple[str, ...]] | None = None,
          now: datetime | None = None, accept_not_disclosed: bool = False,
          retaining: bool = False, epoch: str | None = None,
          clear_quarantine: bool = False, own_page: bool = False,
          correct: bool = False) -> CitedChange:
    """The rule-15 gate. ``epoch``, when given, only states which epoch the caller means: the gate
    reads in the filed fact's own epoch (``fact_epoch``) and refuses (``epoch_not_current``) if
    the two differ. A caller never chooses the epoch the gate reads in. ``clear_quarantine`` lets
    a fresh agreement clear a held mismatch within Jamie's limits
    (``decision.quarantine_clearing``); the fact is then read in that verdict's clearing epoch.
    ``correct`` lets an agreement on a retaining page correct the filed value
    (``decision.retained_correction``, MODEL-573)."""
    now = now or datetime.now(UTC)
    facet_def = _facet(facet)
    if facet_def is None:
        return _refuse("unknown_facet", facet)
    kind = subject_kind(subject)
    if kind is not None and (kind == "offering") != (facet_def.subject == "offering"):
        return _refuse("registry_lookup_failed", f"{facet} is not a facet of a {kind}")
    try:
        found = lookup(subject, facet)
    except LookupFailed as error:
        return _refuse("registry_lookup_failed", str(error))
    # Up front, before any read or attempt: an unresolved verdict on this fact is not lifted here,
    # unless the caller asks for a clearing and the verdict may be cleared (MODEL-552).
    try:
        held = quarantine_rows(found.fact_ids or (f"{subject}#{facet}",), found.fact)
    except LookupFailed as error:
        return _refuse("registry_lookup_failed", str(error))
    # A verdict a valid clearing line released no longer holds the fact in the epochs after the
    # clearing epoch (MODEL-566), by the build's own test; any other verdict still does.
    released, chains = False, []
    if held:
        got = _unreleased(held, found.fact, subject, now=now, sources=found.sources)
        if isinstance(got, CitedChange):
            return got
        held, chains = got
        released = bool(chains)
    clearing = None
    if held:
        refusal, clearing = _clearing_target(held, found.fact, now,
                                             allowed=clear_quarantine and not retaining)
        if refusal is not None:
            return refusal
    row = found.sources.get(source_id)
    if row is None or not row.get("url"):
        return _refuse("registry_lookup_failed", "the cited source is not in the source registry")
    refusal = _check_source(row, facet_def, subject, now, retaining=retaining) \
        or (None if retaining else _check_retaining(found, facet_def, now))
    if refusal is not None:
        return refusal
    refusal = _check_identities(readers)  # before any read: a bad pair is never an attempt
    if refusal is not None:
        return refusal
    # No retry-shopping. Every complete attempt at this subject, facet and epoch, on any page,
    # is counted: any disagreement blocks. An agreement authorises only if it was made through
    # this harness (``harness`` true); an agreement from reads whose blindness was never proven
    # (``harness`` false, seeded) authorises nothing, but a disagreement from them still blocks.
    # The epoch is the filed fact's own (``fact_epoch``), never the caller's.
    from decision.owner_ruling import has_ruling

    current = base = fact_epoch(found.fact)
    if clearing is not None:
        # A clearing is read in the verdict's own clearing epoch (MODEL-552): no attempt in it can
        # come before the verdict. The fact's epoch is counted too: a disagreement there blocks.
        from decision.quarantine_clearing import clearing_epoch, verdict_sha256

        current = clearing_epoch(base, verdict_sha256(clearing[1]))
        refusal = _epoch_at_verdict(clearing[1], subject=subject, facet=facet, first="initial",
                                    base=base)
        if refusal is not None:
            return refusal
    elif has_ruling(found.fact):
        # MODEL-562: a ruled fact (never cleared: ``_clearing_target`` refuses one) is read in the
        # epoch its page names (``decision.ruling_reread``), so the page is fetched first. A cited
        # region the rolling re-read recorded as changed reopens rule 15; anything else is the
        # ruling's epoch, where the disagreement blocks. Bytes a caller supplies, or reads
        # through its own transport, never reopen one.
        own_fetch = page is None and request is None
        if page is None:
            fetched = _fetch(row["url"], request or _http_once, retaining=retaining)
            if isinstance(fetched, CitedChange):
                return fetched
            page = fetched
        current = _ruled_epoch(found, subject, source_id, page[0], own_fetch)
    if epoch is not None and epoch != current:
        return _refuse("epoch_not_current",
                       "the named epoch is not the filed fact's; the gate reads only in that one")
    epoch = current

    def recorded() -> list[dict]:
        """Every attempt counted for disagreement: this epoch's, and the fact's when clearing."""
        return attempts(subject, facet, epoch) + (
            attempts(subject, facet, base) if clearing is not None else [])

    logged = attempts(subject, facet, epoch)
    history = [a for a in recorded() if a.get("complete")]
    if any(not a.get("agreed") for a in history):
        return _refuse("prior_attempt_disagreed",
                       "an earlier complete attempt at this fact did not agree")
    # An answer inside an incomplete attempt counts: two that differ, or one that differs from
    # an agreed value, is a disagreement (MODEL-558 review).
    seen = {_canonical(v, facet_def) for v in _incomplete_values(recorded())} | {
        _canonical(a.get("agreed_value"), facet_def) for a in history if a.get("agreed")}
    if len(seen) > 1:
        return _refuse("prior_attempt_disagreed",
                       "answers recorded in earlier attempts at this fact do not agree")
    if len(logged) >= MAX_ATTEMPTS:
        return _refuse("attempts_exhausted",
                       f"{len(logged)} attempts at this fact are logged in this epoch")
    gate_fetched = page is None
    if page is None:
        fetched = _fetch(row["url"], request or _http_once, retaining=retaining)
        if isinstance(fetched, CitedChange):
            return fetched
        page = fetched
    page_bytes, resolved = page
    if released and clearing is None:
        # ``own_page``: the bytes are the gate module's own fetch (``reread``), never a caller's.
        refusal = _relitigates(chains, page_bytes, first="initial", epoch=epoch, now=now,
                               own_fetch=request is None and (gate_fetched or own_page),
                               region=_region_sha256(row, page_bytes))
        if refusal is not None:
            return refusal
    if retaining:
        # Before any reader is asked: if an engine reader reads the fact from any retaining page
        # the fact cites, the verified path applies.
        pages = {source_id: page_bytes}
        for entry in found.fact.get("sources") or []:
            other = entry.get("source_id")
            other_row = found.sources.get(other) or {}
            if other in pages or cite_only_status(other_row.get("url")) is not False:
                continue  # a cite-only page is not read by the engine and is not fetched here
            got = _fetch(other_row["url"], request or _http_once, retaining=True)
            if isinstance(got, CitedChange):
                return _refuse("engine_reader_reads",
                               f"{other} could not be read for the engine check ({got.reason})")
            pages[other] = got[0]
        method = _engine_reads(found, subject, facet_def, pages)
        if method is not None:
            return _refuse("engine_reader_reads",
                           f"{method} reads this fact; the verified path applies")
    # The bytes are the gate's own fetch, with its own transport (MODEL-573): never a caller's.
    own_fetch = request is None and (gate_fetched or own_page)
    answers: list[ReaderAnswer] = []
    for _ in range(2):  # an incomplete attempt (a reader failed) may be tried once more
        if len(attempts(subject, facet, epoch)) >= MAX_ATTEMPTS:
            return _refuse("attempts_exhausted", "the attempt budget for this fact is spent")
        try:
            answers = read_page(subject=subject, url=row["url"], facet_id=facet,
                                subject_name=found.subject_name, page_bytes=page_bytes,
                                readers=readers, epoch=epoch, definition=found.definition,
                                region_sha256=_region_sha256(row, page_bytes),
                                own_fetch=own_fetch)
            break
        except ReaderError:
            continue
    if not answers:
        values = _incomplete_values(recorded())
        if len({_canonical(v, facet_def) for v in values}) > 1:
            return _refuse("prior_attempt_disagreed",
                           "answers recorded in the incomplete attempts do not agree")
        return _refuse("reader_failed", "a reader returned no usable answer")
    refusal = _check_readers(answers, facet_def, url=row["url"], subject_name=found.subject_name,
                             page_bytes=page_bytes, definition=found.definition)
    if refusal is None and released and clearing is None:
        refusal = _not_a_link(chains, subject=subject, facet=facet, first="initial", epoch=epoch)
    if refusal is not None:
        return refusal
    value = answers[0].value
    filed = found.fact.get("value")
    if any(_canonical(v, facet_def) != _canonical(value, facet_def)
           for v in _incomplete_values(recorded())):
        return _refuse("prior_attempt_disagreed",
                       "an answer recorded in an incomplete attempt differs from this agreement")

    def cleared(outcome: CitedChange) -> CitedChange:
        """The outcome, with the clearing line it needs when it clears a quarantine."""
        if clearing is None or not outcome.changed or outcome.record is None:
            return outcome
        return _with_clearing(outcome, clearing, subject=subject, facet=facet, epoch=epoch,
                              base=base, answers=answers, now=now)

    if retaining:
        return _retained_outcome(subject, facet_def, value, filed, found, row, source_id, now,
                                 page_bytes, answers, resolved, history, epoch=epoch,
                                 correct=correct, released=released, own_fetch=own_fetch)
    if value is None:
        if not accept_not_disclosed:
            return _refuse("no_value",
                           "the readers agree the page states nothing; that is not a change")
        refusal = _check_silence(found, facet_def, source_id, page_bytes, history)
        if refusal is not None:
            return refusal
        if not (allow_unchanged or clearing is not None) \
                and found.fact.get("state") == "not_disclosed" and filed is None:
            return _refuse("value_unchanged", "the fact is filed not_disclosed already")
        record = _record(subject, facet, None, row, source_id, now, sha256(page_bytes),
                         text_sha256(page_bytes), answers, filed, found.registered_ids, resolved)
        record["state"] = "not_disclosed"
        for entry in record["derivation"]["cited_change"]["readers"]:
            entry["finding"] = "not_stated"
        return cleared(CitedChange("cited_change", None, "", record))
    if accept_not_disclosed and any(a.get("agreed") and a.get("agreed_value") is None
                                    for a in history):
        return _refuse("prior_attempt_disagreed", "an earlier agreed attempt found the page silent")
    # A prior agreement on another non-null value is a conflict signal, seeded ones too.
    if any(a.get("agreed") and a.get("agreed_value") is not None
           and _canonical(a.get("agreed_value"), facet_def) != _canonical(value, facet_def)
           for a in history):
        return _refuse("prior_attempt_disagreed", "an earlier agreed attempt returned another value")
    problem = _value_fits(value, facet_def)
    if problem is not None:
        return _refuse("value_invalid", problem)
    # A clearing re-files the filed value too: it is the agreement, not a change, that clears.
    if not (allow_unchanged or clearing is not None) and found.fact.get("state") == "known" \
            and _canonical(value, facet_def) == _canonical(filed, facet_def):
        return _refuse("value_unchanged", "the agreed value is the filed value")
    return cleared(CitedChange("cited_change", None, "", _record(
        subject, facet, value, row, source_id, now, sha256(page_bytes), text_sha256(page_bytes),
        answers, filed,
        found.registered_ids, resolved)))


def _retained_outcome(subject: str, facet_def: Any, value: JsonValue, filed: JsonValue,
                      found: Lookup, row: Mapping[str, Any], source_id: str, now: datetime,
                      page_bytes: bytes, answers: Sequence[ReaderAnswer],
                      resolved: Sequence[str],
                      history: Sequence[Mapping[str, Any]], *, epoch: str,
                      correct: bool = False, released: bool = False,
                      own_fetch: bool = False) -> CitedChange:
    """A retaining page confirms: the agreed value must be the filed, known value. With
    ``correct``, or for a fact a correction filed, an agreed other value corrects it within
    ``decision.retained_correction``'s limits (MODEL-573); anything else is ``value_differs``."""
    from decision.retained_correction import is_correction
    if value is None:
        return _refuse("no_value", "the readers agree the page states nothing; a retaining page "
                       "confirms a value and files no absence")
    if any(a.get("agreed") and _canonical(a.get("agreed_value"), facet_def)
           != _canonical(value, facet_def) for a in history):
        return _refuse("prior_attempt_disagreed",
                       "an earlier agreed attempt returned another value")
    problem = _value_fits(value, facet_def)
    if problem is not None:
        return _refuse("value_invalid", problem)
    same = found.fact.get("state") == "known" \
        and _canonical(value, facet_def) == _canonical(filed, facet_def)
    corrected = is_correction(found.fact)
    if same and not corrected:
        # The filed value is kept as filed (a set's order too): a confirmation changes nothing.
        return CitedChange("cited_change", None, "", _record(
            subject, facet_def.id, filed, row, source_id, now, sha256(page_bytes),
            text_sha256(page_bytes), answers, filed, found.registered_ids, resolved,
            retaining=True))
    if not (correct or corrected):
        return _refuse("value_differs", "the agreed value is not the filed value; a retaining "
                       "page changes nothing, and the fact is listed for the owner")
    return _corrected(subject, facet_def, filed if same else value, filed, found, row, source_id,
                      now, page_bytes, answers, resolved, epoch=epoch, released=released,
                      own_fetch=own_fetch)


def _corrected(subject: str, facet_def: Any, value: JsonValue, filed: JsonValue, found: Lookup,
               row: Mapping[str, Any], source_id: str, now: datetime, page_bytes: bytes,
               answers: Sequence[ReaderAnswer], resolved: Sequence[str], *, epoch: str,
               released: bool, own_fetch: bool) -> CitedChange:
    """The correction record (MODEL-573), or a refusal. The block names the epoch it was read in
    and the agreement just logged by its exact line; the record, as a writer files it, must pass
    the build's own test (``retained_correction.correction_problem``)."""
    from decision.owner_ruling import has_ruling, loads
    from decision.quarantine_clearing import AttemptLog, line_hash
    from decision.retained_correction import DECIDED_BY as CORRECTION_DECIDED_BY
    from decision.retained_correction import RULE as CORRECTION_RULE
    from decision.retained_correction import correction_problem, filed_fact, owner_only

    if owner_only(facet_def.id) or has_ruling(found.fact) or released:
        return _refuse("value_differs", "the agreed value is not the filed value; a licence fact, "
                       "an identity field, a ruled fact and a fact a clearing released are not "
                       "corrected here, and the fact is listed for the owner")
    region = _region_sha256(row, page_bytes)
    if not own_fetch or region is None:
        return _refuse("correction_not_admitted", "a correction rests only on the gate's own "
                       "fetch, with its own transport, of a page whose cited regions it hashed")
    record = _record(subject, facet_def.id, value, row, source_id, now, sha256(page_bytes),
                     text_sha256(page_bytes), answers, filed, found.registered_ids, resolved,
                     retaining=True)
    block = record["derivation"]["cited_change"]
    block["rule"], block["decided_by"] = CORRECTION_RULE, CORRECTION_DECIDED_BY
    from decision.cited_reader import _attempts_path

    try:
        raws = [raw for raw in _attempts_path(None).read_text(encoding="utf-8").split("\n")
                if raw.strip()]
        logged = attempts(subject, facet_def.id, epoch)
        if not raws or not logged or loads(raws[-1]) != logged[-1] \
                or logged[-1].get("prompt_sha256") != answers[0].prompt_sha256:
            return _refuse("registry_lookup_failed",
                           "the agreement just logged is not the attempt log's last line")
        block["epoch"], block["agreement"] = epoch, line_hash(raws[-1])
        block["region_sha256"] = region
        verdicts = _ranked_verdicts()
        log = AttemptLog(raws)
    except (OSError, ValueError, LookupFailed) as error:
        return _refuse("registry_lookup_failed", f"the logs cannot be read: {type(error).__name__}")
    urls = {str(k): str(v.get("url")) for k, v in found.sources.items()
            if isinstance(v, Mapping) and v.get("url")}
    problem = correction_problem(filed_fact(found.fact, record), subject, log=log,
                                 verdicts=verdicts, sources=urls, cutoff=now.astimezone(UTC).date(),
                                 ids=found.fact_ids)
    if problem is not None:
        return _refuse("correction_not_admitted", problem)
    return CitedChange("cited_change", None, "", record)


def _ranked_verdicts() -> Mapping[tuple[str, str, str], Any]:
    """The verification log ranked by the build's own rule, as ``quarantine_rows`` reads it."""
    import os

    from decision.owner_ruling import read_json_lines
    from decision.snapshot import _Compiler

    root = os.environ.get(DATA_DIR_ENV, "").strip()
    if not root:
        raise LookupFailed("no data directory is named")
    try:
        return _Compiler._verification_log(read_json_lines(Path(root) / VERIFICATION_LOG))
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as error:
        raise LookupFailed(f"verification log: {type(error).__name__}") from None


def retained_agreement(*, subject: str, facet: str, source_id: str, readers: Sequence[Reader],
                       request: Request | None = None, correct: bool = False) -> CitedChange:
    """Two readers confirm a filed value on a page whose host retains copies (MODEL-558).

    Jamie, 2026-11-25 (queue 16f): a fact a person confirmed on a structured page that no engine
    reader can read rests on a logged two-reader agreement. Every safeguard of ``cited_change``
    holds unchanged: the fact and its sources are looked up here, a quarantined fact is refused
    before any read, the page is first party, the gate fetches it in memory with redirects off,
    the two readers are distinct known lineages, blindness is proven, and every attempt is
    appended to the same attempt log under the same key, so a disagreement on either path
    blocks both. In place of the cite-only conditions: the host and every redirect hop must be
    classed in the terms register and retain copies, and no deterministic engine reader may read
    the fact from the page (``engine_reader_reads``). A retaining page only confirms: an agreed
    value other than the filed one is refused (``value_differs``) and changes nothing, and an
    agreed absence files nothing (``no_value``). The record is the ``cited_change`` block with
    rule ``RETAINED_RULE``; no ``Verification`` is written.

    ``correct`` (MODEL-573): an agreed value other than the filed one corrects it, within
    ``decision.retained_correction``'s limits: the agreement is in the fact's current epoch, by
    two distinct known families, with no disagreement logged there; the fact is no licence fact
    or identity field, carries no owner's ruling and holds no verdict. The record then carries
    rule ``retained_correction.RULE``, the epoch it was read in and the agreement's line hash,
    and the build serves the value as cited, never as verified, only through the same test.
    Outside the limits it is ``value_differs`` (or ``correction_not_admitted``), as before.
    """
    return _gate(subject=subject, facet=facet, source_id=source_id, readers=readers,
                 request=request, allow_unchanged=True, retaining=True, correct=correct)


def cited_change(*, subject: str, facet: str, source_id: str, readers: Sequence[Reader],
                 request: Request | None = None,
                 accept_not_disclosed: bool = False,
                 clear_quarantine: bool = False) -> CitedChange:
    """Fetch the page, have two readers read it, and write their agreed value as ``cited``,
    or refuse with a named reason.

    The subject is a model (a card fact) or an offering (a fact in ``offerings/``). The filed
    value, the source row (URL, kind, publisher) and every source registered for the subject
    and facet (and any the fact cited before) are looked up here, in the data directory,
    never supplied. The gate fetches the page itself in memory with redirects off, checks
    every hop's host, and calls the reader harness itself: no answer, hash or manifest comes
    from the caller. ``request`` is the HTTP transport only (tests inject it).

    ``accept_not_disclosed`` lets two readers' agreement that the page does not state the
    value file ``not_disclosed`` (see ``_check_silence``); without it that is ``no_value``.

    ``clear_quarantine`` (MODEL-552) lets a fresh agreement clear the fact's one held mismatch,
    within ``decision.quarantine_clearing``'s limits: the record then carries ``clearings``, the
    line the caller appends to the clearing log, and the build admits the value only through it.
    Without it a quarantined fact is refused up front, as before.
    """
    return _gate(subject=subject, facet=facet, source_id=source_id, readers=readers,
                 request=request, allow_unchanged=False,
                 accept_not_disclosed=accept_not_disclosed, clear_quarantine=clear_quarantine)


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
#
# A row's epoch includes the board page (MODEL-555, Jamie 2026-11-25). A row with no cited
# change used to be read in its settings epoch alone, so one split of its readers blocked it for
# good, whatever the board later said. Its epoch now names the row's board region
# (``row_region_sha256``: every eligible source the row cites, each by its cited-region hash,
# ``board_region_sha256``), from pages the gate fetched itself (``board_epoch``): re-reading the
# same board, or one that changed outside the cited region, stays in the epoch where the split
# blocks; a changed cited region opens a new epoch, where two agreeing readers may settle it.
# It fails closed: a complete attempt in the settings epoch with no recorded region hash (logged
# before region hashes, or through a caller's transport) keeps the row in its settings epoch, and
# a region that cannot be selected (a renamed table, a placeholder) or a cited source that is not
# eligible now refuses, so the row stays in its epoch. The region is the rows' cell contents only.

BENCHMARK_PREFIX = "benchmark:"
BENCHMARK_AUTHOR = "benchmark_author"
ABSENCE_GAP = timedelta(hours=24)
READING_KEYS = ("model_id_as_evaluated", "effort", "harness")


class _EveryKind:
    """The reading's own sources count whatever their kind, as the fact gate counts the
    sources registered for a fact."""

    def __contains__(self, item: object) -> bool:
        return True


@dataclass(frozen=True)
class _ReadingFacet:
    """The part of a facet the shared checks read."""

    id: str
    permitted_source_kinds: tuple[str, ...] = (BENCHMARK_AUTHOR,)


@dataclass(frozen=True)
class ReadingLookup:
    subject_name: str
    row: Mapping[str, Any]
    benchmark: Mapping[str, Any]
    sources: Mapping[str, Mapping[str, Any]]
    redirects: Mapping[str, Any]
    publishers: Mapping[str, str]
    #: Every source id the reading's own rows registered: those they cite, their
    #: ``checked_sources`` and the sources a past cited change replaced. Any kind counts.
    own: tuple[str, ...]
    #: The registered sources the benchmark page itself lists (by URL) that are a board
    #: author's or the subject's own lab's. Any kind counts, as for the reading's own rows.
    page: tuple[str, ...]
    #: The reading's own evidence id, as the build keys its verdicts (``e.get("id")``).
    evidence_ids: tuple[str, ...] = ()
    #: ``<model>#<benchmark>#``, for the subject and the card's ``model_id``: a logged id under
    #: one of these is the reading's earlier id unless another current row of the benchmark has it.
    id_prefixes: tuple[str, ...] = ()
    #: The ids of the benchmark's other current rows on the card (kept for callers; they no
    #: longer decide whose a verdict is: ``quarantine_clearing.reading_holds`` does).
    sibling_ids: frozenset[str] = frozenset()
    #: The card's model id: the id the build files the reading under, and the one prefix the
    #: gate and the build both search (``quarantine_clearing.reading_candidates``).
    model_id: str = ""

    def owns(self, logged_id: str) -> bool:
        """A logged evidence id that may hold this reading: its own, or any id under the
        reading's ``<model>#<benchmark>#`` prefix. Only a candidate: an id other than the row's
        own holds it only when its verdict's queue claim shows the same reading
        (``quarantine_clearing.reading_holds``, MODEL-552 follow-up)."""
        return logged_id in self.evidence_ids \
            or any(logged_id.startswith(prefix) for prefix in self.id_prefixes)

    @property
    def cited(self) -> tuple[str, ...]:
        return tuple(dict.fromkeys([*self.own, *self.page]))

    def lookup(self, ids: Sequence[str]) -> Lookup:
        return Lookup(self.subject_name, {"sources": [{"source_id": i} for i in ids],
                                          "checked_sources": []}, self.sources, self.redirects)


def _block_of(row: Mapping[str, Any]) -> Mapping[str, Any] | None:
    block = (row.get("derivation") or {}).get("cited_change") if isinstance(
        row.get("derivation"), Mapping) else None
    return block if isinstance(block, Mapping) else None


#: Marks a board epoch: ``<settings epoch>:board:<cited-region hash>`` (MODEL-555).
BOARD_MARK = ":board:"


def reading_epoch(reading: Mapping[str, Any], row: Mapping[str, Any] | None = None, *,
                  board: str | None = None) -> str:
    """The attempt-log epoch of a reading: its settings, and once the row carries a cited
    change, the text hash that change recorded (as the fact gate's re-read epoch). A later
    reading of a board that moved starts a new epoch; a disagreement within one still blocks.

    ``board`` (MODEL-555, Jamie 2026-11-25): for a row with no cited change, the row's board
    region (``row_region_sha256``) as the gate resolved it from pages it fetched itself
    (``board_epoch``). The epoch is then ``<settings epoch>:board:<hash>``, so a
    board whose cited region changed opens a new epoch for an unchanged row. A row that carries
    a cited change keeps its re-read epoch."""
    base = "reading:" + sha256(canonical({k: reading.get(k) for k in READING_KEYS}, "_"))[:16]
    block = _block_of(row) if row is not None else None
    if block:
        text = block.get('text_sha256') or block.get('sha256')
        cleared = block.get("clearing_epoch")  # as ``fact_epoch`` (MODEL-566)
        return f"{cleared}:reread:{text}" if isinstance(cleared, str) and cleared \
            else f"{base}:reread:{text}"
    return f"{base}{BOARD_MARK}{board}" if board else base


def _fold(text: str) -> str:
    """Rule 15's fold of visible text (``decision.cited_reader.normalised_text``)."""
    import html

    return re.sub(r"\s+", " ", html.unescape(text)).strip()


#: Page parts that announce or rotate, never a board's rows (MODEL-555 review): dropped before the
#: cited region is hashed, as are clock times with or without a zone.
_BOARD_VOLATILE_ROLES = frozenset({"banner", "alert", "alertdialog", "status", "marquee", "timer",
                                   "log"})
_BOARD_VOLATILE_TOKEN = re.compile(
    r"^(?:[\w-]*[-_])?(?:banner|announce\w*|alert|toast|marquee|ticker|carousel|slider|slides?"
    r"|rotat\w*|notice|notification|promo\w*|countdown|clock|timestamp|time-?ago|live)"
    r"(?:[-_][\w-]*)?$", re.IGNORECASE)
_BOARD_CLOCK = re.compile(
    r"\b\d{1,2}:\d{2}(?::\d{2}(?:\.\d+)?)?(?:\s*(?:[ap]\.?m\.?|z\b|utc|gmt|[a-z]{2,4}t\b))?",
    re.IGNORECASE)
_HTML_LIKE = re.compile(rb"<(?:html|body|main|div|table|tr|td|p|span|section|article)\b",
                        re.IGNORECASE)


def _board_volatile(node: Any) -> bool:
    if node.tag in ("marquee", "blink"):
        return True
    live = node.attrs.get("aria-live")
    if live is not None and live.lower() != "off":
        return True
    if node.attrs.get("role", "").lower() in _BOARD_VOLATILE_ROLES:
        return True
    tokens = (*node.classes, *node.attrs.get("id", "").split())
    return any(_BOARD_VOLATILE_TOKEN.match(t) for t in tokens)


def _drop_board_volatile(node: Any) -> None:
    from decision.normalise import Node

    node.children = [c for c in node.children
                     if not (isinstance(c, Node) and _board_volatile(c))]
    for child in node.children:
        if isinstance(child, Node):
            _drop_board_volatile(child)


_ROW_ROLES = frozenset({"row"})
_CELL_ROLES = frozenset({"cell", "gridcell", "columnheader", "rowheader"})


def _ancestors(node: Any):
    up = node.parent
    while up is not None:
        yield up
        up = up.parent


def _outermost(nodes: Sequence[Any]) -> list[Any]:
    ids = {id(n) for n in nodes}
    return [n for n in nodes if not any(id(a) in ids for a in _ancestors(n))]


_DATA_CELL_ROLES = frozenset({"cell", "gridcell"})
_SPACE_RUN = re.compile(r"\s+")
#: A pipe-table separator line: at least two columns and at least one pipe (a bare ``---`` is
#: not one).
_PIPE_RULE = re.compile(r"^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)+\|?\s*$")


def _cell_text(node: Any, rules: Any) -> str:
    """A cell's text for the hash only (MODEL-555 review): its text nodes run together as the
    page shows them (``<br>`` and block children are a break), volatile text and clock times
    stripped, every run of whitespace collapsed to one space and the ends stripped
    (``_collapse``). Markup that splits a value into spans (``5<span>1.2</span>``) or indents it
    hashes as the same visible text, while ``A B`` and ``AB`` stay apart. The normaliser's own
    text (``decision.normalise._inline``) is unchanged."""
    from decision.normalise import BLOCK, Node, _clean_line

    parts: list[str] = []

    def walk(n: Any) -> None:
        for child in n.children:
            if isinstance(child, Node):
                gap = child.tag == "br" or child.tag in BLOCK
                if gap:
                    parts.append(" ")
                walk(child)
                if gap:
                    parts.append(" ")
            else:
                parts.append(child)

    walk(node)
    return _collapse(_clean_line(_collapse("".join(parts)), rules))


def _collapse(text: str) -> str:
    """Clock times stripped, each whitespace run one space, the ends stripped."""
    return _SPACE_RUN.sub(" ", _BOARD_CLOCK.sub(" ", text)).strip()


def _with_body(rows: list[list[str]], body: list[bool]) -> list[list[str]] | None:
    """The rows when at least one is a body row with a non-empty data cell; else ``None`` (a
    header-only skeleton, or a table whose data cells are all empty)."""
    return rows if rows and any(body) else None


def _board_cells(nodes: Sequence[Any], rules: Any) -> list[list[str]] | None:
    """The cell contents of every table row in ``nodes`` (header and body cells, ``<tr>`` with
    ``<th>``/``<td>``, or ARIA rows and cells), row by row, as ``_cell_text`` hashes them.
    Captions and the copy around a table are never read. ``None`` when ``nodes`` hold no table
    row, or no body row with a non-empty data cell (a placeholder or a header-only skeleton).
    A body row is a ``<tbody>`` row or, in a table with no ``<tbody>``, a row outside its
    ``<thead>``: a ``<td>`` in a ``<thead>`` never makes a body. A ``<tfoot>`` row is never
    hashed."""

    def role(e: Any) -> str:
        return e.attrs.get("role", "").lower()

    def cells_of(row: Any) -> list[Any]:
        return [c for c in row.elements()
                if (c.tag in ("td", "th") or role(c) in _CELL_ROLES)
                and next((a for a in _ancestors(c) if a.tag == "tr" or role(a) in _ROW_ROLES),
                         None) is row]

    def section(row: Any, tag: str) -> bool:
        """The row sits in a ``tag`` section of its own table."""
        for up in _ancestors(row):
            if up.tag == tag:
                return True
            if up.tag == "table":
                return False
        return False

    def body_row(row: Any) -> bool:
        table = next((a for a in _ancestors(row) if a.tag == "table"), None)
        has_body = table is not None and any(
            e.tag == "tbody" and next((a for a in _ancestors(e) if a.tag == "table"), None)
            is table for e in table.elements())
        return section(row, "tbody") if has_body else not section(row, "thead")

    found = [e for n in nodes for e in (n, *n.elements())
             if e.tag == "tr" or role(e) in _ROW_ROLES]
    out, body = [], []
    for row in dict.fromkeys(found):
        if section(row, "tfoot"):
            continue
        cells = cells_of(row)
        texts = [_cell_text(c, rules) for c in cells]
        if any(texts):
            out.append(texts)
            body.append(body_row(row) and any(
                t and (c.tag == "td" or role(c) in _DATA_CELL_ROLES)
                for c, t in zip(cells, texts, strict=True)))
    return _with_body(out, body)


def _pipe_cells(line: str) -> list[str] | None:
    """The cells of a pipe-table line, or ``None`` for a line with no pipe."""
    line = line.strip()
    return line.strip("|").split("|") if "|" in line else None


def _text_rows(text: str, rules: Any) -> list[list[str]] | None:
    """The table rows of a plain-text board: the first pipe table (``| a | b |``) whose header
    line is followed by a separator line (``_PIPE_RULE``: ``|---|---|``, two columns or more),
    then its body lines up to the first line that is not a table line; only body rows with the
    header's column count are hashed. Cells are cleaned and collapsed as ``_cell_text`` does.
    Prose is never hashed, pipes or not: ``None`` when the text holds no such table with a
    non-empty body row. ``text`` is the page's own text, lines intact (the normaliser drops a
    separator line as punctuation)."""
    from decision.normalise import _clean_line

    lines = text.splitlines()
    for i in range(len(lines) - 1):
        header = _pipe_cells(lines[i])
        if header is None or not _PIPE_RULE.match(lines[i + 1]) or _PIPE_RULE.match(lines[i]):
            continue
        out = [[_collapse(_clean_line(c, rules)) for c in header]]
        for line in lines[i + 2:]:
            cells = _pipe_cells(line)
            if cells is None or _PIPE_RULE.match(line):
                break
            if len(cells) != len(header):
                continue  # only rows with the header's column count are hashed
            texts = [_collapse(_clean_line(c, rules)) for c in cells]
            if any(texts):
                out.append(texts)
        return _with_body(out, [k > 0 for k in range(len(out))])
    return None


def board_region_sha256(row: Mapping[str, Any], source_id: str, source: Mapping[str, Any],
                        page_bytes: bytes) -> str | None:
    """The hash of the regions of ``source_id`` the board row cites, or ``None`` when any of
    them cannot be selected: no registered region, an unknown normaliser or locator, content the
    normaliser refuses, a locator that matches nothing (a renamed table id), or a region with no
    board rows (a placeholder). ``None`` never opens an epoch: the gate refuses and the row stays
    in its epoch. The hash is shaped as the cited-region hash of engine#1171 (MODEL-562,
    ``decision.ruling_reread.region_sha256``): each region the row's source reference names (or
    every registered one), selected by the source's own locator, folded as rule 15 folds text.

    A board is hashed by its rows' cell contents only (MODEL-555 review): the header and body
    cells of every table row in the region (``<th>``/``<td>``, or ARIA rows and cells), never a
    caption or the copy around the table. An HTML page is parsed as HTML even under a text
    recipe; page furniture and anything that announces or rotates (banner, alert, status and
    live regions, carousels, tickers) is dropped; update times and clock times, with or without
    a zone, are stripped, and a cell's whitespace is removed (``_cell_text``). A region needs a
    body row with a non-empty data cell: an HTML region with no table row, or a header-only
    skeleton, is ``None``. A plain-text page (no markup) is hashed by its pipe-table rows only
    (``_text_rows``); prose is never hashed."""
    from decision.normalise import (
        NORMALISERS, Document, Locator, UnsupportedContentError, _nodes_text, normalise_document,
        select_region, select_region_tables,
    )

    ref = next((r for r in row.get("sources") or () if isinstance(r, Mapping)
                and r.get("source_id") == source_id), None)
    registered = {str(r.get("id")): r for r in source.get("cited_regions") or ()
                  if isinstance(r, Mapping)}
    wanted = [str(i) for i in (ref or {}).get("cited_regions") or ()] or sorted(registered)
    rules = NORMALISERS.get(str(source.get("normaliser") or "html-default"))
    if not wanted or rules is None or any(i not in registered for i in wanted):
        return None
    if rules.content == "text" and _HTML_LIKE.search(page_bytes):
        rules = NORMALISERS["html-default"]
    try:
        doc = normalise_document(page_bytes, rules)
        if doc.root is not None:
            _drop_board_volatile(doc.root)
            doc = Document(doc.rules, _nodes_text([doc.root], doc.rules), doc.root)
        parts = []
        for region_id in wanted:
            locator = registered[region_id].get("locator") or {}
            kind = str(locator.get("kind") or "page")
            kind = "heading" if kind == "heading_anchor" else kind
            where = Locator(kind, str(locator.get("value") or ""))
            if doc.root is not None:
                region: Any = _board_cells(_outermost(select_region_tables(doc, where)), doc.rules)
                if region is None and kind == "css":
                    # a CSS region on ARIA rows (no <table>): its matched nodes' rows
                    from decision.normalise import _matches, _parse_selector

                    steps = _parse_selector(where.value)
                    matched = [n for n in doc.root.elements() if _matches(n, steps)]
                    region = _board_cells(_outermost(matched), doc.rules) if matched else None
            elif kind == "page" and not where.value:
                # a text recipe on text with no markup: its pipe table's rows, never its prose,
                # read from the page's own lines (NFKC, newlines unified)
                raw = unicodedata.normalize("NFKC", page_bytes.decode("utf-8", "replace"))
                region = _text_rows(raw.replace("\r\n", "\n").replace("\r", "\n"), doc.rules)
            else:
                region = None  # a text page has no element to locate: nothing to hash
            if not region:
                return None
            parts.append([region_id, region])
    except (UnsupportedContentError, ValueError, TypeError):
        return None
    return sha256(json.dumps(parts, ensure_ascii=False, separators=(",", ":")))


def _row_sources(found: ReadingLookup, now: datetime) -> tuple[list[str], CitedChange | None]:
    """The row's registered cited sources, in source-id order: the stable set its board region
    is built on. A refusal when any of them is not registered or not eligible (the board
    owner's page on a cite-only host, ``_check_board_source``) at read time."""
    ids = sorted({str(s.get("source_id")) for s in found.row.get("sources") or ()
                  if isinstance(s, Mapping) and s.get("source_id")})
    for source_id in ids:
        refusal = _check_board_source(found, source_id, now)
        if refusal is not None:
            return ids, refusal
    return ids, None


def row_region_sha256(found: ReadingLookup, now: datetime, *, chosen: str,
                      page_bytes: bytes) -> str | None:
    """The board region of the row, not of one source (MODEL-555 review): the hash of every
    source the row cites (``_row_sources``, a stable set), in source-id order, with its
    cited-region hash. The chosen source's page is the one just fetched; every other is fetched
    here, by the gate, with its own transport. ``None`` when any of them is not eligible, cannot
    be read or cannot be hashed: no epoch can open, and the gate refuses."""
    ids, refusal = _row_sources(found, now)
    if refusal is not None or chosen not in ids:
        return None
    parts = []
    for source_id in ids:
        body = page_bytes
        if source_id != chosen:
            fetched = _fetch(found.sources[source_id]["url"], _http_once)
            if isinstance(fetched, CitedChange):
                return None
            body = fetched[0]
        region = board_region_sha256(found.row, source_id, found.sources[source_id], body)
        if region is None:
            return None
        parts.append([source_id, region])
    return sha256(json.dumps(parts, ensure_ascii=False, separators=(",", ":")))


def _reading_lines(subject: str, facet_id: str) -> list[dict[str, Any]]:
    """Every logged attempt at the subject and facet, in every epoch, in file order. Raises
    ``ValueError`` on a line that does not parse and ``OSError`` when the log cannot be read."""
    import os

    from decision.cited_reader import ATTEMPTS_FILE

    root = os.environ.get(DATA_DIR_ENV, "").strip()
    path = Path(root) / ATTEMPTS_FILE if root else None
    if path is None or not path.is_file():
        return []
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            entry = json.loads(line)
            if not isinstance(entry, dict):
                raise ValueError("an attempt line is not an object")
            if (entry.get("subject"), entry.get("facet")) == (subject, facet_id):
                out.append(entry)
    return out


def _board_epochs(lines: Sequence[Mapping[str, Any]], base: str) -> list[dict[str, Any]]:
    """The attempts logged in any board epoch of the settings epoch ``base``."""
    return [dict(e) for e in lines if isinstance(e.get("epoch"), str)
            and e["epoch"].startswith(base + BOARD_MARK)
            and len(e["epoch"]) > len(base + BOARD_MARK)]


_HEX64 = re.compile(r"[0-9a-f]{64}")


def is_board_epoch(epoch: Any, base: str) -> str | None:
    """The region hash a board epoch of ``base`` names, or ``None`` if ``epoch`` is not one."""
    prefix = base + BOARD_MARK
    rest = epoch[len(prefix):] if isinstance(epoch, str) and epoch.startswith(prefix) else ""
    return rest if _HEX64.fullmatch(rest) else None


def board_epoch(*, base: str, lines: Sequence[Mapping[str, Any]], region: str | None) -> str:
    """The epoch an unchanged board row is read in (MODEL-555). ``base`` is the row's settings
    epoch, ``lines`` every logged attempt at the subject and facet, ``region`` the row's board
    region (``row_region_sha256``) from pages the gate fetched itself.

    It fails closed: the row stays in ``base``, where its disagreements block, when no region
    can be computed, or when any complete attempt in ``base`` has no recorded region hash (an
    attempt logged before region hashes, or through a caller's transport: its region cannot be
    shown, so no change can be shown against it) or recorded this region. Otherwise the epoch is
    ``<base>:board:<region>``: re-reading the same board, or one that changed only outside its
    cited region, lands in the same board epoch, so a disagreement there blocks it; a changed
    cited region opens a new one."""
    if region is None or not _HEX64.fullmatch(region):
        return base
    for entry in lines:
        if entry.get("epoch") != base or entry.get("complete") is not True:
            continue
        logged = entry.get("board_region_sha256")
        if not (isinstance(logged, str) and _HEX64.fullmatch(logged)) or logged == region:
            return base
    return f"{base}{BOARD_MARK}{region}"


def _front(path: Path) -> dict[str, Any]:
    front = load_yaml_unique(path.read_text(encoding="utf-8").split("---", 2)[1])
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
        from decision.board_ruling import read_publishers

        publishers = read_publishers(root)  # the one reading the build's owner check shares
        name = front["display_name"]
        rows = [r for r in front["benchmarks"]["evidence"] if r.get("benchmark_id") == benchmark_id]
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
    ids = [s.get("source_id") for r in rows for s in r.get("sources") or []]
    ids += [i for r in rows for i in r.get("checked_sources") or []]
    ids += [i for r in rows for i in (_block_of(r) or {}).get("previous_sources") or []]
    listed = {str(x.get("url")) for x in benchmark.get("sources") or [] if isinstance(x, dict)}
    listed.add(str(benchmark.get("leaderboard_url") or ""))
    lab = subject.split("/", 1)[0]
    unowned = [i for i, src in sources.items() if src.get("url") in listed
               and src.get("kind") in FIRST_PARTY_KINDS and not src.get("publisher")]
    if unowned:  # a lab's page with no recorded publisher cannot be ruled out as the lab's own
        return _refuse("registry_lookup_failed",
                       f"page-listed source {unowned[0]} records no publisher")
    # A page-listed source counts when it is a board author's page or the subject's own lab's
    # (the lab's system card about this model); other labs' sources are not this reading's.
    page = tuple(i for i, src in sources.items()
                 if src.get("url") in listed
                 and (src.get("kind") == BENCHMARK_AUTHOR or src.get("publisher") == lab))
    # The reading's identity in the verification log (MODEL-547): the build keys a row's
    # verdicts by its stored id, which changes with its score and date, so the reading also
    # owns every id logged under its model and benchmark that no other current row has.
    models = tuple(dict.fromkeys(m for m in (subject, front.get("model_id"))
                                 if isinstance(m, str) and m))
    siblings = frozenset(str(r["id"]) for r in rows if r is not hits[0] and r.get("id"))
    own_id = (str(hits[0]["id"]),) if hits[0].get("id") else ()
    model_id = front.get("model_id") if isinstance(front.get("model_id"), str) \
        and front.get("model_id") else subject
    return ReadingLookup(name, hits[0], benchmark, sources, redirects, publishers,
                         tuple(dict.fromkeys(ids)), page, own_id,
                         tuple(f"{m}#{benchmark_id}#" for m in models), siblings - set(own_id),
                         model_id)


def _reading_held(found: ReadingLookup, data_dir: str | Path | None = None
                  ) -> list[tuple[tuple[str, str, str], dict[str, Any]]]:
    """The verdicts that hold the reading, by the one predicate the build applies too
    (``quarantine_clearing.reading_held``): on its own id (any value), or on an earlier id under
    the card's model id whose verdict's queue claim shows the same reading. A sibling row never
    takes a verdict over, nor is it held by another reading's verdict. Raises ``LookupFailed``
    when the log or the queue cannot be read."""
    import os

    from decision.owner_ruling import read_json_lines
    from decision.quarantine_clearing import (
        QUEUE_FILE,
        queue_history,
        reading_candidates,
        reading_held,
    )
    from decision.snapshot import _Compiler

    root = Path(data_dir or os.environ.get(DATA_DIR_ENV, "").strip() or ".")
    try:
        latest = _Compiler._verification_log(read_json_lines(root / VERIFICATION_LOG))
        own = str(found.row.get("id") or "")
        earlier = {key[1] for key, _ in reading_candidates(latest, found.row,
                                                           model_id=found.model_id)
                   if key[1] != own}
        history = queue_history(root / QUEUE_FILE, earlier) if earlier else {}
        return reading_held(latest, found.row, model_id=found.model_id, history=history)
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as error:
        raise LookupFailed(f"verification log or queue: {type(error).__name__}") from None


@dataclass(frozen=True)
class RuledRow:
    """A board row that claims an owner ruling (MODEL-569), as the gate finds it. ``line`` is the
    one ruling line for its block's key (``None``: none), ``attempts`` the attempt log,
    ``reopened`` the sweep's recorded ``(target, epoch)`` pairs, ``standing`` whether the build
    would admit the row on it (``board_ruling.row_problem``) and ``superseded`` the recorded
    reopened epoch an agreement superseded it in (``board_ruling.superseding_epoch``)."""

    line: Mapping[str, Any] | None
    attempts: list[dict[str, Any]]
    reopened: frozenset[tuple[str, str]]
    standing: bool
    superseded: str | None


def ruled_row(found: ReadingLookup, subject: str, *, held: Sequence[Any] = (),
              data_dir: str | Path | None = None) -> RuledRow | None:
    """The row's ``RuledRow``, or ``None`` for a row that claims no ruling. A log or record that
    cannot be read stands nothing and supersedes nothing."""
    import os

    from decision.board_ruling import row_problem, ruling_line, superseding_epoch
    from decision.cited_reader import ATTEMPTS_FILE
    from decision.owner_ruling import RULINGS_FILE, has_ruling, read_lines
    from decision.ruling_reread import Records

    if not has_ruling(found.row):
        return None
    root = Path(data_dir or os.environ.get(DATA_DIR_ENV, "").strip() or ".")
    urls = {str(k): str(v.get("url")) for k, v in found.sources.items()
            if isinstance(v, Mapping) and v.get("url")}
    try:
        rulings, logged = read_lines(root / RULINGS_FILE), read_lines(root / ATTEMPTS_FILE)
        reopened = frozenset(Records.read(root).reopened)
    except (OSError, ValueError):
        return RuledRow(None, [], frozenset(), False, None)
    max_score = (found.benchmark.get("metric") or {}).get("max_score")
    line = ruling_line(found.row, subject, rulings)
    standing = line is not None and row_problem(
        found.row, subject, rulings=rulings, attempts=logged, sources=urls, max_score=max_score,
        held=held, registry=board_registry(found), reopened=reopened) is None
    superseded = superseding_epoch(line, logged, reopened) if line is not None else None
    return RuledRow(line, logged, reopened, standing, superseded)


def standing_row_ruling(found: ReadingLookup, subject: str, *, held: Sequence[Any] = (),
                        data_dir: str | Path | None = None
                        ) -> tuple[Mapping[str, Any], list[dict[str, Any]],
                                   frozenset[tuple[str, str]]] | None:
    """``(ruling line, attempt log, recorded reopenings)`` when the build would admit the row on
    its ruling (MODEL-569), else ``None``."""
    got = ruled_row(found, subject, held=held, data_dir=data_dir)
    if got is None or not got.standing or got.line is None:
        return None
    return got.line, got.attempts, got.reopened


def _host(url: Any) -> str | None:
    from urllib.parse import urlsplit

    try:
        host = (urlsplit(str(url)).hostname or "").lower().rstrip(".")
    except ValueError:
        return None
    return host.removeprefix("www.") or None


def _check_board_source(found: ReadingLookup, source_id: str, now: datetime) -> CitedChange | None:
    """The source is the board's own publisher's page, on a cite-only host."""
    if source_id not in {s.get("source_id") for s in found.row.get("sources") or []}:
        return _refuse("registry_lookup_failed", "the reading's evidence does not cite this source")
    row = found.sources.get(source_id)
    if row is None or not row.get("url"):
        return _refuse("registry_lookup_failed", "the cited source is not in the source registry")
    status = cite_only_origin_status(row["url"], ())
    if status is None:
        return _refuse("host_unreadable", "the source URL does not parse")
    if not status:
        return _refuse("host_not_cite_only", "the host retains copies, so the verified path applies")
    # The board owner's page: the one check the filer and the build make too (MODEL-569).
    problem = owner_problem(board_registry(found), str(found.row.get("benchmark_id")), source_id)
    return None if problem is None else _refuse(*problem)


def board_registry(found: ReadingLookup):
    """The gate's own lookup as a ``board_ruling.BoardRegistry``, keyed by the row's benchmark."""
    from decision.board_ruling import BoardRegistry

    return BoardRegistry(found.sources, found.publishers,
                         {str(found.row.get("benchmark_id")): found.benchmark.get("owner_id")})


def owner_problem(registry: Any, benchmark_id: str, source_id: str) -> tuple[str, str] | None:
    from decision.board_ruling import owner_problem as shared

    return shared(registry, benchmark_id, source_id)


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
    """The attempt's time, or ``None`` when it is missing, unparseable or has no zone."""
    try:
        at = datetime.fromisoformat(str(entry.get("at")))
    except ValueError:
        return None
    return at if at.tzinfo is not None else None


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
                  allow_unchanged: bool = False, clear_quarantine: bool = False) -> CitedChange:
    """The gate for one board reading: fetch the board in memory, have two readers read the one
    row, and return their agreed score as ``cited``, an absence (pending or, on the second read
    at least 24 h later, marked), or a named refusal. Everything but the readers and the
    transport is looked up here. The clock is the gate's own: it cannot be injected.
    ``allow_unchanged`` returns a record for an agreed score equal to the filed one, to give a
    row written before the record existed its ``derivation``. ``clear_quarantine`` (MODEL-552)
    lets a fresh agreement on a score clear the reading's one held mismatch, read in that
    verdict's clearing epoch; the record then carries ``clearings`` (``cited_change``).

    A row with no cited change is read in the board epoch its pages name (MODEL-555,
    ``board_epoch``): the gate fetches the board itself first, and the epoch is the settings
    epoch, or ``<settings epoch>:board:<row region hash>`` (``row_region_sha256``) when nothing
    in the settings epoch holds the row there. Only bytes the gate fetched with its own transport
    name a board epoch; with a caller's ``request`` the row is read in its settings epoch and a
    disagreement in any of its board epochs blocks too. A clearing extends the epoch the row is
    in now."""
    now = datetime.now(UTC)
    if now.tzinfo is None or now > datetime.now(UTC):
        return _refuse("bad_read_date", "the read time is missing, naive or in the future")
    found = reading_lookup(subject, benchmark_id, reading)
    if isinstance(found, CitedChange):
        return found
    facet_id = BENCHMARK_PREFIX + benchmark_id
    # Up front, before any read or attempt (MODEL-547): the fact gate's predicate, for evidence.
    try:
        held = _reading_held(found)
    except LookupFailed as error:
        return _refuse("registry_lookup_failed", str(error))
    holding_any = list(held)  # a ruling stands on a row nothing holds, released or not (MODEL-569)
    released, chains = False, []
    if held:  # as for a fact (MODEL-566): a released verdict holds the row no more
        # A clearing line's target must be one of the ids that hold this row, as in the build.
        holding = frozenset(key[1] for key, _ in held)
        got = _unreleased(held, found.row, subject, now=now, sources=found.sources,
                          owns=holding.__contains__)
        if isinstance(got, CitedChange):
            return got
        held, chains = got
        released = bool(chains)
    clearing = None
    if held:
        refusal, clearing = _clearing_target(held, found.row, now, allowed=clear_quarantine,
                                             kind="evidence")
        if refusal is not None:
            return refusal
    refusal = _check_board_source(found, source_id, now) \
        or _check_retaining(found.lookup(found.own), _ReadingFacet(facet_id, _EveryKind()), now) \
        or _check_retaining(found.lookup(found.cited), _ReadingFacet(facet_id, _EveryKind()), now)
    if refusal is None:
        refusal = _check_identities(readers)
    if refusal is not None:
        return refusal
    epoch = base = reading_epoch(reading, found.row)
    url = found.sources[source_id]["url"]
    unchanged = _block_of(found.row) is None
    fetched: tuple[bytes, tuple[str, ...]] | CitedChange | None = None
    region: str | None = None
    try:
        lines = _reading_lines(subject, facet_id) if unchanged else []
    except (OSError, ValueError) as error:
        return _refuse("registry_lookup_failed", f"the attempt log: {type(error).__name__}")
    current = base
    ruled = ruled_row(found, subject, held=holding_any)
    if ruled is not None:
        # MODEL-569: a ruled row is read in its ruled epoch, where the disagreement blocks, unless
        # the gate fetched every page the row cites itself and the row's board region is a
        # reopened epoch of the ruling that the sweep recorded (MODEL-562's rule for facts). A
        # ruling that no longer stands is read only in the recorded reopened epoch that
        # superseded it: never its base or board epoch, never from bytes a caller supplies.
        from decision.board_ruling import gate_epoch as ruled_reading_epoch

        if not ruled.standing and ruled.superseded is None:
            return _refuse("epoch_not_current", "the row's ruling does not stand and no recorded "
                           "reopened epoch superseded it; the row is not read")
        if request is not None and not ruled.standing:
            return _refuse("epoch_not_current", "a superseded ruling's row is read only from "
                           "pages the gate fetches itself")
        if request is None:
            _ids, refusal = _row_sources(found, now)
            if refusal is not None:
                return refusal
            fetched = _fetch(url, _http_once)
            if isinstance(fetched, CitedChange):
                return fetched
            region = row_region_sha256(found, now, chosen=source_id, page_bytes=fetched[0])
            if region is None:
                return _refuse("page_unreadable", "the board's cited region cannot be selected on "
                               "every page the row cites; the row stays in its ruled epoch")
        current = ruled.superseded if not ruled.standing else ruled_reading_epoch(
            ruled.line, ruled.attempts, region, ruled.reopened)
        lines = []
    elif unchanged and request is None:
        # MODEL-555: an unchanged row's epoch names the row's board region, so the gate fetches
        # the page first, itself, with its own transport, and every other eligible source the
        # row cites (``row_region_sha256``). Only these bytes can name a board epoch.
        # The epoch rests on the row's registered cited sources, a stable set: one that is not
        # eligible now, or a region that cannot be selected (a renamed table, a placeholder),
        # refuses, and the row stays in its epoch. It never opens one.
        _ids, refusal = _row_sources(found, now)
        if refusal is not None:
            return refusal
        fetched = _fetch(url, _http_once)
        if isinstance(fetched, CitedChange):
            return fetched
        region = row_region_sha256(found, now, chosen=source_id, page_bytes=fetched[0])
        if region is None:
            return _refuse("page_unreadable", "the board's cited region cannot be selected on "
                           "every page the row cites; the row stays in its epoch")
        current = board_epoch(base=base, lines=lines, region=region)
    # Outside a board epoch the gate named itself (a caller's transport, or a row its settings
    # epoch holds), every board epoch's attempts count for disagreement too.
    boards = [a for a in _board_epochs(lines, base) if a.get("complete")] \
        if current == base else []
    epoch = current
    if clearing is not None:
        from decision.quarantine_clearing import clearing_epoch, verdict_sha256

        from decision.quarantine_clearing import reading_settings

        # A clearing extends the epoch the row is in now: after a genuine board update, the
        # board epoch the gate named, so a split under an older board region does not block it
        # (and the build counts the same two epochs, ``quarantine_clearing.line_problem``).
        epoch = clearing_epoch(current, verdict_sha256(clearing[1]))
        refusal = _epoch_at_verdict(clearing[1], subject=subject, facet=facet_id,
                                    first=reading_epoch(reading), base=current,
                                    settings=reading_settings({**found.row, **reading}))
        if refusal is not None:
            return refusal
    history = [a for a in attempts(subject, facet_id, epoch) if a.get("complete")]
    if clearing is not None:
        history += [a for a in attempts(subject, facet_id, current) if a.get("complete")]
    base = current
    # What blocks: this epoch's attempts and, outside a board epoch, every board epoch's.
    blocking = history + boards
    if any(_entry_time(a) is None for a in blocking):
        return _refuse("bad_read_date", "a logged attempt has a missing, naive or unreadable time")
    if any(not a.get("agreed") for a in blocking):
        return _refuse("prior_attempt_disagreed",
                       "an earlier complete attempt at this reading did not agree")
    if released and clearing is None:
        # The re-read of a released row counts every answer recorded in its epoch, an answer
        # inside an incomplete attempt too (MODEL-566 review), as the fact gate does and the
        # build's ``epoch_problem`` does: two that differ block.
        recorded = attempts(subject, facet_id, epoch)
        answered = {canonical(v, facet_id) for v in _incomplete_values(recorded)} | {
            canonical(a.get("agreed_value"), facet_id) for a in recorded if a.get("complete")}
        if len(answered) > 1:
            return _refuse("prior_attempt_disagreed",
                           "answers recorded in earlier attempts at this reading do not agree")
    if fetched is None:
        fetched = _fetch(url, request or _http_once)
    if isinstance(fetched, CitedChange):
        return fetched
    page_bytes, resolved = fetched
    if released and clearing is None:
        refusal = _relitigates(chains, page_bytes, first=reading_epoch(reading), epoch=epoch,
                               now=now,
                               own_fetch=request is None)
        if refusal is not None:
            return refusal
    definition = reading_definition(found.benchmark, reading)
    answers: list[ReaderAnswer] = []
    for _ in range(2):
        try:
            answers = read_page(subject=subject, url=url, facet_id=facet_id,
                                subject_name=found.subject_name, page_bytes=page_bytes,
                                readers=readers, epoch=epoch, definition=definition,
                                board_region_sha256=region)
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
    if released and clearing is None:
        refusal = _not_a_link(chains, subject=subject, facet=facet_id,
                              first=reading_epoch(reading), epoch=epoch)
        if refusal is not None:
            return refusal
    mark = {"subject": subject, "benchmark_id": benchmark_id,
            "reading": {k: reading[k] for k in READING_KEYS}}
    if value is None and clearing is not None:
        return _refuse("no_value", "the readers agree the board lists no such row; an absence "
                       "clears no quarantine")
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
    # A prior agreed attempt on another value is a conflict signal, as in the fact gate.
    if any(a.get("agreed") and a.get("agreed_value") is not None
           and canonical(a.get("agreed_value"), facet.id) != canonical(value, facet.id)
           for a in blocking):
        return _refuse("prior_attempt_disagreed", "an earlier agreed attempt returned another value")
    filed = found.row.get("score")
    marked = found.row.get("not_published_since") not in (None, "")
    if canonical(value, facet.id) == canonical(filed, facet.id) and not marked \
            and not allow_unchanged and clearing is None:
        return _refuse("value_unchanged", "the agreed value is the filed value")
    record = _record(subject, facet_id, value, found.sources[source_id], source_id, now,
                     sha256(page_bytes), text_sha256(page_bytes), answers, filed, found.own, resolved)
    record["benchmark_id"] = benchmark_id
    record["reading"] = mark["reading"]
    record["clears_not_published_since"] = found.row.get("not_published_since") not in (None, "")
    del record["facet"]
    outcome = CitedChange("cited_change", None, "", record)
    if clearing is not None:
        return _with_clearing(outcome, clearing, subject=subject, facet=facet_id, epoch=epoch,
                              base=base, answers=answers, now=now)
    return outcome


# --- the re-read ---------------------------------------------------------------------------------


def cited_change_block(fact: Mapping[str, Any]) -> Mapping[str, Any] | None:
    """The ``cited_change`` block of a fact (in its ``derivation``), or ``None``."""
    derivation = fact.get("derivation") if isinstance(fact, Mapping) else None
    block = derivation.get("cited_change") if isinstance(derivation, Mapping) else None
    return block if isinstance(block, Mapping) else None


def fact_epoch(fact: Mapping[str, Any]) -> str:
    """The attempt-log epoch a fact is in: after a cited change, the re-read epoch its recorded
    text hash names; otherwise ``initial``. ``reread`` reads in this epoch."""
    block = cited_change_block(fact)
    if block is None:
        return "initial"
    text = block.get('text_sha256') or block.get('sha256')
    cleared = block.get("clearing_epoch")
    # A block a quarantine clearing made (MODEL-566) is re-read in an epoch named by its
    # clearing epoch: never one a read before the clearing used, so a later clearing's base
    # epoch is never the epoch the record is re-read in after it.
    return f"{cleared}:reread:{text}" if isinstance(cleared, str) and cleared \
        else f"reread:{text}"


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
    """Every fact in the data directory's cards and offering files that carries a
    ``cited_change`` block.

    Each entry has ``subject``, ``facet``, ``value``, ``derivation`` and ``source_id``.
    """
    out: list[dict[str, Any]] = []
    for path in sorted((Path(data_dir) / "models").glob("*/*.md")):
        try:
            front = load_yaml_unique(path.read_text("utf-8").split("---", 2)[1])
            facts = front.get("facts") or []
        except (OSError, IndexError, AttributeError, yaml.YAMLError):
            continue
        for fact in facts:
            if isinstance(fact, dict) and cited_change_block(fact) is not None:
                sources = fact.get("sources") or [{}]
                out.append({"subject": f"{path.parent.name}/{path.stem}", "facet": fact.get("facet"),
                            "value": fact.get("value"), "derivation": fact.get("derivation"),
                            "source_id": sources[0].get("source_id")})
    for path in sorted((Path(data_dir) / "offerings").rglob("*.yaml")):
        try:
            rows = load_yaml_unique(path.read_text("utf-8")) or []
            facts = [f for row in rows for f in row.get("facts") or []]
        except (OSError, AttributeError, TypeError, yaml.YAMLError):
            continue
        for fact in facts:
            if isinstance(fact, dict) and cited_change_block(fact) is not None:
                sources = fact.get("sources") or [{}]
                out.append({"subject": (fact.get("subject") or {}).get("id"),
                            "facet": fact.get("facet"), "value": fact.get("value"),
                            "derivation": fact.get("derivation"),
                            "source_id": sources[0].get("source_id")})
    return out


def cited_change_readings(data_dir: str | Path) -> list[dict[str, Any]]:
    """Every benchmark reading in the data directory's cards that carries a ``cited_change``
    block, shaped like ``cited_change_facts`` entries, with the reading's settings and a
    ``target`` that is unique per reading."""
    out: list[dict[str, Any]] = []
    for path in sorted((Path(data_dir) / "models").glob("*/*.md")):
        try:
            front = load_yaml_unique(path.read_text("utf-8").split("---", 2)[1])
            rows = (front.get("benchmarks") or {}).get("evidence") or []
        except (OSError, IndexError, AttributeError, yaml.YAMLError):
            continue
        for row in rows:
            if isinstance(row, dict) and cited_change_block(row) is not None:
                subject = f"{path.parent.name}/{path.stem}"
                reading = {k: row.get(k) for k in READING_KEYS}
                facet = BENCHMARK_PREFIX + str(row.get("benchmark_id"))
                sources = row.get("sources") or [{}]
                out.append({"subject": subject, "facet": facet, "value": row.get("score"),
                            "derivation": row.get("derivation"), "reading": reading,
                            "source_id": sources[0].get("source_id"),
                            "target": f"{subject}#{facet}#{reading_epoch(reading)}"})
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
    readers; fewer flags the fact. Each recorded sha256 is its own attempt-log epoch. Only the
    subject and facet are taken from ``fact``; the block and the epoch are the filed fact's."""
    subject, facet = str(fact.get("subject")), str(fact.get("facet"))
    try:
        found = lookup(subject, facet)
    except LookupFailed as error:
        return Reread("flagged", "registry_lookup_failed", None, str(error))
    row = found.sources.get(source_id)
    if row is None or not row.get("url"):
        return Reread("flagged", "registry_lookup_failed", None, "the cited source is not registered")
    from decision.owner_ruling import has_ruling

    if has_ruling(found.fact):
        return _reread_ruled(found, subject, facet, source_id, readers, request)
    # The block, and with it the epoch, are the filed fact's own, never the caller's.
    block = cited_change_block(found.fact)
    if block is None:
        return Reread("flagged", "not_a_cited_change", None, "the filed fact carries no block")
    from decision.retained_correction import RULE as CORRECTION_RULE

    # A correction's block (MODEL-573) is re-read on the retaining gate too, and re-filed as a
    # correction: its value rests on an agreement, not on a verification.
    retaining = block.get("rule") in {RETAINED_RULE, CORRECTION_RULE}
    fetched = _fetch(row["url"], request or _http_once, retaining=retaining)
    if isinstance(fetched, CitedChange):
        return Reread("flagged", fetched.reason, None, fetched.detail)
    if not reread_required(found.fact, fetched[0]):
        return Reread("current")
    outcome = _gate(subject=subject, facet=facet, source_id=source_id, readers=readers,
                    request=request, allow_unchanged=True, page=fetched, retaining=retaining,
                    own_page=request is None, correct=block.get("rule") == CORRECTION_RULE,
                    accept_not_disclosed=not retaining
                    and found.fact.get("state") == "not_disclosed")
    if not outcome.changed:
        return Reread("flagged", outcome.reason, None, outcome.detail)
    facet_def = _facet(facet)
    agreed = outcome.record["value"] if outcome.record else None
    same = _canonical(agreed, facet_def) == _canonical(found.fact.get("value"), facet_def)
    return Reread("confirmed" if same else "changed", None, outcome.record)


def _reread_ruled(found: Lookup, subject: str, facet: str, source_id: str,
                  readers: Sequence[Reader], request: Request | None) -> Reread:
    """``reread`` of an owner-ruled fact (MODEL-562). The page is compared with what the ruling's
    resolved disagreement read (``decision.ruling_reread.page_status``), never with the cited-change block
    the fact kept: a page back at the text before the ruling is not ``current``. ``current``
    only for the ruled page or a change outside the cited region; otherwise the gate decides,
    reading the page itself, in the epoch that page names."""
    import os

    from decision.cited_reader import ATTEMPTS_FILE
    from decision.owner_ruling import read_lines
    from decision.ruling_reread import Records, _inputs, page_status, standing_ruling

    row = found.sources[source_id]
    fetched = _fetch(row["url"], request or _http_once)
    if isinstance(fetched, CitedChange):
        return Reread("flagged", fetched.reason, None, fetched.detail)
    root = Path(os.environ.get(DATA_DIR_ENV, "").strip() or ".")
    urls = {str(k): str(v.get("url")) for k, v in found.sources.items()
            if isinstance(v, Mapping) and v.get("url")}
    try:
        ruling = standing_ruling(found.fact, subject, inputs=_inputs(root), sources=urls)
        status = None if ruling is None else page_status(
            found.fact, subject, ruling=ruling, source_id=source_id, row=row,
            page_bytes=fetched[0], attempts=read_lines(root / ATTEMPTS_FILE),
            records=Records.read(root))
    except (OSError, ValueError, KeyError, TypeError) as error:
        return Reread("flagged", "registry_lookup_failed", None, type(error).__name__)
    if status is not None and status.kind == "current":
        return Reread("current")
    outcome = _gate(subject=subject, facet=facet, source_id=source_id, readers=readers,
                    request=request, allow_unchanged=True,
                    accept_not_disclosed=found.fact.get("state") == "not_disclosed")
    if not outcome.changed:
        return Reread("flagged", outcome.reason, None,
                      outcome.detail or (status.kind if status else "no standing ruling"))
    agreed = outcome.record["value"] if outcome.record else None
    same = _canonical(agreed, _facet(facet)) == _canonical(found.fact.get("value"), _facet(facet))
    return Reread("confirmed" if same else "changed", None, outcome.record)


def reread_reading(*, subject: str, benchmark_id: str, reading: Mapping[str, Any], source_id: str,
                   readers: Sequence[Reader], request: Request | None = None) -> Reread:
    """Re-read a board reading that a cited change filed. The gate fetches the page; a page
    whose visible text still hashes as recorded is ``current``. Otherwise two readers read it
    again in the epoch the recorded text hash names, so a board that moved can change the row
    again while a disagreement inside one epoch still blocks. A reading whose score the readers
    confirm is ``confirmed``; another agreed score is ``changed``; anything else is ``flagged``."""
    found = reading_lookup(subject, benchmark_id, reading)
    if isinstance(found, CitedChange):
        return Reread("flagged", found.reason, None, found.detail)
    from decision.owner_ruling import has_ruling

    if has_ruling(found.row):
        return _reread_ruled_reading(found, subject=subject, benchmark_id=benchmark_id,
                                     reading=reading, source_id=source_id, readers=readers,
                                     request=request)
    block = _block_of(found.row)
    if block is None:
        return Reread("flagged", "not_a_cited_change", None, "the row carries no cited_change block")
    row = found.sources.get(source_id)
    if row is None or not row.get("url"):
        return Reread("flagged", "registry_lookup_failed", None, "the cited source is not registered")
    fetched = _fetch(row["url"], request or _http_once)
    if isinstance(fetched, CitedChange):
        return Reread("flagged", fetched.reason, None, fetched.detail)
    if not reread_required({"derivation": found.row["derivation"]}, fetched[0]):
        return Reread("current")
    outcome = cited_reading(subject=subject, benchmark_id=benchmark_id, reading=reading,
                            source_id=source_id, readers=readers, request=request,
                            allow_unchanged=True)
    if outcome.outcome != "cited_change" and not outcome.marked:
        return Reread("flagged", outcome.reason or outcome.outcome, None, outcome.detail)
    if outcome.marked:
        return Reread("flagged", "not_published", outcome.record, "the board no longer lists the row")
    same = canonical(outcome.record["value"], "_") == canonical(found.row.get("score"), "_")
    return Reread("confirmed" if same else "changed", None, outcome.record)


@dataclass(frozen=True)
class RuledRowStatus:
    """What the board shows for an owner-ruled row (MODEL-569). ``kind``: ``current`` (the ruled
    region), ``changed`` (another region, not recorded yet: the sweep records it), ``open`` (a
    reopened epoch the sweep recorded), ``unbaselined`` (the resolved attempts logged no region),
    ``unreadable_region``, ``deferred`` (a page could not be fetched) or ``invalid`` (no ruling
    the build admits). Hashes only."""

    kind: str
    line: Mapping[str, Any] | None = None
    region: str | None = None
    baseline: str | None = None
    epoch: str | None = None


def ruled_row_status(found: ReadingLookup, subject: str, *, source_id: str,
                     request: Request | None = None,
                     data_dir: str | Path | None = None) -> RuledRowStatus:
    """The one comparison the sweep and ``reread_reading`` make for a ruled row, from pages the
    gate module fetches (``request`` only for the chosen page in tests; every other page with the
    gate's own transport). No byte is kept."""
    from decision.board_ruling import baseline, recorded_reopen
    from decision.ruling_reread import reopen_epoch

    try:
        held = _reading_held(found, data_dir)
    except LookupFailed:
        return RuledRowStatus("invalid")
    standing = standing_row_ruling(found, subject, held=held, data_dir=data_dir)
    if standing is None:
        return RuledRowStatus("invalid")
    line, logged, reopened = standing
    now = datetime.now(UTC)
    _ids, refusal = _row_sources(found, now)
    if refusal is not None or source_id not in found.sources:
        return RuledRowStatus("invalid", line)
    fetched = _fetch(found.sources[source_id]["url"], request or _http_once)
    if isinstance(fetched, CitedChange):
        return RuledRowStatus("deferred", line)
    region = row_region_sha256(found, now, chosen=source_id, page_bytes=fetched[0])
    if region is None:
        return RuledRowStatus("unreadable_region", line)
    known = baseline(line, logged)
    if known is None:
        return RuledRowStatus("unbaselined", line, region)
    if region == known:
        return RuledRowStatus("current", line, region, known)
    epoch = reopen_epoch(str(line["epoch"]), region)
    kind = "open" if recorded_reopen(line, logged, region, reopened) == epoch else "changed"
    return RuledRowStatus(kind, line, region, known, epoch)


def _reread_ruled_reading(found: ReadingLookup, *, subject: str, benchmark_id: str,
                          reading: Mapping[str, Any], source_id: str, readers: Sequence[Reader],
                          request: Request | None) -> Reread:
    """``reread_reading`` of an owner-ruled row (MODEL-569). ``current`` while the board region is
    the ruled one (or no change can be shown); once the sweep recorded the reopened epoch the board
    names, the gate decides, fetching the board itself: two agreeing readers supersede the
    ruling."""
    status = ruled_row_status(found, subject, source_id=source_id, request=request).kind
    if status in {"current", "unbaselined"}:
        return Reread("current")
    if status != "open":
        # ``changed``: the sweep has not recorded the reopened epoch yet, so the gate would read
        # the row in its ruled epoch; nothing is read until it does.
        return Reread("flagged", status, None, "the ruled row's board reopened no recorded epoch")
    outcome = cited_reading(subject=subject, benchmark_id=benchmark_id, reading=reading,
                            source_id=source_id, readers=readers, request=None,
                            allow_unchanged=True)
    if outcome.outcome != "cited_change" and not outcome.marked:
        return Reread("flagged", outcome.reason or outcome.outcome, None, outcome.detail)
    if outcome.marked:
        return Reread("flagged", "not_published", outcome.record,
                      "the board no longer lists the row")
    same = canonical(outcome.record["value"], "_") == canonical(found.row.get("score"), "_")
    return Reread("confirmed" if same else "changed", None, outcome.record)


def ruled_readings(data_dir: str | Path) -> list[dict[str, Any]]:
    """Every board reading in the data directory's cards that claims an owner ruling (MODEL-569),
    as ``{"subject", "benchmark_id", "reading", "source_ids", "target"}``."""
    from decision.owner_ruling import has_ruling, ruling_block

    out: list[dict[str, Any]] = []
    for path in sorted((Path(data_dir) / "models").glob("*/*.md")):
        try:
            front = load_yaml_unique(path.read_text("utf-8").split("---", 2)[1])
            rows = (front.get("benchmarks") or {}).get("evidence") or []
        except (OSError, IndexError, AttributeError, yaml.YAMLError):
            continue
        for row in rows:
            if isinstance(row, dict) and has_ruling(row):
                subject = f"{path.parent.name}/{path.stem}"
                reading = {k: row.get(k) for k in READING_KEYS}
                facet = BENCHMARK_PREFIX + str(row.get("benchmark_id"))
                ids = (ruling_block(row) or {}).get("source_ids")
                out.append({"subject": subject, "benchmark_id": row.get("benchmark_id"),
                            "reading": reading,
                            "source_ids": [str(i) for i in ids] if isinstance(ids, list) else [],
                            "target": f"{subject}#{facet}#{reading_epoch(reading)}"})
    return out
