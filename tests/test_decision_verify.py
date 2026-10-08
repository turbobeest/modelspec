"""MODEL-140: two-key verification and quarantine (design §5, "Two keys").

The agent that collects a value never verifies it. These tests run the seeded
error fixture in ``tests/fixtures/verification`` end to end: every correct value
must end ``verified`` and every seeded error ``mismatch``, ``unreachable`` or
unverified, so quarantined. No network and no model call: the LLM extractor is
exercised with a fake completion.
"""

from __future__ import annotations

import json
import re
import subprocess
from datetime import UTC, date, datetime
from pathlib import Path

import pytest
import yaml
from typer.testing import CliRunner

from decision import verify
from decision.model import (
    SourceRef,
    TargetRef,
    Verification,
    VerificationActor,
    VerificationTarget,
    value_hash,
)
from decision.sources import CopyStore, RecheckReport, SourceSnapshot, SourceState

FIXTURES = Path(__file__).parent / "fixtures" / "verification"
TODAY = date(2026, 9, 24)
NOW = datetime(2026, 9, 24, 12, tzinfo=UTC)
SPEC = yaml.safe_load((FIXTURES / "claims.yaml").read_text())
COLLECTOR = VerificationActor(**SPEC["collector"])


def _claim(entry: dict, store: CopyStore) -> verify.Claim:
    src = entry["source"]
    copy = src["copy"]
    ref = store.put((FIXTURES / copy).read_bytes()) if copy else "sha256:" + "0" * 64
    return verify.Claim(
        target=TargetRef(kind=entry.get("kind", "evidence"), id=entry["id"]),
        subject=entry["subject"],
        names=tuple(entry["names"]),
        field=entry["field"],
        label=entry.get("label"),
        value=entry["value"],
        unit=entry.get("unit"),
        conditions=entry.get("conditions", {}),
        collector=COLLECTOR,
        sources=(SourceRef(source_id=src["id"], snapshot_ref=ref, cited_regions=src["regions"]),),
    )


@pytest.fixture
def store(tmp_path) -> CopyStore:
    return CopyStore(tmp_path / "copies")


@pytest.fixture
def regions(store) -> verify.StoredRegions:
    return verify.StoredRegions(store, verify.load_sources(FIXTURES / "sources.yaml"))


@pytest.fixture
def log(tmp_path) -> verify.VerificationLog:
    return verify.VerificationLog(tmp_path / "verification")


def _seeded_run(store, regions, log, **kwargs) -> verify.RunReport:
    queue = verify.Queue(log.directory)
    for entry in SPEC["claims"]:
        queue.file(_claim(entry, store), at=NOW)
    return verify.run(queue, log, regions, verify.deterministic_extractors(), today=TODAY,
                      **kwargs)


# --- the seeded error fixture ------------------------------------------------------------------


def test_every_seeded_claim_ends_as_expected(store, regions, log) -> None:
    report = _seeded_run(store, regions, log)
    got = {r.target.id: r for r in report.results}
    assert set(got) == {e["id"] for e in SPEC["claims"]}
    for entry in SPEC["claims"]:
        result = got[entry["id"]]
        assert result.outcome == entry["expect"], (entry["id"], result)
        if "expect_diff" in entry:
            assert sorted(d.field for d in result.diffs) == sorted(entry["expect_diff"]), (
                entry["id"], result.diffs)


def test_seeded_errors_are_quarantined_and_correct_values_are_not(store, regions, log) -> None:
    _seeded_run(store, regions, log)
    for entry in SPEC["claims"]:
        target = TargetRef(kind=entry.get("kind", "evidence"), id=entry["id"])
        assert log.is_quarantined(target) is (entry["expect"] != "verified"), entry["id"]
    quarantined = {t.id for t in log.quarantined_values()}
    assert quarantined == {e["id"] for e in SPEC["claims"]
                           if e["expect"] in ("mismatch", "unreachable")}


def test_the_log_shows_collector_and_verifier_differ_on_every_record(store, regions, log) -> None:
    _seeded_run(store, regions, log)
    lines = log.path.read_text().splitlines()
    assert len(lines) == sum(e["expect"] != "skipped" for e in SPEC["claims"])
    for line in lines:
        record = Verification.model_validate_json(line)
        assert (record.collector.agent, record.collector.model_family) != (
            record.verifier.agent, record.verifier.model_family)
        assert record.method == record.verifier.method


@pytest.mark.parametrize(
    ("registered", "published"),
    [("type_2", "Type 2"), ("not_offered", "not offered"), ("not_offered", "N/A")],
)
def test_registered_enum_spelling_matches_provider_prose(registered, published) -> None:
    claim = verify.Claim(
        target=verify.TargetRef(kind="fact", id="offering#attestation"),
        subject="provider/model/global/standard",
        names=("Provider API",),
        field="offering.attestation.soc2",
        value=registered,
        collector=COLLECTOR,
        sources=(verify.SourceRef(
            source_id="provider-doc",
            snapshot_ref="sha256:" + "0" * 64,
            cited_regions=["governance"],
        ),),
    )

    assert verify.compare(claim, [verify.Reading("Provider API", published)]) == []


def test_empty_set_matches_an_explicit_none_reading() -> None:
    claim = verify.Claim(
        target=verify.TargetRef(kind="fact", id="model#fits_hardware"),
        subject="lab/model",
        names=("Model",),
        field="model.fits_hardware",
        value=[],
        collector=COLLECTOR,
        sources=(verify.SourceRef(
            source_id="hardware-fit",
            snapshot_ref="sha256:" + "0" * 64,
            cited_regions=["fit"],
        ),),
    )

    assert verify.compare(claim, [verify.Reading("Model", "none")]) == []


def test_currency_with_mtok_header_is_a_per_million_token_price() -> None:
    quantity = verify.parse_quantity("$4", "MTok")
    assert quantity is not None
    assert (quantity.number, quantity.unit) == (4, "usd_per_1m_tokens")


def _price_claim(field: str, value: float, *, name: str = "Claude Opus 4.6") -> verify.Claim:
    return verify.Claim(
        target=verify.TargetRef(kind="fact", id=f"offering#{field}"),
        subject="provider/lab/model/global/standard",
        names=(name,),
        field=f"offering.price.{field}",
        label=field.replace("_", " ").title(),
        value=value,
        unit="usd_per_1m_tokens",
        collector=COLLECTOR,
        sources=(verify.SourceRef(source_id="pricing", snapshot_ref="sha256:" + "0" * 64,
                                  cited_regions=["prices"]),),
    )


def test_offering_price_reader_carries_models_across_continuation_rows() -> None:
    text = """\
Model | Type | Region | Price (/1M tokens) | Cached price (/1M tokens)
Claude Opus 4.6 | Input | Global | $5.00 | $0.50
| Output | Global | $25.00 | N/A
| Batch Input | Global | $2.50 | N/A
| Batch Output | Global | $12.50 | N/A
"""
    extractor = verify.OfferingPriceExtractor()
    for field, value in (("input", 5), ("output", 25), ("cached_input", .5),
                         ("batch_input", 2.5), ("batch_output", 12.5)):
        assert verify.compare(_price_claim(field, value),
                              extractor.extract(_price_claim(field, value), text)) == []


def test_offering_price_reader_reads_labeled_prices_inside_one_cell() -> None:
    text = """\
Model | Pricing (1M Tokens) | Pricing with Batch API (1M Tokens)
GPT-5.4 Global | Input: $2.50 Cached Input: $0.25 Output: $15 | Input: $1.25 Output: $7.50
"""
    extractor = verify.OfferingPriceExtractor()
    for field, value in (("input", 2.5), ("output", 15), ("cached_input", .25),
                         ("batch_input", 1.25), ("batch_output", 7.5)):
        claim = _price_claim(field, value, name="GPT-5.4")
        assert verify.compare(claim, extractor.extract(claim, text)) == []


def test_model_page_price_reader_applies_explicit_batch_discount() -> None:
    text = """\
GPT-6 Astra
Text tokens
Per 1M tokens
Input
$10.00
Cached input
$1.00
Output
$50.00
Batch and Flex are priced at 50% of Standard rates.
"""
    extractor = verify.ModelPageExtractor()
    for field, value in (("input", 10), ("output", 50), ("cached_input", 1),
                         ("batch_input", 5), ("batch_output", 25)):
        claim = _price_claim(field, value, name="GPT-6 Astra")
        assert verify.compare(claim, extractor.extract(claim, text)) == []


def test_offering_price_reader_reads_named_standard_and_batch_sections() -> None:
    text = """\
Gemini 3.8 Flash
gemini-3.8-flash
Standard
| Free Tier | Paid Tier, per 1M tokens in USD
Input price | Free of charge | $0.75 through December 31, 2026.
Output price (including thinking tokens) | Free of charge | $3.75 through December 31, 2026.
Context caching price | Free of charge | $0.075 through December 31, 2026.
Batch
| Free Tier | Paid Tier, per 1M tokens in USD
Input price | Not available | $0.375 through December 31, 2026.
Output price (including thinking tokens) | Not available | $1.875 through December 31, 2026.
Gemini 3.7 Flash
"""
    extractor = verify.OfferingPriceExtractor()
    for field, value in (("input", .75), ("output", 3.75), ("cached_input", .075),
                         ("batch_input", .375), ("batch_output", 1.875)):
        claim = _price_claim(field, value, name="Gemini 3.8 Flash")
        assert verify.compare(claim, extractor.extract(claim, text)) == []


ANTHROPIC_TABLES = """\
Model | Base tokens | Prompt caching
Name | Input | Output | 5m writes | 1h writes | Hits and refreshes
Claude Opus 5.5 For agentic coding | $4 / MTok | $20 / MTok | $5 / MTok | $8 / MTok | $0.40 / MTok
Claude Sonnet 5.5 The best mix | $2 / MTok | $10 / MTok | $2.50 / MTok | $4 / MTok | $0.20 / MTok
 Additional models
Claude Opus 5 | $5 / MTok | $25 / MTok | $6.25 / MTok | $10 / MTok | $0.50 / MTok
Claude Sonnet 5 | / MTok | / MTok | $2.50 / MTok | $4 / MTok | $0.30 / MTok
Batch processing
Model | Batch tokens
Name | Input | Output
Claude Opus 5.5 For agentic coding | $2 / MTok | $10 / MTok
Claude Opus 5 | $2.50 / MTok | $12.50 / MTok
"""


@pytest.mark.parametrize(("name", "field", "value"), [
    ("Claude Opus 5.5", "input", 4), ("Claude Opus 5.5", "cached_input", .4),
    ("Claude Opus 5.5", "batch_input", 2), ("Claude Opus 5.5", "batch_output", 10),
    ("Claude Sonnet 5.5", "output", 10), ("Claude Sonnet 5.5", "cached_input", .2),
    # Below the "Additional models" label, in the same table.
    ("Claude Opus 5", "input", 5), ("Claude Opus 5", "cached_input", .5),
    ("Claude Opus 5", "batch_output", 12.5), ("Claude Sonnet 5", "cached_input", .3),
])
def test_grouped_header_price_tables_are_read(name: str, field: str, value: float) -> None:
    """MODEL-235: Anthropic's two-row headers, read table by table."""
    claim = _price_claim(field, value, name=name)
    readings = verify.OfferingPriceExtractor().extract(claim, ANTHROPIC_TABLES)
    assert verify.compare(claim, readings) == []


@pytest.mark.parametrize(("name", "field", "sibling_value"), [
    ("Claude Opus 5", "input", 4), ("Claude Opus 5", "batch_output", 10),
    ("Claude Sonnet 5", "cached_input", .2), ("Claude Opus 5.5", "input", 5),
    # Sonnet 5 publishes no input price: a sibling's must not stand in for it.
    ("Claude Sonnet 5", "input", 2),
])
def test_grouped_header_tables_never_read_a_sibling_row(
        name: str, field: str, sibling_value: float) -> None:
    claim = _price_claim(field, sibling_value, name=name)
    readings = verify.OfferingPriceExtractor().extract(claim, ANTHROPIC_TABLES)
    assert verify.compare(claim, readings) != []


def test_a_continuation_row_is_never_another_models_scoped_price() -> None:
    """MODEL-235: "| Output | $10.00" under Sonnet 5.5 is not Opus 5.5's output."""
    text = """\
Model | Type | Price (/1M tokens) | Price (/1M tokens) > 200K
Sonnet 5.5 | Input | $2.00 | $2.00
| Output | $10.00 | $10.00
| Batch Output | $5.00 |
Opus 5.5 | Input | $4.00 | $4.00
| Output | $20.00 | $20.00
| Batch Output | $12.50 |
"""
    extractor = verify.OfferingPriceExtractor()
    right = _price_claim("output", 20, name="Opus 5.5")
    assert verify.compare(right, extractor.extract(right, text)) == []
    sibling = _price_claim("output", 10, name="Opus 5.5")
    assert verify.compare(sibling, extractor.extract(sibling, text)) != []


def test_a_usd_per_million_caching_price_needs_the_whole_name() -> None:
    text = "Claude Opus 5.5 caching is billed at a lower rate ($0.20 USD per million tokens)."
    claim = _price_claim("cached_input", .2, name="Claude Opus 5")
    with pytest.raises(verify.ExtractorError):
        verify.OfferingPriceExtractor().extract(claim, text)
    own = _price_claim("cached_input", .2, name="Claude Opus 5.5")
    assert verify.compare(own, verify.OfferingPriceExtractor().extract(own, text)) == []


def test_band_tiered_table_reads_the_price_column_of_the_lowest_band() -> None:
    """MODEL-341: the token-range cell is not the price.

    Shaped like Alibaba Model Studio's Singapore Qwen-Max table. The model's
    first row is the lowest band, and that row's price column is the base price.
    """

    def row(*cells: str) -> str:
        return " | ".join(cells)

    text = "\n".join([
        row("Model ID", "Deployment scope", "Mode", "Input tokens per request",
            "Input price (per 1 million tokens)",
            "Output price (per 1 million tokens) Chain of thought + answer",
            "Free quota (Note)"),
        row("qwen3.8-max-0902 context caching discount", "International",
            "Non-Thinking and Thinking modes", "0<Token≤1M", "$2", "$6",
            "1 million tokens"),
        row("qwen3-max context caching discount", "International",
            "Non-Thinking and Thinking modes", "0<Token≤32K", "$1.2", "$6",
            "1 million tokens"),
        row("32K<Token≤128K", "$2.4", "$12"),
        row("128K<Token≤256K", "$3", "$15"),
    ])
    extractor = verify.OfferingPriceExtractor()
    cases = (
        ("qwen3.8-max-0902", "input", 2, "$2"),
        ("qwen3.8-max-0902", "output", 6, "$6"),
        ("qwen3-max", "input", 1.2, "$1.2"),
        ("qwen3-max", "output", 6, "$6"),
    )
    for name, field, number, published in cases:
        claim = _price_claim(field, number, name=name)
        readings = extractor.extract(claim, text)
        assert [reading.value for reading in readings] == [published]
        assert verify.compare(claim, readings) == []

    higher = _price_claim("input", 2.4, name="qwen3-max")
    assert verify.compare(higher, extractor.extract(higher, text)) != []
    for field in ("cached_input", "batch_input", "batch_output"):
        claim = _price_claim(field, 2, name="qwen3.8-max-0902")
        assert extractor.extract(claim, text) == []


