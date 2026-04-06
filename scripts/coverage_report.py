#!/usr/bin/env python3
"""Generate a weekly coverage report for all model cards.

Outputs a Markdown report to stdout, suitable for posting as a GitHub issue.

Usage:
    python scripts/coverage_report.py
"""

from __future__ import annotations

import sys
from collections import defaultdict
from pathlib import Path

# Ensure the repo root is importable
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from schema.card import ModelCard  # noqa: E402


def load_all_cards() -> list[tuple[str, ModelCard | None, str | None]]:
    """Load every model card. Returns list of (filepath, card_or_none, error_or_none)."""
    models_dir = REPO_ROOT / "models"
    results = []
    for path in sorted(models_dir.rglob("*.md")):
        filepath = str(path.relative_to(REPO_ROOT))
        try:
            card = ModelCard.from_yaml_file(path)
            results.append((filepath, card, None))
        except Exception as e:
            results.append((filepath, None, str(e)))
    return results


def has_benchmarks(card: ModelCard) -> bool:
    """Check if a card has any benchmark data."""
    return card.benchmarks.filled_count() > 0


def has_cost(card: ModelCard) -> bool:
    """Check if a card has any cost data."""
    c = card.cost
    return any(
        v is not None
        for v in [
            c.input,
            c.output,
            c.reasoning,
            c.cache_read,
            c.cache_write,
            c.input_audio,
            c.output_audio,
            c.input_image,
            c.output_image,
            c.output_video_per_sec,
            c.batch_input,
            c.batch_output,
            c.embedding_per_million,
            c.reranking_per_million,
        ]
    )


def has_parameters(card: ModelCard) -> bool:
    """Check if a card has parameter count."""
    return card.architecture.total_parameters is not None


def generate_report(
    all_cards: list[tuple[str, ModelCard | None, str | None]],
) -> str:
    """Generate a Markdown coverage report."""
    valid_cards: list[tuple[str, ModelCard]] = [
        (fp, card) for fp, card, err in all_cards if card is not None
    ]
    invalid_cards: list[tuple[str, str]] = [
        (fp, err) for fp, _, err in all_cards if err is not None  # type: ignore[misc]
    ]

    # --- Provider breakdown ---
    providers: dict[str, list[tuple[str, ModelCard]]] = defaultdict(list)
    for fp, card in valid_cards:
        providers[card.identity.provider].append((fp, card))

    # --- Stats ---
    total = len(all_cards)
    total_valid = len(valid_cards)
    total_invalid = len(invalid_cards)
    completeness_values = [card.card_completeness for _, card in valid_cards]
    avg_completeness = (
        round(sum(completeness_values) / len(completeness_values), 1) if completeness_values else 0
    )

    no_benchmarks = [(fp, c) for fp, c in valid_cards if not has_benchmarks(c)]
    no_cost = [(fp, c) for fp, c in valid_cards if not has_cost(c)]
    no_params = [(fp, c) for fp, c in valid_cards if not has_parameters(c)]

    # Sorted by completeness
    sorted_by_completeness = sorted(valid_cards, key=lambda x: x[1].card_completeness, reverse=True)
    top_10 = sorted_by_completeness[:10]
    bottom_10 = sorted_by_completeness[-10:]

    # --- Build report ---
    lines: list[str] = []
    lines.append("## ModelSpec Weekly Coverage Report\n")
    lines.append(f"**Generated automatically** | {total_valid} valid cards, {total_invalid} errors\n")

    # Summary table
    lines.append("### Summary\n")
    lines.append("| Metric | Value |")
    lines.append("|--------|-------|")
    lines.append(f"| Total models | {total} |")
    lines.append(f"| Valid cards | {total_valid} |")
    lines.append(f"| Invalid cards | {total_invalid} |")
    lines.append(f"| Providers | {len(providers)} |")
    lines.append(f"| Avg completeness | {avg_completeness}% |")
    lines.append(f"| Models without benchmarks | {len(no_benchmarks)} |")
    lines.append(f"| Models without cost data | {len(no_cost)} |")
    lines.append(f"| Models without parameters | {len(no_params)} |")
    lines.append("")

    # Provider breakdown
    lines.append("### Provider Breakdown\n")
    lines.append("| Provider | Cards | Avg Completeness |")
    lines.append("|----------|-------|-----------------|")
    for provider_name in sorted(providers.keys()):
        cards = providers[provider_name]
        avg = round(sum(c.card_completeness for _, c in cards) / len(cards), 1)
        lines.append(f"| {provider_name} | {len(cards)} | {avg}% |")
    lines.append("")

    # Top 10 most complete
    lines.append("### Top 10 Most Complete\n")
    lines.append("| Model | Completeness | Benchmarks | Cost | Parameters |")
    lines.append("|-------|-------------|-----------|------|------------|")
    for fp, card in top_10:
        bm = "yes" if has_benchmarks(card) else "no"
        co = "yes" if has_cost(card) else "no"
        pa = f"{card.architecture.total_parameters:,}" if has_parameters(card) else "n/a"
        lines.append(
            f"| {card.identity.model_id} | {card.card_completeness}% | {bm} | {co} | {pa} |"
        )
    lines.append("")

    # Bottom 10 least complete
    lines.append("### Top 10 Least Complete\n")
    lines.append("| Model | Completeness | Benchmarks | Cost | Parameters |")
    lines.append("|-------|-------------|-----------|------|------------|")
    for fp, card in bottom_10:
        bm = "yes" if has_benchmarks(card) else "no"
        co = "yes" if has_cost(card) else "no"
        pa = f"{card.architecture.total_parameters:,}" if has_parameters(card) else "n/a"
        lines.append(
            f"| {card.identity.model_id} | {card.card_completeness}% | {bm} | {co} | {pa} |"
        )
    lines.append("")

    # Models without benchmarks (first 20)
    lines.append(f"### Models Without Benchmarks ({len(no_benchmarks)} total)\n")
    lines.append("<details><summary>Show list</summary>\n")
    for fp, card in no_benchmarks[:50]:
        lines.append(f"- `{card.identity.model_id}`")
    if len(no_benchmarks) > 50:
        lines.append(f"\n... and {len(no_benchmarks) - 50} more")
    lines.append("\n</details>\n")

    # Models without cost data (first 20)
    lines.append(f"### Models Without Cost Data ({len(no_cost)} total)\n")
    lines.append("<details><summary>Show list</summary>\n")
    for fp, card in no_cost[:50]:
        lines.append(f"- `{card.identity.model_id}`")
    if len(no_cost) > 50:
        lines.append(f"\n... and {len(no_cost) - 50} more")
    lines.append("\n</details>\n")

    # Invalid cards
    if invalid_cards:
        lines.append(f"### Invalid Cards ({total_invalid})\n")
        lines.append("| File | Error |")
        lines.append("|------|-------|")
        for fp, err in invalid_cards:
            # Truncate long errors for the table
            short_err = err[:120].replace("|", "\\|").replace("\n", " ")
            lines.append(f"| `{fp}` | {short_err} |")
        lines.append("")

    return "\n".join(lines)


def main() -> None:
    all_cards = load_all_cards()
    report = generate_report(all_cards)
    print(report)


if __name__ == "__main__":
    main()
