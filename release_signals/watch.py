"""Watch primary sources for model releases and file them as discoveries (MODEL-216).

Grok Bot hears about a release on X. This watcher reads the labs' own model
pages, public provider model lists and Hugging Face org feeds, and diffs each
against a committed baseline. A model that is on a source now, was not in the
baseline, and matches no catalogue alias becomes a `release-discovery` v1 and
enters the same pending queue Grok Bot's signals do.

A discovery is a trigger, never evidence. The pipeline downstream re-reads
primary sources under its two-key rules exactly as it does for Grok Bot.

Every source either answers with at least as many model IDs as its floor, or
the run reports it as an outage. A source is never skipped quietly.
"""

from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any, Literal
from urllib.parse import urlsplit
from urllib.robotparser import RobotFileParser

import yaml

from decision.excluded import excluded_sources
from release_signals.contract import SIGNAL_ONLY_HOSTS, WATCH_PREFIX, ReleaseSignal

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "registry" / "release-watch.yaml"
BASELINE = ROOT / "registry" / "release-watch-baseline.json"
HF_FEED = "https://huggingface.co/api/models?author={org}&sort=createdAt&direction=-1&limit=100"

Kind = Literal["page", "openrouter", "huggingface"]
Status = Literal["ok", "unreachable", "robots_disallowed", "parse_failed", "burst"]


class RegistryError(ValueError):
    """The source registry or its baseline is inconsistent."""


@dataclass(frozen=True)
class Source:
    id: str
    kind: Kind
    url: str
    confidence: float
    provider: str = ""
    providers: Mapping[str, str] = field(default_factory=dict)
    pattern: str = ""
    exclude: str = ""
    require_digit: bool = True
    max_new: int = 10


@dataclass(frozen=True)
class Registry:
    user_agent: str
    recent_days: int
    variant_exclude: str
    page_exclude: str
    sources: tuple[Source, ...]


@dataclass(frozen=True)
class Seen:
    """One model a source lists. `key` is unique within that source."""

    key: str
    model_name: str
    provider: str
    url: str
    created: datetime | None = None


@dataclass(frozen=True)
class SourceRun:
    source: Source
    status: Status
    detail: str = ""
    listed: int = 0
    new: tuple[Seen, ...] = ()


@dataclass(frozen=True)
class Response:
    status: int
    body: bytes


Fetch = Callable[[str], Response]


def load_registry(path: Path = REGISTRY) -> Registry:
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    sources = []
    for row in raw["sources"]:
        row = dict(row)
        if row.get("kind") == "huggingface":
            row["url"] = HF_FEED.format(org=row.pop("org"))
        source = Source(**row)
        _check_source(source)
        sources.append(source)
    ids = [source.id for source in sources]
    if len(ids) != len(set(ids)):
        raise RegistryError("source IDs must be unique")
    return Registry(
        user_agent=raw["user_agent"],
        recent_days=int(raw["recent_days"]),
        variant_exclude=raw["variant_exclude"],
        page_exclude=raw["page_exclude"],
        sources=tuple(sources),
    )


def _check_source(source: Source) -> None:
    parsed = urlsplit(source.url)
    host = (parsed.hostname or "").casefold().removeprefix("www.")
    if parsed.scheme != "https":
        raise RegistryError(f"{source.id}: sources are fetched over https only")
    if any(host == blocked or host.endswith(f".{blocked}") for blocked in SIGNAL_ONLY_HOSTS):
        raise RegistryError(f"{source.id}: X is Grok Bot's channel, not a watched source")
    if excluded_sources().url(source.url):
        raise RegistryError(f"{source.id}: {source.url} is an excluded source")
    if source.kind == "page" and not (source.pattern and source.provider):
        raise RegistryError(f"{source.id}: a page source needs a pattern and a provider")
    if source.kind == "huggingface" and not source.provider:
        raise RegistryError(f"{source.id}: a Hugging Face source needs a provider")
    if source.kind == "openrouter" and not source.providers:
        raise RegistryError(f"{source.id}: an OpenRouter source needs its provider map")
    for rule in (source.pattern, source.exclude):
        try:
            re.compile(rule)
        except re.error as exc:
            raise RegistryError(f"{source.id}: {rule!r} is not a regular expression: {exc}")
    if not 0 <= source.confidence <= 1:
        raise RegistryError(f"{source.id}: confidence must be from 0 through 1")


def load_baseline(path: Path = BASELINE) -> dict[str, frozenset[str]]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    return {source_id: frozenset(keys) for source_id, keys in raw["sources"].items()}


def write_baseline(path: Path, baseline: Mapping[str, Iterable[str]], taken: datetime) -> None:
    payload = {
        "taken_at": taken.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "sources": {source_id: sorted(keys) for source_id, keys in sorted(baseline.items())},
    }
    path.write_text(json.dumps(payload, indent=1) + "\n", encoding="utf-8")


# ── extraction: what one source lists right now ──────────────────────────────

