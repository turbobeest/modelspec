"""Turn the cards, the benchmark pages and the eligibility report into JSON.

One export feeds every consumer: the static pages for both sites and, later,
the CLI snapshot and the recommender. Producing it once means the site and the
CLI can never disagree about what the data says.

Every export carries the build date and the commit it came from, so a published
page is traceable to a revision.
"""

from __future__ import annotations

import json
import subprocess
from collections import defaultdict
from dataclasses import dataclass
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

from pipeline.load import REPO_ROOT, Benchmark, Catalogue, Model


def _commit(root: Path) -> str:
    try:
        out = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True, text=True, cwd=str(root), check=True,
        )
        return out.stdout.strip()
    except (subprocess.CalledProcessError, OSError):
        return "unknown"


@dataclass(frozen=True)
class Build:
    commit: str
    built_at: str
    as_of: date

    def to_json(self) -> dict[str, Any]:
        return {"commit": self.commit, "built_at": self.built_at, "eligibility_as_of": self.as_of.isoformat()}


def make_build(catalogue: Catalogue, root: Path | None = None) -> Build:
    return Build(
        commit=_commit(root or REPO_ROOT),
        built_at=datetime.now(UTC).isoformat(timespec="seconds"),
        as_of=catalogue.as_of,
    )


def models_by_benchmark(models: list[Model]) -> dict[str, list[dict[str, Any]]]:
    """Which models report each benchmark, derived from the cards.

    Never authored on the benchmark page. Each entry carries the date and source
    the card claims for its scores, so a reader can see how old the number is
    rather than being shown a bare figure.
    """
    index: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for model in models:
        for key, value in model.scores.items():
            index[key].append({
                "model_id": model.model_id,
                "display_name": model.display_name,
                "provider": model.provider,
                "provider_display": model.provider_display,
                "score": value,
                "as_of": model.scores_as_of,
                "source": model.scores_source,
                "attribution": "unverified-legacy",
            })
    for rows in index.values():
        rows.sort(key=lambda r: (-float(r["score"]), r["display_name"].lower()))
    return dict(index)


def model_summary(model: Model) -> dict[str, Any]:
    front = model.front
    return {
        "model_id": model.model_id,
        "display_name": model.display_name,
        "provider": model.provider,
        "provider_display": model.provider_display,
        "family": front.get("family"),
        "status": front.get("status"),
        "model_type": front.get("model_type"),
        "release_date": str(front.get("release_date") or "") or None,
        "score_count": len(model.scores),
        "scores_as_of": model.scores_as_of,
    }


def benchmark_summary(bench: Benchmark, catalogue: Catalogue, covered: int) -> dict[str, Any]:
    disposition = catalogue.for_benchmark(bench.benchmark_id)
    return {
        "id": bench.benchmark_id,
        "name": bench.name,
        "category": bench.category,
        "summary": bench.summary,
        "aliases": bench.aliases,
        "disposition": disposition.status,
        "canonical_id": disposition.canonical_id,
        "reasons": list(disposition.reasons),
        "models_covered": covered,
    }


#: What a given site's API actually needs. modelspec.dev links out to
#: benchgraph.dev for benchmark detail and vice versa, so shipping both full
#: sets into both trees would double the deployment for no reader.
PARTS_ALL = ("index", "models", "catalogue", "benchmarks")


def write(out_dir: Path, models: list[Model], benchmarks: list[Benchmark],
          catalogue: Catalogue, build: Build,
          parts: tuple[str, ...] = PARTS_ALL) -> dict[str, int]:
    """Write the export tree. Returns counts for the run summary."""
    out_dir.mkdir(parents=True, exist_ok=True)
    coverage = models_by_benchmark(models)

    def dump(rel: str, payload: Any) -> None:
        path = out_dir / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=1, sort_keys=True, default=str), encoding="utf-8")

    dump("build.json", build.to_json())

    if "models" in parts:
      for model in models:
        dump(f"models/{model.model_id}.json", {
            "build": build.to_json(),
            "card": model.front,
            "body": model.body,
        })

    if "benchmarks" in parts:
      for bench in benchmarks:
        disposition = catalogue.for_benchmark(bench.benchmark_id)
        dump(f"benchmarks/{bench.benchmark_id}.json", {
            "build": build.to_json(),
            "page": bench.front,
            "body": bench.body,
            "disposition": {
                "status": disposition.status,
                "canonical_id": disposition.canonical_id,
                "reasons": list(disposition.reasons),
                "verified_results": list(disposition.results),
            },
            "models_covered": coverage.get(bench.benchmark_id, []),
        })

    if "index" in parts:
        dump("index.json", {
            "build": build.to_json(),
            "count": len(models),
            "models": [model_summary(m) for m in models],
        })

    catalogue_rows = [
        benchmark_summary(b, catalogue, len(coverage.get(b.benchmark_id, [])))
        for b in benchmarks
    ]
    by_status: dict[str, list[str]] = defaultdict(list)
    for row in catalogue_rows:
        by_status[str(row["disposition"])].append(str(row["id"]))
    if "catalogue" in parts:
      dump("catalogue.json", {
        "build": build.to_json(),
        "eligibility_as_of": catalogue.as_of.isoformat(),
        "active_ids": catalogue.active_ids,
        "counts": {k: len(v) for k, v in sorted(by_status.items())},
        "benchmarks": catalogue_rows,
    })

    return {
        "models": len(models),
        "benchmarks": len(benchmarks),
        "active": len(catalogue.active_ids),
        "score_keys": len(coverage),
    }
