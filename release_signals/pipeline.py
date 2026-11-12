"""Resolve a release signal, gather allowed sources, and draft a model card."""

from __future__ import annotations

import json
import os
import re
from collections.abc import Callable, Mapping
from contextlib import nullcontext
from dataclasses import dataclass
from datetime import date
from html.parser import HTMLParser
from pathlib import Path
from typing import Literal
from urllib.parse import urlencode, urlsplit

import yaml

from decision.excluded import excluded_sources
from decision.sources import CopyStore, FetchResult as SourceFetchResult, load_sources
from schema.card import ModelCard
from scripts import attribution
from scripts.refresh_leaderboards import check_score_only
from scripts.seed_huggingface import slugify
from scripts.seed_models_dev import PROVIDER_MAP, load_known_identities

MODELS_DEV_URL = "https://models.dev/api.json"
PRIMARY_URL_FIELDS = ("release_url", "homepage", "url")
SUPPORTING_URL_FIELDS = (
    "documentation_url", "docs_url", "api_docs_url", "model_card_url",
    "huggingface_url", "repository_url",
)
SIGNAL_ONLY_HOSTS = frozenset({"x.com", "twitter.com", "t.co"})
IDENTITY_FIELDS = frozenset({
    "model_id", "display_name", "provider", "provider_display", "family", "version",
    "release_date", "last_updated", "status", "model_type", "model_subtypes", "tags",
    "pipeline_tag",
})


class IdentityUncertainError(ValueError):
    """The gathered sources do not establish one model and lab identity."""


class ModelsDevNotListed(Exception):
    """models.dev has no provider row, or no model row, for this signal."""

    def __init__(self, kind: str) -> None:
        self.kind = kind
        super().__init__(f"models.dev not_listed: {kind}")


class RequiredSourceError(Exception):
    """A mandatory source body cannot be read. The pending signal stays queued.

    This is not a ValueError. A prohibited-source refusal stays a ValueError
    and must not be reported as a retryable source outage.
    """

    def __init__(self, url: str, detail: str) -> None:
        self.url = url
        limit = 500
        shown_url = url.replace("\r", " ").replace("\n", " ")
        if len(shown_url) > 300:
            shown_url = shown_url[:300] + "..."
        flat = detail.replace("\r", " ").replace("\n", " ")
        prefix = f"required source {shown_url} failed: "
        super().__init__((prefix + flat)[:limit])


@dataclass(frozen=True)
class FetchResult:
    url: str
    body: bytes
    content_type: str


@dataclass(frozen=True)
class Resolution:
    status: Literal["existing", "new", "uncertain"]
    model_id: str | None
    candidates: tuple[str, ...] = ()
    reason: str = ""


@dataclass(frozen=True)
class DraftResult:
    resolution: Resolution
    card_path: Path | None
    evidence_urls: tuple[str, ...]
    firecrawl_credits: int = 0
    gather_failures: tuple[str, ...] = ()
    offering_path: Path | None = None
    price_gaps: tuple[dict, ...] = ()
    price_sources: tuple[dict, ...] = ()
    models_dev: str = ""
    primary_host: str = ""
    primary_kind: str = ""
    identity_basis: str = ""


@dataclass(frozen=True)
class GatherResult:
    resolution: Resolution
    display_name: str = ""
    release_date: str = ""
    provider_id: str = ""
    primary_url: str = ""
    supporting_urls: tuple[str, ...] = ()
    evidence_urls: tuple[str, ...] = ()
    gather_failures: tuple[str, ...] = ()
    models_dev: str = ""
    primary_kind: str = ""
    identity_basis: str = ""
    preferred_first_seen: bool = False


@dataclass(frozen=True)
class ChangeDecision:
    merge: Literal["human", "auto"]
    labels: tuple[str, ...]
    score_only: bool
    reasons: tuple[str, ...]
    changed: bool


class FirecrawlBudget:
    """A per-run budget that cannot exceed the MODEL-113 cap."""

    def __init__(self, cap: int = 20) -> None:
        if not 0 <= cap <= 20:
            raise ValueError("the Firecrawl cap must be between 0 and 20 credits")
        self.cap = cap
        self.spent = 0

    def charge(self, credits: int) -> None:
        if credits < 0 or self.spent + credits > self.cap:
            raise RuntimeError(f"Firecrawl credit cap exceeded ({self.spent + credits}>{self.cap})")
        self.spent += credits


