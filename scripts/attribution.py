"""Who built a model listed on models.dev (MODEL-82).

A models.dev provider page lists what that provider *serves*. Alibaba's page
lists Moonshot's Kimi K3 as a bare ``kimi-k3``; the seeder used to read the
page as the author and proposed ``models/qwen/kimi-k3.md``. This module decides
the creating organisation from evidence, and says so when it cannot.

The order is fixed:

1. **An id prefix that names an organisation settles it.** ``moonshotai/kimi-k3``
   is Moonshot's. Code, no model call.
2. **A bare id is looked up across every models.dev page.** If the same id is
   listed elsewhere under exactly one creator prefix (TokenGo lists
   ``moonshotai/kimi-k3``) and no product name contradicts it, that prefix
   settles it. If the page's own organisation is the only one any product name
   points at, and no prefix disagrees, page and name corroborate each other
   (``qwen-plus`` on Alibaba's page). Code, no model call.
3. **Everything else is ambiguous**, and goes to Jev (TypeSafe's System One
   model). Code extracts the candidate organisations from the evidence; Jev
   *selects* one of them with a Choice, or ``cannot_establish``. A Noul asks,
   in the same request, whether the listing platform is reselling someone
   else's model. Jev never names an organisation code did not offer, and its
   answer is only ever mapped back to a catalogue slug from the registry, so no
   scraped text reaches a card field through it.

The confidence bands in ``scripts/attribution.yaml`` decide what a judgment may
write. Below the review band the creator is null and no card is created: a
null beats a guess (standing rule 2). Every raw judgment is kept in a ledger so
a threshold can change without new inference.

If ``TYPESAFE_API_KEY`` is absent the ambiguous listings stay unattributed and
the report says so. There is no fallback to the page.

**The judge never writes its own vendor's card (MODEL-101).** ModelSpec pays
TypeSafe, and the catalogue now carries a TypeSafe card, so a judgment could
otherwise decide a field about the organisation that supplies the judgment.
``supplier_conflict`` refuses that listing before the request is made, and
``apply_policy`` refuses it again before a stored answer is applied, so neither
a new call nor a cached one can write it. The suppliers are
``schema.suppliers.SUPPLIER_SLUGS`` — the same table the site reads to print the
disclosure, so the org we disclose and the org we protect cannot drift apart.
Deterministic attribution is untouched: an id prefix naming TypeSafe is code
reading a string, not the model's opinion about its own maker.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import time
from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any, Protocol

import httpx
import yaml

from schema.suppliers import SUPPLIER_SLUGS

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = PROJECT_ROOT / "scripts" / "attribution.yaml"
LEDGER_PATH = PROJECT_ROOT / "scripts" / "attribution_judgments.jsonl"

CANNOT_ESTABLISH = "cannot_establish"
CREATOR_Q = "creator"
RESELLER_Q = "reseller"

# Status of an attribution. Only the first three put a creator on a card.
DETERMINISTIC = "deterministic"
WRITTEN = "written"  # Jev, high band
REVIEW = "review"  # Jev, medium band: written, and listed for a human
WITHHELD = "withheld"  # Jev answered; the answer does not clear the bar
UNAVAILABLE = "unavailable"  # Jev was needed and could not be asked
NO_CANDIDATE = "no_candidate"  # nothing in the evidence names a catalogue org
CONFLICTED = "conflicted"  # the judge's own vendor is in play (MODEL-101)

WRITES_CREATOR = frozenset({DETERMINISTIC, WRITTEN, REVIEW})


# ── Configuration ───────────────────────────────────────────────


@dataclass(frozen=True)
class Thresholds:
    write: float
    review: float
    reseller_veto: float

    def __post_init__(self) -> None:
        if not 0.0 <= self.review <= self.write <= 1.0:
            raise ValueError(f"need 0 <= review <= write <= 1, got {self}")


@dataclass(frozen=True)
class Config:
    endpoint: str
    model: str
    timeout_seconds: float
    max_retries: int
    max_input_tokens_per_run: int
    thresholds: Thresholds
    creator_namespaces: dict[str, str]
    route_prefixes: frozenset[str]
    brand_tokens: dict[str, frozenset[str]]
    availability_fields: dict[str, str]


def load_config(path: Path | None = None) -> Config:
    raw = yaml.safe_load((path or CONFIG_PATH).read_text(encoding="utf-8"))
    ts = raw["typesafe"]
    th = raw["thresholds"]
    return Config(
        endpoint=ts["endpoint"],
        model=ts["model"],
        timeout_seconds=float(ts["timeout_seconds"]),
        max_retries=int(ts["max_retries"]),
        max_input_tokens_per_run=int(ts["max_input_tokens_per_run"]),
        thresholds=Thresholds(
            write=float(th["write"]),
            review=float(th["review"]),
            reseller_veto=float(th["reseller_veto"]),
        ),
        creator_namespaces={str(k).lower(): v for k, v in raw["creator_namespaces"].items()},
        route_prefixes=frozenset(str(p).lower() for p in raw["route_prefixes"]),
        brand_tokens={
            org: frozenset(t.lower() for t in toks) for org, toks in raw["brand_tokens"].items()
        },
        availability_fields=dict(raw.get("availability_fields") or {}),
    )


# ── Organisations the catalogue can card ───────────────────────


@dataclass(frozen=True)
class Org:
    slug: str
    display: str
    country: str = ""


_FRONT_LINE = re.compile(r"^(provider|provider_display|  origin_country):\s*(.*)$")


def load_registry(models_dir: Path, provider_map: dict[str, dict] | None = None) -> dict[str, Org]:
    """Every organisation the catalogue already has a directory for.

    Display name and country are the most common values on that org's cards;
    the seeder's own provider map wins where it has an entry. A creator that is
    not in the registry cannot be carded by the seeder, whatever the evidence.
    """
    from collections import Counter

    displays: dict[str, Counter] = {}
    countries: dict[str, Counter] = {}
    for path in models_dir.glob("*/*.md"):
        slug = path.parent.name
        display = country = ""
        with path.open(encoding="utf-8") as handle:
            for i, line in enumerate(handle):
                if i and line.startswith("---"):
                    break
                m = _FRONT_LINE.match(line.rstrip("\n"))
                if not m:
                    continue
                value = m.group(2).strip().strip("'\"")
                if m.group(1) == "provider_display":
                    display = value
                elif m.group(1).strip() == "origin_country":
                    country = value
        if display:
            displays.setdefault(slug, Counter())[display] += 1
        if country:
            countries.setdefault(slug, Counter())[country] += 1
    orgs: dict[str, Org] = {}
    for slug in {p.parent.name for p in models_dir.glob("*/*.md")}:
        d = displays.get(slug)
        c = countries.get(slug)
        orgs[slug] = Org(
            slug, d.most_common(1)[0][0] if d else slug, c.most_common(1)[0][0] if c else ""
        )
    for cfg in (provider_map or {}).values():
        orgs[cfg["slug"]] = Org(cfg["slug"], cfg["display"], cfg.get("country", ""))
    return orgs


# ── Evidence ────────────────────────────────────────────────────


@dataclass(frozen=True)
class Listing:
    platform: str  # models.dev provider id of the page
    platform_name: str
    listed_id: str
    name: str
    family: str


def normalise(model_id: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", model_id.lower()).strip("-")


def split_id(listed_id: str, config: Config) -> tuple[str | None, str]:
    """``(prefix, bare)``. Routing segments are skipped; ``~`` and ``hf:`` stripped."""
    parts = [p for p in listed_id.strip().split("/") if p]
    if not parts:
        return None, ""
    bare = parts[-1]
    prefixes = [p.lower().lstrip("~").removeprefix("hf:") for p in parts[:-1]]
    prefixes = [p for p in prefixes if p and p not in config.route_prefixes]
    return (prefixes[0] if prefixes else None), bare


def brand_orgs(texts: Iterable[str], config: Config) -> set[str]:
    words: set[str] = set()
    for text in texts:
        words.update(re.findall(r"[a-z]+", (text or "").lower()))
    return {org for org, tokens in config.brand_tokens.items() if words & tokens}


@dataclass
class ListingIndex:
    """Every models.dev listing by normalised bare id.

    ``routing_pages`` are pages whose prefixes name the host, not the maker.
    LLM Gateway lists ``alibaba/kimi-k3``, ``tencent/kimi-k3`` and
    ``moonshot/kimi-k3`` side by side: one model under several prefixes on one
    page means that page's prefixes route requests. Their prefixes are never
    read as creators, and their prefixed ids are not shown to the judgment.
    """

    by_bare: dict[str, list[tuple[str, str]]]
    routing_pages: frozenset[str]

    @classmethod
    def build(cls, api_data: dict, config: Config) -> ListingIndex:
        by_bare: dict[str, list[tuple[str, str]]] = {}
        routing: set[str] = set()
        for pid, pdata in api_data.items():
            models = (pdata or {}).get("models") if isinstance(pdata, dict) else None
            if not isinstance(models, dict):
                continue
            prefixes_by_bare: dict[str, set[str]] = {}
            for key, raw in models.items():
                listed = str((raw or {}).get("id", key)) if isinstance(raw, dict) else str(key)
                prefix, bare = split_id(listed, config)
                nb = normalise(bare)
                by_bare.setdefault(nb, []).append((pid, listed))
                if prefix:
                    prefixes_by_bare.setdefault(nb, set()).add(prefix)
            if any(len(p) > 1 for p in prefixes_by_bare.values()):
                routing.add(pid)
        return cls(by_bare, frozenset(routing))


@dataclass
class Evidence:
    listing: Listing
    bare_id: str
    vendor: str | None  # catalogue org of the listing page, if it is one
    own_prefix: str | None  # prefix on this listing's own id
    own_prefix_org: str | None
    elsewhere: list[tuple[str, str]]  # (platform, listed id) for the same bare id
    prefix_orgs: dict[str, list[str]]  # org -> listed ids naming it, from elsewhere
    unregistered_prefixes: list[str]
    named_orgs: set[str]  # product names in id / name / family
    first_party_orgs: set[str]  # seeded creator pages that also list this id
    candidates: list[str] = field(default_factory=list)


def gather_evidence(
    listing: Listing,
    index: ListingIndex,
    config: Config,
    registry: dict[str, Org],
    page_orgs: dict[str, str],
) -> Evidence:
    """Collect what the scraped data says about who built ``listing``.

    ``page_orgs`` maps a models.dev provider id to the catalogue org whose own
    page it is (the seeder's provider map).
    """
    prefix, bare = split_id(listing.listed_id, config)
    if listing.platform in index.routing_pages:
        prefix = None
    own_org = config.creator_namespaces.get(prefix) if prefix else None
    vendor = page_orgs.get(listing.platform) or config.creator_namespaces.get(
        listing.platform.lower()
    )
    elsewhere = [
        (pid, lid)
        for pid, lid in index.by_bare.get(normalise(bare), [])
        if not (pid == listing.platform and lid == listing.listed_id)
        and not (pid in index.routing_pages and "/" in lid)
    ]
    prefix_orgs: dict[str, list[str]] = {}
    unregistered: list[str] = []
    for _pid, lid in elsewhere:
        p, _ = split_id(lid, config)
        if not p:
            continue
        org = config.creator_namespaces.get(p)
        if org:
            prefix_orgs.setdefault(org, [])
            if lid not in prefix_orgs[org]:
                prefix_orgs[org].append(lid)
        elif p not in unregistered:
            unregistered.append(p)
    first_party = {page_orgs[pid] for pid, _ in elsewhere if pid in page_orgs}
    named = brand_orgs([bare, listing.name, listing.family], config)
    ev = Evidence(
        listing=listing,
        bare_id=bare,
        vendor=vendor,
        own_prefix=prefix,
        own_prefix_org=own_org,
        elsewhere=elsewhere,
        prefix_orgs=prefix_orgs,
        unregistered_prefixes=unregistered,
        named_orgs=named,
        first_party_orgs=first_party,
    )
    ev.candidates = candidate_orgs(ev, registry)
    return ev


def candidate_orgs(ev: Evidence, registry: dict[str, Org]) -> list[str]:
    """Organisations the evidence names, in a stable order.

    When an id prefix names the model's maker and the listing platform's
    organisation is not among the prefixes, that organisation is not a
    candidate at all, even if a product name mentions it
    (``deepseek-r1-distill-qwen-32b`` on Alibaba's page): a page never
    outvotes the model's own namespace.
    """
    named = set(ev.prefix_orgs) | ev.named_orgs | ev.first_party_orgs
    if ev.own_prefix_org:
        named.add(ev.own_prefix_org)
    prefixed = set(ev.prefix_orgs) | ({ev.own_prefix_org} if ev.own_prefix_org else set())
    if ev.vendor:
        if not prefixed or ev.vendor in prefixed:
            named.add(ev.vendor)
        else:
            named.discard(ev.vendor)
    return sorted(org for org in named if org in registry)


# ── Result ──────────────────────────────────────────────────────


@dataclass
class Attribution:
    listing: Listing
    creator: str | None
    status: str
    basis: str
    candidates: list[str]
    judgment: dict | None = None

    @property
    def writes_creator(self) -> bool:
        return self.status in WRITES_CREATOR and self.creator is not None


def decide_deterministically(ev: Evidence, registry: dict[str, Org]) -> Attribution | None:
    """Tiers 1 and 2. ``None`` means the evidence is ambiguous."""
    lst = ev.listing
    if ev.own_prefix_org:
        org = ev.own_prefix_org
        if org in registry:
            return Attribution(lst, org, DETERMINISTIC, f"id prefix `{ev.own_prefix}`", [org])
        return Attribution(
            lst, None, NO_CANDIDATE, "id prefix names an org the catalogue has no directory for", []
        )
    others_named = ev.named_orgs - set(ev.prefix_orgs)
    if len(ev.prefix_orgs) == 1 and not others_named:
        org = next(iter(ev.prefix_orgs))
        if org in registry:
            return Attribution(
                lst, org, DETERMINISTIC, "same id listed elsewhere under one creator prefix", [org]
            )
    if not ev.prefix_orgs and ev.vendor and ev.named_orgs == {ev.vendor} and ev.vendor in registry:
        return Attribution(
            lst, ev.vendor, DETERMINISTIC, "listing page and product name agree", [ev.vendor]
        )
    if not ev.candidates:
        return Attribution(
            lst, None, NO_CANDIDATE, "nothing in the evidence names a catalogue organisation", []
        )
    return None


# ── The supplier rule (MODEL-101) ───────────────────────────────


def supplier_conflict(ev: Evidence) -> str | None:
    """The supplier this listing could be attributed to, if any.

    ModelSpec pays TypeSafe and the judgment *is* a TypeSafe model, so a Jev
    answer naming TypeSafe would be the supplier writing its own card. The
    check is over ``candidates`` — the only organisations a judgment is ever
    offered, and the only ones ``apply_policy`` will accept — plus the listing
    page's own organisation, which is the other route to a creator.

    Stated as "is a supplier *in play*", not "did the judgment pick one": the
    request is never made, so there is no answer to review, nothing is spent,
    and there is no stored judgment about a supplier for a later threshold
    change to promote.
    """
    named = set(ev.candidates) | ({ev.vendor} if ev.vendor else set())
    conflicted = sorted(named & SUPPLIER_SLUGS)
    return conflicted[0] if conflicted else None


def conflict_basis(supplier: str) -> str:
    """Why nothing was written. One sentence, for the report and the console."""
    return (
        f"{supplier} supplies the judgment; no field on a {supplier} card may be "
        "written by its own model (MODEL-101). Attribute it by hand."
    )


# ── The judgment ────────────────────────────────────────────────

MAX_ELSEWHERE_IN_STATE = 15


def build_state(ev: Evidence) -> dict:
    """The evidence as Jev sees it. Scraped values, labelled as such."""
    seen: set[str] = set()
    elsewhere: list[dict] = []
    # Prefixed ids first: they are the informative ones.
    for pid, lid in sorted(ev.elsewhere, key=lambda x: ("/" not in x[1], x[0])):
        if lid in seen:
            continue
        seen.add(lid)
        elsewhere.append({"platform": pid, "listed_id": lid})
        if len(elsewhere) >= MAX_ELSEWHERE_IN_STATE:
            break
    return {
        "listing": {
            "platform": ev.listing.platform,
            "platform_name": ev.listing.platform_name,
            "listed_id": ev.listing.listed_id,
            "model_name": ev.listing.name,
            "model_family": ev.listing.family,
        },
        "same_model_on_other_platforms": elsewhere,
    }


def build_questions(candidates: list[str], registry: dict[str, Org], config: Config) -> dict:
    criteria: dict[str, Any] = {}
    for slug in candidates:
        org = registry[slug]
        prefixes = sorted(p for p, s in config.creator_namespaces.items() if s == slug)
        products = sorted(config.brand_tokens.get(slug, ()))
        entry: dict[str, Any] = {"organisation": org.display, "id_prefixes": prefixes}
        if products:
            entry["product_names"] = products
        criteria[slug] = entry
    criteria[CANNOT_ESTABLISH] = (
        "The state does not establish which organisation created this model, "
        "or it points to an organisation that is not one of the other options."
    )
    return {
        CREATOR_Q: {
            "type": "choice",
            "instructions": {
                "question": (
                    "Which organisation created the model in `listing`: "
                    "the one that trained and released it?"
                ),
                "evidence": (
                    "Judge only from the state: `listing.listed_id`, `listing.model_name`, "
                    "`listing.model_family`, and the ids in `same_model_on_other_platforms`. "
                    "A prefix on an id, as in `org/model`, names the organisation that made it."
                ),
                "not_evidence": (
                    "`listing.platform` is where the model is offered. Platforms serve and resell "
                    "models made by others, so being listed there does not make that platform's "
                    "organisation the creator."
                ),
            },
            "criteria": criteria,
        },
        RESELLER_Q: {
            "type": "noul",
            "instructions": (
                "Is the platform in `listing.platform` offering a model that a different "
                "organisation created, as a reseller, aggregator or host, rather than listing "
                "a model it created itself?"
            ),
            "criteria": {
                "true": (
                    "The evidence shows the model is another organisation's, "
                    "served by this platform."
                ),
                "false": (
                    "The evidence shows the model is the platform's own, "
                    "or nothing indicates anyone else made it."
                ),
            },
        },
    }


class JudgeUnavailable(RuntimeError):  # noqa: N818 - reads as a state, not a bug
    """The judgment could not be obtained. Fail closed: no creator."""


class Judge(Protocol):
    model: str

    def evaluate(self, state: dict, questions: dict) -> dict:
        """Return the API response body: ``{"answers": ..., "usage": ...}``."""


class TypeSafeJudge:
    """POST /v1/systemone over httpx. See docs.typesafe.ai/api."""

    def __init__(self, api_key: str, config: Config, client: httpx.Client | None = None) -> None:
        self._key = api_key
        self._config = config
        self.model = config.model
        self._client = client or httpx.Client(timeout=config.timeout_seconds)

    @classmethod
    def from_env(cls, config: Config) -> TypeSafeJudge | None:
        key = os.environ.get("TYPESAFE_API_KEY", "").strip()
        return cls(key, config) if key else None

    def evaluate(self, state: dict, questions: dict) -> dict:
        body = {"state": state, "model": self.model, "questions": questions}
        headers = {"Authorization": f"Bearer {self._key}", "Content-Type": "application/json"}
        delay = 1.0
        for attempt in range(self._config.max_retries + 1):
            try:
                resp = self._client.post(self._config.endpoint, json=body, headers=headers)
            except httpx.HTTPError as exc:
                last = f"{type(exc).__name__}"
            else:
                if resp.status_code == 200:
                    return resp.json()
                last = f"HTTP {resp.status_code}"
                if resp.status_code not in (429, 500, 502, 503, 504, 529):
                    break
                retry_after = resp.headers.get("retry-after")
                if retry_after and retry_after.replace(".", "", 1).isdigit():
                    delay = max(delay, float(retry_after))
            if attempt < self._config.max_retries:
                time.sleep(delay)
                delay *= 2
        # Never include the key or the response body: it is not ours to log.
        raise JudgeUnavailable(f"TypeSafe request failed: {last}")


def request_key(model: str, state: dict, questions: dict) -> str:
    blob = json.dumps({"model": model, "state": state, "questions": questions}, sort_keys=True)
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


class Ledger:
    """Append-only record of raw judgments, and a cache keyed by the request.

    The same evidence and the same questions are never paid for twice, and a
    threshold change is re-applied to stored answers, not re-inferred.
    """

    def __init__(self, path: Path | None) -> None:
        self.path = path
        self._rows: dict[str, dict] = {}
        if path and path.is_file():
            for line in path.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    row = json.loads(line)
                    self._rows[row["key"]] = row

    def get(self, key: str) -> dict | None:
        return self._rows.get(key)

    def put(self, row: dict) -> None:
        self._rows[row["key"]] = row
        if self.path:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with self.path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(row, sort_keys=True) + "\n")


def parse_answers(body: dict, candidates: list[str]) -> dict:
    """Keep only typed values. Anything malformed is a failed judgment."""
    try:
        creator = body["answers"][CREATOR_Q]
        reseller = body["answers"][RESELLER_Q]
        out = {
            "choice": str(creator["choice"]),
            "probabilities": {str(k): float(v) for k, v in creator["probabilities"].items()},
            "confidence": float(creator["confidence"]),
            "reseller": float(reseller["noul"]),
        }
    except (KeyError, TypeError, ValueError) as exc:
        raise JudgeUnavailable(f"malformed answer: {type(exc).__name__}") from exc
    return out


def apply_policy(
    ev: Evidence, answers: dict, candidates: list[str], thresholds: Thresholds
) -> Attribution:
    """Turn a stored judgment into an attribution under the current thresholds."""
    lst = ev.listing
    choice = answers["choice"]
    conf = answers["confidence"]
    judgment = dict(answers)
    # MODEL-101, and the second half of the rule: `decide` refuses to ask about
    # a supplier, and this refuses to apply an answer about one. Two refusals
    # because they fail differently — a ledger row written before a slug became
    # a supplier, or any caller reaching this function directly, arrives here
    # without passing the first.
    if choice in SUPPLIER_SLUGS:
        return Attribution(lst, None, CONFLICTED, conflict_basis(choice), candidates, judgment)
    if choice == CANNOT_ESTABLISH:
        return Attribution(
            lst, None, WITHHELD, "judged: cannot be established", candidates, judgment
        )
    if choice not in candidates:
        return Attribution(
            lst, None, WITHHELD, "answer outside the offered options", candidates, judgment
        )
    if choice == ev.vendor and answers["reseller"] >= thresholds.reseller_veto:
        return Attribution(
            lst,
            None,
            WITHHELD,
            "picked the listing platform while judging it a reseller",
            candidates,
            judgment,
        )
    if conf >= thresholds.write:
        return Attribution(
            lst, choice, WRITTEN, f"judged, confidence {conf:.2f}", candidates, judgment
        )
    if conf >= thresholds.review:
        return Attribution(
            lst,
            choice,
            REVIEW,
            f"judged, confidence {conf:.2f}: needs review",
            candidates,
            judgment,
        )
    return Attribution(
        lst,
        None,
        WITHHELD,
        f"judged, confidence {conf:.2f}: below the review band",
        candidates,
        judgment,
    )


@dataclass
class Budget:
    limit: int
    spent: int = 0

    def exhausted(self) -> bool:
        return self.spent >= self.limit


class Attributor:
    """The whole decision for one models.dev listing."""

    def __init__(
        self,
        api_data: dict,
        registry: dict[str, Org],
        page_orgs: dict[str, str],
        judge: Judge | None,
        config: Config | None = None,
        ledger: Ledger | None = None,
    ) -> None:
        self.api_data = api_data
        self.config = config or load_config()
        self.registry = registry
        self.page_orgs = page_orgs
        self.judge = judge
        self.ledger = ledger or Ledger(None)
        self.index = ListingIndex.build(api_data, self.config)
        self.budget = Budget(self.config.max_input_tokens_per_run)
        self.results: list[Attribution] = []

    def listing(self, platform: str, raw: dict, model_key: str) -> Listing:
        pdata = self.api_data.get(platform) or {}
        return Listing(
            platform=platform,
            platform_name=str(pdata.get("name", platform)) if isinstance(pdata, dict) else platform,
            listed_id=str(raw.get("id", model_key)),
            name=str(raw.get("name", "")),
            family=str(raw.get("family", "")),
        )

    def evidence(self, platform: str, raw: dict, model_key: str) -> Evidence:
        return gather_evidence(
            self.listing(platform, raw, model_key),
            self.index,
            self.config,
            self.registry,
            self.page_orgs,
        )

    def attribute(
        self, platform: str, raw: dict, model_key: str, *, deterministic_only: bool = False
    ) -> Attribution:
        ev = self.evidence(platform, raw, model_key)
        result = self.decide(ev, deterministic_only=deterministic_only)
        self.results.append(result)
        return result

    def decide(self, ev: Evidence, *, deterministic_only: bool = False) -> Attribution:
        settled = decide_deterministically(ev, self.registry)
        if settled is not None:
            return settled
        supplier = supplier_conflict(ev)
        if supplier is not None:
            return Attribution(
                ev.listing, None, CONFLICTED, conflict_basis(supplier), ev.candidates
            )
        if deterministic_only:
            return Attribution(
                ev.listing, None, UNAVAILABLE, "ambiguous; judgment not requested", ev.candidates
            )
        return self.judge_evidence(ev)

    def judge_evidence(self, ev: Evidence) -> Attribution:
        candidates = ev.candidates
        state = build_state(ev)
        questions = build_questions(candidates, self.registry, self.config)
        model = self.judge.model if self.judge else self.config.model
        key = request_key(model, state, questions)
        row = self.ledger.get(key)
        if row is None:
            if self.judge is None:
                return Attribution(
                    ev.listing,
                    None,
                    UNAVAILABLE,
                    "TYPESAFE_API_KEY not set; creator left null",
                    candidates,
                )
            if self.budget.exhausted():
                return Attribution(
                    ev.listing,
                    None,
                    UNAVAILABLE,
                    "token budget for this run spent; creator left null",
                    candidates,
                )
            try:
                body = self.judge.evaluate(state, questions)
                answers = parse_answers(body, candidates)
            except JudgeUnavailable as exc:
                return Attribution(
                    ev.listing, None, UNAVAILABLE, f"{exc}; creator left null", candidates
                )
            usage = body.get("usage") or {}
            self.budget.spent += int(usage.get("input_tokens") or 0)
            row = {
                "key": key,
                "date": date.today().isoformat(),
                "model": model,
                "platform": ev.listing.platform,
                "listed_id": ev.listing.listed_id,
                "candidates": candidates,
                "vendor": ev.vendor,
                "answers": answers,
                "usage": {"input_tokens": int(usage.get("input_tokens") or 0)},
            }
            self.ledger.put(row)
        return apply_policy(ev, row["answers"], candidates, self.config.thresholds)


# ── Reporting ───────────────────────────────────────────────────

_UNSAFE = re.compile(r"[^A-Za-z0-9._:/@~+-]")


def safe(value: object, limit: int = 120) -> str:
    """A scraped id reduced to id-like characters, for a PR body."""
    return _UNSAFE.sub("?", str(value))[:limit]


def render_report(results: list[Attribution], *, judge_available: bool, spent_tokens: int) -> str:
    review = [r for r in results if r.status == REVIEW]
    withheld = [
        r for r in results if r.status in (WITHHELD, UNAVAILABLE, NO_CANDIDATE, CONFLICTED)
    ]
    if not review and not withheld and judge_available:
        return ""
    lines = ["### Who built these models (MODEL-82)", ""]
    if not judge_available:
        lines += [
            "**`TYPESAFE_API_KEY` was not available.** Listings whose creator the "
            "evidence does not settle by itself were not attributed and have no card. "
            "Nothing was guessed from the listing page.",
            "",
        ]
    if review:
        lines += [
            "**Check the creator on these cards** (medium confidence, written for review):",
            "",
        ]
        for r in review:
            conf = (r.judgment or {}).get("confidence", 0.0)
            lines.append(
                f"- `{safe(r.listing.platform)}/{safe(r.listing.listed_id)}` → `{safe(r.creator)}` "
                f"(confidence {conf:.2f}; candidates {', '.join(safe(c) for c in r.candidates)})"
            )
        lines.append("")
    if withheld:
        lines += ["**No card: creator not established** (queued for research):", ""]
        for r in withheld:
            lines.append(
                f"- `{safe(r.listing.platform)}/{safe(r.listing.listed_id)}`: "
                f"{safe_reason(r.basis)}"
            )
        lines.append("")
    lines.append(f"Judgment input tokens this run: {spent_tokens}.")
    return "\n".join(lines) + "\n"


def safe_reason(text: str) -> str:
    # Reasons are written by this module, but keep the PR body one line each.
    return re.sub(r"[\x00-\x1f\x7f`]", " ", text)[:200]


# ── Corpus sweep ────────────────────────────────────────────────


@dataclass
class SweepHit:
    path: str
    model_id: str
    provider: str
    found_on: str
    listed_id: str
    evidence_says: str
    basis: str


def sweep_corpus(
    models_dir: Path,
    api_data: dict,
    registry: dict[str, Org],
    page_orgs: dict[str, str],
    config: Config | None = None,
) -> list[SweepHit]:
    """Cards whose provider is the page they were seeded from, against the evidence.

    For each card that records a models.dev page, find that page's listing and
    run the deterministic tiers on it. A card is reported when the evidence
    settles on a different organisation, or when the only thing tying the card
    to its provider is the page (a product name points elsewhere). Reports; changes
    nothing.
    """
    config = config or load_config()
    index = ListingIndex.build(api_data, config)
    hits: list[SweepHit] = []
    for path in sorted(models_dir.glob("*/*.md")):
        text = path.read_text(encoding="utf-8")
        parts = text.split("---", 2)
        if len(parts) < 3:
            continue
        data = yaml.safe_load(parts[1]) or {}
        url = str((data.get("sources") or {}).get("models_dev_url") or "")
        m = re.match(r"https?://models\.dev/([^/?#]+)/?$", url)
        if not m:
            continue
        platform = m.group(1)
        provider = str(data.get("provider", ""))
        slug = str(data.get("model_id", "")).split("/", 1)[-1]
        version = str(data.get("version") or "")
        pdata = api_data.get(platform)
        raw = None
        if isinstance(pdata, dict):
            for key, row in (pdata.get("models") or {}).items():
                lid = str(row.get("id", key))
                if lid == version or normalise(split_id(lid, config)[1]) == normalise(slug):
                    raw, model_key = row, key
                    break
        if raw is None:
            # The page no longer lists it; judge the card's own id and name.
            raw, model_key = (
                {
                    "id": version or slug,
                    "name": data.get("display_name", ""),
                    "family": data.get("family", ""),
                },
                slug,
            )
        listing = Listing(
            platform=platform,
            platform_name=str((pdata or {}).get("name", platform))
            if isinstance(pdata, dict)
            else platform,
            listed_id=str(raw.get("id", model_key)),
            name=str(raw.get("name", "")),
            family=str(raw.get("family", "")),
        )
        ev = gather_evidence(listing, index, config, registry, page_orgs)
        settled = decide_deterministically(ev, registry)
        other_named = sorted((ev.named_orgs | set(ev.prefix_orgs)) - {provider})
        if settled is not None and settled.creator and settled.creator != provider:
            says, basis = settled.creator, settled.basis
        elif (
            (settled is None or settled.creator is None)
            and other_named
            and provider not in ev.named_orgs | set(ev.prefix_orgs)
        ):
            says, basis = (
                " or ".join(other_named),
                "only the listing page ties it to its provider; the evidence names another org",
            )
        else:
            continue
        hits.append(
            SweepHit(
                path=str(path.relative_to(models_dir.parent)),
                model_id=str(data.get("model_id")),
                provider=provider,
                found_on=platform,
                listed_id=listing.listed_id,
                evidence_says=says,
                basis=basis,
            )
        )
    return hits


def main() -> None:
    """``python scripts/attribution.py sweep [--api-json FILE]``: report, change nothing."""
    import argparse
    import sys

    sys.path.insert(0, str(PROJECT_ROOT))
    from scripts.seed_models_dev import PROVIDER_MAP, fetch_models_dev

    parser = argparse.ArgumentParser(description=main.__doc__)
    parser.add_argument("command", choices=["sweep"])
    parser.add_argument("--api-json", type=Path, help="a saved models.dev api.json")
    args = parser.parse_args()
    api = json.loads(args.api_json.read_text()) if args.api_json else fetch_models_dev()
    models_dir = PROJECT_ROOT / "models"
    hits = sweep_corpus(
        models_dir,
        api,
        load_registry(models_dir, PROVIDER_MAP),
        {pid: cfg["slug"] for pid, cfg in PROVIDER_MAP.items()},
    )
    print(f"{len(hits)} cards whose provider is contradicted by the evidence:")
    for h in hits:
        print(
            f"  {h.path}: provider {h.provider}, seeded from models.dev/{h.found_on} "
            f"`{h.listed_id}`; evidence says {h.evidence_says} ({h.basis})"
        )


if __name__ == "__main__":
    main()
