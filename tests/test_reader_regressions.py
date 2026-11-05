"""A table reader needs this model's column before it can judge a claim."""

from datetime import date

import pytest

from decision import verify
from decision.model import SourceRef, TargetRef, VerificationActor


class Page:
    def __init__(self, text, url=None):
        self.body = text
        self.url = url

    def text(self, source_id, copy_ref, region_id):
        return self.body

    def source_url(self, source_id):
        return self.url or "https://fixture.example/model"


def claim(value=4200, *, names=("Fixture Model",), field="model.context_window",
          label="Context window"):
    return verify.Claim(
        target=TargetRef(kind="fact", id=f"fixture#{field}"),
        subject="lab/fixture", names=names, field=field, label=label, value=value,
        collector=VerificationActor(agent="fixture-collector", model_family="human",
                                    method="fixture@1"),
        sources=(SourceRef(source_id="fixture", snapshot_ref="sha256:" + "0" * 64,
                           cited_regions=["page"]),),
    )


def read(text, subject=None, *, readers=None, url=None):
    return verify.verify(subject or claim(), Page(text, url),
                         readers if readers is not None else verify.deterministic_extractors(),
                         today=date(2026, 11, 5))


@pytest.mark.parametrize("header", ["Fixture Model Ultra", "Other Model"])
def test_transposed_table_without_subject_column_abstains(header):
    text = f"| {header} | Third Model\nContext window | 4200 | 9000\n"
    result = read(text, readers=[verify.TransposedTableExtractor()])
    assert result.outcome == "skipped"
    assert result.verification is None
    assert result.diffs == ()


@pytest.mark.parametrize("markdown", [False, True])
@pytest.mark.parametrize("reverse", [False, True])
@pytest.mark.parametrize("published,names", [
    ("FIXTURE--Model", ("Fixture Model",)),
    ("Fixture Global", ("Fixture Model", "Fixture Global")),
])
def test_transposed_table_selects_only_the_exact_subject_column(markdown, reverse, published, names):
    columns = [(published, "4200"), ("Fixture Model Ultra", "9000")]
    if reverse:
        columns.reverse()
    rows = [["", *(name for name, _ in columns)],
            ["Context window", *(value for _, value in columns)]]
    if markdown:
        rows.insert(1, ["---", "---", "---"])
    text = "\n".join(("| " + " | ".join(row) + " |") if markdown
                     else " | ".join(row) for row in rows)
    subject = claim(names=names)
    reader = verify.TransposedTableExtractor()
    result = read(text, subject, readers=[reader])
    assert result.outcome == "verified", result
    assert reader.extract(subject, text) == [verify.Reading(published, "4200")]
    wrong = read(text, claim(9000, names=names), readers=[reader])
    assert wrong.outcome == "mismatch"
    assert [(diff.field, diff.found) for diff in wrong.diffs] == [("value", "4200")]


def test_empty_table_reader_does_not_displace_a_later_exact_model_reading():
    text = ("| Other Model | Third Model\nContext window | 9000 | 7000\n"
            "# Fixture Model\nContext window: 4200\nUnit: tokens\n")
    assert read(text).outcome == "verified"


@pytest.mark.parametrize("label", ["Property", "Metric", "Benchmark"])
def test_transposed_table_with_a_labeled_first_header_selects_the_model(label):
    text = (f"| {label} | Fixture Model Ultra | Fixture Model |\n"
            "| --- | --- | --- |\n| Context window | 9000 | 4200 |\n")
    assert read(text, readers=[verify.TransposedTableExtractor()]).outcome == "verified"


@pytest.mark.parametrize("title", [
    "# Fixture Model: A model for general tasks", "# Fixture Model Model Card",
])
def test_model_heading_grammar_keeps_the_complete_model_name(title):
    text = f"license: mit\nlibrary_name: transformers\n{title}\nContext window: 4200\n"
    assert read(text).outcome == "verified"
    assert read(text, claim("open_weights", field="model.weights_openness",
                            label="weights openness")).outcome == "verified"


@pytest.mark.parametrize("title", [
    "# Fixture Model Ultra: A model for general tasks", "# Fixture Model Ultra Model Card",
    "# Ultra Fixture Model: A model for general tasks", "# Ultra Fixture Model Model Card",
])
def test_model_heading_grammar_does_not_shorten_a_sibling_name(title):
    text = f"license: mit\nlibrary_name: transformers\n{title}\nContext window: 4200\n"
    assert read(text).outcome != "verified"


def test_html_presentation_does_not_close_the_model_section():
    text = ('# Fixture Model\n<hr>\n<div style="line-height: 1;">\n</div>\n'
            '## Introduction\nThis model supports tool calling.\n')
    assert read(text, claim(True, field="feature.tool_calling", label="Function calling")).outcome == "verified"


HF_README = "https://huggingface.co/lab/Fixture-Model/raw/main/README.md"
RICH_METADATA = ("license: mit\ntags:\n- transformers\n- conversational\n"
                 "base_model:\n- lab/base\nmodel-index:\n- name: evaluation\n  results: []\n")


@pytest.mark.parametrize("field,value,label", [
    ("model.weights_openness", "open_weights", "weights openness"),
    ("model.class", "text-generator", "model class"),
    ("model.input_modalities", None, "input modalities"),
    ("model.context_window", 4200, "context window"),
])
def test_exact_hf_readme_identity_binds_its_metadata_and_own_page(field, value, label):
    text = RICH_METADATA + '<img src="banner.svg">\n## Model details\nContext window: 4200\n'
    assert read(text, claim(value, field=field, label=label), url=HF_README).outcome == "verified"


