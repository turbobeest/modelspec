"""MODEL-423: Markdown model pages state token prices in ``Metric | Price`` tables.

A reading here can become a change the weekly re-read writes, so every case runs
the full deterministic verifier on a synthetic page. The cross-review's probes are
the wrong-row cases below: each must fail to verify, never read another row.
"""

from __future__ import annotations

from dataclasses import replace
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
def reads(verify_on):
    """Whether the verifier confirms ``field == value`` for a model on ``page``."""
    return lambda *args, **kwargs: verify_on(*args, **kwargs).outcome == "verified"


@pytest.fixture
def verify_on(tmp_path):
    """The full deterministic verifier's result for ``field == value`` on ``page``."""
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
        return verify.verify(claim, verify.StoredRegions(store, sources),
                             verify.deterministic_extractors(), today=date(2026, 10, 20))

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


# --- Round 2 of the cross-review: binding to the model heading, table ends ------------------


def test_the_verifier_sees_the_page_without_blank_lines():
    """The probes above and below run on this text, not on the raw Markdown."""
    from decision.normalise import NORMALISERS, normalise_document

    text = normalise_document((STANDARD + "\n| Endpoint | Price |\n").encode(),
                              NORMALISERS["text-default"]).text
    assert "\n\n" not in text and "| Output | $0.50 | 1M tokens |\n| Endpoint | Price |" in text


DECLARED_MINI_TABLE_UNDER_MAXI = """\
# Example Mini
Model ID: `example-mini`
Input
$0.10

# Example Maxi
## Pricing
| Metric | Price | Unit |
| Input | $8.00 | 1M tokens |
| Output | $16.00 | 1M tokens |
"""

TABLE_UNDER_MINI_MAXI_AFTER = STANDARD + """\

# Example Maxi
Input
$8.00
"""


def test_a_table_under_another_models_heading_is_never_the_declared_models(reads):
    page = DECLARED_MINI_TABLE_UNDER_MAXI
    for name, value in (("Example Mini", 8), ("Example Mini", .1), ("Example Maxi", 8)):
        assert not reads(page, "input", value, name=name)
    assert not reads(page, "output", 16, name="Example Mini")


def test_the_reverse_layout_reads_only_the_declared_models_own_table(reads):
    page = TABLE_UNDER_MINI_MAXI_AFTER
    assert reads(page, "input", .1)
    assert not reads(page, "input", 8)
    assert not reads(page, "input", 8, name="Example Maxi")
    assert not reads(page, "input", .1, name="Example Maxi")


def test_a_table_with_no_model_heading_above_it_is_not_read(reads):
    page = STANDARD.replace("# Example Mini\n", "")
    assert not reads(page, "input", .1)


@pytest.mark.parametrize("header", [
    "| Metric | Price (per 1M tokens) | Unit |", "| Metric | Price | Unit |",
])
def test_a_second_header_row_ends_the_table_even_with_a_digit_in_it(reads, header):
    page = ("# Example Mini\nModel ID: `example-mini`\n### Text tokens\n"
            "| Metric | Price | Unit |\n| Input | $0.10 | 1M tokens |\n"
            f"{header}\n| Output | $30.00 | 1M tokens |\n")
    # Two standard tables for one model: nothing is read, so nothing is written.
    assert not reads(page, "output", 30)
    assert not reads(page, "input", .1)


def test_a_price_header_with_a_unit_in_parentheses_is_read(reads):
    page = STANDARD.replace("| Metric | Price | Unit |",
                            "| Metric | Price (per 1M tokens) | Unit |")
    assert reads(page, "input", .1)


def test_a_markdown_rule_under_the_header_is_part_of_it(reads):
    page = STANDARD.replace("| Metric | Price | Unit |\n",
                            "| Metric | Price | Unit |\n|---|:---:|---|\n")
    assert reads(page, "input", .1) and reads(page, "output", .5)
    # text-default drops rule lines; on text that keeps them, a rule after the
    # first row ends the table, so the rows under it are not this table's.
    ruled = page.replace("| Output |", "|---|---|---|\n| Output |")
    table = verify.MetricPriceTable.read(ruled)
    assert table.reading(_claim("output")).value is None
    assert table.reading(_claim("input")).value == "$0.10"


