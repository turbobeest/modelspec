"""Every verification reader binds a published subject before accepting its value."""

import json
from dataclasses import replace
from datetime import date

import pytest

from decision import verify
from decision.model import SourceRef, TargetRef, VerificationActor


class Regions:
    def __init__(self, page, *, licence=None):
        self.page = page
        self.licence = licence

    def text(self, source_id, copy_ref, region_id):
        return self.licence if source_id == "licence" else self.page

    def source_kind(self, source_id):
        return "licence_text" if source_id == "licence" else "provider_documentation"

    def source_url(self, source_id):
        return f"https://fixture.example/{source_id}"


def claim(field, value, names=("Fixture Plan",)):
    return verify.Claim(
        target=TargetRef(kind="fact", id=f"fixture/plan#{field}"),
        subject="fixture/subscription/plan", names=names, field=field, value=value,
        collector=VerificationActor(agent="fixture-collector", model_family="fixture", method="fixture@1"),
        sources=(SourceRef(source_id="page", snapshot_ref="sha256:" + "a" * 64,
                           cited_regions=["page"]),),
    )


@pytest.mark.parametrize("field, value, page", [
    ("offering.subscription.price", 50,
     "Fixture Plan Ultra $50/month\nPlan prices\nTerms apply."),
    ("offering.subscription.billing_period", "monthly",
     "Features | Fixture Plan Ultra\nBilling cycle | Monthly\nPlan prices"),
    ("offering.subscription.billing_period", "monthly",
     "Fixture Plan Ultra is billed monthly.\nPlan prices\nTerms apply."),
    ("offering.subscription.programmatic_or_agent_use", "Codex",
     "Fixture Plan Ultra includes Codex.\nPlan prices\nTerms apply."),
    ("offering.subscription.allowance.window", "five hours",
     "Fixture Plan Ultra includes a five-hour usage limit.\nCodex\nTerms apply."),
])
def test_subscription_sibling_never_verifies(field, value, page):
    result = verify.verify(claim(field, value), Regions(page),
                           verify.deterministic_extractors(), today=date(2026, 11, 4))
    assert result.outcome != "verified", result


def test_subscription_family_requires_a_registered_alias():
    subject = claim("offering.subscription.availability", "retired", ("Fixture Plan Plus",))
    page = "Fixture Plan is retired.\nAvailability\nTerms apply."
    result = verify.verify(subject, Regions(page), verify.deterministic_extractors(),
                           today=date(2026, 11, 4))
    assert result.outcome != "verified", result


@pytest.mark.parametrize("field, value, name, page", [
    ("offering.subscription.price", 100, "Fixture Plan 5x",
     "$100/month: 5x higher usage limits vs. Pro\nPlan prices\nTerms apply."),
    ("offering.subscription.usage_allowance", "5x more usage than Pro", "Fixture Plan 5x",
     "Choose 5x or 20x more usage than Pro\nPlan prices\nTerms apply."),
    ("offering.subscription.price", 20, "Claude Pro",
     "$20 if billed monthly\nCodex\nTerms apply."),
    ("offering.subscription.price", 100, "Claude Max 5x",
     "Max from $100\nCodex\nTerms apply."),
])
def test_subscription_cannot_infer_missing_source_identity(field, value, name, page):
    result = verify.verify(claim(field, value, (name,)), Regions(page),
                           verify.deterministic_extractors(), today=date(2026, 11, 4))
    assert result.outcome != "verified", result


def test_subscription_multiplier_source_requires_its_explicit_alias():
    subject = claim("offering.subscription.price", 100, ("Fixture Plan 5x", "5x"))
    page = "$100/month: 5x higher usage limits vs. Pro\nPlan prices\nTerms apply."
    result = verify.verify(subject, Regions(page), verify.deterministic_extractors(),
                           today=date(2026, 11, 4))
    assert result.outcome == "verified", result
    readings = verify.SubscriptionPageExtractor().extract(subject, page)
    assert readings
    assert {reading.subject for reading in readings} == {"5x"}


def test_subscription_plus_sibling_cannot_replace_the_exact_card_price():
    subject = claim("offering.subscription.price", 100)
    page = "Fixture Plan\n$20/month\nFixture Plan+\n$100/month\nMore usage"
    result = verify.verify(subject, Regions(page), verify.deterministic_extractors(),
                           today=date(2026, 11, 4))
    assert result.outcome != "verified", result


@pytest.mark.parametrize("heading", ["# Fixture Plan Ultra", "Fixture Plan Ultra", "Mini Fixture Plan"])
def test_subscription_price_search_stops_before_a_sibling_card(heading):
    subject = claim("offering.subscription.price", 50)
    page = f"Fixture Plan\n{heading}\n$50/month\nMore usage"
    result = verify.verify(subject, Regions(page), verify.deterministic_extractors(),
                           today=date(2026, 11, 4))
    assert result.outcome != "verified", result


@pytest.mark.parametrize("names", [("Fixture Plan",), ("Fixture", "Fixture Plan")])
def test_subscription_exact_price_keeps_published_subject(names):
    subject = claim("offering.subscription.price", 20, names)
    page = "FIXTURE--Plan $20/month\nPlan prices\nTerms apply."
    result = verify.verify(subject, Regions(page), verify.deterministic_extractors(),
                           today=date(2026, 11, 4))
    assert result.outcome == "verified", result
    readings = verify.SubscriptionPageExtractor().extract(subject, page)
    assert readings
    assert {reading.subject for reading in readings} == {"FIXTURE--Plan"}


@pytest.mark.parametrize("published", ["Fixture Model Ultra", "Mini Fixture Model"])
def test_licence_binding_cannot_use_a_sibling_name(published):
    subject = claim("licence.commercial_use", "permitted", ("Fixture Model",))
    subject = replace(subject, sources=(*subject.sources, SourceRef(
        source_id="licence", snapshot_ref="sha256:" + "b" * 64,
        cited_regions=["page"],
    )))
    licence = "Permission is hereby granted to use this software."
    page = f"{published}\nlicense_link: https://fixture.example/licence\nModel documentation"
    reader = verify.LicenceExtractor(
        lambda prompt: json.dumps({"value": "permitted", "clauses": [licence]}),
        agent="fixture-reader", model="fixture", model_family="independent-fixture",
    )
    result = verify.verify(subject, Regions(page, licence=licence), [reader],
                           today=date(2026, 11, 4))
    assert result.outcome != "verified", result
