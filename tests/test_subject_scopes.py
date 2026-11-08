"""Whole-page verification keeps values inside their published subject's block."""

from datetime import date

import pytest

from decision.model import SourceRef, TargetRef, VerificationActor
from decision.normalise import NORMALISERS, normalise_document
from decision.verify import Claim, deterministic_extractors, verify


class Page:
    def __init__(self, text):
        self.body = text

    def text(self, source_id, copy_ref, region_id):
        return self.body


def verify_page(text, field, value, *, names=("Fixture Model",)):
    price = field.startswith("offering.price.")
    label = field.removeprefix("offering.price.") if price else field.removeprefix("model.")
    claim = Claim(
        target=TargetRef(kind="fact", id=f"fixture#{field}"),
        subject="provider/lab/fixture/global/standard" if price else "lab/fixture",
        names=names, field=field, label=label.replace("_", " "), value=value,
        unit="usd_per_1m_tokens" if price else "tokens" if field == "model.context_window" else None,
        collector=VerificationActor(agent="fixture-collector", model_family="human", method="fixture@1"),
        sources=(SourceRef(source_id="fixture", snapshot_ref="sha256:" + "0" * 64,
                           cited_regions=["page"]),),
    )
    return verify(claim, Page(text), deterministic_extractors(), today=date(2026, 11, 5))


@pytest.mark.parametrize("earlier_exact", [False, True])
@pytest.mark.parametrize("layout", ["markdown", "html"])
@pytest.mark.parametrize("field,value,lines", [
    ("offering.price.input", 5, ["$5 input", "$9 output"]),
    ("model.context_window", 5000, ["5000 context window", "Additional model details."]),
])
def test_inverse_label_values_remain_with_the_sibling(
        earlier_exact, layout, field, value, lines):
    titles = (["Fixture Model"] if earlier_exact else []) + ["Fixture Model Ultra"]
    if layout == "markdown":
        text = "\n".join([*("# " + name for name in titles), *lines])
    else:
        body = "".join(f"<h2>{name}</h2>" for name in titles)
        body += "".join(f"<p>{line}</p>" for line in lines)
        text = normalise_document(body.encode(), NORMALISERS["html-default"]).text
    assert verify_page(text, field, value).outcome != "verified"


@pytest.mark.parametrize("title", ["# Fixture Model", "# Model Card for Fixture Model"])
def test_leading_license_metadata_belongs_to_the_first_exact_model_title(title):
    text = f"license: mit\nlibrary_name: transformers\n{title}\nModel details."
    assert verify_page(text, "model.weights_openness", "open_weights").outcome == "verified"


@pytest.mark.parametrize("text", [
    "license: mit\n# Fixture Model Ultra\n# Fixture Model\nModel details.",
    "license: mit\nModel: Fixture Model Ultra\n# Fixture Model\nModel details.",
    "# Fixture Model\n# Fixture Model Ultra\nlicense: mit\nModel details.",
    "license: mit\n# Model Card for Fixture Model Ultra\n# Fixture Model\nModel details.",
])
def test_sibling_license_metadata_does_not_describe_an_exact_model_elsewhere(text):
    assert verify_page(text, "model.weights_openness", "open_weights").outcome != "verified"


def test_priority_heading_is_not_a_standard_price():
    text = "# Fixture Model\n## Priority\nInput\n$5\nOutput\n$9"
    assert verify_page(text, "offering.price.input", 5).outcome != "verified"


@pytest.mark.parametrize("published", ["Fixture Model Ultra", "Ultra Fixture Model"])
def test_a_siblings_feature_sentence_does_not_inherit_the_pages_model(published):
    text = f"# Fixture Model\n{published} supports function calling.\nMore details follow."
    assert verify_page(text, "feature.tool_calling", "supported").outcome != "verified"


def test_exact_model_feature_sentence_under_introduction_still_verifies():
    text = "# Fixture Model\n## Introduction\nFixture Model supports function calling."
    assert verify_page(text, "feature.tool_calling", "supported").outcome == "verified"
