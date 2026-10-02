"""Invariant checks over every inventoried claim. Findings never contain values."""

from __future__ import annotations

import math
from collections import defaultdict
from datetime import date
from functools import cache
from typing import Any
from urllib.parse import parse_qsl, urlsplit

from pydantic import ValidationError

from decision.excluded import excluded_sources
from decision.model import Fact, Model, Offering, Source, verification_counts
from decision.registry import Registry, UnknownIdError
from decision.verify import unit_id
from schema.benchmark import Metric
from scripts.data_trust.catalogue import Catalogue, Finding, day
from scripts.slo.report import load_config


def field_type(f: dict) -> str:
    name = str(f["field"])
    if f["kind"] == "evidence" or name.startswith("benchmarks.scores."):
        return "benchmark"
    if "price" in name or "cost" in name:
        return "price"
    if "context" in name or "token" in name:
        return "context"
    if name.startswith("plan.") or name.startswith("offering.subscription."):
        return "plan"
    if "speed" in name:
        return "speed"
    return "model"


@cache
def _targets():
    return load_config()


def slo_days(f: dict) -> int | None:
    targets = _targets()
    target = {
        "benchmark": "live-reading-age",
        "price": "offering-price-age",
        "plan": "plan-age",
        "speed": "premier-speed-age",
    }.get(field_type(f))
    if target is None:
        return None
    t = targets.target(target)
    return int(t.params["max_age_days"]) if t.in_force else None


def safe_url(url: Any) -> bool:
    """Credential-bearing URLs are never sent to the network or saved in reports."""
    try:
        p = urlsplit(str(url))
        return (
            p.scheme in ("http", "https")
            and bool(p.hostname)
            and not p.username
            and not p.password
            and not any(
                k.lower() in {"token", "api_key", "key", "password", "secret", "authorization"}
                for k, _ in parse_qsl(p.query)
            )
        )
    except ValueError:
        return False


def source_urls(f: dict, c: Catalogue) -> list[str]:
    urls = []
    for ref in f.get("sources") or []:
        if isinstance(ref, str):
            url = ref
        elif isinstance(ref, dict):
            url = ref.get("url") or c.sources.get(ref.get("source_id"), {}).get("url")
        else:
            continue
        if url:
            urls.append(str(url))
    if f.get("source_url"):
        urls.append(str(f["source_url"]))
    if f.get("source_id") in c.sources:
        urls.append(str(c.sources[f["source_id"]]["url"]))
    return urls


