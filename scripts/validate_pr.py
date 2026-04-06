#!/usr/bin/env python3
"""Validate model cards changed in a PR.

Called by the validate-cards GitHub Action. Outputs JSON to stdout
that the workflow consumes for PR comments and labels.

Usage:
    python scripts/validate_pr.py          # validate PR-changed cards
    python scripts/validate_pr.py --all    # validate every card in models/
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

# Ensure the repo root is importable
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from schema.card import ModelCard  # noqa: E402


# ─── Field helpers ─────────────────────────────────────────────

BENCHMARK_FIELDS = set(ModelCard.model_fields["benchmarks"].annotation.model_fields.keys()) - {
    "benchmark_source",
    "benchmark_as_of",
    "benchmark_notes",
}

COST_FIELDS = set(ModelCard.model_fields["cost"].annotation.model_fields.keys()) - {
    "note",
    "free_tier",
    "free_tier_limits",
}


def count_non_null_fields(card: ModelCard) -> int:
    """Count all non-null, non-empty, non-default fields across the card."""
    filled, _ = card._count_fields(card)
    return filled


def get_field_names(card: ModelCard) -> set[str]:
    """Return a flat set of 'section.field' strings that are filled."""
    filled_fields: set[str] = set()
    for section_name in (
        "architecture",
        "lineage",
        "licensing",
        "modalities",
        "capabilities",
        "cost",
        "availability",
        "benchmarks",
        "deployment",
        "risk_governance",
        "inference_performance",
        "adoption",
        "downselect",
        "sources",
    ):
        section = getattr(card, section_name)
        _collect_filled(section, section_name, filled_fields)
    return filled_fields


def _collect_filled(obj: object, prefix: str, result: set[str]) -> None:
    """Recursively collect filled field paths."""
    from pydantic import BaseModel

    if not isinstance(obj, BaseModel):
        return
    for field_name in obj.model_fields:
        value = getattr(obj, field_name)
        full_name = f"{prefix}.{field_name}"
        if isinstance(value, BaseModel):
            _collect_filled(value, full_name, result)
        elif isinstance(value, list):
            if len(value) > 0:
                result.add(full_name)
        elif isinstance(value, dict):
            if len(value) > 0:
                result.add(full_name)
        elif value is not None and value != "" and value is not False:
            result.add(full_name)


# ─── File discovery ────────────────────────────────────────────


def get_changed_model_files() -> list[str]:
    """Get model card files changed in this PR (vs origin/main)."""
    result = subprocess.run(
        ["git", "diff", "--name-only", "origin/main...HEAD"],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
    )
    if result.returncode != 0:
        print(f"Warning: git diff failed: {result.stderr}", file=sys.stderr)
        return []
    return [
        f
        for f in result.stdout.strip().split("\n")
        if f.startswith("models/") and f.endswith(".md") and f.strip()
    ]


def get_all_model_files() -> list[str]:
    """Get every model card file in the repo."""
    models_dir = REPO_ROOT / "models"
    return sorted(
        str(p.relative_to(REPO_ROOT)) for p in models_dir.rglob("*.md")
    )


def file_is_new(filepath: str) -> bool:
    """Check if a file is newly added (not on origin/main)."""
    result = subprocess.run(
        ["git", "diff", "--diff-filter=A", "--name-only", "origin/main...HEAD"],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
    )
    new_files = set(result.stdout.strip().split("\n"))
    return filepath in new_files


# ─── Baseline completeness ────────────────────────────────────


def get_baseline_completeness(filepath: str) -> float | None:
    """Get the completeness of the file on origin/main (before PR changes)."""
    result = subprocess.run(
        ["git", "show", f"origin/main:{filepath}"],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
    )
    if result.returncode != 0:
        return None  # File is new
    try:
        card = ModelCard.from_yaml_string(result.stdout)
        return card.card_completeness
    except Exception:
        return None


def get_baseline_fields(filepath: str) -> set[str]:
    """Get the filled field names from the origin/main version."""
    result = subprocess.run(
        ["git", "show", f"origin/main:{filepath}"],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
    )
    if result.returncode != 0:
        return set()
    try:
        card = ModelCard.from_yaml_string(result.stdout)
        return get_field_names(card)
    except Exception:
        return set()


# ─── Validation ────────────────────────────────────────────────


def validate_card(filepath: str, compute_diff: bool = True) -> dict:
    """Validate a single model card and return a result dict."""
    full_path = REPO_ROOT / filepath
    entry: dict = {"file": filepath}

    try:
        card = ModelCard.from_yaml_file(full_path)
    except Exception as e:
        entry["status"] = "invalid"
        entry["error"] = str(e)
        return entry

    entry["status"] = "valid"
    entry["model_id"] = card.identity.model_id
    entry["completeness"] = card.card_completeness
    entry["fields_filled"] = count_non_null_fields(card)

    if compute_diff:
        baseline = get_baseline_completeness(filepath)
        entry["completeness_delta"] = (
            round(card.card_completeness - baseline, 1) if baseline is not None else None
        )
        entry["is_new"] = baseline is None

        # Detect added fields
        current_fields = get_field_names(card)
        baseline_fields = get_baseline_fields(filepath)
        added_fields = sorted(current_fields - baseline_fields)
        entry["fields_added"] = added_fields
        entry["fields_added_count"] = len(added_fields)

        # Categorize changes
        entry["has_benchmark_changes"] = any(
            f.startswith("benchmarks.") and f.split(".")[-1] in BENCHMARK_FIELDS
            for f in added_fields
        )
        entry["has_cost_changes"] = any(
            f.startswith("cost.") and f.split(".")[-1] in COST_FIELDS
            for f in added_fields
        )
    return entry


def validate_all_quick() -> list[dict]:
    """Quick schema validation of all cards -- just check they parse."""
    errors = []
    for filepath in get_all_model_files():
        full_path = REPO_ROOT / filepath
        try:
            ModelCard.from_yaml_file(full_path)
        except Exception as e:
            errors.append({"file": filepath, "error": str(e)})
    return errors


# ─── Main ──────────────────────────────────────────────────────


def main() -> None:
    run_all = "--all" in sys.argv

    if run_all:
        files = get_all_model_files()
        results = [validate_card(f, compute_diff=False) for f in files]
        output = {
            "mode": "all",
            "results": results,
            "total": len(results),
            "valid": sum(1 for r in results if r["status"] == "valid"),
            "invalid": sum(1 for r in results if r["status"] == "invalid"),
        }
    else:
        changed_files = get_changed_model_files()
        if not changed_files:
            output = {
                "mode": "pr",
                "results": [],
                "total": 0,
                "valid": 0,
                "invalid": 0,
                "new_cards": 0,
                "regression_errors": [],
                "labels": [],
            }
            print(json.dumps(output, indent=2))
            return

        # Validate changed cards with diff info
        results = [validate_card(f, compute_diff=True) for f in changed_files]

        # Also do a quick regression check on all cards
        regression_errors = validate_all_quick()

        # Determine labels
        labels: list[str] = []
        has_new = any(r.get("is_new") for r in results)
        has_benchmark = any(r.get("has_benchmark_changes") for r in results)
        has_cost = any(r.get("has_cost_changes") for r in results)
        has_enrichment = any(
            not r.get("is_new") and r.get("fields_added_count", 0) > 0 for r in results
        )
        all_valid = all(r["status"] == "valid" for r in results) and len(regression_errors) == 0

        if has_new:
            labels.append("new-models")
        if has_benchmark:
            labels.append("benchmark-update")
        if has_cost:
            labels.append("cost-update")
        if has_enrichment:
            labels.append("enrichment")
        labels.append("schema-valid" if all_valid else "schema-invalid")

        total_fields_added = sum(r.get("fields_added_count", 0) for r in results)

        output = {
            "mode": "pr",
            "results": results,
            "total": len(results),
            "valid": sum(1 for r in results if r["status"] == "valid"),
            "invalid": sum(1 for r in results if r["status"] == "invalid"),
            "new_cards": sum(1 for r in results if r.get("is_new")),
            "total_fields_added": total_fields_added,
            "regression_errors": regression_errors,
            "labels": labels,
        }

    print(json.dumps(output, indent=2))

    # Exit with error if any cards are invalid
    if output.get("invalid", 0) > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