def test_scoped_provider_price_table_and_free_output_are_read() -> None:
    meta = """Models: muse-spark-1.3, muse-spark-1.1.
Usage | Price per 1M tokens
Input | $1.25
"""
    claim = _price_claim("input", 1.25, name="Muse Spark 1.3")
    assert verify.compare(claim, verify.OfferingPriceExtractor().extract(claim, meta)) == []

    jev = """Jev 1.13\nPrice (per Btok / per Mtok) | $42 / $0.042\nOutput tokens are free.\n"""
    for field, value in (("input", .042), ("output", 0)):
        claim = _price_claim(field, value, name="Jev 1.13")
        assert verify.compare(claim, verify.OfferingPriceExtractor().extract(claim, jev)) == []


def test_governance_prose_reader_handles_provider_wide_statements() -> None:
    extractor = verify.GovernanceProseExtractor()
    cases = [
        ("offering.data.trains_on_customer_data", False,
         "For Paid Services, Google does not use your prompts or responses "
         "to improve our products."),
        ("offering.data.zero_retention", False,
         "Customer data is typically retained for limited periods. "
         "For guaranteed zero data retention, use Vertex AI."),
        ("offering.data.retention", 30,
         "By default, all API requests and responses are stored for 30 days."),
        ("offering.data.zero_retention", True,
         "ZDR ensures that API request inputs and outputs are never persisted to disk."),
        ("offering.attestation.soc2", "type_2", "We are SOC 2 Type 2 compliant."),
        ("offering.attestation.baa", True,
         "Customers must review and accept Google's Business Associate Agreement (BAA)."),
    ]
    for facet, value, text in cases:
        claim = verify.Claim(
            target=TargetRef(kind="fact", id=f"offering#{facet}"),
            subject="provider/lab/model/global/standard", names=("Provider API",),
            field=facet, value=value,
            unit="days" if facet == "offering.data.retention" else None,
            collector=COLLECTOR,
            sources=(SourceRef(source_id="provider", snapshot_ref="sha256:" + "0" * 64,
                               cited_regions=["page"]),),
        )
        assert verify.compare(claim, extractor.extract(claim, text)) == []


def test_markdown_escaped_currency_is_a_price() -> None:
    quantity = verify.parse_quantity(r"\$0.26", "usd_per_1m_tokens")
    assert quantity is not None
    assert (quantity.number, quantity.unit) == (0.26, "usd_per_1m_tokens")


def test_explicit_no_training_sentence_matches_false() -> None:
    claim = verify.Claim(
        target=verify.TargetRef(kind="fact", id="offering#training"),
        subject="provider/model/global/standard",
        names=("Provider API",),
        field="offering.data.trains_on_customer_data",
        value=False,
        collector=COLLECTOR,
        sources=(verify.SourceRef(
            source_id="provider-doc",
            snapshot_ref="sha256:" + "0" * 64,
            cited_regions=["governance"],
        ),),
    )
    reading = verify.Reading(
        "Provider API",
        "does not use your inputs or outputs to train models or improve the service",
    )
    assert verify.compare(claim, [reading]) == []


def test_explicit_never_training_sentence_matches_false() -> None:
    claim = verify.Claim(
        target=verify.TargetRef(kind="fact", id="offering#training-never"),
        subject="provider/model/global/standard",
        names=("Provider API",),
        field="offering.data.trains_on_customer_data",
        value=False,
        collector=COLLECTOR,
        sources=(verify.SourceRef(
            source_id="provider-doc",
            snapshot_ref="sha256:" + "0" * 64,
            cited_regions=["governance"],
        ),),
    )
    reading = verify.Reading("Provider API", "will never use your data for model training")
    assert verify.compare(claim, [reading]) == []


@pytest.mark.parametrize(
    ("field", "published"),
    [
        ("offering.data.zero_retention", "Zero data retention"),
        ("offering.attestation.baa", "BAA available"),
    ],
)
def test_explicit_availability_phrases_match_true(field, published) -> None:
    claim = verify.Claim(
        target=verify.TargetRef(kind="fact", id="offering#available"),
        subject="provider/model/global/standard",
        names=("Provider API",),
        field=field,
        value=True,
        collector=COLLECTOR,
        sources=(verify.SourceRef(source_id="provider-doc",
                                  snapshot_ref="sha256:" + "0" * 64,
                                  cited_regions=["governance"]),),
    )
    assert verify.compare(claim, [verify.Reading("Provider API", published)]) == []


def test_soc2_type_2_phrase_matches_registered_enum() -> None:
    claim = verify.Claim(
        target=verify.TargetRef(kind="fact", id="offering#soc2"),
        subject="provider/model/global/standard",
        names=("Provider API",),
        field="offering.attestation.soc2",
        value="type_2",
        collector=COLLECTOR,
        sources=(verify.SourceRef(source_id="provider-doc",
                                  snapshot_ref="sha256:" + "0" * 64,
                                  cited_regions=["governance"]),),
    )
    assert verify.compare(claim, [verify.Reading("Provider API", "SOC 2 Type 2")]) == []


def test_canonical_model_ids_match_published_model_names() -> None:
    claim = verify.Claim(
        target=verify.TargetRef(kind="fact", id="xai/subscription/supergrok#models"),
        subject="xai/subscription/supergrok",
        names=("SuperGrok",),
        field="offering.subscription.models_covered",
        value=["xai/grok-4-6"],
        collector=COLLECTOR,
        sources=(verify.SourceRef(
            source_id="model-173-xai-consumer-pricing",
            snapshot_ref="sha256:" + "0" * 64,
            cited_regions=["page"],
        ),),
    )

    assert verify.compare(claim, [verify.Reading("SuperGrok", "Grok 4.6 model")]) == []


def test_canonical_model_ids_reject_the_same_slug_from_the_wrong_lab() -> None:
    claim = verify.Claim(
        target=verify.TargetRef(kind="fact", id="xai/subscription/supergrok#models"),
        subject="xai/subscription/supergrok",
        names=("SuperGrok",),
        field="offering.subscription.models_covered",
        value=["wrong-lab/grok-4-6"],
        collector=COLLECTOR,
        sources=(verify.SourceRef(
            source_id="model-173-xai-consumer-pricing",
            snapshot_ref="sha256:" + "0" * 64,
            cited_regions=["page"],
        ),),
    )

    assert verify.compare(
        claim, [verify.Reading("SuperGrok", "Grok 4.6 model")]
    ) == [verify.Diff("value", ["wrong-lab/grok-4-6"], "Grok 4.6 model")]


@pytest.mark.parametrize("plan", ["SuperGrok", "SuperGrok Plus"])
def test_subscription_page_models_include_inherited_plan_features(plan) -> None:
    claim = verify.Claim(
        target=verify.TargetRef(kind="fact", id=f"xai/subscription/{plan}#models"),
        subject=f"xai/subscription/{plan}",
        names=(plan,),
        field="offering.subscription.models_covered",
        value=["xai/grok-4-6"],
        collector=COLLECTOR,
        sources=(verify.SourceRef(
            source_id="model-173-xai-consumer-pricing",
            snapshot_ref="sha256:" + "0" * 64,
            cited_regions=["page"],
        ),),
    )
    page = """Free
$0/month
SuperGrok
$30/month
Grok 4.6 model
SuperGrok Plus
$100/month
Everything in SuperGrok, plus:
Create 1080p videos
"""

    readings = verify.SubscriptionPageExtractor().extract(claim, page)

    assert verify.compare(claim, readings) == []


@pytest.mark.parametrize(
    ("field", "value", "names", "page"),
    [
        (
            "offering.subscription.billing_period",
            "monthly",
            ("SuperGrok",),
            "SuperGrok\n$30/month\nGrok 4.6 model\n",
        ),
        (
            "offering.subscription.billing_period",
            "monthly",
            ("Claude Max 5x", "Max 5x"),
            """Features | Free | Pro | Max 5x | Max 20x
Billing cycle | n/a | Monthly and annual | Monthly | Monthly
""",
        ),
        (
            "offering.subscription.usage_allowance",
            "4x higher than standard limits",
            ("Google AI Pro", "AI Pro"),
            """Plan | Limit
Without an AI plan | Standard limits
AI Plus | 2x higher than standard limits
AI Pro | 4x higher than standard limits
AI Ultra | 5x or 20x higher than AI Pro limits depending on your subscription
""",
        ),
        (
            "offering.subscription.usage_allowance",
            "5x more usage than Pro",
            ("Claude Max 5x", "Max 5x"),
            "Choose 5x or 20x more usage than Pro\n",
        ),
        (
            "offering.subscription.price",
            100,
            ("ChatGPT Pro 5x", "Pro $100"),
            "Pro $200 unlocks 20x usage, while Pro $100 unlocks 5x higher usage than Plus.\n",
        ),
        (
            "offering.subscription.programmatic_or_agent_use",
            "Codex",
            ("ChatGPT Plus", "Plus plans"),
            "Plus plans include GPT-6 Astra in ChatGPT Work and Codex.\n",
        ),
        (
            "offering.subscription.programmatic_or_agent_use",
            "Expanded Google AI Studio, Google Antigravity, and Jules limits",
            ("Google AI Pro", "AI Pro"),
            """Features | Google AI Plus /mo | Google AI Pro /mo | Google AI Ultra 5x /mo
Google Antigravity
Agent requests | Limited | Expanded | Higher
Google AI Studio 6
Access to our most capable models | Limited | Expanded | Higher
Jules 7
Task limits | Limited | Expanded | Higher
""",
        ),
        (
            "offering.subscription.programmatic_or_agent_use",
            "Grok Bot access",
            ("SuperGrok Plus",),
            """SuperGrok
$30/month
Grok Bot access
SuperGrok Plus
$100/month
Everything in SuperGrok, plus:
Create 1080p videos
""",
        ),
    ],
)
def test_subscription_page_extracts_supported_plan_facts(field, value, names, page) -> None:
    claim = verify.Claim(
        target=verify.TargetRef(kind="fact", id=f"plan#{field}"),
        subject="provider/subscription/plan",
        names=names,
        field=field,
        value=value,
        collector=COLLECTOR,
        sources=(verify.SourceRef(
            source_id="subscription-page",
            snapshot_ref="sha256:" + "0" * 64,
            cited_regions=["page"],
        ),),
    )

    readings = verify.SubscriptionPageExtractor().extract(claim, page)

    assert verify.compare(claim, readings) == []


CHATGPT_MODELS = """Models
GPT-6 Astra
Plan: Go, Feature: GPT-6 Astra, No
Plan: Plus, Feature: GPT-6 Astra, Yes
Plan: Pro, Feature: GPT-6 Astra, Expanded
GPT-5.6 Sol Pro
Plan: Go, Feature: GPT-5.6 Sol Pro, No
Plan: Plus, Feature: GPT-5.6 Sol Pro, No
Plan: Pro, Feature: GPT-5.6 Sol Pro, Yes
GPT-5.6 Terra
Plan: Go, Feature: GPT-5.6 Terra, Limited access in Work and Codex on desktop
Plan: Plus, Feature: GPT-5.6 Terra, Yes
Plan: Pro, Feature: GPT-5.6 Terra, Unlimited*
GPT-5 Thinking Mini
Plan: Go, Feature: GPT-5 Thinking Mini, Yes
Plan: Plus, Feature: GPT-5 Thinking Mini, Expanded
Plan: Pro, Feature: GPT-5 Thinking Mini, Unlimited*
GPT Instant total context window
Plan: Plus, Feature: GPT Instant total context window, 54K
Codex
Plan: Plus, Feature: Codex, Yes
"""


def _chatgpt_models_claim(names, value):
    return verify.Claim(
        target=verify.TargetRef(kind="fact", id="openai/subscription/plan#models"),
        subject="openai/subscription/plan",
        names=names,
        field="offering.subscription.models_covered",
        value=value,
        collector=COLLECTOR,
        sources=(verify.SourceRef(
            source_id="model-201-openai-pricing",
            snapshot_ref="sha256:" + "0" * 64,
            cited_regions=["page"],
        ),),
    )


@pytest.mark.parametrize(
    ("names", "value"),
    [
        (("ChatGPT Plus", "Plus"), ["openai/gpt-6-astra", "openai/gpt-5-6-terra"]),
        (("ChatGPT Pro 20x", "Pro"), ["openai/gpt-6-astra", "openai/gpt-5-6-terra"]),
        (("ChatGPT Go", "Go"), ["openai/gpt-5-6-terra"]),
    ],
)
def test_subscription_page_reads_a_chatgpt_plan_column(names, value) -> None:
    # GPT-5.6 Sol Pro and GPT-5 Thinking Mini have no catalogue ID: the facet
    # holds catalogue IDs only, so they cannot be claimed and are not required.
    claim = _chatgpt_models_claim(names, value)

    readings = verify.SubscriptionPageExtractor().extract(claim, CHATGPT_MODELS)

    assert verify.compare(claim, readings) == []


@pytest.mark.parametrize(
    ("names", "value"),
    [
        # Go's GPT-6 Astra cell is "No".
        (("ChatGPT Go", "Go"), ["openai/gpt-6-astra", "openai/gpt-5-6-terra"]),
        # A catalogued model the column lists is missing from the claim.
        (("ChatGPT Plus", "Plus"), ["openai/gpt-6-astra"]),
    ],
)
def test_subscription_page_chatgpt_column_rejects_a_wrong_model_set(names, value) -> None:
    claim = _chatgpt_models_claim(names, value)

    readings = verify.SubscriptionPageExtractor().extract(claim, CHATGPT_MODELS)

    assert [d.field for d in verify.compare(claim, readings)] == ["value"]


