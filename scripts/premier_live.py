"""Read current private records for the shared premier-set selection rules."""

from __future__ import annotations

import logging
import math
from dataclasses import replace
from datetime import date, timedelta
from pathlib import Path

import yaml

from decision.excluded import excluded_sources
from decision.registry import default as default_registry
from decision.snapshot import LoadedSnapshot, build_snapshot, collect_repo
from pipeline.data_source import check_private

# The approved lineup counted the lab API as one recorded provider, and a
# cite-only guaranteed fact as verified when the verification log records it.
# Both switches default to that lineup. A snapshot citation alone does not.
COUNT_LAB_API = True
CITE_ONLY_FACTS_COUNT_AS_VERIFIED = True


def _verified_record(index: LoadedSnapshot, record_id: str | None) -> bool:
    if record_id is None:
        return False
    record = index.record(record_id)
    return (
        not record.get("citation")
        and (record.get("verification") or {}).get("outcome") == "verified"
    )


def _cited_or_verified(index: LoadedSnapshot, record_id: str | None) -> bool:
    if record_id is None:
        return False
    record = index.record(record_id)
    return (record.get("verification") or {}).get("outcome") == "verified"


def _guaranteed_verified(
    index: LoadedSnapshot, model_id: str, facets: set[str], logged: bool,
) -> bool:
    if CITE_ONLY_FACTS_COUNT_AS_VERIFIED and logged:
        return True
    check = _cited_or_verified if CITE_ONLY_FACTS_COUNT_AS_VERIFIED else _verified_record
    return all(check(index, index.fact(model_id, facet).record_id) for facet in facets)