def extract(source: Source, body: bytes, registry: Registry) -> dict[str, Seen]:
    if source.kind == "page":
        return _page(source, body.decode("utf-8", errors="replace"), registry)
    payload = json.loads(body)
    if source.kind == "openrouter":
        return _openrouter(source, payload, registry)
    return _huggingface(source, payload, registry)


def _page(source: Source, text: str, registry: Registry) -> dict[str, Seen]:
    # Model IDs sit in prose, tables and inlined JSON alike, so the page is read
    # as text. The boundaries keep a match from being a piece of a URL path,
    # a file name or a longer slug.
    token = re.compile(
        rf"(?<![A-Za-z0-9._/-])(?:{source.pattern})(?![A-Za-z0-9_-]|\.[A-Za-z0-9])",
        re.IGNORECASE,
    )
    rejected = [
        re.compile(rule, re.IGNORECASE)
        for rule in (registry.page_exclude, source.exclude) if rule
    ]
    found: dict[str, Seen] = {}
    for match in token.finditer(text):
        name = match.group(0).lower()
        if source.require_digit and not re.search(r"\d", name):
            continue
        if any(rule.search(name) for rule in rejected):
            continue
        found.setdefault(name, Seen(name, name, source.provider, source.url))
    return found


def _openrouter(source: Source, payload: Any, registry: Registry) -> dict[str, Seen]:
    variant = re.compile(registry.variant_exclude, re.IGNORECASE)
    found: dict[str, Seen] = {}
    for row in payload.get("data") or []:
        listed = str(row.get("id") or "")
        # `~lab/…-latest` is a moving alias and `:free`/`:batch` a pricing
        # variant of a model that is listed on its own anyway.
        if not listed or listed.startswith("~") or ":" in listed:
            continue
        prefix, _, name = listed.partition("/")
        provider = source.providers.get(prefix)
        if not provider or not name or variant.search(name):
            continue
        created = row.get("created")
        found[listed] = Seen(
            listed, name, provider, f"https://openrouter.ai/{listed}",
            datetime.fromtimestamp(created, UTC) if isinstance(created, (int, float)) else None,
        )
    return found


def _huggingface(source: Source, payload: Any, registry: Registry) -> dict[str, Seen]:
    variant = re.compile(registry.variant_exclude, re.IGNORECASE)
    rejected = re.compile(source.exclude, re.IGNORECASE) if source.exclude else None
    found: dict[str, Seen] = {}
    for row in payload if isinstance(payload, list) else []:
        repo = str(row.get("id") or "")
        _, _, name = repo.partition("/")
        if not name or row.get("private") or variant.search(name):
            continue
        if rejected and rejected.search(name):
            continue
        created = _instant(row.get("createdAt"))
        found[repo] = Seen(repo, name, source.provider, f"https://huggingface.co/{repo}", created)
    return found


def _instant(value: object) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(UTC)
    except ValueError:
        return None


# ── one run ──────────────────────────────────────────────────────────────────

def allowed_by_robots(url: str, user_agent: str, fetch: Fetch) -> bool:
    """RFC 9309 §2.3.1: any 4xx is "unavailable" and allows; a 5xx disallows."""
    parts = urlsplit(url)
    robots = f"{parts.scheme}://{parts.netloc}/robots.txt"
    response = fetch(robots)
    parser = RobotFileParser(robots)
    if response.status >= 500:
        return False
    if response.status >= 400:
        return True
    parser.parse(response.body.decode("utf-8", errors="replace").splitlines())
    return parser.can_fetch(user_agent, url)