def _claim(field):
    return verify.Claim(
        target=TargetRef(kind="fact", id=f"offering#{field}"),
        subject="example/example/model/global/standard", names=("Example Mini",),
        field=f"offering.price.{field}", value=0, unit="usd_per_1m_tokens",
        collector=COLLECTOR, sources=(SourceRef(source_id="model-page",
                                                snapshot_ref="sha256:" + "0" * 64,
                                                cited_regions=["page"]),))


def test_a_change_in_column_count_ends_the_table(reads):
    page = STANDARD.replace("| Output | $0.50 | 1M tokens |", "| Output | $30.00 |")
    assert not reads(page, "output", 30)
    assert reads(page, "input", .1)


@pytest.mark.parametrize("heading", ["### Standard (non-batch)", "### Standard (non batch)"])
def test_a_non_batch_heading_is_a_standard_section(reads, heading):
    page = STANDARD.replace("### Text tokens", heading)
    assert reads(page, "input", .1)
    assert not reads(page, "batch_input", .1)
    assert reads(page + HALF, "batch_input", .05)


def test_an_input_cached_row_is_the_cached_input_price(reads):
    page = STANDARD.replace("| Cached input |", "| Input (cached) |")
    assert reads(page, "cached_input", .01)
    assert not reads(page, "input", .01)
    assert reads(page, "input", .1)


def test_no_model_declaration_or_two_agreeing_standard_tables_read_nothing(reads):
    assert not reads(STANDARD.replace("Model ID: `example-mini`\n", ""), "input", .1)
    twice = STANDARD + "### Text tokens\n| Metric | Price | Unit |\n| Input | $0.10 | 1M tokens |\n"
    assert not reads(twice, "input", .1)


# --- Round 3 of the cross-review: the nearest model heading, the price column ---------------


def _table_reading(page, field, name):
    from decision.normalise import NORMALISERS, normalise_document

    text = normalise_document(page.encode(), NORMALISERS["text-default"]).text
    claim = replace(_claim(field), names=(name,))
    return verify.MetricPriceTable.read(text).reading(claim).value


MAXI_UNDER_DECLARED_MINI = """\
# Example Mini
Model ID: `example-mini`
## Example Maxi
| Metric | Price | Unit |
| Input | $8.00 | 1M tokens |
| Output | $16.00 | 1M tokens |
"""

MINI_HEADING_UNDER_MAXI = """\
# Example Mini
Model ID: `example-mini`

# Example Maxi
## Example Mini
| Metric | Price | Unit |
| Input | $8.00 | 1M tokens |
| Output | $16.00 | 1M tokens |
"""

BATCH_COLUMN_FIRST = """\
# Example Mini
Model ID: `example-mini`
## Pricing
### Text tokens
| Metric | Price (batch) | Price |
| Input | $0.04 | $0.10 |
| Output | $0.20 | $0.50 |
"""


@pytest.mark.parametrize("page", [MAXI_UNDER_DECLARED_MINI, MINI_HEADING_UNDER_MAXI])
@pytest.mark.parametrize("name", ["Example Mini", "Example Maxi"])
@pytest.mark.parametrize("field", ["input", "output"])
def test_a_table_under_a_heading_naming_another_model_is_read_for_no_model(page, name, field):
    assert _table_reading(page, field, name) is None


def test_another_models_heading_never_donates_its_price_to_the_declared_model(reads):
    assert not reads(MAXI_UNDER_DECLARED_MINI, "input", 8)
    assert not reads(MAXI_UNDER_DECLARED_MINI, "output", 16)


