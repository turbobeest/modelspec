"""MODEL-140: two-key verification and quarantine (design §5, "Two keys").

The agent that collects a value never verifies it. These tests run the seeded
error fixture in ``tests/fixtures/verification`` end to end: every correct value
must end ``verified`` and every seeded error ``mismatch``, ``unreachable`` or
unverified, so quarantined. No network and no model call: the LLM extractor is
exercised with a fake completion.
"""

from __future__ import annotations

import json
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
    from cli.modelspec import cli as cli_mod

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
    from cli.modelspec import cli as cli_mod

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


def test_llm_cache_key_is_copy_region_and_facet(tmp_path, store, regions) -> None:
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
])
def test_an_effort_written_as_prose_is_read_as_its_level(store, regions, found, outcome) -> None:
    claim = _prose_claim(store)
    claim = verify.Claim(**{**claim.__dict__, "conditions": {"effort": "max"}})
    reading = _FakeLLM(json.dumps([{
        "subject": "GPT-6 Sol", "value": "400,000", "unit": "tokens", "effort": found,
        "quoted_sentence": "It accepts up to 400,000 tokens of context.",
    }]))
    assert verify.verify(claim, regions, [reading.extractor], today=TODAY).outcome == outcome