def run(c: Catalogue, registry: Registry, as_of: date, snapshot: dict | None = None) -> dict:
    findings = list(c.findings)

    def add(f, rule, severity="error"):
        findings.append(Finding(str(f["id"]), str(f.get("field") or "record"), rule, severity))

    for mid, card in c.models.items():
        try:
            Model.model_validate({"id": mid, "lifecycle": card.get("lifecycle", "active")})
        except ValidationError:
            findings.append(Finding(mid, "model", "model_schema"))
    for sid, source in c.sources.items():
        try:
            Source.model_validate(source)
        except ValidationError:
            findings.append(Finding(sid, "source", "source_schema"))
    for bid, board in c.boards.items():
        try:
            Metric.model_validate(board.get("metric") or {})
            for tag in board.get("domains") or []:
                registry.domain(tag["id"])
                if tag.get("directness") not in ("direct", "proxy"):
                    raise ValueError("invalid directness")
        except (ValidationError, UnknownIdError, ValueError, KeyError):
            findings.append(Finding(bid, "metric_or_domains", "benchmark_schema"))
    seen = set()
    grouped = defaultdict(list)
    values = defaultdict(dict)
    weights_by_model = defaultdict(list)
    served = [f for f in c.facts if f["kind"] != "legacy"]
    for f in served:
        if f["id"] in seen:
            add(f, "duplicate_id")
        seen.add(f["id"])
        subject, name = f["subject_id"], f["field"]
        if name == "model.weights_openness":
            weights_by_model[subject].append(f)
        if subject not in c.models and subject not in c.offerings:
            add(f, "subject_resolves")
        unknown = f.get("state") == "unknown"
        # Unknown is absence of a claim, so it needs no fabricated source/date.
        if not unknown:
            urls = source_urls(f, c)
            if not urls:
                add(f, "source_required")
            for ref in f.get("sources") or []:
                if (
                    isinstance(ref, dict)
                    and ref.get("source_id")
                    and ref["source_id"] not in c.sources
                ):
                    add(f, "source_id_resolves")
            if any(not safe_url(url) for url in urls):
                add(f, "source_url_valid")
            if any(excluded_sources().url(url) for url in urls):
                add(f, "excluded_source")
            read = day(f.get("read_date"))
            if read is None:
                add(f, "read_date_required")
            elif read > as_of:
                add(f, "read_date_future")
            elif (limit := slo_days(f)) is not None and (as_of - read).days > limit:
                add(f, "field_slo", "warning")
            grouped[
                (
                    subject,
                    name,
                    f.get("effort"),
                    f.get("harness"),
                    f.get("evidence_date"),
                    f.get("benchmark_version"),
                    f.get("configuration"),
                )
            ].append(f)
            values[subject][name] = f.get("value")
        if f["kind"] == "fact":
            try:
                facet = registry.facet(name)
                if f.get("unit") and f["unit"] != facet.unit:
                    add(f, "unit_matches_facet")
                raw = {k: f[k] for k in Fact.model_fields if k in f}
                if not raw.get("verification"):
                    raw.pop("verification", None)
                raw.setdefault(
                    "subject",
                    {"kind": "model" if subject in c.models else "offering", "id": subject},
                )
                Fact.model_validate(raw, context={"registry": registry})
                if facet.value_type.values_from == "model_ids" and isinstance(f.get("value"), list):
                    if any(mid not in c.models for mid in f["value"]):
                        add(f, "model_id_resolves")
            except UnknownIdError:
                add(f, "facet_resolves")
            except (ValidationError, ValueError, TypeError):
                add(f, "fact_schema")
        value = f.get("value")
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            if not math.isfinite(value):
                add(f, "finite_number")
            if field_type(f) in ("price", "context"):
                if value < 0:
                    add(f, "nonnegative")
                ceiling = 1_000_000 if field_type(f) == "price" else 100_000_000
                if value > ceiling:
                    add(f, "plausible_magnitude")
        if f["kind"] == "evidence" or str(name).startswith("benchmarks.scores."):
            bid = name if f["kind"] == "evidence" else name.removeprefix("benchmarks.scores.")
            board = c.boards.get(bid)
            if board is None:
                add(f, "benchmark_resolves")
            else:
                metric = board.get("metric") or {}
                low, high = metric.get("min_score", 0), metric.get("max_score")
                if not isinstance(value, (int, float)) or isinstance(value, bool):
                    add(f, "benchmark_numeric")
                elif value < low or high is not None and value > high:
                    add(f, "benchmark_range")
                elif high is None:
                    add(f, "benchmark_range_unbounded", "warning")
            # Admission permits an unknown date; after-filtering refuses it.
            if f.get("evidence_date") and day(f["evidence_date"]) is None:
                add(f, "benchmark_date_valid")
            elif day(f.get("evidence_date")) and day(f["evidence_date"]) > as_of:
                add(f, "benchmark_date_future")
            board_unit = (board.get("metric") or {}).get("unit") if board else None
            if (
                f.get("unit")
                and board
                and (unit_id(f["unit"]) or f["unit"]) != (unit_id(board_unit) or board_unit)
            ):
                add(f, "benchmark_unit", "warning")

    for rows in grouped.values():
        for i, left in enumerate(rows):
            for right in rows[i + 1 :]:
                if left.get("value") != right.get("value") and set(source_urls(left, c)) != set(
                    source_urls(right, c)
                ):
                    add(left, "cross_source_contradiction", "warning")
                    add(right, "cross_source_contradiction", "warning")
    for subject, fields in values.items():
        pairs = [
            ("offering.price.cached_input", "offering.price.input"),
            ("offering.price.batch_input", "offering.price.input"),
            ("offering.price.batch_output", "offering.price.output"),
            ("pricing.cached_input", "pricing.input"),
            ("pricing.batch_input", "pricing.input"),
            ("pricing.batch_output", "pricing.output"),
            ("cost.cache_read", "cost.input"),
            ("cost.batch_input", "cost.input"),
            ("cost.batch_output", "cost.output"),
        ]
        for discount, standard in pairs:
            a, b = fields.get(discount), fields.get(standard)
            if all(isinstance(v, (int, float)) for v in (a, b)) and a > b:
                add({"id": subject, "field": discount}, "discount_le_standard")

    offered = set()
    for oid, o in c.offerings.items():
        if "model" in o:
            try:
                Offering.model_validate({**o, "facts": []}, context={"registry": registry})
            except ValidationError:
                add({"id": oid, "field": "offering"}, "offering_schema")
            if o["model"] not in c.models:
                add({"id": oid, "field": "model"}, "model_id_resolves")
            offered.add(o["model"])
        try:
            registry.plan_owner(o["provider"])
        except (UnknownIdError, KeyError):
            add({"id": oid, "field": "provider"}, "provider_resolves")
        for f in o.get("facts") or []:
            if f.get("facet") == "offering.subscription.models_covered" and isinstance(
                f.get("value"), list
            ):
                offered.update(f["value"])
                for mid in f["value"]:
                    if mid not in c.models:
                        add({"id": oid, "field": f["facet"]}, "model_id_resolves")
    for mid, card in c.models.items():
        if card.get("lifecycle", card.get("status", "active")) in (
            "retired",
            "deprecated",
            "sunset",
        ):
            continue
        weights = weights_by_model[mid]
        open_sourced = any(_open_weights(f, c) for f in weights)
        if mid not in offered and not open_sourced:
            add(
                {"id": mid, "field": "model.weights_openness"},
                "offering_or_verified_open_weights",
                "warning",
            )
    if snapshot is not None:
        for candidate in snapshot.get("lineup", {}).get("candidates", []):
            kind, id_ = candidate.get("kind"), candidate.get("id")
            table = c.models if kind == "model" else c.offerings
            if id_ not in table:
                add({"id": id_, "field": "snapshot.lineup"}, "snapshot_id_resolves")
        for facet in snapshot.get("facet_subjects", {}):
            try:
                registry.facet(facet)
            except UnknownIdError:
                add({"id": "snapshot", "field": facet}, "facet_resolves")
    findings = sorted(set(findings), key=lambda f: (f.severity, f.rule, f.id, f.field))
    return {
        "facts": len(served),
        "served_counts": c.served_counts,
        "legacy_provenance": provenance(c),
        "benchmark_range_classes": range_classes(served, c),
        "offering_rule_status": "warning until MODEL-266 PR #456 merges",
        "models": len(c.models),
        "offerings": len(c.offerings),
        "errors": sum(f.severity == "error" for f in findings),
        "warnings": sum(f.severity == "warning" for f in findings),
        "findings": [f.__dict__ for f in findings],
    }


