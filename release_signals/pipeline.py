"""Resolve a release signal, gather allowed sources, and draft a model card."""

from __future__ import annotations

import json
import re
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import date
from html.parser import HTMLParser
from pathlib import Path
from typing import Literal
from urllib.parse import urlencode, urlsplit

import yaml

from decision.excluded import excluded_sources
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


def _provider_slugs(signal_provider: str, models_dir: Path) -> tuple[str, ...]:
    wanted = attribution.normalise(signal_provider)
    slugs: set[str] = set()
    for path in sorted(models_dir.glob("*/*.md")):
        front = _front(path)
        provider = str(front.get("provider") or path.parent.name)
        display = str(front.get("provider_display") or "")
        if wanted in {
            attribution.normalise(provider),
            attribution.normalise(display),
            attribution.normalise(path.parent.name),
        }:
            slugs.add(provider)
    return tuple(sorted(slugs))


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
    matches: list[str] = []
    known_path = root / "scripts" / "models_dev_known_identities.yaml"
    if known_path.is_file():
        known = load_known_identities(known_path)
        for listed, canonical in known.items():
            listed_provider, separator, listed_name = listed.partition("/")
            canonical_path = root / "models" / canonical.replace("/", "/", 1)
            canonical_path = canonical_path.with_suffix(".md")
            if (
                separator
                and attribution.normalise(listed_provider) in {
                    attribution.normalise(provider), attribution.normalise(signal.provider)
                }
                and attribution.normalise(listed_name) == wanted
                and canonical_path.is_file()
            ):
                matches.append(canonical)
    for path in sorted((models_dir / provider).glob("*.md")):
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
    matches = sorted(set(matches))
    if len(matches) == 1:
        return Resolution("existing", matches[0], tuple(matches), "exact catalogue alias")
    if len(matches) > 1:
        return Resolution("uncertain", None, tuple(matches), "more than one exact alias matched")
    model_id = f"{provider}/{slugify(signal.model_name)}"
    return Resolution("new", model_id, (), "no exact catalogue alias matched")


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


def _models_dev_listing(payload: object, provider: str, model_name: str) -> tuple[str, dict]:
    if not isinstance(payload, Mapping):
        raise ValueError("models.dev returned no provider map")
    provider_rows = [
        (key, value) for key, value in payload.items()
        if attribution.normalise(str(key)) == attribution.normalise(provider)
        or attribution.normalise(str((value or {}).get("name", "")))
        == attribution.normalise(provider)
    ]
    if len(provider_rows) != 1:
        raise IdentityUncertainError("models.dev did not identify exactly one provider")
    provider_id, provider_row = provider_rows[0]
    models = (provider_row or {}).get("models")
    if not isinstance(models, Mapping):
        raise ValueError("models.dev provider row has no models map")
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
    if len(matches) != 1:
        raise IdentityUncertainError(
            "models.dev did not identify exactly one model listing"
        )
    listing = matches[0]
    if provider_row.get("doc"):
        listing.setdefault("api_docs_url", provider_row["doc"])
    return str(provider_id), listing


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
        try:
            value = json.loads("".join(self.buffer))
        except json.JSONDecodeError:
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


def _primary_identity(
    page: FetchResult, expected_name: str, expected_provider: str
) -> tuple[str, str]:
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
            attribution.normalise(clause)
            for clause in re.split(r"[.!?;:\n]+", text)
            if attribution.normalise(clause)
        ]
        if not any(normalised_name in clause for clause in clauses):
            raise IdentityUncertainError("the primary source does not name the model")
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
        relationships = (
            f"{normalised_name}-by-{normalised_provider}",
            f"{normalised_provider}-announces-{normalised_name}",
            f"{normalised_provider}-introduces-{normalised_name}",
            f"{normalised_provider}-launches-{normalised_name}",
            f"{normalised_provider}-releases-{normalised_name}",
        )
        if not any(
            relationship in clause
            for clause in clauses
            for relationship in relationships
        ):
            raise IdentityUncertainError(
                "the primary source does not identify the stated lab"
            )
        return expected_name, ""
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
        date.fromisoformat(published)
    return str(row["name"]).strip(), published


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
    except Exception as exc:  # the optional source never blocks a provider-backed card
        return "", f"Hugging Face search failed: {type(exc).__name__}: {exc}"
    wanted_model = attribution.normalise(model_name)
    wanted_provider = attribution.normalise(provider)
    matches = []
    for row in payload if isinstance(payload, list) else []:
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
    models_dev_payload = json.loads(listing_response.body)
    try:
        provider_id, listing = _models_dev_listing(
            models_dev_payload, signal.provider, signal.model_name
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
    except IdentityUncertainError as exc:
        return GatherResult(Resolution(
            "uncertain", None, resolution.candidates, str(exc)
        ))
    primary_candidates = [
        require_allowed_source(str(listing[field]))
        for field in PRIMARY_URL_FIELDS if listing.get(field)
    ]
    primary_candidates = list(dict.fromkeys(primary_candidates))
    if not primary_candidates:
        primary_candidates = [
            require_allowed_source(str(listing[field]))
            for field in SUPPORTING_URL_FIELDS if listing.get(field)
        ]
    if not primary_candidates:
        raise ValueError("the listing does not name a primary provider source")
    primary_url = primary_candidates[0]
    primary = _fetch_allowed(fetch, primary_url)
    try:
        display_name, release_date = _primary_identity(
            primary, signal.model_name, signal.provider
        )
    except IdentityUncertainError as exc:
        return GatherResult(Resolution(
            "uncertain", None, resolution.candidates, str(exc)
        ))
    supporting_urls = list(dict.fromkeys(
        require_allowed_source(str(listing[field]))
        for field in SUPPORTING_URL_FIELDS if listing.get(field)
    ))
    for url in supporting_urls:
        _fetch_allowed(fetch, url)

    failures: list[str] = []
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
        "provider_docs_url": api_docs_url,
    }
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


def draft_signal(
    signal,
    *,
    root: Path,
    fetch: Callable[[str], FetchResult],
    read_date: date,
    models_dev_url: str = MODELS_DEV_URL,
    firecrawl_budget: FirecrawlBudget | None = None,
    discover_huggingface: bool = False,
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
    huggingface_url = next((url for url in supporting_urls if "huggingface.co" in url), "")
    api_docs_url = next((url for url in supporting_urls if url != huggingface_url), primary_url)
    front = {
        "model_id": resolution.model_id,
        "display_name": display_name,
        "provider": provider,
        "provider_display": provider_display,
        "release_date": release_date,
        "cost": {},
        "benchmarks": {"scores": {}, "evidence": []},
        "sources": {
            "models_dev_url": f"https://models.dev/{gathered.provider_id}",
            "provider_docs_url": api_docs_url,
            "huggingface_url": huggingface_url,
            "last_scraped_models_dev": accessed,
            "last_scraped_pricing": "",
        },
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
    return DraftResult(
        resolution,
        card_path,
        gathered.evidence_urls,
        (firecrawl_budget or FirecrawlBudget()).spent,
        gathered.gather_failures,
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
