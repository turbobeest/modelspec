"""Availability notices apply to explicitly listed tiers of their named family."""

from datetime import date

import pytest

from decision.model import SourceRef, TargetRef, VerificationActor
from decision.verify import Claim, deterministic_extractors, verify


class Page:
    def __init__(self, text):
        self.body = text

    def text(self, *_args):
        return self.body

    def source_kind(self, *_args):
        return "provider_documentation"

    def source_url(self, *_args):
        return "https://fixture.example/plans/notice"


def verify_availability(text, name, value="existing_subscribers_only", *, aliases=()):
    claim = Claim(
        target=TargetRef(kind="fact", id="fixture/subscription/tier#availability"),
        subject="fixture/subscription/tier", names=(name, *aliases),
        field="offering.subscription.availability", value=value,
        collector=VerificationActor(agent="fixture-collector", model_family="human",
                                    method="fixture@1"),
        sources=(SourceRef(source_id="notice", snapshot_ref="sha256:" + "0" * 64,
                           cited_regions=["page"]),),
    )
    return verify(claim, Page(text), deterministic_extractors(), today=date(2026, 11, 5))


@pytest.mark.parametrize("tier", ["Plus", "Max", "Ultra"])
def test_family_notice_covers_only_its_explicit_table_tiers(tier):
    text = """# Existing Fixture Plan subscribers
Fixture Plan is no longer available for new purchases.
Current Fixture Plan tier | New Other Plan tiers
Plus | Standard
Max | Premium
Ultra | Enterprise
"""
    result = verify_availability(text, f"Fixture Plan {tier}")
    assert result.outcome == "verified", result


@pytest.mark.parametrize("tier", ["Plus", "Max", "Ultra"])
def test_family_and_tier_tokens_match_a_registered_slug_alias(tier):
    text = """# Existing Fixture Plan subscribers
With the launch of Other Plan, Fixture Plan is no longer available for new purchases.
Existing subscribers can continue using their plan.
Current Fixture Plan tier | New Other Plan tiers
Plus | Standard
Max | Premium
Ultra | Enterprise
"""
    result = verify_availability(text, f"Provider Fixture Plan {tier}",
                                 aliases=(f"fixture-{tier.lower()}",))
    assert result.outcome == "verified", result


@pytest.mark.parametrize("table,notice", [
    ("Current Fixture Plan tier | New Other Plan tiers\nPlus Ultra | Premium",
     "Fixture Plan is no longer available for new purchases."),
    ("Current Fixture Plan tier | New Other Plan tiers\nSuper Plus | Premium",
     "Fixture Plan is no longer available for new purchases."),
    ("Current Other Plan tier | New Fixture Plan tiers\nPlus | Premium",
     "Fixture Plan is no longer available for new purchases."),
    ("Current Fixture Plan tier | New Other Plan tiers\nPlus | Premium",
     "Other Plan is no longer available for new purchases."),
    ("Current Fixture Plan tier | New Other Plan tiers\nMax | Premium",
     "Fixture Plan is no longer available for new purchases."),
    ("Plan | New Other Plan tiers\nPlus | Premium",
     "Fixture Plan is no longer available for new purchases."),
    ("Current Fixture Plan tier | New Other Plan tiers\nPlus | Premium",
     "Fixture Plan is no longer available for new purchases?"),
    ("Current Fixture Plan tier | New Other Plan tiers\nPlus | Premium",
     "Fixture Plan is no longer available for new purchases.\n# Another plan family"),
])
def test_family_notice_does_not_invent_tiers_or_cross_family_boundaries(table, notice):
    text = f"# Existing Fixture Plan subscribers\n{notice}\n{table}"
    result = verify_availability(text, "Provider Fixture Plan Plus", aliases=("fixture-plus",))
    assert result.outcome != "verified", result


def test_new_plan_column_does_not_inherit_the_current_familys_notice():
    text = """# Existing Fixture Plan subscribers
Fixture Plan is no longer available for new purchases.
Current Fixture Plan tier | New Other Plan tiers
Plus | Ultra
"""
    result = verify_availability(text, "Other Plan Ultra", aliases=("other-ultra",))
    assert result.outcome != "verified", result