TEAM_CARD = """Pricing varies by seat type and billing interval:
Standard seats
$25 per member per month, billed monthly
$20 per member per month, billed annually
Premium seats
$125 per member per month, billed monthly
$100 per member per month, billed annually
"""
MISTRAL_CARD = """Popular
Pro
Education plan
Full access to Vibe for all-day coding and long-running tasks.
$14.99
/mo
Excluding taxes
"""
ZAI_CARD = """## Max
Max Usage
Power use
$117.6/month$168/month
Subscribe
- 14× Lite usage
"""
MINIMAX_TABLE = """| Plus | Max | Ultra
Price | $22 /month | $55 /month | $132 /month
Best for | Personal projects | Daily coding | Heavy Agent workflows
"""
GEMINI_TIERS = """Starting at:
$99.99/ month
$99.99/ month: 5x higher usage limits vs. AI Pro
$199.99 / month: 20x higher usage limits vs. AI Pro
"""
SEAT_TABLE = """Seat type | Price per seat | Included access | Billing model
Standard seat | Monthly plan: $25 per user per month Annual plan: $20 per user per month, billed annually | ChatGPT, ChatGPT Work, and Codex | Fixed per-user cost
Premium seat | Monthly plan: $125 per user per month Annual plan: $100 per user per month, billed annually | ChatGPT, ChatGPT Work, and Codex with higher usage limits | Fixed per-user cost
"""
MODEL_LIST_TABLE = """| Pro
Supported models | Only the following exact model versions are supported: Recommended models: qwen3.7-plus (vision), glm-5 , and MiniMax-M2.5 More models: qwen3-max-2026-01-23 , and glm-4.7 Models not listed above are not supported.
Price | $ 50 /month
"""


@pytest.mark.parametrize(
    ("field", "value", "names", "page"),
    [
        ("offering.subscription.price", 25, ("Standard seats",), TEAM_CARD),
        ("offering.subscription.billing_period", "monthly", ("Standard seats",), TEAM_CARD),
        ("offering.subscription.price", 125, ("Premium seats",), TEAM_CARD),
        ("offering.subscription.price", 14.99, ("Pro",), MISTRAL_CARD),
        ("offering.subscription.billing_period", "monthly", ("Pro",), MISTRAL_CARD),
        ("offering.subscription.price", 168, ("Max",), ZAI_CARD),
        ("offering.subscription.billing_period", "monthly", ("Max",), ZAI_CARD),
        ("offering.subscription.price", 55, ("Max",), MINIMAX_TABLE),
        ("offering.subscription.billing_period", "monthly", ("Ultra",), MINIMAX_TABLE),
        ("offering.subscription.price", 199.99, ("Google AI Ultra 20x", "Ultra 20x"),
         GEMINI_TIERS),
        ("offering.subscription.usage_allowance", "5x higher usage limits vs. AI Pro",
         ("Google AI Ultra 5x", "Ultra 5x"), GEMINI_TIERS),
        ("offering.subscription.price", 125, ("Premium seat",), SEAT_TABLE),
        ("offering.subscription.programmatic_or_agent_use",
         "ChatGPT, ChatGPT Work, and Codex", ("Standard seat",), SEAT_TABLE),
        ("offering.subscription.models_covered",
         ["qwen/qwen3-7-plus", "zhipu/glm-5", "minimax/minimax-m2-5", "zhipu/glm-4-7"],
         ("Pro",), MODEL_LIST_TABLE),
        ("offering.subscription.models_covered", ["zhipu/glm-5-3", "zhipu/glm-5-3-flash"],
         ("Lite",), "Supported Models\nAll plans support GLM-5.3, GLM-5.3-Flash.\n"),
        ("offering.subscription.models_covered", ["xai/grok-4-6"], ("Business",),
         "### Models\nImagine\nVoice\nGrok 4.6\n### Security & compliance\n"),
    ],
)
def test_subscription_page_reads_plan_cards_and_tables(field, value, names, page) -> None:
    claim = verify.Claim(
        target=verify.TargetRef(kind="fact", id=f"plan#{field}"),
        subject="provider/subscription/plan",
        names=names,
        field=field,
        value=value,
        collector=COLLECTOR,
        sources=(verify.SourceRef(
            source_id="subscription-page",
            snapshot_ref="sha256:" + "0" * 64,
            cited_regions=["page"],
        ),),
    )

    readings = verify.SubscriptionPageExtractor().extract(claim, page)

    assert verify.compare(claim, readings) == []


PLAN_ARTICLE = """Skip to main content
What is the Enterprise plan?
Updated over
Enterprise uses a single seat type, priced per user per month and billed annually.
All usage is billed at API rates. There are no per-seat usage limits and no included token allowance.
"""


@pytest.mark.parametrize(
    ("field", "value", "names", "page"),
    [
        ("offering.subscription.usage_allowance",
         "There are no per-seat usage limits and no included token allowance.",
         ("Claude Enterprise", "Enterprise plan"), PLAN_ARTICLE),
        ("offering.subscription.billing_period", "annual",
         ("Claude Enterprise", "Enterprise plan"), PLAN_ARTICLE),
        ("offering.subscription.usage_allowance", "Up to 6,000 requests per 5 hours",
         ("Pro",), "| Pro\nQuota | Up to 6,000 requests per 5 hours\n"),
    ],
)
def test_subscription_page_reads_plan_articles_and_quota_rows(field, value, names, page) -> None:
    claim = verify.Claim(
        target=verify.TargetRef(kind="fact", id=f"plan#{field}"),
        subject="provider/subscription/plan",
        names=names,
        field=field,
        value=value,
        collector=COLLECTOR,
        sources=(verify.SourceRef(
            source_id="subscription-page",
            snapshot_ref="sha256:" + "0" * 64,
            cited_regions=["page"],
        ),),
    )

    readings = verify.SubscriptionPageExtractor().extract(claim, page)

    assert verify.compare(claim, readings) == []


def test_a_plan_article_does_not_speak_for_another_plan() -> None:
    claim = verify.Claim(
        target=verify.TargetRef(kind="fact", id="plan#allowance"),
        subject="provider/subscription/plan",
        names=("Claude Team", "Team plan"),
        field="offering.subscription.usage_allowance",
        value="There are no per-seat usage limits and no included token allowance.",
        collector=COLLECTOR,
        sources=(verify.SourceRef(
            source_id="subscription-page",
            snapshot_ref="sha256:" + "0" * 64,
            cited_regions=["page"],
        ),),
    )

    readings = verify.SubscriptionPageExtractor().extract(claim, PLAN_ARTICLE)

    assert verify.compare(claim, readings) != []


#: An abridged Team plan help article (support.claude.com, read 2026-09-29): a skip
#: link, title, "Updated" stamp, one labelled line per seat, then the help
#: centre's footer (MODEL-240).
TEAM_HELP_PAGE = """Skip to main content
What is the Team plan?
Updated over a week ago
The Team plan is a paid plan for our Claude chat experience built for ambitious teams.
Usage limits differ between Standard and Premium seats in the following ways:
Standard seats: Team plan Standard seats include 1.25x the Pro plan's per-session usage \
allowance and have a weekly usage limit that applies across all models.
Premium seats: Team plan Premium seats include 6.25x the Pro plan's per-session usage \
allowance and have a weekly usage limit that applies across all models.
Did this answer your question?
Related Articles
What is the Enterprise plan?
"""

_CHROME = {"Skip to main content", "Updated over a week ago", "Did this answer your question?",
           "Related Articles", "What is the Enterprise plan?"}


#: The names MODEL-201 filed for the Premium seat, as the verification queue has them.
_PREMIUM = ("Claude Team (Premium seat)", "Premium seats", "Team plan", "Team", "team-premium")


def _seat_claim(names, value, field="offering.subscription.usage_allowance"):
    return verify.Claim(
        target=verify.TargetRef(kind="fact", id=f"anthropic/subscription/team#{field}"),
        subject="anthropic/subscription/team",
        names=names,
        field=field,
        value=value,
        collector=COLLECTOR,
        sources=(verify.SourceRef(
            source_id="subscription-page",
            snapshot_ref="sha256:" + "0" * 64,
            cited_regions=["page"],
        ),),
    )


@pytest.mark.parametrize(
    ("names", "value"),
    [
        (_PREMIUM, "6.25x the Pro plan's per-session usage allowance"),
        (("Claude Team (Standard seat)", "Standard seats", "Team plan", "Team", "team-standard"),
         "1.25x the Pro plan's per-session usage allowance"),
    ],
)
def test_a_plan_article_reads_the_allowance_its_seat_line_states(names, value) -> None:
    claim = _seat_claim(names, value)

    readings = verify.SubscriptionPageExtractor().extract(claim, TEAM_HELP_PAGE)

    assert verify.compare(claim, readings) == []


def test_a_seat_line_does_not_speak_for_another_seat() -> None:
    claim = _seat_claim(_PREMIUM, "1.25x the Pro plan's per-session usage allowance")

    readings = verify.SubscriptionPageExtractor().extract(claim, TEAM_HELP_PAGE)

    assert verify.compare(claim, readings) != []


@pytest.mark.parametrize(
    "field",
    ["offering.subscription.usage_allowance", "offering.subscription.coverage_quote",
     "offering.subscription.programmatic_or_agent_use"],
)
def test_no_subscription_reading_is_page_chrome(field) -> None:
    claim = _seat_claim(_PREMIUM, "a value this page does not state", field)

    readings = verify.SubscriptionPageExtractor().extract(claim, TEAM_HELP_PAGE)
    diffs = verify.compare(claim, readings)

    assert not {r.value for r in readings} & _CHROME
    assert not {d.found for d in diffs} & _CHROME


@pytest.mark.parametrize(
    ("field", "value", "names", "page"),
    [
        # Another seat's price, and a seat's annual rate when a monthly one is published.
        ("offering.subscription.price", 125, ("Standard seats",), TEAM_CARD),
        ("offering.subscription.price", 20, ("Standard seats",), TEAM_CARD),
        # Another tier's column and another tier's line.
        ("offering.subscription.price", 22, ("Max",), MINIMAX_TABLE),
        ("offering.subscription.price", 99.99, ("Google AI Ultra 20x", "Ultra 20x"),
         GEMINI_TIERS),
        # A price published only as billed annually is not a monthly plan.
        ("offering.subscription.billing_period", "monthly", ("Pro",),
         "Pro\nAdvanced answers\n$17\n/month when billed annually\n"),
    ],
)
def test_subscription_page_plan_cards_reject_a_sibling_value(field, value, names, page) -> None:
    claim = verify.Claim(
        target=verify.TargetRef(kind="fact", id=f"plan#{field}"),
        subject="provider/subscription/plan",
        names=names,
        field=field,
        value=value,
        collector=COLLECTOR,
        sources=(verify.SourceRef(
            source_id="subscription-page",
            snapshot_ref="sha256:" + "0" * 64,
            cited_regions=["page"],
        ),),
    )

    readings = verify.SubscriptionPageExtractor().extract(claim, page)

    assert verify.compare(claim, readings) != []


@pytest.mark.parametrize(
    "page",
    [
        "Plus plans do not include Codex.",
        "Plus plans don't include Codex.",
        "Plus plans include no Codex.",
        "Plus plans no longer include Codex.",
        "Plus plans never include Codex.",
        "Plus plans will not include Codex.",
        "Codex is not included with Plus plans.",
    ],
)
def test_subscription_page_preserves_codex_restrictions(page) -> None:
    claim = verify.Claim(
        target=verify.TargetRef(kind="fact", id="openai/subscription/plus#agent-use"),
        subject="openai/subscription/plus",
        names=("ChatGPT Plus", "Plus plans"),
        field="offering.subscription.programmatic_or_agent_use",
        value="Codex",
        collector=COLLECTOR,
        sources=(verify.SourceRef(
            source_id="subscription-page",
            snapshot_ref="sha256:" + "0" * 64,
            cited_regions=["page"],
        ),),
    )

    readings = verify.SubscriptionPageExtractor().extract(claim, page)

    assert readings == [verify.Reading("ChatGPT Plus", page)]
    assert verify.compare(claim, readings) == [verify.Diff("value", "Codex", page)]


def test_zero_retention_phrase_means_zero_retention_days() -> None:
    claim = verify.Claim(
        target=verify.TargetRef(kind="fact", id="offering#retention"),
        subject="provider/model/global/standard",
        names=("Provider API",),
        field="offering.data.retention",
        value=0,
        unit="days",
        collector=COLLECTOR,
        sources=(verify.SourceRef(source_id="provider-doc",
                                  snapshot_ref="sha256:" + "0" * 64,
                                  cited_regions=["governance"]),),
    )
    assert verify.compare(claim, [verify.Reading("Provider API", "zero data retention")]) == []


def test_a_mismatch_records_a_structured_diff(store, regions, log) -> None:
    _seeded_run(store, regions, log)
    record = log.latest()[("evidence", "sol-max-filed-as-default")]
    assert record.outcome == "mismatch"
    assert json.loads(record.diff) == [
        {"field": "effort", "expected": "default", "found": "max"}]
    sibling = log.latest()[("evidence", "sol-copied-from-sibling")]
    diff = {d["field"]: d for d in json.loads(sibling.diff)}
    assert diff["model"] == {"field": "model", "expected": "GPT-6 Sol", "found": "GPT-6 Astra"}
    assert diff["value"]["expected"] == "58.3 percent"
    assert diff["value"]["found"] == "64.0 percent"


def test_mismatches_and_unreachables_are_requeued_for_recrawl(store, regions, log) -> None:
    _seeded_run(store, regions, log)
    recrawl = {t.id: outcome for t, outcome in verify.Queue(log.directory).recrawl_requests()}
    assert recrawl == {e["id"]: e["expect"] for e in SPEC["claims"]
                       if e["expect"] in ("mismatch", "unreachable")}


def test_a_second_run_has_nothing_left_to_do(store, regions, log) -> None:
    _seeded_run(store, regions, log)
    before = log.path.read_text()
    report = verify.run(verify.Queue(log.directory), log, regions,
                        verify.deterministic_extractors(), today=TODAY)
    # Only the skipped claim is still pending: it was never verified.
    assert [r.target.id for r in report.results] == ["sol-prose-no-extractor"]
    assert log.path.read_text() == before


# --- two keys ----------------------------------------------------------------------------------


class _FakeLLM:
    def __init__(self, reply: str, *, family: str = "claude",
                 agent: str = "verify-llm") -> None:
        self.reply = reply
        self.calls: list[str] = []
        self.extractor = verify.LLMExtractor(
            self, agent=agent, model="claude-sonnet-5", model_family=family)

    def __call__(self, prompt: str) -> str:
        self.calls.append(prompt)
        return self.reply


def _prose_claim(store, collector=COLLECTOR) -> verify.Claim:
    entry = next(e for e in SPEC["claims"] if e["id"] == "sol-prose-no-extractor")
    claim = _claim(entry, store)
    return verify.Claim(**{**claim.__dict__, "collector": collector})


def test_the_llm_extractor_verifies_prose_and_records_its_model(store, regions) -> None:
    llm = _FakeLLM(json.dumps([{
        "subject": "GPT-6 Sol",
        "value": "400,000",
        "unit": "tokens",
        "quoted_sentence": "It accepts up to 400,000 tokens of context.",
    }]))
    extractors = [*verify.deterministic_extractors(), llm.extractor]
    result = verify.verify(_prose_claim(store), regions, extractors, today=TODAY)
    assert result.outcome == "verified"
    assert result.verification.verifier == VerificationActor(
        agent="verify-llm", model_family="claude", method="llm-extract:claude-sonnet-5")
    assert "400,000 tokens of context" in llm.calls[0]
    assert '"quoted_sentence"' in llm.calls[0]


