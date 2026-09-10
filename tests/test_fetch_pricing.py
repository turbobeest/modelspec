"""Conservative matching from provider pricing tables onto model cards."""

# ruff: noqa: E501

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.fetch_pricing import (  # noqa: E402
    CardRef,
    PricingRow,
    apply_values,
    classify_table,
    extract_pricing_rows,
    match_keys,
    match_row,
    merge_row_values,
    parse_context,
    parse_price,
    slugify,
    url_slug_is_safe,
    write_fields,
)

TOGETHER_DOCS = """
## Chat models

| Organization | Model name | API model string | Context length | Input pricing (per 1M tokens) | Cached input pricing (per 1M tokens) | Output pricing (per 1M tokens) |
| --- | --- | --- | --- | --- | --- | --- |
| Minimax | MiniMax M3 | MiniMaxAI/MiniMax-M3 | 524288 | $0.30 | $0.06 | $1.20 |
| Meta | Llama 3.3 70B Instruct Turbo | meta-llama/Llama-3.3-70B-Instruct-Turbo | 131072 | $1.04 | - | $1.04 |
| Qwen | Qwen3.8-2.4T-A95B | Qwen/Qwen3.8-2.4T-A95B | - | $2.00 | $0.50 | $6.00 |
| Prism ML | Ternary Bonsai 27B | Prism-ML/Ternary-Bonsai-27B | 262144 | Free | - | Free |
| Qwen | Qwen3.5 9B | Qwen/Qwen3.5-9B | 262144 | $0.17 | - | $0.25 |

## Image models

| Organization | Model name | Model string for API | Price per MP | Default steps |
| --- | --- | --- | --- | --- |
| Qwen | Qwen Image | Qwen/Qwen-Image | $0.0058 | - |
"""

TOGETHER_MARKETING = """
Price per 1M tokens

| Model | Input | output |
| --- | --- | --- |
| [MiniMax M3](https://www.together.ai/models/minimax-m3) | $0.30<br>$0.06 (cached) | $1.20 |
| [Llama 3.3 70B](https://www.together.ai/models/llama-3-3-70b) | $1.04 | $1.04 |
| [Qwen3 235B A22B Instruct 2507 FP8 Throughput](https://www.together.ai/models/qwen3-235b-a22b-instruct-2507-fp8) | $0.20 | $0.60 |
| [Ternary Bonsai 27B](https://www.together.ai/models/prism-ml-ternary-bonsai-27b) | $0.00 | $0.00 |

| Model | Price per mp | Price per iMAGE | Default steps |
| --- | --- | --- | --- |
| [FLUX.2 pro](https://www.together.ai/models/flux-2-pro) | - | $0.03 | - |
"""

FIREWORKS_DOCS = """
| Model | Standard | Priority | Reserved Throughput |
| --- | --- | --- | --- |
| [Kimi K3](https://app.fireworks.ai/models/fireworks/kimi-k3) | $3.00 / $0.30 / $15.00 | $3.75 / $0.375 / $18.75 | ✓ |
| [Kimi K3 Fast](https://app.fireworks.ai/models/fireworks/kimi-k3) | $4.50 / $0.45 / $22.50 | — | ✓ |
| [Kimi K3 US](https://app.fireworks.ai/models/fireworks/kimi-k3) | $3.30 / $0.33 / $16.50 | $4.125 / $0.4125 / $20.625 |  |
| [MiniMax M3](https://app.fireworks.ai/models/fireworks/minimax-m3) | $0.30 / $0.06 / $1.20 | $0.45 / $0.09 / $1.80 |  |

## Embeddings

| Base model parameter count | $ / 1M input tokens |
| --- | --- |
| Qwen3 8B | $0.10 |
"""


def _card(model_id: str, display: str = "", **existing: float | int | None) -> CardRef:
    suffix = slugify(model_id)
    filled = {
        "cost.input": existing.get("cost.input"),
        "cost.output": existing.get("cost.output"),
        "context_window": existing.get("context_window"),
    }
    return CardRef(
        model_id=model_id,
        path=Path(f"models/{model_id}.md"),
        display_name=display or model_id.split("/", 1)[-1],
        suffix=suffix,
        existing=filled,
    )


def _index(cards: list[CardRef]) -> dict[str, list[CardRef]]:
    from scripts.fetch_pricing import build_card_indexes

    index, _ambiguous = build_card_indexes(cards)
    return index


def test_slugify_drops_org_and_punctuation() -> None:
    assert slugify("Qwen/Qwen3.5-9B") == "qwen3-5-9b"
    assert slugify("MiniMaxAI/MiniMax-M3") == "minimax-m3"
    assert slugify("https://www.together.ai/models/qwen3-8-max") == "qwen3-8-max"


