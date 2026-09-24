"""Turn the cards, the benchmark pages and the eligibility report into JSON.

One export feeds every consumer: the static pages for both sites and, later,
the CLI snapshot and the recommender. Producing it once means the site and the
CLI can never disagree about what the data says.

Every export carries the build date, the commit it came from, and
`export_schema_version` so a published page is traceable to a revision and a
consumer can tell when the JSON *shape* changed. That field is not the CLI
`--json` envelope (`schema_version` "1.0") and not the ranking-report document
(`rankings.json` top-level `schema_version` "2.0").
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
from schema.card import applicability_block

#: Shape of the published JSON tree (`/api/index.json`, per-model files,
#: `/api/rank/candidates.json`, `/api/rank/profiles.json`, graph views).
#: Bump the major when a consumer pinning this value would mis-parse those
#: files. Leave it alone for additive fields.
#:
#: Distinct from:
#: * CLI envelope `schema_version` (`cli.modelspec.offline.SCHEMA_VERSION`, "1.0")
#: * ranking-report `schema_version` (`rankings.json` and `pipeline.ranking` JSON,
#:   "2.0") — that file is not what the CLI snapshot fetches. The two now hold
#:   the same *string*; they remain different fields in different files, and a
#:   consumer tells them apart by name, not by value.
#:
#: 1.0 -> 2.0 (MODEL-77). `/api/models/<id>.json` publishes the card
#: frontmatter verbatim, so the policy reshape is a change to this tree:
#: `licensing.commercial_use` stopped being `true | false | null` and became a
#: `UsePermission` string that includes two values no 1.x consumer has ever
#: seen (`restricted`, `withheld`), and
#: `availability.primary_provider.data_residency` stopped being a list and
#: became `list | null` beside a new `data_residency_disclosure`. Both are
#: range-widening under the MODEL-59 rule, and they ship as one bump because
#: they are one decision. See `docs/cli-contract.md`.
#:
#: 2.0 -> 3.0 (MODEL-98). `model_type` gained `decision-model`, a value no
#: consumer switching on that field has ever seen, published in
#: `/api/models/<id>.json`, `index.json`, `/api/rank/candidates.json` and the
#: graph nodes. A new enum value is the textbook widening in the MODEL-59 rule.
#: MODEL-97's applicability block rides this bump but did not require it: it
#: adds a key rather than widening a field, and is additive on its own. See
#: `docs/design/class-and-null-semantics.md`.
EXPORT_SCHEMA_VERSION = "3.0"


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
        return {
            "commit": self.commit,
            "built_at": self.built_at,
            "eligibility_as_of": self.as_of.isoformat(),
            "export_schema_version": EXPORT_SCHEMA_VERSION,
        }


def make_build(catalogue: Catalogue, root: Path | None = None) -> Build:
    return Build(
        commit=_commit(root or REPO_ROOT),
        built_at=datetime.now(UTC).isoformat(timespec="seconds"),
        as_of=catalogue.as_of,
    )


#: What an evidence record says about its own score beyond the date and source.
#: A flat card score says none of it, so these are null on its row, not absent.
_EVIDENCE_ROW_KEYS = ("unit", "date_type", "source_kind", "model_id_as_evaluated",
                      "benchmark_version", "configuration", "verified_at")


def _coverage_row(model: Model, score: float, as_of: Any, source: Any,
                  attribution: str, record: dict[str, Any]) -> dict[str, Any]:
    return {
        "model_id": model.model_id,
        "display_name": model.display_name,
        "provider": model.provider,
        "provider_display": model.provider_display,
        "score": score,
        "as_of": as_of,
        "source": source,
        "attribution": attribution,
        **{key: record.get(key) for key in _EVIDENCE_ROW_KEYS},
    }


def models_by_benchmark(models: list[Model],
                        benchmarks: list[Benchmark]) -> dict[str, list[dict[str, Any]]]:
    """Which models report each benchmark, derived from the cards, best first.

    Never authored on the benchmark page. Every row carries its own date and
    attribution, so a reader can see how old a number is and who stands behind
    it rather than being shown a bare figure.

    A reviewed evidence record is `verified` and dated by its own
    `evidence_date`. A card can hold several for one benchmark (a provider's
    claim beside an independent run), and each is its own row. A flat card
    score is `unverified-legacy`, dated by the card's one collection date, and
    is dropped where the same card has evidence for that benchmark: it is the
    same measurement, checked. The ranking engine applies the same precedence.
    """
    index: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for model in models:
        for record in model.evidence:
            index[str(record["benchmark_id"])].append(_coverage_row(
                model, record["score"], record.get("evidence_date"),
                record.get("source_url"), "verified", record))
        reviewed = {str(record["benchmark_id"]) for record in model.evidence}
        for key, value in model.scores.items():
            if key not in reviewed:
                index[key].append(_coverage_row(
                    model, value, model.scores_as_of, model.scores_source,
                    "unverified-legacy", {}))
    ascending = {b.benchmark_id for b in benchmarks if b.lower_is_better}
    for key, rows in index.items():
        sign = 1.0 if key in ascending else -1.0
        rows.sort(key=lambda r: (sign * float(r["score"]), r["display_name"].lower()))
    return dict(index)


def models_reporting(rows: list[dict[str, Any]]) -> int:
    """Distinct models in one benchmark's coverage; one model can hold several rows."""
    return len({row["model_id"] for row in rows})


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
    coverage = models_by_benchmark(models, benchmarks)

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
            # MODEL-97. Derived from the card's class, never stored on it, so
            # the `card` tree above stays the frontmatter verbatim and no
            # field in it changes type, name, meaning or range. A consumer
            # that ignores this key reads exactly what it read before; one
            # that reads it can tell a null nobody has researched from a null
            # this class can never have.
            "applicability": applicability_block(
                model.front.get("model_type"), model.front.get("model_subtypes") or (),
                card=model.front),
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
        benchmark_summary(b, catalogue, models_reporting(coverage.get(b.benchmark_id, [])))
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