def test_a_price_batch_column_is_the_batch_price_not_the_standard_price(reads):
    for field, value in (("input", .1), ("output", .5), ("batch_input", .04),
                         ("batch_output", .2)):
        assert reads(BATCH_COLUMN_FIRST, field, value)
    assert not reads(BATCH_COLUMN_FIRST, "input", .04)
    assert not reads(BATCH_COLUMN_FIRST, "output", .2)


@pytest.mark.parametrize("header", [
    "| Metric | Price (flex) | Unit |",
    "| Metric | Price | Price |",
    "| Metric | Price (batch) | Batch price |",
    "| Metric | Pricing note | Unit |",
])
def test_an_unclear_price_column_reads_nothing(reads, header):
    page = STANDARD.replace("| Metric | Price | Unit |", header)
    assert not reads(page, "input", .1)


def test_a_cached_price_column_states_the_cached_input_price(reads):
    page = STANDARD.replace("| Metric | Price | Unit |", "| Metric | Price | Price (cached) |") \
        .replace("| Input | $0.10 | 1M tokens |", "| Input | $0.10 | $0.01 |") \
        .replace("| Cached input | $0.01 | 1M tokens |\n", "")
    assert reads(page, "input", .1) and reads(page, "cached_input", .01)
    assert not reads(page, "input", .01)


# --- Round 4 of the cross-review: columns inside a batch section ----------------------------


def _batch_section(header, input_row, output_row):
    return STANDARD + f"## Batch\n{header}\n{input_row}\n{output_row}\n"


BOTH_BATCH_COLUMNS = [
    _batch_section("| Metric | Price (batch) | Price |", "| Input | $0.04 | $0.10 |",
                   "| Output | $0.20 | $0.50 |"),
    _batch_section("| Metric | Price | Price (batch) |", "| Input | $0.10 | $0.04 |",
                   "| Output | $0.50 | $0.20 |"),
]


@pytest.mark.parametrize("page", BOTH_BATCH_COLUMNS, ids=["batch-first", "price-first"])
def test_a_batch_section_with_a_batch_and_a_plain_price_column_that_differ_reads_nothing(
        reads, page):
    for value in (.04, .1):
        assert not reads(page, "batch_input", value)
    for value in (.2, .5):
        assert not reads(page, "batch_output", value)
    assert reads(page, "input", .1)  # the standard section above is unaffected


@pytest.mark.parametrize(("header", "row"), [
    ("| Metric | Price | Unit |", "| Input | $0.04 | 1M tokens |"),
    ("| Metric | Price (batch) | Unit |", "| Input | $0.04 | 1M tokens |"),
    ("| Metric | Price (batch) | Price |", "| Input | $0.04 | $0.04 |"),
])
def test_a_batch_section_states_its_one_batch_price(reads, header, row):
    page = STANDARD + f"## Batch\n{header}\n{row}\n"
    assert reads(page, "batch_input", .04)
    assert not reads(page, "batch_input", .1)


def test_a_cached_column_in_a_batch_section_reads_nothing(reads):
    page = STANDARD + ("## Batch\n| Metric | Price | Price (cached) |\n"
                       "| Input | $0.04 | $0.01 |\n")
    assert not reads(page, "batch_input", .04)
    assert not reads(page, "cached_input", .01)


BATCH_FACT = "example/example/model/global/standard#offering.price.batch_input"