def test_deterministic_extractors_are_used_before_the_llm(store, regions) -> None:
    llm = _FakeLLM("[]")
    entry = next(e for e in SPEC["claims"] if e["id"] == "sol-default")
    result = verify.verify(_claim(entry, store), regions,
                           [llm.extractor, *verify.deterministic_extractors()], today=TODAY)
    assert result.outcome == "verified"
    assert result.verification.verifier.model_family == "deterministic"
    assert llm.calls == []


def test_an_unparseable_llm_reply_is_not_evidence_of_absence(store, regions) -> None:
    llm = _FakeLLM("I think it is about 400k?")
    result = verify.verify(_prose_claim(store), regions,
                           [*verify.deterministic_extractors(), llm.extractor], today=TODAY)
    assert result.outcome == "skipped"
    assert result.verification is None
    assert "extractor_error" in result.reason


def test_llm_reader_accepts_cli_markdown_fence_and_scoped_absence(store, regions) -> None:
    prose = _prose_claim(store)
    present = _FakeLLM("""```json
[{"subject":"GPT-6 Sol","value":"400,000","unit":"tokens",
  "quoted_sentence":"It accepts up to 400,000 tokens of context."}]
```""")
    assert verify.verify(prose, regions, [present.extractor], today=TODAY).outcome == "verified"

    absent_claim = verify.Claim(**{**prose.__dict__, "value": None})
    absent = _FakeLLM("[]")
    result = verify.verify(absent_claim, regions, [absent.extractor], today=TODAY)
    assert result.outcome == "verified"


# --- conditions stated once for a region (MODEL-233) -------------------------------------------

READER_REPLIES = yaml.safe_load((FIXTURES / "captioned-results.reader.yaml").read_text())
READER_CLAIMS = {e["id"]: e for e in SPEC["reader_claims"]}


def _replay(replies: dict) -> verify.LLMExtractor:
    """A reader that answers from recorded replies, by the label the prompt asks about."""

    def complete(prompt: str) -> str:
        label = re.search(r'gives for "([^"]+)"', prompt).group(1)
        return json.dumps(replies.get(label, []))

    return verify.LLMExtractor(complete, agent="verify-llm", model="claude-sonnet-5",
                               model_family="claude")


@pytest.mark.parametrize("claim_id", list(READER_CLAIMS))
def test_every_reader_claim_ends_as_expected(claim_id, store, regions) -> None:
    entry = READER_CLAIMS[claim_id]
    claim = _claim(entry, store)
    reader = _replay(READER_REPLIES["replies"])

    result = verify.verify(claim, regions, [*verify.deterministic_extractors(), reader],
                           today=TODAY)
    assert result.outcome == entry["expect"], result
    if "expect_reader_diff" in entry:
        alone = verify.verify(claim, regions, [reader], today=TODAY)
        assert sorted(d.field for d in alone.diffs) == entry["expect_reader_diff"], alone.diffs


def test_a_caption_effort_the_reader_leaves_null_is_the_model_233_mismatch(store, regions) -> None:
    claim = _claim(READER_CLAIMS["nimbus-caption-max"], store)
    result = verify.verify(claim, regions, [_replay(READER_REPLIES["before_model_233"])],
                           today=TODAY)
    assert result.outcome == "mismatch"
    assert [d.to_dict() for d in result.diffs] == [
        {"field": "effort", "expected": "max", "found": None}]


@pytest.mark.parametrize("effort, condition_sentence", [
    ("xhigh", None),
    ("xhigh", "Unless otherwise noted, all Nimbus 3 results use extended thinking at max effort"),
    ("max", "All Nimbus 3 results use max effort."),
], ids=["level-not-in-region", "level-not-in-sentence-or-region", "sentence-not-in-region"])
def test_an_effort_the_region_does_not_state_is_not_evidence(
        effort, condition_sentence, store, regions) -> None:
    # Told to carry a caption's condition to every value, a reader can attach one the
    # region never states, or quote a caption the region does not have.
    claim = _claim({**READER_CLAIMS["nimbus-caption-max"], "conditions": {"effort": effort}},
                   store)
    reader = _replay({"Coding": [{
        "subject": "Nimbus 3", "value": "71.2", "effort": effort,
        "quoted_sentence": "Coding | 71.2 | 64.0", "condition_sentence": condition_sentence,
    }]})
    result = verify.verify(claim, regions, [reader], today=TODAY)
    assert result.outcome == "skipped"
    assert "extractor_error" in result.reason


CAPTION = ("Unless otherwise noted, all Nimbus 3 results use extended thinking at max effort, "
           "default sampling settings, averaged over five trials.")


@pytest.mark.parametrize("subject, value, effort", [
    ("GPT-6 Sol", "64.0", "max"),
    ("Nimbus 3", "71.2", "default"),
], ids=["caption-for-another-model", "caption-word-that-is-not-an-effort"])
def test_a_caption_does_not_lend_an_effort_it_does_not_state_for_the_value(
        subject, value, effort, store, regions) -> None:
    # The caption states max for Nimbus 3 only, and "default" only for sampling.
    claim = _claim({**READER_CLAIMS["nimbus-caption-max"], "names": [subject],
                    "value": float(value), "conditions": {"effort": effort}}, store)
    reader = _replay({"Coding": [{
        "subject": subject, "value": value, "effort": effort,
        "quoted_sentence": "Coding | 71.2 | 64.0", "condition_sentence": CAPTION,
    }]})
    result = verify.verify(claim, regions, [reader], today=TODAY)
    assert result.outcome == "skipped"
    assert "extractor_error" in result.reason


@pytest.mark.parametrize("sibling_in_reply", [True, False], ids=["sibling-row", "no-sibling-row"])
def test_a_caption_for_a_longer_name_does_not_lend_its_effort_to_a_sibling(
        sibling_in_reply, store) -> None:
    # The Opus 5.5 system card caption names "Claude Opus 5.5"; the Claude Opus 5
    # column beside it has no stated effort (MODEL-233 review).
    caption = ("Unless otherwise noted, all Claude Opus 5.5 results use the following "
               "standard configuration: adaptive thinking at max effort.")
    regions = _InlineRegions("Evaluation | Claude Opus 5.5 | Claude Opus 5\n"
                             f"SWE-bench Pro | 89.9 | 79.2\n{caption}\n")
    claim = _claim({**READER_CLAIMS["nimbus-caption-max"], "names": ["Claude Opus 5"],
                    "label": "SWE-bench Pro", "value": 79.2}, store)
    rows = [{"subject": "Claude Opus 5", "value": "79.2", "effort": "max",
             "quoted_sentence": "SWE-bench Pro | 89.9 | 79.2", "condition_sentence": caption}]
    if sibling_in_reply:
        rows.append({**rows[0], "subject": "Claude Opus 5.5", "value": "89.9"})
    result = verify.verify(claim, regions, [_replay({"SWE-bench Pro": rows})], today=TODAY)
    assert result.outcome == "skipped"
    assert "extractor_error" in result.reason


OPUS_TABLE = "Evaluation | Claude Opus 5.5 | Claude Opus 5\nSWE-bench Pro | 89.9 | 79.2\n"


@pytest.mark.parametrize("region, effort, quote, condition_sentence", [
    (OPUS_TABLE + "Default sampling settings were used.\n", "default",
     "SWE-bench Pro | 89.9 | 79.2\nDefault sampling settings were used.", None),
    (OPUS_TABLE + "Claude Opus 5.5 SWE-bench Pro results use max effort.\n", "max",
     "SWE-bench Pro | 89.9 | 79.2", "Claude Opus 5.5 SWE-bench Pro results use max effort."),
    ("Claude Opus 5.5 uses max effort.\n" + OPUS_TABLE, "max",
     "SWE-bench Pro | 89.9 | 79.2", None),
    (OPUS_TABLE, "max", "SWE-bench Pro | 89.9 | 79.2", None),
    (OPUS_TABLE + "Claude Opus 5.5 uses max effort.\n", "max",
     "SWE-bench Pro | 89.9 | 79.2\nClaude Opus 5.5 uses max effort.", None),
], ids=["row-word-that-is-not-an-effort", "benchmark-sentence-about-another-model",
        "first-line-about-another-model", "qualifier-the-source-does-not-have",
        "quote-line-without-the-value"])
def test_the_region_must_state_the_effort_for_this_model(
        region, effort, quote, condition_sentence, store) -> None:
    # Independent review (codex) of the MODEL-233 fix: each of these verified a
    # Claude Opus 5 value at an effort the region states for no Opus 5 value.
    claim = _claim({**READER_CLAIMS["nimbus-caption-max"], "names": ["Claude Opus 5"],
                    "label": "SWE-bench Pro", "value": 79.2,
                    "conditions": {"effort": effort}}, store)
    subject = "Claude Opus 5 (max effort)" if region == OPUS_TABLE else "Claude Opus 5"
    rows = [{"subject": subject, "value": "79.2", "effort": effort,
             "quoted_sentence": quote, "condition_sentence": condition_sentence},
            {"subject": "Claude Opus 5.5", "value": "89.9", "effort": None,
             "quoted_sentence": quote}]
    result = verify.verify(claim, _InlineRegions(region), [_replay({"SWE-bench Pro": rows})],
                           today=TODAY)
    assert result.outcome == "skipped"
    assert "extractor_error" in result.reason


def test_an_effort_column_with_a_standard_cell_reads_as_default(store) -> None:
    claim = _claim({**READER_CLAIMS["nimbus-caption-max"], "value": 1.0,
                    "conditions": {"effort": "default"}}, store)
    reader = _replay({"Coding": [{"subject": "Nimbus 3", "value": "1", "effort": "default",
                                  "quoted_sentence": "Nimbus 3 | standard | 1"}]})
    regions = _InlineRegions("Model | Effort | Coding\nNimbus 3 | standard | 1\n")
    assert verify.verify(claim, regions, [reader], today=TODAY).outcome == "verified"


def test_a_heading_effort_needs_no_condition_sentence(store, regions) -> None:
    # Mistral's reply for DeepSeek-V4.1-Flash's HLE w/ tools row (MODEL-233): the
    # heading's effort, with no condition sentence quoted. A caption is not a
    # heading, so the same reply against the captioned region is refused.
    claim = _claim(READER_CLAIMS["nimbus-caption-max"], store)
    reader = _replay({"Coding": [{
        "subject": "Nimbus 3", "value": "71.2", "effort": "max", "condition_sentence": None,
        "quoted_sentence": "Coding | 71.2 | 64.0",
    }]})
    headed = _InlineRegions("Comparison with frontier models (Max reasoning effort)\n"
                            "Benchmark | Nimbus 3 | GPT-6 Sol\nCoding | 71.2 | 64.0\n")
    assert verify.verify(claim, headed, [reader], today=TODAY).outcome == "verified"
    assert verify.verify(claim, regions, [reader], today=TODAY).outcome == "skipped"
    row_first = _InlineRegions("GPT-6 Sol (max effort) | 64.0\nNimbus 3 | 71.2\n")
    reader = _replay({"Coding": [{"subject": "Nimbus 3", "value": "71.2", "effort": "max",
                                  "quoted_sentence": "Nimbus 3 | 71.2"}]})
    assert verify.verify(claim, row_first, [reader], today=TODAY).outcome == "skipped"


class _InlineRegions:
    """Every cited region is ``text``."""

    def __init__(self, text: str) -> None:
        self.body = text

    def text(self, source_id, copy_ref, region_id):
        return self.body


def test_an_effort_named_in_the_model_cell_needs_no_condition_sentence(store) -> None:
    claim = _claim(READER_CLAIMS["nimbus-caption-max"], store)
    claim = verify.Claim(**{**claim.__dict__, "value": 66.6})
    reader = _replay({"Coding": [{
        "subject": "Nimbus 3 (max effort)", "value": "66.6", "effort": "max",
        "quoted_sentence": "Nimbus 3 (max effort) | 66.6",
    }]})
    regions = _InlineRegions("Model | Score\nNimbus 3 (max effort) | 66.6\n")
    assert verify.verify(claim, regions, [reader], today=TODAY).outcome == "verified"


def test_a_prompt_change_does_not_reuse_cached_replies(tmp_path, store, regions,
                                                        monkeypatch) -> None:
    calls: list[str] = []
    replies = READER_REPLIES["replies"]

    def complete(prompt: str) -> str:
        calls.append(prompt)
        return json.dumps(replies["Coding"])

    reader = verify.LLMExtractor(complete, agent="verify-llm", model="claude-sonnet-5",
                                 model_family="claude",
                                 cache=verify.LLMCache(tmp_path / "llm-cache"))
    claim = _claim(READER_CLAIMS["nimbus-caption-max"], store)
    verify.verify(claim, regions, [reader], today=TODAY)
    verify.verify(claim, regions, [reader], today=TODAY)
    monkeypatch.setattr(verify, "LLM_PROMPT", verify.LLM_PROMPT + "\nOne more rule.\n")
    verify.verify(claim, regions, [reader], today=TODAY)
    assert len(calls) == 2


def test_a_scoped_key_value_region_can_verify_not_disclosed(store) -> None:
    from decision.model import Fact

    body = b"Model: Nimbus 3\nContext Window: 128K tokens\n"
    ref = store.put(body)
    fact = Fact(
        id="lab/nimbus-3#model.max_output_tokens",
        subject={"kind": "model", "id": "lab/nimbus-3"},
        facet="model.max_output_tokens",
        state="not_disclosed",
        sources=[{
            "source_id": "nimbus-spec",
            "snapshot_ref": ref,
            "cited_regions": ["spec"],
        }],
    )
    claim = verify.Claim.from_fact(fact, names=["Nimbus 3"], collector=COLLECTOR)

    class Regions:
        def text(self, source_id: str, copy_ref: str, region_id: str) -> str | None:
            return body.decode()

    result = verify.verify(claim, Regions(), verify.deterministic_extractors(), today=TODAY)
    assert result.outcome == "verified"


@pytest.mark.parametrize(
    ("label", "value", "unit"),
    [
        ("context window", 1_050_000, "tokens"),
        ("function calling", True, None),
        ("input", ["text", "image"], None),
    ],
)
def test_model_page_labels_are_read_deterministically(label, value, unit) -> None:
    text = """\
GPT-6 Astra
1,050,000 context window
Modalities
Input
Text, Image
Features
Function calling
Supported
"""
    claim = verify.Claim(
        target=TargetRef(kind="fact", id=f"astra-{label}"),
        subject="openai/gpt-6-astra",
        names=("GPT-6 Astra",),
        field=label,
        label=label,
        value=value,
        unit=unit,
        collector=COLLECTOR,
        sources=(SourceRef(
            source_id="astra-model-page",
            snapshot_ref="sha256:" + "0" * 64,
            cited_regions=["spec"],
        ),),
    )

    readings = verify.ModelPageExtractor().extract(claim, text)
    assert verify.compare(claim, readings) == []