@pytest.mark.parametrize("url", [
    HF_README.replace("Fixture-Model/", "Fixture-Model-Ultra/"),
    HF_README.replace("huggingface.co", "fixture.example"),
])
def test_an_unbound_repository_does_not_supply_page_identity(url):
    text = RICH_METADATA + "## Model details\nContext window: 4200\n"
    assert read(text, url=url).outcome != "verified"


def test_exact_repository_does_not_lend_identity_to_a_sibling_section():
    text = RICH_METADATA + "# Fixture Model Ultra\nContext window: 4200\n"
    assert read(text, url=HF_README).outcome != "verified"


@pytest.mark.parametrize("field,value", [("batch_input", 0.57), ("batch_output", 2.4)])
def test_batch_billing_qualifier_keeps_the_exact_models_price(field, value):
    text = ("Batch prices per million tokens.\n"
            "Model | Unit | Input Price (Cache Hit) | Input Price (Cache Miss) | Output Price\n"
            "Fixture Model Ultra (Batch) | 1M tokens | $1 | $5 | $9\n"
            "FIXTURE--Model (Batch) | 1M tokens | $0.10 | $0.57 | $2.40\n")
    subject = claim(value, field=f"offering.price.{field}", label=field.replace("_", " "))
    result = read(text, subject)
    assert result.outcome == "verified", result
    readings = verify.OfferingPriceExtractor().extract(subject, text)
    assert readings
    assert {reading.subject for reading in readings} == {"FIXTURE--Model (Batch)"}


@pytest.mark.parametrize("field", ["input", "batch_input"])
@pytest.mark.parametrize("name", ["Fixture Model Ultra (Batch)", "Fixture Model (Priority)"])
def test_a_billing_qualifier_cannot_hide_a_sibling_or_a_different_tier(field, name):
    text = f"Model | Input Price | Output Price\n{name} | $5 | $9\nPrices per million tokens."
    assert read(text, claim(5, field=f"offering.price.{field}", label="input")).outcome != "verified"


def test_batch_price_is_not_a_standard_price():
    text = "Model | Input Price | Output Price\nFixture Model (Batch) | $5 | $9\nBatch pricing."
    assert read(text, claim(5, field="offering.price.input", label="input")).outcome != "verified"


@pytest.mark.parametrize("text", [
    "Model | Context window\nFixture Model Ultra | 4200\nDetails follow.",
    "# Fixture Model Ultra\nContext window: 4200\nUnit: tokens",
    "Model: Fixture Model Ultra\nContext window: 4200\nUnit: tokens",
])
def test_only_a_reading_for_the_claimed_model_can_create_a_mismatch(text):
    result = read(text)
    assert result.outcome == "skipped"
    assert result.verification is None
    assert result.diffs == ()


def test_an_exact_subject_with_a_different_value_still_mismatches():
    result = read("Model: Fixture Model\nContext window: 9000\nUnit: tokens")
    assert result.outcome == "mismatch"
    assert any(diff.field == "value" and diff.found == "9000 tokens" for diff in result.diffs)


def test_transposed_column_ownership_ends_at_the_next_table_header():
    text = ("| Property | Fixture Model | Other Model |\n| --- | --- | --- |\n"
            "| Context window | 4200 | 7000 |\n"
            "| Property | Fixture Model Ultra | Other Model |\n| --- | --- | --- |\n"
            "| Context window | 9000 | 7000 |\n")
    reader = verify.TransposedTableExtractor()
    assert read(text, claim(9000), readers=[reader]).outcome == "mismatch"
    assert reader.extract(claim(), text) == [verify.Reading("Fixture Model", "4200")]


@pytest.mark.parametrize("description", [
    "Fixture Model is a model for general tasks. It has a multimodal architecture.",
    "Our model handles text and images (with a separate encoder).",
])
@pytest.mark.parametrize("field,value,label", [
    ("model.input_modalities", ["text", "image"], "Input"),
    ("model.release_date", "2026-10-01", "Release date"),
])
def test_a_description_before_metadata_does_not_rename_the_model(description, field, value, label):
    text = (f"# Fixture Model\n{description}\n- API names: `fixture-model`, `fixture-latest`\n"
            "- Release date: 2026-10-01\n- Input: text, image\n")
    assert read(text, claim(value, field=field, label=label)).outcome == "verified"


@pytest.mark.parametrize("body", [
    "Features\nBatching\nAgents & Conversations",
    "- Features: Chat Completions, Function Calling, Batching",
])
def test_batching_is_a_named_capability_of_its_exact_model(body):
    text = f"# Fixture Model\n{body}\nModel documentation.\n"
    assert read(text, claim(True, field="feature.batch", label="Batch interface")).outcome == "verified"


def test_a_siblings_batching_capability_does_not_describe_this_model():
    text = "# Fixture Model\n# Fixture Model Ultra\nFeatures\nBatching\nAgents & Conversations"
    assert read(text, claim(True, field="feature.batch", label="Batch interface")).outcome != "verified"


def test_price_display_labels_do_not_rename_a_models_capability_section():
    text = ("Fixture Model\nInput\nSale price\nOriginal price: $1.00Sale price: $0.50\n"
            "M Tokens\nOriginal price: $2.00Sale price: $1.00\nM Tokens\nFeatures\n"
            "Batching\nAgents & Conversations\n")
    assert read(text, claim(True, field="feature.batch", label="Batch interface")).outcome == "verified"