@pytest.mark.parametrize(("filed_page", "filed"), [
    # Filed from a batch section whose only price column was Price.
    (STANDARD + "## Batch\n| Metric | Price | Unit |\n| Input | $0.10 | 1M tokens |\n", .1),
    # Filed from a batch section whose only price column was Price (batch).
    (STANDARD + "## Batch\n| Metric | Price (batch) | Unit |\n| Input | $0.04 | 1M tokens |\n",
     .04),
], ids=["filed-from-price", "filed-from-price-batch"])
def test_a_two_column_batch_section_never_reconfirms_a_stale_batch_price(
        tmp_path, filed_page, filed):
    """The reviewer's --write case: the Price (batch) cell changed to $0.01."""
    import json
    from datetime import UTC, datetime

    import yaml
    from scripts import price_reread

    root = tmp_path / "repo"
    (root / "registry").mkdir(parents=True)
    (root / "registry/sources.yaml").write_text(SOURCES)
    store = CopyStore(tmp_path / "copies")
    ref = store.put(filed_page.encode(), source_url="https://fixture.example/")
    path = root / "offerings/example/example/model.yaml"
    path.parent.mkdir(parents=True)
    subject = "example/example/model/global/standard"
    fact = {"id": BATCH_FACT, "subject": {"kind": "offering", "id": subject},
            "facet": "offering.price.batch_input", "state": "known", "value": filed,
            "sources": [{"source_id": "model-page", "snapshot_ref": ref,
                         "cited_regions": ["page"]}]}
    path.write_text(yaml.safe_dump([{"model": "example/model", "provider": "example",
                                     "region": "global", "tier": "standard", "facts": [fact]}],
                                   sort_keys=False))
    claim = verify.Claim(
        target=TargetRef(kind="fact", id=BATCH_FACT), subject=subject,
        names=("Example Mini", "example-mini"), field="offering.price.batch_input",
        label="Batch Input", value=filed, unit="usd_per_1m_tokens", collector=COLLECTOR,
        sources=(SourceRef(source_id="model-page", snapshot_ref=ref, cited_regions=["page"]),))
    queue, log = verify.Queue(root / "verification"), verify.VerificationLog(root / "verification")
    queue.file(claim, at=datetime(2026, 10, 17, tzinfo=UTC))
    regions = verify.StoredRegions(store, load_sources(root / "registry/sources.yaml"))
    result = verify.verify(claim, regions, verify.deterministic_extractors(),
                           today=date(2026, 10, 17))
    assert result.outcome == "verified", result
    log.append(result.verification)
    before = {p: p.read_text() for p in (path, queue.path, log.path)}
    new_page = _batch_section("| Metric | Price (batch) | Price |", "| Input | $0.01 | $0.10 |",
                              "| Output | $0.20 | $0.50 |")

    class Fetcher:
        def fetch(self, url, **kwargs):
            from decision.sources import FetchResult

            return FetchResult("ok", 200, body=new_page.encode(), content_type="text/plain",
                               charset="utf-8")

    report = price_reread.run(root=root, fetcher=Fetcher(), store=store,
                              today=date(2026, 10, 20), write=True)
    [result] = report.facts
    assert result.status in {price_reread.Status.NEEDS_REVIEW, price_reread.Status.UNREADABLE}, \
        json.dumps(result.to_dict())
    assert {p: p.read_text() for p in before} == before


# --- MODEL-426: the looser offering-price reader keeps to the same heading rule -------------

MINI_UNDER_DECLARED_MAXI = """\
# Example Maxi
Model ID: `example-maxi`
## Example Mini
| Metric | Price | Unit |
| Input | $8.00 | 1M tokens |
| Output | $16.00 | 1M tokens |
"""

#: Round 4's stale-table page: the pricing section states $10, and a later table
#: under ``## Example Mini`` inside ``# Example Maxi`` still states the filed $8.
STALE_TABLE_UNDER_MAXI = """\
# Example Mini
Model ID: `example-mini`
## Pricing
### Text tokens
| Metric | Price | Unit |
| Input | $10.00 | 1M tokens |
| Output | $16.00 | 1M tokens |

# Example Maxi
## Example Mini
| Metric | Price | Unit |
| Input | $8.00 | 1M tokens |
| Output | $16.00 | 1M tokens |
"""


@pytest.mark.parametrize("page", [MAXI_UNDER_DECLARED_MINI, MINI_UNDER_DECLARED_MAXI,
                                  MINI_HEADING_UNDER_MAXI],
                         ids=["maxi-under-mini", "mini-under-maxi", "two-h1s-and-an-h2"])