def test_an_unrelated_table_does_not_block_a_later_deterministic_reader() -> None:
    text = """\
Model | Price
GPT-6 Astra | $10
GPT-6 Astra
1,050,000 context window
"""
    claim = verify.Claim(
        target=TargetRef(kind="fact", id="astra-context"),
        subject="openai/gpt-6-astra",
        names=("GPT-6 Astra",),
        field="model.context_window",
        label="context window",
        value=1_050_000,
        unit="tokens",
        collector=COLLECTOR,
        sources=(SourceRef(
            source_id="astra-model-page",
            snapshot_ref="sha256:" + "0" * 64,
            cited_regions=["spec"],
        ),),
    )

    class Regions:
        def text(self, source_id: str, copy_ref: str, region_id: str) -> str | None:
            return text

    result = verify.verify(claim, Regions(), verify.deterministic_extractors(), today=TODAY)
    assert result.outcome == "verified"


def test_structured_snapshot_rows_are_read_by_subject_and_label() -> None:
    text = json.dumps({
        "source_url": "https://board.example.test/results",
        "rows": [{"model_name": "GPT-6 Astra", "rating": 1498.47,
                  "leaderboard_publish_date": "2026-09-13"}],
    })
    claim = verify.Claim(
        target=TargetRef(kind="evidence", id="astra-arena"),
        subject="openai/gpt-6-astra",
        names=("GPT-6 Astra",),
        field="arena_elo_style_control",
        label="rating",
        value=1498.47,
        unit="Arena score (Elo scale)",
        conditions={"date": "2026-09-13"},
        collector=COLLECTOR,
        sources=(SourceRef(
            source_id="arena-snapshot",
            snapshot_ref="sha256:" + "0" * 64,
            cited_regions=["rows"],
        ),),
    )

    readings = verify.StructuredDataExtractor().extract(claim, text)
    assert verify.compare(claim, readings) == []


def test_structured_reader_verifies_evidence_uncertainty_and_quality_metadata() -> None:
    sources = {
        "arena": json.dumps({"rows": [{
            "model_name": "GPT-6 Astra",
            "rating": 1507.5817,
            "rating_lower": 1499.4288,
            "rating_upper": 1515.7347,
            "vote_count": 5783.0,
            "leaderboard_publish_date": "2026-09-13",
        }]}),
        "math": json.dumps({"rows": [{
            "model": "GPT-6 Astra",
            "accuracy": 95.83,
            "release_warning": True,
        }]}),
        "math-quality": json.dumps({"rows": [{
            "model": "AIME 2026",
            "deprecated": True,
        }]}),
    }

    class Regions:
        def text(self, source_id: str, copy_ref: str, region_id: str) -> str | None:
            return sources[source_id]

    def ref(source_id: str) -> SourceRef:
        return SourceRef(
            source_id=source_id,
            snapshot_ref="sha256:" + "0" * 64,
            cited_regions=["rows"],
        )

    arena = verify.Claim(
        target=TargetRef(kind="evidence", id="astra-arena"),
        subject="openai/gpt-6-astra",
        names=("GPT-6 Astra",),
        field="arena_elo_overall",
        label="rating",
        value={
            "score": 1507.58,
            "interval": [1499.43, 1515.73],
            "n": 5783,
            "quality_flags": [],
        },
        unit="Arena score (Elo scale)",
        conditions={"date": "2026-09-13"},
        collector=COLLECTOR,
        sources=(ref("arena"),),
    )
    quality = verify.Claim(
        target=TargetRef(kind="evidence", id="astra-aime"),
        subject="openai/gpt-6-astra",
        names=("GPT-6 Astra",),
        field="aime_2026",
        label="accuracy",
        value={
            "score": 95.83,
            "interval": None,
            "n": None,
            "quality_flags": ["contamination_warning", "deprecated"],
        },
        unit="percent",
        collector=COLLECTOR,
        sources=(ref("math"), ref("math-quality")),
    )

    for claim in (arena, quality):
        result = verify.verify(
            claim, Regions(), verify.deterministic_extractors(), today=TODAY
        )
        assert result.outcome == "verified"
        assert result.verification.target.value_hash == value_hash(claim.value)


def test_the_collector_never_verifies_its_own_value(store, regions) -> None:
    # The collector is the same agent and model family as the only extractor that accepts
    # prose: model validation refuses the pair, so nothing is verified.
    llm = _FakeLLM(json.dumps([{
        "subject": "GPT-6 Sol", "value": "400000", "unit": "tokens",
        "quoted_sentence": "It accepts up to 400,000 tokens of context.",
    }]),
                   family="grok")
    same = VerificationActor(agent="verify-llm", model_family="grok", method="anything")
    result = verify.verify(_prose_claim(store, same), regions,
                           [*verify.deterministic_extractors(), llm.extractor], today=TODAY)
    assert result.outcome == "skipped"
    assert result.reason == "no_independent_extractor"
    assert llm.calls == []


def test_same_agent_different_model_family_is_independent(store, regions) -> None:
    llm = _FakeLLM(json.dumps([{
        "subject": "GPT-6 Sol", "value": "400000", "unit": "tokens",
        "quoted_sentence": "It accepts up to 400,000 tokens of context.",
    }]))
    same_agent = VerificationActor(agent="verify-llm", model_family="grok", method="scrape")
    result = verify.verify(_prose_claim(store, same_agent), regions,
                           [*verify.deterministic_extractors(), llm.extractor], today=TODAY)
    assert result.outcome == "verified"


# --- comparison rules --------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("text", "hint", "number", "unit"),
    [
        ("71.2", "%", 71.2, "percent"),
        ("71.2%", None, 71.2, "percent"),
        ("400K tokens", None, 400, "k_tokens"),
        ("400,000 tokens", None, 400000, "tokens"),
        ("$2.50 / 1M tokens", None, 2.5, "usd_per_1m_tokens"),
        ("400K", "tokens", 400, "k_tokens"),
        ("n/a", None, None, None),
    ],
)
def test_quantities_parse_with_their_units(text, hint, number, unit) -> None:
    q = verify.parse_quantity(text, hint)
    if number is None:
        assert q is None
    else:
        assert (q.number, q.unit) == (number, unit)


@pytest.mark.parametrize(
    ("claimed", "unit", "found", "ok"),
    [
        (71.2, "percent", "71.2%", True),
        (71.24, "percent", "71.2%", True),   # the claim carries more digits than the source
        (71, "percent", "71.2%", True),      # the claim is the source rounded
        (71.3, "percent", "71.2%", False),
        (0.712, "fraction", "71.2%", True),
        (5.388066666666667, "p-MRR (x100)", "0.05388066666666667 fraction", True),
        (-2.9, "p-MRR (x100)", "-0.029 fraction", True),
        (5.388066666666667, "p-MRR (x100)", "0.5388066666666667 fraction", False),
        (400000, "tokens", "400K tokens", True),
        (401000, "tokens", "400,000 tokens", False),
    ],
)
def test_the_rounding_tolerance(claimed, unit, found, ok) -> None:
    assert verify.numbers_agree(claimed, unit, verify.parse_quantity(found)) is ok


def test_the_tolerance_rule_is_recorded() -> None:
    assert "0.5" in verify.TOLERANCE_RULE


@pytest.mark.parametrize(
    ("cell", "name", "effort"),
    [
        ("GPT-6 Sol", "gpt 6 sol", None),
        ("GPT-6 Sol (max effort)", "gpt 6 sol", "max"),
        ("GPT-6 Sol [high]", "gpt 6 sol", "high"),
        ("GPT-6 Sol (thinking)", "gpt 6 sol thinking", None),
        ("GPT-6 Astra", "gpt 6 astra", None),
    ],
)
def test_model_cells_split_into_identity_and_effort(cell, name, effort) -> None:
    assert verify.split_model_cell(cell) == (name, effort)


# --- the log -----------------------------------------------------------------------------------


def _record(target_id: str, outcome: str, day: date) -> Verification:
    return Verification(
        target=VerificationTarget(kind="fact", id=target_id, value_hash=value_hash(1)),
        collector=COLLECTOR,
        verifier=VerificationActor(agent="v", model_family="deterministic", method="m"),
        method="m",
        outcome=outcome,
        date=day,
        diff='[{"field": "value"}]' if outcome == "mismatch" else None,
    )


def test_the_log_is_append_only_and_the_latest_outcome_wins(log) -> None:
    target = TargetRef(kind="fact", id="x")
    assert log.is_quarantined(target)  # never verified
    log.append(_record("x", "verified", date(2026, 9, 1)))
    assert not log.is_quarantined(target)
    log.append(_record("x", "mismatch", date(2026, 9, 1)))  # same day, later line
    assert log.is_quarantined(target)
    log.append(_record("x", "verified", date(2026, 9, 2)))
    assert not log.is_quarantined(target)
    log.append(_record("x", "unreachable", date(2026, 8, 30)))  # an older record, appended late
    assert not log.is_quarantined(target)
    assert len(log.path.read_text().splitlines()) == 4
    assert log.path.parent.name == "verification" and log.path.suffix == ".jsonl"


def test_quarantined_values_include_values_never_verified(log) -> None:
    log.append(_record("ok", "verified", TODAY))
    log.append(_record("bad", "mismatch", TODAY))
    never = TargetRef(kind="fact", id="never")
    ids = {t.id for t in log.quarantined_values([never, TargetRef(kind="fact", id="ok")])}
    assert ids == {"never"}
    assert {t.id for t in log.quarantined_values()} == {"bad"}


def test_module_level_quarantine_helpers_read_a_directory(log) -> None:
    log.append(_record("bad", "unreachable", TODAY))
    target = TargetRef(kind="fact", id="bad")
    assert verify.is_quarantined(target, directory=log.directory)
    [quarantined] = verify.quarantined_values(directory=log.directory)
    assert quarantined == VerificationTarget(
        kind="fact", id="bad", value_hash=value_hash(1)
    )


# --- triggers: change detection re-queues, --changed-only ---------------------------------------


def test_changed_regions_are_reverified_against_the_new_copy(store, regions, log) -> None:
    _seeded_run(store, regions, log)
    queue = verify.Queue(log.directory)
    # The leaderboard changed: Sol's default score is now 65.0.
    page = (FIXTURES / "leaderboard.html").read_text().replace(
        "<td>64.0</td>", "<td>65.0</td>")
    new_ref = store.put(page.encode())
    state = SourceState("seeded-leaderboard", SourceSnapshot(
        source_id="seeded-leaderboard",
        retrieved_at=NOW,
        page_fingerprint="sha256:" + "1" * 64,
        region_fingerprints={},
        copy_ref=new_ref,
    ))
    report = RecheckReport(requeue=["evidence:sol-default", "evidence:sol-max"],
                           states={"seeded-leaderboard": state})
    queue.requeue(report, at=NOW)
    later = date(2026, 9, 25)
    result = verify.run(queue, log, regions, verify.deterministic_extractors(), today=later,
                        changed_only=True)
    assert {r.target.id: r.outcome for r in result.results} == {
        "sol-default": "mismatch", "sol-max": "verified"}
    assert log.is_quarantined(TargetRef(kind="evidence", id="sol-default"))
    assert not log.is_quarantined(TargetRef(kind="evidence", id="sol-max"))


def test_changed_only_skips_new_values(store, regions, log) -> None:
    queue = verify.Queue(log.directory)
    entry = next(e for e in SPEC["claims"] if e["id"] == "sol-default")
    queue.file(_claim(entry, store), at=NOW)
    report = verify.run(queue, log, regions, verify.deterministic_extractors(), today=TODAY,
                        changed_only=True)
    assert report.results == []
    report = verify.run(queue, log, regions, verify.deterministic_extractors(), today=TODAY)
    assert [r.outcome for r in report.results] == ["verified"]


def test_a_requeued_ref_with_no_filed_claim_is_reported(log) -> None:
    queue = verify.Queue(log.directory)
    queue.requeue(RecheckReport(requeue=["fact:nobody-filed-this"]), at=NOW)
    report = verify.run(queue, log, verify.StoredRegions(CopyStore(log.directory / "c"), {}),
                        verify.deterministic_extractors(), today=TODAY)
    assert report.results == []
    assert report.unknown == [TargetRef(kind="fact", id="nobody-filed-this")]


def test_refs_parse_as_kind_and_id() -> None:
    assert verify.target_ref("fact:openai/gpt-6#context_window") == TargetRef(
        kind="fact", id="openai/gpt-6#context_window")
    with pytest.raises(ValueError):
        verify.target_ref("openai/gpt-6")


# --- the CLI -----------------------------------------------------------------------------------


def _repo(tmp_path, store) -> Path:
    root = tmp_path / "repo"
    (root / "registry").mkdir(parents=True)
    (root / "registry" / "sources.yaml").write_text((FIXTURES / "sources.yaml").read_text())
    queue = verify.Queue(root / "verification")
    for entry in SPEC["claims"]:
        queue.file(_claim(entry, store), at=NOW)
    return root


def test_cli_verifies_what_is_queued_and_prints_a_summary(tmp_path, store, monkeypatch) -> None:
    from cli.modelspec import legacy as cli_mod

    monkeypatch.setenv("MODELSPEC_SOURCE_CACHE", str(store.root))
    root = _repo(tmp_path, store)
    result = CliRunner().invoke(cli_mod.app, ["verify", "--root", str(root)])
    assert result.exit_code == 0, result.output
    counts = {k: sum(e["expect"] == k for e in SPEC["claims"])
              for k in ("verified", "mismatch", "unreachable", "skipped")}
    for outcome, n in counts.items():
        assert f"{outcome}: {n}" in result.output
    assert "sol-max-filed-as-default" in result.output
    assert (root / "verification" / "log.jsonl").is_file()

    again = CliRunner().invoke(cli_mod.app, ["verify", "--root", str(root), "--changed-only",
                                             "--json"])
    assert again.exit_code == 0, again.output
    payload = json.loads(again.output)
    assert payload["changed_only"] is True
    assert payload["counts"] == {"verified": 0, "mismatch": 0, "unreachable": 0, "skipped": 0}


def test_cli_claude_reader_uses_an_injected_extractor(tmp_path, store, monkeypatch) -> None:
    from cli.modelspec import legacy as cli_mod

    monkeypatch.setenv("MODELSPEC_SOURCE_CACHE", str(store.root))
    root = _repo(tmp_path, store)
    fake = _FakeLLM(json.dumps([{
        "subject": "GPT-6 Sol", "value": "400,000", "unit": "tokens",
        "quoted_sentence": "It accepts up to 400,000 tokens of context.",
    }]), family="anthropic", agent="claude-cli")
    monkeypatch.setattr(verify, "claude_extractor", lambda **kwargs: fake.extractor)

    result = CliRunner().invoke(
        cli_mod.app, ["verify", "--root", str(root), "--llm-reader", "claude", "--json"]
    )

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    prose = next(row for row in payload["results"] if "sol-prose-no-extractor" in row["target"])
    assert prose["outcome"] == "verified"
    assert prose["verifier"] == {
        "agent": "claude-cli",
        "model_family": "anthropic",
        "method": "llm-extract:claude-sonnet-5",
    }
    assert any("400,000 tokens of context" in prompt for prompt in fake.calls)