def test_fast_row_must_not_reuse_base_url_slug() -> None:
    assert not url_slug_is_safe("kimi-k3-fast", "kimi-k3")
    assert not url_slug_is_safe("kimi-k3-us", "kimi-k3")
    assert url_slug_is_safe("minimax-m3", "minimax-m3")
    # Display is a different product name, not a serving SKU of the URL.
    assert url_slug_is_safe("qwen3-8-2-4t-a95b", "qwen3-8-max")


def test_together_docs_extracts_token_prices_and_integer_context() -> None:
    rows = extract_pricing_rows(TOGETHER_DOCS, "https://docs.together.ai/docs/serverless-models")
    by_name = {row.name: row for row in rows}
    assert "Qwen Image" not in by_name
    m3 = by_name["MiniMax M3"]
    assert m3.input_per_million == 0.30
    assert m3.output_per_million == 1.20
    assert m3.context_window == 524288
    assert m3.api_id == "MiniMaxAI/MiniMax-M3"
    turbo = by_name["Llama 3.3 70B Instruct Turbo"]
    assert turbo.input_per_million == 1.04
    bonsai = by_name.get("Ternary Bonsai 27B")
    assert bonsai is None or bonsai.input_per_million is None


NESTED_IMAGE = r"""
| Model | Input | output |
| --- | --- | --- |
| [![](https://cdn.prod.website-files.com/abc/qwen.png)\<br>\<br>Qwen3.8-2.4T-A95B](https://www.together.ai/models/qwen3-8-max) | $2.00<br>$0.25 (cached) | $6.00 |
"""


def test_together_marketing_uses_first_price_not_cached() -> None:
    rows = extract_pricing_rows(TOGETHER_MARKETING, "https://www.together.ai/pricing")
    by_name = {row.name: row for row in rows}
    assert "FLUX.2 pro" not in by_name
    m3 = by_name["MiniMax M3"]
    assert m3.input_per_million == 0.30
    assert m3.page_slug == "minimax-m3"
    assert "Ternary Bonsai 27B" not in by_name  # $0.00 skipped


def test_nested_cdn_image_does_not_become_a_match_key() -> None:
    rows = extract_pricing_rows(NESTED_IMAGE, "https://www.together.ai/pricing")
    assert len(rows) == 1
    row = rows[0]
    assert row.name == "Qwen3.8-2.4T-A95B"
    assert row.page_slug == "qwen3-8-max"
    keys = match_keys(row)
    assert "qwen3-8-max" in keys
    assert all("png" not in key and "cdn" not in key for key in keys)


def test_together_product_url_matches_card_when_display_name_differs() -> None:
    cards = [_card("qwen/qwen3-8-max", "Qwen3.8 Max")]
    index = _index(cards)
    rows = extract_pricing_rows(NESTED_IMAGE, "https://www.together.ai/pricing")
    card, reason = match_row(rows[0], index)
    assert reason is None
    assert card is not None and card.model_id == "qwen/qwen3-8-max"


def test_fireworks_standard_triplet_and_skips_embeddings() -> None:
    rows = extract_pricing_rows(
        FIREWORKS_DOCS, "https://docs.fireworks.ai/serverless/pricing"
    )
    names = [row.name for row in rows]
    assert "Qwen3 8B" not in names
    kimi = next(row for row in rows if row.name == "Kimi K3")
    assert kimi.input_per_million == 3.00
    assert kimi.output_per_million == 15.00
    fast = next(row for row in rows if row.name == "Kimi K3 Fast")
    assert fast.input_per_million == 4.50
    assert "kimi-k3-fast" in match_keys(fast)
    assert "kimi-k3" not in match_keys(fast)


def test_128k_context_is_refused() -> None:
    assert parse_context("128K") is None
    assert parse_context("262144") == 262144
    assert parse_context("1,048,576") == 1048576


def test_parse_price_skips_free_and_zero() -> None:
    assert parse_price("Free") is None
    assert parse_price("$0.00") is None
    assert parse_price("$0.30<br>$0.06 (cached)") == 0.30


def test_unique_suffix_matches() -> None:
    cards = [
        _card("minimax/minimax-m3", "MiniMax-M3"),
        _card("meta/llama-3-3-70b-instruct", "Llama 3.3 70B Instruct"),
        _card("qwen/qwen3-235b-a22b", "Qwen3 235B-A22B"),
        _card("moonshot/kimi-k3", "Kimi K3"),
    ]
    index = _index(cards)
    m3 = PricingRow("MiniMax M3", "https://example", 0.3, 1.2, 524288, page_slug="minimax-m3")
    card, reason = match_row(m3, index)
    assert reason is None
    assert card is not None and card.model_id == "minimax/minimax-m3"


