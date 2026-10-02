"""The AEO prompt inventory: load it, validate it, report its coverage (MODEL-254).

    python -m scripts.aeo.inventory PATH [--coverage]

The inventory itself is private (``modelspec-business/aeo/prompts.yaml``): it
records who we think buys and how they phrase it. This module is the public
half, so the measurement harness (MODEL-256) and any reviewer read the file the
same way. Contract: ``docs/aeo/prompt-inventory.md``.

The JSON Schema (``schemas/aeo-prompt-inventory-v1.schema.json``) holds the
shape. The checks it cannot express live here:

* ids are unique;
* a ``constrained`` prompt names at least one constraint, and every constraint
  is a facet or capability domain the decision registry knows, so the engine
  can actually answer the question the prompt asks;
* a ``template`` names a decide template that exists;
* a ``disambiguation`` prompt succeeds only by being ``disambiguated``, and no
  other prompt may claim that outcome.

``--coverage`` adds the bar the inventory must clear before measurement starts:
25 to 40 prompts, at least 4 in every cluster.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = ROOT / "schemas" / "aeo-prompt-inventory-v1.schema.json"
TEMPLATES_PATH = ROOT / "registry" / "templates.yaml"

CLUSTERS = ("category", "constrained", "agent", "disambiguation")
MIN_PER_CLUSTER = 4
TOTAL_RANGE = (25, 40)


@dataclass(frozen=True)
class Vocabulary:
    """What a constrained prompt may name."""

    facets: frozenset[str]
    domains: frozenset[str]
    templates: frozenset[str]

    @classmethod
    def from_registry(cls) -> Vocabulary:
        from decision import registry

        reg = registry.load()
        raw = yaml.safe_load(TEMPLATES_PATH.read_text(encoding="utf-8"))
        templates = raw.get("templates", raw) if isinstance(raw, dict) else raw
        return cls(
            facets=frozenset(f.id for f in reg.facets()),
            domains=frozenset(d.id for d in reg.domains()),
            templates=frozenset(t["id"] for t in templates),
        )


def _schema_errors(document: Any) -> list[str]:
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)
    return [
        f"{'/'.join(str(p) for p in error.absolute_path) or '(root)'}: {error.message}"
        for error in sorted(validator.iter_errors(document), key=lambda e: list(e.absolute_path))
    ]


def _semantic_errors(prompts: list[Mapping[str, Any]], vocabulary: Vocabulary) -> list[str]:
    errors: list[str] = []
    seen: Counter[str] = Counter(p["id"] for p in prompts)
    errors += [f"{pid}: id is used {n} times" for pid, n in sorted(seen.items()) if n > 1]
    for prompt in prompts:
        pid, cluster = prompt["id"], prompt["cluster"]
        constraints = prompt.get("constraints", [])
        if cluster == "constrained" and not constraints:
            errors.append(f"{pid}: a constrained prompt must name at least one constraint")
        for constraint in constraints:
            if constraint not in vocabulary.facets and constraint not in vocabulary.domains:
                errors.append(f"{pid}: constraint {constraint!r} is not a registry facet or domain")
        template = prompt.get("template")
        if template is not None and template not in vocabulary.templates:
            errors.append(f"{pid}: template {template!r} is not in registry/templates.yaml")
        if (cluster == "disambiguation") != (prompt["success"] == "disambiguated"):
            errors.append(f"{pid}: success 'disambiguated' belongs to the disambiguation cluster, and only there")
    return errors


def validate(document: Any, vocabulary: Vocabulary | None = None) -> list[str]:
    """Every problem with an inventory document, or an empty list."""
    errors = _schema_errors(document)
    if errors:
        return errors
    return _semantic_errors(document["prompts"], vocabulary or Vocabulary.from_registry())


def coverage_errors(prompts: Iterable[Mapping[str, Any]]) -> list[str]:
    """Whether the inventory is big and balanced enough to start measuring."""
    prompts = list(prompts)
    counts = Counter(p["cluster"] for p in prompts)
    low, high = TOTAL_RANGE
    errors = [] if low <= len(prompts) <= high else [f"{len(prompts)} prompts; need {low} to {high}"]
    errors += [
        f"cluster {cluster!r} has {counts[cluster]} prompts; need at least {MIN_PER_CLUSTER}"
        for cluster in CLUSTERS if counts[cluster] < MIN_PER_CLUSTER
    ]
    return errors


def load(path: Path, vocabulary: Vocabulary | None = None) -> list[dict[str, Any]]:
    """The prompts in ``path``. Raises ``ValueError`` listing every problem."""
    document = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    errors = validate(document, vocabulary)
    if errors:
        raise ValueError(f"{path}: invalid prompt inventory:\n  " + "\n  ".join(errors))
    return document["prompts"]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m scripts.aeo.inventory", description=__doc__.splitlines()[0])
    parser.add_argument("path", type=Path)
    parser.add_argument("--coverage", action="store_true",
                        help=f"also require {TOTAL_RANGE[0]}-{TOTAL_RANGE[1]} prompts, {MIN_PER_CLUSTER}+ per cluster")
    args = parser.parse_args(argv)
    try:
        prompts = load(args.path)
    except ValueError as exc:
        print(exc, file=sys.stderr)
        return 1
    counts = Counter(p["cluster"] for p in prompts)
    sources = Counter(p["source"] for p in prompts)
    print(f"{len(prompts)} prompts: " + ", ".join(f"{c} {counts[c]}" for c in CLUSTERS))
    print("sources: " + ", ".join(f"{s} {n}" for s, n in sorted(sources.items())))
    if args.coverage:
        problems = coverage_errors(prompts)
        for problem in problems:
            print(f"coverage: {problem}", file=sys.stderr)
        if problems:
            return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