def test_claude_reader_uses_the_requested_cli_and_unwraps_json(monkeypatch) -> None:
    seen = []

    def fake_run(command, **kwargs):
        seen.append((command, kwargs))
        answer = json.dumps([{
            "subject": "GPT-6 Sol", "value": "400,000", "unit": "tokens",
            "quoted_sentence": "GPT-6 Sol has 400,000 tokens of context.",
        }])
        return subprocess.CompletedProcess(command, 0, json.dumps({"result": answer}), "")

    monkeypatch.setattr(subprocess, "run", fake_run)
    complete = verify.ClaudeCLICompletion()
    assert json.loads(complete("read this"))[0]["value"] == "400,000"
    command, kwargs = seen[0]
    assert command == [
        "claude", "-p", "read this", "--model", "claude-sonnet-5", "--effort", "low",
        "--output-format", "json",
    ]
    assert kwargs["stdin"] is subprocess.DEVNULL


def test_llm_cache_key_is_copy_region_facet_and_names(tmp_path, store, regions) -> None:
    reply = json.dumps([{
        "subject": "GPT-6 Sol", "value": "400,000", "unit": "tokens",
        "quoted_sentence": "It accepts up to 400,000 tokens of context.",
    }])
    llm = _FakeLLM(reply)
    extractor = verify.LLMExtractor(
        llm,
        agent="claude-cli",
        model="claude-sonnet-5",
        model_family="anthropic",
        cache=verify.LLMCache(tmp_path / "llm-cache"),
    )
    claim = _prose_claim(store)

    first = verify.verify(claim, regions, [extractor], today=TODAY)
    second = verify.verify(claim, regions, [extractor], today=TODAY)
    other_facet = verify.Claim(**{**claim.__dict__, "field": "model.max_output_tokens"})
    verify.verify(other_facet, regions, [extractor], today=TODAY)

    assert first.outcome == second.outcome == "verified"
    assert len(llm.calls) == 2


def test_sibling_claims_on_one_region_each_get_their_own_reading(tmp_path, store, regions) -> None:
    # The prompt names the subject, and a reader answers mostly for it; a row with
    # no subject is read as the named one. A reply cached for one sibling must not
    # answer for another, or it can confirm a value the source never gave it.
    replies = iter([
        json.dumps([{"subject": None, "value": "400,000", "unit": "tokens",
                     "quoted_sentence": "It accepts up to 400,000 tokens of context."}]),
        json.dumps([]),
    ])
    seen: list[str] = []

    def complete(prompt: str) -> str:
        seen.append(prompt)
        return next(replies)

    extractor = verify.LLMExtractor(
        complete, agent="claude-cli", model="claude-sonnet-5", model_family="anthropic",
        cache=verify.LLMCache(tmp_path / "llm-cache"),
    )
    claim = _prose_claim(store)
    sibling = verify.Claim(**{**claim.__dict__, "names": ("GPT-6 Luna",),
                              "target": verify.TargetRef(kind="fact", id="luna#context")})

    assert verify.verify(claim, regions, [extractor], today=TODAY).outcome == "verified"
    assert verify.verify(sibling, regions, [extractor], today=TODAY).outcome == "mismatch"
    assert len(seen) == 2 and "GPT-6 Luna" in seen[1]


def test_claude_reader_stops_before_call_401(monkeypatch) -> None:
    monkeypatch.setattr(
        subprocess,
        "run",
        lambda command, **kwargs: subprocess.CompletedProcess(command, 0, '{"result":"[]"}', ""),
    )
    complete = verify.ClaudeCLICompletion(max_calls=1)
    assert complete("first") == "[]"
    with pytest.raises(verify.LLMCallBudgetExceededError, match="400-call budget|1-call budget"):
        complete("second")


def test_claims_build_from_model_evidence(store, regions) -> None:
    from decision.model import Evidence

    ref = store.put((FIXTURES / "leaderboard.html").read_bytes())
    evidence = Evidence(
        id="sol-default-from-model", subject={"kind": "model", "id": "openai/gpt-6-sol"},
        benchmark_id="seeded-coding", model_id_as_evaluated="GPT-6 Sol", score=64.0,
        unit="percent", source_url="https://leaderboard.example.test/coding",
        source_kind="independent_evaluator", evidence_date="2026-08-14",
        date_type="evaluated", verified_at="2026-08-20", effort="default",
        sources=[{"source_id": "seeded-leaderboard", "snapshot_ref": ref,
                  "cited_regions": ["results"]}],
    )
    claim = verify.Claim.from_evidence(evidence, names=["GPT-6 Sol"], collector=COLLECTOR,
                                       label="Score")
    # The harness is not on the evidence, so the source's harness column is a mismatch:
    # the claim dropped a qualifier the source attaches to the value.
    result = verify.verify(claim, regions, verify.deterministic_extractors(), today=TODAY)
    assert [d.field for d in result.diffs] == ["harness"]


def test_claim_from_evidence_binds_decision_affecting_metadata() -> None:
    from decision.model import Evidence

    evidence = Evidence(
        id="alpha-composite",
        subject={"kind": "model", "id": "lab/alpha"},
        benchmark_id="seeded-coding",
        model_id_as_evaluated="Alpha",
        score=55.0,
        interval=[51.0, 59.0],
        n=500,
        quality_flags=["deprecated"],
        unit="percent",
        source_url="https://leaderboard.example.test/coding",
        source_kind="independent_evaluator",
        evidence_date="2026-08-14",
        date_type="evaluated",
        verified_at="2026-08-20",
        sources=[{
            "source_id": "seeded-leaderboard",
            "snapshot_ref": "sha256:" + "0" * 64,
            "cited_regions": ["results"],
        }],
    )

    claim = verify.Claim.from_evidence(
        evidence,
        names=["Alpha"],
        collector=COLLECTOR,
    )

    assert claim.value == {
        "score": 55.0,
        "interval": [51.0, 59.0],
        "n": 500,
        "quality_flags": ["deprecated"],
    }
    assert value_hash(claim.value) == (
        "sha256:671b0003430ee71833ba940afc9cf532504e4743f68e90afbbcc8977d81bbd9f"
    )


def _harness_reading(harness: str | None) -> _FakeLLM:
    return _FakeLLM(json.dumps([{
        "subject": "GPT-6 Sol", "value": "400,000", "unit": "tokens", "harness": harness,
        "quoted_sentence": "It accepts up to 400,000 tokens of context.",
    }]))


@pytest.mark.parametrize(("found", "outcome"), [
    ("Claude Code in --bare mode", "verified"),  # named, but no registered version
    ("claude-code@2.1.282", "mismatch"),  # a registered harness is not `unregistered`
    (None, "mismatch"),  # the source names no harness at all
])
def test_an_unregistered_harness_claim_matches_a_named_unregistered_harness(
        store, regions, found, outcome) -> None:
    claim = _prose_claim(store)
    claim = verify.Claim(**{**claim.__dict__, "conditions": {"harness": "unregistered"}})
    result = verify.verify(claim, regions, [_harness_reading(found).extractor], today=TODAY)
    assert result.outcome == outcome
    if outcome == "mismatch":
        assert [d.field for d in result.diffs] == ["harness"]


@pytest.mark.parametrize(("found", "outcome"), [
    ("maximum thinking effort", "verified"),
    ("max reasoning effort", "verified"),
    ("high thinking effort", "mismatch"),
    # Mistral's reading of the Opus 5.5 system card caption (MODEL-233).
    ("adaptive thinking at max effort", "verified"),
    ("max effort, xhigh effort for one benchmark", "mismatch"),
    ("no max effort", "mismatch"),
    ("without max reasoning effort", "mismatch"),
    ("without adaptive thinking at max effort", "mismatch"),
    ("low effort rather than max effort", "mismatch"),
])
def test_an_effort_written_as_prose_is_read_as_its_level(store, found, outcome) -> None:
    claim = _prose_claim(store)
    claim = verify.Claim(**{**claim.__dict__, "conditions": {"effort": "max"}})
    sentence = f"At {found}, it accepts up to 400,000 tokens of context."
    reading = _FakeLLM(json.dumps([{
        "subject": "GPT-6 Sol", "value": "400,000", "unit": "tokens", "effort": found,
        "quoted_sentence": sentence,
    }]))
    regions = _InlineRegions(f"GPT-6 Sol is our most capable model. {sentence}")
    assert verify.verify(claim, regions, [reading.extractor], today=TODAY).outcome == outcome


# --- MODEL-201: plan facts (surfaces, families, quotes, allowance, CNY price) ----

CLAUDE_MODELS_TABLE = """Models and usage
Features | Free | Pro | Max 5x | Max 20x
Fable | No | Usage credits | 50% of weekly limits* | 50% of weekly limits*
Opus | No | Yes | Yes | Yes
Sonnet | Yes | Yes | Yes | Yes
Haiku | Yes | Yes | Yes | Yes
Context window | Up to 1M | Up to 1M | Up to 1M | Up to 1M
"""
CLAUDE_CODE_ARTICLE = """Use Claude Code with your Pro or Max plan
With Pro and Max plans, you now have access to both Claude on the web, desktop, and mobile apps and Claude Code in your terminal with one unified subscription.
Your Pro or Max plan also covers Claude Code in supported IDEs, including VS Code, Cursor and other VS Code forks.
"""
MAX_ARTICLE = """What is the Max plan?
Max 5x includes five times the Pro plan's per-session usage allowance. This tier is ideal for frequent users.
Max 20x includes 20 times the Pro plan's per-session usage allowance.
Your session-based usage limit will reset every five hours.
"""
PRO_TIERS = """General FAQ
Both Pro tiers include the same core capabilities. The main difference is usage allowance: Pro $100 unlocks 5x higher usage than Plus, while Pro $200 unlocks 20x usage than Plus.
"""
KIMI_PAGE = """Plan | Best for | Auto-renewing monthly | Auto-renewing annual
Andante | Everyday use | ¥49/month | Better value annually
Moderato | Productivity upgrade | ¥99/month | Better value annually
Plan Benefits
Andante — ¥49/month
About 30 Agent uses
Kimi Code available
Moderato — ¥99/month
Everything in Andante, plus:
About 60 Agent uses
Kimi Code available
Kimi Code also has a separate limit of 5 hours per week, which applies only to Kimi Code.
"""


def _plan_claim(field, value, names, subject="provider/subscription/plan"):
    return verify.Claim(
        target=verify.TargetRef(kind="fact", id=f"{subject}#{field}"),
        subject=subject,
        names=names,
        field=field,
        value=value,
        collector=COLLECTOR,
        sources=(verify.SourceRef(
            source_id="subscription-page",
            snapshot_ref="sha256:" + "0" * 64,
            cited_regions=["page"],
        ),),
    )


@pytest.mark.parametrize(
    ("field", "value", "names", "subject", "page"),
    [
        ("offering.subscription.families_covered",
         ["anthropic/claude-opus", "anthropic/claude-sonnet", "anthropic/claude-haiku"],
         ("Claude Pro", "Pro"), "anthropic/subscription/pro", CLAUDE_MODELS_TABLE),
        ("offering.subscription.families_covered",
         ["anthropic/claude-fable", "anthropic/claude-opus", "anthropic/claude-sonnet",
          "anthropic/claude-haiku"],
         ("Claude Max 5x", "Max 5x"), "anthropic/subscription/max-5x", CLAUDE_MODELS_TABLE),
        ("offering.subscription.coverage_quote",
         "Opus | No | Yes | Yes | Yes\nSonnet | Yes | Yes | Yes | Yes",
         ("Claude Pro", "Pro"), "anthropic/subscription/pro", CLAUDE_MODELS_TABLE),
        ("offering.subscription.surfaces",
         ["chat_app", "coding_tool:claude-code", "desktop_app", "mobile_app"],
         ("Claude Pro", "Pro"), "anthropic/subscription/pro", CLAUDE_CODE_ARTICLE),
        ("offering.subscription.allowance.multiplier", 20,
         ("Claude Max 20x", "Max 20x", "Max plan"), "anthropic/subscription/max-20x", MAX_ARTICLE),
        ("offering.subscription.allowance.relative_to", "anthropic/subscription/pro",
         ("Claude Max 5x", "Max 5x", "Max plan"), "anthropic/subscription/max-5x", MAX_ARTICLE),
        ("offering.subscription.allowance.window", "five hours",
         ("Claude Max 5x", "Max 5x", "Max plan"), "anthropic/subscription/max-5x", MAX_ARTICLE),
        ("offering.subscription.allowance.multiplier", 20,
         ("ChatGPT Pro 20x", "Pro $200", "Pro"), "openai/subscription/pro-20x", PRO_TIERS),
        ("offering.subscription.allowance.relative_to", "openai/subscription/plus",
         ("ChatGPT Pro 5x", "Pro $100", "Pro"), "openai/subscription/pro-5x", PRO_TIERS),
        ("offering.subscription.allowance.multiplier", 20,
         ("Google AI Ultra 20x", "Ultra 20x"), "google-gemini-api/subscription/ai-ultra-20x",
         GEMINI_TIERS),
        ("offering.subscription.allowance.relative_to", "google-gemini-api/subscription/ai-pro",
         ("Google AI Ultra 5x", "Ultra 5x"), "google-gemini-api/subscription/ai-ultra-5x",
         GEMINI_TIERS),
        ("offering.subscription.allowance.window", "five hours", ("Lite",),
         "zai/subscription/glm-coding-lite",
         "Each plan is subject to both a 5-hour usage limit and a weekly usage limit.\n"),
        ("offering.subscription.allowance.window", "five hours", ("Max",),
         "minimax/subscription/token-max",
         "| Plus | Max\nQuota windows | 5-hour rolling and weekly windows | 5-hour rolling and weekly windows\n"),
        ("offering.subscription.price_cny", 99, ("Moderato",), "moonshot/subscription/moderato",
         KIMI_PAGE),
        ("offering.subscription.billing_period", "monthly", ("Moderato",),
         "moonshot/subscription/moderato", KIMI_PAGE),
        ("offering.subscription.usage_allowance", "About 60 Agent uses", ("Moderato",),
         "moonshot/subscription/moderato", KIMI_PAGE),
        ("offering.subscription.programmatic_or_agent_use", "Kimi Code available",
         ("Moderato",), "moonshot/subscription/moderato", KIMI_PAGE),
        ("offering.subscription.usage_allowance", "More messages and web searches.", ("Pro",),
         "mistral/subscription/pro",
         MISTRAL_CARD + "More access and usage.\nMore messages and web searches.\nTeam\nSecure.\n$24.99\n"),
    ],
)
def test_plan_facts_are_read_from_plan_scoped_text(field, value, names, subject, page) -> None:
    claim = _plan_claim(field, value, names, subject)

    readings = verify.SubscriptionPageExtractor().extract(claim, page)

    assert verify.compare(claim, readings) == []


