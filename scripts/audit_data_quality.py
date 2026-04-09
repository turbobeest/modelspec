#!/usr/bin/env python3
"""ModelSpec Data Quality Audit

Scans all model cards for missing fields, anomalies, and inconsistencies.
Outputs a report grouped by severity and category.

Usage:
  python scripts/audit_data_quality.py              # Full report
  python scripts/audit_data_quality.py --provider anthropic  # One provider
  python scripts/audit_data_quality.py --json       # JSON output
  python scripts/audit_data_quality.py --fix-context  # Auto-fix known context windows
"""

import sys
import json
import argparse
from pathlib import Path
from collections import Counter, defaultdict

sys.path.insert(0, str(Path(__file__).parent.parent))
from schema.card import ModelCard


# ═══════════════════════════════════════════════════════════════
# Known values for auto-fix
# ═══════════════════════════════════════════════════════════════

# Context windows that Anthropic doesn't list but are publicly known
KNOWN_CONTEXT_WINDOWS = {
    # Anthropic — all publicly documented
    "anthropic/claude-3-haiku-20240307": 200000,
    "anthropic/claude-3-sonnet-20240229": 200000,
    "anthropic/claude-3-opus-20240229": 200000,
    "anthropic/claude-3-5-haiku-20241022": 200000,
    "anthropic/claude-3-5-haiku-latest": 200000,
    "anthropic/claude-3-5-sonnet-20240620": 200000,
    "anthropic/claude-3-5-sonnet-20241022": 200000,
    "anthropic/claude-3-7-sonnet-20250219": 200000,
    "anthropic/claude-haiku-4-5": 200000,
    "anthropic/claude-haiku-4-5-20251001": 200000,
    "anthropic/claude-sonnet-4": 200000,
    "anthropic/claude-sonnet-4-0": 200000,
    "anthropic/claude-sonnet-4-20250514": 200000,
    "anthropic/claude-sonnet-4-5": 200000,
    "anthropic/claude-sonnet-4-5-20250929": 200000,
    "anthropic/claude-sonnet-4-6": 1000000,
    "anthropic/claude-opus-4-0": 200000,
    "anthropic/claude-opus-4-20250514": 200000,
    "anthropic/claude-opus-4-1": 200000,
    "anthropic/claude-opus-4-1-20250805": 200000,
    "anthropic/claude-opus-4-5": 200000,
    "anthropic/claude-opus-4-5-20251101": 200000,
    "anthropic/claude-opus-4-6": 1000000,
    "anthropic/claude-mythos-preview": 1000000,
}

# Models where parameters are intentionally undisclosed (not a data gap)
PARAMS_UNDISCLOSED = {
    "anthropic",  # Never disclosed
}

# Model types that don't need certain fields
NO_CONTEXT_NEEDED = {
    "image-generation", "image-gen", "embedding-text", "embedding-multimodal",
    "reranker", "safety-classifier", "reward-model", "audio-tts", "audio-asr",
    "video-generation",
}

NO_PARAMS_NEEDED = {
    "image-generation", "image-gen", "video-generation",
}


# ═══════════════════════════════════════════════════════════════
# Audit rules
# ═══════════════════════════════════════════════════════════════

