"""Read the repository's sources of truth into plain Python objects.

Three sources, in dependency order:

* `models/`     — one Markdown file per model card, YAML front matter.
* `benchmarks/` — one Markdown file per benchmark page, YAML front matter.
* the eligibility report — which benchmarks may be presented as current.

Nothing here reaches the network and nothing writes. The loader is deliberately
tolerant about *absent* data and strict about *malformed* data: a missing
optional field is normal in a 692-field schema where null means "not yet
researched", but a file that claims to be a card and will not parse is a defect
worth surfacing.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
FRONT_MATTER = re.compile(r"^---\n(.*?)\n---\n?(.*)\Z", re.S)

#: Prose that lives beside the data and is not itself data.
NOT_CONTENT = {"LICENSE.md", "README.md", "AUTHORING.md", "CONTRIBUTING.md"}


class LoadError(RuntimeError):
    """A file that should have parsed did not."""


def split_front_matter(text: str) -> tuple[dict[str, Any], str]:
    match = FRONT_MATTER.match(text)
    if not match:
        raise LoadError("no YAML front matter")
    try:
        front = yaml.safe_load(match.group(1))
    except yaml.YAMLError as exc:
        raise LoadError(f"front matter is not valid YAML: {exc}") from exc
    if not isinstance(front, dict):
        raise LoadError("front matter is not a mapping")
    return front, match.group(2)


@dataclass(frozen=True)
class Model:
    model_id: str
    path: Path
    front: dict[str, Any]
    body: str

    @property
    def slug(self) -> str:
        return self.model_id

    @property
    def display_name(self) -> str:
        return str(self.front.get("display_name") or self.model_id)

    @property
    def provider(self) -> str:
        return str(self.front.get("provider") or self.path.parent.name)

    @property
    def provider_display(self) -> str:
        return str(self.front.get("provider_display") or self.provider)

    @property
    def scores(self) -> dict[str, float]:
        block = self.front.get("benchmarks") or {}
        raw = block.get("scores") if isinstance(block, dict) else None
        if not isinstance(raw, dict):
            return {}
        return {k: v for k, v in raw.items() if isinstance(v, (int, float))}

    @property
    def scores_as_of(self) -> str | None:
        block = self.front.get("benchmarks") or {}
        value = block.get("benchmark_as_of") if isinstance(block, dict) else None
        return str(value) if value else None

    @property
    def scores_source(self) -> str | None:
        block = self.front.get("benchmarks") or {}
        value = block.get("benchmark_source") if isinstance(block, dict) else None
        return str(value) if value else None


@dataclass(frozen=True)
class Benchmark:
    benchmark_id: str
    path: Path
    front: dict[str, Any]
    body: str

    @property
    def name(self) -> str:
        return str(self.front.get("name") or self.benchmark_id)

    @property
    def category(self) -> str:
        return str(self.front.get("category") or "uncategorised")

    @property
    def summary(self) -> str:
        return str(self.front.get("summary") or "").strip()

    @property
    def aliases(self) -> list[str]:
        raw = self.front.get("aliases")
        return [str(a) for a in raw] if isinstance(raw, list) else []


@dataclass(frozen=True)
class Disposition:
    """One benchmark's standing in the active catalogue.

    `status` is the spec's vocabulary: active, historical, unverified, alias, or
    unassessed for a discovery lead nobody has evaluated yet. `unassessed` is not
    a judgement — the spec is explicit that missing evidence is not staleness and
    not illegitimacy.
    """

    status: str
    canonical_id: str
    reasons: tuple[str, ...] = ()
    results: tuple[dict[str, Any], ...] = ()

    @property
    def is_active(self) -> bool:
        return self.status == "active"


@dataclass
class Catalogue:
    as_of: date
    dispositions: dict[str, Disposition] = field(default_factory=dict)

    def for_benchmark(self, benchmark_id: str) -> Disposition:
        return self.dispositions.get(
            benchmark_id, Disposition(status="unassessed", canonical_id=benchmark_id)
        )

    @property
    def active_ids(self) -> list[str]:
        return sorted(i for i, d in self.dispositions.items() if d.is_active)


def load_models(root: Path | None = None) -> list[Model]:
    directory = (root or REPO_ROOT) / "models"
    out: list[Model] = []
    for path in sorted(directory.rglob("*.md")):
        if path.name in NOT_CONTENT:
            continue
        front, body = split_front_matter(path.read_text(encoding="utf-8", errors="replace"))
        model_id = front.get("model_id")
        if not model_id:
            # Prose without a model_id is not a card; skip rather than fail, the
            # same rule the PR validator applies.
            continue
        out.append(Model(str(model_id), path, front, body))
    return out


def load_benchmarks(root: Path | None = None) -> list[Benchmark]:
    directory = (root or REPO_ROOT) / "benchmarks"
    out: list[Benchmark] = []
    seen: dict[str, Path] = {}
    for path in sorted(directory.glob("*.md")):
        if path.name in NOT_CONTENT:
            continue
        front, body = split_front_matter(path.read_text(encoding="utf-8", errors="replace"))
        benchmark_id = front.get("id")
        if not benchmark_id:
            raise LoadError(f"{path}: benchmark page has no id")
        benchmark_id = str(benchmark_id)
        if benchmark_id in seen:
            raise LoadError(f"duplicate benchmark id {benchmark_id!r}: {seen[benchmark_id]} and {path}")
        seen[benchmark_id] = path
        out.append(Benchmark(benchmark_id, path, front, body))
    return out


def load_catalogue(root: Path | None = None) -> Catalogue:
    """Read the eligibility report.

    Absent report means an empty active set, which the spec says is a valid
    outcome. It must never fall back to treating the census queue as a catalogue.
    """
    path = (root or REPO_ROOT) / "benchmarks/_census/eligibility/current-report.json"
    if not path.is_file():
        return Catalogue(as_of=date.today())
    report = json.loads(path.read_text(encoding="utf-8"))
    as_of = date.fromisoformat(str(report["as_of"]))
    dispositions: dict[str, Disposition] = {}
    for row in report.get("rows", []):
        dispositions[str(row["candidate_id"])] = Disposition(
            status=str(row["status"]),
            canonical_id=str(row.get("canonical_id") or row["candidate_id"]),
            reasons=tuple(str(r) for r in row.get("reasons", [])),
            results=tuple(row.get("accepted_results", [])),
        )
    return Catalogue(as_of=as_of, dispositions=dispositions)