def test_turbo_and_fp8_and_instruct_are_not_guessed() -> None:
    cards = [
        _card("meta/llama-3-3-70b-instruct"),
        _card("qwen/qwen3-235b-a22b"),
        _card("qwen/qwen2-5-7b-instruct"),
    ]
    index = _index(cards)
    turbo = PricingRow(
        "Llama 3.3 70B Instruct Turbo",
        "https://example",
        1.04,
        1.04,
        api_id="meta-llama/Llama-3.3-70B-Instruct-Turbo",
    )
    card, reason = match_row(turbo, index)
    assert card is None and reason is None  # unmatched, not a guess

    fp8 = PricingRow(
        "Qwen3 235B A22B Instruct 2507 FP8 Throughput",
        "https://example",
        0.20,
        0.60,
        page_slug="qwen3-235b-a22b-instruct-2507-fp8",
    )
    card, reason = match_row(fp8, index)
    assert card is None

    llama = PricingRow(
        "Llama 3.3 70B",
        "https://example",
        1.04,
        1.04,
        page_slug="llama-3-3-70b",
    )
    card, reason = match_row(llama, index)
    assert card is None


def test_fireworks_fast_does_not_match_base_card() -> None:
    cards = [_card("moonshot/kimi-k3", "Kimi K3")]
    index = _index(cards)
    rows = extract_pricing_rows(
        FIREWORKS_DOCS, "https://docs.fireworks.ai/serverless/pricing"
    )
    fast = next(row for row in rows if row.name == "Kimi K3 Fast")
    card, reason = match_row(fast, index)
    assert card is None
    base = next(row for row in rows if row.name == "Kimi K3")
    card, reason = match_row(base, index)
    assert card is not None and card.model_id == "moonshot/kimi-k3"


def test_duplicate_suffix_is_refused() -> None:
    cards = [_card("cerebras/gpt-oss-120b"), _card("openai/gpt-oss-120b")]
    index = _index(cards)
    row = PricingRow("gpt-oss-120B", "https://example", 0.15, 0.60, page_slug="gpt-oss-120b")
    card, reason = match_row(row, index)
    assert card is None
    assert reason is not None and "ambiguous" in reason


def test_never_overwrite_existing() -> None:
    existing = {"cost.input": 0.2, "cost.output": None, "context_window": 131072}
    fetched = {"cost.input": 0.14, "cost.output": 0.28, "context_window": 1048576}
    gained, conflicts, already = apply_values(existing, fetched)
    assert gained == {"cost.output": 0.28}
    assert already == []
    fields = {c["field"] for c in conflicts}
    assert fields == {"cost.input", "context_window"}


def test_source_disagreement_refuses_the_field() -> None:
    together = PricingRow("MiniMax M3", "https://together", 0.30, 1.20)
    fireworks = PricingRow("MiniMax M3", "https://fireworks", 0.40, 1.20)
    merged, conflicts = merge_row_values([together, fireworks])
    assert merged == {"cost.output": 1.20}
    assert conflicts[0]["field"] == "cost.input"


def test_classify_skips_non_token_tables() -> None:
    assert classify_table(["Model", "Price per mp", "Default steps"]) is None
    assert classify_table(["Base model parameter count", "$ / 1M input tokens"]) is None
    assert classify_table(["Model", "Input", "output"]) == "input_output"
    assert classify_table(["Model", "Standard", "Priority"]) == "fireworks_standard"


def test_write_round_trips_through_model_card(tmp_path: Path) -> None:
    from schema.card import ModelCard

    path = tmp_path / "tiny.md"
    path.write_text(
        "---\n"
        "model_id: test/tiny\n"
        "display_name: Tiny\n"
        "provider: test\n"
        "cost:\n"
        "  input: null\n"
        "  output: 9.0\n"
        "modalities:\n"
        "  text:\n"
        "    context_window: null\n"
        "benchmarks:\n"
        "  scores: {}\n"
        "---\n\nprose\n",
        encoding="utf-8",
    )
    gained = {"cost.input": 0.15, "context_window": 131072}
    write_fields(path, gained)
    card = ModelCard.from_yaml_file(path)
    assert card.cost.input == 0.15
    assert card.cost.output == 9.0
    assert card.modalities.text.context_window == 131072
    assert card.benchmarks.scores == {}
    assert card.prose_body == "prose"