def load_inputs(root: Path, as_of: date) -> dict:
    """Adapt admitted records without writing a snapshot or changing the lineup."""
    from scripts.premier_slice1 import (
        MAJOR_PLATFORMS,
        SLICE_CLASSES,
        leaderboards,
        load_cards,
        local_candidate_universe,
        slice1_board_id,
    )

    root = check_private(root)
    cards = load_cards(root)
    inputs = collect_repo(root)
    registry = default_registry()
    identity_values = {
        part: registry.allowed_values(registry.facet(f"offering.{part}"))
        for part in ("provider", "region", "tier")
    }
    offerings = [
        offering for offering in inputs.offerings
        if all(allowed is None or offering[part] in allowed
               for part, allowed in identity_values.items())
    ]
    if len(offerings) != len(inputs.offerings):
        logging.getLogger(__name__).warning(
            "%d offerings have unregistered identities; excluded from live selection",
            len(inputs.offerings) - len(offerings),
        )
    # Only model and metered-offering records participate in these clauses.
    # Historical invalid offering identities cannot supply a provider or price.
    inputs = replace(inputs, offerings=offerings, subscriptions=(), hardware=(),
                     hardware_fit_records=())
    snapshot = build_snapshot(
        inputs, registry=registry, guard=excluded_sources(), as_of=as_of,
    )
    index = LoadedSnapshot(
        snapshot.envelope(key=None, ed25519_signer=None),
        include_archive=True,
        signature_verified=False,
    )
    active = {
        model["id"] for model in inputs.models
        if model["lifecycle"] != "retired" and cards[model["id"]]["status"] != "sunset"
    }
    guaranteed = {
        facet.id for facet in registry.facets()
        if facet.subject == "model" and facet.tier == "guaranteed"
        and facet.computed_by is None
    }
    for model_id, card in cards.items():
        if model_id not in active:
            card["status"] = "sunset"
        if not COUNT_LAB_API:
            card["platforms"] = [name for name in card["platforms"] if name != "lab_api"]
        card["guaranteed_facts_verified"] = model_id in active and _guaranteed_verified(
            index, model_id, guaranteed, bool(card["guaranteed_facts_verified"]),
        )

    major_providers = {
        provider.id: provider.v1_availability_field
        for provider in registry.providers()
        if provider.v1_availability_field in MAJOR_PLATFORMS
    }
    for offering in inputs.offerings:
        model_id = offering["model"]
        card = cards.get(model_id)
        platform = major_providers.get(offering["provider"])
        if card is not None and model_id in active and platform:
            card["platforms"].append(platform)
    for card in cards.values():
        card["platforms"] = sorted(set(card["platforms"]))

    earliest = as_of - timedelta(days=365)
    pinned_domain = {board["id"]: board["domain"] for board in leaderboards()}
    boards = {}
    evidence_by_model = {}
    for model_id, evidence in index.corpus_evidence():
        card = cards.get(model_id)
        if (
            card is None
            or card["class_id"] not in SLICE_CLASSES
            or (evidence.date is not None and evidence.date > as_of)
            or not evidence.verified
            or not _verified_record(index, evidence.record_id)
        ):
            continue
        record = index.record(evidence.record_id)
        if model_id in active:
            evidence_by_model.setdefault(model_id, evidence)
        if evidence.date is None or evidence.date < earliest:
            continue
        metric = inputs.benchmark_metadata.get(evidence.benchmark_id)
        if metric is None or not inputs.benchmark_domains.get(evidence.benchmark_id):
            continue
        url = record.get("source_url") or index.source_url(evidence.source_ids[0])
        board_id = slice1_board_id(
            evidence.benchmark_id,
            harness=evidence.harness,
            version=evidence.version,
            source_url=url,
            configuration=record.get("configuration"),
        )
        if board_id not in pinned_domain:
            continue
        board = boards.setdefault(board_id, {
            "id": board_id,
            "domain": pinned_domain[board_id],
            "url": url,
            "direction": metric.get("direction", "higher_is_better"),
            "rows": [],
        })
        board["rows"].append({
            "name": record.get("model_id_as_evaluated") or model_id,
            "model_id": model_id,
            "score": evidence.value,
            "date": evidence.date.isoformat(),
            "org": card["provider"],
            "url": url,
        })

    cheapest = {}
    for offering in inputs.offerings:
        model_id = offering["model"]
        if model_id not in evidence_by_model:
            continue
        offering_id = "/".join(
            str(offering[key]) for key in ("provider", "model", "region", "tier")
        )
        prices = [index.fact(offering_id, f"offering.price.{kind}")
                  for kind in ("input", "output")]
        if not all(
            price.state == "known"
            and isinstance(price.value, (int, float)) and not isinstance(price.value, bool)
            and math.isfinite(price.value) and price.value >= 0
            and _verified_record(index, price.record_id)
            for price in prices
        ):
            continue
        input_record = index.record(prices[0].record_id)
        candidate = {
            "model_id": model_id,
            "class": cards[model_id]["class_id"],
            "input_price_per_million": prices[0].value,
            "output_price_per_million": prices[1].value,
            "benchmark_id": evidence_by_model[model_id].benchmark_id,
            "source_url": index.source_url(prices[0].sources[0]),
            "read_date": str(input_record["verification"]["date"])[:10],
            "prices_verified": True,
            "has_admitted_evidence": True,
        }
        price_key = (prices[0].value, prices[1].value)
        current = cheapest.get(model_id)
        if current is None or price_key < (
            current["input_price_per_million"], current["output_price_per_million"],
        ):
            cheapest[model_id] = candidate

    slice2 = yaml.safe_load((root / "premier/inputs/slice-2.yaml").read_text())
    current = yaml.safe_load((root / "premier/slice-1.yaml").read_text())
    reviewer_clauses = {}
    for row in current.get("models", []):
        clauses = [
            clause for clause in row.get("clauses", [])
            if clause.get("clause") == 4
            and (reason := (clause.get("note") or clause.get("reason") or "").strip())
            and reason != "Admission packet for human review"
        ]
        if clauses:
            reviewer_clauses[row["model_id"]] = clauses
    return {
        "cards": cards,
        "boards": sorted(boards.values(), key=lambda board: board["id"]),
        "budget_candidates": list(cheapest.values()),
        "local_candidates": local_candidate_universe(slice2["local"]["candidates"], root),
        "slice2": slice2,
        "reviewer_clauses": reviewer_clauses,
        "aliases": {},
    }
