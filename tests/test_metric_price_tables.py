"""MODEL-423: Markdown model pages state token prices in ``Metric | Price`` tables.

A reading here can become a change the weekly re-read writes, so every case runs
the full deterministic verifier on a synthetic page. The cross-review's probes are
the wrong-row cases below: each must fail to verify, never read another row.
"""

from __future__ import annotations

from datetime import date

import pytest
from decision import verify
from decision.model import SourceRef, TargetRef, VerificationActor
from decision.sources import CopyStore, load_sources

SOURCES = """\
schema_version: 1
sources:
- id: model-page
  url: https://docs.example/models/example-mini.md
  fetch: conditional_http
  normaliser: text-default
  cited_regions:
  - id: page
    locator: {kind: page, value: ''}
"""
COLLECTOR = VerificationActor(agent="fixture-collector", model_family="anthropic",
                              method="fixture@1")
HALF = "- Batch and Flex are priced at 50% of Standard rates.\n"
STANDARD = """\
# Example Mini
Model ID: `example-mini`
## Pricing
### Text tokens
| Metric | Price | Unit |
| Input | $0.10 | 1M tokens |
| Cached input | $0.01 | 1M tokens |
| Cache writes | $0.125 | 1M tokens |
| Output | $0.50 | 1M tokens |
"""


@pytest.fixture
def reads(tmp_path):
    """Whether the verifier confirms ``field == value`` for a model on ``page``."""
    (tmp_path / "sources.yaml").write_text(SOURCES)
    sources = load_sources(tmp_path / "sources.yaml")
    store = CopyStore(tmp_path / "copies")

    def check(page: str, field: str, value: float, *, name: str = "Example Mini",
              label: str | None = "default") -> bool:
        ref = store.put(page.encode(), source_url="https://fixture.example/")
        claim = verify.Claim(
            target=TargetRef(kind="fact", id=f"offering#{field}"),
            subject="example/example/model/global/standard",
            names=(name, name.lower().replace(" ", "-")),
            field=f"offering.price.{field}",
            label=field.replace("_", " ").title() if label == "default" else label,
            value=value, unit="usd_per_1m_tokens", collector=COLLECTOR,
            sources=(SourceRef(source_id="model-page", snapshot_ref=ref,
                               cited_regions=["page"]),),
        )
        result = verify.verify(claim, verify.StoredRegions(store, sources),
                               verify.deterministic_extractors(), today=date(2026, 10, 20))
        return result.outcome == "verified"

    return check


@pytest.mark.parametrize("label", ["default", None])
@pytest.mark.parametrize(("field", "value"), [
    ("input", .1), ("cached_input", .01), ("output", .5), ("batch_input", .05),
    ("batch_output", .25),
])
def test_a_single_model_page_states_its_standard_cached_and_half_batch_prices(
        reads, field, value, label):
    assert reads(STANDARD + HALF, field, value, label=label)


@pytest.mark.parametrize(("field", "value"), [
    ("input", .12), ("cached_input", .1), ("output", .1), ("batch_input", .1),
])
def test_a_price_the_page_does_not_state_for_that_kind_does_not_verify(reads, field, value):
    assert not reads(STANDARD + HALF, field, value)


def test_no_batch_price_without_a_batch_statement(reads):
    assert not reads(STANDARD, "batch_input", .05)


def test_a_fine_tuning_table_never_states_the_standard_price(reads):
    page = STANDARD + "### Fine-tuning\n| Metric | Price | Unit |\n" \
        "| Input | $25.00 | 1M tokens |\n| Output | $30.00 | 1M tokens |\n"
    assert reads(page, "input", .1) and reads(page, "output", .5)
    assert not reads(page, "input", 25) and not reads(page, "output", 30)
    nested = page.replace("### Fine-tuning", "## Fine-tuning\n### Text tokens")
    assert not reads(nested, "input", 25)


@pytest.mark.parametrize("gap", ["\n", ""])
def test_an_endpoint_price_table_after_the_metric_table_is_not_read(reads, gap):
    page = STANDARD + gap + "| Endpoint | Price |\n| Input | $9.00 |\n"
    assert not reads(page, "input", 9)
    # A row with no amount starts the next table even without a blank line.
    assert reads(page, "input", .1)


def test_a_cached_section_input_row_is_neither_input_nor_cached_input(reads):
    page = STANDARD + "### Cached\n| Metric | Price |\n| Input | $0.05 |\n"
    assert not reads(page, "input", .05)
    assert not reads(page, "cached_input", .05)
    assert reads(page, "input", .1)


def test_an_explicit_batch_row_that_contradicts_the_half_price_rule_reads_neither(reads):
    page = STANDARD.replace("| Output |", "| Batch input | $0.04 | 1M tokens |\n| Output |")
    assert not reads(page + HALF, "batch_input", .04)
    assert not reads(page + HALF, "batch_input", .05)
    assert reads(page, "batch_input", .04)
    agreeing = page.replace("$0.04", "$0.05")
    assert reads(agreeing + HALF, "batch_input", .05)


def test_a_batch_price_column_is_read_and_checked_against_the_half_price_rule(reads):
    page = STANDARD.replace("| Metric | Price | Unit |", "| Metric | Price | Batch price |") \
        .replace("| Input | $0.10 | 1M tokens |", "| Input | $0.10 | $0.04 |")
    assert reads(page, "batch_input", .04)
    assert not reads(page, "batch_input", .05)
    assert not reads(page + HALF, "batch_input", .04)
    assert not reads(page + HALF, "batch_input", .05)


def test_one_models_price_never_verifies_another_models_claim(reads):
    maxi = STANDARD.replace("Example Mini", "Example Maxi") \
        .replace("example-mini", "example-maxi").replace("$0.10", "$8.00")
    both = STANDARD + maxi
    for name, value in (("Example Mini", 8), ("Example Mini", .1), ("Example Maxi", 8),
                        ("Example Maxi", .1)):
        assert not reads(both, "input", value, name=name)
    assert not reads(STANDARD, "input", .1, name="Example Maxi")


@pytest.mark.parametrize("page", [
    STANDARD.replace("| Input | $0.10 | 1M tokens |", "| **Input** | **$0.10** | 1M tokens |"),
    STANDARD.replace("| Metric | Price | Unit |", "| Metric | Unit | Price |")
    .replace("| Input | $0.10 | 1M tokens |", "| Input | 1M tokens | $0.10 |"),
])
def test_bold_cells_and_a_moved_price_column_are_read_by_header(reads, page):
    assert reads(page, "input", .1)


def test_an_output_row_on_the_last_line_still_derives_its_batch_price(reads):
    page = HALF + STANDARD
    assert reads(page, "output", .5) and reads(page, "batch_output", .25)


def test_a_kind_stated_twice_with_different_amounts_is_not_read(reads):
    page = STANDARD.replace("| Output |", "| Input | $0.20 | 1M tokens |\n| Output |")
    assert not reads(page, "input", .1) and not reads(page, "input", .2)
    assert reads(page, "output", .5)