@pytest.mark.parametrize(
    ("field", "value", "names", "subject", "page"),
    [
        # Pro's Fable cell is "Usage credits": paid per use, not covered.
        ("offering.subscription.families_covered",
         ["anthropic/claude-fable", "anthropic/claude-opus", "anthropic/claude-sonnet",
          "anthropic/claude-haiku"],
         ("Claude Pro", "Pro"), "anthropic/subscription/pro", CLAUDE_MODELS_TABLE),
        # The sibling tier's multiplier, and a plan named in its own alias.
        ("offering.subscription.allowance.multiplier", 20,
         ("ChatGPT Pro 5x", "Pro $100", "Pro"), "openai/subscription/pro-5x", PRO_TIERS),
        ("offering.subscription.allowance.multiplier", 5,
         ("Claude Max 20x", "Max 20x", "Max plan"), "anthropic/subscription/max-20x", MAX_ARTICLE),
        # "no 5-hour usage limit" and "5 hours per week" are not a five-hour window.
        ("offering.subscription.allowance.window", "five hours", ("Premium seat", "Premium"),
         "openai/subscription/business-premium",
         "Premium includes 5x more usage than Standard seats, no 5-hour usage limit.\n"),
        ("offering.subscription.allowance.window", "five hours", ("Moderato",),
         "moonshot/subscription/moderato", KIMI_PAGE),
        # A yuan amount is not a dollar price.
        ("offering.subscription.price", 99, ("Moderato",), "moonshot/subscription/moderato",
         KIMI_PAGE),
        # A quote that is not on the page.
        ("offering.subscription.coverage_quote", "Opus | Yes | Yes | Yes | Yes",
         ("Claude Pro", "Pro"), "anthropic/subscription/pro", CLAUDE_MODELS_TABLE),
        # The IDE sentence names Cursor, but not the web, desktop or mobile apps.
        ("offering.subscription.surfaces", ["coding_tool:claude-code"],
         ("Claude Pro", "Pro"), "anthropic/subscription/pro",
         "Your Pro or Max plan also covers Claude Code in supported IDEs.\n"
         "With Pro and Max plans you get Claude on the web.\n"),
    ],
)
def test_plan_facts_reject_what_the_page_does_not_say(field, value, names, subject, page) -> None:
    claim = _plan_claim(field, value, names, subject)

    readings = verify.SubscriptionPageExtractor().extract(claim, page)

    assert verify.compare(claim, readings) != []


# Counterexamples from MODEL-201's independent review, on real page wording.
TEAM_ARTICLE = """What is the Team plan?
Standard seats: Team plan Standard seats include 1.25x the Pro plan's per-session usage allowance and have a weekly usage limit that applies across all models.
Premium seats: Team plan Premium seats include 6.25x the Pro plan's per-session usage allowance and have a weekly usage limit that applies across all models.
"""
BUSINESS_INTRO = """ChatGPT Business - Overview
Introducing Premium seats for ChatGPT Business. Premium seats cost $100 per user per month when billed annually, or $125 per user per month when billed monthly. Premium includes 5x more usage than Standard seats, no 5-hour usage limit.
"""
ENTERPRISE_ARTICLE = """What is the Enterprise plan?
Enterprise uses a single seat type, priced per user per month and billed annually.
Usage billing | Credits purchased upfront | Billed monthly in arrears
"""
XAI_CARD = """SuperGrok Plus
$100/month
Go further with significantly higher usage.
Everything in SuperGrok, plus:
Early access to new features
Compare features across plans
Free
SuperGrok Heavy
Grok Build
Grok Bot
"""


@pytest.mark.parametrize(
    ("field", "value", "names", "subject", "page"),
    [
        ("offering.subscription.allowance.multiplier", 20,
         ("Claude Max 5x", "Max 5x", "Max plan"), "anthropic/subscription/max-5x",
         MAX_ARTICLE + "We do not offer standard discounted pricing any of our paid plans, "
         "including Max 5x and 20x plans.\n"),
        ("offering.subscription.allowance.multiplier", 20,
         ("ChatGPT Pro 5x", "Pro $100", "Pro"), "openai/subscription/pro-5x",
         "We're temporarily pausing new sign-ups and upgrades to the ChatGPT Pro $200 plan (Pro 20X).\n"),
        ("offering.subscription.allowance.multiplier", 6.25,
         ("Claude Team (Standard seat)", "Standard seats", "Team plan", "Team"),
         "anthropic/subscription/team-standard", TEAM_ARTICLE),
        ("offering.subscription.allowance.multiplier", 1.25,
         ("Claude Team (Premium seat)", "Premium seats", "Team plan", "Team"),
         "anthropic/subscription/team-premium", TEAM_ARTICLE),
        ("offering.subscription.billing_period", "monthly",
         ("Claude Enterprise", "Enterprise plan"), "anthropic/subscription/enterprise",
         ENTERPRISE_ARTICLE),
        ("offering.subscription.billing_period", "annual", ("Moderato",),
         "moonshot/subscription/moderato", KIMI_PAGE),
        ("offering.subscription.billing_period", "annual", ("Standard seats",),
         "anthropic/subscription/team-standard", TEAM_CARD),
        ("offering.subscription.price", 100, ("ChatGPT Business (Standard seat)", "Standard seat"),
         "openai/subscription/business-standard", BUSINESS_INTRO),
        ("offering.subscription.price", 99.99, ("Google AI Pro", "AI Pro"),
         "google-gemini-api/subscription/ai-pro", GEMINI_TIERS),
        ("offering.subscription.price", 20, ("Google AI Pro", "AI Pro"),
         "google-gemini-api/subscription/ai-pro", "Google AI Pro\n$19.99/ month\n"),
        ("offering.subscription.programmatic_or_agent_use", "Grok Build",
         ("SuperGrok Plus",), "xai/subscription/supergrok-plus", XAI_CARD),
    ],
)
def test_review_counterexamples_do_not_verify(field, value, names, subject, page) -> None:
    claim = _plan_claim(field, value, names, subject)

    readings = verify.SubscriptionPageExtractor().extract(claim, page)

    assert verify.compare(claim, readings) != []


@pytest.mark.parametrize(
    ("field", "value", "names", "subject", "page"),
    [
        ("offering.subscription.allowance.multiplier", 1.25,
         ("Claude Team (Standard seat)", "Standard seats", "Team plan", "Team"),
         "anthropic/subscription/team-standard", TEAM_ARTICLE),
        ("offering.subscription.billing_period", "annual",
         ("Claude Enterprise", "Enterprise plan"), "anthropic/subscription/enterprise",
         ENTERPRISE_ARTICLE),
        ("offering.subscription.billing_period", "monthly", ("Moderato",),
         "moonshot/subscription/moderato", KIMI_PAGE),
        ("offering.subscription.surfaces",
         ["chat_app", "coding_tool:claude-code", "desktop_app", "mobile_app"],
         ("Claude Max 5x", "Max 5x", "Max plan"), "anthropic/subscription/max-5x",
         CLAUDE_CODE_ARTICLE),
    ],
)
def test_review_fixes_keep_the_true_value(field, value, names, subject, page) -> None:
    claim = _plan_claim(field, value, names, subject)

    readings = verify.SubscriptionPageExtractor().extract(claim, page)

    assert verify.compare(claim, readings) == []


def test_a_subscription_price_must_match_exactly() -> None:
    claim = _plan_claim("offering.subscription.price", 20, ("Google AI Pro",))
    assert verify.compare(claim, [verify.Reading("Google AI Pro", "$19.99/ month")]) != []


def test_unknown_model_names_are_dropped_only_for_models_covered() -> None:
    claim = verify.Claim(
        target=verify.TargetRef(kind="fact", id="m#base"), subject="lab/m",
        names=("M",), field="origin.base_models", value=["openai/gpt-6-sol"],
        collector=COLLECTOR,
        sources=(verify.SourceRef(source_id="s", snapshot_ref="sha256:" + "0" * 64,
                                  cited_regions=["page"]),),
    )
    assert verify.compare(claim, [verify.Reading("M", "GPT-6 Sol, Not A Catalogued Model")]) != []


# ── MODEL-205: the subscription-only vendors' plan pages ──────────────────

VENDOR_POOLS = """Models & Pricing
Cursor supports frontier models from OpenAI and more. Pro, Pro Plus, and Ultra include two usage pools so you can pick.
There are two separate usage pools, each resetting with your monthly billing cycle:
Cursor Models
The Cursor Models pool includes Grok 4.7, Grok 4.6, and Composer 2.5.
Name | | | |
Grok 4.7 (Fast) | $ 4 | - | $ 1 | $ 12
Other Models
When you select a specific third-party model, usage is drawn from the Other Models pool.
Name | | | |
Claude Opus 5.5 | $ 4 | $ 5 | $ 0.2 | $ 20
Gemini 3.1 Pro | $ 2 | - | $ 0.2 | $ 12
Plans
Pro, Pro Plus, and Ultra include unlimited tab completions and access to Cloud Agents. Start covers the Cursor Models pool.
Plan | Price | Cursor Models | Other Models
Start (India only) | ₹649/mo | Included | Not included
Pro | $20/mo | Included | Included
"""
POOL_MODELS = ["anthropic/claude-opus-5-5", "xai/grok-4-6", "xai/grok-4-7"]


@pytest.mark.parametrize(("field", "value", "names"), [
    ("offering.subscription.models_covered", POOL_MODELS, ("Cursor Pro", "Pro")),
    ("offering.subscription.usage_allowance",
     "There are two separate usage pools, each resetting with your monthly billing cycle",
     ("Cursor Pro", "Pro")),
    ("offering.subscription.programmatic_or_agent_use",
     "Pro, Pro Plus, and Ultra include unlimited tab completions and access to Cloud Agents.",
     ("Cursor Ultra", "Ultra")),
    ("offering.subscription.surfaces", ["coding_tool:cursor"], ("Cursor Pro", "Pro")),
])
def test_subscription_page_reads_a_vendors_pools_and_plan_list(field, value, names) -> None:
    claim = _plan_claim(field, value, names, subject="cursor/subscription/pro")

    readings = verify.SubscriptionPageExtractor().extract(claim, VENDOR_POOLS)

    assert verify.compare(claim, readings) == []


@pytest.mark.parametrize(("field", "value", "names"), [
    # Start's "Other Models" cell is "Not included".
    ("offering.subscription.models_covered", POOL_MODELS, ("Cursor Start", "Start")),
    # A pool model missing from the claim.
    ("offering.subscription.models_covered", POOL_MODELS[1:], ("Cursor Pro", "Pro")),
    # "Cursor Models" names a pool, not the editor; the Plans paragraph says nothing
    # about where Ultra works, and Start is in no plan list.
    ("offering.subscription.surfaces", ["coding_tool:cursor"], ("Cursor Start", "Start")),
])
def test_subscription_page_vendor_layouts_reject_a_sibling_or_a_wrong_set(
        field, value, names) -> None:
    claim = _plan_claim(field, value, names, subject="cursor/subscription/start")

    readings = verify.SubscriptionPageExtractor().extract(claim, VENDOR_POOLS)

    assert verify.compare(claim, readings) != []


COPILOT_PLANS = """GitHub Copilot plans
Copilot plans overview
The table below provides an overview of differences between plans. All plans include Copilot CLI and Copilot app.
Plan | Price per month | Base credits | Flex allotment | Total monthly AI credits
Copilot Pro | $10 USD | 1,000 | 500 | 1,500
Copilot Pro+ | $39 USD | 3,900 | 3,100 | 7,000
Models
Available models | Copilot Pro | Copilot Pro+
Claude Haiku 4.5 | Included | Included
Claude Opus 5.5 | Not included | Included
GPT-6 Sol | Not included | Included
"""


@pytest.mark.parametrize(("field", "value", "names"), [
    ("offering.subscription.models_covered", ["anthropic/claude-haiku-4-5-20251001"],
     ("GitHub Copilot Pro", "Copilot Pro")),
    ("offering.subscription.models_covered",
     ["anthropic/claude-haiku-4-5-20251001", "anthropic/claude-opus-5-5", "openai/gpt-6-sol"],
     ("GitHub Copilot Pro+", "Copilot Pro+")),
    ("offering.subscription.usage_allowance", "Total monthly AI credits: 1,500",
     ("GitHub Copilot Pro", "Copilot Pro")),
    ("offering.subscription.billing_period", "monthly", ("GitHub Copilot Pro", "Copilot Pro")),
    ("offering.subscription.programmatic_or_agent_use",
     "All plans include Copilot CLI and Copilot app.", ("GitHub Copilot Pro", "Copilot Pro")),
    ("offering.subscription.surfaces", ["coding_tool:copilot-cli"],
     ("GitHub Copilot Pro", "Copilot Pro")),
])
def test_subscription_page_reads_an_icon_column_and_a_plan_row(field, value, names) -> None:
    claim = _plan_claim(field, value, names, subject="github-copilot/subscription/pro")

    readings = verify.SubscriptionPageExtractor().extract(claim, COPILOT_PLANS)

    assert verify.compare(claim, readings) == []


@pytest.mark.parametrize(("field", "value"), [
    # Pro+'s models and credits never confirm Pro: "Copilot Pro+" is not "Copilot Pro".
    ("offering.subscription.models_covered",
     ["anthropic/claude-haiku-4-5-20251001", "anthropic/claude-opus-5-5", "openai/gpt-6-sol"]),
    ("offering.subscription.usage_allowance", "Total monthly AI credits: 7,000"),
])
def test_subscription_page_icon_column_rejects_a_siblings_values(field, value) -> None:
    claim = _plan_claim(field, value, ("GitHub Copilot Pro", "Copilot Pro"),
                        subject="github-copilot/subscription/pro")

    readings = verify.SubscriptionPageExtractor().extract(claim, COPILOT_PLANS)

    assert verify.compare(claim, readings) != []


PLAN_CARDS = """Choose your plan
Advanced answers and top AI models
$17
/month when billed annually
Expanded Computer access
4,000 bonus credits
Get Pro
Unlimited usage and top performance
$167
/month when billed annually
10,000 monthly credits
Get Max
What models do I get access to?
Pro includes GPT-5.6 Terra, Claude Sonnet 5, Grok 4.1, and Perplexity's in-house Sonar 2 model.
"""