def _open_weights(f, c):
    v = f.get("verification") or {}
    try:
        return (
            f.get("state") == "known"
            and f.get("value") == "open_weights"
            and bool(source_urls(f, c))
            and all(safe_url(u) and not excluded_sources().url(u) for u in source_urls(f, c))
            and v.get("outcome") == "verified"
            and verification_counts(
                v["outcome"], v["collector"]["model_family"], v["verifier"]["model_family"]
            )
        )
    except KeyError:
        return False


def provenance(c: Catalogue) -> dict:
    """Field-level coverage only. A card-wide source list is not a citation."""
    families = defaultdict(lambda: {"fields": 0, "sourced": 0})
    rows = [*c.legacy, *(f for f in c.facts if f["kind"] == "legacy")]
    for f in rows:
        family = str(f["field"]).split(".")[0] if f["kind"] == "legacy" else f["kind"]
        families[family]["fields"] += 1
        families[family]["sourced"] += bool(source_urls(f, c))

    def metric(row):
        return {**row, "share": row["sourced"] / row["fields"] if row["fields"] else None}

    total = {"fields": len(rows), "sourced": sum(r["sourced"] for r in families.values())}
    return {
        **metric(total),
        "by_family": {k: metric(v) for k, v in sorted(families.items())},
        "range_classes": range_classes(rows, c),
    }


def range_classes(rows: list[dict], c: Catalogue) -> dict:
    counts = defaultdict(int)
    for f in rows:
        name, value = str(f["field"]), f.get("value")
        if f["kind"] != "evidence" and not name.startswith("benchmarks.scores."):
            continue
        bid = name.removeprefix("benchmarks.scores.")
        metric = c.boards.get(bid, {}).get("metric", {})
        high = metric.get("max_score")
        if (
            isinstance(value, (int, float))
            and not isinstance(value, bool)
            and (value < metric.get("min_score", 0) or high is not None and value > high)
        ):
            counts[bid] += 1
    return dict(sorted(counts.items()))
