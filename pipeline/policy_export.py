"""The public half of the compliance answer: `/api/policy/catalogue.json`.

MODEL-80. `POST /v1/policy-check` has to read four things about a model —
licence, origin country, commercial-use grant and where each platform processes
data — and the published export carried none of them in a form an endpoint
could read. `/api/models/<id>.json` publishes a whole card each, which is 1,339
fetches for one policy check, and `/api/rank/candidates.json` carries scoring
inputs only.

So this writes one file with exactly the policy fields, for every card, keyed
the way the endpoint asks the question: **per model, and per platform**. A
residency requirement is answered by the place a model is served from, not by
the model (`scripts/residency/platforms.py`), so the rows this file emits carry
the platform slugs each card says it is available on and the endpoint produces
one verdict per pair.

**Everything here is already public.** This is a reshaping of card front matter
and adds no information to the world: `commercial_use` is `withheld` or
`unspecified` on all 1,339 cards today, and this file repeats that faithfully.
The determinations themselves are in the private enrichment layer, permanently
(`docs/business/decision-record.md` §2.2, mirrored in `schema/enrichment.py`),
are not read by this module, and must never be written into this export. What
makes the paid tier different is a second store the Worker reads at runtime —
see `docs/policy-check-api.md` — not a richer copy of this file.

**Why the empty states are copied rather than flattened.** A consumer must be
able to tell "nobody looked" from "determined and held back" from "the provider
commits to no region", because those three lead to different actions. The card
schema went to some trouble to keep them apart (`UsePermission.WITHHELD`,
`DisclosureState`), and collapsing them here — to a null, or to `false` — would
undo that at the one point a customer reads. A `withheld` disclosure is a
promise the paid tier can resolve from the determination store (a region list,
or the no-commitment finding). This file still does not carry that answer.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from schema.card import Availability, ModelCard, PlatformEntry, PolicySource
from scripts.residency.platforms import is_local_runtime, platform_slugs

#: Bumped for an incompatible change to this file, under the same rule as every
#: other contract here (MODEL-59: widening a field's range is a major bump).
#: Distinct from `build.export_schema_version`, which versions the card tree.
POLICY_EXPORT_SCHEMA_VERSION = "1.0"

#: Where the file lands under a site's `api/` root.
CATALOGUE_PATH = "policy/catalogue.json"


def _source(source: PolicySource | None) -> dict[str, Any] | None:
    """A citation, or `None` when there is nothing cited.

    `read_on` rides along because a licence can be rewritten without notice and
    a compliance answer has to be defensible on the day it was given, not only
    on the day it was computed.
    """
    if source is None:
        return None
    return {
        "kind": str(source.kind),
        "url": source.url,
        "read_on": source.read_on,
        "quote": source.quote,
    }


def _platform_rows(availability: Availability) -> list[dict[str, Any]]:
    """The named platforms this card says it is available on.

    `other_platforms` is excluded for the reason `platform_slugs()` excludes it:
    it is free-form overflow with no stable identity, so a residency
    determination cannot be keyed to it and a verdict against it would be a
    verdict against a string somebody typed.
    """
    rows = []
    for name, value in availability:
        if isinstance(value, PlatformEntry) and value.available:
            rows.append({
                "platform": name,
                "model_id_on_platform": value.model_id,
                "url": value.url,
                "gated": value.gated,
                # The card's own per-platform region list, which is an
                # availability note ("served from these regions") and is *not*
                # a residency determination. Published as-is, and never read as
                # one: the endpoint answers residency from the determination
                # store keyed by platform, or says it cannot.
                "listed_regions": list(value.regions),
            })
    return rows


def policy_row(card: ModelCard) -> dict[str, Any]:
    """One card's public policy facts, in the shape the endpoint reads."""
    licensing = card.licensing
    provider = card.availability.primary_provider
    return {
        "model_id": card.identity.model_id,
        "display_name": card.identity.display_name,
        "provider": card.identity.provider,
        "licence": {
            "license_type": licensing.license_type.value if licensing.license_type else None,
            "license_url": licensing.license_url,
            "tos_url": licensing.tos_url,
            "open_weights": licensing.open_weights,
        },
        "commercial_use": {
            "value": licensing.commercial_use.value,
            "conditions": licensing.commercial_use_conditions,
            "source": _source(licensing.commercial_use_source),
        },
        "origin": {
            "country": licensing.origin_country,
            "org_type": licensing.origin_org_type.value if licensing.origin_org_type else None,
        },
        # The primary provider is the one place a *published* residency
        # determination can currently appear on a card. It is disclosure-tagged
        # rather than flattened, so `unresearched` and `withheld` stay apart.
        "primary_provider": {
            "name": provider.name,
            "data_residency": (list(provider.data_residency)
                               if provider.data_residency is not None else None),
            "data_residency_disclosure": provider.data_residency_disclosure.value,
            "data_residency_source": _source(provider.data_residency_source),
        },
        "platforms": _platform_rows(card.availability),
    }


def platform_classes() -> dict[str, list[str]]:
    """The platform namespace, and which of it residency cannot be asked about.

    Published rather than hardcoded in the endpoint. `LOCAL_RUNTIMES` is a fact
    about what the software *is* (MODEL-79) and it already has one home in
    `scripts/residency/platforms.py`; a second copy in the Worker would be a
    list that goes stale the day a local runtime is added, and the failure would
    be a country list attached to Ollama — exactly what that module refuses.
    """
    slugs = platform_slugs()
    return {
        "all": sorted(slugs),
        #: Residency is a property of the operator's machine here, so no region
        #: list can be true of the platform and none is ever determined.
        "unbounded": sorted(s for s in slugs if is_local_runtime(s)),
    }


def build_catalogue(cards: list[ModelCard], build_json: dict[str, Any]) -> dict[str, Any]:
    """The whole file, sorted by `model_id` so two builds of one commit match."""
    rows = sorted((policy_row(c) for c in cards), key=lambda r: r["model_id"])
    return {
        "schema_version": POLICY_EXPORT_SCHEMA_VERSION,
        "build": build_json,
        "platform_classes": platform_classes(),
        "count": len(rows),
        "models": rows,
    }


def write_export(out_dir: Any, cards: list[ModelCard],
                 build_json: dict[str, Any]) -> dict[str, int]:
    """Write `<out_dir>/policy/catalogue.json`. Returns counts for the summary."""
    out = Path(out_dir)
    catalogue = build_catalogue(cards, build_json)
    path = out / CATALOGUE_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(catalogue, sort_keys=True, default=str), encoding="utf-8")
    return {
        "models": catalogue["count"],
        "platform_rows": sum(len(r["platforms"]) for r in catalogue["models"]),
    }