def audit_card(card: ModelCard, path: Path) -> list[dict]:
    """Run all audit rules on a single card. Returns list of findings."""
    findings = []
    mid = card.identity.model_id
    provider = mid.split("/")[0] if "/" in mid else ""
    mtype = card.identity.model_type.value if card.identity.model_type else ""
    subtypes = [s.value for s in card.identity.model_subtypes] if card.identity.model_subtypes else []
    all_types = [mtype] + subtypes

    def add(severity, category, field, message):
        findings.append({
            "model_id": mid,
            "provider": provider,
            "severity": severity,
            "category": category,
            "field": field,
            "message": message,
        })

    # ── Missing critical fields ───────────────────────────────

    # Parameters
    if card.architecture.total_parameters is None:
        if provider not in PARAMS_UNDISCLOSED and mtype not in NO_PARAMS_NEEDED:
            add("warning", "missing", "total_parameters",
                "No parameter count — affects hardware fit estimation and gravity well")

    # Context window
    if card.modalities.text.context_window is None or card.modalities.text.context_window == 0:
        is_text_model = any(t in ["llm-chat", "llm-reasoning", "llm-code", "llm-base", "vlm"]
                           for t in all_types)
        if is_text_model:
            add("warning", "missing", "context_window",
                "Text model with no context window — affects ranking and filtering")

    # Benchmarks
    bench_count = card.benchmarks.filled_count()
    is_llm = any(t.startswith("llm") or t == "vlm" for t in all_types)
    if is_llm and bench_count == 0:
        add("info", "missing", "benchmarks",
            "LLM with zero benchmark scores — invisible to ranking engine")
    elif is_llm and bench_count < 3:
        add("info", "sparse", "benchmarks",
            f"Only {bench_count} benchmark scores — may rank poorly due to missing data")

    # Arena ELO — important for ranking
    if is_llm and bench_count > 0 and "arena_elo_overall" not in card.benchmarks.scores:
        add("info", "missing", "arena_elo_overall",
            "Has benchmarks but no Arena ELO — missing from preference-based ranking")

    # Cost
    if is_llm and card.cost.input is None and not card.licensing.open_weights:
        add("info", "missing", "cost_input",
            "API model with no pricing — can't be filtered by cost")

    # Capability tiers
    if is_llm and bench_count > 5:
        if not any(True for cap_name in ["coding", "reasoning", "tool_use"]
                   for _ in []
                   if getattr(getattr(card.capabilities, cap_name, None), "overall", None)):
            # Check each individually
            for cap_name in ["coding", "reasoning", "tool_use"]:
                cap_section = getattr(card.capabilities, cap_name, None)
                if cap_section and getattr(cap_section, "overall", None) is None:
                    add("info", "missing", f"capabilities.{cap_name}.overall",
                        f"No {cap_name} tier — may lose points vs models with tiers set")

    # ── Anomalies ─────────────────────────────────────────────

    # Suspiciously small context window for modern models
    ctx = card.modalities.text.context_window
    if ctx and ctx > 0:
        release = card.identity.release_date or ""
        if release >= "2024" and ctx < 4096 and is_llm:
            add("warning", "anomaly", "context_window",
                f"Context window {ctx} seems low for a 2024+ model")
        if release >= "2025" and ctx <= 8192 and is_llm and "haiku" not in mid and "mini" not in mid:
            add("info", "anomaly", "context_window",
                f"Context window {ctx} — most 2025+ models have 32K+")

    # Parameters that look wrong
    params = card.architecture.total_parameters
    if params and params > 0:
        if params < 100 and is_llm:
            add("error", "anomaly", "total_parameters",
                f"Parameter count {params} — probably missing scale factor (should be in raw count, not billions)")
        if params > 10_000_000_000_000:
            add("warning", "anomaly", "total_parameters",
                f"Parameter count {params/1e12:.1f}T — verify this is correct")

    # Benchmark scores out of range
    for bench_id, value in card.benchmarks.scores.items():
        if "arena_elo" in bench_id:
            if value < 500 or value > 2000:
                add("warning", "anomaly", f"scores.{bench_id}",
                    f"Arena ELO {value} is outside expected range 500-2000")
        elif "mt_bench" in bench_id:
            if value < 1 or value > 10:
                add("warning", "anomaly", f"scores.{bench_id}",
                    f"MT-Bench score {value} — expected range 1-10")
        elif value < 0 or value > 100:
            if bench_id not in ("arena_elo_overall", "arena_elo_coding", "arena_elo_math",
                                "arena_elo_vision", "arena_elo_hard_prompts",
                                "arena_elo_style_control", "mt_bench",
                                "openrouter_usage_rank"):
                add("info", "anomaly", f"scores.{bench_id}",
                    f"Score {value} outside 0-100 range for {bench_id}")

    # ── Inconsistencies ───────────────────────────────────────

    # Model type says VLM but vision not supported
    if "vlm" in all_types and not card.modalities.vision.supported:
        add("warning", "inconsistency", "vision.supported",
            "Model type includes 'vlm' but vision.supported is false")

    # Has tool_use capability but function_calling is false
    tool_overall = getattr(card.capabilities.tool_use, "overall", None)
    if tool_overall and not card.capabilities.tool_use.function_calling:
        add("info", "inconsistency", "tool_use.function_calling",
            f"Tool use tier is {tool_overall} but function_calling is false")

    # Open weights but no license type
    if card.licensing.open_weights and card.licensing.license_type and \
       card.licensing.license_type.value == "proprietary":
        add("warning", "inconsistency", "license_type",
            "Open weights model with proprietary license — likely should be a specific license")

    # Status is active but release_date is empty
    if card.identity.status and card.identity.status.value == "active" and not card.identity.release_date:
        add("info", "missing", "release_date",
            "Active model with no release date")

    return findings