@pytest.mark.parametrize("name", ["Example Mini", "Example Maxi"])
@pytest.mark.parametrize(("field", "value"), [("input", 8), ("output", 16)])
def test_a_table_under_another_models_heading_verifies_for_no_model(
        reads, page, name, field, value):
    """The reviewers' pages: neither reader takes the table for either model."""
    assert not reads(page, field, value, name=name)


@pytest.mark.parametrize("page", [MAXI_UNDER_DECLARED_MINI, MINI_UNDER_DECLARED_MAXI,
                                  MINI_HEADING_UNDER_MAXI],
                         ids=["maxi-under-mini", "mini-under-maxi", "two-h1s-and-an-h2"])
@pytest.mark.parametrize("name", ["Example Mini", "Example Maxi"])
def test_the_offering_reader_binds_a_table_to_its_heading_path(page, name):
    """OfferingPriceExtractor alone, without the strict reader in front of it."""
    claim = replace(_claim("input"), names=(name,), value=8)
    assert verify.OfferingPriceExtractor().extract(claim, page) == []


def test_a_stale_table_under_another_models_heading_never_reconfirms_the_filed_price(verify_on):
    stale = verify_on(STALE_TABLE_UNDER_MAXI, "input", 8)
    assert stale.outcome == "mismatch"
    assert [(diff.expected, diff.found) for diff in stale.diffs] == [
        ("8 usd_per_1m_tokens", "10.00 usd_per_1m_tokens"),
    ]
    current = verify_on(STALE_TABLE_UNDER_MAXI, "input", 10)
    assert current.outcome == "verified"
    assert current.verification.method == "model-page-label-match@1"


@pytest.mark.parametrize("heading", ["# Example Mini", "# Pricing\n## Example Mini",
                                     "# Example Mini\n## Example Mini"])
def test_the_offering_reader_still_reads_a_table_under_the_models_own_heading(heading):
    page = f"{heading}\n| Usage | Price per 1M tokens |\n| Input | $8.00 |\n"
    claim = replace(_claim("input"), names=("Example Mini",), value=8)
    readings = verify.OfferingPriceExtractor().extract(claim, page)
    assert [(reading.subject, reading.value) for reading in readings] == [("Example Mini", "$8.00")]


@pytest.mark.parametrize("heading", ["# Example Maxi\n## Example Mini",
                                     "# Example Mini\n## Example Maxi\n### Example Mini"])
def test_the_offering_reader_refuses_a_non_metric_table_under_another_models_heading(heading):
    page = f"{heading}\n| Usage | Price per 1M tokens |\n| Input | $8.00 |\n"
    claim = replace(_claim("input"), names=("Example Mini",), value=8)
    assert verify.OfferingPriceExtractor().extract(claim, page) == []


#: Each table sits directly under the model's own heading, so the offering reader
#: alone would read its first price cell. The strict reader refuses each one.
REFUSED_BY_THE_STRICT_READER = {
    # Which column is the standard price is not clear.
    "flex-column": """\
# Example Mini
Model ID: `example-mini`
## Example Mini
| Metric | Price (flex) | Price |
| Input | $0.04 | $0.10 |
| Output | $0.20 | $0.50 |
""",
    # The page declares two model IDs.
    "two-model-ids": """\
Model ID: `example-mini`
Default snapshot: `example-mini-2026`
# Example Mini
| Metric | Price | Unit |
| Input | $0.04 | 1M tokens |
| Output | $0.20 | 1M tokens |
""",
}


@pytest.mark.parametrize("page", REFUSED_BY_THE_STRICT_READER.values(),
                         ids=REFUSED_BY_THE_STRICT_READER.keys())
def test_a_looser_reader_never_overrides_the_strict_readers_refusal(verify_on, page):
    claim = replace(_claim("input"), names=("Example Mini",), value=.04)
    loose = verify.OfferingPriceExtractor().extract(claim, page)
    assert verify.compare(claim, loose) == []  # the looser reader alone would verify it
    for field, value in (("input", .04), ("output", .2)):
        result = verify_on(page, field, value)
        assert result.outcome != "verified", result
