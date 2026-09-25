"""Validate MODEL-129 capability estimates against the admitted snapshot evidence."""

from __future__ import annotations

import argparse
import json
import statistics
import time
from collections.abc import Mapping
from datetime import date
from pathlib import Path
from typing import Any

from decision.capability import (
    BenchmarkSpec,
    CapabilityObservation,
    backtest_capabilities,
    backtest_newest_capabilities,
)
from decision.contract import parse_spec
from decision.engine import decide
from decision.excluded import excluded_sources
from decision.registry import default as default_registry
from decision.snapshot import (
    LoadedSnapshot,
    build_snapshot,
    collect_repo,
    load_premier,
    load_snapshot_bytes,
)

ROOT = Path(__file__).resolve().parents[1]


def _observations(snapshot: LoadedSnapshot) -> list[CapabilityObservation]:
    tags = snapshot.benchmark_domain_tags()
    rows: list[CapabilityObservation] = []
    for model_id in snapshot.candidates():
        if snapshot.kind(model_id) != "model":
            continue
        for benchmark_id, domains in tags.items():
            for row in snapshot.evidence(model_id, benchmark_id):
                if row.date is None or row.record_id is None:
                    continue
                rows.append(
                    CapabilityObservation(
                        model_id=model_id,
                        benchmark_id=benchmark_id,
                        value=float(row.value),
                        unit=row.unit,
                        measured_by=row.measured_by,
                        date=row.date,
                        record_id=row.record_id,
                        version=row.version,
                        domains=domains,
                    )
                )
    return rows


def _disagreements(
    snapshot: LoadedSnapshot, metadata: Mapping[str, Mapping[str, Any]]
) -> list[dict[str, Any]]:
    tags = snapshot.benchmark_domain_tags()
    models = [cid for cid in snapshot.candidates() if snapshot.kind(cid) == "model"]
    rows = []
    for domain in snapshot.domain_ids():
        estimated = [
            (snapshot.capability_estimate(model_id, domain), model_id) for model_id in models
        ]
        estimated = [(estimate, model_id) for estimate, model_id in estimated if estimate]
        if not estimated:
            continue
        estimate_top = max(estimated, key=lambda pair: (pair[0].value, pair[1]))[1]
        for benchmark, domain_tags in sorted(tags.items()):
            directness = dict(domain_tags).get(domain)
            if directness is None:
                continue
            candidates = []
            direction = metadata.get(benchmark, {}).get("direction", "higher_is_better")
            for model_id in models:
                evidence = snapshot.evidence(model_id, benchmark)
                if not evidence:
                    continue
                leader = sorted(
                    evidence,
                    key=lambda item: (
                        item.value if direction == "higher_is_better" else -item.value,
                        item.date or date.min,
                        item.record_id or "",
                    ),
                    reverse=True,
                )[0]
                candidates.append((leader, model_id))
            if not candidates:
                continue
            single, single_top = max(
                candidates,
                key=lambda pair: (
                    pair[0].value if direction == "higher_is_better" else -pair[0].value,
                    pair[1],
                ),
            )
            if single_top == estimate_top:
                continue
            rows.append(
                {
                    "domain": domain,
                    "benchmark": benchmark,
                    "directness": directness,
                    "estimate_top": estimate_top,
                    "single_benchmark_top": single_top,
                    "single_benchmark_date": single.date.isoformat() if single.date else None,
                    "sources": sorted(snapshot.source_url(source) for source in single.source_ids),
                    "reason": (
                        "the estimate combines every tagged item with learned "
                        "discrimination, source offset, directness and recency; the "
                        "benchmark row uses one measurement"
                    ),
                }
            )
    return rows