def test_subscription_page_reads_a_card_ending_in_get_plan_and_a_plan_includes_sentence():
    pro = ("Perplexity Pro", "Pro")
    allowance = _plan_claim("offering.subscription.usage_allowance", "4,000 bonus credits", pro)
    sibling = _plan_claim("offering.subscription.usage_allowance", "10,000 monthly credits", pro)
    models = _plan_claim("offering.subscription.models_covered",
                         ["anthropic/claude-sonnet-5", "openai/gpt-5-6-terra"], pro)
    extractor = verify.SubscriptionPageExtractor()

    assert verify.compare(allowance, extractor.extract(allowance, PLAN_CARDS)) == []
    assert verify.compare(sibling, extractor.extract(sibling, PLAN_CARDS)) != []
    assert verify.compare(models, extractor.extract(models, PLAN_CARDS)) == []


def test_a_card_without_its_own_price_never_borrows_the_card_before_it() -> None:
    page = PLAN_CARDS.replace("What models do I get access to?",
                              "For your organisation\nContact us for pricing\nGet Team\n"
                              "What models do I get access to?")
    claim = _plan_claim("offering.subscription.usage_allowance", "10,000 monthly credits",
                        ("Perplexity Team", "Team"))

    readings = verify.SubscriptionPageExtractor().extract(claim, page)

    assert verify.compare(claim, readings) != []


def test_a_name_on_two_cards_is_the_card_so_named_and_a_literal_id_is_that_id() -> None:
    # "Claude Haiku 4.5" is the dated card's display name and the alias card's ID stem.
    assert verify._catalogue_model_matches("Claude Haiku 4.5") == {
        "anthropic/claude-haiku-4-5-20251001"}
    assert verify._catalogue_model_matches("claude-haiku-4-5") == {"anthropic/claude-haiku-4-5"}


@pytest.mark.parametrize(("claimed", "published", "agrees"), [
    (0.2, "$0.20 / MTok", True), (0.2, "$0.25 / MTok", False),
    (2.0, "$2 / MTok", True), (2.0, "$2.50 / MTok", False), (0.075, "$0.075", True),
])
def test_a_pay_per_use_list_price_is_exact(claimed: float, published: str, agrees: bool) -> None:
    """MODEL-235: the rounding tolerance let 0.2 agree with $0.25, so the weekly
    re-read would have missed that price change."""
    claim = _price_claim("cached_input", claimed, name="Claude Opus 5")
    reading = verify.Reading("Claude Opus 5", published, "usd_per_1m_tokens")
    assert (verify.compare(claim, [reading]) == []) is agrees


def test_model_price_page_reads_amount_after_tokens_category():
    text = 'Example Model\nPricing\nInput\nTokens\n$4.00/ 1M tokens\nOutput\nTokens\n$12.00/ 1M tokens\n'
    for field, amount in [('input', 4), ('output', 12)]:
        claim = _price_claim(field, amount, name='Example Model')
        readings = verify.ModelPageExtractor().extract(claim, text)
        assert verify.compare(claim, readings) == []


def test_model_price_page_without_numeric_amount_has_no_price_reading():
    claim = _price_claim('input', 4, name='Example Model')
    readings = verify.ModelPageExtractor().extract(claim, 'Example Model\nInput\nTokens\nOutput\nTokens\n')
    assert not any(reading.value is not None for reading in readings)


def test_transposed_benchmark_table_converts_percent_to_fraction_and_selects_exact_column(store):
    claim = verify.Claim(target=TargetRef(kind='evidence', id='fixture-score'),
                         subject='lab/model', names=('Example Model',), field='fixture',
                         label='8 needle average', value=.42, unit='fraction',
                         collector=COLLECTOR, sources=(SourceRef(source_id='fixture',
                             snapshot_ref='sha256:' + '0' * 64, cited_regions=['rows']),))
    text = '| Example Model | Example Model Small\n8 needle average | 42% | 24%\n4 needle average | 84% | 48%\n'
    extractor = verify.TransposedTableExtractor()
    assert verify.compare(claim, extractor.extract(claim, text)) == []
    from dataclasses import replace
    assert verify.compare(replace(claim, value=.24), extractor.extract(claim, text))


# --- licence terms (MODEL-345) -----------------------------------------------------------------


MIT_TEXT = """\
MIT License

Copyright (c) 2023 DeepSeek

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
MIT_QUOTE = (
    "Permission is hereby granted, free of charge, to any person obtaining a copy"
)
CAP_TEXT = """\
Fabricated weights licence.

Use of the weights is permitted.
If the licensee serves more than 100 million monthly active users, a separate agreement is required.
Redistribution of the weights is permitted.
"""
CAP_QUOTE = (
    "If the licensee serves more than 100 million monthly active users, "
    "a separate agreement is required."
)
_LICENCE = SourceRef(source_id="nimbus-licence", snapshot_ref="sha256:" + "a" * 64,
                     cited_regions=["page"])
_README = SourceRef(source_id="nimbus-readme", snapshot_ref="sha256:" + "b" * 64,
                    cited_regions=["page"])


class _KindRegions:
    """Per-region text, plus the source kind and URL a licence binding needs."""

    def __init__(self, texts: dict[tuple[str, str], str], kinds: dict[str, str | None],
                 urls: dict[str, str] | None = None) -> None:
        self.texts = texts
        self.kinds = kinds
        self.urls = urls or {}

    def text(self, source_id: str, copy_ref: str, region_id: str) -> str | None:
        return self.texts.get((source_id, region_id))

    def source_kind(self, source_id: str) -> str | None:
        return self.kinds.get(source_id)

    def source_url(self, source_id: str) -> str | None:
        return self.urls.get(source_id)


def _licence_reader(complete, *, family: str = "anthropic") -> verify.LicenceExtractor:
    return verify.LicenceExtractor(
        complete, agent="claude-cli", model="claude-sonnet-5", model_family=family,
    )


def _licence_claim(field: str, value, sources, *, unit: str | None = None,
                   label: str | None = None) -> verify.Claim:
    return verify.Claim(
        target=TargetRef(kind="fact", id=f"lab/nimbus-3#{field}"),
        subject="lab/nimbus-3",
        names=("Nimbus 3",),
        field=field,
        label=label,
        value=value,
        unit=unit,
        collector=COLLECTOR,
        sources=sources,
    )


def _reply(value, clauses) -> str:
    return json.dumps({"value": value, "clauses": clauses})


def test_mit_text_verifies_permitted_on_all_four_licence_facets() -> None:
    readme = "---\nlicense: mit\n---\nNimbus 3\n"
    regions = _KindRegions(
        {("nimbus-licence", "page"): MIT_TEXT, ("nimbus-readme", "page"): readme},
        {"nimbus-licence": "licence_text", "nimbus-readme": "weights_repository"},
        {"nimbus-licence": "https://example.test/LICENSE"},
    )
    calls: list[str] = []

    def complete(prompt: str) -> str:
        calls.append(prompt)
        facet = re.search(r"Facet: (\S+)", prompt).group(1)
        value = "unbounded" if facet == "licence.user_cap" else "permitted"
        return _reply(value, [MIT_QUOTE])

    reader = _licence_reader(complete)
    expected = {
        "licence.commercial_use": "permitted",
        "licence.user_cap": "unbounded",
        "licence.output_training": "permitted",
        "licence.fine_tuning": "permitted",
    }
    for field, value in expected.items():
        unit = "monthly_active_users" if field == "licence.user_cap" else None
        claim = _licence_claim(field, value, (_LICENCE, _README), unit=unit)
        result = verify.verify(claim, regions, [reader], today=TODAY)
        assert result.outcome == "verified", (field, result)
    cap_prompt = next(prompt for prompt in calls if "licence.user_cap" in prompt)
    assert "unbounded" in cap_prompt
    assert "no such cap" in cap_prompt
    assert "Nimbus 3" not in cap_prompt


def test_a_mau_cap_is_read_as_the_number_and_the_claim_is_not_in_the_prompt() -> None:
    readme = "license: other\nNimbus 3\nhttps://example.test/CAP\n"
    regions = _KindRegions(
        {("nimbus-licence", "page"): CAP_TEXT, ("nimbus-readme", "page"): readme},
        {"nimbus-licence": "licence_text"},
        {"nimbus-licence": "https://example.test/CAP"},
    )
    calls: list[str] = []

    def complete(prompt: str) -> str:
        calls.append(prompt)
        return _reply(100000000, [CAP_QUOTE])

    claim = _licence_claim("licence.user_cap", 100_000_000, (_LICENCE, _README),
                           unit="monthly_active_users")
    result = verify.verify(claim, regions, [_licence_reader(complete)], today=TODAY)
    assert result.outcome == "verified", result
    assert "100000000" not in calls[0]
    assert "unbounded" in calls[0]


def test_a_non_verbatim_licence_quote_is_not_evidence() -> None:
    regions = _KindRegions(
        {("nimbus-licence", "page"): MIT_TEXT, ("nimbus-readme", "page"): "license: mit\nNimbus 3\n"},
        {"nimbus-licence": "licence_text"},
        {"nimbus-licence": "https://example.test/LICENSE"},
    )
    reader = _licence_reader(lambda prompt: _reply("permitted", ["this sentence is not in the licence"]))
    claim = _licence_claim("licence.commercial_use", "permitted", (_LICENCE, _README))
    result = verify.verify(claim, regions, [reader], today=TODAY)
    assert result.outcome == "skipped"
    assert result.verification is None
    assert "extractor_error" in result.reason


def test_not_disclosed_on_a_readme_is_not_verified() -> None:
    regions = _KindRegions(
        {("nimbus-readme", "page"): "Model: Nimbus 3\nLicense: mit\n"},
        {"nimbus-readme": "weights_repository"},
    )
    claim = _licence_claim("licence.commercial_use", None, (_README,))
    result = verify.verify(claim, regions, verify.deterministic_extractors(), today=TODAY)
    assert result.outcome == "mismatch"
    assert [d.field for d in result.diffs] == ["source_kind"]
    assert result.diffs[0].found == "weights_repository"


def test_not_disclosed_on_a_kindless_licence_source_is_not_verified() -> None:
    regions = _KindRegions(
        {("nimbus-readme", "page"): "Model: Nimbus 3\nLicense: mit\n"},
        {"nimbus-readme": None},
    )
    claim = _licence_claim("licence.commercial_use", None, (_README,))
    result = verify.verify(claim, regions, verify.deterministic_extractors(), today=TODAY)
    assert result.outcome == "mismatch"
    assert result.diffs[0].found == "unknown"


def test_silence_on_output_training_verifies_not_disclosed() -> None:
    readme = "license: mit\nNimbus 3\n"
    regions = _KindRegions(
        {("nimbus-licence", "page"): MIT_TEXT, ("nimbus-readme", "page"): readme},
        {"nimbus-licence": "licence_text"},
        {"nimbus-licence": "https://example.test/LICENSE"},
    )
    reader = _licence_reader(lambda prompt: _reply("not_disclosed", [MIT_QUOTE]))
    claim = _licence_claim("licence.output_training", None, (_LICENCE, _README))
    result = verify.verify(claim, regions, [reader], today=TODAY)
    assert result.outcome == "verified", result


def test_a_licence_cited_without_a_binding_page_does_not_verify() -> None:
    regions = _KindRegions(
        {("nimbus-licence", "page"): MIT_TEXT},
        {"nimbus-licence": "licence_text"},
        {"nimbus-licence": "https://example.test/LICENSE"},
    )
    reader = _licence_reader(lambda prompt: _reply("permitted", [MIT_QUOTE]))
    claim = _licence_claim("licence.commercial_use", "permitted", (_LICENCE,))
    result = verify.verify(claim, regions, [reader], today=TODAY)
    assert result.outcome == "mismatch"
    assert result.diffs[0].field == "model"

    cited = _licence_claim("licence.commercial_use", "permitted", (_LICENCE, _README))
    named_only = "Nimbus 3 weights are in this repository.\n"
    unbound = _KindRegions(
        {("nimbus-licence", "page"): MIT_TEXT, ("nimbus-readme", "page"): named_only},
        {"nimbus-licence": "licence_text"},
        {"nimbus-licence": "https://example.test/LICENSE"},
    )
    result = verify.verify(cited, unbound, [reader], today=TODAY)
    assert result.outcome == "mismatch"
    assert result.diffs[0].field == "model"

    linked = "Nimbus 3\nhttps://example.test/LICENSE\n"
    bound = _KindRegions(
        {("nimbus-licence", "page"): MIT_TEXT, ("nimbus-readme", "page"): linked},
        {"nimbus-licence": "licence_text"},
        {"nimbus-licence": "https://example.test/LICENSE"},
    )
    result = verify.verify(cited, bound, [reader], today=TODAY)
    assert result.outcome == "verified", result


def test_deterministic_extractors_do_not_claim_a_licence_region() -> None:
    text = "Model: Nimbus 3\nCommercial use: permitted\n"
    regions = _KindRegions(
        {("nimbus-licence", "page"): text, ("nimbus-readme", "page"): "license: mit\nNimbus 3\n"},
        {"nimbus-licence": "licence_text"},
        {"nimbus-licence": "https://example.test/LICENSE"},
    )
    claim = _licence_claim("licence.commercial_use", "permitted", (_LICENCE, _README),
                           label="Commercial use")
    alone = verify.verify(claim, regions, verify.deterministic_extractors(), today=TODAY)
    assert alone.outcome == "skipped"
    assert alone.verification is None

    calls: list[str] = []

    def complete(prompt: str) -> str:
        calls.append(prompt)
        return _reply("prohibited", ["Commercial use: permitted"])

    result = verify.verify(
        claim, regions,
        [*verify.deterministic_extractors(), _licence_reader(complete)],
        today=TODAY,
    )
    assert calls
    assert result.outcome == "mismatch"
    assert result.diffs[0].field == "value"


def test_an_absence_from_a_disallowed_source_kind_does_not_verify() -> None:
    from decision.model import Fact

    body = "Model: Nimbus 3\nContext Window: 128K tokens\n"
    fact = Fact(
        id="lab/nimbus-3#model.max_output_tokens",
        subject={"kind": "model", "id": "lab/nimbus-3"},
        facet="model.max_output_tokens",
        state="not_disclosed",
        sources=[{"source_id": "nimbus-spec", "snapshot_ref": "sha256:" + "c" * 64,
                  "cited_regions": ["spec"]}],
    )
    claim = verify.Claim.from_fact(fact, names=["Nimbus 3"], collector=COLLECTOR)
    regions = _KindRegions({("nimbus-spec", "spec"): body}, {"nimbus-spec": "weights_repository"})
    result = verify.verify(claim, regions, verify.deterministic_extractors(), today=TODAY)
    assert result.outcome == "mismatch"
    assert result.diffs[0].field == "source_kind"

    allowed = _KindRegions({("nimbus-spec", "spec"): body}, {"nimbus-spec": "lab_documentation"})
    assert verify.verify(claim, allowed, verify.deterministic_extractors(), today=TODAY).outcome \
        == "verified"