# ═══════════════════════════════════════════════════════════════
# Report generation
# ═══════════════════════════════════════════════════════════════

def run_audit(models_dir: Path, provider_filter: str = None) -> list[dict]:
    """Run audit on all cards, return findings."""
    all_findings = []
    cards = sorted(models_dir.rglob("*.md"))

    for card_path in cards:
        try:
            card = ModelCard.from_yaml_file(card_path)
        except Exception as e:
            all_findings.append({
                "model_id": str(card_path.relative_to(models_dir)),
                "provider": card_path.parent.name,
                "severity": "error",
                "category": "parse",
                "field": "yaml",
                "message": f"Failed to parse: {e}",
            })
            continue

        mid = card.identity.model_id
        provider = mid.split("/")[0] if "/" in mid else ""
        if provider_filter and provider != provider_filter:
            continue

        findings = audit_card(card, card_path)
        all_findings.extend(findings)

    return all_findings


def print_report(findings: list[dict]):
    """Print human-readable audit report."""
    if not findings:
        print("No findings. All cards look good.")
        return

    # Summary
    by_severity = Counter(f["severity"] for f in findings)
    by_category = Counter(f["category"] for f in findings)
    by_field = Counter(f["field"] for f in findings)
    by_provider = Counter(f["provider"] for f in findings)

    print("=" * 70)
    print("  ModelSpec Data Quality Audit")
    print("=" * 70)
    print(f"\n  Total findings: {len(findings)}")
    print(f"  Errors: {by_severity.get('error', 0)}")
    print(f"  Warnings: {by_severity.get('warning', 0)}")
    print(f"  Info: {by_severity.get('info', 0)}")

    print(f"\n  By category:")
    for cat, count in by_category.most_common():
        print(f"    {cat}: {count}")

    print(f"\n  Top missing fields:")
    for field, count in by_field.most_common(15):
        print(f"    {field}: {count}")

    print(f"\n  Top providers with issues:")
    for prov, count in by_provider.most_common(15):
        print(f"    {prov}: {count}")

    # Detail by severity
    for sev in ["error", "warning", "info"]:
        sev_findings = [f for f in findings if f["severity"] == sev]
        if not sev_findings:
            continue

        icon = {"error": "!!!", "warning": " ! ", "info": "   "}[sev]
        print(f"\n{'─' * 70}")
        print(f"  [{sev.upper()}] — {len(sev_findings)} findings")
        print(f"{'─' * 70}")

        # Group by field for readability
        by_field_detail = defaultdict(list)
        for f in sev_findings:
            by_field_detail[f["field"]].append(f)

        for field, items in sorted(by_field_detail.items(), key=lambda x: -len(x[1])):
            print(f"\n  {field} ({len(items)} models):")
            # Show first 10 examples
            for item in items[:10]:
                print(f"  {icon} {item['model_id']}: {item['message']}")
            if len(items) > 10:
                print(f"      ... and {len(items) - 10} more")


def main():
    parser = argparse.ArgumentParser(description="ModelSpec Data Quality Audit")
    parser.add_argument("--provider", help="Filter to a specific provider")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--severity", choices=["error", "warning", "info"],
                        help="Filter by minimum severity")
    args = parser.parse_args()

    models_dir = Path(__file__).parent.parent / "models"
    findings = run_audit(models_dir, args.provider)

    if args.severity:
        severity_rank = {"error": 0, "warning": 1, "info": 2}
        max_rank = severity_rank[args.severity]
        findings = [f for f in findings if severity_rank[f["severity"]] <= max_rank]

    if args.json:
        print(json.dumps(findings, indent=2))
    else:
        print_report(findings)


if __name__ == "__main__":
    main()