def validate(root: Path, report_date: date) -> dict[str, Any]:
    registry = default_registry()
    inputs = collect_repo(root)
    snapshot = build_snapshot(
        inputs,
        registry=registry,
        premier=load_premier(root / "premier" / "slice-1.yaml"),
        as_of=report_date,
        guard=excluded_sources(),
        gate=False,
    )
    loaded = load_snapshot_bytes(snapshot.to_bytes(key=None), key=None)
    observations = _observations(loaded)
    specs = {
        benchmark: BenchmarkSpec(
            random_baseline=metadata.get("random_baseline"),
            sample_size=metadata.get("sample_size"),
            direction=metadata.get("direction", "higher_is_better"),
        )
        for benchmark, metadata in inputs.benchmark_metadata.items()
    }
    held_cells = backtest_capabilities(observations, specs, as_of=report_date)
    held_newest = backtest_newest_capabilities(observations, specs, as_of=report_date)

    timings = []
    for domain in loaded.domain_ids():
        spec = parse_spec(
            {
                "spec_version": 1,
                "optimize": {"max": domain},
                "explain": "summary",
                "limit": 10,
            },
            facets=registry.facet,
        )
        started = time.perf_counter()
        decide(spec, loaded, facets=registry.facet)
        timings.append((time.perf_counter() - started) * 1000)

    return {
        "date": report_date.isoformat(),
        "snapshot": loaded.snapshot_id,
        "models": sum(loaded.kind(cid) == "model" for cid in loaded.candidates()),
        "observations": len(observations),
        "items": len(loaded.capability_items),
        "domains": len(loaded.domain_ids()),
        "holdout_cells": held_cells.__dict__,
        "holdout_newest": held_newest.__dict__,
        "summary_latency_ms": {
            "median": statistics.median(timings),
            "max": max(timings),
            "runs": len(timings),
            "environment": "local Worker-equivalent Python decision path",
        },
        "disagreements": _disagreements(loaded, inputs.benchmark_metadata),
    }


def _markdown(result: dict[str, Any]) -> str:
    cells, newest = result["holdout_cells"], result["holdout_newest"]
    latency = result["summary_latency_ms"]
    lines = [
        "# Capability model validation",
        "",
        f"Date: {result['date']}; snapshot: `{result['snapshot']}`.",
        "",
        f"The fit used {result['observations']} admitted observations over "
        f"{result['models']} lineup models, {result['items']} learned items and "
        f"{result['domains']} registry domains.",
        "",
        "## Backtests",
        "",
        "Errors are RMSE after scaling each held-out value by its benchmark's spread.",
        "",
        f"- Benchmark-cell holdout ({cells['cells']} predictions): model "
        f"{cells['model_rmse']:.4f}; benchmark-mean baseline {cells['naive_rmse']:.4f}.",
        f"- Each model's newest eligible score ({newest['cells']} predictions): model "
        f"{newest['model_rmse']:.4f}; benchmark-mean baseline {newest['naive_rmse']:.4f}.",
        "",
        "## Request latency",
        "",
        f"`explain: summary` over all {latency['runs']} domain objectives: median "
        f"{latency['median']:.1f} ms; maximum {latency['max']:.1f} ms. "
        f"Measured on the {latency['environment']}; this is not a deployed-Worker network timing.",
        "",
        "## Estimate/single-benchmark disagreements",
        "",
        "Each row compares the estimate leader with the best admitted raw score on one tagged "
        "benchmark. A disagreement is expected when the other evidence, learned item "
        "discrimination, source offset, directness or recency changes the combined ordering.",
        "",
        "| Domain | Benchmark | Tag | Estimate leader | Single-benchmark leader | Reading |",
        "|---|---|---|---|---|---|",
    ]
    for row in result["disagreements"]:
        links = ", ".join(f"[{index + 1}]({url})" for index, url in enumerate(row["sources"]))
        reading = row["single_benchmark_date"] or "date unavailable"
        if links:
            reading += "; " + links
        lines.append(
            f"| `{row['domain']}` | `{row['benchmark']}` | {row['directness']} | "
            f"`{row['estimate_top']}` | `{row['single_benchmark_top']}` | {reading} |"
        )
    if not result["disagreements"]:
        lines.append("| — | No disagreements | — | — | — | — |")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--date", type=date.fromisoformat, default=date.today())
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = validate(args.root.resolve(), args.date)
    output = args.output or args.root / "docs" / "validation" / "capability-model.md"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(_markdown(result), encoding="utf-8")
    output.with_suffix(".json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