def _front(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    parts = text.split("---", 2)
    loaded = yaml.safe_load(parts[1] if len(parts) >= 3 else text) or {}
    return loaded if isinstance(loaded, dict) else {}


# One card scan and one organisation map per catalogue root for this process.
_SLUG_INDEX: dict[Path, dict[str, frozenset[str]]] = {}
_HF_ORG_INDEX: dict[Path, dict[str, frozenset[str]]] = {}


def clear_catalogue_cache() -> None:
    """Drop the card index and the Hugging Face organisation map."""
    _SLUG_INDEX.clear()
    _HF_ORG_INDEX.clear()


def _slug_index(models_dir: Path) -> dict[str, frozenset[str]]:
    """Normalised provider key to the lab slugs written on those cards."""
    key = models_dir.resolve()
    cached = _SLUG_INDEX.get(key)
    if cached is not None:
        return cached
    index: dict[str, set[str]] = {}
    if models_dir.is_dir():
        for path in sorted(models_dir.glob("*/*.md")):
            front = _front(path)
            provider = str(front.get("provider") or path.parent.name)
            display = str(front.get("provider_display") or "")
            for name in {
                attribution.normalise(provider),
                attribution.normalise(display),
                attribution.normalise(path.parent.name),
            }:
                index.setdefault(name, set()).add(provider)
    frozen = {name: frozenset(slugs) for name, slugs in index.items()}
    _SLUG_INDEX[key] = frozen
    return frozen


def _provider_slugs(signal_provider: str, models_dir: Path) -> tuple[str, ...]:
    wanted = attribution.normalise(signal_provider)
    return tuple(sorted(_slug_index(models_dir).get(wanted, ())))


def _catalogue_matches(
    signal_provider: str, provider: str, wanted: str, root: Path,
) -> list[str]:
    """Card ids whose exact alias normalises to `wanted`."""
    matches: list[str] = []
    known_path = root / "scripts" / "models_dev_known_identities.yaml"
    if known_path.is_file():
        known = load_known_identities(known_path)
        for listed, canonical in known.items():
            listed_provider, separator, listed_name = listed.partition("/")
            canonical_path = (root / "models" / canonical).with_suffix(".md")
            if (
                separator
                and attribution.normalise(listed_provider) in {
                    attribution.normalise(provider),
                    attribution.normalise(signal_provider),
                }
                and attribution.normalise(listed_name) == wanted
                and canonical_path.is_file()
            ):
                matches.append(canonical)
    for path in sorted((root / "models" / provider).glob("*.md")):
        front = _front(path)
        model_id = str(front.get("model_id") or "")
        aliases = {
            attribution.normalise(str(front.get("display_name") or "")),
            attribution.normalise(str(front.get("version") or "")),
            attribution.normalise(model_id.rsplit("/", 1)[-1]),
            attribution.normalise(path.stem),
        }
        if wanted in aliases:
            matches.append(model_id)
    return sorted(set(matches))


def resolve_signal(signal, root: Path) -> Resolution:
    """Resolve only exact aliases. Ambiguity stays explicit."""
    models_dir = root / "models"
    providers = _provider_slugs(signal.provider, models_dir)
    if len(providers) != 1:
        return Resolution(
            "uncertain", None, providers,
            "the provider does not resolve to exactly one catalogue lab",
        )
    provider = providers[0]
    wanted = attribution.normalise(signal.model_name)
    matches = _catalogue_matches(signal.provider, provider, wanted, root)
    if len(matches) == 1:
        return Resolution("existing", matches[0], tuple(matches), "exact catalogue alias")
    if len(matches) > 1:
        return Resolution("uncertain", None, tuple(matches), "more than one exact alias matched")
    model_id = f"{provider}/{slugify(signal.model_name)}"
    return Resolution("new", model_id, (), "no exact catalogue alias matched")


def _absolute_https_url(value: object) -> str | None:
    """An absolute https URL with a host, or None when the value is not one."""
    if not isinstance(value, str):
        return None
    try:
        parsed = urlsplit(value)
    except ValueError:
        return None
    if parsed.scheme != "https" or not parsed.hostname:
        return None
    return value


def _page_host(url: str) -> str:
    """Host of an https URL, without a leading www. Empty when the URL is not https."""
    try:
        parsed = urlsplit(url)
    except ValueError:
        return ""
    if parsed.scheme != "https" or not parsed.hostname:
        return ""
    return parsed.hostname.casefold().removeprefix("www.")


def _host_is(host: str, names: frozenset[str]) -> bool:
    """Exact host, or a subdomain when the registry entry is written `*.parent`."""
    for name in names:
        if name.startswith("*."):
            parent = name[2:]
            if parent and host.endswith("." + parent):
                return True
        elif host == name:
            return True
    return False


def _signal_lab_hosts(root: Path, signal, resolution: Resolution) -> frozenset[str]:
    """Hosts for the signal's provider text and for the resolved catalogue lab."""
    hosts = set(registered_lab_hosts(root, signal.provider))
    model_id = resolution.model_id or ""
    lab, separator, _rest = model_id.partition("/")
    if separator and lab:
        hosts.update(registered_lab_hosts(root, lab))
    return frozenset(hosts)


def registered_lab_hosts(root: Path, provider: str) -> frozenset[str]:
    """Hosts registered for this lab in code or in this root's watch file.

    The watch file is read only when ``root/registry/release-watch.yaml`` exists.
    A test root with no watch file does not inherit the repository watch list.
    """
    from scripts.admission_drafter import LAB_HOSTS

    wanted = attribution.normalise(provider)
    hosts: set[str] = set()
    for slug, names in LAB_HOSTS.items():
        if attribution.normalise(slug) != wanted:
            continue
        for name in names:
            host = name.casefold().removeprefix("www.")
            if host:
                hosts.add(host)
    watch = root / "registry" / "release-watch.yaml"
    if not watch.is_file():
        return frozenset(hosts)
    loaded = yaml.safe_load(watch.read_text(encoding="utf-8")) or {}
    sources = loaded.get("sources") if isinstance(loaded, Mapping) else None
    if not isinstance(sources, list):
        return frozenset(hosts)
    for source in sources:
        if not isinstance(source, Mapping) or str(source.get("kind") or "") != "page":
            continue
        if attribution.normalise(str(source.get("provider") or "")) != wanted:
            continue
        host = _page_host(str(source.get("url") or ""))
        if host:
            hosts.add(host)
    return frozenset(hosts)


_HUGGINGFACE_NON_REPOS = frozenset({"spaces", "datasets"})
_HF_REPO_SEGMENT = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*\Z")


def registered_huggingface_orgs(root: Path, provider: str) -> frozenset[str]:
    """Hugging Face orgs whose watch source names this lab. Casefolded.

    The source provider matches this name, or it resolves to this lab slug
    the way ``resolve_signal`` resolves a provider. Read only from
    ``kind: huggingface`` rows. The host ``huggingface.co`` is not added to
    the lab host set. A test root with no watch file has none.
    """
    return _huggingface_org_index(root).get(attribution.normalise(provider), frozenset())


def _huggingface_org_index(root: Path) -> dict[str, frozenset[str]]:
    """Normalised lab name to the Hugging Face orgs registered for it."""
    key = root.resolve()
    cached = _HF_ORG_INDEX.get(key)
    if cached is not None:
        return cached
    built: dict[str, set[str]] = {}
    watch = root / "registry" / "release-watch.yaml"
    if watch.is_file():
        loaded = yaml.safe_load(watch.read_text(encoding="utf-8")) or {}
        sources = loaded.get("sources") if isinstance(loaded, Mapping) else None
        if isinstance(sources, list):
            slugs = _slug_index(root / "models")
            for source in sources:
                if not isinstance(source, Mapping) or str(source.get("kind") or "") != "huggingface":
                    continue
                org = str(source.get("org") or "").strip().casefold()
                if not org:
                    continue
                source_provider = str(source.get("provider") or "")
                names = {attribution.normalise(source_provider)}
                resolved = slugs.get(attribution.normalise(source_provider), frozenset())
                if len(resolved) == 1:
                    names.add(attribution.normalise(next(iter(resolved))))
                for name in names:
                    built.setdefault(name, set()).add(org)
    frozen = {name: frozenset(orgs) for name, orgs in built.items()}
    _HF_ORG_INDEX[key] = frozen
    return frozen


def _signal_hf_orgs(root: Path, signal, resolution: Resolution) -> frozenset[str]:
    """Orgs for the signal's provider text and for the resolved catalogue lab."""
    orgs = set(registered_huggingface_orgs(root, signal.provider))
    model_id = resolution.model_id or ""
    lab, separator, _rest = model_id.partition("/")
    if separator and lab:
        orgs.update(registered_huggingface_orgs(root, lab))
    return frozenset(orgs)


def _huggingface_org_repo(url: str, orgs: frozenset[str]) -> tuple[str, str] | None:
    """``(org, repo)`` when ``url`` is that lab's own model repository.

    The path is exactly ``/<org>/<repo>``. One trailing slash is allowed.
    Each segment matches ``[A-Za-z0-9][A-Za-z0-9._-]*``. An empty segment,
    a percent sign anywhere in the path, or any further segment is not the
    lab's page. The query and the fragment are ignored. ``spaces`` and
    ``datasets`` are not model repositories.
    """
    if not orgs or _page_host(url) != "huggingface.co":
        return None
    try:
        path = urlsplit(url).path
    except ValueError:
        return None
    if "%" in path or not path.startswith("/"):
        return None
    parts = path.split("/")
    if parts[-1] == "":
        parts = parts[:-1]
    if len(parts) != 3 or parts[0] != "":
        return None
    org, repo = parts[1], parts[2]
    if (
        _HF_REPO_SEGMENT.fullmatch(org) is None
        or _HF_REPO_SEGMENT.fullmatch(repo) is None
        or org.casefold() in _HUGGINGFACE_NON_REPOS
        or org.casefold() not in orgs
    ):
        return None
    return org, repo


def _accepted_page_kind(url: str, lab_hosts: frozenset[str], hf_orgs: frozenset[str]) -> str:
    """Lab host class, or ``huggingface-org`` when only the org repository matches.

    Cite-only, excluded and signal-only hosts stay in that class. A retention
    rule that already forbids ``huggingface.co`` is not overridden.
    """
    kind = first_seen_host_class(url, lab_hosts)
    if kind == "unregistered" and _huggingface_org_repo(url, hf_orgs):
        return "huggingface-org"
    return kind


def first_seen_host_class(url: str, lab_hosts: frozenset[str]) -> str:
    """Classify a first-seen URL. ``lab`` wins over cite-only for a registered lab host."""
    from decision.retention import cite_only_hosts

    host = _page_host(url)
    if not host:
        return "invalid"
    if any(host == blocked or host.endswith(f".{blocked}") for blocked in SIGNAL_ONLY_HOSTS):
        return "signal-only"
    if excluded_sources().url(url):
        return "excluded"
    if _host_is(host, lab_hosts):
        return "lab"
    if _host_is(host, frozenset(cite_only_hosts())):
        return "cite-only"
    return "unregistered"


def require_allowed_source(url: str) -> str:
    parsed = urlsplit(url)
    if parsed.scheme not in {"http", "https"}:
        raise ValueError(f"source is not an HTTP URL: {url}")
    host = (parsed.hostname or "").casefold().removeprefix("www.")
    if any(host == blocked or host.endswith(f".{blocked}") for blocked in SIGNAL_ONLY_HOSTS):
        raise ValueError(f"signal-only source cannot be card evidence: {url}")
    if excluded_sources().url(url):
        raise ValueError(f"excluded source: {url}")
    return url


def _fetch_allowed(fetch: Callable[[str], FetchResult], url: str) -> FetchResult:
    """Validate both the requested URL and the final URL after redirects."""
    requested = require_allowed_source(url)
    response = fetch(requested)
    require_allowed_source(response.url)
    return response


def _models_dev_listing(
    payload: object, provider: str, model_name: str, *, source_url: str,
) -> tuple[str, dict, str | None]:
    if not isinstance(payload, Mapping):
        raise RequiredSourceError(source_url, "models.dev returned no provider map")
    wanted_provider = attribution.normalise(provider)
    provider_rows: list[tuple[object, Mapping]] = []
    for key, value in payload.items():
        if isinstance(value, Mapping):
            row: Mapping = value
        elif not value:
            row = {}
        else:
            raise RequiredSourceError(source_url, "models.dev provider row is not an object")
        row_name = attribution.normalise(str(row.get("name", "")))
        if attribution.normalise(str(key)) == wanted_provider or row_name == wanted_provider:
            provider_rows.append((key, row))
    if len(provider_rows) == 0:
        raise ModelsDevNotListed("provider")
    if len(provider_rows) != 1:
        raise IdentityUncertainError("models.dev did not identify exactly one provider")
    provider_id, provider_row = provider_rows[0]
    models = provider_row.get("models")
    if not isinstance(models, Mapping):
        raise RequiredSourceError(source_url, "models.dev provider row has no models map")
    wanted = attribution.normalise(model_name)
    matches = [
        dict(raw) for key, raw in models.items()
        if isinstance(raw, Mapping)
        and wanted in {
            attribution.normalise(str(key)),
            attribution.normalise(str(raw.get("id", ""))),
            attribution.normalise(str(raw.get("name", ""))),
        }
    ]
    if len(matches) == 0:
        raise ModelsDevNotListed("model")
    if len(matches) != 1:
        raise IdentityUncertainError(
            "models.dev did not identify exactly one model listing"
        )
    listing = matches[0]
    doc = provider_row.get("doc")
    provider_doc = None
    if doc and "api_docs_url" not in listing:
        listing["api_docs_url"] = doc
        provider_doc = doc
    return str(provider_id), listing, provider_doc


_JSON_LD_MAX_DEPTH = 64
_JSON_LD_MAX_INTEGER_DIGITS = 1000


def _json_ld_unreadable(text: str) -> bool:
    """True when nesting is deeper than the bound, or an integer is too long.

    Depth rises on ``{`` and ``[`` and falls on ``}`` and ``]``, outside
    strings. It does not go below zero. Brackets inside strings, including
    after an escaped quote, do not move it.
    """
    depth = 0
    digits = 0
    in_string = False
    escape = False
    for char in text:
        if in_string:
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
            digits = 0
            continue
        if char in "{[":
            depth += 1
            digits = 0
            if depth > _JSON_LD_MAX_DEPTH:
                return True
            continue
        if char in "}]":
            if depth:
                depth -= 1
            digits = 0
            continue
        if char.isdigit():
            digits += 1
            if digits > _JSON_LD_MAX_INTEGER_DIGITS:
                return True
            continue
        digits = 0
    return False


class _JsonLd(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.capture = False
        self.buffer: list[str] = []
        self.documents: list[dict] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key.casefold(): (value or "") for key, value in attrs}
        self.capture = tag.casefold() == "script" and values.get("type") == "application/ld+json"
        self.buffer = [] if self.capture else self.buffer

    def handle_data(self, data: str) -> None:
        if self.capture:
            self.buffer.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag.casefold() != "script" or not self.capture:
            return
        self.capture = False
        raw = "".join(self.buffer)
        if _json_ld_unreadable(raw):
            return
        try:
            value = json.loads(raw)
        except Exception:
            return
        values = value if isinstance(value, list) else [value]
        self.documents.extend(item for item in values if isinstance(item, dict))


class _VisibleText(HTMLParser):
    _BLOCK_TAGS = {
        "address", "article", "aside", "blockquote", "br", "div", "footer",
        "h1", "h2", "h3", "h4", "h5", "h6", "header", "li", "main", "nav",
        "ol", "p", "section", "table", "td", "th", "tr", "ul",
    }

    def __init__(self) -> None:
        super().__init__()
        self.hidden = 0
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.casefold()
        if tag in {"script", "style"}:
            self.hidden += 1
        elif not self.hidden and tag in self._BLOCK_TAGS:
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        tag = tag.casefold()
        if tag in {"script", "style"} and self.hidden:
            self.hidden -= 1
        elif not self.hidden and tag in self._BLOCK_TAGS:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        if not self.hidden:
            self.parts.append(data)


def _contains_name(text: str, name: str) -> bool:
    """True when the normalised model name is a hyphen-bounded token in the text."""
    haystack = attribution.normalise(text)
    needle = attribution.normalise(name)
    if not needle:
        return False
    return re.search(rf"(^|-){re.escape(needle)}(-|$)", haystack) is not None


def _primary_identity(
    page: FetchResult,
    expected_name: str,
    expected_provider: str,
    lab_hosts: frozenset[str] = frozenset(),
    hf_orgs: frozenset[str] = frozenset(),
) -> tuple[str, str, str]:
    repo = _huggingface_org_repo(page.url, hf_orgs)
    if repo is not None:
        if attribution.normalise(repo[1]) == attribution.normalise(expected_name):
            return expected_name, "", "repo-name"
        raise IdentityUncertainError(
            "the primary source does not identify the stated lab"
        )
    parser = _JsonLd()
    html = page.body.decode("utf-8", errors="replace")
    parser.feed(html)
    matches = [
        row for row in parser.documents
        if attribution.normalise(str(row.get("name", "")))
        == attribution.normalise(expected_name)
    ]
    if not matches:
        visible = _VisibleText()
        visible.feed(html)
        text = "".join(visible.parts)
        normalised_name = attribution.normalise(expected_name)
        normalised_provider = attribution.normalise(expected_provider)
        clauses = [
            clause.strip()
            for clause in re.split(r"[!?;:\n]+|\.(?=\s|$)", text)
            if clause.strip()
        ]
        explicit_publishers = re.findall(
            rf"\b{re.escape(expected_name)}\s+by\s+([^.!?;:\n]+)",
            text,
            flags=re.IGNORECASE,
        )
        if any(
            attribution.normalise(publisher) != normalised_provider
            for publisher in explicit_publishers
        ):
            raise IdentityUncertainError(
                "the primary source does not identify the stated lab"
            )
        publishers: set[str] = set()
        for clause in clauses:
            announcement = re.fullmatch(
                r"(.+?)\s+(?:announces|introduces|launches|releases)\s+(.+)",
                clause, flags=re.IGNORECASE,
            )
            credit = re.fullmatch(r"(.+?)\s+by\s+(.+)", clause, flags=re.IGNORECASE)
            if announcement:
                provider, name = announcement.groups()
            elif credit:
                name, provider = credit.groups()
            else:
                continue
            if attribution.normalise(name) == normalised_name:
                publishers.add(attribution.normalise(provider))
        if publishers == {normalised_provider}:
            return expected_name, "", "page-text"
        if publishers:
            raise IdentityUncertainError(
                "the primary source does not identify the stated lab"
            )
        host = _page_host(page.url)
        if host and _host_is(host, lab_hosts) and _contains_name(text, expected_name):
            return expected_name, "", "page-text"
        raise IdentityUncertainError(
            "the primary source does not identify the stated lab"
        )
    if len(matches) != 1:
        raise IdentityUncertainError(
            "the primary source identifies more than one matching model"
        )
    row = matches[0]
    publisher = row.get("publisher") or {}
    publisher_name = publisher.get("name") if isinstance(publisher, Mapping) else publisher
    if attribution.normalise(str(publisher_name or "")) != attribution.normalise(expected_provider):
        raise IdentityUncertainError(
            "the primary source does not identify the stated lab"
        )
    published = str(row.get("datePublished") or "")
    if published:
        try:
            date.fromisoformat(published)
        except ValueError as exc:
            raise RequiredSourceError(page.url, f"unusable datePublished: {exc}") from exc
    return str(row["name"]).strip(), published, "json-ld"


def _attribution_result(
    *, root: Path, payload: Mapping, provider_id: str, listing: Mapping,
) -> attribution.Attribution | None:
    """Run the existing models.dev attribution cascade when its registry is present."""
    config_path = root / "scripts" / "attribution.yaml"
    if not config_path.is_file():
        return None
    config = attribution.load_config(config_path)
    registry = attribution.load_registry(root / "models", PROVIDER_MAP)
    page_orgs = {
        page: row["slug"] for page, row in PROVIDER_MAP.items() if row["slug"] in registry
    }
    row = attribution.Listing(
        platform=provider_id,
        platform_name=str((payload.get(provider_id) or {}).get("name") or provider_id),
        listed_id=str(listing.get("id") or ""),
        name=str(listing.get("name") or ""),
        family=str(listing.get("family") or ""),
    )
    evidence = attribution.gather_evidence(
        row,
        attribution.ListingIndex.build(dict(payload), config),
        config,
        registry,
        page_orgs,
    )
    if attribution.supplier_conflict(evidence):
        decided = attribution.decide_deterministically(evidence, registry)
        if decided is None:
            raise IdentityUncertainError(
                "supplier attribution needs a person; the judgment is refused"
            )
        return decided
    return attribution.decide_deterministically(evidence, registry)


def _huggingface_repo(
    *, fetch: Callable[[str], FetchResult], model_name: str, provider: str,
) -> tuple[str, str | None]:
    search_url = "https://huggingface.co/api/models?" + urlencode({
        "search": model_name, "limit": 20,
    })
    try:
        payload = json.loads(_fetch_allowed(fetch, search_url).body)
        if not isinstance(payload, list) or any(not isinstance(row, Mapping) for row in payload):
            raise ValueError("expected a list of repository objects")
    except Exception as exc:  # the optional source never blocks a provider-backed card
        return "", f"Hugging Face search failed: {type(exc).__name__}: {exc}"
    wanted_model = attribution.normalise(model_name)
    wanted_provider = attribution.normalise(provider)
    matches = []
    for row in payload:
        model_id = str(row.get("id") or row.get("modelId") or "")
        author, separator, name = model_id.partition("/")
        if (
            separator
            and attribution.normalise(name) == wanted_model
            and attribution.normalise(author) == wanted_provider
        ):
            matches.append(model_id)
    if len(matches) != 1:
        return "", None
    repo_url = require_allowed_source(f"https://huggingface.co/{matches[0]}")
    try:
        _fetch_allowed(fetch, repo_url)
    except Exception as exc:
        return "", f"Hugging Face repository failed: {type(exc).__name__}: {exc}"
    return repo_url, None


def _load_required_json(page: FetchResult) -> object:
    """Read one mandatory JSON body, naming that source when the bytes are unusable."""
    try:
        return json.loads(page.body)
    except (ValueError, RecursionError) as exc:
        raise RequiredSourceError(page.url, f"{type(exc).__name__}: {exc}") from exc


def _gather_unlisted(
    signal,
    resolution: Resolution,
    *,
    root: Path,
    fetch: Callable[[str], FetchResult],
    models_dev_url: str,
    discover_huggingface: bool,
) -> GatherResult:
    """Use the signal's own first-seen page when models.dev has no row.

    The page is fetched when its host is a registered lab host, or when it is
    that lab's own Hugging Face repository. The fetch result's URL is the page
    after redirects. It is classified again, and the final host is the one
    recorded. Any other host class stays uncertain. A cite-only Hugging Face
    host is not fetched.
    """
    lab_hosts = _signal_lab_hosts(root, signal, resolution)
    hf_orgs = _signal_hf_orgs(root, signal, resolution)
    kind = _accepted_page_kind(signal.first_seen_url, lab_hosts, hf_orgs)
    if kind not in {"lab", "huggingface-org"}:
        return GatherResult(Resolution(
            "uncertain", None, resolution.candidates,
            f"models.dev not_listed; host class {kind}",
        ))
    requested = require_allowed_source(signal.first_seen_url)
    primary = fetch(requested)
    final_kind = _accepted_page_kind(primary.url, lab_hosts, hf_orgs)
    if final_kind not in {"lab", "huggingface-org"}:
        return GatherResult(Resolution(
            "uncertain", None, resolution.candidates,
            f"models.dev not_listed; host class {final_kind}",
        ))
    require_allowed_source(primary.url)
    try:
        display_name, release_date, identity_basis = _primary_identity(
            primary, signal.model_name, signal.provider,
            lab_hosts=lab_hosts,
            hf_orgs=hf_orgs,
        )
    except IdentityUncertainError as exc:
        return GatherResult(Resolution(
            "uncertain", None, resolution.candidates, str(exc)
        ))
    failures: list[str] = []
    supporting: list[str] = []
    if discover_huggingface:
        huggingface_url, failure = _huggingface_repo(
            fetch=fetch,
            model_name=display_name,
            provider=resolution.model_id.split("/", 1)[0] if resolution.model_id else signal.provider,
        )
        if failure:
            failures.append(failure)
        if huggingface_url:
            supporting.append(huggingface_url)
    return GatherResult(
        resolution=resolution,
        display_name=display_name,
        release_date=release_date,
        provider_id="",
        primary_url=primary.url,
        supporting_urls=tuple(supporting),
        evidence_urls=tuple(dict.fromkeys((primary.url, *supporting))),
        gather_failures=tuple(failures),
        models_dev="not_listed",
        primary_kind="huggingface-org" if final_kind == "huggingface-org" else "",
        identity_basis=identity_basis,
    )


def gather_signal(
    signal,
    *,
    root: Path,
    fetch: Callable[[str], FetchResult],
    models_dev_url: str = MODELS_DEV_URL,
    discover_huggingface: bool = False,
) -> GatherResult:
    """Gather allowed primary sources for one resolved model identity."""
    resolution = resolve_signal(signal, root)
    if resolution.status == "uncertain" or resolution.model_id is None:
        return GatherResult(resolution)

    models_dev_url = require_allowed_source(models_dev_url)
    listing_response = _fetch_allowed(fetch, models_dev_url)
    models_dev_payload = _load_required_json(listing_response)
    try:
        provider_id, listing, provider_doc = _models_dev_listing(
            models_dev_payload, signal.provider, signal.model_name,
            source_url=listing_response.url,
        )
        attributed = _attribution_result(
            root=root, payload=models_dev_payload, provider_id=provider_id, listing=listing
        )
        if attributed and attributed.writes_creator \
                and attributed.creator != resolution.model_id.split("/", 1)[0]:
            raise IdentityUncertainError(
                f"signal names lab {signal.provider!r}, but the attribution cascade names "
                f"{attributed.creator!r}; identity is uncertain"
            )
    except ModelsDevNotListed as exc:
        # An existing card keeps its identity. A new signal may use its own lab page.
        if resolution.status == "existing":
            return GatherResult(Resolution(
                "uncertain", None, resolution.candidates, str(exc)
            ))
        return _gather_unlisted(
            signal, resolution, root=root, fetch=fetch,
            models_dev_url=models_dev_url, discover_huggingface=discover_huggingface,
        )
    except IdentityUncertainError as exc:
        # RequiredSourceError is not caught here, so a broken source stays pending.
        return GatherResult(Resolution(
            "uncertain", None, resolution.candidates, str(exc)
        ))
    lab_hosts = _signal_lab_hosts(root, signal, resolution)
    hf_orgs = _signal_hf_orgs(root, signal, resolution)
    primary_candidates = []
    for field in PRIMARY_URL_FIELDS:
        value = listing.get(field)
        if not value:
            continue
        if field == "release_url":
            value = _absolute_https_url(value)
            if value is None:
                continue
        primary_candidates.append(require_allowed_source(str(value)))
    primary_candidates = list(dict.fromkeys(primary_candidates))
    raw_supporting = list(dict.fromkeys(
        str(listing[field]) for field in SUPPORTING_URL_FIELDS if listing.get(field)
    ))
    first_seen_kind = _accepted_page_kind(signal.first_seen_url, lab_hosts, hf_orgs)
    preferred_first_seen = False
    if (
        not primary_candidates
        and provider_doc
        and raw_supporting[:1] == [str(provider_doc)]
        and first_seen_kind in {"lab", "huggingface-org"}
    ):
        primary_candidates = [require_allowed_source(signal.first_seen_url)]
        raw_supporting = [url for url in raw_supporting if url != str(provider_doc)]
        preferred_first_seen = True
    elif not primary_candidates:
        primary_candidates = [require_allowed_source(url) for url in raw_supporting]
    if not primary_candidates:
        raise ValueError("the listing does not name a primary provider source")
    primary_url = primary_candidates[0]
    failures: list[str] = []
    fallback_note = ""
    primary: FetchResult | None = None
    if preferred_first_seen:
        try:
            primary = _fetch_allowed(fetch, primary_url)
        except ValueError:
            # A prohibited host is a gate refusal, not a dead page.
            raise
        except Exception as exc:
            fallback_note = f"{_page_host(primary_url)}: {type(exc).__name__}"
            failures.append(fallback_note)
        else:
            final_kind = _accepted_page_kind(primary.url, lab_hosts, hf_orgs)
            if final_kind not in {"lab", "huggingface-org"}:
                fallback_note = f"host class {final_kind}"
                primary = None
            else:
                primary_url = primary.url
    else:
        primary = _fetch_allowed(fetch, primary_url)
    if primary is not None:
        try:
            display_name, release_date, identity_basis = _primary_identity(
                primary, signal.model_name, signal.provider,
                lab_hosts=lab_hosts,
                hf_orgs=hf_orgs,
            )
        except IdentityUncertainError as exc:
            if not preferred_first_seen:
                return GatherResult(Resolution(
                    "uncertain", None, resolution.candidates, str(exc)
                ))
            primary = None
    if primary is None:
        doc_url = require_allowed_source(str(provider_doc))
        try:
            primary = _fetch_allowed(fetch, doc_url)
        except ValueError:
            raise
        except Exception as exc:
            doc_failure = f"{_page_host(doc_url)}: {type(exc).__name__}"
            failures.append(doc_failure)
            reason = f"{fallback_note}; {doc_failure}" if fallback_note else doc_failure
            return GatherResult(
                Resolution("uncertain", None, resolution.candidates, reason),
                gather_failures=tuple(failures),
            )
        primary_url = doc_url
        try:
            display_name, release_date, identity_basis = _primary_identity(
                primary, signal.model_name, signal.provider,
                lab_hosts=lab_hosts,
                hf_orgs=hf_orgs,
            )
        except IdentityUncertainError as doc_exc:
            reason = f"{fallback_note}; {doc_exc}" if fallback_note else str(doc_exc)
            return GatherResult(
                Resolution("uncertain", None, resolution.candidates, reason),
                gather_failures=tuple(failures),
            )
        preferred_first_seen = False
        if str(provider_doc) not in raw_supporting:
            raw_supporting.append(str(provider_doc))
    supporting_urls = list(dict.fromkeys(
        require_allowed_source(url) for url in raw_supporting
    ))
    for url in supporting_urls:
        _fetch_allowed(fetch, url)

    huggingface_url = next((url for url in supporting_urls if "huggingface.co" in url), "")
    if discover_huggingface and not huggingface_url:
        huggingface_url, failure = _huggingface_repo(
            fetch=fetch, model_name=display_name, provider=resolution.model_id.split("/", 1)[0]
        )
        if failure:
            failures.append(failure)
        if huggingface_url:
            supporting_urls.append(huggingface_url)
    return GatherResult(
        resolution=resolution,
        display_name=display_name,
        release_date=release_date,
        provider_id=provider_id,
        primary_url=primary_url,
        supporting_urls=tuple(supporting_urls),
        evidence_urls=tuple(dict.fromkeys((primary_url, models_dev_url, *supporting_urls))),
        gather_failures=tuple(failures),
        primary_kind=(
            "huggingface-org"
            if _accepted_page_kind(primary_url, lab_hosts, hf_orgs) == "huggingface-org"
            else ""
        ),
        identity_basis=identity_basis,
        preferred_first_seen=preferred_first_seen,
    )


def update_existing_card(gathered: GatherResult, *, root: Path, read_date: date) -> Path:
    """Update primary-source metadata on one resolved card."""
    model_id = gathered.resolution.model_id
    if gathered.resolution.status != "existing" or model_id is None:
        raise ValueError("an existing resolved model is required")
    matches = [
        path for path in sorted((root / "models").glob("*/*.md"))
        if str(_front(path).get("model_id") or "") == model_id
    ]
    if len(matches) != 1:
        raise ValueError(f"existing card is not unique: {model_id}")
    path = matches[0]
    text = path.read_text(encoding="utf-8")
    parts = text.split("---", 2)
    if len(parts) != 3:
        raise ValueError(f"card has no YAML front matter: {path}")
    front = yaml.safe_load(parts[1]) or {}
    sources = dict(front.get("sources") or {})
    supporting = list(gathered.supporting_urls)
    huggingface_url = next((url for url in supporting if "huggingface.co" in url), "")
    api_docs_url = next((url for url in supporting if url != huggingface_url),
                        gathered.primary_url)
    accessed = read_date.isoformat()
    source_facts = {
        "models_dev_url": f"https://models.dev/{gathered.provider_id}",
    }
    if gathered.primary_kind == "huggingface-org":
        if not sources.get("huggingface_url"):
            filled = huggingface_url or gathered.primary_url
            if filled:
                source_facts["huggingface_url"] = filled
    elif gathered.preferred_first_seen and sources.get("provider_docs_url"):
        source_facts["provider_docs_url"] = sources["provider_docs_url"]
        if huggingface_url and not sources.get("huggingface_url"):
            source_facts["huggingface_url"] = huggingface_url
    else:
        source_facts["provider_docs_url"] = api_docs_url
        if huggingface_url:
            source_facts["huggingface_url"] = huggingface_url
    material_change = any(sources.get(key) != value for key, value in source_facts.items())
    if not material_change:
        return path

    sources.update(source_facts)
    sources.update({
        "last_scraped_models_dev": accessed,
    })
    if huggingface_url:
        sources["last_scraped_huggingface"] = accessed
    front["sources"] = sources
    front["card_updated"] = accessed
    content = "---\n" + yaml.dump(front, sort_keys=False, allow_unicode=True) + "---" + parts[2]
    ModelCard.from_yaml_string(content)
    path.write_text(content, encoding="utf-8")
    return path


class _PriceTransport:
    def __init__(self, fetch: Callable[[str], FetchResult]) -> None:
        self._fetch = fetch

    def fetch(self, url: str) -> SourceFetchResult:
        try:
            response = _fetch_allowed(self._fetch, url)
        except Exception as exc:
            return SourceFetchResult("unreachable", error=f"{type(exc).__name__}: {exc}")
        return SourceFetchResult(
            "ok", 200, body=response.body, content_type=response.content_type,
            resolved_urls=(response.url,),
        )


def draft_signal(
    signal,
    *,
    root: Path,
    fetch: Callable[[str], FetchResult],
    read_date: date,
    models_dev_url: str = MODELS_DEV_URL,
    firecrawl_budget: FirecrawlBudget | None = None,
    discover_huggingface: bool = False,
    price_fetcher=None,
    source_cache: Path | None = None,
) -> DraftResult:
    """Draft one new card. X is never fetched or written as a source."""
    gathered = gather_signal(
        signal,
        root=root,
        fetch=fetch,
        models_dev_url=models_dev_url,
        discover_huggingface=discover_huggingface,
    )
    resolution = gathered.resolution
    if resolution.status != "new" or resolution.model_id is None:
        return DraftResult(resolution, None, gathered.evidence_urls,
                           (firecrawl_budget or FirecrawlBudget()).spent,
                           gathered.gather_failures)

    provider, slug = resolution.model_id.split("/", 1)
    provider_display = signal.provider
    for existing in sorted((root / "models" / provider).glob("*.md")):
        provider_display = str(_front(existing).get("provider_display") or provider_display)
        break
    accessed = read_date.isoformat()
    display_name = gathered.display_name
    release_date = gathered.release_date
    primary_url = gathered.primary_url
    supporting_urls = list(gathered.supporting_urls)
    if gathered.primary_kind == "huggingface-org":
        huggingface_url = primary_url
        api_docs_url = ""
    else:
        huggingface_url = next((url for url in supporting_urls if "huggingface.co" in url), "")
        api_docs_url = next(
            (url for url in supporting_urls if url != huggingface_url), primary_url,
        )
    sources = {
        "models_dev_url": (
            f"https://models.dev/{gathered.provider_id}" if gathered.provider_id else ""
        ),
        "provider_docs_url": api_docs_url,
        "huggingface_url": huggingface_url,
        "last_scraped_pricing": "",
    }
    if gathered.models_dev != "not_listed":
        sources["last_scraped_models_dev"] = accessed
    front = {
        "model_id": resolution.model_id,
        "display_name": display_name,
        "provider": provider,
        "provider_display": provider_display,
        "release_date": release_date,
        "cost": {},
        "benchmarks": {"scores": {}, "evidence": []},
        "sources": sources,
        "card_schema_version": "3.0",
        "card_author": "release-signal-pipeline",
        "card_created": accessed,
        "card_updated": accessed,
    }
    prose = (
        f"# {display_name}\n\n"
        f"The provider source identifies this model by name. "
        f"Source: {primary_url} (read {accessed}).\n"
    )
    card_path = root / "models" / provider / f"{slug}.md"
    card_path.parent.mkdir(parents=True, exist_ok=True)
    card_path.write_text(
        "---\n" + yaml.dump(front, sort_keys=False, allow_unicode=True) + "---\n\n" + prose,
        encoding="utf-8",
    )
    ModelCard.from_yaml_file(card_path)
    from scripts.admission_drafter import load_source_terms
    from scripts.offering_drafter import draft_offering
    from scripts.offering_fetch import OfferingFetcher

    pricing = nullcontext(price_fetcher) if price_fetcher is not None else OfferingFetcher(
        _PriceTransport(fetch), lab=provider, terms=load_source_terms(root),
        sources=load_sources(root / "registry/sources.yaml"), renderer=False,
    )
    with pricing as pricing_fetcher:
        offering = draft_offering(
            root=root, model_id=resolution.model_id, fetcher=pricing_fetcher,
            store=CopyStore(source_cache or os.environ.get("MODELSPEC_SOURCE_CACHE")
                            or root / "source-copies"),
            today=read_date,
        )
        offering.write(root)
        price_report = offering.to_dict()
        price_credits = pricing_fetcher.credits_spent
    return DraftResult(
        resolution,
        card_path,
        gathered.evidence_urls,
        (firecrawl_budget or FirecrawlBudget()).spent + price_credits,
        gathered.gather_failures,
        root / offering.offering_path if offering.offering_path else None,
        tuple(price_report["gaps"]),
        tuple(price_report["sources"]),
        gathered.models_dev,
        _page_host(primary_url) if gathered.models_dev == "not_listed" else "",
        gathered.primary_kind if gathered.models_dev == "not_listed" else "",
        gathered.identity_basis,
    )


class ChangePolicy:
    """Classify generated changes before any pull request is opened."""

    @staticmethod
    def classify(before: Path, after: Path) -> ChangeDecision:
        before_files = {
            path.relative_to(before): path.read_bytes()
            for path in before.rglob("*") if path.is_file()
        }
        after_files = {
            path.relative_to(after): path.read_bytes()
            for path in after.rglob("*") if path.is_file()
        }
        if before_files == after_files:
            return ChangeDecision("auto", (), False, (), False)

        before_cards = {p.relative_to(before) for p in (before / "models").glob("*/*.md")} \
            if (before / "models").exists() else set()
        after_cards = {p.relative_to(after) for p in (after / "models").glob("*/*.md")} \
            if (after / "models").exists() else set()
        created = sorted(after_cards - before_cards)
        removed = sorted(before_cards - after_cards)
        reasons = [f"card created: {path.as_posix()}" for path in created]
        reasons.extend(f"card removed: {path.as_posix()}" for path in removed)

        for relative in sorted(before_cards & after_cards):
            old, new = _front(before / relative), _front(after / relative)
            if any(old.get(field) != new.get(field) for field in IDENTITY_FIELDS):
                reasons.append(f"identity changed: {relative.as_posix()}")
            if (old.get("licensing") or {}) != (new.get("licensing") or {}):
                reasons.append(f"licence changed: {relative.as_posix()}")
        if reasons:
            return ChangeDecision("human", ("new-model",), False, tuple(reasons), True)

        score_check = check_score_only(before, after)
        if score_check.ok:
            return ChangeDecision("auto", (), True, (), True)
        return ChangeDecision("human", (), False, score_check.errors, True)
