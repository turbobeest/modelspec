"""A reader's JSON cannot rename the model stated by its source quotation."""

import json
from datetime import date

import pytest

from decision import verify
from decision.model import SourceRef, TargetRef, VerificationActor


class Regions:
    def __init__(self, page):
        self.page = page

    def text(self, *_args):
        return self.page

    def source_kind(self, *_args):
        return "provider_documentation"


def claim(names=("Fixture Model",)):
    return verify.Claim(
        target=TargetRef(kind="fact", id="fixture/model#offering.price.input"),
        subject="fixture/model", names=names, field="offering.price.input", label="Input",
        value=5, unit="usd_per_1m_tokens",
        collector=VerificationActor(agent="collector", model_family="collector", method="fixture"),
        sources=(SourceRef(source_id="page", snapshot_ref="sha256:" + "a" * 64,
                           cited_regions=["page"]),),
    )


def reader(quote):
    return verify.LLMExtractor(
        lambda prompt: json.dumps([{"subject": "Fixture Model", "value": "$5",
                                    "unit": "usd_per_1m_tokens", "quoted_sentence": quote}]),
        agent="fixture-reader", model="fixture", model_family="independent-fixture",
    )


@pytest.mark.parametrize("page, quote", [
    ("Model | Input | Output\nFixture Model Ultra | $5 | $9\nToken prices",
     "Fixture Model Ultra | $5 | $9"),
    ("Fixture Model Ultra costs $5 per million input tokens.\nPrices\nTerms apply.",
     "Fixture Model Ultra costs $5 per million input tokens."),
    ("# Fixture Model Ultra\nIt costs $5 per million input tokens.\nPrices",
     "It costs $5 per million input tokens."),
    ("# Fixture Model\nInput\n$2\n# Fixture Model Ultra\nIt costs $5 per million input tokens.",
     "It costs $5 per million input tokens."),
    ("Fixture Model\nInput\n$2\nFixture Model Ultra\nInput\n$5", "Input\n$5"),
])
def test_llm_cannot_rename_a_sibling_source_subject(page, quote):
    result = verify.verify(claim(), Regions(page), [reader(quote)], today=date(2026, 11, 4))
    assert result.outcome != "verified", result


@pytest.mark.parametrize("published, names", [
    ("FIXTURE--Model", ("Fixture Model",)),
    ("Fixture Model Global", ("Fixture Model", "Fixture Model Global")),
])
def test_llm_preserves_the_exact_source_subject_or_registered_alias(published, names):
    quote = f"{published} | $5 | $9"
    page = f"Model | Input | Output\n{quote}\nToken prices"
    subject = claim(names)
    extractor = reader(quote)
    result = verify.verify(subject, Regions(page), [extractor], today=date(2026, 11, 4))
    assert result.outcome == "verified", result
    readings = extractor.extract(subject, page)
    assert len(readings) == 1
    assert readings[0].subject == published