def watch_source(
    source: Source,
    *,
    registry: Registry,
    baseline: frozenset[str],
    fetch: Fetch,
    now: datetime,
    catalogued: Callable[[Seen], bool] | None = None,
) -> SourceRun:
    try:
        if not allowed_by_robots(source.url, registry.user_agent, fetch):
            return SourceRun(source, "robots_disallowed", "robots.txt does not allow this URL")
        response = fetch(source.url)
    except Exception as exc:  # noqa: BLE001 - any failure to read is an outage to report
        return SourceRun(source, "unreachable", f"{type(exc).__name__}: {exc}")
    if response.status != 200:
        return SourceRun(source, "unreachable", f"HTTP {response.status}")
    try:
        listed = extract(source, response.body, registry)
    except (ValueError, AttributeError, TypeError) as exc:
        return SourceRun(source, "parse_failed", f"{type(exc).__name__}: {exc}")

    # Half the baseline is the floor. A page that stops yielding IDs has moved
    # or become script-only, and that is an outage, not an empty day.
    floor = max(1, len(baseline) // 2)
    if len(listed) < floor:
        return SourceRun(
            source, "parse_failed",
            f"{len(listed)} model IDs, below the floor of {floor}", len(listed),
        )

    cutoff = now - timedelta(days=registry.recent_days)
    new = tuple(
        seen for key, seen in sorted(listed.items())
        if key not in baseline
        and (seen.created is None or seen.created >= cutoff)
        and (catalogued is None or not catalogued(seen))
    )
    if catalogued is not None and len(new) > source.max_new:
        return SourceRun(
            source, "burst",
            f"{len(new)} new IDs at once, above {source.max_new}; the source may have "
            "changed shape. Check it, then rebaseline or raise max_new.",
            len(listed), new,
        )
    return SourceRun(source, "ok", "", len(listed), new)


def _robots_once(fetch: Fetch) -> Fetch:
    """Read each host's robots.txt once per run; 21 sources share huggingface.co."""
    seen: dict[str, Response] = {}

    def cached(url: str) -> Response:
        if not url.endswith("/robots.txt"):
            return fetch(url)
        if url not in seen:
            seen[url] = fetch(url)
        return seen[url]

    return cached


def signal_id(provider: str, model_name: str) -> str:
    """Stable per lab and model, so two sources listing one model file it once."""
    # Dots become hyphens as in `attribution.normalise`, so OpenRouter's
    # `claude-opus-5.5` and the lab page's `claude-opus-5-5` are one ID.
    lab = re.sub(r"[^a-z0-9]+", "-", provider.lower()).strip("-")
    name = re.sub(r"[^a-z0-9]+", "-", model_name.lower()).strip("-")
    candidate = f"{WATCH_PREFIX}{lab}:{name}"
    if len(candidate) <= 128:
        return candidate
    return f"{candidate[:115]}-{hashlib.sha256(candidate.encode()).hexdigest()[:12]}"


def discoveries(runs: Iterable[SourceRun], now: datetime) -> list[ReleaseSignal]:
    """The signals to file, one per ID, first source in registry order wins."""
    stamp = now.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    chosen: dict[str, ReleaseSignal] = {}
    for run in runs:
        if run.status != "ok":
            continue
        for seen in run.new:
            identifier = signal_id(seen.provider, seen.model_name)
            if identifier in chosen:
                continue
            chosen[identifier] = ReleaseSignal.parse({
                "model_name": seen.model_name,
                "provider": seen.provider,
                "first_seen_url": seen.url,
                "timestamp": stamp,
                "confidence": run.source.confidence,
                "signal_id": identifier,
            }, discovered=True)
    return list(chosen.values())


def run_all(
    registry: Registry,
    baseline: Mapping[str, frozenset[str]],
    *,
    fetch: Fetch,
    now: datetime,
    catalogued: Callable[[Seen], bool] | None = None,
) -> list[SourceRun]:
    missing = [source.id for source in registry.sources if source.id not in baseline]
    if missing:
        raise RegistryError(f"no baseline for {missing}; run with --rebaseline --source")
    fetch = _robots_once(fetch)
    return [
        watch_source(
            source, registry=registry, baseline=baseline[source.id],
            fetch=fetch, now=now, catalogued=catalogued,
        )
        for source in registry.sources
    ]


@dataclass(frozen=True)
class Catalogue:
    """One pass over the cards: which lab a name means, and each lab's aliases.

    The same rules as `pipeline.resolve_signal`, read once per run instead of
    once per model. This only decides what not to file; the pipeline's own
    resolution stays the authority on anything the watcher does file.
    """

    labs: Mapping[str, frozenset[str]]
    aliases: Mapping[str, frozenset[str]]

    def lab(self, provider: str) -> str | None:
        labs = self.labs.get(_normalise(provider), frozenset())
        return next(iter(labs)) if len(labs) == 1 else None

    def catalogued(self, seen: Seen) -> bool:
        lab = self.lab(seen.provider)
        return lab is not None and _normalise(seen.model_name) in self.aliases.get(lab, ())


def load_catalogue(root: Path = ROOT) -> Catalogue:
    loader = getattr(yaml, "CSafeLoader", yaml.SafeLoader)
    labs: dict[str, set[str]] = {}
    aliases: dict[str, set[str]] = {}
    for path in sorted((root / "models").glob("*/*.md")):
        parts = path.read_text(encoding="utf-8").split("---", 2)
        front = yaml.load(parts[1], Loader=loader) if len(parts) >= 3 else None
        if not isinstance(front, dict):
            continue
        provider = str(front.get("provider") or path.parent.name)
        for name in (provider, front.get("provider_display"), path.parent.name):
            if name:
                labs.setdefault(_normalise(str(name)), set()).add(provider)
        model_id = str(front.get("model_id") or "")
        aliases.setdefault(path.parent.name, set()).update(
            _normalise(str(value)) for value in (
                front.get("display_name"), front.get("version"),
                model_id.rsplit("/", 1)[-1], path.stem,
            ) if value
        )
    known = root / "scripts" / "models_dev_known_identities.yaml"
    if known.is_file():
        from scripts.seed_models_dev import load_known_identities

        for listed, canonical in load_known_identities(known).items():
            listed_lab, _, listed_name = listed.partition("/")
            if listed_name and (root / "models" / f"{canonical}.md").is_file():
                for lab in labs.get(_normalise(listed_lab), ()):
                    aliases.setdefault(lab, set()).add(_normalise(listed_name))
    return Catalogue(
        {name: frozenset(value) for name, value in labs.items()},
        {name: frozenset(value) for name, value in aliases.items()},
    )


def _normalise(value: str) -> str:
    """`scripts.attribution.normalise`, without importing its HTTP client."""
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
