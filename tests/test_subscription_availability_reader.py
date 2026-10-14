"""Published availability applies only to the subscription plan it names."""

from dataclasses import replace
from datetime import date

import pytest

from decision import verify
from decision.model import SourceRef, TargetRef, VerificationActor


def claim() -> verify.Claim:
    return verify.Claim(
        target=TargetRef(kind="fact", id="minimax/subscription/token-plan#availability"),
        subject="minimax/subscription/token-plan",
        names=("MiniMax Token Plan", "Token Plan"),
        field="offering.subscription.availability",
        value="existing_subscribers_only",
        collector=VerificationActor(agent="collector", model_family="collector",
                                    method="fixture"),
        sources=(SourceRef(source_id="plan-availability", snapshot_ref="sha256:" + "0" * 64,
                           cited_regions=["page"]),),
    )


@pytest.mark.parametrize(
    ("page", "value"),
    [
        ("Token Plan is open to new subscribers.", "open"),
        ("MiniMax Token Plan is available for new subscriptions.", "open"),
        ("Token Plan is available only to existing subscribers.", "existing_subscribers_only"),
        ("Token Plan is closed to new subscribers.", "existing_subscribers_only"),
        ("Token Plan is no longer available for new subscriptions. "
         "Existing subscribers can continue renewing.", "existing_subscribers_only"),
        ("Token Plan has been retired.", "retired"),
        ("Token Plan is discontinued for all subscribers.", "retired"),
        ("## Token Plan\nRetired", "retired"),
        ("## Token Plan\nExisting subscribers only\n## M Plan\nOpen to new subscribers",
         "existing_subscribers_only"),
        ("Plan | Availability\nToken Plan | Existing subscribers only\nM Plan | Open to new subscribers",
         "existing_subscribers_only"),
        ("Features | Token Plan | M Plan\nAvailability | Retired | Open to new subscribers",
         "retired"),
    ],
)
def test_reader_reads_explicit_plan_availability(page, value):
    reader = verify.SubscriptionPageExtractor()

    assert reader.accepts(page)
    assert reader.extract(claim(), page) == [verify.Reading("MiniMax Token Plan", value)]


@pytest.mark.parametrize(
    "page",
    [
        "Token Plan\n$10/month\nIncludes coding tools",
        "Token Plan is no longer listed on the pricing page.",
        "Token Plan is not retired.",
        "Token Plan is retired? No, it is still available to new subscribers.",
        "## Token Plan\nRetired? No, the plan is still available to new subscribers.",
        "Plan | Availability\nToken Plan | Retired?",
        "Token Plan will be retired next year.",
        "Premium Token Plan is retired.",
        "Token Plan Plus is closed to new subscribers.",
        "M Plan is open to new subscribers and replaces Token Plan.",
        "## Token Plan\nIncludes coding tools\n## M Plan\nRetired",
        "**Token Plan**\nIncludes coding tools\n**M Plan**\nRetired",
        "Token Plan\nIncludes coding tools\nToken Plan Plus\nRetired",
        "Plan | Availability\nToken Plan | Not disclosed\nM Plan | Retired",
        "Features | Token Plan | M Plan\nAvailability | Not disclosed | Retired",
        "Plan | Availability\nM Plan | Retired\n\nModel | Lifecycle\nToken Plan | Retired",
    ],
)
def test_reader_never_guesses_availability_or_uses_a_sibling_plan(page):
    assert verify.SubscriptionPageExtractor().extract(claim(), page) == []


@pytest.mark.parametrize(
    ("name", "page"),
    [
        ("Pro", "Pro\nNot disclosed\nPlus\nRetired"),
        ("ChatGPT Pro", "ChatGPT Pro\nNot disclosed\nChatGPT Plus\nRetired"),
    ],
)
def test_reader_does_not_inherit_retirement_from_an_unpriced_bare_sibling(name, page):
    pro = replace(claim(), subject="openai/subscription/pro", names=(name,))

    assert verify.SubscriptionPageExtractor().extract(pro, page) == []


def _tier(*names: str) -> verify.Claim:
    return replace(claim(), subject="minimax/subscription/token-plus", names=names)


@pytest.mark.parametrize(
    "page",
    [
        "Token Plan is no longer available for new purchases.",
        "Token Plan is no longer available for new purchase.",
        "With the launch of M Plan, Token Plan is no longer available for new purchases.",
        "Token Plan is no longer offered to new customers.",
        "Token Plan is closed to new sign-ups.",
    ],
)
def test_family_purchase_statement_closes_the_named_tier(page):
    reader = verify.SubscriptionPageExtractor()
    tier = _tier("Token Plan Plus")

    assert reader.accepts(page)
    assert reader.extract(tier, page) == [
        verify.Reading("Token Plan Plus", "existing_subscribers_only")]


def test_family_purchase_statement_closes_the_catalogue_tier_name():
    """The filed name is the vendor plus the family plus one tier word."""
    reader = verify.SubscriptionPageExtractor()
    tier = _tier("MiniMax Token Plan Plus", "Plus", "token-plus")
    page = "With the launch of M Plan, Token Plan is no longer available for new purchases."

    assert reader.accepts(page)
    assert reader.extract(tier, page) == [
        verify.Reading("MiniMax Token Plan Plus", "existing_subscribers_only")]


@pytest.mark.parametrize(
    "page",
    [
        "M Plan is no longer available for new purchases.",
        "Token Plan new purchases are now available.",
        "Is Token Plan no longer available for new purchases?",
        "Token Plan is no longer available for new purchases?",
        "Token Pro is no longer available for new purchases.",
        "MyToken Plan is no longer available for new purchases.",
        "Token Plan is available for new purchases.",
    ],
)
def test_family_purchase_statement_rejects_siblings_questions_and_open_wording(page):
    assert verify.SubscriptionPageExtractor().extract(_tier("Token Plan Plus"), page) == []


@pytest.mark.parametrize("names", [("M Plan",), ("Token Pro",)])
def test_token_plan_family_statement_does_not_apply_to_another_plan(names):
    other = _tier(*names)
    page = "Token Plan is no longer available for new purchases."

    assert verify.SubscriptionPageExtractor().extract(other, page) == []


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("offering.subscription.price", 10),
        ("offering.subscription.billing_period", "monthly"),
        ("offering.subscription.usage_allowance", None),
    ],
)
def test_availability_only_page_keeps_other_subscription_claims_skipped(field, value):
    class Regions:
        def text(self, *_args):
            return "Token Plan is retired."

        def source_kind(self, *_args):
            return "provider_documentation"

    result = verify.verify(
        replace(claim(), field=field, value=value), Regions(),
        verify.deterministic_extractors(), today=date(2026, 10, 13),
    )

    assert result.outcome == "skipped"
